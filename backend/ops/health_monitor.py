"""Health monitoring — comprehensive subsystem health checks."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone

from backend.ops import HealthReport, SubsystemHealth

logger = logging.getLogger("uvicorn")


class HealthMonitor:
    """Monitors health of all VELYNX subsystems."""

    def __init__(self) -> None:
        self._start_time = time.time()

    async def check_all(self) -> HealthReport:
        """Check all subsystems in parallel and return aggregate report."""
        checks = [
            self.check_database(),
            self.check_redis(),
            self.check_event_bus(),
            self.check_memory(),
        ]
        results = await asyncio.gather(*checks, return_exceptions=True)

        subsystems = []
        for result in results:
            if isinstance(result, Exception):
                subsystems.append(SubsystemHealth(
                    name="unknown",
                    status="unavailable",
                    message=str(result),
                ))
            else:
                subsystems.append(result)

        # Determine overall status
        statuses = [s.status for s in subsystems]
        if "unavailable" in statuses:
            overall = "not_ready"
        elif "degraded" in statuses:
            overall = "degraded"
        else:
            overall = "ready"

        return HealthReport(
            overall_status=overall,
            subsystems=subsystems,
            uptime_seconds=round(time.time() - self._start_time, 1),
        )

    async def check_database(self) -> SubsystemHealth:
        """Check database connectivity and pool status."""
        start = time.perf_counter()
        try:
            from database.engine import async_engine
            async with async_engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            pool = async_engine.pool
            latency = (time.perf_counter() - start) * 1000
            return SubsystemHealth(
                name="database",
                status="healthy",
                latency_ms=round(latency, 2),
                message=f"Pool: {pool.checkedout()} out, {pool.checkedin()} in",
            )
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            return SubsystemHealth(
                name="database",
                status="unavailable",
                latency_ms=round(latency, 2),
                message=str(exc)[:200],
            )

    async def check_redis(self) -> SubsystemHealth:
        """Check Redis connectivity."""
        start = time.perf_counter()
        try:
            from database.redis_cache import redis_cache
            if not redis_cache.available:
                return SubsystemHealth(
                    name="redis",
                    status="unavailable",
                    message="Redis not initialized",
                )
            await redis_cache._client.ping()
            latency = (time.perf_counter() - start) * 1000
            return SubsystemHealth(
                name="redis",
                status="healthy",
                latency_ms=round(latency, 2),
            )
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            return SubsystemHealth(
                name="redis",
                status="unavailable",
                latency_ms=round(latency, 2),
                message=str(exc)[:200],
            )

    async def check_event_bus(self) -> SubsystemHealth:
        """Check event bus consumer health."""
        try:
            from runtime.event_bus import event_bus
            if not event_bus._running:
                return SubsystemHealth(
                    name="event_bus",
                    status="unavailable",
                    message="Event bus not running",
                )
            if event_bus._consumer_task and event_bus._consumer_task.done():
                return SubsystemHealth(
                    name="event_bus",
                    status="unavailable",
                    message="Consumer task has exited",
                )
            queue_size = event_bus._queue.qsize() if event_bus._queue else 0
            status = "degraded" if queue_size > 1000 else "healthy"
            return SubsystemHealth(
                name="event_bus",
                status=status,
                message=f"Queue depth: {queue_size}",
            )
        except Exception as exc:
            return SubsystemHealth(
                name="event_bus",
                status="unavailable",
                message=str(exc)[:200],
            )

    async def check_memory(self) -> SubsystemHealth:
        """Check memory subsystem health."""
        try:
            from memory.memory_manager import memory_manager
            stats = await memory_manager.stats()
            total = stats.total_entries if hasattr(stats, "total_entries") else 0
            status = "degraded" if total > 100000 else "healthy"
            return SubsystemHealth(
                name="memory",
                status=status,
                message=f"Entries: {total}",
            )
        except Exception as exc:
            return SubsystemHealth(
                name="memory",
                status="degraded",
                message=str(exc)[:200],
            )

    def is_ready(self, report: HealthReport | None = None) -> bool:
        """Check if system is ready to serve requests."""
        if report:
            return report.overall_status == "ready"
        # If no report, assume ready (backward compat)
        return True

    def is_alive(self) -> bool:
        """Check if process is responsive."""
        return True


# Module-level singleton
health_monitor = HealthMonitor()
