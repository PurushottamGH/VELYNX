"""Synthetic nonlinear latent environment for E0.

Generates a sequence from a known hidden Markov model with K latent states
and nonlinear observation mixing. The nonlinearity is configured so that a
linear or fixed-capacity predictor cannot recover the latent structure
(verified offline by experiments/E0/leakage_check.py).

Reference: PROGRAM_D_CANONICAL.md §7 (E0)
           SCIENTIFIC_EXECUTION_SPEC.md §E0
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np


class NonlinearLatentEnvironment:
    """Synthetic environment with K latent states and nonlinear observations.

    The latent process is a Markov chain over K discrete states with a
    random transition matrix (Dirichlet-distributed rows).

    The observation at each step is a nonlinear (polynomial + sinusoidal)
    mixing of the latent state's base vector. This ensures that linear
    methods cannot trivially recover the latent structure.

    Parameters
    ----------
    num_latent_states : int
        Number of latent states K (default 10).
    observation_dim : int
        Dimensionality of the observation vector (default 16).
    transition_alpha : float
        Dirichlet concentration for transition matrix rows (default 1.0).
        Lower values produce more deterministic dynamics.
    noise_sigma : float
        Standard deviation of Gaussian observation noise (default 0.05).
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        num_latent_states: int = 10,
        observation_dim: int = 16,
        transition_alpha: float = 1.0,
        noise_sigma: float = 0.05,
        seed: Optional[int] = None,
    ):
        if num_latent_states < 2:
            raise ValueError("num_latent_states must be >= 2")
        if observation_dim < 2:
            raise ValueError("observation_dim must be >= 2")

        self.K = num_latent_states
        self.D = observation_dim
        self.noise_sigma = noise_sigma
        self._transition_alpha = transition_alpha
        self._rng = np.random.RandomState(seed)
        self._env_seed = seed

        # Generate random transition matrix (Dirichlet-distributed rows)
        self._transition_matrix: np.ndarray = self._rng.dirichlet(
            [transition_alpha] * self.K,
            size=self.K,
        )

        # Generate latent state base vectors on a hypersphere
        self._base_vectors: np.ndarray = self._rng.randn(self.K, self.D)
        self._base_vectors /= np.linalg.norm(self._base_vectors, axis=1, keepdims=True)

        # Generate random nonlinear mixing coefficients
        # Each latent state has a 3rd-order polynomial mixing
        self._mixing_coeffs: np.ndarray = self._rng.randn(self.K, self.D, 4) * 0.5

        # Current latent state
        self._current_state: int = self._rng.randint(0, self.K)

        # Observation history (for analysis)
        self._latent_history: List[int] = [self._current_state]
        self._observation_history: List[np.ndarray] = []

    @property
    def current_latent_state(self) -> int:
        """The current true latent state index."""
        return self._current_state

    @property
    def latent_history(self) -> List[int]:
        """Full history of latent states."""
        return self._latent_history.copy()

    @property
    def observation_history(self) -> List[np.ndarray]:
        """Full history of observations."""
        return self._observation_history.copy()

    @property
    def transition_matrix(self) -> np.ndarray:
        """The K x K transition probability matrix."""
        return self._transition_matrix.copy()

    @property
    def base_vectors(self) -> np.ndarray:
        """The K base vectors (one per latent state)."""
        return self._base_vectors.copy()

    def step(self) -> Tuple[int, np.ndarray]:
        """Advance one time step.

        Returns
        -------
        Tuple[int, np.ndarray]
            (latent_state, observation_vector)
            observation_vector is a D-dimensional float array.
        """
        # Sample next latent state from transition matrix
        self._current_state = self._rng.choice(
            self.K,
            p=self._transition_matrix[self._current_state],
        )

        # Generate nonlinear observation
        obs = self._nonlinear_observation(self._current_state)

        # Add Gaussian noise
        obs += self._rng.randn(self.D) * self.noise_sigma

        self._latent_history.append(self._current_state)
        self._observation_history.append(obs.copy())

        return self._current_state, obs

    def generate_sequence(self, length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate a full sequence of observations and latent states.

        Parameters
        ----------
        length : int
            Number of time steps to generate.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            (latent_states, observations)
            latent_states : shape (length,) integer array
            observations  : shape (length, D) float array
        """
        states: List[int] = []
        observations: List[np.ndarray] = []
        for _ in range(length):
            s, o = self.step()
            states.append(s)
            observations.append(o)
        return np.array(states), np.array(observations)

    def generate_train_test_sequences(
        self,
        train_length: int,
        test_length: int,
    ) -> Dict[str, np.ndarray]:
        """Generate non-overlapping train and test sequences.

        The test sequence uses the same transition matrix and base vectors
        but starts from a random state (no overlap with training).

        Returns
        -------
        dict with keys: train_states, train_obs, test_states, test_obs
        """
        # Train
        self.reset()
        train_states, train_obs = self.generate_sequence(train_length)

        # Test (starts fresh, different initial state)
        self.reset()
        test_states, test_obs = self.generate_sequence(test_length)

        return {
            "train_states": train_states,
            "train_obs": train_obs,
            "test_states": test_states,
            "test_obs": test_obs,
        }

    def reset(self) -> None:
        """Reset to initial state at t=0."""
        self._current_state = self._rng.randint(0, self.K)
        self._latent_history = [self._current_state]
        self._observation_history = []

    def get_state_info(self) -> dict:
        """Return environment metadata for reproducibility."""
        return {
            "num_latent_states": self.K,
            "observation_dim": self.D,
            "noise_sigma": self.noise_sigma,
            "env_seed": self._env_seed,
            "transition_matrix_shape": list(self._transition_matrix.shape),
        }

    # --- Internal ---

    def _nonlinear_observation(self, latent_state: int) -> np.ndarray:
        """Generate a nonlinear mixing of the latent state's base vector.

        The observation is a 3rd-order polynomial function of the base
        vector components, with cross-term interactions between dimensions.
        This creates a nonlinear mapping that linear methods cannot invert.

        f(x) = a0 + a1*x + a2*x^2 + a3*sin(x) + cross_terms
        """
        base = self._base_vectors[latent_state]
        coeffs = self._mixing_coeffs[latent_state]
        obs = np.zeros(self.D)

        for d in range(self.D):
            x = base[d]
            # Polynomial: a0 + a1*x + a2*x^2 + a3*sin(x)
            obs[d] = (
                coeffs[d, 0]
                + coeffs[d, 1] * x
                + coeffs[d, 2] * x**2
                + coeffs[d, 3] * math.sin(x * math.pi)
            )

        # Add cross-dimensional interactions (nonlinear mixing)
        # Sample a few random cross-term pairs for additional nonlinearity
        cross_terms = 0.0
        for _ in range(min(3, self.D // 2)):
            d1 = self._rng.randint(0, self.D)
            d2 = self._rng.randint(0, self.D)
            if d1 != d2:
                cross_terms += 0.1 * base[d1] * base[d2] * base[(d1 + d2) % self.D]

        obs += cross_terms

        # Normalize to unit norm
        norm = np.linalg.norm(obs)
        if norm > 0:
            obs /= norm

        return obs


def create_environment(
    num_latent_states: int = 10,
    observation_dim: int = 16,
    seed: Optional[int] = None,
) -> NonlinearLatentEnvironment:
    """Factory function for creating a nonlinear latent environment."""
    return NonlinearLatentEnvironment(
        num_latent_states=num_latent_states,
        observation_dim=observation_dim,
        seed=seed,
    )
