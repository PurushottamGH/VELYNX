"""Source schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from ..enums import AccessStatus, ObjectType, SourceStatus
from .common import CanonicalRecordBase, NonEmptyStr, TzAwareDatetime


class Source(CanonicalRecordBase):
    object_type: Literal[ObjectType.SOURCE]
    status: SourceStatus

    source_type: NonEmptyStr
    citation: NonEmptyStr
    persistent_identifier: str | None
    access_status: AccessStatus
    accessed_at: TzAwareDatetime | None

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Citation",
        "## Relevance",
        "## Directly Demonstrates",
        "## Limitations",
        "## Verification Notes",
    )
