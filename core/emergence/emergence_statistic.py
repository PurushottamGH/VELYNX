"""Emergence statistics.

Normalized Mutual Information (NMI) estimator and related functions
for detecting emergent structure in predictive processing systems.
"""
import math
from typing import Dict, List
from collections import Counter


def compute_nmi(labels_true: List[int], labels_pred: List[int]) -> float:
    """Normalized Mutual Information between two cluster assignments.

    Uses the standard NMI formulation:
        NMI(X, Y) = 2 * I(X; Y) / (H(X) + H(Y))

    where I(X; Y) is mutual information and H is entropy.
    """
    n = len(labels_true)
    if n == 0:
        return 0.0

    contingency = {}
    for t, p in zip(labels_true, labels_pred):
        contingency[(t, p)] = contingency.get((t, p), 0) + 1

    n_t = Counter(labels_true)
    n_p = Counter(labels_pred)

    mi = 0.0
    for (t, p), n_tp in contingency.items():
        if n_tp > 0:
            mi += n_tp / n * math.log(n * n_tp / (n_t[t] * n_p[p]) + 1e-15)

    def entropy(counts):
        return -sum(c / n * math.log(c / n + 1e-15) for c in counts.values())

    h_true = entropy(n_t)
    h_pred = entropy(n_p)

    if h_true + h_pred == 0:
        return 0.0

    return 2.0 * mi / (h_true + h_pred)


def compute_held_out_log_likelihood(
    train_assignments: List[int],
    test_assignments: List[int],
    alpha: float = 1.0,
) -> float:
    """Held-out log-likelihood under a Dirichlet-Markov model.

    Uses add-alpha smoothing. Higher values indicate better generalization.
    """
    counts = Counter(train_assignments)
    total = sum(counts.values())
    k = len(counts)

    ll = 0.0
    for a in test_assignments:
        smoothed_p = (counts.get(a, 0) + alpha) / (total + alpha * k)
        ll += math.log(smoothed_p + 1e-15)

    return ll / len(test_assignments) if test_assignments else 0.0
