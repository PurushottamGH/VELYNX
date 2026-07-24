"""Experiment schema (spec section 15).

Milestone 1 defines structure only; it does not register or hash experiments.
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, StrictBool

from ..enums import ExperimentStatus, ObjectType, OutcomeClass
from ..identifiers import IdField, IdListField
from .common import CanonicalRecordBase, NonEmptyStr


class ProspectiveUpdateRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: NonEmptyStr
    outcome_class: OutcomeClass
    decision_required: StrictBool
    proposed_actions: list[NonEmptyStr]


class Experiment(CanonicalRecordBase):
    object_type: Literal[ObjectType.EXPERIMENT]
    status: ExperimentStatus

    question_id: IdField("question")
    hypothesis_ids: IdListField("hypothesis")
    competing_hypothesis_ids: IdListField("hypothesis")
    competing_claim_ids: IdListField("claim")
    primary_metric: NonEmptyStr
    secondary_metrics: list[NonEmptyStr]
    independent_variables: list[NonEmptyStr]
    dependent_variables: list[NonEmptyStr]
    controls: list[NonEmptyStr]
    baselines: list[NonEmptyStr]
    resource_budgets: dict[str, str]
    randomization: NonEmptyStr
    seed_policy: NonEmptyStr
    exclusions: list[NonEmptyStr]
    failure_conditions: list[NonEmptyStr]
    invalidation_conditions: list[NonEmptyStr]
    analysis_plan: NonEmptyStr
    prospective_update_rules: list[ProspectiveUpdateRule]

    REQUIRED_HEADINGS: ClassVar[tuple[str, ...]] = (
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
