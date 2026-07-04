"""Central metacognition orchestrator — coordinates all analysis components."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone

from backend.metacognition import (
    AdaptationRecommendation,
    CognitionHealthReport,
    HealthIndicator,
    MetacognitionReport,
    RuntimePerformanceMetrics,
    TimeWindow,
)
from backend.metacognition.cognition_metrics import CognitionMetrics
from backend.metacognition.pattern_analyzer import PatternAnalyzer
from backend.metacognition.confidence_calibrator import ConfidenceCalibrator
from backend.metacognition.strategy_analyzer import CrossDomainStrategyAnalyzer
from backend.metacognition.adaptation_engine import AdaptationEngine

logger = logging.getLogger("uvicorn")


class MetaMonitor:
    """Central metacognition orchestrator."""

    def __init__(self) -> None:
        self._metrics = CognitionMetrics()
        self._patterns = PatternAnalyzer()
        self._calibrator = ConfidenceCalibrator()
        self._strategy_analyzer = CrossDomainStrategyAnalyzer()
        self._adaptation_engine = AdaptationEngine()
        self._last_report: MetacognitionReport | None = None
        self._last_report_time: float = 0.0

    async def analyze(
        self, window_hours: int = 24, force: bool = False
    ) -> MetacognitionReport:
        """Run full metacognition analysis. Cached for 5 minutes."""
        if not force and self._last_report and (time.time() - self._last_report_time < 300):
            return self._last_report
        report = await self._run_analysis(window_hours)
        self._last_report = report
        self._last_report_time = time.time()
        return report

    async def get_health(self) -> CognitionHealthReport:
        """Quick health check from cache or lightweight analysis."""
        if self._last_report and (time.time() - self._last_report_time < 300):
            return self._last_report.health
        # Lightweight: just runtime metrics
        runtime = self._build_runtime_metrics()
        return self._build_health_report_from_runtime(runtime)

    async def get_recommendations(
        self, window_hours: int = 24
    ) -> list[AdaptationRecommendation]:
        """Get current recommendations."""
        report = await self.analyze(window_hours=window_hours)
        return report.recommendations

    async def get_runtime_metrics(self) -> RuntimePerformanceMetrics:
        """Get runtime performance metrics."""
        return self._build_runtime_metrics()

    async def _run_analysis(self, window_hours: int) -> MetacognitionReport:
        """Execute all analysis components in parallel."""
        start = time.perf_counter()

        # Run independent analyses in parallel
        metrics_report, pattern_clusters, calibration_report, strategy_analysis = (
            await asyncio.gather(
                self._metrics.compute_report(window_hours=window_hours),
                self._patterns.detect_patterns(),
                self._calibrator.analyze(),
                self._strategy_analyzer.analyze(),
            )
        )

        runtime_metrics = self._build_runtime_metrics()
        health = self._build_health_report(
            metrics_report, calibration_report, runtime_metrics, pattern_clusters
        )
        recommendations = self._adaptation_engine.generate(
            metrics_report, pattern_clusters, calibration_report,
            strategy_analysis, health, runtime_metrics
        )

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info("Metacognition analysis completed in %.0fms", duration_ms)

        report = MetacognitionReport(
            window=TimeWindow(hours=window_hours),
            metrics=metrics_report,
            patterns=pattern_clusters,
            calibration=calibration_report,
            strategy_analysis=strategy_analysis,
            health=health,
            runtime=runtime_metrics,
            recommendations=recommendations,
        )

        # Publish event (fire-and-forget)
        self._publish_event(report)

        # Persist to DB (fire-and-forget)
        self._persist_report(report)

        return report

    def _build_health_report(
        self, metrics_report, calibration_report, runtime_metrics, pattern_clusters
    ) -> CognitionHealthReport:
        """Build health report from sub-analysis results."""
        indicators = []

        # Reasoning quality
        rq = metrics_report.reasoning_quality
        indicators.append(self._evaluate_health_indicator(
            "reasoning_quality",
            rq.current,
            warning_threshold=0.4,
            critical_threshold=0.2,
            description=f"Current: {rq.current:.2f}, trend: {rq.direction}",
        ))

        # Hallucination risk
        hr = metrics_report.hallucination_risk
        indicators.append(self._evaluate_health_indicator(
            "hallucination_risk",
            1.0 - hr.current,  # invert: lower risk = healthier
            warning_threshold=0.5,
            critical_threshold=0.3,
            description=f"Risk: {hr.current:.2f}, trend: {hr.direction}",
        ))

        # Calibration
        indicators.append(self._evaluate_health_indicator(
            "calibration",
            1.0 - calibration_report.calibration_error,
            warning_threshold=0.8,
            critical_threshold=0.6,
            description=f"Error: {calibration_report.calibration_error:.3f}",
        ))

        # Runtime errors
        indicators.append(self._evaluate_health_indicator(
            "runtime",
            1.0 - runtime_metrics.error_rate,
            warning_threshold=0.95,
            critical_threshold=0.9,
            description=f"Error rate: {runtime_metrics.error_rate:.1%}",
        ))

        # Pattern diversity
        indicators.append(self._evaluate_health_indicator(
            "pattern_diversity",
            min(len(pattern_clusters) / 5.0, 1.0),
            warning_threshold=0.3,
            critical_threshold=0.1,
            description=f"{len(pattern_clusters)} distinct clusters",
        ))

        overall_status, score = self._compute_overall_health(indicators)
        warnings = [
            f"{i.name}: {i.description}" for i in indicators if i.status != "healthy"
        ]

        return CognitionHealthReport(
            overall_status=overall_status,
            indicators=indicators,
            score=score,
            warnings=warnings,
        )

    def _build_health_report_from_runtime(self, runtime: RuntimePerformanceMetrics) -> CognitionHealthReport:
        """Quick health from runtime only."""
        indicator = self._evaluate_health_indicator(
            "runtime", 1.0 - runtime.error_rate,
            warning_threshold=0.95, critical_threshold=0.9,
            description=f"Error rate: {runtime.error_rate:.1%}",
        )
        status = indicator.status
        score = indicator.value if status == "healthy" else 0.5
        return CognitionHealthReport(
            overall_status=status,
            indicators=[indicator],
            score=score,
        )

    def _evaluate_health_indicator(
        self, name: str, value: float,
        warning_threshold: float, critical_threshold: float, description: str
    ) -> HealthIndicator:
        if value < critical_threshold:
            status = "critical"
        elif value < warning_threshold:
            status = "warning"
        else:
            status = "healthy"
        return HealthIndicator(
            name=name, status=status, value=value,
            threshold=warning_threshold, description=description,
        )

    def _compute_overall_health(
        self, indicators: list[HealthIndicator]
    ) -> tuple[str, float]:
        statuses = [i.status for i in indicators]
        if "critical" in statuses:
            critical = [i for i in indicators if i.status == "critical"]
            return "critical", min(i.value for i in critical)
        if "warning" in statuses:
            warnings = [i for i in indicators if i.status == "warning"]
            return "degraded", sum(i.value for i in warnings) / len(warnings)
        return "healthy", 1.0

    def _build_runtime_metrics(self) -> RuntimePerformanceMetrics:
        """Read from RuntimeMonitor singleton."""
        try:
            from runtime.runtime_monitor import runtime_monitor
            stats = runtime_monitor.get_stats()
            total_errors = sum(
                h.get("error_count", 0) for h in stats.get("handlers", {}).values()
            )
            total_calls = sum(
                h.get("call_count", 0) for h in stats.get("handlers", {}).values()
            )
            avg_latency = 0.0
            latencies = [
                h.get("avg_ms", 0) for h in stats.get("handlers", {}).values()
            ]
            if latencies:
                avg_latency = sum(latencies) / len(latencies)

            return RuntimePerformanceMetrics(
                uptime_seconds=stats.get("uptime_seconds", 0),
                total_events=stats.get("total_events", 0),
                event_counts=stats.get("event_counts", {}),
                handler_stats=stats.get("handlers", {}),
                error_rate=total_errors / total_calls if total_calls > 0 else 0.0,
                avg_handler_latency_ms=avg_latency,
            )
        except Exception:
            return RuntimePerformanceMetrics()

    def _publish_event(self, report: MetacognitionReport) -> None:
        try:
            from runtime.event_bus import event_bus
            from runtime.event_models import Event, EventType
            from runtime.tracing import get_correlation_id
            asyncio.create_task(event_bus.publish(Event(
                type=EventType.METACOGNITION_ANALYZED,
                correlation_id=get_correlation_id(),
                source="meta_monitor",
                payload={
                    "health_status": report.health.overall_status,
                    "health_score": report.health.score,
                    "recommendation_count": len(report.recommendations),
                },
            )))
        except Exception:
            pass

    def _persist_report(self, report: MetacognitionReport) -> None:
        """Persist report to PostgreSQL (fire-and-forget)."""
        try:
            from database.engine import async_session
            from database.repositories import MetacognitionRepository

            async def _do_persist():
                async with async_session() as session:
                    repo = MetacognitionRepository(session)
                    await repo.store(
                        window_hours=report.window.hours,
                        overall_health=report.health.overall_status,
                        health_score=report.health.score,
                        report=report.model_dump(mode="json"),
                    )
            asyncio.create_task(_do_persist())
        except Exception:
            pass


# Module-level singleton
meta_monitor = MetaMonitor()
