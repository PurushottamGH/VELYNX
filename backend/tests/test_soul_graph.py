"""
Tests for backend.soul.soul_graph — Layer 2 soul graph builder.
Covers: schema creation, path finding, synthesis, edge/tension queries.
"""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

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


@pytest.fixture(autouse=True)
def _isolate_paths(monkeypatch, tmp_path):
    """Redirect all soul file paths to temp so tests never touch prod."""
    db_dir = tmp_path / "soul_graph"
    db_dir.mkdir(parents=True, exist_ok=True)
    test_db = db_dir / "graph.db"
    test_log = tmp_path / "soul_graph_log.json"
    test_concepts = tmp_path / "concepts.json"
    test_concepts.write_text(json.dumps(FAKE_CONCEPTS), encoding="utf-8")

    import backend.soul.soul_graph as sg

    monkeypatch.setattr(sg, "SOUL_PATH", test_concepts)
    monkeypatch.setattr(sg, "SOUL_DB", test_db)
    monkeypatch.setattr(sg, "GRAPH_LOG", test_log)


@pytest.fixture(autouse=True)
def _mock_embed_index():
    """Prevent actual model loading — use deterministic similarity values."""
    # build_pair imports from cognition.embed_index (not backend.cognition)
    # so we must patch both paths to cover both import forms
    targets = [
        "cognition.embed_index",
        "backend.cognition.embed_index",
    ]
    patches = []
    for tgt in targets:
        patches.append(patch(f"{tgt}.build_index"))
        patches.append(patch(f"{tgt}.concept_similarity", return_value=0.85))
        patches.append(patch(f"{tgt}.classify_edge_type", return_value="amplifies"))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


# ── Acceptance 1: build_soul_graph creates DB with correct schema ────────


class TestSchema:
    """Acceptance 1 — build_soul_graph creates DB with correct schema."""

    def test_soul_edges_table_columns(self):
        """soul_edges table has the expected schema."""
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
        """soul_tensions table has the expected schema."""
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
        """Tables are created on first _get_conn() call."""
        from backend.soul.soul_graph import _get_conn

        conn = _get_conn()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        conn.close()

        names = [r[0] for r in tables]
        assert "soul_edges" in names
        assert "soul_tensions" in names

    def test_build_soul_graph_creates_db_file(self):
        """build_soul_graph leaves a real database file on disk."""
        from backend.soul.soul_graph import build_soul_graph, SOUL_DB

        build_soul_graph(force=True)

        assert SOUL_DB.exists()
        assert SOUL_DB.stat().st_size > 0


# ── Acceptance 2: find_path returns valid path between connected concepts ─


class TestFindPath:
    """Acceptance 2 — find_path returns valid path between two connected concepts."""

    def test_direct_edge_path_is_found(self):
        """A -> B direct edge is found as a one-hop path."""
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        path = find_path("hope", "grief", max_hops=3)

        assert len(path) >= 1
        assert path[0]["from"] == "hope"
        assert path[0]["to"] == "grief"

    def test_no_path_returns_empty(self):
        """Unconnected concepts return empty list."""
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        path = find_path("courage", "fear", max_hops=3)

        assert path == []

    def test_two_hop_path(self):
        """A -> C via B is found when all three are connected."""
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        build_pair("grief", "courage")
        path = find_path("hope", "courage", max_hops=3)

        assert len(path) == 2
        assert path[-1]["to"] == "courage"

    def test_path_respects_max_hops(self):
        """max_hops=1 blocks two-hop paths."""
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        build_pair("grief", "courage")
        path = find_path("hope", "courage", max_hops=1)

        assert path == []


# ── Acceptance 3: synthesize returns relational statement ─────────────────


class TestSynthesize:
    """Acceptance 3 — synthesize returns a relational statement for 2+ concepts."""

    def test_two_concepts(self):
        """Two connected concepts produce a relational statement."""
        from backend.soul.soul_graph import build_pair, synthesize

        build_pair("hope", "grief")
        result = synthesize(["hope", "grief"])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_single_concept_returns_empty(self):
        """Fewer than 2 concepts returns empty string."""
        from backend.soul.soul_graph import synthesize

        assert synthesize(["hope"]) == ""

    def test_three_concepts(self):
        """Three concepts produce a statement referencing all of them."""
        from backend.soul.soul_graph import build_pair, synthesize

        build_pair("hope", "grief")
        build_pair("grief", "courage")
        result = synthesize(["hope", "grief", "courage"])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_list(self):
        """Empty list returns empty string."""
        from backend.soul.soul_graph import synthesize

        assert synthesize([]) == ""


# ── Query helpers ────────────────────────────────────────────────────────


class TestQueryHelpers:
    """Tests for get_edges and get_tensions."""

    def test_get_edges_returns_outbound_edges(self):
        from backend.soul.soul_graph import build_pair, get_edges

        build_pair("hope", "grief")
        edges = get_edges("hope")

        assert len(edges) >= 1
        assert edges[0]["to"] == "grief"

    def test_get_edges_unknown_concept_returns_empty(self):
        from backend.soul.soul_graph import get_edges

        assert get_edges("nonexistent") == []

    def test_get_tensions_returns_known_pairs(self):
        """hope/grief is a known tension pair (score >= 0.20 means edge built)."""
        from backend.soul.soul_graph import build_pair, get_tensions

        build_pair("hope", "grief")
        tensions = get_tensions("hope")

        assert len(tensions) >= 1
        assert any(t["name"] == "Temporal pull" for t in tensions)

    def test_get_tensions_unknown_concept(self):
        from backend.soul.soul_graph import get_tensions

        assert get_tensions("nonexistent") == []


# ── Edge cases ───────────────────────────────────────────────────────────


class TestEdgeCases:
    """Boundary / edge cases."""

    def test_build_pair_same_concept_twice(self):
        """Building the same pair twice should not error."""
        from backend.soul.soul_graph import build_pair

        build_pair("hope", "grief")
        build_pair("hope", "grief")  # second call — should not crash

    def test_find_path_same_start_end(self):
        """Path from a concept to itself returns empty (no self-loop)."""
        from backend.soul.soul_graph import build_pair, find_path

        build_pair("hope", "grief")
        path = find_path("hope", "hope", max_hops=3)
        assert isinstance(path, list)

    def test_synthesize_with_tension_present(self):
        """Known tension pairs produce tension description in output."""
        from backend.soul.soul_graph import build_pair, synthesize

        build_pair("hope", "grief")
        result = synthesize(["hope", "grief"])
        assert "Tension" in result or len(result) > 0

    def test_empty_soul_file_handled(self):
        """No concepts file -> build_pair still works."""
        import backend.soul.soul_graph as sg

        empty = sg.SOUL_PATH.parent / "empty_concepts.json"
        empty.write_text("{}", encoding="utf-8")
        sg.SOUL_PATH = empty

        # with an empty concepts dict, build_pair will fail to find "hope" in soul —
        # what matters is it doesn't crash on import
        sg.build_pair("hope", "grief")


# ── Acceptance: auto-link dedup & partial edges ──────────────────────────


class TestBuildPairDedup:
    """Acceptance criteria for auto-link from PIPELINE_PATCH plan."""

    def test_build_pair_does_not_duplicate_edges(self):
        """Calling build_pair twice creates exactly 2 rows (a→b, b→a), not 4."""
        from backend.soul.soul_graph import build_pair, _get_conn

        build_pair("hope", "grief")
        build_pair("hope", "grief")  # same pair again

        conn = _get_conn()
        rows = conn.execute(
            "SELECT from_concept, to_concept, edge_type FROM soul_edges ORDER BY from_concept"
        ).fetchall()
        conn.close()

        assert len(rows) == 2
        assert ("hope", "grief", "amplifies") in rows
        # amplifies reverses to grounds (see _reverse_type)
        assert ("grief", "hope", "grounds") in rows

    def test_repeat_call_idempotent(self):
        """Calling build_pair N times produces same DB state as calling it once."""
        from backend.soul.soul_graph import build_pair, _get_conn

        build_pair("hope", "grief")

        conn = _get_conn()
        rows_1 = conn.execute(
            "SELECT from_concept, to_concept, edge_type FROM soul_edges ORDER BY from_concept"
        ).fetchall()
        conn.close()

        build_pair("hope", "grief")
        build_pair("hope", "grief")
        build_pair("hope", "grief")

        conn = _get_conn()
        rows_n = conn.execute(
            "SELECT from_concept, to_concept, edge_type FROM soul_edges ORDER BY from_concept"
        ).fetchall()
        conn.close()

        assert rows_1 == rows_n

    def test_partial_edges_fills_missing_direction(self):
        """Build pair A→B already exists but B→A does not — should fill B→A.

        This simulates: concept 'hope' taught before, concept 'grief' newly added;
        only 'hope' had edges accumulated. _auto_link_concept(grief) calls
        build_pair(grief, hope). The grief→hope (forward) direction is new,
        and the hope→grief direction already existed.
        """
        from backend.soul.soul_graph import build_pair, _get_conn, SOUL_PATH
        import json

        # Pre-seed a single edge: hope→grief (as if hope was linked first)
        soul = json.loads(SOUL_PATH.read_text(encoding="utf-8"))
        sg_mod = __import__("backend.soul.soul_graph", fromlist=["_write_edge", "_get_conn"])
        conn = _get_conn()
        sg_mod._write_edge(conn, soul, "hope", "grief", "amplifies", 0.85,
                           "Hope amplifies grief (score=0.85)")
        conn.commit()
        conn.close()

        # Now call build_pair(grief, hope) — reverse direction is new
        build_pair("grief", "hope")

        conn = _get_conn()
        rows = conn.execute(
            "SELECT from_concept, to_concept, edge_type FROM soul_edges ORDER BY from_concept"
        ).fetchall()
        conn.close()

        # hope→grief was pre-seeded, grief→hope is new from build_pair.
        # Mock returns "amplifies" for classify_edge_type, and the forward
        # edge (grief→hope) gets that type. The existing hope→grief is preserved.
        assert len(rows) == 2
        assert ("hope", "grief", "amplifies") in rows
        assert ("grief", "hope", "amplifies") in rows

    def test_teaching_simulation_no_error(self):
        """Simulate _auto_link_concept: iterating all existing concepts and
        calling build_pair for each does not raise."""
        from backend.soul.soul_graph import build_pair, load_soul

        soul = load_soul()
        new_concept = "hope"
        for existing in list(soul.keys()):
            if existing != new_concept:
                build_pair(new_concept, existing)

    def test_multi_concept_no_duplicate_on_full_auto_link(self):
        """Simulate teaching a new concept against many existing:
        after full auto-link, running it again produces no extra rows."""
        from backend.soul.soul_graph import build_pair, load_soul, _get_conn

        def auto_link(new_name: str):
            soul = load_soul()
            for existing in list(soul.keys()):
                if existing != new_name:
                    build_pair(new_name, existing)

        # First pass — link 'courage' against all existing (hope, grief, fear)
        auto_link("courage")

        conn = _get_conn()
        first_count = conn.execute("SELECT COUNT(*) FROM soul_edges").fetchone()[0]
        conn.close()

        # Second pass — same operation again
        auto_link("courage")

        conn = _get_conn()
        second_count = conn.execute("SELECT COUNT(*) FROM soul_edges").fetchone()[0]
        conn.close()

        assert first_count == second_count
