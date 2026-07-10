"""Shared fixtures for tests/program_a/.

Provides ``build_snapshot_dir`` -- writes a well-formed frozen-retrieval
snapshot directory (``snapshot_manifest.json`` + ``documents.json``) whose
hashes are computed with the SAME scheme the production module owns, so tests
exercise the real integrity path rather than a parallel reimplementation.

Scope: tests only; no production-code changes. All corpora here are synthetic
and disjoint from the frozen EXP-1 dataset (dataset-spec Section 12.3).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from program_a.evidence.snapshot_format import (
    DOCUMENTS_FILENAME,
    MANIFEST_FILENAME,
    _aggregate_hash,
    _doc_hash,
)

_DEFAULT_DOCS: dict[str, dict[str, str]] = {
    "d1": {"origin_domain": "example.com", "title": "First doc", "text": "alpha beta"},
    "d2": {"origin_domain": "other.com", "title": "Second doc", "text": "gamma delta"},
    "d3": {"origin_domain": "third.org", "title": "Third doc", "text": "epsilon zeta"},
}
_DEFAULT_PROVENANCE: dict[str, str] = {
    "built_from": "unified_retriever@abc123",
    "leakage_review_ref": "A3-2026-01",
    "created_commit": "abc123",
}


def _write_documents(path: Path, docs: dict[str, dict[str, str]]) -> None:
    (path / DOCUMENTS_FILENAME).write_text(
        json.dumps(docs, sort_keys=True, ensure_ascii=False), encoding="utf-8"
    )


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    (path / MANIFEST_FILENAME).write_text(
        json.dumps(manifest, sort_keys=True, ensure_ascii=False), encoding="utf-8"
    )


def _build_manifest(docs: dict[str, dict[str, str]], provenance: dict[str, str]) -> dict[str, Any]:
    doc_hashes = {did: _doc_hash(rec) for did, rec in docs.items()}
    return {
        "aggregate_hash": _aggregate_hash(doc_hashes),
        "doc_hashes": doc_hashes,
        **provenance,
    }


@pytest.fixture
def build_snapshot_dir(tmp_path: Path):
    """Factory writing a valid snapshot dir; returns (path, manifest_dict, doc_hashes).

    Call as ``build_snapshot_dir(docs=None, provenance=None, write_docs=True,
    manifest_override=None)``. ``write_docs=False`` skips writing documents.json
    (for missing-file tests). ``manifest_override`` merges into the manifest
    (e.g. to tamper a hash). The caller may also mutate files after the call.
    """

    def _make(
        docs: dict[str, dict[str, str]] | None = None,
        provenance: dict[str, str] | None = None,
        write_docs: bool = True,
        manifest_override: dict[str, Any] | None = None,
    ) -> tuple[Path, dict[str, Any], dict[str, str]]:
        use_docs = dict(_DEFAULT_DOCS) if docs is None else dict(docs)
        use_prov = dict(_DEFAULT_PROVENANCE) if provenance is None else dict(provenance)
        snap_dir = tmp_path / "snapshot"
        snap_dir.mkdir()
        manifest = _build_manifest(use_docs, use_prov)
        if manifest_override:
            manifest.update(manifest_override)
        if write_docs:
            _write_documents(snap_dir, use_docs)
        _write_manifest(snap_dir, manifest)
        return snap_dir, manifest, dict(manifest["doc_hashes"])

    return _make


@pytest.fixture
def block_socket(monkeypatch):
    """Fail any socket creation while active -- asserts no network in PA-1."""
    import socket

    def _boom(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("network access forbidden in program_a evidence path")

    monkeypatch.setattr(socket, "socket", _boom)
    monkeypatch.setattr("socket.create_connection", _boom)
    yield
