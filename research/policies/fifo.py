"""
research/policies/fifo.py
=========================

The :class:`FIFOAgePolicy` — merge the two oldest surviving clusters.

A classic cache-eviction heuristic transplanted to memory consolidation: the
longest-lived clusters are fused first, on the assumption that age alone is a
reasonable proxy for "ready to be compressed". It uses no geometry and no
free-energy signal, so it isolates the value of *age-based* selection.
"""

from __future__ import annotations

from typing import Any, Optional

from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    MergeProposal,
    PolicyContext,
    oldest_pair,
)


class FIFOAgePolicy(ConsolidationPolicy):
    """Merge the two oldest clusters (lowest ids), then always commit."""

    name = "fifo"
    description = "Merge the two oldest surviving clusters (commits unconditionally)."

    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        return oldest_pair(engine, strategy="fifo_age")

    def accept(self, score: Any, context: PolicyContext) -> AcceptVerdict:
        return True, "fifo: commit oldest pair unconditionally"


__all__ = ["FIFOAgePolicy"]
