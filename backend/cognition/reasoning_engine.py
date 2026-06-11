"""LLM reasoning engine — replaces deterministic reasoning_core with LLM inference."""
from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, Field

from models.llm_client import LLMMessage, LLMResponse, llm_client

logger = logging.getLogger("uvicorn")

_SYSTEM_PROMPT = """You are VELYNX, a cognitive reasoning system that answers questions based on provided evidence.

RULES:
- Answer ONLY based on the provided sources and prior knowledge
- If sources are insufficient, say so honestly and rate confidence as LOW
- Cite sources by number [1], [2], etc.
- Identify gaps in the evidence
- Never fabricate information not present in the sources

{constitution_block}

RESPOND IN VALID JSON:
{{
  "answer": "your detailed answer here",
  "confidence": "CERTAIN|PROBABLE|DEBATED|LOW|UNKNOWN",
  "citations": ["[1]", "[2]"],
  "gaps": ["any gaps in evidence"],
  "reasoning": "brief chain of thought"
}}"""


class ReasoningResult(BaseModel):
    """Structured output from LLM reasoning."""
    answer: str = ""
    confidence: str = "UNKNOWN"
    citations: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    reasoning_content: str = ""
    raw_response: dict[str, Any] = Field(default_factory=dict)
    token_usage: dict[str, int] = Field(default_factory=dict)


async def reason(
    query: str,
    sources: list[dict],
    *,
    constitution: str | None = None,
    cognitive_layer: str | None = None,
    memory_context: str | None = None,
    monologue_context: str | None = None,
    mode_prompt_addendum: str | None = None,
    temperature_override: float | None = None,
    resonance_context: str | None = None,
) -> ReasoningResult | None:
    """Reason across sources using LLM. Returns None if LLM unavailable."""
    if not llm_client.available:
        return None

    system_prompt = _build_system_prompt(constitution, cognitive_layer)
    if mode_prompt_addendum:
        system_prompt += f"\n\nREASONING MODE:\n{mode_prompt_addendum}"
    user_prompt = _build_user_prompt(query, sources, memory_context, resonance_context)
    if monologue_context:
        user_prompt = f"REASONING TRACE:\n{monologue_context}\n\n{user_prompt}"

    messages = [
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=user_prompt),
    ]

    response = await llm_client.chat(
        messages,
        temperature=temperature_override or 0.3,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )

    return _parse_reasoning(response)


def _build_system_prompt(constitution: str | None, cognitive_layer: str | None) -> str:
    constitution_block = ""
    if constitution:
        constitution_block = f"CONSTITUTIONAL PRINCIPLES:\n{constitution[:1500]}"
    if cognitive_layer:
        constitution_block += f"\n\nCOGNITIVE LAYER: {cognitive_layer}"

    return _SYSTEM_PROMPT.format(constitution_block=constitution_block)


def _build_user_prompt(query: str, sources: list[dict], memory_context: str | None, resonance_context: str | None = None) -> str:
    parts = []

    if resonance_context:
        parts.append(f"{resonance_context}\n")

    parts.append(f"QUESTION: {query}\n")

    if sources:
        parts.append("EVIDENCE:")
        for i, s in enumerate(sources, 1):
            title = s.get("title") or s.get("url") or f"Source {i}"
            snippet = (s.get("snippet") or "")[:500]
            parts.append(f"[{i}] {title}: {snippet}")
        parts.append("")

    if memory_context:
        parts.append(f"PRIOR KNOWLEDGE:\n{memory_context}\n")

    return "\n".join(parts)


def _parse_reasoning(response: LLMResponse) -> ReasoningResult:
    parsed = llm_client.parse_json_content(response)

    if not parsed:
        logger.warning("Failed to parse LLM JSON, using raw content")
        return ReasoningResult(
            answer=response.content,
            confidence="UNKNOWN",
            reasoning_content=response.reasoning_content,
            raw_response={"raw": response.content},
            token_usage=response.usage.model_dump(),
        )

    confidence = parsed.get("confidence", "UNKNOWN").upper()
    if confidence not in ("CERTAIN", "PROBABLE", "DEBATED", "LOW", "UNKNOWN"):
        confidence = "UNKNOWN"

    return ReasoningResult(
        answer=parsed.get("answer", ""),
        confidence=confidence,
        citations=parsed.get("citations", []),
        gaps=parsed.get("gaps", []),
        reasoning_content=parsed.get("reasoning", response.reasoning_content),
        raw_response=parsed,
        token_usage=response.usage.model_dump(),
    )
