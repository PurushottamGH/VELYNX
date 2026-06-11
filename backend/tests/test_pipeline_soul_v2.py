"""Tests for _soul_lookup in app.pipeline — V2 soul pipeline integration (primary lookup)."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

# ── Fixtures ─────────────────────────────────────────────────────────────

FAKE_CONCEPTS = {
    "grief": {
        "core": "Grief is the deep sorrow from loss.",
        "definition": "Grief is the deep sorrow from loss.",
    },
    "hope": {
        "core": "Hope is the quiet conviction that things can get better.",
        "definition": "Hope is the quiet conviction that things can get better.",
    },
    "forgiveness": {
        "core": "Forgiveness is releasing the need for revenge.",
        "definition": "Forgiveness is releasing the need for revenge.",
    },
}

FAKE_SCENARIO_RESPONSE = {
    "query": "What is grief?",
    "query_type": "direct",
    "concepts": ["grief"],
    "scores": {"grief": 1.0},
    "arc": "This activates grief",
    "soul_used": True,
    "confidence_hint": "CERTAIN",
}

FAKE_SCENARIO_RELATIONAL = {
    "query": "How does grief relate to hope?",
    "query_type": "relational",
    "concepts": ["grief", "hope"],
    "scores": {"grief": 1.0, "hope": 0.8},
    "arc": "Grief and hope are in tension: both true at once",
    "soul_used": True,
    "confidence_hint": "CERTAIN",
}

FAKE_SCENARIO_SCENARIO = {
    "query": "A man forgaved someone who never apologized",
    "query_type": "scenario",
    "concepts": ["forgiveness"],
    "scores": {"forgiveness": 0.9},
    "arc": "This activates forgiveness",
    "soul_used": True,
    "confidence_hint": "CERTAIN",
}

FAKE_SCENARIO_NO_CONCEPTS = {
    "query": "xyzzynonsense",
    "query_type": "direct",
    "concepts": [],
    "scores": {},
    "arc": "",
    "soul_used": False,
    "confidence_hint": "LOW",
}


@pytest.fixture(autouse=True)
def _mock_deps_and_path(tmp_path, monkeypatch):
    """Mock inline imports + set SOUL_PATH."""
    test_concepts = tmp_path / "concepts.json"
    test_concepts.write_text(json.dumps(FAKE_CONCEPTS), encoding="utf-8")

    # Patch source modules that _soul_lookup_v2 imports inline
    patcher_ps = patch("cognition.scenario_engine.parse_scenario")
    patcher_syn = patch("soul.soul_graph.synthesize", return_value="Grief grounds hope.")
    patcher_edges = patch("soul.soul_graph.get_edges", return_value=[])
    patcher_tens = patch("soul.soul_graph.get_tensions", return_value=[])

    mock_parse_scenario = patcher_ps.start()
    patcher_syn.start()
    patcher_edges.start()
    patcher_tens.start()

    import app.pipeline as pipeline
    monkeypatch.setattr(pipeline, "SOUL_PATH", test_concepts)

    yield mock_parse_scenario  # give tests the mock to configure

    patcher_ps.stop()
    patcher_syn.stop()
    patcher_edges.stop()
    patcher_tens.stop()


# ── Acceptance criteria ──────────────────────────────────────────────────


class TestAcceptance:
    """AC 1–3 for _soul_lookup_v2."""

    def test_direct_query_returns_definition(self, _mock_deps_and_path):
        """AC1: Direct query returns a definition string."""
        _mock_deps_and_path.return_value = FAKE_SCENARIO_RESPONSE
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("What is grief?")

        assert result is not None
        assert "answer" in result
        assert result["concepts"] == ["grief"]
        assert result["v2"] is True
        assert "Grief is the deep sorrow" in result["answer"]

    def test_scenario_query_returns_arc(self, _mock_deps_and_path):
        """AC2: Scenario/relational query returns an emotional arc."""
        _mock_deps_and_path.return_value = FAKE_SCENARIO_RELATIONAL
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("How does grief relate to hope?")

        assert result is not None
        assert result["answer"] == "Grief and hope are in tension: both true at once"

    def test_nonsoul_query_returns_none(self, _mock_deps_and_path):
        """AC3: Non-soul query returns None — existing pipeline unchanged."""
        _mock_deps_and_path.return_value = FAKE_SCENARIO_NO_CONCEPTS
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("What is the capital of France?")

        assert result is None


# ── Query type routing ──────────────────────────────────────────────────


class TestTypeRouting:
    """_soul_lookup_v2 routes correctly by query_type."""

    def test_direct_single_concept_uses_definition(self, _mock_deps_and_path):
        _mock_deps_and_path.return_value = {**FAKE_SCENARIO_RESPONSE, "query_type": "direct", "concepts": ["grief"]}
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("What is grief?")
        assert "Grief is the deep sorrow" in result["answer"]

    def test_direct_multi_concept_falls_to_arc(self, _mock_deps_and_path):
        _mock_deps_and_path.return_value = {**FAKE_SCENARIO_RESPONSE, "query_type": "direct", "concepts": ["grief", "hope"]}
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("grief hope")
        assert result["answer"]

    def test_relational_uses_arc(self, _mock_deps_and_path):
        _mock_deps_and_path.return_value = {**FAKE_SCENARIO_RELATIONAL, "query_type": "relational"}
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("How does grief relate to hope?")
        assert result["answer"] == "Grief and hope are in tension: both true at once"

    def test_scenario_uses_arc(self, _mock_deps_and_path):
        _mock_deps_and_path.return_value = {**FAKE_SCENARIO_SCENARIO, "query_type": "scenario", "concepts": ["forgiveness"]}
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("A man forgaved someone")
        assert result["answer"] == "This activates forgiveness"

    def test_empty_arc_falls_back_to_synthesize(self, _mock_deps_and_path):
        _mock_deps_and_path.return_value = {**FAKE_SCENARIO_RELATIONAL, "query_type": "relational", "arc": ""}
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("grief hope")
        assert "grounds" in result["answer"]

    def test_missing_soul_file_returns_none(self, _mock_deps_and_path, tmp_path):
        import app.pipeline as pipeline
        pipeline.SOUL_PATH = tmp_path / "nonexistent.json"
        _mock_deps_and_path.return_value = FAKE_SCENARIO_RESPONSE

        result = pipeline._soul_lookup("What is grief?")
        assert result is None


# ── Edge cases ──────────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases for _soul_lookup_v2."""

    def test_no_concepts_returns_none(self, _mock_deps_and_path):
        _mock_deps_and_path.return_value = FAKE_SCENARIO_NO_CONCEPTS
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("xyzzynonsense")
        assert result is None

    def test_v2_flag_on_result(self, _mock_deps_and_path):
        _mock_deps_and_path.return_value = FAKE_SCENARIO_RESPONSE
        import app.pipeline as pipeline

        result = pipeline._soul_lookup("What is grief?")
        assert result["v2"] is True
