"""
research/attribution/evaluator.py
==================================

The :class:`CounterfactualMergeEvaluator` — the R3 "market" that scores and
ranks every proposal in a :class:`~research.proposals.pool.ProposalPool`,
selects a winner, and decorates every :class:`~research.proposals.proposal.RichProposal`
with its full ranking metadata.

Replaces the ``market.py`` placeholder from the original spec.

Design
------
The evaluator performs three steps for every consolidation window:

1. **Score every proposal.** Each :class:`RichProposal` is scored via its
   ``.score()`` method (free-energy verdict). This populates
   ``decision_trace`` with energy_before, energy_after, acceptance, etc.

2. **Rank.** Proposals are sorted ascending by ``energy_after`` (lower
   free-energy is better). The full ranking is annotated into each proposal's
   ``decision_trace`` with ``rank`` (1-based) and ``margin`` (distance to the
   next-best energy_after, or ``inf`` for the last).

3. **Select.** The winning proposal is ``argmin energy_after`` among *accepted*
   proposals only (the R3 selection rule). If no proposal is accepted, no
   winner is returned.

Standard library only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from research.proposals.pool import ProposalPool
from research.proposals.proposal import RichProposal


@dataclass
class EvaluatorResult:
    """The output of one evaluation pass over a proposal pool.

    Attributes
    ----------
    winner :
        The selected proposal (``argmin energy_after`` among accepted), or
        ``None`` if no proposal was accepted.
    rankings :
        Every proposal with its ``decision_trace`` annotated with ``rank`` and
        ``margin``, sorted best-to-worst (ascending energy_after).
    pool_diversity :
        The pool's diversity report at evaluation time.
    accepted_count :
        How many proposals were accepted by the free-energy gate.
    total_scored :
        How many proposals were scored in total.
    """

    winner: Optional[RichProposal] = None
    rankings: List[RichProposal] = field(default_factory=list)
    pool_diversity: Dict[str, Any] = field(default_factory=dict)
    accepted_count: int = 0
    total_scored: int = 0

    def winner_id(self) -> Optional[str]:
        """The proposal_id of the winner, or ``None``."""
        return self.winner.proposal_id if self.winner else None

    def as_dict(self) -> Dict[str, Any]:
        """JSON-safe summary with all recovered fields."""
        return {
            "winner_id": self.winner_id(),
            "total_scored": self.total_scored,
            "accepted_count": self.accepted_count,
            "pool_diversity": self.pool_diversity,
            "rankings": [
                {
                    # Original fields
                    "rank": r.get("rank"),
                    "proposal_id": r.get("proposal_id"),
                    "energy_after": r.get("energy_after"),
                    "accepted": r.get("accepted"),
                    "margin": r.get("margin"),
                    # Recovered from decision_trace (already computed by policy)
                    "energy_before": r.get("energy_before"),
                    "delta_energy": r.get("delta_energy"),
                    "delta_prediction": r.get("delta_prediction"),
                    "delta_entropy": r.get("delta_entropy"),
                    "delta_load": r.get("delta_load"),
                    "expected_complexity_change": r.get("expected_complexity_change"),
                    # Recovered from replay_metrics (already computed by engine)
                    "prediction_before": _extract_metric(p.replay_metrics, "metrics_before", "prediction_error"),
                    "prediction_after": _extract_metric(p.replay_metrics, "metrics_after", "prediction_error"),
                    "entropy_before": _extract_metric(p.replay_metrics, "metrics_before", "entropy"),
                    "entropy_after": _extract_metric(p.replay_metrics, "metrics_after", "entropy"),
                    "load_before": _extract_metric(p.replay_metrics, "metrics_before", "active_load"),
                    "load_after": _extract_metric(p.replay_metrics, "metrics_after", "active_load"),
                }
                for p in self.rankings
                for r in [p.decision_trace]
            ],
        }


class CounterfactualMergeEvaluator:
    """Score, rank and select the best proposal from a pool.

    Parameters
    ----------
    free_energy_weights :
        The ``{"lam", "mu", "nu"}`` coefficients for the free-energy scorer.
        Passed through to each proposal's ``.score()`` via the context.
    """

    def __init__(self, free_energy_weights: Optional[Dict[str, float]] = None):
        self.weights = free_energy_weights or {"lam": 1.0, "mu": 2.0, "nu": 0.5}

    def evaluate(self, pool: ProposalPool) -> EvaluatorResult:
        """Score every proposal in ``pool``, rank them, and select a winner.

        Returns an :class:`EvaluatorResult` with the winner and the full ranked
        listing. Each proposal's ``decision_trace`` is enriched with ``rank``
        and ``margin`` fields.
        """
        if pool.is_empty():
            return EvaluatorResult(
                pool_diversity=pool.diversity_report(),
            )

        proposals = pool.proposals

        # --- Step 1: score every proposal via free-energy verdict ----------
        scored: List[RichProposal] = []
        for p in proposals:
            try:
                p.score()
            except ValueError:
                # Proposal has no context and none was passed — cannot score.
                # This shouldn't happen in normal operation (pool always has
                # context-ful proposals), but guard anyway.
                continue
            scored.append(p)

        # --- Step 2: rank by energy_after ascending -----------------------
        # Stable sort so deterministic ordering for equal energies.
        scored.sort(key=lambda p: float(p.decision_trace.get("energy_after", float("inf"))))

        # Annotate every proposal with rank and margin.
        for i, p in enumerate(scored):
            rank = i + 1
            energy = float(p.decision_trace.get("energy_after", float("inf")))
            # margin = distance to the next-best (higher energy_after)
            if i < len(scored) - 1:
                next_energy = float(scored[i + 1].decision_trace.get("energy_after", float("inf")))
                margin = next_energy - energy
            else:
                margin = float("inf")

            p.decision_trace["rank"] = rank
            p.decision_trace["margin"] = _json_float(margin)
            p.decision_trace["energy_score"] = energy

        # --- Step 3: select winner (argmin energy_after among accepted) ---
        accepted = [p for p in scored if p.decision_trace.get("accepted", False)]
        accepted_count = len(accepted)
        winner: Optional[RichProposal] = None
        if accepted:
            # Already sorted ascending by energy_after, so first accepted is
            # the argmin among accepted.
            winner = accepted[0]

        return EvaluatorResult(
            winner=winner,
            rankings=scored,
            pool_diversity=pool.diversity_report(),
            accepted_count=accepted_count,
            total_scored=len(scored),
        )


def _json_float(value: float) -> Optional[float]:
    """Coerce a float to JSON-safe (``nan``/``inf`` -> ``None``)."""
    if math.isnan(value) or math.isinf(value):
        return None
    return float(value)


def _extract_metric(
    replay_metrics: Optional[Dict[str, Any]], phase: str, key: str
) -> Optional[float]:
    """Extract a single vital from the replay_metrics structure.

    Parameters
    ----------
    replay_metrics :
        The ``RichProposal.replay_metrics`` dict, e.g.
        ``{"metrics_before": {...}, "metrics_after": {...}}``.
    phase :
        ``"metrics_before"`` or ``"metrics_after"``.
    key :
        The vital key, e.g. ``"prediction_error"``, ``"entropy"``,
        ``"active_load"``.

    Returns
    -------
    float or None
        The metric value, or ``None`` if the structure is absent or
        incomplete.  Only returns ``None`` when data is missing; the
        metric itself may be zero.
    """
    if replay_metrics is None:
        return None
    snapshot = replay_metrics.get(phase)
    if snapshot is None:
        return None
    value = snapshot.get(key)
    if value is None:
        return None
    return float(value)


__all__ = [
    "CounterfactualMergeEvaluator",
    "EvaluatorResult",
]
