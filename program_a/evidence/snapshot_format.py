"""PA-1 -- frozen retrieval-snapshot on-disk schema + integrity verification.

A snapshot is a static, content-addressed corpus: a manifest
(``snapshot_manifest.json``: aggregate SHA-256, per-document hashes, build
provenance, leakage-review reference) plus documents (``documents.json``).
Read-only at execution (Q7: frozen assets readable). Integrity failure is a
hard pre-run error (drift detectable before any output; FM-6 mitigation).

On-disk snapshot layout (owned by this module; the offline builder
``snapshot_builder.py`` MUST conform when it is implemented in step 6)::

    <path>/
        snapshot_manifest.json   # the 5-field manifest
        documents.json           # {doc_id: {origin_domain, title, text}}

Hashing (deterministic; no scientific content)::

    doc_hash(doc)  = sha256(canonical_json({origin_domain, title, text})).hex()
    aggregate_hash = sha256(canonical_pair_array(doc_hashes)).hex()

    where canonical_json(obj) = json.dumps(obj, sort_keys=True,
                                           separators=(",", ":"),
                                           ensure_ascii=False).encode("utf-8")

    and canonical_pair_array(doc_hashes) =
        json.dumps([[doc_id, doc_hashes[doc_id]]
                    for doc_id in sorted(doc_hashes)],
                   separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8")

    The pair array is a JSON array of 2-element [doc_id, doc_hash] arrays
    sorted by doc_id in Unicode code-point order. JSON string escaping
    disambiguates every character of every doc_id (including ":", newline,
    NUL, and control characters), so the serialization is injective: two
    distinct doc_hashes dicts cannot produce the same bytes and therefore
    cannot share an aggregate_hash. Sorting by doc_id keeps the aggregate
    independent of dict/JSON key order (replay determinism). doc_hash is a
    64-character lowercase hex SHA-256 digest by construction and never
    contains ":", newline, NUL, or any character that would break the
    pair-array encoding; no separate doc_id alphabet restriction is applied.

This module implements the constant-independent integrity half of PA-1 only.
It contains no ordering rule, no lookup rule, no tier/state logic, and no
scientific constants. ``verify_snapshot`` is the replay-safety gate: a snapshot
whose bytes drift from its manifest cannot reach the execution path.

Reference: PROGRAM_A_FINAL_ARCHITECTURE.md Section 4 PA-1;
PROGRAM_A_MODULE_SPEC.md Section 3.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# --- On-disk filenames (owned here so the builder conforms) -------------------
MANIFEST_FILENAME: str = "snapshot_manifest.json"
DOCUMENTS_FILENAME: str = "documents.json"

# --- Manifest field names (the frozen 5-field schema) -------------------------
_MANIFEST_REQUIRED_FIELDS: tuple[str, ...] = (
    "aggregate_hash",
    "doc_hashes",
    "built_from",
    "leakage_review_ref",
    "created_commit",
)


class SnapshotIntegrityError(Exception):
    """Raised when a snapshot fails structural or cryptographic integrity checks.

    A snapshot is content-addressed: any byte drift, missing/extra document,
    malformed manifest, or recomputed-hash mismatch is a hard pre-run error.
    Catching this is never the right answer at execution time -- the snapshot
    must be rebuilt and re-frozen. (FM-6 mitigation; prereg replay guarantee.)
    """


@dataclass(frozen=True)
class SnapshotManifest:
    """Manifest of a content-addressed frozen retrieval snapshot."""

    aggregate_hash: str
    doc_hashes: dict[str, str]
    built_from: str
    leakage_review_ref: str
    created_commit: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable view of the manifest (structural)."""
        return {
            "aggregate_hash": self.aggregate_hash,
            "doc_hashes": dict(self.doc_hashes),
            "built_from": self.built_from,
            "leakage_review_ref": self.leakage_review_ref,
            "created_commit": self.created_commit,
        }


# --------------------------------------------------------------------------- #
# Canonical serialization + hashing (pure, deterministic, no I/O)
# --------------------------------------------------------------------------- #


def _canonical_record_bytes(record: dict[str, Any]) -> bytes:
    """Canonical UTF-8 bytes of a document record over {origin_domain,title,text}.

    Only the three payload fields are hashed; ``doc_id`` is the addressing key
    and is folded into the aggregate separately. ``sort_keys=True`` + tight
    separators make the hash independent of authoring key order, so a benign
    re-serialization of ``documents.json`` does not flip the hash.
    """
    payload = {
        "origin_domain": record["origin_domain"],
        "title": record["title"],
        "text": record["text"],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _doc_hash(record: dict[str, Any]) -> str:
    """SHA-256 hex digest of one document record's canonical bytes."""
    return hashlib.sha256(_canonical_record_bytes(record)).hexdigest()


def _aggregate_hash(doc_hashes: dict[str, str]) -> str:
    """SHA-256 hex digest over the sorted ``[doc_id, doc_hash]`` pair array.

    The material is a compact JSON array of 2-element ``[doc_id, doc_hash]``
    arrays, sorted by ``doc_id`` in Unicode code-point order::

        json.dumps([[doc_id, doc_hashes[doc_id]]
                    for doc_id in sorted(doc_hashes)],
                   separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    JSON string escaping makes this injective over every permitted doc_id
    (any non-empty string, including ":", newline, NUL, and control chars)
    and the fixed 64-char lowercase-hex doc_hash alphabet, so two distinct
    ``doc_hashes`` dicts cannot share an aggregate. Sorting by ``doc_id``
    keeps the aggregate independent of dict/JSON key order -- the replay
    guarantee: two structurally-identical snapshots share one aggregate.
    """
    material = json.dumps(
        [[doc_id, doc_hashes[doc_id]] for doc_id in sorted(doc_hashes)],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


# --------------------------------------------------------------------------- #
# JSON loading + structural validation (deterministic; no network)
# --------------------------------------------------------------------------- #


def _read_json_file(path: Path) -> Any:
    """Read and JSON-parse a file, wrapping decode errors as SnapshotIntegrityError."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise SnapshotIntegrityError(f"missing required file: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise SnapshotIntegrityError(f"malformed JSON in {path.name}: {exc}") from exc


def _require_str(value: Any, field: str, source: str) -> str:
    if not isinstance(value, str):
        raise SnapshotIntegrityError(f"{source}: field '{field}' must be a string")
    if value == "":
        raise SnapshotIntegrityError(f"{source}: field '{field}' must be non-empty")
    return value


def _load_manifest(path: Path) -> dict[str, Any]:
    """Load + structurally validate ``snapshot_manifest.json``."""
    raw = _read_json_file(path / MANIFEST_FILENAME)
    if not isinstance(raw, dict):
        raise SnapshotIntegrityError("manifest: top-level JSON must be an object")
    for field in _MANIFEST_REQUIRED_FIELDS:
        if field not in raw:
            raise SnapshotIntegrityError(f"manifest: missing required field '{field}'")

    aggregate_hash = _require_str(raw["aggregate_hash"], "aggregate_hash", "manifest")

    doc_hashes_raw = raw["doc_hashes"]
    if not isinstance(doc_hashes_raw, dict):
        raise SnapshotIntegrityError("manifest: field 'doc_hashes' must be an object")
    if len(doc_hashes_raw) == 0:
        raise SnapshotIntegrityError("manifest: field 'doc_hashes' must be non-empty")
    doc_hashes: dict[str, str] = {}
    for did, dh in doc_hashes_raw.items():
        if not isinstance(did, str) or did == "":
            raise SnapshotIntegrityError("manifest: doc_hashes keys must be non-empty strings")
        if not isinstance(dh, str) or dh == "":
            raise SnapshotIntegrityError(
                f"manifest: doc_hashes['{did}'] must be a non-empty string"
            )
        doc_hashes[did] = dh

    built_from = _require_str(raw["built_from"], "built_from", "manifest")
    leakage_review_ref = _require_str(raw["leakage_review_ref"], "leakage_review_ref", "manifest")
    created_commit = _require_str(raw["created_commit"], "created_commit", "manifest")

    return {
        "aggregate_hash": aggregate_hash,
        "doc_hashes": doc_hashes,
        "built_from": built_from,
        "leakage_review_ref": leakage_review_ref,
        "created_commit": created_commit,
    }


def _load_documents(path: Path) -> dict[str, dict[str, str]]:
    """Load + structurally validate ``documents.json``."""
    raw = _read_json_file(path / DOCUMENTS_FILENAME)
    if not isinstance(raw, dict):
        raise SnapshotIntegrityError("documents: top-level JSON must be an object")
    docs: dict[str, dict[str, str]] = {}
    for did, rec in raw.items():
        if not isinstance(did, str) or did == "":
            raise SnapshotIntegrityError("documents: keys must be non-empty strings")
        if not isinstance(rec, dict):
            raise SnapshotIntegrityError(f"documents['{did}']: record must be an object")
        for sub in ("origin_domain", "title", "text"):
            if sub not in rec:
                raise SnapshotIntegrityError(f"documents['{did}']: missing required field '{sub}'")
            if not isinstance(rec[sub], str):
                raise SnapshotIntegrityError(f"documents['{did}']: field '{sub}' must be a string")
        docs[did] = {
            "origin_domain": rec["origin_domain"],
            "title": rec["title"],
            "text": rec["text"],
        }
    return docs


# --------------------------------------------------------------------------- #
# Public integrity verification
# --------------------------------------------------------------------------- #


def verify_snapshot(path: str | Path) -> SnapshotManifest:
    """Load and integrity-verify a snapshot, raising on any mismatch.

    Recomputes every per-document SHA-256 and the aggregate SHA-256 from the
    on-disk documents and compares them against the manifest. Any structural
    problem (missing files, malformed JSON, wrong types), any missing or extra
    document, or any hash mismatch raises :class:`SnapshotIntegrityError`.

    Returns the parsed :class:`SnapshotManifest` on success. Pure filesystem +
    SHA-256: no network, no wall-clock, no env vars.
    """
    root = Path(path)
    if not root.exists():
        raise SnapshotIntegrityError(f"snapshot path does not exist: {root}")
    if not root.is_dir():
        raise SnapshotIntegrityError(f"snapshot path must be a directory: {root}")

    manifest = _load_manifest(root)
    doc_hashes: dict[str, str] = manifest["doc_hashes"]
    documents = _load_documents(root)

    # 1. Every manifest-declared document must be present with a matching hash.
    recomputed: dict[str, str] = {}
    for doc_id, expected_hash in doc_hashes.items():
        if doc_id not in documents:
            raise SnapshotIntegrityError(
                f"manifest declares document '{doc_id}' but it is absent from documents.json"
            )
        actual_hash = _doc_hash(documents[doc_id])
        recomputed[doc_id] = actual_hash
        if actual_hash != expected_hash:
            raise SnapshotIntegrityError(
                f"hash mismatch for document '{doc_id}': "
                f"manifest={expected_hash} recomputed={actual_hash}"
            )

    # 2. No undeclared documents (the corpus must equal the manifest exactly).
    extra = sorted(set(documents) - set(doc_hashes))
    if extra:
        raise SnapshotIntegrityError(
            f"documents.json contains undeclared document(s) not in manifest: {extra}"
        )

    # 3. The aggregate must reproduce from the recomputed per-document hashes.
    actual_aggregate = _aggregate_hash(recomputed)
    if actual_aggregate != manifest["aggregate_hash"]:
        raise SnapshotIntegrityError(
            f"aggregate hash mismatch: manifest={manifest['aggregate_hash']} "
            f"recomputed={actual_aggregate}"
        )

    return SnapshotManifest(
        aggregate_hash=manifest["aggregate_hash"],
        # Hand the manifest its own dict copy so the frozen object owns its data.
        doc_hashes=dict(doc_hashes),
        built_from=manifest["built_from"],
        leakage_review_ref=manifest["leakage_review_ref"],
        created_commit=manifest["created_commit"],
    )


__all__ = [
    "MANIFEST_FILENAME",
    "DOCUMENTS_FILENAME",
    "SnapshotIntegrityError",
    "SnapshotManifest",
    "verify_snapshot",
]
