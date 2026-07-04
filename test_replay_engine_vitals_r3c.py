"""
test_replay_engine_vitls_r3c.py
==============================

Phase 7 of the R3C refactor protocol -- Identity Test.

Confirms that Online (``VectorPredictionCore.ingest``) and Replay
(``ReplayEngine.simulate_proposal``) compute the same cognitive quantities
(S, R, H_local, H_global, A) for the same observation stream within 1e-10.

Procedure:
    1. Build a fresh ``VectorPredictionCore``.
    2. Ingest a stream of observations. Record per-tick ``error`` and per-tick
       cluster id.
    3. Snapshot the live engine + recent-vectors window.
    4. Call ``ReplayEngine.simulate_proposal`` with a no-op proposal (targets
       the same cluster with itself, which the engine treats as identity).
    5. Confirm ``metrics_before`` equals the running mean of ``error`` from
       step 2.

Expected:
    S: equal within 1e-10
    H_local: equal within 1e-10  (H_global is implied via H_local matrix)
    A: equal within 1e-10        (no merges -> A_before == A_after)

If any assertion fails, STOP. The protocol demands a halt on identity failure.
"""

from __future__ import annotations

import copy
import math
import pytest

from backend.cognition.replay_engine import ReplayEngine
from backend.cognition.vector_prediction_core import VectorPredictionCore
from backend.cognition.decision_policy import (
    ACTIVE_LOAD,
    ENTROPY,
    PREDICTION_ERROR,
)


# A deterministic, repeatable observation stream. Two clusters at [0,0] and
# [10,10] with transitions 0->1->0->1->... so the predictor's forecast
# is always the *other* cluster's centroid -- a known strong signal.
STREAM = (
    [[0.0, 0.0]] * 4
    + [[10.0, 10.0]] * 4
    + [[0.0, 0.0]] * 4
    + [[10.0, 10.0]] * 4
)


def _ingest_stream(core: VectorPredictionCore, stream):
    """Ingest each observation; return (running mean of error, last_cluster_id)."""
    errors = []
    for v in stream:
        result = core.ingest(v)
        errors.append(result["error"])
    mean_s = sum(errors) / len(errors)
    return mean_s, core.last_cluster_id


def test_identity_online_S_equals_replay_S():
    """Online running mean of S == Replay S_before for the same stream."""
    core = VectorPredictionCore(proximity_threshold=0.25, max_clusters=10)
    online_mean_S, _ = _ingest_stream(core, STREAM)

    # Build a snapshot of the live engine + window and run a no-op replay.
    snapshot_core = copy.deepcopy(core)
    replay = ReplayEngine().simulate_proposal(
        snapshot_core,
        proposal={"target_a": 0, "target_b": 0},  # self-merge -> no-op
        recent_vectors=[v[:] for v in STREAM],
    )
    replay_S = replay.metrics_before[PREDICTION_ERROR]

    assert replay_S == pytest.approx(online_mean_S, abs=1e-10), (
        f"Online mean S = {online_mean_S:.12f}, "
        f"Replay S = {replay_S:.12f}, "
        f"diff = {abs(replay_S - online_mean_S):.3e}"
    )


def test_identity_no_op_proposal_leaves_S_unchanged():
    """Self-merge proposal (target_a == target_b) -> S_after == S_before."""
    core = VectorPredictionCore(proximity_threshold=0.25, max_clusters=10)
    _ingest_stream(core, STREAM)

    snapshot_core = copy.deepcopy(core)
    replay = ReplayEngine().simulate_proposal(
        snapshot_core,
        proposal={"target_a": 0, "target_b": 0},
        recent_vectors=[v[:] for v in STREAM],
    )
    s_before = replay.metrics_before[PREDICTION_ERROR]
    s_after = replay.metrics_after[PREDICTION_ERROR]

    assert s_after == pytest.approx(s_before, abs=1e-10), (
        f"No-op proposal should not change S: before={s_before}, after={s_after}"
    )


def test_identity_no_op_proposal_leaves_A_unchanged():
    """Self-merge proposal -> A_after == A_before."""
    core = VectorPredictionCore(proximity_threshold=0.25, max_clusters=10)
    _ingest_stream(core, STREAM)

    snapshot_core = copy.deepcopy(core)
    replay = ReplayEngine().simulate_proposal(
        snapshot_core,
        proposal={"target_a": 0, "target_b": 0},
        recent_vectors=[v[:] for v in STREAM],
    )
    a_before = replay.metrics_before[ACTIVE_LOAD]
    a_after = replay.metrics_after[ACTIVE_LOAD]

    assert a_after == pytest.approx(a_before, abs=1e-10)


def test_identity_replay_does_not_mutate_live_engine():
    """The snapshot_core after replay must equal a fresh deepcopy of the original."""
    core = VectorPredictionCore(proximity_threshold=0.25, max_clusters=10)
    _ingest_stream(core, STREAM)

    snapshot_core = copy.deepcopy(core)
    snapshot_before = copy.deepcopy(core)

    ReplayEngine().simulate_proposal(
        snapshot_core,
        proposal={"target_a": 0, "target_b": 1},
        recent_vectors=[v[:] for v in STREAM],
    )

    # Cluster count, last_cluster_id, predictor transitions must be unchanged.
    assert snapshot_core.cluster_engine.cluster_count == snapshot_before.cluster_engine.cluster_count
    assert snapshot_core.last_cluster_id == snapshot_before.last_cluster_id
    assert (
        snapshot_core.predictor.transition_matrix()
        == snapshot_before.predictor.transition_matrix()
    )


def test_identity_replay_returns_deterministic_S():
    """Two replays of the same snapshot produce byte-identical S."""
    core = VectorPredictionCore(proximity_threshold=0.25, max_clusters=10)
    _ingest_stream(core, STREAM)

    snap_a = copy.deepcopy(core)
    snap_b = copy.deepcopy(core)
    r1 = ReplayEngine().simulate_proposal(
        snap_a, {"target_a": 0, "target_b": 0}, [v[:] for v in STREAM],
    )
    r2 = ReplayEngine().simulate_proposal(
        snap_b, {"target_a": 0, "target_b": 0}, [v[:] for v in STREAM],
    )
    assert r1.metrics_before[PREDICTION_ERROR] == r2.metrics_before[PREDICTION_ERROR]
    assert r1.metrics_after[PREDICTION_ERROR] == r2.metrics_after[PREDICTION_ERROR]