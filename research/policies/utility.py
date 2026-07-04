"""
research/policies/utility.py
============================

The :class:`UtilityPolicy` — merge the two least-used clusters.

A usage-based eviction heuristic: the clusters that have absorbed the fewest
observations (lowest ``count``, i.e. lowest access frequency) are deemed least
useful and are fused first. It isolates the value of *utility/frequency-based*
selection, with no geometry and no free-energy signal.
"""

from __future__ import annotations

from typing import Any, Optional

from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    MergeProposal,
    PolicyContext,
    lowest_utility_pair,
)


class UtilityPolicy(ConsolidationPolicy):
    """Merge the two lowest-utility (least-accessed) clusters, then commit."""

    name = "utility"
    description = (
        "Merge the two lowest-utility clusters by access frequency "
        "(commits unconditionally)."
    )

    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        return lowest_utility_pair(engine, strategy="utility")

    def accept(self, score: Any, context: PolicyContext) -> AcceptVerdict:
        return True, "utility: commit least-used pair unconditionally"


__all__ = ["UtilityPolicy"]
