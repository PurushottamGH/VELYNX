"""Confidence calibration accuracy tracking."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from collections import defaultdict

from database.engine import async_session
from database.repositories import ReflectionRepository, FeedbackRepository
from metacognition import CalibrationRecord, CalibrationReport, MetricPoint, MetricTrend

logger = logging.getLogger("uvicorn")

_CONFIDENCE_VALUES = {
    "CERTAIN": 0.9, "PROBABLE": 0.7, "DEBATED": 0.5, "LOW": 0.3, "UNKNOWN": 0.1
}


class ConfidenceCalibrator:
    """Analyzes confidence calibration accuracy over time."""

    async def analyze(self, limit: int = 200) -> CalibrationReport:
        """Compute calibration accuracy from reflection + feedback data."""
        reflections, feedback_by_query = await self._load_data(limit)
        if not reflections:
            return CalibrationReport()

        records = self._build_records(reflections, feedback_by_query)
        if not records:
            return CalibrationReport()

        deltas = [abs(r.calibration_delta) for r in records]
        mean_abs_delta = sum(deltas) / len(deltas)

        overconfident = sum(1 for r in records if r.was_overconfident)
        underconfident = sum(1 for r in records if r.was_underconfident)

        calibration_error = self._compute_brier_score(records)
        by_level = self._compute_by_confidence_level(records)
        trend = self._build_trend(records)

        return CalibrationReport(
            total_records=len(records),
            mean_absolute_delta=mean_abs_delta,
            overconfidence_rate=overconfident / len(records) if records else 0.0,
            underconfidence_rate=underconfident / len(records) if records else 0.0,
            calibration_error=calibration_error,
            by_confidence_level=by_level,
            trend=trend,
            records=records[:20],  # limit stored records
        )

    async def _load_data(self, limit: int) -> tuple[list, dict[str, int]]:
        """Load reflections and feedback, index feedback by query."""
        reflections = []
        feedback_by_query: dict[str, int] = {}
        try:
            async with async_session() as session:
                reflections = await ReflectionRepository(session).get_history(limit=limit)
                feedback = await FeedbackRepository(session).get_recent(limit=limit)
                for f in feedback:
                    if f.query:
                        feedback_by_query[f.query] = f.rating
        except Exception as exc:
            logger.debug("Data load skipped: %s", exc)
        return reflections, feedback_by_query

    def _build_records(
        self, reflections: list, feedback_by_query: dict[str, int]
    ) -> list[CalibrationRecord]:
        """Build CalibrationRecord for each reflection."""
        records = []
        for r in reflections:
            conf = r.confidence_estimate or {}
            if not isinstance(conf, dict):
                continue

            initial = conf.get("initial", "UNKNOWN")
            calibrated = conf.get("calibrated", "UNKNOWN")
            delta = conf.get("delta", 0.0) or 0.0
            quality = r.reasoning_quality or 0.0

            expected = self._expected_confidence_from_quality(quality)
            expected_val = _CONFIDENCE_VALUES.get(expected, 0.1)
            calibrated_val = _CONFIDENCE_VALUES.get(calibrated, 0.1)

            records.append(CalibrationRecord(
                query=r.query[:200] if r.query else "",
                initial_confidence=initial,
                calibrated_confidence=calibrated,
                calibration_delta=delta,
                reasoning_quality=quality,
                user_rating=feedback_by_query.get(r.query),
                was_overconfident=calibrated_val > expected_val + 0.1,
                was_underconfident=calibrated_val < expected_val - 0.1,
            ))
        return records

    def _expected_confidence_from_quality(self, quality: float) -> str:
        """Map reasoning_quality to expected confidence level."""
        if quality >= 0.8:
            return "CERTAIN"
        if quality >= 0.6:
            return "PROBABLE"
        if quality >= 0.4:
            return "DEBATED"
        if quality >= 0.2:
            return "LOW"
        return "UNKNOWN"

    def _compute_brier_score(self, records: list[CalibrationRecord]) -> float:
        """Mean squared error between calibrated and expected confidence values."""
        if not records:
            return 0.0
        total = 0.0
        for r in records:
            cal_val = _CONFIDENCE_VALUES.get(r.calibrated_confidence, 0.1)
            exp_val = _CONFIDENCE_VALUES.get(
                self._expected_confidence_from_quality(r.reasoning_quality), 0.1
            )
            total += (cal_val - exp_val) ** 2
        return total / len(records)

    def _compute_by_confidence_level(
        self, records: list[CalibrationRecord]
    ) -> dict[str, dict[str, float]]:
        """Group by initial confidence level and compute per-level stats."""
        groups: dict[str, list[CalibrationRecord]] = defaultdict(list)
        for r in records:
            groups[r.initial_confidence].append(r)

        result = {}
        for level, group in groups.items():
            deltas = [r.calibration_delta for r in group]
            over = sum(1 for r in group if r.was_overconfident)
            result[level] = {
                "count": len(group),
                "avg_delta": sum(deltas) / len(deltas) if deltas else 0.0,
                "overconfidence_rate": over / len(group) if group else 0.0,
            }
        return result

    def _build_trend(self, records: list[CalibrationRecord]) -> MetricTrend:
        """Build calibration error trend over time."""
        if not records:
            return MetricTrend(name="calibration_error")

        points = []
        for r in records:
            cal_val = _CONFIDENCE_VALUES.get(r.calibrated_confidence, 0.1)
            exp_val = _CONFIDENCE_VALUES.get(
                self._expected_confidence_from_quality(r.reasoning_quality), 0.1
            )
            error = (cal_val - exp_val) ** 2
            points.append(MetricPoint(
                timestamp=datetime.now(timezone.utc),
                value=error,
            ))

        values = [p.value for p in points]
        mean = sum(values) / len(values) if values else 0.0
        return MetricTrend(
            name="calibration_error",
            points=points[-50:],
            current=values[-1] if values else 0.0,
            mean=mean,
            min_val=min(values) if values else 0.0,
            max_val=max(values) if values else 0.0,
        )
