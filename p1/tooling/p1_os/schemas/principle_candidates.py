"""Principle Candidate schema (spec section 15).

No real Principle Candidate record may be created during the pilot;
Milestone 1 defines the schema only.
"""

from __future__ import annotations

from typing import ClassVar, Literal

from ..enums import ObjectType, PrincipleCandidateStatus
from ..identifiers import IdListField
from .common import CanonicalRecordBase, NonEmptyStr


class PrincipleCandidate(CanonicalRecordBase):
    object_type: Literal[ObjectType.PRINCIPLE_CANDIDATE]
    status: PrincipleCandidateStatus

    claim_ids: IdListField("claim")
    scope: NonEmptyStr
    reversal_conditions: list[NonEmptyStr]

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Candidate Principle",
        "## Supporting Claims",
        "## Scope and Exclusions",
        "## Reversal Conditions",
    )
