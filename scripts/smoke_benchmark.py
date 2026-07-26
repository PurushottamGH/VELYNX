#!/usr/bin/env python3
"""Smoke test for benchmark infrastructure.

Verifies that benchmarks/ package is importable and basic metrics compute correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_metrics_import():
    from experiments.metrics import (
        LAMBDA,
        MU,
        NU,
        ENTROPY_HIGH,
        SURPRISE_HIGH,
        ENERGY_EXHAUSTION,
        MetricsCollector,
        MetricsReport,
        bootstrap_ci,
        effect_size_cohens_d,
        permutation_test,
    )

    assert LAMBDA == 1.0
    assert MU == 2.0
    assert NU == 0.5
    assert ENTROPY_HIGH == 2.0
    assert SURPRISE_HIGH == 0.5
    assert ENERGY_EXHAUSTION == 18.0

    collector = MetricsCollector("test", "smoke")
    collector.record(tick=0, free_energy=1.0, entropy=0.5, surprise=0.1, structural_load=0.2)
    collector.record(tick=1, free_energy=2.0, entropy=1.0, surprise=0.3, structural_load=0.5)
    assert len(collector.records) == 2
    summary = collector.summary()
    assert summary["num_ticks"] == 2
    assert summary["mean_free_energy"] == 1.5
    print("[OK] MetricsCollector")

    fe = collector.compute_free_energy(entropy=1.0, surprise=0.5, structural_load=0.2)
    expected = LAMBDA * 1.0 + MU * 0.5 + NU * 0.2
    assert abs(fe - expected) < 1e-10
    print("[OK] compute_free_energy")

    kc = collector.check_kill_criteria(free_energy=100.0, entropy=10.0, surprise=10.0)
    assert len(kc) > 0
    print(f"[OK] check_kill_criteria: {kc}")

    print("[OK] Metrics subsystem smoke test")


def test_artifact_store():
    from experiments.artifacts import ArtifactStore
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        store = ArtifactStore(base_path=Path(tmp))
        path = store.store_artifact("test_exp", "run_001", "test_data", {"key": "value"})
        assert path.exists()
        data = store.retrieve_artifact("test_exp", "run_001", "test_data")
        assert data == {"key": "value"}
        assert store.verify_integrity("test_exp", "run_001")
        runs = store.list_runs("test_exp")
        assert "run_001" in runs
        print("[OK] ArtifactStore")


def test_kill_criteria():
    from experiments.metrics import MetricsCollector

    collector = MetricsCollector("test", "kill")
    kc = collector.check_kill_criteria(free_energy=5.0, entropy=0.5, surprise=0.1)
    assert len(kc) == 0
    kc2 = collector.check_kill_criteria(free_energy=20.0, entropy=3.0, surprise=1.0)
    assert "energy_exhaustion" in kc2
    assert "entropy_high" in kc2
    assert "surprise_high" in kc2
    print("[OK] Kill criteria thresholds")


def test_stats():
    from experiments.metrics import bootstrap_ci, effect_size_cohens_d, permutation_test
    import numpy as np

    control = np.array([1.0, 1.1, 0.9, 1.0, 1.05])
    treatment = np.array([2.0, 2.1, 1.9, 2.0, 2.05])

    d = effect_size_cohens_d(control, treatment)
    assert abs(d) > 1.0
    print(f"[OK] effect_size_cohens_d: {d:.3f}")

    p = permutation_test(control, treatment, n_permutations=1000)
    assert p < 0.05
    print(f"[OK] permutation_test: p={p:.4f}")

    lower, upper = bootstrap_ci(control)
    assert lower < upper
    print(f"[OK] bootstrap_ci: [{lower:.3f}, {upper:.3f}]")


def test_runner_import():
    from experiments.runner import load_registry, list_experiments
    import yaml

    reg_path = Path(__file__).resolve().parent.parent / "experiment_registry.yaml"
    reg = load_registry(reg_path)
    assert "E0" in reg.get("experiment_registry", {})
    print("[OK] Experiment runner import + registry load")


def main():
    print("=" * 60)
    print("Benchmark Infrastructure Smoke Test")
    print("=" * 60)

    tests = [
        test_metrics_import,
        test_artifact_store,
        test_kill_criteria,
        test_stats,
        test_runner_import,
    ]

    failures = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            import traceback

            traceback.print_exc()
            failures += 1

    print("-" * 60)
    if failures:
        print(f"SMOKE TEST FAILED: {failures} failures")
        sys.exit(1)
    else:
        print(f"SMOKE TEST PASSED: {len(tests)}/{len(tests)} tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
