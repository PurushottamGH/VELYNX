"""Belief state management — tracks what VELYNX currently believes across turns."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn")


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BeliefStatus(str):
    ACTIVE = "active"
    CONTRADICTED = "contradicted"
    ABANDONED = "abandoned"
    SUPERSEDED = "superseded"


class Belief(BaseModel):
    """A single belief held by the system."""
    belief_id: str = Field(default_factory=_new_id)
    topic: str
    claim: str
    confidence: str = "PROBABLE"
    source_turns: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    last_verified: datetime = Field(default_factory=_now)
    contradiction_flags: list[str] = Field(default_factory=list)
    status: str = BeliefStatus.ACTIVE


class BeliefStore:
    """In-memory belief store keyed by topic."""

    def __init__(self) -> None:
        self._beliefs: dict[str, list[Belief]] = {}

    def add_belief(
        self,
        topic: str,
        claim: str,
        confidence: str = "PROBABLE",
        source_turn: str = "",
        evidence: list[str] | None = None,
    ) -> Belief:
        """Create and store a new belief."""
        belief = Belief(
            topic=topic.lower(),
            claim=claim,
            confidence=confidence,
            source_turns=[source_turn] if source_turn else [],
            supporting_evidence=evidence or [],
        )
        key = belief.topic
        if key not in self._beliefs:
            self._beliefs[key] = []
        self._beliefs[key].append(belief)
        logger.debug("Belief formed: [%s] %s", topic, claim[:80])
        return belief

    def update_belief(
        self,
        belief_id: str,
        new_confidence: str | None = None,
        new_evidence: str | None = None,
    ) -> Belief | None:
        """Update an existing belief's confidence or evidence."""
        belief = self._find_belief(belief_id)
        if not belief:
            return None
        if new_confidence:
            belief.confidence = new_confidence
        if new_evidence:
            belief.supporting_evidence.append(new_evidence)
        belief.last_verified = _now()
        return belief

    def contradict_belief(
        self,
        belief_id: str,
        contradicting_evidence: str,
        source_turn: str = "",
    ) -> Belief | None:
        """Mark a belief as contradicted with evidence."""
        belief = self._find_belief(belief_id)
        if not belief:
            return None
        belief.contradicting_evidence.append(contradicting_evidence)
        belief.contradiction_flags.append(f"contradicted_by:{source_turn}" if source_turn else "contradicted")
        belief.status = BeliefStatus.CONTRADICTED
        logger.debug("Belief contradicted: [%s] %s", belief.topic, belief.claim[:80])
        return belief

    def abandon_belief(self, belief_id: str) -> Belief | None:
        """Mark a belief as abandoned."""
        belief = self._find_belief(belief_id)
        if not belief:
            return None
        belief.status = BeliefStatus.ABANDONED
        return belief

    def get_beliefs_for_topic(self, topic: str) -> list[Belief]:
        """Get all active beliefs for a topic."""
        beliefs = self._beliefs.get(topic.lower(), [])
        return [b for b in beliefs if b.status == BeliefStatus.ACTIVE]

    def get_contradicted(self) -> list[Belief]:
        """Get all contradicted beliefs across all topics."""
        result = []
        for beliefs in self._beliefs.values():
            result.extend(b for b in beliefs if b.status == BeliefStatus.CONTRADICTED)
        return result

    def get_belief_summary(self, topic: str) -> str:
        """Format active beliefs for a topic as a string for LLM context."""
        beliefs = self.get_beliefs_for_topic(topic)
        if not beliefs:
            return ""
        parts = []
        for b in beliefs:
            parts.append(f"- {b.claim} (confidence: {b.confidence})")
        return f"Current beliefs about '{topic}':\n" + "\n".join(parts)

    def get_all_active_summary(self) -> str:
        """Format all active beliefs as a string for LLM context."""
        active = []
        for beliefs in self._beliefs.values():
            active.extend(b for b in beliefs if b.status == BeliefStatus.ACTIVE)
        if not active:
            return ""
        parts = []
        for b in active[:10]:  # cap at 10
            parts.append(f"- [{b.topic}] {b.claim} ({b.confidence})")
        return "Current beliefs:\n" + "\n".join(parts)

    def _find_belief(self, belief_id: str) -> Belief | None:
        """Find a belief by ID across all topics."""
        for beliefs in self._beliefs.values():
            for b in beliefs:
                if b.belief_id == belief_id:
                    return b
        return None


# Module-level singleton
belief_store = BeliefStore()
