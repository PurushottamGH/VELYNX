"""Stage-1 envelope, relation, OBS/2, immutable model and event tests."""

import json
from types import MappingProxyType

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

import v2.lske
from ros.admissibility import Tier, Verdict
from v2.lske import events
from v2.lske.errors import LskeError, OntologyError, SchemaViolation
from v2.lske.schema import (
    ONTOLOGY_VERSION,
    _APPLICATORS,
    _SCHEMA_BY_ID,
    LskeRecord,
    admissibility_payload,
    all_schemas,
    content_hash,
    edge_state,
    seal,
    validate,
)

TS = "2026-08-02T00:00:00Z"
HEX = "0" * 64


def base_record(key="hypotheses"):
    from v2.lske.schema import COLLECTION_SPEC_BY_KEY, DIMENSION_KEYS

    spec = COLLECTION_SPEC_BY_KEY[key]
    confidence = None
    if spec.primitive == "Claim":
        confidence = {
            "level": None,
            "scope": None,
            "dimensions": {
                name: {"state": "unassessed", "evidence_ids": []} for name in DIMENSION_KEYS
            },
        }
    return {
        "id": f"{spec.prefix}-2026-0001",
        "type": spec.object_type,
        "primitive": spec.primitive,
        "title": "test",
        "record_version": 1,
        "ontology_version": ONTOLOGY_VERSION,
        "content_hash": HEX,
        "created": {"at": TS, "by": "tester", "authority": "ENGINEER", "target": "repo.test"},
        "revisions": [],
        "supersedes": None,
        "superseded_by": None,
        "provenance": {
            "kind": "human_assertion",
            "run_ids": [],
            "protocol_id": None,
            "source_paths": [],
            "citation": None,
            "derivation": None,
        },
        "authority": {
            "write_target": "repo.test",
            "committed_by": "tester",
            "is_human": False,
            "escalated_from": None,
        },
        "confidence": confidence,
        "lifecycle": {
            "state": "CANDIDATE",
            "status": "Proposed" if key == "hypotheses" else "Candidate",
            "transitions": [
                {
                    "from": None,
                    "to": "CANDIDATE",
                    "at": TS,
                    "by": "tester",
                    "event_id": "LEV-" + "a" * 32,
                    "cause": "test",
                }
            ],
        },
        "immutability": {"append_only": spec.append_only, "frozen_at": None, "seal": None},
    }


def valid_hypothesis():
    record = base_record()
    record.update(
        {
            "statement": "A falsifiable statement",
            "falsifier": "A failed observation",
            "question_id": "RQS-2026-0001",
            "mechanism_ids": [],
            "discriminates_from": [],
            "scope": {"population": "P1", "regime": "test", "environment_ids": [], "limits": []},
        }
    )
    return record


def valid_relation(kind="supports"):
    return {
        "from": "EVD-2026-0001",
        "to": "HYP-2026-0001",
        "type": kind,
        "direction": (
            "supports" if kind in {"supports", "refutes", "contradicts", "validated_by"} else None
        ),
        "semantic_note": "test",
        "established_by": "DEC-2026-0001",
        "established_at": TS,
        "record_version_at": {"source": 1, "target": 1},
        "retracted_by": None,
        "confidence_basis": "evidence",
    }


def test_valid_record_and_multiple_failure_payload():
    record = valid_hypothesis()
    validate(record, "hypotheses")
    record["statement"] = ""
    record["scope"]["population"] = ""
    with pytest.raises(SchemaViolation) as caught:
        validate(record, "hypotheses")
    failures = caught.value.failures
    assert failures and all(type(item) is tuple and len(item) == 4 for item in failures)
    assert failures == tuple(
        sorted(set(failures), key=lambda item: (item[3], item[0], item[1], item[2]))
    )
    assert all(item[2] not in {"allOf", "oneOf", "if", "then", "$ref"} for item in failures)
    assert any(item[2] == "unevaluatedProperties" and item[3] for item in failures)


def test_genuine_undeclared_key_is_primary_closure_failure():
    record = valid_hypothesis()
    record["undeclared"] = True
    with pytest.raises(SchemaViolation) as caught:
        validate(record, "hypotheses")
    assert any(
        item[2] == "unevaluatedProperties" and item[3] is False for item in caught.value.failures
    )


def test_record_hashing_immutability_and_constructor_predicate():
    payload = valid_hypothesis()
    computed = content_hash(payload)
    payload["content_hash"] = computed
    record = LskeRecord.from_payload(payload, "hypotheses")
    assert record.content_hash == computed
    assert record.stored_content_hash == computed
    mutable = record.as_dict()
    mutable["title"] = "changed"
    assert record.payload["title"] == "test"
    clone = LskeRecord(record.collection_key, record.payload)
    assert clone == record
    with pytest.raises(SchemaViolation) as caught:
        LskeRecord("hypotheses", payload)
    assert caught.value.failures == (("", "", "frozen", False),)
    assert LskeRecord("hypotheses", MappingProxyType({})).payload == {}
    with pytest.raises(SchemaViolation) as nested:
        LskeRecord("hypotheses", MappingProxyType({"a": []}))
    assert nested.value.failures == (("/a", "", "frozen", False),)


def test_block_h_excluded_from_scientific_hash_but_in_structural_identity():
    first = valid_hypothesis()
    first["content_hash"] = content_hash(first)
    second = json.loads(json.dumps(first))
    second["immutability"] = {
        "append_only": True,
        "frozen_at": TS,
        "seal": seal(first["content_hash"], TS),
    }
    a = LskeRecord.from_payload(first, "hypotheses")
    b = LskeRecord.from_payload(second, "hypotheses")
    assert a.content_hash == b.content_hash
    assert a != b
    assert hash(a) != hash(b)


def test_relation_contract_and_edge_state():
    relation = valid_relation()
    validate(relation, "relation")
    relation["post_hoc"] = False
    with pytest.raises(SchemaViolation):
        validate(relation, "relation")
    for kind in list(all_schemas()["relation"]["properties"]["type"]["enum"])[4:]:
        item = valid_relation(kind)
        validate(item, "relation")
    active = {"lifecycle": {"state": "ACTIVE"}}
    candidate = {"lifecycle": {"state": "CANDIDATE"}}
    dormant = {"lifecycle": {"state": "DORMANT"}}
    assert edge_state(valid_relation(), active, active) == "ACTIVE"
    assert edge_state(valid_relation(), active, candidate) == "CANDIDATE"
    assert edge_state(valid_relation(), active, dormant) == "DORMANT"
    retracted = valid_relation()
    retracted["retracted_by"] = "DEC-2026-0002"
    assert edge_state(retracted, candidate, dormant) == "DELETED"


def test_obs2_closes_its_top_level_but_not_observatory_payload_interiors():
    payload = {
        "schema": "obs/2",
        "plate": "V01",
        "phase": "test",
        "subject": "HYP-2026-0001",
        "cause": "unattributed",
        "zoom_level": 1,
        "primitive": "Claim",
        "nodes": [{"observatory_owned": {"anything": True}}],
        "edges": [{}],
        "overlays": {f"overlay_{i}": {"anything": i} for i in range(8)},
        "store_content_hash": HEX,
        "snapshot_id": None,
        "governance_banner": None,
    }
    validate(payload, "obs2")
    payload["extra"] = True
    with pytest.raises(SchemaViolation):
        validate(payload, "obs2")


def test_admissibility_mapping_is_exact():
    verdict = Verdict(Tier.EXPLORATORY, reasons=("reason",), ceilings=("ceiling",))
    assert admissibility_payload(verdict) == {
        "admissible": True,
        "tier": "exploratory-admissible",
        "ceiling": ["ceiling"],
        "reasons": ["reason"],
    }


def _registry():
    registry = Registry()
    for schema in all_schemas().values():
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def _catalogue_cases():
    dims = {
        name: {"state": "unassessed", "evidence_ids": []}
        for name in all_schemas()["record"]["$defs"]["dimensions"]["required"]
    }
    transition = {
        "from": None,
        "to": "CANDIDATE",
        "at": TS,
        "by": "tester",
        "event_id": "LEV-" + "a" * 32,
        "cause": "create",
    }
    return [
        (
            "N-01",
            "record",
            "#/$defs/created",
            {"at": TS, "by": "tester", "authority": "ENGINEER", "target": "repo.test"},
        ),
        (
            "N-02",
            "record",
            "#/$defs/revision",
            {
                "record_version": 1,
                "at": TS,
                "by": "tester",
                "authority": "ENGINEER",
                "target": "repo.test",
                "change_kind": "create",
                "rationale": "test",
                "prior_content_hash": None,
            },
        ),
        (
            "N-03",
            "record",
            "#/$defs/provenance",
            {
                "kind": "human_assertion",
                "run_ids": [],
                "protocol_id": None,
                "source_paths": [],
                "citation": None,
                "derivation": None,
            },
        ),
        (
            "N-04",
            "record",
            "#/$defs/citation",
            {"kind": "doi", "identifier": "10/x", "title": "test", "year": None},
        ),
        ("N-05", "record", "#/$defs/source_path", {"path": "a.txt", "content_hash": HEX}),
        (
            "N-06",
            "record",
            "#/$defs/authority",
            {
                "write_target": "repo.test",
                "committed_by": "tester",
                "is_human": False,
                "escalated_from": None,
            },
        ),
        (
            "N-07",
            "record",
            "#/$defs/confidence",
            {"level": None, "scope": None, "dimensions": dims},
        ),
        (
            "N-08",
            "record",
            "#/$defs/scope",
            {"population": "P1", "regime": "test", "environment_ids": [], "limits": []},
        ),
        ("N-09", "record", "#/$defs/dimensions", dims),
        ("N-10", "record", "#/$defs/dimension", {"state": "unassessed", "evidence_ids": []}),
        (
            "N-11",
            "record",
            "#/$defs/lifecycle",
            {"state": "CANDIDATE", "status": "Candidate", "transitions": [transition]},
        ),
        ("N-12", "record", "#/$defs/transition", transition),
        (
            "N-13",
            "record",
            "#/$defs/immutability",
            {"append_only": True, "frozen_at": None, "seal": None},
        ),
        (
            "N-14",
            "protocols",
            "#/$defs/freeze",
            {
                "protocol_id": "P1",
                "digest": HEX,
                "source": "p.yaml",
                "frozen_at_commit": None,
                "algorithm": "blake2b-256-canonical-json",
            },
        ),
        (
            "N-15",
            "protocols",
            "#/$defs/sesoi",
            {"value": 1.0, "units": "score", "metric_id": "MET-2026-0001"},
        ),
        (
            "N-16",
            "runs",
            "#/$defs/admissibility",
            {"admissible": False, "tier": "inadmissible", "ceiling": [], "reasons": ["reason"]},
        ),
        ("N-17", "runs", "#/$defs/environment", {"python": "3.13", "platform": "test", "ci": ""}),
        (
            "N-18",
            "observations",
            "#/$defs/uncertainty",
            {"kind": "none", "interval": None, "n": None, "method": "not quantified"},
        ),
        (
            "N-19",
            "observations",
            "#/$defs/coverage",
            {"measured": 1, "expected": 1, "missing_reason": None},
        ),
        (
            "N-20",
            "observations",
            "#/$defs/declared_null_comparison",
            {"declared_null": "no effect", "outcome": "not_evaluated", "basis": "not run"},
        ),
        (
            "N-21",
            "datasets",
            "#/$defs/generator",
            {
                "seed": None,
                "config_path": "config.yaml",
                "config_digest": HEX,
                "code_version": "abc",
            },
        ),
        (
            "N-22",
            "datasets",
            "#/$defs/leakage_audit",
            {"audited": False, "at": None, "by": None, "findings": []},
        ),
        ("N-23", "datasets", "#/$defs/splits", {"train": {"digest": HEX, "record_count": 0}}),
        ("N-24", "datasets", "#/$defs/split", {"digest": HEX, "record_count": 0}),
        (
            "N-25",
            "theories",
            "#/$defs/risky_prediction",
            {
                "statement": "prediction",
                "observable": "metric",
                "declared_null": "none",
                "established_at": TS,
                "outcome": "unassessed",
            },
        ),
        ("N-26", "decisions", "#/$defs/dissent", {"by": "reviewer", "at": TS, "statement": "none"}),
        (
            "N-27",
            "evidence",
            "#/$defs/unexcluded_alternative",
            {"statement": "alternative", "why_not_excluded": ""},
        ),
        (
            "N-28",
            "sessions",
            "#/$defs/annotation",
            {"at": TS, "target_id": "HYP-2026-0001", "text": "note"},
        ),
        ("N-29", "relation", "#/$defs/record_version_at", {"source": 1, "target": 1}),
        (
            "N-30",
            "obs2",
            "",
            {
                "schema": "obs/2",
                "plate": "V01",
                "phase": "test",
                "subject": "HYP-2026-0001",
                "cause": "unattributed",
                "zoom_level": 1,
                "primitive": "Claim",
                "nodes": [],
                "edges": [],
                "overlays": {f"overlay_{i}": {} for i in range(8)},
                "store_content_hash": HEX,
                "snapshot_id": None,
                "governance_banner": None,
            },
        ),
        ("N-31", "obs2", "#/$defs/payload_object", {}),
        ("N-32", "obs2", "#/properties/overlays", {f"overlay_{i}": {} for i in range(8)}),
    ]


@pytest.mark.parametrize("catalogue_id,owner,pointer,payload", _catalogue_cases())
def test_all_32_catalogue_entries_accept_minimal_legal_payload(
    catalogue_id, owner, pointer, payload
):
    schema = all_schemas()[owner]
    target = schema if pointer == "" else {"$ref": schema["$id"] + pointer}
    assert not list(
        Draft202012Validator(target, registry=_registry()).iter_errors(payload)
    ), catalogue_id


@pytest.mark.parametrize("catalogue_id,owner,pointer,payload", _catalogue_cases())
def test_catalogue_entries_reject_one_undeclared_key_where_lske_owns_closure(
    catalogue_id, owner, pointer, payload
):
    if catalogue_id == "N-31":
        pytest.skip("N-31 interior is Observatory-owned and intentionally unconstrained")
    schema = all_schemas()[owner]
    target = schema if pointer == "" else {"$ref": schema["$id"] + pointer}
    illegal = json.loads(json.dumps(payload))
    illegal["undeclared"] = True
    assert list(
        Draft202012Validator(target, registry=_registry()).iter_errors(illegal)
    ), catalogue_id


def test_cross_value_and_collection_specific_normative_conditions():
    observation = base_record("observations")
    observation.update(
        {
            "run_ids": ["RUN-2026-0001"],
            "metric_id": "MET-2026-0001",
            "value": None,
            "uncertainty": {"kind": "ci95", "interval": [2.0, 1.0], "n": 2, "method": "bootstrap"},
            "coverage": {"measured": 1, "expected": 2, "missing_reason": None},
            "validity": "valid",
            "declared_null_comparison": None,
            "blinded": False,
        }
    )
    with pytest.raises(SchemaViolation) as caught:
        validate(observation, "observations")
    pointers = {item[0] for item in caught.value.failures}
    assert {"/validity", "/coverage/missing_reason"} <= pointers
    # The `value: null` conditional (RB-05 cl. 3) owns both of the above. The
    # ascending-interval rule of N-18 is NOT reported here, and that is the ruled
    # Stage-1 boundary rather than a gap: LSKE v1.1.3 RG-02 splits N-18 into a
    # structural half owned by this schema layer and a semantic half owned by
    # MEM-11 in ros.store._check_memory at Stage 4 (RG-01 cl. 2, RG-03).
    # Reporting an ordering failure here would require a `keyword` outside the
    # RF-01 cl. 3 item 3 value space and would reopen D-03, so `validate` must
    # not invent one. Stage-4 obligation: AC-P1-28.
    assert "/uncertainty/interval" not in pointers

    decision = base_record("decisions")
    decision.update(
        {
            "action": "no_change",
            "subject_ids": ["HYP-2026-0001"],
            "evidence_ids": [],
            "rationale": "no change",
            "alternatives_considered": ["wait"],
            "dissent": [],
            "human_committer": "scientist",
            "propagation_receipt_id": "RCT-test",
        }
    )
    decision["authority"] = {
        "write_target": "repo.test",
        "committed_by": "scientist",
        "is_human": False,
        "escalated_from": None,
    }
    with pytest.raises(SchemaViolation):
        validate(decision, "decisions")

    projected = valid_hypothesis()
    projected["provenance"] = {
        "kind": "projection",
        "run_ids": [],
        "protocol_id": None,
        "source_paths": [],
        "citation": None,
        "derivation": "render",
    }
    with pytest.raises(SchemaViolation):
        validate(projected, "hypotheses")


def _observation_with(uncertainty):
    # A structurally valid `observations` record whose only variable is
    # `uncertainty`, so that a reported failure at /uncertainty/... is
    # attributable to N-18 and to nothing else. `value` is non-null and
    # `coverage` is complete, which keeps the RB-05 cl. 3 conditionals silent.
    observation = base_record("observations")
    observation.update(
        {
            "run_ids": ["RUN-2026-0001"],
            "metric_id": "MET-2026-0001",
            "value": 1.0,
            "uncertainty": uncertainty,
            "coverage": {"measured": 2, "expected": 2, "missing_reason": None},
            "validity": "valid",
            "declared_null_comparison": None,
            "blinded": False,
        }
    )
    return observation


def _n18_failure_pointers(uncertainty):
    try:
        validate(_observation_with(uncertainty), "observations")
    except SchemaViolation as exc:
        return {item[0] for item in exc.failures}
    return set()


# LSKE v1.1.3 RG-02: N-18's structural half is Stage 1's, its ascending half is
# MEM-11's at Stage 4. Every ordering of two numbers is therefore structurally
# valid here, including the descending one -- ordering is not this layer's
# subject. The Stage-4 counterpart is AC-P1-28.
@pytest.mark.parametrize("kind", ["ci95", "iqr"])
@pytest.mark.parametrize("interval", [[1.0, 2.0], [1.0, 1.0], [2.0, 1.0]])
def test_n18_stage1_accepts_every_ordering_of_two_numbers(kind, interval):
    assert _n18_failure_pointers(
        {"kind": kind, "interval": interval, "n": 2, "method": "bootstrap"}
    ) == set()


@pytest.mark.parametrize("kind", ["ci95", "iqr"])
@pytest.mark.parametrize(
    "interval",
    [
        [1.0],
        ["1.0", 2.0],
        [1.0, "2.0"],
        [],
        None,
    ],
)
def test_n18_stage1_rejects_malformed_interval_structure(kind, interval):
    # Structure IS Stage 1's: item count, item type, and the kind-conditional
    # non-nullability of RG-02 cl. 1. Each vector must be reported at or below
    # /uncertainty/interval.
    pointers = _n18_failure_pointers(
        {"kind": kind, "interval": interval, "n": 2, "method": "bootstrap"}
    )
    assert any(
        p == "/uncertainty/interval" or p.startswith("/uncertainty/interval/") for p in pointers
    ), (kind, interval, pointers)


@pytest.mark.parametrize("kind", ["ci95", "iqr"])
def test_n18_stage1_rejects_an_over_long_interval(kind):
    # N18-E1, closed. A three-item interval is a structural failure and RF-01
    # cl. 3 contracts a `SchemaViolation` carrying it. The co-located
    # `maxItems: 2` is the reportable assertion; the childless `items: false`
    # applicator alongside it is discharged against that assertion under
    # §9.5.1 cl. 4 rather than escaping as an unrelated `OntologyError`.
    with pytest.raises(SchemaViolation) as raised:
        validate(
            _observation_with(
                {"kind": kind, "interval": [1.0, 2.0, 3.0], "n": 2, "method": "bootstrap"}
            ),
            "observations",
        )
    failures = raised.value.failures
    assert any(
        pointer == "/uncertainty/interval" and keyword == "maxItems"
        for pointer, _, keyword, _ in failures
    ), failures
    # R9-15 / RF-01 cl. 3: no item may name an applicator keyword.
    assert not [item for item in failures if item[2] in _APPLICATORS], failures


def test_n18e1_over_long_interval_reports_a_resolvable_schema_pointer():
    # RF-01 cl. 3 item 2: every reported schema pointer resolves in the
    # registered graph. The N18-E1 repair must not report a pointer it cannot
    # resolve, which is what D-02 closed for the leaf case.
    with pytest.raises(SchemaViolation) as raised:
        validate(
            _observation_with(
                {"kind": "ci95", "interval": [1.0, 2.0, 3.0], "n": 2, "method": "bootstrap"}
            ),
            "observations",
        )
    for _, schema_pointer, _, _ in raised.value.failures:
        assert schema_pointer, raised.value.failures
        resource_id, _, fragment = schema_pointer.partition("#")
        node = _SCHEMA_BY_ID[resource_id]
        for token in [t for t in fragment.split("/") if t]:
            token = token.replace("~1", "/").replace("~0", "~")
            node = node[int(token)] if isinstance(node, list) else node[token]


@pytest.mark.parametrize("kind", ["none", "sd", "se"])
def test_n18_stage1_requires_null_interval_when_kind_is_not_ci95_or_iqr(kind):
    # RG-02 cl. 1, the `else` branch: null is required, a two-item array is not
    # admissible however it is ordered.
    assert (
        _n18_failure_pointers({"kind": kind, "interval": None, "n": None, "method": "not quantified"})
        == set()
    )
    for interval in ([1.0, 2.0], [2.0, 1.0]):
        assert "/uncertainty/interval" in _n18_failure_pointers(
            {"kind": kind, "interval": interval, "n": 2, "method": "bootstrap"}
        ), (kind, interval)


@pytest.mark.parametrize("kind", ["ci95", "iqr"])
def test_n18_stage1_rejects_null_interval_when_kind_is_ci95_or_iqr(kind):
    assert "/uncertainty/interval" in _n18_failure_pointers(
        {"kind": kind, "interval": None, "n": 2, "method": "bootstrap"}
    )


def event_body(kind="lifecycle"):
    return {
        "kind": kind,
        "at": TS,
        "by": "tester",
        "authority": "ENGINEER",
        "target": "repo.test",
        "record_id": "HYP-2026-0001",
        "from": None,
        "to": "CANDIDATE",
        "cause": "test",
    }


def test_durable_event_writer_is_append_only_and_has_one_public_callable(tmp_path):
    public_callables = [name for name in events.__all__ if callable(getattr(events, name))]
    assert public_callables == ["append_event"]
    first_id = events.append_event(tmp_path, event_body())
    path = tmp_path / ".ros" / "lske_events.jsonl"
    first_bytes = path.read_bytes()
    second_id = events.append_event(tmp_path, event_body())
    assert second_id == first_id
    assert path.read_bytes().startswith(first_bytes)
    assert path.read_bytes().count(b"\n") == 2
    assert json.loads(first_bytes)["event_id"] == first_id
    with pytest.raises(SchemaViolation):
        bad = event_body()
        bad.pop("cause")
        events.append_event(tmp_path, bad)
    with pytest.raises(SchemaViolation):
        bad = event_body()
        bad["extra"] = True
        events.append_event(tmp_path, bad)
    with pytest.raises(OntologyError):
        events.append_event(tmp_path, event_body("third"))


def test_version_ownership_and_validator_ownership():
    assert ONTOLOGY_VERSION == "1.1.2"
    assert not hasattr(v2.lske, "ONTOLOGY_VERSION")
    assert v2.lske.__version__ == "1.1.0"
    assert [name for name in all_schemas()] and validate.__name__ == "validate"
