from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Hypothesis
from payloads import valid_payload


def test_valid_hypothesis():
    record = Hypothesis.model_validate(valid_payload("hypothesis"))
    assert record.claim_ids == ["P1-C000001"]


def test_claim_ids_must_be_claim_prefixed():
    payload = valid_payload("hypothesis")
    payload["claim_ids"] = ["P1-Q000001"]
    with pytest.raises(ValidationError):
        Hypothesis.model_validate(payload)


def test_competing_hypothesis_ids_must_be_hypothesis_prefixed():
    payload = valid_payload("hypothesis")
    payload["competing_hypothesis_ids"] = ["P1-C000001"]
    with pytest.raises(ValidationError):
        Hypothesis.model_validate(payload)


def test_prediction_must_be_nonempty():
    payload = valid_payload("hypothesis")
    payload["prediction"] = ""
    with pytest.raises(ValidationError):
        Hypothesis.model_validate(payload)


def test_variable_list_items_must_be_nonempty_strings():
    payload = valid_payload("hypothesis")
    payload["independent_variables"] = [""]
    with pytest.raises(ValidationError):
        Hypothesis.model_validate(payload)


def test_required_headings_constant():
    assert Hypothesis.REQUIRED_HEADINGS == (
        "## Hypothesis",
        "## Competing Explanations",
        "## Predictions",
        "## Falsification Criteria",
        "## Scope",
    )
