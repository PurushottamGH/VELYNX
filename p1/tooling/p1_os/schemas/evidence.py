"""Evidence schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict

from ..enums import EvidenceStatus, ObjectType, Stance, VerificationStatus
from ..identifiers import IdField
from .common import CanonicalRecordBase, NonEmptyStr


class ClaimLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: IdField("claim")
    stance: Stance


class Evidence(CanonicalRecordBase):
    object_type: Literal[ObjectType.EVIDENCE]
    status: EvidenceStatus

    source_id: IdField("source")
    claim_links: list[ClaimLink]
    evidence_kind: NonEmptyStr
    scope: NonEmptyStr
    source_locator: NonEmptyStr
    verification_status: VerificationStatus

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Evidence Statement",
        "## Directly Establishes",
        "## Does Not Establish",
        "## Generalization Limits",
        "## Verification",
    )
