"""PA-1 builder-side ONLY -- offline snapshot construction (not on the EXP-1 path).

The ONLY module permitted to import ``backend.retrieval.unified_retriever``.
The import is DEFERRED to the function body so this module stays importable
without the (unpackaged) backend present; the conformance import-guard test
allow-lists ``backend.retrieval.unified_retriever`` for this module path only.
Its output passes the documented leakage review (CF-R4 / gate A3) before any
frozen-row exposure.

Reference: PROGRAM_A_FINAL_ARCHITECTURE.md Section 4 PA-1, Section 7;
PROGRAM_A_MODULE_SPEC.md Section 5.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Protocol, runtime_checkable

from program_a.evidence.snapshot_format import SnapshotManifest


@runtime_checkable
class Retriever(Protocol):
    """Builder-side retriever seam; the only sanctioned backend-retriever abstraction.

    Stubbable in CI so the builder smoke test never touches the live network.
    """

    def retrieve(self, query: str) -> list[dict]:
        """Return raw documents for one query (deterministic shape)."""
        ...


def build_snapshot(queries: Iterable[str], out_dir: str | Path) -> SnapshotManifest:
    """Build a frozen retrieval snapshot offline, before freeze.

    Drives ``backend.retrieval.unified_retriever`` (deferred import) to fetch
    documents, writes ``snapshot_manifest.json`` plus the documents, and returns
    the manifest. Run manually / in CI, never at execution time. Output must pass
    the leakage review (A3) before freeze.
    """
    raise NotImplementedError(
        "TODO(phase-6): deferred-import backend.retrieval.unified_retriever, fetch "
        "docs, write snapshot_manifest.json + docs, return SnapshotManifest; output "
        "passes leakage review (A3) before freeze."
    )


__all__ = ["build_snapshot", "Retriever"]
