"""Stage-1 schema generation and composition acceptance tests."""

import json
from pathlib import Path
from types import MappingProxyType

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from v2.lske.errors import OntologyError
from v2.lske.schema import COLLECTION_SPECS, all_schemas, collection_schema, record_schema

ROOT = Path(__file__).parents[2]
SCHEMA_DIR = ROOT / "schemas" / "lske"


def _serialized(schema):
    return (json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def test_exactly_23_generated_schema_files_are_byte_identical_to_canonical_state():
    schemas = all_schemas()
    assert len(schemas) == 23
    assert list(schemas) == ["record", *(spec.key for spec in COLLECTION_SPECS), "relation", "obs2"]
    expected_names = []
    for name, schema in schemas.items():
        filename = "record.schema.json" if name == "record" else f"{name}.schema.json"
        expected_names.append(filename)
        path = SCHEMA_DIR / filename
        assert path.read_bytes() == _serialized(schema)
    assert sorted(path.name for path in SCHEMA_DIR.glob("*.schema.json")) == sorted(expected_names)


def test_draft_compilation_and_complete_offline_resolution():
    schemas = all_schemas()
    registry = Registry()
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    for schema in schemas.values():
        validator = Draft202012Validator(schema, registry=registry)
        list(validator.iter_errors({}))
    datasets_uri = schemas["datasets"]["$id"]
    validator = Draft202012Validator({"$ref": f"{datasets_uri}#/$defs/splits"}, registry=registry)
    assert not list(validator.iter_errors({"train": {"digest": "0" * 64, "record_count": 1}}))


def test_collection_composition_and_record_fragment_closure():
    record = record_schema()
    assert "additionalProperties" not in record
    assert "unevaluatedProperties" not in record
    for spec in COLLECTION_SPECS:
        schema = collection_schema(spec.key)
        assert schema["allOf"] == [{"$ref": "record.schema.json"}, {"$ref": "#/$defs/collection"}]
        assert schema["unevaluatedProperties"] is False
        assert "additionalProperties" not in schema
        assert "$dynamicRef" not in json.dumps(schema)


def test_accessor_isolation_and_mutable_values():
    first = all_schemas()
    second = all_schemas()
    assert isinstance(first, MappingProxyType)
    assert first == second and first is not second
    with pytest.raises(TypeError):
        first["new"] = {}
    first["record"]["title"] = "mutated"
    assert all_schemas()["record"]["title"] != "mutated"
    one = record_schema()
    two = record_schema()
    assert one == two and one is not two


def test_unknown_collection_is_an_ontology_error():
    with pytest.raises(OntologyError):
        collection_schema("unknown")


def _walk_schemas(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_schemas(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_schemas(value)


def test_all_objects_use_only_the_three_frozen_closure_forms():
    for name, schema in all_schemas().items():
        for node in _walk_schemas(schema):
            if node.get("type") != "object":
                continue
            is_collection = name not in {"record", "relation", "obs2"}
            is_collection_top = is_collection and node is schema
            collection = schema["$defs"]["collection"] if is_collection else None
            is_collection_fragment = is_collection and node is collection
            is_envelope_narrowing = is_collection and any(
                node is collection["properties"].get(key)
                for key in ("confidence", "immutability", "lifecycle", "authority", "provenance")
            )
            is_record_top = name == "record" and node is schema
            is_observatory_payload = name == "obs2" and node == {"type": "object"}
            if is_record_top or is_observatory_payload or is_envelope_narrowing:
                continue
            if is_collection_top:
                assert node.get("unevaluatedProperties") is False
                assert "additionalProperties" not in node
            elif is_collection_fragment:
                assert "additionalProperties" not in node
                assert set(node["required"]) <= set(node["properties"])
            elif "propertyNames" in node:
                assert "additionalProperties" in node
                assert node.get("minProperties", 0) >= 1
            else:
                assert node.get("additionalProperties") is False
                assert set(node.get("required", ())) == set(node.get("properties", ()))


def test_collection_conditionals_do_not_introduce_undeclared_properties():
    for spec in COLLECTION_SPECS:
        collection = collection_schema(spec.key)["$defs"]["collection"]
        declared = set(collection["properties"])
        for conditional in collection.get("allOf", []):
            assert set(conditional.get("then", {}).get("required", ())) <= declared
            for branch in ("if", "then", "else"):
                introduced = set(conditional.get(branch, {}).get("properties", ()))
                assert introduced <= declared


def test_catalogue_ownership_and_count_is_exact():
    schemas = all_schemas()
    owners = {
        "record": [
            "created",
            "revision",
            "provenance",
            "citation",
            "source_path",
            "authority",
            "confidence",
            "scope",
            "dimensions",
            "dimension",
            "lifecycle",
            "transition",
            "immutability",
        ],
        "protocols": ["freeze", "sesoi"],
        "runs": ["admissibility", "environment"],
        "observations": ["uncertainty", "coverage", "declared_null_comparison"],
        "datasets": ["generator", "leakage_audit", "splits", "split"],
        "theories": ["risky_prediction"],
        "decisions": ["dissent"],
        "evidence": ["unexcluded_alternative"],
        "sessions": ["annotation"],
        "relation": ["record_version_at"],
        "obs2": ["payload_object"],
    }
    fixed_defs = 0
    for owner, names in owners.items():
        for name in names:
            assert name in schemas[owner]["$defs"]
            fixed_defs += 1
    assert fixed_defs == 30  # N-01..N-29 plus N-31; N-23 is map-keyed rather than fixed-key.
    assert schemas["datasets"]["$defs"]["splits"]["propertyNames"] == {
        "pattern": r"^[a-z][a-z0-9_]{0,31}$"
    }  # N-23
    assert schemas["obs2"]["additionalProperties"] is False  # N-30
    assert schemas["obs2"]["$defs"]["payload_object"] == {"type": "object"}  # N-31
    overlays = schemas["obs2"]["properties"]["overlays"]
    assert overlays["minProperties"] == overlays["maxProperties"] == 8  # N-32
    assert fixed_defs + 2 == 32  # N-30 and N-32 are the only inline catalogue entries.
