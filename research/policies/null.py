"""
research/policies/null.py
=========================

The :class:`NullPolicy` — the *no-consolidation* control.

This is the scientifically essential baseline: a brain that never restructures
its memory at all. Every other policy's value can only be judged relative to
doing nothing, so this control anchors the whole ablation.
"""

from __future__ import annotations

from typing import Any, Optional

from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    MergeProposal,
    PolicyContext,
)


class NullPolicy(ConsolidationPolicy):
    """Never consolidate: propose nothing, commit nothing."""

    name = "null"
    description = "Never consolidate (no-op control baseline)."

    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        # No proposal is ever made, so the consolidation loop is a no-op and the
        # cluster substrate is left exactly as the perception path built it.
        return None

    def accept(self, score: Any, context: PolicyContext) -> AcceptVerdict:
        # Unreachable in normal flow (select_candidate returns None first), but
        # defined for contract completeness: the null policy accepts nothing.
        return False, "null: never consolidate"


__all__ = ["NullPolicy"]
