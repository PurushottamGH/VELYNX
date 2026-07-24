"""Result schema (spec section 15).

Result records must not contain Claim conclusions; Milestone 1 validates
structure only and cannot enforce that semantic constraint in code.
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import model_validator

from ..enums import ObjectType, OutcomeClass, ResultStatus
from ..identifiers import IdField, IdListField
from .common import CanonicalRecordBase, NonEmptyStr, TzAwareDatetime


class Result(CanonicalRecordBase):
    object_type: Literal[ObjectType.RESULT]
    status: ResultStatus

    experiment_id: IdField("experiment")
    protocol_hash: NonEmptyStr
    amendment_ids: IdListField("research_artifact")
    started_at: TzAwareDatetime
    ended_at: TzAwareDatetime
    environment: dict[str, Any]
    seeds: list[int]
    measurements: list[Any]
    exclusions_applied: list[NonEmptyStr]
    protocol_deviations: list[NonEmptyStr]
    failure_facts: list[NonEmptyStr]
    outcome_class: OutcomeClass
    raw_artifact_ids: IdListField("research_artifact")

    @model_validator(mode="after")
    def _validate_ended_at_not_before_started_at(self) -> "Result":
        if self.ended_at < self.started_at:
            raise ValueError("ended_at must not precede started_at")
        return self

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Protocol Facts",
        "## Raw Measurements",
        "## Exclusions and Deviations",
        "## Outcome Classification",
    )
