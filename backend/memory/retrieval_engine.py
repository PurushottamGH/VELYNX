"""Retrieval engine — multi-signal ranking for semantic memory + state backend."""
from __future__ import annotations

import asyncio
import math
from datetime import datetime, timezone
from typing import Sequence

from backend.memory.memory_schemas import MemoryEntry, RetrievalResult

# Scoring weights
_W_SEMANTIC = 0.50
_W_IMPORTANCE = 0.20
_W_RECENCY = 0.15
_W_FREQUENCY = 0.15

# State-backend blend weights (same ratios MemoryRetriever used)
_TRIGGER_W = 0.7
_STATE_W = 0.3

# State-backend secondary rank weights
_COSINE_W = 0.8
_STRENGTH_W = 0.2
_MAX_THEORETICAL_STRENGTH = 10.0


def _state_query_to_vector(
    text_or_concepts: str | dict[str, float] | list[str],
) -> dict[str, float]:
    """
    Convert query text (or a bare concept list) into a concept-weight dict for
    the state vector backend.

    This replaces ``MemoryRetriever._normalize_query()``.  It accepts:
    * a string — parses into words, gives each a weight of 1.0
    * a dict — returned as-is (already a concept-weight mapping)
    * a list — each concept gets unit weight
    """
    if isinstance(text_or_concepts, dict):
        return {str(k): float(v) for k, v in text_or_concepts.items()}

    if isinstance(text_or_concepts, list):
        return {str(c): 1.0 for c in text_or_concepts}

    if isinstance(text_or_concepts, str):
        words = text_or_concepts.lower().split()
        return {w: 1.0 for w in words if len(w) > 2}

    return {}


def _cosine_similarity_state(
    query: dict[str, float], memory: dict[str, float]
) -> float:
    """
    Cosine similarity over the union of concept keys. Returns 0.0 when either
    vector has zero magnitude.

    Moved from ``MemoryRetriever._cosine_similarity()``.
    """
    if not query or not memory:
        return 0.0
    dot = 0.0
    for concept, qv in query.items():
        mv = memory.get(concept)
        if mv is not None:
            dot += float(qv) * float(mv)
    q_mag = sum(float(v) * float(v) for v in query.values()) ** 0.5
    m_mag = sum(float(v) * float(v) for v in memory.values()) ** 0.5
    if q_mag == 0.0 or m_mag == 0.0:
        return 0.0
    return dot / (q_mag * m_mag)


# ── Main entry point ───────────────────────────────────────────────────────────


async def retrieve(
    query_embedding: Sequence[float],
    backend,
    collection: str,
    limit: int = 5,
    *,
    query_concepts: dict[str, float] | None = None,
    state_backend=None,
) -> list[RetrievalResult]:
    """
    Retrieve and rank memories by multi-signal scoring.

    When *collection* is ``"state"``, the function uses the SQLite
    ``memory_log``-backed cosine path (``state_backend``) instead of the
    standard embedding backend.  The dense *query_embedding* is ignored for
    this collection; ranking is driven by *query_concepts* and the state
    backend's built-in concept-space cosine.

    For all other collections, the standard dense-embedding path runs.
    """
    # ── "state" collection: SQLite concept-cosine path ──────────────────────
    if collection == "state":
        return await _retrieve_state(
            query_concepts=query_concepts or {},
            state_backend=state_backend,
            limit=limit,
        )

    # ── Standard dense-embedding path ───────────────────────────────────────
    raw_hits = await backend.search(collection, query_embedding, limit=limit * 3)

    if not raw_hits:
        return []

    entry_ids = [entry_id for entry_id, _ in raw_hits]
    score_map = {entry_id: score for entry_id, score in raw_hits}
    entries = await backend.get_by_ids(collection, entry_ids)
    entries_with_scores: list[tuple[MemoryEntry, float]] = [
        (entry, score_map[entry.id]) for entry in entries if entry.id in score_map
    ]

    ranked = _rank_results(entries_with_scores)

    for result in ranked[:limit]:
        result.entry.access_count += 1
        result.entry.last_accessed = datetime.now(timezone.utc)

    return ranked[:limit]


# ── State collection handler ────────────────────────────────────────────────────


async def _retrieve_state(
    query_concepts: dict[str, float],
    state_backend,
    limit: int = 5,
) -> list[RetrievalResult]:
    """
    Retrieve from ``memory_log`` via concept-cosine similarity.

    Uses ``state_backend.search_by_concept_vector()`` (the
    ``StateVectorBackend`` method) to get scored row IDs, then re-ranks with
    the same hybrid blend + multi-signal formula the standard path uses.
    """
    from backend.memory.vector_backend import StateVectorBackend

    sb: StateVectorBackend | None = state_backend
    if sb is None:
        return []

    # Step 1: get raw cosine hits (oversample for re-rank)
    raw_hits = await sb.search_by_concept_vector(query_concepts, limit=limit * 3)

    if not raw_hits:
        return []

    # Step 2: load full MemoryEntry objects
    entry_ids = [eid for eid, _ in raw_hits]
    score_map = {eid: sc for eid, sc in raw_hits}
    entries = await sb.get_by_ids("state", entry_ids)

    # Step 3: re-rank with secondary blend (cosine * 0.8 + strength * 0.2)
    results: list[RetrievalResult] = []
    now = datetime.now(timezone.utc)

    for entry in entries:
        if entry.id not in score_map:
            continue
        cosine_raw = score_map[entry.id]
        # Normalize memory_strength from metadata as the secondary signal
        strength_raw = float(entry.metadata.get("memory_strength", 0.0) or 0.0)
        strength_norm = max(0.0, min(1.0, strength_raw / _MAX_THEORETICAL_STRENGTH))
        composite = (cosine_raw * _COSINE_W) + (strength_norm * _STRENGTH_W)

        results.append(RetrievalResult(
            entry=entry,
            score=round(composite, 4),
            rank=0,
            match_reason=f"state_cosine:{cosine_raw:.3f} strength:{strength_norm:.3f}",
        ))

    results.sort(key=lambda r: r.score, reverse=True)

    # Deduplicate by id
    seen: set[str] = set()
    deduped: list[RetrievalResult] = []
    for result in results:
        if result.entry.id not in seen:
            seen.add(result.entry.id)
            deduped.append(result)

    for i, result in enumerate(deduped):
        result.rank = i + 1

    return deduped[:limit]


# ── Ranking helpers ─────────────────────────────────────────────────────────────


def _rank_results(entries_with_scores: list[tuple[MemoryEntry, float]]) -> list[RetrievalResult]:
    """Apply multi-signal fusion scoring."""
    now = datetime.now(timezone.utc)
    scored: list[RetrievalResult] = []

    for entry, semantic_score in entries_with_scores:
        importance_score = entry.importance
        recency_score = _compute_recency(entry.created_at, now)
        frequency_score = _compute_frequency(entry.access_count)

        composite = (
            _W_SEMANTIC * semantic_score
            + _W_IMPORTANCE * importance_score
            + _W_RECENCY * recency_score
            + _W_FREQUENCY * frequency_score
        )

        reason = _explain_match(semantic_score, importance_score, recency_score, frequency_score)

        scored.append(RetrievalResult(
            entry=entry,
            score=round(composite, 4),
            rank=0,
            match_reason=reason,
        ))

    scored.sort(key=lambda r: r.score, reverse=True)

    # Deduplicate by id
    seen: set[str] = set()
    deduped: list[RetrievalResult] = []
    for result in scored:
        if result.entry.id not in seen:
            seen.add(result.entry.id)
            deduped.append(result)

    for i, result in enumerate(deduped):
        result.rank = i + 1

    return deduped


def _compute_recency(created_at: datetime, now: datetime) -> float:
    """Exponential decay: newer memories score higher. Half-life ~14 days."""
    age_seconds = max((now - created_at).total_seconds(), 0)
    half_life = 14 * 86400  # 14 days in seconds
    return math.exp(-0.693 * age_seconds / half_life)


def _compute_frequency(access_count: int) -> float:
    """Log-scaled access frequency. Saturates around 20 accesses."""
    if access_count <= 0:
        return 0.0
    return min(math.log1p(access_count) / math.log1p(20), 1.0)


def _explain_match(semantic: float, importance: float, recency: float, frequency: float) -> str:
    """Human-readable explanation of why this memory matched."""
    parts = []
    if semantic >= 0.7:
        parts.append("strong semantic match")
    elif semantic >= 0.4:
        parts.append("moderate semantic match")
    else:
        parts.append("weak semantic match")

    if importance >= 0.7:
        parts.append("high importance")
    if recency >= 0.8:
        parts.append("recent")
    if frequency >= 0.5:
        parts.append("frequently accessed")

    return ", ".join(parts)
