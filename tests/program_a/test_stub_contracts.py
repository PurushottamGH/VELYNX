"""Stub-contract guard tests for program_a modules not yet implemented.

These tests pin the *current unimplemented* state of the still-stubbed
program_a surfaces so that:

1. an accidental partial implementation that silently returns a wrong-typed
   value instead of raising is caught immediately by CI (the guard fails
   loudly, signalling "update this test", rather than passing silently), and
2. removal/renaming of a stub's public signature during implementation is
   visible as an import error here rather than discovered downstream.

ALREADY IMPLEMENTED (real tests live elsewhere -- do NOT re-stub them):
  * program_a/types.py                        -> tests/program_a/test_types.py
  * program_a/evidence/snapshot_format.py
      (SnapshotManifest.to_dict, verify_snapshot) -> test_snapshot_format.py
  * program_a/evidence/snapshot_store.py
      (SnapshotStore.load / snapshot_hash / documents()) -> test_snapshot_store.py
      evidence_for() is an explicit RuntimeError guard (not a NotImplementedError
      stub): EVIDENCE_ORDERING_KEY is now frozen at T1/G4, but it still refuses
      to invent the PA-1 query->document lookup substrate pending the A3
      retrieval-mode decision. That refusal is pinned below AND in
      test_snapshot_store.py.
  * program_a/extraction/claim_extraction.py
      (extract_claims) -> tests/program_a/test_claim_extraction.py

Scope: tests only, no production-code changes.
"""

from __future__ import annotations

import pytest

from program_a import constants
from program_a.binding.exp1_binding import program_a_answer_fn
from program_a.evidence.snapshot_builder import build_snapshot
from program_a.evidence.snapshot_store import EvidenceSource, SnapshotStore
from program_a.mechanism import emission
from program_a.mechanism.evidence_states import classify
from program_a.mechanism.support_tests import (
    contradicts,
    independent_origins,
    is_material,
    supports,
)
from program_a.types import CandidateClaim, CandidateClaims, EvidenceItem, EvidenceSet


def _evidence_item(doc_id: str = "d1") -> EvidenceItem:
    return EvidenceItem(
        doc_id=doc_id,
        origin_domain="example.com",
        title="t",
        text="text",
        snapshot_hash_ref="h",
    )


def _claim() -> CandidateClaim:
    return CandidateClaim(claim_text="x", supporting_doc_ids=("d1",))


# --------------------------------------------------------------------------- #
# constants.py
#
# Constants freeze-state coverage has MOVED to tests/program_a/test_constants_freeze.py.
# That dedicated module imports ONLY program_a.constants, so it is collectable
# now; this file (test_stub_contracts.py) remains un-collectable pre-GO because
# it imports the relocated-to-sandbox emission/binding stubs (see
# program_a/__init__.py). Do not duplicate the constants tests here.
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# evidence/snapshot_store.py  --  evidence_for() explicit refusal guard
#
# SnapshotStore.load / snapshot_hash / documents() are now REAL (no longer
# stubs): real coverage lives in tests/program_a/test_snapshot_store.py.
# evidence_for() is NOT a NotImplementedError stub; it is a structural
# RuntimeError guard: EVIDENCE_ORDERING_KEY is now frozen at T1/G4, but it
# refuses to invent the PA-1 query->document lookup substrate pending the
# A3 retrieval-mode decision.
# --------------------------------------------------------------------------- #


def test_snapshot_store_evidence_for_refuses_pending_t1_freeze(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    with pytest.raises(RuntimeError, match="EVIDENCE_ORDERING_KEY"):
        store.evidence_for("some query")
    # snapshot_hash / documents() are real now; isinstance() resolves normally
    # (no longer raises through the Protocol's hasattr probe).
    assert isinstance(store, EvidenceSource)


# --------------------------------------------------------------------------- #
# evidence/snapshot_builder.py
# --------------------------------------------------------------------------- #


def test_build_snapshot_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-6\\)"):
        build_snapshot(["q1"], "/tmp/does-not-matter")


# --------------------------------------------------------------------------- #
# extraction/claim_extraction.py
#
# extract_claims() is now REAL (no longer a stub): real coverage lives in
# tests/program_a/test_claim_extraction.py (determinism, entity-level
# matching, fabrication-pressure negatives, supporting-doc-id subset,
# ordering stability, no-network / no-wall-clock). PA-2 is package-internal
# per MODULE_SPEC Section 11; it is not re-exported from program_a/__init__.
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# mechanism/support_tests.py
# --------------------------------------------------------------------------- #


def test_supports_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-8\\)"):
        supports(_claim(), _evidence_item())


def test_contradicts_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-8\\)"):
        contradicts(_claim(), _claim())


def test_is_material_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-8\\)"):
        is_material(_claim(), _claim())


def test_independent_origins_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-8\\)"):
        independent_origins((_evidence_item(),))


# --------------------------------------------------------------------------- #
# mechanism/evidence_states.py
# --------------------------------------------------------------------------- #


def test_classify_is_still_a_stub() -> None:
    evidence = EvidenceSet(items=(_evidence_item(),))
    claims = CandidateClaims(claims=(_claim(),))
    with pytest.raises(NotImplementedError, match="TODO\\(phase-8\\)"):
        classify("some query", evidence, claims)


# --------------------------------------------------------------------------- #
# mechanism/emission.py
# --------------------------------------------------------------------------- #


def test_program_a_answer_query_is_still_a_stub() -> None:
    instance = emission.ProgramA(snapshot_store=SnapshotStore())
    with pytest.raises(NotImplementedError, match="TODO\\(phase-9\\)"):
        instance.answer_query("some query", seed=1)


def test_program_a_mechanism_id_is_still_a_stub() -> None:
    instance = emission.ProgramA(snapshot_store=SnapshotStore())
    with pytest.raises(NotImplementedError, match="TODO\\(phase-9\\)"):
        instance.mechanism_id()


def test_build_program_a_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-9\\)"):
        emission.build_program_a("does-not-matter")


def test_module_level_answer_query_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-9\\)"):
        emission.answer_query("some query", seed=1)


def test_module_level_mechanism_id_is_still_a_stub() -> None:
    with pytest.raises(NotImplementedError, match="TODO\\(phase-9\\)"):
        emission.mechanism_id()


# --------------------------------------------------------------------------- #
# binding/exp1_binding.py
# --------------------------------------------------------------------------- #


def test_program_a_answer_fn_is_still_a_stub() -> None:
    from experiments.EXP1.dataset import QueryRecord

    query = QueryRecord(
        query_id="q1",
        query="what is x?",
        query_family="known_factual",
        gold_rubric="frozen rubric",
    )
    with pytest.raises(NotImplementedError, match="TODO\\(phase-10\\)"):
        program_a_answer_fn(query, seed=1)


# --------------------------------------------------------------------------- #
# Import-guard / package-surface regression
# --------------------------------------------------------------------------- #


def test_package_public_surface_matches_declared_all() -> None:
    import program_a

    assert set(program_a.__all__) == {
        "answer_query",
        "build_program_a",
        "mechanism_id",
        "program_a_answer_fn",
    }
    for name in program_a.__all__:
        assert hasattr(program_a, name)
