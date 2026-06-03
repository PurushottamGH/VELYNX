"""Load shedding — request concurrency limits and priority-based shedding."""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

logger = logging.getLogger("uvicorn")


class LoadShedder:
    """Manages request concurrency with priority-based shedding."""

    def __init__(self, max_concurrent: int = 10) -> None:
        self._max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_count = 0
        self._shed_count = 0

    @asynccontextmanager
    async def acquire(self, priority: str = "normal") -> AsyncIterator[None]:
        """Acquire a concurrency slot. Raises LoadShedError if at capacity."""
        if priority == "low":
            # Low priority (benchmarks, trials) — check capacity without blocking
            if self._active_count >= self._max_concurrent:
                self._shed_count += 1
                raise LoadShedError(
                    f"At capacity ({self._active_count}/{self._max_concurrent}). "
                    f"Low-priority request shed."
                )

        try:
            await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=5.0,
            )
        except asyncio.TimeoutError:
            self._shed_count += 1
            raise LoadShedError(
                f"Could not acquire slot within 5s. "
                f"Active: {self._active_count}/{self._max_concurrent}"
            )

        self._active_count += 1
        try:
            yield
        finally:
            self._active_count -= 1
            self._semaphore.release()

    def get_stats(self) -> dict:
        """Get current load shedding statistics."""
        return {
            "max_concurrent": self._max_concurrent,
            "active_count": self._active_count,
            "shed_count": self._shed_count,
            "available_slots": self._max_concurrent - self._active_count,
        }


class LoadShedError(Exception):
    """Raised when a request is shed due to load."""
    pass


# Module-level singleton
load_shedder = LoadShedder(max_concurrent=10)
