"""Circuit breaker pattern for external dependencies."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from backend.ops import CircuitState

logger = logging.getLogger("uvicorn")


class CircuitBreaker:
    """Async circuit breaker with closed/open/half-open states."""

    def __init__(
        self,
        name: str,
        threshold: int = 5,
        cooldown_seconds: float = 30.0,
    ) -> None:
        self._name = name
        self._threshold = threshold
        self._cooldown = cooldown_seconds
        self._state = "closed"
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._half_open_calls = 0

    @property
    def state(self) -> str:
        if self._state == "open":
            if time.time() - self._last_failure_time >= self._cooldown:
                self._state = "half_open"
                self._half_open_calls = 0
        return self._state

    def get_circuit_state(self) -> CircuitState:
        """Get current circuit state as a model."""
        from datetime import datetime, timezone
        return CircuitState(
            name=self._name,
            state=self.state,
            failure_count=self._failure_count,
            last_failure=datetime.fromtimestamp(self._last_failure_time, tz=timezone.utc)
            if self._last_failure_time else None,
            next_retry=datetime.fromtimestamp(
                self._last_failure_time + self._cooldown, tz=timezone.utc
            ) if self._last_failure_time and self._state == "open" else None,
        )

    async def call(self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        """Execute a function with circuit breaker protection."""
        current_state = self.state

        if current_state == "open":
            raise CircuitOpenError(
                f"Circuit '{self._name}' is open. "
                f"Retry after {self._cooldown}s."
            )

        if current_state == "half_open":
            if self._half_open_calls >= 1:
                raise CircuitOpenError(
                    f"Circuit '{self._name}' is half-open, probe in progress."
                )
            self._half_open_calls += 1

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        if self._state == "half_open":
            logger.info("Circuit '%s' closed (probe succeeded)", self._name)
        self._state = "closed"
        self._failure_count = 0
        self._half_open_calls = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == "half_open":
            self._state = "open"
            logger.warning("Circuit '%s' reopened (probe failed)", self._name)
        elif self._failure_count >= self._threshold:
            self._state = "open"
            logger.warning(
                "Circuit '%s' opened after %d failures",
                self._name, self._failure_count,
            )

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self._state = "closed"
        self._failure_count = 0
        self._half_open_calls = 0


class CircuitOpenError(Exception):
    """Raised when a circuit breaker is open."""
    pass


# Module-level singletons for common external dependencies
llm_circuit = CircuitBreaker("llm", threshold=5, cooldown_seconds=30)
redis_circuit = CircuitBreaker("redis", threshold=3, cooldown_seconds=15)
embedding_circuit = CircuitBreaker("embedding", threshold=3, cooldown_seconds=60)
