"""
research/policies/random_policy.py
==================================

The :class:`RandomPolicy` — merge two clusters chosen uniformly at random.

A *lower bound on intelligence*: it consolidates exactly as often as the
scheduler fires, but with zero insight into which clusters ought to be fused.
If a principled policy cannot beat random merging, it is adding no value.
"""

from __future__ import annotations

from typing import Any, Optional

from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    MergeProposal,
    PolicyContext,
    random_pair,
)


class RandomPolicy(ConsolidationPolicy):
    """Merge two uniformly-random distinct clusters, then always commit."""

    name = "random"
    description = "Merge two uniformly-random clusters (commits unconditionally)."

    @property
    def is_deterministic(self) -> bool:
        # Selection consumes the context RNG, so the *pair chosen* depends on the
        # seed (over and above the seed's effect on the world). Reported honestly
        # so artifacts flag this as the one stochastic-selection policy.
        return False

    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        return random_pair(engine, context.rng, strategy="random")

    def accept(self, score: Any, context: PolicyContext) -> AcceptVerdict:
        # Random consolidation is unconditional: having picked a pair, it fuses
        # it regardless of the measured effect. The replay measurement is still
        # recorded by the runner for comparability, but it does not gate here.
        return True, "random: commit unconditionally"


__all__ = ["RandomPolicy"]
