"""Experiment scheduler: one run, a sweep, or a grid — sequential or parallel.

Responsibility: turn a sweep definition into a set of run configurations, decide
which of them still need executing, and execute them.

Design decisions and their reasons:

  * **Expansion is separate from execution.** `expand()` is a pure function, so a
    sweep can be inspected (`p1 sweep --dry-run`) before hours of compute are
    spent, and so expansion is unit-testable without running anything.
  * **Parallelism cannot change results.** Each run is seeded from its own config
    and writes its own directory, so `--workers 8` and `--workers 1` produce
    identical numbers. A test asserts this. Processes, not threads: the loop is
    pure-Python and would not scale under the GIL.
  * **Resume is per run, keyed by config hash.** A completed run of the *same*
    config is skipped; a completed run of a *different* config that happens to
    share a directory is not. Interrupted runs (`status: running`) are re-executed,
    because a partial artifact set is not a result.
  * **Multi-seed is a first-class axis, not a grid dimension.** Seeds are the
    independent unit for the paired inference in `science/stats.py`; keeping them
    separate from the parameter grid makes "20 seeds x 3 conditions" express what
    it means.

Mid-run resumption (restarting a single interrupted run from a checkpoint) is
deliberately not implemented: a v0 run takes seconds, so the added state-restore
machinery would cost more complexity than it saves. See docs/engineering/M2 plan.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from core.types import RunResult, RunStatus
from experiments.engine.artifacts import is_complete, read_status
from experiments.engine.config import (
    CONFIG_VERSION,
    SUPPORTED_VERSIONS,
    ConfigError,
    RunConfig,
    apply_overrides,
    flatten_axes,
    read_mapping,
)
from experiments.engine.engine import DEFAULT_ROOT, build_components, run, run_dir_for
from core.seeds import SeedSet

_SWEEP_KEYS = frozenset(
    {"config_version", "name", "description", "base", "seeds", "grid", "conditions", "root"}
)


@dataclass(frozen=True)
class Sweep:
    """A named set of runs derived from one base configuration.

    `grid`       {dotted path: [values]} — full cross product.
    `conditions` [{dotted path: value}]  — named points, for control sets that are
                 not a cross product (a gate swap usually implies matching params,
                 which a grid would combine wrongly).
    `seeds`      the multi-seed axis, applied to every grid/condition point.
    """

    name: str
    base: RunConfig
    grid: Dict[str, List[Any]] = field(default_factory=dict)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    seeds: List[int] = field(default_factory=lambda: [0])
    description: str = ""

    @classmethod
    def load(cls, path: str | Path) -> "Sweep":
        raw = read_mapping(path)
        unknown = set(raw) - _SWEEP_KEYS
        if unknown:
            raise ConfigError(f"sweep: unexpected keys {sorted(unknown)}")
        version = raw.get("config_version")
        if version not in SUPPORTED_VERSIONS:
            raise ConfigError(
                f"sweep config_version {version!r} not supported (expected one of "
                f"{list(SUPPORTED_VERSIONS)}, current {CONFIG_VERSION})"
            )
        if "base" not in raw:
            raise ConfigError("sweep: missing 'base' (path to the base run config)")
        base_path = (Path(path).parent / str(raw["base"])).resolve()
        base = RunConfig.load(base_path)

        grid_raw = raw.get("grid") or {}
        if not isinstance(grid_raw, Mapping):
            raise ConfigError("sweep.grid must be a mapping of dotted path -> list")
        grid: Dict[str, List[Any]] = {}
        for key, values in grid_raw.items():
            if not isinstance(values, (list, tuple)) or not values:
                raise ConfigError(f"sweep.grid[{key!r}] must be a non-empty list")
            grid[str(key)] = list(values)

        conditions_raw = raw.get("conditions") or []
        if not isinstance(conditions_raw, (list, tuple)):
            raise ConfigError("sweep.conditions must be a list of override mappings")
        conditions = []
        for entry in conditions_raw:
            if not isinstance(entry, Mapping):
                raise ConfigError("sweep.conditions entries must be mappings")
            conditions.append(dict(entry))

        seeds = _parse_seeds(raw.get("seeds"))
        return cls(
            name=str(raw.get("name", base.name)),
            base=base,
            grid=grid,
            conditions=conditions,
            seeds=seeds,
            description=str(raw.get("description", "")),
        )

    def expand(self) -> List[RunConfig]:
        """All run configs this sweep implies. Pure: touches no disk, no registry.

        Duplicates are dropped by config hash, so overlapping conditions and grid
        points cannot schedule the same run twice.
        """
        base_raw = self.base.as_dict()
        points: List[Dict[str, Any]] = []
        for grid_point in flatten_axes(self.grid):
            if self.conditions:
                for condition in self.conditions:
                    merged = {**condition, **grid_point}
                    points.append(merged)
            else:
                points.append(dict(grid_point))

        configs: List[RunConfig] = []
        seen: set[str] = set()
        for index, overrides in enumerate(points):
            for seed in self.seeds:
                raw = apply_overrides(base_raw, overrides)
                raw["name"] = self.name
                raw["seeds"] = {**raw.get("seeds", {}), "master": int(seed)}
                if overrides:
                    raw["description"] = _label(overrides)
                config = RunConfig.from_dict(raw)
                if config.config_hash in seen:
                    continue
                seen.add(config.config_hash)
                configs.append(config)
        if not configs:
            raise ConfigError(f"sweep {self.name!r} expanded to zero runs")
        return configs

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "base_name": self.base.name,
            "grid": {k: list(v) for k, v in self.grid.items()},
            "conditions": [dict(c) for c in self.conditions],
            "seeds": list(self.seeds),
            "n_runs": len(self.expand()),
        }


def validate_batch(configs: Sequence[RunConfig]) -> None:
    """Instantiate every config's components without running anything.

    Catches the whole class of error that a pure config-schema check cannot: a
    parameter name the schema accepts (`model.params` is a free-form mapping) but
    no component declares — `decy` for `decay`, `treshold` for `threshold`. Because
    factories no longer swallow unknown keyword arguments, constructing them is a
    complete check.

    Reports *every* bad arm at once. Discovering the second typo after a two-hour
    sweep is a worse outcome than a slightly longer error message.

    Cost is one component construction per run, which is negligible next to
    executing it — and it is the difference between failing in seconds and failing
    after hours of compute.
    """
    problems: List[str] = []
    for config in configs:
        try:
            seeds = SeedSet.build(config.seeds.master, config.seeds.mode, config.seeds.overrides)
            build_components(config, seeds)
        except Exception as exc:  # noqa: BLE001 — any construction failure is a config fault
            problems.append(f"  {config.run_id} ({config.description or 'base'}): {exc}")
    if problems:
        raise ConfigError(
            f"{len(problems)} of {len(configs)} runs are misconfigured:\n" + "\n".join(problems)
        )


def run_batch(
    configs: Sequence[RunConfig],
    root: str | Path = DEFAULT_ROOT,
    workers: int = 1,
    resume: bool = True,
    quiet: bool = True,
    progress: Optional[Any] = None,
    validate: bool = True,
) -> List[RunResult]:
    """Execute configs, sequentially or across processes. Order of results follows
    `configs`, regardless of completion order, so downstream pairing is stable."""
    if workers < 1:
        raise ValueError("workers must be >= 1")
    if validate:
        validate_batch(configs)

    pending = list(configs)
    if workers == 1 or len(pending) == 1:
        results = []
        for index, config in enumerate(pending):
            result = run(config, root=root, resume=resume, quiet=quiet)
            _report(progress, index, len(pending), result)
            results.append(result)
        return results

    payloads = [(_serialise(config), str(root), resume) for config in pending]
    results_by_index: Dict[int, RunResult] = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_worker, payload): i for i, payload in enumerate(payloads)}
        for done, future in enumerate(as_completed(futures)):
            index = futures[future]
            try:
                results_by_index[index] = _deserialise(future.result())
            except Exception as exc:  # noqa: BLE001 — a dead worker must not kill the batch
                config = pending[index]
                results_by_index[index] = RunResult(
                    run_id=config.run_id,
                    config_hash=config.config_hash,
                    status=RunStatus.FAILED,
                    run_dir=str(run_dir_for(config, root)),
                    error=f"worker failure: {type(exc).__name__}: {exc}",
                )
            _report(progress, done, len(payloads), results_by_index[index])
    return [results_by_index[i] for i in range(len(payloads))]


def pending_runs(
    configs: Sequence[RunConfig], root: str | Path = DEFAULT_ROOT
) -> Tuple[List[RunConfig], List[RunConfig]]:
    """Split configs into (to run, already complete). Used by `--dry-run`."""
    todo: List[RunConfig] = []
    done: List[RunConfig] = []
    for config in configs:
        (done if is_complete(run_dir_for(config, root), config.config_hash) else todo).append(
            config
        )
    return todo, done


def batch_summary(results: Sequence[RunResult]) -> Dict[str, Any]:
    """Counts and failures, for the CLI's final line and for CI assertions."""
    failed = [r for r in results if not r.ok]
    return {
        "runs": len(results),
        "completed": len(results) - len(failed),
        "failed": len(failed),
        "failures": [{"run_id": r.run_id, "error": r.error} for r in failed],
        "total_seconds": round(
            sum(float(r.compute.get("wall_seconds", 0.0) or 0.0) for r in results), 3
        ),
    }


def interrupted_runs(root: str | Path = DEFAULT_ROOT) -> List[str]:
    """Run directories left in `running` state — i.e. killed mid-execution."""
    out: List[str] = []
    for status_path in sorted(Path(root).rglob("status.json")):
        status = read_status(status_path.parent)
        if status and status.get("status") == RunStatus.RUNNING.value:
            out.append(str(status_path.parent))
    return out


# --------------------------------------------------------------------------- #
# Process-pool plumbing
# --------------------------------------------------------------------------- #


def _worker(payload: Tuple[str, str, bool]) -> str:
    """Top-level so it is picklable on Windows spawn semantics."""
    config_json, root, resume = payload
    config = RunConfig.from_dict(json.loads(config_json))
    result = run(config, root=root, resume=resume, quiet=True)
    return json.dumps(result.as_dict())


def _serialise(config: RunConfig) -> str:
    return json.dumps(config.as_dict())


def _deserialise(payload: str) -> RunResult:
    raw = json.loads(payload)
    return RunResult(
        run_id=raw["run_id"],
        config_hash=raw["config_hash"],
        status=RunStatus(raw["status"]),
        metrics=raw.get("metrics", {}),
        compute=raw.get("compute", {}),
        run_dir=raw.get("run_dir", ""),
        error=raw.get("error", ""),
    )


def _parse_seeds(raw: Any) -> List[int]:
    """Accept `[0, 1, 2]` or `{start: 0, count: 20}` or `{start: 0, stop: 20}`."""
    if raw is None:
        return [0]
    if isinstance(raw, (list, tuple)):
        if not raw:
            raise ConfigError("sweep.seeds must not be empty")
        return [int(s) for s in raw]
    if isinstance(raw, Mapping):
        unknown = set(raw) - {"start", "count", "stop", "step"}
        if unknown:
            raise ConfigError(f"sweep.seeds: unexpected keys {sorted(unknown)}")
        start = int(raw.get("start", 0))
        step = int(raw.get("step", 1))
        if "count" in raw:
            count = int(raw["count"])
        elif "stop" in raw:
            count = max(0, (int(raw["stop"]) - start + step - 1) // step)
        else:
            raise ConfigError("sweep.seeds mapping needs 'count' or 'stop'")
        if count < 1:
            raise ConfigError("sweep.seeds resolves to zero seeds")
        return [start + i * step for i in range(count)]
    raise ConfigError(f"sweep.seeds: cannot read {type(raw).__name__}")


def _label(overrides: Mapping[str, Any]) -> str:
    """Human-readable condition label, e.g. `gate.name=surprise decay=1.0`."""
    parts = []
    for key, value in sorted(overrides.items()):
        short = key.split(".")[-1] if key.endswith((".name", ".decay")) else key
        parts.append(f"{short}={value}")
    return " ".join(parts)


def _report(progress: Optional[Any], index: int, total: int, result: RunResult) -> None:
    if progress is None:
        return
    try:
        progress(index + 1, total, result)
    except Exception:  # noqa: BLE001 — progress reporting is never load-bearing
        pass


def iter_expanded(sweeps: Iterable[Sweep]) -> List[RunConfig]:
    """Flatten several sweeps into one batch, dropping duplicate configs."""
    seen: set[str] = set()
    out: List[RunConfig] = []
    for sweep in sweeps:
        for config in sweep.expand():
            if config.config_hash in seen:
                continue
            seen.add(config.config_hash)
            out.append(config)
    return out
