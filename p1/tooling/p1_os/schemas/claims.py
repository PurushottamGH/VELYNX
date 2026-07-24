"""Claim schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from ..enums import ClaimMaturity, ClaimRole, ClaimStatus, ObjectType
from ..identifiers import IdListField
from .common import CanonicalRecordBase, NonEmptyStr


class Claim(CanonicalRecordBase):
    object_type: Literal[ObjectType.CLAIM]
    status: ClaimStatus

    question_ids: IdListField("question")
    unknown_ids: IdListField("unknown")
    claim_role: ClaimRole
    maturity: ClaimMaturity
    scope: NonEmptyStr
    competes_with_claim_ids: IdListField("claim")

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Claim",
        "## Scope",
        "## Current Justification",
        "## Strongest Counterargument",
        "## Reversal or Revision Conditions",
    )
