"""
research/tests/test_evaluation_protocol.py
==========================================

Unit tests for :class:`research.evaluation.protocol.EvaluationProtocol`.

The protocol is the runner-facing hook: given a trained monitor it produces a
single held-out predictive RMSE measurement, drawn from a training-disjoint
seed, without mutating the live model.
"""

from __future__ import annotations

import math

from research.evaluation.protocol import (
    DEFAULT_PROBE_TICKS,
    HELD_OUT_RMSE_KEY,
    EvaluationProtocol,
)
from research.evaluation.read_only import ReadOnlyEvaluator
from research.evaluation.split import probe_seed
from validation.datasets import build_dataset
from validation.monitor import VectorMonitor


def _trained_monitor(seed: int = 1, ticks: int = 300) -> VectorMonitor:
    monitor = VectorMonitor(proximity_threshold=0.25, max_clusters=50)
    dataset = build_dataset("environment", seed=seed, noise_sigma=0.05)
    for _ in range(ticks):
        monitor.tick(dataset.get_next_tick())
    return monitor


# -- seed derivation --------------------------------------------------------

def test_held_out_seed_matches_split_derivation():
    proto = EvaluationProtocol(train_seed=3)
    assert proto.held_out_seed() == probe_seed(3, 0)


def test_probe_index_selects_distinct_stream():
    a = EvaluationProtocol(train_seed=3, probe_index=0).held_out_seed()
    b = EvaluationProtocol(train_seed=3, probe_index=1).held_out_seed()
    assert a != b


# -- finalize ---------------------------------------------------------------

def test_finalize_returns_held_out_rmse_key():
    monitor = _trained_monitor()
    proto = EvaluationProtocol(train_seed=1, num_probe_ticks=120)
    result = proto.finalize(monitor)

    assert set(result) == {HELD_OUT_RMSE_KEY}
    assert isinstance(result[HELD_OUT_RMSE_KEY], float)
    assert result[HELD_OUT_RMSE_KEY] > 0.0


def test_finalize_is_deterministic():
    monitor = _trained_monitor(seed=2)
    proto = EvaluationProtocol(train_seed=2, num_probe_ticks=100)
    first = proto.finalize(monitor)
    second = proto.finalize(monitor)
    assert first[HELD_OUT_RMSE_KEY] == second[HELD_OUT_RMSE_KEY]


def test_finalize_matches_manual_read_only_evaluation():
    # The protocol is exactly: build the disjoint stream, score it read-only.
    monitor = _trained_monitor(seed=1)
    proto = EvaluationProtocol(train_seed=1, num_probe_ticks=100)

    eval_seed = proto.held_out_seed()
    dataset = build_dataset("environment", seed=eval_seed, noise_sigma=0.05)
    vectors = [dataset.get_next_tick() for _ in range(100)]
    expected = ReadOnlyEvaluator(monitor).evaluate(vectors, seed=eval_seed).rmse

    assert math.isclose(proto.finalize(monitor)[HELD_OUT_RMSE_KEY], expected)


def test_finalize_does_not_mutate_live_monitor():
    monitor = _trained_monitor()
    snap_before = monitor.snapshot()
    cluster_count_before = snap_before["cluster_count"]

    EvaluationProtocol(train_seed=1, num_probe_ticks=150).finalize(monitor)

    snap_after = monitor.snapshot()
    assert snap_after["cluster_count"] == cluster_count_before
    assert snap_after["transitions"] == snap_before["transitions"]


def test_default_probe_ticks_constant():
    proto = EvaluationProtocol(train_seed=1)
    assert proto.num_probe_ticks == DEFAULT_PROBE_TICKS
