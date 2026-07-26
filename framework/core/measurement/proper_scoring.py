"""Proper scoring rules for evaluating predictive distributions.

Extracted from backend/cognition/decision_policy.py (log-loss component).
"""

import math
from typing import List, Optional, Sequence


def log_loss(y_true: List[float], y_pred: List[float], eps: float = 1e-15) -> float:
    """Logarithmic loss (cross-entropy) between true and predicted probabilities.

    LL = -sum(y_true_i * log(y_pred_i)) / n

    Lower is better. Perfect score is 0.0.
    """
    n = len(y_true)
    if n == 0:
        return 0.0

    total = 0.0
    for t, p in zip(y_true, y_pred):
        p = max(min(p, 1.0 - eps), eps)
        total += t * math.log(p) + (1.0 - t) * math.log(1.0 - p)

    return -total / n


def brier_score(y_true: List[float], y_pred: List[float]) -> float:
    """Brier score: mean squared error between predictions and outcomes.

    BS = sum((y_true_i - y_pred_i)^2) / n

    Lower is better. Perfect score is 0.0.
    """
    n = len(y_true)
    if n == 0:
        return 0.0

    return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n


def expected_calibration_error(
    probabilities: List[float],
    outcomes: List[int],
    n_bins: int = 10,
) -> float:
    """Expected Calibration Error (ECE).

    Partitions predictions into n_bins equally-spaced bins and computes
    the weighted average of |accuracy - confidence| within each bin.
    """
    if len(probabilities) == 0:
        return 0.0

    bin_boundaries = [i / n_bins for i in range(n_bins + 1)]
    ece = 0.0
    total = len(probabilities)

    for i in range(n_bins):
        in_bin = [
            j for j, p in enumerate(probabilities) if bin_boundaries[i] <= p < bin_boundaries[i + 1]
        ]
        if not in_bin:
            continue

        bin_accuracy = sum(outcomes[j] for j in in_bin) / len(in_bin)
        bin_confidence = sum(probabilities[j] for j in in_bin) / len(in_bin)

        ece += (len(in_bin) / total) * abs(bin_accuracy - bin_confidence)

    return ece


def predictive_log_likelihood(
    predicted_probs: Sequence[float],
    actual_index: int,
    eps: float = 1e-15,
) -> float:
    """Canonical log score L = -log P_θ(x_{t+1} | x_{≤t}).

    The unique local strictly-proper scoring rule (Bernardo 1979) —
    a derivation, not a choice. Permanently replaces E = λH + μS + νA.

    Reference: PROGRAM_D_CANONICAL.md §5.3

    Parameters
    ----------
    predicted_probs : Sequence[float]
        Predictive probability distribution over next observation.
    actual_index : int
        Index of the actual observed value in the distribution.
    eps : float
        Small constant to prevent log(0).

    Returns
    -------
    float
        The log-likelihood log P_θ(x_{t+1} | x_{≤t}).
        Higher values indicate better predictions.
        The negative of this is the proper scoring loss L.
    """
    probs = list(predicted_probs)
    if actual_index < 0 or actual_index >= len(probs):
        return math.log(eps)
    p = max(min(probs[actual_index], 1.0 - eps), eps)
    return math.log(p)


def scoring_loss(
    predicted_probs: Sequence[float],
    actual_index: int,
    eps: float = 1e-15,
) -> float:
    """Proper scoring loss L = -log P_θ(x_{t+1} | x_{≤t}).

    This is the canonical loss used in E0's DV-a.
    Lower values indicate better predictions.
    Perfect score is 0.0.

    Reference: PROGRAM_D_CANONICAL.md §5.3
    """
    return -predictive_log_likelihood(predicted_probs, actual_index, eps)


def r2_score(y_true: List[float], y_pred: List[float]) -> float:
    """Coefficient of determination (R^2).

    R^2 = 1 - SS_res / SS_tot

    Best possible score is 1.0. Can be negative.
    """
    n = len(y_true)
    if n < 2:
        return 0.0

    mean_true = sum(y_true) / n
    ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))
    ss_tot = sum((t - mean_true) ** 2 for t in y_true)

    if ss_tot == 0:
        return 0.0

    return 1.0 - ss_res / ss_tot
