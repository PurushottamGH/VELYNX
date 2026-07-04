"""
VELYNX Phase 63 — Interface Gateway for Counterfactual Premises
===============================================================

The entry layer that transforms raw user intent into validated data
structures the :class:`~backend.simulation.causal_evaluator.CounterfactualEvaluator`
consumes.

Design
------
Pure additive layer — no imports from ``pipeline.py``, no modifications to
existing graph readers. Relies only on the Phase 62 layer:

* :mod:`backend.knowledge.world_model_schema` — ``Entity``, ``AttributeSchema``
* :mod:`backend.knowledge.schema_gatekeeper` — entity resolution, predicate
  mapping, value coercion
* :mod:`backend.knowledge.world_model_context` — registry singleton

Flow::

    raw_input (dict)
        │  parse_user_input()
        ▼
    CounterfactualPremise  (Pydantic model)
        │  validate_premise()
        ▼
    ValidationResult  (accepted_overrides / rejected_overrides)
        │  .to_premise_dict()
        ▼
    CausalEvaluator.evaluate(query, premise_dict)

The gatekeeper's **Stage 3** (schema membership) logic is replicated here in
read-only form so callers can check compatibility *before* allocating a
simulation window. No gatekeeper state is mutated.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator

from backend.knowledge.schema_gatekeeper import (
    REASON_CONSTRAINT_VIOLATION,
    REASON_TYPE_MISMATCH,
    REASON_UNKNOWN_ATTRIBUTE,
    _coerce,
    _resolve_entity,
)
from backend.knowledge.world_model_schema import Entity, SchemaError

__all__ = [
    "CounterfactualPremise",
    "PremiseScope",
    "ValidationResult",
    "AttributeValidation",
    "PremiseParseError",
    "validate_premise",
    "parse_user_input",
    "READ_ONLY_ATTRIBUTES",
]

logger = logging.getLogger("velynx.simulation.interface")

# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

READ_ONLY_ATTRIBUTES: Set[str] = {
    "id",
    "name",
    "entity_type",
}
"""Attributes that may NOT be overridden by a counterfactual premise.

These are structural / identity-bearing fields on ``Entity``. Trying to
override them is a semantic error — if the user wants to *rename* an entity or
change its type, that is a different operation (entity creation / type
reclassification), not a counterfactual fork.
"""

VALID_SCOPES = {"local", "session"}


# ══════════════════════════════════════════════════════════════════════════════
# Pydantic model
# ══════════════════════════════════════════════════════════════════════════════


class PremiseScope(str, Enum):
    """Whether the premise applies to a single query or persists across turns."""

    LOCAL = "local"
    SESSION = "session"


class CounterfactualPremise(BaseModel):
    """A validated counterfactual premise describing which entity to fork and how.

    Parameters
    ----------
    target_entity
        The name of the entity to fork (case-insensitive; resolved against the
        live :class:`~backend.knowledge.world_model_schema.WorldModelRegistry`).
        Must be a non-empty string naming a registered entity.
    attribute_overrides
        Key-value pairs of attributes to change on the forked entity. Keys are
        snake_case attribute names from the entity's resolved schema. Values
        are coerced to the schema's declared datatype during validation.
    scope
        ``"local"`` — applies to just this query evaluation.
        ``"session"`` — carries forward to subsequent queries in the same
        conversation (the caller is responsible for persistence).
    """

    target_entity: str = Field(
        ...,
        min_length=1,
        description="Name of the entity to fork in the counterfactual.",
    )
    attribute_overrides: Dict[str, Any] = Field(
        default_factory=dict,
        description="Attributes to override on the forked entity.",
    )
    scope: PremiseScope = Field(
        default=PremiseScope.LOCAL,
        description="Whether this premise is local or session-scoped.",
    )

    @field_validator("target_entity")
    @classmethod
    def _entity_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("target_entity must be a non-empty string")
        return stripped

    # ── Serialisation helpers ────────────────────────────────────────────────

    def to_premise_dict(self) -> Dict[str, Dict[str, Any]]:
        """Convert to the nested dict shape the ``CausalEvaluator`` expects.

        The evaluator's ``evaluate()`` method consumes
        ``{entity_name: {attr: value, ...}}``. This helper wraps the model's
        fields into that form in one call.
        """
        return {self.target_entity: dict(self.attribute_overrides)}

    def to_session_key(self) -> str:
        """Return a stable dict key for session-scoped deduplication.

        Used by callers that maintain a session-level premise registry to
        avoid re-validating an identical premise.
        """
        return f"{self.target_entity}::{sorted(self.attribute_overrides)}"

    model_config = {"extra": "forbid"}


# ══════════════════════════════════════════════════════════════════════════════
# Validation result types
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class AttributeValidation:
    """Result of validating a single attribute override against the ontology.

    Every override is validated independently so the caller can see *which*
    attributes passed and which failed — no early-exit, no partial rollback.
    """

    attribute_key: str
    original_value: Any
    coerced_value: Any
    accepted: bool
    reason_code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attribute": self.attribute_key,
            "original_value": self.original_value,
            "coerced_value": self.coerced_value,
            "accepted": self.accepted,
            "reason": self.reason_code,
            "message": self.message,
        }


@dataclass
class ValidationResult:
    """Result of validating a complete :class:`CounterfactualPremise`.

    Carries two separate lists of overrides:
    * ``accepted_overrides`` — attributes the ontology validates, ready to
      apply in a simulation context
    * ``rejected_overrides`` — attributes that failed (read-only, unknown,
      type mismatch, constraint violation), each with a human-readable reason

    An empty ``rejected_overrides`` means the premise is fully valid.
    """

    premise: CounterfactualPremise
    accepted_overrides: Dict[str, Any] = field(default_factory=dict)
    rejected_overrides: List[AttributeValidation] = field(default_factory=list)
    entity_resolved: bool = False
    entity_type_name: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """True when the entity was found AND every override was accepted."""
        return self.entity_resolved and not self.rejected_overrides

    @property
    def is_partial(self) -> bool:
        """True when some overrides passed and some failed."""
        return (
            self.entity_resolved
            and bool(self.accepted_overrides)
            and bool(self.rejected_overrides)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_entity": self.premise.target_entity,
            "entity_type": self.entity_type_name,
            "entity_resolved": self.entity_resolved,
            "is_valid": self.is_valid,
            "accepted_overrides": dict(self.accepted_overrides),
            "rejected_overrides": [r.to_dict() for r in self.rejected_overrides],
            "scope": self.premise.scope.value,
        }


# ══════════════════════════════════════════════════════════════════════════════
# Validation
# ══════════════════════════════════════════════════════════════════════════════


def validate_premise(premise: CounterfactualPremise) -> ValidationResult:
    """Validate a premise's attribute overrides against the ontology.

    This is a **read-only check** — no gatekeeper state is mutated, no
    simulation context is allocated. It answers the question: *would* the
    ontology accept these overrides?

    Validation rules (mirroring the SchemaGatekeeper's Stage 3 + Stage 4):
        1. **Read-only guard** — structural attributes (``id``, ``name``,
           ``entity_type``) are rejected immediately.
        2. **Entity resolution** — the target must exist in the live registry.
        3. **Schema membership** — each attribute key must be declared on the
           entity's resolved (inherited + facet) schema.
        4. **Type coercion** — the value must be coercible to the attribute's
           declared datatype.
        5. **Constraint check** — the coerced value must satisfy the
           attribute's ``enum`` / ``min`` / ``max`` / ``pattern`` constraints.

    Parameters
    ----------
    premise
        The parsed, Pydantic-validated premise to check.

    Returns
    -------
    ValidationResult
        Carries accepted and rejected overrides. ``result.is_valid`` is True
        when every override passed.
    """
    # 1. Entity resolution.
    entity = _resolve_entity(premise.target_entity)
    if entity is None:
        logger.info(
            "validate_premise: entity %r not found in registry",
            premise.target_entity,
        )
        return ValidationResult(
            premise=premise,
            accepted_overrides={},
            rejected_overrides=[
                AttributeValidation(
                    attribute_key="(entity)",
                    original_value=premise.target_entity,
                    coerced_value=None,
                    accepted=False,
                    reason_code="UNKNOWN_ENTITY",
                    message=(
                        f"Entity {premise.target_entity!r} is not registered "
                        f"in the world model. Cannot apply counterfactual premise."
                    ),
                )
            ],
            entity_resolved=False,
        )

    schema = entity._resolved_schema()
    accepted: Dict[str, Any] = {}
    rejected: List[AttributeValidation] = []

    for attr_key, value in premise.attribute_overrides.items():
        # 2. Read-only guard.
        if attr_key in READ_ONLY_ATTRIBUTES:
            rejected.append(
                AttributeValidation(
                    attribute_key=attr_key,
                    original_value=value,
                    coerced_value=None,
                    accepted=False,
                    reason_code="READ_ONLY",
                    message=(
                        f"Attribute {attr_key!r} is read-only and may not be "
                        f"modified by a counterfactual premise. Structural "
                        f"attributes ({', '.join(sorted(READ_ONLY_ATTRIBUTES))}) "
                        f"define entity identity."
                    ),
                )
            )
            continue

        # 3. Schema membership.
        attr_schema = schema.get(attr_key)
        if attr_schema is None:
            valid_attrs = sorted(schema)
            rejected.append(
                AttributeValidation(
                    attribute_key=attr_key,
                    original_value=value,
                    coerced_value=None,
                    accepted=False,
                    reason_code=REASON_UNKNOWN_ATTRIBUTE,
                    message=(
                        f"Entity {entity.name!r} (type: {entity.type.name}) "
                        f"does not have attribute {attr_key!r}. "
                        f"Valid attributes: {', '.join(valid_attrs)}."
                    ),
                )
            )
            continue

        # 4. Type coercion (mirrors SchemaGatekeeper Stage 4).
        coerced, coerce_err = _coerce(str(value), attr_schema.datatype)
        if coerce_err is not None:
            rejected.append(
                AttributeValidation(
                    attribute_key=attr_key,
                    original_value=value,
                    coerced_value=coerced,
                    accepted=False,
                    reason_code=REASON_TYPE_MISMATCH,
                    message=(
                        f"Attribute {attr_key!r} on {entity.name!r} expects "
                        f"{attr_schema._type_name()}, but {value!r} could not "
                        f"be parsed ({coerce_err})."
                    ),
                )
            )
            continue

        # 5. Constraint validation (strict — counterfactuals still must be
        #    schema-valid; the simulation's relaxed gatekeeper handles
        #    deliberately impossible values like max_speed=999999).
        try:
            attr_schema.validate(coerced)
        except SchemaError as exc:
            rejected.append(
                AttributeValidation(
                    attribute_key=attr_key,
                    original_value=value,
                    coerced_value=coerced,
                    accepted=False,
                    reason_code=REASON_CONSTRAINT_VIOLATION,
                    message=str(exc),
                )
            )
            continue

        accepted[attr_key] = coerced

    result = ValidationResult(
        premise=premise,
        accepted_overrides=accepted,
        rejected_overrides=rejected,
        entity_resolved=True,
        entity_type_name=entity.type.name,
    )

    if rejected:
        log_rejected = [(r.attribute_key, r.reason_code) for r in rejected]
        logger.info(
            "validate_premise: %d/%d overrides rejected for %r: %s",
            len(rejected),
            len(premise.attribute_overrides),
            premise.target_entity,
            log_rejected,
        )

    return result


# ══════════════════════════════════════════════════════════════════════════════
# Parser
# ══════════════════════════════════════════════════════════════════════════════


class PremiseParseError(ValueError):
    """Raised when raw user input cannot be parsed into a ``CounterfactualPremise``.

    Carries a human-readable message describing the specific parse failure
    (missing required fields, wrong types, read-only attribute usage, etc.)
    so the error can be surfaced directly in the API response.
    """


def parse_user_input(raw_input: dict) -> CounterfactualPremise:
    """Parse raw API input into a validated ``CounterfactualPremise``.

    This is the **factory function** that transforms free-form user input
    (from an HTTP endpoint, CLI flag, or LLM tool call) into the typed,
    validated data structure the rest of the pipeline consumes.

    Expected input shape::

        {
            "target_entity": "Tesla Model 3",
            "attribute_overrides": {"mobility_type": "hover"},
            "scope": "local",            # optional, defaults to "local"
        }

    The function performs two validation phases:

    **Phase 1 — Pydantic validation**: checks the structural shape of the
    input (required fields present, correct types, scope is a valid enum).

    **Phase 2 — Ontology validation**: calls ``validate_premise()`` to check
    every attribute override against the entity's schema. Any read-only
    attribute usage causes an explicit ``PremiseParseError`` with the
    offending keys named.

    Parameters
    ----------
    raw_input
        The raw dict from the API layer.

    Returns
    -------
    CounterfactualPremise
        The parsed and validated model, ready to pass to
        ``validate_premise()`` or ``CounterfactualEvaluator.evaluate()``.

    Raises
    ------
    PremiseParseError
        If the input is structurally malformed (missing required fields, wrong
        types) or if any attribute override targets a read-only attribute
        (like ``id``, ``name``, ``entity_type``). The error message is
        self-explanatory for API error responses.
    """
    if not isinstance(raw_input, dict):
        raise PremiseParseError(
            f"Expected a dict, got {type(raw_input).__name__}: {raw_input!r}"
        )

    # Phase 1 — Pydantic validation.
    try:
        premise = CounterfactualPremise(**raw_input)
    except Exception as exc:
        raise PremiseParseError(str(exc)) from exc

    # Phase 2 — Ontology validation with explicit read-only check.
    result = validate_premise(premise)

    if not result.entity_resolved:
        # Entity not found — the premise is structurally sound but refers to
        # a non-existent entity. Surface the rejection.
        err_msg = result.rejected_overrides[0].message if result.rejected_overrides else (
            f"Entity {premise.target_entity!r} not found in world model."
        )
        logger.info(
            "parse_user_input: entity %r not found", premise.target_entity,
        )
        raise PremiseParseError(err_msg)

    # Surface read-only attribute violations as explicit parse errors.
    read_only_rejections = [
        r for r in result.rejected_overrides if r.reason_code == "READ_ONLY"
    ]
    if read_only_rejections:
        keys = [r.attribute_key for r in read_only_rejections]
        raise PremiseParseError(
            f"Cannot override read-only attribute(s): {', '.join(keys)}. "
            f"Structural attributes ({', '.join(sorted(READ_ONLY_ATTRIBUTES))}) "
            f"define entity identity and may not be modified by "
            f"a counterfactual premise."
        )

    # Log warnings for non-fatal rejections (type mismatches, constraint
    # violations) so callers can surface them in the response.
    if result.rejected_overrides:
        logger.warning(
            "parse_user_input: %d non-fatal validation warnings for %r: %s",
            len(result.rejected_overrides),
            premise.target_entity,
            [(r.attribute_key, r.reason_code) for r in result.rejected_overrides],
        )

    return premise
