"""Persistence — memory recording and local SQLite storage."""
from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path

from backend.memory.memory_manager import memory_manager

logger = logging.getLogger("uvicorn")

_KG_DB = Path(__file__).resolve().parent.parent / "velynx_data" / "knowledge_graph" / "graph.db"


async def record_memory_turn(
    query: str,
    response: dict,
    source: str,
    tags: list[str] | None = None,
    concept_tags: list[str] | None = None,
) -> None:
    """Store an episodic memory for a pipeline turn."""
    confidence = str(response.get("confidence") or "UNKNOWN")
    if confidence == "UNKNOWN":
        return
    try:
        combined_tags = (tags or []) + (concept_tags or [])
        await memory_manager.store_episodic(
            query,
            str(response.get("answer") or ""),
            confidence=confidence,
            source=source,
            tags=combined_tags,
            kind=source,
            importance=0.7 if confidence == "CERTAIN" else 0.5,
        )
    except Exception as exc:
        # Non-critical: a failed embedding/storage must never crash the
        # reasoning loop. Surface it as a warning so the failure is visible.
        logger.warning("Memory storage failed (non-critical): %s", exc)


def persist_local(
    query: str,
    answer: str,
    confidence: str,
    session_id: str | None = None,
) -> None:
    """Persist a query/answer pair to the local SQLite database."""
    if not _KG_DB.exists():
        return
    try:
        db = sqlite3.connect(str(_KG_DB))
        db.execute(
            "CREATE TABLE IF NOT EXISTS sessions "
            "(session_id TEXT, query TEXT, answer TEXT, confidence TEXT, timestamp REAL)"
        )
        ts = time.time()
        db.execute(
            "INSERT OR REPLACE INTO understandings "
            "(topic, summary, confidence, query_count, timestamp) "
            "VALUES (?, ?, ?, "
            "COALESCE((SELECT query_count FROM understandings WHERE topic=?), 0) + 1, ?)",
            (query[:80], answer[:500], confidence, query[:80], ts),
        )
        db.execute(
            "INSERT OR REPLACE INTO sessions "
            "(session_id, query, answer, confidence, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id or "default", query[:200], answer[:500], confidence, ts),
        )
        db.commit()
        db.close()
    except Exception:
        pass
