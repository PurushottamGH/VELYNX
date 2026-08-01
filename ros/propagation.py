"""P1 Research Operating System — the propagation transaction (invariant K1).

``SCIENTIFIC_INDEX.md`` closes with a rule that is currently enforced by memory:

    Every completed experiment must add or update: execution validity;
    observations; evidence relations; interpretation and alternatives; a
    Scientific Decision; dependent hypothesis/mechanism status; assumptions,
    unknowns, and debt; roadmap priority; Living Scientific Model.
    **No result is complete until this propagation occurs.**

Nine obligations, discharged by hand, across ten registries, with no instrument
checking. That is the highest-probability failure in the laboratory: not a wrong
result, but a right result that never reached the record, leaving the next
decision to be taken against a stale state.

This module makes propagation a transaction. It is satisfied completely or the
experiment is not complete, and the report names exactly which obligation is
outstanding and where to discharge it.

Read-only: it audits the store, it does not write it. Writing obligation 5 (the
Scientific Decision) is an evidence-bearing act reserved to humans by
:mod:`ros.authority`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .store import Record, Store


class Obligation(str, Enum):
    """The nine propagation obligations, in the order the rule states them."""

    EXECUTION_VALIDITY = "execution_validity"
    OBSERVATIONS = "observations"
    EVIDENCE_RELATIONS = "evidence_relations"
    INTERPRETATION = "interpretation_and_alternatives"
    DECISION = "scientific_decision"
    DEPENDENT_STATUS = "dependent_status"
    ASSUMPTIONS_UNKNOWNS_DEBT = "assumptions_unknowns_debt"
    ROADMAP = "roadmap_priority"
    LIVING_MODEL = "living_scientific_model"


#: Where each obligation is discharged, for the message an engineer reads.
DISCHARGE_SITE: dict[Obligation, str] = {
    Obligation.EXECUTION_VALIDITY: "experiment record: validity / invalidity_reason",
    Obligation.OBSERVATIONS: "observations collection, referenced by the experiment",
    Obligation.EVIDENCE_RELATIONS: "evidence collection, with direction and target",
    Obligation.INTERPRETATION: "evidence.rationale or an interpretation record",
    Obligation.DECISION: "decisions collection (human write: skb.decision)",
    Obligation.DEPENDENT_STATUS: "status of every hypothesis and mechanism the experiment names",
    Obligation.ASSUMPTIONS_UNKNOWNS_DEBT: "assumptions / unknowns / scientific_debt collections",
    Obligation.ROADMAP: "science/09_RESEARCH_ROADMAP_24_MONTHS.md priority for the next step",
    Obligation.LIVING_MODEL: "science/11_LIVING_SCIENTIFIC_MODEL.md synthesis",
}


@dataclass(frozen=True)
class ObligationResult:
    obligation: Obligation
    satisfied: bool
    detail: str

    def __str__(self) -> str:  # pragma: no cover - display only
        mark = "ok  " if self.satisfied else "MISS"
        return f"{mark} {self.obligation.value}: {self.detail}"


#: Experiment statuses for which propagation is *not yet* due. An experiment that
#: has never executed cannot have propagated its results, and reporting that as a
#: defect would make the instrument fire on a known negative — which Lock E2
#: names as disqualifying for a measurement.
NOT_YET_EXECUTED: frozenset[str] = frozenset(
    {"designed", "proposed", "blocked_confirmatory", "blocked", "planned", "retired"}
)


@dataclass(frozen=True)
class PropagationReport:
    """The result of auditing one experiment's propagation."""

    experiment_id: str
    results: tuple[ObligationResult, ...]
    #: False when the experiment has not executed, so no obligation is yet due.
    due: bool = True
    status: str = ""

    @property
    def complete(self) -> bool:
        return all(r.satisfied for r in self.results)

    @property
    def outstanding(self) -> tuple[ObligationResult, ...]:
        """Obligations that are unsatisfied *and* due."""
        if not self.due:
            return ()
        return tuple(r for r in self.results if not r.satisfied)

    def render(self) -> str:
        if not self.due:
            return (
                f"{self.experiment_id}: NOT DUE (status {self.status!r}; "
                "no execution, so no propagation is owed)"
            )
        header = (
            f"{self.experiment_id}: "
            f"{'COMPLETE' if self.complete else f'{len(self.outstanding)} obligation(s) outstanding'}"
        )
        lines = [header]
        for result in self.results:
            lines.append(f"  {result}")
            if not result.satisfied:
                lines.append(f"       discharge at: {DISCHARGE_SITE[result.obligation]}")
        return "\n".join(lines)


def _referenced_ids(record: Record, prefix: str) -> list[str]:
    return sorted({i for _, i in record.references() if i.startswith(prefix)})


def _decisions_touching(store: Store, experiment_id: str, related: set[str]) -> list[Record]:
    hits = []
    for decision in store.by_collection("decisions"):
        cited = {i for _, i in decision.references()}
        if experiment_id in cited or cited & related:
            hits.append(decision)
    return hits


def audit(store: Store, experiment_id: str) -> PropagationReport:
    """Audit one experiment against the nine obligations."""
    experiment = store.get(experiment_id)
    if experiment is None or experiment.collection.key != "experiments":
        raise KeyError(f"{experiment_id} is not an experiment in the store")

    observations = _referenced_ids(experiment, "OBS-")
    evidence_ids = _referenced_ids(experiment, "EVD-")
    hypotheses = _referenced_ids(experiment, "HYP-")
    related = set(observations) | set(evidence_ids) | set(hypotheses)

    checks: list[tuple[Obligation, Callable[[], tuple[bool, str]]]] = [
        (
            Obligation.EXECUTION_VALIDITY,
            lambda: (
                bool(experiment.data.get("validity")),
                str(experiment.data.get("validity") or "no validity field"),
            ),
        ),
        (
            Obligation.OBSERVATIONS,
            lambda: (
                bool(observations),
                f"{len(observations)} observation(s): {', '.join(observations) or 'none'}",
            ),
        ),
        (
            Obligation.EVIDENCE_RELATIONS,
            lambda: (
                bool(evidence_ids),
                f"{len(evidence_ids)} evidence record(s): {', '.join(evidence_ids) or 'none'}",
            ),
        ),
        (Obligation.INTERPRETATION, lambda: _check_interpretation(store, evidence_ids)),
        (
            Obligation.DECISION,
            lambda: _summarise(
                _decisions_touching(store, experiment_id, related),
                "decision",
                "no decision cites this experiment or anything it references",
            ),
        ),
        (Obligation.DEPENDENT_STATUS, lambda: _check_dependent_status(store, hypotheses)),
        (
            Obligation.ASSUMPTIONS_UNKNOWNS_DEBT,
            lambda: _check_debt_linkage(store, experiment_id, related),
        ),
        (Obligation.ROADMAP, lambda: _check_next_step(experiment)),
        (Obligation.LIVING_MODEL, lambda: _check_living_model(store, experiment_id)),
    ]

    results = []
    for obligation, check in checks:
        satisfied, detail = check()
        results.append(ObligationResult(obligation, satisfied, detail))

    status = str(experiment.data.get("status") or "")
    executed = bool(experiment.data.get("executions")) or (
        status.strip().lower() not in NOT_YET_EXECUTED
    )
    return PropagationReport(experiment_id, tuple(results), due=executed, status=status)


def _summarise(records: list[Record], noun: str, absent: str) -> tuple[bool, str]:
    if not records:
        return False, absent
    ids = ", ".join(r.identifier for r in records)
    return True, f"{len(records)} {noun}(s): {ids}"


def _check_interpretation(store: Store, evidence_ids: list[str]) -> tuple[bool, str]:
    if not evidence_ids:
        return False, "no evidence to interpret"
    missing = [
        eid
        for eid in evidence_ids
        if not (store.get(eid) and store.get(eid).data.get("rationale"))  # type: ignore[union-attr]
    ]
    if missing:
        return False, f"evidence without a recorded interpretation: {', '.join(missing)}"
    return True, f"all {len(evidence_ids)} evidence record(s) carry a rationale"


def _check_dependent_status(store: Store, hypotheses: list[str]) -> tuple[bool, str]:
    if not hypotheses:
        return False, "experiment names no hypothesis; nothing could have been updated"
    unstated = [h for h in hypotheses if not (store.get(h) and store.get(h).status)]  # type: ignore[union-attr]
    if unstated:
        return False, f"hypotheses without a status: {', '.join(unstated)}"
    statuses = ", ".join(f"{h}={store.get(h).status}" for h in hypotheses)  # type: ignore[union-attr]
    return True, statuses


def _check_debt_linkage(store: Store, experiment_id: str, related: set[str]) -> tuple[bool, str]:
    touched = []
    for key in ("assumptions", "unknowns", "scientific_debt"):
        for record in store.by_collection(key):
            cited = {i for _, i in record.references()}
            if experiment_id in cited or cited & related:
                touched.append(record.identifier)
    if not touched:
        return False, "no assumption, unknown or debt record links to this experiment"
    return True, f"{len(touched)} linked: {', '.join(sorted(touched))}"


def _check_next_step(experiment: Record) -> tuple[bool, str]:
    for field_name in (
        "limitations",
        "execution_gate",
        "unavailable_primary_metrics",
        "invalidity_reason",
    ):
        value = experiment.data.get(field_name)
        if value:
            return True, f"forward priority recorded via {field_name!r}"
    return False, "no limitation, gate or follow-up recorded to prioritise the next step"


def _check_living_model(store: Store, experiment_id: str) -> tuple[bool, str]:
    """The Living Scientific Model is a projection; propagation into it is
    satisfied when the store carries what the projection renders from."""
    for relation in store.relations:
        if experiment_id in (relation.source, relation.target):
            return True, f"linked in the evidence graph via relation {relation.kind!r}"
    return False, "experiment appears in no typed relation, so no projection can render it"


def audit_all(store: Store, include_not_due: bool = False) -> list[PropagationReport]:
    """Audit every experiment in the store, most incomplete first.

    By default only experiments whose propagation is *due* are returned, so the
    report counts real outstanding work rather than experiments that have simply
    not run yet.
    """
    reports = [audit(store, r.identifier) for r in store.by_collection("experiments")]
    if not include_not_due:
        reports = [r for r in reports if r.due]
    return sorted(reports, key=lambda r: (-len(r.outstanding), r.experiment_id))


__all__ = [
    "DISCHARGE_SITE",
    "Obligation",
    "ObligationResult",
    "PropagationReport",
    "audit",
    "audit_all",
]
