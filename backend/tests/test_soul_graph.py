"""
Tests for backend.soul.soul_graph — Layer 2 soul graph builder.

Phase 62 unification: ``build_pair`` now writes into the unified
``living_edges`` Brain Stem store (brain_stem.db) — the SAME table the read
path (``get_edges`` / ``find_path`` / ``get_tensions`` / ``synthesize``)
queries. Before the fix it wrote to a standalone ``soul_edges`` table that the
readers never consulted, so auto-linked edges were permanently invisible. These
tests pin the unified contract.

Isolation
---------
``VELYNX_TEST_MODE=1`` (set below before any source import) redirects every
SQLite database — including brain_stem.db — into
``backend/tests/data/_isolated/`` via backend.memory._sqlite.resolve_db_path,
so the suite never touches live user data. Each test wipes the isolated
brain_stem.db so edge-count assertions are deterministic.
"""
import os

# MUST be set before importing any backend module that resolves a DB path.
os.environ.setdefault("VELYNX_TEST_MODE", "1")

import sys
import json
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure backend/ is importable as a top-level root so the source's
# ``from cognition.embed_index import ...`` (and our patch of the
# ``backend.cognition.embed_index`` fallback) both resolve.
_BACKEND_ROOT = str(Path(__file__).resolve().parent.parent)
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)


# ── helpers ──────────────────────────────────────────────────────────────

FAKE_CONCEPTS = {
    "hope": {
        "core": "Hope is the quiet conviction that things can get better.",
        "definition": "Hope is the quiet conviction that things can get better.",
    },
    "grief": {
        "core": "Grief is the deep sorrow from loss.",
        "definition": "Grief is the deep sorrow from loss.",
    },
    "courage": {
        "core": "Courage is acting despite fear.",
        "definition": "Courage is acting despite fear.",
    },
    "fear": {
        "core": "Fear is the anticipation of harm or danger.",
        "definition": "Fear is the anticipation of harm or danger.",
    },
}


def _isolated_brain_stem_path() -> Path:
    """Resolve the redirected brain_stem.db path under VELYNX_TEST_MODE."""
    from backend.memory._sqlite import canonical_db_path, resolve_db_path
    return Path(resolve_db_path(canonical_db_path("brain_stem.db")))


def _wipe_brain_stem():
    """Reset the isolated Brain Stem to an empty state.

    We TRUNCATE the tables rather than unlink the file: under WAL mode the
    committed data lives partly in the ``-wal`` sidecar, so deleting only the
    main ``.db`` can leave rows that SQLite replays on the next open. Clearing
    every table via SQL is deterministic and avoids cross-test state leakage.
    """
    from velynx.graph.living_edges import initialize_schema
    from backend.soul.soul_graph import get_db_connection

    initialize_schema()
    conn = get_db_connection()
    try:
        for table in ("edge_evidence", "living_edges",
                      "coactivation_counts", "concepts"):
            try:
                conn.execute(f"DELETE FROM {table}")
            except Exception:
                pass  # table may not exist on a brand-new DB
        conn.commit()
        # Force a full WAL checkpoint so the truncation is flushed from the
        # -wal sidecar into the main DB and is unconditionally visible to every
        # subsequent fresh connection (each add_living_edge / get_edges call
        # opens its own). Without this, WAL snapshot isolation can let a later
        # test observe pre-wipe rows, leaking state across tests.
        try:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except Exception:
            pass
    finally:
        conn.close()


@pytest.fixture(autouse=True)
def _isolate_paths(monkeypatch, tmp_path):
    """Redirect the soul concepts file to temp and reset the Brain Stem DB.

    The brain_stem.db itself is already redirected into the isolated test dir
    by VELYNX_TEST_MODE; we wipe it per-test so edge-count assertions start from
    empty. SOUL_PATH (the concepts JSON read by _generate_reason / load_soul) is
    pointed at a temp fixture file.
    """
    test_concepts = tmp_path / "concepts.json"
    test_concepts.write_text(json.dumps(FAKE_CONCEPTS), encoding="utf-8")

    import backend.soul.soul_graph as sg

    monkeypatch.setattr(sg, "SOUL_PATH", test_concepts)

    _wipe_brain_stem()
    # Create the unified schema fresh.
    from velynx.graph.living_edges import initialize_schema
    initialize_schema()
    yield
    _wipe_brain_stem()


@pytest.fixture(autouse=True)
def _mock_embed_index():
    """Prevent real model loading — deterministic similarity / edge typing.

    The source imports ``from cognition.embed_index import ...`` with a
    ``backend.cognition.embed_index`` fallback. With backend/ on sys.path these
    resolve to TWO DISTINCT module objects (top-level ``cognition`` package vs
    the ``backend.cognition`` package), so we must patch BOTH names — patching
    only one leaves the other (the one build_pair actually binds) using the real
    model. A similarity of 0.85 is comfortably above the 0.20 relational floor,
    so build_pair always writes an edge, and classify_edge_type is pinned to
    'amplifies' (reverse 'grounds') for deterministic relation assertions.
    """
    targets = ["cognition.embed_index", "backend.cognition.embed_index"]
    patches = []
    for tgt in targets:
        try:
            __import__(tgt)
        except Exception:
            continue
        patches.append(patch(f"{tgt}.build_index"))
        patches.append(patch(f"{tgt}.concept_similarity", return_value=0.85))
        patches.append(patch(f"{tgt}.classify_edge_type", return_value="amplifies"))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


# ── Acceptance 1: legacy soul_edges schema still provisioned ─────────────


class TestSchema:
    """The legacy ``soul_edges`` / ``soul_tensions`` schema is retained for
    build_soul_graph() and the migrate_flat_edges() legacy-import path. Its
    creation contract (via _get_conn) is unchanged by the unification."""

    def test_soul_edges_table_columns(self):
        from backend.soul.soul_graph import _get_conn

        conn = _get_conn()
        c = conn.execute("PRAGMA table_info(soul_edges)")
        cols = {row[1]: row[2] for row in c.fetchall()}
        conn.close()

        assert "id" in cols
        assert "from_concept" in cols
        assert "to_concept" in cols
        assert "edge_type" in cols
        assert "weight" in cols
        assert "reason" in cols
        assert "source" in cols
        assert "created_at" in cols

    def test_soul_tensions_table_columns(self):
        from backend.soul.soul_graph import _get_conn

        conn = _get_conn()
        c = conn.execute("PRAGMA table_info(soul_tensions)")
        cols = {row[1]: row[2] for row in c.fetchall()}
        conn.close()

        assert "id" in cols
        assert "concept_a" in cols
        assert "concept_b" in cols
        assert "name" in cols
        assert "description" in cols
        assert "severity" in cols
        assert "created_at" in cols

    def test_tables_created_on_first_connect(self):
        from backend.soul.soul_graph import _get_conn

        conn = _get_conn()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        conn.close()

        names = [r[0] for r in tables]
        assert "soul_edges" in names
        assert "soul_tensions" in names

    def test_living_edges_schema_present(self):
        """The unified Brain Stem ``living_edges`` table — the write+read target
        after unification — exists with its key columns."""
        from backend.soul.soul_graph import get_db_connection

        conn = get_db_connection()
        cols = {row[1] for row in conn.execute("PRAGMA table_info(living_edges)")}
        conn.close()

        for expected in ("source", "relation", "target",
                         "asymptotic_weight", "status", "confidence"):
            assert expected in cols, f"living_edges missing column {expected!r}"


# ── Acceptance 2: build_pair writes to the unified store readers query ───


class TestWriteReadUnification:
    """The core regression fix: edges written by build_pair MUST be visible to
    the readers (they previously wrote to a table no reader consulted)."""

    def test_build_pair_is_visible_to_get_edges(self):
        from backend.soul.soul_graph import build_pair, get_edges

        build_pair("hope", "grief")
        edges = get_edges("hope")

        assert len(edges) >= 1, "build_pair edge invisible to get_edges (unification broken)"
        assert any(e["target"] == "grief" for e in edges)

    def test_build_pair_writes_both_directions(self):
        from backend.soul.soul_graph import build_pair, get_edges

        build_pair("hope", "grief")
        assert any(e["target"] == "grief" for e in get_edges("hope"))
        assert any(e["target"] == "hope" for e in get_edges("grief"))

    def test_edges_land_in_living_edges_table(self):
        from backend.soul.soul_graph import build_pair, get_db_connection

        build_pair("hope", "grief")

        conn = get_db_connection()
        rows = conn.execute(
            "SELECT source, target, relation, status FROM living_edges "
            "WHERE relation != 'tension' ORDER BY source"
        ).fetchall()
        conn.close()

        pairs = {(r[0], r[1]) for r in rows}
        assert ("hope", "grief") in pairs
        assert ("grief", "hope") in pairs
        # Mock returns 'amplifies'; reverse is 'grounds' (see _reverse_type).
        by_dir = {(r[0], r[1]): r[2] for r in rows}
        assert by_dir[("hope", "grief")] == "amplifies"
        assert by_dir[("grief", "hope")] == "grounds"
        # Semantic edges remain active so the readers traverse them.
        assert all(r[3] == "active" for r in rows)


# ── Acceptance 3: find_path returns valid path between connected concepts ─


class TestFindPath:
    """find_path traverses the unified living_edges graph and returns a node
    list (list[str]) — start ... end."""

    def test_direct_edge_path_is_found(self):
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        path = find_path("hope", "grief", max_hops=3)

        assert path[0] == "hope"
        assert path[-1] == "grief"

    def test_no_path_returns_empty(self):
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        # courage/fear were never linked -> no path
        path = find_path("courage", "fear", max_hops=3)

        assert path == []

    def test_two_hop_path(self):
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        build_pair("grief", "courage")
        path = find_path("hope", "courage", max_hops=3)

        assert path[0] == "hope"
        assert path[-1] == "courage"
        assert "grief" in path  # the bridging node

    def test_path_respects_max_hops(self):
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        build_pair("grief", "courage")
        path = find_path("hope", "courage", max_hops=1)

        assert path == []


# ── Acceptance 4: synthesize returns relational statement ─────────────────


class TestSynthesize:
    def test_two_concepts(self):
        from backend.soul.soul_graph import build_pair, synthesize

        build_pair("hope", "grief")
        result = synthesize(["hope", "grief"])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_single_concept_returns_empty(self):
        from backend.soul.soul_graph import synthesize

        assert synthesize(["hope"]) == ""

    def test_three_concepts(self):
        from backend.soul.soul_graph import build_pair, synthesize

        build_pair("hope", "grief")
        build_pair("grief", "courage")
        result = synthesize(["hope", "grief", "courage"])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_list(self):
        from backend.soul.soul_graph import synthesize

        assert synthesize([]) == ""


# ── Query helpers ────────────────────────────────────────────────────────


class TestQueryHelpers:
    """get_edges / get_tensions over the unified living_edges store."""

    def test_get_edges_returns_outbound_edges(self):
        from backend.soul.soul_graph import build_pair, get_edges

        build_pair("hope", "grief")
        edges = get_edges("hope")

        assert len(edges) >= 1
        assert any(e["target"] == "grief" for e in edges)

    def test_get_edges_unknown_concept_returns_empty(self):
        from backend.soul.soul_graph import get_edges

        assert get_edges("nonexistent") == []

    def test_get_tensions_returns_known_pairs(self):
        """hope/grief is a known semantic tension ('Temporal pull'). build_pair
        records it as a contested 'tension' edge surfaced by get_tensions."""
        from backend.soul.soul_graph import build_pair, get_tensions

        build_pair("hope", "grief")
        tensions = get_tensions("hope")

        assert len(tensions) >= 1
        assert any(t["context"] == "Temporal pull" for t in tensions)
        # Tension edges are contested (kept distinct from active semantic edges).
        assert all(t["relation"] == "tension" for t in tensions)

    def test_get_tensions_unknown_concept(self):
        from backend.soul.soul_graph import get_tensions

        assert get_tensions("nonexistent") == []

    def test_tension_edges_excluded_from_get_edges(self):
        """A contested tension edge must NOT appear in get_edges (active-only)."""
        from backend.soul.soul_graph import build_pair, get_edges

        build_pair("hope", "grief")
        edges = get_edges("hope")

        assert all(e["relation"] != "tension" for e in edges)


# ── Edge cases ───────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_build_pair_same_concept_twice(self):
        from backend.soul.soul_graph import build_pair

        build_pair("hope", "grief")
        build_pair("hope", "grief")  # second call — should not crash

    def test_find_path_same_start_end(self):
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        path = find_path("hope", "hope", max_hops=3)
        assert isinstance(path, list)

    def test_synthesize_with_tension_present(self):
        from backend.soul.soul_graph import build_pair, synthesize

        build_pair("hope", "grief")
        result = synthesize(["hope", "grief"])
        assert "Tension" in result or len(result) > 0

    def test_empty_soul_file_handled(self):
        """No concepts file -> build_pair still works (writes edges regardless,
        reasons just fall back to bare concept names)."""
        import backend.soul.soul_graph as sg

        empty = Path(sg.SOUL_PATH).parent / "empty_concepts.json"
        empty.write_text("{}", encoding="utf-8")
        sg.SOUL_PATH = empty

        sg.build_pair("hope", "grief")  # must not crash


# ── Acceptance: auto-link dedup & partial edges (idempotency) ────────────


class TestBuildPairDedup:
    """build_pair is idempotent against the unified living_edges store."""

    def test_build_pair_does_not_duplicate_edges(self):
        """Two calls create exactly 2 semantic rows (a→b, b→a), not 4."""
        from backend.soul.soul_graph import build_pair, get_db_connection

        build_pair("hope", "grief")
        build_pair("hope", "grief")  # same pair again

        conn = get_db_connection()
        rows = conn.execute(
            "SELECT source, target, relation FROM living_edges "
            "WHERE relation != 'tension' ORDER BY source"
        ).fetchall()
        conn.close()

        assert len(rows) == 2
        assert ("hope", "grief", "amplifies") in [tuple(r) for r in rows]
        # amplifies reverses to grounds (see _reverse_type)
        assert ("grief", "hope", "grounds") in [tuple(r) for r in rows]

    def test_repeat_call_idempotent(self):
        """Calling build_pair N times == calling it once (same DB state)."""
        from backend.soul.soul_graph import build_pair, get_db_connection

        def _snapshot():
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT source, target, relation, status FROM living_edges "
                "ORDER BY source, target, relation"
            ).fetchall()
            conn.close()
            return [tuple(r) for r in rows]

        build_pair("hope", "grief")
        rows_1 = _snapshot()

        build_pair("hope", "grief")
        build_pair("hope", "grief")
        build_pair("hope", "grief")
        rows_n = _snapshot()

        assert rows_1 == rows_n

    def test_teaching_simulation_no_error(self):
        """Simulate teach.py _auto_link_concept: link a new concept against all
        existing concepts. Must not raise."""
        from backend.soul.soul_graph import build_pair, load_soul

        soul = load_soul()
        new_concept = "hope"
        for existing in list(soul.keys()):
            if existing != new_concept:
                build_pair(new_concept, existing)

    def test_multi_concept_no_duplicate_on_full_auto_link(self):
        """After a full auto-link pass, repeating it adds no extra rows."""
        from backend.soul.soul_graph import build_pair, load_soul, get_db_connection

        def auto_link(new_name: str):
            soul = load_soul()
            for existing in list(soul.keys()):
                if existing != new_name:
                    build_pair(new_name, existing)

        def _count():
            conn = get_db_connection()
            n = conn.execute("SELECT COUNT(*) FROM living_edges").fetchone()[0]
            conn.close()
            return n

        auto_link("courage")
        first_count = _count()

        auto_link("courage")
        second_count = _count()

        assert first_count == second_count
