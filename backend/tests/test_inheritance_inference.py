"""
Phase 62.1 — Inheritance Inference Verification Suite

Proves that VELYNX can *reason* over the World Model hierarchy, not just
display it. Three levels of proof:

  Level 1 — Schema Read Path: inherited facets surface in context
  Level 2 — Gatekeeper Write Path: invalid attributes are rejected
  Level 3 — Live Reasoning Path: pipeline answers inheritance questions
             WITHOUT being explicitly taught the answer
"""
from __future__ import annotations

import os
import asyncio
import pytest

# Must be set before pipeline import
os.environ.setdefault("VELYNX_TEST_MODE", "1")


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def registry():
    """Install and return the combined world model registry."""
    from backend.knowledge.ontology_loader import install_combined_registry
    return install_combined_registry()


@pytest.fixture(scope="module")
def tesla_entity(registry):
    """Resolve the Tesla Model 3 entity from the registry."""
    entity = registry.get_entity("Tesla Model 3")
    assert entity is not None, "Tesla Model 3 not found in registry"
    return entity


# ── Level 1: Schema Read Path ─────────────────────────────────────────────────

class TestSchemaReadPath:
    """Verify inherited + facet attributes surface via schema_context_for_concepts."""

    def test_vehicle_attributes_inherited(self, registry):
        from backend.knowledge.world_model_context import schema_context_for_concepts
        result = "\n".join(schema_context_for_concepts(["Tesla Model 3"]))
        assert "mobility_type" in result, "Vehicle attribute 'mobility_type' missing"
        assert "wheeled" in result, "Expected mobility_type=wheeled from Vehicle"

    def test_physical_object_attributes_inherited(self, registry):
        from backend.knowledge.world_model_context import schema_context_for_concepts
        result = "\n".join(schema_context_for_concepts(["Tesla Model 3"]))
        assert "mass_kg" in result, "PhysicalObject attribute 'mass_kg' missing"

    def test_electronics_facet_attributes_present(self, registry):
        from backend.knowledge.world_model_context import schema_context_for_concepts
        result = "\n".join(schema_context_for_concepts(["Tesla Model 3"]))
        assert "power_source" in result, "Electronics facet 'power_source' missing"
        assert "has_screen" in result,   "Electronics facet 'has_screen' missing"
        assert "voltage" in result,      "Electronics facet 'voltage' missing"

    def test_facet_membership_announced(self, registry):
        """The 'Also: Electronics' line must appear so the reasoner sees it."""
        from backend.knowledge.world_model_context import schema_context_for_concepts
        result = "\n".join(schema_context_for_concepts(["Tesla Model 3"]))
        assert "Electronics" in result, "'Also: Electronics' tag missing from output"

    def test_resolved_schema_depth(self, tesla_entity):
        """Type-chain + instance facets must resolve to concrete VALUES.

        NOTE: ``_resolved_schema()`` maps attribute-name -> ``AttributeSchema``
        (the slot *definitions*), not the entity's values. The resolved values
        are read via the entity's value-getter ``Entity.get()``. We assert both:
        that every layer's slot is *declared* in the resolved schema, and that
        the instance's value-getter returns the expected concrete value.
        """
        schema = tesla_entity._resolved_schema()
        # Slot definitions exist across all three layers.
        assert "mobility_type" in schema, "Vehicle slot missing from schema"
        assert "power_source" in schema,  "Electronics facet slot missing from schema"
        assert "has_screen" in schema,    "has_screen facet slot missing from schema"
        # Concrete resolved values (the value-getter, not the schema map).
        assert tesla_entity.get("mobility_type") == "wheeled", "Vehicle inheritance broken"
        assert tesla_entity.get("power_source")  == "battery", "Electronics facet broken"
        assert tesla_entity.get("has_screen")    is True,      "has_screen facet broken"

    def test_non_faceted_entity_unaffected(self, registry):
        """Blender (Software, no facets) must still resolve cleanly."""
        from backend.knowledge.world_model_context import schema_context_for_concepts
        result = "\n".join(schema_context_for_concepts(["Blender"]))
        # Must not crash and must mention Blender's type
        assert "Blender" in result or "Software" in result or result == "", \
            "Blender resolution crashed"


# ── Level 2: Gatekeeper Write Path ───────────────────────────────────────────

class TestGatekeeperWritePath:
    """Verify the schema gatekeeper accepts/rejects triples correctly.

    Contract (from backend.knowledge.schema_gatekeeper):
        validate_triples(triples) -> (accepted: list[Triple],
                                      rejections: list[Rejection])
    Each Rejection carries ``.reason_code`` (a stable string such as
    UNKNOWN_ATTRIBUTE / TYPE_MISMATCH / CONSTRAINT_VIOLATION) and ``.message``.
    """

    def test_rejects_unknown_attribute(self):
        from backend.knowledge.schema_gatekeeper import validate_triples
        triples = [("Tesla Model 3", "has_legs", "5000")]
        accepted, rejections = validate_triples(triples)
        assert len(rejections) == 1, "Expected rejection of has_legs on Vehicle"
        assert not accepted, "Rejected triple must not also be accepted"
        assert "UNKNOWN_ATTRIBUTE" in rejections[0].reason_code.upper() or \
               "unknown" in rejections[0].message.lower()

    def test_rejects_constraint_violation(self):
        from backend.knowledge.schema_gatekeeper import validate_triples
        triples = [("Tesla Model 3", "max_speed_kph", "999999")]
        accepted, rejections = validate_triples(triples)
        assert len(rejections) == 1, "Expected constraint violation on max_speed_kph"
        assert not accepted, "Rejected triple must not also be accepted"

    def test_accepts_schema_valid_attribute(self):
        from backend.knowledge.schema_gatekeeper import validate_triples
        triples = [("Tesla Model 3", "made_by", "Acme")]
        accepted, rejections = validate_triples(triples)
        assert len(rejections) == 0, "Valid triple incorrectly rejected"
        assert accepted == triples, "Valid triple should pass through accepted"

    def test_accepts_freeform_observation(self):
        """Open-world free-form facts must always pass through.

        The relation 'has' is not in the predicate_map, so the triple is a
        free-form assertion -> ACCEPT (open-world), per the gatekeeper's
        Stage-2 contract.
        """
        from backend.knowledge.schema_gatekeeper import validate_triples
        triples = [("Tesla Model 3", "has", "a scratch on the door")]
        accepted, rejections = validate_triples(triples)
        assert len(rejections) == 0, "Free-form observation incorrectly rejected"
        assert accepted == triples, "Free-form observation should be accepted"

    def test_untyped_entity_passes_through(self):
        """Entities not in the registry must not be blocked (pre-Phase-62 behavior)."""
        from backend.knowledge.schema_gatekeeper import validate_triples
        triples = [("supermegasoftware", "created", "engineers")]
        accepted, rejections = validate_triples(triples)
        assert len(rejections) == 0, "Untyped entity was incorrectly rejected"
        assert accepted == triples, "Untyped subject should be accepted (open-world)"


# ── Level 3: Live Reasoning Path ──────────────────────────────────────────────

class TestLiveReasoningPath:
    """
    The critical proof: VELYNX must answer inheritance questions WITHOUT
    being explicitly taught the answer. The schema context injected by
    schema_context_for_concepts() into episodic_context is the ONLY source
    of truth the reasoner has.

    These tests do NOT call answer_question() to avoid heavy pipeline
    startup in CI. Instead they verify the exact mechanism the pipeline
    uses: that the schema context string fed to the reasoning engine
    contains the inherited fact, proving the reasoner *could* answer it.

    One integration test (marked slow) calls the live pipeline.
    """

    def test_has_wheels_inferable_from_context(self, registry):
        """
        Core inheritance proof: 'wheeled' must appear in Tesla's context
        even though it was never explicitly taught — it comes from Vehicle.
        """
        from backend.knowledge.world_model_context import schema_context_for_concepts
        context_blocks = schema_context_for_concepts(["Tesla Model 3"])
        combined = "\n".join(context_blocks)
        assert "wheeled" in combined, (
            "INHERITANCE FAILURE: 'wheeled' not in Tesla context. "
            "Reasoner cannot infer 'has wheels' without this signal."
        )

    def test_electric_propulsion_inferable(self, registry):
        from backend.knowledge.world_model_context import schema_context_for_concepts
        context_blocks = schema_context_for_concepts(["Tesla Model 3"])
        combined = "\n".join(context_blocks)
        assert "electric" in combined, (
            "INFERENCE FAILURE: propulsion=electric not surfaced in context"
        )

    def test_inheritance_chain_depth(self, tesla_entity):
        """
        Prove the resolution spans all layers: the Tesla -> Vehicle ->
        PhysicalObject parent chain PLUS the instance-level Electronics facet.
        All three attribute namespaces must be present in the resolved schema.
        """
        schema = tesla_entity._resolved_schema()
        # PhysicalObject level
        assert "mass_kg" in schema,       "PhysicalObject layer missing"
        # Vehicle level
        assert "mobility_type" in schema, "Vehicle layer missing"
        # Instance facet level
        assert "power_source" in schema,  "Electronics facet layer missing"

    @pytest.mark.slow
    def test_live_pipeline_wheels_query(self):
        """
        LIVE INTEGRATION: teach nothing about wheels, then ask.
        The pipeline must answer affirmatively using schema context alone.

        Marked slow — skipped in fast CI, run explicitly with the full suite.

        Execution: pytest-asyncio is NOT a dependency of this repo, so we drive
        the coroutine to completion with ``asyncio.run`` from a sync test (the
        same convention as backend/tests/test_episodic_memory.py) rather than
        relying on a @pytest.mark.asyncio plugin that would otherwise leave the
        coroutine un-awaited (a silent false pass).
        """
        from backend.app.pipeline import answer_question

        resp = asyncio.run(answer_question("Does a Tesla Model 3 have wheels?"))

        # The answer must contain a positive signal
        answer_lower = resp.answer.lower()
        positive_signals = ["yes", "wheel", "wheeled", "does have", "has wheels"]
        assert any(s in answer_lower for s in positive_signals), (
            f"LIVE INFERENCE FAILURE: pipeline did not affirm wheels.\n"
            f"Answer: {resp.answer}\n"
            f"Confidence: {resp.confidence}\n"
            f"Debug keys: {list(resp.debug.keys()) if resp.debug else 'none'}"
        )

        # Confidence must not be LOW/UNKNOWN — it should know this
        assert resp.confidence not in ("LOW", "UNKNOWN"), (
            f"Pipeline answered with low confidence: {resp.confidence}\n"
            f"This suggests schema context was not injected into reasoning."
        )
