"""
KG fast-path supersession guard — race-condition regression suite
=================================================================

Covers the fix for the "Avatar ghost" stale read: the KG retrieval fast path
must DEFER (return ``None`` -> fall through to reasoning) when a personal
preference has a *pending* (un-consolidated) revision, but must add ZERO latency
to abstract / definitional questions.

The fix has three load-bearing pieces, each tested here in isolation because the
fast path's KG lookup is currently inert (``memory.knowledge_graph`` exports no
``knowledge_graph`` singleton, so the import raises and the path returns ``None``
regardless). These tests therefore pin the *logic* the path will use once the
lookup is revived, plus the now-correct pending-revision semantics:

  1. ``_looks_like_preference_query``  — the cheap, DB-free latency gate.
  2. ``consolidator.has_pending_revision`` — scoped to ``consolidated = 0`` so a
     RESOLVED revision stops deferring (the previous ``COUNT(DISTINCT object)``
     guard deferred a re-taught subject forever).
  3. ``knowledge_router._has_pending_supersession`` — the router's defensive
     delegation to the consolidator.

Run:
    pytest backend/tests/test_fastpath_supersession.py -v
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# ── Path bootstrap (same convention as test_belief_revision.py) ───────────────
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]          # .../VELYNX/backend
_REPO_ROOT = _HERE.parents[2]            # .../VELYNX
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from backend.knowledge import consolidator  # noqa: E402
from backend.pipeline import knowledge_router  # noqa: E402


# ── helpers ───────────────────────────────────────────────────────────────────
def _seed_triples(db_path: Path, rows: list[tuple[str, str, str, int]]) -> None:
    """Create a raw ``triples`` table (real schema + consolidated flag) and seed.

    ``rows`` items are ``(subject, relation, object, consolidated)``.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS triples (
                id INTEGER PRIMARY KEY,
                subject TEXT NOT NULL,
                relation TEXT NOT NULL,
                object TEXT NOT NULL,
                confidence REAL,
                source TEXT,
                timestamp REAL,
                consolidated INTEGER NOT NULL DEFAULT 0,
                UNIQUE(subject, relation, object)
            )
            """
        )
        conn.executemany(
            "INSERT OR IGNORE INTO triples (subject, relation, object, consolidated) "
            "VALUES (?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


class _FakeNode:
    """Minimal stand-in for a KG node: only the ``.concept`` subject is read."""

    def __init__(self, concept: str) -> None:
        self.concept = concept


# ══════════════════════════════════════════════════════════════════════════════
# 1. Latency gate — abstract questions must never qualify for the DB check.
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize(
    "query",
    [
        "What is my favorite movie?",
        "what's your favourite color",
        "Tell me about my favorite movie",
        "Do you prefer tea or coffee?",
        "remind me of my favorite food",
    ],
)
def test_preference_queries_qualify_for_check(query):
    assert knowledge_router._looks_like_preference_query(query) is True


@pytest.mark.parametrize(
    "query",
    [
        "What is love?",
        "What is justice?",
        "Explain the theory of relativity.",
        "define entropy",
        "Who created Blender?",   # not a personal preference -> stays cheap
        "",
    ],
)
def test_abstract_queries_skip_the_check(query):
    assert knowledge_router._looks_like_preference_query(query) is False


# ══════════════════════════════════════════════════════════════════════════════
# 2. Pending-revision detection — scoped to un-consolidated singular rows.
# ══════════════════════════════════════════════════════════════════════════════
def test_pending_unconsolidated_preference_is_a_revision(tmp_path, monkeypatch):
    # Arrange: a favorite-movie re-teach sitting un-consolidated in raw memory.
    db = tmp_path / "graph.db"
    _seed_triples(db, [("User's favorite movie", "be", "Avatar", 0)])

    # Patch both the path resolver AND the local open_connection reference to
    # insulate against test-pollution that corrupts the consolidator's state.
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: db)
    monkeypatch.setattr(
        consolidator, "open_connection",
        lambda path, **kw: sqlite3.connect(str(db), **kw),
    )

    # Act / Assert: the consolidator reports a pending revision -> fast path defers.
    assert consolidator.has_pending_revision("User's favorite movie") is True


def test_consolidated_revision_no_longer_defers(tmp_path, monkeypatch):
    # The bug-fix contract: once reconciled (consolidated=1), the subject's fast
    # path must resume — the old COUNT(DISTINCT object) guard deferred forever.
    db = tmp_path / "graph.db"
    _seed_triples(
        db,
        [
            ("User's favorite movie", "be", "Interstellar", 1),
            ("User's favorite movie", "be", "Avatar", 1),
        ],
    )
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: db)

    assert consolidator.has_pending_revision("User's favorite movie") is False


def test_non_singular_pending_fact_is_not_a_revision(tmp_path, monkeypatch):
    # "knows" is open / multi-valued: a pending row is not a functional revision.
    db = tmp_path / "graph.db"
    _seed_triples(db, [("User", "knows", "Python", 0)])
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: db)

    assert consolidator.has_pending_revision("User") is False


def test_missing_db_is_safe(tmp_path, monkeypatch):
    # Fully defensive: no DB file -> False, never raises, never creates the store.
    missing = tmp_path / "does_not_exist.db"
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: missing)

    assert consolidator.has_pending_revision("User's favorite movie") is False
    assert not missing.exists()


def test_blank_subject_is_safe(tmp_path, monkeypatch):
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: tmp_path / "x.db")
    assert consolidator.has_pending_revision("") is False
    assert consolidator.has_pending_revision("   ") is False


# ══════════════════════════════════════════════════════════════════════════════
# 3. Router guard — defensive delegation to the consolidator.
# ══════════════════════════════════════════════════════════════════════════════
def test_router_guard_detects_pending_preference(tmp_path, monkeypatch):
    db = tmp_path / "graph.db"
    _seed_triples(db, [("User's favorite movie", "be", "Avatar", 0)])
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: db)
    monkeypatch.setattr(
        consolidator, "open_connection",
        lambda path, **kw: sqlite3.connect(str(db), **kw),
    )

    assert knowledge_router._has_pending_supersession(_FakeNode("User's favorite movie")) is True


def test_router_guard_false_for_clean_subject(tmp_path, monkeypatch):
    db = tmp_path / "graph.db"
    _seed_triples(db, [("User's favorite movie", "be", "Avatar", 1)])
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: db)

    assert knowledge_router._has_pending_supersession(_FakeNode("User's favorite movie")) is False


def test_router_guard_false_without_subject(tmp_path, monkeypatch):
    monkeypatch.setattr(consolidator, "_raw_triples_db_path", lambda: tmp_path / "x.db")
    assert knowledge_router._has_pending_supersession(_FakeNode("")) is False


if __name__ == "__main__":  # pragma: no cover - standalone convenience
    sys.exit(pytest.main([__file__, "-v"]))
