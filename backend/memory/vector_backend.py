"""Vector storage backends — abstract protocol with ChromaDB, JSON, and SQLite implementations."""
from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, Sequence

from backend.memory import _sqlite
from backend.memory.memory_schemas import MemoryEntry

logger = logging.getLogger("uvicorn")

_CHROMA_DIR = Path("data/chroma_db")
_JSON_BACKEND_PATH = Path("data/vector_backend.json")


class VectorBackend(Protocol):
    """Abstract vector storage interface."""

    async def upsert(self, collection: str, entry: MemoryEntry, embedding: Sequence[float]) -> None: ...
    async def search(self, collection: str, embedding: Sequence[float], limit: int = 5) -> list[tuple[str, float]]: ...
    async def delete(self, collection: str, entry_id: str) -> None: ...
    async def count(self, collection: str) -> int: ...
    async def get_by_id(self, collection: str, entry_id: str) -> MemoryEntry | None: ...
    async def get_by_ids(self, collection: str, entry_ids: list[str]) -> list[MemoryEntry]: ...
    async def get_all(self, collection: str) -> list[MemoryEntry]: ...
    async def get_by_tag(self, collection: str, tag: str, limit: int = 5) -> list[MemoryEntry]: ...


class ChromaVectorBackend:
    """ChromaDB persistent vector store."""

    def __init__(self, persist_dir: Path = _CHROMA_DIR) -> None:
        import chromadb

        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collections: dict[str, Any] = {}

    def _get_collection(self, name: str):
        if name not in self._collections:
            self._collections[name] = self._client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[name]

    async def upsert(self, collection: str, entry: MemoryEntry, embedding: Sequence[float]) -> None:
        import asyncio

        col = self._get_collection(collection)
        metadata = {
            "kind": entry.kind,
            "source": entry.source or "",
            "confidence": entry.confidence,
            "importance": entry.importance,
            "access_count": entry.access_count,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "tags": json.dumps(entry.tags),
        }
        await asyncio.to_thread(
            col.upsert,
            ids=[entry.id],
            embeddings=[list(embedding)],
            documents=[entry.text],
            metadatas=[metadata],
        )

    async def search(self, collection: str, embedding: Sequence[float], limit: int = 5) -> list[tuple[str, float]]:
        import asyncio

        col = self._get_collection(collection)
        if col.count() == 0:
            return []

        def _query():
            results = col.query(
                query_embeddings=[list(embedding)],
                n_results=min(limit, col.count()),
                include=["documents", "distances", "metadatas"],
            )
            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]
            # ChromaDB returns cosine distance (0=identical, 2=opposite)
            # Convert to similarity: 1 - (distance / 2)
            return [(id_, 1.0 - d / 2.0) for id_, d in zip(ids, distances)]

        return await asyncio.to_thread(_query)

    async def delete(self, collection: str, entry_id: str) -> None:
        import asyncio

        col = self._get_collection(collection)
        await asyncio.to_thread(col.delete, ids=[entry_id])

    async def count(self, collection: str) -> int:
        col = self._get_collection(collection)
        return col.count()

    async def get_by_id(self, collection: str, entry_id: str) -> MemoryEntry | None:
        import asyncio

        col = self._get_collection(collection)

        def _fetch():
            results = col.get(ids=[entry_id], include=["documents", "metadatas"])
            ids = results.get("ids", [])
            if not ids:
                return None
            docs = results.get("documents", [])
            metas = results.get("metadatas", [])
            return _reconstruct_entry(ids[0], docs[0] if docs else "", metas[0] if metas else {})

        return await asyncio.to_thread(_fetch)

    async def get_by_ids(self, collection: str, entry_ids: list[str]) -> list[MemoryEntry]:
        import asyncio

        if not entry_ids:
            return []
        col = self._get_collection(collection)

        def _fetch():
            results = col.get(ids=entry_ids, include=["documents", "metadatas"])
            entries = []
            for id_, doc, meta in zip(
                results.get("ids", []),
                results.get("documents", []),
                results.get("metadatas", []),
            ):
                entries.append(_reconstruct_entry(id_, doc, meta))
            return entries

        return await asyncio.to_thread(_fetch)

    async def get_all(self, collection: str) -> list[MemoryEntry]:
        import asyncio

        col = self._get_collection(collection)

        def _fetch():
            if col.count() == 0:
                return []
            results = col.get(include=["documents", "metadatas"])
            entries = []
            for id_, doc, meta in zip(
                results.get("ids", []),
                results.get("documents", []),
                results.get("metadatas", []),
            ):
                entries.append(_reconstruct_entry(id_, doc, meta))
            return entries

        return await asyncio.to_thread(_fetch)

    async def get_by_tag(self, collection: str, tag: str, limit: int = 5) -> list[MemoryEntry]:
        import asyncio

        col = self._get_collection(collection)

        def _fetch():
            if col.count() == 0:
                return []
            results = col.get(
                where={"tags": {"$contains": tag}},
                limit=limit,
                include=["documents", "metadatas"],
            )
            entries = []
            for id_, doc, meta in zip(
                results.get("ids", []),
                results.get("documents", []),
                results.get("metadatas", []),
            ):
                entries.append(_reconstruct_entry(id_, doc, meta))
            return entries

        return await asyncio.to_thread(_fetch)


class JSONVectorBackend:
    """Fallback: stores entries as JSON with numpy embeddings on the side."""

    def __init__(self, path: Path = _JSON_BACKEND_PATH) -> None:
        self._path = path
        self._state = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return {}

    def _persist(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._state, default=str), encoding="utf-8")

    def _ensure_collection(self, name: str) -> dict:
        if name not in self._state:
            self._state[name] = {}
        return self._state[name]

    async def upsert(self, collection: str, entry: MemoryEntry, embedding: Sequence[float]) -> None:
        import asyncio

        col = self._ensure_collection(collection)
        col[entry.id] = {
            "entry": entry.model_dump(mode="json"),
            "embedding": list(embedding),
        }
        await asyncio.to_thread(self._persist)

    async def search(self, collection: str, embedding: Sequence[float], limit: int = 5) -> list[tuple[str, float]]:
        import asyncio

        col = self._ensure_collection(collection)
        if not col:
            return []

        def _search():
            import numpy as np

            query_vec = np.array(embedding, dtype=np.float32)
            results = []
            for entry_id, data in col.items():
                stored = np.array(data["embedding"], dtype=np.float32)
                sim = float(np.dot(query_vec, stored) / (np.linalg.norm(query_vec) * np.linalg.norm(stored) + 1e-8))
                results.append((entry_id, sim))
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]

        return await asyncio.to_thread(_search)

    async def delete(self, collection: str, entry_id: str) -> None:
        import asyncio

        col = self._ensure_collection(collection)
        col.pop(entry_id, None)
        await asyncio.to_thread(self._persist)

    async def count(self, collection: str) -> int:
        col = self._ensure_collection(collection)
        return len(col)

    async def get_by_id(self, collection: str, entry_id: str) -> MemoryEntry | None:
        col = self._ensure_collection(collection)
        data = col.get(entry_id)
        if not data:
            return None
        return MemoryEntry(**data["entry"])

    async def get_by_ids(self, collection: str, entry_ids: list[str]) -> list[MemoryEntry]:
        col = self._ensure_collection(collection)
        entries = []
        for eid in entry_ids:
            data = col.get(eid)
            if data:
                entries.append(MemoryEntry(**data["entry"]))
        return entries

    async def get_all(self, collection: str) -> list[MemoryEntry]:
        col = self._ensure_collection(collection)
        return [MemoryEntry(**data["entry"]) for data in col.values()]

    async def get_by_tag(self, collection: str, tag: str, limit: int = 5) -> list[MemoryEntry]:
        col = self._ensure_collection(collection)
        matches = []
        for data in col.values():
            entry = MemoryEntry(**data["entry"])
            if tag in entry.tags:
                matches.append(entry)
        return matches[:limit]


def _reconstruct_entry(entry_id: str, document: str, metadata: dict) -> MemoryEntry:
    """Reconstruct a MemoryEntry from ChromaDB stored data."""
    tags_raw = metadata.get("tags", "[]")
    tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw

    return MemoryEntry(
        id=entry_id,
        text=document,
        kind=metadata.get("kind", ""),
        source=metadata.get("source") or None,
        confidence=metadata.get("confidence", "UNKNOWN"),
        importance=metadata.get("importance", 0.5),
        access_count=metadata.get("access_count", 0),
        created_at=datetime.fromisoformat(metadata["created_at"]) if metadata.get("created_at") else datetime.now(timezone.utc),
        updated_at=datetime.fromisoformat(metadata["updated_at"]) if metadata.get("updated_at") else datetime.now(timezone.utc),
        tags=tags,
    )


class StateVectorBackend:
    """Read-only VectorBackend adapter over the SQLite ``memory_log`` table.

    Instead of dense embedding search, it queries ``memory_log`` rows by concept
    overlap (LIKE on ``activated_concepts_json`` / ``dominant_concepts_json``)
    and scores them with cosine similarity over concept-weight dicts.

    This replaces the legacy ``MemoryRetriever.retrieve_by_context()`` path —
    the cosine logic is identical, but the surface now conforms to the
    ``VectorBackend`` protocol so ``retrieval_engine.retrieve()`` can dispatch
    to it via the ``"state"`` collection handler.
    """

    def __init__(self, db_path: str = "velynx_state.db"):
        self.db_path = db_path

    # ── protocol methods ────────────────────────────────────
    # StateVectorBackend is a *read* adapter over a separate write path
    # (MemoryStore.log_experience).  Mutations are not supported.

    async def upsert(self, collection: str, entry: MemoryEntry, embedding: Sequence[float]) -> None:
        raise NotImplementedError("StateVectorBackend is read-only")

    async def search(
        self, collection: str, embedding: Sequence[float], limit: int = 5
    ) -> list[tuple[str, float]]:
        # Dense-embedding search makes no sense on concept-weight columns.
        # Call ``search_by_concept_vector()`` instead.
        return []

    async def delete(self, collection: str, entry_id: str) -> None:
        raise NotImplementedError("StateVectorBackend is read-only")

    # ── concept-vector search (the actual entry point) ─────

    async def search_by_concept_vector(
        self,
        query_concepts: dict[str, float],
        limit: int = 5,
    ) -> list[tuple[str, float]]:
        """
        Query ``memory_log`` rows whose concept columns share keys with
        ``query_concepts``, score them with cosine similarity over the
        *hybrid* representation (trigger 0.7 / state 0.3 blend), and return
        scored (row_id, score) pairs.

        This is the same two-stage scoring that ``MemoryRetriever`` used, but
        ported to return ``VectorBackend``-compatible output so the retrieval
        engine can dispatch to it through the standard ``retrieve()`` API.
        """
        if not query_concepts:
            return []

        with _sqlite.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(memory_log)")
            columns = {row[1] for row in cursor.fetchall()}
            has_activated = "activated_concepts_json" in columns

            search_cols = ["dominant_concepts_json"]
            if has_activated:
                search_cols.append("activated_concepts_json")

            like_parts: list[str] = []
            params: list[str] = []
            for concept in query_concepts:
                token = f'%"{concept}"%'
                for col in search_cols:
                    like_parts.append(f"{col} LIKE ?")
                    params.append(token)

            if not like_parts:
                return []

            like_clause = " OR ".join(like_parts)
            activated_select = (
                "activated_concepts_json" if has_activated else "NULL AS activated_concepts_json"
            )

            cursor.execute(f"""
                SELECT turn_index, memory_type, priority, user_input,
                       dominant_concepts_json, {activated_select}, memory_strength
                FROM memory_log
                WHERE priority IN ('high', 'medium')
                  AND ({like_clause})
            """, params)

            rows = cursor.fetchall()

        if not rows:
            return []

        TRIGGER_W = 0.7
        STATE_W = 0.3

        scored: list[tuple[str, float]] = []
        for row in rows:
            turn_index = row[0]
            dominant = _safe_json_state(row[4])
            activated = _safe_json_state(row[5]) if has_activated else {}

            trigger_cos = _cosine_similarity_state(query_concepts, activated)
            state_cos = _cosine_similarity_state(query_concepts, dominant)
            hybrid = (trigger_cos * TRIGGER_W) + (state_cos * STATE_W)

            row_id = str(turn_index)
            scored.append((row_id, round(hybrid, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    async def count(self, collection: str) -> int:
        with _sqlite.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM memory_log")
            return cur.fetchone()[0] or 0

    async def get_by_id(self, collection: str, entry_id: str) -> MemoryEntry | None:
        try:
            turn = int(entry_id)
        except (ValueError, TypeError):
            return None
        with _sqlite.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(memory_log)")
            has_activated = "activated_concepts_json" in {r[1] for r in cur.fetchall()}
            activated_col = "activated_concepts_json" if has_activated else "NULL AS activated_concepts_json"
            cur.execute(f"""
                SELECT turn_index, user_input, memory_type, priority,
                       dominant_concepts_json, {activated_col}, memory_strength
                FROM memory_log WHERE turn_index = ?
            """, (turn,))
            row = cur.fetchone()
        if not row:
            return None
        return _memory_log_row_to_entry(row)

    async def get_by_ids(self, collection: str, entry_ids: list[str]) -> list[MemoryEntry]:
        entries: list[MemoryEntry] = []
        for eid in entry_ids:
            e = await self.get_by_id(collection, eid)
            if e:
                entries.append(e)
        return entries

    async def get_all(self, collection: str) -> list[MemoryEntry]:
        with _sqlite.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(memory_log)")
            has_activated = "activated_concepts_json" in {r[1] for r in cur.fetchall()}
            activated_col = "activated_concepts_json" if has_activated else "NULL AS activated_concepts_json"
            cur.execute(f"""
                SELECT turn_index, user_input, memory_type, priority,
                       dominant_concepts_json, {activated_col}, memory_strength
                FROM memory_log ORDER BY turn_index DESC
            """)
            return [_memory_log_row_to_entry(row) for row in cur.fetchall()]

    async def get_by_tag(self, collection: str, tag: str, limit: int = 5) -> list[MemoryEntry]:
        with _sqlite.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(memory_log)")
            has_activated = "activated_concepts_json" in {r[1] for r in cur.fetchall()}
            if not has_activated:
                return []
            activated_col = "activated_concepts_json"
            token = f'%"{tag}"%'
            cur.execute(f"""
                SELECT turn_index, user_input, memory_type, priority,
                       dominant_concepts_json, {activated_col}, memory_strength
                FROM memory_log WHERE activated_concepts_json LIKE ?
                ORDER BY memory_strength DESC LIMIT ?
            """, (token, limit))
            return [_memory_log_row_to_entry(row) for row in cur.fetchall()]


# ── helpers ────────────────────────────────────────────────────────────────────


def _safe_json_state(raw: Any) -> dict[str, float]:
    """Parse a JSON concept-map column; empty dict on failure."""
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def _cosine_similarity_state(
    query: dict[str, float], memory: dict[str, float]
) -> float:
    """
    Cosine similarity over the union of concept keys. Returns 0.0 when either
    vector has zero magnitude.
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


def _memory_log_row_to_entry(row: sqlite3.Row | tuple) -> MemoryEntry:
    """
    Convert a ``memory_log`` row into a ``MemoryEntry`` so the retrieval engine
    can wrap it in a ``RetrievalResult``.

    Expected column order (from all SELECT queries above):
      0  turn_index
      1  user_input
      2  memory_type
      3  priority
      4  dominant_concepts_json
      5  activated_concepts_json
      6  memory_strength
    """
    turn_index = row[0]
    user_input = str(row[1] or "")
    mem_type = str(row[2] or "observation")
    priority = str(row[3] or "low")
    dominant = _safe_json_state(row[4])
    activated = _safe_json_state(row[5])
    strength = float(row[6] or 0.0)

    tags: list[str] = list(dominant.keys()) + [
        f"priority:{priority}",
        f"type:{mem_type}",
        f"state_turn:{turn_index}",
    ]

    return MemoryEntry(
        id=str(turn_index),
        text=user_input,
        kind="state",
        tags=tags,
        confidence="PROBABLE" if priority in ("high", "medium") else "LOW",
        importance=min(1.0, strength),
        metadata={
            "turn_index": turn_index,
            "memory_type": mem_type,
            "priority": priority,
            "dominant_concepts": dominant,
            "activated_concepts": activated,
            "memory_strength": strength,
        },
    )


def create_backend() -> VectorBackend:
    """Factory: create the configured vector backend."""
    backend_type = os.getenv("VELYNX_MEMORY_BACKEND", "chroma").lower()

    if backend_type == "chroma":
        try:
            return ChromaVectorBackend()
        except Exception as exc:
            logger.warning("ChromaDB init failed (%s), falling back to JSON backend", exc)
            return JSONVectorBackend()

    return JSONVectorBackend()
