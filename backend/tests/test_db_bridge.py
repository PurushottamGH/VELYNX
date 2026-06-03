"""Tests for database bridge — Phase 4 persistence layer."""
from __future__ import annotations

import os
import sys
import pytest

# Ensure test DB mode
os.environ["VELYNX_TEST_DB"] = "1"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.mark.asyncio
async def test_persist_episode():
    """Test episode persistence degrades gracefully."""
    from app.db_bridge import persist_episode
    from database.runtime_state import runtime_state
    await runtime_state.initialize()
    await persist_episode(
        prompt="What is quantum computing?",
        answer="Quantum computing uses qubits...",
        confidence="PROBABLE",
        source="retrieval",
        tags=["test", "quantum"],
        kind="retrieval",
        importance=0.7,
    )


@pytest.mark.asyncio
async def test_persist_reflection():
    """Test reflection persistence degrades gracefully."""
    from app.db_bridge import persist_reflection
    from database.runtime_state import runtime_state
    await runtime_state.initialize()

    class MockAudit:
        issues = []
        hallucination_risk = 0.2
        overall_quality = 0.8
        reasoning_coherence = 0.9

    class MockConfidence:
        initial = 0.7
        calibrated = 0.75
        calibration_delta = 0.05
        rationale = "Good source coverage"

    class MockImprovement:
        category = "sources"
        priority = 5
        description = "Add more sources"

    class MockReflection:
        audit = MockAudit()
        confidence_estimate = MockConfidence()
        improvements = [MockImprovement()]
        reasoning_quality = 0.85

    await persist_reflection(
        query="What is quantum computing?",
        answer="Quantum computing uses qubits...",
        reflection_result=MockReflection(),
    )


@pytest.mark.asyncio
async def test_persist_context_snapshot():
    """Test context snapshot persistence degrades gracefully."""
    from app.db_bridge import persist_context_snapshot
    from database.runtime_state import runtime_state
    await runtime_state.initialize()
    await persist_context_snapshot(
        session_id="test-session",
        snapshot_data={
            "intent": {"dimensions": ["scientific"]},
            "sources_count": 5,
            "conflicts": [],
            "confidence": "PROBABLE",
        },
    )


@pytest.mark.asyncio
async def test_persist_feedback():
    """Test feedback persistence degrades gracefully."""
    from app.db_bridge import persist_feedback
    from database.runtime_state import runtime_state
    await runtime_state.initialize()
    await persist_feedback(
        query="What is quantum computing?",
        answer="Quantum computing uses qubits...",
        rating=1,
        correction=None,
    )


@pytest.mark.asyncio
async def test_persist_source_trust():
    """Test source trust persistence degrades gracefully."""
    from app.db_bridge import persist_source_trust
    from database.runtime_state import runtime_state
    await runtime_state.initialize()
    await persist_source_trust("wikipedia.org", 0.05)
    await persist_source_trust("unreliable-source.com", -0.05)


@pytest.mark.asyncio
async def test_persist_permanence():
    """Test permanence persistence degrades gracefully."""
    from app.db_bridge import persist_permanence
    from database.runtime_state import runtime_state
    await runtime_state.initialize()
    await persist_permanence(
        fact="Quantum computing uses qubits",
        score_delta=0.05,
        source="retrieval",
    )


@pytest.mark.asyncio
async def test_persist_learned_rule():
    """Test learned rule persistence degrades gracefully."""
    from app.db_bridge import persist_learned_rule
    from database.runtime_state import runtime_state
    await runtime_state.initialize()
    await persist_learned_rule(
        title="Always cite sources",
        body="Every answer must include source citations",
        domains=["epistemology"],
        risk="low",
        status="active",
        cognitive_layer="metacognition",
    )


@pytest.mark.asyncio
async def test_graceful_degradation():
    """Test that all functions degrade gracefully when DB is unavailable."""
    from app.db_bridge import (
        persist_episode,
        persist_feedback,
        persist_source_trust,
        persist_permanence,
        persist_learned_rule,
        persist_context_snapshot,
    )
    # These should not raise even if DB is unavailable
    await persist_episode(prompt="test", answer="test")
    await persist_feedback(query="test", answer="test", rating=0)
    await persist_source_trust("test", 0.0)
    await persist_permanence("test", 0.0)
    await persist_learned_rule("test", "test")
    await persist_context_snapshot(session_id=None, snapshot_data={"test": True})
