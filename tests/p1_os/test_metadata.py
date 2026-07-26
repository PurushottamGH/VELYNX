"""Tests for common canonical metadata and provenance (spec section 13, 14)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.metadata import ProvenanceEntry
from p1_os.schemas import Question
from payloads import valid_payload


def test_valid_common_metadata_round_trips():
    payload = valid_payload("question")
    record = Question.model_validate(payload)
    assert record.id == "P1-Q000001"
    assert record.status.value == "draft"
    assert record.schema_version == "1.0"


def test_title_must_be_nonempty():
    payload = valid_payload("question")
    payload["title"] = "   "
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_unsupported_schema_version_fails():
    payload = valid_payload("question")
    payload["schema_version"] = "2.0"
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_unknown_top_level_field_fails():
    payload = valid_payload("question")
    payload["unexpected_field"] = "nope"
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_created_must_be_timezone_aware():
    payload = valid_payload("question")
    payload["created"] = "2026-01-01T00:00:00"  # naive
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_last_reviewed_must_be_timezone_aware_when_present():
    payload = valid_payload("question")
    payload["last_reviewed"] = "2026-01-02T00:00:00"  # naive
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_last_reviewed_must_not_precede_created():
    payload = valid_payload("question")
    payload["created"] = "2026-01-05T00:00:00Z"
    payload["last_reviewed"] = "2026-01-01T00:00:00Z"
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_last_reviewed_may_equal_created():
    payload = valid_payload("question")
    payload["last_reviewed"] = payload["created"]
    Question.model_validate(payload)


def test_created_by_must_be_a_valid_actor_handle():
    payload = valid_payload("question")
    payload["created_by"] = "Not Valid"
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_provenance_may_be_empty_list():
    payload = valid_payload("question")
    payload["provenance"] = []
    Question.model_validate(payload)


def test_provenance_is_required_key():
    payload = valid_payload("question")
    del payload["provenance"]
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_id_prefix_must_match_object_type():
    payload = valid_payload("question")
    payload["id"] = "P1-C000001"
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_object_type_literal_mismatch_fails():
    payload = valid_payload("question")
    payload["object_type"] = "claim"
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


# --- Provenance --------------------------------------------------------


def test_provenance_entry_requires_at_least_one_field():
    with pytest.raises(ValueError):
        ProvenanceEntry.model_validate({})


def test_provenance_entry_accepts_artifact_id_only():
    entry = ProvenanceEntry.model_validate({"artifact_id": "P1-AR000001"})
    assert entry.artifact_id == "P1-AR000001"


def test_provenance_entry_rejects_non_artifact_id_for_artifact_id_field():
    with pytest.raises(ValueError):
        ProvenanceEntry.model_validate({"artifact_id": "P1-C000001"})


def test_provenance_entry_rejects_duplicate_derived_from_ids():
    with pytest.raises(ValueError):
        ProvenanceEntry.model_validate({"derived_from_ids": ["P1-C000001", "P1-C000001"]})


def test_provenance_entry_rejects_unknown_fields():
    with pytest.raises(ValueError):
        ProvenanceEntry.model_validate({"artifact_id": "P1-AR000001", "bogus": "nope"})


def test_record_with_populated_provenance_entry():
    payload = valid_payload("question")
    payload["provenance"] = [
        {
            "artifact_id": "P1-AR000001",
            "derived_from_ids": ["P1-C000002"],
            "source_locator": "Page 12, section 3",
            "note": "Candidate claim extracted from a report.",
        }
    ]
    record = Question.model_validate(payload)
    assert record.provenance[0].note == "Candidate claim extracted from a report."
