"""Runtime observability — event counters, handler latency, stats."""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

from runtime.event_models import Event, HandlerResult

logger = logging.getLogger("uvicorn")


@dataclass
class LatencyStats:
    """Rolling latency statistics for a handler."""
    samples: deque[float] = field(default_factory=lambda: deque(maxlen=1000))

    def record(self, duration_ms: float) -> None:
        self.samples.append(duration_ms)

    @property
    def count(self) -> int:
        return len(self.samples)

    @property
    def avg_ms(self) -> float:
        return sum(self.samples) / len(self.samples) if self.samples else 0.0

    @property
    def p99_ms(self) -> float:
        if not self.samples:
            return 0.0
        sorted_samples = sorted(self.samples)
        idx = int(len(sorted_samples) * 0.99)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]

    @property
    def max_ms(self) -> float:
        return max(self.samples) if self.samples else 0.0


class RuntimeMonitor:
    """Observability: event counters and handler latency tracking."""

    def __init__(self) -> None:
        self._event_counts: dict[str, int] = defaultdict(int)
        self._handler_latency: dict[str, LatencyStats] = defaultdict(LatencyStats)
        self._handler_errors: dict[str, int] = defaultdict(int)
        self._total_events: int = 0
        self._start_time: float = time.time()

    async def on_event(self, event: Event) -> None:
        """Global event handler — records event count by type."""
        self._event_counts[event.type.value] += 1
        self._total_events += 1

    def record_handler_result(self, result: HandlerResult) -> None:
        """Record a handler execution result for latency/error tracking."""
        self._handler_latency[result.handler_name].record(result.duration_ms)
        if not result.success:
            self._handler_errors[result.handler_name] += 1

    def get_stats(self) -> dict:
        """Snapshot of all observability data."""
        uptime_seconds = time.time() - self._start_time
        handler_stats = {}
        for name, latency in self._handler_latency.items():
            handler_stats[name] = {
                "call_count": latency.count,
                "avg_ms": round(latency.avg_ms, 2),
                "p99_ms": round(latency.p99_ms, 2),
                "max_ms": round(latency.max_ms, 2),
                "error_count": self._handler_errors.get(name, 0),
            }

        return {
            "uptime_seconds": round(uptime_seconds, 1),
            "total_events": self._total_events,
            "event_counts": dict(self._event_counts),
            "handlers": handler_stats,
        }

    def reset(self) -> None:
        """Reset all counters."""
        self._event_counts.clear()
        self._handler_latency.clear()
        self._handler_errors.clear()
        self._total_events = 0
        self._start_time = time.time()


# Module-level singleton
runtime_monitor = RuntimeMonitor()
