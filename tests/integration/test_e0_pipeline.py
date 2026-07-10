"""E0 integration test — full pipeline end-to-end on a small config.

Runs the complete E0 experiment (environment, conditions, analysis, decision)
on a minimal configuration to verify the pipeline works end-to-end.
"""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pytest

from experiments.E0.dataset import NonlinearLatentEnvironment
from experiments.E0.run import (
    run_single_seed,
    DEFAULT_CONFIG,
)
from experiments.E0.analysis import (
    analyze_conditions,
    compute_held_out_log_likelihood,
    compute_emergence_statistic,
)
from experiments.E0.decision import E0Decider
from core.predictors.dirichlet_markov import DirichletMarkovPredictor
from core.mdl.mdl_growth import compute_lambda_model, compute_lambda_model_corrected, should_grow
from core.measurement.proper_scoring import predictive_log_likelihood, scoring_loss


class TestE0EndToEnd:
    """End-to-end E0 pipeline on minimal config."""

    MINIMAL_CONFIG = {
        "experiment_id": "E0",
        "seed": 42,
        "env_seed": 101,
        "num_train_steps": 200,
        "num_test_steps": 50,
        "environment": {
            "num_latent_states": 3,
            "observation_dim": 4,
            "transition_alpha": 1.0,
            "noise_sigma": 0.05,
        },
        "predictor": {
            "initial_capacity": 2,
            "alpha": 1.0,
        },
        "growth": {
            "b": 1.0,
            "evaluate_every": 50,
            "warmup_steps": 30,
        },
        "conditions": ["T", "C1", "C2", "C3"],
        "num_seeds": 5,
        "results_dir": None,
    }

    def test_environment_observation_shape(self):
        """Environment produces correctly-shaped observations."""
        env = NonlinearLatentEnvironment(
            num_latent_states=3,
            observation_dim=4,
            seed=42,
        )
        states, obs = env.generate_sequence(50)
        assert obs.shape == (50, 4)
        assert states.shape == (50,)

    def test_predictor_capacity_growth(self):
        """Predictor can grow capacity."""
        pred = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        assert pred.capacity == 2
        pred.grow()
        assert pred.capacity == 3
        pred.grow()
        assert pred.capacity == 4

    def test_predictor_log_probability(self):
        """Predictor returns finite log probabilities."""
        pred = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        # Feed some observations
        for _ in range(10):
            pred.update([0.5, 0.5])

        lp = pred.log_predictive_probability([0.5, 0.5], [0.5, 0.5])
        assert not np.isinf(lp)
        assert not np.isnan(lp)

    def test_predictor_entropy(self):
        """Predictor entropy returns finite float."""
        pred = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        h = pred.entropy()
        assert isinstance(h, float)
        assert not np.isnan(h)
        assert not np.isinf(h)

    def test_mdl_lambda_computation(self):
        """λ_model is computed deterministically from canonical formula."""
        lam = compute_lambda_model(k=2, n=2, N=50)
        expected = 2.0 + 2.0 * math.log2(50)
        assert lam == pytest.approx(expected)

    def test_mdl_lambda_corrected(self):
        """λ_corrected = b + log₂N per F-A preregistration."""
        lam = compute_lambda_model_corrected(N=50)
        expected = 1.0 + math.log2(50)
        assert lam == pytest.approx(expected, rel=1e-12)

    def test_mdl_should_grow(self):
        """should_grow makes correct decisions using F-A corrected marginal cost."""
        # λ_corrected = 1.0 + log₂(50) ≈ 6.64
        # G = 50 * (30.0 - 2.0) - 6.64 = 1393.36 > 0 → should grow
        decision, gain, lam = should_grow(
            entropy_before=30.0,
            entropy_after=2.0,
            k=2, n=2, N=50,
        )
        assert decision is True, f"G={gain:.2f}, lam={lam:.2f}: Large gain should trigger growth"
        assert gain > 0

        # ΔH = 0 → G < 0 regardless of N (positive threshold always)
        decision, gain, lam = should_grow(
            entropy_before=4.9,
            entropy_after=4.9,
            k=5, n=5, N=100,
        )
        assert decision is False, f"G={gain:.2f}: Zero ΔH should never trigger growth"
        assert gain < 0

        # ΔH < 0 → G < 0 always
        decision, gain, lam = should_grow(
            entropy_before=4.9,
            entropy_after=5.0,
            k=5, n=5, N=100,
        )
        assert decision is False, f"G={gain:.2f}: Negative ΔH should never trigger growth"
        assert gain < 0

    def test_log_loss_monotonic(self):
        """Better predictions should give lower loss."""
        pred_good = predictive_log_likelihood([0.9, 0.1], 0)
        pred_bad = predictive_log_likelihood([0.1, 0.9], 0)
        assert pred_good > pred_bad
        assert scoring_loss([0.9, 0.1], 0) < scoring_loss([0.1, 0.9], 0)

    def test_single_seed_run(self):
        """Full single-seed run completes without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(
                seed=42,
                env_seed=101,
                config=self.MINIMAL_CONFIG,
                output_dir=tmpdir,
            )
            assert "conditions" in results
            assert "analysis" in results
            assert "decision" in results

            # Check all four conditions present
            for cond in ["T", "C1", "C2", "C3"]:
                assert cond in results["conditions"], f"Missing condition {cond}"

            # Check basic analysis
            for cond_name in ["T", "C1", "C2", "C3"]:
                cond = results["conditions"][cond_name]
                assert "log_likelihoods" in cond
                assert "latent_states" in cond

    def test_analysis_produces_metrics(self):
        """Analysis module produces valid DV-a and DV-b metrics."""
        conditions = {}
        for cond_name in ["T", "C1", "C2", "C3"]:
            conditions[cond_name] = {
                "log_likelihoods": [-0.5 - i * 0.01 for i in range(100)],
                "latent_states": [i % 3 for i in range(100)],
                "true_latent_states": [i % 3 for i in range(100)],
                "growth_events": [50, 100] if cond_name == "T" else [],
                "final_capacity": 4 if cond_name == "T" else 2,
            }

        analysis = analyze_conditions(conditions)

        # DV-a: Should have held-out LL for all conditions
        for cond_name in ["T", "C1", "C2", "C3"]:
            assert cond_name in analysis
            assert "held_out_ll" in analysis[cond_name]
            ll = analysis[cond_name]["held_out_ll"]["mean_log_likelihood"]
            assert ll <= 0.0  # Log-likelihood should be non-positive

        # DV-b: Treatment should have emergence statistic
        if "T" in analysis:
            assert "emergence_statistic" in analysis.get("T", {})

    def test_decision_produces_verdict(self):
        """Decision module produces valid verdict."""
        decider = E0Decider(p_threshold=0.05, min_seeds=2)

        # Simulate multi-seed results
        per_seed = []
        for s in range(2):
            per_seed.append({
                "conditions": {
                    "T": {"log_likelihoods": [-0.5 + s * 0.1] * 100},
                    "C1": {"log_likelihoods": [-1.0] * 100},
                    "C2": {"log_likelihoods": [-0.8] * 100},
                },
                "analysis": {
                    "T": {
                        "held_out_ll": {
                            "mean_log_likelihood": -0.5 + s * 0.1,
                            "mean_log_loss": 0.5,
                            "n_held_out": 20,
                        },
                        "emergence_statistic": {
                            "m_statistic": 0.2 + s * 0.05,
                            "nmi_learned_true": 0.4,
                            "nmi_learned_shuffled": 0.15,
                        },
                        "growth_events": 3,
                        "final_capacity": 5,
                    },
                },
            })

        decision = decider.evaluate_multi_seed(per_seed)
        assert "verdict" in decision
        assert "pass" in decision
        assert "n_seeds" in decision

    def test_full_pipeline_with_results_output(self):
        """Full pipeline produces JSON-serializable results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(
                seed=42,
                env_seed=101,
                config=self.MINIMAL_CONFIG,
                output_dir=tmpdir,
            )
            # Check serializability
            serialized = json.dumps(results, default=str)
            assert len(serialized) > 0

    def test_kill_criteria_two_attempts(self):
        """Two-attempt falsification protocol works."""
        decider = E0Decider(p_threshold=0.05, min_seeds=2)

        # Both attempts fail (treatment worse than controls)
        for _ in range(2):
            per_seed = []
            for s in range(2):
                per_seed.append({
                    "conditions": {
                        "T": {"log_likelihoods": [-1.0] * 100},
                        "C1": {"log_likelihoods": [-0.5] * 100},
                        "C2": {"log_likelihoods": [-0.3] * 100},
                    },
                    "analysis": {
                        "T": {
                            "held_out_ll": {"mean_log_likelihood": -1.0, "mean_log_loss": 1.0, "n_held_out": 20},
                            "emergence_statistic": {"m_statistic": 0.01, "nmi_learned_true": 0.1, "nmi_learned_shuffled": 0.09},
                        },
                    },
                })

            decision = decider.evaluate_multi_seed(per_seed)
            decider.record_attempt(decision)

        should_falsify, reason = decider.should_falsify()
        assert isinstance(should_falsify, bool)
        assert len(reason) > 0

    @pytest.mark.slow
    def test_seeded_reproducibility(self):
        """Same seed produces identical results."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            r1 = run_single_seed(42, 101, self.MINIMAL_CONFIG, str(tmpdir1))

        with tempfile.TemporaryDirectory() as tmpdir2:
            r2 = run_single_seed(42, 101, self.MINIMAL_CONFIG, str(tmpdir2))

        # Compare log-likelihoods for all conditions
        for cond in ["T", "C1", "C2"]:
            ll1 = r1["conditions"][cond]["log_likelihoods"]
            ll2 = r2["conditions"][cond]["log_likelihoods"]
            assert np.allclose(ll1, ll2), (
                f"Condition {cond} not reproducible between runs"
            )


class TestE0ArtifactGeneration:
    """Test publication-ready artifact generation."""

    def test_results_json_serializable(self):
        """Results must be JSON-serializable (for publication artifacts)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(42, 101, TestE0EndToEnd.MINIMAL_CONFIG, str(tmpdir))
            try:
                json_str = json.dumps(results, indent=2, default=str)
                assert len(json_str) > 0
            except (TypeError, ValueError) as e:
                pytest.fail(f"Results not JSON-serializable: {e}")

    def test_decision_output(self):
        """Decision output must be machine-readable."""
        decider = E0Decider(p_threshold=0.05, min_seeds=2)
        per_seed = []
        for s in range(2):
            per_seed.append({
                "conditions": {
                    "T": {"log_likelihoods": [-0.5] * 100},
                    "C1": {"log_likelihoods": [-1.0] * 100},
                    "C2": {"log_likelihoods": [-0.8] * 100},
                },
                "analysis": {
                    "T": {
                        "held_out_ll": {"mean_log_likelihood": -0.5, "mean_log_loss": 0.5, "n_held_out": 20},
                        "emergence_statistic": {"m_statistic": 0.2, "nmi_learned_true": 0.4, "nmi_learned_shuffled": 0.2},
                    },
                },
            })
        decision = decider.evaluate_multi_seed(per_seed)
        assert isinstance(decision["pass"], bool)
        assert isinstance(decision["verdict"], str)
        assert isinstance(decision["dv_a"], dict)
        assert isinstance(decision["dv_b"], dict)
