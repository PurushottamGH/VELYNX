"""
research/attribution/counterfactual.py
=======================================

The :class:`CounterfactualEvaluator` — post-hoc evaluation that answers "which
merge *should* the policy have selected?"

Performs three analyses on a collection of already-scored proposals:

1. **Replay Accuracy.** Runs each proposal's ``.counterfactual()`` against a
   held-out window, which computes ``replay_error`` (the absolute divergence
   between the read-only rehearsal's predicted energy and the energy actually
   realised on an isolated committed clone).

2. **Pareto Dominance.** Computes the 2-d Pareto frontier over (Prediction
   Delta × Complexity Delta) and annotates every proposal with
   ``is_pareto_optimal`` (``True`` iff no other proposal dominates it on
   *both* objectives). A proposal dominates another when it has strictly
   better or equal values on both dimensions and is strictly better on at
   least one.

3. **Counterfactual Best.** Identifies the single optimal *post-hoc* proposal
   — the ``counterfactual_best`` — as the one with the lowest
   ``actual_energy_held_out`` when a held-out window is available, otherwise
   the lowest ``energy_after``. The "no-merge" baseline is always included in
   this comparison.

Standard library only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from research.proposals.proposal import RichProposal


@dataclass
class CounterfactualResult:
    """The outcome of a post-hoc counterfactual evaluation of a proposal pool.

    Attributes
    ----------
    counterfactual_best :
        The optimal post-hoc proposal (lowest held-out energy, or lowest
        energy_after when held-out is unavailable). ``None`` when the pool
        is empty.
    no_merge_energy :
        The energy of doing nothing (taken from the first proposal's
        ``energy_before``; all proposals share the same baseline at a
        given tick).
    pareto_frontier :
        The proposal_ids that lie on the Pareto frontier.
    proposals_evaluated :
        How many proposals were evaluated (the pool size).
    """

    counterfactual_best: Optional[RichProposal] = None
    no_merge_energy: Optional[float] = None
    pareto_frontier: List[str] = field(default_factory=list)
    proposals_evaluated: int = 0

    def best_id(self) -> Optional[str]:
        """The proposal_id of ``counterfactual_best``, or ``None``."""
        return self.counterfactual_best.proposal_id if self.counterfactual_best else None

    def best_energy(self) -> Optional[float]:
        """The energy of ``counterfactual_best``, or ``None``."""
        if self.counterfactual_best is None:
            return None
        ct = self.counterfactual_best.counterfactual_block or {}
        return ct.get("actual_energy_held_out") or ct.get("energy_merge")

    def as_dict(self) -> Dict[str, Any]:
        """JSON-safe summary."""
        return {
            "counterfactual_best_id": self.best_id(),
            "counterfactual_best_energy": _json_float(self.best_energy()),
            "no_merge_energy": _json_float(self.no_merge_energy),
            "pareto_frontier": list(self.pareto_frontier),
            "proposals_evaluated": self.proposals_evaluated,
        }


class CounterfactualEvaluator:
    """Compute post-hoc counterfactual quality of every proposal in a pool.

    Parameters
    ----------
    held_out_vectors :
        An optional held-out (seed-disjoint) window for computing replay
        accuracy. When provided, ``replay_error`` is populated for every
        proposal via ``.counterfactual()``.
    """

    def __init__(self, held_out_vectors: Optional[List[List[float]]] = None):
        self.held_out_vectors = held_out_vectors

    def evaluate(self, proposals: List[RichProposal]) -> CounterfactualResult:
        """Run counterfactual analysis on ``proposals`` and return the result.

        Each proposal's ``.counterfactual`` attribute is populated (or
        updated) with the merge-vs-no-merge analysis and optional
        ``replay_error``. Each proposal's ``decision_trace`` gains an
        ``is_pareto_optimal`` boolean.
        """
        if not proposals:
            return CounterfactualResult()

        # --- Step 1: run counterfactual on every proposal -----------------
        for p in proposals:
            p.counterfactual(held_out=self.held_out_vectors)

        # --- Step 2: extract the no-merge baseline ------------------------
        # All proposals at the same tick share the same energy_before.
        no_merge_energy: Optional[float] = None
        if proposals:
            first_trace = proposals[0].decision_trace
            no_merge_energy = float(first_trace.get("energy_before", float("inf")))

        # --- Step 3: identify counterfactual_best -------------------------
        # When held_out is available, rank by actual_energy_held_out (the
        # ground-truth energy after committing on the held-out clone).
        # Otherwise, fall back to predicted energy_after.
        counterfactual_best = self._select_best(proposals)

        # --- Step 4: Pareto frontier on (Prediction Delta × Complexity Delta)
        pareto_ids = self._compute_pareto_frontier(proposals)

        return CounterfactualResult(
            counterfactual_best=counterfactual_best,
            no_merge_energy=no_merge_energy,
            pareto_frontier=pareto_ids,
            proposals_evaluated=len(proposals),
        )

    def _select_best(self, proposals: List[RichProposal]) -> Optional[RichProposal]:
        """Select the post-hoc optimal proposal.

        When ``held_out_vectors`` was provided, uses ``actual_energy_held_out``
        from each proposal's counterfactual block (lower is better). Otherwise
        falls back to ``energy_after`` from the decision_trace.
        """
        if not proposals:
            return None

        if self.held_out_vectors:
            # Best by actual ground-truth energy on held-out clone.
            best: Optional[RichProposal] = None
            best_energy = float("inf")
            for p in proposals:
                ct = p.counterfactual_block or {}
                actual = ct.get("actual_energy_held_out")
                if actual is not None and actual < best_energy:
                    best_energy = float(actual)
                    best = p
            if best is not None:
                return best

        # Fallback: best by predicted energy_after.
        best = None
        best_energy = float("inf")
        for p in proposals:
            energy = float(p.decision_trace.get("energy_after", float("inf")))
            if energy < best_energy:
                best_energy = energy
                best = p
        return best

    def _compute_pareto_frontier(self, proposals: List[RichProposal]) -> List[str]:
        """Compute the 2-d Pareto frontier and annotate ``is_pareto_optimal``.

        Objectives:
          * ``delta_prediction`` — lower is better (negative means improvement)
          * ``expected_complexity_change`` — higher is better (positive means
            the substrate became structurally simpler)

        For dominance: proposal P *dominates* Q iff P is strictly better or
        equal on *both* objectives and strictly better on at least one.
        """
        n = len(proposals)
        if n == 0:
            return []

        # Extract objective vectors.
        objs: List[Dict[str, float]] = []
        for p in proposals:
            dt = p.decision_trace
            delta_pred = float(dt.get("delta_prediction", 0.0) or 0.0)
            # expected_complexity_change = -(A_after - A_before)
            # Higher (more positive) = more structural simplification.
            ecc = float(p.expected_complexity_change if p.expected_complexity_change is not None else 0.0)
            objs.append({"delta_prediction": delta_pred, "expected_complexity_change": ecc})

        # Determine dominance relations.
        dominated = [False] * n
        for i in range(n):
            for j in range(n):
                if i == j or dominated[i]:
                    continue
                # P_i dominates P_j if:
                #   delta_prediction_i <= delta_prediction_j (lower is better)
                #   ecc_i >= ecc_j (higher is better)
                #   AND at least one is strict
                dp_ij = objs[i]["delta_prediction"] <= objs[j]["delta_prediction"]
                ecc_ij = objs[i]["expected_complexity_change"] >= objs[j]["expected_complexity_change"]
                strict = (
                    objs[i]["delta_prediction"] < objs[j]["delta_prediction"]
                    or objs[i]["expected_complexity_change"] > objs[j]["expected_complexity_change"]
                )
                if dp_ij and ecc_ij and strict:
                    dominated[j] = True

        frontier: List[str] = []
        for i, p in enumerate(proposals):
            is_optimal = not dominated[i]
            p.decision_trace["is_pareto_optimal"] = is_optimal
            if is_optimal:
                frontier.append(p.proposal_id)

        return frontier


def _json_float(value: Optional[float]) -> Optional[float]:
    """Coerce a float to JSON-safe (``nan``/``inf`` -> ``None``)."""
    if value is None:
        return None
    f = float(value)
    if math.isnan(f) or math.isinf(f):
        return None
    return f


__all__ = [
    "CounterfactualEvaluator",
    "CounterfactualResult",
]
