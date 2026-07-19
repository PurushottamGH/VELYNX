"""
test_shared_metrics_v1.py
=========================

Reference tests for the R3C canonical cognitive-metric layer
(``validation/shared_metrics_v1.py``).

Phase 3 of the R3C refactor protocol -- independent mathematics-only tests.
No Replay, no Online pipeline, no fixtures. These tests verify the *pure*
definitions of:

    S -- compute_S_surprise           (Markov forecast error)
    R -- compute_R_representation_error (nearest-centroid distance)
    H -- compute_H_global             (Markov chain entropy)
    H -- compute_H_local              (window-induced transition entropy)
    A -- compute_A_active_load        (cluster count + anomaly volume)

Each test specifies the expected value by hand from first principles so a
silent regression in the canonical layer is detectable.

Run::

    python -m pytest test_shared_metrics_v1.py -v
"""

from __future__ import annotations

import math

import pytest

from validation.shared_metrics_v1 import (
    METRICS_VERSION,
    MetricDefinition,
    compute_A_active_load,
    compute_H_global,
    compute_H_local,
    compute_R_representation_error,
    compute_S_surprise,
)


# ---------------------------------------------------------------------------
# Version contract
# ---------------------------------------------------------------------------


def test_metrics_version_is_v1():
    """The canonical layer is version v1 and must declare so explicitly."""
    assert METRICS_VERSION == "v1"
    assert MetricDefinition().version == "v1"


def test_metric_definition_is_frozen():
    """The contract dataclass must be immutable to lock the canonical surface."""
    with pytest.raises(Exception):
        MetricDefinition().version = "v2"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# S -- Markov forecast error
# ---------------------------------------------------------------------------


def test_S_zero_when_vectors_identical():
    """S = 0 iff predicted == observed."""
    assert compute_S_surprise([0.0, 0.0], [0.0, 0.0]) == 0.0
    assert compute_S_surprise([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 0.0


def test_S_3_4_5_right_triangle():
    """||[3,0,0] - [0,4,0]|| == 5."""
    assert compute_S_surprise([3.0, 0.0, 0.0], [0.0, 4.0, 0.0]) == pytest.approx(5.0)


def test_S_unit_distance_axis_aligned():
    """||[1,0,0] - [0,0,0]|| == 1."""
    assert compute_S_surprise([1.0, 0.0, 0.0], [0.0, 0.0, 0.0]) == pytest.approx(1.0)


def test_S_is_symmetric():
    """||a - b|| == ||b - a|| (Euclidean symmetry)."""
    a, b = [1.5, -2.0, 0.7], [-0.3, 4.1, 2.0]
    assert compute_S_surprise(a, b) == pytest.approx(compute_S_surprise(b, a))


def test_S_is_zero_on_empty_inputs():
    """Defensive: empty predicted or empty observed returns 0."""
    assert compute_S_surprise([], [1.0, 2.0]) == 0.0
    assert compute_S_surprise([1.0, 2.0], []) == 0.0
    assert compute_S_surprise([], []) == 0.0


def test_S_higher_dimensional_hand_check():
    """||[1,1,1,1] - [0,0,0,0]|| == 2."""
    assert compute_S_surprise([1.0, 1.0, 1.0, 1.0], [0.0, 0.0, 0.0, 0.0]) == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# R -- Representation error (nearest-centroid distance)
# ---------------------------------------------------------------------------


def test_R_zero_when_observation_matches_a_centroid():
    """If the observation exactly equals a centroid, R = 0."""
    centroids = [[0.0, 0.0], [5.0, 5.0]]
    assert compute_R_representation_error(centroids, [0.0, 0.0]) == 0.0
    assert compute_R_representation_error(centroids, [5.0, 5.0]) == 0.0


def test_R_picks_nearest_centroid():
    """R selects the centroid with minimum distance."""
    centroids = [[0.0, 0.0], [10.0, 10.0]]
    # observation [1,1] is distance 1.414 from [0,0] and 12.73 from [10,10]
    assert compute_R_representation_error(centroids, [1.0, 1.0]) == pytest.approx(math.sqrt(2.0))
    # observation [9,9] is distance 12.73 from [0,0] and 1.414 from [10,10]
    assert compute_R_representation_error(centroids, [9.0, 9.0]) == pytest.approx(math.sqrt(2.0))


def test_R_three_centroids_midpoint():
    """With three centroids the nearest wins."""
    centroids = [[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]]
    # observation [5,5] -> all distances are ~7.07
    d = math.sqrt(50.0)
    assert compute_R_representation_error(centroids, [5.0, 5.0]) == pytest.approx(d)
    # observation [1,1] -> nearest is [0,0] at sqrt(2)
    assert compute_R_representation_error(centroids, [1.0, 1.0]) == pytest.approx(math.sqrt(2.0))


def test_R_zero_when_no_centroids():
    """Empty centroids: defensive return 0 (no basis for representation)."""
    assert compute_R_representation_error([], [1.0, 2.0]) == 0.0


def test_R_attention_weights_amplify_weighted_dim():
    """With dim_weights, the weighted distance is computed, not the raw L2.

    The function returns the *minimum* over centroids, so we must pick an
    observation whose nearest-centroid is the far-away one (otherwise the
    nearer centroid wins with distance 0).
    """
    centroids = [[0.0, 0.0], [3.0, 4.0]]
    weights = [1.0, 100.0]  # heavy weight on dim 1
    # Observation [3, 4] sits exactly on centroid [3,4] -> weighted distance 0.
    assert compute_R_representation_error(centroids, [3.0, 4.0], dim_weights=weights) == pytest.approx(0.0)
    # Observation [0, 0] sits on centroid [0,0] -> weighted distance 0 (nearest wins).
    assert compute_R_representation_error(centroids, [0.0, 0.0], dim_weights=weights) == pytest.approx(0.0)
    # Observation [6, 0]: to [0,0] weighted = sqrt(1*36 + 100*0) = 6;
    #                    to [3,4] weighted = sqrt(1*9 + 100*16) = 40.11.
    # Nearest is [0,0] at 6.
    assert compute_R_representation_error(centroids, [6.0, 0.0], dim_weights=weights) == pytest.approx(6.0)
    # Observation [0, 8]: to [0,0] weighted = sqrt(1*0 + 100*64) = 80;
    #                    to [3,4] weighted = sqrt(1*9 + 100*16) = 40.11.
    # Nearest is [3,4] at sqrt(1609).
    assert compute_R_representation_error(centroids, [0.0, 8.0], dim_weights=weights) == pytest.approx(math.sqrt(1609.0))


# ---------------------------------------------------------------------------
# H_global -- Markov chain entropy
# ---------------------------------------------------------------------------


def test_H_global_zero_on_empty_matrix():
    assert compute_H_global({}) == 0.0


def test_H_global_zero_on_no_transitions():
    """A chain with one source -> one target with 100% probability has H = 0."""
    assert compute_H_global({0: {1: 10}}) == 0.0


def test_H_global_deterministic_chain_is_zero():
    """Deterministic chain: H = 0."""
    # 0 -> 1 (always), 1 -> 2 (always)
    matrix = {0: {1: 5}, 1: {2: 7}}
    assert compute_H_global(matrix) == 0.0


def test_H_global_equiprobable_two_targets():
    """0 -> {1:5, 2:5}, nothing else.  H(0) = 1 bit, weight = 10/10 = 1.0.
    Expected H_global = 1.0.
    """
    matrix = {0: {1: 5, 2: 5}}
    assert compute_H_global(matrix) == pytest.approx(1.0)


def test_H_global_equiprobable_three_targets():
    """0 -> {1:4, 2:4, 3:4}. H(0) = log2(3) ~ 1.58496.
    Only source is 0, weight 1.0. Expected H_global = log2(3).
    """
    matrix = {0: {1: 4, 2: 4, 3: 4}}
    assert compute_H_global(matrix) == pytest.approx(math.log2(3.0))


def test_H_global_uniform_chain():
    """Two sources each equiprobable over two targets.
    0 -> {a:5, b:5}   H(0) = 1, weight 10
    1 -> {a:5, b:5}   H(1) = 1, weight 10
    H_global = (10*1 + 10*1) / 20 = 1.0
    """
    matrix = {0: {"a": 5, "b": 5}, 1: {"a": 5, "b": 5}}
    assert compute_H_global(matrix) == pytest.approx(1.0)


def test_H_global_weighted_mixed_uncertainty():
    """Mixed deterministic and equiprobable rows.

    Matrix: {0: {x: 100}, 1: {a: 25, b: 25, c: 25, d: 25}}
    total_transitions = 200.
    Row 0 weight = 100/200 = 0.5, entropy = 0.
    Row 1 weight = 100/200 = 0.5, entropy = log2(4) = 2.
    H_global = 0.5 * 0 + 0.5 * 2 = 1.0
    """
    matrix = {0: {"x": 100}, 1: {"a": 25, "b": 25, "c": 25, "d": 25}}
    assert compute_H_global(matrix) == pytest.approx(1.0)


def test_H_global_uneven_row_weights():
    """Confirm the weighting scheme by using uneven row totals.

    Matrix: {0: {a: 1, b: 1}, 1: {a: 8}}
    total_transitions = 10.
    Row 0 weight = 2/10 = 0.2, entropy = 1 bit.
    Row 1 weight = 8/10 = 0.8, entropy = 0.
    H_global = 0.2 * 1 + 0.8 * 0 = 0.2
    """
    matrix = {0: {"a": 1, "b": 1}, 1: {"a": 8}}
    assert compute_H_global(matrix) == pytest.approx(0.2)


# ---------------------------------------------------------------------------
# H_local -- window-induced transition entropy
# ---------------------------------------------------------------------------


def test_H_local_zero_on_short_sequence():
    """Fewer than 2 cluster ids -> H_local = 0."""
    assert compute_H_local([]) == 0.0
    assert compute_H_local([7]) == 0.0


def test_H_local_deterministic_alternation():
    """0,1,0,1,0,1 -> transitions {0:{1:3}, 1:{0:3}}. H = 0."""
    assert compute_H_local([0, 1, 0, 1, 0, 1]) == 0.0


def test_H_local_two_state_equiprobable():
    """0,1,2,0,1,2 -> transitions {0:{1:2}, 1:{2:2}, 2:{0:2}}.
    Each row has exactly one target, so each row's entropy is 0.
    H_local = 0 (chain is deterministic despite 3 states).
    """
    assert compute_H_local([0, 1, 2, 0, 1, 2]) == 0.0


def test_H_local_branching_decision_point():
    """Sequence [0,1,0,2,0,1,0,2] -- consecutive pairs:
    (0,1),(1,0),(0,2),(2,0),(0,1),(1,0),(0,2)  -> 7 transitions.
    Matrix:
        0: {1:2, 2:2}    row total 4, H = 1 bit
        1: {0:2}         row total 2, H = 0
        2: {0:1}         row total 1, H = 0
    total_transitions = 7.
    H_global = (4*1 + 2*0 + 1*0) / 7 = 4/7
    """
    assert compute_H_local([0, 1, 0, 2, 0, 1, 0, 2]) == pytest.approx(4.0 / 7.0)


def test_H_local_uses_same_definition_as_H_global():
    """H_local(seq) == H_global(matrix built from seq)."""
    seq = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    h_loc = compute_H_local(seq)
    # Build matrix by hand.
    matrix = {}
    for s, d in zip(seq[:-1], seq[1:]):
        matrix.setdefault(s, {})
        matrix[s][d] = matrix[s].get(d, 0) + 1
    h_glob = compute_H_global(matrix)
    assert h_loc == pytest.approx(h_glob)


# ---------------------------------------------------------------------------
# A -- Active load (R3C-reconciled)
# ---------------------------------------------------------------------------


def test_A_is_cluster_count_when_no_anomalies():
    """anomaly_volume = 0 -> A = cluster_count."""
    assert compute_A_active_load(0, 0.0) == 0.0
    assert compute_A_active_load(7, 0.0) == 7.0


def test_A_adds_linear_volume():
    """A = cluster_count + anomaly_volume (linear, NOT power-1.5)."""
    assert compute_A_active_load(3, 2.0) == pytest.approx(5.0)
    assert compute_A_active_load(5, 0.5) == pytest.approx(5.5)


def test_A_does_not_use_power_1_5():
    """Defensive: explicitly verify the formula is NOT the orphan **1.5 form.
    2.0 ** 1.5 = 2.828..., so c + v**1.5 would give a different value.
    R3C canonical must give c + v.
    """
    cluster_count, anomaly_volume = 4, 9.0
    expected = cluster_count + anomaly_volume  # linear
    not_expected = cluster_count + anomaly_volume ** 1.5  # orphan (forbidden)
    assert compute_A_active_load(cluster_count, anomaly_volume) == pytest.approx(expected)
    assert compute_A_active_load(cluster_count, anomaly_volume) != pytest.approx(not_expected)


def test_A_returns_float():
    """API contract: returns float (not int)."""
    result = compute_A_active_load(2, 0.0)
    assert isinstance(result, float)