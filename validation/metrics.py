"""
validation/metrics.py
======================

The core Free-Energy / Cognitive-Health logic, migrated out of
``cognitive_health.py`` under the project's Proxy-Refactoring strategy.

This module is the *single source of truth* for the spatial cognitive
quantities grounded in Karl Friston's Free Energy Principle (FEP):

        E = (lambda * H) + (mu * S) + (nu * A)

    H -- Entropy:     conditional Shannon entropy H(next | current) of the
                      K-Means cluster-transition Markov chain (bits).
    S -- Surprise:    raw Euclidean distance between the predicted centroid and
                      the observed sensory vector.
    A -- Active Load: number of live clusters plus the spatial volume (total
                      variance) of the quarantined anomaly cloud.

Two layers live here:

1. The original pure functions and constants (``transition_entropy``,
   ``surprise``, ``active_load``, ``cognitive_energy`` ...). These are kept
   byte-for-byte faithful so ``cognitive_health.py`` -- now a thin proxy -- and
   ``cognitive_core.py`` continue to behave exactly as before.

2. Concrete :class:`~validation.interfaces.Metric` implementations that wrap
   those functions behind the Interface-First contract. Each takes a run's
   ``logs`` and returns a single scalar score, so the validation harness can
   treat every cognitive quantity uniformly.

``logs`` shape (mapping *or* object) consumed by the metric classes:
    - ``transitions``        : {src_cluster: {dst_cluster: count}}
    - ``predicted_centroid`` : Sequence[float]
    - ``observed_vector``    : Sequence[float]
    - ``cluster_count``      : int
    - ``anomaly_vectors``    : Sequence[Sequence[float]]

Pure Python standard library (``math`` only) plus the local ``Metric`` ABC.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Mapping, Sequence

from validation.interfaces import Metric

# Kept as ``Sequence[float]`` (not the tuple alias in ``interfaces``) to remain
# byte-for-byte compatible with the original ``cognitive_health.Vector`` that
# legacy callers import.
Vector = Sequence[float]


# ---------------------------------------------------------------------------
# Coupling coefficients (the "physics constants" of this cognitive universe)
# ---------------------------------------------------------------------------
LAMBDA = 1.0  # weight on transition uncertainty (Entropy H)
MU = 2.0  # weight on spatial prediction error (Surprise S)
NU = 0.5  # weight on structural load (Active clusters + anomaly volume)


# ---------------------------------------------------------------------------
# Regime thresholds (tuned for continuous / spatial scales)
# ---------------------------------------------------------------------------
ENTROPY_HIGH = 2.0  # bits of next-cluster uncertainty considered high
SURPRISE_HIGH = 0.50  # Euclidean prediction error considered high
SURPRISE_MILD = 0.20  # threshold for "actively learning" surprise
PRESSURE_HIGH = 1.00  # anomalies-per-cluster considered overwhelming
PRESSURE_MILD = 0.25  # anomalies-per-cluster considered "adapting"
ENERGY_EXHAUSTION = 18.0  # total free energy that signals fragmentation


class Regime(Enum):
    """The distinct cognitive states the engine can occupy."""

    OPTIMAL = "Optimal / Rested"
    LEARNING = "Learning / Adapting"
    EXHAUSTION = "Cognitive Exhaustion / Chaos"

    @property
    def glyph(self) -> str:
        return {
            Regime.OPTIMAL: "[ ~ ]",
            Regime.LEARNING: "[ ^ ]",
            Regime.EXHAUSTION: "[ ! ]",
        }[self]


# ---------------------------------------------------------------------------
# Vector helpers (mirrors vector_prediction_core; kept local so this module
# stays import-light and standard-library only)
# ---------------------------------------------------------------------------


def euclidean_distance(a: Vector, b: Vector) -> float:
    """Euclidean distance between two equal-dimension vectors.

    Defensive against ragged inputs: only the overlapping prefix is compared
    (``zip`` semantics), matching ``vector_prediction_core.euclidean_distance``.
    """
    s = 0.0
    for ai, bi in zip(a, b):
        d = ai - bi
        s += d * d
    return math.sqrt(s)


# ---------------------------------------------------------------------------
# H -- Entropy of the Markov transition chain across K-Means clusters
# ---------------------------------------------------------------------------


def transition_entropy(
    transitions: Mapping[int, Mapping[int, float]],
) -> float:
    """Shannon entropy of the cluster-transition Markov chain (bits).

    ``transitions`` is the first-order Markov chain emitted by
    ``VectorPredictor.transition_matrix()`` -- a mapping
    ``{source_cluster_id: {target_cluster_id: count}}``.

    For each *source* cluster we turn its outgoing counts into a probability
    distribution and take its Shannon entropy, then weight each source row by
    how often that source has actually been visited. The result is the chain's
    conditional entropy H(next | current) -- the engine's expected next-step
    unpredictability.
    """
    weighted_sum = 0.0
    total_weight = 0.0

    for _src, targets in transitions.items():
        counts = [c for c in targets.values() if c > 0]
        row_total = sum(counts)
        if row_total <= 0:
            continue

        row_h = 0.0
        for c in counts:
            p = c / row_total
            row_h -= p * math.log2(p)

        weighted_sum += row_h * row_total
        total_weight += row_total

    if total_weight <= 0:
        return 0.0
    return weighted_sum / total_weight


# ---------------------------------------------------------------------------
# S -- Surprise as raw Euclidean prediction error
# ---------------------------------------------------------------------------


def surprise(predicted_centroid: Vector, observed_vector: Vector) -> float:
    """Spatial surprise S = || predicted_centroid - observed_vector ||.

    How far reality landed from where the predictor's chosen centroid said it
    would land -- the raw Euclidean distance in sensory-vector space.
    """
    return euclidean_distance(predicted_centroid, observed_vector)


# ---------------------------------------------------------------------------
# A -- Active load: live clusters + spatial volume of the quarantine cloud
# ---------------------------------------------------------------------------


def anomaly_spatial_volume(anomaly_vectors: Sequence[Vector]) -> float:
    """Spatial volume of the quarantined anomaly cloud (total variance).

    Measured as the trace of the cloud's covariance matrix -- the sum of
    per-dimension variances. Grows when quarantined anomalies scatter widely
    (a fragmenting model) and stays near zero when they cluster tightly. A
    single anomaly (or none) has no spread, hence zero volume.
    """
    n = len(anomaly_vectors)
    if n < 2:
        return 0.0

    dim = min(len(v) for v in anomaly_vectors)
    volume = 0.0
    for d in range(dim):
        column = [v[d] for v in anomaly_vectors]
        mean_d = sum(column) / n
        variance_d = sum((x - mean_d) ** 2 for x in column) / n
        volume += variance_d
    return volume


def active_load(
    cluster_count: int,
    anomaly_vectors: Sequence[Vector],
) -> float:
    """Structural load A = (active K-Means clusters) + (anomaly cloud volume)."""
    return float(cluster_count) + anomaly_spatial_volume(anomaly_vectors)


def cognitive_energy(
    H: float,
    S: float,
    A: float,
    lam: float = LAMBDA,
    mu: float = MU,
    nu: float = NU,
) -> float:
    """The headline Free-Energy proxy:  E = lam*H + mu*S + nu*A."""
    return (lam * H) + (mu * S) + (nu * A)


# ---------------------------------------------------------------------------
# Interface-First Metric implementations
# ---------------------------------------------------------------------------
# Each wraps one of the pure functions above behind the Metric ABC so the
# validation harness can score any run uniformly via ``calculate(logs)``.


def _field(logs: Any, name: str, default: Any = None) -> Any:
    """Read ``name`` from ``logs`` whether it is a mapping or an object."""
    if isinstance(logs, Mapping):
        return logs.get(name, default)
    return getattr(logs, name, default)


class EntropyMetric(Metric):
    """H -- conditional entropy of the cluster-transition chain (bits).

    Directionality: lower is better (more predictable dynamics). Units: bits.
    """

    def calculate(self, logs: Any) -> float:
        transitions = _field(logs, "transitions", {}) or {}
        return transition_entropy(transitions)


class SurpriseMetric(Metric):
    """S -- spatial prediction error.

    Directionality: lower is better. Units: Euclidean distance in vector space.
    """

    def calculate(self, logs: Any) -> float:
        predicted = _field(logs, "predicted_centroid")
        observed = _field(logs, "observed_vector")
        if predicted is None or observed is None:
            return 0.0
        return surprise(predicted, observed)


class ActiveLoadMetric(Metric):
    """A -- structural load: live clusters + anomaly cloud volume.

    Directionality: lower is better. Units: clusters + variance.
    """

    def calculate(self, logs: Any) -> float:
        cluster_count = int(_field(logs, "cluster_count", 0) or 0)
        anomaly_vectors = _field(logs, "anomaly_vectors", []) or []
        return active_load(cluster_count, anomaly_vectors)


class CognitiveEnergyMetric(Metric):
    """E -- the headline Free-Energy proxy E = lam*H + mu*S + nu*A.

    Composes the three sub-metrics above. This is the primary quantity the
    "Freeze" rule's regression gate is expected to track.

    Directionality: lower is better. Units: weighted free-energy (a.u.).
    """

    def __init__(
        self,
        lam: float = LAMBDA,
        mu: float = MU,
        nu: float = NU,
    ) -> None:
        self.lam = lam
        self.mu = mu
        self.nu = nu
        self._entropy = EntropyMetric()
        self._surprise = SurpriseMetric()
        self._load = ActiveLoadMetric()

    def calculate(self, logs: Any) -> float:
        H = self._entropy.calculate(logs)
        S = self._surprise.calculate(logs)
        A = self._load.calculate(logs)
        return cognitive_energy(H, S, A, lam=self.lam, mu=self.mu, nu=self.nu)


__all__ = [
    # type alias
    "Vector",
    # constants
    "LAMBDA",
    "MU",
    "NU",
    "ENTROPY_HIGH",
    "SURPRISE_HIGH",
    "SURPRISE_MILD",
    "PRESSURE_HIGH",
    "PRESSURE_MILD",
    "ENERGY_EXHAUSTION",
    # enum
    "Regime",
    # pure functions
    "euclidean_distance",
    "transition_entropy",
    "surprise",
    "anomaly_spatial_volume",
    "active_load",
    "cognitive_energy",
    # Metric ABC implementations
    "EntropyMetric",
    "SurpriseMetric",
    "ActiveLoadMetric",
    "CognitiveEnergyMetric",
]
