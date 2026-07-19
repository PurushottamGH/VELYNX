"""Consolidated metrics.

Single source of truth for all cognitive metrics.
Consolidates from validation/metrics.py, validation/shared_metrics_v1.py,
and research/metrics.py.
"""
import math
from typing import Dict, List, Mapping, Optional, Sequence, Tuple


# --- Free Energy Coefficients ---
LAMBDA = 1.0
MU = 2.0
NU = 0.5

# --- Thresholds ---
ENTROPY_HIGH = 2.0
SURPRISE_HIGH = 0.50
SURPRISE_MILD = 0.20
PRESSURE_HIGH = 1.00
PRESSURE_MILD = 0.25
ENERGY_EXHAUSTION = 18.0

Vector = Sequence[float]


def euclidean_distance(a: Vector, b: Vector) -> float:
    s = 0.0
    for ai, bi in zip(a, b):
        d = ai - bi
        s += d * d
    return math.sqrt(s)


def transition_entropy(transitions: Mapping[int, Mapping[int, float]]) -> float:
    """Shannon entropy of the cluster-transition Markov chain (bits)."""
    h = 0.0
    for src, dsts in transitions.items():
        total = sum(dsts.values())
        if total == 0:
            continue
        src_h = 0.0
        for count in dsts.values():
            p = count / total
            if p > 0:
                src_h -= p * math.log2(p)
        h += src_h / max(len(transitions), 1)
    return h


def surprise(predicted: Vector, observed: Vector) -> float:
    """Spatial prediction error (Euclidean distance)."""
    return euclidean_distance(predicted, observed)


def active_load(cluster_count: int, anomaly_vectors: Sequence[Vector]) -> float:
    """Structural load: live clusters + anomaly cloud spatial volume."""
    if not anomaly_vectors:
        return float(cluster_count)
    dim = len(anomaly_vectors[0]) if anomaly_vectors else 1
    var = [0.0] * dim
    n = len(anomaly_vectors)
    if n < 2:
        return float(cluster_count)
    means = [sum(v[i] for v in anomaly_vectors) / n for i in range(dim)]
    for v in anomaly_vectors:
        for i in range(dim):
            var[i] += (v[i] - means[i]) ** 2
    volume = math.sqrt(sum(v / (n - 1) for v in var))
    return cluster_count + volume


def cognitive_energy(
    entropy_val: float,
    surprise_val: float,
    load_val: float,
    lam: float = LAMBDA,
    mu: float = MU,
    nu: float = NU,
) -> float:
    """Free energy proxy: E = lam*H + mu*S + nu*A."""
    return lam * entropy_val + mu * surprise_val + nu * load_val


def prediction_rmse(predictions: Sequence[float], observations: Sequence[float]) -> float:
    """Root Mean Squared Error for predictions vs observations."""
    if not predictions or not observations:
        return 0.0
    n = min(len(predictions), len(observations))
    if n == 0:
        return 0.0
    mse = sum((predictions[i] - observations[i]) ** 2 for i in range(n)) / n
    return math.sqrt(mse)


def shannon_entropy(counts: Dict[int, int]) -> float:
    """Shannon entropy from a count dict (bits)."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def kl_divergence(p: Dict[int, float], q: Dict[int, float]) -> float:
    """KL divergence D_KL(P || Q)."""
    kl = 0.0
    for k, p_k in p.items():
        q_k = q.get(k, 1e-15)
        if p_k > 0:
            kl += p_k * math.log(p_k / q_k)
    return kl
