"""
research/tests/test_evaluation_split.py
=======================================

Unit tests for the held-out seed partitioning in
:mod:`research.evaluation.split`.

The contract under test: evaluation seeds are reproducible, live in a high
well-separated band, and are provably disjoint (at the world+sensor lineage
granularity) from the training seeds they are derived from.
"""

from __future__ import annotations

import pytest

from research.evaluation.split import (
    EVAL_SEED_BASE,
    EVAL_SEED_STRIDE,
    assert_disjoint,
    probe_seed,
    seed_lineage,
)


# -- probe_seed -------------------------------------------------------------

def test_probe_seed_is_in_high_band():
    s = probe_seed(1)
    assert s == EVAL_SEED_BASE + 1 * EVAL_SEED_STRIDE
    assert s >= EVAL_SEED_BASE


def test_probe_seed_is_deterministic():
    assert probe_seed(7) == probe_seed(7)
    assert probe_seed(7, index=3) == probe_seed(7, index=3)


def test_probe_seed_distinct_train_seeds_get_distinct_blocks():
    # Even with the maximum in-block index, train seed 1's block cannot reach
    # train seed 2's block.
    top_of_block_1 = probe_seed(1, index=EVAL_SEED_STRIDE - 1)
    bottom_of_block_2 = probe_seed(2, index=0)
    assert top_of_block_1 < bottom_of_block_2


def test_probe_seed_index_offsets_within_block():
    base = probe_seed(4, index=0)
    assert probe_seed(4, index=5) == base + 5


def test_probe_seed_rejects_negative_train_seed():
    with pytest.raises(ValueError):
        probe_seed(-1)


def test_probe_seed_rejects_out_of_range_index():
    with pytest.raises(ValueError):
        probe_seed(1, index=EVAL_SEED_STRIDE)
    with pytest.raises(ValueError):
        probe_seed(1, index=-1)


# -- seed_lineage -----------------------------------------------------------

def test_seed_lineage_includes_sensor_seed():
    # EnvironmentDataset seeds world=seed, sensor=seed+1.
    assert seed_lineage(10) == frozenset({10, 11})


# -- assert_disjoint --------------------------------------------------------

def test_derived_probe_seed_is_disjoint_from_training():
    train_seeds = [1, 2, 3, 4, 5]
    eval_seeds = [probe_seed(s) for s in train_seeds]
    # Must not raise.
    assert_disjoint(train_seeds, eval_seeds)


def test_assert_disjoint_raises_on_direct_overlap():
    with pytest.raises(ValueError, match="overlap"):
        assert_disjoint([5], [5])


def test_assert_disjoint_raises_on_adjacent_sensor_seed_overlap():
    # Train seed 5 consumes {5, 6}; eval seed 6 consumes {6, 7}. They share 6.
    with pytest.raises(ValueError, match="overlap"):
        assert_disjoint([5], [6])


def test_assert_disjoint_allows_separated_seeds():
    # Train {5,6} vs eval {8,9}: no overlap.
    assert_disjoint([5], [8])
