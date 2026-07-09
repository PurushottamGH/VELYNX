"""Shared snapshot-on-disk fixture builder + independent hashing oracle.

Not a test_*.py module -- pytest does not collect this file directly. It is
imported by test_snapshot_format.py and test_snapshot_store.py so both share
one on-disk fixture shape without duplicating (and risking drift in) the
hashing oracle.

The hashing functions here are a DELIBERATE, independent reimplementation of
the algorithm documented in program_a/evidence/snapshot_format.py's module
docstring. They must not import program_a's own _doc_hash/_aggregate_hash --
comparing GLM's implementation against a from-spec oracle is the point; an
oracle built from GLM's own helpers would only ever agree with itself.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


def oracle_doc_hash(origin_domain: str, title: str, text: str) -> str:
    """Independent reimplementation of doc_hash(doc) per the module docstring."""
    payload = {"origin_domain": origin_domain, "title": title, "text": text}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def oracle_aggregate_hash(doc_hashes: Mapping[str, str]) -> str:
    """Independent reimplementation of aggregate_hash per the module docstring.

    The material is a JSON array of 2-element ``[doc_id, doc_hash]`` arrays
    sorted by ``doc_id`` in Unicode code-point order. JSON string escaping
    makes the serialization injective over every permitted doc_id, so two
    distinct ``doc_hashes`` dicts cannot share an aggregate.
    """
    material = json.dumps(
        [[doc_id, doc_hashes[doc_id]] for doc_id in sorted(doc_hashes)],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def write_valid_snapshot(
    root: Path,
    docs: Mapping[str, Mapping[str, str]],
    *,
    built_from: str = "unified_retriever@commit",
    leakage_review_ref: str = "A3-2026-01",
    created_commit: str = "abc123",
    doc_key_order: list[str] | None = None,
) -> dict[str, str]:
    """Write a structurally-valid snapshot dir (manifest + documents) built via
    the independent oracle. Returns the oracle-computed doc_hashes dict.

    ``doc_key_order`` lets a caller force a specific on-disk JSON key order in
    documents.json, independent of ``docs`` iteration order, to test that the
    aggregate hash (and therefore replay identity) does not depend on
    JSON/dict key order.
    """
    root.mkdir(parents=True, exist_ok=True)
    doc_hashes = {
        doc_id: oracle_doc_hash(rec["origin_domain"], rec["title"], rec["text"])
        for doc_id, rec in docs.items()
    }
    aggregate = oracle_aggregate_hash(doc_hashes)

    manifest = {
        "aggregate_hash": aggregate,
        "doc_hashes": doc_hashes,
        "built_from": built_from,
        "leakage_review_ref": leakage_review_ref,
        "created_commit": created_commit,
    }
    (root / "snapshot_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    ordered_keys = doc_key_order if doc_key_order is not None else list(docs.keys())
    ordered_docs = {k: docs[k] for k in ordered_keys}
    (root / "documents.json").write_text(json.dumps(ordered_docs), encoding="utf-8")
    return doc_hashes


_DEFAULT_DOCS: dict[str, dict[str, str]] = {
    "d1": {"origin_domain": "example.com", "title": "T1", "text": "text one"},
    "d2": {"origin_domain": "other.com", "title": "T2", "text": "text two"},
    "d3": {"origin_domain": "example.com", "title": "T3", "text": "text three"},
}


def default_docs() -> dict[str, dict[str, str]]:
    return {k: dict(v) for k, v in _DEFAULT_DOCS.items()}
