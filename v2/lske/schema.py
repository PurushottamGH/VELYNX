"""Frozen Project P1-v2 LSKE Stage-1 schemas and pure record utilities."""

from __future__ import annotations

import copy
import hashlib
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from ros.admissibility import Tier, Verdict
from ros.authority import AuthorityClass, ENGINEERING_TARGETS, EVIDENCE_TARGETS
from ros.model import DECISION_ACTIONS, EVIDENCE_DIRECTIONS, HYPOTHESIS_STATUSES, ID_PATTERN
from ros.protocol import canonical_bytes
from v2.lske.errors import OntologyError, SchemaViolation

SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_BASE_URI = "https://p1.local/schemas/lske/"
ONTOLOGY_VERSION = "1.1.2"

PRIMITIVES = (
    "Run",
    "Environment",
    "Tick",
    "Event",
    "Snapshot",
    "Neuron",
    "Kind",
    "Edge",
    "Graph",
    "DelayLine",
    "EpisodicMemory",
    "Ledger",
    "Policy",
    "Intervention",
    "Protocol",
    "Measurement",
    "Claim",
    "Evidence",
    "Decision",
)
DIMENSION_KEYS = (
    "existence",
    "measurement_validity",
    "effect_existence",
    "magnitude",
    "mechanism",
    "robustness",
    "generalisation",
    "necessity_over_simpler",
    "resource_efficiency",
    "observability_completeness",
)
DIMENSION_STATES = (
    "unassessed",
    "assessed_supported",
    "assessed_contested",
    "assessed_failed",
)
LIFECYCLE_STATES = ("CANDIDATE", "ACTIVE", "DORMANT", "TOMBSTONED", "DELETED")
LIFECYCLE_TRANSITIONS = (
    ("CANDIDATE", "ACTIVE"),
    ("ACTIVE", "DORMANT"),
    ("DORMANT", "ACTIVE"),
    ("ACTIVE", "TOMBSTONED"),
    ("DORMANT", "TOMBSTONED"),
    ("TOMBSTONED", "DELETED"),
    ("TOMBSTONED", "ACTIVE"),
    ("CANDIDATE", "DELETED"),
)
CHANGE_KINDS = (
    "create",
    "amend",
    "annotate",
    "status_transition",
    "supersede",
    "tombstone",
    "restore",
    "delete",
)
RELATION_TYPES = (
    "supports",
    "refutes",
    "contradicts",
    "validated_by",
    "generated",
    "observed",
    "measured",
    "derived_from",
    "depends_on",
    "belongs_to",
    "extends",
    "predicts",
    "supersedes",
    "explains",
    "causes",
)
CONFIDENCE_BASES = ("evidence", "human_assertion", "structural")


@dataclass(frozen=True)
class CollectionSpec:
    key: str
    prefix: str
    object_type: str
    primitive: str
    append_only: bool


COLLECTION_SPECS = (
    CollectionSpec("research_questions", "RQS", "research_question", "Claim", False),
    CollectionSpec("hypotheses", "HYP", "hypothesis", "Claim", True),
    CollectionSpec("protocols", "PROT", "protocol", "Protocol", True),
    CollectionSpec("experiments", "EXP", "experiment", "Run", True),
    CollectionSpec("runs", "RUN", "run", "Run", True),
    CollectionSpec("observations", "OBS", "observation", "Measurement", True),
    CollectionSpec("metrics", "MET", "metric", "Measurement", False),
    CollectionSpec("datasets", "DSET", "dataset", "Environment", False),
    CollectionSpec("artifacts", "ART", "artifact", "Snapshot", True),
    CollectionSpec("evidence", "EVD", "evidence", "Evidence", True),
    CollectionSpec("decisions", "DEC", "decision", "Decision", True),
    CollectionSpec("mechanisms", "MEC", "mechanism", "Claim", False),
    CollectionSpec("theories", "THY", "theory", "Claim", False),
    CollectionSpec("assumptions", "ASM", "assumption", "Claim", False),
    CollectionSpec("unknowns", "UNK", "unknown", "Claim", False),
    CollectionSpec("scientific_debt", "SDEBT", "scientific_debt", "Claim", False),
    CollectionSpec("negative_results", "NEG", "negative_result", "Evidence", True),
    CollectionSpec("programs", "PROG", "research_program", "Claim", False),
    CollectionSpec("sessions", "SESS", "research_session", "Intervention", True),
    CollectionSpec("snapshots", "SNAP", "knowledge_snapshot", "Snapshot", True),
)
COLLECTION_SPEC_BY_KEY = MappingProxyType({spec.key: spec for spec in COLLECTION_SPECS})


def _ref(name: str) -> dict[str, str]:
    return {"$ref": name}


def _string(
    *,
    enum: Sequence[str] | None = None,
    pattern: str | None = None,
    minimum_length: int | None = None,
    const: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "string"}
    if enum is not None:
        result["enum"] = list(enum)
    if pattern is not None:
        result["pattern"] = pattern
    if minimum_length is not None:
        result["minLength"] = minimum_length
    if const is not None:
        result["const"] = const
    return result


def _array(
    items: dict[str, Any], *, min_items: int | None = None, unique: bool = False
) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "array", "items": items}
    if min_items is not None:
        result["minItems"] = min_items
    if unique:
        result["uniqueItems"] = True
    return result


def _nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"oneOf": [schema, {"type": "null"}]}


def _present(schema: dict[str, Any]) -> dict[str, Any]:
    # The non-null half of a _nullable() property, for the `then` branch of a
    # conditional that RB-02 cl. 2 / §9.2.4 states as "non-null with a value
    # from <set>". Expressed as the positive assertion the specification names
    # rather than {"not": {"type": "null"}}: a failing `not` is an applicator
    # with no child context, which R9-15 forbids reporting and which therefore
    # cannot be reported at all (D-01).
    return copy.deepcopy(schema)


def _fixed(
    properties: Mapping[str, dict[str, Any]],
    required: Sequence[str] | None = None,
    *,
    all_of: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "object",
        "properties": dict(properties),
        "required": list(required if required is not None else properties),
        "additionalProperties": False,
    }
    if all_of:
        result["allOf"] = all_of
    return result


_RECORD_ID = _ref("record.schema.json#/$defs/record_id")
_HEX64 = _ref("record.schema.json#/$defs/hex64")
_TIMESTAMP = _ref("record.schema.json#/$defs/timestamp")
_NONEMPTY = _string(minimum_length=1)
_STATES = _string(enum=LIFECYCLE_STATES)


def _record_schema() -> dict[str, Any]:
    authority_names = [member.name for member in AuthorityClass]
    write_targets = sorted(EVIDENCE_TARGETS | ENGINEERING_TARGETS)
    dimension = _fixed(
        {
            "state": _string(enum=DIMENSION_STATES),
            "evidence_ids": _array(_ref("#/$defs/record_id")),
        },
        all_of=[
            {
                "if": {
                    "properties": {"state": {"const": "unassessed"}},
                    "required": ["state"],
                },
                "then": {"properties": {"evidence_ids": {"maxItems": 0}}},
                "else": {"properties": {"evidence_ids": {"minItems": 1}}},
            }
        ],
    )
    dimensions = _fixed({key: _ref("#/$defs/dimension") for key in DIMENSION_KEYS})
    transition_pairs = [(None, "CANDIDATE"), *LIFECYCLE_TRANSITIONS]
    transition = _fixed(
        {
            "from": _nullable(_string(enum=LIFECYCLE_STATES)),
            "to": _STATES,
            "at": _ref("#/$defs/timestamp"),
            "by": _NONEMPTY,
            "event_id": _ref("#/$defs/event_id"),
            "cause": _NONEMPTY,
        },
        all_of=[
            {
                "anyOf": [
                    {
                        "properties": {
                            "from": {"const": source},
                            "to": {"const": target},
                        },
                        "required": ["from", "to"],
                    }
                    for source, target in transition_pairs
                ]
            }
        ],
    )
    provenance = _fixed(
        {
            "kind": _string(
                enum=(
                    "human_assertion",
                    "run_derived",
                    "document_derived",
                    "external_literature",
                    "projection",
                )
            ),
            "run_ids": _array(_ref("#/$defs/record_id")),
            "protocol_id": _nullable(_ref("#/$defs/record_id")),
            "source_paths": _array(_ref("#/$defs/source_path")),
            "citation": _nullable(_ref("#/$defs/citation")),
            "derivation": _nullable(_NONEMPTY),
        },
        all_of=[
            {
                "if": {"properties": {"kind": {"const": "run_derived"}}, "required": ["kind"]},
                "then": {"properties": {"run_ids": {"minItems": 1}}},
            },
            {
                "if": {"properties": {"kind": {"const": "document_derived"}}, "required": ["kind"]},
                "then": {"properties": {"source_paths": {"minItems": 1}}},
            },
            {
                "if": {
                    "properties": {"kind": {"const": "external_literature"}},
                    "required": ["kind"],
                },
                "then": {"properties": {"citation": _present(_ref("#/$defs/citation"))}},
            },
            {
                "if": {"properties": {"kind": {"const": "projection"}}, "required": ["kind"]},
                "then": {"properties": {"derivation": _present(_NONEMPTY)}},
            },
        ],
    )
    immutability = _fixed(
        {
            "append_only": {"type": "boolean"},
            "frozen_at": _nullable(_ref("#/$defs/timestamp")),
            "seal": _nullable(_ref("#/$defs/hex64")),
        },
        all_of=[
            {
                "if": {"properties": {"frozen_at": {"type": "null"}}, "required": ["frozen_at"]},
                "then": {"properties": {"seal": {"type": "null"}}},
            },
            {
                "if": {
                    "properties": {"frozen_at": {"not": {"type": "null"}}},
                    "required": ["frozen_at"],
                },
                "then": {"properties": {"seal": _present(_ref("#/$defs/hex64"))}},
            },
        ],
    )
    defs = {
        "record_id": _string(pattern=r"^[A-Z]{3,5}-[0-9]{4}-[0-9]{4}$"),
        "timestamp": _string(
            pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"
        ),
        "semver": _string(pattern=r"^[0-9]+[.][0-9]+[.][0-9]+$"),
        "hex64": _string(pattern=r"^[0-9a-f]{64}$"),
        "write_target": _string(enum=write_targets),
        "authority_class": _string(enum=authority_names),
        "event_id": _string(pattern=r"^LEV-[0-9a-f]{32}$"),
        "created": _fixed(
            {
                "at": _ref("#/$defs/timestamp"),
                "by": _NONEMPTY,
                "authority": _ref("#/$defs/authority_class"),
                "target": _ref("#/$defs/write_target"),
            }
        ),
        "revision": _fixed(
            {
                "record_version": {"type": "integer", "minimum": 1},
                "at": _ref("#/$defs/timestamp"),
                "by": _NONEMPTY,
                "authority": _ref("#/$defs/authority_class"),
                "target": _ref("#/$defs/write_target"),
                "change_kind": _string(enum=CHANGE_KINDS),
                "rationale": _NONEMPTY,
                "prior_content_hash": _nullable(_ref("#/$defs/hex64")),
            }
        ),
        "provenance": provenance,
        "citation": _fixed(
            {
                "kind": _string(enum=("doi", "arxiv", "isbn", "url", "report")),
                "identifier": _NONEMPTY,
                "title": _NONEMPTY,
                "year": _nullable({"type": "integer"}),
            }
        ),
        "source_path": _fixed({"path": _NONEMPTY, "content_hash": _ref("#/$defs/hex64")}),
        "authority": _fixed(
            {
                "write_target": _ref("#/$defs/write_target"),
                "committed_by": _NONEMPTY,
                "is_human": {"type": "boolean"},
                "escalated_from": _nullable(_ref("#/$defs/write_target")),
            },
            all_of=[
                {
                    "if": {
                        "properties": {"write_target": {"enum": sorted(EVIDENCE_TARGETS)}},
                        "required": ["write_target"],
                    },
                    "then": {"properties": {"is_human": {"const": True}}},
                }
            ],
        ),
        "confidence": _fixed(
            {
                "level": _nullable({"type": "integer", "minimum": 0, "maximum": 5}),
                "scope": _nullable(_ref("#/$defs/scope")),
                "dimensions": _ref("#/$defs/dimensions"),
            }
        ),
        "scope": _fixed(
            {
                "population": _NONEMPTY,
                "regime": _NONEMPTY,
                "environment_ids": _array(_ref("#/$defs/record_id")),
                "limits": _array(_NONEMPTY),
            }
        ),
        "dimensions": dimensions,
        "dimension": dimension,
        "lifecycle": _fixed(
            {
                "state": _STATES,
                "status": _NONEMPTY,
                "transitions": _array(_ref("#/$defs/transition"), min_items=1),
            }
        ),
        "transition": transition,
        "immutability": immutability,
    }
    properties = {
        "id": _ref("#/$defs/record_id"),
        "type": _NONEMPTY,
        "primitive": _string(enum=PRIMITIVES),
        "title": _NONEMPTY,
        "record_version": {"type": "integer", "minimum": 1},
        "ontology_version": _ref("#/$defs/semver"),
        "content_hash": _ref("#/$defs/hex64"),
        "created": _ref("#/$defs/created"),
        "revisions": _array(_ref("#/$defs/revision")),
        "supersedes": _nullable(_ref("#/$defs/record_id")),
        "superseded_by": _nullable(_ref("#/$defs/record_id")),
        "provenance": _ref("#/$defs/provenance"),
        "authority": _ref("#/$defs/authority"),
        "confidence": _nullable(_ref("#/$defs/confidence")),
        "lifecycle": _ref("#/$defs/lifecycle"),
        "immutability": _ref("#/$defs/immutability"),
    }
    return {
        "$schema": SCHEMA_DRAFT,
        "$id": SCHEMA_BASE_URI + "record.schema.json",
        "title": "LSKE universal record envelope",
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "$defs": defs,
    }


def _collection_fields(
    key: str,
) -> tuple[dict[str, Any], list[str], list[dict[str, Any]], dict[str, Any]]:
    rid = _RECORD_ID
    arr_id = lambda min_items=None: _array(rid, min_items=min_items)
    sarr = lambda min_items=None: _array(_NONEMPTY, min_items=min_items)
    fields: dict[str, tuple[dict[str, Any], list[str]]] = {
        "research_questions": (
            {
                "question": _NONEMPTY,
                "decision_value": _string(
                    enum=("changes_roadmap", "changes_design", "changes_measurement", "none")
                ),
                "program_id": rid,
                "hypothesis_ids": arr_id(),
                "resolved_by": _nullable(rid),
            },
            ["question", "decision_value", "program_id", "hypothesis_ids", "resolved_by"],
        ),
        "hypotheses": (
            {
                "statement": _NONEMPTY,
                "falsifier": _NONEMPTY,
                "question_id": rid,
                "mechanism_ids": arr_id(),
                "discriminates_from": arr_id(),
                "scope": _ref("record.schema.json#/$defs/scope"),
            },
            [
                "statement",
                "falsifier",
                "question_id",
                "mechanism_ids",
                "discriminates_from",
                "scope",
            ],
        ),
        "protocols": (
            {
                "path": _NONEMPTY,
                "digest": _HEX64,
                "freeze": _ref("#/$defs/freeze"),
                "hypothesis_ids": arr_id(1),
                "intent": _string(enum=("exploratory", "confirmatory")),
                "determinism_tier": _string(enum=("D0", "D1", "D2")),
                "stopping_rule": _NONEMPTY,
                "sesoi": _ref("#/$defs/sesoi"),
                "exclusion_rules": sarr(),
                "declared_null": _NONEMPTY,
                "frozen_before_first_run": {"type": "boolean"},
            },
            [
                "path",
                "digest",
                "freeze",
                "hypothesis_ids",
                "intent",
                "determinism_tier",
                "stopping_rule",
                "sesoi",
                "exclusion_rules",
                "declared_null",
                "frozen_before_first_run",
            ],
        ),
        "experiments": (
            {
                "protocol_id": rid,
                "run_ids": arr_id(),
                "validity": _string(enum=("valid", "invalid", "partially_valid")),
                "invalidity_reason": _NONEMPTY,
                "hypothesis_ids": arr_id(1),
                "observation_ids": arr_id(),
                "evidence_ids": arr_id(),
                "treatment_activated": {"type": "boolean"},
                "executions": sarr(),
                "limitations": sarr(),
                "execution_gate": _NONEMPTY,
                "unavailable_primary_metrics": sarr(),
            },
            ["run_ids", "hypothesis_ids"],
        ),
        "runs": (
            {
                "experiment_id": rid,
                "protocol_id": rid,
                "runtime_run_id": _NONEMPTY,
                "manifest_path": _NONEMPTY,
                "manifest_digest": _HEX64,
                "admissibility": _ref("#/$defs/admissibility"),
                "determinism_tier": _string(enum=("D0", "D1", "D2")),
                "event_log_path": _NONEMPTY,
                "artifact_ids": arr_id(),
                "environment": _ref("#/$defs/environment"),
                "clean_checkout": {"type": "boolean"},
            },
            [
                "experiment_id",
                "protocol_id",
                "runtime_run_id",
                "manifest_path",
                "manifest_digest",
                "admissibility",
                "determinism_tier",
                "event_log_path",
                "artifact_ids",
                "environment",
                "clean_checkout",
            ],
        ),
        "observations": (
            {
                "run_ids": arr_id(1),
                "metric_id": rid,
                "value": {"type": ["number", "string", "null"]},
                "uncertainty": _ref("#/$defs/uncertainty"),
                "coverage": _ref("#/$defs/coverage"),
                "validity": _string(enum=("valid", "invalid", "unavailable")),
                "declared_null_comparison": _nullable(_ref("#/$defs/declared_null_comparison")),
                "blinded": {"type": "boolean"},
            },
            [
                "run_ids",
                "metric_id",
                "value",
                "uncertainty",
                "coverage",
                "validity",
                "declared_null_comparison",
                "blinded",
            ],
        ),
        "metrics": (
            {
                "formula": _NONEMPTY,
                "units": _NONEMPTY,
                "direction": _string(enum=("higher_is_better", "lower_is_better", "none")),
                "estimator_version": _ref("record.schema.json#/$defs/semver"),
                "aggregation_rule": _NONEMPTY,
                "declared_null": _NONEMPTY,
                "validity_status": _string(enum=("validated", "provisional", "defective")),
                "known_defects": sarr(),
            },
            [
                "formula",
                "units",
                "direction",
                "estimator_version",
                "aggregation_rule",
                "declared_null",
                "validity_status",
                "known_defects",
            ],
        ),
        "datasets": (
            {
                "content_digest": _HEX64,
                "generator": _nullable(_ref("#/$defs/generator")),
                "leakage_audit": _ref("#/$defs/leakage_audit"),
                "splits": _ref("#/$defs/splits"),
                "provenance_reliability": _string(
                    enum=("reconstructable", "archived", "legacy_uncertain", "unrecoverable")
                ),
            },
            ["content_digest", "generator", "leakage_audit", "splits", "provenance_reliability"],
        ),
        "artifacts": (
            {
                "run_id": rid,
                "path": _NONEMPTY,
                "digest": _HEX64,
                "kind": _string(
                    enum=(
                        "manifest",
                        "metrics",
                        "events",
                        "checkpoint",
                        "log",
                        "figure",
                        "inventory",
                    )
                ),
                "integrity": _string(enum=("verified", "failed", "absent")),
                "retention": _string(enum=("permanent", "evidence_bearing", "transient")),
            },
            ["run_id", "path", "digest", "kind", "integrity", "retention"],
        ),
        "evidence": (
            {
                "source_observation_ids": arr_id(1),
                "run_ids": arr_id(1),
                "target_id": rid,
                "direction": _string(enum=sorted(EVIDENCE_DIRECTIONS)),
                "dimensions": _array(_string(enum=DIMENSION_KEYS), min_items=1, unique=True),
                "eligibility": _string(
                    enum=("exploratory-admissible", "confirmatory-admissible", "ineligible")
                ),
                "assumptions_relied_upon": _array(
                    {
                        "oneOf": [
                            _string(pattern=r"^ASM-[0-9]{4}-[0-9]{4}$"),
                            {"const": "none_declared"},
                        ]
                    },
                    min_items=1,
                ),
                "unexcluded_alternatives": _array(_ref("#/$defs/unexcluded_alternative")),
                "rationale": _NONEMPTY,
                "independence_group": _NONEMPTY,
            },
            [
                "source_observation_ids",
                "run_ids",
                "target_id",
                "direction",
                "dimensions",
                "eligibility",
                "assumptions_relied_upon",
                "unexcluded_alternatives",
                "rationale",
                "independence_group",
            ],
        ),
        "decisions": (
            {
                "action": _string(enum=sorted(DECISION_ACTIONS)),
                "subject_ids": arr_id(1),
                "evidence_ids": arr_id(),
                "rationale": _NONEMPTY,
                "scope_after": _nullable(_ref("record.schema.json#/$defs/scope")),
                "level_after": _nullable({"type": "integer", "minimum": 0, "maximum": 5}),
                "alternatives_considered": sarr(1),
                "dissent": _array(_ref("#/$defs/dissent")),
                "human_committer": _NONEMPTY,
                "propagation_receipt_id": _NONEMPTY,
            },
            [
                "action",
                "subject_ids",
                "evidence_ids",
                "rationale",
                "alternatives_considered",
                "dissent",
                "human_committer",
                "propagation_receipt_id",
            ],
        ),
        "mechanisms": (
            {
                "statement": _NONEMPTY,
                "hypothesis_ids": arr_id(1),
                "bundled_with": arr_id(),
                "identifiability": _string(enum=("identified", "bundled", "unidentified")),
                "operability": _string(enum=("demonstrated", "undemonstrated", "failed")),
            },
            ["statement", "hypothesis_ids", "bundled_with", "identifiability", "operability"],
        ),
        "theories": (
            {
                "statement": _NONEMPTY,
                "constituent_hypothesis_ids": arr_id(),
                "integrated_principle": _nullable(_NONEMPTY),
                "risky_prediction": _nullable(_ref("#/$defs/risky_prediction")),
                "outperforms": arr_id(),
            },
            [
                "statement",
                "constituent_hypothesis_ids",
                "integrated_principle",
                "risky_prediction",
                "outperforms",
            ],
        ),
        "assumptions": (
            {
                "statement": _NONEMPTY,
                "load_bearing_for": arr_id(1),
                "test_status": _string(enum=("untested", "supported", "opposed", "refuted")),
                "opposing_evidence_ids": arr_id(),
                "failure_consequence": _NONEMPTY,
            },
            [
                "statement",
                "load_bearing_for",
                "test_status",
                "opposing_evidence_ids",
                "failure_consequence",
            ],
        ),
        "unknowns": (
            {
                "statement": _NONEMPTY,
                "expected_decision_value": _string(
                    enum=("changes_roadmap", "changes_design", "changes_measurement", "none")
                ),
                "blocks_ids": arr_id(),
                "cheapest_resolving_experiment": _nullable(_NONEMPTY),
            },
            ["statement", "expected_decision_value", "blocks_ids", "cheapest_resolving_experiment"],
        ),
        "scientific_debt": (
            {
                "statement": _NONEMPTY,
                "severity": _string(
                    enum=(
                        "blocks_validation",
                        "blocks_program_decision",
                        "scientific_stop",
                        "advisory",
                    )
                ),
                "blocks_ids": arr_id(),
                "discharge_condition": _NONEMPTY,
                "incurred_by": arr_id(),
            },
            ["statement", "severity", "blocks_ids", "discharge_condition", "incurred_by"],
        ),
        "negative_results": (
            {
                "statement": _NONEMPTY,
                "hypothesis_id": rid,
                "scope": _ref("record.schema.json#/$defs/scope"),
                "equivalence_established": {"type": "boolean"},
                "retry_prohibited": {"type": "boolean"},
                "evidence_ids": arr_id(1),
            },
            [
                "statement",
                "hypothesis_id",
                "scope",
                "equivalence_established",
                "retry_prohibited",
                "evidence_ids",
            ],
        ),
        "programs": (
            {
                "statement": _NONEMPTY,
                "gate": _string(enum=("G1", "G2", "G3", "G4", "G5")),
                "question_ids": arr_id(),
                "entry_condition": _NONEMPTY,
                "exit_condition": _NONEMPTY,
            },
            ["statement", "gate", "question_ids", "entry_condition", "exit_condition"],
        ),
        "sessions": (
            {
                "actor": _NONEMPTY,
                "opened": _TIMESTAMP,
                "closed": _nullable(_TIMESTAMP),
                "records_touched": arr_id(),
                "annotations": _array(_ref("#/$defs/annotation")),
                "blinding_state": _string(enum=("blinded", "unblinded", "not_applicable")),
            },
            ["actor", "opened", "closed", "records_touched", "annotations", "blinding_state"],
        ),
        "snapshots": (
            {
                "store_content_hash": _HEX64,
                "commit": _NONEMPTY,
                "at": _TIMESTAMP,
                "record_count": {"type": "integer", "minimum": 0},
                "cause": _string(enum=("decision", "gate_run", "scheduled", "manual")),
                "caused_by": _nullable(rid),
            },
            ["store_content_hash", "commit", "at", "record_count", "cause", "caused_by"],
        ),
    }
    props, required = fields[key]
    defs: dict[str, Any] = {}
    conditionals: list[dict[str, Any]] = []
    if key != "snapshots":
        props["provenance"] = {
            "type": "object",
            "properties": {
                "kind": {
                    "enum": [
                        "human_assertion",
                        "run_derived",
                        "document_derived",
                        "external_literature",
                    ]
                }
            },
        }
    if key == "experiments":
        executed_statuses = ("Executed", "Invalidated")
        conditionals.extend(
            [
                {
                    "if": {
                        "properties": {
                            "lifecycle": {
                                "properties": {"status": {"not": {"const": "Designed"}}},
                                "required": ["status"],
                            }
                        },
                        "required": ["lifecycle"],
                    },
                    "then": {"required": ["protocol_id"]},
                },
                {
                    "if": {
                        "properties": {
                            "lifecycle": {
                                "properties": {"status": {"enum": list(executed_statuses)}},
                                "required": ["status"],
                            }
                        },
                        "required": ["lifecycle"],
                    },
                    "then": {
                        "required": [
                            "validity",
                            "observation_ids",
                            "evidence_ids",
                            "treatment_activated",
                        ]
                    },
                },
                {
                    "if": {
                        "properties": {"validity": {"enum": ["invalid", "partially_valid"]}},
                        "required": ["validity"],
                    },
                    "then": {"required": ["invalidity_reason"]},
                },
            ]
        )
    elif key == "observations":
        conditionals.append(
            {
                "if": {
                    "properties": {"value": {"type": "null"}},
                    "required": ["value"],
                },
                "then": {
                    "properties": {
                        "validity": {"const": "unavailable"},
                        "coverage": {"properties": {"missing_reason": _present(_NONEMPTY)}},
                    }
                },
            }
        )
    elif key == "decisions":
        conditionals.extend(
            [
                {
                    "if": {
                        "properties": {"action": {"enum": ["accept_within_scope", "narrow"]}},
                        "required": ["action"],
                    },
                    "then": {"required": ["scope_after"]},
                },
                {
                    "if": {
                        "properties": {"action": {"not": {"const": "no_change"}}},
                        "required": ["action"],
                    },
                    "then": {"properties": {"evidence_ids": {"minItems": 1}}},
                },
            ]
        )
    if key == "protocols":
        defs = {
            "freeze": _fixed(
                {
                    "protocol_id": _NONEMPTY,
                    "digest": _HEX64,
                    "source": _NONEMPTY,
                    "frozen_at_commit": _nullable(_NONEMPTY),
                    "algorithm": {"const": "blake2b-256-canonical-json"},
                }
            ),
            "sesoi": _fixed({"value": {"type": "number"}, "units": _NONEMPTY, "metric_id": rid}),
        }
    elif key == "runs":
        defs = {
            "admissibility": _fixed(
                {
                    "admissible": {"type": "boolean"},
                    "tier": _string(enum=[tier.value for tier in Tier]),
                    "ceiling": sarr(),
                    "reasons": sarr(1),
                }
            ),
            "environment": _fixed({"python": _NONEMPTY, "platform": _NONEMPTY, "ci": _string()}),
        }
    elif key == "observations":
        _interval_schema = {
            "type": "array",
            "prefixItems": [
                {"type": "number"},
                {"type": "number"},
            ],
            "items": False,
            "minItems": 2,
            "maxItems": 2,
        }
        defs = {
            "uncertainty": _fixed(
                {
                    "kind": _string(enum=("none", "sd", "se", "ci95", "iqr")),
                    "interval": _nullable(_interval_schema),
                    "n": _nullable({"type": "integer", "minimum": 1}),
                    "method": _NONEMPTY,
                },
                all_of=[
                    {
                        "if": {
                            "properties": {"kind": {"enum": ["ci95", "iqr"]}},
                            "required": ["kind"],
                        },
                        "then": {"properties": {"interval": _present(_interval_schema)}},
                        "else": {"properties": {"interval": {"type": "null"}}},
                    }
                ],
            ),
            "coverage": _fixed(
                {
                    "measured": {"type": "integer", "minimum": 0},
                    "expected": {"type": "integer", "minimum": 0},
                    "missing_reason": _nullable(_NONEMPTY),
                }
            ),
            "declared_null_comparison": _fixed(
                {
                    "declared_null": _NONEMPTY,
                    "outcome": _string(
                        enum=(
                            "consistent_with_null",
                            "inconsistent_with_null",
                            "indeterminate",
                            "not_evaluated",
                        )
                    ),
                    "basis": _NONEMPTY,
                }
            ),
        }
    elif key == "datasets":
        split = _fixed({"digest": _HEX64, "record_count": {"type": "integer", "minimum": 0}})
        defs = {
            "generator": _fixed(
                {
                    "seed": _nullable({"type": "integer"}),
                    "config_path": _NONEMPTY,
                    "config_digest": _HEX64,
                    "code_version": _NONEMPTY,
                }
            ),
            "leakage_audit": _fixed(
                {
                    "audited": {"type": "boolean"},
                    "at": _nullable(_TIMESTAMP),
                    "by": _nullable(_NONEMPTY),
                    "findings": sarr(),
                },
                all_of=[
                    {
                        "if": {
                            "properties": {"audited": {"const": True}},
                            "required": ["audited"],
                        },
                        "then": {
                            "properties": {
                                "at": _present(_NONEMPTY),
                                "by": _present(_NONEMPTY),
                            }
                        },
                    }
                ],
            ),
            "splits": {
                "type": "object",
                "minProperties": 1,
                "propertyNames": {"pattern": r"^[a-z][a-z0-9_]{0,31}$"},
                "additionalProperties": _ref("#/$defs/split"),
            },
            "split": split,
        }
    elif key == "theories":
        defs = {
            "risky_prediction": _fixed(
                {
                    "statement": _NONEMPTY,
                    "observable": _NONEMPTY,
                    "declared_null": _NONEMPTY,
                    "established_at": _TIMESTAMP,
                    "outcome": _string(enum=DIMENSION_STATES),
                }
            )
        }
    elif key == "decisions":
        defs = {"dissent": _fixed({"by": _NONEMPTY, "at": _TIMESTAMP, "statement": _NONEMPTY})}
    elif key == "evidence":
        defs = {
            "unexcluded_alternative": _fixed(
                {"statement": _NONEMPTY, "why_not_excluded": _string()}
            )
        }
    elif key == "sessions":
        defs = {"annotation": _fixed({"at": _TIMESTAMP, "target_id": rid, "text": _NONEMPTY})}
    return props, required, conditionals, defs


_STATUS_BY_KEY = {
    "research_questions": ("Open", "Partially Answered", "Answered", "Retired", "Superseded"),
    "hypotheses": tuple(sorted(HYPOTHESIS_STATUSES)),
    "experiments": (
        "Designed",
        "Blocked",
        "Blocked Confirmatory",
        "Planned",
        "Executed",
        "Invalidated",
        "Retired",
    ),
    "metrics": ("Active", "Provisional", "Defective", "Retired", "Superseded"),
}
_DEFAULT_STATUS = ("Candidate", "Active", "Dormant", "Tombstoned", "Deleted")


def _collection_schema(spec: CollectionSpec) -> dict[str, Any]:
    props, required, conditionals, defs = _collection_fields(spec.key)
    props = {
        "id": _string(pattern=rf"^{spec.prefix}-[0-9]{{4}}-[0-9]{{4}}$"),
        "type": {"const": spec.object_type},
        "primitive": {"const": spec.primitive},
        "confidence": {"type": "object" if spec.primitive == "Claim" else "null"},
        "immutability": {
            "type": "object",
            "properties": {"append_only": {"const": spec.append_only}},
        },
        "lifecycle": {
            "type": "object",
            "properties": {"status": _string(enum=_STATUS_BY_KEY.get(spec.key, _DEFAULT_STATUS))},
        },
        "legacy_ids": _array(_string()),
        **props,
    }
    if spec.key == "decisions":
        props["authority"] = {
            "type": "object",
            "properties": {
                "write_target": {"const": "skb.decision"},
                "is_human": {"const": True},
            },
        }
    collection: dict[str, Any] = {"type": "object", "properties": props, "required": required}
    if conditionals:
        collection["allOf"] = conditionals
    return {
        "$schema": SCHEMA_DRAFT,
        "$id": SCHEMA_BASE_URI + f"{spec.key}.schema.json",
        "title": spec.key,
        "type": "object",
        "allOf": [{"$ref": "record.schema.json"}, {"$ref": "#/$defs/collection"}],
        "unevaluatedProperties": False,
        "$defs": {"collection": collection, **defs},
    }


def _relation_schema() -> dict[str, Any]:
    evidential = RELATION_TYPES[:4]
    props = {
        "from": _RECORD_ID,
        "to": _RECORD_ID,
        "type": _string(enum=RELATION_TYPES),
        "direction": _nullable(_string(enum=sorted(EVIDENCE_DIRECTIONS))),
        "semantic_note": _NONEMPTY,
        "established_by": _NONEMPTY,
        "established_at": _TIMESTAMP,
        "record_version_at": _ref("#/$defs/record_version_at"),
        "retracted_by": _nullable(_RECORD_ID),
        "confidence_basis": _string(enum=CONFIDENCE_BASES),
    }
    result = _fixed(
        props,
        all_of=[
            {
                "if": {"properties": {"type": {"enum": list(evidential)}}, "required": ["type"]},
                "then": {"properties": {"direction": _present(_string(enum=sorted(EVIDENCE_DIRECTIONS)))}},
                "else": {"properties": {"direction": {"type": "null"}}},
            }
        ],
    )
    result.update(
        {
            "$schema": SCHEMA_DRAFT,
            "$id": SCHEMA_BASE_URI + "relation.schema.json",
            "title": "LSKE relation",
            "$defs": {
                "record_version_at": _fixed(
                    {
                        "source": {"type": "integer", "minimum": 1},
                        "target": {"type": "integer", "minimum": 1},
                    }
                )
            },
        }
    )
    return result


def _obs2_schema() -> dict[str, Any]:
    overlays = {
        "type": "object",
        "minProperties": 8,
        "maxProperties": 8,
        "propertyNames": {"pattern": r"^[a-z][a-z0-9_]{0,31}$"},
        "additionalProperties": {"type": "object"},
    }
    props = {
        "schema": {"const": "obs/2"},
        "plate": _string(pattern=r"^V(0[1-9]|[12][0-9]|3[0-6])$"),
        "phase": _NONEMPTY,
        "subject": _NONEMPTY,
        "cause": _NONEMPTY,
        "zoom_level": {"type": "integer", "minimum": 1, "maximum": 8},
        "primitive": _string(enum=PRIMITIVES),
        "nodes": _array(_ref("#/$defs/payload_object")),
        "edges": _array(_ref("#/$defs/payload_object")),
        "overlays": overlays,
        "store_content_hash": _HEX64,
        "snapshot_id": _nullable(_RECORD_ID),
        "governance_banner": _nullable(_string()),
    }
    result = _fixed(props)
    result.update(
        {
            "$schema": SCHEMA_DRAFT,
            "$id": SCHEMA_BASE_URI + "obs2.schema.json",
            "title": "OBS/2 render payload",
            "$defs": {"payload_object": {"type": "object"}},
        }
    )
    return result


_CANONICAL_RECORD = _record_schema()
_CANONICAL_COLLECTIONS = {spec.key: _collection_schema(spec) for spec in COLLECTION_SPECS}
_CANONICAL_RELATION = _relation_schema()
_CANONICAL_OBS2 = _obs2_schema()
_CANONICAL_SCHEMAS: dict[str, dict[str, Any]] = {
    "record": _CANONICAL_RECORD,
    **_CANONICAL_COLLECTIONS,
    "relation": _CANONICAL_RELATION,
    "obs2": _CANONICAL_OBS2,
}


def record_schema() -> dict[str, Any]:
    return copy.deepcopy(_CANONICAL_RECORD)


def collection_schema(collection_key: str) -> dict[str, Any]:
    try:
        return copy.deepcopy(_CANONICAL_COLLECTIONS[collection_key])
    except KeyError as exc:
        raise OntologyError(f"unknown LSKE collection: {collection_key}") from exc


def relation_schema() -> dict[str, Any]:
    return copy.deepcopy(_CANONICAL_RELATION)


def obs2_schema() -> dict[str, Any]:
    return copy.deepcopy(_CANONICAL_OBS2)


def all_schemas() -> Mapping[str, dict[str, Any]]:
    return MappingProxyType(
        {name: copy.deepcopy(schema) for name, schema in _CANONICAL_SCHEMAS.items()}
    )


def _registry() -> Registry:
    registry = Registry()
    for schema in _CANONICAL_SCHEMAS.values():
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


_REGISTRY = _registry()
_APPLICATORS = frozenset(
    {
        "allOf",
        "anyOf",
        "oneOf",
        "not",
        "if",
        "then",
        "else",
        "properties",
        "patternProperties",
        "items",
        "prefixItems",
        "$ref",
        "$defs",
    }
)


def _pointer(parts: Iterable[Any]) -> str:
    def escape(part: Any) -> str:
        return str(part).replace("~", "~0").replace("/", "~1")

    encoded = [escape(part) for part in parts]
    return "" if not encoded else "/" + "/".join(encoded)


_SCHEMA_BY_ID = MappingProxyType(
    {schema["$id"]: schema for schema in _CANONICAL_SCHEMAS.values()}
)


def _unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _follow_ref(ref: str, resource_id: str) -> tuple[str, list[str], dict[str, Any]]:
    """Resolve one `$ref` against the registered schema graph.

    Returns the `$id` of the resource that now contains the keyword, the RFC 6901
    pointer *from that resource's root*, and the subschema itself. Only the
    canonical dicts are consulted: no private ``jsonschema`` attribute is read.
    """
    uri, _, fragment = ref.partition("#")
    target_id = resource_id if not uri else SCHEMA_BASE_URI + uri
    try:
        node: Any = _SCHEMA_BY_ID[target_id]
    except KeyError as exc:  # pragma: no cover - guarded by test_schema_pointers
        raise OntologyError(f"unregistered schema resource in $ref: {ref}") from exc
    parts = [_unescape(token) for token in fragment.split("/") if token]
    for part in parts:
        try:
            node = node[part]
        except (KeyError, TypeError) as exc:  # pragma: no cover - guarded by tests
            raise OntologyError(f"unresolvable $ref fragment: {ref}") from exc
    return target_id, parts, node


def _schema_pointer_for(error: Any, entry_schema: Mapping[str, Any]) -> str:
    """Build the RF-01 cl. 3 item 2 schema pointer for a leaf assertion error.

    jsonschema 4.25.1 reports ``absolute_schema_path`` in the *entry* schema's
    coordinate space with every ``$ref``/``$defs`` splice point omitted, so the
    raw path dead-ends when walked against the resource that actually contains
    the failing keyword. This walks the registered graph along that path,
    re-basing onto the crossed resource's ``$id`` at each ``$ref``, which is what
    the clause requires and what makes the pointer resolvable.
    """
    resource_id = entry_schema["$id"]
    node: Any = entry_schema
    parts: list[str] = []
    path = [str(token) for token in getattr(error, "absolute_schema_path", error.schema_path)]
    for index, token in enumerate(path):
        # A `$ref` splice point is omitted from the reported path, so cross it
        # whenever the current node cannot itself consume the next token.
        while isinstance(node, Mapping) and "$ref" in node and token not in node:
            resource_id, parts, node = _follow_ref(node["$ref"], resource_id)
        try:
            node = node[int(token)] if isinstance(node, (list, tuple)) else node[token]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise OntologyError(
                "unresolvable schema path for "
                f"{error.validator!r} at {'/'.join(path)!r} (stalled on {token!r} "
                f"after {index} steps in {resource_id})"
            ) from exc
        parts = [*parts, token]
    return f"{resource_id}#{_pointer(parts)}"


def _leaf_assertion_errors(error: Any, childless: list[Any]) -> list[Any]:
    """Descend an error tree to the assertion keywords that actually failed.

    R9-15 (§9.13.3): an applicator is never reported; the subschema assertions
    that failed are reported instead. Under ``jsonschema`` 4.25.1 three of the
    applicators of ``_APPLICATORS`` can fail while reporting no child context at
    all -- ``items`` when its subschema is ``false``, ``not`` when its subschema
    matches, and ``oneOf`` when more than one branch matches. Such an error has
    no legal representation of its own, because RF-01 cl. 3 item 3 forbids
    naming an applicator keyword, and it must never be silently discarded,
    because discarding it can convert schema-invalid into valid (D-01).

    So it is neither reported nor dropped here: it is appended to ``childless``
    and discharged by :func:`validate` against the failure set as a whole, which
    is the only place the co-located assertions are all known. A site that no
    reported failure covers is a genuine defect in the schema and fails closed
    there.
    """
    if error.validator not in _APPLICATORS:
        return [error]
    leaves: list[Any] = []
    for child in error.context or ():
        leaves.extend(_leaf_assertion_errors(child, childless))
    if not leaves:
        childless.append(error)
    return leaves


def _discharge(childless: Iterable[Any], raw: Iterable[tuple[str, str, str]]) -> None:
    """Fail closed on any childless applicator site no reported failure covers.

    A site is *represented* when some reported failure is at or below its
    instance pointer, by the one containment test of §9.5.1 cl. 4: the caller is
    then told which part of the instance is invalid, and the applicator keyword
    RF-01 cl. 3 item 3 forbids naming never enters the payload. A site nothing
    covers has no legal representation and no substitute, so it raises rather
    than being dropped -- dropping it could convert schema-invalid into public
    valid, which is exactly what D-01 closed.

    Sites are sorted before the check so that the one named by the message is a
    function of the failure set alone and not of iteration order (RF-0.2).
    """
    reported = list(raw)
    sites = sorted(
        {
            (
                _pointer(error.absolute_path),
                _pointer(getattr(error, "absolute_schema_path", error.schema_path)),
                str(error.validator),
            )
            for error in childless
        }
    )
    for instance_pointer, schema_path, keyword in sites:
        prefix = instance_pointer + "/"
        if not any(
            pointer == instance_pointer or pointer.startswith(prefix)
            for pointer, _, _ in reported
        ):
            raise OntologyError(
                f"unrepresentable failure: applicator {keyword!r} at instance "
                f"{instance_pointer!r} / schema {schema_path!r} failed with no "
                "reportable child assertion and no co-located reported failure"
            )


def validate(payload: Mapping[str, Any], schema_name: str) -> None:
    try:
        schema = _CANONICAL_SCHEMAS[schema_name]
    except KeyError as exc:
        raise OntologyError(f"unknown LSKE schema: {schema_name}") from exc
    validator = Draft202012Validator(schema, registry=_REGISTRY)
    raw: list[tuple[str, str, str]] = []
    childless: list[Any] = []
    for error in validator.iter_errors(payload):
        for leaf in _leaf_assertion_errors(error, childless):
            raw.append(
                (
                    _pointer(leaf.absolute_path),
                    _schema_pointer_for(leaf, schema),
                    str(leaf.validator),
                )
            )
    raw = list(dict.fromkeys(raw))
    _discharge(childless, raw)
    failures = []
    for instance_pointer, schema_pointer, keyword in raw:
        derived = False
        if keyword == "unevaluatedProperties":
            prefix = instance_pointer + "/" if instance_pointer else "/"
            derived = any(
                other_keyword != "unevaluatedProperties"
                and (other_pointer == instance_pointer or other_pointer.startswith(prefix))
                for other_pointer, _, other_keyword in raw
            )
        failures.append((instance_pointer, schema_pointer, keyword, derived))
    if failures:
        normalized = SchemaViolation("validation failed", failures).failures
        first = normalized[0]
        message = f"{first[0]} {first[1]} {first[2]}"
        raise SchemaViolation(message, normalized)


def canonical_json(payload: Mapping[str, Any]) -> bytes:
    return canonical_bytes(dict(payload))


def content_hash(payload: Mapping[str, Any]) -> str:
    body = {
        key: value for key, value in payload.items() if key not in {"content_hash", "immutability"}
    }
    return hashlib.sha256(canonical_json(body)).hexdigest()


def seal(content_hash_hex: str, frozen_at: str) -> str:
    return hashlib.sha256(
        canonical_json({"content_hash": content_hash_hex, "frozen_at": frozen_at})
    ).hexdigest()


def allocate_record_id(collection_key: str, existing: Iterable[str], year: int) -> str:
    try:
        prefix = COLLECTION_SPEC_BY_KEY[collection_key].prefix
    except KeyError as exc:
        raise OntologyError(f"unknown LSKE collection: {collection_key}") from exc
    pattern = re.compile(rf"^{prefix}-{year:04d}-([0-9]{{4}})$")
    maximum = max(
        (
            int(match.group(1))
            for identifier in existing
            if (match := pattern.fullmatch(identifier))
        ),
        default=0,
    )
    if maximum >= 9999:
        raise OntologyError(f"identifier sequence exhausted for {collection_key} in {year}")
    return f"{prefix}-{year:04d}-{maximum + 1:04d}"


_EVENT_KEYS = ("kind", "at", "by", "authority", "target", "record_id", "from", "to", "cause")


def allocate_event_id(payload: Mapping[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "event_id"}
    if any(key not in body for key in _EVENT_KEYS):
        raise SchemaViolation("event body missing required key", (("", "", "required", False),))
    return "LEV-" + hashlib.sha256(canonical_json(body)).hexdigest()[:32]


def edge_state(
    relation: Mapping[str, Any], source: Mapping[str, Any], target: Mapping[str, Any]
) -> str:
    if relation["retracted_by"] is not None:
        return "DELETED"
    endpoint_states = {source["lifecycle"]["state"], target["lifecycle"]["state"]}
    if "CANDIDATE" in endpoint_states:
        return "CANDIDATE"
    if endpoint_states & {"TOMBSTONED", "DORMANT"}:
        return "DORMANT"
    return "ACTIVE"


def admissibility_payload(verdict: Verdict) -> dict[str, Any]:
    return {
        "admissible": verdict.admissible,
        "tier": verdict.tier.value,
        "ceiling": list(verdict.ceilings),
        "reasons": list(verdict.reasons),
    }


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _deep_thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _deep_thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_deep_thaw(item) for item in value]
    return value


def _frozen_failure(value: Any, pointer: str = "", *, root: bool = False) -> str | None:
    if root and not isinstance(value, MappingProxyType):
        return pointer
    if isinstance(value, MappingProxyType):
        if any(not isinstance(key, str) for key in value):
            return pointer
        for key in sorted(value):
            child = _frozen_failure(
                value[key], pointer + "/" + key.replace("~", "~0").replace("/", "~1")
            )
            if child is not None:
                return child
        return None
    if isinstance(value, tuple):
        for index, item in enumerate(value):
            child = _frozen_failure(item, f"{pointer}/{index}")
            if child is not None:
                return child
        return None
    # RF-05 (§9.13.4 cl. 2.1): a leaf is None or *an instance of* str/bool/int/float.
    # `type(value) in {...}` is an exact-type test and rejects subclasses, which
    # `_deep_freeze` passes through unchanged, so a round-tripped payload could be
    # rejected as unfrozen (D-04).
    if value is None or isinstance(value, (str, bool, int, float)):
        return None
    return pointer


@dataclass(frozen=True)
class LskeRecord:
    collection_key: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        pointer = _frozen_failure(self.payload, root=True)
        if pointer is not None:
            raise SchemaViolation("payload is not deeply frozen", ((pointer, "", "frozen", False),))

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], collection_key: str) -> "LskeRecord":
        validate(payload, collection_key)
        return cls(collection_key, _deep_freeze(payload))

    @property
    def id(self) -> str:
        return self.payload["id"]

    @property
    def object_type(self) -> str:
        return self.payload["type"]

    @property
    def primitive(self) -> str:
        return self.payload["primitive"]

    @property
    def record_version(self) -> int:
        return self.payload["record_version"]

    @property
    def lifecycle_state(self) -> str:
        return self.payload["lifecycle"]["state"]

    @property
    def stored_content_hash(self) -> str:
        return self.payload["content_hash"]

    @property
    def content_hash(self) -> str:
        return content_hash(self.as_dict())

    @property
    def sealed(self) -> bool:
        return self.payload["immutability"]["frozen_at"] is not None

    def as_dict(self) -> dict[str, Any]:
        return _deep_thaw(self.payload)

    def __hash__(self) -> int:
        body = {"collection": self.collection_key, "payload": self.as_dict()}
        return int.from_bytes(hashlib.sha256(canonical_json(body)).digest()[:8], "big")


__all__ = [
    "SCHEMA_DRAFT",
    "SCHEMA_BASE_URI",
    "ONTOLOGY_VERSION",
    "PRIMITIVES",
    "DIMENSION_KEYS",
    "DIMENSION_STATES",
    "LIFECYCLE_STATES",
    "LIFECYCLE_TRANSITIONS",
    "CHANGE_KINDS",
    "RELATION_TYPES",
    "CONFIDENCE_BASES",
    "CollectionSpec",
    "COLLECTION_SPECS",
    "COLLECTION_SPEC_BY_KEY",
    "record_schema",
    "collection_schema",
    "relation_schema",
    "obs2_schema",
    "all_schemas",
    "validate",
    "LskeRecord",
    "allocate_record_id",
    "allocate_event_id",
    "canonical_json",
    "content_hash",
    "seal",
    "edge_state",
    "admissibility_payload",
]
