from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Interpretation
from payloads import valid_payload


def test_valid_interpretation():
    record = Interpretation.model_validate(valid_payload("interpretation"))
    assert record.result_ids == ["P1-R000001"]


def test_result_ids_must_be_result_prefixed():
    payload = valid_payload("interpretation")
    payload["result_ids"] = ["P1-C000001"]
    with pytest.raises(ValidationError):
        Interpretation.model_validate(payload)


def test_hypothesis_ids_must_be_hypothesis_prefixed():
    payload = valid_payload("interpretation")
    payload["hypothesis_ids"] = ["P1-C000001"]
    with pytest.raises(ValidationError):
        Interpretation.model_validate(payload)


def test_uncertainty_must_be_nonempty():
    payload = valid_payload("interpretation")
    payload["uncertainty"] = ""
    with pytest.raises(ValidationError):
        Interpretation.model_validate(payload)


def test_required_headings_constant():
    assert Interpretation.REQUIRED_HEADINGS == (
        "## Bounded Interpretation",
        "## Alternative Explanations",
        "## Prohibited Inference",
        "## Uncertainty",
    )
