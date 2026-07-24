"""Research Artifact schema (spec section 15)."""

from __future__ import annotations

from typing import ClassVar, Literal

from ..enums import ObjectType, ResearchArtifactStatus
from .common import CanonicalRecordBase, NonEmptyStr


class ResearchArtifact(CanonicalRecordBase):
    object_type: Literal[ObjectType.RESEARCH_ARTIFACT]
    status: ResearchArtifactStatus

    artifact_kind: NonEmptyStr
    media_type: NonEmptyStr
    content_hash: str | None
    external_locator: str | None

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
        "## Description",
        "## Provenance",
        "## Integrity",
    )
