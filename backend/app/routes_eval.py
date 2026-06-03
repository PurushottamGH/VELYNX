"""Metacognition, evaluation, and trials API routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter

logger = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/metacognition/analyze")
async def metacognition_analyze(window_hours: int = 24) -> dict:
    """Run metacognition analysis."""
    from metacognition.meta_monitor import meta_monitor
    analysis = await meta_monitor.analyze(window_hours=window_hours)
    return analysis.model_dump(mode="json")


@router.get("/metacognition/health")
async def metacognition_health() -> dict:
    """Metacognition system health."""
    from metacognition.meta_monitor import meta_monitor
    return meta_monitor.get_health()


@router.get("/metacognition/recommendations")
async def metacognition_recommendations(window_hours: int = 24) -> dict:
    """Get metacognition recommendations."""
    from metacognition.adaptation_engine import adaptation_engine
    recs = await adaptation_engine.generate_recommendations(window_hours=window_hours)
    return {"recommendations": [r.model_dump(mode="json") for r in recs]}


@router.post("/evaluation/benchmark")
async def run_benchmark(suite_name: str = "reasoning_coherence") -> dict:
    """Run a benchmark suite."""
    from evaluation.benchmark_runner import benchmark_runner
    report = await benchmark_runner.run_suite(suite_name)
    return report.model_dump(mode="json")


@router.get("/evaluation/stability")
async def evaluation_stability() -> dict:
    """Runtime stability report."""
    from evaluation.stability_monitor import stability_monitor
    return stability_monitor.get_report()


@router.get("/evaluation/hallucination")
async def evaluate_hallucination(query: str, answer: str) -> dict:
    """Check an answer for hallucination."""
    from evaluation.hallucination_detector import hallucination_detector
    result = hallucination_detector.detect(query, answer)
    return result.model_dump(mode="json")


@router.post("/trials/run")
async def run_trial(suite_name: str = "reasoning_coherence", max_queries: int = 10) -> dict:
    """Run a trial suite with profiling."""
    from evaluation.trial_runner import trial_runner
    report = await trial_runner.run_trial(suite_name, max_queries=max_queries)
    return report.model_dump(mode="json")


@router.post("/trials/adversarial")
async def run_adversarial_trial() -> dict:
    """Run adversarial tests."""
    from evaluation.adversarial_tests import adversarial_tests
    results = adversarial_tests.run_all()
    return {"results": [r.model_dump(mode="json") for r in results]}


@router.post("/trials/reality-check")
async def run_reality_check() -> dict:
    """Run reality checks."""
    from evaluation.reality_checks import reality_checks
    results = reality_checks.run_all()
    return {"results": [r.model_dump(mode="json") for r in results]}


@router.get("/trials/replay/{correlation_id}")
async def replay_trial_session(correlation_id: str) -> dict:
    """Replay a trial session."""
    from evaluation.session_replay import session_replay
    return await session_replay.replay(correlation_id)
