"""Application lifespan — startup and shutdown sequence."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

logger = logging.getLogger("uvicorn")


def _log_retrieval_sources() -> None:
    """Log which retrieval sources are active at boot time."""
    active = ["wikipedia (free)", "arxiv (free)", "duckduckgo (free)"]
    optional: list[str] = []

    if os.getenv("OPENGATEWAY_API_KEY", "").strip():
        optional.append("opengateway/llm (enhanced reasoning)")
    if os.getenv("BRAVE_SEARCH_API_KEY", "").strip():
        optional.append("brave (enhanced search)")
    if os.getenv("TAVILY_API_KEY", "").strip():
        optional.append("tavily (enhanced search)")
    if os.getenv("SEARXNG_BASE_URL", "").strip():
        optional.append("searxng (self-hosted search)")

    logger.info("Core retrieval sources: %s", ", ".join(active))
    if optional:
        logger.info("Optional enhancements: %s", ", ".join(optional))


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _log_retrieval_sources()

    # Initialize database (Phase 4)
    try:
        from database.runtime_state import runtime_state
        await runtime_state.initialize()
        logger.info("Database initialized")
    except Exception as exc:
        logger.warning("Database init skipped: %s", exc)

    # Initialize Redis cache
    try:
        from database.redis_cache import redis_cache
        await redis_cache.initialize(os.getenv("REDIS_URL"))
    except Exception as exc:
        logger.debug("Redis cache skipped: %s", exc)

    # Create session
    _session_id = None
    try:
        from database.engine import async_session
        from database.repositories import SessionRepository
        async with async_session() as db:
            sess = await SessionRepository(db).create()
            _session_id = sess.id
            _app.state.session_id = _session_id
            logger.info("Session started: %s", _session_id)
    except Exception as exc:
        logger.debug("Session creation skipped: %s", exc)

    # Initialize event bus (Phase 6)
    try:
        from runtime.event_bus import event_bus
        from runtime.event_handlers import register_default_handlers
        from database.redis_cache import redis_cache as _redis
        register_default_handlers(event_bus)
        await event_bus.initialize(redis_cache=_redis, persistence_enabled=True)
        logger.info("Event bus initialized")
    except Exception as exc:
        logger.warning("Event bus init skipped: %s", exc)

    # Initialize runtime supervisor (Phase 10)
    try:
        from ops.runtime_supervisor import runtime_supervisor
        await runtime_supervisor.startup()
        logger.info("Runtime supervisor started")
    except Exception as exc:
        logger.warning("Runtime supervisor init skipped: %s", exc)

    # Run memory decay on startup
    try:
        from memory.memory_manager import memory_manager
        decay_stats = await memory_manager.decay()
        logger.info("Memory decay: %s", decay_stats)
    except Exception as exc:
        logger.debug("Memory decay skipped: %s", exc)

    # Phase 20: Proactive Cognition
    try:
        from learning.proactive_cognition import proactive_cognition
        await proactive_cognition.start(interval_override=300)
        logger.info("Proactive cognition started")
    except Exception as exc:
        logger.warning("Proactive cognition init skipped: %s", exc)

    yield

    # Shutdown: proactive cognition
    try:
        from learning.proactive_cognition import proactive_cognition as _pc
        await _pc.stop()
    except Exception:
        pass

    # Shutdown: runtime supervisor
    try:
        from ops.runtime_supervisor import runtime_supervisor as _supervisor
        await _supervisor.shutdown()
    except Exception:
        pass

    # Shutdown: event bus
    try:
        from runtime.event_bus import event_bus as _bus
        await _bus.shutdown()
    except Exception:
        pass

    # Shutdown: end session
    if _session_id:
        try:
            from database.engine import async_session
            from database.repositories import SessionRepository
            async with async_session() as db:
                await SessionRepository(db).end_session(_session_id)
                logger.info("Session ended: %s", _session_id)
        except Exception:
            pass

    # Shutdown: close Redis
    try:
        from database.redis_cache import redis_cache
        await redis_cache.close()
    except Exception:
        pass
