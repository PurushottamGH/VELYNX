"""Paired inference: the decision rules that replace the rejected M1 criterion.

The M0 review rejected "ranking stable across seeds with non-overlapping CIs".
These tests pin down the replacement: paired differences at the environment-seed
level, an effect size with a CI, a SESOI-based decision, and an explicit
equivalence test — with "inconclusive" as a real, reportable outcome.
"""

from __future__ import annotations

import pytest

from science.stats import (
    decide_equivalence,
    decide_superiority,
    holm,
    paired_bootstrap,
    paired_differences,
)


class TestPairing:
    def test_pairs_by_shared_seed(self):
        diffs = paired_differences({0: 3.0, 1: 5.0}, {0: 1.0, 1: 1.0})
        assert diffs == {0: 2.0, 1: 4.0}

    def test_unmatched_seeds_are_dropped_not_filled(self):
        """Substituting a mean would fabricate pairing."""
        diffs = paired_differences({0: 1.0, 5: 9.0}, {0: 0.5})
        assert diffs == {0: 0.5}

    def test_missing_values_are_dropped(self):
        assert paired_differences({0: None, 1: 2.0}, {0: 1.0, 1: 1.0}) == {1: 1.0}
        assert paired_differences({0: float("nan")}, {0: 1.0}) == {}


class TestBootstrap:
    def test_interval_brackets_a_clear_effect(self):
        boot = paired_bootstrap([-1.0, -1.1, -0.9, -1.05, -0.95, -1.02], seed=1)
        assert boot["n"] == 6
        assert boot["mean"] == pytest.approx(-1.0033, abs=1e-3)
        assert boot["ci_hi"] < 0
        assert boot["fraction_negative"] == 1.0

    def test_interval_spans_zero_for_noise(self):
        boot = paired_bootstrap([0.5, -0.4, 0.6, -0.5, 0.1, -0.2], seed=2)
        assert boot["ci_lo"] < 0 < boot["ci_hi"]

    def test_is_reproducible(self):
        a = paired_bootstrap([1.0, 2.0, 3.0, 4.0], seed=7)
        b = paired_bootstrap([1.0, 2.0, 3.0, 4.0], seed=7)
        assert a == b

    def test_declines_to_invent_an_interval_from_two_points(self):
        """A CI from n=2 would look precise and mean nothing."""
        boot = paired_bootstrap([1.0, 2.0])
        assert boot["n"] == 2
        assert boot["ci_lo"] != boot["ci_lo"]  # nan
        assert "note" in boot

    def test_empty_input_is_reported_not_crashed(self):
        assert paired_bootstrap([])["n"] == 0


class TestDecisions:
    def test_supported_requires_the_interval_to_clear_the_sesoi(self):
        boot = {"ci_lo": -1.2, "ci_hi": -0.8}
        assert decide_superiority(boot, sesoi=0.5) == "supported"

    def test_effect_smaller_than_the_sesoi_is_not_supported(self):
        """Statistically detectable but scientifically irrelevant must not pass."""
        boot = {"ci_lo": -0.10, "ci_hi": -0.02}
        assert decide_superiority(boot, sesoi=0.5) == "not_supported"

    def test_wide_interval_is_inconclusive_not_negative(self):
        boot = {"ci_lo": -2.0, "ci_hi": 0.4}
        assert decide_superiority(boot, sesoi=0.5) == "inconclusive"

    def test_direction_can_be_reversed(self):
        boot = {"ci_lo": 0.8, "ci_hi": 1.4}
        assert decide_superiority(boot, sesoi=0.5, direction="higher_is_better") == "supported"
        assert decide_superiority(boot, sesoi=0.5, direction="lower_is_better") == "not_supported"

    def test_equivalence_needs_containment_in_the_margin(self):
        assert decide_equivalence({"ci_lo": -0.05, "ci_hi": 0.04}, margin=0.1) == "equivalent"
        assert decide_equivalence({"ci_lo": 0.2, "ci_hi": 0.4}, margin=0.1) == "different"
        assert decide_equivalence({"ci_lo": -0.3, "ci_hi": 0.05}, margin=0.1) == "inconclusive"

    def test_failing_to_detect_a_difference_is_not_equivalence(self):
        """The distinction V0-1's no-decay control depends on."""
        wide = {"ci_lo": -0.9, "ci_hi": 0.9}
        assert decide_superiority(wide, sesoi=0.2) == "inconclusive"
        assert decide_equivalence(wide, margin=0.2) == "inconclusive"

    def test_missing_interval_is_inconclusive(self):
        assert (
            decide_superiority({"ci_lo": float("nan"), "ci_hi": float("nan")}, 0.5)
            == "inconclusive"
        )

    def test_sesoi_and_margin_must_be_positive(self):
        with pytest.raises(ValueError):
            decide_superiority({"ci_lo": -1, "ci_hi": -1}, sesoi=0.0)
        with pytest.raises(ValueError):
            decide_equivalence({"ci_lo": 0, "ci_hi": 0}, margin=-1.0)

    def test_unknown_direction_is_rejected(self):
        with pytest.raises(ValueError, match="direction"):
            decide_superiority({"ci_lo": -1, "ci_hi": -1}, 0.5, direction="sideways")


class TestMultiplicity:
    def test_holm_is_monotone_and_conservative(self):
        adjusted = holm({"a": 0.01, "b": 0.04, "c": 0.20})
        assert adjusted["a"] == pytest.approx(0.03)
        assert adjusted["b"] == pytest.approx(0.08)
        assert adjusted["c"] == pytest.approx(0.20)
        assert adjusted["a"] <= adjusted["b"] <= adjusted["c"]

    def test_caps_at_one(self):
        assert holm({"a": 0.9, "b": 0.95})["b"] <= 1.0
