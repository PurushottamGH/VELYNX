"""Tests for the cognitive runtime event system."""
from __future__ import annotations

import asyncio
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from runtime.event_models import Event, EventType, EventPriority, HandlerResult
from runtime.tracing import new_correlation_id, get_correlation_id, set_correlation_id, trace
from runtime.runtime_monitor import RuntimeMonitor, LatencyStats
from runtime.event_bus import EventBus


# ── Event Models ─────────────────────────────────────────────────

class TestEventModels:
    def test_event_creation(self):
        event = Event(type=EventType.QUERY_RECEIVED, source="test")
        assert event.type == EventType.QUERY_RECEIVED
        assert event.source == "test"
        assert event.priority == EventPriority.NORMAL
        assert len(event.id) == 16
        assert event.payload == {}

    def test_event_with_payload(self):
        event = Event(
            type=EventType.GOAL_CREATED,
            source="goal_engine",
            payload={"goal_id": "abc123", "description": "test goal"},
        )
        assert event.payload["goal_id"] == "abc123"

    def test_event_priority_enum(self):
        assert EventPriority.CRITICAL == 9
        assert EventPriority.HIGH == 7
        assert EventPriority.NORMAL == 5
        assert EventPriority.LOW == 3

    def test_event_type_values(self):
        assert EventType.QUERY_RECEIVED.value == "query_received"
        assert EventType.TASK_FAILED.value == "task_failed"
        assert EventType.MEMORY_STORED.value == "memory_stored"

    def test_handler_result(self):
        result = HandlerResult(
            handler_name="test_handler",
            event_id="abc",
            success=True,
            duration_ms=1.5,
        )
        assert result.success is True
        assert result.error is None

    def test_event_serialization(self):
        event = Event(type=EventType.PLAN_CREATED, source="planner")
        data = event.model_dump(mode="json")
        assert "type" in data
        assert data["type"] == "plan_created"
        # Round-trip
        restored = Event.model_validate(data)
        assert restored.type == EventType.PLAN_CREATED


# ── Tracing ──────────────────────────────────────────────────────

class TestTracing:
    def test_new_correlation_id(self):
        cid = new_correlation_id()
        assert len(cid) == 16
        assert cid != new_correlation_id()  # unique

    def test_set_get_correlation_id(self):
        set_correlation_id("test123")
        assert get_correlation_id() == "test123"

    @pytest.mark.asyncio
    async def test_trace_context_manager(self):
        async with trace("my_cid") as cid:
            assert cid == "my_cid"
            assert get_correlation_id() == "my_cid"
        # After exit, should be reset
        # (default is empty, get_correlation_id generates new)

    @pytest.mark.asyncio
    async def test_trace_auto_generates(self):
        async with trace() as cid:
            assert len(cid) == 16


# ── Runtime Monitor ──────────────────────────────────────────────

class TestRuntimeMonitor:
    def test_event_counting(self):
        monitor = RuntimeMonitor()
        event = Event(type=EventType.QUERY_RECEIVED, source="test")
        asyncio.get_event_loop().run_until_complete(monitor.on_event(event))
        asyncio.get_event_loop().run_until_complete(monitor.on_event(event))
        stats = monitor.get_stats()
        assert stats["total_events"] == 2
        assert stats["event_counts"]["query_received"] == 2

    def test_handler_latency(self):
        monitor = RuntimeMonitor()
        result = HandlerResult(
            handler_name="test_handler",
            event_id="abc",
            success=True,
            duration_ms=5.0,
        )
        monitor.record_handler_result(result)
        stats = monitor.get_stats()
        assert "test_handler" in stats["handlers"]
        assert stats["handlers"]["test_handler"]["call_count"] == 1

    def test_handler_error_tracking(self):
        monitor = RuntimeMonitor()
        result = HandlerResult(
            handler_name="bad_handler",
            event_id="abc",
            success=False,
            error="something broke",
            duration_ms=1.0,
        )
        monitor.record_handler_result(result)
        stats = monitor.get_stats()
        assert stats["handlers"]["bad_handler"]["error_count"] == 1

    def test_latency_stats(self):
        stats = LatencyStats()
        for i in range(100):
            stats.record(float(i))
        assert stats.count == 100
        assert stats.avg_ms == 49.5
        assert stats.max_ms == 99.0
        assert stats.p99_ms >= 98.0


# ── Event Bus ────────────────────────────────────────────────────

class TestEventBus:
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.QUERY_RECEIVED, handler)
        await bus.initialize()
        await bus.publish(Event(type=EventType.QUERY_RECEIVED, source="test"))
        # Give consumer time to process
        await asyncio.sleep(0.2)
        assert len(received) == 1
        assert received[0].type == EventType.QUERY_RECEIVED
        await bus.shutdown()

    @pytest.mark.asyncio
    async def test_global_handler(self):
        bus = EventBus()
        received = []

        async def global_handler(event: Event):
            received.append(event)

        bus.subscribe_all(global_handler)
        await bus.initialize()
        await bus.publish(Event(type=EventType.QUERY_RECEIVED, source="test"))
        await bus.publish(Event(type=EventType.GOAL_CREATED, source="test"))
        await asyncio.sleep(0.2)
        assert len(received) == 2
        await bus.shutdown()

    @pytest.mark.asyncio
    async def test_handler_failure_isolation(self):
        bus = EventBus()
        good_received = []

        async def bad_handler(event: Event):
            raise RuntimeError("handler broke")

        async def good_handler(event: Event):
            good_received.append(event)

        bus.subscribe(EventType.QUERY_RECEIVED, bad_handler)
        bus.subscribe(EventType.QUERY_RECEIVED, good_handler)
        await bus.initialize()
        await bus.publish(Event(type=EventType.QUERY_RECEIVED, source="test"))
        await asyncio.sleep(0.2)
        # Good handler should still receive the event
        assert len(good_received) == 1
        await bus.shutdown()

    @pytest.mark.asyncio
    async def test_no_cross_type_delivery(self):
        bus = EventBus()
        received = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.QUERY_RECEIVED, handler)
        await bus.initialize()
        await bus.publish(Event(type=EventType.GOAL_CREATED, source="test"))
        await asyncio.sleep(0.2)
        assert len(received) == 0
        await bus.shutdown()
