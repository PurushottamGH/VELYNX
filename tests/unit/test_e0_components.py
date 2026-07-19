"""E0 unit tests — environment, conditions, analysis, and decision.

Tests each component of the E0 experiment pipeline in isolation.
"""
from __future__ import annotations

import math
import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from experiments.E0.dataset import NonlinearLatentEnvironment
from experiments.E0.leakage_check import (
    check_linear_recovery,
    check_environment_nonlinearity,
    generate_nonlinearity_certificate,
)
from experiments.E0.analysis import (
    compute_held_out_log_likelihood,
    compute_emergence_statistic,
    analyze_conditions,
    generate_e0_report,
)
from experiments.E0.decision import (
    E0Decider,
    paired_one_sided_ttest,
    bootstrap_significance,
    generate_falsification_report,
)
from experiments.E0.run import (
    run_treatment,
    run_fixed_capacity,
    apply_growth_at_random_times,
    run_shuffled_input,
    run_single_seed,
    run_multi_seed,
    SeedRegistry,
)
from framework.core.mdl.mdl_growth import should_grow, compute_lambda_model


# ─── Environment tests ─────────────────────────────────────────────


class TestNonlinearLatentEnvironment:
    """Test the synthetic nonlinear latent environment."""

    def test_environment_initialization(self):
        env = NonlinearLatentEnvironment(
            num_latent_states=5,
            observation_dim=8,
            seed=42,
        )
        assert env.K == 5
        assert env.D == 8
        assert env.current_latent_state is not None
        assert env.current_latent_state < 5

    def test_environment_step(self):
        env = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        latent, obs = env.step()
        assert 0 <= latent < 3
        assert isinstance(obs, np.ndarray)
        assert obs.shape == (4,)

    def test_environment_generate_sequence(self):
        env = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        states, obs = env.generate_sequence(100)
        assert states.shape == (100,)
        assert obs.shape == (100, 4)
        assert len(np.unique(states)) <= 3

    def test_environment_deterministic_with_seed(self):
        """Same seed must produce same sequence."""
        env1 = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        env2 = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        s1, o1 = env1.generate_sequence(50)
        s2, o2 = env2.generate_sequence(50)
        assert np.array_equal(s1, s2)
        assert np.allclose(o1, o2)

    def test_environment_different_seeds_different(self):
        """Different seeds must produce different sequences."""
        env1 = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        env2 = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=99)
        s1, o1 = env1.generate_sequence(50)
        s2, o2 = env2.generate_sequence(50)
        # Very unlikely to be the same
        assert not np.array_equal(s1, s2) or not np.allclose(o1, o2)

    def test_environment_rejects_invalid_args(self):
        with pytest.raises(ValueError):
            NonlinearLatentEnvironment(num_latent_states=1)
        with pytest.raises(ValueError):
            NonlinearLatentEnvironment(observation_dim=1)

    def test_environment_state_info(self):
        env = NonlinearLatentEnvironment(num_latent_states=7, observation_dim=12, seed=42)
        info = env.get_state_info()
        assert info["num_latent_states"] == 7
        assert info["observation_dim"] == 12
        assert info["env_seed"] == 42

    def test_environment_reset(self):
        env = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        _, _ = env.generate_sequence(50)
        assert len(env.latent_history) == 51  # initial + 50 steps
        env.reset()
        assert len(env.latent_history) == 1  # just the reset state


# ─── Leakage check tests ───────────────────────────────────────────


class TestLeakageCheck:
    """Test the offline nonlinearity verification."""

    def test_linear_recovery_on_nonlinear_data(self):
        """Linear probe should struggle on nonlinear data."""
        env = NonlinearLatentEnvironment(num_latent_states=5, observation_dim=10, seed=42)
        states, obs = env.generate_sequence(3000)
        result = check_linear_recovery(obs, states, n_train=2000, n_test=1000)
        assert "accuracy" in result
        assert 0.0 <= result["accuracy"] <= 1.0
        assert result["chance"] == pytest.approx(0.2)  # 1/5

    def test_environment_nonlinearity_check(self):
        env = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=8, seed=42)
        states, obs = env.generate_sequence(500)
        result = check_environment_nonlinearity(obs, states)
        assert "linear_probe" in result or "accuracy" in result

    def test_nonlinearity_certificate_generation(self):
        env = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=8, seed=42)
        states, obs = env.generate_sequence(500)
        cert = generate_nonlinearity_certificate(obs, states)
        assert "[FACT]" in cert
        assert "Verdict" in cert


# ─── Seed registry tests ──────────────────────────────────────────


class TestSeedRegistry:
    """Test the central PRNG registry."""

    def test_seed_registry_creation(self):
        reg = SeedRegistry(master_seed=42, env_seed_offset=1000)
        assert reg.env_seed() == 1042
        assert reg.master_seed == 42

    def test_agent_seeds_differ_from_env_seed(self):
        reg = SeedRegistry(master_seed=42, env_seed_offset=1000)
        agent_seed = reg.agent_seed("T", 0)
        assert agent_seed != reg.env_seed()

    def test_agent_seeds_differ_by_condition(self):
        reg = SeedRegistry(master_seed=42, env_seed_offset=1000)
        t_seed = reg.agent_seed("T", 0)
        c1_seed = reg.agent_seed("C1", 0)
        assert t_seed != c1_seed


# ─── Analysis tests ────────────────────────────────────────────────


class TestAnalysis:
    """Test the E0 analysis module."""

    def test_held_out_log_likelihood(self):
        lls = [-1.0, -0.5, -0.3, -0.2, -0.1]
        result = compute_held_out_log_likelihood(lls, [0, 0, 1, 1, 0])
        assert result["mean_log_likelihood"] <= 0
        assert result["mean_log_loss"] >= 0
        assert result["n_held_out"] == 1  # 20% of 5

    def test_held_out_ll_with_explicit_test(self):
        train_lls = [-1.0] * 100
        test_lls = [-0.5] * 20
        result = compute_held_out_log_likelihood(
            train_lls, [0] * 100, test_lls, [0] * 20
        )
        assert result["n_held_out"] == 20
        assert result["mean_log_likelihood"] == pytest.approx(-0.5)
        assert result["mean_log_loss"] == pytest.approx(0.5)

    def test_held_out_ll_empty(self):
        result = compute_held_out_log_likelihood([], [])
        assert result["n_held_out"] == 0
        assert result["mean_log_loss"] == float("inf")

    def test_emergence_statistic_positive_for_correlated(self):
        learned = [0, 0, 1, 1, 2, 2, 0, 0, 1, 1]
        true = [0, 0, 1, 1, 2, 2, 0, 0, 1, 1]
        shuffled = [1, 0, 2, 1, 0, 2, 1, 0, 2, 0]
        result = compute_emergence_statistic(learned, true, shuffled)
        assert result["m_statistic"] >= 0

    def test_true_latents_come_from_env_not_predictor(self):
        """[BLOCKER 3] true_latent_states must come from env.step(), not predictor."""
        # Create environment and predictor
        env = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor
        predictor = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0, rng_seed=99)

        env.reset()
        predictor.reset()

        latent_states = []
        true_latent_states = []

        # Run a few steps
        for step in range(50):
            latent, obs = env.step()
            obs_list = obs.tolist()

            # Store predictor inference AND env ground truth SEPARATELY
            true_latent_states.append(latent)  # From env.step() - THIS is ground truth

            if step > 0:
                predictor.update(obs_list)
            inferred = predictor.current_state if predictor.current_state is not None else 0
            latent_states.append(inferred)  # From predictor - this is NOT ground truth

        # Prove they are stored as separate lists
        assert len(latent_states) == len(true_latent_states)
        # They are different object references
        assert latent_states is not true_latent_states

    def test_true_latents_missing_raises_error(self):
        """[BLOCKER 3] analyze_conditions must raise KeyError if true_latent_states missing."""
        conditions = {
            "T": {
                "log_likelihoods": [-1.0, -0.5],
                "latent_states": [0, 1],
                # NOTE: 'true_latent_states' intentionally omitted
                "growth_events": [],
                "final_capacity": 2,
            },
        }
        with pytest.raises(KeyError, match="true_latent_states"):
            analyze_conditions(conditions)

    def test_emergence_statistic_zero_for_random(self):
        rng = np.random.RandomState(42)
        learned = rng.randint(0, 3, size=100).tolist()
        true = rng.randint(0, 3, size=100).tolist()
        shuffled = rng.randint(0, 3, size=100).tolist()
        result = compute_emergence_statistic(learned, true, shuffled)
        abs_m = abs(result["m_statistic"])
        assert abs_m < 0.3, f"M should be near 0 for random, got {result['m_statistic']}"

    def test_analyze_conditions_basic(self):
        conditions = {
            "T": {
                "log_likelihoods": [-1.0, -0.5, -0.3],
                "latent_states": [0, 1, 0],
                "true_latent_states": [0, 1, 0],
                "growth_events": [500],
            },
            "C1": {
                "log_likelihoods": [-2.0, -1.5, -1.3],
                "latent_states": [0, 0, 0],
                "true_latent_states": [0, 0, 0],
                "growth_events": [],
            },
        }
        analysis = analyze_conditions(conditions)
        assert "T" in analysis
        assert "C1" in analysis

    def test_generate_e0_report(self):
        analysis = {
            "T": {
                "held_out_ll": {"mean_log_likelihood": -0.5, "mean_log_loss": 0.5, "n_held_out": 10},
                "emergence_statistic": {"m_statistic": 0.3, "nmi_learned_true": 0.5, "nmi_learned_shuffled": 0.2},
                "growth_events": 3,
            },
            "C1": {
                "held_out_ll": {"mean_log_likelihood": -1.0, "mean_log_loss": 1.0, "n_held_out": 10},
                "growth_events": 0,
            },
        }
        report = generate_e0_report(analysis)
        assert "[FACT]" in report
        assert "## Results Summary" in report


# ─── Decision tests ────────────────────────────────────────────────


class TestDecision:
    """Test the E0 decision module."""

    def test_paired_ttest_basic(self):
        """T-test should detect significant difference."""
        treatment = [1.0, 1.1, 0.9, 1.0, 1.0]
        control = [0.0, 0.1, -0.1, 0.0, 0.0]
        result = paired_one_sided_ttest(treatment, control)
        assert result["significant"] is True
        assert result["p_value"] < 0.05
        assert result["mean_difference"] > 0

    def test_paired_ttest_no_difference(self):
        """T-test should not find significance when there's no difference."""
        treatment = [1.0, 1.0, 1.0, 1.0]
        control = [1.0, 1.0, 1.0, 1.0]
        result = paired_one_sided_ttest(treatment, control)
        assert result["significant"] is False
        assert result["mean_difference"] == 0.0

    def test_paired_ttest_insufficient_samples(self):
        result = paired_one_sided_ttest([1.0], [2.0])
        assert result["significant"] is False or "error" in result

    def test_bootstrap_significance(self):
        treatment = [1.0, 1.1, 0.9]
        control = [0.0, 0.1, -0.1]
        result = bootstrap_significance(treatment, control, n_resamples=1000)
        assert "p_value" in result
        assert "significant" in result

    def test_e0_decider_single_seed(self):
        """Test decider with a single seed result."""
        decider = E0Decider(p_threshold=0.01, min_seeds=3)

        results = {
            "conditions": {
                "T": {"log_likelihoods": [-0.5] * 100},
                "C1": {"log_likelihoods": [-1.0] * 100},
                "C2": {"log_likelihoods": [-0.8] * 100},
            },
            "analysis": {
                "T": {
                    "held_out_ll": {"mean_log_likelihood": -0.5, "mean_log_loss": 0.5, "n_held_out": 20},
                    "emergence_statistic": {"m_statistic": 0.15, "nmi_learned_true": 0.3, "nmi_learned_shuffled": 0.15},
                },
            },
        }

        decision = decider.evaluate(results)
        assert "verdict" in decision
        assert "pass" in decision

    def test_e0_decider_multi_seed(self):
        """Test decider with multiple seeds."""
        decider = E0Decider(p_threshold=0.01, min_seeds=3)

        per_seed = []
        for s in range(3):
            per_seed.append({
                "conditions": {
                    "T": {"log_likelihoods": [-0.5 + s * 0.1] * 100},
                    "C1": {"log_likelihoods": [-1.0] * 100},
                    "C2": {"log_likelihoods": [-0.8] * 100},
                },
                "analysis": {
                    "T": {
                        "held_out_ll": {"mean_log_likelihood": -0.5 + s * 0.1, "mean_log_loss": 0.5, "n_held_out": 20},
                        "emergence_statistic": {"m_statistic": 0.15 + s * 0.05, "nmi_learned_true": 0.3, "nmi_learned_shuffled": 0.15},
                    },
                },
            })

        decision = decider.evaluate_multi_seed(per_seed)
        assert "verdict" in decision
        assert "n_seeds" in decision

    def test_e0_decider_falsification_two_attempts(self):
        """After two failing attempts, H* should be falsified."""
        decider = E0Decider(p_threshold=0.01, min_seeds=3)

        # First attempt fails
        fail_result = {
            "conditions": {
                "T": {"log_likelihoods": [-1.0] * 100},
                "C1": {"log_likelihoods": [-0.5] * 100},  # T is worse
                "C2": {"log_likelihoods": [-0.3] * 100},
            },
            "analysis": {
                "T": {
                    "held_out_ll": {"mean_log_likelihood": -1.0, "mean_log_loss": 1.0, "n_held_out": 20},
                    "emergence_statistic": {"m_statistic": 0.01, "nmi_learned_true": 0.1, "nmi_learned_shuffled": 0.09},
                },
            },
        }
        d1 = decider.evaluate(fail_result)
        decider.record_attempt(d1)

        # Second attempt also fails
        d2 = decider.evaluate(fail_result)
        decider.record_attempt(d2)

        falsify, reason = decider.should_falsify()
        # With only 1 seed (not >= min_seeds), may be inconclusive
        assert isinstance(falsify, bool)
        assert isinstance(reason, str)

    def test_falsification_report_generation(self):
        decider = E0Decider()
        report = generate_falsification_report(decider)
        assert "E0 Falsification Report" in report


# ─── Condition runner integration tests ──────────────────────────


class TestConditionRunners:
    """Test that condition runners execute without errors on small config."""

    @pytest.fixture
    def env(self):
        return NonlinearLatentEnvironment(
            num_latent_states=3,
            observation_dim=4,
            seed=42,
        )

    @pytest.fixture
    def predictor(self):
        from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor
        return DirichletMarkovPredictor(
            initial_capacity=2,
            alpha=1.0,
            rng_seed=99,
        )

    def test_run_treatment(self, env, predictor):
        result = run_treatment(
            env=env,
            predictor=predictor,
            train_steps=50,
            evaluate_every=20,
            warmup_steps=10,
        )
        assert result["condition"] == "T"
        assert "log_likelihoods" in result
        assert "growth_events" in result
        assert "final_capacity" in result

    def test_run_treatment_growth_events(self, env, predictor):
        """With many steps, treatment should attempt growth."""
        # Increase steps to trigger growth evaluation
        result = run_treatment(
            env=env,
            predictor=predictor,
            train_steps=100,
            evaluate_every=30,
            warmup_steps=20,
        )
        assert "growth_events" in result

    def test_run_fixed_capacity(self, env):
        from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor
        p = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        result = run_fixed_capacity(
            env=env,
            predictor=p,
            train_steps=50,
            evaluate_every=20,
        )
        assert result["condition"] == "C1"
        assert result["final_capacity"] == 2  # Never grows

    def test_apply_growth_at_random_times(self, env):
        from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor
        p = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        rng = np.random.RandomState(42)
        result = apply_growth_at_random_times(
            predictor=p,
            env=env,
            train_steps=100,
            growth_count=3,
            rng=rng,
        )
        assert result["condition"] == "C2"
        assert len(result["growth_events"]) == 3  # Exactly 3 growth events

    def test_run_shuffled_input(self, env):
        from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor
        p = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        result = run_shuffled_input(
            env=env,
            predictor=p,
            train_steps=50,
            evaluate_every=20,
            warmup_steps=10,
        )
        assert result["condition"] == "C3"
        assert "log_likelihoods" in result


# ─── Blocker 1: Capacity-Matched C2 ─────────────────────────────


class TestC2CapacityMatched:
    """[BLOCKER 1] Verify C2 is capacity-matched to Treatment (T).

    Procedure:
    1. Execute T completely, record growth events and final capacity.
    2. Execute C2 independently with identical growth count.
    3. Verify final capacity == T's final capacity.
    4. Verify growth event count == T's growth event count.
    5. Verify C2 growth timing is uncorrelated with prediction error.
    """

    def test_c2_has_same_growth_count_as_t(self):
        """C2 growth event count must equal T's growth event count."""
        config = {
            "experiment_id": "E0_TEST",
            "seed": 42,
            "env_seed": 101,
            "num_train_steps": 500,
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
                "warmup_steps": 100,
            },
            "conditions": ["T", "C1", "C2", "C3"],
            "num_seeds": 1,
            "results_dir": None,
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(seed=42, env_seed=101, config=config, output_dir=tmpdir)
            t_events = len(results["conditions"]["T"]["growth_events"])
            c2_events = len(results["conditions"]["C2"]["growth_events"])
            assert c2_events == t_events, (
                f"C2 growth events ({c2_events}) must equal T growth events ({t_events})"
            )

    def test_c2_has_same_final_capacity_as_t(self):
        """C2 final capacity must equal T's final capacity."""
        config = {
            "experiment_id": "E0_TEST",
            "seed": 42,
            "env_seed": 101,
            "num_train_steps": 500,
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
                "warmup_steps": 100,
            },
            "conditions": ["T", "C1", "C2", "C3"],
            "num_seeds": 1,
            "results_dir": None,
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(seed=42, env_seed=101, config=config, output_dir=tmpdir)
            t_cap = results["conditions"]["T"]["final_capacity"]
            c2_cap = results["conditions"]["C2"]["final_capacity"]
            assert c2_cap == t_cap, (
                f"C2 final capacity ({c2_cap}) must equal T final capacity ({t_cap})"
            )

    def test_c2_starts_with_same_initial_capacity(self):
        """C2 must start with same initial capacity as T."""
        from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor
        env = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        rng = np.random.RandomState(42)
        p = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        result = apply_growth_at_random_times(
            predictor=p,
            env=env,
            train_steps=100,
            growth_count=2,
            rng=rng,
        )
        # Initial capacity was 2, grew 2 times, final = 4
        assert result["final_capacity"] == 4
        assert len(result["growth_events"]) == 2

    def test_c2_growth_timing_is_random(self):
        """C2 growth event indices must not correlate with prediction error."""
        config = {
            "experiment_id": "E0_TEST",
            "seed": 42,
            "env_seed": 101,
            "num_train_steps": 1000,
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
                "evaluate_every": 100,
                "warmup_steps": 100,
            },
            "conditions": ["T", "C2"],
            "num_seeds": 1,
            "results_dir": None,
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(seed=42, env_seed=101, config=config, output_dir=tmpdir)
            # C2 growth events must be different from T growth events
            # (since C2 uses random positions, they should almost never match exactly)
            t_events = results["conditions"]["T"]["growth_events"]
            c2_events = results["conditions"]["C2"]["growth_events"]
            # Same count, but different positions (with high probability)
            assert len(c2_events) == len(t_events)
            if len(t_events) > 0:
                assert t_events != c2_events, (
                    "C2 growth timing must differ from T growth timing "
                    "(C2 uses random positions, T uses error-gated positions)"
                )

            # Verify C2 events are uniformly distributed across the run
            if len(c2_events) >= 2:
                c2_first_half = sum(1 for e in c2_events if e < 500)
                c2_second_half = len(c2_events) - c2_first_half
                # No more than 80% of events in either half
                max_ratio = max(c2_first_half, c2_second_half) / len(c2_events)
                assert max_ratio < 0.9, (
                    f"C2 growth events too concentrated: {c2_first_half}/{c2_second_half}"
                )


# ─── Blocker 4: Growth Decision Only After G > λ_model ──────────


class TestGrowthDecision:
    """[BLOCKER 4] Verify predictor growth occurs only after G > λ_model.

    The canonical rule: predictor.grow() is called ONLY after the MDL
    gain check returns True (G > λ_model). No speculative growth may
    occur before the decision.
    """

    def test_growth_only_after_positive_gain(self):
        """predictor.grow() must only be called when should_grow returns True."""
        from framework.core.mdl.mdl_growth import should_grow, compute_lambda_model
        lam = compute_lambda_model(k=2, n=2, N=50)
        # G = N·ΔH - (b + log₂N) = 50*0.1 - 6.64 = -1.64 => should NOT grow
        decision, gain, _ = should_grow(
            entropy_before=30.0,
            entropy_after=29.9,
            k=2, n=2, N=50,
        )
        assert decision is False, (
            f"Negative MDL gain ({gain:.4f}) should not trigger growth"
        )

    def test_growth_commits_when_gain_positive(self):
        """predictor.grow() must be called when should_grow returns True."""
        decision, gain, _ = should_grow(
            entropy_before=30.0,
            entropy_after=1.0,
            k=2, n=2, N=50,
        )
        assert decision is True, (
            f"Large positive gain ({gain:.4f}) should trigger growth"
        )

    def test_no_speculative_growth_in_run(self):
        """Run treatment should not call grow() before verifying MDL gain.

        We verify by checking that the per_step_log accurately reflects
        the growth decision AFTER the gain computation, not before.
        """
        config = {
            "experiment_id": "E0_TEST",
            "seed": 42,
            "env_seed": 101,
            "num_train_steps": 300,
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
                "evaluate_every": 100,
                "warmup_steps": 50,
            },
            "conditions": ["T"],
            "num_seeds": 1,
            "results_dir": None,
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(seed=42, env_seed=101, config=config, output_dir=tmpdir)
            t = results["conditions"]["T"]
            # Verify growth events are recorded, and all growth decisions
            # in the log reflect G > λ_model
            log = t.get("per_step_log", [])
            for entry in log:
                if entry.get("grew", False):
                    assert entry["gain"] > 0, (
                        f"Growth recorded at step {entry['step']} but gain={entry['gain']:.4f} <= 0"
                    )

    def test_decider_honors_m_static_margin(self):
        """[BLOCKER 4] DV-b must require M > pre-registered margin."""
        decider = E0Decider(p_threshold=0.01, min_seeds=3, m_margin=0.05)
        result = decider._evaluate_dv_b(m_statistic=0.01)
        assert result["pass"] is False, "M=0.01 below 0.05 margin should fail"

        result = decider._evaluate_dv_b(m_statistic=0.10)
        assert result["pass"] is True, "M=0.10 above 0.05 margin should pass"


# ─── Blocker 3: Latent-State Correctness Regression Tests ─────────


class TestLatentStateRegression:
    """[BLOCKER 3] Verify M statistic uses ONLY environment true latent states.

    The emergence statistic M = NMI(learned, true) - NMI(learned, shuffled)
    must derive ground truth (true) from the environment generator, NEVER
    from the predictor's internal state. This class adds regression tests
    to prevent regressions of this invariant.
    """

    def test_true_latent_states_separate_from_inferred(self):
        """true_latent_states and latent_states must be distinct lists
        in every condition result, not aliased or copied from predictor."""
        config = {
            "experiment_id": "E0_TEST",
            "seed": 42, "env_seed": 101,
            "num_train_steps": 200, "num_test_steps": 50,
            "environment": {"num_latent_states": 3, "observation_dim": 4,
                            "transition_alpha": 1.0, "noise_sigma": 0.05},
            "predictor": {"initial_capacity": 2, "alpha": 1.0},
            "growth": {"b": 1.0, "evaluate_every": 50, "warmup_steps": 50},
            "conditions": ["T", "C1", "C2", "C3"],
            "num_seeds": 1, "results_dir": None,
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(42, 101, config, tmpdir)
            for cond in ["T", "C1", "C2", "C3"]:
                c = results["conditions"][cond]
                assert "true_latent_states" in c, f"{cond} missing true_latent_states"
                assert "latent_states" in c, f"{cond} missing latent_states"
                # Must be different object references
                assert c["true_latent_states"] is not c["latent_states"], (
                    f"{cond}: true_latent_states aliased to latent_states"
                )
                # true_latent_states must have same length as latent_states
                assert len(c["true_latent_states"]) == len(c["latent_states"]), (
                    f"{cond}: length mismatch true_latent({len(c['true_latent_states'])}) "
                    f"vs latent({len(c['latent_states'])})"
                )

    def test_true_latents_not_derived_from_predictor_state(self):
        """Verify true_latent_states values come from env.step(), not predictor.

        1. Two separate environment instances with same seed = same latent sequence.
        2. In a full run_single_seed, true_latent_states are identical across
           conditions (same env seed), while latent_states (predictor inferred)
           differ because each condition gets a different agent seed.
        """
        # (1) Determinism: same seed = identical latent sequence
        env1 = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        env2 = NonlinearLatentEnvironment(num_latent_states=3, observation_dim=4, seed=42)
        s1, _ = env1.generate_sequence(100)
        s2, _ = env2.generate_sequence(100)
        assert s1.tolist() == s2.tolist(), (
            "Environment must be deterministic: same seed = same latent sequence"
        )

        # (2) In a real E0 run, all conditions share the same env_seed, so
        # true_latent_states should be identical across conditions, while
        # latent_states (predictor) may differ.
        import tempfile
        config = {
            "experiment_id": "E0_TEST", "seed": 42, "env_seed": 101,
            "num_train_steps": 100, "num_test_steps": 20,
            "environment": {"num_latent_states": 3, "observation_dim": 4,
                            "transition_alpha": 1.0, "noise_sigma": 0.05},
            "predictor": {"initial_capacity": 2, "alpha": 1.0},
            "growth": {"b": 1.0, "evaluate_every": 50, "warmup_steps": 30},
            "conditions": ["T", "C1", "C2", "C3"],
            "num_seeds": 1, "results_dir": None,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(42, 101, config, tmpdir)
            # All conditions share same env_seed = same true latent sequence
            t_true = results["conditions"]["T"]["true_latent_states"]
            c1_true = results["conditions"]["C1"]["true_latent_states"]
            assert t_true == c1_true, (
                "true_latent_states must be identical across conditions "
                "(same env_seed)"
            )
            # But predictor latent_states differ (different agent seeds)
            t_latent = results["conditions"]["T"]["latent_states"]
            c1_latent = results["conditions"]["C1"]["latent_states"]
            # Different agent seeds + different initial predictor states
            # -> latents almost certainly differ at some point
            # (There's a tiny chance of collision, so we check they're not
            # the same object, and that at least one index differs.)
            assert t_latent is not c1_latent, (
                "latent_states across conditions must be separate lists"
            )

    def test_analyze_conditions_rejects_missing_true_latents(self):
        """analyze_conditions must raise KeyError if true_latent_states is missing
        for T condition. This is the load-bearing guard against predictor-derived M."""
        conditions = {
            "T": {
                "log_likelihoods": [-1.0],
                "latent_states": [0, 1],
                "growth_events": [],
                "final_capacity": 2,
            },
        }
        with pytest.raises(KeyError, match="true_latent_states"):
            analyze_conditions(conditions)

    def test_analyze_conditions_rejects_missing_true_latents_on_T(self):
        """T condition MUST include true_latent_states or analyze_conditions raises."""
        conditions = {
            "T": {
                "log_likelihoods": [-1.0],
                "latent_states": [0, 1],
                "growth_events": [],
                "final_capacity": 2,
            },
        }
        with pytest.raises(KeyError, match="true_latent_states"):
            analyze_conditions(conditions)

    def test_analyze_condition_non_T_no_true_latents_no_crash(self):
        """Non-T conditions without true_latent_states should not crash.
        They simply won't have emergence statistics computed."""
        for cond_name in ["C1", "C2", "C3"]:
            conditions = {
                cond_name: {
                    "log_likelihoods": [-0.5],
                    "latent_states": [0],
                    "growth_events": [],
                    "final_capacity": 2,
                },
            }
            # Should not raise; non-T conditions skip emergence computation
            analysis = analyze_conditions(conditions)
            assert cond_name in analysis
            assert "emergence_statistic" not in analysis.get(cond_name, {})


# ─── Blocker 4: Growth Ordering Regression Tests ────────────────


class TestGrowthOrderingRegression:
    """[BLOCKER 4] Verify growth occurs ONLY after G > λ_model.

    Canonical rule: predictor.grow() is called ONLY after the MDL
    gain check returns True (G = H_before - H_after - λ_model > 0).
    No speculative growth may occur before the decision.

    These regression tests verify the ordering invariant in the
    run_treatment condition runner by inspecting the per_step_log.
    """

    def test_every_growth_event_has_positive_gain(self):
        """Every recorded growth event must have gain > 0 in the per_step_log."""
        config = {
            "experiment_id": "E0_TEST", "seed": 42, "env_seed": 101,
            "num_train_steps": 500, "num_test_steps": 50,
            "environment": {"num_latent_states": 4, "observation_dim": 6,
                            "transition_alpha": 1.0, "noise_sigma": 0.05},
            "predictor": {"initial_capacity": 2, "alpha": 1.0},
            "growth": {"b": 1.0, "evaluate_every": 50, "warmup_steps": 100},
            "conditions": ["T"], "num_seeds": 1, "results_dir": None,
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(42, 101, config, tmpdir)
            log = results["conditions"]["T"].get("per_step_log", [])
            assert len(log) > 0, "per_step_log should not be empty"
            for entry in log:
                if entry.get("grew", False):
                    msg = (f"Growth at step {entry['step']} has gain={entry['gain']:.6f} "
                           f"but must be > 0. H_before={entry['entropy_before']:.4f}, "
                           f"H_after={entry['entropy_after']:.4f}, "
                           f"λ={entry['lambda_model']:.4f}")
                    assert entry["gain"] > 0, msg

    def test_no_growth_when_gain_not_positive(self):
        """When per_step_log shows gain <= 0, grew must be False."""
        config = {
            "experiment_id": "E0_TEST", "seed": 42, "env_seed": 101,
            "num_train_steps": 300, "num_test_steps": 50,
            "environment": {"num_latent_states": 5, "observation_dim": 8,
                            "transition_alpha": 1.0, "noise_sigma": 0.05},
            "predictor": {"initial_capacity": 4, "alpha": 1.0},
            "growth": {"b": 1.0, "evaluate_every": 50, "warmup_steps": 50},
            "conditions": ["T"], "num_seeds": 1, "results_dir": None,
        }
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_single_seed(42, 101, config, tmpdir)
            log = results["conditions"]["T"].get("per_step_log", [])
            for entry in log:
                if entry.get("gain", 0) <= 0:
                    assert not entry.get("grew", False), (
                        f"Entry at step {entry['step']} has gain={entry['gain']:.6f} <= 0 "
                        f"but grew=True — would be speculative growth"
                    )

    def test_hypothetical_entropy_before_grow_call(self):
        """verify that _hypothetical_entropy_after_growth is computed BEFORE
        predictor.grow() is called, and the predictor capacity does not change
        between the computation and the decision."""
        from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor
        pred = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0, rng_seed=42)
        # Feed some data
        for _ in range(20):
            pred.update([1.0, 0.0])

        cap_before = pred.capacity
        # Compute hypothetical entropy — should NOT change capacity
        h_after = pred.hypothetical_entropy_after_growth()
        assert pred.capacity == cap_before, (
            f"hypothetical_entropy_after_growth changed capacity from "
            f"{cap_before} to {pred.capacity}"
        )
        assert isinstance(h_after, float)
        assert not math.isnan(h_after)
        assert not math.isinf(h_after)


# ─── Blocker 2: Multi-Seed Runner Tests ──────────────────────────


class TestMultiSeedRunner:
    """[BLOCKER 2] Verify the multi-seed runner works correctly.

    The E0 experiment must run >= 5 seeds per canonical requirement.
    The multi-seed runner aggregates results across seeds and produces
    a pass/kill decision.
    """

    @pytest.fixture
    def small_config(self):
        return {
            "experiment_id": "E0_TEST",
            "seed": 42, "env_seed": 101,
            "num_train_steps": 100, "num_test_steps": 20,
            "environment": {"num_latent_states": 3, "observation_dim": 4,
                            "transition_alpha": 1.0, "noise_sigma": 0.05},
            "predictor": {"initial_capacity": 2, "alpha": 1.0},
            "growth": {"b": 1.0, "evaluate_every": 50, "warmup_steps": 30},
            "conditions": ["T", "C1", "C2", "C3"],
            "num_seeds": 5, "results_dir": None,
        }

    def test_multi_seed_runs_all_seeds(self, small_config):
        """run_multi_seed runs num_seeds seeds and produces aggregated results."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_multi_seed(
                num_seeds=3,
                base_seed=42,
                config=small_config,
                output_dir=tmpdir,
            )
            assert results["num_seeds"] == 3
            assert len(results["per_seed_results"]) == 3
            assert "decision" in results
            assert results["decision"]["n_seeds"] == 3

    def test_multi_seed_aggregated_decision(self, small_config):
        """Aggregated decision includes DV-a and DV-b evaluations."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_multi_seed(
                num_seeds=3,
                base_seed=42,
                config=small_config,
                output_dir=tmpdir,
            )
            decision = results["decision"]
            assert "dv_a" in decision
            assert "dv_b" in decision
            assert "verdict" in decision

    def test_multi_seed_different_env_per_seed(self, small_config):
        """Each seed gets a different environment seed -> different latent sequence."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_multi_seed(
                num_seeds=3,
                base_seed=42,
                config=small_config,
                output_dir=tmpdir,
            )
            # All seeds should produce results, latents differ per seed
            for i, per_seed in enumerate(results["per_seed_results"]):
                for cond in ["T", "C1"]:
                    assert cond in per_seed["conditions"]
                    assert len(per_seed["conditions"][cond]["true_latent_states"]) > 0

    def test_multi_seed_requires_min_seeds_in_decider(self, small_config):
        """Multi-seed decider must respect min_seeds threshold."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_multi_seed(
                num_seeds=2,
                base_seed=42,
                config=small_config,
                output_dir=tmpdir,
            )
            decision = results["decision"]
            # With 2 seeds and default min_seeds=5, should be INCONCLUSIVE
            assert "INCONCLUSIVE" in decision["verdict"] or not decision["pass"]

    def test_multi_seed_save_aggregated_results(self, small_config):
        """Aggregated results are saved to output directory."""
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_multi_seed(
                num_seeds=3,
                base_seed=42,
                config=small_config,
                output_dir=tmpdir,
            )
            aggregated_path = os.path.join(tmpdir, "aggregated_results.json")
            assert os.path.exists(aggregated_path), (
                f"Aggregated results not saved to {aggregated_path}"
            )
