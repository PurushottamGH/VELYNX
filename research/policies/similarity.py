"""
research/policies/similarity.py
===============================

The :class:`SimilarityPolicy` — merge the two nearest clusters by centroid
distance, then commit unconditionally.

This is the strongest *un-principled* baseline and the most important contrast
for FreeEnergy: it uses the **same selection** as FreeEnergy (the nearest pair)
but skips the free-energy accept/reject test. The gap between Similarity and
FreeEnergy therefore isolates the contribution of the free-energy *gate* alone,
holding candidate selection constant.
"""

from __future__ import annotations

from typing import Any, Optional

from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    MergeProposal,
    PolicyContext,
    nearest_pair,
)


class SimilarityPolicy(ConsolidationPolicy):
    """Merge the two nearest centroids, then always commit."""

    name = "similarity"
    description = "Merge the two nearest centroids (commits unconditionally)."

    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        proposal = nearest_pair(engine)
        if proposal is None:
            return None
        # Re-tag the strategy so the audit attributes the merge to this policy
        # rather than the shared nearest-pair generator.
        return MergeProposal(
            target_a=proposal.target_a,
            target_b=proposal.target_b,
            distance=proposal.distance,
            strategy="similarity",
        )

    def accept(self, score: Any, context: PolicyContext) -> AcceptVerdict:
        return True, "similarity: commit nearest pair unconditionally"


__all__ = ["SimilarityPolicy"]
