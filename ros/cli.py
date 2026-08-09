"""P1 Research Operating System — command line.

``python -m ros <command>``. One entry point, used identically by a human at a
terminal, by CI, and by an agent shelling out. That is not a convenience: if
agents used a different interface from CI, the two would eventually disagree
about whether the laboratory is in a good state, and nobody would know which to
believe.

Exit codes are part of the contract:

* ``0`` — the checked property holds
* ``1`` — it does not, and a blocking gate says so
* ``2`` — the command could not run (bad arguments, unreadable store)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .admissibility import ClaimScope, Determinism, Manifest, assess
from .governance import RegistryState, load_registration
from .store import Store, load_default

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_ERROR = 2


def _configure_stdout() -> None:
    """Force UTF-8 output.

    The default Windows console encoding is cp1252 and cannot represent the
    characters used in this output, so an unconfigured stream turns a passing
    check into a UnicodeEncodeError traceback. A tool that reports the wrong
    answer because of the terminal it ran in is worse than no tool.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):  # pragma: no cover - stream not reconfigurable
                pass


def _load(args: argparse.Namespace) -> Store:
    return load_default(args.root)


def _git_commit(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):  # pragma: no cover - git absent
        return None
    return out.stdout.strip() or None


# ------------------------------------------------------------- commands


def cmd_check(args: argparse.Namespace) -> int:
    store = _load(args)
    findings = store.check()
    errors = [f for f in findings if f.severity == "error"]
    for finding in findings:
        print(finding)
    print(
        f"\n{len(store)} records, {len(store.relations)} relations, "
        f"digest {store.content_hash()[:16]}"
    )
    print(f"{len(errors)} error(s), {len(findings) - len(errors)} warning(s)")
    return EXIT_FAILED if errors else EXIT_OK


def cmd_gates(args: argparse.Namespace) -> int:
    from .gates import GATE_BY_NAME, run_gates

    store = _load(args)
    unknown = [n for n in (args.only or []) if n not in GATE_BY_NAME]
    if unknown:
        print(f"unknown gate(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"available: {', '.join(GATE_BY_NAME)}", file=sys.stderr)
        return EXIT_ERROR
    run = run_gates(store, args.root, args.only or None)
    print(run.render(verbose=args.verbose))
    return run.exit_code


def cmd_admissibility(args: argparse.Namespace) -> int:
    registration = load_registration(args.root)
    manifest = Manifest(
        run_id=args.run_id,
        determinism=Determinism(args.determinism),
        clean_checkout=not args.dirty,
        complete=not args.incomplete,
        protocol_frozen_before_first_run=args.protocol_frozen,
        protocol_hash_matched=args.protocol_matched,
        coverage_disclosed=args.coverage_disclosed,
        stream_complete_for_scope=not args.incomplete,
        faults_intact=not args.faults_dropped,
    )
    verdict = assess(manifest, registration, ClaimScope(args.scope))
    if args.json:
        print(
            json.dumps(
                {
                    "run_id": manifest.run_id,
                    "scope": args.scope,
                    "tier": verdict.tier.value,
                    "admissible": verdict.admissible,
                    "reasons": list(verdict.reasons),
                    "ceilings": list(verdict.ceilings),
                },
                indent=2,
            )
        )
    else:
        print(verdict.explain())
    return EXIT_OK if verdict.admissible else EXIT_FAILED


def cmd_propagation(args: argparse.Namespace) -> int:
    from .propagation import audit, audit_all

    store = _load(args)
    if args.experiment:
        reports = [audit(store, args.experiment)]
    else:
        reports = audit_all(store, include_not_due=args.all)
    for report in reports:
        print(report.render())
        print()
    due = [r for r in reports if r.due]
    incomplete = [r for r in due if not r.complete]
    print(f"{len(due)} due, {len(due) - len(incomplete)} complete, {len(incomplete)} outstanding")
    return EXIT_FAILED if incomplete else EXIT_OK


def cmd_protocol(args: argparse.Namespace) -> int:
    from . import protocol as proto

    path = Path(args.path)
    if args.action == "lint":
        findings = proto.lint(proto.load(path))
        for finding in findings:
            print(finding)
        print(f"{len(findings)} finding(s)")
        return EXIT_FAILED if findings else EXIT_OK
    if args.action == "freeze":
        try:
            record = proto.freeze(path, commit=_git_commit(Path(args.root)))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_FAILED
        print(f"froze {record.protocol_id} as {record.digest}")
        print(f"wrote {proto.freeze_path_for(path)}")
        return EXIT_OK
    matched, message = proto.verify(path)
    print(message)
    return EXIT_OK if matched else EXIT_FAILED


def cmd_kpi(args: argparse.Namespace) -> int:
    from . import kpi

    store = _load(args)
    metrics = kpi.compute(store, load_registration(args.root))
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "key": m.key,
                        "name": m.name,
                        "value": m.value,
                        "rendered": m.rendered,
                        "target": m.target,
                        "healthy": m.healthy,
                    }
                    for m in metrics
                ],
                indent=2,
            )
        )
    else:
        print(kpi.render(metrics))
    return EXIT_OK


def cmd_render(args: argparse.Namespace) -> int:
    from .projections import render_laboratory_state

    store = _load(args)
    target = render_laboratory_state(store, args.root)
    print(f"wrote {target}")
    return EXIT_OK


def cmd_drift(args: argparse.Namespace) -> int:
    from .projections import drift

    store = _load(args)
    report = drift(store, args.root)
    print(report.render())
    return EXIT_OK if report.clean else EXIT_FAILED


def cmd_doctor(args: argparse.Namespace) -> int:
    """One screen answering: can this laboratory produce admissible evidence,
    and if not, what exactly is in the way?"""
    from . import kpi
    from .gates import run_gates

    root = Path(args.root)
    store = _load(args)
    registration = load_registration(root)

    print(f"P1 Research Operating System {__version__}")
    print(f"repository: {root.resolve()}")
    commit = _git_commit(root)
    print(f"commit:     {commit or 'unknown'}")
    print(f"store:      {store.path.as_posix()}  digest {store.content_hash()[:16]}")
    print()

    print("== Admissibility ==")
    if registration.active:
        print("registration active: runs may bear evidence subject to their manifest")
    else:
        print("registration NOT active — Article L-11")
        for gap in registration.missing():
            print(f"  - {gap}")
        try:
            state = RegistryState.load(root / "GOVERNANCE_REGISTRY.yaml")
            for path in state.unregistered_governing_artifacts():
                print(f"  - unregistered governing artifact: {path}")
        except (OSError, ValueError):
            pass
    print()

    print("== Gates ==")
    run = run_gates(store, root)
    print(run.render(verbose=False))
    print()

    print("== Indicators ==")
    print(kpi.render(kpi.compute(store, registration)))
    return run.exit_code


# --------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ros",
        description="P1 Research Operating System — the operating system around the "
        "frozen P1-v2 architecture.",
    )
    parser.add_argument("--version", action="version", version=f"ros {__version__}")
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="integrity-check the scientific store")
    check.set_defaults(func=cmd_check)

    gates = subparsers.add_parser("gates", help="run quality gates (CI entry point)")
    gates.add_argument("--only", nargs="+", metavar="GATE", help="run only these gates")
    gates.add_argument("-v", "--verbose", action="store_true", help="show passing findings too")
    gates.set_defaults(func=cmd_gates)

    adm = subparsers.add_parser("admissibility", help="assess a run manifest against the Lock")
    adm.add_argument("run_id")
    adm.add_argument("--determinism", choices=["D0", "D1", "D2"], default="D0")
    adm.add_argument("--scope", choices=["object", "population", "run"], default="object")
    adm.add_argument("--dirty", action="store_true", help="working tree was not clean")
    adm.add_argument("--incomplete", action="store_true", help="observation stream was truncated")
    adm.add_argument("--faults-dropped", action="store_true", help="FAULT records were dropped")
    adm.add_argument("--protocol-frozen", action="store_true", help="frozen before the first run")
    adm.add_argument("--protocol-matched", action="store_true", help="protocol hash matched")
    adm.add_argument("--coverage-disclosed", action="store_true", help="coverage was disclosed")
    adm.add_argument("--json", action="store_true")
    adm.set_defaults(func=cmd_admissibility)

    prop = subparsers.add_parser("propagation", help="audit the nine propagation obligations")
    prop.add_argument("experiment", nargs="?", help="one experiment id (default: all due)")
    prop.add_argument("--all", action="store_true", help="include experiments not yet executed")
    prop.set_defaults(func=cmd_propagation)

    protocol = subparsers.add_parser("protocol", help="lint, freeze or verify a protocol")
    protocol.add_argument("action", choices=["lint", "freeze", "verify"])
    protocol.add_argument("path")
    protocol.set_defaults(func=cmd_protocol)

    kpis = subparsers.add_parser("kpi", help="compute laboratory indicators")
    kpis.add_argument("--json", action="store_true")
    kpis.set_defaults(func=cmd_kpi)

    render = subparsers.add_parser("render", help="regenerate generated projections")
    render.set_defaults(func=cmd_render)

    drift = subparsers.add_parser("drift", help="check registries against the store")
    drift.set_defaults(func=cmd_drift)

    doctor = subparsers.add_parser("doctor", help="full laboratory status on one screen")
    doctor.set_defaults(func=cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FileNotFoundError as exc:
        print(f"ros: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except (KeyError, ValueError) as exc:
        print(f"ros: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
