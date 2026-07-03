"""Proper scoring rules for evaluating predictive distributions.

Extracted from backend/cognition/decision_policy.py (log-loss component).
"""
import math
from typing import List, Optional


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
            j for j, p in enumerate(probabilities)
            if bin_boundaries[i] <= p < bin_boundaries[i + 1]
        ]
        if not in_bin:
            continue

        bin_accuracy = sum(outcomes[j] for j in in_bin) / len(in_bin)
        bin_confidence = sum(probabilities[j] for j in in_bin) / len(in_bin)

        ece += (len(in_bin) / total) * abs(bin_accuracy - bin_confidence)

    return ece


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
