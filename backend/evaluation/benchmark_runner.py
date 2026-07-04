"""Benchmark runner — orchestrates evaluation test suites."""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, Awaitable

from backend.evaluation import (
    BenchmarkResult,
    BenchmarkSuiteResult,
    TestScenario,
    TestSuite,
)

logger = logging.getLogger("uvicorn")

# Type for the query executor function
QueryExecutor = Callable[[str], Awaitable[dict[str, Any]]]


class BenchmarkRunner:
    """Runs benchmark suites against a query executor."""

    async def run_suite(
        self,
        suite: TestSuite,
        executor: QueryExecutor,
    ) -> BenchmarkSuiteResult:
        """Run all scenarios in a test suite."""
        results: list[BenchmarkResult] = []
        for scenario in suite.scenarios:
            result = await self.run_scenario(scenario, executor)
            results.append(result)

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        avg_score = sum(r.score for r in results) / len(results) if results else 0.0
        avg_duration = sum(r.duration_ms for r in results) / len(results) if results else 0.0

        # Build summary by category
        summary: dict[str, float] = {}
        for r in results:
            cat = r.metadata.get("category", "unknown")
            if cat not in summary:
                summary[cat] = 0.0
            summary[cat] += r.score
        for cat in summary:
            cat_results = [r for r in results if r.metadata.get("category") == cat]
            summary[cat] = summary[cat] / len(cat_results) if cat_results else 0.0

        return BenchmarkSuiteResult(
            suite_id=suite.id,
            suite_name=suite.name,
            total_scenarios=len(results),
            passed=passed,
            failed=failed,
            pass_rate=passed / len(results) if results else 0.0,
            avg_score=avg_score,
            avg_duration_ms=avg_duration,
            results=results,
            summary=summary,
        )

    async def run_scenario(
        self,
        scenario: TestScenario,
        executor: QueryExecutor,
    ) -> BenchmarkResult:
        """Run a single test scenario."""
        start = time.perf_counter()
        errors: list[str] = []
        score = 0.0
        actual_answer = ""
        actual_confidence = ""
        actual_source_count = 0
        reasoning_quality = 0.0
        hallucination_risk = 0.0
        confidence_delta = 0.0

        try:
            response = await executor(scenario.query)
            duration_ms = (time.perf_counter() - start) * 1000

            actual_answer = str(response.get("answer", ""))
            actual_confidence = str(response.get("confidence", "UNKNOWN"))
            sources = response.get("sources", [])
            actual_source_count = len(sources) if isinstance(sources, list) else 0

            # Extract reflection data if available
            debug = response.get("debug", {})
            reflection = debug.get("reflection", {})
            if isinstance(reflection, dict):
                reasoning_quality = reflection.get("reasoning_quality", 0.0)
                hallucination_risk = reflection.get("hallucination_risk", 0.0)
                conf_est = reflection.get("confidence_estimate", {})
                if isinstance(conf_est, dict):
                    confidence_delta = conf_est.get("delta", 0.0) or 0.0

            # Evaluate results
            score = self._compute_score(
                scenario, actual_answer, actual_confidence,
                actual_source_count, reasoning_quality, hallucination_risk,
            )

            # Check specific expectations
            if scenario.expected_confidence and actual_confidence != scenario.expected_confidence:
                # Allow adjacent confidence levels
                conf_levels = ["CERTAIN", "PROBABLE", "DEBATED", "LOW", "UNKNOWN"]
                expected_idx = conf_levels.index(scenario.expected_confidence) if scenario.expected_confidence in conf_levels else -1
                actual_idx = conf_levels.index(actual_confidence) if actual_confidence in conf_levels else -1
                if expected_idx >= 0 and actual_idx >= 0 and abs(expected_idx - actual_idx) > 1:
                    errors.append(
                        f"Confidence mismatch: expected ~{scenario.expected_confidence}, "
                        f"got {actual_confidence}"
                    )
                    score *= 0.8  # penalize but don't fail

            if scenario.expected_sources_min > 0 and actual_source_count < scenario.expected_sources_min:
                errors.append(
                    f"Source count below minimum: {actual_source_count} < {scenario.expected_sources_min}"
                )
                score *= 0.9

            if scenario.expected_answer:
                if self._answer_contains(actual_answer, scenario.expected_answer):
                    score = min(score + 0.1, 1.0)
                else:
                    errors.append(f"Expected answer content not found: {scenario.expected_answer[:50]}")
                    score *= 0.7

        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            errors.append(f"Execution error: {exc}")
            score = 0.0

        passed = score >= 0.5 and not any("error" in e.lower() for e in errors)

        return BenchmarkResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            passed=passed,
            score=round(score, 3),
            duration_ms=round(duration_ms, 2),
            actual_answer=actual_answer[:500],
            actual_confidence=actual_confidence,
            actual_source_count=actual_source_count,
            reasoning_quality=round(reasoning_quality, 3),
            hallucination_risk=round(hallucination_risk, 3),
            confidence_delta=round(confidence_delta, 3),
            errors=errors,
            metadata={"category": scenario.category, "difficulty": scenario.difficulty},
        )

    def _compute_score(
        self,
        scenario: TestScenario,
        answer: str,
        confidence: str,
        source_count: int,
        reasoning_quality: float,
        hallucination_risk: float,
    ) -> float:
        """Compute a 0.0-1.0 score for a scenario result."""
        score = 0.5  # base score for getting a response

        # Answer quality
        if answer and len(answer) > 20:
            score += 0.1
        if answer and len(answer) > 100:
            score += 0.05

        # Reasoning quality from reflection
        score += reasoning_quality * 0.2

        # Hallucination penalty
        score -= hallucination_risk * 0.15

        # Source coverage bonus
        if source_count >= scenario.expected_sources_min:
            score += 0.1
        elif source_count > 0:
            score += 0.05

        # Confidence alignment
        if scenario.expected_confidence:
            conf_levels = ["CERTAIN", "PROBABLE", "DEBATED", "LOW", "UNKNOWN"]
            if scenario.expected_confidence in conf_levels and confidence in conf_levels:
                expected_idx = conf_levels.index(scenario.expected_confidence)
                actual_idx = conf_levels.index(confidence)
                distance = abs(expected_idx - actual_idx)
                score += max(0, 0.1 - distance * 0.03)

        return max(0.0, min(1.0, score))

    def _answer_contains(self, actual: str, expected: str) -> bool:
        """Check if actual answer contains expected content (case-insensitive)."""
        return expected.lower() in actual.lower()


# Module-level singleton
benchmark_runner = BenchmarkRunner()
