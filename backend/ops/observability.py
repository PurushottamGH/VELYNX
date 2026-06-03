"""Observability — Prometheus metrics export and structured logging."""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any

logger = logging.getLogger("uvicorn")


class ObservabilityManager:
    """Manages metrics collection and export."""

    def __init__(self) -> None:
        self._prometheus_available = False
        self._counters: dict[str, int] = defaultdict(int)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}

    def initialize(self) -> None:
        """Initialize Prometheus registry if available."""
        try:
            import prometheus_client
            self._prometheus_available = True
            logger.info("Prometheus client available")
        except ImportError:
            logger.debug("Prometheus client not installed, using in-memory metrics")

    def record_event(self, event_type: str, handler: str, duration_ms: float) -> None:
        """Record an event handler execution."""
        self._counters[f"events_total{{type=\"{event_type}\"}}"] += 1
        self._counters[f"handler_calls{{handler=\"{handler}\"}}"] += 1
        self._histograms[f"handler_duration_ms{{handler=\"{handler}\"}}"].append(duration_ms)

    def record_llm_call(
        self, model: str, tokens: int, duration_ms: float, status: str
    ) -> None:
        """Record an LLM API call."""
        self._counters[f"llm_requests_total{{model=\"{model}\",status=\"{status}\"}}"] += 1
        self._counters[f"llm_tokens_total{{model=\"{model}\"}}"] += tokens
        self._histograms[f"llm_duration_ms{{model=\"{model}\"}}"].append(duration_ms)

    def record_retrieval(self, source: str, duration_ms: float, success: bool) -> None:
        """Record a retrieval operation."""
        status = "success" if success else "failure"
        self._counters[f"retrieval_total{{source=\"{source}\",status=\"{status}\"}}"] += 1
        self._histograms[f"retrieval_duration_ms{{source=\"{source}\"}}"].append(duration_ms)

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge value."""
        self._gauges[name] = value

    def get_metrics(self) -> str:
        """Get metrics in Prometheus text format."""
        lines = []

        # Counters
        for name, value in sorted(self._counters.items()):
            lines.append(f"# TYPE {name.split('{')[0]} counter")
            lines.append(f"{name} {value}")

        # Histograms (simplified: just avg, p99, count)
        for name, values in sorted(self._histograms.items()):
            if not values:
                continue
            base = name.split("{")[0]
            labels = name[len(base):]
            lines.append(f"# TYPE {base} histogram")
            lines.append(f"{base}_count{labels} {len(values)}")
            lines.append(f"{base}_sum{labels} {sum(values):.2f}")

        # Gauges
        for name, value in sorted(self._gauges.items()):
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")

        return "\n".join(lines) + "\n"

    def get_stats(self) -> dict:
        """Get metrics as a dictionary."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histogram_counts": {k: len(v) for k, v in self._histograms.items()},
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._histograms.clear()
        self._gauges.clear()


# Module-level singleton
observability = ObservabilityManager()
