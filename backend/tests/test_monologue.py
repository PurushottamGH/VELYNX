"""Tests for Phase 11B — Inner Monologue Engine."""
from __future__ import annotations

import pytest

from conversation.monologue import (
    InnerMonologue,
    MonologueStep,
    MonologueTrace,
    inner_monologue,
)


@pytest.fixture
def monologue() -> InnerMonologue:
    return InnerMonologue()


class TestMonologueStep:
    def test_create_step(self):
        step = MonologueStep(type="hypothesis", content="The user is asking about AI", confidence=0.7)
        assert step.type == "hypothesis"
        assert step.step_id  # auto-generated
        assert step.confidence == 0.7


class TestMonologueTrace:
    def test_empty_trace(self):
        trace = MonologueTrace()
        assert trace.summary() == ""
        assert trace.steps == []

    def test_trace_summary(self):
        trace = MonologueTrace(steps=[
            MonologueStep(type="hypothesis", content="User asks about quantum", confidence=0.6),
            MonologueStep(type="evaluation", content="Found 3 relevant sources", confidence=0.7),
            MonologueStep(type="decision", content="Can answer confidently", confidence=0.8),
        ])
        summary = trace.summary()
        assert "[hypothesis]" in summary
        assert "[evaluation]" in summary
        assert "[decision]" in summary


class TestInnerMonologue:
    @pytest.mark.asyncio
    async def test_deterministic_with_sources(self, monologue: InnerMonologue):
        sources = [
            {"title": "Quantum Computing", "snippet": "Uses qubits", "score": 0.8},
            {"title": "Quantum Gates", "snippet": "Manipulate qubits", "score": 0.7},
            {"title": "Quantum Algorithms", "snippet": "Shor's algorithm", "score": 0.6},
        ]
        trace = await monologue.generate_monologue("What is quantum computing?", sources)
        assert len(trace.steps) >= 3
        assert trace.final_confidence > 0
        assert trace.duration_ms >= 0
        # Should have hypothesis, evaluation, decision
        types = [s.type for s in trace.steps]
        assert "hypothesis" in types
        assert "evaluation" in types

    @pytest.mark.asyncio
    async def test_deterministic_no_sources(self, monologue: InnerMonologue):
        trace = await monologue.generate_monologue("What is X?", [])
        assert len(trace.steps) >= 2
        assert trace.final_confidence <= 0.3
        # Should have a dead_end
        types = [s.type for s in trace.steps]
        assert "dead_end" in types

    @pytest.mark.asyncio
    async def test_with_conversation_context(self, monologue: InnerMonologue):
        sources = [{"title": "Test", "snippet": "Content", "score": 0.5}]
        trace = await monologue.generate_monologue(
            "Follow up question", sources, conversation_context="Prior context about AI"
        )
        assert len(trace.steps) >= 3
        # Should mention building on context
        contents = [s.content for s in trace.steps]
        assert any("context" in c.lower() for c in contents)

    @pytest.mark.asyncio
    async def test_with_reasoning_mode(self, monologue: InnerMonologue):
        sources = [{"title": "Test", "snippet": "Content", "score": 0.5}]
        trace = await monologue.generate_monologue(
            "Test query", sources, reasoning_mode="adversarial"
        )
        assert trace.reasoning_mode_used == "adversarial"

    @pytest.mark.asyncio
    async def test_many_sources(self, monologue: InnerMonologue):
        sources = [{"title": f"Source {i}", "snippet": f"Content {i}", "score": 0.5 + i * 0.05} for i in range(10)]
        trace = await monologue.generate_monologue("Test query", sources)
        # Should only use first 5 in LLM call (but all in evaluation)
        assert trace.final_confidence > 0


class TestModuleSingleton:
    def test_singleton_exists(self):
        assert inner_monologue is not None
        assert isinstance(inner_monologue, InnerMonologue)
