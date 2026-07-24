"""Unknown schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from ..enums import ObjectType, UnknownStatus
from ..identifiers import IdListField
from .common import CanonicalRecordBase, NonEmptyStr


class Unknown(CanonicalRecordBase):
    object_type: Literal[ObjectType.UNKNOWN]
    status: UnknownStatus

    question_ids: IdListField("question")
    priority: NonEmptyStr
    blocks: IdListField()
    resolution_criteria: list[NonEmptyStr]

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Unknown",
        "## Why It Matters",
        "## Current Evidence State",
        "## Resolution Criteria",
    )
