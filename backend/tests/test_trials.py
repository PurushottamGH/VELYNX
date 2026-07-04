"""Tests for the cognition trials framework."""
from __future__ import annotations

import asyncio
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.evaluation import TestScenario, TestSuite
from backend.evaluation.trial_runner import TrialRunner
from backend.evaluation.scenario_loader import (
    get_all_trial_suites, get_trial_suite_by_name, get_all_trial_scenarios,
    DEFAULT_TRIAL_SUITES,
)
from backend.evaluation.adversarial_tests import AdversarialTestRunner
from backend.evaluation.reality_checks import RealityChecker
from backend.evaluation.failure_analysis import FailureAnalyzer
from backend.evaluation.cognition_drift_monitor import CognitionDriftMonitor
from backend.evaluation.session_replay import SessionReplay


# ── Scenario Loader Tests ────────────────────────────────────────

class TestScenarioLoader:
    def test_default_trial_suites(self):
        assert len(DEFAULT_TRIAL_SUITES) == 8

    def test_get_all_trial_suites(self):
        suites = get_all_trial_suites()
        assert len(suites) == 8

    def test_get_trial_suite_by_name(self):
        suite = get_trial_suite_by_name("adversarial_prompts")
        assert suite is not None
        assert len(suite.scenarios) == 3

    def test_get_trial_suite_by_name_unknown(self):
        assert get_trial_suite_by_name("nonexistent") is None

    def test_get_all_trial_scenarios(self):
        scenarios = get_all_trial_scenarios()
        assert len(scenarios) == 24

    def test_all_scenarios_have_queries(self):
        for scenario in get_all_trial_scenarios():
            assert scenario.query, f"Scenario '{scenario.name}' has no query"


# ── Trial Runner Tests ───────────────────────────────────────────

class TestTrialRunner:
    @pytest.mark.asyncio
    async def test_run_trial(self):
        runner = TrialRunner()
        queries = ["What is 2+2?", "What is the speed of light?"]

        async def mock_executor(query: str) -> dict:
            return {
                "answer": "42",
                "confidence": "CERTAIN",
                "sources": [{"url": "http://test.com"}],
                "debug": {
                    "reflection": {
                        "reasoning_quality": 0.8,
                        "hallucination_risk": 0.1,
                    }
                },
            }

        result = await runner.run_trial("test_trial", queries, mock_executor)
        assert result["trial_name"] == "test_trial"
        assert result["total_queries"] == 2
        assert result["avg_reasoning_quality"] > 0.0

    @pytest.mark.asyncio
    async def test_run_trial_with_error(self):
        runner = TrialRunner()
        queries = ["fail query"]

        async def failing_executor(query: str) -> dict:
            raise RuntimeError("test error")

        result = await runner.run_trial("error_trial", queries, failing_executor)
        assert result["total_queries"] == 1
        assert result["failed"] == 1

    @pytest.mark.asyncio
    async def test_run_benchmark_trial(self):
        runner = TrialRunner()

        async def mock_executor(query: str) -> dict:
            return {"answer": "test", "confidence": "PROBABLE", "sources": []}

        result = await runner.run_benchmark_trial("reasoning_coherence", mock_executor)
        assert result["suite_name"] == "reasoning_coherence"
        assert result["total_scenarios"] > 0

    @pytest.mark.asyncio
    async def test_run_long_session(self):
        runner = TrialRunner()
        queries = [f"query {i}" for i in range(25)]

        async def mock_executor(query: str) -> dict:
            return {
                "answer": "answer",
                "confidence": "PROBABLE",
                "sources": [],
                "debug": {"reflection": {"reasoning_quality": 0.7, "hallucination_risk": 0.2}},
            }

        result = await runner.run_long_session("long_test", queries, mock_executor, checkpoint_interval=10)
        assert len(result["checkpoints"]) >= 2
        assert "drift_detected" in result

    def test_detect_drift_no_drift(self):
        runner = TrialRunner()
        checkpoints = [
            {"avg_quality": 0.7, "avg_risk": 0.2},
            {"avg_quality": 0.71, "avg_risk": 0.19},
        ]
        drift = runner._detect_drift(checkpoints)
        assert drift["detected"] is False

    def test_detect_drift_with_drift(self):
        runner = TrialRunner()
        checkpoints = [
            {"avg_quality": 0.8, "avg_risk": 0.1},
            {"avg_quality": 0.4, "avg_risk": 0.6},
        ]
        drift = runner._detect_drift(checkpoints)
        assert drift["detected"] is True


# ── Adversarial Tests ────────────────────────────────────────────

class TestAdversarialTests:
    @pytest.mark.asyncio
    async def test_run_adversarial_test(self):
        runner = AdversarialTestRunner()

        async def mock_executor(query: str) -> dict:
            return {
                "answer": "I cannot confirm this claim",
                "confidence": "LOW",
                "sources": [],
            }

        result = await runner.run_adversarial_test(mock_executor)
        assert result["test_name"] == "adversarial_resistance"
        assert result["total_queries"] == 8
        assert result["avg_risk_score"] >= 0.0


# ── Reality Checks ───────────────────────────────────────────────

class TestRealityChecks:
    @pytest.mark.asyncio
    async def test_run_reality_check(self):
        checker = RealityChecker()

        async def mock_executor(query: str) -> dict:
            if "speed of light" in query.lower():
                return {"answer": "299792458 m/s", "confidence": "CERTAIN", "sources": []}
            return {"answer": "test", "confidence": "PROBABLE", "sources": []}

        result = await checker.run_reality_check(mock_executor)
        assert result["test_name"] == "reality_check"
        assert result["total_facts"] == 10
        assert "category_scores" in result


# ── Failure Analysis ─────────────────────────────────────────────

class TestFailureAnalysis:
    def test_analyze_no_failures(self):
        analyzer = FailureAnalyzer()
        results = [{"passed": True}, {"passed": True}]
        report = analyzer.analyze_failures(results)
        assert report["total_failures"] == 0

    def test_analyze_with_failures(self):
        analyzer = FailureAnalyzer()
        results = [
            {"passed": True},
            {"passed": False, "hallucination_risk": 0.8, "query": "test"},
            {"passed": False, "hallucination_risk": 0.9, "query": "test2"},
        ]
        report = analyzer.analyze_failures(results)
        assert report["total_failures"] == 2
        assert len(report["clusters"]) > 0

    def test_classify_failure_high_hallucination(self):
        analyzer = FailureAnalyzer()
        failure = {"hallucination_risk": 0.8}
        assert analyzer._classify_failure(failure) == "high_hallucination"

    def test_classify_failure_error(self):
        analyzer = FailureAnalyzer()
        failure = {"error": "timeout occurred"}
        assert analyzer._classify_failure(failure) == "timeout"

    def test_hallucination_accumulation(self):
        analyzer = FailureAnalyzer()
        results = [{"hallucination_risk": 0.1} for _ in range(5)] + \
                  [{"hallucination_risk": 0.6} for _ in range(5)]
        report = analyzer.analyze_hallucination_accumulation(results, window_size=5)
        assert len(report["windows"]) == 2


# ── Cognition Drift Monitor ──────────────────────────────────────

class TestDriftMonitor:
    def test_record_and_analyze(self):
        monitor = CognitionDriftMonitor()
        for i in range(30):
            monitor.record_query_metrics({
                "reasoning_quality": 0.7 - i * 0.01,
                "hallucination_risk": 0.1 + i * 0.01,
                "duration_ms": 1000 + i * 10,
            })
        result = monitor.analyze_drift(window_size=10)
        assert len(result["windows"]) >= 2
        assert "quality_trend" in result

    def test_no_drift(self):
        monitor = CognitionDriftMonitor()
        for _ in range(30):
            monitor.record_query_metrics({
                "reasoning_quality": 0.7,
                "hallucination_risk": 0.2,
                "duration_ms": 1000,
            })
        result = monitor.analyze_drift(window_size=10)
        assert result["drift_detected"] is False

    def test_insufficient_data(self):
        monitor = CognitionDriftMonitor()
        for _ in range(5):
            monitor.record_query_metrics({"reasoning_quality": 0.7})
        result = monitor.analyze_drift(window_size=10)
        assert result["drift_detected"] is False
        assert result["reason"] == "insufficient_data"

    def test_compute_trend_stable(self):
        monitor = CognitionDriftMonitor()
        trend = monitor._compute_trend([0.5, 0.5, 0.5, 0.5, 0.5])
        assert trend["direction"] == "stable"

    def test_compute_trend_degrading(self):
        monitor = CognitionDriftMonitor()
        trend = monitor._compute_trend([0.8, 0.7, 0.6, 0.5, 0.4])
        assert trend["direction"] == "degrading"


# ── Session Replay ───────────────────────────────────────────────

class TestSessionReplay:
    @pytest.mark.asyncio
    async def test_replay_nonexistent(self):
        replay = SessionReplay()
        result = await replay.replay_session("nonexistent_id")
        assert result["event_count"] == 0
        assert "error" in result
