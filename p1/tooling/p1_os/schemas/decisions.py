"""Decision schema (spec section 15).

Milestone 1 defines only the record schema; it does not apply changes.
"""

from __future__ import annotations

from datetime import date
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict

from ..enums import ClaimMaturity, ClaimStatus, DecisionStatus, ObjectType, UnknownStatus
from ..identifiers import ActorHandleField, IdField, IdListField
from .common import CanonicalRecordBase, NonEmptyStr


class ClaimChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: IdField("claim")
    prior_status: ClaimStatus
    proposed_status: ClaimStatus
    prior_maturity: ClaimMaturity
    proposed_maturity: ClaimMaturity
    update_rule_id: NonEmptyStr
    rationale: NonEmptyStr


class UnknownChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unknown_id: IdField("unknown")
    prior_status: UnknownStatus
    proposed_status: UnknownStatus
    rationale: NonEmptyStr


class Decision(CanonicalRecordBase):
    object_type: Literal[ObjectType.DECISION]
    status: DecisionStatus

    result_ids: IdListField("result")
    interpretation_ids: IdListField("interpretation")
    claim_changes: list[ClaimChange]
    unknown_changes: list[UnknownChange]
    accepted_conclusion: NonEmptyStr
    prohibited_conclusions: list[NonEmptyStr]
    scope: NonEmptyStr
    uncertainty: NonEmptyStr
    reversal_conditions: list[NonEmptyStr]
    reviewer_id: ActorHandleField
    decision_date: date
    counterevidence_review: str | None

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Decision Rationale",
        "## Evidence Considered",
        "## Boundaries",
        "## Reversal Conditions",
    )
