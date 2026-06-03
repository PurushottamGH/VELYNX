"""Reasoning audit — analyzes reasoning quality for contradictions, hallucinations, and coherence."""
from __future__ import annotations

import json
import logging
from typing import Any

from models.llm_client import LLMMessage, llm_client
from reflection import AuditIssue, AuditResult

logger = logging.getLogger("uvicorn")

_AUDIT_PROMPT = """Analyze this reasoning for quality issues. Be strict and specific.

QUESTION: {query}
ANSWER: {answer}
SOURCES: {sources}
REASONING TRACE: {reasoning_content}

Respond in JSON:
{{
  "issues": [
    {{"category": "contradiction|hallucination|weak_reasoning|repetitive|unsupported", "severity": 0.0-1.0, "description": "...", "evidence": "..."}}
  ],
  "overall_quality": 0.0-1.0,
  "hallucination_risk": 0.0-1.0,
  "reasoning_coherence": 0.0-1.0
}}"""


async def audit_reasoning(
    query: str,
    answer: str,
    sources: list[dict],
    reasoning_content: str = "",
) -> AuditResult:
    """Audit reasoning quality using LLM analysis."""
    if llm_client.available and reasoning_content:
        return await _llm_audit(query, answer, sources, reasoning_content)
    return _heuristic_audit(query, answer, sources, reasoning_content)


async def _llm_audit(
    query: str,
    answer: str,
    sources: list[dict],
    reasoning_content: str,
) -> AuditResult:
    """LLM-based reasoning audit."""
    sources_text = "\n".join(
        f"[{i+1}] {s.get('title', 'Unknown')}: {s.get('snippet', '')[:200]}"
        for i, s in enumerate(sources[:5])
    )

    prompt = _AUDIT_PROMPT.format(
        query=query,
        answer=answer[:1000],
        sources=sources_text,
        reasoning_content=reasoning_content[:1000],
    )

    try:
        response = await llm_client.chat(
            [LLMMessage(role="user", content=prompt)],
            temperature=0.2,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        parsed = llm_client.parse_json_content(response)
        if parsed:
            return _parse_audit_result(parsed)
    except Exception as exc:
        logger.warning("LLM audit failed, using heuristic: %s", exc)

    return _heuristic_audit(query, answer, sources, reasoning_content)


def _parse_audit_result(data: dict[str, Any]) -> AuditResult:
    """Parse LLM audit response into AuditResult."""
    issues = []
    for issue_data in data.get("issues", []):
        issues.append(AuditIssue(
            category=issue_data.get("category", "unknown"),
            severity=min(max(issue_data.get("severity", 0.5), 0.0), 1.0),
            description=issue_data.get("description", ""),
            evidence=issue_data.get("evidence", ""),
        ))

    return AuditResult(
        issues=issues,
        overall_quality=min(max(data.get("overall_quality", 0.5), 0.0), 1.0),
        hallucination_risk=min(max(data.get("hallucination_risk", 0.0), 0.0), 1.0),
        reasoning_coherence=min(max(data.get("reasoning_coherence", 0.5), 0.0), 1.0),
    )


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
