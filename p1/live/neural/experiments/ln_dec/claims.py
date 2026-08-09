"""Executable claim firewall for the repaired experiment."""

from __future__ import annotations

from enum import Enum
from typing import Iterable


class ClaimClass(str, Enum):
    R0 = "R0 NO LEARNING EVIDENCE"
    R1 = "R1 MEMORIZATION / RETRIEVAL CONSISTENT"
    R2 = "R2 STATISTICAL SEQUENCE LEARNING"
    R3 = "R3 LIMITED OUT-OF-DISTRIBUTION GENERALIZATION"
    R4 = "R4 REPLICATED COMPOSITIONAL GENERALIZATION"
    R5 = "R5 INCONCLUSIVE"


ALLOWED_CLAIM_CLASSES = frozenset(item.value for item in ClaimClass)
FORBIDDEN_CLAIM_TERMS = frozenset(
    {
        "agi",
        "intelligence",
        "understanding",
        "reasoning",
        "consciousness",
        "mind",
    }
)


def validate_claim_class(value: str) -> ClaimClass:
    """Reject labels outside the R0-R5 executable firewall."""
    try:
        return ClaimClass(value)
    except ValueError as exc:
        raise ValueError(f"claim class must be one of {sorted(ALLOWED_CLAIM_CLASSES)}") from exc


def assert_claim_text_safe(text: str) -> None:
    """Reject anthropomorphic or capability-inflating report text."""
    lowered = text.lower()
    found = sorted(term for term in FORBIDDEN_CLAIM_TERMS if term in lowered)
    if found:
        raise ValueError(f"claim firewall rejected forbidden term(s): {found}")


def allowed_claims() -> Iterable[str]:
    return tuple(item.value for item in ClaimClass)


__all__ = ["ALLOWED_CLAIM_CLASSES", "ClaimClass", "allowed_claims", "assert_claim_text_safe", "validate_claim_class"]

