"""Improvement engine — generates actionable suggestions from audit and confidence analysis."""
from __future__ import annotations

import logging
from typing import Any

from models.llm_client import LLMMessage, llm_client
from reflection import AuditResult, ConfidenceEstimate, ImprovementSuggestion

logger = logging.getLogger("uvicorn")

_IMPROVEMENT_PROMPT = """Based on these reasoning quality findings, generate improvement suggestions.

AUDIT:
- Overall quality: {quality:.2f}
- Hallucination risk: {hallucination_risk:.2f}
- Reasoning coherence: {coherence:.2f}
- Issues: {issues}

CONFIDENCE:
- Initial: {initial_confidence}
- Calibrated: {calibrated_confidence}
- Delta: {delta:+.3f}
- Rationale: {rationale}

Respond in JSON:
{{
  "suggestions": [
    {{"category": "sources|reasoning|confidence|memory", "priority": 1-10, "description": "...", "actionable": true}}
  ]
}}"""


async def suggest_improvements(
    audit_result: AuditResult,
    confidence_estimate: ConfidenceEstimate,
) -> list[ImprovementSuggestion]:
    """Generate improvement suggestions based on audit and confidence analysis."""
    if llm_client.available and audit_result.issues:
        return await _llm_suggestions(audit_result, confidence_estimate)
    return _rule_based_suggestions(audit_result, confidence_estimate)


async def _llm_suggestions(
    audit_result: AuditResult,
    confidence_estimate: ConfidenceEstimate,
) -> list[ImprovementSuggestion]:
    """LLM-powered improvement suggestions."""
    issues_text = "\n".join(
        f"- [{i.category}] {i.description} (severity: {i.severity:.2f})"
        for i in audit_result.issues
    ) or "No issues detected"

    prompt = _IMPROVEMENT_PROMPT.format(
        quality=audit_result.overall_quality,
        hallucination_risk=audit_result.hallucination_risk,
        coherence=audit_result.reasoning_coherence,
        issues=issues_text,
        initial_confidence=confidence_estimate.initial,
        calibrated_confidence=confidence_estimate.calibrated,
        delta=confidence_estimate.calibration_delta,
        rationale=confidence_estimate.rationale,
    )

    try:
        response = await llm_client.chat(
            [LLMMessage(role="user", content=prompt)],
            temperature=0.3,
            max_tokens=512,
            response_format={"type": "json_object"},
        )
        parsed = llm_client.parse_json_content(response)
        if parsed:
            return _parse_suggestions(parsed)
    except Exception as exc:
        logger.warning("LLM suggestions failed, using rules: %s", exc)

    return _rule_based_suggestions(audit_result, confidence_estimate)


def _parse_suggestions(data: dict[str, Any]) -> list[ImprovementSuggestion]:
    """Parse LLM suggestions response."""
    suggestions = []
    for s in data.get("suggestions", []):
        suggestions.append(ImprovementSuggestion(
            category=s.get("category", "reasoning"),
            priority=min(max(s.get("priority", 5), 1), 10),
            description=s.get("description", ""),
            actionable=s.get("actionable", True),
        ))
    return suggestions


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
