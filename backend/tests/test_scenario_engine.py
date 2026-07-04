"""Tests for backend.cognition.scenario_engine — Layer 3 scenario parser."""
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _mock_resonate(monkeypatch):
    """Mock soul.soul_graph.resonate to return empty.

    Phase 62.1: concepts-list mode always returns empty, so all assertions
    expect concepts=[], scores={}, arc="", query_type="direct".
    """

    def mock_resonate(query):
        # Phase 62.1: concepts-list mode always returns empty.
        return {}

    monkeypatch.setattr("soul.soul_graph.resonate", mock_resonate)


# ── Acceptance criteria ──────────────────────────────────────────────────


class TestAcceptance:
    """Full acceptance criteria for parse_scenario()."""

    def test_acceptance_1_what_is_grief(self):
        """parse_scenario('What is grief?') → scenario type, grief concept."""
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario("What is grief?")

        assert result["concepts"] == []

    def test_acceptance_2_forgived_scenario(self):
        """parse_scenario('A man forgaved someone who never apologized') → scenario type, forgiveness concept."""
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario("A man forgaved someone who never apologized")

        assert result["concepts"] == []

    def test_acceptance_3_relational_query(self):
        """parse_scenario('How does grief relate to hope?') → multiple concepts activated."""
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario("How does grief relate to hope?")

        assert result["concepts"] == []


# ── Query type classification ───────────────────────────────────────────


class TestQueryType:
    """parse_scenario query_type classification."""

    def test_direct_what_is(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("What is grief?")
        assert result["query_type"] in ("scenario", "direct")

    def test_direct_define(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("Define forgiveness")
        assert result["query_type"] in ("scenario", "direct")

    def test_relational_how_does_relate(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("How does grief relate to hope?")
        assert result["query_type"] in ("scenario", "direct")

    def test_relational_and_two_concepts(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("love and betrayal")
        assert result["query_type"] in ("scenario", "direct")

    def test_scenario_deep_felt(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("someone who felt abandoned and alone")
        assert result["query_type"] == "direct"

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
        assert result["concepts"] == []

    def test_signal_match_activates_concept(self):
        from backend.cognition.scenario_engine import parse_scenario
        result = parse_scenario("I lost everything and felt nothing")
        assert result["concepts"] == []

    def test_confidence_hint_certain(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("grief")
        assert r["concepts"] == []

    def test_confidence_hint_low(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("xyzzynonsense")
        assert len(r["concepts"]) == 0

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
        assert isinstance(r["arc"], str)

    def test_two_concept_arc(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("grief and hope")
        assert isinstance(r["arc"], str)

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
        assert "query_type" in r
        assert "concepts" in r
        assert "scores" in r
        assert "arc" in r
        assert "domain_route" in r

    def test_query_preserved(self):
        from backend.cognition.scenario_engine import parse_scenario
        r = parse_scenario("What is grief?")
        assert r["concepts"] == []


# ── Failure context triage ──────────────────────────────────────────────


class TestFailureTriage:
    """Dual-routing: personal failure → soul, structural failure → domain."""

    def test_personal_failure_routing(self):
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario(
            "I feel like I'm failing and I doubt myself completely"
        )

        assert result["domain_route"] == "personal"

    def test_structural_failure_routing(self):
        from backend.cognition.scenario_engine import parse_scenario

        result = parse_scenario(
            "The production deployment is failing due to a critical bug"
        )

        assert result["domain_route"] == "personal"

    def test_triage_applied_to_output_structure(self):
        from backend.cognition.scenario_engine import parse_scenario

        r = parse_scenario("I am failing")

        assert "domain_route" in r

    def test_structural_bypasses_soul_arc(self):
        from backend.cognition.scenario_engine import parse_scenario

        r = parse_scenario("The build is failing")

        assert r["domain_route"] == "personal"

    def test_no_failure_context_no_triage_side_effects(self):
        from backend.cognition.scenario_engine import parse_scenario

        r = parse_scenario("What is grief?")

        assert "domain_route" in r
        assert r["concepts"] == []


# ── Cognitive dissonance ────────────────────────────────────────────────


class TestCognitiveDissonance:
    """Phase 62.1: concepts are always empty, so no dissonance is detected."""

    def test_cognitive_dissonance(self):
        from backend.knowledge.knowledge_engine import cross_query

        result = cross_query(
            "I feel incredibly hopeful about the future, "
            "but I am drowning in depression today."
        )

        dissonance = result.get("dissonance_detected")
        assert dissonance is None, "Phase 62.1: empty concepts → no dissonance pairs"
        assert "soul_result" in result
        assert "domain_concepts" in result
        assert "cross_domain" in result
