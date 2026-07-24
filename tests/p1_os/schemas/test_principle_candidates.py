from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import PrincipleCandidate
from payloads import valid_payload


def test_valid_principle_candidate():
    record = PrincipleCandidate.model_validate(valid_payload("principle_candidate"))
    assert record.claim_ids == ["P1-C000001"]
    assert record.status.value == "draft"


def test_claim_ids_must_be_claim_prefixed():
    payload = valid_payload("principle_candidate")
    payload["claim_ids"] = ["P1-U000001"]
    with pytest.raises(ValidationError):
        PrincipleCandidate.model_validate(payload)


def test_only_draft_status_is_valid_during_pilot():
    """No real Principle Candidate record may be created during the pilot
    (spec section 3, 5 PI-005); Milestone 1 restricts the status enum to
    the sole textually-evidenced value (draft) accordingly."""
    payload = valid_payload("principle_candidate")
    payload["status"] = "active"
    with pytest.raises(ValidationError):
        PrincipleCandidate.model_validate(payload)


def test_reversal_conditions_items_must_be_nonempty():
    payload = valid_payload("principle_candidate")
    payload["reversal_conditions"] = [""]
    with pytest.raises(ValidationError):
        PrincipleCandidate.model_validate(payload)


def test_required_headings_constant():
    assert PrincipleCandidate.REQUIRED_HEADINGS == (
        "## Candidate Principle",
        "## Supporting Claims",
        "## Scope and Exclusions",
        "## Reversal Conditions",
    )
