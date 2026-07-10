"""PA-1 -- evidence acquisition: load a verified snapshot, answer evidence_for.

The only execution-path evidence source. ``SnapshotStore`` is the concrete
implementation; ``EvidenceSource`` is the Protocol formalizing the PA-1 -> PA-2
seam so tests can inject synthetic sources.

Scope of THIS module (constant-independent half only):

* ``SnapshotStore.load`` -- verify a snapshot's integrity and index its
  documents into an immutable, provenance-tagged ``EvidenceItem`` map.
* ``snapshot_hash`` -- the loaded snapshot's aggregate SHA-256 (feeds
  ``mechanism_id``). REAL.
* ``evidence_for`` -- NOT YET IMPLEMENTABLE. It requires (a) the frozen
  ``constants.EVIDENCE_ORDERING_KEY`` total-order rule (now frozen at T1/G4
  from the Section 5 register), and (b) the PA-1 query->document lookup
  substrate (still gated by the A3 retrieval-mode decision, absent from the
  frozen 5-field SnapshotManifest schema). Rather than invent behavior, it
  raises ``RuntimeError`` naming the remaining prerequisite. No lookup rule may
  be guessed (CR-6/CR-11).

Deterministic guarantees for the implemented surface: identical snapshot dir
-> identical ``snapshot_hash`` and identical indexed ``EvidenceItem`` set, with
no network, no wall-clock, no env vars, no caching, no hidden state. The
``score`` and ``timestamp`` fields are absent from ``EvidenceItem`` by
construction (prereg Section 5; DATAFLOW Section 3 row 1).

Reference: PROGRAM_A_FINAL_ARCHITECTURE.md Section 4 PA-1;
PROGRAM_A_MODULE_SPEC.md Section 4.
"""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import Protocol, runtime_checkable

from program_a.constants import EVIDENCE_ORDERING_KEY
from program_a.evidence.snapshot_format import (
    _load_documents,
    SnapshotManifest,
    verify_snapshot,
)
from program_a.types import EvidenceItem, EvidenceSet


@runtime_checkable
class EvidenceSource(Protocol):
    """PA-1 -> PA-2 evidence seam; ``SnapshotStore`` implements it."""

    @property
    def snapshot_hash(self) -> str:
        """The loaded snapshot aggregate SHA-256 (feeds ``mechanism_id``)."""
        ...

    def evidence_for(self, query_text: str) -> EvidenceSet:
        """Return the ordered evidence set for one query."""
        ...


class SnapshotStore:
    """Verified-snapshot-backed evidence source (PA-1 execution path).

    Structurally satisfies ``EvidenceSource`` (runtime-checkable Protocol).
    Construct via :meth:`load`; do not instantiate directly.
    """

    __slots__ = ("_manifest", "_index")

    _manifest: SnapshotManifest
    _index: MappingProxyType[str, EvidenceItem]

    @classmethod
    def load(cls, path: str | Path) -> "SnapshotStore":
        """Load and integrity-verify a snapshot, returning a store.

        Calls :func:`verify_snapshot` (hard pre-run integrity gate), then
        indexes every document into an immutable ``EvidenceItem`` map keyed by
        ``doc_id``. Each item carries ``snapshot_hash_ref`` = the manifest
        aggregate hash, so downstream stages can attribute provenance without
        re-reading the snapshot.

        Pure filesystem read + dataclass construction: no network, no
        wall-clock, no env vars, no caching.
        """
        manifest = verify_snapshot(path)
        documents = _load_documents(Path(path))
        index: dict[str, EvidenceItem] = {}
        for doc_id, rec in documents.items():
            index[doc_id] = EvidenceItem(
                doc_id=doc_id,
                origin_domain=rec["origin_domain"],
                title=rec["title"],
                text=rec["text"],
                snapshot_hash_ref=manifest.aggregate_hash,
            )
        instance = cls.__new__(cls)
        instance._manifest = manifest
        instance._index = MappingProxyType(index)
        return instance

    @property
    def snapshot_hash(self) -> str:
        """The loaded snapshot's aggregate SHA-256 (feeds ``mechanism_id``)."""
        return self._manifest.aggregate_hash

    @property
    def manifest(self) -> SnapshotManifest:
        """The verified manifest (read-only view of the loaded snapshot)."""
        return self._manifest

    def documents(self) -> MappingProxyType[str, EvidenceItem]:
        """Read-only mapping ``doc_id -> EvidenceItem`` over the indexed corpus."""
        return self._index

    def evidence_for(self, query_text: str) -> EvidenceSet:
        """Return the ordered evidence set for ``query_text``.

        NOT YET IMPLEMENTABLE -- raises ``RuntimeError``.

        Prerequisite 1 -- the frozen total-order rule
        ``constants.EVIDENCE_ORDERING_KEY`` -- is now frozen at T1/G4 from the
        Section 5 register. Prerequisite 2 -- the PA-1 query->document lookup
        substrate (which documents answer a given query) -- is still gated by
        the A3 retrieval-mode decision and not present in the frozen 5-field
        ``SnapshotManifest`` schema; it must not be guessed (CR-6/CR-11).

        The moment prerequisite 2 is frozen, this method is implemented
        against the loaded index (no new I/O): select the matching doc_ids,
        apply the frozen total order, and wrap in an ``EvidenceSet``.
        """
        raise RuntimeError(
            "SnapshotStore.evidence_for is not implementable yet: "
            "EVIDENCE_ORDERING_KEY is now frozen at T1/G4 "
            f"({EVIDENCE_ORDERING_KEY!r}); the remaining prerequisite is the "
            "PA-1 query->document lookup substrate, which is gated by the A3 "
            "retrieval-mode decision and absent from the frozen 5-field "
            "SnapshotManifest schema. No lookup rule may be guessed "
            "(CR-6/CR-11)."
        )


__all__ = ["SnapshotStore", "EvidenceSource"]
