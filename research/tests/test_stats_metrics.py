"""
research/tests/test_stats_metrics.py
=====================================

Unit tests for the statistics layer and the metric registry/aggregation.
"""

from __future__ import annotations

import math

from research.metrics import (
    METRICS_BY_NAME,
    aggregate,
    available_metrics,
    extract_all,
    metrics_for,
    PRIMARY,
)
from research.stats import (
    BootstrapMeanDifferenceTest,
    SummaryStatistics,
    build_test,
    t_critical_95,
)


# -- SummaryStatistics ------------------------------------------------------

def test_summary_basic_values():
    s = SummaryStatistics.from_samples([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert s.n == 8
    assert math.isclose(s.mean, 5.0)
    assert math.isclose(s.median, 4.5)
    assert math.isclose(s.std, 2.138, abs_tol=1e-3)  # sample stdev
    assert s.minimum == 2.0
    assert s.maximum == 9.0
    assert s.ci95_low < s.mean < s.ci95_high


def test_summary_empty_is_null():
    s = SummaryStatistics.from_samples([])
    assert s.n == 0
    assert s.mean is None and s.ci95_low is None and s.std is None


def test_summary_single_sample_has_zero_spread():
    s = SummaryStatistics.from_samples([3.0])
    assert s.n == 1
    assert s.std == 0.0
    assert s.ci95_low == s.ci95_high == 3.0


def test_summary_drops_none_entries():
    s = SummaryStatistics.from_samples([1.0, None, 3.0])
    assert s.n == 2
    assert math.isclose(s.mean, 2.0)


def test_t_critical_table_and_fallback():
    assert math.isclose(t_critical_95(1), 12.706)
    assert math.isclose(t_critical_95(4), 2.776)
    # Large df falls back toward the normal z.
    assert math.isclose(t_critical_95(100000), 1.96)


# -- Hypothesis tests -------------------------------------------------------

def test_bootstrap_identical_samples_not_significant():
    t = BootstrapMeanDifferenceTest(iterations=2000, seed=0)
    data = [1.0, 1.1, 0.9, 1.05, 0.95]
    res = t.compare(data, list(data))
    assert abs(res.effect) < 1e-9
    assert res.p_value is not None and res.p_value > 0.2


def test_bootstrap_separated_samples_significant():
    t = BootstrapMeanDifferenceTest(iterations=4000, seed=0)
    baseline = [10.0, 10.2, 9.8, 10.1, 9.9]
    treatment = [1.0, 1.2, 0.8, 1.1, 0.9]
    res = t.compare(baseline, treatment)
    assert res.effect < 0  # treatment lower than baseline
    assert res.p_value is not None and res.p_value < 0.05


def test_bootstrap_empty_group_returns_null():
    t = BootstrapMeanDifferenceTest(iterations=100, seed=0)
    res = t.compare([], [1.0, 2.0])
    assert res.effect is None and res.p_value is None


def test_build_test_registry():
    t = build_test("bootstrap_mean_difference", iterations=10, seed=1)
    assert isinstance(t, BootstrapMeanDifferenceTest)


# -- Metric registry --------------------------------------------------------

def test_unavailable_primary_metrics_extract_none():
    record = {"prediction_rmse": 0.3}
    extracted = extract_all(record)
    # The one available primary metric is present...
    assert extracted["PredictionRMSE"] == 0.3
    # ...the rest of the primary tier is honestly unavailable.
    for name in ["HeldOutPredictiveLogLikelihood", "RareEventRecall",
                 "KnowledgeRetentionScore", "GeneralizationScore", "TransferScore"]:
        assert extracted[name] is None
        assert METRICS_BY_NAME[name].available is False


def test_available_metrics_exclude_unavailable():
    names = {m.name for m in available_metrics()}
    assert "PredictionRMSE" in names
    assert "HeldOutPredictiveLogLikelihood" not in names


def test_aggregate_produces_summary_per_metric():
    records = [
        {"prediction_rmse": 0.30, "final_energy": 19.0, "final_cluster_count": 40},
        {"prediction_rmse": 0.32, "final_energy": 19.4, "final_cluster_count": 41},
        {"prediction_rmse": 0.28, "final_energy": 18.6, "final_cluster_count": 39},
    ]
    agg = aggregate(records)
    assert agg["PredictionRMSE"].n == 3
    assert math.isclose(agg["PredictionRMSE"].mean, 0.30, abs_tol=1e-9)
    # An unavailable metric aggregates to an empty summary, never a fake number.
    assert agg["RareEventRecall"].n == 0
    assert agg["RareEventRecall"].mean is None


def test_metrics_for_filters_by_category():
    primaries = metrics_for(PRIMARY)
    assert all(m.category == PRIMARY for m in primaries)
    assert any(m.name == "PredictionRMSE" for m in primaries)
