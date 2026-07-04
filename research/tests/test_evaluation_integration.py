"""
research/tests/test_evaluation_integration.py
=============================================

Integration tests for the R2A wiring: the :class:`EvaluationProtocol` attached
to a :class:`RunConfig`, exercised through :func:`run_single`, surfacing as the
``HeldOutPredictiveRMSE`` metric.

Short runs (700 ticks) so the scheduler's time-trigger fires once, matching the
existing runner integration suite.
"""

from __future__ import annotations

from research.evaluation.protocol import HELD_OUT_RMSE_KEY, EvaluationProtocol
from research.metrics import METRICS_BY_NAME, PRIMARY, extract_all
from research.runner import RunConfig, run_single

TICKS = 700


def test_run_without_protocol_has_no_held_out_key():
    r = run_single(RunConfig(policy="free_energy", seed=1, num_ticks=TICKS))
    assert HELD_OUT_RMSE_KEY not in r.measurements
    # The metric still extracts cleanly as "not measured" (None), never faked.
    assert extract_all(r.measurements)["HeldOutPredictiveRMSE"] is None


def test_run_with_protocol_populates_held_out_rmse():
    proto = EvaluationProtocol(train_seed=1, num_probe_ticks=120)
    r = run_single(
        RunConfig(
            policy="free_energy", seed=1, num_ticks=TICKS,
            evaluation_protocol=proto,
        )
    )
    assert HELD_OUT_RMSE_KEY in r.measurements
    value = r.measurements[HELD_OUT_RMSE_KEY]
    assert isinstance(value, float) and value > 0.0
    assert extract_all(r.measurements)["HeldOutPredictiveRMSE"] == value


def test_held_out_rmse_metric_is_registered_primary_lower_is_better():
    spec = METRICS_BY_NAME["HeldOutPredictiveRMSE"]
    assert spec.category == PRIMARY
    assert spec.available is True
    assert spec.direction == "lower_is_better"


def test_protocol_does_not_disturb_in_sample_measurements():
    # Attaching the protocol must not change any of the training-loop metrics:
    # the held-out evaluation runs on a deepcopy after measurement.
    base = run_single(RunConfig(policy="free_energy", seed=4, num_ticks=TICKS))
    with_eval = run_single(
        RunConfig(
            policy="free_energy", seed=4, num_ticks=TICKS,
            evaluation_protocol=EvaluationProtocol(train_seed=4, num_probe_ticks=80),
        )
    )
    for key in ["prediction_rmse", "final_energy", "final_cluster_count",
                "final_entropy", "final_active_load", "merges_committed"]:
        assert base.measurements[key] == with_eval.measurements[key]


def test_config_as_dict_excludes_evaluation_protocol():
    # The hook is a runtime concern, not part of the reproducible spec, so it
    # must stay out of as_dict() (which feeds artifact serialization + hashing).
    cfg = RunConfig(
        policy="null", seed=1, num_ticks=TICKS,
        evaluation_protocol=EvaluationProtocol(train_seed=1),
    )
    assert "evaluation_protocol" not in cfg.as_dict()
