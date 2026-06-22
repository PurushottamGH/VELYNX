"""Reflection routing — reflection phase with timeout wrapper."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.reflection.reflection_engine import reflection_engine

logger = logging.getLogger("uvicorn")


async def run_reflection(
    query: str,
    answer: str,
    sources: list[dict],
    reasoning_content: str,
    confidence: str,
) -> Any:
    """
    Run the reflection engine with a 5-second timeout.

    Returns a ReflectionResult on success, or a timed-out fallback result.
    """
    try:
        result = await asyncio.wait_for(
            reflection_engine.reflect(
                query=query,
                answer=answer,
                sources=sources,
                reasoning_content=reasoning_content,
                confidence=confidence,
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        from reflection import AuditResult, ConfidenceEstimate
        from reflection.reflection_engine import ReflectionResult

        result = ReflectionResult(
            audit=AuditResult(
                issues=[], overall_quality=0.5, hallucination_risk=0.5,
                reasoning_coherence=0.5,
            ),
            confidence_estimate=ConfidenceEstimate(
                initial=0.5, calibrated=0.5, calibration_delta=0.0,
                rationale="reflection timed out",
            ),
            improvements=[],
            memory_priority=0.3,
            reasoning_quality=0.5,
        )
    return result
