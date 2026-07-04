"""
test_c8_decision_policy.py
==========================

Verification suite for the C8-final DecisionPolicy upgrade:

* The ReplayEngine is now a *pure simulator*: simulate_proposal returns a
  DecisionScore (before/after vitals) and renders no verdict; it never mutates
  the live engine.
* The DecisionPolicy renders the accept/reject judgement from the brain's
  native cognitive vitals — Free Energy Minimization by default, with a strict
  Pareto-dominance alternate strategy.
* E = H + 2S + 0.5A (lower-is-better), deltas = before - after.

Run from the repo root::

    python -m pytest test_c8_decision_policy.py -v
"""

from __future__ import annotations

import math

import pytest

from backend.cognition.decision_policy import (
    ACTIVE_LOAD,
    ENTROPY,
    PREDICTION_ERROR,
    STRATEGY_FREE_ENERGY,
    STRATEGY_PARETO,
    DecisionPolicy,
    DecisionScore,
)
from backend.cognition.replay_engine import ReplayEngine
from backend.cognition.vector_prediction_core import ClusterEngine


def _m(prediction, entropy, load):
    """Shorthand metric snapshot."""
    return {PREDICTION_ERROR: prediction, ENTROPY: entropy, ACTIVE_LOAD: load}


# ---------------------------------------------------------------------------
# Task 1 -- vital deltas + energy formula
# ---------------------------------------------------------------------------


def test_energy_formula_matches_E_equals_H_plus_2S_plus_half_A():
    """E = (1*H) + (2*S) + (0.5*A) with the default coefficients."""
    policy = DecisionPolicy()
    verdict = policy.evaluate_metrics(_m(3.0, 2.0, 4.0), _m(3.0, 2.0, 4.0))
    # E = 2*1 + 3*2 + 4*0.5 = 2 + 6 + 2 = 10
    assert verdict["energy_before"] == pytest.approx(10.0)
    assert verdict["energy_after"] == pytest.approx(10.0)


def test_deltas_are_before_minus_after():
    """Signed improvement is before - after for every vital (lower-is-better)."""
    policy = DecisionPolicy()
    before = _m(1.0, 2.0, 8.0)   # E = 2*1 + 2 + 4 = 8
    after = _m(0.5, 1.0, 7.0)    # E = 1 + 1 + 3.5 = 5.5
    verdict = policy.evaluate_metrics(before, after)
    assert verdict["delta_prediction"] == pytest.approx(0.5)
    assert verdict["delta_entropy"] == pytest.approx(1.0)
    assert verdict["delta_load"] == pytest.approx(1.0)
    assert verdict["delta_energy"] == pytest.approx(8.0 - 5.5)


# ---------------------------------------------------------------------------
# Task 2 -- Free Energy Minimization (default)
# ---------------------------------------------------------------------------


def test_free_energy_accepts_when_energy_decreases():
    policy = DecisionPolicy()
    verdict = policy.evaluate_metrics(_m(1.0, 1.0, 8.0), _m(1.0, 1.0, 6.0))
    assert verdict["accepted"] is True
    assert verdict["delta_energy"] > 0
    assert "free-energy accept" in verdict["reason"].lower()


def test_free_energy_accepts_on_exact_tie():
    """ΔE == 0 (energy_after == energy_before) is accepted (>= rule)."""
    policy = DecisionPolicy()
    verdict = policy.evaluate_metrics(_m(1.0, 1.0, 4.0), _m(1.0, 1.0, 4.0))
    assert verdict["accepted"] is True
    assert verdict["delta_energy"] == pytest.approx(0.0)


def test_free_energy_rejects_when_energy_increases():
    policy = DecisionPolicy()
    # Surprise rises sharply; energy goes up despite one fewer cluster.
    verdict = policy.evaluate_metrics(_m(0.0, 0.5, 2.0), _m(7.0, 0.0, 1.0))
    assert verdict["accepted"] is False
    assert verdict["delta_energy"] < 0
    assert "reject" in verdict["reason"].lower()


def test_free_energy_tolerance_allows_small_regression():
    policy = DecisionPolicy(tolerance=1.0)
    # ΔE = -0.5 (small regression) within tolerance 1.0 -> accepted.
    verdict = policy.evaluate_metrics(_m(0.0, 0.0, 2.0), _m(0.25, 0.0, 2.0))
    assert verdict["delta_energy"] == pytest.approx(-0.5)
    assert verdict["accepted"] is True


# ---------------------------------------------------------------------------
# Task 2 -- strict Pareto Dominance (alternate strategy)
# ---------------------------------------------------------------------------


def test_pareto_rejects_only_when_all_four_vitals_worsen():
    policy = DecisionPolicy(strategy=STRATEGY_PARETO)
    # Every vital gets worse (after > before on all of S, H, A => E too).
    verdict = policy.evaluate_metrics(_m(1.0, 1.0, 2.0), _m(2.0, 2.0, 4.0))
    assert verdict["accepted"] is False
    assert "dominated" in verdict["reason"].lower()


def test_pareto_accepts_when_any_single_vital_improves():
    policy = DecisionPolicy(strategy=STRATEGY_PARETO)
    # Surprise and entropy worsen, but load improves (fewer clusters) -> survives.
    verdict = policy.evaluate_metrics(_m(1.0, 1.0, 8.0), _m(2.0, 2.0, 4.0))
    assert verdict["accepted"] is True
    assert "accept" in verdict["reason"].lower()


def test_pareto_and_free_energy_can_disagree():
    """A merge that raises energy but improves load: pareto keeps, free-energy drops."""
    before = _m(0.0, 0.0, 4.0)   # E = 2.0
    after = _m(5.0, 0.0, 3.0)    # E = 10 + 1.5 = 11.5 (energy worse, load better)
    assert DecisionPolicy().evaluate_metrics(before, after)["accepted"] is False
    assert (
        DecisionPolicy(strategy=STRATEGY_PARETO)
        .evaluate_metrics(before, after)["accepted"]
        is True
    )


def test_invalid_strategy_and_tolerance_raise():
    with pytest.raises(ValueError):
        DecisionPolicy(strategy="bogus")
    with pytest.raises(ValueError):
        DecisionPolicy(tolerance=-0.1)


def test_decide_unpacks_a_decision_score():
    policy = DecisionPolicy()
    score = DecisionScore(
        metrics_before=_m(1.0, 1.0, 8.0), metrics_after=_m(1.0, 1.0, 6.0)
    )
    assert policy.decide(score)["accepted"] is True


# ---------------------------------------------------------------------------
# Task 3 -- ReplayEngine is a pure simulator returning a DecisionScore
# ---------------------------------------------------------------------------


def _two_identical_clusters():
    engine = ClusterEngine(proximity_threshold=0.25, max_clusters=10)
    engine._create_cluster([0.0, 0.0])  # id 0
    engine._create_cluster([0.0, 0.0])  # id 1 (identical)
    return engine


def test_simulate_returns_before_after_vitals_and_no_decision():
    engine = _two_identical_clusters()
    recent = [[0.0, 0.0]] * 5
    score = ReplayEngine().simulate_proposal(
        engine, {"target_a": 0, "target_b": 1}, recent
    )

    assert isinstance(score, DecisionScore)
    for snap in (score.metrics_before, score.metrics_after):
        assert set(snap) == {PREDICTION_ERROR, ENTROPY, ACTIVE_LOAD}
    # Merging the two clusters removes one => active_load drops by exactly 1.
    assert score.metrics_before[ACTIVE_LOAD] == pytest.approx(2.0)
    assert score.metrics_after[ACTIVE_LOAD] == pytest.approx(1.0)
    # Identical clusters at the origin: surprise and entropy are flat at zero.
    assert score.metrics_before[PREDICTION_ERROR] == pytest.approx(0.0)
    assert score.metrics_after[PREDICTION_ERROR] == pytest.approx(0.0)
    assert score.metrics_before[ENTROPY] == pytest.approx(0.0)
    assert score.metrics_after[ENTROPY] == pytest.approx(0.0)
    # The DecisionScore carries no verdict field — the engine renders none.
    assert not hasattr(score, "accepted")


def test_simulate_does_not_mutate_the_live_engine():
    engine = _two_identical_clusters()
    before_count = engine.cluster_count
    ReplayEngine().simulate_proposal(
        engine, {"target_a": 0, "target_b": 1}, [[0.0, 0.0]]
    )
    assert engine.cluster_count == before_count  # live engine untouched


def test_commit_proposal_mutates_live_engine():
    engine = _two_identical_clusters()
    ReplayEngine().commit_proposal(engine, {"target_a": 0, "target_b": 1})
    assert engine.cluster_count == 1  # two fused into one


def test_policy_accepts_beneficial_merge_from_simulation():
    """End-to-end: identical-cluster merge lowers energy (fewer clusters)."""
    engine = _two_identical_clusters()
    score = ReplayEngine().simulate_proposal(
        engine, {"target_a": 0, "target_b": 1}, [[0.0, 0.0]] * 5
    )
    verdict = DecisionPolicy().evaluate_metrics(
        score.metrics_before, score.metrics_after
    )
    assert verdict["accepted"] is True
    assert verdict["delta_load"] == pytest.approx(1.0)


def test_policy_rejects_merge_that_spikes_surprise():
    """Fusing two well-separated clusters wrecks prediction => free-energy reject."""
    engine = ClusterEngine(proximity_threshold=0.25, max_clusters=10)
    engine._create_cluster([0.0, 0.0])    # id 0
    engine._create_cluster([10.0, 10.0])  # id 1
    recent = [[0.0, 0.0], [0.0, 0.0], [10.0, 10.0], [10.0, 10.0]]

    score = ReplayEngine().simulate_proposal(
        engine, {"target_a": 0, "target_b": 1}, recent
    )
    # Sanity: surprise must rise materially after the merge.
    assert score.metrics_after[PREDICTION_ERROR] > score.metrics_before[PREDICTION_ERROR]

    verdict = DecisionPolicy().evaluate_metrics(
        score.metrics_before, score.metrics_after
    )
    assert verdict["accepted"] is False
    assert verdict["delta_energy"] < 0
