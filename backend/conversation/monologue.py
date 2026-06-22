"""Inner monologue engine — generates private reasoning traces before answering."""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn")


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


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
    """Generates private reasoning traces deterministically (no LLM)."""

    async def generate_monologue(
        self,
        query: str,
        sources: list[dict],
        conversation_context: str = "",
        reasoning_mode: str = "",
    ) -> MonologueTrace:
        """Generate an inner monologue trace for a query (deterministic)."""
        start = time.monotonic()
        trace = self._deterministic_monologue(query, sources, conversation_context, reasoning_mode)
        trace.duration_ms = (time.monotonic() - start) * 1000
        return trace

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
