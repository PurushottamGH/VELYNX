"""Dialogue manager — multi-turn conversation flow controller."""
from __future__ import annotations

import logging
import re
from enum import Enum

from pydantic import BaseModel, Field

from backend.conversation.working_memory import WorkingContext

logger = logging.getLogger("uvicorn")

# Pronouns and implicit references that signal follow-ups
_FOLLOW_UP_SIGNALS = [
    "it", "that", "this", "those", "these", "them", "they",
    "the same", "what about", "how about", "and", "also",
    "too", "as well", "earlier", "before", "you said",
    "you mentioned", "going back", "regarding",
]

_GREETING_PATTERNS = re.compile(
    r"^(hi|hello|hey|good morning|good afternoon|good evening|greetings|yo)\b",
    re.IGNORECASE,
)
_FAREWELL_PATTERNS = re.compile(
    r"^(bye|goodbye|see you|thanks|thank you|that's all|no more|done|ok thanks)\b",
    re.IGNORECASE,
)
_ACKNOWLEDGMENT_PATTERNS = re.compile(
    r"^(ok|okay|sure|alright|got it|i see|makes sense|understood|right|yes|yeah|yep|no|nope)\s*[.!?]?\s*$",
    re.IGNORECASE,
)


class DialogueAct(str, Enum):
    NEW_TOPIC = "new_topic"
    FOLLOW_UP = "follow_up"
    CLARIFICATION = "clarification"
    CORRECTION = "correction"
    GREETING = "greeting"
    FAREWELL = "farewell"
    CHALLENGE = "challenge"
    ACKNOWLEDGMENT = "acknowledgment"


class DialogueState(str, Enum):
    EXPLORING = "exploring"
    CONVERGING = "converging"
    CONCLUDED = "concluded"


class DialogueDecision(BaseModel):
    """Result of dialogue analysis for a turn."""
    act: DialogueAct = DialogueAct.NEW_TOPIC
    state: DialogueState = DialogueState.EXPLORING
    needs_clarification: bool = False
    clarification_prompt: str = ""
    topic_shift_detected: bool = False
    implicit_reference_resolved: bool = False
    should_push_back: bool = False
    confidence: float = 0.8


class DialogueManager:
    """Analyzes conversation turns and manages dialogue flow."""

    def analyze_turn(
        self,
        query: str,
        working_context: WorkingContext | None = None,
    ) -> DialogueDecision:
        """Classify the dialogue act and determine flow for this turn."""
        if not working_context or working_context.turn_count == 0:
            # First turn
            if _GREETING_PATTERNS.match(query.strip()):
                return DialogueDecision(act=DialogueAct.GREETING, state=DialogueState.EXPLORING)
            return DialogueDecision(act=DialogueAct.NEW_TOPIC, state=DialogueState.EXPLORING)

        # Check greeting/farewell first
        if _GREETING_PATTERNS.match(query.strip()):
            return DialogueDecision(act=DialogueAct.GREETING, state=DialogueState.EXPLORING)
        if _FAREWELL_PATTERNS.match(query.strip()):
            return DialogueDecision(act= DialogueAct.FAREWELL, state=DialogueState.CONCLUDED)
        if _ACKNOWLEDGMENT_PATTERNS.match(query.strip()):
            return DialogueDecision(act=DialogueAct.ACKNOWLEDGMENT, state=DialogueState.CONCLUDED)

        # Detect follow-ups
        is_follow_up = self._detect_follow_up(query, working_context)

        # Detect topic shifts
        topic_shift = self._detect_topic_shift(query, working_context)

        # Detect correction
        is_correction = self._detect_correction(query)

        # Detect challenge
        is_challenge = self._detect_challenge(query)

        # Determine dialogue act
        if is_correction:
            act = DialogueAct.CORRECTION
        elif is_challenge:
            act = DialogueAct.CHALLENGE
        elif is_follow_up:
            act = DialogueAct.FOLLOW_UP
            topic_shift = False  # follow-ups are never topic shifts
        elif topic_shift:
            act = DialogueAct.NEW_TOPIC
        else:
            act = DialogueAct.NEW_TOPIC

        # Determine state
        if is_follow_up:
            state = DialogueState.CONVERGING
        elif topic_shift:
            state = DialogueState.EXPLORING
        else:
            state = DialogueState.EXPLORING

        # Check if clarification is needed
        needs_clarification, clarification_prompt = self._check_clarification(query, working_context)

        return DialogueDecision(
            act=act,
            state=state,
            needs_clarification=needs_clarification,
            clarification_prompt=clarification_prompt,
            topic_shift_detected=topic_shift,
            implicit_reference_resolved=is_follow_up,
            should_push_back=is_challenge,
            confidence=0.8,
        )

    def _detect_follow_up(self, query: str, ctx: WorkingContext) -> bool:
        """Detect if the query is a follow-up to the previous turn."""
        lowered = query.lower()
        query_words = set(re.findall(r"[a-zA-Z]{4,}", lowered))

        # Check for implicit references — but only if the query shares some topic overlap
        for signal in _FOLLOW_UP_SIGNALS:
            if signal in lowered:
                # If query also has many new topic words, it's likely a topic shift
                if ctx.active_topics:
                    topic_overlap = len(query_words & set(ctx.active_topics))
                    if topic_overlap == 0 and len(query_words) > 3:
                        return False  # topic shift, not follow-up
                return True

        # Short queries after complex topics are likely follow-ups
        if len(query.split()) < 5 and ctx.turn_count > 0:
            last_assistant_turns = [t for t in ctx.turns if t.role == "assistant"]
            if last_assistant_turns and len(last_assistant_turns[-1].text) > 100:
                return True

        return False

    def _detect_topic_shift(self, query: str, ctx: WorkingContext) -> bool:
        """Detect if the query introduces a new topic."""
        if not ctx.active_topics:
            return False

        query_words = set(re.findall(r"[a-zA-Z]{4,}", query.lower()))
        topic_words = set(ctx.active_topics)

        if not topic_words:
            return False

        overlap = len(query_words & topic_words)
        overlap_ratio = overlap / len(topic_words) if topic_words else 0

        return overlap_ratio < 0.2 and len(query.split()) > 3

    def _detect_correction(self, query: str) -> bool:
        """Detect if the user is correcting VELYNX."""
        correction_signals = [
            "no, that's wrong", "incorrect", "actually", "not quite",
            "that's not right", "i meant", "what i meant", "correction",
            "no, i asked", "wrong", "mistake",
        ]
        lowered = query.lower()
        return any(s in lowered for s in correction_signals)

    def _detect_challenge(self, query: str) -> bool:
        """Detect if the user is challenging the premise or answer."""
        challenge_signals = [
            "but", "however", "are you sure", "really", "prove",
            "source?", "evidence?", "that can't be", "i disagree",
            "that doesn't make sense", "explain why", "how do you know",
        ]
        lowered = query.lower()
        return any(s in lowered for s in challenge_signals)

    def _check_clarification(self, query: str, ctx: WorkingContext) -> tuple[bool, str]:
        """Check if the query needs clarification."""
        # Very short queries that are ambiguous
        words = query.split()
        if len(words) <= 2 and ctx.turn_count > 0:
            # Single-word or two-word queries might be ambiguous
            last_topic = ctx.active_topics[0] if ctx.active_topics else ""
            if last_topic:
                return True, f"Could you clarify what you mean about {last_topic}?"

        return False, ""


# Module-level singleton
dialogue_manager = DialogueManager()
