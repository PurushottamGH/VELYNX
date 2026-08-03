"""Minimal schema-valid payloads for all 23 LSKE entry surfaces.

Drives the D-01 differential harness and the Section 7 mutation corpus. Each
payload is the smallest legal instance of its entry schema, selecting the
conditional branch that adds the fewest obligations. Every payload is asserted
raw-valid against its schema before any mutation is applied (see
`test_differential.py::test_every_entry_surface_has_a_raw_valid_baseline`), so a
fixture error surfaces as a harness failure rather than as a false PASS.
"""

from __future__ import annotations

import copy
from typing import Any

from v2.lske.schema import COLLECTION_SPECS, all_schemas

_SCHEMAS = all_schemas()
_TS = "2026-08-02T00:00:00Z"
_HEX = "a" * 64
_LEV = "LEV-" + "b" * 32
_RID = {spec.key: f"{spec.prefix}-2026-0001" for spec in COLLECTION_SPECS}

_DIMENSION_KEYS = tuple(_SCHEMAS["record"]["$defs"]["dimensions"]["required"])
_SCOPE = {"population": "all", "regime": "standard", "environment_ids": [], "limits": []}


def _confidence() -> dict[str, Any]:
    # `state: unassessed` is the branch whose `evidence_ids` may stay empty.
    return {
        "level": None,
        "scope": None,
        "dimensions": {
            key: {"state": "unassessed", "evidence_ids": []} for key in _DIMENSION_KEYS
        },
    }


def _base(record_id: str) -> dict[str, Any]:
    """The sixteen record-level required properties, at their smallest legal values."""
    return {
        "id": record_id,
        "type": "placeholder",
        "primitive": "Claim",
        "title": "Title",
        "record_version": 1,
        "ontology_version": "1.1.2",
        "content_hash": _HEX,
        "created": {"at": _TS, "by": "t", "authority": "ENGINEER", "target": "repo.test"},
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
            "committed_by": "t",
            "is_human": False,
            "escalated_from": None,
        },
        "confidence": None,
        "lifecycle": {
            "state": "CANDIDATE",
            "status": "Candidate",
            "transitions": [
                {
                    "from": None,
                    "to": "CANDIDATE",
                    "at": _TS,
                    "by": "t",
                    "event_id": _LEV,
                    "cause": "create",
                }
            ],
        },
        "immutability": {"append_only": False, "frozen_at": None, "seal": None},
    }


# Per-collection narrowings. `confidence` is `{"type": "object"}` on the
# Claim-realizing collections and `{"type": "null"}` on the rest, so it is stated
# explicitly wherever it differs from the record-level default.
_EXTRAS: dict[str, dict[str, Any]] = {
    "research_questions": {
        "type": "research_question",
        "confidence": _confidence(),
        "immutability": {"append_only": False},
        "lifecycle": {"status": "Open"},
        "question": "Is X true?",
        "decision_value": "none",
        "program_id": "PROG-2026-0001",
        "hypothesis_ids": [],
        "resolved_by": None,
    },
    "hypotheses": {
        "type": "hypothesis",
        "confidence": _confidence(),
        "immutability": {"append_only": True},
        "lifecycle": {"status": "Exploratory"},
        "statement": "X causes Y.",
        "falsifier": "Measure Y without X.",
        "question_id": "RQS-2026-0001",
        "mechanism_ids": [],
        "discriminates_from": [],
        "scope": _SCOPE,
    },
    "protocols": {
        "type": "protocol",
        "primitive": "Protocol",
        "immutability": {"append_only": True},
        "path": "protocols/p.yaml",
        "digest": _HEX,
        "freeze": {
            "protocol_id": "PROT-2026-0001",
            "digest": _HEX,
            "source": "protocols/p.yaml",
            "frozen_at_commit": None,
            "algorithm": "blake2b-256-canonical-json",
        },
        "hypothesis_ids": ["HYP-2026-0001"],
        "intent": "exploratory",
        "determinism_tier": "D0",
        "stopping_rule": "n=100",
        "sesoi": {"value": 0.1, "units": "ms", "metric_id": "MET-2026-0001"},
        "exclusion_rules": [],
        "declared_null": "no effect",
        "frozen_before_first_run": False,
    },
    "experiments": {
        "type": "experiment",
        "primitive": "Run",
        "immutability": {"append_only": True},
        # `Designed` is the only status that does not require `protocol_id`.
        "lifecycle": {"status": "Designed"},
        "run_ids": [],
        "hypothesis_ids": ["HYP-2026-0001"],
    },
    "runs": {
        "type": "run",
        "primitive": "Run",
        "immutability": {"append_only": True},
        "experiment_id": "EXP-2026-0001",
        "protocol_id": "PROT-2026-0001",
        "runtime_run_id": "run-001",
        "manifest_path": "runs/r.yaml",
        "manifest_digest": _HEX,
        "admissibility": {
            "admissible": True,
            "tier": "exploratory-admissible",
            "ceiling": ["exploratory-admissible"],
            "reasons": ["baseline"],
        },
        "determinism_tier": "D0",
        "event_log_path": "runs/events.jsonl",
        "artifact_ids": [],
        "environment": {"python": "3.11.9", "platform": "linux", "ci": ""},
        "clean_checkout": True,
    },
    "observations": {
        "type": "observation",
        "primitive": "Measurement",
        "immutability": {"append_only": True},
        "run_ids": ["RUN-2026-0001"],
        "metric_id": "MET-2026-0001",
        # A non-null `value` keeps the §9.2.4 value-null conditional untriggered.
        "value": 1.0,
        # `kind: none` is the branch that requires `interval` to be null.
        "uncertainty": {"kind": "none", "interval": None, "n": None, "method": "direct"},
        "coverage": {"measured": 1, "expected": 1, "missing_reason": None},
        "validity": "valid",
        "declared_null_comparison": None,
        "blinded": False,
    },
    "metrics": {
        "type": "metric",
        "primitive": "Measurement",
        "immutability": {"append_only": False},
        "lifecycle": {"status": "Active"},
        "formula": "mean(x)",
        "units": "ms",
        "direction": "lower_is_better",
        "estimator_version": "1.0.0",
        "aggregation_rule": "mean",
        "declared_null": "no effect",
        "validity_status": "validated",
        "known_defects": [],
    },
    "datasets": {
        "type": "dataset",
        "primitive": "Environment",
        "immutability": {"append_only": False},
        "content_digest": _HEX,
        "generator": None,
        # `audited: false` is the branch that permits null `at`/`by`.
        "leakage_audit": {"audited": False, "at": None, "by": None, "findings": []},
        "splits": {"train": {"digest": _HEX, "record_count": 0}},
        "provenance_reliability": "reconstructable",
    },
    "artifacts": {
        "type": "artifact",
        "primitive": "Snapshot",
        "immutability": {"append_only": True},
        "run_id": "RUN-2026-0001",
        "path": "artifacts/a.json",
        "digest": _HEX,
        "kind": "manifest",
        "integrity": "verified",
        "retention": "permanent",
    },
    "evidence": {
        "type": "evidence",
        "primitive": "Evidence",
        "immutability": {"append_only": True},
        "source_observation_ids": ["OBS-2026-0001"],
        "run_ids": ["RUN-2026-0001"],
        "target_id": "HYP-2026-0001",
        "direction": "supports",
        "dimensions": ["existence"],
        "eligibility": "exploratory-admissible",
        "assumptions_relied_upon": ["none_declared"],
        "unexcluded_alternatives": [],
        "rationale": "Because X.",
        "independence_group": "g1",
    },
    "decisions": {
        "type": "decision",
        "primitive": "Decision",
        "immutability": {"append_only": True},
        # The collection narrows authority to the human decision target.
        "authority": {
            "write_target": "skb.decision",
            "committed_by": "scientist",
            "is_human": True,
            "escalated_from": None,
        },
        # `no_change` is the only action that permits empty `evidence_ids`.
        "action": "no_change",
        "subject_ids": ["HYP-2026-0001"],
        "evidence_ids": [],
        "rationale": "No change.",
        "alternatives_considered": ["wait"],
        "dissent": [],
        "human_committer": "scientist",
        "propagation_receipt_id": "RCT-001",
    },
    "mechanisms": {
        "type": "mechanism",
        "confidence": _confidence(),
        "immutability": {"append_only": False},
        "statement": "X works via Y.",
        "hypothesis_ids": ["HYP-2026-0001"],
        "bundled_with": [],
        "identifiability": "identified",
        "operability": "demonstrated",
    },
    "theories": {
        "type": "theory",
        "confidence": _confidence(),
        "immutability": {"append_only": False},
        "statement": "Unified account.",
        "constituent_hypothesis_ids": [],
        "integrated_principle": None,
        "risky_prediction": None,
        "outperforms": [],
    },
    "assumptions": {
        "type": "assumption",
        "confidence": _confidence(),
        "immutability": {"append_only": False},
        "statement": "Assume X.",
        "load_bearing_for": ["HYP-2026-0001"],
        "test_status": "untested",
        "opposing_evidence_ids": [],
        "failure_consequence": "Invalidates HYP-2026-0001.",
    },
    "unknowns": {
        "type": "unknown",
        "confidence": _confidence(),
        "immutability": {"append_only": False},
        "statement": "Unknown X.",
        "expected_decision_value": "none",
        "blocks_ids": [],
        "cheapest_resolving_experiment": None,
    },
    "scientific_debt": {
        "type": "scientific_debt",
        "confidence": _confidence(),
        "immutability": {"append_only": False},
        "statement": "Debt X.",
        "severity": "advisory",
        "blocks_ids": [],
        "discharge_condition": "Resolve X.",
        "incurred_by": [],
    },
    "negative_results": {
        "type": "negative_result",
        "primitive": "Evidence",
        "immutability": {"append_only": True},
        "statement": "X did not hold.",
        "hypothesis_id": "HYP-2026-0001",
        "scope": _SCOPE,
        "equivalence_established": False,
        "retry_prohibited": False,
        "evidence_ids": ["EVD-2026-0001"],
    },
    "programs": {
        "type": "research_program",
        "confidence": _confidence(),
        "immutability": {"append_only": False},
        "statement": "Program X.",
        "gate": "G1",
        "question_ids": [],
        "entry_condition": "Start.",
        "exit_condition": "End.",
    },
    "sessions": {
        "type": "research_session",
        "primitive": "Intervention",
        "immutability": {"append_only": True},
        "actor": "scientist",
        "opened": _TS,
        "closed": None,
        "records_touched": [],
        "annotations": [],
        "blinding_state": "unblinded",
    },
    "snapshots": {
        "type": "knowledge_snapshot",
        "primitive": "Snapshot",
        "immutability": {"append_only": True},
        "store_content_hash": _HEX,
        "commit": "abc1234",
        "at": _TS,
        "record_count": 0,
        "cause": "manual",
        "caused_by": None,
    },
}

_RELATION = {
    "from": "HYP-2026-0001",
    "to": "HYP-2026-0002",
    # A non-evidential type is the branch that requires `direction` to be null.
    "type": "belongs_to",
    "direction": None,
    "semantic_note": "note",
    "established_by": "scientist",
    "established_at": _TS,
    "record_version_at": {"source": 1, "target": 1},
    "retracted_by": None,
    "confidence_basis": "structural",
}

_OBS2 = {
    "schema": "obs/2",
    "plate": "V01",
    "phase": "phase-1",
    "subject": "HYP-2026-0001",
    "cause": "manual",
    "zoom_level": 1,
    "primitive": "Claim",
    "nodes": [],
    "edges": [],
    "overlays": {f"overlay_{index}": {} for index in range(8)},
    "store_content_hash": _HEX,
    "snapshot_id": None,
    "governance_banner": None,
}


def valid_payload(name: str) -> dict[str, Any]:
    """A minimal payload satisfying the entry schema `name`."""
    if name == "relation":
        return copy.deepcopy(_RELATION)
    if name == "obs2":
        return copy.deepcopy(_OBS2)
    if name == "record":
        return _base("HYP-2026-0001")

    payload = _base(_RID[name])
    extras = copy.deepcopy(_EXTRAS[name])
    # `lifecycle` and `immutability` are narrowed, not replaced: the collection
    # adds `status`/`append_only` on top of the record-level members.
    for shared in ("lifecycle", "immutability"):
        if shared in extras:
            payload[shared].update(extras.pop(shared))
    payload.update(extras)
    return payload


def all_valid_payloads() -> dict[str, dict[str, Any]]:
    return {name: valid_payload(name) for name in _SCHEMAS}
