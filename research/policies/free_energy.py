"""
research/policies/free_energy.py
================================

The :class:`FreeEnergyPolicy` — a **thin adapter** over the frozen C8
:class:`~backend.cognition.decision_policy.DecisionPolicy`.

This policy adds *zero* behavioural change to the production free-energy logic.
It only re-expresses the existing two-stage C8 pipeline behind the unified
:class:`~research.policies.base.ConsolidationPolicy` contract so it can be swept
against the heuristics on equal footing:

* **Selection** — the nearest centroid pair, via the unchanged
  :class:`~backend.cognition.candidate_generator.CandidateGenerator` (the exact
  candidate the production runner feeds the replay engine).
* **Acceptance** — delegated verbatim to a wrapped, unmodified
  :class:`DecisionPolicy` (default ``"free_energy"`` strategy). The merge is
  committed iff total cognitive energy does not increase.

Because the verdict is produced by the frozen policy object itself, this adapter
cannot drift from production behaviour: any change would have to happen inside
``decision_policy.py``, which Sprint R1 forbids touching.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.cognition.decision_policy import (
    STRATEGY_FREE_ENERGY,
    DecisionPolicy,
    DecisionScore,
)
from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    MergeProposal,
    PolicyContext,
    nearest_pair,
)


class FreeEnergyPolicy(ConsolidationPolicy):
    """Adapter exposing the frozen C8 DecisionPolicy as a ConsolidationPolicy.

    Parameters (all optional, forwarded to the wrapped DecisionPolicy)
    -----------------------------------------------------------------
    strategy : str
        ``"free_energy"`` (default) or ``"pareto"`` — the frozen policy's own
        selection strategies. Kept configurable because both already exist in
        the unchanged module; neither is a behavioural modification.
    lam, mu, nu : float
        Energy coupling coefficients. Default to the module's ``(1.0, 2.0, 0.5)``.
    tolerance : float
        Free-energy slack; defaults to the module default ``0.0``.
    """

    name = "free_energy"
    description = (
        "VELYNX C8 Free-Energy Minimization: merge nearest pair, accept iff "
        "total cognitive energy does not increase (wraps the frozen "
        "DecisionPolicy unchanged)."
    )

    def __init__(
        self,
        strategy: str = STRATEGY_FREE_ENERGY,
        lam: float = 1.0,
        mu: float = 2.0,
        nu: float = 0.5,
        tolerance: float = 0.0,
    ) -> None:
        super().__init__(
            strategy=strategy, lam=lam, mu=mu, nu=nu, tolerance=tolerance
        )
        # The wrapped, UNMODIFIED production policy. All judgement is delegated
        # to this object; this class adds no decision logic of its own.
        self._policy = DecisionPolicy(
            strategy=strategy, lam=lam, mu=mu, nu=nu, tolerance=tolerance
        )

    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        # Identical selection to the production runner: the nearest centroid
        # pair. Re-tagged so the audit attributes the merge to this policy.
        proposal = nearest_pair(engine)
        if proposal is None:
            return None
        return MergeProposal(
            target_a=proposal.target_a,
            target_b=proposal.target_b,
            distance=proposal.distance,
            strategy="free_energy",
        )

    def accept(self, score: DecisionScore, context: PolicyContext) -> AcceptVerdict:
        # Verdict produced verbatim by the frozen DecisionPolicy.
        verdict = self._policy.evaluate_metrics(
            score.metrics_before, score.metrics_after
        )
        return bool(verdict["accepted"]), str(verdict["reason"])

    def describe(self) -> Dict[str, Any]:
        info = super().describe()
        # Surface the resolved coefficients explicitly for the policy.json
        # artifact, so a reader can reproduce the exact energy function.
        info["energy"] = {
            "strategy": self._policy.strategy,
            "lambda": self._policy.lam,
            "mu": self._policy.mu,
            "nu": self._policy.nu,
            "tolerance": self._policy.tolerance,
            "formula": "E = lambda*H + mu*S + nu*A",
        }
        return info


__all__ = ["FreeEnergyPolicy"]
