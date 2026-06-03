"""Retrieval engine — multi-signal ranking for semantic memory."""
from __future__ import annotations

import asyncio
import math
from datetime import datetime, timezone
from typing import Sequence

from memory.memory_schemas import MemoryEntry, RetrievalResult

# Scoring weights
_W_SEMANTIC = 0.50
_W_IMPORTANCE = 0.20
_W_RECENCY = 0.15
_W_FREQUENCY = 0.15


async def retrieve(
    query_embedding: Sequence[float],
    backend,
    collection: str,
    limit: int = 5,
) -> list[RetrievalResult]:
    """Retrieve and rank memories by multi-signal scoring."""
    # Step 1: Get semantic matches from vector backend (oversample for re-ranking)
    raw_hits = await backend.search(collection, query_embedding, limit=limit * 3)

    if not raw_hits:
        return []

    # Step 2: Load full entries in batch (single round-trip instead of N+1)
    entry_ids = [entry_id for entry_id, _ in raw_hits]
    score_map = {entry_id: score for entry_id, score in raw_hits}
    entries = await backend.get_by_ids(collection, entry_ids)
    entries_with_scores: list[tuple[MemoryEntry, float]] = [
        (entry, score_map[entry.id]) for entry in entries if entry.id in score_map
    ]

    # Step 3: Re-rank with multi-signal scoring
    ranked = _rank_results(entries_with_scores)

    # Step 4: Update access counts
    for result in ranked[:limit]:
        result.entry.access_count += 1
        result.entry.last_accessed = datetime.now(timezone.utc)

    return ranked[:limit]


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
