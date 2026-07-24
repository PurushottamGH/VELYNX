from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Source
from payloads import valid_payload


def test_valid_source():
    record = Source.model_validate(valid_payload("source"))
    assert record.access_status.value == "not_checked"


@pytest.mark.parametrize(
    "value", ["not_checked", "abstract_only", "full_text_checked", "inaccessible"]
)
def test_all_access_statuses_valid(value):
    payload = valid_payload("source")
    payload["access_status"] = value
    Source.model_validate(payload)


def test_invalid_access_status_fails():
    payload = valid_payload("source")
    payload["access_status"] = "checked"
    with pytest.raises(ValidationError):
        Source.model_validate(payload)


def test_accessed_at_naive_datetime_fails():
    payload = valid_payload("source")
    payload["accessed_at"] = "2026-01-01T00:00:00"
    with pytest.raises(ValidationError):
        Source.model_validate(payload)


def test_accessed_at_tz_aware_datetime_accepted():
    payload = valid_payload("source")
    payload["accessed_at"] = "2026-01-01T00:00:00Z"
    record = Source.model_validate(payload)
    assert record.accessed_at.tzinfo is not None


def test_citation_must_be_nonempty():
    payload = valid_payload("source")
    payload["citation"] = ""
    with pytest.raises(ValidationError):
        Source.model_validate(payload)


def test_required_headings_constant():
    assert Source.REQUIRED_HEADINGS == (
        "## Citation",
        "## Relevance",
        "## Directly Demonstrates",
        "## Limitations",
        "## Verification Notes",
    )
