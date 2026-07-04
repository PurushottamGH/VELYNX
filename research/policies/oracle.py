"""
research/policies/oracle.py
===========================

The optional :class:`PlaceholderOraclePolicy`.

Sprint R1 explicitly asks for an *unimplemented* oracle: a slot reserved for a
future ground-truth-aware policy (one that could see the environment's hidden
regime labels and merge optimally). Implementing real oracle logic now is out of
scope and would risk leaking ground truth into the comparison, so this class
deliberately does nothing except declare its own absence.

It is registered so the framework's hot-swap surface is complete, but invoking
it raises a clear, explicit error rather than silently degrading to a no-op —
the honest behaviour for a not-yet-built component.
"""

from __future__ import annotations

from typing import Any, Optional

from research.policies.base import (
    AcceptVerdict,
    ConsolidationPolicy,
    MergeProposal,
    PolicyContext,
)

_NOT_IMPLEMENTED = "Oracle policy not implemented"


class OracleNotImplementedError(NotImplementedError):
    """Raised on any attempt to actually run the placeholder oracle."""


class PlaceholderOraclePolicy(ConsolidationPolicy):
    """A reserved, deliberately-unimplemented ground-truth oracle slot."""

    name = "oracle"
    description = f"{_NOT_IMPLEMENTED} (reserved placeholder)."

    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        # Emit the required message and refuse, rather than pretending to work.
        raise OracleNotImplementedError(_NOT_IMPLEMENTED)

    def accept(self, score: Any, context: PolicyContext) -> AcceptVerdict:
        raise OracleNotImplementedError(_NOT_IMPLEMENTED)


__all__ = ["PlaceholderOraclePolicy", "OracleNotImplementedError"]
