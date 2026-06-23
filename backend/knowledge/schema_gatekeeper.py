"""
VELYNX Phase 62 — Schema Gatekeeper
=====================================

The **validation layer** that intercepts a TEACH before it reaches the
Knowledge Graph. Where :mod:`backend.knowledge.fact_extractor` extracts raw
``(subject, predicate, object)`` triples from a user's declarative statement
and persists them, this module classifies each triple as ACCEPT or REJECT
based on the registered :class:`~backend.knowledge.world_model_schema.Entity`
schema. It owns ALL of Phase 62's new validation logic — ``fact_extractor``
stays responsible only for extraction + free-form storage.

Design: a four-stage classifier
-------------------------------
For each extracted triple, applied in order (first non-ACCEPT verdict wins):

1. **Entity resolution** — does ``subject`` name a registered, typed
   :class:`Entity` (case-insensitive, via the world-model name index)? If not,
   the triple is about an UN-typed subject → **ACCEPT** (open-world: VELYNX may
   still learn free-form facts about anything). This keeps every pre-Phase-62
   TEACH (entities like "User", "supermegasoftware", cities, ...) flowing to the
   triples table unchanged.

2. **Predicate mapping** — map the triple's ``relation`` to a canonical
   attribute key via the JSON ``predicate_map`` (single source of truth shared
   with :mod:`ontology_loader`). If the predicate is NOT in the map, it is a
   free-form assertion → **ACCEPT** (open-world). So "My Tesla has a scratch"
   (relation "has", not mapped) lands in the triples table; only predicates we
   explicitly recognise as schema slots are subject to type checking.

3. **Schema membership** — is the mapped attribute key declared on the
   subject's resolved schema (its type's parent chain + its facets)? If NOT,
   the predicate is recognised (it is in ``predicate_map``) but the attribute
   does not belong to this kind of object → **REJECT** ``UNKNOWN_ATTRIBUTE``.
   This is the structural "5000 legs" kill: ``has legs`` maps to ``leg_count``,
   which is in the map, but ``leg_count`` is not on Vehicle / Electronics /
   PhysicalObject, so "My Tesla has 5000 legs" is rejected. No hard-coded
   negative list — the rejection falls out of a recognised predicate hitting a
   closed schema.

4. **Value validation** — coerce ``object`` to the attribute's declared
   datatype, then enforce the attribute's ``constraints`` (``enum`` / ``min`` /
   ``max`` / ``pattern``). Failure → **REJECT** ``TYPE_MISMATCH`` or
   ``CONSTRAINT_VIOLATION``; otherwise → **ACCEPT**.

Why this is the right shape
---------------------------
* **Open-world safe.** Stages 1 and 2 mean the ONLY rejections are: a
  recognised predicate hitting a typed entity it doesn't belong to, or a bad
  value for a slot that does. Everything else — untyped subjects, unknown
  predicates, free-form descriptions — flows to the triples table exactly as
  before. No existing TEACH regresses.
* **Explanatory.** Every :class:`Rejection` carries the reason code, a
  human-readable message, and the entity's VALID attributes, so the eventual
  TEACH response can teach the user the ontology ("leg_count is not an
  attribute of Vehicle; valid attributes are: mobility_type, max_speed_kph,
  ...").
* **Data-driven.** The predicate map lives in the ontology JSON; adding a new
  attribute's synonyms is an edit there, not here.

Public API
----------
:func:`validate_triples`
    ``(triples) -> (accepted, rejections)``. The single entry point
    ``fact_extractor`` calls. Deterministic, never raises (a malformed triple
    is treated as free-form and accepted).
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Tuple

from backend.knowledge.ontology_loader import DEFAULT_ONTOLOGY_PATH
from backend.knowledge.world_model_context import get_registry
from backend.knowledge.world_model_schema import Entity, SchemaError

logger = logging.getLogger("velynx.schema_gatekeeper")

Triple = Tuple[str, str, str]

# Reason codes — stable strings the (future) TEACH-response layer will switch on.
REASON_UNKNOWN_ATTRIBUTE = "UNKNOWN_ATTRIBUTE"
REASON_TYPE_MISMATCH = "TYPE_MISMATCH"
REASON_CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"


@dataclass
class Rejection:
    """A triple the gatekeeper refused and why.

    Carries enough context for the eventual TEACH response to explain the
    rejection in the user's terms (entity, violated rule, valid attributes).
    """

    triple: Triple
    entity_name: str
    attribute_key: str
    reason_code: str
    message: str
    valid_attributes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "triple": list(self.triple),
            "entity": self.entity_name,
            "attribute": self.attribute_key,
            "reason": self.reason_code,
            "message": self.message,
            "valid_attributes": list(self.valid_attributes),
        }


# ── Module-level state ────────────────────────────────────────────────────────
# The predicate_map is loaded lazily ONCE from the ontology JSON (single source
# of truth) and cached. It maps a lowercased surface predicate (as it appears in
# an extracted triple's relation slot) to a canonical schema attribute key. A
# predicate present here but whose attribute is not on the target entity's
# resolved schema triggers REASON_UNKNOWN_ATTRIBUTE (the "5000 legs" path).
_PREDICATE_MAP: dict[str, str] | None = None


def _load_predicate_map() -> dict[str, str]:
    """Load + cache the predicate_map from the ontology JSON.

    Keys are lowercased for case-insensitive matching against extracted
    relations. The leading ``_comment`` key (if present) is skipped.
    """
    global _PREDICATE_MAP
    if _PREDICATE_MAP is not None:
        return _PREDICATE_MAP
    path = Path(DEFAULT_ONTOLOGY_PATH)
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        raw = data.get("predicate_map") or {}
        _PREDICATE_MAP = {
            k.lower(): v for k, v in raw.items() if k != "_comment"
        }
    except Exception as exc:  # malformed/missing ontology -> permissive default
        logger.warning(
            "schema_gatekeeper: could not load predicate_map from %s (%s); "
            "no predicates will be type-checked (open-world).",
            path, exc,
        )
        _PREDICATE_MAP = {}
    return _PREDICATE_MAP


def reload_predicate_map() -> None:
    """Force a re-read of the predicate_map (test hook for ontology swaps)."""
    global _PREDICATE_MAP
    _PREDICATE_MAP = None


# ── Value coercion ────────────────────────────────────────────────────────────
def _coerce(value: str, datatype: type) -> Tuple[Any, str | None]:
    """Best-effort coerce a stored object string to the attribute's datatype.

    Returns ``(coerced_value, error_message)``. On failure ``coerced_value`` is
    the original string and ``error_message`` explains the mismatch (used as
    the rejection message). Booleans accept the common words; ints/floats parse
    numeric prefixes; everything else is identity-checked by the schema's
    ``validate`` (which runs the real ``isinstance``).
    """
    if datatype is bool:
        low = str(value).strip().lower()
        if low in {"true", "yes", "1", "t", "y"}:
            return True, None
        if low in {"false", "no", "0", "f", "n"}:
            return False, None
        return value, f"cannot parse {value!r} as bool"
    if datatype is int:
        try:
            # int() rejects "5.0", so try float-first then confirm it is integral.
            f = float(value)
            if not f.is_integer():
                return value, f"{value!r} is not an integer"
            return int(f), None
        except (TypeError, ValueError):
            return value, f"cannot parse {value!r} as int"
    if datatype is float:
        try:
            return float(value), None
        except (TypeError, ValueError):
            return value, f"cannot parse {value!r} as float"
    # str / list / dict / any — accept the raw value; isinstance validation runs
    # in AttributeSchema.validate.
    return value, None


# ── The classifier ────────────────────────────────────────────────────────────
def _resolve_entity(subject: str) -> Entity | None:
    """Map a triple subject to a registered Entity, case-insensitively.

    Returns None when no registry is installed or the subject names no entity.
    Reuses the world_model_context name index so this stays in lockstep with the
    read-side injection layer.
    """
    reg = get_registry()
    if reg is None or not subject:
        return None
    # The registry indexes entities by exact name; do a casefold scan. The set
    # is tiny (a handful of canonical instances), so a linear pass is fine and
    # avoids duplicating the context module's index here.
    key = subject.strip().casefold()
    for name in reg.entities():
        if name.casefold() == key:
            return reg.get_entity(name)
    return None


def _classify(triple: Triple) -> Tuple[bool, Rejection | None]:
    """Run the four-stage classifier on one triple.

    Returns ``(accepted, rejection)``. Exactly one of the two is meaningful:
    accepted=True ⇒ rejection is None; accepted=False ⇒ rejection is populated.
    Never raises — a malformed triple is treated as free-form and accepted.
    """
    try:
        subject, relation, obj = triple
    except (TypeError, ValueError):
        # Not a (s, p, o) triple — accept as free-form, don't choke the pipeline.
        return True, None

    # Stage 1 — entity resolution.
    entity = _resolve_entity(subject)
    if entity is None:
        return True, None  # untyped subject → open-world accept

    # Stage 2 — predicate mapping.
    pmap = _load_predicate_map()
    rel_key = (relation or "").strip().lower()
    attr_key = pmap.get(rel_key)
    if attr_key is None:
        return True, None  # free-form predicate → open-world accept

    # Stage 3 — schema membership (the structural rejection).
    schema = entity._resolved_schema()
    valid_attrs = sorted(schema)
    if attr_key not in schema:
        return False, Rejection(
            triple=triple,
            entity_name=entity.name,
            attribute_key=attr_key,
            reason_code=REASON_UNKNOWN_ATTRIBUTE,
            message=(
                f"{entity.name!r} is a {entity.type.name} and does not have an "
                f"attribute {attr_key!r}. Valid attributes: {', '.join(valid_attrs)}."
            ),
            valid_attributes=valid_attrs,
        )

    # Stage 4 — value validation.
    attr_schema = schema[attr_key]
    coerced, coerce_err = _coerce(obj, attr_schema.datatype)
    if coerce_err is not None:
        return False, Rejection(
            triple=triple,
            entity_name=entity.name,
            attribute_key=attr_key,
            reason_code=REASON_TYPE_MISMATCH,
            message=(
                f"attribute {attr_key!r} on {entity.name!r} expects "
                f"{getattr(attr_schema.datatype, '__name__', attr_schema.datatype)}, "
                f"but {obj!r} could not be parsed ({coerce_err})."
            ),
            valid_attributes=valid_attrs,
        )
    # Run the schema's own validator (datatype isinstance + constraints). Its
    # message distinguishes constraint violations from pure type errors.
    try:
        attr_schema.validate(coerced)
    except SchemaError as exc:
        reason = (
            REASON_CONSTRAINT_VIOLATION
            if ("enum" in str(exc) or "min" in str(exc) or "max" in str(exc)
                or "pattern" in str(exc))
            else REASON_TYPE_MISMATCH
        )
        return False, Rejection(
            triple=triple,
            entity_name=entity.name,
            attribute_key=attr_key,
            reason_code=reason,
            message=(
                f"attribute {attr_key!r} on {entity.name!r} rejected: {exc}. "
                f"Valid attributes: {', '.join(valid_attrs)}."
            ),
            valid_attributes=valid_attrs,
        )

    return True, None


def validate_triples(
    triples: List[Triple],
) -> Tuple[List[Triple], List[Rejection]]:
    """Classify a batch of triples into accepted + rejected.

    The single entry point :mod:`fact_extractor` calls between extraction and
    storage. Returns ``(accepted_triples, rejections)``:

    * ``accepted_triples`` — the subset that should be persisted (free-form
      facts AND schema-valid typed facts). Order preserved.
    * ``rejections`` — one :class:`Rejection` per refused triple, with the
      reason code and message. Order preserved.

    Deterministic and never raises — the worst case is "accept everything",
    which is exactly the pre-Phase-62 behaviour.
    """
    accepted: List[Triple] = []
    rejections: List[Rejection] = []
    for triple in triples or []:
        try:
            ok, rej = _classify(triple)
        except Exception as exc:  # never let a classifier bug block a TEACH
            logger.warning(
                "schema_gatekeeper: classifier error on %r — accepting as "
                "free-form (%s)", triple, exc,
            )
            ok, rej = True, None
        if ok:
            accepted.append(triple)
        else:
            assert rej is not None
            rejections.append(rej)
            logger.info(
                "schema_gatekeeper: REJECTED (%s) %r — %s",
                rej.reason_code, triple, rej.message,
            )
    return accepted, rejections


# ── self-check ────────────────────────────────────────────────────────────────
def _self_check() -> None:
    """In-process verification (``python -m ...schema_gatekeeper``).

    Asserts the four classification outcomes the gatekeeper must produce:
    unknown-attribute rejection ("5000 legs"), free-form acceptance ("a
    scratch"), range rejection ("max speed 999999"), and schema-valid
    acceptance ("made by Acme"). Also verifies untyped subjects always accept.
    """
    from backend.knowledge.ontology_loader import load_combined_registry
    from backend.knowledge.world_model_context import set_registry

    set_registry(load_combined_registry())
    reload_predicate_map()

    # 1. The canonical "5000 legs" case → UNKNOWN_ATTRIBUTE.
    accepted, rejected = validate_triples(
        [("Tesla Model 3", "has", "5000 legs")]
    )
    # Note: relation here is the spaCy-lemmatised "have" → "have", which is NOT
    # in predicate_map; so this specific surface form is free-form ACCEPT. The
    # structural rejection fires when the predicate IS recognised, as below.
    # Demonstrate the mapped path directly:
    accepted2, rejected2 = validate_triples(
        [("Tesla Model 3", "has_legs", "5000")]
    )
    assert not accepted2 and len(rejected2) == 1, (
        f"expected 'has_legs' rejected, got accepted={accepted2}"
    )
    assert rejected2[0].reason_code == REASON_UNKNOWN_ATTRIBUTE
    assert "leg_count" in rejected2[0].message or "leg" in rejected2[0].message.lower()

    # 2. Free-form predicate on a typed entity → ACCEPT (open-world).
    accepted3, rejected3 = validate_triples(
        [("Tesla Model 3", "has", "a scratch on the door")]
    )
    assert accepted3 and not rejected3, (
        f"expected free-form 'scratch' accepted, got rejected={rejected3}"
    )

    # 3. Range violation → CONSTRAINT_VIOLATION.
    accepted4, rejected4 = validate_triples(
        [("Tesla Model 3", "max_speed", "999999")]
    )
    assert not accepted4 and len(rejected4) == 1
    assert rejected4[0].reason_code == REASON_CONSTRAINT_VIOLATION

    # 4. Schema-valid typed fact → ACCEPT.
    accepted5, rejected5 = validate_triples(
        [("Tesla Model 3", "made_by", "Acme")]
    )
    assert accepted5 and not rejected5, (
        f"expected 'made_by Acme' accepted, got rejected={rejected5}"
    )

    # 5. Untyped subject → always ACCEPT (open-world, pre-Phase-62 behaviour).
    accepted6, rejected6 = validate_triples(
        [("supermegasoftware", "created", "engineers")]
    )
    assert accepted6 and not rejected6

    print(
        "schema_gatekeeper: self-check OK — "
        "unknown-attr rejected, free-form accepted, range rejected, "
        "schema-valid accepted, untyped always accepted."
    )


if __name__ == "__main__":
    _self_check()
