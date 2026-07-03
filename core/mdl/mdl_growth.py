"""MDL-based growth trigger and description length computation.

The MDL criterion for concept birth:
    G = H_before - H_after - lambda_model

A new concept is born when the description-length gain G exceeds a threshold.
"""
import math
from typing import List, Optional, Tuple


def description_length(data: List[float], model_params: int) -> float:
    """Compute two-part MDL description length.

    L(D, M) = L(M) + L(D | M)

    Where L(M) is the model complexity (function of parameter count) and
    L(D | M) is the negative log-likelihood of data under the model.
    """
    n = len(data)
    if n == 0:
        return 0.0

    log_likelihood = _negative_log_likelihood(data)
    model_cost = model_params * math.log(n) / 2.0

    return model_cost + log_likelihood


def mdl_gain(
    entropy_before: float,
    entropy_after: float,
    lambda_model: float = 1.0,
) -> float:
    """MDL gain from adding a new concept.

    G = H_before - H_after - lambda_model

    Positive gain means the new concept improves the description.
    """
    return entropy_before - entropy_after - lambda_model


def should_birth_concept(
    entropy_before: float,
    entropy_after: float,
    birth_threshold: float = 1.0,
    lambda_model: float = 1.0,
) -> Tuple[bool, float]:
    """Decide whether a new concept should be born based on MDL gain.

    Returns (decision, gain).
    """
    gain = mdl_gain(entropy_before, entropy_after, lambda_model)
    return gain > birth_threshold, gain


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
