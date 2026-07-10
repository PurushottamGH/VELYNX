"""Tests for program_a/evidence/snapshot_store.py.

Covers the implemented (constant-independent) surface of ``SnapshotStore``:
``load``, ``snapshot_hash``, the immutable document index, and the explicit
``RuntimeError`` guard on ``evidence_for``. Categories: unit, determinism,
integrity propagation, conformance, regression.

``evidence_for`` is deliberately NOT implemented pending the T1/G4 freeze of
``EVIDENCE_ORDERING_KEY`` (B-2/B-13) and the A3 retrieval-mode decision; it
must raise ``RuntimeError``, never invent behavior (CR-6/CR-11).

Reference: PROGRAM_A_MODULE_SPEC.md Section 4.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from program_a.evidence.snapshot_format import (
    DOCUMENTS_FILENAME,
    SnapshotIntegrityError,
)
from program_a.evidence.snapshot_store import EvidenceSource, SnapshotStore
from program_a.types import EvidenceItem


def _write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, ensure_ascii=False), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Unit
# --------------------------------------------------------------------------- #


def test_load_returns_snapshot_store(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    assert isinstance(store, SnapshotStore)


def test_snapshot_hash_equals_manifest_aggregate(build_snapshot_dir) -> None:
    path, manifest, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    assert store.snapshot_hash == manifest["aggregate_hash"]


def test_load_indexes_every_document_as_evidence_item(build_snapshot_dir) -> None:
    docs = {
        "d1": {"origin_domain": "example.com", "title": "T1", "text": "alpha"},
        "d2": {"origin_domain": "other.com", "title": "T2", "text": "beta"},
    }
    path, manifest, _ = build_snapshot_dir(docs=docs)
    store = SnapshotStore.load(path)
    index = store.documents()
    assert set(index) == {"d1", "d2"}
    for did, rec in docs.items():
        item = index[did]
        assert isinstance(item, EvidenceItem)
        assert item.doc_id == did
        assert item.origin_domain == rec["origin_domain"]
        assert item.title == rec["title"]
        assert item.text == rec["text"]
        assert item.snapshot_hash_ref == manifest["aggregate_hash"]


def test_documents_returns_readonly_mapping(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    index = store.documents()
    with pytest.raises(TypeError):
        index["d1"] = store.documents()["d1"]  # type: ignore[index]


# --------------------------------------------------------------------------- #
# Determinism / replay
# --------------------------------------------------------------------------- #


def test_two_loads_produce_equal_snapshot_hash_and_items(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    a = SnapshotStore.load(path)
    b = SnapshotStore.load(path)
    assert a.snapshot_hash == b.snapshot_hash
    assert sorted(a.documents().values(), key=lambda x: x.doc_id) == sorted(
        b.documents().values(), key=lambda x: x.doc_id
    )


def test_load_is_independent_of_documents_json_key_order(tmp_path) -> None:
    docs = {
        "d1": {"origin_domain": "a", "title": "b", "text": "c"},
        "d2": {"origin_domain": "d", "title": "e", "text": "f"},
    }
    from program_a.evidence.snapshot_format import _aggregate_hash, _doc_hash

    doc_hashes = {did: _doc_hash(rec) for did, rec in docs.items()}
    manifest = {
        "aggregate_hash": _aggregate_hash(doc_hashes),
        "doc_hashes": doc_hashes,
        "built_from": "u@x",
        "leakage_review_ref": "A3",
        "created_commit": "cc",
    }
    d1 = tmp_path / "ordered"
    d2 = tmp_path / "shuffled"
    d1.mkdir()
    d2.mkdir()
    # Write manifest identically; write documents.json with reversed key order.
    _write_json(d1 / DOCUMENTS_FILENAME, docs)
    _write_json(d2 / DOCUMENTS_FILENAME, dict(reversed(list(docs.items()))))
    _write_json(d1 / "snapshot_manifest.json", manifest)
    _write_json(d2 / "snapshot_manifest.json", manifest)
    s1 = SnapshotStore.load(d1)
    s2 = SnapshotStore.load(d2)
    assert s1.snapshot_hash == s2.snapshot_hash
    assert sorted(s1.documents().values(), key=lambda x: x.doc_id) == sorted(
        s2.documents().values(), key=lambda x: x.doc_id
    )


# --------------------------------------------------------------------------- #
# Integrity propagation
# --------------------------------------------------------------------------- #


def test_load_propagates_integrity_error_on_tampered_doc(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    docs_path = path / DOCUMENTS_FILENAME
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    docs["d1"]["text"] = "TAMPERED"
    _write_json(docs_path, docs)
    with pytest.raises(SnapshotIntegrityError):
        SnapshotStore.load(path)


# --------------------------------------------------------------------------- #
# evidence_for explicit guard
# --------------------------------------------------------------------------- #


def test_evidence_for_always_raises_runtime_error(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    with pytest.raises(RuntimeError) as excinfo:
        store.evidence_for("any query")
    msg = str(excinfo.value)
    assert "EVIDENCE_ORDERING_KEY" in msg
    assert "TODO-T1" in msg or "T1/G4" in msg
    assert "CR-6" in msg or "ordering rule" in msg.lower() or "guessed" in msg.lower()


def test_evidence_for_error_mentions_both_prerequisites(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    with pytest.raises(RuntimeError) as excinfo:
        store.evidence_for("q")
    msg = str(excinfo.value)
    assert "EVIDENCE_ORDERING_KEY" in msg
    assert "lookup substrate" in msg or "A3" in msg


# --------------------------------------------------------------------------- #
# Conformance
# --------------------------------------------------------------------------- #


def test_loaded_store_conforms_to_evidence_source_protocol(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    assert isinstance(store, EvidenceSource)


# --------------------------------------------------------------------------- #
# Regression
# --------------------------------------------------------------------------- #


def test_regression_indexed_items_have_no_score_or_timestamp_field(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    store = SnapshotStore.load(path)
    for item in store.documents().values():
        fields = set(EvidenceItem.__dataclass_fields__)
        assert "score" not in fields
        assert "timestamp" not in fields


def test_load_uses_no_network(build_snapshot_dir, block_socket) -> None:
    path, _, _ = build_snapshot_dir()
    SnapshotStore.load(path)  # completes with socket blocked


# --------------------------------------------------------------------------- #
# Property
# --------------------------------------------------------------------------- #


def test_loaded_index_doc_ids_match_documents_json_keys(build_snapshot_dir) -> None:
    docs = {
        f"d{i}": {"origin_domain": f"dom{i}.com", "title": f"t{i}", "text": f"x{i}"}
        for i in range(5)
    }
    path, _, _ = build_snapshot_dir(docs=docs)
    store = SnapshotStore.load(path)
    assert set(store.documents()) == set(docs)
