"""Conversational working memory — session-scoped 'RAM' for tracking conversation arc."""
from __future__ import annotations

import logging
import uuid
from collections import OrderedDict
from datetime import datetime, timezone

from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn")

_MAX_SESSIONS = 50
_COMPRESS_THRESHOLD = 20  # compress when turns exceed this


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ConversationTurn(BaseModel):
    """A single turn in a conversation."""
    turn_id: str = Field(default_factory=_new_id)
    role: str  # "user" or "assistant"
    text: str
    timestamp: datetime = Field(default_factory=_now)
    intent: dict = Field(default_factory=dict)
    confidence: str = "UNKNOWN"
    dialogue_act: str | None = None
    metadata: dict = Field(default_factory=dict)


class WorkingContext(BaseModel):
    """Full working context for a conversation session."""
    turns: list[ConversationTurn] = Field(default_factory=list)
    established_facts: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    active_topics: list[str] = Field(default_factory=list)
    intent_evolution: list[str] = Field(default_factory=list)
    turn_count: int = 0
    compressed_summary: str = ""


class ConversationBuffer:
    """In-memory conversation buffer keyed by session_id with LRU eviction."""

    def __init__(self) -> None:
        self._sessions: OrderedDict[str, list[ConversationTurn]] = OrderedDict()

    def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Append a turn to the session buffer. Triggers compression if needed."""
        if session_id not in self._sessions:
            # Evict oldest if at capacity
            if len(self._sessions) >= _MAX_SESSIONS:
                evicted_id, _ = self._sessions.popitem(last=False)
                logger.debug("Evicted session %s (LRU)", evicted_id)
            self._sessions[session_id] = []
        else:
            # Move to end (most recently used)
            self._sessions.move_to_end(session_id)

        self._sessions[session_id].append(turn)

        # Compress if over threshold
        if len(self._sessions[session_id]) > _COMPRESS_THRESHOLD:
            self._compress(session_id)

    def get_recent_turns(self, session_id: str, max_turns: int = 10) -> list[ConversationTurn]:
        """Get the most recent turns for a session."""
        turns = self._sessions.get(session_id, [])
        return turns[-max_turns:]

    def get_context_window(self, session_id: str, max_turns: int = 10) -> str:
        """Format recent turns as a string for LLM context injection."""
        turns = self.get_recent_turns(session_id, max_turns)
        if not turns:
            return ""
        parts = []
        for t in turns:
            role_label = "User" if t.role == "user" else "VELYNX"
            parts.append(f"{role_label}: {t.text[:300]}")
        return "\n".join(parts)

    def get_working_context(self, session_id: str) -> WorkingContext:
        """Build a full working context from conversation history."""
        turns = self._sessions.get(session_id, [])
        if not turns:
            return WorkingContext()

        # Extract active topics from recent user turns
        topics = self._extract_topics(turns)

        # Extract intent evolution
        intent_evolution = [
            t.intent.get("query", t.text[:80])
            for t in turns
            if t.role == "user" and t.intent
        ][-5:]

        # Extract established facts from assistant turns with high confidence
        facts = self._extract_facts(turns)

        # Extract open questions from user turns
        questions = [
            t.text for t in turns
            if t.role == "user" and ("?" in t.text or any(
                w in t.text.lower() for w in ["what", "why", "how", "when", "where", "who"]
            ))
        ][-5:]

        return WorkingContext(
            turns=turns[-10:],
            established_facts=facts,
            open_questions=questions,
            active_topics=topics,
            intent_evolution=intent_evolution,
            turn_count=len(turns),
        )

    def get_turn_count(self, session_id: str) -> int:
        """Get the number of turns in a session."""
        return len(self._sessions.get(session_id, []))

    def clear(self, session_id: str | None = None) -> None:
        """Clear one session's buffer, or ALL sessions when ``session_id`` is None.

        Clearing all is used to reset in-memory conversation state between
        live-fire runs — a disk wipe cannot reach this RAM buffer, so without it
        a fact stated in a prior turn ("Avatar") survives and resurfaces.
        """
        if session_id is None:
            self._sessions.clear()
        else:
            self._sessions.pop(session_id, None)

    def _extract_topics(self, turns: list[ConversationTurn]) -> list[str]:
        """Extract active topics from conversation turns."""
        # Collect keywords from recent user turns
        recent_user = [t for t in turns[-6:] if t.role == "user"]
        keyword_counts: dict[str, int] = {}
        for t in recent_user:
            words = t.text.lower().split()
            for w in words:
                w = w.strip("?!.,;:'\"")
                if len(w) > 3 and w not in _STOP_WORDS:
                    keyword_counts[w] = keyword_counts.get(w, 0) + 1
        # Return top keywords appearing in multiple turns
        return [w for w, c in sorted(keyword_counts.items(), key=lambda x: -x[1]) if c >= 1][:5]

    def _extract_facts(self, turns: list[ConversationTurn]) -> list[str]:
        """Extract established facts from high-confidence assistant turns."""
        facts = []
        for t in turns:
            if t.role == "assistant" and t.confidence in ("CERTAIN", "PROBABLE"):
                facts.append(t.text[:200])
        return facts[-5:]

    def _compress(self, session_id: str) -> None:
        """Compress old turns into a summary, keeping recent turns intact."""
        turns = self._sessions.get(session_id, [])
        if len(turns) <= _COMPRESS_THRESHOLD:
            return

        # Keep last 10 turns, compress the rest
        recent = turns[-10:]
        old = turns[:-10]

        # Heuristic compression: extract key info from old turns
        summary_parts = []
        user_turns = [t for t in old if t.role == "user"]
        assistant_turns = [t for t in old if t.role == "assistant"]

        if user_turns:
            topics_discussed = list(set(
                t.text[:80] for t in user_turns[-5:]
            ))
            summary_parts.append(f"Topics discussed: {'; '.join(topics_discussed)}")

        if assistant_turns:
            confidences = [t.confidence for t in assistant_turns if t.confidence != "UNKNOWN"]
            if confidences:
                summary_parts.append(f"Prior confidence levels: {', '.join(confidences[-3:])}")

        compressed_summary = ". ".join(summary_parts) if summary_parts else ""

        # Store summary in the first remaining turn's metadata
        if recent and compressed_summary:
            recent[0].metadata["compressed_summary"] = compressed_summary

        self._sessions[session_id] = recent
        logger.debug("Compressed session %s: %d old turns -> summary", session_id, len(old))


_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must", "about",
    "above", "after", "again", "all", "also", "and", "any", "because",
    "before", "between", "both", "but", "by", "each", "for", "from",
    "further", "get", "got", "here", "how", "into", "just", "like",
    "make", "many", "more", "most", "much", "must", "never", "new",
    "now", "only", "other", "our", "out", "over", "own", "part",
    "per", "put", "said", "same", "see", "she", "should", "since",
    "so", "some", "still", "such", "take", "than", "that", "their",
    "them", "then", "there", "these", "they", "this", "those", "through",
    "together", "too", "under", "until", "upon", "very", "want", "was",
    "well", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "within", "without", "would", "your", "tell",
    "think", "know", "really", "actually", "please", "help",
}

# Module-level singleton
conversation_buffer = ConversationBuffer()
