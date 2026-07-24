from __future__ import annotations

import datetime as dt

import pytest
from pydantic import ValidationError

from p1_os.schemas import Decision
from payloads import valid_payload


def test_valid_decision():
    record = Decision.model_validate(valid_payload("decision"))
    assert record.claim_changes[0].claim_id == "P1-C000001"
    assert record.claim_changes[0].prior_maturity.value == "L0"
    assert isinstance(record.decision_date, dt.date)


def test_reviewer_id_must_be_valid_actor_handle():
    payload = valid_payload("decision")
    payload["reviewer_id"] = "Not Valid"
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_claim_change_prior_status_must_be_valid_claim_status():
    payload = valid_payload("decision")
    payload["claim_changes"][0]["prior_status"] = "rejected"
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_claim_change_maturity_must_be_valid():
    payload = valid_payload("decision")
    payload["claim_changes"][0]["prior_maturity"] = "L9"
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_claim_change_claim_id_must_be_claim_prefixed():
    payload = valid_payload("decision")
    payload["claim_changes"][0]["claim_id"] = "P1-U000001"
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_unknown_change_status_must_be_valid_unknown_status():
    payload = valid_payload("decision")
    payload["unknown_changes"][0]["prior_status"] = "archived"
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_unknown_change_unknown_id_must_be_unknown_prefixed():
    payload = valid_payload("decision")
    payload["unknown_changes"][0]["unknown_id"] = "P1-C000001"
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_claim_change_unknown_field_fails():
    payload = valid_payload("decision")
    payload["claim_changes"][0]["extra"] = 1
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_counterevidence_review_may_be_null():
    payload = valid_payload("decision")
    payload["counterevidence_review"] = None
    Decision.model_validate(payload)


def test_counterevidence_review_may_be_string():
    payload = valid_payload("decision")
    payload["counterevidence_review"] = "Reviewed prior counterevidence."
    record = Decision.model_validate(payload)
    assert record.counterevidence_review == "Reviewed prior counterevidence."


def test_decision_date_must_be_valid_date():
    payload = valid_payload("decision")
    payload["decision_date"] = "not-a-date"
    with pytest.raises(ValidationError):
        Decision.model_validate(payload)


def test_required_headings_constant():
    assert Decision.REQUIRED_HEADINGS == (
        "## Decision Rationale",
        "## Evidence Considered",
        "## Boundaries",
        "## Reversal Conditions",
    )
