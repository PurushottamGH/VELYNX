"""Tests for the metacognition layer."""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.metacognition import (
    TimeWindow, MetricPoint, MetricTrend, CognitionMetricsReport,
    ReasoningPattern, PatternCluster, CalibrationRecord, CalibrationReport,
    StrategyPerformance, StrategyAnalysis, HealthIndicator, CognitionHealthReport,
    AdaptationRecommendation, RuntimePerformanceMetrics, MetacognitionReport,
)
from backend.metacognition.cognition_metrics import CognitionMetrics
from backend.metacognition.pattern_analyzer import PatternAnalyzer
from backend.metacognition.confidence_calibrator import ConfidenceCalibrator
from backend.metacognition.strategy_analyzer import CrossDomainStrategyAnalyzer
from backend.metacognition.adaptation_engine import AdaptationEngine
from backend.metacognition.meta_monitor import MetaMonitor


# ── Model Tests ──────────────────────────────────────────────────

class TestModels:
    def test_metric_trend_defaults(self):
        trend = MetricTrend(name="test")
        assert trend.name == "test"
        assert trend.direction == "stable"
        assert trend.points == []

    def test_cognition_metrics_report_defaults(self):
        report = CognitionMetricsReport()
        assert report.total_reflections == 0
        assert report.reasoning_quality.name == "reasoning_quality"

    def test_pattern_cluster_defaults(self):
        cluster = PatternCluster(cluster_id="abc", label="test")
        assert cluster.size == 0
        assert cluster.patterns == []

    def test_calibration_record(self):
        record = CalibrationRecord(query="test", calibration_delta=0.1)
        assert record.was_overconfident is False
        assert record.user_rating is None

    def test_calibration_report_defaults(self):
        report = CalibrationReport()
        assert report.total_records == 0
        assert report.calibration_error == 0.0

    def test_strategy_analysis_defaults(self):
        analysis = StrategyAnalysis()
        assert analysis.strategies == []
        assert analysis.best_performing is None

    def test_health_indicator(self):
        indicator = HealthIndicator(name="test", status="healthy", value=0.9)
        assert indicator.status == "healthy"

    def test_cognition_health_report_defaults(self):
        report = CognitionHealthReport()
        assert report.overall_status == "healthy"
        assert report.score == 1.0

    def test_adaptation_recommendation(self):
        rec = AdaptationRecommendation(
            category="strategy",
            priority=8,
            title="Test recommendation",
            description="Test description",
        )
        assert rec.risk == "low"
        assert rec.priority == 8

    def test_metacognition_report_defaults(self):
        report = MetacognitionReport()
        assert report.health.overall_status == "healthy"
        assert report.recommendations == []

    def test_runtime_performance_metrics_defaults(self):
        metrics = RuntimePerformanceMetrics()
        assert metrics.error_rate == 0.0
        assert metrics.total_events == 0

    def test_serialization_roundtrip(self):
        report = MetacognitionReport()
        data = report.model_dump(mode="json")
        restored = MetacognitionReport.model_validate(data)
        assert restored.health.overall_status == "healthy"


# ── Cognition Metrics Tests ──────────────────────────────────────

class TestCognitionMetrics:
    @pytest.mark.asyncio
    async def test_compute_report_empty(self):
        metrics = CognitionMetrics()
        report = await metrics.compute_report(window_hours=24, limit=10)
        assert report.total_reflections == 0
        assert report.reasoning_quality.direction == "stable"

    def test_compute_direction_improving(self):
        metrics = CognitionMetrics()
        direction = metrics._compute_direction([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        assert direction == "improving"

    def test_compute_direction_degrading(self):
        metrics = CognitionMetrics()
        direction = metrics._compute_direction([0.6, 0.5, 0.4, 0.3, 0.2, 0.1])
        assert direction == "degrading"

    def test_compute_direction_stable(self):
        metrics = CognitionMetrics()
        direction = metrics._compute_direction([0.5, 0.5, 0.5, 0.5, 0.5])
        assert direction == "stable"

    def test_build_trend_empty(self):
        metrics = CognitionMetrics()
        trend = metrics._build_trend("test", [], 24)
        assert trend.name == "test"
        assert trend.points == []

    def test_count_categories(self):
        metrics = CognitionMetrics()

        class MockReflection:
            audit_issues = [
                {"category": "hallucination", "severity": 0.5},
                {"category": "weak_reasoning", "severity": 0.3},
            ]

        counts = metrics._count_categories([MockReflection()], "audit_issues")
        assert counts["hallucination"] == 1
        assert counts["weak_reasoning"] == 1

    def test_safe_mean(self):
        assert CognitionMetrics._safe_mean([1.0, 2.0, 3.0]) == 2.0
        assert CognitionMetrics._safe_mean([]) == 0.0

    def test_safe_std_dev(self):
        std = CognitionMetrics._safe_std_dev([1.0, 2.0, 3.0], 2.0)
        assert std > 0.0
        assert CognitionMetrics._safe_std_dev([], 0.0) == 0.0


# ── Adaptation Engine Tests ──────────────────────────────────────

class TestAdaptationEngine:
    def test_generate_empty_inputs(self):
        engine = AdaptationEngine()
        recs = engine.generate(
            metrics=CognitionMetricsReport(),
            patterns=[],
            calibration=CalibrationReport(),
            strategy_analysis=StrategyAnalysis(),
            health=CognitionHealthReport(),
            runtime=RuntimePerformanceMetrics(),
        )
        assert isinstance(recs, list)

    def test_strategy_recommendations_underused(self):
        engine = AdaptationEngine()
        analysis = StrategyAnalysis(underused_strategies=["incremental", "parallel"])
        recs = engine._strategy_recommendations(analysis)
        assert len(recs) > 0
        assert any("underused" in r.title.lower() for r in recs)

    def test_confidence_recommendations_overconfident(self):
        engine = AdaptationEngine()
        calibration = CalibrationReport(overconfidence_rate=0.5, calibration_error=0.15)
        recs = engine._confidence_recommendations(calibration)
        assert len(recs) >= 1
        assert any("overconfidence" in r.title.lower() for r in recs)

    def test_reasoning_recommendations_degrading(self):
        engine = AdaptationEngine()
        metrics = CognitionMetricsReport()
        metrics.reasoning_quality.direction = "degrading"
        metrics.reasoning_quality.current = 0.3
        recs = engine._reasoning_recommendations(metrics, [])
        assert len(recs) > 0
        assert any("degrading" in r.title.lower() or "downward" in r.title.lower() for r in recs)

    def test_runtime_recommendations_high_error(self):
        engine = AdaptationEngine()
        runtime = RuntimePerformanceMetrics(error_rate=0.1)
        recs = engine._runtime_recommendations(runtime)
        assert len(recs) > 0
        assert any("error" in r.title.lower() for r in recs)

    def test_prioritize_sorted(self):
        engine = AdaptationEngine()
        recs = [
            AdaptationRecommendation(category="a", priority=3, title="low"),
            AdaptationRecommendation(category="b", priority=8, title="high"),
            AdaptationRecommendation(category="c", priority=5, title="mid"),
        ]
        prioritized = engine._prioritize(recs)
        assert prioritized[0].priority >= prioritized[1].priority >= prioritized[2].priority

    def test_prioritize_deduplication(self):
        engine = AdaptationEngine()
        recs = [
            AdaptationRecommendation(category="a", priority=8, title="same"),
            AdaptationRecommendation(category="b", priority=5, title="same"),
        ]
        prioritized = engine._prioritize(recs)
        assert len(prioritized) == 1


# ── Meta Monitor Tests ───────────────────────────────────────────

class TestMetaMonitor:
    def test_evaluate_health_indicator_healthy(self):
        monitor = MetaMonitor()
        indicator = monitor._evaluate_health_indicator(
            "test", 0.9, warning_threshold=0.5, critical_threshold=0.3, description="ok"
        )
        assert indicator.status == "healthy"

    def test_evaluate_health_indicator_warning(self):
        monitor = MetaMonitor()
        indicator = monitor._evaluate_health_indicator(
            "test", 0.4, warning_threshold=0.5, critical_threshold=0.3, description="low"
        )
        assert indicator.status == "warning"

    def test_evaluate_health_indicator_critical(self):
        monitor = MetaMonitor()
        indicator = monitor._evaluate_health_indicator(
            "test", 0.2, warning_threshold=0.5, critical_threshold=0.3, description="bad"
        )
        assert indicator.status == "critical"

    def test_compute_overall_health_healthy(self):
        monitor = MetaMonitor()
        indicators = [
            HealthIndicator(name="a", status="healthy", value=0.9),
            HealthIndicator(name="b", status="healthy", value=0.8),
        ]
        status, score = monitor._compute_overall_health(indicators)
        assert status == "healthy"
        assert score == 1.0

    def test_compute_overall_health_critical(self):
        monitor = MetaMonitor()
        indicators = [
            HealthIndicator(name="a", status="healthy", value=0.9),
            HealthIndicator(name="b", status="critical", value=0.2),
        ]
        status, score = monitor._compute_overall_health(indicators)
        assert status == "critical"
        assert score == 0.2

    def test_build_runtime_metrics_no_crash(self):
        monitor = MetaMonitor()
        metrics = monitor._build_runtime_metrics()
        assert isinstance(metrics, RuntimePerformanceMetrics)
