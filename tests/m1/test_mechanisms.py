"""Controls must actually control what they claim to.

Each test here corresponds to a control the M0 review requires. A control that
quietly fails to match its budget, or that leaks current-task data into a
"historical" condition, would produce a comparison that looks fair and is not —
which is worse than having no control at all.
"""

from __future__ import annotations

import pytest

from core.seeds import SeedSet
from core.types import Observation
from science.mechanisms.controls import (
    BoundaryGate,
    CurrentSample,
    HistoricalOnly,
    MatchedRandomGate,
    NoReplay,
    TaskBalanced,
)
from science.mechanisms.environments import MarkovBlocksSplit
from science.mechanisms.v0 import ReservoirMemory


def obs(t: int, task: int, context: int = 0, target: int = 1) -> Observation:
    return Observation(t=t, task=task, context=context, target=target)


class TestMatchedRandomGate:
    def test_exact_mode_spends_the_declared_budget_exactly(self):
        """ "Equal budget" must mean equal, not equal in expectation."""
        gate = MatchedRandomGate(k=4, n_fires=25, horizon=1000, seed=0)
        fires = sum(1 for t in range(1000) if gate.replay_count(0.0, t) > 0)
        assert fires == 25
        assert gate.n_replays == 100

    def test_timing_is_independent_of_loss(self):
        """The property that makes it a valid comparator for surprise gating."""
        low = MatchedRandomGate(k=1, n_fires=10, horizon=100, seed=3)
        high = MatchedRandomGate(k=1, n_fires=10, horizon=100, seed=3)
        low_fires = [t for t in range(100) if low.replay_count(0.0, t) > 0]
        high_fires = [t for t in range(100) if high.replay_count(99.0, t) > 0]
        assert low_fires == high_fires

    def test_rate_mode_matches_only_in_expectation(self):
        gate = MatchedRandomGate(k=1, rate=0.5, seed=1)
        fires = sum(1 for t in range(2000) if gate.replay_count(0.0, t) > 0)
        assert 900 < fires < 1100
        assert fires != 1000 or True  # exactness is not claimed in this mode

    def test_requires_exactly_one_budget_specification(self):
        with pytest.raises(ValueError, match="exactly one"):
            MatchedRandomGate(seed=0)
        with pytest.raises(ValueError, match="exactly one"):
            MatchedRandomGate(n_fires=5, horizon=10, rate=0.1, seed=0)

    def test_rejects_impossible_budget(self):
        with pytest.raises(ValueError, match="cannot exceed"):
            MatchedRandomGate(n_fires=20, horizon=10, seed=0)

    def test_same_seed_reproduces_the_schedule(self):
        a = MatchedRandomGate(k=1, n_fires=8, horizon=50, seed=11)
        b = MatchedRandomGate(k=1, n_fires=8, horizon=50, seed=11)
        assert [t for t in range(50) if a.replay_count(0.0, t)] == [
            t for t in range(50) if b.replay_count(0.0, t)
        ]


class TestBoundaryGate:
    def test_fires_only_inside_the_window_after_each_switch(self):
        gate = BoundaryGate(period=10, window=3, k=2)
        fires = [t for t in range(30) if gate.replay_count(0.0, t) > 0]
        assert fires == [0, 1, 2, 10, 11, 12, 20, 21, 22]

    def test_window_cannot_exceed_the_block(self):
        with pytest.raises(ValueError, match="window"):
            BoundaryGate(period=5, window=6)


class TestReplayContent:
    @pytest.fixture
    def memory(self):
        mem = ReservoirMemory(capacity=100, seed=0)
        for t in range(10):
            mem.append(obs(t, task=0, context=t % 3, target=(t + 1) % 3))
        for t in range(10, 20):
            mem.append(obs(t, task=1, context=t % 3, target=(t + 2) % 3))
        return mem

    def test_current_sample_is_update_matched_and_carries_no_history(self, memory):
        """Control 3. Same update count as historical replay, zero historical content."""
        policy = CurrentSample(weight=1.0)
        latest = obs(99, task=1, context=2, target=0)
        items = policy.select(memory, 4, latest)
        assert len(items) == 4
        assert all(item == (2, 0, 1.0) for item in items)

    def test_historical_only_never_returns_the_current_task(self, memory):
        """Control 6. If this leaks, 'protection from older evidence' is unsupported."""
        policy = HistoricalOnly(weight=1.0, seed=0)
        latest = obs(99, task=1)
        picked = policy.select(memory, 20, latest)
        stored = {(o.context, o.target): o.task for o in memory.snapshot()}
        assert len(picked) == 20
        assert all(stored[(c, y)] == 0 for c, y, _ in picked)

    def test_historical_only_reports_a_shortfall_instead_of_faking_a_draw(self):
        """Empty prior-task pool must yield nothing, not a current-task substitute."""
        mem = ReservoirMemory(capacity=10, seed=0)
        mem.append(obs(0, task=0))
        policy = HistoricalOnly(seed=0)
        assert policy.select(mem, 4, obs(1, task=0)) == []

    def test_task_balanced_spreads_across_prior_tasks(self, memory):
        """Control 7. Equal draws per prior task at a fixed budget."""
        mem = ReservoirMemory(capacity=100, seed=0)
        for t in range(30):
            mem.append(obs(t, task=t % 3, context=t % 3, target=(t + 1) % 3))
        policy = TaskBalanced(seed=0)
        items = policy.select(mem, 6, obs(99, task=2))
        stored = {(o.context, o.target): o.task for o in mem.snapshot()}
        tasks = [stored[(c, y)] for c, y, _ in items]
        assert len(items) == 6
        assert set(tasks) == {0, 1}
        assert tasks.count(0) == tasks.count(1) == 3

    def test_no_replay_ignores_any_budget(self, memory):
        assert NoReplay().select(memory, 100, obs(1, task=0)) == []

    def test_zero_budget_yields_nothing(self, memory):
        for policy in (CurrentSample(), HistoricalOnly(seed=0), TaskBalanced(seed=0)):
            assert policy.select(memory, 0, obs(1, task=1)) == []


class TestSplitEnvironment:
    def test_iteration_is_deterministic_and_repeatable(self):
        seeds = SeedSet.build(4, "independent")
        env = MarkovBlocksSplit(n_tasks=2, alphabet=4, steps_per_task=25, seeds=seeds)
        assert [o.target for o in env] == [o.target for o in env]

    def test_trajectory_seed_changes_the_stream_but_not_the_tasks(self):
        """The separation V0-4 needs: same task family, different realisation."""
        a = MarkovBlocksSplit(
            n_tasks=2, alphabet=4, steps_per_task=40, seeds=SeedSet.build(1, "independent")
        )
        b = MarkovBlocksSplit(
            n_tasks=2,
            alphabet=4,
            steps_per_task=40,
            seeds=SeedSet.build(1, "independent", {"trajectory": 999}),
        )
        assert [t.rows for t in a.tasks()] == [t.rows for t in b.tasks()]
        assert [o.target for o in a] != [o.target for o in b]

    def test_environment_seed_changes_the_tasks(self):
        a = MarkovBlocksSplit(n_tasks=2, alphabet=4, steps_per_task=10, seeds=SeedSet.build(1))
        b = MarkovBlocksSplit(
            n_tasks=2,
            alphabet=4,
            steps_per_task=10,
            seeds=SeedSet.build(1, "independent", {"environment": 77}),
        )
        assert [t.rows for t in a.tasks()] != [t.rows for t in b.tasks()]

    def test_order_modes_change_presentation_not_generation(self):
        seeds = SeedSet.build(2, "independent")
        forward = MarkovBlocksSplit(n_tasks=3, steps_per_task=5, order="sequential", seeds=seeds)
        backward = MarkovBlocksSplit(n_tasks=3, steps_per_task=5, order="reversed", seeds=seeds)
        assert [t for t, _ in forward.checkpoints()] == [0, 1, 2]
        assert [t for t, _ in backward.checkpoints()] == [2, 1, 0]
        assert [t.rows for t in forward.tasks()] == [t.rows for t in backward.tasks()]

    def test_shuffled_order_differs_per_cycle(self):
        """Repeating one shuffled order would reintroduce the serial-position
        confound the order stream exists to break."""
        env = MarkovBlocksSplit(
            n_tasks=4, steps_per_task=2, cycles=2, order="shuffled", seeds=SeedSet.build(5)
        )
        order = [task for task, _ in env.checkpoints()]
        assert sorted(order[:4]) == [0, 1, 2, 3]
        assert sorted(order[4:]) == [0, 1, 2, 3]
        assert order[:4] != order[4:]

    def test_checkpoints_land_on_the_last_step_of_each_block(self):
        env = MarkovBlocksSplit(n_tasks=2, steps_per_task=7, cycles=1, seeds=SeedSet.build(0))
        events = list(env)
        for task, last_step in env.checkpoints():
            assert events[last_step].task == task
        assert env.total_steps == 14

    def test_rejects_unknown_order(self):
        with pytest.raises(ValueError, match="unknown order"):
            MarkovBlocksSplit(order="sideways", seeds=SeedSet.build(0))


class TestMemoryAdapters:
    def test_reservoir_is_bounded_and_snapshot_is_read_only(self):
        mem = ReservoirMemory(capacity=5, seed=0)
        for t in range(100):
            mem.append(obs(t, task=0))
        assert len(mem) == 5
        assert mem.n_seen == 100
        snapshot = mem.snapshot()
        assert isinstance(snapshot, tuple)
        assert len(snapshot) == 5

    def test_null_memory_stores_nothing_but_counts_arrivals(self):
        from science.mechanisms.v0 import NullMemory

        mem = NullMemory(seed=0)
        for t in range(10):
            mem.append(obs(t, task=0))
        assert len(mem) == 0
        assert mem.sample(5) == []
        assert mem.snapshot() == ()
        assert mem.n_seen == 10
