"""Command-line entry point.

Responsibility: parse arguments, call the engine or scheduler, and choose an exit
code. It contains no experiment logic — anything it could do, a script can do by
importing the same functions.

    p1 run    configs/v0/baseline.yaml [--set model.params.decay=1.0]
    p1 sweep  configs/v0/v0_2_matched_updates.yaml --workers 8 [--dry-run]
    p1 list
    p1 status
    p1 verify artifacts/runs/<experiment>/<run_id>

Exit codes are meaningful, so CI can depend on them:
    0  everything completed
    1  at least one run failed
    2  the request was invalid (bad config, unknown component, missing file)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

from core.types import RunResult
from experiments.engine.artifacts import read_status
from experiments.engine.config import ConfigError, RunConfig
from experiments.engine.engine import DEFAULT_ROOT, run, run_dir_for
from experiments.engine.plugins import registry_summary
from experiments.engine.scheduler import (
    Sweep,
    batch_summary,
    interrupted_runs,
    pending_runs,
    run_batch,
    validate_batch,
)

EXIT_OK = 0
EXIT_FAILED_RUNS = 1
EXIT_BAD_REQUEST = 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="p1", description="P1 experiment platform")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="execute one configuration")
    p_run.add_argument("config", help="path to a run config (YAML or JSON)")
    _add_common(p_run)
    p_run.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="PATH=VALUE",
        help="override a dotted config path, e.g. --set model.params.decay=1.0",
    )

    p_sweep = sub.add_parser("sweep", help="execute a sweep, grid or multi-seed batch")
    p_sweep.add_argument("sweep", help="path to a sweep definition")
    _add_common(p_sweep)
    p_sweep.add_argument("--workers", type=int, default=1, help="parallel processes (default 1)")
    p_sweep.add_argument(
        "--dry-run",
        action="store_true",
        help="print the expanded run list and what would be skipped, then exit",
    )

    sub.add_parser("list", help="show every registered component")

    p_status = sub.add_parser("status", help="summarise runs under the artifact root")
    p_status.add_argument("--root", default=str(DEFAULT_ROOT))

    p_verify = sub.add_parser("verify", help="re-check a run's artifact hashes")
    p_verify.add_argument("run_dir")

    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            return _cmd_run(args)
        if args.command == "sweep":
            return _cmd_sweep(args)
        if args.command == "list":
            return _cmd_list()
        if args.command == "status":
            return _cmd_status(args.root)
        if args.command == "verify":
            return _cmd_verify(args.run_dir)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return EXIT_BAD_REQUEST
    except KeyError as exc:
        # Registry lookups raise KeyError with the available names attached.
        print(f"unknown component: {exc}", file=sys.stderr)
        return EXIT_BAD_REQUEST
    except FileNotFoundError as exc:
        print(f"not found: {exc}", file=sys.stderr)
        return EXIT_BAD_REQUEST
    return EXIT_BAD_REQUEST


def _add_common(parser: Any) -> None:
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="artifact root directory")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="re-execute runs even if a completed artifact set exists",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress per-run console events")


def _cmd_run(args: Any) -> int:
    config = RunConfig.load(args.config)
    overrides = _parse_overrides(args.overrides)
    if overrides:
        config = config.with_overrides(overrides)
    result = run(config, root=args.root, resume=not args.no_resume, quiet=args.quiet)
    _print_run(result)
    return EXIT_OK if result.ok else EXIT_FAILED_RUNS


def _cmd_sweep(args: Any) -> int:
    sweep = Sweep.load(args.sweep)
    configs = sweep.expand()
    todo, done = pending_runs(configs, args.root)

    if args.dry_run:
        print(f"sweep: {sweep.name}")
        print(f"  runs expanded : {len(configs)}")
        print(f"  already done  : {len(done)}")
        print(f"  to execute    : {len(todo)}")
        for config in configs:
            mark = "skip" if config in done else "run "
            print(f"  [{mark}] {config.run_id}  {config.description}")
        # A dry run that did not check the configs would give false confidence:
        # validation is the expensive-to-discover half of "would this work?".
        validate_batch(configs)
        print("  validation    : all runs constructible")
        return EXIT_OK

    results = run_batch(
        configs,
        root=args.root,
        workers=args.workers,
        resume=not args.no_resume,
        quiet=True,
        progress=_progress,
    )
    summary = batch_summary(results)
    print(
        f"sweep {sweep.name}: {summary['completed']}/{summary['runs']} completed "
        f"in {summary['total_seconds']}s"
    )
    for failure in summary["failures"]:
        print(f"  FAILED {failure['run_id']}: {failure['error']}", file=sys.stderr)
    return EXIT_OK if summary["failed"] == 0 else EXIT_FAILED_RUNS


def _cmd_list() -> int:
    for kind, names in sorted(registry_summary().items()):
        print(f"{kind}:")
        for name in names:
            print(f"  {name}")
    return EXIT_OK


def _cmd_status(root: str) -> int:
    root_path = Path(root)
    if not root_path.exists():
        print(f"no artifact root at {root_path}")
        return EXIT_OK
    counts: Dict[str, int] = {}
    for status_path in sorted(root_path.rglob("status.json")):
        status = read_status(status_path.parent) or {}
        key = str(status.get("status", "unknown"))
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        print(f"no runs under {root_path}")
        return EXIT_OK
    for key, count in sorted(counts.items()):
        print(f"{key:10s} {count}")
    stuck = interrupted_runs(root_path)
    for path in stuck:
        print(f"  interrupted: {path}", file=sys.stderr)
    return EXIT_OK


def _cmd_verify(run_dir: str) -> int:
    """Recompute every artifact hash and compare with `inventory.json`."""
    import hashlib

    path = Path(run_dir)
    inventory_path = path / "inventory.json"
    if not inventory_path.is_file():
        print(f"no inventory.json in {path}", file=sys.stderr)
        return EXIT_BAD_REQUEST
    inventory = json.loads(inventory_path.read_text(encoding="utf-8")).get("files", {})
    bad: List[str] = []
    missing: List[str] = []
    for relative, entry in sorted(inventory.items()):
        target = path / relative
        if not target.is_file():
            missing.append(relative)
            continue
        digest = hashlib.sha256()
        with target.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                digest.update(chunk)
        if digest.hexdigest() != entry.get("sha256"):
            bad.append(relative)
    print(f"verified {len(inventory)} files in {path}")
    for relative in missing:
        print(f"  MISSING  {relative}", file=sys.stderr)
    for relative in bad:
        print(f"  MODIFIED {relative}", file=sys.stderr)
    return EXIT_OK if not bad and not missing else EXIT_FAILED_RUNS


def _parse_overrides(raw: Sequence[str]) -> Dict[str, Any]:
    """`path=value` pairs. Values go through the YAML scalar parser, so `1.0` is a
    float, `true` is a bool and `null` is None — matching config-file semantics."""
    out: Dict[str, Any] = {}
    for item in raw:
        if "=" not in item:
            raise ConfigError(f"--set expects PATH=VALUE, got {item!r}")
        path, _, value = item.partition("=")
        path = path.strip()
        if not path:
            raise ConfigError(f"--set has an empty path in {item!r}")
        try:
            out[path] = yaml.safe_load(value)
        except yaml.YAMLError as exc:
            raise ConfigError(f"--set {path}: cannot parse value {value!r} ({exc})") from exc
    return out


def _print_run(result: RunResult) -> None:
    print(f"{result.status.value}: {result.run_id}")
    print(f"  artifacts: {result.run_dir}")
    if result.error:
        print(f"  error: {result.error}", file=sys.stderr)
        return
    compute = result.compute or {}
    print(
        f"  steps={compute.get('steps')} updates={compute.get('updates_total')} "
        f"seconds={compute.get('wall_seconds')}"
    )
    for name, payload in sorted(result.metrics.items()):
        if isinstance(payload, dict):
            headline = _headline(payload)
            if headline:
                print(f"  {name}: {headline}")


_HEADLINE_KEYS = (
    "online_loss_tail",
    "final_prior_excess_mean",
    "degradation_prior_mean",
    "retention",
    "adaptation_auc",
    "updates_total",
    "fired_steps",
)


def _headline(payload: Dict[str, Any]) -> str:
    parts = []
    for key in _HEADLINE_KEYS:
        if key in payload and isinstance(payload[key], (int, float)):
            parts.append(f"{key}={payload[key]:.4f}")
    return " ".join(parts)


def _progress(done: int, total: int, result: RunResult) -> None:
    mark = "ok " if result.ok else "FAIL"
    print(f"  [{done}/{total}] {mark} {result.run_id}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
