"""
research/tests/test_policies.py
===============================

Unit tests for the :class:`ConsolidationPolicy` family and registry.
"""

from __future__ import annotations

import random

import pytest

from backend.cognition.decision_policy import DecisionScore
from backend.cognition.vector_prediction_core import ClusterEngine
from research.policies import (
    DEFAULT_POLICY_ORDER,
    FreeEnergyPolicy,
    OracleNotImplementedError,
    PlaceholderOraclePolicy,
    available_policies,
    build_policy,
)
from research.policies.base import PolicyContext


def _engine_with_clusters():
    """Build a real ClusterEngine with three well-separated clusters.

    Assignments: cluster 0 gets two vectors (count=2), clusters 1 and 2 get one
    each (count=1). Ids are monotonic 0,1,2 (so 0 is oldest).
    """
    eng = ClusterEngine(proximity_threshold=0.1, auto_seed=True, max_clusters=10)
    eng.assign([0.0, 0.0])     # -> cluster 0
    eng.assign([0.02, 0.0])    # within 0.1 -> updates cluster 0 (count=2)
    eng.assign([5.0, 0.0])     # -> cluster 1
    eng.assign([10.0, 0.0])    # -> cluster 2
    return eng


def _ctx(seed: int = 0) -> PolicyContext:
    return PolicyContext(rng=random.Random(seed), tick=0,
                         energy_weights={"lam": 1.0, "mu": 2.0, "nu": 0.5})


def test_registry_contains_all_policies():
    names = available_policies()
    for expected in ["null", "random", "fifo", "similarity", "utility",
                     "free_energy", "oracle"]:
        assert expected in names
    # The default ablation order excludes the oracle.
    assert "oracle" not in DEFAULT_POLICY_ORDER
    assert DEFAULT_POLICY_ORDER[0] == "null"
    assert DEFAULT_POLICY_ORDER[-1] == "free_energy"


def test_build_policy_unknown_raises():
    with pytest.raises(KeyError):
        build_policy("does_not_exist")


def test_null_never_proposes():
    pol = build_policy("null")
    assert pol.select_candidate(_engine_with_clusters(), _ctx()) is None


def test_fifo_selects_oldest_pair():
    pol = build_policy("fifo")
    prop = pol.select_candidate(_engine_with_clusters(), _ctx())
    assert prop is not None
    assert {prop.target_a, prop.target_b} == {0, 1}  # two lowest ids


def test_utility_selects_lowest_count_pair():
    pol = build_policy("utility")
    prop = pol.select_candidate(_engine_with_clusters(), _ctx())
    assert prop is not None
    # Clusters 1 and 2 have count=1 (lowest); cluster 0 has count=2.
    assert {prop.target_a, prop.target_b} == {1, 2}


def test_similarity_selects_nearest_pair():
    pol = build_policy("similarity")
    prop = pol.select_candidate(_engine_with_clusters(), _ctx())
    assert prop is not None
    # Nearest centroids: 0@x=0.01 and 1@x=5 (dist 5) tie with 1@5 and 2@10
    # (dist 5); the generator scans upper-triangle and keeps the first minimum,
    # which is the (0,1) pair.
    assert {prop.target_a, prop.target_b} == {0, 1}
    assert prop.strategy == "similarity"


def test_random_is_nondeterministic_flag_and_valid_pair():
    pol = build_policy("random")
    assert pol.is_deterministic is False
    prop = pol.select_candidate(_engine_with_clusters(), _ctx(seed=1))
    assert prop is not None
    assert prop.target_a != prop.target_b


def test_random_selection_reproducible_with_same_seed():
    eng = _engine_with_clusters()
    p1 = build_policy("random").select_candidate(eng, _ctx(seed=42))
    p2 = build_policy("random").select_candidate(_engine_with_clusters(), _ctx(seed=42))
    assert (p1.target_a, p1.target_b) == (p2.target_a, p2.target_b)


def test_unconditional_policies_accept():
    ctx = _ctx()
    score = DecisionScore(metrics_before={}, metrics_after={})
    for name in ["random", "fifo", "similarity", "utility"]:
        accepted, reason = build_policy(name).accept(score, ctx)
        assert accepted is True
        assert isinstance(reason, str) and reason


def test_free_energy_accepts_when_energy_falls():
    pol = FreeEnergyPolicy()
    # after has strictly lower vitals -> energy falls -> accept.
    score = DecisionScore(
        metrics_before={"prediction_error": 1.0, "entropy": 1.0, "active_load": 4.0},
        metrics_after={"prediction_error": 0.5, "entropy": 0.5, "active_load": 3.0},
    )
    accepted, reason = pol.accept(score, _ctx())
    assert accepted is True
    assert "free" in reason.lower()


def test_free_energy_rejects_when_energy_rises():
    pol = FreeEnergyPolicy()
    score = DecisionScore(
        metrics_before={"prediction_error": 0.5, "entropy": 0.5, "active_load": 3.0},
        metrics_after={"prediction_error": 1.0, "entropy": 1.0, "active_load": 4.0},
    )
    accepted, _ = pol.accept(score, _ctx())
    assert accepted is False


def test_free_energy_describe_exposes_energy_function():
    info = FreeEnergyPolicy(lam=1.0, mu=2.0, nu=0.5).describe()
    assert info["name"] == "free_energy"
    assert info["energy"]["mu"] == 2.0
    assert "E = lambda*H" in info["energy"]["formula"]


def test_oracle_is_not_implemented():
    pol = build_policy("oracle")
    assert isinstance(pol, PlaceholderOraclePolicy)
    assert "not implemented" in pol.description.lower()
    with pytest.raises(OracleNotImplementedError):
        pol.select_candidate(_engine_with_clusters(), _ctx())


def test_policies_do_not_import_each_other():
    """Structural check: no policy module imports a sibling policy module."""
    import importlib
    import pkgutil
    import research.policies as pkg

    sibling_names = {"null", "random_policy", "fifo", "similarity", "utility",
                     "free_energy", "oracle"}
    for mod_info in pkgutil.iter_modules(pkg.__path__):
        if mod_info.name not in sibling_names:
            continue
        mod = importlib.import_module(f"research.policies.{mod_info.name}")
        src = mod.__file__
        with open(src, "r", encoding="utf-8") as fh:
            text = fh.read()
        for other in sibling_names - {mod_info.name}:
            assert f"research.policies.{other}" not in text, (
                f"{mod_info.name} imports sibling policy {other}"
            )
