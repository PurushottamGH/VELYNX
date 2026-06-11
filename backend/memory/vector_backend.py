"""Vector storage backends — abstract protocol with ChromaDB and JSON implementations."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, Sequence

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
