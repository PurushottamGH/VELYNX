"""Time-windowed cognition metric aggregation from reflection history."""
from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone

from backend.database.engine import async_session
from backend.database.repositories import ReflectionRepository
from backend.metacognition import CognitionMetricsReport, MetricPoint, MetricTrend, TimeWindow

logger = logging.getLogger("uvicorn")


class CognitionMetrics:
    """Aggregates cognition metrics from reflection repository."""

    async def compute_report(
        self, window_hours: int = 24, limit: int = 200
    ) -> CognitionMetricsReport:
        """Compute a full cognition metrics report for the given time window."""
        reflections = await self._load_reflections(limit)
        if not reflections:
            return CognitionMetricsReport(
                window=TimeWindow(hours=window_hours),
                total_reflections=0,
            )

        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=window_hours)
        window = TimeWindow(hours=window_hours, start=window_start, end=now)

        filtered = self._filter_by_window(reflections, window_start)

        # Extract metric series
        quality_points = [
            (r.created_at, r.reasoning_quality) for r in filtered if r.reasoning_quality is not None
        ]
        risk_points = [
            (r.created_at, r.hallucination_risk) for r in filtered if r.hallucination_risk is not None
        ]
        delta_points = []
        for r in filtered:
            if r.confidence_estimate and isinstance(r.confidence_estimate, dict):
                delta = r.confidence_estimate.get("delta", 0.0)
                if delta is not None:
                    delta_points.append((r.created_at, float(delta)))

        # Count categories
        issue_counts = self._count_categories(filtered, "audit_issues")
        improvement_counts = self._count_categories(filtered, "improvements")

        return CognitionMetricsReport(
            window=window,
            total_reflections=len(filtered),
            reasoning_quality=self._build_trend("reasoning_quality", quality_points, window_hours),
            hallucination_risk=self._build_trend("hallucination_risk", risk_points, window_hours),
            confidence_delta=self._build_trend("confidence_delta", delta_points, window_hours),
            issue_category_counts=issue_counts,
            improvement_category_counts=improvement_counts,
        )

    async def _load_reflections(self, limit: int) -> list:
        """Load recent reflections from DB with graceful degradation."""
        try:
            async with async_session() as session:
                repo = ReflectionRepository(session)
                return await repo.get_history(limit=limit)
        except Exception as exc:
            logger.debug("Reflection load skipped: %s", exc)
            return []

    def _filter_by_window(self, reflections: list, window_start: datetime) -> list:
        """Filter reflections within the time window."""
        return [r for r in reflections if r.created_at and r.created_at >= window_start]

    def _build_trend(
        self, name: str, points: list[tuple[datetime, float]], window_hours: int
    ) -> MetricTrend:
        """Build a MetricTrend from (timestamp, value) pairs."""
        if not points:
            return MetricTrend(name=name, window_hours=window_hours)

        values = [v for _, v in points]
        mean = self._safe_mean(values)
        std = self._safe_std_dev(values, mean)

        metric_points = [
            MetricPoint(timestamp=ts, value=v) for ts, v in sorted(points)
        ]

        return MetricTrend(
            name=name,
            points=metric_points,
            current=values[-1] if values else 0.0,
            mean=mean,
            std_dev=std,
            min_val=min(values) if values else 0.0,
            max_val=max(values) if values else 0.0,
            direction=self._compute_direction(values),
            window_hours=window_hours,
        )

    def _compute_direction(self, values: list[float]) -> str:
        """Determine trend direction via simple linear regression slope."""
        if len(values) < 3:
            return "stable"
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        if denominator == 0:
            return "stable"
        slope = numerator / denominator
        if slope > 0.005:
            return "improving"
        if slope < -0.005:
            return "degrading"
        return "stable"

    def _count_categories(self, reflections: list, field: str) -> dict[str, int]:
        """Count occurrences of categories in JSONB fields."""
        counts: dict[str, int] = {}
        for r in reflections:
            items = getattr(r, field, None)
            if not items or not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    cat = item.get("category", "unknown")
                    counts[cat] = counts.get(cat, 0) + 1
        return counts

    @staticmethod
    def _safe_mean(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def _safe_std_dev(values: list[float], mean: float) -> float:
        if len(values) < 2:
            return 0.0
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        return math.sqrt(variance)
