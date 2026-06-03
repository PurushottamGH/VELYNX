"""Metacognition layer — cognition analytics, pattern detection, calibration tracking."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TimeWindow(BaseModel):
    """Specifies an analysis time window."""
    hours: int = 24
    start: datetime | None = None
    end: datetime | None = None


class MetricPoint(BaseModel):
    """A single metric measurement at a point in time."""
    timestamp: datetime
    value: float
    label: str = ""


class MetricTrend(BaseModel):
    """Trend data for a single metric over time."""
    name: str
    unit: str = ""
    points: list[MetricPoint] = Field(default_factory=list)
    current: float = 0.0
    mean: float = 0.0
    std_dev: float = 0.0
    min_val: float = 0.0
    max_val: float = 0.0
    direction: str = "stable"
    window_hours: int = 24


class CognitionMetricsReport(BaseModel):
    """Aggregate cognition metrics over a time window."""
    window: TimeWindow = Field(default_factory=TimeWindow)
    total_reflections: int = 0
    reasoning_quality: MetricTrend = Field(default_factory=lambda: MetricTrend(name="reasoning_quality"))
    hallucination_risk: MetricTrend = Field(default_factory=lambda: MetricTrend(name="hallucination_risk"))
    confidence_delta: MetricTrend = Field(default_factory=lambda: MetricTrend(name="confidence_delta"))
    issue_category_counts: dict[str, int] = Field(default_factory=dict)
    improvement_category_counts: dict[str, int] = Field(default_factory=dict)
    avg_source_count: float = 0.0


class ReasoningPattern(BaseModel):
    """A detected pattern in reasoning behavior."""
    pattern_type: str
    category: str
    frequency: int = 0
    avg_severity: float = 0.0
    example_queries: list[str] = Field(default_factory=list)
    description: str = ""


class PatternCluster(BaseModel):
    """A cluster of similar reasoning patterns."""
    cluster_id: str
    label: str
    size: int = 0
    dominant_category: str = ""
    avg_quality: float = 0.0
    avg_hallucination_risk: float = 0.0
    patterns: list[ReasoningPattern] = Field(default_factory=list)
    recommendation: str = ""


class CalibrationRecord(BaseModel):
    """A single calibration data point linking prediction to outcome."""
    query: str
    initial_confidence: str = ""
    calibrated_confidence: str = ""
    calibration_delta: float = 0.0
    reasoning_quality: float = 0.0
    user_rating: int | None = None
    was_overconfident: bool = False
    was_underconfident: bool = False


class CalibrationReport(BaseModel):
    """Confidence calibration accuracy analysis."""
    total_records: int = 0
    mean_absolute_delta: float = 0.0
    overconfidence_rate: float = 0.0
    underconfidence_rate: float = 0.0
    calibration_error: float = 0.0
    by_confidence_level: dict[str, dict[str, float]] = Field(default_factory=dict)
    trend: MetricTrend = Field(default_factory=lambda: MetricTrend(name="calibration_error"))
    records: list[CalibrationRecord] = Field(default_factory=list)


class StrategyPerformance(BaseModel):
    """Performance data for a single strategy."""
    strategy_name: str
    query_type: str = ""
    learned_score: float = 0.0
    usage_count: int = 0
    avg_reasoning_quality: float = 0.0
    avg_hallucination_risk: float = 0.0


class StrategyAnalysis(BaseModel):
    """Cross-domain strategy performance analysis."""
    strategies: list[StrategyPerformance] = Field(default_factory=list)
    best_performing: StrategyPerformance | None = None
    worst_performing: StrategyPerformance | None = None
    underused_strategies: list[str] = Field(default_factory=list)
    domain_recommendations: dict[str, str] = Field(default_factory=dict)


class HealthIndicator(BaseModel):
    """A single cognition health signal."""
    name: str
    status: str
    value: float = 0.0
    threshold: float = 0.0
    description: str = ""


class CognitionHealthReport(BaseModel):
    """Overall cognition health assessment."""
    overall_status: str = "healthy"
    indicators: list[HealthIndicator] = Field(default_factory=list)
    score: float = 1.0
    warnings: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_now)


class AdaptationRecommendation(BaseModel):
    """A recommendation for system improvement (observe-only, never auto-applied)."""
    category: str
    priority: int = 5
    title: str = ""
    description: str = ""
    rationale: str = ""
    affected_component: str = ""
    suggested_change: str = ""
    risk: str = "low"


class RuntimePerformanceMetrics(BaseModel):
    """Runtime performance snapshot from RuntimeMonitor."""
    uptime_seconds: float = 0.0
    total_events: int = 0
    event_counts: dict[str, int] = Field(default_factory=dict)
    handler_stats: dict[str, dict[str, Any]] = Field(default_factory=dict)
    error_rate: float = 0.0
    avg_handler_latency_ms: float = 0.0


class MetacognitionReport(BaseModel):
    """Complete metacognition analysis output."""
    timestamp: datetime = Field(default_factory=_now)
    window: TimeWindow = Field(default_factory=TimeWindow)
    metrics: CognitionMetricsReport = Field(default_factory=CognitionMetricsReport)
    patterns: list[PatternCluster] = Field(default_factory=list)
    calibration: CalibrationReport = Field(default_factory=CalibrationReport)
    strategy_analysis: StrategyAnalysis = Field(default_factory=StrategyAnalysis)
    health: CognitionHealthReport = Field(default_factory=CognitionHealthReport)
    runtime: RuntimePerformanceMetrics = Field(default_factory=RuntimePerformanceMetrics)
    recommendations: list[AdaptationRecommendation] = Field(default_factory=list)
