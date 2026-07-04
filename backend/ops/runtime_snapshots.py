"""Runtime snapshots — periodic state capture for debugging."""
from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from typing import Any

from backend.ops import ResourceSnapshot
from backend.ops.resource_manager import resource_manager

logger = logging.getLogger("uvicorn")


class RuntimeSnapshotter:
    """Captures and stores runtime state snapshots."""

    def __init__(self, max_snapshots: int = 100) -> None:
        self._snapshots: deque[dict] = deque(maxlen=max_snapshots)
        self._llm_contexts: deque[dict] = deque(maxlen=50)
        self._retrieval_contexts: deque[dict] = deque(maxlen=50)

    async def capture(self, label: str = "") -> ResourceSnapshot:
        """Capture a resource snapshot."""
        snapshot = await resource_manager.get_snapshot()
        entry = {
            "label": label,
            "timestamp": snapshot.timestamp.isoformat(),
            "memory_entries": snapshot.memory_entries,
            "db_pool_out": snapshot.db_pool_checked_out,
            "db_pool_in": snapshot.db_pool_checked_in,
            "redis_connected": snapshot.redis_connected,
            "event_queue_depth": snapshot.event_queue_depth,
        }
        self._snapshots.append(entry)
        return snapshot

    def capture_llm_context(
        self,
        query: str,
        context: str,
        model_params: dict[str, Any] | None = None,
    ) -> None:
        """Capture pre-LLM call context for debugging."""
        self._llm_contexts.append({
            "timestamp": time.time(),
            "query": query[:200],
            "context_length": len(context),
            "model_params": model_params or {},
        })

    def capture_retrieval_context(
        self,
        query: str,
        sources: list[dict],
    ) -> None:
        """Capture retrieval context for debugging."""
        self._retrieval_contexts.append({
            "timestamp": time.time(),
            "query": query[:200],
            "source_count": len(sources),
            "sources": [
                {"url": s.get("url", ""), "title": s.get("title", "")}
                for s in sources[:5]
            ],
        })

    def get_recent(self, limit: int = 10) -> list[dict]:
        """Get recent snapshots."""
        return list(self._snapshots)[-limit:]

    def get_recent_llm_contexts(self, limit: int = 10) -> list[dict]:
        """Get recent LLM call contexts."""
        return list(self._llm_contexts)[-limit:]

    def get_recent_retrieval_contexts(self, limit: int = 10) -> list[dict]:
        """Get recent retrieval contexts."""
        return list(self._retrieval_contexts)[-limit:]

    def get_summary(self) -> dict:
        """Get a summary of captured snapshots."""
        if not self._snapshots:
            return {"snapshot_count": 0}

        latest = self._snapshots[-1]
        return {
            "snapshot_count": len(self._snapshots),
            "llm_context_count": len(self._llm_contexts),
            "retrieval_context_count": len(self._retrieval_contexts),
            "latest": latest,
        }


# Module-level singleton
runtime_snapshotter = RuntimeSnapshotter()
