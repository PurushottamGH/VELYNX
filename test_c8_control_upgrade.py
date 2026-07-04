"""
test_c8_control_upgrade.py
==========================

Verification suite for the C8 control-system upgrade:

* Task 1 -- MemoryScheduler hysteresis (enter>=20, exit<=10) + 50-tick cooldown.
* Task 2 -- merge budget: at most 3 committed merges per triggered sleep cycle.
* Task 3 -- immediate quarantine replay: drain the queue after each commit,
            counting quarantine_replayed and resolving re-homed anomalies,
            with no duplicate records.

Run from the repo root::

    python -m pytest test_c8_control_upgrade.py -v
"""

from __future__ import annotations

from backend.cognition.memory_scheduler import MemoryScheduler
from backend.cognition.vector_prediction_core import ClusterEngine
from validation.interfaces import Dataset
from validation.runner import BenchmarkRunner, _MAX_MERGES_PER_CYCLE


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


class _Telemetry:
    """Mutable telemetry source: lets a test dial active_anomalies_count."""

    def __init__(self, active: int = 0) -> None:
        self.active = active

    def get_memory_summary(self) -> dict:
        return {"active_anomalies_count": self.active}


class _FixedDataset(Dataset):
    """Dataset that always yields the same vector."""

    def __init__(self, vector):
        self._vector = list(vector)

    def get_next_tick(self):
        return list(self._vector)

    def reset(self) -> None:
        return None


class _FakeMonitor:
    """Minimal monitor exposing the runner's consolidation surface."""

    def __init__(self, engine, active_count):
        self.cluster_engine = engine
        self._active = active_count

    def tick(self, vector):
        return {"prediction": None, "surprise": None, "regime": "stable"}

    def get_memory_summary(self):
        return {"active_anomalies_count": self._active}


# ---------------------------------------------------------------------------
# Task 1 -- Hysteresis & cooldown
# ---------------------------------------------------------------------------


def test_hysteresis_enters_at_high_watermark():
    """No trigger below 20; fires the moment active_anomalies_count hits 20."""
    tele = _Telemetry(active=19)
    sched = MemoryScheduler(tele, time_interval=10_000)  # disable time trigger

    assert sched.tick() is False  # 19 < 20: stay off
    assert sched.in_consolidation is False

    tele.active = 20
    assert sched.tick() is True  # 20 >= 20: enter
    assert sched.in_consolidation is True


def test_hysteresis_holds_in_dead_band_until_low_watermark():
    """Once latched on, the controller holds through the 11..19 dead band."""
    tele = _Telemetry(active=25)
    sched = MemoryScheduler(tele, time_interval=10_000)

    assert sched.tick() is True  # enter at 25

    # In the dead band (exit=10 < active < enter=20) the latch holds ON.
    for val in (19, 15, 11):
        tele.active = val
        assert sched.tick() is True, f"should hold latched at active={val}"
        assert sched.in_consolidation is True

    # Drop to the low watermark -> exit.
    tele.active = 10
    assert sched.tick() is False
    assert sched.in_consolidation is False

    # Below the dead band stays off until the high watermark is crossed again.
    tele.active = 19
    assert sched.tick() is False


def test_cooldown_blocks_triggers_for_50_ticks_after_reset():
    """reset() arms a strict 50-tick refractory window, even under max pressure."""
    tele = _Telemetry(active=1000)  # permanently slammed against the ceiling
    sched = MemoryScheduler(tele, time_interval=10_000, cooldown=50)

    assert sched.tick() is True  # enters immediately
    sched.reset()  # cycle ends -> cooldown armed, latch cleared
    assert sched.in_consolidation is False

    # Exactly 50 ticks of suppression despite active=1000 the whole time.
    for i in range(50):
        assert sched.tick() is False, f"cooldown breached at tick {i}"

    # 51st evaluation is allowed again and re-enters on the standing pressure.
    assert sched.tick() is True


def test_anomaly_pressure_alias_back_compat():
    """Legacy anomaly_pressure kwarg still tunes the enter (high) watermark."""
    tele = _Telemetry(active=30)
    sched = MemoryScheduler(tele, time_interval=10_000, anomaly_pressure=30)
    assert sched.enter_pressure == 30
    assert sched.anomaly_pressure == 30

    tele.active = 29
    assert sched.tick() is False
    tele.active = 30
    assert sched.tick() is True


# ---------------------------------------------------------------------------
# Task 3 -- ClusterEngine.reingest_quarantined mechanic
# ---------------------------------------------------------------------------


def test_reingest_joins_nearby_cluster_and_resolves_without_duplicate():
    """A quarantined vector close to a cluster joins it and is marked absorbed."""
    engine = ClusterEngine(proximity_threshold=0.25, max_clusters=2)
    engine._create_cluster([0.0, 0.0])     # id 0
    engine._create_cluster([10.0, 10.0])   # id 1  (budget now full)

    rec = engine._open_quarantine([0.05, 0.05])  # within 0.25 of cluster 0
    assert rec.status == "active"
    assert len(engine.anomaly_records) == 1

    ok = engine.reingest_quarantined(rec.id)
    assert ok is True
    assert rec.status == "absorbed"
    # No duplicate record was spawned by the re-ingest.
    assert len(engine.anomaly_records) == 1
    # Resolved -> no longer counts as active pressure.
    assert engine.get_memory_summary()["active_anomalies_count"] == 0


def test_reingest_fails_when_budget_full_then_seeds_after_slot_freed():
    """Far vector cannot place while budget is full; seeds once a slot opens."""
    engine = ClusterEngine(proximity_threshold=0.25, max_clusters=2)
    engine._create_cluster([0.0, 0.0])     # id 0
    engine._create_cluster([10.0, 10.0])   # id 1  (budget full)

    rec = engine._open_quarantine([5.0, 5.0])  # far from both, budget full
    assert engine.reingest_quarantined(rec.id) is False
    assert rec.status == "active"
    assert len(engine.anomaly_records) == 1  # still no duplicate

    # Simulate a merge freeing a slot.
    engine.clusters = [c for c in engine.clusters if c.id != 1]
    assert engine.reingest_quarantined(rec.id) is True
    assert rec.status == "absorbed"
    assert len(engine.anomaly_records) == 1


def test_reingest_ignores_non_active_records():
    """Only active records can be re-ingested; others are a no-op."""
    engine = ClusterEngine(proximity_threshold=0.25, max_clusters=5)
    engine._create_cluster([0.0, 0.0])
    rec = engine._open_quarantine([0.01, 0.01])
    assert engine.reingest_quarantined(rec.id) is True
    # Second call: already absorbed -> no-op False, no new record.
    assert engine.reingest_quarantined(rec.id) is False
    assert engine.reingest_quarantined(999) is False


# ---------------------------------------------------------------------------
# Task 2 -- Merge budget (integration via the runner)
# ---------------------------------------------------------------------------


def _engine_with_identical_clusters(n):
    """Engine holding ``n`` clusters all at the origin (every merge accepted)."""
    engine = ClusterEngine(proximity_threshold=0.25, max_clusters=50)
    for _ in range(n):
        engine._create_cluster([0.0, 0.0])
    return engine


def test_merge_budget_caps_commits_at_three_per_cycle():
    """A single triggered sleep cycle commits at most _MAX_MERGES_PER_CYCLE."""
    assert _MAX_MERGES_PER_CYCLE == 3

    engine = _engine_with_identical_clusters(8)  # plenty of merge candidates
    monitor = _FakeMonitor(engine, active_count=20)  # forces a trigger
    runner = BenchmarkRunner(dataset=_FixedDataset([0.0, 0.0]), monitor=monitor)

    runner.run_experiment({"num_ticks": 1})  # one tick -> one trigger

    tracker = runner.consolidation_tracker
    assert tracker.scheduler_triggers == 1
    # Capped at 3 even though 8 clusters could yield more merges.
    assert tracker.merges_committed == 3
    # 8 clusters - 3 fusions = 5 clusters remaining.
    assert engine.cluster_count == 5


# ---------------------------------------------------------------------------
# Task 3 -- Immediate quarantine replay (integration via the runner)
# ---------------------------------------------------------------------------


def test_quarantine_drain_runs_after_each_commit_and_resolves():
    """After a commit the runner drains the queue, counting + resolving anomalies."""
    engine = _engine_with_identical_clusters(8)
    # Pre-seed 5 active quarantined vectors near the origin: a merge frees a
    # slot and they are all within proximity, so the first drain re-homes them.
    seeded = [engine._open_quarantine([0.01, 0.01]) for _ in range(5)]
    assert engine.get_memory_summary()["active_anomalies_count"] == 5

    monitor = _FakeMonitor(engine, active_count=20)
    runner = BenchmarkRunner(dataset=_FixedDataset([0.0, 0.0]), monitor=monitor)
    runner.run_experiment({"num_ticks": 1})

    tracker = runner.consolidation_tracker
    assert tracker.merges_committed == 3
    # The first post-commit drain checked all 5 active records (counter > 0).
    assert tracker.quarantine_replayed == 5
    # Every seeded anomaly was re-homed (resolved), none left active.
    assert all(r.status == "absorbed" for r in seeded)
    assert engine.get_memory_summary()["active_anomalies_count"] == 0
    # No duplicate records were created by the drain.
    assert len(engine.anomaly_records) == 5


def test_drain_no_op_when_no_active_quarantine():
    """With nothing quarantined, the drain leaves quarantine_replayed at zero."""
    engine = _engine_with_identical_clusters(6)
    monitor = _FakeMonitor(engine, active_count=20)
    runner = BenchmarkRunner(dataset=_FixedDataset([0.0, 0.0]), monitor=monitor)
    runner.run_experiment({"num_ticks": 1})

    assert runner.consolidation_tracker.merges_committed == 3
    assert runner.consolidation_tracker.quarantine_replayed == 0
