"""Resource manager — memory pressure, connection pool tracking, resource limits."""
from __future__ import annotations

import logging

from backend.ops import ResourceSnapshot

logger = logging.getLogger("uvicorn")


class ResourceManager:
    """Monitors system resources and provides pressure signals."""

    def __init__(self, memory_threshold: int = 100000) -> None:
        self._memory_threshold = memory_threshold

    async def get_snapshot(self) -> ResourceSnapshot:
        """Capture current resource usage snapshot."""
        memory_entries = 0
        try:
            from memory.memory_manager import memory_manager
            stats = await memory_manager.stats()
            memory_entries = stats.total_entries if hasattr(stats, "total_entries") else 0
        except Exception:
            pass

        db_pool_out = 0
        db_pool_in = 0
        try:
            from database.engine import async_engine
            pool = async_engine.pool
            db_pool_out = pool.checkedout()
            db_pool_in = pool.checkedin()
        except Exception:
            pass

        redis_connected = False
        try:
            from database.redis_cache import redis_cache
            redis_connected = redis_cache.available
        except Exception:
            pass

        event_queue_depth = 0
        try:
            from runtime.event_bus import event_bus
            event_queue_depth = event_bus._queue.qsize() if event_bus._queue else 0
        except Exception:
            pass

        return ResourceSnapshot(
            memory_entries=memory_entries,
            db_pool_checked_out=db_pool_out,
            db_pool_checked_in=db_pool_in,
            redis_connected=redis_connected,
            event_queue_depth=event_queue_depth,
        )

    def check_memory_pressure(self, snapshot: ResourceSnapshot | None = None) -> bool:
        """Check if memory entries exceed threshold."""
        if snapshot:
            return snapshot.memory_entries > self._memory_threshold
        return False

    def check_pool_exhaustion(self, snapshot: ResourceSnapshot | None = None) -> bool:
        """Check if DB pool is near capacity."""
        if snapshot:
            total = snapshot.db_pool_checked_out + snapshot.db_pool_checked_in
            if total > 0:
                return snapshot.db_pool_checked_out / total > 0.9
        return False

    def get_recommendations(self, snapshot: ResourceSnapshot) -> list[str]:
        """Generate resource recommendations from snapshot."""
        recs = []
        if snapshot.memory_entries > self._memory_threshold:
            recs.append(
                f"High memory usage ({snapshot.memory_entries} entries). "
                f"Consider running memory decay."
            )
        if self.check_pool_exhaustion(snapshot):
            recs.append(
                f"DB pool near exhaustion ({snapshot.db_pool_checked_out} checked out). "
                f"Consider increasing pool size."
            )
        if snapshot.event_queue_depth > 1000:
            recs.append(
                f"Event queue depth is high ({snapshot.event_queue_depth}). "
                f"Check for slow handlers."
            )
        return recs


# Module-level singleton
resource_manager = ResourceManager()
