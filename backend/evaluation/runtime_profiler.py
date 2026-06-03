"""Runtime profiler — measures latency, throughput, and resource usage."""
from __future__ import annotations

import logging
import time
from collections import defaultdict

from evaluation import ProfileReport, ProfileSample

logger = logging.getLogger("uvicorn")


class RuntimeProfiler:
    """Profiles runtime performance during evaluation."""

    def __init__(self) -> None:
        self._samples: list[ProfileSample] = []
        self._start_time: float = 0.0
        self._section_starts: dict[str, float] = {}

    def start(self) -> None:
        """Start profiling session."""
        self._samples = []
        self._start_time = time.perf_counter()

    def start_section(self, label: str) -> None:
        """Start timing a named section."""
        self._section_starts[label] = time.perf_counter()

    def end_section(self, label: str, metadata: dict | None = None) -> float:
        """End timing a named section. Returns duration in ms."""
        if label not in self._section_starts:
            return 0.0
        duration_ms = (time.perf_counter() - self._section_starts[label]) * 1000
        self._samples.append(ProfileSample(
            label=label,
            duration_ms=round(duration_ms, 2),
            metadata=metadata or {},
        ))
        del self._section_starts[label]
        return duration_ms

    def record(self, label: str, duration_ms: float, metadata: dict | None = None) -> None:
        """Record a measurement directly."""
        self._samples.append(ProfileSample(
            label=label,
            duration_ms=round(duration_ms, 2),
            metadata=metadata or {},
        ))

    def get_report(self) -> ProfileReport:
        """Generate a profiling report with bottleneck analysis."""
        total_ms = (time.perf_counter() - self._start_time) * 1000 if self._start_time else 0.0

        # Identify bottlenecks (sections taking >20% of total time)
        bottlenecks: list[str] = []
        for sample in self._samples:
            if total_ms > 0 and sample.duration_ms / total_ms > 0.2:
                bottlenecks.append(
                    f"{sample.label}: {sample.duration_ms:.0f}ms "
                    f"({sample.duration_ms / total_ms * 100:.0f}% of total)"
                )

        # Generate recommendations
        recommendations: list[str] = []
        if total_ms > 10000:
            recommendations.append("Total evaluation time >10s — consider reducing test scope")
        for sample in self._samples:
            if sample.duration_ms > 5000:
                recommendations.append(f"Section '{sample.label}' took {sample.duration_ms:.0f}ms — consider optimization")

        return ProfileReport(
            total_duration_ms=round(total_ms, 2),
            samples=self._samples,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
        )

    def get_section_stats(self) -> dict[str, dict[str, float]]:
        """Get aggregated stats per section label."""
        by_label: dict[str, list[float]] = defaultdict(list)
        for s in self._samples:
            by_label[s.label].append(s.duration_ms)

        stats = {}
        for label, durations in by_label.items():
            stats[label] = {
                "count": len(durations),
                "total_ms": round(sum(durations), 2),
                "avg_ms": round(sum(durations) / len(durations), 2),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
            }
        return stats


# Module-level singleton
runtime_profiler = RuntimeProfiler()
