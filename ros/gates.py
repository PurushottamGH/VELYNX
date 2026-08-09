"""P1 Research Operating System — quality gates.

A gate is a check with an exit code. Everything the ROS knows how to verify is
exposed here in one shape so that CI, a pre-commit hook and a human at a terminal
all run the identical predicate and get the identical answer.

One distinction carries most of the design: **blocking** versus **advisory**.

A blocking gate fails the build. Only defects that are the repository's fault
block: an inconsistent store, a projection that contradicts it, an executed
experiment whose results never propagated, a protocol edited after freezing.

Registration is *advisory*, and deliberately so. Article L-11 makes unregistered
work engineering-only, not forbidden — engineering is exactly what P1 should be
doing while registration is pending. A gate that failed the build on it would
halt legitimate work to protest a governance state the engineer cannot fix, and
the first thing anyone would do is disable the gate. An advisory gate that is
read is worth more than a blocking gate that is switched off.

Vocabulary conformance is likewise advisory, for a different reason: closing that
gap requires either amending a Lock vocabulary (a constitutional change) or
rewriting evidence records (a scientific act). Neither is something CI may
compel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .store import Finding, Store, errors as store_errors

#: Directory scanned for protocols by the protocol gate.
PROTOCOL_GLOB = "configs/protocols/*.yaml"


@dataclass
class GateResult:
    name: str
    passed: bool
    summary: str
    findings: tuple[Finding, ...] = ()
    blocking: bool = True

    @property
    def blocks(self) -> bool:
        return self.blocking and not self.passed

    def render(self, verbose: bool = False) -> str:
        if self.passed:
            mark = "PASS"
        else:
            mark = "FAIL" if self.blocking else "warn"
        lines = [f"{mark}  {self.name}: {self.summary}"]
        if not self.passed or verbose:
            for finding in self.findings:
                lines.append(f"        {finding}")
        return "\n".join(lines)


@dataclass
class Gate:
    name: str
    description: str
    run: Callable[[Store, Path], GateResult]
    blocking: bool = True


# ------------------------------------------------------------------ gates


def _gate_store_integrity(store: Store, root: Path) -> GateResult:
    findings = store.check()
    errs = store_errors(findings)
    return GateResult(
        "store-integrity",
        not errs,
        (
            f"{len(store)} records, {len(store.relations)} relations, "
            f"{len(errs)} error(s), {len(findings) - len(errs)} warning(s)"
        ),
        tuple(errs),
    )


def _gate_projection_drift(store: Store, root: Path) -> GateResult:
    from .projections import drift

    report = drift(store, root)
    errs = [f for f in report.findings if f.severity == "error"]
    return GateResult(
        "projection-drift",
        not errs,
        ("every registry agrees with the store" if not errs else f"{len(errs)} disagreement(s)"),
        tuple(report.findings),
    )


def _gate_propagation(store: Store, root: Path) -> GateResult:
    from .propagation import audit_all

    reports = audit_all(store)
    incomplete = [r for r in reports if not r.complete]
    findings = tuple(
        Finding(
            "PROP-401",
            "error",
            report.experiment_id,
            f"outstanding: {', '.join(o.obligation.value for o in report.outstanding)}",
        )
        for report in incomplete
    )
    return GateResult(
        "propagation",
        not incomplete,
        f"{len(reports) - len(incomplete)}/{len(reports)} executed experiments fully propagated",
        findings,
    )


def _gate_protocols(store: Store, root: Path) -> GateResult:
    from .protocol import freeze_path_for, lint, load, verify

    findings: list[Finding] = []
    paths = sorted(root.glob(PROTOCOL_GLOB))
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            protocol = load(path)
        except Exception as exc:  # unparseable protocol is a gate failure
            findings.append(Finding("PROTO-200", "error", relative, f"cannot load: {exc}"))
            continue
        findings.extend(lint(protocol))
        if freeze_path_for(path).exists():
            matched, message = verify(path)
            if not matched:
                findings.append(Finding("PROTO-240", "error", relative, message))
    errs = [f for f in findings if f.severity == "error"]
    return GateResult(
        "protocols",
        not errs,
        (
            f"{len(paths)} protocol(s) checked, {len(errs)} error(s)"
            if paths
            else f"no protocols found at {PROTOCOL_GLOB}"
        ),
        tuple(findings),
    )


def _gate_registration(store: Store, root: Path) -> GateResult:
    from .governance import load_registration

    registration = load_registration(root)
    missing = registration.missing()
    return GateResult(
        "registration",
        registration.active,
        (
            "registration active; runs may bear evidence"
            if registration.active
            else (
                f"{len(missing)} precondition(s) unmet — Article L-11: all work in "
                "this repository is engineering-only and produces no admissible evidence"
            )
        ),
        tuple(Finding("GOV-501", "warning", "GOVERNANCE_REGISTRY.yaml", m) for m in missing),
        blocking=False,
    )


def _gate_vocabulary(store: Store, root: Path) -> GateResult:
    findings = [f for f in store.check() if f.code in {"SKB-131", "SKB-132"}]
    return GateResult(
        "lock-vocabulary",
        not findings,
        (
            "all evidence directions and decision actions drawn from Lock E4/E5"
            if not findings
            else (
                f"{len(findings)} record(s) use terms outside Lock E4/E5; closing this "
                "requires either a constitutional change request or a Scientific Decision"
            )
        ),
        tuple(findings),
        blocking=False,
    )


GATES: tuple[Gate, ...] = (
    Gate("store-integrity", "The store is internally consistent.", _gate_store_integrity),
    Gate("projection-drift", "No projection contradicts the store.", _gate_projection_drift),
    Gate("propagation", "Every executed experiment propagated.", _gate_propagation),
    Gate("protocols", "Every protocol lints clean and matches its freeze.", _gate_protocols),
    Gate(
        "registration",
        "Governing artifacts are registered (advisory).",
        _gate_registration,
        blocking=False,
    ),
    Gate(
        "lock-vocabulary",
        "Records use Lock E4/E5 vocabularies (advisory).",
        _gate_vocabulary,
        blocking=False,
    ),
)

GATE_BY_NAME: dict[str, Gate] = {g.name: g for g in GATES}


@dataclass
class GateRun:
    results: list[GateResult] = field(default_factory=list)

    @property
    def blocked(self) -> list[GateResult]:
        return [r for r in self.results if r.blocks]

    @property
    def exit_code(self) -> int:
        return 1 if self.blocked else 0

    def render(self, verbose: bool = False) -> str:
        lines = [r.render(verbose) for r in self.results]
        if self.blocked:
            names = ", ".join(r.name for r in self.blocked)
            lines.append(f"\nBLOCKED by: {names}")
        else:
            advisory = [r for r in self.results if not r.passed]
            suffix = f" ({len(advisory)} advisory warning(s))" if advisory else ""
            lines.append(f"\nAll blocking gates pass{suffix}.")
        return "\n".join(lines)


def run_gates(store: Store, root: Path | str = ".", only: list[str] | None = None) -> GateRun:
    """Run every gate, or a named subset. Never raises for a gate failure."""
    root = Path(root)
    selected = GATES if not only else tuple(GATE_BY_NAME[n] for n in only)
    run = GateRun()
    for gate in selected:
        try:
            result = gate.run(store, root)
        except Exception as exc:  # a gate that crashes is a failing gate
            result = GateResult(
                gate.name,
                False,
                f"gate raised {type(exc).__name__}: {exc}",
                blocking=gate.blocking,
            )
        result.blocking = gate.blocking
        run.results.append(result)
    return run


__all__ = ["GATES", "GATE_BY_NAME", "Gate", "GateResult", "GateRun", "run_gates"]
