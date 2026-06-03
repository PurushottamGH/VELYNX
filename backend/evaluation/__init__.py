"""Evaluation, benchmarking, and runtime stabilization framework."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Test Scenarios ───────────────────────────────────────────────

class TestScenario(BaseModel):
    """A reproducible test scenario for benchmarking."""
    id: str = Field(default_factory=_new_id)
    name: str
    description: str = ""
    category: str = ""  # reasoning, retrieval, memory, planning, hallucination, stress
    query: str = ""
    expected_answer: str = ""
    expected_confidence: str = ""
    expected_sources_min: int = 0
    tags: list[str] = Field(default_factory=list)
    difficulty: str = "normal"  # easy, normal, hard, extreme
    metadata: dict[str, Any] = Field(default_factory=dict)


class TestSuite(BaseModel):
    """A collection of test scenarios."""
    id: str = Field(default_factory=_new_id)
    name: str
    description: str = ""
    scenarios: list[TestScenario] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


# ── Benchmark Results ────────────────────────────────────────────

class BenchmarkResult(BaseModel):
    """Result of running a single test scenario."""
    scenario_id: str
    scenario_name: str
    passed: bool = False
    score: float = 0.0  # 0.0-1.0
    duration_ms: float = 0.0
    actual_answer: str = ""
    actual_confidence: str = ""
    actual_source_count: int = 0
    reasoning_quality: float = 0.0
    hallucination_risk: float = 0.0
    confidence_delta: float = 0.0
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class BenchmarkSuiteResult(BaseModel):
    """Result of running an entire test suite."""
    suite_id: str = ""
    suite_name: str = ""
    total_scenarios: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0
    avg_score: float = 0.0
    avg_duration_ms: float = 0.0
    results: list[BenchmarkResult] = Field(default_factory=list)
    summary: dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


# ── Profiling ────────────────────────────────────────────────────

class ProfileSample(BaseModel):
    """A single profiling measurement."""
    label: str
    duration_ms: float = 0.0
    memory_mb: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProfileReport(BaseModel):
    """Runtime profiling report."""
    total_duration_ms: float = 0.0
    samples: list[ProfileSample] = Field(default_factory=list)
    bottlenecks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_now)


# ── Evaluation Reports ───────────────────────────────────────────

class MetricEvaluation(BaseModel):
    """Evaluation of a single metric against thresholds."""
    name: str
    value: float = 0.0
    threshold: float = 0.0
    passed: bool = False
    description: str = ""


class EvaluationReport(BaseModel):
    """Complete evaluation report."""
    id: str = Field(default_factory=_new_id)
    name: str = ""
    benchmark_results: BenchmarkSuiteResult = Field(default_factory=BenchmarkSuiteResult)
    profile: ProfileReport = Field(default_factory=ProfileReport)
    metric_evaluations: list[MetricEvaluation] = Field(default_factory=list)
    stability_score: float = 1.0  # 0.0-1.0
    overall_score: float = 0.0
    passed: bool = False
    warnings: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_now)


# ── Hallucination Detection ─────────────────────────────────────

class HallucinationSignal(BaseModel):
    """A signal indicating potential hallucination."""
    signal_type: str  # unsupported_claim, factual_error, source_mismatch, overconfidence
    severity: float = 0.0  # 0.0-1.0
    description: str = ""
    evidence: str = ""


class HallucinationReport(BaseModel):
    """Report on hallucination detection for a query/answer pair."""
    query: str = ""
    answer: str = ""
    risk_score: float = 0.0  # 0.0-1.0
    signals: list[HallucinationSignal] = Field(default_factory=list)
    source_coverage: float = 0.0  # fraction of claims with sources
    confidence_reliability: float = 0.0
    timestamp: datetime = Field(default_factory=_now)


# ── Stability Monitoring ────────────────────────────────────────

class StabilityWindow(BaseModel):
    """Stability metrics over a time window."""
    window_minutes: int = 5
    error_count: int = 0
    total_operations: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    memory_growth_mb: float = 0.0
    event_throughput: float = 0.0  # events per second


class StabilityReport(BaseModel):
    """Overall stability assessment."""
    status: str = "stable"  # stable, degraded, unstable
    score: float = 1.0  # 0.0-1.0
    windows: list[StabilityWindow] = Field(default_factory=list)
    regressions: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_now)


# ── Regression Detection ────────────────────────────────────────

class Regression(BaseModel):
    """A detected regression in cognition quality."""
    metric_name: str
    baseline_value: float = 0.0
    current_value: float = 0.0
    change_pct: float = 0.0
    severity: str = "warning"  # warning, critical
    description: str = ""
    timestamp: datetime = Field(default_factory=_now)


class RegressionReport(BaseModel):
    """Report on detected regressions."""
    has_regressions: bool = False
    regressions: list[Regression] = Field(default_factory=list)
    baseline_timestamp: datetime | None = None
    current_timestamp: datetime = Field(default_factory=_now)
