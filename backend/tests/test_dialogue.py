"""Tests for Phase 11D — Dialogue Management."""
from __future__ import annotations

import pytest

from conversation.dialogue_manager import (
    DialogueAct,
    DialogueDecision,
    DialogueManager,
    DialogueState,
    dialogue_manager,
)
from conversation.working_memory import ConversationTurn, WorkingContext


@pytest.fixture
def dm() -> DialogueManager:
    return DialogueManager()


def _make_ctx(turn_count: int = 1, topics: list[str] | None = None, turns: list[ConversationTurn] | None = None) -> WorkingContext:
    return WorkingContext(
        turns=turns or [],
        active_topics=topics or [],
        turn_count=turn_count,
    )


class TestDialogueAct:
    def test_greeting(self, dm: DialogueManager):
        decision = dm.analyze_turn("Hello!")
        assert decision.act == DialogueAct.GREETING
        assert decision.state == DialogueState.EXPLORING

    def test_farewell(self, dm: DialogueManager):
        ctx = _make_ctx(turn_count=2)
        decision = dm.analyze_turn("Goodbye!", ctx)
        assert decision.act == DialogueAct.FAREWELL
        assert decision.state == DialogueState.CONCLUDED

    def test_acknowledgment(self, dm: DialogueManager):
        ctx = _make_ctx(turn_count=2)
        decision = dm.analyze_turn("ok", ctx)
        assert decision.act == DialogueAct.ACKNOWLEDGMENT

    def test_new_topic_first_turn(self, dm: DialogueManager):
        decision = dm.analyze_turn("What is quantum computing?")
        assert decision.act == DialogueAct.NEW_TOPIC

    def test_follow_up_with_pronoun(self, dm: DialogueManager):
        turns = [
            ConversationTurn(role="user", text="What is quantum computing?"),
            ConversationTurn(role="assistant", text="Quantum computing is a type of computation that uses quantum mechanical phenomena."),
        ]
        ctx = _make_ctx(turn_count=2, topics=["quantum"], turns=turns)
        decision = dm.analyze_turn("Tell me more about it", ctx)
        assert decision.act == DialogueAct.FOLLOW_UP
        assert decision.state == DialogueState.CONVERGING

    def test_follow_up_short_query(self, dm: DialogueManager):
        turns = [
            ConversationTurn(role="user", text="What is quantum computing?"),
            ConversationTurn(role="assistant", text="Quantum computing is a type of computation that uses quantum mechanical phenomena. " * 5),
        ]
        ctx = _make_ctx(turn_count=2, topics=["quantum"], turns=turns)
        decision = dm.analyze_turn("How?", ctx)
        assert decision.act == DialogueAct.FOLLOW_UP

    def test_correction(self, dm: DialogueManager):
        ctx = _make_ctx(turn_count=2)
        decision = dm.analyze_turn("No, that's wrong. I meant quantum entanglement.", ctx)
        assert decision.act == DialogueAct.CORRECTION

    def test_challenge(self, dm: DialogueManager):
        ctx = _make_ctx(turn_count=2)
        decision = dm.analyze_turn("Are you sure about that? Prove it.", ctx)
        assert decision.act == DialogueAct.CHALLENGE
        assert decision.should_push_back is True

    def test_topic_shift(self, dm: DialogueManager):
        ctx = _make_ctx(turn_count=3, topics=["quantum", "computing"])
        decision = dm.analyze_turn("Tell me about the French Revolution and Napoleon", ctx)
        assert decision.topic_shift_detected is True
        assert decision.state == DialogueState.EXPLORING

    def test_clarification_short_query(self, dm: DialogueManager):
        turns = [ConversationTurn(role="assistant", text="Some prior answer")]
        ctx = _make_ctx(turn_count=1, topics=["quantum"], turns=turns)
        decision = dm.analyze_turn("what?", ctx)
        assert decision.needs_clarification is True
        assert decision.clarification_prompt


class TestModuleSingleton:
    def test_singleton_exists(self):
        assert dialogue_manager is not None
        assert isinstance(dialogue_manager, DialogueManager)
