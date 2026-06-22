"""Memory manager — orchestrates episodic, semantic, and working memory."""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from backend.memory.memory_schemas import (
    EpisodicMemory,
    MemoryEntry,
    MemoryStats,
    RetrievalResult,
    SemanticMemory,
    WorkingMemory,
)
from backend.memory.embedding_service import embedding_service
from backend.memory.vector_backend import StateVectorBackend, VectorBackend, create_backend
from backend.memory import retrieval_engine
from backend.memory.retrieval_engine import _state_query_to_vector

logger = logging.getLogger("uvicorn")

_COLLECTIONS = ("episodic", "semantic", "working")


def _to_serializable(embedding):
    """Convert a numpy embedding to a plain list of Python floats.

    The JSON-backed vector store cannot serialize numpy float32 scalars, so any
    array-like embedding must be coerced to native Python types before upsert.
    Already-list or None values pass through untouched.
    """
    if embedding is None:
        return None
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return embedding


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
        await self._backend.upsert("episodic", entry, _to_serializable(embedding))

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
        await self._backend.upsert("semantic", entry, _to_serializable(embedding))

        return SemanticMemory(
            entry=entry,
            concept=concept,
            relationships=relationships or [],
        )

    # ── Targeted semantic lookup / deletion (Phase 56 belief revision) ──

    async def find_semantic_memories(
        self, query_text: str, *, limit: int = 50, min_score: float = 0.0
    ) -> list[MemoryEntry]:
        """Return semantic entries most similar to ``query_text`` (full entries).

        Uses the backend's dense-vector ``search`` rather than ``get_all`` so a
        targeted fact is reliably retrieved regardless of how large the
        collection has grown (``get_all`` is subject to backend pagination and
        can silently omit the very row we need to revise). An exact-text fact
        embeds to ~identical vectors and lands at the top of the results.

        Returns ``[]`` when the embedding service is unavailable.
        """
        if not self._embedding.available:
            logger.warning(
                "Embedding service unavailable — cannot search semantic memories for %r",
                query_text[:60],
            )
            return []
        embedding = _to_serializable(await self._embedding.embed(query_text))
        hits = await self._backend.search("semantic", embedding, limit=limit)
        ids = [h[0] for h in hits if (h[1] if len(h) > 1 else 1.0) >= min_score]
        if not ids:
            return []
        return await self._backend.get_by_ids("semantic", ids)

    async def delete_semantic(self, ids: str | list[str]) -> int:
        """Delete semantic memories by id, pushing the delete down to the backend.

        Accepts a single id or a list. Returns the number actually deleted.
        Failures are logged loudly (``logger.exception``) and re-raised so a
        deletion that silently no-ops can never masquerade as success.
        """
        if isinstance(ids, str):
            ids = [ids]
        deleted = 0
        for entry_id in ids:
            try:
                await self._backend.delete("semantic", entry_id)
                deleted += 1
            except Exception:
                logger.exception("delete_semantic failed for id=%r", entry_id)
                raise
        return deleted

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
        await self._backend.upsert("working", entry, _to_serializable(embedding))

        return WorkingMemory(entry=entry, priority=priority)

    # ── Recall ───────────────────────────────────────────────────

    async def recall(
        self,
        query: str,
        limit: int = 5,
        kinds: list[str] | None = None,
        fallback_chain: list[str] | None = None,
    ) -> list[RetrievalResult]:
        """Recall memories across all kinds, ranked by multi-signal scoring.

        When *fallback_chain* is provided, collections are tried in the given
        order and results accumulate from all of them.  Recognised values:

        * ``"semantic"`` — dense-embedding search over episodic/semantic/working
          (the ``_backend`` configured via ``VELYNX_MEMORY_BACKEND``).
        * ``"state"``    — concept-cosine search over the SQLite ``memory_log``
          table (the ``StateVectorBackend``).
        * ``"tag"``      — tag-based lookup via ``recall_by_tag()``.

        If *fallback_chain* is omitted, only the *kinds* argument (defaulting to
        all three dense-embedding collections) is used — preserving the existing
        behaviour.
        """
        if fallback_chain is not None:
            return await self._recall_with_fallback(query, limit, fallback_chain)

        if not self._embedding.available:
            logger.warning("Embedding service not available, skipping semantic recall")
            return []

        query_embedding = _to_serializable(await self._embedding.embed(query))
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

    async def _recall_with_fallback(
        self,
        query: str,
        limit: int,
        fallback_chain: list[str],
    ) -> list[RetrievalResult]:
        """Dispatch across the backends listed in *fallback_chain*."""
        all_results: list[RetrievalResult] = []
        query_concepts = _state_query_to_vector(query)

        for stage in fallback_chain:
            stage = stage.strip().lower()

            if stage == "semantic":
                if not self._embedding.available:
                    continue
                query_embedding = _to_serializable(await self._embedding.embed(query))
                for kind in _COLLECTIONS:
                    results = await retrieval_engine.retrieve(
                        query_embedding, self._backend, kind, limit=limit,
                    )
                    all_results.extend(results)

            elif stage == "state":
                sb = StateVectorBackend()
                results = await retrieval_engine.retrieve(
                    query_embedding=[],  # unused for "state"
                    backend=self._backend,
                    collection="state",
                    limit=limit,
                    query_concepts=query_concepts,
                    state_backend=sb,
                )
                all_results.extend(results)

            elif stage == "tag":
                for tag_candidate in query_concepts:
                    tagged = await self.recall_by_tag(tag_candidate, limit=limit)
                    all_results.extend(tagged)

        # Global re-rank
        all_results.sort(key=lambda r: r.score, reverse=True)

        seen: set[str] = set()
        deduped: list[RetrievalResult] = []
        for result in all_results:
            if result.entry.id not in seen:
                seen.add(result.entry.id)
                deduped.append(result)

        for i, result in enumerate(deduped[:limit]):
            result.rank = i + 1

        return deduped[:limit]

    async def recall_by_tag(
        self,
        tag: str,
        collection: str = "episodic",
        limit: int = 5,
    ) -> list[RetrievalResult]:
        """Recall memories tagged with a specific concept tag."""
        entries = await self._backend.get_by_tag(collection, tag, limit=limit)
        results = []
        for entry in entries:
            results.append(RetrievalResult(
                entry=entry,
                score=entry.importance,
                rank=0,
                match_reason=f"concept_tag:{tag}",
            ))
        for i, result in enumerate(results):
            result.rank = i + 1
        return results

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
        await self._backend.upsert(collection, entry, _to_serializable(embedding))
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
                    await self._backend.upsert(collection, entry, _to_serializable(embedding))
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
