"""P1 Research Operating System — laboratory metrics.

Every metric here is computed from the store, never entered by hand. That is a
deliberate constraint: a KPI a human types is a claim about the laboratory with
no manifest behind it, and this laboratory does not accept those.

The metric set answers one question — *is uncertainty being reduced per unit of
effort?* — and deliberately excludes the numbers a research organisation
normally reaches for. There is no document count, no lines-of-code, no commit
rate, no "experiments run". Those measure motion. Under Article L-9 a deletion is
a scientific success, so a metric that rewards accumulation would reward the
wrong behaviour: ``uncertainty_resolution`` counts *closed* unknowns, and
``negative_result_preservation`` counts results that could have been quietly
dropped and were not.

Two metrics have no target because they are capacity, not performance:
``admissible_capacity`` is 0 or 1 and gates all the others.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .admissibility import ClaimScope, Manifest, Registration, Determinism, assess
from .model import DECISION_ACTIONS, EVIDENCE_DIRECTIONS, conforms
from .store import Store, errors as store_errors

#: Statuses meaning an unknown or a debt item is no longer open.
_CLOSED = frozenset({"resolved", "closed", "retired", "discharged", "paid", "superseded"})

#: Hypothesis statuses meaning the hypothesis is currently exposed to refutation,
#: drawn from the seven in ``SCIENTIFIC_OPERATING_SYSTEM.md`` section 5. Proposed
#: is excluded because nothing is testing it yet; Validated, Rejected, Superseded
#: and Archived are excluded because they are settled.
_UNDER_TEST = frozenset({"exploratory", "under validation"})


@dataclass(frozen=True)
class Metric:
    """One computed indicator.

    ``healthy`` is deliberately tri-state: ``None`` means the metric has no
    target and is reported for interpretation rather than judged.
    """

    key: str
    name: str
    value: float
    rendered: str
    interpretation: str
    target: str = ""
    healthy: bool | None = None

    def __str__(self) -> str:  # pragma: no cover - display only
        mark = {True: "ok  ", False: "WARN", None: "--  "}[self.healthy]
        suffix = f"  (target {self.target})" if self.target else ""
        return f"{mark} {self.name}: {self.rendered}{suffix}"


def _ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def _pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a (0 eligible)"
    return f"{numerator}/{denominator} ({100.0 * numerator / denominator:.0f}%)"


def _status_of(record: Any) -> str:
    return str(getattr(record, "status", "") or "").strip().lower()


def compute(store: Store, registration: Registration) -> list[Metric]:
    """Compute the full metric set. Pure with respect to the filesystem."""
    from .propagation import audit_all

    metrics: list[Metric] = []

    # --- capacity ------------------------------------------------------
    # The best manifest the laboratory could possibly produce today. If even
    # this is inadmissible, the constraint is governance, not engineering.
    best_possible = Manifest(
        run_id="hypothetical-perfect-run",
        determinism=Determinism.D0,
        clean_checkout=True,
        complete=True,
        protocol_frozen_before_first_run=True,
        protocol_hash_matched=True,
        coverage_disclosed=True,
        stream_complete_for_scope=True,
    )
    verdict = assess(best_possible, registration, ClaimScope.OBJECT)
    metrics.append(
        Metric(
            key="admissible_capacity",
            name="Admissible evidence capacity",
            value=1.0 if verdict.admissible else 0.0,
            rendered=("yes" if verdict.admissible else f"no — ceiling {verdict.tier.value}"),
            interpretation=(
                "Whether a flawless run today could bear admissible evidence. "
                "When this is 'no', confirmatory compute is wasted and the "
                "binding constraint is registration, not engineering."
            ),
            healthy=verdict.admissible,
        )
    )

    # --- uncertainty reduction ----------------------------------------
    unknowns = store.by_collection("unknowns")
    closed_unknowns = [u for u in unknowns if _status_of(u) in _CLOSED]
    metrics.append(
        Metric(
            key="uncertainty_resolution",
            name="Unknowns resolved",
            value=_ratio(len(closed_unknowns), len(unknowns)),
            rendered=_pct(len(closed_unknowns), len(unknowns)),
            interpretation=(
                "The primary output of a research laboratory. Rises when an "
                "unknown is closed by evidence, including by being shown "
                "unanswerable."
            ),
            target="monotonically rising",
        )
    )

    hypotheses = store.by_collection("hypotheses")
    under_test = [h for h in hypotheses if _status_of(h) in _UNDER_TEST]
    metrics.append(
        Metric(
            key="hypotheses_under_test",
            name="Hypotheses exposed to refutation",
            value=float(len(under_test)),
            rendered=f"{len(under_test)} of {len(hypotheses)}",
            interpretation=(
                "A hypothesis nobody is trying to break is not being "
                "investigated. Counts only statuses that admit refutation."
            ),
            target="≥ 1",
            healthy=len(under_test) >= 1,
        )
    )

    # --- falsifier coverage (invariant K3) -----------------------------
    experiments = store.by_collection("experiments")
    tested = set()
    for experiment in experiments:
        tested.update(i for _, i in experiment.references() if i.startswith("HYP-"))
    covered = [h for h in hypotheses if h.identifier in tested]
    metrics.append(
        Metric(
            key="falsifier_coverage",
            name="Hypotheses with a designed falsifier",
            value=_ratio(len(covered), len(hypotheses)),
            rendered=_pct(len(covered), len(hypotheses)),
            interpretation=(
                "Invariant K3: the falsifier ships before the mechanism. A "
                "hypothesis with no experiment naming it is an opinion."
            ),
            target="100%",
            healthy=len(covered) == len(hypotheses),
        )
    )

    # --- propagation completeness -------------------------------------
    reports = audit_all(store)
    complete = [r for r in reports if r.complete]
    metrics.append(
        Metric(
            key="propagation_completeness",
            name="Propagation complete",
            value=_ratio(len(complete), len(reports)),
            rendered=_pct(len(complete), len(reports)),
            interpretation=(
                "Of experiments that have executed, the share whose nine "
                "propagation obligations are all discharged. A right result "
                "that never reached the record is a wrong state."
            ),
            target="100%",
            healthy=len(complete) == len(reports),
        )
    )

    # --- negative-result preservation (Article L-3) --------------------
    negatives = store.by_collection("negative_results")
    invalid = [
        e
        for e in experiments
        if e.data.get("invalidity_reason") or _status_of(e).startswith("invalid")
    ]
    preserved = len(negatives) + len(invalid)
    metrics.append(
        Metric(
            key="negative_result_preservation",
            name="Negative results preserved",
            value=float(preserved),
            rendered=(f"{len(negatives)} negative record(s), {len(invalid)} invalid execution(s)"),
            interpretation=(
                "Article L-3: loss is legal, silence is not. Counts results "
                "that could have been quietly dropped and were kept. Zero in a "
                "laboratory that has run experiments is a reporting failure, "
                "not a run of good luck."
            ),
            target="> 0 once experiments have executed",
            healthy=None if not reports else preserved > 0,
        )
    )

    # --- decision throughput ------------------------------------------
    decisions = store.by_collection("decisions")
    metrics.append(
        Metric(
            key="decision_density",
            name="Decisions per executed experiment",
            value=_ratio(len(decisions), len(reports)),
            rendered=(
                f"{len(decisions)} decision(s) / {len(reports)} executed = "
                f"{_ratio(len(decisions), len(reports)):.2f}"
            ),
            interpretation=(
                "The unit of research output is a decision, not an experiment. "
                "A falling ratio means runs are accumulating without changing "
                "what the laboratory believes."
            ),
            target="≥ 1.0",
            healthy=None if not reports else _ratio(len(decisions), len(reports)) >= 1.0,
        )
    )

    # --- open scientific debt -----------------------------------------
    debt = store.by_collection("scientific_debt")
    open_debt = [d for d in debt if _status_of(d) not in _CLOSED]
    metrics.append(
        Metric(
            key="open_scientific_debt",
            name="Open scientific debt",
            value=float(len(open_debt)),
            rendered=f"{len(open_debt)} open of {len(debt)}",
            interpretation=(
                "Known-unsound foundations carried forward deliberately. "
                "Healthy at low non-zero: zero usually means debt is being "
                "incurred without being recorded."
            ),
            target="bounded and declining",
        )
    )

    # --- vocabulary conformance ---------------------------------------
    evidence = store.by_collection("evidence")
    off_vocab_evidence = [
        e for e in evidence if not conforms(e.data.get("direction"), EVIDENCE_DIRECTIONS)
    ]
    off_vocab_decisions = [
        d for d in decisions if not conforms(d.data.get("action"), DECISION_ACTIONS)
    ]
    off = len(off_vocab_evidence) + len(off_vocab_decisions)
    total_typed = len(evidence) + len(decisions)
    metrics.append(
        Metric(
            key="vocabulary_conformance",
            name="Lock vocabulary conformance",
            value=_ratio(total_typed - off, total_typed),
            rendered=_pct(total_typed - off, total_typed),
            interpretation=(
                "Share of evidence directions and decision actions drawn from "
                "the Lock E4/E5 vocabularies. Below 100% the records cannot be "
                "aggregated mechanically, and closing the gap is a "
                "constitutional question, not a cleanup task."
            ),
            target="100%",
            healthy=off == 0,
        )
    )

    # --- store integrity ----------------------------------------------
    errors = store_errors(store.check())
    metrics.append(
        Metric(
            key="store_integrity",
            name="Store integrity errors",
            value=float(len(errors)),
            rendered=("clean" if not errors else f"{len(errors)} error(s)"),
            interpretation=(
                "Dangling references, duplicate identifiers, broken "
                "supersession lineage. Must be zero; the store is the only "
                "source of truth and an inconsistent one is worse than none."
            ),
            target="0",
            healthy=not errors,
        )
    )

    return metrics


def failing(metrics: list[Metric]) -> list[Metric]:
    """Metrics with a target that are not meeting it."""
    return [m for m in metrics if m.healthy is False]


def render(metrics: list[Metric]) -> str:
    return "\n".join(str(m) for m in metrics)


__all__ = ["Metric", "compute", "failing", "render"]
