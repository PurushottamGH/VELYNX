"""Common canonical metadata field order and Provenance model (spec section 13, 14)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .identifiers import object_type_for_id

COMMON_FIELD_ORDER: tuple[str, ...] = (
    "id",
    "title",
    "object_type",
    "status",
    "schema_version",
    "created",
    "last_reviewed",
    "created_by",
    "provenance",
)


class ProvenanceEntry(BaseModel):
    """A single provenance entry (spec section 14).

    At least one of the four fields must be present; unknown fields are
    prohibited; derived_from_ids must not contain duplicates.
    """

    model_config = ConfigDict(extra="forbid")

    artifact_id: str | None = None
    derived_from_ids: list[str] | None = None
    source_locator: str | None = None
    note: str | None = None

    @field_validator("artifact_id")
    @classmethod
    def _validate_artifact_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if object_type_for_id(value) != "research_artifact":
            raise ValueError(f"artifact_id must be a Research Artifact ID: {value!r}")
        return value

    @field_validator("derived_from_ids")
    @classmethod
    def _validate_derived_from_ids(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        for identifier in value:
            object_type_for_id(identifier)
        if len(value) != len(set(value)):
            raise ValueError(f"derived_from_ids must not contain duplicates: {value!r}")
        return value

    @model_validator(mode="after")
    def _validate_at_least_one_field(self) -> "ProvenanceEntry":
        if all(
            getattr(self, name) is None
            for name in ("artifact_id", "derived_from_ids", "source_locator", "note")
        ):
            raise ValueError("A provenance entry must set at least one field")
        return self
