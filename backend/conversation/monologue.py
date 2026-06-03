"""Inner monologue engine — generates private reasoning traces before answering."""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from models.llm_client import LLMMessage, llm_client

logger = logging.getLogger("uvicorn")


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


_MONOLOGUE_SYSTEM_PROMPT = """You are VELYNX's internal reasoning engine. Think step by step about this question. This reasoning is private — the user will not see it.

Analyze:
1. What is the user really asking?
2. What do the sources tell me?
3. What are the possible answers?
4. What are the weaknesses in my reasoning?
5. What is my confidence at each step?

Respond in VALID JSON:
{{
  "steps": [
    {{"type": "hypothesis", "content": "...", "confidence": 0.7}},
    {{"type": "evaluation", "content": "...", "confidence": 0.8}},
    {{"type": "decision", "content": "...", "confidence": 0.85}}
  ],
  "final_confidence": 0.85
}}

Step types: hypothesis, evaluation, dead_end, alternative, decision"""


class MonologueStep(BaseModel):
    """A single step in the inner monologue reasoning trace."""
    step_id: str = Field(default_factory=_new_id)
    type: str  # hypothesis, evaluation, dead_end, alternative, decision
    content: str
    confidence: float = 0.5
    timestamp: datetime = Field(default_factory=_now)


class MonologueTrace(BaseModel):
    """Complete inner monologue trace for a single query."""
    trace_id: str = Field(default_factory=_new_id)
    steps: list[MonologueStep] = Field(default_factory=list)
    final_confidence: float = 0.5
    reasoning_mode_used: str = ""
    duration_ms: float = 0.0

    def summary(self) -> str:
        """Format trace as a condensed string for reasoning context."""
        if not self.steps:
            return ""
        parts = []
        for s in self.steps:
            parts.append(f"[{s.type}] {s.content}")
        return "\n".join(parts)


class InnerMonologue:
    """Generates private reasoning traces using LLM or deterministic fallback."""

    async def generate_monologue(
        self,
        query: str,
        sources: list[dict],
        conversation_context: str = "",
        reasoning_mode: str = "",
    ) -> MonologueTrace:
        """Generate an inner monologue trace for a query."""
        start = time.monotonic()

        # Try LLM-based monologue
        if llm_client.available:
            try:
                trace = await self._llm_monologue(query, sources, conversation_context, reasoning_mode)
                trace.duration_ms = (time.monotonic() - start) * 1000
                return trace
            except Exception as exc:
                logger.debug("LLM monologue unavailable, using deterministic: %s", exc)

        # Deterministic fallback
        trace = self._deterministic_monologue(query, sources, conversation_context, reasoning_mode)
        trace.duration_ms = (time.monotonic() - start) * 1000
        return trace

    async def _llm_monologue(
        self,
        query: str,
        sources: list[dict],
        conversation_context: str,
        reasoning_mode: str,
    ) -> MonologueTrace:
        """Generate monologue using LLM."""
        # Build evidence summary
        evidence_parts = []
        for i, s in enumerate(sources[:5], 1):
            title = s.get("title") or s.get("url") or f"Source {i}"
            snippet = (s.get("snippet") or "")[:300]
            evidence_parts.append(f"[{i}] {title}: {snippet}")
        evidence = "\n".join(evidence_parts) if evidence_parts else "No sources available."

        user_prompt = f"QUESTION: {query}\n\nEVIDENCE:\n{evidence}"
        if conversation_context:
            user_prompt += f"\n\nCONVERSATION CONTEXT:\n{conversation_context[:1000]}"
        if reasoning_mode:
            user_prompt += f"\n\nREASONING MODE: {reasoning_mode}"

        messages = [
            LLMMessage(role="system", content=_MONOLOGUE_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

        response = await llm_client.chat(
            messages,
            temperature=0.4,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )

        parsed = llm_client.parse_json_content(response)
        if not parsed:
            raise ValueError("Failed to parse monologue JSON")

        steps = []
        for s in parsed.get("steps", []):
            steps.append(MonologueStep(
                type=s.get("type", "evaluation"),
                content=s.get("content", ""),
                confidence=float(s.get("confidence", 0.5)),
            ))

        return MonologueTrace(
            steps=steps,
            final_confidence=float(parsed.get("final_confidence", 0.5)),
            reasoning_mode_used=reasoning_mode,
        )

    def _deterministic_monologue(
        self,
        query: str,
        sources: list[dict],
        conversation_context: str,
        reasoning_mode: str,
    ) -> MonologueTrace:
        """Generate a deterministic monologue when LLM is unavailable."""
        steps = []

        # Step 1: Hypothesize based on query
        steps.append(MonologueStep(
            type="hypothesis",
            content=f"User is asking: {query[:200]}",
            confidence=0.5,
        ))

        # Step 2: Evaluate evidence
        source_count = len(sources)
        avg_score = sum(s.get("score", 0) for s in sources) / max(source_count, 1)
        if source_count > 0:
            steps.append(MonologueStep(
                type="evaluation",
                content=f"Found {source_count} sources with average relevance {avg_score:.2f}",
                confidence=min(avg_score + 0.1, 1.0),
            ))
        else:
            steps.append(MonologueStep(
                type="evaluation",
                content="No sources found — answer will have low confidence",
                confidence=0.2,
            ))

        # Step 3: Consider conversation context
        if conversation_context:
            steps.append(MonologueStep(
                type="evaluation",
                content="Building on prior conversation context",
                confidence=0.6,
            ))

        # Step 4: Decision based on evidence quality
        if source_count >= 3 and avg_score > 0.5:
            steps.append(MonologueStep(
                type="decision",
                content="Strong evidence available — can provide a confident answer",
                confidence=0.75,
            ))
            final_conf = 0.75
        elif source_count >= 1:
            steps.append(MonologueStep(
                type="decision",
                content="Limited evidence — answer will be qualified",
                confidence=0.5,
            ))
            final_conf = 0.5
        else:
            steps.append(MonologueStep(
                type="dead_end",
                content="No evidence found — cannot answer confidently",
                confidence=0.2,
            ))
            final_conf = 0.2

        return MonologueTrace(
            steps=steps,
            final_confidence=final_conf,
            reasoning_mode_used=reasoning_mode,
        )


# Module-level singleton
inner_monologue = InnerMonologue()
