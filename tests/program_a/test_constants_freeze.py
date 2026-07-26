"""Program A constants freeze-state tests (G4-prep).

Dedicated, collectable coverage for ``program_a.constants`` -- imports ONLY
``program_a.constants`` (no relocated-to-sandbox emission/binding stubs), so it
runs pre-GO. The companion ``test_stub_contracts.py`` constants section points
here.

Scope (G4-prep state, 2026-07-09):
  * Concrete frozen values transcribed verbatim from the T1 Section-5 register.
  * Four dict register entries (SUPPORT_TEST_PARAMS, CONTRADICTION_MATERIALITY_
    PARAMS, EXTRACTION_PARAMS, ANSWER_TEMPLATES) remain PENDING (addendum
    Section C condition 4); held as {} and NOT fabricated.
  * frozen_constants_digest() machinery implemented per Section 6.1 but gated
    pending; CONSTANTS_HASH is None.
  * CR-8/L8 firewall: no constant collides with an EXP-1 tier probability or
    bin boundary.

Reference: PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md Sections 5-6;
PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md Section A6-DIGEST and Section C;
PROGRAM_A_MODULE_SPEC.md Section 2.
"""

from __future__ import annotations

import pytest

from program_a import constants


def test_frozen_constants_digest_pending_until_register_complete() -> None:
    # Four register entries are owed at the G4 freeze step (addendum Section C
    # condition 4). Until they are transcribed, frozen_constants_digest() must
    # REFUSE to emit a value (no fabricated hash over placeholders) and
    # CONSTANTS_HASH must be None.
    assert constants.CONSTANTS_HASH is None
    with pytest.raises(constants.FrozenConstantsIncomplete) as excinfo:
        constants.frozen_constants_digest()
    msg = str(excinfo.value)
    for owed in (
        "SUPPORT_TEST_PARAMS",
        "CONTRADICTION_MATERIALITY_PARAMS",
        "EXTRACTION_PARAMS",
        "ANSWER_TEMPLATES",
    ):
        assert owed in msg
    assert "addendum Section C" in msg


def test_constants_freeze_state() -> None:
    # Concrete frozen values transcribed verbatim from the T1 Section-5 register
    # (G4-prep); the four dict entries below remain pending (owed at the freeze
    # step) and are NOT fabricated here.
    assert constants.SPEC_VERSION == "es1-t1-2026-07-09"
    assert constants.MIN_INDEPENDENT_ORIGINS_FOR_S3 == 2
    assert constants.INDEPENDENCE_RELATION == (
        "two evidence items are independent iff they have distinct "
        "origin_domain provenance, with mirror/syndication domains counted once"
    )
    assert constants.EVIDENCE_ORDERING_KEY == "lexicographic on (origin_domain, doc_id)"
    assert constants.PA3_RULESET_VERSION == "pa3-ruleset-2026-07-09"
    # Pending (addendum Section C condition 4) -- held as {}, not fabricated:
    assert constants.SUPPORT_TEST_PARAMS == {}
    assert constants.CONTRADICTION_MATERIALITY_PARAMS == {}
    assert constants.EXTRACTION_PARAMS == {}
    assert constants.ANSWER_TEMPLATES == {}
    assert set(constants._FREEZE_PENDING_ENTRIES) == {
        "SUPPORT_TEST_PARAMS",
        "CONTRADICTION_MATERIALITY_PARAMS",
        "EXTRACTION_PARAMS",
        "ANSWER_TEMPLATES",
    }


def test_constants_state_tier_map_and_confidence_tiers_frozen() -> None:
    # CR-8/L8 structural mapping, not tunable. Guard against accidental edits.
    assert constants.STATE_TIER_MAP == {
        "S0": "UNKNOWN",
        "S1": "DEBATED",
        "S2": "PROBABLE",
        "S3": "CERTAIN",
    }
    assert constants.CONFIDENCE_TIERS == ("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")


def test_constants_contain_no_exp1_probability_or_bin_value() -> None:
    # CR-8/L8 firewall: no member of constants.py may equal an EXP-1
    # tier->probability value (0.125/0.375/0.625/0.875) or a bin boundary
    # (0.0/0.25/0.5/0.75/1.0). Values asserted here, not imported into
    # program_a (experiments.EXP1.calibration is deny-listed). Guards the freeze
    # integrity independently of the pending entries.
    forbidden = {0.125, 0.375, 0.625, 0.875, 0.0, 0.25, 0.5, 0.75, 1.0}
    for name in constants.__all__:
        value = getattr(constants, name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            assert (
                value not in forbidden
            ), f"{name}={value} collides with a frozen EXP-1 value (CR-8/L8)"
