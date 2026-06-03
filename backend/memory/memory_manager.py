"""Memory manager — orchestrates episodic, semantic, and working memory."""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from memory.memory_schemas import (
    EpisodicMemory,
    MemoryEntry,
    MemoryStats,
    RetrievalResult,
    SemanticMemory,
    WorkingMemory,
)
from memory.embedding_service import embedding_service
from memory.vector_backend import VectorBackend, create_backend
from memory import retrieval_engine

logger = logging.getLogger("uvicorn")

_COLLECTIONS = ("episodic", "semantic", "working")


class MemoryManager:
    """Unified memory orchestrator across three memory kinds."""

    def __init__(self, backend: VectorBackend | None = None) -> None:
        self._backend = backend or create_backend()
        self._embedding = embedding_service

    # ── Store ────────────────────────────────────────────────────

    async def store_episodic(
        self,
        prompt: str,
        answer: str,
        *,
        confidence: str = "PROBABLE",
        source: str | None = None,
        tags: list[str] | None = None,
        kind: str = "retrieval",
        importance: float = 0.5,
        context_snapshot: dict[str, Any] | None = None,
    ) -> EpisodicMemory:
        """Store a prompt-answer episode."""
        entry = MemoryEntry(
            text=f"{prompt}\n{answer}",
            kind="episodic",
            source=source,
            tags=tags or [],
            confidence=confidence,
            importance=importance,
            metadata={"prompt": prompt, "answer": answer, "episode_kind": kind},
        )
        embedding = await self._embedding.embed(entry.text)
        await self._backend.upsert("episodic", entry, embedding)

        return EpisodicMemory(
            entry=entry,
            prompt=prompt,
            answer=answer,
            context_snapshot=context_snapshot or {},
        )

    async def store_semantic(
        self,
        concept: str,
        text: str,
        *,
        relationships: list[str] | None = None,
        source: str | None = None,
        importance: float = 0.6,
    ) -> SemanticMemory:
        """Store a semantic concept."""
        entry = MemoryEntry(
            text=text,
            kind="semantic",
            source=source,
            importance=importance,
            metadata={"concept": concept, "relationships": relationships or []},
        )
        embedding = await self._embedding.embed(text)
        await self._backend.upsert("semantic", entry, embedding)

        return SemanticMemory(
            entry=entry,
            concept=concept,
            relationships=relationships or [],
        )

    async def store_working(
        self,
        text: str,
        *,
        priority: int = 5,
        ttl_seconds: int = 3600,
        source: str | None = None,
    ) -> WorkingMemory:
        """Store a short-lived working memory entry."""
        entry = MemoryEntry(
            text=text,
            kind="working",
            source=source,
            importance=priority / 10.0,
            ttl_seconds=ttl_seconds,
            metadata={"priority": priority},
        )
        embedding = await self._embedding.embed(text)
        await self._backend.upsert("working", entry, embedding)

        return WorkingMemory(entry=entry, priority=priority)

    # ── Recall ───────────────────────────────────────────────────

    async def recall(
        self,
        query: str,
        limit: int = 5,
        kinds: list[str] | None = None,
    ) -> list[RetrievalResult]:
        """Recall memories across all kinds, ranked by multi-signal scoring."""
        if not self._embedding.available:
            logger.warning("Embedding service not available, skipping semantic recall")
            return []

        query_embedding = await self._embedding.embed(query)
        target_kinds = kinds or list(_COLLECTIONS)

        all_results: list[RetrievalResult] = []
        for kind in target_kinds:
            results = await retrieval_engine.retrieve(
                query_embedding, self._backend, kind, limit=limit
            )
            all_results.extend(results)

        # Global re-rank across all kinds
        all_results.sort(key=lambda r: r.score, reverse=True)

        # Deduplicate
        seen: set[str] = set()
        deduped: list[RetrievalResult] = []
        for result in all_results:
            if result.entry.id not in seen:
                seen.add(result.entry.id)
                deduped.append(result)

        for i, result in enumerate(deduped[:limit]):
            result.rank = i + 1

        return deduped[:limit]

    # ── Reinforce ────────────────────────────────────────────────

    async def reinforce(self, entry_id: str, weight: float = 0.1, collection: str = "episodic") -> bool:
        """Increase importance of a memory entry."""
        entry = await self._backend.get_by_id(collection, entry_id)
        if not entry:
            return False

        entry.importance = min(entry.importance + weight, 1.0)
        entry.access_count += 1
        entry.last_accessed = datetime.now(timezone.utc)
        entry.updated_at = datetime.now(timezone.utc)

        embedding = await self._embedding.embed(entry.text)
        await self._backend.upsert(collection, entry, embedding)
        return True

    # ── Decay ────────────────────────────────────────────────────

    async def decay(self) -> dict[str, int]:
        """Apply memory decay — reduce importance of old, low-access entries."""
        stats = {"decayed": 0, "evicted": 0}
        now = datetime.now(timezone.utc)

        for collection in _COLLECTIONS:
            entries = await self._backend.get_all(collection)
            for entry in entries:
                age = now - entry.created_at

                # Evict expired working memory
                if collection == "working" and entry.ttl_seconds:
                    if age.total_seconds() > entry.ttl_seconds:
                        await self._backend.delete(collection, entry.id)
                        stats["evicted"] += 1
                        continue

                # Decay old, low-access entries
                if age > timedelta(days=30) and entry.access_count < 3:
                    entry.importance *= 0.9
                    entry.updated_at = now
                    embedding = await self._embedding.embed(entry.text)
                    await self._backend.upsert(collection, entry, embedding)
                    stats["decayed"] += 1

                # Evict very old, very low importance
                if age > timedelta(days=90) and entry.importance < 0.1:
                    await self._backend.delete(collection, entry.id)
                    stats["evicted"] += 1

        return stats

    # ── Stats ────────────────────────────────────────────────────

    async def stats(self) -> MemoryStats:
        """Get aggregate memory statistics."""
        total = 0
        by_kind: dict[str, int] = {}
        all_importances: list[float] = []
        oldest: datetime | None = None
        newest: datetime | None = None

        for collection in _COLLECTIONS:
            entries = await self._backend.get_all(collection)
            count = len(entries)
            by_kind[collection] = count
            total += count

            for entry in entries:
                all_importances.append(entry.importance)
                if oldest is None or entry.created_at < oldest:
                    oldest = entry.created_at
                if newest is None or entry.created_at > newest:
                    newest = entry.created_at

        return MemoryStats(
            total_entries=total,
            by_kind=by_kind,
            avg_importance=sum(all_importances) / len(all_importances) if all_importances else 0.0,
            oldest=oldest,
            newest=newest,
        )


# Module-level singleton
memory_manager = MemoryManager()
