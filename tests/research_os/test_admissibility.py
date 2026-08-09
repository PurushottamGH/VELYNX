"""The admissibility kernel (invariant K2).

These tests are the kernel's specification. Each maps to a named article or
constraint of the frozen Constitution Lock, so a test failure is a statement
about which frozen rule stopped holding.
"""

from __future__ import annotations

import pytest

from ros.admissibility import (
    ClaimScope,
    Determinism,
    Manifest,
    Registration,
    Tier,
    assess,
    required_tier_for,
)

REGISTERED = Registration(True, True, True, True)
UNREGISTERED = Registration(False, False, False, False)


def manifest(**overrides) -> Manifest:
    """A flawless manifest, overridable field by field."""
    base = dict(
        run_id="run-0001",
        determinism=Determinism.D0,
        clean_checkout=True,
        complete=True,
        protocol_frozen_before_first_run=True,
        protocol_hash_matched=True,
        coverage_disclosed=True,
        stream_complete_for_scope=True,
        faults_intact=True,
    )
    base.update(overrides)
    return Manifest(**base)  # type: ignore[arg-type]


# --------------------------------------------------------- tier ordering


def test_tiers_are_ordered():
    assert Tier.INADMISSIBLE < Tier.ENGINEERING_ONLY < Tier.EXPLORATORY < Tier.CONFIRMATORY


def test_tier_comparison_does_not_fall_back_to_string_ordering():
    """`Tier` subclasses `str`. Any comparison operator left undefined would
    compare the *labels* alphabetically, under which 'confirmatory-admissible'
    sorts below 'exploratory-admissible' and the strongest tier reads as the
    weakest. All four operators must be rank-based."""
    assert Tier.CONFIRMATORY > Tier.EXPLORATORY
    assert Tier.CONFIRMATORY >= Tier.EXPLORATORY
    assert not Tier.EXPLORATORY > Tier.CONFIRMATORY
    assert Tier.INADMISSIBLE < Tier.CONFIRMATORY
    # The alphabetical ordering these must not use:
    assert str(Tier.CONFIRMATORY.value) < str(Tier.EXPLORATORY.value)


def test_engineering_only_is_not_admissible():
    """The distinction the whole kernel exists to preserve: work may be legal
    and still bear no evidence."""
    assert not assess(manifest(), UNREGISTERED).admissible


# ------------------------------------------------------------ positive control


def test_flawless_registered_run_is_confirmatory():
    verdict = assess(manifest(), REGISTERED, ClaimScope.OBJECT)
    assert verdict.tier is Tier.CONFIRMATORY
    assert verdict.admissible
    assert verdict.permits(Tier.CONFIRMATORY)


# ----------------------------------------------------------- Article L-11


def test_unregistered_lock_forces_engineering_only():
    verdict = assess(manifest(), UNREGISTERED, ClaimScope.OBJECT)
    assert verdict.tier is Tier.ENGINEERING_ONLY
    assert "L-11" in verdict.reasons[0]


@pytest.mark.parametrize(
    "registration",
    [
        Registration(False, True, True, True),
        Registration(True, False, True, True),
        Registration(True, True, False, True),
        Registration(True, True, True, False),
    ],
)
def test_every_registration_precondition_is_load_bearing(registration):
    """Each of the four preconditions alone is enough to block admissibility.
    A precondition that could be dropped without changing the verdict would be
    documentation, not a gate."""
    assert not registration.active
    assert assess(manifest(), registration).tier is Tier.ENGINEERING_ONLY


# ------------------------------------------------------------ Article L-3


def test_suppressed_fault_is_inadmissible():
    verdict = assess(manifest(faults_intact=False), REGISTERED)
    assert verdict.tier is Tier.INADMISSIBLE
    assert "L-3" in verdict.reasons[0]


def test_fault_suppression_outranks_a_clean_manifest():
    """A run that is perfect except for a dropped fault must not be rescued by
    its other virtues."""
    assert assess(manifest(faults_intact=False), REGISTERED).tier < Tier.ENGINEERING_ONLY


# --------------------------------------------------------------- Lock E1


def test_unfrozen_protocol_caps_at_exploratory():
    verdict = assess(manifest(protocol_frozen_before_first_run=False), REGISTERED)
    assert verdict.tier is Tier.EXPLORATORY
    assert "protocol frozen before first run" in verdict.ceilings


def test_protocol_hash_mismatch_caps_at_exploratory():
    verdict = assess(manifest(protocol_hash_matched=False), REGISTERED)
    assert verdict.tier is Tier.EXPLORATORY
    assert "protocol hash match" in verdict.ceilings


# --------------------------------------------------------------- Lock R1


def test_d2_cannot_be_confirmatory():
    verdict = assess(manifest(determinism=Determinism.D2), REGISTERED, ClaimScope.POPULATION)
    assert verdict.tier is Tier.EXPLORATORY


def test_incomplete_run_cannot_be_confirmatory():
    verdict = assess(manifest(complete=False), REGISTERED, ClaimScope.POPULATION)
    assert verdict.tier is Tier.EXPLORATORY


def test_dirty_checkout_caps_at_exploratory():
    verdict = assess(manifest(clean_checkout=False), REGISTERED, ClaimScope.POPULATION)
    assert verdict.tier is Tier.EXPLORATORY
    assert "clean checkout" in verdict.ceilings


# ----------------------------------------------------------- Constraint C-a


def test_object_claim_from_d2_is_inadmissible():
    """C-a is stricter than R1 here: D2 merely blocks confirmatory in general,
    but cannot support an object-level claim at any tier."""
    verdict = assess(manifest(determinism=Determinism.D2), REGISTERED, ClaimScope.OBJECT)
    assert verdict.tier is Tier.INADMISSIBLE


def test_object_claim_needs_a_complete_stream():
    verdict = assess(manifest(stream_complete_for_scope=False), REGISTERED, ClaimScope.OBJECT)
    assert verdict.tier is Tier.INADMISSIBLE


def test_population_claim_needs_coverage_disclosure():
    verdict = assess(manifest(coverage_disclosed=False), REGISTERED, ClaimScope.POPULATION)
    assert verdict.tier is Tier.EXPLORATORY
    assert "C-a coverage disclosure" in verdict.ceilings


def test_coverage_disclosure_is_not_required_for_object_claims():
    """C-a attaches coverage disclosure to population claims. Applying it to
    object claims would be stricter than the Lock, which is its own defect."""
    verdict = assess(manifest(coverage_disclosed=False), REGISTERED, ClaimScope.OBJECT)
    assert verdict.tier is Tier.CONFIRMATORY


# -------------------------------------------------------------- reporting


def test_all_binding_rules_are_reported_not_just_the_first():
    verdict = assess(
        manifest(clean_checkout=False, complete=False, protocol_hash_matched=False),
        REGISTERED,
        ClaimScope.POPULATION,
    )
    assert len(verdict.ceilings) == 3
    assert {"clean checkout", "run completeness", "protocol hash match"} <= set(verdict.ceilings)


def test_clean_verdict_states_why_it_passed():
    verdict = assess(manifest(), REGISTERED, ClaimScope.OBJECT)
    assert verdict.reasons and "All applicable rules satisfied" in verdict.reasons[0]


def test_kernel_is_pure():
    """Same inputs, same verdict — the property that makes a verdict reviewable."""
    first = assess(manifest(), REGISTERED, ClaimScope.OBJECT)
    second = assess(manifest(), REGISTERED, ClaimScope.OBJECT)
    assert first == second


# ---------------------------------------------------------- required tier


@pytest.mark.parametrize("intent", ["accept_within_scope", "reject", "validate", "generalize"])
def test_claim_advancing_intents_require_confirmatory(intent):
    assert required_tier_for(intent) is Tier.CONFIRMATORY


@pytest.mark.parametrize("intent", ["nominate_hypothesis", "redirect_engineering", "screen"])
def test_exploratory_intents_require_exploratory(intent):
    assert required_tier_for(intent) is Tier.EXPLORATORY


def test_unknown_intent_is_treated_as_strictest():
    """Failing open on an unrecognised intent would let a new use silently
    bypass the confirmatory bar."""
    assert required_tier_for("something-nobody-registered") is Tier.CONFIRMATORY
