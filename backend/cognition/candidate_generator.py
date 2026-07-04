"""
backend/cognition/candidate_generator.py
=========================================

C8.1 — The Candidate Generator.

A standalone, **purely functional** component that inspects the current state
of cluster memory and proposes a restructuring when a sleep cycle is triggered
(see :class:`~backend.cognition.memory_scheduler.MemoryScheduler`).

This module *only proposes*. It never mutates the ``ClusterEngine`` or any
cluster -- the actual merge is applied by a later stage. Keeping proposal and
mutation separate means a proposal can be inspected, logged, or vetoed before
anything in memory changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from backend.cognition.vector_prediction_core import euclidean_distance


@dataclass(frozen=True)
class MergeProposal:
    """A non-binding proposal to merge the two closest clusters.

    Frozen so a generated proposal cannot be accidentally mutated between
    being produced and being applied.
    """

    target_a: int
    target_b: int
    distance: float
    strategy: str = "merge"

    def as_dict(self) -> dict:
        """Render as the plain ``{"strategy", "target_a", ...}`` mapping."""
        return {
            "strategy": self.strategy,
            "target_a": self.target_a,
            "target_b": self.target_b,
            "distance": self.distance,
        }


class CandidateGenerator:
    """Generate non-destructive memory-restructuring proposals."""

    def generate_merge_proposal(
        self, cluster_engine: Any
    ) -> Optional[MergeProposal]:
        """Propose merging the two closest clusters by centroid distance.

        Scans every pair of active cluster centroids, finds the pair with the
        minimum pairwise Euclidean distance, and returns a :class:`MergeProposal`
        describing it. Returns ``None`` when there are fewer than two clusters
        (nothing to merge).

        The ``cluster_engine`` is treated as read-only: this method inspects
        ``cluster_engine.clusters`` but never modifies it.
        """
        clusters = list(cluster_engine.clusters)
        if len(clusters) < 2:
            return None

        best_a: Optional[int] = None
        best_b: Optional[int] = None
        min_distance = float("inf")

        # Pairwise scan over the upper triangle (each unordered pair once).
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                distance = euclidean_distance(
                    clusters[i].centroid, clusters[j].centroid
                )
                if distance < min_distance:
                    min_distance = distance
                    best_a = clusters[i].id
                    best_b = clusters[j].id

        return MergeProposal(
            target_a=best_a,
            target_b=best_b,
            distance=min_distance,
        )


__all__ = ["CandidateGenerator", "MergeProposal"]
