"""
research/tests/test_runner_artifacts_report.py
==============================================

Integration tests: the ResearchRunner, the immutable artifact writer, and the
report/analysis layer. These use short runs (700 ticks so the scheduler's
time-trigger fires once) and remain stdlib-only.
"""

from __future__ import annotations

import json
import os

import pytest

from research.artifacts import (
    ArtifactWriter,
    EXPERIMENT_FILE,
    METRICS_FILE,
    SUMMARY_FILE,
    CONFIGURATION_FILE,
    POLICY_FILE,
    SEED_FILE,
    DECISION_AUDIT_FILE,
    allocate_experiment_dir,
    load_artifact,
)
from research.report import build_analysis, render_report
from research.runner import (
    NON_DETERMINISTIC_MEASUREMENTS,
    RunConfig,
    run_single,
)

TICKS = 700  # enough for one scheduler time-trigger


def _cfg(policy: str, seed: int = 1) -> RunConfig:
    return RunConfig(
        policy=policy, replay_horizon=50, noise_sigma=0.08, seed=seed,
        num_ticks=TICKS,
    )


# -- runner -----------------------------------------------------------------

def test_null_policy_commits_nothing():
    r = run_single(_cfg("null"))
    assert r.counters["merges_committed"] == 0
    assert r.decision_audit == []


def test_active_policy_consolidates_and_audits():
    r = run_single(_cfg("similarity"))
    assert r.counters["scheduler_triggers"] >= 1
    assert r.counters["merges_committed"] >= 1
    assert len(r.decision_audit) == r.counters["proposals"]
    # Every audit entry carries the uniform free-energy delta breakdown.
    entry = r.decision_audit[0]
    for key in ["tick", "policy", "targets", "accepted", "prediction_delta",
                "entropy_delta", "load_delta", "energy_delta", "reason"]:
        assert key in entry


def test_runner_is_deterministic_on_scientific_content():
    a = run_single(_cfg("free_energy", seed=3))
    b = run_single(_cfg("free_energy", seed=3))
    # The decision audit (the scientific content) is bit-identical.
    assert a.decision_audit == b.decision_audit
    # Deterministic measurements match; only timing/memory differ.
    det_a = {k: v for k, v in a.measurements.items()
             if k not in NON_DETERMINISTIC_MEASUREMENTS}
    det_b = {k: v for k, v in b.measurements.items()
             if k not in NON_DETERMINISTIC_MEASUREMENTS}
    assert det_a == det_b


def test_random_policy_deterministic_given_seed():
    a = run_single(_cfg("random", seed=7))
    b = run_single(_cfg("random", seed=7))
    assert a.decision_audit == b.decision_audit


def test_measurements_have_expected_keys():
    r = run_single(_cfg("free_energy"))
    for key in ["prediction_rmse", "final_energy", "final_cluster_count",
                "final_entropy", "final_active_load", "runtime_seconds",
                "peak_memory_bytes", "merges_committed"]:
        assert key in r.measurements


# -- artifacts --------------------------------------------------------------

def test_artifacts_writes_seven_files(tmp_path):
    r = run_single(_cfg("free_energy"))
    exp_dir = allocate_experiment_dir(str(tmp_path))
    paths = ArtifactWriter().write(
        r, exp_dir, experiment_id=os.path.basename(exp_dir),
    )
    for fname in [EXPERIMENT_FILE, METRICS_FILE, SUMMARY_FILE, CONFIGURATION_FILE,
                  POLICY_FILE, SEED_FILE, DECISION_AUDIT_FILE]:
        assert os.path.isfile(os.path.join(exp_dir, fname)), fname
    # ArtifactSize metric is populated post-write.
    metrics = load_artifact(exp_dir, METRICS_FILE)
    assert metrics["measurements"]["artifact_size_bytes"] is not None
    assert metrics["extracted"]["ArtifactSize"] is not None


def test_artifacts_are_immutable(tmp_path):
    r = run_single(_cfg("null"))
    exp_dir = allocate_experiment_dir(str(tmp_path))
    writer = ArtifactWriter()
    writer.write(r, exp_dir, experiment_id="exp_test")
    # A second write into the same non-empty dir is refused.
    with pytest.raises(FileExistsError):
        writer.write(r, exp_dir, experiment_id="exp_test")


def test_content_hash_reproducible_across_reruns(tmp_path):
    # Two runs of the IDENTICAL config must yield the same content hash, even
    # though wall-clock timings differ.
    h = []
    for i in range(2):
        r = run_single(_cfg("free_energy", seed=5))
        exp_dir = allocate_experiment_dir(str(tmp_path))
        ArtifactWriter().write(r, exp_dir, experiment_id=os.path.basename(exp_dir))
        experiment = load_artifact(exp_dir, EXPERIMENT_FILE)
        h.append(experiment["content_hash"])
    assert h[0] == h[1]


def test_allocate_experiment_dir_sequential(tmp_path):
    d1 = allocate_experiment_dir(str(tmp_path))
    d2 = allocate_experiment_dir(str(tmp_path))
    assert os.path.basename(d1) == "exp_0001"
    assert os.path.basename(d2) == "exp_0002"


# -- report / analysis ------------------------------------------------------

def _records_for(policies, seeds=(1, 2)):
    records = []
    for pol in policies:
        for seed in seeds:
            r = run_single(_cfg(pol, seed=seed))
            records.append({
                "policy": pol, "replay_horizon": 50, "noise_sigma": 0.08,
                "seed": seed, "measurements": r.measurements,
            })
    return records


def test_build_analysis_and_render_report():
    records = _records_for(["null", "similarity", "free_energy"])
    analysis = build_analysis(records)
    assert analysis["treatment"] == "free_energy"
    assert "free_energy" in analysis["per_policy"]
    # Verdict computed for each headline metric.
    for metric in ["PredictionRMSE", "FinalEnergy"]:
        assert metric in analysis["verdict"]
        assert analysis["verdict"][metric]["decision"] in (
            "treatment_wins", "treatment_loses", "tie", "indeterminate"
        )

    matrix = {
        "replay_horizons": [50], "noise_levels": [0.08], "seeds": [1, 2],
        "num_ticks": TICKS, "dataset_name": "environment",
    }
    md = render_report(analysis, matrix)
    for section in ["## Research Question", "## Experimental Design",
                    "## Independent Variables", "## Dependent Variables",
                    "## Results", "## Statistical Summary", "## Limitations",
                    "## Threats to Validity", "## Future Work"]:
        assert section in md
    # Honesty: the unavailable primary metrics are flagged in the DV table.
    assert "HeldOutPredictiveLogLikelihood" in md
