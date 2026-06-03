"""Tests for the runtime hardening ops module."""
from __future__ import annotations

import asyncio
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ops import (
    SubsystemHealth, HealthReport, CircuitState, ResourceSnapshot,
    TokenBudget, DeploymentProfile, PROFILES,
)
from ops.circuit_breakers import CircuitBreaker, CircuitOpenError
from ops.load_shedding import LoadShedder, LoadShedError
from ops.token_budget_manager import TokenBudgetManager
from ops.resource_manager import ResourceManager
from ops.runtime_snapshots import RuntimeSnapshotter
from ops.observability import ObservabilityManager
from ops.failure_recovery import FailureRecovery
from ops.runtime_supervisor import RuntimeSupervisor


# ── Model Tests ──────────────────────────────────────────────────

class TestModels:
    def test_subsystem_health(self):
        h = SubsystemHealth(name="test", status="healthy")
        assert h.status == "healthy"

    def test_health_report(self):
        r = HealthReport()
        assert r.overall_status == "ready"
        assert r.version == "1.0.0"

    def test_circuit_state(self):
        s = CircuitState(name="test")
        assert s.state == "closed"
        assert s.failure_count == 0

    def test_resource_snapshot(self):
        s = ResourceSnapshot()
        assert s.memory_entries == 0

    def test_token_budget(self):
        b = TokenBudget()
        assert b.period == "hour"
        assert b.remaining == 100000

    def test_deployment_profiles(self):
        assert "development" in PROFILES
        assert "staging" in PROFILES
        assert "production" in PROFILES
        assert PROFILES["production"].max_concurrent_queries > PROFILES["development"].max_concurrent_queries


# ── Circuit Breaker Tests ────────────────────────────────────────

class TestCircuitBreaker:
    @pytest.mark.asyncio
    async def test_closed_state_passes(self):
        cb = CircuitBreaker("test", threshold=3, cooldown_seconds=1)

        async def success():
            return "ok"

        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == "closed"

    @pytest.mark.asyncio
    async def test_opens_after_threshold(self):
        cb = CircuitBreaker("test", threshold=3, cooldown_seconds=10)

        async def fail():
            raise RuntimeError("fail")

        for _ in range(3):
            with pytest.raises(RuntimeError):
                await cb.call(fail)

        assert cb.state == "open"
        with pytest.raises(CircuitOpenError):
            await cb.call(fail)

    @pytest.mark.asyncio
    async def test_half_open_after_cooldown(self):
        cb = CircuitBreaker("test", threshold=1, cooldown_seconds=0.1)

        async def fail():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == "open"

        await asyncio.sleep(0.15)
        assert cb.state == "half_open"

    @pytest.mark.asyncio
    async def test_closes_on_half_open_success(self):
        cb = CircuitBreaker("test", threshold=1, cooldown_seconds=0.1)

        async def fail():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            await cb.call(fail)

        await asyncio.sleep(0.15)

        async def success():
            return "ok"

        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == "closed"

    def test_reset(self):
        cb = CircuitBreaker("test", threshold=1, cooldown_seconds=10)
        cb._state = "open"
        cb._failure_count = 5
        cb.reset()
        assert cb.state == "closed"
        assert cb._failure_count == 0

    def test_get_circuit_state(self):
        cb = CircuitBreaker("test", threshold=5, cooldown_seconds=30)
        state = cb.get_circuit_state()
        assert state.name == "test"
        assert state.state == "closed"


# ── Load Shedding Tests ──────────────────────────────────────────

class TestLoadShedding:
    @pytest.mark.asyncio
    async def test_acquire_release(self):
        shedder = LoadShedder(max_concurrent=2)
        async with shedder.acquire():
            stats = shedder.get_stats()
            assert stats["active_count"] == 1
        stats = shedder.get_stats()
        assert stats["active_count"] == 0

    @pytest.mark.asyncio
    async def test_low_priority_shed(self):
        shedder = LoadShedder(max_concurrent=1)
        async with shedder.acquire():
            with pytest.raises(LoadShedError):
                async with shedder.acquire(priority="low"):
                    pass

    def test_get_stats(self):
        shedder = LoadShedder(max_concurrent=10)
        stats = shedder.get_stats()
        assert stats["max_concurrent"] == 10
        assert stats["active_count"] == 0


# ── Token Budget Tests ───────────────────────────────────────────

class TestTokenBudget:
    def test_record_usage(self):
        mgr = TokenBudgetManager(hourly_limit=1000, request_limit=100)
        mgr.record_usage(500)
        budget = mgr.check_budget()
        assert budget.used == 500
        assert budget.remaining == 500

    def test_can_proceed(self):
        mgr = TokenBudgetManager(hourly_limit=1000, request_limit=100)
        assert mgr.can_proceed(500) is True
        mgr.record_usage(800)
        assert mgr.can_proceed(500) is False

    def test_reset(self):
        mgr = TokenBudgetManager(hourly_limit=1000, request_limit=100)
        mgr.record_usage(500)
        mgr.reset()
        budget = mgr.check_budget()
        assert budget.used == 0

    def test_total_usage(self):
        mgr = TokenBudgetManager()
        mgr.record_usage(100)
        mgr.record_usage(200)
        assert mgr.get_total_usage() == 300


# ── Resource Manager Tests ───────────────────────────────────────

class TestResourceManager:
    @pytest.mark.asyncio
    async def test_get_snapshot(self):
        mgr = ResourceManager()
        snapshot = await mgr.get_snapshot()
        assert isinstance(snapshot, ResourceSnapshot)

    def test_memory_pressure(self):
        mgr = ResourceManager(memory_threshold=1000)
        snapshot = ResourceSnapshot(memory_entries=500)
        assert mgr.check_memory_pressure(snapshot) is False
        snapshot2 = ResourceSnapshot(memory_entries=2000)
        assert mgr.check_memory_pressure(snapshot2) is True

    def test_recommendations(self):
        mgr = ResourceManager(memory_threshold=1000)
        snapshot = ResourceSnapshot(memory_entries=5000, event_queue_depth=5000)
        recs = mgr.get_recommendations(snapshot)
        assert len(recs) >= 2


# ── Observability Tests ──────────────────────────────────────────

class TestObservability:
    def test_record_event(self):
        obs = ObservabilityManager()
        obs.record_event("query_received", "handler1", 10.5)
        stats = obs.get_stats()
        assert len(stats["counters"]) > 0

    def test_record_llm_call(self):
        obs = ObservabilityManager()
        obs.record_llm_call("gpt-4", 1000, 500.0, "success")
        stats = obs.get_stats()
        assert len(stats["counters"]) > 0

    def test_get_metrics(self):
        obs = ObservabilityManager()
        obs.record_event("test", "handler", 10.0)
        metrics = obs.get_metrics()
        assert "events_total" in metrics

    def test_set_gauge(self):
        obs = ObservabilityManager()
        obs.set_gauge("memory_entries", 42)
        assert obs._gauges["memory_entries"] == 42

    def test_reset(self):
        obs = ObservabilityManager()
        obs.record_event("test", "handler", 10.0)
        obs.reset()
        assert len(obs._counters) == 0


# ── Runtime Snapshotter Tests ────────────────────────────────────

class TestRuntimeSnapshotter:
    @pytest.mark.asyncio
    async def test_capture(self):
        snapshotter = RuntimeSnapshotter()
        snapshot = await snapshotter.capture("test")
        assert isinstance(snapshot, ResourceSnapshot)
        recent = snapshotter.get_recent(1)
        assert len(recent) == 1

    def test_capture_llm_context(self):
        snapshotter = RuntimeSnapshotter()
        snapshotter.capture_llm_context("test query", "test context")
        contexts = snapshotter.get_recent_llm_contexts()
        assert len(contexts) == 1

    def test_capture_retrieval_context(self):
        snapshotter = RuntimeSnapshotter()
        snapshotter.capture_retrieval_context("test", [{"url": "http://x.com"}])
        contexts = snapshotter.get_recent_retrieval_contexts()
        assert len(contexts) == 1

    def test_get_summary(self):
        snapshotter = RuntimeSnapshotter()
        summary = snapshotter.get_summary()
        assert summary["snapshot_count"] == 0


# ── Runtime Supervisor Tests ─────────────────────────────────────

class TestRuntimeSupervisor:
    @pytest.mark.asyncio
    async def test_startup_shutdown(self):
        supervisor = RuntimeSupervisor()
        await supervisor.startup()
        assert supervisor._initialized is True
        await supervisor.shutdown()
        assert supervisor._initialized is False

    @pytest.mark.asyncio
    async def test_get_status(self):
        supervisor = RuntimeSupervisor()
        await supervisor.startup()
        status = await supervisor.get_status()
        assert "health" in status
        assert "resources" in status
        await supervisor.shutdown()
