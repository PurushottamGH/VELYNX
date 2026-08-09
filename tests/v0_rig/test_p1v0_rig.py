"""Smoke and invariant tests for the P1 v0 rig.

These are the acceptance tests for milestone M0. They check that the rig can
(a) reproduce a run exactly, (b) actually learn, and (c) actually detect
forgetting -- without which any ablation result would be meaningless.
"""

from __future__ import annotations

import math

import pytest

from p1v0 import metrics
from p1v0.gate import AlwaysGate, NeverGate, SurpriseGate
from p1v0.loop import run
from p1v0.memory import NullBuffer, ReplayBuffer
from p1v0.model import CountModel, scoring_loss
from p1v0.probe import ProbeSuite
from p1v0.runner import Config, execute
from p1v0.stream import TaskStream

SMALL = dict(n_tasks=3, alphabet=6, steps_per_task=400, seed=1)


def test_stream_is_deterministic():
    a = list(TaskStream(**SMALL))
    b = list(TaskStream(**SMALL))
    assert a == b
    assert len(a) == 3 * 400


def test_stream_blocks_align_with_task_labels():
    stream = TaskStream(**SMALL)
    events = list(stream)
    for task, end in stream.blocks():
        assert events[end].task == task


def test_scoring_loss_matches_definition():
    assert scoring_loss([0.5, 0.5], 0) == pytest.approx(math.log(2))
    assert scoring_loss([1.0, 0.0], 0) == pytest.approx(0.0, abs=1e-9)
    # out-of-range index is penalised, not crashed
    assert scoring_loss([0.5, 0.5], 7) > 10.0


def test_model_beats_uniform_baseline_on_a_single_task():
    stream = TaskStream(n_tasks=1, alphabet=6, steps_per_task=2000, seed=2)
    model = CountModel(alphabet=6, decay=1.0)
    losses = [r.loss for r in run(stream, model, NullBuffer(), NeverGate())]
    tail = metrics.mean(losses[-500:])
    assert tail < metrics.uniform_baseline(6) - 0.3


def test_decay_causes_measurable_forgetting():
    """A recency-biased model must lose competence on earlier tasks."""
    stream = TaskStream(**SMALL)
    probes = ProbeSuite(stream, n_pairs=200)
    model = CountModel(alphabet=6, decay=0.9)
    for _ in run(stream, model, NullBuffer(), NeverGate()):
        pass
    final = probes.evaluate(model)
    # loss on the last-trained task is lower than on the first-trained task
    assert final[2] < final[0]


def test_replay_reduces_forgetting_relative_to_online():
    base = dict(
        n_tasks=3,
        alphabet=6,
        steps_per_task=1500,
        cycles=1,
        decay=0.9,
        probe_pairs=300,
        seed=3,
    )
    online, _ = execute(Config(variant="online", **base))
    replay, _ = execute(Config(variant="replay_always", replay_k=4, **base))
    assert replay["retention"] < online["retention"]


def test_gates_report_their_own_activity():
    stream = TaskStream(**SMALL)
    model = CountModel(alphabet=6)
    memory = ReplayBuffer(capacity=100, seed=1)
    gate = SurpriseGate(threshold=1.0, k=2)
    for _ in run(stream, model, memory, gate):
        pass
    assert gate.n_fired > 0
    assert gate.n_replays == 2 * gate.n_fired

    never = NeverGate()
    assert never.replay_count(99.0) == 0
    always = AlwaysGate(k=3)
    assert always.replay_count(0.0) == 3


def test_reservoir_buffer_is_bounded_and_samples():
    buf = ReplayBuffer(capacity=10, seed=0)
    for i in range(1000):
        buf.append((i % 5, i % 3))
    assert len(buf) == 10
    assert buf.n_seen == 1000
    assert len(buf.sample(7)) == 7
    assert buf.sample(0) == []


def test_execute_is_reproducible_and_shaped():
    cfg = Config(variant="replay_surprise", n_tasks=3, alphabet=6, steps_per_task=300, seed=5)
    s1, r1 = execute(cfg)
    s2, r2 = execute(cfg)
    assert r1 == r2
    assert s1["online"] == s2["online"]
    assert len(s1["probe_matrix"]) == 3
    assert len(s1["probe_matrix"][0]) == 3
    assert s1["block_tasks"] == [0, 1, 2]
