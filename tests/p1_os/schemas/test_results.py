from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Result
from payloads import valid_payload


def test_valid_result():
    record = Result.model_validate(valid_payload("result"))
    assert record.outcome_class.value == "inconclusive"


@pytest.mark.parametrize(
    "value", ["supports_primary", "supports_competing", "inconclusive", "invalid"]
)
def test_all_outcome_classes_valid(value):
    payload = valid_payload("result")
    payload["outcome_class"] = value
    Result.model_validate(payload)


def test_invalid_outcome_class_fails():
    payload = valid_payload("result")
    payload["outcome_class"] = "maybe"
    with pytest.raises(ValidationError):
        Result.model_validate(payload)


def test_experiment_id_must_be_experiment_prefixed():
    payload = valid_payload("result")
    payload["experiment_id"] = "P1-Q000001"
    with pytest.raises(ValidationError):
        Result.model_validate(payload)


def test_started_at_naive_datetime_fails():
    payload = valid_payload("result")
    payload["started_at"] = "2026-01-01T00:00:00"
    with pytest.raises(ValidationError):
        Result.model_validate(payload)


def test_seeds_must_be_integers():
    payload = valid_payload("result")
    payload["seeds"] = ["not-an-int"]
    with pytest.raises(ValidationError):
        Result.model_validate(payload)


def test_environment_accepts_arbitrary_mapping():
    payload = valid_payload("result")
    payload["environment"] = {"python": "3.11.9", "os": "windows"}
    record = Result.model_validate(payload)
    assert record.environment == {"python": "3.11.9", "os": "windows"}


def test_protocol_hash_must_be_nonempty():
    payload = valid_payload("result")
    payload["protocol_hash"] = ""
    with pytest.raises(ValidationError):
        Result.model_validate(payload)


def test_amendment_ids_must_be_research_artifact_prefixed():
    payload = valid_payload("result")
    payload["amendment_ids"] = ["P1-C000001"]
    with pytest.raises(ValidationError):
        Result.model_validate(payload)


def test_required_headings_constant():
    assert Result.REQUIRED_HEADINGS == (
        "## Protocol Facts",
        "## Raw Measurements",
        "## Exclusions and Deviations",
        "## Outcome Classification",
    )


# --- Milestone 1.1: ended_at >= started_at ----------------------------------


def test_ended_at_before_started_at_fails():
    payload = valid_payload("result")
    payload["started_at"] = "2026-01-01T01:00:00Z"
    payload["ended_at"] = "2026-01-01T00:00:00Z"
    with pytest.raises(ValidationError):
        Result.model_validate(payload)


def test_ended_at_equal_started_at_passes():
    payload = valid_payload("result")
    payload["started_at"] = "2026-01-01T00:00:00Z"
    payload["ended_at"] = "2026-01-01T00:00:00Z"
    record = Result.model_validate(payload)
    assert record.started_at == record.ended_at


def test_ended_at_after_started_at_passes():
    payload = valid_payload("result")
    payload["started_at"] = "2026-01-01T00:00:00Z"
    payload["ended_at"] = "2026-01-01T01:00:00Z"
    record = Result.model_validate(payload)
    assert record.ended_at > record.started_at


def test_ended_at_before_started_at_across_offsets_fails():
    # Same instant expressed with different UTC offsets: still an ordering
    # violation once compared as timezone-aware instants, not naive text.
    payload = valid_payload("result")
    payload["started_at"] = "2026-01-01T06:00:00+05:30"  # == 2026-01-01T00:30:00Z
    payload["ended_at"] = "2026-01-01T00:00:00Z"
    with pytest.raises(ValidationError):
        Result.model_validate(payload)
