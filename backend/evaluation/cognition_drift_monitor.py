"""Cognition drift monitor — tracks quality degradation over long sessions."""
from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger("uvicorn")


class CognitionDriftMonitor:
    """Monitors cognition quality drift over time."""

    def __init__(self) -> None:
        self._session_metrics: list[dict[str, Any]] = []

    def record_query_metrics(self, metrics: dict[str, Any]) -> None:
        """Record metrics from a single query execution."""
        self._session_metrics.append(metrics)

    def analyze_drift(
        self, window_size: int = 10
    ) -> dict[str, Any]:
        """Analyze drift across the recorded session."""
        if len(self._session_metrics) < window_size * 2:
            return {
                "drift_detected": False,
                "reason": "insufficient_data",
                "windows": [],
            }

        # Compute per-window metrics
        windows = []
        for i in range(0, len(self._session_metrics) - window_size + 1, window_size):
            window = self._session_metrics[i:i + window_size]
            qualities = [m.get("reasoning_quality", 0) for m in window if "reasoning_quality" in m]
            risks = [m.get("hallucination_risk", 0) for m in window if "hallucination_risk" in m]
            durations = [m.get("duration_ms", 0) for m in window]
            errors = sum(1 for m in window if "error" in m)

            windows.append({
                "window_index": len(windows),
                "start_index": i,
                "avg_quality": round(sum(qualities) / len(qualities), 3) if qualities else 0.0,
                "avg_risk": round(sum(risks) / len(risks), 3) if risks else 0.0,
                "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0.0,
                "error_count": errors,
            })

        if len(windows) < 2:
            return {"drift_detected": False, "reason": "insufficient_windows", "windows": windows}

        # Analyze trends
        quality_trend = self._compute_trend([w["avg_quality"] for w in windows])
        risk_trend = self._compute_trend([w["avg_risk"] for w in windows])
        duration_trend = self._compute_trend([w["avg_duration_ms"] for w in windows])

        # Detect significant drift
        quality_drift = abs(quality_trend["slope"]) > 0.01
        risk_drift = abs(risk_trend["slope"]) > 0.01
        duration_drift = abs(duration_trend["slope"]) > 100

        drift_detected = quality_drift or risk_drift or duration_drift

        return {
            "drift_detected": drift_detected,
            "quality_trend": quality_trend,
            "risk_trend": risk_trend,
            "duration_trend": duration_trend,
            "windows": windows,
            "summary": self._generate_summary(quality_trend, risk_trend, duration_trend),
        }

    def _compute_trend(self, values: list[float]) -> dict[str, Any]:
        """Compute trend via simple linear regression."""
        if len(values) < 2:
            return {"slope": 0.0, "direction": "stable", "r_squared": 0.0}

        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return {"slope": 0.0, "direction": "stable", "r_squared": 0.0}

        slope = numerator / denominator

        # R-squared
        ss_res = sum((v - (y_mean + slope * (i - x_mean))) ** 2 for i, v in enumerate(values))
        ss_tot = sum((v - y_mean) ** 2 for v in values)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        direction = "stable"
        if slope > 0.005:
            direction = "improving"
        elif slope < -0.005:
            direction = "degrading"

        return {
            "slope": round(slope, 6),
            "direction": direction,
            "r_squared": round(max(0, r_squared), 3),
        }

    def _generate_summary(
        self, quality_trend: dict, risk_trend: dict, duration_trend: dict
    ) -> str:
        """Generate a human-readable summary of drift analysis."""
        parts = []

        if quality_trend["direction"] == "degrading":
            parts.append("Reasoning quality is degrading over the session")
        elif quality_trend["direction"] == "improving":
            parts.append("Reasoning quality is improving over the session")
        else:
            parts.append("Reasoning quality is stable")

        if risk_trend["direction"] == "improving":
            parts.append("hallucination risk is increasing")
        elif risk_trend["direction"] == "degrading":
            parts.append("hallucination risk is decreasing")
        else:
            parts.append("hallucination risk is stable")

        if duration_trend["direction"] == "improving":
            parts.append("latency is increasing")
        elif duration_trend["direction"] == "degrading":
            parts.append("latency is decreasing")
        else:
            parts.append("latency is stable")

        return "; ".join(parts)

    def reset(self) -> None:
        """Reset session metrics."""
        self._session_metrics.clear()


# Module-level singleton
cognition_drift_monitor = CognitionDriftMonitor()
