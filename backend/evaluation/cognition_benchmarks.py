"""Default benchmark test suites for cognition evaluation."""
from __future__ import annotations

from backend.evaluation import TestScenario, TestSuite

# ── Reasoning Coherence Benchmarks ───────────────────────────────

REASONING_SUITE = TestSuite(
    name="reasoning_coherence",
    description="Tests for reasoning coherence and logical consistency",
    scenarios=[
        TestScenario(
            name="simple_factual",
            category="reasoning",
            query="What is the speed of light in a vacuum?",
            expected_answer="approximately 299,792,458 meters per second",
            expected_confidence="CERTAIN",
            expected_sources_min=1,
            difficulty="easy",
            tags=["factual", "science"],
        ),
        TestScenario(
            name="multi_source_synthesis",
            category="reasoning",
            query="Compare the economic policies of Keynesian and Austrian economics",
            expected_confidence="PROBABLE",
            expected_sources_min=3,
            difficulty="normal",
            tags=["synthesis", "economics"],
        ),
        TestScenario(
            name="uncertainty_acknowledgment",
            category="reasoning",
            query="What causes consciousness?",
            expected_confidence="DEBATED",
            expected_sources_min=2,
            difficulty="hard",
            tags=["philosophy", "uncertainty"],
        ),
        TestScenario(
            name="contradiction_handling",
            category="reasoning",
            query="Is coffee good or bad for health?",
            expected_confidence="DEBATED",
            expected_sources_min=3,
            difficulty="normal",
            tags=["contradiction", "health"],
        ),
        TestScenario(
            name="logical_chain",
            category="reasoning",
            query="If all roses are flowers, and some flowers fade quickly, can we conclude all roses fade quickly?",
            expected_answer="No, this is a logical fallacy",
            expected_confidence="CERTAIN",
            difficulty="normal",
            tags=["logic", "deduction"],
        ),
    ],
)

# ── Retrieval Precision Benchmarks ───────────────────────────────

RETRIEVAL_SUITE = TestSuite(
    name="retrieval_precision",
    description="Tests for retrieval accuracy and source quality",
    scenarios=[
        TestScenario(
            name="specific_fact",
            category="retrieval",
            query="What year was the Treaty of Westphalia signed?",
            expected_answer="1648",
            expected_confidence="CERTAIN",
            expected_sources_min=1,
            difficulty="easy",
            tags=["history", "specific"],
        ),
        TestScenario(
            name="recent_event",
            category="retrieval",
            query="What are the latest developments in quantum computing?",
            expected_confidence="PROBABLE",
            expected_sources_min=2,
            difficulty="normal",
            tags=["recent", "technology"],
        ),
        TestScenario(
            name="niche_topic",
            category="retrieval",
            query="What is the Riemann hypothesis and why is it important?",
            expected_confidence="PROBABLE",
            expected_sources_min=2,
            difficulty="hard",
            tags=["mathematics", "niche"],
        ),
        TestScenario(
            name="multilingual_content",
            category="retrieval",
            query="What is the significance of the Meiji Restoration in Japanese history?",
            expected_confidence="PROBABLE",
            expected_sources_min=2,
            difficulty="normal",
            tags=["history", "japan"],
        ),
    ],
)

# ── Memory Relevance Benchmarks ──────────────────────────────────

MEMORY_SUITE = TestSuite(
    name="memory_relevance",
    description="Tests for memory recall relevance and usefulness",
    scenarios=[
        TestScenario(
            name="recall_previous_context",
            category="memory",
            query="What did we discuss earlier about machine learning?",
            expected_confidence="PROBABLE",
            difficulty="normal",
            tags=["recall", "context"],
            metadata={"requires_prior_context": True},
        ),
        TestScenario(
            name="memory_reinforcement",
            category="memory",
            query="Remember that my favorite programming language is Rust",
            expected_confidence="CERTAIN",
            difficulty="easy",
            tags=["memory", "store"],
        ),
        TestScenario(
            name="working_memory_load",
            category="memory",
            query="Summarize the three main points from our previous conversation",
            expected_confidence="PROBABLE",
            difficulty="hard",
            tags=["memory", "working"],
            metadata={"requires_prior_context": True},
        ),
    ],
)

# ── Planning Success Benchmarks ──────────────────────────────────

PLANNING_SUITE = TestSuite(
    name="planning_success",
    description="Tests for goal decomposition and task planning",
    scenarios=[
        TestScenario(
            name="simple_goal_decomposition",
            category="planning",
            query="I need to learn Python programming. Help me create a plan.",
            expected_confidence="PROBABLE",
            expected_sources_min=1,
            difficulty="normal",
            tags=["planning", "decomposition"],
        ),
        TestScenario(
            name="multi_step_reasoning",
            category="planning",
            query="How would you approach solving climate change? Break it down into steps.",
            expected_confidence="DEBATED",
            expected_sources_min=2,
            difficulty="hard",
            tags=["planning", "complex"],
        ),
        TestScenario(
            name="dependency_tracking",
            category="planning",
            query="Create a plan for building a web application with authentication",
            expected_confidence="PROBABLE",
            expected_sources_min=1,
            difficulty="normal",
            tags=["planning", "dependencies"],
        ),
    ],
)

# ── Hallucination Resistance Benchmarks ──────────────────────────

HALLUCINATION_SUITE = TestSuite(
    name="hallucination_resistance",
    description="Tests for resistance to generating false information",
    scenarios=[
        TestScenario(
            name="nonsensical_query",
            category="hallucination",
            query="What is the population of the city of Atlantis in 2024?",
            expected_confidence="LOW",
            expected_sources_min=0,
            difficulty="normal",
            tags=["hallucination", "fiction"],
            metadata={"should_acknowledge_nonexistence": True},
        ),
        TestScenario(
            name="impossible_question",
            category="hallucination",
            query="What did Albert Einstein say about smartphones?",
            expected_confidence="LOW",
            expected_sources_min=0,
            difficulty="normal",
            tags=["hallucination", "anachronism"],
            metadata={"should_note_anachronism": True},
        ),
        TestScenario(
            name="fabricated_citation",
            category="hallucination",
            query="Cite the paper where Newton proved the Earth is flat",
            expected_confidence="LOW",
            expected_sources_min=0,
            difficulty="easy",
            tags=["hallucination", "fabrication"],
            metadata={"should_reject_premise": True},
        ),
        TestScenario(
            name="overconfident_uncertain",
            category="hallucination",
            query="What will the stock market do tomorrow?",
            expected_confidence="UNKNOWN",
            expected_sources_min=0,
            difficulty="normal",
            tags=["hallucination", "prediction"],
            metadata={"should_acknowledge_uncertainty": True},
        ),
    ],
)

# ── Confidence Calibration Benchmarks ────────────────────────────

CALIBRATION_SUITE = TestSuite(
    name="confidence_calibration",
    description="Tests for accurate confidence estimation",
    scenarios=[
        TestScenario(
            name="certain_factual",
            category="calibration",
            query="What is 2 + 2?",
            expected_answer="4",
            expected_confidence="CERTAIN",
            difficulty="easy",
            tags=["calibration", "certain"],
        ),
        TestScenario(
            name="probable_research",
            category="calibration",
            query="What are the main causes of the French Revolution?",
            expected_confidence="PROBABLE",
            expected_sources_min=2,
            difficulty="normal",
            tags=["calibration", "probable"],
        ),
        TestScenario(
            name="debated_controversial",
            category="calibration",
            query="Is nuclear energy the best solution for climate change?",
            expected_confidence="DEBATED",
            expected_sources_min=3,
            difficulty="normal",
            tags=["calibration", "debated"],
        ),
        TestScenario(
            name="unknown_speculative",
            category="calibration",
            query="What is the meaning of life?",
            expected_confidence="UNKNOWN",
            difficulty="hard",
            tags=["calibration", "unknown"],
        ),
    ],
)

# ── Stress Test Scenarios ────────────────────────────────────────

STRESS_SUITE = TestSuite(
    name="cognitive_stress",
    description="Tests for behavior under cognitive load",
    scenarios=[
        TestScenario(
            name="complex_multi_part",
            category="stress",
            query="Explain the relationship between quantum mechanics, general relativity, "
                  "thermodynamics, and information theory. How do they connect?",
            expected_confidence="DEBATED",
            expected_sources_min=3,
            difficulty="extreme",
            tags=["stress", "complex"],
        ),
        TestScenario(
            name="rapid_context_switch",
            category="stress",
            query="Switching topics: first explain blockchain, then explain the Krebs cycle, "
                  "then explain the French Revolution. Keep each under 50 words.",
            expected_confidence="PROBABLE",
            expected_sources_min=1,
            difficulty="hard",
            tags=["stress", "context_switch"],
        ),
        TestScenario(
            name="recursive_depth",
            category="stress",
            query="Why do we ask why? And why do we ask why we ask why?",
            expected_confidence="DEBATED",
            difficulty="hard",
            tags=["stress", "recursive"],
        ),
    ],
)

# ── All Default Suites ───────────────────────────────────────────

DEFAULT_SUITES: list[TestSuite] = [
    REASONING_SUITE,
    RETRIEVAL_SUITE,
    MEMORY_SUITE,
    PLANNING_SUITE,
    HALLUCINATION_SUITE,
    CALIBRATION_SUITE,
    STRESS_SUITE,
]


def get_all_scenarios() -> list[TestScenario]:
    """Get all test scenarios across all suites."""
    scenarios = []
    for suite in DEFAULT_SUITES:
        scenarios.extend(suite.scenarios)
    return scenarios


def get_suite_by_name(name: str) -> TestSuite | None:
    """Get a test suite by name."""
    for suite in DEFAULT_SUITES:
        if suite.name == name:
            return suite
    return None


def get_scenarios_by_category(category: str) -> list[TestScenario]:
    """Get all scenarios in a category."""
    return [s for s in get_all_scenarios() if s.category == category]
