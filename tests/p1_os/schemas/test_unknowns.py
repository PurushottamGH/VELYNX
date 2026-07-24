from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Unknown
from payloads import valid_payload


def test_valid_unknown():
    record = Unknown.model_validate(valid_payload("unknown"))
    assert record.question_ids == ["P1-Q000001"]


def test_question_ids_must_be_question_prefixed():
    payload = valid_payload("unknown")
    payload["question_ids"] = ["P1-C000001"]
    with pytest.raises(ValidationError):
        Unknown.model_validate(payload)


def test_question_ids_must_be_well_formed():
    payload = valid_payload("unknown")
    payload["question_ids"] = ["not-an-id"]
    with pytest.raises(ValidationError):
        Unknown.model_validate(payload)


def test_resolution_criteria_items_must_be_nonempty_strings():
    payload = valid_payload("unknown")
    payload["resolution_criteria"] = [""]
    with pytest.raises(ValidationError):
        Unknown.model_validate(payload)


def test_blocks_accepts_any_recognized_id_prefix():
    payload = valid_payload("unknown")
    payload["blocks"] = ["P1-U000002"]
    Unknown.model_validate(payload)


def test_blocks_rejects_malformed_id():
    payload = valid_payload("unknown")
    payload["blocks"] = ["not-an-id"]
    with pytest.raises(ValidationError):
        Unknown.model_validate(payload)


def test_invalid_status_fails():
    payload = valid_payload("unknown")
    payload["status"] = "archived"
    with pytest.raises(ValidationError):
        Unknown.model_validate(payload)


def test_required_headings_constant():
    assert Unknown.REQUIRED_HEADINGS == (
        "## Unknown",
        "## Why It Matters",
        "## Current Evidence State",
        "## Resolution Criteria",
    )
