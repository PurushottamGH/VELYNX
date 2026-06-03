"""Tests for the evaluation framework."""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluation import (
    TestScenario, TestSuite, BenchmarkResult, BenchmarkSuiteResult,
    ProfileSample, ProfileReport, MetricEvaluation, EvaluationReport,
    HallucinationSignal, HallucinationReport, StabilityWindow, StabilityReport,
    Regression, RegressionReport,
)
from evaluation.cognition_benchmarks import (
    DEFAULT_SUITES, get_all_scenarios, get_suite_by_name, get_scenarios_by_category,
)
from evaluation.benchmark_runner import BenchmarkRunner
from evaluation.runtime_profiler import RuntimeProfiler
from evaluation.reflection_evaluator import ReflectionEvaluator
from evaluation.memory_retrieval_tests import MemoryRetrievalEvaluator
from evaluation.planning_evaluator import PlanningEvaluator
from evaluation.hallucination_detector import HallucinationDetector
from evaluation.stability_monitor import StabilityMonitor


# ── Model Tests ──────────────────────────────────────────────────

class TestModels:
    def test_test_scenario_defaults(self):
        scenario = TestScenario(name="test", query="what?")
        assert scenario.difficulty == "normal"
        assert scenario.tags == []

    def test_test_suite_defaults(self):
        suite = TestSuite(name="test_suite")
        assert suite.scenarios == []

    def test_benchmark_result_defaults(self):
        result = BenchmarkResult(scenario_id="abc", scenario_name="test")
        assert result.passed is False
        assert result.score == 0.0

    def test_benchmark_suite_result(self):
        result = BenchmarkSuiteResult(suite_id="abc", suite_name="test")
        assert result.pass_rate == 0.0

    def test_profile_report_defaults(self):
        report = ProfileReport()
        assert report.total_duration_ms == 0.0
        assert report.bottlenecks == []

    def test_metric_evaluation(self):
        eval = MetricEvaluation(name="test", value=0.7, threshold=0.5, passed=True)
        assert eval.passed is True

    def test_hallucination_signal(self):
        signal = HallucinationSignal(signal_type="unsupported_claim", severity=0.5)
        assert signal.severity == 0.5

    def test_hallucination_report_defaults(self):
        report = HallucinationReport()
        assert report.risk_score == 0.0
        assert report.signals == []

    def test_stability_window(self):
        window = StabilityWindow(window_minutes=5, error_count=1, total_operations=100)
        assert window.error_rate == 0.0  # computed, not set

    def test_stability_report_defaults(self):
        report = StabilityReport()
        assert report.status == "stable"
        assert report.score == 1.0

    def test_regression(self):
        reg = Regression(metric_name="quality", baseline_value=0.8, current_value=0.6, change_pct=-25.0)
        assert reg.severity == "warning"

    def test_serialization_roundtrip(self):
        report = EvaluationReport()
        data = report.model_dump(mode="json")
        restored = EvaluationReport.model_validate(data)
        assert restored.passed is False


# ── Benchmark Suite Tests ────────────────────────────────────────

class TestCognitionBenchmarks:
    def test_default_suites_count(self):
        assert len(DEFAULT_SUITES) == 7

    def test_get_all_scenarios(self):
        scenarios = get_all_scenarios()
        assert len(scenarios) == 26

    def test_get_suite_by_name(self):
        suite = get_suite_by_name("reasoning_coherence")
        assert suite is not None
        assert suite.name == "reasoning_coherence"

    def test_get_suite_by_name_unknown(self):
        suite = get_suite_by_name("nonexistent")
        assert suite is None

    def test_get_scenarios_by_category(self):
        reasoning = get_scenarios_by_category("reasoning")
        assert len(reasoning) == 5

    def test_all_scenarios_have_queries(self):
        for scenario in get_all_scenarios():
            assert scenario.query, f"Scenario '{scenario.name}' has no query"


# ── Benchmark Runner Tests ───────────────────────────────────────

class TestBenchmarkRunner:
    @pytest.mark.asyncio
    async def test_run_suite(self):
        runner = BenchmarkRunner()
        suite = get_suite_by_name("reasoning_coherence")

        async def mock_executor(query: str) -> dict:
            return {
                "answer": "This is a test answer about the speed of light.",
                "confidence": "PROBABLE",
                "sources": [{"url": "http://example.com", "title": "Test"}],
                "debug": {
                    "reflection": {
                        "reasoning_quality": 0.7,
                        "hallucination_risk": 0.1,
                        "confidence_estimate": {"delta": 0.05},
                    }
                },
            }

        result = await runner.run_suite(suite, mock_executor)
        assert result.total_scenarios == 5
        assert result.avg_score > 0.0

    @pytest.mark.asyncio
    async def test_run_scenario(self):
        runner = BenchmarkRunner()
        scenario = TestScenario(
            name="test", query="test query", expected_confidence="PROBABLE"
        )

        async def mock_executor(query: str) -> dict:
            return {
                "answer": "Test answer",
                "confidence": "PROBABLE",
                "sources": [],
            }

        result = await runner.run_scenario(scenario, mock_executor)
        assert result.scenario_name == "test"
        assert result.score > 0.0

    def test_compute_score(self):
        runner = BenchmarkRunner()
        scenario = TestScenario(name="test", query="q", expected_confidence="PROBABLE")
        score = runner._compute_score(scenario, "A good answer", "PROBABLE", 2, 0.7, 0.1)
        assert score > 0.5

    def test_answer_contains(self):
        runner = BenchmarkRunner()
        assert runner._answer_contains("The answer is 42", "answer is 42")
        assert not runner._answer_contains("Hello", "goodbye")


# ── Runtime Profiler Tests ───────────────────────────────────────

class TestRuntimeProfiler:
    def test_profiling_flow(self):
        profiler = RuntimeProfiler()
        profiler.start()
        profiler.start_section("test")
        import time
        time.sleep(0.01)
        duration = profiler.end_section("test")
        assert duration > 0
        report = profiler.get_report()
        assert len(report.samples) == 1

    def test_record_measurement(self):
        profiler = RuntimeProfiler()
        profiler.start()
        profiler.record("test", 100.0)
        report = profiler.get_report()
        assert len(report.samples) == 1
        assert report.samples[0].duration_ms == 100.0

    def test_section_stats(self):
        profiler = RuntimeProfiler()
        profiler.start()
        profiler.record("a", 10.0)
        profiler.record("a", 20.0)
        profiler.record("b", 30.0)
        stats = profiler.get_section_stats()
        assert stats["a"]["count"] == 2
        assert stats["a"]["avg_ms"] == 15.0
        assert stats["b"]["count"] == 1


# ── Reflection Evaluator Tests ───────────────────────────────────

class TestReflectionEvaluator:
    def test_evaluate_good_reflection(self):
        evaluator = ReflectionEvaluator()
        reflection = {
            "reasoning_quality": 0.8,
            "hallucination_risk": 0.1,
            "audit": {"issues": [], "overall_quality": 0.8},
            "confidence_estimate": {"delta": 0.05},
            "improvements": [],
        }
        evaluations = evaluator.evaluate(reflection)
        assert len(evaluations) > 0
        assert all(e.passed for e in evaluations)

    def test_evaluate_poor_reflection(self):
        evaluator = ReflectionEvaluator()
        reflection = {
            "reasoning_quality": 0.3,
            "hallucination_risk": 0.6,
            "audit": {"issues": [{"category": "x"}] * 5, "overall_quality": 0.3},
            "confidence_estimate": {"delta": -0.3},
            "improvements": [{"priority": 8, "category": "sources"}],
        }
        evaluations = evaluator.evaluate(reflection)
        failed = [e for e in evaluations if not e.passed]
        assert len(failed) > 0

    def test_score_reflection(self):
        evaluator = ReflectionEvaluator()
        reflection = {"reasoning_quality": 0.8, "hallucination_risk": 0.1}
        score = evaluator.score_reflection(reflection)
        assert 0.0 <= score <= 1.0

    def test_evaluate_batch(self):
        evaluator = ReflectionEvaluator()
        reflections = [
            {"reasoning_quality": 0.8, "hallucination_risk": 0.1},
            {"reasoning_quality": 0.6, "hallucination_risk": 0.2},
        ]
        stats = evaluator.evaluate_batch(reflections)
        assert stats["avg_quality"] == pytest.approx(0.7)
        assert stats["avg_risk"] == pytest.approx(0.15)


# ── Hallucination Detector Tests ─────────────────────────────────

class TestHallucinationDetector:
    def test_analyze_basic(self):
        detector = HallucinationDetector()
        report = detector.analyze(
            query="What is 2+2?",
            answer="4",
            sources=[{"url": "http://example.com"}],
            confidence="CERTAIN",
        )
        assert report.risk_score >= 0.0

    def test_analyze_no_sources(self):
        detector = HallucinationDetector()
        report = detector.analyze(
            query="Tell me something",
            answer="A very long answer with lots of content that has no sources at all",
            sources=[],
        )
        assert report.risk_score > 0.0
        assert any(s.signal_type == "unsupported_claim" for s in report.signals)

    def test_analyze_overconfident(self):
        detector = HallucinationDetector()
        report = detector.analyze(
            query="test",
            answer="This is definitely certainly absolutely true",
            confidence="CERTAIN",
            reasoning_quality=0.2,
        )
        assert any(s.signal_type == "overconfidence" for s in report.signals)

    def test_analyze_fabricated_citation(self):
        detector = HallucinationDetector()
        report = detector.analyze(
            query="test",
            answer="According to [5] and [10], this is true",
            sources=[{"url": "http://a.com"}, {"url": "http://b.com"}],
        )
        assert any(s.signal_type == "source_mismatch" for s in report.signals)


# ── Planning Evaluator Tests ─────────────────────────────────────

class TestPlanningEvaluator:
    def test_evaluate_valid_plan(self):
        evaluator = PlanningEvaluator()
        plan = {
            "tasks": [
                {"id": "a", "description": "First task"},
                {"id": "b", "description": "Second task"},
            ],
            "edges": [("a", "b")],
            "strategy": "broad_retrieval",
        }
        evaluations = evaluator.evaluate_plan(plan)
        assert all(e.passed for e in evaluations)

    def test_evaluate_empty_plan(self):
        evaluator = PlanningEvaluator()
        plan = {"tasks": [], "edges": [], "strategy": ""}
        evaluations = evaluator.evaluate_plan(plan)
        task_count = next(e for e in evaluations if e.name == "task_count")
        assert task_count.passed is False

    def test_compute_max_depth(self):
        evaluator = PlanningEvaluator()
        tasks = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        edges = [("a", "b"), ("b", "c")]
        depth = evaluator._compute_max_depth(tasks, edges)
        assert depth == 2

    def test_evaluate_plan_execution(self):
        evaluator = PlanningEvaluator()
        report = {"total_tasks": 10, "completed": 7, "failed": 1, "overall_progress": 0.7}
        evaluations = evaluator.evaluate_plan_execution(report)
        assert any(e.name == "execution_fail_rate" for e in evaluations)


# ── Stability Monitor Tests ──────────────────────────────────────

class TestStabilityMonitor:
    def test_record_operations(self):
        monitor = StabilityMonitor(window_minutes=1)
        for i in range(100):
            monitor.record_operation(latency_ms=float(i), error=(i % 10 == 0))
        # Force window close
        monitor._window_start = 0  # force close
        report = monitor.get_stability_report()
        assert len(report.windows) > 0

    def test_detect_regressions(self):
        monitor = StabilityMonitor()
        monitor.set_baseline({"quality": 0.8, "error_rate": 0.02})
        report = monitor.detect_regressions({"quality": 0.5, "error_rate": 0.08})
        assert report.has_regressions
        assert len(report.regressions) > 0

    def test_detect_no_regressions(self):
        monitor = StabilityMonitor()
        monitor.set_baseline({"quality": 0.8})
        report = monitor.detect_regressions({"quality": 0.82})
        assert not report.has_regressions

    def test_empty_report(self):
        monitor = StabilityMonitor()
        report = monitor.get_stability_report()
        assert report.status == "stable"
