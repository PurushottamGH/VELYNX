"""Runtime supervisor — overall lifecycle management."""
from __future__ import annotations

import logging
import time
from typing import Any

from backend.ops.health_monitor import health_monitor
from backend.ops.failure_recovery import failure_recovery
from backend.ops.resource_manager import resource_manager
from backend.ops.observability import observability

logger = logging.getLogger("uvicorn")


class RuntimeSupervisor:
    """Manages the overall runtime lifecycle."""

    def __init__(self) -> None:
        self._startup_time: float = 0.0
        self._initialized = False

    async def startup(self) -> None:
        """Initialize all ops subsystems."""
        self._startup_time = time.time()
        observability.initialize()
        self._initialized = True
        logger.info("Runtime supervisor started")

    async def shutdown(self) -> None:
        """Graceful shutdown of ops subsystems."""
        logger.info("Runtime supervisor shutting down")
        self._initialized = False

    async def get_status(self) -> dict[str, Any]:
        """Get overall runtime status with auto-recovery on failures."""
        health = await health_monitor.check_all()
        resources = await resource_manager.get_snapshot()

        # Auto-recover unhealthy components
        recovery_attempts: dict[str, bool] = {}
        if hasattr(health, "database") and not getattr(health.database, "healthy", True):
            logger.warning("Database unhealthy — attempting auto-recovery")
            recovery_attempts["database"] = await failure_recovery.recover_database()
        if hasattr(health, "redis") and not getattr(health.redis, "healthy", True):
            logger.warning("Redis unhealthy — attempting auto-recovery")
            recovery_attempts["redis"] = await failure_recovery.recover_redis()
        if hasattr(health, "event_bus") and not getattr(health.event_bus, "healthy", True):
            logger.warning("Event bus unhealthy — attempting auto-recovery")
            recovery_attempts["event_bus"] = await failure_recovery.recover_event_bus()

        return {
            "initialized": self._initialized,
            "uptime_seconds": round(time.time() - self._startup_time, 1) if self._startup_time else 0,
            "health": health.model_dump(mode="json"),
            "resources": resources.model_dump(mode="json"),
            "observability": observability.get_stats(),
            "auto_recovery": recovery_attempts if recovery_attempts else None,
        }

    async def force_recovery(self, component: str) -> bool:
        """Attempt recovery of a specific component."""
        if component == "database":
            return await failure_recovery.recover_database()
        elif component == "redis":
            return await failure_recovery.recover_redis()
        elif component == "event_bus":
            return await failure_recovery.recover_event_bus()
        else:
            logger.warning("Unknown component: %s", component)
            return False


# Module-level singleton
runtime_supervisor = RuntimeSupervisor()
