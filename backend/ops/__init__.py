"""Runtime hardening and production deployment operations."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SubsystemHealth(BaseModel):
    """Health status of a single subsystem."""
    name: str
    status: str = "healthy"  # healthy, degraded, unavailable
    latency_ms: float = 0.0
    message: str = ""
    last_check: datetime = Field(default_factory=_now)


class HealthReport(BaseModel):
    """Overall system health report."""
    overall_status: str = "ready"  # ready, degraded, not_ready
    subsystems: list[SubsystemHealth] = Field(default_factory=list)
    uptime_seconds: float = 0.0
    version: str = "1.0.0"


class CircuitState(BaseModel):
    """State of a circuit breaker."""
    name: str
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    last_failure: datetime | None = None
    next_retry: datetime | None = None


class ResourceSnapshot(BaseModel):
    """Point-in-time resource usage snapshot."""
    timestamp: datetime = Field(default_factory=_now)
    memory_entries: int = 0
    db_pool_checked_out: int = 0
    db_pool_checked_in: int = 0
    redis_connected: bool = False
    event_queue_depth: int = 0
    active_requests: int = 0


class TokenBudget(BaseModel):
    """Token budget status."""
    period: str = "hour"  # request, hour, day
    limit: int = 100000
    used: int = 0
    remaining: int = 100000


class DeploymentProfile(BaseModel):
    """Configuration preset for deployment environments."""
    name: str = "development"  # development, staging, production
    max_concurrent_queries: int = 10
    query_timeout_seconds: int = 30
    token_budget_per_hour: int = 100000
    circuit_breaker_threshold: int = 5
    enable_prometheus: bool = False
    enable_opentelemetry: bool = False


# Default deployment profiles
DEVELOPMENT_PROFILE = DeploymentProfile(
    name="development",
    max_concurrent_queries=5,
    query_timeout_seconds=60,
    token_budget_per_hour=500000,
    circuit_breaker_threshold=10,
    enable_prometheus=False,
    enable_opentelemetry=False,
)

STAGING_PROFILE = DeploymentProfile(
    name="staging",
    max_concurrent_queries=10,
    query_timeout_seconds=30,
    token_budget_per_hour=200000,
    circuit_breaker_threshold=5,
    enable_prometheus=True,
    enable_opentelemetry=False,
)

PRODUCTION_PROFILE = DeploymentProfile(
    name="production",
    max_concurrent_queries=20,
    query_timeout_seconds=15,
    token_budget_per_hour=100000,
    circuit_breaker_threshold=3,
    enable_prometheus=True,
    enable_opentelemetry=True,
)

PROFILES = {
    "development": DEVELOPMENT_PROFILE,
    "staging": STAGING_PROFILE,
    "production": PRODUCTION_PROFILE,
}
