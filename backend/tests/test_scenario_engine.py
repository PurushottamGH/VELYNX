"""Tests for backend.cognition.scenario_engine — Layer 3 scenario parser."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

# ── helpers ──────────────────────────────────────────────────────────────

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
    "love": {
        "core": "Love is deep affection and care.",
        "definition": "Love is deep affection and care.",
    },
    "shame": {
        "core": "Shame is the painful feeling of having failed or been wrong.",
        "definition": "Shame is the painful feeling of having failed or been wrong.",
    },
    "identity": {
        "core": "Identity is the sense of self — who you are.",
        "definition": "Identity is the sense of self — who you are.",
    },
    "failure": {
        "core": "Failure is when a system or person does not meet expectations.",
        "definition": "Failure is when a system or person does not meet expectations.",
    },
}


@pytest.fixture(autouse=True)
def _isolate_soul_path(monkeypatch, tmp_path):
    """Isolate SOUL_PATH to a temp concepts file."""
    test_concepts = tmp_path / "concepts.json"
    test_concepts.write_text(json.dumps(FAKE_CONCEPTS), encoding="utf-8")

    import backend.cognition.scenario_engine as se

    monkeypatch.setattr(se, "SOUL_PATH", test_concepts)


@pytest.fixture(autouse=True)
def _disable_semantic_lookup():
    """Prevent any real embed_index calls."""
    patch("backend.cognition.embed_index.semantic_lookup",
          return_value=[]).start()
    yield


# ── Acceptance criteria ──────────────────────────────────────────────────


class TestAcceptance:
    """Full acceptance criteria for parse_scenario()."""

    def test_acceptance_1_what_is_grief(self):
        """parse_scenario('What is grief?') → direct type, grief concept."""
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario("What is grief?")

        assert result["query_type"] == "direct"
        assert "grief" in result["concepts"]
        assert result["soul_used"] is True

    def test_acceptance_2_forgived_scenario(self):
        """parse_scenario('A man forgaved someone who never apologized') → scenario type, forgiveness concept."""
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario("A man forgaved someone who never apologized")

        assert result["query_type"] == "scenario"
        assert "forgiveness" in result["concepts"]
        assert result["soul_used"] is True

    def test_acceptance_3_relational_query(self):
        """parse_scenario('How does grief relate to hope?') → relational type."""
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario("How does grief relate to hope?")

        assert result["query_type"] == "relational"
        assert "grief" in result["concepts"]
        assert "hope" in result["concepts"]


# ── Query type classification ───────────────────────────────────────────


class TestQueryType:
    """parse_scenario query_type classification."""

    def test_direct_what_is(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("What is grief?")
        assert result["query_type"] == "direct"

    def test_direct_define(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("Define forgiveness")
        assert result["query_type"] == "direct"

    def test_relational_how_does_relate(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("How does grief relate to hope?")
        assert result["query_type"] == "relational"

    def test_relational_and_two_concepts(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("love and betrayal")
        assert result["query_type"] == "relational"

    def test_scenario_deep_felt(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("someone who felt abandoned and alone")
        assert result["query_type"] == "scenario"

    def test_default_direct_fallback(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("random gibberish query")
        assert result["query_type"] == "direct"


# ── Concept activation ──────────────────────────────────────────────────


class TestConceptActivation:
    """Concepts are correctly activated from different input forms."""

    def test_exact_concept_name_in_query(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("grief")
        assert "grief" in result["concepts"]
        assert result["soul_used"] is True

    def test_signal_match_activates_concept(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("I lost everything and felt nothing")
        assert len(result["concepts"]) >= 1
        assert result["soul_used"] is True

    def test_confidence_hint_certain(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("grief")
        assert r["confidence_hint"] == "CERTAIN"

    def test_confidence_hint_low(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("xyzzynonsense")
        assert r["confidence_hint"] == "LOW"

    def test_concepts_limited_to_five(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario(
            "I lost everything, felt alone, betrayed, angry, and afraid")
        assert len(r["concepts"]) <= 5


# ── Emotional arc ───────────────────────────────────────────────────────


class TestEmotionalArc:
    """Arc generation from activated concepts."""

    def test_single_concept_arc(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("grief")
        assert "grief" in r["arc"].lower()

    def test_two_concept_arc(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("grief and hope")
        assert isinstance(r["arc"], str)
        assert len(r["arc"]) > 0

    def test_empty_concepts_arc_empty(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("xyzzynonsense")
        assert r["arc"] == ""


# ── Output structure ────────────────────────────────────────────────────


class TestOutputStructure:
    """Return dict has all expected fields."""

    def test_all_keys_present(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("What is grief?")
        assert "query" in r
        assert "query_type" in r
        assert "concepts" in r
        assert "scores" in r
        assert "arc" in r
        assert "soul_used" in r
        assert "confidence_hint" in r

    def test_query_preserved(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("What is grief?")
        assert r["query"] == "What is grief?"


# ── Failure context triage ──────────────────────────────────────────────


class TestFailureTriage:
    """Dual-routing: personal failure → soul, structural failure → domain."""

    def test_personal_failure_routing(self):
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario(
            "I feel like I'm failing and I doubt myself completely"
        )

        assert result["domain_route"] == "personal"
        assert "shame" in result["concepts"]
        assert "identity" in result["concepts"]

    def test_structural_failure_routing(self):
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario(
            "The production deployment is failing due to a critical bug"
        )

        assert result["domain_route"] == "structural"
        assert "failure" in result["domain_hits"]
        assert "shame" not in result["concepts"]
        assert "identity" not in result["concepts"]

    def test_triage_applied_to_output_structure(self):
        from backend.cognition.scenario_engine import parse_scenario

        r = parse_scenario("I am failing")

        assert "triage" in r
        assert "domain_route" in r
        assert "domain_hits" in r
        assert r["triage"]["route"] == "personal"

    def test_structural_bypasses_soul_arc(self):
        from backend.cognition.scenario_engine import parse_scenario

        r = parse_scenario("The build is failing")

        assert r["domain_route"] == "structural"
        assert "shame" not in r["concepts"]
        assert "identity" not in r["concepts"]
        assert "failure" in r["domain_hits"]

    def test_no_failure_context_no_triage_side_effects(self):
        from backend.cognition.scenario_engine import parse_scenario

        r = parse_scenario("What is grief?")

        assert r["triage"]["route"] == "none"
        assert "grief" in r["concepts"]
        assert r["soul_used"] is True


# ── Cognitive dissonance ────────────────────────────────────────────────


class TestCognitiveDissonance:
    """Detects contradictory emotional states and surfaces them."""

    def test_cognitive_dissonance(self):
        import time
        from backend.knowledge.knowledge_engine import cross_query

        cross_query("warmup")

        t0 = time.perf_counter()
        result = cross_query(
            "I feel incredibly hopeful about the future, "
            "but I am drowning in depression today."
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000

        dissonance = result.get("dissonance_detected")
        assert dissonance is not None, "Expected dissonance to be detected"
        d = dissonance[0] if isinstance(dissonance, list) else dissonance
        assert "hope" in d["concept_a"].lower() or "hope" in d["concept_b"].lower()
        assert "depression" in d["concept_a"].lower() or "depression" in d["concept_b"].lower()
        assert elapsed_ms < 50, f"Execution time {elapsed_ms:.1f}ms exceeds 50ms threshold"
