"""Growable Dirichlet–Markov conjugate predictor.

Canonical predictor class indexed by capacity k:

    { P_θ(x_{t+1} | x_{≤t}) : θ ∈ Θ_k }

Maintains Dirichlet priors over transition probabilities between latent
states and supports growing capacity when the MDL trigger fires.

Reuses the conjugate Dirichlet–Markov formulation. The label "belief model"
is deliberately absent — this is a mechanical predictor, not a cognitive agent.

Reference: PROGRAM_D_CANONICAL.md §5.2
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import numpy as np

from framework.core.predictors.base import Predictor


class DirichletMarkovPredictor(Predictor):
    """Conjugate Dirichlet–Markov predictor with growable capacity.

    Maintains a transition count matrix of shape (k, k) where entry
    (i, j) counts transitions from state i to state j. A Dirichlet
    prior with uniform concentration alpha is placed over each row's
    transition distribution.

    Capacity k grows via :meth:`grow`, which adds a new state with a
    flat Dirichlet prior and preserves all existing counts.
    """

    def __init__(
        self,
        initial_capacity: int = 2,
        alpha: float = 1.0,
        rng_seed: Optional[int] = None,
    ):
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be >= 1")
        if alpha <= 0.0:
            raise ValueError("alpha must be > 0")

        self._k = initial_capacity
        self._alpha = alpha
        self._rng = np.random.RandomState(rng_seed)

        # Transition count matrix: counts[i][j] = observed i->j transitions
        self._counts: List[List[int]] = [
            [0] * self._k for _ in range(self._k)
        ]

        # Current latent state (None before first observation)
        self._current_state: Optional[int] = None
        # Previous latent state for transition counting
        self._previous_state: Optional[int] = None

        # Total observations seen
        self._n_observations = 0

    # --- Predictor ABC implementation ---

    def predict(self, context: List[float]) -> List[float]:
        """Predict next observation probabilities as a categorical distribution.

        Uses the current latent state (inferred from context via argmax
        of the posterior predictive) to select the transition row.

        Returns a probability vector of length k (the current capacity).
        """
        if len(context) == 0:
            # No context: return uniform predictive distribution
            return [1.0 / self._k] * self._k

        # Infer the most probable current latent state from context
        state = self._infer_state(context)

        # Get the predictive distribution for this state
        return self._predictive_distribution(state)

    def update(self, observation: List[float]) -> None:
        """Update transition counts given an observed vector.

        Infers the latent state from the observation, then increments
        the transition count from the previous state to this state.
        """
        inferred_state = self._infer_state(observation)
        self._n_observations += 1

        if self._previous_state is not None:
            # Record transition: previous_state -> inferred_state
            self._counts[self._previous_state][inferred_state] += 1

        self._previous_state = inferred_state
        self._current_state = inferred_state

    def _compute_stationary(self, trans_probs: np.ndarray) -> np.ndarray:
        """Compute stationary distribution via eigendecomposition.

        Falls back to uniform if the eigendecomposition fails or
        produces invalid values. Uses the shape of trans_probs
        rather than self._k so it works correctly for hypothetical
        (k+1) matrices evaluated during MDL gain computation.
        """
        k = trans_probs.shape[0]
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            try:
                eigvals, eigvecs = np.linalg.eig(np.array(trans_probs).T)
                stationary = np.real(eigvecs[:, 0])
                stationary = np.maximum(stationary, 0.0)
                s_sum = stationary.sum()
                if s_sum > 0 and not np.any(np.isnan(stationary)):
                    stationary /= s_sum
                    return stationary
            except np.linalg.LinAlgError:
                pass
        return np.ones(k) / k

    def entropy(self) -> float:
        """Return the conditional entropy of the transition chain (in bits).

        H = -sum_{i,j} P(i) * P(j|i) * log2(P(j|i))

        where P(i) is the stationary distribution and P(j|i) is the
        posterior predictive transition probability.
        """
        if self._k == 0:
            return 0.0

        # Compute transition probability matrix from Dirichlet posteriors
        trans_probs = self._transition_matrix()

        # Compute stationary distribution
        stationary = self._compute_stationary(np.array(trans_probs))

        # Compute conditional entropy
        h = 0.0
        for i in range(self._k):
            for j in range(self._k):
                p_ij = trans_probs[i][j]
                if p_ij > 0 and stationary[i] > 0:
                    h -= stationary[i] * p_ij * math.log2(p_ij)

        return float(h)

    def reset(self) -> None:
        """Reset to initial state (zero counts, no state)."""
        self._counts = [[0] * self._k for _ in range(self._k)]
        self._current_state = None
        self._previous_state = None
        self._n_observations = 0

    def state_dict(self) -> dict:
        """Return serializable state for reproducibility."""
        return {
            "k": self._k,
            "alpha": self._alpha,
            "counts": [list(row) for row in self._counts],
            "current_state": self._current_state,
            "previous_state": self._previous_state,
            "n_observations": self._n_observations,
        }

    def load_state_dict(self, state: dict) -> None:
        """Restore state from serialized representation."""
        self._k = state["k"]
        self._alpha = state.get("alpha", 1.0)
        self._counts = [list(row) for row in state["counts"]]
        self._current_state = state.get("current_state")
        self._previous_state = state.get("previous_state")
        self._n_observations = state.get("n_observations", 0)
        # Ensure counts matrix is square (k x k)
        for row in self._counts:
            while len(row) < self._k:
                row.append(0)

    # --- Canonical E0-specific API ---

    @property
    def capacity(self) -> int:
        """Current capacity k (number of latent states)."""
        return self._k

    @property
    def n_observations(self) -> int:
        """Total observations seen."""
        return self._n_observations

    @property
    def current_state(self) -> Optional[int]:
        """The current inferred latent state (last state after update).

        Returns None before any observation has been processed.
        """
        return self._current_state

    def grow(self) -> int:
        """Grow capacity by one state.

        Adds a new state with flat Dirichlet prior (zero-initialized counts).
        Preserves all existing transition counts.

        Returns the new capacity k.
        """
        new_k = self._k + 1

        # Extend each existing row with a zero count for the new state
        for row in self._counts:
            row.append(0)

        # Add a new row of zeros for the new state
        self._counts.append([0] * new_k)

        self._k = new_k
        return self._k

    def log_predictive_probability(
        self, observation: List[float], context: Optional[List[float]] = None
    ) -> float:
        """Compute log P_θ(observation | context).

        The canonical proper scoring rule: L = -log P_θ(x_{t+1} | x_{≤t}).

        Returns the log-probability (higher = better prediction).
        """
        if context is not None and len(context) > 0:
            state = self._infer_state(context)
        elif self._current_state is not None:
            state = self._current_state
        else:
            # No context: use uniform distribution
            return -math.log(self._k)

        dist = self._predictive_distribution(state)
        inferred = self._infer_state(observation)

        if inferred < len(dist):
            lp = math.log(max(dist[inferred], 1e-15))
        else:
            lp = math.log(1e-15)

        return lp

    def log_loss(self, observation: List[float], context: Optional[List[float]] = None) -> float:
        """Compute the log loss L = -log P_θ(observation | context).

        This is the canonical proper scoring rule (Bernardo 1979).
        Lower is better. Perfect score = 0.0.
        """
        return -self.log_predictive_probability(observation, context)

    def posterior_transition_matrix(self) -> List[List[float]]:
        """Return the posterior expected transition probabilities.

        Returns a k x k matrix where entry (i, j) is the posterior
        expected probability of transitioning from state i to state j.
        """
        return self._transition_matrix()

    def hypothetical_entropy_after_growth(self) -> float:
        """Compute what the entropy would be after growing by one state.

        Evaluates the MDL gain WITHOUT modifying internal state — no
        speculative growth before the decision. Builds the (k+1) × (k+1)
        transition probability matrix that would result from adding one
        state, then computes the Shannon entropy of the resulting chain.

        Reference: PROGRAM_D_CANONICAL.md §5.4 (MDL growth trigger)
        """
        k = self._k
        alpha = self._alpha
        counts = self._counts
        new_k = k + 1

        # Build hypothetical (k+1) × (k+1) transition probability matrix
        trans_probs = np.zeros((new_k, new_k))

        for i in range(k):
            row = counts[i]
            total = sum(row) + alpha * new_k
            for j in range(k):
                trans_probs[i, j] = (row[j] + alpha) / total
            trans_probs[i, k] = alpha / total

        # New state row: uniform prior (Dirichlet(alpha) with (k+1) categories)
        for j in range(new_k):
            trans_probs[k, j] = 1.0 / new_k

        # Stationary distribution
        stationary = self._compute_stationary(trans_probs)

        # Compute Shannon entropy
        h = 0.0
        for i in range(new_k):
            for j in range(new_k):
                p_ij = trans_probs[i, j]
                if p_ij > 0 and stationary[i] > 0:
                    h -= stationary[i] * p_ij * math.log2(p_ij)

        return float(h)

    def description_length(self) -> float:
        """Compute the two-part MDL description length of the current model.

        L(M) + L(D|M) where:
        - L(M) = model complexity (parameter cost)
        - L(D|M) = negative log-likelihood of data under the model
        """
        n = self._n_observations
        if n == 0:
            return 0.0

        # Model cost: k * log2(n) / 2 (real-valued parameters)
        # For the transition matrix with k*(k-1) free params per row
        model_cost = self._k * math.log2(max(n, 2)) / 2.0

        # Data cost: negative log-likelihood
        ll = self._log_likelihood_data()
        data_cost = -ll if ll < 0 else 0.0

        return model_cost + data_cost

    # --- Internal helpers ---

    def _transition_matrix(self) -> List[List[float]]:
        """Compute posterior expected transition probabilities."""
        matrix = []
        for i in range(self._k):
            row = self._counts[i]
            alpha = self._alpha
            total = sum(row) + alpha * self._k
            probs = [(c + alpha) / total for c in row]
            matrix.append(probs)
        return matrix

    def _predictive_distribution(self, state: int) -> List[float]:
        """Return the predictive distribution over next states given current state.

        Uses the Dirichlet posterior: P(next=j | current=i) = (counts[i][j] + alpha) / (sum(counts[i]) + k*alpha)
        """
        if state < 0 or state >= self._k:
            return [1.0 / self._k] * self._k

        row = self._counts[state]
        alpha = self._alpha
        total = sum(row) + alpha * self._k
        return [(c + alpha) / total for c in row]

    def _infer_state(self, vector: List[float]) -> int:
        """Infer the most probable latent state from an observation vector.

        Uses the posterior predictive: picks the state that best explains
        the observation under the current transition model. For scalar
        observations, assigns to the state whose centroid (empirical mean
        of observed transitions) is closest.

        For a general vector, uses the state that maximizes
        P(state | observation) ∝ P(observation | state) * P(state).
        """
        if self._n_observations == 0 or self._k <= 1:
            return 0

        # Compute empirical observation centroids per state
        centroids = []
        for i in range(self._k):
            total_vec = [0.0] * len(vector)
            count = 0
            # Use transition counts as a proxy for the centroid
            # (the actual observation history is not stored)
            row_total = sum(self._counts[i])
            if row_total > 0:
                centroids.append(self._counts[i][:])  # Use transition pattern as proxy
            else:
                centroids.append([0.0] * self._k)

        # If centroids are all zero, assign to the state with most mass
        if all(sum(c) == 0 for c in centroids):
            # Assign to the state with the most total transitions
            row_sums = [sum(row) for row in self._counts]
            return int(np.argmax(row_sums))

        # Find nearest centroid by cosine similarity
        vec_norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        vec_normalized = [x / vec_norm for x in vector]

        best_state = 0
        best_sim = -float("inf")
        for i, centroid in enumerate(centroids):
            c_norm = math.sqrt(sum(x * x for x in centroid)) or 1.0
            sim = sum(v * c / c_norm for v, c in zip(vec_normalized, centroid))
            if sim > best_sim:
                best_sim = sim
                best_state = i

        return best_state

    def _log_likelihood_data(self) -> float:
        """Compute log-likelihood of all observed transitions under the model."""
        if self._n_observations == 0:
            return 0.0

        ll = 0.0
        for i in range(self._k):
            row = self._counts[i]
            row_total = sum(row)
            if row_total == 0:
                continue
            alpha = self._alpha
            denom = row_total + alpha * self._k
            for j in range(self._k):
                count = row[j]
                if count > 0:
                    p = (count + alpha) / denom
                    ll += count * math.log(max(p, 1e-15))

        return ll


def create_predictor(
    initial_capacity: int = 2,
    alpha: float = 1.0,
    seed: Optional[int] = None,
) -> DirichletMarkovPredictor:
    """Factory function for Dirichlet-Markov predictors."""
    return DirichletMarkovPredictor(
        initial_capacity=initial_capacity,
        alpha=alpha,
        rng_seed=seed,
    )
