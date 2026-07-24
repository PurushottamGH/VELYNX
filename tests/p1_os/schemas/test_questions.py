from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Question
from payloads import valid_payload


def test_valid_question():
    record = Question.model_validate(valid_payload("question"))
    assert record.selected is False


def test_selected_must_be_bool():
    payload = valid_payload("question")
    payload["selected"] = "not-a-bool"
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_scope_must_be_nonempty():
    payload = valid_payload("question")
    payload["scope"] = "   "
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_missing_scope_fails():
    payload = valid_payload("question")
    del payload["scope"]
    with pytest.raises(ValidationError):
        Question.model_validate(payload)


def test_required_headings_constant():
    assert Question.REQUIRED_HEADINGS == (
        "## Research Question",
        "## Rationale",
        "## Scope",
        "## Selection Criteria",
    )
