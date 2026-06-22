"""
VELYNX Phase 61 — Episodic Narrative Memory (discovery alias)
=============================================================

The Episodic Narrative subsystem lives in :mod:`backend.memory.episodic`. This
thin module exists purely as a stable, conventionally-named *entry point* so the
narrative handler can be discovered under the ``…episodic_memory`` path (the name
the Phase 61 harness and external callers probe for) without importers needing to
know the internal module layout.

It re-exports the public narrative surface and adds nothing of its own — all
behaviour is defined once in :mod:`backend.memory.episodic`.
"""
from __future__ import annotations

from backend.memory.episodic import (  # noqa: F401
    EpisodicManager,
    EpisodicNarrativeHandler,
    NarrativeCompressor,
    episodic_manager,
    episodic_narrative_handler,
    extract_learning_subject,
    narrative_compressor,
)

__all__ = [
    "EpisodicManager",
    "EpisodicNarrativeHandler",
    "NarrativeCompressor",
    "episodic_manager",
    "episodic_narrative_handler",
    "extract_learning_subject",
    "narrative_compressor",
]
