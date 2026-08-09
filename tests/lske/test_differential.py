"""Adversarial acceptance tests for the D-01…D-04 remediation.

The invariant these tests exist to hold is:

    RAW_VALIDATOR_RESULT == PUBLIC_VALIDATE_RESULT

for every payload, mutated or not. `validate` may enrich how a failure is
represented, but it may never convert schema-invalid into valid (D-01) and never
schema-valid into invalid. Everything else here is a consequence of that:
pointers must resolve (D-02), keywords must name real schema assertions (D-03),
and the frozen-leaf predicate must not reject values the schemas admit (D-04).
"""

from __future__ import annotations

import copy
import re
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from tests.lske._synth import all_valid_payloads, valid_payload
from v2.lske.errors import OntologyError, SchemaViolation
from v2.lske.schema import (
    _APPLICATORS,
    _REGISTRY,
    _SCHEMA_BY_ID,
    EVIDENCE_DIRECTIONS,
    LskeRecord,
    _discharge,
    _leaf_assertion_errors,
    all_schemas,
    validate,
)

_SCHEMAS = all_schemas()
_NAMES = sorted(_SCHEMAS)

# RF-01 cl. 3 item 3: the value space is the assertion keywords as written in the
# schema, plus exactly three names that are not schema keywords.
_NON_KEYWORD_VALUES = frozenset({"required", "additionalProperties", "frozen"})
_LEGAL_KEYWORDS = (
    frozenset(
        {
            "type",
            "enum",
            "const",
            "pattern",
            "minLength",
            "maxLength",
            "minimum",
            "maximum",
            "minItems",
            "maxItems",
            "uniqueItems",
            "minProperties",
            "maxProperties",
            "propertyNames",
            "unevaluatedProperties",
            "items",
        }
    )
    | _NON_KEYWORD_VALUES
)


def _raw_valid(payload: Any, name: str) -> bool:
    return Draft202012Validator(_SCHEMAS[name], registry=_REGISTRY).is_valid(payload)


def _public_failures(payload: Any, name: str) -> list[tuple[str, str, str, bool]] | None:
    """`None` when `validate` accepts; the normalized failure list otherwise."""
    try:
        validate(payload, name)
    except SchemaViolation as exc:
        return list(exc.failures)
    return None


def _assert_agrees(payload: Any, name: str, label: str) -> list[tuple[str, str, str, bool]] | None:
    raw_ok = _raw_valid(payload, name)
    failures = _public_failures(payload, name)
    assert raw_ok == (failures is None), (
        f"{label}: raw validator says {'valid' if raw_ok else 'invalid'} but "
        f"validate() says {'valid' if failures is None else 'invalid'}"
    )
    return failures


# --------------------------------------------------------------------------
# Baselines
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", _NAMES)
def test_every_entry_surface_has_a_raw_valid_baseline(name):
    """The mutation corpus is only meaningful if the unmutated payload is valid."""
    errors = list(
        Draft202012Validator(_SCHEMAS[name], registry=_REGISTRY).iter_errors(valid_payload(name))
    )
    assert errors == [], [f"/{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in errors]


@pytest.mark.parametrize("name", _NAMES)
def test_validate_accepts_every_valid_baseline(name):
    validate(valid_payload(name), name)


def test_all_23_surfaces_are_covered():
    assert len(_NAMES) == 23
    assert len(all_valid_payloads()) == 23


# --------------------------------------------------------------------------
# D-01 — the silent-accept class
# --------------------------------------------------------------------------


@pytest.mark.parametrize("relation_type", ["supports", "refutes", "contradicts", "validated_by"])
def test_null_direction_on_every_evidential_relation_type_is_reported(relation_type):
    """RB-02 cl. 2. The `not`-based encoding made all four of these silently valid."""
    payload = valid_payload("relation")
    payload["type"] = relation_type
    payload["direction"] = None
    failures = _assert_agrees(payload, "relation", f"{relation_type}/null-direction")
    assert failures is not None, f"{relation_type} with direction=null was accepted"
    assert any(item[0] == "/direction" for item in failures), failures
    assert all(item[2] not in _APPLICATORS for item in failures), failures


@pytest.mark.parametrize("relation_type", ["supports", "refutes", "contradicts", "validated_by"])
def test_string_null_remains_a_legal_direction(relation_type):
    """`EVIDENCE_DIRECTIONS` contains the string "null", distinct from JSON null."""
    assert "null" in EVIDENCE_DIRECTIONS
    payload = valid_payload("relation")
    payload["type"] = relation_type
    payload["direction"] = "null"
    validate(payload, "relation")


@pytest.mark.parametrize("relation_type", ["supports", "refutes", "contradicts", "validated_by"])
def test_non_enum_direction_is_rejected_on_evidential_types(relation_type):
    """The old `{"not": {"type": "null"}}` form admitted `direction: 42`."""
    payload = valid_payload("relation")
    payload["type"] = relation_type
    payload["direction"] = 42
    assert _assert_agrees(payload, "relation", f"{relation_type}/int-direction") is not None


def test_applicator_with_no_reportable_leaf_fails_closed():
    """A failure with no legal representation must raise, never vanish.

    This is the durable half of the D-01 fix. `{"not": {...}}` is the canonical
    producer of an applicator error whose `context` is empty: there is no child
    assertion to report, because the child *succeeded*. Before the fix this
    returned `[]` and the failure disappeared.

    N18-E1 moved the point of enforcement without weakening it: the descent
    collects the childless site instead of raising at it, and the site is
    discharged against the co-located failures once they are all known. Here
    there are none, so it is uncovered and must still fail closed.
    """
    probe = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"x": {"not": {"type": "null"}}},
    }
    errors = list(Draft202012Validator(probe).iter_errors({"x": None}))
    assert len(errors) == 1 and errors[0].validator == "not", errors
    assert not errors[0].context, "probe did not produce an empty-context applicator"

    childless: list = []
    assert _leaf_assertion_errors(errors[0], childless) == []
    assert [error.validator for error in childless] == ["not"]
    with pytest.raises(OntologyError, match="unrepresentable failure"):
        _discharge(childless, raw=[])


def test_leaf_assertion_errors_passes_through_plain_assertions():
    """The fail-closed guard must not fire on ordinary reportable failures."""
    probe = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "properties": {"x": {"type": "string"}},
    }
    errors = list(Draft202012Validator(probe).iter_errors({"x": 1}))
    childless: list = []
    assert [error.validator for error in _leaf_assertion_errors(errors[0], childless)] == ["type"]
    assert childless == []


def test_oneof_with_two_matches_also_fails_closed():
    """The second empty-context producer: `oneOf` satisfied by more than one branch."""
    probe = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "oneOf": [{"type": "integer"}, {"minimum": 0}],
    }
    errors = list(Draft202012Validator(probe).iter_errors(1))
    assert len(errors) == 1 and errors[0].validator == "oneOf", errors
    assert not errors[0].context
    childless: list = []
    assert _leaf_assertion_errors(errors[0], childless) == []
    with pytest.raises(OntologyError, match="unrepresentable failure"):
        _discharge(childless, raw=[])


def test_childless_site_is_discharged_by_a_co_located_reported_failure():
    """N18-E1: a childless site co-located with a real assertion is represented.

    `items: false` is the third empty-context producer and the one N18-E1 was
    raised against. It never travels alone in the frozen schemas: a `maxItems`
    bound sits beside it and is perfectly reportable. The caller is told the
    instance is invalid and where, no applicator keyword is named (RF-01 cl. 3
    item 3), and nothing is discarded.
    """
    probe = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "array",
        "prefixItems": [{"type": "number"}, {"type": "number"}],
        "items": False,
        "maxItems": 2,
    }
    errors = list(Draft202012Validator(probe).iter_errors([1.0, 2.0, 3.0]))
    childless: list = []
    leaves = [leaf for error in errors for leaf in _leaf_assertion_errors(error, childless)]
    assert [error.validator for error in childless] == ["items"]
    assert [leaf.validator for leaf in leaves] == ["maxItems"]
    # The co-located `maxItems` covers the site, so the discharge is silent.
    _discharge(childless, raw=[("", "", "maxItems")])


# --------------------------------------------------------------------------
# D-02 — resource-aware, resolvable pointers
# --------------------------------------------------------------------------


_MISSING = object()


def _resolve_pointer(pointer: str) -> Any:
    """Walk an emitted `<$id>#<RFC6901>` pointer back to the keyword it names.

    Returns `_MISSING` if the pointer does not resolve. A resolved value of
    `None` is legitimate — `{"const": null}` is a real assertion — so absence
    must be signalled out-of-band rather than by returning `None`.
    """
    resource_id, _, fragment = pointer.partition("#")
    if resource_id not in _SCHEMA_BY_ID:
        return _MISSING
    node: Any = _SCHEMA_BY_ID[resource_id]
    for token in (t for t in fragment.split("/") if t):
        token = token.replace("~1", "/").replace("~0", "~")
        try:
            node = node[int(token)] if isinstance(node, list) else node[token]
        except (KeyError, IndexError, TypeError, ValueError):
            return _MISSING
    return node


# --------------------------------------------------------------------------
# Mutation corpus — Section 7
# --------------------------------------------------------------------------


def _first_key(payload: dict[str, Any], schema_name: str) -> str | None:
    required = _SCHEMAS[schema_name].get("required") or []
    for key in required:
        if key in payload:
            return key
    return next(iter(payload), None)


def _mutations(payload: dict[str, Any], name: str):
    """Yield `(label, mutated_payload)` across the eleven mutation families."""
    schema = _SCHEMAS[name]

    key = _first_key(payload, name)
    if key is not None:
        removed = copy.deepcopy(payload)
        del removed[key]
        yield f"remove-required:{key}", removed

    unknown = copy.deepcopy(payload)
    unknown["undeclared_key_zzz"] = True
    yield "add-unknown", unknown

    if key is not None:
        retyped = copy.deepcopy(payload)
        retyped[key] = [] if not isinstance(payload[key], list) else "not-a-list"
        yield f"replace-scalar-type:{key}", retyped

    for prop, sub in _iter_leaf_props(payload, schema, name):
        if "enum" in sub or "const" in sub:
            broken = copy.deepcopy(payload)
            broken[prop] = "__not_a_member__"
            yield f"replace-enum:{prop}", broken
            break

    for prop in payload:
        if payload[prop] is not None and _forbids_null(schema, name, prop):
            nulled = copy.deepcopy(payload)
            nulled[prop] = None
            yield f"null-forbidden:{prop}", nulled
            break

    for prop, value in payload.items():
        if isinstance(value, dict) and value:
            nested = copy.deepcopy(payload)
            nested[prop] = {**value, "undeclared_nested_zzz": True}
            yield f"break-nested-object:{prop}", nested
            break

    for prop, value in payload.items():
        if isinstance(value, list) and value:
            arrayed = copy.deepcopy(payload)
            arrayed[prop] = [*value, {"undeclared_item_zzz": True}]
            yield f"break-array-item:{prop}", arrayed
            break

    for prop, value in payload.items():
        if isinstance(value, dict) and value and all(isinstance(v, dict) for v in value.values()):
            mapped = copy.deepcopy(payload)
            mapped[prop] = {**value, "extra_map_key": "not-an-object"}
            yield f"break-map-value:{prop}", mapped
            break

    # Conditional / allOf-branch breakage, per surface.
    if name == "relation":
        broken = copy.deepcopy(payload)
        broken["type"] = "supports"
        yield "break-conditional:evidential-direction", broken
    if name == "observations":
        broken = copy.deepcopy(payload)
        broken["value"] = None
        yield "break-conditional:value-null", broken
        interval = copy.deepcopy(payload)
        interval["uncertainty"] = {**payload["uncertainty"], "kind": "ci95"}
        yield "break-conditional:interval-required", interval
    if name == "datasets":
        broken = copy.deepcopy(payload)
        broken["leakage_audit"] = {**payload["leakage_audit"], "audited": True}
        yield "break-conditional:leakage-audited", broken
    if name == "experiments":
        broken = copy.deepcopy(payload)
        broken["lifecycle"] = {**payload["lifecycle"], "status": "Executed"}
        yield "break-conditional:executed-requires", broken
    if name == "decisions":
        broken = copy.deepcopy(payload)
        broken["action"] = "revise"
        yield "break-conditional:action-requires-evidence", broken
    if name not in {"relation", "obs2"}:
        broken = copy.deepcopy(payload)
        broken["immutability"] = {**payload["immutability"], "frozen_at": _TS_INVALID}
        yield "break-conditional:frozen-requires-seal", broken
        branch = copy.deepcopy(payload)
        branch["id"] = "ZZZ-9999-9999"
        yield "break-allof-branch:id-prefix", branch
        nested_ref = copy.deepcopy(payload)
        nested_ref["created"] = {**payload["created"], "at": "not-a-timestamp"}
        yield "break-nested-ref:created.at", nested_ref
        not_branch = copy.deepcopy(payload)
        not_branch["lifecycle"] = {
            **payload["lifecycle"],
            "transitions": [{**payload["lifecycle"]["transitions"][0], "from": "ACTIVE"}],
        }
        yield "break-not-branch:illegal-transition", not_branch


_TS_INVALID = "2026-08-02T00:00:00Z"


def _iter_leaf_props(payload, schema, name):
    props = schema.get("properties", {})
    if not props:
        for branch in schema.get("allOf", []):
            ref = branch.get("$ref", "")
            if ref.startswith("#/$defs/"):
                props = schema["$defs"][ref.split("/")[-1]].get("properties", {})
                break
    for prop in payload:
        sub = props.get(prop)
        if isinstance(sub, dict):
            yield prop, sub


def _forbids_null(schema, name, prop) -> bool:
    for _, sub in _iter_leaf_props({prop: None}, schema, name):
        declared = sub.get("type")
        if isinstance(declared, str) and declared != "null":
            return True
        if isinstance(declared, list):
            return "null" not in declared
    return False


def _mutation_cases() -> list[tuple[str, str, dict[str, Any]]]:
    cases: list[tuple[str, str, dict[str, Any]]] = []
    for name in _NAMES:
        for label, mutated in _mutations(valid_payload(name), name):
            cases.append((name, label, mutated))
    return cases


# `_RAW_CASES` stays unpackable for the aggregate coverage assertions; `_CASES`
# is the parametrization view, where each tuple is wrapped in a `pytest.param`.
_RAW_CASES = _mutation_cases()
_CASES = [
    pytest.param(name, label, payload, id=f"{name}::{label}") for name, label, payload in _RAW_CASES
]


@pytest.mark.parametrize("name,label,payload", _CASES)
def test_raw_and_public_validators_agree_on_every_mutation(name, label, payload):
    """D-01: the public validator may never disagree with the raw one on validity."""
    _assert_agrees(payload, name, f"{name}::{label}")


@pytest.mark.parametrize("name,label,payload", _CASES)
def test_every_emitted_pointer_resolves_and_names_its_keyword(name, label, payload):
    """D-02: `<$id>#<RFC6901>`, resolvable against the registered schema graph."""
    failures = _public_failures(payload, name)
    if failures is None:
        pytest.skip("mutation left the payload valid")
    for instance_pointer, schema_pointer, keyword, _ in failures:
        assert re.fullmatch(
            r"https://p1\.local/schemas/lske/[a-z0-9_]+\.schema\.json#(/.*)?", schema_pointer
        ), f"{name}::{label}: malformed schema pointer {schema_pointer!r}"
        node = _resolve_pointer(schema_pointer)
        assert (
            node is not _MISSING
        ), f"{name}::{label}: {schema_pointer!r} does not resolve against the schema graph"
        # The final pointer segment must be the keyword that was reported, except
        # for the three non-keyword values RF-01 cl. 3 item 3 admits.
        if keyword not in _NON_KEYWORD_VALUES:
            assert (
                schema_pointer.split("/")[-1] == keyword
            ), f"{name}::{label}: pointer {schema_pointer!r} does not end in {keyword!r}"
        assert instance_pointer == "" or instance_pointer.startswith("/"), instance_pointer


@pytest.mark.parametrize("name,label,payload", _CASES)
def test_no_emitted_keyword_is_outside_the_frozen_vocabulary(name, label, payload):
    """D-03: no invented vocabulary, and never an applicator (R9-15)."""
    failures = _public_failures(payload, name)
    if failures is None:
        pytest.skip("mutation left the payload valid")
    for _, _, keyword, _ in failures:
        assert keyword not in _APPLICATORS, f"{name}::{label}: applicator {keyword!r} reported"
        assert keyword in _LEGAL_KEYWORDS, f"{name}::{label}: illegal keyword {keyword!r}"


@pytest.mark.parametrize("name,label,payload", _CASES)
def test_failure_lists_are_normalized_and_deterministic(name, label, payload):
    """RF-01: deduped, sorted by (derived, instance, schema, keyword), stable."""
    first = _public_failures(payload, name)
    if first is None:
        pytest.skip("mutation left the payload valid")
    assert first == _public_failures(payload, name), f"{name}::{label} is not deterministic"
    assert len(first) == len(set(first)), f"{name}::{label} contains duplicates"
    assert first == sorted(first, key=lambda item: (item[3], item[0], item[1], item[2]))


def test_the_corpus_actually_exercises_every_surface_and_family():
    surfaces = {name for name, _, _ in _RAW_CASES}
    assert surfaces == set(_NAMES), sorted(set(_NAMES) - surfaces)
    families = {label.split(":")[0] for _, label, _ in _RAW_CASES}
    assert {
        "remove-required",
        "add-unknown",
        "replace-scalar-type",
        "replace-enum",
        "null-forbidden",
        "break-conditional",
        "break-allof-branch",
        "break-not-branch",
        "break-nested-ref",
        "break-nested-object",
        "break-array-item",
        "break-map-value",
    } <= families, sorted(families)


def test_at_least_one_mutation_per_surface_is_actually_rejected():
    """A corpus that silently leaves everything valid would prove nothing."""
    rejected = {
        name for name, _, payload in _RAW_CASES if _public_failures(payload, name) is not None
    }
    assert rejected == set(_NAMES), sorted(set(_NAMES) - rejected)


# `record` is the shared envelope fragment, not an entry surface a caller writes
# to. Two mutations are legitimately accepted there, and pinning them keeps the
# skips in the corpus explained rather than merely tolerated:
#
#   add-unknown            `record` carries neither `additionalProperties` nor
#                          `unevaluatedProperties` — closure is the collection
#                          schema's job (§9.13.1, asserted by
#                          test_collection_composition_and_record_fragment_closure).
#   break-allof-branch     `#/$defs/record_id` is `^[A-Z]{3,5}-[0-9]{4}-[0-9]{4}$`,
#                          which `ZZZ-9999-9999` satisfies. The per-collection
#                          narrowing to `^HYP-…` is what rejects it, and that is
#                          exercised on all 22 collection surfaces.
_EXPECTED_ACCEPTED = frozenset(
    {("record", "add-unknown"), ("record", "break-allof-branch:id-prefix")}
)


def test_exactly_the_expected_mutations_are_accepted():
    """Freeze the accepted set: a new silent accept elsewhere must fail loudly."""
    accepted = {
        (name, label)
        for name, label, payload in _RAW_CASES
        if _public_failures(payload, name) is None
    }
    assert accepted == _EXPECTED_ACCEPTED, {
        "unexpectedly accepted": sorted(accepted - _EXPECTED_ACCEPTED),
        "no longer accepted": sorted(_EXPECTED_ACCEPTED - accepted),
    }


def test_the_record_fragment_delegates_closure_to_its_collections():
    """Why `record::add-unknown` is accepted, asserted rather than asserted-by-comment."""
    record = _SCHEMAS["record"]
    assert "additionalProperties" not in record
    assert "unevaluatedProperties" not in record
    # Every collection that composes it does close, so the leak is not reachable
    # through any surface a caller actually writes to.
    for name in _NAMES:
        if name in {"record", "relation", "obs2"}:
            continue
        assert _SCHEMAS[name]["unevaluatedProperties"] is False, name
        payload = valid_payload(name)
        payload["undeclared_key_zzz"] = True
        assert _public_failures(payload, name) is not None, name


def test_the_generic_record_id_pattern_is_narrowed_by_every_collection():
    """Why `record::break-allof-branch:id-prefix` is accepted."""
    assert _SCHEMAS["record"]["$defs"]["record_id"]["pattern"] == r"^[A-Z]{3,5}-[0-9]{4}-[0-9]{4}$"
    for name in _NAMES:
        if name in {"record", "relation", "obs2"}:
            continue
        payload = valid_payload(name)
        payload["id"] = "ZZZ-9999-9999"
        failures = _public_failures(payload, name)
        assert failures is not None, f"{name} did not narrow the generic record_id pattern"
        assert any(item[0] == "/id" and item[2] == "pattern" for item in failures), failures


# --------------------------------------------------------------------------
# D-04 — the frozen leaf predicate
# --------------------------------------------------------------------------


class _StrSubclass(str):
    pass


class _IntSubclass(int):
    pass


class _FloatSubclass(float):
    pass


def test_frozen_predicate_accepts_str_subclasses():
    """RF-05 cl. 2.1: a leaf is None or an *instance* of str/bool/int/float.

    `type(value) in {...}` rejected every subclass. A `str` subclass is
    schema-valid (jsonschema checks `isinstance`), so the pre-fix code produced a
    payload that `validate` accepted but the freeze check reported as unfrozen.
    """
    payload = {**valid_payload("hypotheses"), "title": _StrSubclass("subclassed title")}
    record = LskeRecord.from_payload(payload, "hypotheses")
    assert record.payload["title"] == "subclassed title"


@pytest.mark.parametrize(
    "value", [_StrSubclass("x"), True, False, 0, 1, 1.5, _IntSubclass(3), _FloatSubclass(2.5), None]
)
def test_frozen_leaf_predicate_admits_every_scalar_instance(value):
    """Directly exercise the predicate over scalars, subclasses, and None."""
    from v2.lske.schema import _frozen_failure

    assert _frozen_failure(value, "/probe") is None, f"{value!r} ({type(value).__name__}) rejected"


@pytest.mark.parametrize("value", [[], {}, set(), object()])
def test_frozen_leaf_predicate_still_rejects_non_scalars(value):
    """The widening must not turn the predicate into a no-op."""
    from v2.lske.schema import _frozen_failure

    assert _frozen_failure(value, "/probe") == "/probe"


def test_from_payload_output_is_always_accepted_by_the_constructor():
    """`from_payload` must not be able to build a value `LskeRecord` itself rejects."""
    for name in _NAMES:
        payload = valid_payload(name)
        record = LskeRecord.from_payload(payload, name)
        # Reconstructing from the already-frozen payload must not raise.
        LskeRecord(record.collection_key, record.payload)


def test_subclass_leaves_survive_the_full_from_payload_roundtrip():
    """End-to-end: subclassed scalars must not trip the deep-freeze audit."""
    payload = valid_payload("hypotheses")
    payload["title"] = _StrSubclass("subclassed title")
    payload["record_version"] = _IntSubclass(payload["record_version"])
    record = LskeRecord.from_payload(payload, "hypotheses")
    LskeRecord(record.collection_key, record.payload)
