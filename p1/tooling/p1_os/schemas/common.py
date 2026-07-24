"""Shared base model for the 12 canonical object schemas (spec section 13)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, field_validator, model_validator

from ..enums import ObjectType
from ..identifiers import validate_actor_handle, validate_id
from ..metadata import ProvenanceEntry


def _check_nonempty(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("value must be nonempty")
    return value


def _check_tz_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime value must be timezone-aware")
    return value


NonEmptyStr = Annotated[str, AfterValidator(_check_nonempty)]
TzAwareDatetime = Annotated[datetime, AfterValidator(_check_tz_aware)]


class CanonicalRecordBase(BaseModel):
    """Common canonical metadata (spec section 13).

    Concrete object schemas override ``object_type`` (Literal of one
    ObjectType member) and ``status`` (the object's own Status enum);
    Pydantic preserves each overridden field's original declared
    position, so field order stays: id, title, object_type, status,
    schema_version, created, last_reviewed, created_by, provenance.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    object_type: ObjectType
    status: str
    schema_version: Literal["1.0"]
    created: datetime
    last_reviewed: datetime | None
    created_by: str
    provenance: list[ProvenanceEntry]

    @field_validator("title")
    @classmethod
    def _validate_title_nonempty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("title must be nonempty")
        return value

    @field_validator("created_by")
    @classmethod
    def _validate_created_by(cls, value: str) -> str:
        return validate_actor_handle(value)

    @field_validator("created")
    @classmethod
    def _validate_created_tz_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("created must be timezone-aware")
        return value

    @field_validator("last_reviewed")
    @classmethod
    def _validate_last_reviewed_tz_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("last_reviewed must be timezone-aware")
        return value

    @model_validator(mode="after")
    def _validate_cross_fields(self) -> "CanonicalRecordBase":
        validate_id(self.id, object_type=self.object_type.value)
        if self.last_reviewed is not None and self.last_reviewed < self.created:
            raise ValueError("last_reviewed must not precede created")
        return self
