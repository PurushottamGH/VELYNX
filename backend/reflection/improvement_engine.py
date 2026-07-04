"""Improvement engine — generates actionable suggestions from audit and confidence analysis (deterministic, no LLM)."""
from __future__ import annotations

import logging

from backend.reflection import AuditResult, ConfidenceEstimate, ImprovementSuggestion

logger = logging.getLogger("uvicorn")


async def suggest_improvements(
    audit_result: AuditResult,
    confidence_estimate: ConfidenceEstimate,
) -> list[ImprovementSuggestion]:
    """Generate improvement suggestions using deterministic rules (no LLM)."""
    return _rule_based_suggestions(audit_result, confidence_estimate)


def _rule_based_suggestions(
    audit_result: AuditResult,
    confidence_estimate: ConfidenceEstimate,
) -> list[ImprovementSuggestion]:
    """Rule-based improvement suggestions (fallback)."""
    suggestions: list[ImprovementSuggestion] = []

    # High hallucination risk
    if audit_result.hallucination_risk > 0.5:
        suggestions.append(ImprovementSuggestion(
            category="sources",
            priority=8,
            description="High hallucination risk — retrieve additional sources to verify claims",
        ))

    # Low reasoning coherence
    if audit_result.reasoning_coherence < 0.4:
        suggestions.append(ImprovementSuggestion(
            category="reasoning",
            priority=7,
            description="Reasoning chain is weak — consider breaking query into sub-questions",
        ))

    # Confidence mismatch
    if confidence_estimate.calibration_delta < -0.1:
        suggestions.append(ImprovementSuggestion(
            category="confidence",
            priority=6,
            description=f"Confidence was reduced from {confidence_estimate.initial} to {confidence_estimate.calibrated} — {confidence_estimate.rationale}",
        ))

    # Unsupported claims
    unsupported = [i for i in audit_result.issues if i.category == "unsupported"]
    if unsupported:
        suggestions.append(ImprovementSuggestion(
            category="sources",
            priority=7,
            description="Some claims lack source citations — ensure all key claims reference evidence",
        ))

    # Weak reasoning issues
    weak = [i for i in audit_result.issues if i.category == "weak_reasoning"]
    if weak:
        suggestions.append(ImprovementSuggestion(
            category="reasoning",
            priority=5,
            description="Reasoning gaps detected — strengthen logical connections between evidence and conclusions",
        ))

    # Good quality — no suggestions needed
    if not suggestions and audit_result.overall_quality >= 0.7:
        suggestions.append(ImprovementSuggestion(
            category="reasoning",
            priority=1,
            description="Reasoning quality is good — no immediate improvements needed",
            actionable=False,
        ))

    return suggestions
