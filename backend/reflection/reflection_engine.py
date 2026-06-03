"""Reflection engine — orchestrates metacognitive analysis of reasoning quality."""
from __future__ import annotations

import logging
from typing import Any

from reflection import ReflectionResult
from reflection.reasoning_audit import audit_reasoning
from reflection.confidence_estimator import estimate_confidence
from reflection.improvement_engine import suggest_improvements

logger = logging.getLogger("uvicorn")


async def reflect(
    query: str,
    answer: str,
    sources: list[dict],
    reasoning_content: str = "",
    confidence: str = "UNKNOWN",
    memory_context: str | None = None,
) -> ReflectionResult:
    """Run full reflection pipeline on a reasoning result.

    Orchestrates: audit → confidence estimation → improvement suggestions.
    """
    # Step 1: Audit reasoning quality
    audit = await audit_reasoning(query, answer, sources, reasoning_content)

    # Step 2: Calibrate confidence
    confidence_est = estimate_confidence(answer, sources, reasoning_content, confidence)

    # Step 3: Generate improvement suggestions
    improvements = await suggest_improvements(audit, confidence_est)

    # Step 4: Compute overall reasoning quality
    reasoning_quality = _compute_reasoning_quality(audit, confidence_est)

    # Step 5: Determine memory priority (how important is this reflection to store)
    memory_priority = _compute_memory_priority(audit, confidence_est, reasoning_quality)

    return ReflectionResult(
        audit=audit,
        confidence_estimate=confidence_est,
        improvements=improvements,
        memory_priority=memory_priority,
        reasoning_quality=reasoning_quality,
    )


def _compute_reasoning_quality(audit, confidence_est) -> float:
    """Compute overall reasoning quality from audit and confidence signals."""
    # Weight audit quality heavily
    quality = audit.overall_quality * 0.5

    # Reasoning coherence
    quality += audit.reasoning_coherence * 0.25

    # Penalize hallucination risk
    quality -= audit.hallucination_risk * 0.15

    # Bonus for stable confidence (no large negative delta)
    if confidence_est.calibration_delta >= 0:
        quality += 0.1
    elif confidence_est.calibration_delta > -0.1:
        quality += 0.05

    return max(0.0, min(1.0, quality))


def _compute_memory_priority(audit, confidence_est, reasoning_quality) -> float:
    """Determine how important this reflection is to store in memory."""
    priority = reasoning_quality * 0.5

    # High hallucination risk = high priority (learn from mistakes)
    if audit.hallucination_risk > 0.5:
        priority += 0.2

    # Large confidence drop = high priority (calibration issue)
    if confidence_est.calibration_delta < -0.15:
        priority += 0.15

    # Many issues = high priority
    if len(audit.issues) >= 3:
        priority += 0.1

    return max(0.0, min(1.0, priority))


# Module-level singleton
class _ReflectionEngine:
    """Wrapper to provide a clean module-level interface."""

    async def reflect(self, **kwargs) -> ReflectionResult:
        return await reflect(**kwargs)


reflection_engine = _ReflectionEngine()
