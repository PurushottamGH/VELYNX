"""Cross-module regression: the CONFIDENCE_TIERS / _TIERS triplication risk.

Three independent literal 4-tuples currently encode the same canonical tier
label set:

  - program_a.types._TIERS                       (module-private, leaf)
  - program_a.constants.CONFIDENCE_TIERS          (frozen, non-placeholder)
  - experiments.EXP1.dataset.CONFIDENCE_TIERS     (EXP-1 side; program_a may
                                                    not import this at runtime,
                                                    but a TEST may)

program_a/types.py's own docstring documents this as deliberate ("Duplicated
here ONLY because this is a leaf module forbidden from importing
`experiments`"), but a deliberate duplication is exactly the shape that
silently drifts. tests/program_a/test_types.py already asserts types.py vs
constants.py equality; this file adds the missing third leg (vs
experiments.EXP1.dataset) from a test-only vantage point, which is legitimate
because program_a's OWN source may not import experiments -- nothing here
imports experiments.EXP1 from inside program_a/.

Scope: tests only, no production-code changes.
"""
from __future__ import annotations

from program_a import constants
from program_a.types import Emission


def _types_tiers() -> tuple[str, ...]:
    # types.py's _TIERS is module-private; reach it via the one place its
    # value is externally observable without re-implementing validation:
    # Emission's __post_init__ raises with the tuple embedded in the message.
    import re

    try:
        Emission(answer="a", tier="__NOT_A_TIER__", raw_numeric_confidence=None, metadata={})
    except ValueError as exc:
        match = re.search(r"one of \((.*?)\); got", str(exc))
        assert match, f"could not parse tier tuple out of Emission error message: {exc}"
        return tuple(part.strip().strip("'\"") for part in match.group(1).split(","))
    raise AssertionError("Emission accepted a tier that should be invalid")


def test_types_private_tier_tuple_matches_constants_confidence_tiers() -> None:
    assert _types_tiers() == constants.CONFIDENCE_TIERS


def test_types_private_tier_tuple_matches_exp1_dataset_confidence_tiers() -> None:
    from experiments.EXP1.dataset import CONFIDENCE_TIERS as EXP1_CONFIDENCE_TIERS

    assert _types_tiers() == EXP1_CONFIDENCE_TIERS


def test_constants_confidence_tiers_matches_exp1_dataset_confidence_tiers() -> None:
    from experiments.EXP1.dataset import CONFIDENCE_TIERS as EXP1_CONFIDENCE_TIERS

    assert constants.CONFIDENCE_TIERS == EXP1_CONFIDENCE_TIERS


def test_constants_state_tier_map_values_are_a_subset_of_all_three_tier_sources() -> None:
    from experiments.EXP1.dataset import CONFIDENCE_TIERS as EXP1_CONFIDENCE_TIERS

    values = set(constants.STATE_TIER_MAP.values())
    assert values <= set(constants.CONFIDENCE_TIERS)
    assert values <= set(EXP1_CONFIDENCE_TIERS)
    assert values <= set(_types_tiers())
