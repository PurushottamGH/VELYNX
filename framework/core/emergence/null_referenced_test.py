"""Null-referenced emergence test.

    M_0(θ_k) = M(θ_k) - E[M | H_0]

Where H_0 is the null hypothesis that observed structure is no different from
a shuffled or capacity-matched random process.
"""
import numpy as np
from typing import Callable, Optional


def null_referenced_statistic(
    observed_value: float,
    null_distribution: np.ndarray,
) -> dict:
    """Compute the null-referenced emergence statistic.

    Parameters
    ----------
    observed_value : float
        The value of the metric M on real data.
    null_distribution : np.ndarray
        Distribution of M under the null hypothesis H_0.

    Returns
    -------
    dict with keys:
        centered: M(θ_k) - E[M | H_0]
        z_score: (observed - mean_null) / std_null
        p_value: proportion of null distribution >= observed (one-sided)
    """
    mean_null = float(np.mean(null_distribution))
    std_null = float(np.std(null_distribution))

    centered = observed_value - mean_null
    z_score = centered / std_null if std_null > 0 else 0.0
    p_value = float(np.mean(null_distribution >= observed_value))

    return {
        "centered": centered,
        "z_score": z_score,
        "p_value": p_value,
        "mean_null": mean_null,
        "std_null": std_null,
    }


def shuffled_null_distribution(
    data: np.ndarray,
    metric_fn: Callable[[np.ndarray], float],
    n_shuffles: int = 1000,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Generate null distribution by shuffling temporal order.

    Preserves the marginal distribution of data while destroying temporal
    structure. This tests whether the metric captures genuine temporal
    dependencies rather than static statistical properties.
    """
    rng = np.random.RandomState(seed)
    null_values = []

    for _ in range(n_shuffles):
        shuffled = data.copy()
        rng.shuffle(shuffled)
        null_values.append(metric_fn(shuffled))

    return np.array(null_values)


def capacity_matched_null_distribution(
    data: np.ndarray,
    metric_fn: Callable[[np.ndarray], float],
    capacity: int,
    n_simulations: int = 1000,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Generate null distribution using capacity-matched random process.

    Creates a random process with the same capacity (number of states) as
    the observed system but without any structured dynamics. This tests
    whether the observed structure exceeds what a random process of
    equivalent complexity would produce.
    """
    rng = np.random.RandomState(seed)
    null_values = []

    indices = rng.randint(0, capacity, size=len(data))
    unique_states = np.unique(data)

    for _ in range(n_simulations):
        random_data = rng.choice(unique_states, size=len(data))
        null_values.append(metric_fn(random_data))

    return np.array(null_values)
