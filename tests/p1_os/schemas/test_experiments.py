from __future__ import annotations

import pytest
from pydantic import ValidationError

from p1_os.schemas import Experiment
from payloads import valid_payload


def test_valid_experiment():
    record = Experiment.model_validate(valid_payload("experiment"))
    assert record.question_id == "P1-Q000001"
    assert record.prospective_update_rules[0].outcome_class.value == "supports_primary"


def test_question_id_must_be_question_prefixed():
    payload = valid_payload("experiment")
    payload["question_id"] = "P1-C000001"
    with pytest.raises(ValidationError):
        Experiment.model_validate(payload)


def test_hypothesis_ids_must_be_hypothesis_prefixed():
    payload = valid_payload("experiment")
    payload["hypothesis_ids"] = ["P1-C000001"]
    with pytest.raises(ValidationError):
        Experiment.model_validate(payload)


def test_resource_budgets_must_be_a_mapping():
    payload = valid_payload("experiment")
    payload["resource_budgets"] = ["not", "a", "mapping"]
    with pytest.raises(ValidationError):
        Experiment.model_validate(payload)


def test_prospective_update_rule_outcome_class_must_be_valid():
    payload = valid_payload("experiment")
    payload["prospective_update_rules"][0]["outcome_class"] = "maybe"
    with pytest.raises(ValidationError):
        Experiment.model_validate(payload)


def test_prospective_update_rule_decision_required_must_be_bool():
    payload = valid_payload("experiment")
    payload["prospective_update_rules"][0]["decision_required"] = "yes"
    with pytest.raises(ValidationError):
        Experiment.model_validate(payload)


def test_prospective_update_rule_unknown_field_fails():
    payload = valid_payload("experiment")
    payload["prospective_update_rules"][0]["extra"] = 1
    with pytest.raises(ValidationError):
        Experiment.model_validate(payload)


def test_required_headings_constant():
    assert Experiment.REQUIRED_HEADINGS == (
        "## Research Question",
        "## Hypotheses",
        "## Variables",
        "## Controls and Baselines",
        "## Resource Budgets",
        "## Randomization and Seeds",
        "## Exclusions",
        "## Failure and Invalidation Conditions",
        "## Analysis Plan",
        "## Prospective Decision Rules",
    )
