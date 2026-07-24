from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Claim
from payloads import valid_payload


def test_valid_claim():
    record = Claim.model_validate(valid_payload("claim"))
    assert record.claim_role.value == "candidate"
    assert record.maturity.value == "L0"


@pytest.mark.parametrize(
    "role", ["candidate", "competing", "constraint", "scope_limit"]
)
def test_all_claim_roles_valid(role):
    payload = valid_payload("claim")
    payload["claim_role"] = role
    Claim.model_validate(payload)


def test_invalid_claim_role_fails():
    payload = valid_payload("claim")
    payload["claim_role"] = "primary"
    with pytest.raises(ValidationError):
        Claim.model_validate(payload)


@pytest.mark.parametrize("level", ["L0", "L1", "L2", "L3", "L4", "L5"])
def test_all_maturity_levels_valid(level):
    payload = valid_payload("claim")
    payload["maturity"] = level
    Claim.model_validate(payload)


def test_invalid_maturity_fails():
    payload = valid_payload("claim")
    payload["maturity"] = "L6"
    with pytest.raises(ValidationError):
        Claim.model_validate(payload)


def test_unknown_ids_must_be_unknown_prefixed():
    payload = valid_payload("claim")
    payload["unknown_ids"] = ["P1-Q000001"]
    with pytest.raises(ValidationError):
        Claim.model_validate(payload)


def test_competes_with_claim_ids_must_be_claim_prefixed():
    payload = valid_payload("claim")
    payload["competes_with_claim_ids"] = ["P1-U000001"]
    with pytest.raises(ValidationError):
        Claim.model_validate(payload)


def test_invalid_status_fails():
    payload = valid_payload("claim")
    payload["status"] = "rejected"
    with pytest.raises(ValidationError):
        Claim.model_validate(payload)


def test_required_headings_constant():
    assert Claim.REQUIRED_HEADINGS == (
        "## Claim",
        "## Scope",
        "## Current Justification",
        "## Strongest Counterargument",
        "## Reversal or Revision Conditions",
    )
