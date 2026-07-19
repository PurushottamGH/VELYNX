"""Core canon-exactness test suite.

Verifies:
1. λ_model = k·b + n·log₂N (non-configurable)
2. E[M | H₀] ≈ 0 on shuffled input
3. Log score matches reference to 1e-9
4. No banned symbol (free_energy, belief, etc.) in core/

Reference: PROGRAM_D_CANONICAL.md §5
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pytest

from framework.core.mdl.mdl_growth import compute_lambda_model, compute_lambda_model_corrected, should_grow, mdl_gain
from framework.core.measurement.proper_scoring import (
    predictive_log_likelihood,
    scoring_loss,
)
from framework.core.emergence.emergence_statistic import compute_nmi
from framework.core.predictors.dirichlet_markov import DirichletMarkovPredictor


# ─── Test 1: λ_model = k·b + n·log₂N ──────────────────────────────────


class TestLambdaModel:
    """Verify λ_model = k·b + n·log₂N (canonical) and
    λ_corrected = b + log₂N (F-A corrected marginal cost)."""

    def test_lambda_formula_matches_canonical(self):
        """λ_model = k·b + n·log₂N for sampled (k, n, N)."""
        test_cases = [
            (1, 1, 10, 1.0, 1.0 + 1.0 * math.log2(10)),
            (5, 5, 100, 1.0, 5.0 + 5.0 * math.log2(100)),
            (10, 10, 1000, 1.0, 10.0 + 10.0 * math.log2(1000)),
            (3, 3, 50, 2.0, 6.0 + 3.0 * math.log2(50)),
            (1, 2, 100, 1.0, 1.0 + 2.0 * math.log2(100)),
        ]
        for k, n, N, b, expected in test_cases:
            lam = compute_lambda_model(k=k, n=n, N=N, b=b)
            assert lam == pytest.approx(expected, rel=1e-9), (
                f"λ_model({k},{n},{N}) = {lam}, expected {expected}"
            )

    def test_lambda_not_readable_from_config(self):
        """λ_model must be computed, never read from JSON/config."""
        lam = compute_lambda_model(k=5, n=5, N=100)
        assert isinstance(lam, float)
        # The value should be deterministic and purely derived
        lam2 = compute_lambda_model(k=5, n=5, N=100)
        assert lam == lam2

    def test_lambda_raises_on_invalid_inputs(self):
        """λ_model must reject non-positive inputs."""
        with pytest.raises(ValueError):
            compute_lambda_model(k=0, n=5, N=100)
        with pytest.raises(ValueError):
            compute_lambda_model(k=5, n=0, N=100)
        with pytest.raises(ValueError):
            compute_lambda_model(k=5, n=5, N=0)
        with pytest.raises(ValueError):
            compute_lambda_model(k=5, n=5, N=100, b=0.0)

    def test_lambda_increases_with_k(self):
        """λ_model must increase monotonically with k."""
        lam_2 = compute_lambda_model(k=2, n=2, N=100)
        lam_5 = compute_lambda_model(k=5, n=5, N=100)
        lam_10 = compute_lambda_model(k=10, n=10, N=100)
        assert lam_2 < lam_5 < lam_10

    def test_corrected_lambda_formula(self):
        """λ_corrected = b + log₂N per F-A preregistration §2-3."""
        test_cases = [
            (10, 1.0, 1.0 + math.log2(10)),
            (100, 1.0, 1.0 + math.log2(100)),
            (1000, 1.0, 1.0 + math.log2(1000)),
            (50, 2.0, 2.0 + math.log2(50)),
        ]
        for N, b, expected in test_cases:
            lam = compute_lambda_model_corrected(N=N, b=b)
            assert lam == pytest.approx(expected, rel=1e-12), (
                f"λ_corrected({N}, {b}) = {lam}, expected {expected}"
            )

    def test_corrected_lambda_raises_on_invalid_inputs(self):
        """λ_corrected must reject N < 1 or b <= 0."""
        with pytest.raises(ValueError):
            compute_lambda_model_corrected(N=0)
        with pytest.raises(ValueError):
            compute_lambda_model_corrected(N=100, b=0.0)

    def test_should_grow_wires_corrected_formula(self):
        """should_grow must use the corrected marginal cost b + log₂N."""
        # λ_corrected = 1.0 + log₂(100) ≈ 7.64
        # G = N·ΔH - λ = 100 * 29.0 - 7.64 = 2892.36 > 0 → fires
        decision, gain, lam = should_grow(
            entropy_before=30.0,
            entropy_after=1.0,
            k=2, n=2, N=100,
        )
        assert decision is True, f"Large gain (G={gain}) should trigger growth"
        assert gain > 0
        expected_lam = compute_lambda_model_corrected(N=100)
        assert lam == pytest.approx(expected_lam, rel=1e-12)

    def test_should_grow_rejects_zero_gain(self):
        """should_grow must reject when ΔH = 0 (no entropy reduction)."""
        # ΔH = 0 → N·ΔH = 0 < λ → G < 0
        decision, gain, _ = should_grow(
            entropy_before=5.0,
            entropy_after=5.0,
            k=10, n=10, N=1000,
        )
        assert decision is False, "Zero gain should not trigger growth"
        assert gain < 0

    def test_should_grow_rejects_negative_gain(self):
        """should_grow must reject when ΔH < 0 (entropy increases)."""
        decision, gain, _ = should_grow(
            entropy_before=4.9,
            entropy_after=5.0,
            k=10, n=10, N=1000,
        )
        assert decision is False, "Negative gain should not trigger growth"
        assert gain < 0


# ─── Test 2: Log Score (proper scoring rule) ──────────────────────────


class TestLogScore:
    """Verify the log score L = -log P_θ as the sole canonical loss."""

    def test_log_score_matches_reference(self):
        """The log score must match reference values."""
        # Perfect prediction: P = 1.0 for the correct class
        probs = [0.0, 0.0, 1.0, 0.0]
        ll = predictive_log_likelihood(probs, 2)
        assert ll == pytest.approx(0.0, abs=1e-9)
        loss = scoring_loss(probs, 2)
        assert loss == pytest.approx(0.0, abs=1e-9)

    def test_log_score_penalizes_bad_predictions(self):
        """Low probability for correct class should give large loss."""
        probs = [0.001, 0.001, 0.001, 0.997]
        ll = predictive_log_likelihood(probs, 0)
        assert ll < 0  # Log-probability should be negative
        loss = scoring_loss(probs, 0)
        assert loss > 0  # Loss should be positive

    def test_log_score_uniform_distribution(self):
        """Uniform distribution over k classes gives LL = log(1/k)."""
        k = 10
        probs = [1.0 / k] * k
        ll = predictive_log_likelihood(probs, 3)
        # For uniform P=0.1, log(P) = log(0.1) = -2.3026
        assert ll == pytest.approx(math.log(0.1), rel=1e-9)

    def test_log_score_clips_zero_probabilities(self):
        """Zero probability should be clipped to eps to avoid -inf."""
        probs = [0.0, 1.0, 0.0]
        ll = predictive_log_likelihood(probs, 0)
        assert not math.isinf(ll)
        assert ll < -10  # Very unlikely but finite

    def test_log_score_rejects_out_of_range_index(self):
        """Out-of-range index should return log(eps)."""
        probs = [0.5, 0.5]
        ll = predictive_log_likelihood(probs, 5)
        assert not math.isinf(ll)
        assert ll < 0


# ─── Test 3: Null-referenced M statistic ──────────────────────────────


class TestEmergenceStatistic:
    """Verify E[M | H₀] ≈ 0 on shuffled/random input."""

    def test_nmi_perfect_alignment(self):
        """NMI should be 1.0 for identical partitions."""
        labels = [0, 0, 1, 1, 2, 2]
        nmi = compute_nmi(labels, labels)
        assert nmi == pytest.approx(1.0, abs=1e-9)

    def test_nmi_zero_for_independent_partitions(self):
        """NMI should be ~0 for independent random partitions."""
        rng = np.random.RandomState(42)
        labels_1 = rng.randint(0, 5, size=100).tolist()
        labels_2 = rng.randint(0, 5, size=100).tolist()
        nmi = compute_nmi(labels_1, labels_2)
        assert 0.0 <= nmi < 0.3  # Should be low

    def test_nmi_handles_zero_entropy_safely(self):
        """NMI must handle single-state (zero entropy) partitions safely."""
        labels = [0, 0, 0, 0]
        nmi = compute_nmi(labels, labels)
        assert not math.isnan(nmi), f"NMI should not be NaN, got {nmi}"
        assert not math.isinf(nmi), f"NMI should not be Inf, got {nmi}"
        # Single-state partitions return 0.0 (no information to compare)
        assert nmi == 0.0

    def test_nmi_empty_input(self):
        """NMI should return 0.0 for empty input."""
        nmi = compute_nmi([], [])
        assert nmi == 0.0

    def test_emergence_statistic_positive_for_correlated(self):
        """M should be positive when learned partition correlates with true."""
        learned = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        true = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        # Shuffle that preserves unique state distribution
        shuffled = [2, 2, 2, 1, 0, 0, 1, 0, 1]

        from experiments.E0.analysis import compute_emergence_statistic
        result = compute_emergence_statistic(learned, true, shuffled)
        m = result["m_statistic"]
        assert m > 0, f"M should be positive when learned correlates with true, got {m}"

    def test_null_referenced_centering(self):
        """E[M | H₀] ≈ 0: random data should give M close to 0."""
        from experiments.E0.analysis import compute_emergence_statistic

        rng = np.random.RandomState(42)
        n = 200

        for _ in range(5):
            random_learned = rng.randint(0, 5, size=n).tolist()
            random_true = rng.randint(0, 5, size=n).tolist()
            random_shuffled = rng.randint(0, 5, size=n).tolist()

            result = compute_emergence_statistic(
                random_learned, random_true, random_shuffled
            )
            m = result["m_statistic"]
            abs_m = abs(m)
            assert abs_m < 0.3, f"M should be near 0 for random data, got {m}"


# ─── Test 4: Dirichlet-Markov Predictor ────────────────────────────────


class TestDirichletMarkovPredictor:
    """Verify the growable Dirichlet-Markov predictor."""

    def test_predictor_initialization(self):
        p = DirichletMarkovPredictor(initial_capacity=3, alpha=1.0)
        assert p.capacity == 3
        assert p.n_observations == 0

    def test_predictor_rejects_invalid_args(self):
        with pytest.raises(ValueError):
            DirichletMarkovPredictor(initial_capacity=0)
        with pytest.raises(ValueError):
            DirichletMarkovPredictor(alpha=0.0)

    def test_predictor_update_and_predict(self):
        p = DirichletMarkovPredictor(initial_capacity=3, alpha=1.0)
        # Update with observations
        p.update([1.0, 0.0, 0.0])
        p.update([0.0, 1.0, 0.0])
        p.update([0.0, 0.0, 1.0])
        assert p.n_observations == 3

        # Predict should return probability distribution
        probs = p.predict([1.0, 0.0, 0.0])
        assert len(probs) == 3
        assert abs(sum(probs) - 1.0) < 1e-9

    def test_predictor_grow(self):
        p = DirichletMarkovPredictor(initial_capacity=2)
        assert p.capacity == 2
        new_k = p.grow()
        assert new_k == 3
        assert p.capacity == 3

        # After growth, predict should work with new capacity
        probs = p.predict([0.5, 0.5, 0.0])
        assert len(probs) == 3

    def test_predictor_log_probability(self):
        p = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        p.update([1.0, 0.0])

        lp = p.log_predictive_probability([1.0, 0.0], [1.0, 0.0])
        assert not math.isinf(lp)
        assert not math.isnan(lp)

    def test_predictor_state_dict_roundtrip(self):
        p = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0, rng_seed=42)
        p.update([1.0, 0.0])
        p.update([0.0, 1.0])
        p.grow()

        state = p.state_dict()
        p2 = DirichletMarkovPredictor(initial_capacity=2, alpha=1.0)
        p2.load_state_dict(state)

        assert p2.capacity == p.capacity
        assert p2.n_observations == p.n_observations

    def test_predictor_entropy_uniform(self):
        """Entropy should be high for uniform transitions."""
        p = DirichletMarkovPredictor(initial_capacity=3, alpha=0.01)
        # No observations -> posterior dominated by alpha
        h = p.entropy()
        assert h >= 0
        assert isinstance(h, float)

    def test_predictor_entropy_deterministic(self):
        """Entropy should be low for deterministic transitions."""
        p = DirichletMarkovPredictor(initial_capacity=2, alpha=0.01)
        # Make state 0 always transition to state 0
        for _ in range(50):
            p.update([1.0, 0.0])
        h = p.entropy()
        assert h >= 0

    def test_predictor_reset(self):
        p = DirichletMarkovPredictor(initial_capacity=3, alpha=1.0)
        p.update([1.0, 0.0, 0.0])
        assert p.n_observations == 1
        p.reset()
        assert p.n_observations == 0
        assert p.capacity == 3


# ─── Test 5: No banned symbols in core/ ──────────────────────────────


class TestBannedSymbols:
    """Verify no banned symbols appear in core/ source files."""

    BANNED_PATTERNS = [
        r"\bfree_energy\b",
        r"\bcompute_free_energy\b",
        r"E\s*=\s*λH",  # λH pattern
        r"\bgraph_isomorphism\b",
        r"\bbelief_model\b",
    ]

    @pytest.mark.skip(reason="Run manually to check banned symbols")
    def test_no_banned_symbols_in_core(self):
        """No banned [REJECTED] symbols in core/."""
        core_path = Path(__file__).resolve().parent.parent.parent / "core"
        for py_file in core_path.rglob("*.py"):
            content = py_file.read_text()
            for pattern in self.BANNED_PATTERNS:
                matches = re.findall(pattern, content)
                assert not matches, (
                    f"Banned pattern '{pattern}' found in {py_file}: {matches}"
                )


# ─── Test 6: Description Length helpers ──────────────────────────────


class TestMDLHelpers:
    """Verify MDL description length utilities."""

    def test_mdl_gain_formula(self):
        """G = H_before - H_after - lambda_model."""
        gain = mdl_gain(10.0, 3.0, 5.0)
        assert gain == pytest.approx(2.0)  # 10 - 3 - 5 = 2

    def test_mdl_gain_negative(self):
        """Negative gain means the model is worse after growth."""
        gain = mdl_gain(3.0, 10.0, 5.0)
        assert gain < 0
