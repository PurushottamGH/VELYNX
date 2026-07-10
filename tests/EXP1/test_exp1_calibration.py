from __future__ import annotations

import pytest

from experiments.EXP1.calibration import (
    BIN_BOUNDARIES,
    ECE_PASS_THRESHOLD,
    TIER_TO_CONFIDENCE,
    bin_index_for_confidence,
    compute_ece,
    confidence_for_tier,
)
from experiments.EXP1.dataset import EvaluatedRecord


def _record(tier: str, correctness: int, index: int) -> EvaluatedRecord:
    return EvaluatedRecord(
        query_id=f"q{index}",
        answer="answer",
        tier=tier,
        correctness=correctness,
        query_family="known_factual",
    )


def test_locked_tier_confidence_mapping_matches_preregistration() -> None:
    assert TIER_TO_CONFIDENCE == {
        "UNKNOWN": 0.125,
        "DEBATED": 0.375,
        "PROBABLE": 0.625,
        "CERTAIN": 0.875,
    }
    assert confidence_for_tier("unknown") == 0.125
    with pytest.raises(ValueError):
        confidence_for_tier("LOW")


def test_equal_width_bin_boundaries_are_locked() -> None:
    assert BIN_BOUNDARIES == (0.0, 0.25, 0.5, 0.75, 1.0)
    assert bin_index_for_confidence(0.0) == 0
    assert bin_index_for_confidence(0.2499) == 0
    assert bin_index_for_confidence(0.25) == 1
    assert bin_index_for_confidence(0.5) == 2
    assert bin_index_for_confidence(0.75) == 3
    assert bin_index_for_confidence(1.0) == 3


def test_compute_ece_uses_weighted_bin_accuracy_minus_confidence() -> None:
    records = [
        _record("UNKNOWN", correctness, index)
        for index, correctness in enumerate([0, 0, 0, 1])
    ]
    records.extend(
        _record("CERTAIN", correctness, index + 4)
        for index, correctness in enumerate([1, 1, 1, 0])
    )

    result = compute_ece(records)

    assert result.n == 8
    assert result.ece == pytest.approx(0.125)
    assert result.bins[0].accuracy == pytest.approx(0.25)
    assert result.bins[0].confidence == pytest.approx(0.125)
    assert result.bins[0].ece_contribution == pytest.approx(0.0625)
    assert result.bins[3].accuracy == pytest.approx(0.75)
    assert result.bins[3].confidence == pytest.approx(0.875)
    assert result.bins[3].ece_contribution == pytest.approx(0.0625)


def test_empty_bins_are_reported_with_zero_ece_weight() -> None:
    result = compute_ece([_record("UNKNOWN", 0, 1), _record("CERTAIN", 1, 2)])

    assert result.bins[1].count == 0
    assert result.bins[1].accuracy is None
    assert result.bins[1].confidence is None
    assert result.bins[1].ece_contribution == 0.0
    assert result.bins[2].count == 0
    assert result.bins[2].ece_contribution == 0.0


def test_ece_pass_gate_is_strictly_less_than_point_one() -> None:
    passing = compute_ece(
        [_record("DEBATED", c, i) for i, c in enumerate([1, 1, 1, 0, 0, 0, 0, 0])]
    )
    failing = compute_ece(
        [_record("PROBABLE", c, i) for i, c in enumerate([0, 0, 0, 0, 1, 1, 1, 1])]
    )

    assert ECE_PASS_THRESHOLD == 0.10
    assert passing.ece < ECE_PASS_THRESHOLD
    assert passing.passes_ece_gate is True
    assert failing.ece >= ECE_PASS_THRESHOLD
    assert failing.passes_ece_gate is False
