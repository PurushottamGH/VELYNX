"""Default event handlers — observability, persistence, learning triggers."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backend.runtime.event_models import Event, EventType
from backend.runtime.runtime_monitor import runtime_monitor

if TYPE_CHECKING:
    from runtime.event_bus import EventBus

logger = logging.getLogger("uvicorn")


async def observability_handler(event: Event) -> None:
    """Global handler — records every event for monitoring."""
    await runtime_monitor.on_event(event)


async def persistence_handler(event: Event) -> None:
    """Persist specific event types to PostgreSQL via db_bridge."""
    from app.db_bridge import (
        persist_episode,
        persist_reflection,
        persist_context_snapshot,
        persist_feedback,
    )

    match event.type:
        case EventType.EPISODE_STORED:
            p = event.payload
            await persist_episode(
                prompt=p.get("prompt", ""),
                answer=p.get("answer", ""),
                confidence=p.get("confidence", "UNKNOWN"),
                source=p.get("source"),
                tags=p.get("tags"),
                kind=p.get("kind", "retrieval"),
                importance=p.get("importance", 0.5),
            )
        case EventType.REFLECTION_COMPLETED:
            p = event.payload
            await persist_reflection(
                query=p.get("query", ""),
                answer=p.get("answer", ""),
                reflection_result=p.get("reflection_result"),
            )
        case EventType.CONTEXT_SNAPSHOT_CREATED:
            p = event.payload
            await persist_context_snapshot(
                session_id=p.get("session_id"),
                snapshot_data=p.get("snapshot", {}),
            )
        case EventType.FEEDBACK_RECEIVED:
            p = event.payload
            await persist_feedback(
                query=p.get("query", ""),
                answer=p.get("answer", ""),
                rating=p.get("rating", 0),
                correction=p.get("correction"),
            )


async def learning_trigger_handler(event: Event) -> None:
    """Trigger learning subsystem on negative feedback."""
    from learning.online_learner import persist_learning_to_db

    if event.type == EventType.FEEDBACK_NEGATIVE:
        p = event.payload
        try:
            await persist_learning_to_db(
                query=p.get("query", ""),
                rating=p.get("rating", -1),
                meta=p.get("meta", {}),
                result=p.get("learning_result", {}),
            )
        except Exception as exc:
            logger.debug("Learning trigger skipped: %s", exc)


async def memory_event_handler(event: Event) -> None:
    """Log memory lifecycle events for debugging."""
    logger.debug(
        "Memory event: %s (correlation=%s)",
        event.type.value,
        event.correlation_id,
    )


def register_default_handlers(bus: "EventBus") -> None:
    """Register all default handlers on the event bus. Called at startup."""
    # Global observability handler (receives all events)
    bus.subscribe_all(observability_handler)

    # Persistence for specific event types
    bus.subscribe(EventType.EPISODE_STORED, persistence_handler)
    bus.subscribe(EventType.REFLECTION_COMPLETED, persistence_handler)
    bus.subscribe(EventType.CONTEXT_SNAPSHOT_CREATED, persistence_handler)
    bus.subscribe(EventType.FEEDBACK_RECEIVED, persistence_handler)

    # Learning triggers
    bus.subscribe(EventType.FEEDBACK_NEGATIVE, learning_trigger_handler)

    # Memory lifecycle logging
    bus.subscribe(EventType.MEMORY_STORED, memory_event_handler)
    bus.subscribe(EventType.MEMORY_DECAYED, memory_event_handler)
    bus.subscribe(EventType.MEMORY_EVICTED, memory_event_handler)
