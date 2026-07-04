"""
VELYNX Phase 63 — Simulation Engine Test Suite
===============================================

Proves three safety guarantees of the counterfactual reasoning pipeline:

1. ``validate_premise`` — read-only ontology validation that correctly accepts
   valid overrides and rejects structural violations.
2. ``SimulationMemoryContext`` — the Boundary pattern restores original
   gatekeeper and store functions even when an exception is raised inside the
   ``with`` block.
3. ``CounterfactualEvaluator`` — the ``CausalDelta.answer_flipped`` heuristic
   fires when confidence drops or reasoning paths collapse.

All tests are self-contained (pytest mocks, no database, no pipeline).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ── Path bootstrap (matches existing test pattern) ──────────────────────────
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]
_REPO_ROOT = _HERE.parents[2]
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ══════════════════════════════════════════════════════════════════════════════
#  Shared fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def vehicle_schema() -> dict:
    """Build a typed attribute schema matching a Vehicle-like entity.

    Returns a dict of ``{attribute_key: AttributeSchema}``.
    """
    from backend.knowledge.world_model_schema import AttributeSchema

    return {
        "mobility_type": AttributeSchema(
            name="mobility_type",
            datatype=str,
            constraints={"enum": ["wheeled", "tracked", "hover", "stationary"]},
        ),
        "wheel_count": AttributeSchema(
            name="wheel_count",
            datatype=int,
            constraints={"min": 0, "max": 100},
        ),
        "max_speed_kph": AttributeSchema(
            name="max_speed_kph",
            datatype=float,
            constraints={"min": 0, "max": 1000},
        ),
        "color": AttributeSchema(
            name="color",
            datatype=str,
            description="Vehicle color.",
        ),
    }


@pytest.fixture
def mock_entity(vehicle_schema):
    """A mocked Entity that looks like a registered Vehicle entity."""
    from unittest.mock import MagicMock

    entity = MagicMock()
    entity.name = "Tesla Model 3"
    entity.type.name = "Vehicle"
    entity._resolved_schema.return_value = vehicle_schema
    return entity


@pytest.fixture
def simple_coercer():
    """Return a *coerce* callable that mimics the gatekeeper's ``_coerce``.

    Handles int, float, bool, str. Used to patch
    ``backend.simulation.interface._coerce`` in ``validate_premise`` tests.
    """
    def _coerce(value: str, datatype: type):
        try:
            if datatype is bool:
                if value.strip().lower() in ("true", "yes", "1", "t", "y"):
                    return True, None
                if value.strip().lower() in ("false", "no", "0", "f", "n"):
                    return False, None
                return value, f"cannot parse {value!r} as bool"
            if datatype is int:
                f = float(value)
                if not f.is_integer():
                    return value, f"{value!r} is not an integer"
                return int(f), None
            if datatype is float:
                return float(value), None
            return value, None
        except (TypeError, ValueError) as exc:
            return value, str(exc)

    return _coerce


# ══════════════════════════════════════════════════════════════════════════════
#  1. interface.py — validate_premise
# ══════════════════════════════════════════════════════════════════════════════


class TestValidatePremise:
    """Tests for ``interface.validate_premise``.

    Every test patches ``_resolve_entity`` and ``_coerce`` at the
    ``backend.simulation.interface`` level so no real gatekeeper, registry,
    or database is touched.
    """

    # ── 1a. Valid overrides are accepted ───────────────────────────────────────

    @pytest.mark.parametrize("attr_key,value", [
        ("mobility_type", "hover"),
        ("wheel_count", 0),
        ("max_speed_kph", 200.0),
        ("color", "matte black"),
    ])
    def test_valid_override_accepted(
        self, mock_entity, simple_coercer, attr_key, value,
    ):
        from backend.simulation.interface import CounterfactualPremise, validate_premise

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={attr_key: value},
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            with patch("backend.simulation.interface._coerce", side_effect=simple_coercer):
                result = validate_premise(premise)

        assert result.is_valid, (
            f"expected valid for {attr_key}={value!r}, got rejected: {result.rejected_overrides}"
        )
        assert result.entity_resolved is True
        assert result.entity_type_name == "Vehicle"
        assert attr_key in result.accepted_overrides
        assert len(result.rejected_overrides) == 0

    def test_multiple_valid_overrides_all_accepted(self, mock_entity, simple_coercer):
        from backend.simulation.interface import CounterfactualPremise, validate_premise

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={
                "mobility_type": "hover",
                "wheel_count": 0,
                "color": "crimson",
            },
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            with patch("backend.simulation.interface._coerce", side_effect=simple_coercer):
                result = validate_premise(premise)

        assert result.is_valid
        assert set(result.accepted_overrides) == {"mobility_type", "wheel_count", "color"}
        assert len(result.rejected_overrides) == 0

    # ── 1b. Read-only attributes are rejected ─────────────────────────────────

    @pytest.mark.parametrize("read_only_attr", ["id", "name", "entity_type"])
    def test_read_only_attr_rejected(self, mock_entity, simple_coercer, read_only_attr):
        from backend.simulation.interface import CounterfactualPremise, validate_premise

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={read_only_attr: "some-value"},
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            with patch("backend.simulation.interface._coerce", side_effect=simple_coercer):
                result = validate_premise(premise)

        assert not result.is_valid
        assert result.is_partial is False  # no accepted overrides
        assert len(result.rejected_overrides) >= 1
        ro_rejection = next(
            (r for r in result.rejected_overrides if r.reason_code == "READ_ONLY"),
            None,
        )
        assert ro_rejection is not None, (
            f"expected READ_ONLY rejection for {read_only_attr}, "
            f"got: {[(r.attribute_key, r.reason_code) for r in result.rejected_overrides]}"
        )
        assert ro_rejection.attribute_key == read_only_attr

    def test_read_only_alongside_valid_creates_partial_result(
        self, mock_entity, simple_coercer,
    ):
        """Mixing valid overrides with read-only ones produces a partial result."""
        from backend.simulation.interface import CounterfactualPremise, validate_premise

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={
                "mobility_type": "hover",
                "id": "doppelganger-42",
            },
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            with patch("backend.simulation.interface._coerce", side_effect=simple_coercer):
                result = validate_premise(premise)

        assert not result.is_valid
        assert result.is_partial
        assert "mobility_type" in result.accepted_overrides
        ro_rejection = next(
            r for r in result.rejected_overrides if r.reason_code == "READ_ONLY"
        )
        assert ro_rejection.attribute_key == "id"

    # ── 1c. Unknown entity rejection ──────────────────────────────────────────

    def test_unknown_entity_returns_not_resolved(self):
        from backend.simulation.interface import CounterfactualPremise, validate_premise

        premise = CounterfactualPremise(
            target_entity="Spaceship X",
            attribute_overrides={"color": "red"},
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=None):
            result = validate_premise(premise)

        assert not result.is_valid
        assert result.entity_resolved is False
        assert len(result.rejected_overrides) >= 1
        assert result.rejected_overrides[0].reason_code == "UNKNOWN_ENTITY"

    # ── 1d. Unknown attribute rejection ───────────────────────────────────────

    def test_unknown_attribute_rejected(self, mock_entity, simple_coercer):
        from backend.simulation.interface import CounterfactualPremise, validate_premise
        from backend.knowledge.schema_gatekeeper import REASON_UNKNOWN_ATTRIBUTE

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={"leg_count": 4},
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            with patch("backend.simulation.interface._coerce", side_effect=simple_coercer):
                result = validate_premise(premise)

        assert not result.is_valid
        assert len(result.rejected_overrides) >= 1
        attr_rejection = next(
            r for r in result.rejected_overrides
            if r.reason_code == REASON_UNKNOWN_ATTRIBUTE
        )
        assert attr_rejection.attribute_key == "leg_count"

    # ── 1e. Type mismatch rejection ──────────────────────────────────────────

    def test_type_mismatch_rejected(self, mock_entity):
        """wheel_count expects int; a non-numeric string should trigger type mismatch."""
        from backend.simulation.interface import CounterfactualPremise, validate_premise
        from backend.knowledge.schema_gatekeeper import REASON_TYPE_MISMATCH

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={"wheel_count": "not-a-number"},
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            # Have _coerce fail for the non-numeric string
            with patch("backend.simulation.interface._coerce", return_value=("not-a-number", "cannot parse 'not-a-number' as int")):
                result = validate_premise(premise)

        assert not result.is_valid
        assert len(result.rejected_overrides) >= 1
        mismatch = next(
            r for r in result.rejected_overrides
            if r.reason_code == REASON_TYPE_MISMATCH
        )
        assert mismatch.attribute_key == "wheel_count"

    # ── 1f. Constraint violation rejection ────────────────────────────────────

    def test_constraint_violation_rejected(self, mock_entity, simple_coercer):
        """wheel_count with value 999 exceeds the max constraint of 100."""
        from backend.simulation.interface import CounterfactualPremise, validate_premise
        from backend.knowledge.schema_gatekeeper import REASON_CONSTRAINT_VIOLATION

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={"wheel_count": 999},
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            with patch("backend.simulation.interface._coerce", side_effect=simple_coercer):
                result = validate_premise(premise)

        assert not result.is_valid
        assert len(result.rejected_overrides) >= 1
        violation = next(
            r for r in result.rejected_overrides
            if r.reason_code == REASON_CONSTRAINT_VIOLATION
        )
        assert violation.attribute_key == "wheel_count"

    def test_enum_violation_rejected(self, mock_entity, simple_coercer):
        """mobility_type 'flying' is not in the allowed enum."""
        from backend.simulation.interface import CounterfactualPremise, validate_premise
        from backend.knowledge.schema_gatekeeper import REASON_CONSTRAINT_VIOLATION

        premise = CounterfactualPremise(
            target_entity="Tesla Model 3",
            attribute_overrides={"mobility_type": "flying"},
        )

        with patch("backend.simulation.interface._resolve_entity", return_value=mock_entity):
            with patch("backend.simulation.interface._coerce", side_effect=simple_coercer):
                result = validate_premise(premise)

        assert not result.is_valid
        assert len(result.rejected_overrides) >= 1
        violation = next(
            r for r in result.rejected_overrides
            if r.reason_code == REASON_CONSTRAINT_VIOLATION
        )
        assert violation.attribute_key == "mobility_type"


# ══════════════════════════════════════════════════════════════════════════════
#  2. simulation_memory_context.py — Boundary pattern exception safety
# ══════════════════════════════════════════════════════════════════════════════

class TestSimulationMemoryContextExceptionSafety:
    """Prove that ``SimulationMemoryContext.__exit__`` restores the original
    ``gk.validate_triples`` and ``fe._store_triples`` even when a deliberate
    exception is raised inside the ``with`` block.
    """

    def test_restores_validate_triples_on_exception(self):
        """Raise ValueError inside with block; verify gk.validate_triples restored."""
        from backend.simulation.simulation_memory_context import SimulationMemoryContext

        original_validate = MagicMock(side_effect=lambda triples: (triples, []))
        original_store = MagicMock(return_value=0)

        with patch(
            "backend.knowledge.schema_gatekeeper.validate_triples", original_validate,
        ):
            with patch(
                "backend.knowledge.fact_extractor._store_triples", original_store,
            ):
                # These imports happen AFTER patching so they see the mock module.
                import backend.knowledge.schema_gatekeeper as gk
                import backend.knowledge.fact_extractor as fe

                ctx = SimulationMemoryContext()

                try:
                    with ctx:
                        # Inside the context: verify functions were swapped.
                        assert gk.validate_triples is not original_validate
                        assert fe._store_triples is not original_store
                        raise ValueError("deliberate crash inside simulation")
                except ValueError:
                    pass

                # After __exit__: original functions MUST be back.
                assert (
                    gk.validate_triples is original_validate
                ), f"expected original_validate, got {gk.validate_triples}"
                assert (
                    fe._store_triples is original_store
                ), f"expected original_store, got {fe._store_triples}"

    def test_restores_after_multiple_exception_types(self):
        """Different exception types (RuntimeError, KeyError) must all be safe."""
        from backend.simulation.simulation_memory_context import SimulationMemoryContext

        original_validate = MagicMock(side_effect=lambda triples: (triples, []))
        original_store = MagicMock(return_value=0)

        for exc_type in (RuntimeError, KeyError, ZeroDivisionError, SystemExit):
            with patch(
                "backend.knowledge.schema_gatekeeper.validate_triples", original_validate,
            ):
                with patch(
                    "backend.knowledge.fact_extractor._store_triples", original_store,
                ):
                    import backend.knowledge.schema_gatekeeper as gk
                    import backend.knowledge.fact_extractor as fe

                    ctx = SimulationMemoryContext()

                    try:
                        with ctx:
                            raise exc_type("deliberate")
                    except exc_type:
                        pass

                    assert gk.validate_triples is original_validate, (
                        f"failed to restore after {exc_type.__name__}"
                    )
                    assert fe._store_triples is original_store, (
                        f"failed to restore after {exc_type.__name__}"
                    )

    def test_clean_exit_also_restores(self):
        """Clean exit (no exception) must also restore originals."""
        from backend.simulation.simulation_memory_context import SimulationMemoryContext

        original_validate = MagicMock(side_effect=lambda triples: (triples, []))
        original_store = MagicMock(return_value=0)

        with patch(
            "backend.knowledge.schema_gatekeeper.validate_triples", original_validate,
        ):
            with patch(
                "backend.knowledge.fact_extractor._store_triples", original_store,
            ):
                import backend.knowledge.schema_gatekeeper as gk
                import backend.knowledge.fact_extractor as fe

                ctx = SimulationMemoryContext()

                with ctx:
                    # Do something harmless inside the context.
                    ctx.fork_entity("Tesla Model 3", attribute_overrides={"color": "red"})
                    ctx.record_triple("Tesla Model 3", "color", "red")

                assert gk.validate_triples is original_validate
                assert fe._store_triples is original_store

    def test_context_is_not_active_and_buffers_cleared_after_exception(self):
        """After exception, is_active must be False and buffers cleared."""
        from backend.simulation.simulation_memory_context import SimulationMemoryContext

        original_validate = MagicMock(side_effect=lambda triples: (triples, []))
        original_store = MagicMock(return_value=0)

        with patch(
            "backend.knowledge.schema_gatekeeper.validate_triples", original_validate,
        ):
            with patch(
                "backend.knowledge.fact_extractor._store_triples", original_store,
            ):
                ctx = SimulationMemoryContext()

                try:
                    with ctx:
                        ctx.fork_entity("Tesla Model 3", attribute_overrides={"color": "red"})
                        ctx.record_triple("Tesla Model 3", "color", "red")
                        raise ValueError("boom")
                except ValueError:
                    pass

                assert ctx.is_active is False
                assert ctx.is_dirty is False
                assert ctx.counterfactual_triple_count == 0
                assert ctx.forked_entity_names == []


# ══════════════════════════════════════════════════════════════════════════════
#  3. causal_evaluator.py — CausalDelta answer_flipped heuristics
# ══════════════════════════════════════════════════════════════════════════════


class TestCounterfactualEvaluatorAnswerFlipped:
    """Tests for ``CounterfactualEvaluator.evaluate()`` → ``CausalDelta.answer_flipped``.

    We mock ``_run_baseline`` and ``_run_simulated`` directly to return
    controlled ``ReasoningTrace`` objects, bypassing the actual
    ``SimulationMemoryContext`` and reasoning engine. This keeps the test pure
    logic — we are testing the *delta computation* and *heuristic*, not the
    pass orchestration.
    """

    # ── Builder helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _fact(subject: str, predicate: str, obj: str, confidence: float = 0.5):
        """Shorthand for creating a Fact."""
        from backend.cognition.reasoning_engine import Fact
        return Fact(subject=subject, predicate=predicate, obj=obj, confidence=confidence)

    @staticmethod
    def _path(start: str, end: str, confidence: float = 0.7):
        """Shorthand for creating a ReasoningPath."""
        from backend.cognition.reasoning_engine import ReasoningPath, PathStep
        return ReasoningPath(
            start=start,
            end=end,
            steps=[PathStep(fact=TestCounterfactualEvaluatorAnswerFlipped._fact(start, "related_to", end))],
            confidence=confidence,
        )

    @staticmethod
    def _trace(
        concepts: list[str] | None = None,
        paths: list | None = None,
        winning_facts: list | None = None,
        inferred_facts: list | None = None,
        contradictions: list | None = None,
        confidence: float = 0.5,
    ):
        """Shorthand for creating a ReasoningTrace."""
        from backend.cognition.reasoning_engine import ReasoningTrace
        return ReasoningTrace(
            query_concepts=concepts or [],
            paths=paths or [],
            winning_facts=winning_facts or [],
            inferred_facts=inferred_facts or [],
            contradictions=contradictions or [],
            confidence=confidence,
        )

    # ── Fixtures ─────────────────────────────────────────────────────────────

    @pytest.fixture
    def evaluator(self):
        """A CounterfactualEvaluator with mocked dependencies.

        The evaluator is used as a shell — we patch its internal methods to
        isolate the delta-computation logic.
        """
        from backend.simulation.causal_evaluator import CounterfactualEvaluator

        mock_reason = MagicMock()
        mock_retrieve = MagicMock(return_value=[])
        mock_extract = MagicMock(return_value=[])

        return CounterfactualEvaluator(
            reason_fn=mock_reason,
            triple_retriever=mock_retrieve,
            concept_extractor=mock_extract,
        )

    # ── Heuristic 1: query-relevant fact lost or gained ──────────────────────

    def test_fact_lost_triggers_flip(self, evaluator):
        """Losing a query-relevant fact must set answer_flipped = True."""
        baseline = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.8,
        )
        simulated = self._trace(
            concepts=["Tesla"],
            winning_facts=[],  # fact is gone
            confidence=0.8,
        )

        evaluator._concept_extractor = MagicMock(return_value=["Tesla"])
        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is True
        assert len(delta.facts_lost) >= 1

    def test_fact_gained_triggers_flip(self, evaluator):
        """Gaining a new query-relevant fact must set answer_flipped = True."""
        baseline = self._trace(
            concepts=["Tesla"],
            winning_facts=[],
            confidence=0.8,
        )
        simulated = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.8,
        )

        evaluator._concept_extractor = MagicMock(return_value=["Tesla"])
        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is True
        assert len(delta.facts_gained) >= 1

    # ── Heuristic 2: confidence collapse ─────────────────────────────────────

    def test_confidence_drop_triggers_flip(self, evaluator):
        """Baseline confidence >= 0.5 and drop >= 0.3 → answer_flipped = True."""
        baseline = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.8,
        )
        simulated = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.3)],
            confidence=0.4,  # drop >= 0.3
        )

        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is True
        assert delta.confidence_delta == pytest.approx(-0.4)

    def test_small_confidence_drop_does_not_flip(self, evaluator):
        """Drop of less than 0.3 from baseline >= 0.5 must NOT flip."""
        baseline = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.8,
        )
        simulated = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.6,  # drop = 0.2, below threshold
        )

        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is False

    def test_low_baseline_confidence_drop_does_not_flip(self, evaluator):
        """Baseline < 0.5 → confidence drop does NOT trigger flip (no certainty
        to lose)."""
        baseline = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.3)],
            confidence=0.4,  # below 0.5 threshold
        )
        simulated = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.3)],
            confidence=0.1,  # drop = 0.3, but baseline < 0.5
        )

        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is False

    # ── Heuristic 3: path collapse ──────────────────────────────────────────

    def test_path_collapse_triggers_flip(self, evaluator):
        """All reasoning paths breaking → answer_flipped = True."""
        baseline = self._trace(
            concepts=["Tesla", "wheels"],
            paths=[self._path("Tesla", "wheels")],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.8,
        )
        simulated = self._trace(
            concepts=["Tesla", "wheels"],
            paths=[],  # all paths collapsed
            winning_facts=[],
            confidence=0.1,
        )

        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is True
        assert len(delta.paths_lost) >= 1
        assert delta.path_count_delta < 0

    def test_some_paths_remain_does_not_flip_by_heuristic_3(self, evaluator):
        """If baseline has 2 paths and simulated has 1, heuristic 3 does NOT
        fire (but heuristic 1 or 2 might)."""
        p1 = self._path("Tesla", "wheels")
        p2 = self._path("Tesla", "mobility")
        baseline = self._trace(
            concepts=["Tesla", "wheels"],
            paths=[p1, p2],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.8,
        )
        simulated = self._trace(
            concepts=["Tesla", "wheels"],
            paths=[p1],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            confidence=0.8,
        )

        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        # Heuristic 3 requires ALL paths broken — p1 still exists, so no flip
        # via heuristic 3. Heuristics 1-2 also don't fire.
        assert delta.answer_flipped is False

    # ── No change case ───────────────────────────────────────────────────────

    def test_no_change_no_flip(self, evaluator):
        """Identical traces → no flip."""
        trace = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            paths=[self._path("Tesla", "wheels")],
            confidence=0.85,
        )

        with patch.object(evaluator, "_run_baseline", return_value=(trace, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(trace, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is False
        assert delta.confidence_delta == pytest.approx(0.0)
        assert len(delta.facts_lost) == 0
        assert len(delta.facts_gained) == 0
        assert len(delta.paths_lost) == 0
        assert len(delta.paths_gained) == 0

    # ── Confidence increase (no flip) ────────────────────────────────────────

    def test_confidence_increase_does_not_flip(self, evaluator):
        """Higher confidence in simulated run must NOT trigger a flip."""
        baseline = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.7)],
            confidence=0.6,
        )
        simulated = self._trace(
            concepts=["Tesla"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.95)],
            confidence=0.9,  # increased!
        )

        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is False
        assert delta.confidence_delta > 0

    # ── Facts lost + paths lost simultaneously ───────────────────────────────

    def test_facts_and_paths_both_lost(self, evaluator):
        """Combined fact + path loss — still flips (should not double-count)."""
        baseline = self._trace(
            concepts=["Tesla", "wheels"],
            winning_facts=[self._fact("Tesla", "has", "wheels", 0.9)],
            paths=[self._path("Tesla", "wheels")],
            confidence=0.8,
        )
        simulated = self._trace(
            concepts=["Tesla", "wheels"],
            winning_facts=[],
            paths=[],
            confidence=0.2,
        )

        with patch.object(evaluator, "_run_baseline", return_value=(baseline, [])):
            with patch.object(evaluator, "_run_simulated", return_value=(simulated, [])):
                delta = evaluator.evaluate("Does Tesla have wheels?", {"Tesla": {}})

        assert delta.answer_flipped is True
        assert delta.confidence_delta == pytest.approx(-0.6)
        assert len(delta.facts_lost) >= 1
        assert len(delta.paths_lost) >= 1


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
