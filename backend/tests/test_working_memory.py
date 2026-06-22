"""Tests for Conversational Working Memory.

Two suites live in this file:

* Phase 11A unit tests for the ``ConversationBuffer`` data structure (class-based,
  pytest fixtures) — the low-level building block.
* Phase 55 falsifiable END-TO-END suite (bottom of file) that drives the real
  ``app.pipeline.answer_question`` entry point across TWO sequential turns sharing
  one ``session_id``, asserting pronoun resolution / context carry-over. Run it
  standalone with ``python backend/tests/test_working_memory.py`` for a PASS/FAIL
  report, or under pytest like everything else.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ── Path bootstrap (shared by both suites) ────────────────────────────────────
# The pipeline mixes bare imports (``from app.pipeline import ...``) with absolute
# package imports (``from backend.memory._sqlite import ...``), so BOTH the
# ``backend/`` directory and the repo root must be importable. This also lets the
# Phase 55 suite run as a standalone script. Same convention as test_cognition.py
# / test_semantic_grounding.py.
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]          # .../VELYNX/backend
_REPO_ROOT = _HERE.parents[2]            # .../VELYNX
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

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


# ═════════════════════════════════════════════════════════════════════════════
# Phase 55 — WORKING MEMORY: Falsifiable End-to-End Pronoun-Resolution Suite
# ═════════════════════════════════════════════════════════════════════════════
"""
Phase 55 gives VELYNX a short-term memory buffer so it can resolve pronouns and
carry context across sequential conversational turns. The unit tests above prove
the ``ConversationBuffer`` data structure works in isolation; the suite below
proves the FULL pipeline actually USES it to ground a pronoun.

We drive the EXACT backend entry point the CLI and the FastAPI ``/query`` route
both call — ``app.pipeline.answer_question`` (an async coroutine) — across two
turns that share ONE ``session_id`` (a continuous conversation):

  TURN 1 — SET CONTEXT
      Feed "My favorite coffee shop is Third Wave." and assert it is committed to
      memory (the deterministic Knowledge-Acquisition acknowledgement), making
      "Third Wave" the active concept.

  TURN 2 — PRONOUN RESOLUTION  (the Phase 55 contract)
      Ask "Is it expensive?" — where "it" can ONLY mean "Third Wave" from turn 1.
      Assert the pipeline resolved the pronoun and injected "Third Wave" into the
      semantic-search / reasoning-graph query, proven via the ``debug`` payload.
      A bare, context-free handling of "it" FAILS.

Falsifiability
--------------
Every assertion is concrete and can FAIL. Until Phase 55 wires the conversation
buffer into pronoun resolution + query expansion, TURN 2 is EXPECTED to fail —
that failure is the signal the feature does not yet exist. A green run is the
definition of "done".
"""

import asyncio

# Windows consoles default to cp1252; pipeline answers contain Unicode. Force
# UTF-8 with a safe fallback so printing a failure report can never itself crash.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

from app.pipeline import answer_question  # noqa: E402


# ── Phase 55 fixtures / constants ─────────────────────────────────────────────
# A single shared session id is what makes the two turns one conversation. This
# is the crux of the test — the pronoun in turn 2 is only resolvable because turn
# 1 ran under the SAME session.
WM_SESSION_ID = "working-memory-suite"

# TURN 1 sets the active concept ...
TURN1_STATEMENT = "My favorite coffee shop is Third Wave."
ACTIVE_CONCEPT = "Third Wave"

# ... TURN 2 refers to it ONLY by pronoun.
TURN2_PRONOUN_QUESTION = "Is it expensive?"

# The deterministic acknowledgement from the Knowledge-Acquisition layer.
COMMIT_MESSAGE = "I have committed that to memory."

# ``debug.working_memory`` already exposes these PASSIVE fields today (turn count
# + extracted topics). They must NOT be what satisfies the injection assertion —
# otherwise "Third Wave" merely lingering in active_topics would falsely pass
# without any real pronoun resolution. We exclude them and demand the concept
# appear in an ACTIVE query/search/reasoning region instead.
PASSIVE_DEBUG_PATH_PREFIXES = (
    "working_memory.active_topics",
    "working_memory.turn_count",
)


def _run(coro):
    """Drive an async pipeline call to completion from sync test context."""
    return asyncio.run(coro)


async def _two_turn_conversation(turn1: str, turn2: str):
    """
    Run two sequential turns inside ONE event loop, on the SAME session, so the
    conversation buffer populated by turn 1 is live when turn 2 is processed.
    """
    first = await answer_question(turn1, session_id=WM_SESSION_ID)
    second = await answer_question(turn2, session_id=WM_SESSION_ID)
    return first, second


def _concept_paths_in_debug(node, concept: str, _prefix: str = "") -> list[str]:
    """
    Recursively walk a debug payload and return the dotted key-paths whose
    stringified leaf value mentions ``concept`` (case-insensitive). Lists/tuples
    are indexed (``key.[0]``). Used to PROVE *where* a resolved concept surfaced.
    """
    concept_lc = concept.lower()
    hits: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            hits += _concept_paths_in_debug(value, concept, f"{_prefix}{key}.")
    elif isinstance(node, (list, tuple)):
        for idx, value in enumerate(node):
            hits += _concept_paths_in_debug(value, concept, f"{_prefix}[{idx}].")
    else:
        if concept_lc in str(node).lower():
            hits.append(_prefix.rstrip("."))
    return hits


def _active_injection_paths(debug: dict | None, concept: str) -> list[str]:
    """Concept mentions in debug EXCLUDING the passive working_memory fields."""
    paths = _concept_paths_in_debug(debug or {}, concept)
    return [
        p for p in paths
        if not any(p.startswith(prefix) for prefix in PASSIVE_DEBUG_PATH_PREFIXES)
    ]


# ─────────────────────────────────────────────────────────────────────────────
# TURN 1 — SET CONTEXT
# ─────────────────────────────────────────────────────────────────────────────
def test_phase55_turn1_sets_context():
    """The 'Third Wave' statement must be committed to memory, establishing context."""
    resp = _run(answer_question(TURN1_STATEMENT, session_id=WM_SESSION_ID))

    assert resp.answer.strip() == COMMIT_MESSAGE, (
        f"Expected the commitment message {COMMIT_MESSAGE!r}, got {resp.answer!r}. "
        "Turn 1 must commit the fact so 'Third Wave' becomes the active concept."
    )
    assert resp.confidence == "CERTAIN", (
        f"Commit should be CERTAIN, got confidence={resp.confidence!r}"
    )
    debug = resp.debug or {}
    assert debug.get("knowledge_acquisition") is True, (
        "debug.knowledge_acquisition flag missing — extraction did not run."
    )
    learned = debug.get("learned_triples") or []
    flat = " ".join(str(part) for triple in learned for part in triple).lower()
    assert ACTIVE_CONCEPT.lower() in flat, (
        f"The active concept {ACTIVE_CONCEPT!r} was not captured in any learned "
        f"triple: {learned!r}. Without it stored, turn 2 has nothing to resolve to."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 2 — PRONOUN RESOLUTION  (Phase 55 contract)
# ─────────────────────────────────────────────────────────────────────────────
def test_phase55_turn2_resolves_pronoun():
    """
    "Is it expensive?" on the SAME session must resolve "it" -> "Third Wave" and
    inject that concept into the semantic-search / reasoning-graph query.
    """
    _turn1, resp = _run(_two_turn_conversation(TURN1_STATEMENT, TURN2_PRONOUN_QUESTION))
    debug = resp.debug or {}

    # (a) Continuity: the buffer must have carried turn 1 into turn 2's processing.
    #     A working buffer reports >= 2 turns for this session by the time turn 2
    #     builds its debug payload.
    wm = (debug.get("working_memory") or {}) if isinstance(debug, dict) else {}
    turn_count = wm.get("turn_count", 0)
    assert turn_count >= 2, (
        f"Conversation continuity broken: working_memory.turn_count={turn_count!r} "
        "(<2). Turn 1 was not carried into turn 2 under the shared session, so the "
        "pronoun has no antecedent. (Today the commit path returns before the buffer "
        "records the turn — Phase 55 must fix that.)"
    )

    # (b) THE CORE CONTRACT: "Third Wave" must appear in an ACTIVE query/search/
    #     reasoning region of the debug payload — proving the pronoun "it" was
    #     resolved and the concept injected into the query that drives retrieval.
    #     Passive working_memory.active_topics is explicitly excluded so a lingering
    #     topic cannot fake a pass.
    injection_paths = _active_injection_paths(debug, ACTIVE_CONCEPT)
    assert injection_paths, (
        f"Pronoun resolution failed: {ACTIVE_CONCEPT!r} was NOT injected into any "
        f"active search/reasoning region of the debug payload. The pronoun 'it' in "
        f"{TURN2_PRONOUN_QUESTION!r} was processed literally, with no antecedent from "
        f"turn 1. Searched all debug paths except {list(PASSIVE_DEBUG_PATH_PREFIXES)!r}; "
        f"none mentioned the concept. debug keys={list(debug.keys())!r}"
    )

    # (c) The raw query echoed back must still be the verbatim pronoun question —
    #     resolution is an internal expansion, not a rewrite of the user's words.
    assert resp.query == TURN2_PRONOUN_QUESTION, (
        f"Pipeline altered the user's query: expected {TURN2_PRONOUN_QUESTION!r}, "
        f"got {resp.query!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _phase55_main() -> int:
    tests = [
        ("TURN 1 - SET CONTEXT (commit 'Third Wave')", test_phase55_turn1_sets_context),
        ("TURN 2 - PRONOUN RESOLUTION ('it' -> 'Third Wave')", test_phase55_turn2_resolves_pronoun),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 55 — Working Memory)")
    print("=" * 72)

    failures = 0
    for label, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failures += 1
            print(f"[FAIL] {label}\n       {exc}")
        except Exception as exc:  # infrastructure / import / runtime error
            failures += 1
            print(f"[ERROR] {label}\n        {type(exc).__name__}: {exc}")
        else:
            print(f"[PASS] {label}")

    print("-" * 72)
    total = len(tests)
    print(f"Result: {total - failures}/{total} passed.")
    if failures:
        print("Working memory NOT closing the loop — Phase 55 is not 'done'.")
    else:
        print("Pronoun resolution across turns verified. Phase 55 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_phase55_main())
