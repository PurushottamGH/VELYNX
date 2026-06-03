"""Tests for Phase 11A — Conversational Working Memory."""
from __future__ import annotations

import pytest

from conversation.working_memory import (
    ConversationBuffer,
    ConversationTurn,
    WorkingContext,
    conversation_buffer,
)


@pytest.fixture
def buffer() -> ConversationBuffer:
    return ConversationBuffer()


def _user_turn(text: str, **kw) -> ConversationTurn:
    return ConversationTurn(role="user", text=text, **kw)


def _assistant_turn(text: str, **kw) -> ConversationTurn:
    return ConversationTurn(role="assistant", text=text, **kw)


class TestConversationTurn:
    def test_create_turn(self):
        turn = _user_turn("What is quantum computing?")
        assert turn.role == "user"
        assert turn.text == "What is quantum computing?"
        assert turn.turn_id  # auto-generated
        assert turn.confidence == "UNKNOWN"

    def test_turn_with_metadata(self):
        turn = _assistant_turn("Quantum computing uses qubits.", confidence="PROBABLE")
        assert turn.confidence == "PROBABLE"


class TestConversationBuffer:
    def test_add_and_retrieve(self, buffer: ConversationBuffer):
        buffer.add_turn("s1", _user_turn("Hello"))
        buffer.add_turn("s1", _assistant_turn("Hi there!", confidence="CERTAIN"))
        turns = buffer.get_recent_turns("s1")
        assert len(turns) == 2
        assert turns[0].role == "user"
        assert turns[1].role == "assistant"

    def test_separate_sessions(self, buffer: ConversationBuffer):
        buffer.add_turn("s1", _user_turn("Topic A"))
        buffer.add_turn("s2", _user_turn("Topic B"))
        assert buffer.get_turn_count("s1") == 1
        assert buffer.get_turn_count("s2") == 1

    def test_max_turns_limit(self, buffer: ConversationBuffer):
        for i in range(15):
            buffer.add_turn("s1", _user_turn(f"Turn {i}"))
        recent = buffer.get_recent_turns("s1", max_turns=5)
        assert len(recent) == 5
        assert recent[0].text == "Turn 10"

    def test_lru_eviction(self, buffer: ConversationBuffer):
        # Fill up to max sessions
        for i in range(50):
            buffer.add_turn(f"s{i}", _user_turn(f"Session {i}"))
        assert buffer.get_turn_count("s0") == 1

        # Add one more — should evict s0
        buffer.add_turn("s_new", _user_turn("New session"))
        assert buffer.get_turn_count("s0") == 0
        assert buffer.get_turn_count("s_new") == 1

    def test_context_window_empty(self, buffer: ConversationBuffer):
        assert buffer.get_context_window("nonexistent") == ""

    def test_context_window_format(self, buffer: ConversationBuffer):
        buffer.add_turn("s1", _user_turn("What is AI?"))
        buffer.add_turn("s1", _assistant_turn("AI is artificial intelligence.", confidence="CERTAIN"))
        ctx = buffer.get_context_window("s1")
        assert "User: What is AI?" in ctx
        assert "VELYNX: AI is artificial intelligence." in ctx

    def test_working_context_empty(self, buffer: ConversationBuffer):
        ctx = buffer.get_working_context("nonexistent")
        assert ctx.turn_count == 0
        assert ctx.active_topics == []

    def test_working_context_topics(self, buffer: ConversationBuffer):
        buffer.add_turn("s1", _user_turn("Tell me about quantum computing"))
        buffer.add_turn("s1", _assistant_turn("Quantum computing uses qubits."))
        buffer.add_turn("s1", _user_turn("How do quantum gates work?"))
        ctx = buffer.get_working_context("s1")
        assert ctx.turn_count == 3
        assert len(ctx.open_questions) >= 1

    def test_clear_session(self, buffer: ConversationBuffer):
        buffer.add_turn("s1", _user_turn("Hello"))
        buffer.clear("s1")
        assert buffer.get_turn_count("s1") == 0

    def test_compression_trigger(self, buffer: ConversationBuffer):
        # Add enough turns to trigger compression
        for i in range(25):
            buffer.add_turn("s1", _user_turn(f"Question {i} about quantum physics"))
            buffer.add_turn("s1", _assistant_turn(f"Answer {i}", confidence="PROBABLE"))
        # Should have compressed at least once — total should be less than 50
        count = buffer.get_turn_count("s1")
        assert count < 50  # compression happened
        assert count <= 20  # kept near threshold


class TestModuleSingleton:
    def test_singleton_exists(self):
        assert conversation_buffer is not None
        assert isinstance(conversation_buffer, ConversationBuffer)
