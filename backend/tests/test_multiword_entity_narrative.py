"""Regression test for the Interaction #21 multi-word-entity truncation bug.

Live-fire reproduction: a multi-word named entity ("Driftwood OS") taught via a
creator fact must be narratable by the autobiographical "How did you learn who
created X?" query. Before the fix, ``intent_engine`` split "Driftwood OS" into
the separate proper nouns ["Driftwood", "OS"]; ``extract_query_concepts`` never
regrouped them, so the QUERY_FAILURE episode was tagged to the bare entity "os"
and the narrative resolved to "os" — answering "I haven't actually learned
about os yet."

This drives the SAME entry point as the live harness
(:func:`app.pipeline.answer_question`) so it exercises the real extraction →
episodic-tagging → narrative-resolution path end to end.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

# Bootstrap sys.path the same way the harness does: backend/ for `pipeline.*` /
# `app.*` imports, and the workspace root for `backend.*` imports.
_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(_BACKEND)
for _p in (_BACKEND, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _reset_state() -> None:
    """Best-effort wipe of semantic + episodic state so the run is isolated."""
    try:
        from tests.live_fire_harness import reset_state

        reset_state(verbose=False)
    except Exception:
        # If the harness wipe is unavailable, the test still runs; it just is
        # not guaranteed isolated from prior state.
        pass


PERSON = "Marla Quinn"
PRODUCT = "Driftwood OS"


@pytest.mark.parametrize("person,product", [(PERSON, PRODUCT)])
def test_multiword_entity_learning_narrative(person: str, product: str) -> None:
    from app.pipeline import answer_question

    async def _run() -> str:
        # TURN 1 — ask about an unknown multi-word entity (produces QUERY_FAILURE
        # that, pre-fix, got tagged to the truncated entity "os").
        await answer_question(f"Who created {product}?")
        # TURN 2 — teach the creator fact (KNOWLEDGE_ACQUIRED).
        await answer_question(f"{person} created {product}.")
        # TURN 3 — the autobiographical narrative query.
        resp = await answer_question(f"How did you learn who created {product}?")
        return str(getattr(resp, "answer", "") or "")

    _reset_state()
    answer = asyncio.run(_run())
    low = answer.lower()

    # The narrative must reference the actual creator we taught.
    assert person.lower() in low, (
        f"narrative did not mention the creator {person!r}: {answer!r}"
    )

    # The regression guard: it must NOT collapse the entity to the truncated
    # token "os" and claim ignorance.
    assert "learned about os" not in low, (
        f"entity truncated to 'os' — the #21 bug is back: {answer!r}"
    )
    assert "haven't actually learned" not in low, (
        f"false ignorance for a taught multi-word entity: {answer!r}"
    )


def test_query_concepts_group_multiword_entity() -> None:
    """Unit-level guard: the concept extractor keeps the full phrase together."""
    from pipeline import intent_engine
    from pipeline.reasoning_wiring import extract_query_concepts

    intent = intent_engine.decompose_query("Who created Driftwood OS?")
    concepts = extract_query_concepts("Who created Driftwood OS?", intent, [])
    assert concepts, "no concepts extracted"
    # The most-specific concept (what tags the failure episode) must be the full
    # multi-word entity, never the bare trailing token.
    assert concepts[-1].lower() == "driftwood os", concepts
    assert "os" not in [c.lower() for c in concepts], concepts

    # Single-word entities must be unaffected (no regression).
    intent_b = intent_engine.decompose_query("Who created Blender?")
    concepts_b = extract_query_concepts("Who created Blender?", intent_b, [])
    assert [c.lower() for c in concepts_b] == ["blender"], concepts_b
