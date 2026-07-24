"""Question schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import StrictBool

from ..enums import ObjectType, QuestionStatus
from .common import CanonicalRecordBase, NonEmptyStr


class Question(CanonicalRecordBase):
    object_type: Literal[ObjectType.QUESTION]
    status: QuestionStatus

    selected: StrictBool
    scope: NonEmptyStr

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Research Question",
        "## Rationale",
        "## Scope",
        "## Selection Criteria",
    )
