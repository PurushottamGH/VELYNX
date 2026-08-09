"""Stage-1 collection registers and identifier acceptance tests."""

import re

import pytest

from ros.model import ID_PATTERN
from v2.lske.errors import OntologyError
from v2.lske.schema import (
    COLLECTION_SPECS,
    PRIMITIVES,
    allocate_event_id,
    allocate_record_id,
)

EXPECTED_KEYS = [
    "research_questions",
    "hypotheses",
    "protocols",
    "experiments",
    "runs",
    "observations",
    "metrics",
    "datasets",
    "artifacts",
    "evidence",
    "decisions",
    "mechanisms",
    "theories",
    "assumptions",
    "unknowns",
    "scientific_debt",
    "negative_results",
    "programs",
    "sessions",
    "snapshots",
]


def test_collection_register_is_exact_and_well_formed():
    assert [spec.key for spec in COLLECTION_SPECS] == EXPECTED_KEYS
    assert len({spec.key for spec in COLLECTION_SPECS}) == 20
    assert len({spec.prefix for spec in COLLECTION_SPECS}) == 20
    for spec in COLLECTION_SPECS:
        assert re.fullmatch(r"[A-Z]{3,5}", spec.prefix)
        assert ID_PATTERN.fullmatch(f"{spec.prefix}-2026-0001")
        assert spec.primitive in PRIMITIVES
    assert COLLECTION_SPECS[0].prefix == "RQS"


def test_exact_claim_realizing_collections():
    assert {spec.key for spec in COLLECTION_SPECS if spec.primitive == "Claim"} == {
        "research_questions",
        "hypotheses",
        "mechanisms",
        "theories",
        "assumptions",
        "unknowns",
        "scientific_debt",
        "programs",
    }


def test_record_identifier_allocation_contract():
    assert allocate_record_id("hypotheses", [], 2026) == "HYP-2026-0001"
    existing = ["HYP-2026-0009", "HYP-2025-9999", "EXP-2026-0010", "HYP-2026-0003"]
    assert allocate_record_id("hypotheses", existing, 2026) == "HYP-2026-0010"
    assert allocate_record_id("hypotheses", reversed(existing), 2026) == "HYP-2026-0010"
    with pytest.raises(OntologyError):
        allocate_record_id("missing", [], 2026)
    with pytest.raises(OntologyError):
        allocate_record_id("hypotheses", ["HYP-2026-9999"], 2026)


def test_event_identifier_is_content_addressed_and_disjoint():
    body = {
        "kind": "lifecycle",
        "at": "2026-08-02T00:00:00Z",
        "by": "tester",
        "authority": "ENGINEER",
        "target": "repo.test",
        "record_id": "HYP-2026-0001",
        "from": None,
        "to": "CANDIDATE",
        "cause": "test",
    }
    first = allocate_event_id(body)
    assert first == allocate_event_id(dict(reversed(list(body.items()))))
    assert re.fullmatch(r"LEV-[0-9a-f]{32}", first)
    assert not ID_PATTERN.fullmatch(first)
