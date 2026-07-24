"""Hypothesis schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from ..enums import HypothesisStatus, ObjectType
from ..identifiers import IdListField
from .common import CanonicalRecordBase, NonEmptyStr


class Hypothesis(CanonicalRecordBase):
    object_type: Literal[ObjectType.HYPOTHESIS]
    status: HypothesisStatus

    claim_ids: IdListField("claim")
    competing_hypothesis_ids: IdListField("hypothesis")
    prediction: NonEmptyStr
    independent_variables: list[NonEmptyStr]
    dependent_variables: list[NonEmptyStr]
    falsification_criteria: list[NonEmptyStr]
    scope: NonEmptyStr

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Hypothesis",
        "## Competing Explanations",
        "## Predictions",
        "## Falsification Criteria",
        "## Scope",
    )
