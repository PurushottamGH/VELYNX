"""Stability monitor — tracks runtime stability over time windows."""
from __future__ import annotations

import logging
import time
from collections import deque

from evaluation import Regression, RegressionReport, StabilityReport, StabilityWindow

logger = logging.getLogger("uvicorn")


class StabilityMonitor:
    """Monitors runtime stability across time windows."""

    def __init__(self, window_minutes: int = 5, max_windows: int = 12) -> None:
        self._window_minutes = window_minutes
        self._max_windows = max_windows
        self._windows: deque[StabilityWindow] = deque(maxlen=max_windows)
        self._current_ops: int = 0
        self._current_errors: int = 0
        self._current_latencies: deque[float] = deque(maxlen=1000)
        self._window_start: float = time.time()
        self._events_processed: int = 0
        self._baseline: dict[str, float] | None = None

    def record_operation(self, latency_ms: float, error: bool = False) -> None:
        """Record a single operation."""
        self._current_ops += 1
        self._current_latencies.append(latency_ms)
        if error:
            self._current_errors += 1
        self._events_processed += 1

        # Check if window should be closed
        elapsed = time.time() - self._window_start
        if elapsed >= self._window_minutes * 60:
            self._close_window()

    def record_event(self) -> None:
        """Record an event processed."""
        self._events_processed += 1

    def _close_window(self) -> None:
        """Close current window and start a new one."""
        elapsed = time.time() - self._window_start
        if elapsed <= 0:
            return

        latencies = list(self._current_latencies)
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        p99_latency = 0.0
        if latencies:
            sorted_lat = sorted(latencies)
            idx = int(len(sorted_lat) * 0.99)
            p99_latency = sorted_lat[min(idx, len(sorted_lat) - 1)]

        throughput = self._events_processed / elapsed if elapsed > 0 else 0.0

        window = StabilityWindow(
            window_minutes=self._window_minutes,
            error_count=self._current_errors,
            total_operations=self._current_ops,
            error_rate=self._current_errors / self._current_ops if self._current_ops > 0 else 0.0,
            avg_latency_ms=round(avg_latency, 2),
            p99_latency_ms=round(p99_latency, 2),
            event_throughput=round(throughput, 2),
        )
        self._windows.append(window)

        # Reset for next window
        self._current_ops = 0
        self._current_errors = 0
        self._current_latencies.clear()
        self._events_processed = 0
        self._window_start = time.time()

    def get_report(self) -> StabilityReport:
        """Generate a stability report from collected windows."""
        return self.get_stability_report()

    def get_stability_report(self) -> StabilityReport:
        """Generate a stability report from collected windows (alias)."""
        # Close current window if it has data
        if self._current_ops > 0:
            self._close_window()

        windows = list(self._windows)
        if not windows:
            return StabilityReport(status="stable", score=1.0)

        # Compute aggregate metrics
        avg_error_rate = sum(w.error_rate for w in windows) / len(windows)
        avg_latency = sum(w.avg_latency_ms for w in windows) / len(windows)
        max_p99 = max(w.p99_latency_ms for w in windows)

        # Determine status
        status = "stable"
        score = 1.0

        if avg_error_rate > 0.1:
            status = "unstable"
            score -= 0.4
        elif avg_error_rate > 0.05:
            status = "degraded"
            score -= 0.2

        if avg_latency > 5000:
            status = "degraded" if status == "stable" else status
            score -= 0.2
        elif avg_latency > 10000:
            status = "unstable"
            score -= 0.2

        if max_p99 > 30000:
            score -= 0.1

        score = max(0.0, score)

        # Generate recommendations
        recommendations: list[str] = []
        if avg_error_rate > 0.05:
            recommendations.append(f"Error rate is {avg_error_rate:.1%} — investigate failing handlers")
        if avg_latency > 5000:
            recommendations.append(f"Average latency is {avg_latency:.0f}ms — optimize slow paths")
        if max_p99 > 30000:
            recommendations.append(f"P99 latency is {max_p99:.0f}ms — check for timeouts")

        return StabilityReport(
            status=status,
            score=round(score, 3),
            windows=windows,
            recommendations=recommendations,
        )

    def set_baseline(self, metrics: dict[str, float]) -> None:
        """Set baseline metrics for regression detection."""
        self._baseline = metrics

    def detect_regressions(
        self, current_metrics: dict[str, float], threshold_pct: float = 10.0
    ) -> RegressionReport:
        """Detect regressions by comparing current metrics to baseline."""
        if not self._baseline:
            return RegressionReport(has_regressions=False)

        regressions: list[Regression] = []
        for name, current_val in current_metrics.items():
            baseline_val = self._baseline.get(name)
            if baseline_val is None:
                continue

            if baseline_val == 0:
                continue

            change_pct = ((current_val - baseline_val) / abs(baseline_val)) * 100

            # For error rates and latency, increase is bad
            is_error_metric = any(k in name.lower() for k in ["error", "latency", "risk", "fail"])
            if is_error_metric and change_pct > threshold_pct:
                regressions.append(Regression(
                    metric_name=name,
                    baseline_value=baseline_val,
                    current_value=current_val,
                    change_pct=round(change_pct, 1),
                    severity="critical" if change_pct > 50 else "warning",
                    description=f"{name} increased by {change_pct:.1f}%",
                ))
            # For quality metrics, decrease is bad
            elif not is_error_metric and change_pct < -threshold_pct:
                regressions.append(Regression(
                    metric_name=name,
                    baseline_value=baseline_val,
                    current_value=current_val,
                    change_pct=round(change_pct, 1),
                    severity="critical" if change_pct < -50 else "warning",
                    description=f"{name} decreased by {abs(change_pct):.1f}%",
                ))

        return RegressionReport(
            has_regressions=len(regressions) > 0,
            regressions=regressions,
        )


# Module-level singleton
stability_monitor = StabilityMonitor()
