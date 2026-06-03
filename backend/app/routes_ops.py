"""Ops and health API routes."""
from __future__ import annotations

import time

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Comprehensive health check."""
    from ops.health_monitor import health_monitor
    report = await health_monitor.check_all()
    return report.model_dump(mode="json")


@router.get("/readiness")
async def readiness() -> dict:
    """Readiness probe — checks critical dependencies."""
    from ops.health_monitor import health_monitor
    report = await health_monitor.check_all()
    return {
        "ready": report.overall == "healthy",
        "status": report.overall,
    }


@router.get("/liveness")
async def liveness() -> dict:
    """Liveness probe — always OK if process is running."""
    return {"alive": True}


@router.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    from ops.observability import observability
    return observability.get_stats()


@router.get("/ops/snapshot")
async def ops_snapshot() -> dict:
    """Point-in-time resource snapshot."""
    from ops.resource_manager import resource_manager
    snapshot = await resource_manager.get_snapshot()
    return snapshot.model_dump(mode="json")


@router.get("/ops/resources")
async def ops_resources() -> dict:
    """Resource utilization history."""
    from ops.resource_manager import resource_manager
    return {
        "current": (await resource_manager.get_snapshot()).model_dump(mode="json"),
        "history": [s.model_dump(mode="json") for s in resource_manager._history[-50:]],
    }


@router.get("/ops/token-budget")
async def ops_token_budget() -> dict:
    """Token budget status."""
    from ops.token_budget_manager import token_budget_manager
    return token_budget_manager.get_status()


@router.get("/ops/circuits")
async def ops_circuits() -> dict:
    """Circuit breaker states."""
    from ops.circuit_breakers import llm_circuit, redis_circuit, embedding_circuit
    return {
        "circuits": [
            llm_circuit.get_circuit_state().model_dump(mode="json"),
            redis_circuit.get_circuit_state().model_dump(mode="json"),
            embedding_circuit.get_circuit_state().model_dump(mode="json"),
        ]
    }


@router.get("/ops/status")
async def ops_status() -> dict:
    """Combined ops status."""
    from ops.runtime_supervisor import runtime_supervisor
    return await runtime_supervisor.get_status()


@router.get("/runtime/stats")
async def runtime_stats() -> dict:
    """Runtime event statistics."""
    from runtime.runtime_monitor import runtime_monitor
    return runtime_monitor.get_stats()


@router.get("/runtime/replay/{correlation_id}")
async def replay_events(correlation_id: str) -> list[dict]:
    """Replay events for a correlation ID."""
    from runtime.runtime_monitor import runtime_monitor
    return runtime_monitor.replay(correlation_id)
