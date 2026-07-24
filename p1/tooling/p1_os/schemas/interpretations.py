"""Interpretation schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from ..enums import InterpretationStatus, ObjectType
from ..identifiers import IdListField
from .common import CanonicalRecordBase, NonEmptyStr


class Interpretation(CanonicalRecordBase):
    object_type: Literal[ObjectType.INTERPRETATION]
    status: InterpretationStatus

    result_ids: IdListField("result")
    hypothesis_ids: IdListField("hypothesis")
    scope: NonEmptyStr
    uncertainty: NonEmptyStr

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Bounded Interpretation",
        "## Alternative Explanations",
        "## Prohibited Inference",
        "## Uncertainty",
    )
