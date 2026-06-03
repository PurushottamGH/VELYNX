"""Trial runner — orchestrates real-world cognition trials."""
from __future__ import annotations

import logging
import time
from typing import Any, Callable, Awaitable

from evaluation import (
    BenchmarkResult,
    BenchmarkSuiteResult,
    TestScenario,
    TestSuite,
)
from evaluation.benchmark_runner import BenchmarkRunner
from evaluation.runtime_profiler import RuntimeProfiler
from evaluation.stability_monitor import StabilityMonitor
from evaluation.hallucination_detector import hallucination_detector
from evaluation.reflection_evaluator import reflection_evaluator
from runtime.tracing import trace, get_correlation_id
from runtime.event_bus import event_bus

logger = logging.getLogger("uvicorn")

# Type for the query executor function
QueryExecutor = Callable[[str], Awaitable[dict[str, Any]]]


class TrialRunner:
    """Runs real-world cognition trials with full instrumentation."""

    def __init__(self) -> None:
        self._benchmark_runner = BenchmarkRunner()
        self._profiler = RuntimeProfiler()
        self._stability = StabilityMonitor(window_minutes=5)
        self._trial_history: list[dict[str, Any]] = []

    async def run_trial(
        self,
        name: str,
        queries: list[str],
        executor: QueryExecutor,
        max_queries: int = 100,
    ) -> dict[str, Any]:
        """Run a cognition trial with a list of queries."""
        self._profiler.start()
        self._stability = StabilityMonitor(window_minutes=5)

        results: list[dict[str, Any]] = []
        total_start = time.perf_counter()

        for i, query in enumerate(queries[:max_queries]):
            query_start = time.perf_counter()
            error = False
            result: dict[str, Any] = {}

            try:
                async with trace() as correlation_id:
                    self._profiler.start_section(f"query_{i}")
                    response = await executor(query)
                    duration_ms = self._profiler.end_section(f"query_{i}")

                    # Extract reflection data
                    debug = response.get("debug", {})
                    reflection = debug.get("reflection", {})
                    sources = response.get("sources", [])

                    # Hallucination analysis
                    hallucination = hallucination_detector.analyze(
                        query=query,
                        answer=str(response.get("answer", "")),
                        sources=sources if isinstance(sources, list) else [],
                        confidence=str(response.get("confidence", "UNKNOWN")),
                        reasoning_quality=reflection.get("reasoning_quality", 0.5)
                        if isinstance(reflection, dict) else 0.5,
                    )

                    # Reflection evaluation
                    reflection_score = 0.0
                    if isinstance(reflection, dict):
                        reflection_score = reflection_evaluator.score_reflection(reflection)

                    # Record stability
                    self._stability.record_operation(duration_ms, error=False)

                    result = {
                        "query_index": i,
                        "query": query[:200],
                        "answer": str(response.get("answer", ""))[:500],
                        "confidence": str(response.get("confidence", "UNKNOWN")),
                        "source_count": len(sources) if isinstance(sources, list) else 0,
                        "reasoning_quality": reflection.get("reasoning_quality", 0.0)
                        if isinstance(reflection, dict) else 0.0,
                        "hallucination_risk": hallucination.risk_score,
                        "reflection_score": reflection_score,
                        "duration_ms": round(duration_ms, 2),
                        "correlation_id": correlation_id,
                        "passed": hallucination.risk_score < 0.5,
                    }

            except Exception as exc:
                duration_ms = (time.perf_counter() - query_start) * 1000
                self._stability.record_operation(duration_ms, error=True)
                result = {
                    "query_index": i,
                    "query": query[:200],
                    "error": str(exc),
                    "duration_ms": round(duration_ms, 2),
                    "passed": False,
                }
                error = True

            results.append(result)

        total_duration_ms = (time.perf_counter() - total_start) * 1000

        # Compute aggregate metrics
        passed = sum(1 for r in results if r.get("passed", False))
        failed = len(results) - passed
        durations = [r.get("duration_ms", 0) for r in results]
        qualities = [r.get("reasoning_quality", 0) for r in results if "reasoning_quality" in r]
        risks = [r.get("hallucination_risk", 0) for r in results if "hallucination_risk" in r]
        reflection_scores = [r.get("reflection_score", 0) for r in results if "reflection_score" in r]

        # Get stability report
        stability = self._stability.get_stability_report()

        # Get profiling report
        profile = self._profiler.get_report()

        trial_result = {
            "trial_name": name,
            "total_queries": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / len(results), 3) if results else 0.0,
            "avg_score": round(sum(1 if r.get("passed") else 0 for r in results) / len(results), 3) if results else 0.0,
            "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0.0,
            "total_duration_ms": round(total_duration_ms, 2),
            "avg_reasoning_quality": round(sum(qualities) / len(qualities), 3) if qualities else 0.0,
            "avg_hallucination_risk": round(sum(risks) / len(risks), 3) if risks else 0.0,
            "avg_reflection_score": round(sum(reflection_scores) / len(reflection_scores), 3) if reflection_scores else 0.0,
            "stability": stability.model_dump(mode="json"),
            "profile": profile.model_dump(mode="json"),
            "results": results,
        }

        self._trial_history.append(trial_result)
        logger.info(
            "Trial '%s' completed: %d/%d passed (%.0f%%), avg quality %.3f, avg risk %.3f",
            name, passed, len(results),
            passed / len(results) * 100 if results else 0,
            trial_result["avg_reasoning_quality"],
            trial_result["avg_hallucination_risk"],
        )

        return trial_result

    async def run_benchmark_trial(
        self,
        suite_name: str,
        executor: QueryExecutor,
    ) -> dict[str, Any]:
        """Run a benchmark suite as a trial."""
        from evaluation.cognition_benchmarks import get_suite_by_name

        suite = get_suite_by_name(suite_name)
        if not suite:
            return {"error": f"Unknown suite: {suite_name}"}

        self._profiler.start()

        # Run with profiling
        result = await self._benchmark_runner.run_suite(suite, executor)

        profile = self._profiler.get_report()

        return {
            "trial_name": f"benchmark_{suite_name}",
            "suite_name": suite_name,
            "total_scenarios": result.total_scenarios,
            "passed": result.passed,
            "failed": result.failed,
            "pass_rate": result.pass_rate,
            "avg_score": result.avg_score,
            "avg_duration_ms": result.avg_duration_ms,
            "profile": profile.model_dump(mode="json"),
            "results": [r.model_dump(mode="json") for r in result.results],
        }

    async def run_long_session(
        self,
        name: str,
        queries: list[str],
        executor: QueryExecutor,
        checkpoint_interval: int = 10,
    ) -> dict[str, Any]:
        """Run a long-session trial with periodic checkpoints."""
        self._profiler.start()
        self._stability = StabilityMonitor(window_minutes=5)

        results: list[dict[str, Any]] = []
        checkpoints: list[dict[str, Any]] = []
        total_start = time.perf_counter()

        for i, query in enumerate(queries):
            query_start = time.perf_counter()

            try:
                async with trace() as correlation_id:
                    self._profiler.start_section(f"query_{i}")
                    response = await executor(query)
                    duration_ms = self._profiler.end_section(f"query_{i}")

                    debug = response.get("debug", {})
                    reflection = debug.get("reflection", {})
                    sources = response.get("sources", [])

                    hallucination = hallucination_detector.analyze(
                        query=query,
                        answer=str(response.get("answer", "")),
                        sources=sources if isinstance(sources, list) else [],
                        confidence=str(response.get("confidence", "UNKNOWN")),
                    )

                    self._stability.record_operation(duration_ms, error=False)

                    result = {
                        "query_index": i,
                        "query": query[:200],
                        "answer": str(response.get("answer", ""))[:500],
                        "confidence": str(response.get("confidence", "UNKNOWN")),
                        "reasoning_quality": reflection.get("reasoning_quality", 0.0)
                        if isinstance(reflection, dict) else 0.0,
                        "hallucination_risk": hallucination.risk_score,
                        "duration_ms": round(duration_ms, 2),
                        "correlation_id": correlation_id,
                    }
                    results.append(result)

            except Exception as exc:
                duration_ms = (time.perf_counter() - query_start) * 1000
                self._stability.record_operation(duration_ms, error=True)
                results.append({
                    "query_index": i,
                    "query": query[:200],
                    "error": str(exc),
                    "duration_ms": round(duration_ms, 2),
                })

            # Checkpoint
            if (i + 1) % checkpoint_interval == 0:
                checkpoint = self._compute_checkpoint(results, i + 1)
                checkpoints.append(checkpoint)
                logger.info("Checkpoint %d: quality=%.3f, risk=%.3f", i + 1, checkpoint["avg_quality"], checkpoint["avg_risk"])

        total_duration_ms = (time.perf_counter() - total_start) * 1000

        # Detect drift
        drift = self._detect_drift(checkpoints)

        stability = self._stability.get_stability_report()
        profile = self._profiler.get_report()

        return {
            "trial_name": name,
            "total_queries": len(results),
            "total_duration_ms": round(total_duration_ms, 2),
            "checkpoints": checkpoints,
            "drift_detected": drift,
            "stability": stability.model_dump(mode="json"),
            "profile": profile.model_dump(mode="json"),
            "results": results,
        }

    def _compute_checkpoint(self, results: list[dict], count: int) -> dict[str, Any]:
        """Compute metrics for a checkpoint window."""
        window = results[-count:] if len(results) >= count else results
        qualities = [r.get("reasoning_quality", 0) for r in window if "reasoning_quality" in r]
        risks = [r.get("hallucination_risk", 0) for r in window if "hallucination_risk" in r]
        durations = [r.get("duration_ms", 0) for r in window]
        errors = sum(1 for r in window if "error" in r)

        return {
            "query_count": len(window),
            "avg_quality": round(sum(qualities) / len(qualities), 3) if qualities else 0.0,
            "avg_risk": round(sum(risks) / len(risks), 3) if risks else 0.0,
            "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0.0,
            "error_count": errors,
        }

    def _detect_drift(self, checkpoints: list[dict]) -> dict[str, Any]:
        """Detect cognition drift across checkpoints."""
        if len(checkpoints) < 2:
            return {"detected": False, "reason": "insufficient_data"}

        first = checkpoints[0]
        last = checkpoints[-1]

        quality_drift = last["avg_quality"] - first["avg_quality"]
        risk_drift = last["avg_risk"] - first["avg_risk"]

        detected = abs(quality_drift) > 0.15 or abs(risk_drift) > 0.15

        return {
            "detected": detected,
            "quality_drift": round(quality_drift, 3),
            "risk_drift": round(risk_drift, 3),
            "quality_trend": "improving" if quality_drift > 0.05 else "degrading" if quality_drift < -0.05 else "stable",
            "risk_trend": "increasing" if risk_drift > 0.05 else "decreasing" if risk_drift < -0.05 else "stable",
        }

    def get_trial_history(self) -> list[dict[str, Any]]:
        """Get history of all trials run in this session."""
        return self._trial_history


# Module-level singleton
trial_runner = TrialRunner()
