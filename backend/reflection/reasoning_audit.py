"""Reasoning audit — analyzes reasoning quality for contradictions, hallucinations, and coherence (deterministic, no LLM)."""
from __future__ import annotations

import logging

from reflection import AuditIssue, AuditResult

logger = logging.getLogger("uvicorn")


async def audit_reasoning(
    query: str,
    answer: str,
    sources: list[dict],
    reasoning_content: str = "",
) -> AuditResult:
    """Audit reasoning quality using deterministic heuristics (no LLM)."""
    return _heuristic_audit(query, answer, sources, reasoning_content)


def _heuristic_audit(
    query: str,
    answer: str,
    sources: list[dict],
    reasoning_content: str,
) -> AuditResult:
    """Heuristic-based reasoning audit (fallback when LLM unavailable)."""
    issues: list[AuditIssue] = []
    quality = 0.5
    hallucination_risk = 0.3
    coherence = 0.5

    # Check answer length
    if len(answer) < 50:
        issues.append(AuditIssue(
            category="weak_reasoning",
            severity=0.6,
            description="Answer is very short — may lack detail or evidence",
        ))
        quality -= 0.15

    # Check source count
    if len(sources) < 2:
        issues.append(AuditIssue(
            category="unsupported",
            severity=0.5,
            description="Answer based on fewer than 2 sources — higher hallucination risk",
        ))
        hallucination_risk += 0.2
        quality -= 0.1

    # Check for citations in answer
    has_citations = any(f"[{i}]" in answer or f"[{i+1}]" in answer for i in range(5))
    if not has_citations and len(sources) > 0:
        issues.append(AuditIssue(
            category="unsupported",
            severity=0.4,
            description="Answer does not cite sources despite having them available",
        ))
        coherence -= 0.15

    # Check reasoning content presence
    if not reasoning_content:
        issues.append(AuditIssue(
            category="weak_reasoning",
            severity=0.3,
            description="No reasoning trace available — cannot verify reasoning chain",
        ))
        coherence -= 0.1

    # Check for hedging language (uncertainty indicators)
    hedge_words = ["might", "possibly", "perhaps", "maybe", "not sure", "unclear"]
    hedge_count = sum(1 for w in hedge_words if w in answer.lower())
    if hedge_count >= 3:
        hallucination_risk += 0.1

    # Normalize scores
    quality = max(0.0, min(1.0, quality))
    hallucination_risk = max(0.0, min(1.0, hallucination_risk))
    coherence = max(0.0, min(1.0, coherence))

    return AuditResult(
        issues=issues,
        overall_quality=quality,
        hallucination_risk=hallucination_risk,
        reasoning_coherence=coherence,
    )
