"""Failure recovery — automatic recovery strategies for common failure modes."""
from __future__ import annotations

import logging

logger = logging.getLogger("uvicorn")


class FailureRecovery:
    """Attempts automatic recovery of failed subsystems."""

    async def recover_database(self) -> bool:
        """Attempt to recover database connectivity."""
        try:
            from database.engine import async_engine
            async with async_engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            logger.info("Database recovery successful")
            return True
        except Exception as exc:
            logger.warning("Database recovery failed: %s", exc)
            return False

    async def recover_redis(self) -> bool:
        """Attempt to recover Redis connectivity."""
        try:
            from database.redis_cache import redis_cache
            import os
            await redis_cache.initialize(os.getenv("REDIS_URL"))
            logger.info("Redis recovery successful")
            return True
        except Exception as exc:
            logger.warning("Redis recovery failed: %s", exc)
            return False

    async def recover_event_bus(self) -> bool:
        """Attempt to restart event bus consumer."""
        try:
            from runtime.event_bus import event_bus
            if event_bus._consumer_task and event_bus._consumer_task.done():
                event_bus._running = True
                event_bus._consumer_task = __import__("asyncio").create_task(
                    event_bus._consume_loop()
                )
                logger.info("Event bus consumer restarted")
                return True
            return True  # Already running
        except Exception as exc:
            logger.warning("Event bus recovery failed: %s", exc)
            return False

    async def recover_all(self) -> dict[str, bool]:
        """Attempt recovery of all subsystems."""
        results = {}
        results["database"] = await self.recover_database()
        results["redis"] = await self.recover_redis()
        results["event_bus"] = await self.recover_event_bus()
        return results


# Module-level singleton
failure_recovery = FailureRecovery()
