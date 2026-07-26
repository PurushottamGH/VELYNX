from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Evidence
from payloads import valid_payload


def test_valid_evidence():
    record = Evidence.model_validate(valid_payload("evidence"))
    assert record.claim_links[0].stance.value == "supports"


@pytest.mark.parametrize(
    "stance", ["supports", "contradicts", "contextualizes", "null_evidence", "limits"]
)
def test_all_stances_valid(stance):
    payload = valid_payload("evidence")
    payload["claim_links"] = [{"claim_id": "P1-C000001", "stance": stance}]
    Evidence.model_validate(payload)


def test_invalid_stance_fails():
    payload = valid_payload("evidence")
    payload["claim_links"] = [{"claim_id": "P1-C000001", "stance": "confirms"}]
    with pytest.raises(ValidationError):
        Evidence.model_validate(payload)


def test_claim_link_claim_id_must_be_claim_prefixed():
    payload = valid_payload("evidence")
    payload["claim_links"] = [{"claim_id": "P1-U000001", "stance": "supports"}]
    with pytest.raises(ValidationError):
        Evidence.model_validate(payload)


def test_claim_link_unknown_field_fails():
    payload = valid_payload("evidence")
    payload["claim_links"] = [{"claim_id": "P1-C000001", "stance": "supports", "extra": 1}]
    with pytest.raises(ValidationError):
        Evidence.model_validate(payload)


@pytest.mark.parametrize("value", ["pending", "partially_verified", "verified", "unverifiable"])
def test_all_verification_statuses_valid(value):
    payload = valid_payload("evidence")
    payload["verification_status"] = value
    Evidence.model_validate(payload)


def test_invalid_verification_status_fails():
    payload = valid_payload("evidence")
    payload["verification_status"] = "confirmed"
    with pytest.raises(ValidationError):
        Evidence.model_validate(payload)


def test_source_id_must_be_source_prefixed():
    payload = valid_payload("evidence")
    payload["source_id"] = "P1-C000001"
    with pytest.raises(ValidationError):
        Evidence.model_validate(payload)


def test_required_headings_constant():
    assert Evidence.REQUIRED_HEADINGS == (
        "## Evidence Statement",
        "## Directly Establishes",
        "## Does Not Establish",
        "## Generalization Limits",
        "## Verification",
    )
