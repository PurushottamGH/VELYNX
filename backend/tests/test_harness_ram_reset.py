"""
Live-fire harness RAM reset — regression suite
==============================================

After a disk wipe, the harness must also drop the pipeline's in-RAM singletons,
or a taught-then-wiped fact ("Avatar") survives in memory and resurfaces on the
next interaction. The relevant state is never persisted to disk, so the wipe
alone cannot reach it.

Covers:
  * BeliefStore.clear() empties the (never-persisted) belief store.
  * ConversationBuffer.clear() with no arg clears ALL sessions; with a
    session_id it still clears just that one (backward compatible).
  * _drop_ram_singletons() resets the EXACT live instances reachable off the
    imported pipeline module, and is a safe no-op when the pipeline is absent.

Run:
    pytest backend/tests/test_harness_ram_reset.py -v
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

# ── Path bootstrap (same convention as the other suites) ──────────────────────
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]
_REPO_ROOT = _HERE.parents[2]
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from backend.conversation.beliefs import BeliefStore, belief_store  # noqa: E402
from backend.conversation.working_memory import ConversationBuffer, ConversationTurn  # noqa: E402
from backend.memory.working_memory import working_memory_manager  # noqa: E402
from backend.tests.live_fire_harness import _drop_ram_singletons  # noqa: E402


# ══════════════════════════════════════════════════════════════════════════════
# BeliefStore.clear()
# ══════════════════════════════════════════════════════════════════════════════
def test_belief_store_clear_empties_all_topics():
    store = BeliefStore()
    store.add_belief("favorite movie", "Avatar")
    store.add_belief("favorite color", "blue")
    assert store.get_beliefs_for_topic("favorite movie")

    store.clear()

    assert store.get_beliefs_for_topic("favorite movie") == []
    assert store.get_beliefs_for_topic("favorite color") == []
    assert store._beliefs == {}


# ══════════════════════════════════════════════════════════════════════════════
# ConversationBuffer.clear() — clear-all vs per-session (backward compatible)
# ══════════════════════════════════════════════════════════════════════════════
def _turn(text: str) -> ConversationTurn:
    return ConversationTurn(role="user", text=text)


def test_conversation_buffer_clear_all_sessions():
    buf = ConversationBuffer()
    buf.add_turn("s1", _turn("my favorite movie is Avatar"))
    buf.add_turn("s2", _turn("hello"))

    buf.clear()  # no arg -> wipe everything

    assert buf.get_recent_turns("s1") == []
    assert buf.get_recent_turns("s2") == []


def test_conversation_buffer_clear_single_session_still_works():
    buf = ConversationBuffer()
    buf.add_turn("s1", _turn("a"))
    buf.add_turn("s2", _turn("b"))

    buf.clear("s1")  # positional session_id -> only that session

    assert buf.get_recent_turns("s1") == []
    assert buf.get_recent_turns("s2")  # s2 survives


# ══════════════════════════════════════════════════════════════════════════════
# _drop_ram_singletons() — resets the exact live instances off the pipeline module
# ══════════════════════════════════════════════════════════════════════════════
def test_drop_ram_singletons_clears_live_instances(monkeypatch):
    # Arrange: seed the real singletons, then expose them on a stub pipeline
    # module under the key the harness actually uses ("app.pipeline").
    belief_store.add_belief("favorite movie", "Avatar")
    working_memory_manager.update("sess", ["Avatar"])
    assert belief_store.get_beliefs_for_topic("favorite movie")
    assert working_memory_manager.get_active_concepts("sess")

    fake = types.ModuleType("app.pipeline")
    fake.belief_store = belief_store
    fake.working_memory_manager = working_memory_manager
    # conversation_buffer included to mirror the real pipeline surface.
    from conversation.working_memory import conversation_buffer
    conversation_buffer.add_turn("sess", _turn("my favorite movie is Avatar"))
    fake.conversation_buffer = conversation_buffer
    monkeypatch.setitem(sys.modules, "app.pipeline", fake)

    # Act
    _drop_ram_singletons(verbose=False)

    # Assert: every wipe-surviving RAM store is emptied.
    assert belief_store.get_beliefs_for_topic("favorite movie") == []
    assert working_memory_manager.get_active_concepts("sess") == []
    assert conversation_buffer.get_recent_turns("sess") == []


def test_drop_ram_singletons_is_noop_without_pipeline(monkeypatch):
    # No app.pipeline / backend.app.pipeline in sys.modules -> must not raise.
    monkeypatch.delitem(sys.modules, "app.pipeline", raising=False)
    monkeypatch.delitem(sys.modules, "backend.app.pipeline", raising=False)
    _drop_ram_singletons(verbose=False)  # should simply return


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-v"]))
