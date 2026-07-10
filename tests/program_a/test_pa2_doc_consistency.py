"""Documentation-consistency guard for PA-2 (Claim Extraction).

Asserts that PROGRAM_A_FINAL_ARCHITECTURE.md PA-2 section matches the
implemented CandidateClaim contract. PA-2 closure sprint action C2 per
PA2_ACCEPTANCE_DECISION.md. Non-ES-1: tests the PA-2 leaf type and its docs
only; no frozen constants, no emission/binding/EXP-1.
"""
from __future__ import annotations

from pathlib import Path

from program_a.extraction.claim_extraction import extract_claims
from program_a.types import CandidateClaim, EvidenceSet


def _repo_root() -> Path:
    # tests/program_a/test_pa2_doc_consistency.py -> parents[2] = repo root
    return Path(__file__).resolve().parents[2]


def _pa2_section() -> str:
    path = _repo_root() / "PROGRAM_A_FINAL_ARCHITECTURE.md"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("### PA-2"):
            start = i
            break
    assert start is not None, "PA-2 section header not found in PROGRAM_A_FINAL_ARCHITECTURE.md"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("### "):
            end = j
            break
    return "\n".join(lines[start:end])


def test_pa2_doc_documents_supporting_doc_ids() -> None:
    section = _pa2_section()
    assert "supporting_doc_ids" in section


def test_pa2_doc_does_not_document_claim_id() -> None:
    section = _pa2_section()
    assert "claim_id" not in section


def test_pa2_doc_field_set_matches_implemented_candidate_claim() -> None:
    implemented = set(CandidateClaim.__dataclass_fields__)
    assert implemented == {"claim_text", "supporting_doc_ids"}
    assert "claim_id" not in implemented


def test_pa2_behavior_empty_evidence_yields_empty_claims() -> None:
    out = extract_claims("What is Aspirin?", EvidenceSet(items=()))
    assert len(out) == 0
    assert out.claims == ()