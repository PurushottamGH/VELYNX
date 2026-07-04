"""Async in-process event bus with priority queue, routing, and failure isolation."""
from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from backend.runtime.event_models import (
    Event,
    EventEnvelope,
    EventType,
    HandlerResult,
)

logger = logging.getLogger("uvicorn")

# Handler type: async callable that receives an Event
EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    """Async in-process event bus with typed routing and priority."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._global_handlers: list[EventHandler] = []
        self._redis_cache: Any = None
        self._persistence_enabled: bool = False
        self._running: bool = False
        self._queue: asyncio.PriorityQueue[tuple[int, int, Event]] | None = None
        self._consumer_task: asyncio.Task | None = None
        self._counter: int = 0  # tiebreaker for PriorityQueue

    async def initialize(
        self, redis_cache: Any = None, persistence_enabled: bool = False
    ) -> None:
        """Wire up Redis transport and start the priority queue consumer."""
        self._redis_cache = redis_cache
        self._persistence_enabled = (
            persistence_enabled and redis_cache and redis_cache.available
        )
        self._queue = asyncio.PriorityQueue()
        self._running = True
        self._consumer_task = asyncio.create_task(self._consume_loop())
        logger.info(
            "Event bus initialized (persistence=%s)", self._persistence_enabled
        )

    def subscribe(self, event_type: EventType | str, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        key = event_type.value if isinstance(event_type, EventType) else event_type
        self._handlers[key].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Register a handler that receives every event."""
        self._global_handlers.append(handler)

    async def publish(self, event: Event) -> list[HandlerResult]:
        """Publish an event. Routes to matching handlers + global handlers."""
        results: list[HandlerResult] = []

        # Enqueue for priority processing (priority, counter, event)
        if self._queue:
            # Queue depth protection
            if self._queue.qsize() > 10000:
                logger.warning("Event queue depth exceeds 10000, dropping event %s", event.type.value)
                return results
            self._counter += 1
            await self._queue.put((10 - event.priority, self._counter, event))

        # Optional persistence to Redis list
        if self._persistence_enabled:
            asyncio.create_task(self._persist_event(event))

        # Redis pub/sub broadcast (fire-and-forget)
        if self._redis_cache and self._redis_cache.available:
            asyncio.create_task(self._redis_publish(event))

        return results

    async def _consume_loop(self) -> None:
        """Priority queue consumer — dispatches events to handlers."""
        while self._running:
            try:
                _priority_val, _counter, event = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
                await self._dispatch(event)
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.debug("Event consume error: %s", exc)

    async def _dispatch(self, event: Event) -> list[HandlerResult]:
        """Dispatch a single event to all matching handlers. Failure-isolated."""
        results: list[HandlerResult] = []
        handlers = list(self._handlers.get(event.type.value, []))
        handlers.extend(self._global_handlers)

        for handler in handlers:
            result = await self._safe_invoke(handler, event)
            results.append(result)

        return results

    async def _safe_invoke(
        self, handler: EventHandler, event: Event
    ) -> HandlerResult:
        """Invoke a handler with timing, timeout, and failure isolation."""
        handler_name = getattr(handler, "__name__", repr(handler))
        start = time.perf_counter()
        try:
            await asyncio.wait_for(handler(event), timeout=5.0)
            duration_ms = (time.perf_counter() - start) * 1000
            return HandlerResult(
                handler_name=handler_name,
                event_id=event.id,
                success=True,
                duration_ms=duration_ms,
            )
        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.warning(
                "Handler %s timed out for event %s (%s)",
                handler_name, event.type.value, event.id,
            )
            return HandlerResult(
                handler_name=handler_name,
                event_id=event.id,
                success=False,
                error="Handler timed out (5s)",
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.warning(
                "Handler %s failed for event %s (%s): %s",
                handler_name, event.type.value, event.id, exc,
            )
            return HandlerResult(
                handler_name=handler_name,
                event_id=event.id,
                success=False,
                error=str(exc),
                duration_ms=duration_ms,
            )

    async def _persist_event(self, event: Event) -> None:
        """Push event to a Redis list for replay. TTL prevents unbounded growth."""
        try:
            key = f"events:{event.correlation_id}"
            await self._redis_cache._client.rpush(key, event.model_dump_json())
            await self._redis_cache._client.expire(key, 86400)
        except Exception:
            pass

    async def _redis_publish(self, event: Event) -> None:
        """Publish event to Redis pub/sub channel."""
        try:
            envelope = EventEnvelope(event=event)
            await self._redis_cache._client.publish(
                "velynx:events", envelope.model_dump_json()
            )
        except Exception:
            pass

    async def replay(self, correlation_id: str) -> list[Event]:
        """Replay all events for a correlation ID from Redis persistence."""
        if not self._persistence_enabled:
            return []
        try:
            key = f"events:{correlation_id}"
            raw_list = await self._redis_cache._client.lrange(key, 0, -1)
            return [Event.model_validate_json(raw) for raw in raw_list]
        except Exception:
            return []

    async def shutdown(self) -> None:
        """Drain the queue and stop the consumer."""
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass


# Module-level singleton
event_bus = EventBus()
