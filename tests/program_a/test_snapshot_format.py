"""Tests for program_a/evidence/snapshot_format.py.

Covers the real (non-stub) surface of this module:
``SnapshotManifest.to_dict`` and ``verify_snapshot`` (SHA-256 integrity
verification). Categories: unit, integrity, determinism/replay, property,
regression, fuzz.

Reference: PROGRAM_A_MODULE_SPEC.md Section 3.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

from program_a.evidence.snapshot_format import (
    DOCUMENTS_FILENAME,
    MANIFEST_FILENAME,
    SnapshotIntegrityError,
    SnapshotManifest,
    _aggregate_hash,
    _doc_hash,
    verify_snapshot,
)
from tests.program_a._snapshot_fixtures import (
    oracle_aggregate_hash,
    oracle_doc_hash,
    write_valid_snapshot,
)


def _manifest(**overrides) -> SnapshotManifest:
    fields = dict(
        aggregate_hash="agg-hash",
        doc_hashes={"d1": "h1", "d2": "h2"},
        built_from="unified_retriever@commit",
        leakage_review_ref="A3-2026-01",
        created_commit="abc123",
    )
    fields.update(overrides)
    return SnapshotManifest(**fields)


def _write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, ensure_ascii=False), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Unit: SnapshotManifest.to_dict
# --------------------------------------------------------------------------- #


def test_to_dict_returns_all_fields() -> None:
    manifest = _manifest()
    d = manifest.to_dict()
    assert d == {
        "aggregate_hash": "agg-hash",
        "doc_hashes": {"d1": "h1", "d2": "h2"},
        "built_from": "unified_retriever@commit",
        "leakage_review_ref": "A3-2026-01",
        "created_commit": "abc123",
    }


def test_to_dict_returns_a_copy_of_doc_hashes() -> None:
    manifest = _manifest()
    d = manifest.to_dict()
    d["doc_hashes"]["d1"] = "mutated"
    assert manifest.doc_hashes["d1"] == "h1"


def test_to_dict_is_deterministic_across_calls() -> None:
    manifest = _manifest()
    assert manifest.to_dict() == manifest.to_dict()


def test_to_dict_json_roundtrip_preserves_structure() -> None:
    manifest = _manifest()
    roundtripped = json.loads(json.dumps(manifest.to_dict()))
    assert roundtripped == manifest.to_dict()


# --------------------------------------------------------------------------- #
# Unit: verify_snapshot -- well-formed snapshots
# --------------------------------------------------------------------------- #


def test_verify_well_formed_snapshot_returns_manifest(build_snapshot_dir) -> None:
    path, manifest, doc_hashes = build_snapshot_dir()
    got = verify_snapshot(path)
    assert isinstance(got, SnapshotManifest)
    assert got.aggregate_hash == manifest["aggregate_hash"]
    assert got.doc_hashes == doc_hashes
    assert got.built_from == manifest["built_from"]
    assert got.leakage_review_ref == manifest["leakage_review_ref"]
    assert got.created_commit == manifest["created_commit"]


def test_verify_returns_doc_hashes_as_independent_dict(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    got = verify_snapshot(path)
    got.doc_hashes["d1"] = "tampered"
    again = verify_snapshot(path)
    assert again.doc_hashes["d1"] != "tampered"


# --------------------------------------------------------------------------- #
# Integrity: tamper / structural failure rejection
# --------------------------------------------------------------------------- #


def test_verify_rejects_tampered_document_text(build_snapshot_dir, tmp_path) -> None:
    path, manifest, _ = build_snapshot_dir()
    docs_path = path / DOCUMENTS_FILENAME
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    docs["d1"]["text"] = "TAMPERED"
    _write_json(docs_path, docs)
    with pytest.raises(SnapshotIntegrityError, match="hash mismatch for document 'd1'"):
        verify_snapshot(path)


def test_verify_rejects_tampered_doc_hash_in_manifest(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    manifest_path = path / MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["doc_hashes"]["d1"] = "0" * 64
    _write_json(manifest_path, manifest)
    with pytest.raises(SnapshotIntegrityError, match="hash mismatch for document 'd1'"):
        verify_snapshot(path)


def test_verify_rejects_tampered_aggregate_hash(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    manifest_path = path / MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["aggregate_hash"] = "f" * 64
    _write_json(manifest_path, manifest)
    with pytest.raises(SnapshotIntegrityError, match="aggregate hash mismatch"):
        verify_snapshot(path)


def test_verify_rejects_missing_document_in_documents_json(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    docs_path = path / DOCUMENTS_FILENAME
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    del docs["d1"]
    _write_json(docs_path, docs)
    with pytest.raises(SnapshotIntegrityError, match="manifest declares document 'd1'"):
        verify_snapshot(path)


def test_verify_rejects_extra_document_not_in_manifest(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    docs_path = path / DOCUMENTS_FILENAME
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    docs["rogue"] = {"origin_domain": "x", "title": "y", "text": "z"}
    _write_json(docs_path, docs)
    with pytest.raises(SnapshotIntegrityError, match="undeclared document"):
        verify_snapshot(path)


def test_verify_rejects_missing_manifest_file(tmp_path) -> None:
    snap = tmp_path / "snapshot"
    snap.mkdir()
    _write_json(
        snap / DOCUMENTS_FILENAME, {"d1": {"origin_domain": "a", "title": "b", "text": "c"}}
    )
    with pytest.raises(SnapshotIntegrityError, match="missing required file"):
        verify_snapshot(snap)


def test_verify_rejects_missing_documents_file(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir(write_docs=False)
    with pytest.raises(SnapshotIntegrityError, match="missing required file"):
        verify_snapshot(path)


def test_verify_rejects_path_is_file_not_dir(tmp_path) -> None:
    f = tmp_path / "not_a_dir.json"
    f.write_text("{}", encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="must be a directory"):
        verify_snapshot(f)


def test_verify_rejects_nonexistent_path(tmp_path) -> None:
    with pytest.raises(SnapshotIntegrityError, match="does not exist"):
        verify_snapshot(tmp_path / "nope")


def test_verify_rejects_malformed_manifest_json(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    (path / MANIFEST_FILENAME).write_text("{not valid json", encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="malformed JSON"):
        verify_snapshot(path)


def test_verify_rejects_manifest_missing_required_field(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    manifest_path = path / MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["aggregate_hash"]
    _write_json(manifest_path, manifest)
    with pytest.raises(SnapshotIntegrityError, match="missing required field 'aggregate_hash'"):
        verify_snapshot(path)


def test_verify_rejects_manifest_doc_hashes_wrong_type(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    manifest_path = path / MANIFEST_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["doc_hashes"] = ["not", "a", "dict"]
    _write_json(manifest_path, manifest)
    with pytest.raises(SnapshotIntegrityError, match="'doc_hashes' must be an object"):
        verify_snapshot(path)


def test_verify_rejects_manifest_doc_hashes_empty(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir(docs={})
    with pytest.raises(SnapshotIntegrityError, match="'doc_hashes' must be non-empty"):
        verify_snapshot(path)


def test_verify_rejects_manifest_top_level_not_object(tmp_path) -> None:
    snap = tmp_path / "snapshot"
    snap.mkdir()
    _write_json(snap / MANIFEST_FILENAME, [1, 2, 3])
    _write_json(snap / DOCUMENTS_FILENAME, {})
    with pytest.raises(SnapshotIntegrityError, match="top-level JSON must be an object"):
        verify_snapshot(snap)


def test_verify_rejects_documents_top_level_not_object(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    _write_json(path / DOCUMENTS_FILENAME, [1, 2, 3])
    with pytest.raises(SnapshotIntegrityError, match="top-level JSON must be an object"):
        verify_snapshot(path)


def test_verify_rejects_document_record_missing_field(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    docs_path = path / DOCUMENTS_FILENAME
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    del docs["d1"]["text"]
    _write_json(docs_path, docs)
    with pytest.raises(SnapshotIntegrityError, match="missing required field 'text'"):
        verify_snapshot(path)


def test_verify_rejects_document_record_wrong_type(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    docs_path = path / DOCUMENTS_FILENAME
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    docs["d1"]["title"] = 123
    _write_json(docs_path, docs)
    with pytest.raises(SnapshotIntegrityError, match="field 'title' must be a string"):
        verify_snapshot(path)


# --------------------------------------------------------------------------- #
# Determinism / replay
# --------------------------------------------------------------------------- #


def test_verify_deterministic_across_calls(build_snapshot_dir) -> None:
    path, _, _ = build_snapshot_dir()
    first = verify_snapshot(path)
    second = verify_snapshot(path)
    assert first == second
    assert first is not second


def test_two_identical_snapshots_produce_equal_manifests(tmp_path) -> None:
    docs = {"d1": {"origin_domain": "a", "title": "b", "text": "c"}}
    doc_hashes = {did: _doc_hash(rec) for did, rec in docs.items()}
    agg = _aggregate_hash(doc_hashes)
    manifest = {
        "aggregate_hash": agg,
        "doc_hashes": doc_hashes,
        "built_from": "u@x",
        "leakage_review_ref": "A3",
        "created_commit": "cc",
    }
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    for d in (a, b):
        _write_json(d / DOCUMENTS_FILENAME, docs)
        _write_json(d / MANIFEST_FILENAME, manifest)
    assert verify_snapshot(a) == verify_snapshot(b)


# --------------------------------------------------------------------------- #
# Property (hypothesis)
# --------------------------------------------------------------------------- #


@st.composite
def _doc_record(draw):
    return {
        "origin_domain": draw(st.text(min_size=1, max_size=12)),
        "title": draw(st.text(min_size=1, max_size=12)),
        "text": draw(st.text(min_size=1, max_size=40)),
    }


@given(
    st.dictionaries(
        st.text(min_size=1, max_size=6, alphabet=st.characters(blacklist_categories=("Cs",))),
        _doc_record(),
        min_size=1,
        max_size=5,
    )
)
def test_property_recomputed_aggregate_equals_manifest_aggregate(docs) -> None:
    doc_hashes = {did: _doc_hash(rec) for did, rec in docs.items()}
    assert _aggregate_hash(doc_hashes) == _aggregate_hash(doc_hashes)


@given(_doc_record())
def test_property_doc_hash_stable_under_record_key_reorder(rec) -> None:
    ordered = json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    shuffled = json.dumps(
        {"text": rec["text"], "origin_domain": rec["origin_domain"], "title": rec["title"]},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    assert ordered == shuffled  # sort_keys normalizes order
    assert _doc_hash(rec) == _doc_hash(
        {"text": rec["text"], "origin_domain": rec["origin_domain"], "title": rec["title"]}
    )


# --------------------------------------------------------------------------- #
# Regression
# --------------------------------------------------------------------------- #


def test_regression_manifest_is_not_frozen_dataclass_with_hash() -> None:
    original = _manifest()
    duplicate = copy.deepcopy(original)
    assert duplicate.doc_hashes is not original.doc_hashes
    assert duplicate == original


def test_regression_to_dict_is_json_serializable() -> None:
    json.dumps(_manifest().to_dict())  # must not raise


def test_verify_uses_no_network(build_snapshot_dir, block_socket) -> None:
    path, _, _ = build_snapshot_dir()
    verify_snapshot(path)  # completes with socket blocked


# --------------------------------------------------------------------------- #
# Property: to_dict doc_hashes
# --------------------------------------------------------------------------- #


@given(st.dictionaries(st.text(min_size=1, max_size=10), st.text(min_size=1, max_size=10)))
def test_property_to_dict_doc_hashes_matches_input(doc_hashes: dict) -> None:
    manifest = _manifest(doc_hashes=doc_hashes)
    assert manifest.to_dict()["doc_hashes"] == doc_hashes
    assert manifest.to_dict()["doc_hashes"] is not manifest.doc_hashes


# --------------------------------------------------------------------------- #
# Injective serialization (collision fix regression + property + fuzz)
# --------------------------------------------------------------------------- #


def _old_text_aggregate_bytes(doc_hashes: dict[str, str]) -> bytes:
    """The PRE-FIX text-style serialization (kept only as a regression oracle)."""
    return "".join(f"{doc_id}:{doc_hashes[doc_id]}\n" for doc_id in sorted(doc_hashes)).encode(
        "utf-8"
    )


def test_regression_aggregate_injective_against_glm_collision() -> None:
    """The GLM-reported collision is broken by the new pair-array scheme.

    Under the OLD text-style formula both inputs serialize to ``b"a:1\nb:2\n"``
    (one had key ``"a:1\\nb"`` -> ``"a:1\\nb:2\\n"``, the other two keys
    ``"a"``/``"b"`` -> ``"a:1\\nb:2\\n"``), hence collided. The new JSON
    pair-array serialization distinguishes them.
    """
    d_collision = {"a:1\nb": "2"}
    d_two_keys = {"a": "1", "b": "2"}
    # Guard: the old text-style formula DID collide on these two inputs.
    assert _old_text_aggregate_bytes(d_collision) == b"a:1\nb:2\n"
    assert _old_text_aggregate_bytes(d_two_keys) == b"a:1\nb:2\n"
    assert _old_text_aggregate_bytes(d_collision) == _old_text_aggregate_bytes(d_two_keys)
    # The new pair-array scheme distinguishes them.
    assert _aggregate_hash(d_collision) != _aggregate_hash(d_two_keys)


@given(
    d1=st.dictionaries(
        keys=st.text(min_size=1, max_size=8, alphabet=st.characters(blacklist_categories=("Cs",))),
        values=st.from_regex(r"[0-9a-f]{64}"),
        min_size=1,
        max_size=8,
    ),
    d2=st.dictionaries(
        keys=st.text(min_size=1, max_size=8, alphabet=st.characters(blacklist_categories=("Cs",))),
        values=st.from_regex(r"[0-9a-f]{64}"),
        min_size=1,
        max_size=8,
    ),
)
def test_property_aggregate_injective_over_unicode(d1: dict, d2: dict) -> None:
    """Two distinct doc_hashes dicts must yield distinct aggregate hashes.

    doc_ids may be any non-empty text (C0 controls + NUL included, surrogates
    excluded); doc_hashes are 64-char lowercase hex.
    """
    from hypothesis import assume

    assume(d1 != d2)
    assert _aggregate_hash(d1) != _aggregate_hash(d2)


@settings(max_examples=200)
@given(
    dicts=st.lists(
        st.dictionaries(
            keys=st.one_of(
                st.from_regex(r"[A-Za-z0-9_./:\-]{1,32}"),
                st.text(min_size=1, max_size=8),
            ),
            values=st.from_regex(r"[0-9a-f]{64}"),
            min_size=1,
            max_size=50,
        ),
        min_size=1,
        max_size=50,
        unique_by=lambda d: tuple(sorted(d.items())),
    )
)
def test_fuzz_aggregate_injective_realistic(dicts: list) -> None:
    """Up to 50 distinct doc_hashes dicts must yield 50 distinct aggregates.

    doc_ids draw from a realistic charset plus a ~10% admixture of arbitrary
    text (injecting ``:``, newlines, and control characters).
    """
    aggregates = {_aggregate_hash(d) for d in dicts}
    assert len(aggregates) == len(dicts)


def test_verify_snapshot_distinguishes_collision_pair(tmp_path) -> None:
    """End-to-end: two on-disk snapshots that collided under the old scheme
    now verify and carry distinct aggregate_hash values.
    """
    T_a = {"origin_domain": "dom-a", "title": "TA", "text": "alpha"}
    T_b = {"origin_domain": "dom-b", "title": "TB", "text": "beta"}
    h_a = oracle_doc_hash(T_a["origin_domain"], T_a["title"], T_a["text"])

    dir1 = tmp_path / "two_docs"
    dir2 = tmp_path / "one_doc_collision"
    dir1.mkdir()
    dir2.mkdir()

    # dir1: two docs {"a": T_a, "b": T_b}.
    write_valid_snapshot(dir1, {"a": T_a, "b": T_b})

    # dir2: single doc whose id is "a:" + h_a + "\nb", carrying T_b.
    collision_id = "a:" + h_a + "\nb"
    write_valid_snapshot(dir2, {collision_id: T_b})

    m1 = verify_snapshot(dir1)
    m2 = verify_snapshot(dir2)
    assert isinstance(m1, SnapshotManifest)
    assert isinstance(m2, SnapshotManifest)

    # Guard: under the OLD text-style formula these two aggregates WERE equal.
    old1 = hashlib.sha256(_old_text_aggregate_bytes(m1.doc_hashes)).hexdigest()
    old2 = hashlib.sha256(_old_text_aggregate_bytes(m2.doc_hashes)).hexdigest()
    assert old1 == old2

    # The new scheme distinguishes them.
    assert m1.aggregate_hash != m2.aggregate_hash


def test_characterization_doc_id_charset_boundary(tmp_path) -> None:
    """A doc_id containing ":", newline, NUL, and control chars verifies fine;
    an empty string or non-string key is rejected with the existing messages.
    """
    weird_id = "a:1\nb\x00\x01\x7f"
    T = {"origin_domain": "d", "title": "t", "text": "x"}
    snap = tmp_path / "weird_charset"
    snap.mkdir()
    write_valid_snapshot(snap, {weird_id: T})

    manifest = verify_snapshot(snap)
    assert weird_id in manifest.doc_hashes

    # Empty-string doc_id in manifest is rejected (existing message).
    bad_manifest = tmp_path / "empty_key"
    bad_manifest.mkdir()
    write_valid_snapshot(bad_manifest, {"ok": T})
    mpath = bad_manifest / MANIFEST_FILENAME
    raw = json.loads(mpath.read_text(encoding="utf-8"))
    raw["doc_hashes"][""] = raw["doc_hashes"]["ok"]
    mpath.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="doc_hashes keys must be non-empty strings"):
        verify_snapshot(bad_manifest)

    # Empty-string doc_id in documents.json is rejected (existing message).
    bad_docs = tmp_path / "empty_key_docs"
    bad_docs.mkdir()
    write_valid_snapshot(bad_docs, {"ok": T})
    dpath = bad_docs / DOCUMENTS_FILENAME
    docs = json.loads(dpath.read_text(encoding="utf-8"))
    docs[""] = docs["ok"]
    dpath.write_text(json.dumps(docs), encoding="utf-8")
    with pytest.raises(SnapshotIntegrityError, match="documents: keys must be non-empty strings"):
        verify_snapshot(bad_docs)


def test_replay_determinism_key_order_independent(tmp_path) -> None:
    """Same documents in two dirs, reversed key order in both documents.json
    and the manifest doc_hashes, must verify and share one aggregate_hash.
    """
    T_a = {"origin_domain": "d", "title": "A", "text": "alpha"}
    T_b = {"origin_domain": "d", "title": "B", "text": "beta"}
    docs = {"a": T_a, "b": T_b}
    doc_hashes = {
        did: oracle_doc_hash(rec["origin_domain"], rec["title"], rec["text"])
        for did, rec in docs.items()
    }
    aggregate = oracle_aggregate_hash(doc_hashes)

    keys_forward = ["a", "b"]
    keys_reverse = ["b", "a"]

    dir1 = tmp_path / "forward"
    dir2 = tmp_path / "reverse"
    dir1.mkdir()
    dir2.mkdir()
    write_valid_snapshot(dir1, docs, doc_key_order=keys_forward)
    write_valid_snapshot(dir2, docs, doc_key_order=keys_reverse)

    m1 = verify_snapshot(dir1)
    m2 = verify_snapshot(dir2)
    assert m1.aggregate_hash == m2.aggregate_hash == aggregate


def test_conftest_real_aggregate_verifies_snapshot(build_snapshot_dir) -> None:
    """The conftest fixture (which uses the REAL _aggregate_hash) yields a
    snapshot that verifies end-to-end."""
    path, manifest, _ = build_snapshot_dir()
    got = verify_snapshot(path)
    assert got.aggregate_hash == manifest["aggregate_hash"]


@given(
    doc_hashes=st.dictionaries(
        keys=st.text(min_size=1, max_size=8, alphabet=st.characters(blacklist_categories=("Cs",))),
        values=st.from_regex(r"[0-9a-f]{64}"),
        min_size=1,
        max_size=8,
    )
)
def test_oracle_mirrors_new_scheme(doc_hashes: dict) -> None:
    """The from-spec oracle_aggregate_hash must equal the production helper."""
    assert oracle_aggregate_hash(doc_hashes) == _aggregate_hash(doc_hashes)
