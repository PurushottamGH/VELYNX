"""MDL-based growth trigger — pinned canonical derivation.

Canonical MDL growth operator:

    G = H_before − H_after − λ_model > 0

where λ_model = k · b + n · log₂ N  (concept-birth ledger).

This is a **derivation, not a configurable threshold**. A hand-set λ
violates I2 by construction (failure mode F2). The formula is hardcoded
and non-tunable.

Reference: PROGRAM_D_CANONICAL.md §5.4
           literature/program_d_mathematical_provenance.md §2
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple


# --- Canonical constants ---

BITS_PER_PARAMETER = 1.0
"""Bit cost per model parameter (b in the canonical formula).

This is a scientific constant, not a tunable hyperparameter.
It represents the cost of encoding one integer state index in bits.
"""


# --- Canonical λ_model derivation ---


def compute_lambda_model(
    k: int,
    n: int,
    N: int,
    b: float = BITS_PER_PARAMETER,
) -> float:
    """Compute the canonical MDL model complexity penalty.

    λ_model = k · b + n · log₂ N

    Parameters
    ----------
    k : int
        Number of model parameters (current capacity = number of states).
    n : int
        Dimensionality of each parameter (typically = k for a k×k
        transition matrix).
    N : int
        Total number of observations (data points) seen so far.
    b : float
        Bit cost per parameter. Default is BITS_PER_PARAMETER = 1.0.

    Returns
    -------
    float
        The model complexity penalty in bits.

    Raises
    ------
    ValueError
        If any argument is non-positive.
    """
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if N < 1:
        raise ValueError(f"N must be >= 1, got {N}")
    if b <= 0.0:
        raise ValueError(f"b must be > 0, got {b}")

    return float(k * b + n * math.log2(max(N, 1)))


# --- Canonical growth trigger ---


def mdl_gain(
    entropy_before: float,
    entropy_after: float,
    lambda_model: float,
) -> float:
    """Compute the MDL gain from a growth operation.

    G = H_before − H_after − λ_model

    A positive gain means the structural addition (e.g., new state)
    genuinely improves the model description, justifying the added
    complexity.

    Parameters
    ----------
    entropy_before : float
        Predictive entropy (or description length) before growth.
    entropy_after : float
        Predictive entropy (or description length) after growth.
    lambda_model : float
        Model complexity penalty (from compute_lambda_model).

    Returns
    -------
    float
        The MDL gain. Positive => growth is justified.
    """
    return entropy_before - entropy_after - lambda_model


def should_grow(
    entropy_before: float,
    entropy_after: float,
    k: int,
    n: int,
    N: int,
    b: float = BITS_PER_PARAMETER,
) -> Tuple[bool, float, float]:
    """Canonical growth decision: should the model grow?

    Wires together the MDL gain check: grows iff the description length
    strictly decreases (G > 0).

    This function replaces all configurable `birth_threshold` parameters
    with the derived λ_model. There is no tunable threshold.

    Parameters
    ----------
    entropy_before : float
        Predictive entropy before adding capacity.
    entropy_after : float
        Predictive entropy after adding capacity.
    k : int
        Current number of states (before growth).
    n : int
        Dimensionality of parameters (typically = k).
    N : int
        Total observations seen.
    b : float
        Bit cost per parameter (default 1.0).

    Returns
    -------
    Tuple[bool, float, float]
        (decision, gain, lambda_model)
        decision : True if model should grow (gain > 0)
        gain     : The MDL gain value
        lambda_model : The computed complexity penalty
    """
    lam = compute_lambda_model(k=k, n=n, N=N, b=b)
    gain = mdl_gain(entropy_before, entropy_after, lam)
    return gain > 0.0, gain, lam


# --- Description length utilities ---


def two_part_description_length(
    model_params: int,
    log_likelihood: float,
    n_observations: int,
) -> float:
    """Two-part MDL description length.

    L(M, D) = L(M) + L(D | M)

    Where L(M) is the model cost and L(D | M) is the negative
    log-likelihood of the data under the model.

    Parameters
    ----------
    model_params : int
        Number of free parameters in the model.
    log_likelihood : float
        Log-likelihood of the data under the model (natural log).
    n_observations : int
        Number of data points.

    Returns
    -------
    float
        Total description length in bits.
    """
    if n_observations <= 0:
        return 0.0

    # Model cost: (k * log2(N)) / 2 for continuous params, or k*b for discrete
    model_cost = model_params * math.log2(max(n_observations, 2)) / 2.0

    # Data cost: -log-likelihood (convert from nats to bits if needed)
    data_cost = -log_likelihood / math.log(2.0)

    return model_cost + data_cost


# --- Deprecated / legacy compatibility shim ---

def description_length(data: List[float], model_params: int) -> float:
    """Legacy description length (kept for backward compatibility).

    **Note:** This function predates the canonical derivation and
    should not be used in new E0 experiment code. Use
    :func:`two_part_description_length` instead.
    """
    n = len(data)
    if n == 0:
        return 0.0

    log_likelihood = _negative_log_likelihood(data)
    model_cost = model_params * math.log(n) / 2.0
    return model_cost + log_likelihood


def _negative_log_likelihood(data: List[float]) -> float:
    """Negative log-likelihood assuming Gaussian distribution."""
    n = len(data)
    if n < 2:
        return 0.0
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / (n - 1)
    if variance <= 0:
        return 0.0
    ll = -0.5 * n * (math.log(2 * math.pi * variance) + 1)
    return -ll


def normalized_entropy(counts: List[int]) -> float:
    """Shannon entropy normalized by log2(number of bins).

    Returns 0.0 for degenerate input, 1.0 for uniform distribution.
    """
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    k = len(counts)
    if k <= 1:
        return 0.0
    return h / math.log2(k)
