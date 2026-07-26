# validation/shared_metrics_v1.py
"""
R3C Canonical Cognitive Metrics (version 1).

Single source of truth for the five cognitive quantities consumed by both the
Online predictor path (``backend.cognition.vector_prediction_core``) and the
Replay sandbox (``backend.cognition.replay_engine``):

    S = compute_S_surprise          (Markov forecast error)
    R = compute_R_representation    (nearest-centroid distance)
    H = compute_H_global            (Markov chain entropy, accumulated)
    H = compute_H_local             (window-induced transition entropy)
    A = compute_A_active_load       (cluster count + anomaly spatial volume)

Contract
--------
* Pure functions only -- no I/O, no mutation, no engine access.
* No coupling coefficients (lambda/mu/nu) live here -- those are policy-level.
* All functions are independently testable.
* A is reconciled to the linear live formula per R3C user direction.

This module is intentionally import-light: ``math``, ``numpy``, ``collections``
and the ``dataclasses`` stdlib only. No imports from ``validation.metrics``,
``backend.cognition.*`` or any other VELYNX module, so it can be used in
isolation (regression tests, audit scripts, future deployments).
"""

import math
import numpy as np
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

METRICS_VERSION = "v1"


@dataclass(frozen=True)
class MetricDefinition:
    """Frozen contract for the canonical cognitive metric set."""

    version: str = METRICS_VERSION
    description: str = (
        "Canonical separation of Markov Prediction Error (S) and "
        "Representation Error (R), plus the local/global entropy split "
        "and the reconciled active-load A."
    )


def compute_S_surprise(predicted_vector: List[float], observed_vector: List[float]) -> float:
    """
    Canonical S: Markov Prediction Error.
    Objective, unweighted Euclidean distance between the system's forecast and reality.
    """
    if not predicted_vector or not observed_vector:
        return 0.0
    return float(np.linalg.norm(np.array(predicted_vector) - np.array(observed_vector)))


def compute_R_representation_error(
    centroids: List[List[float]],
    observed_vector: List[float],
    dim_weights: Optional[List[float]] = None,
) -> float:
    """
    Canonical R: Representation/Novelty Error.
    Nearest-centroid distance. If attention is active, the distance IS precision-weighted.
    """
    if not centroids:
        return 0.0

    obs = np.array(observed_vector)
    if dim_weights:
        weights = np.array(dim_weights)
        distances = [np.sqrt(np.sum(weights * (np.array(c) - obs) ** 2)) for c in centroids]
    else:
        distances = [float(np.linalg.norm(np.array(c) - obs)) for c in centroids]

    return min(distances)


def _shannon_entropy(counts: Dict[int, int]) -> float:
    """Helper for entropy calculation."""
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def compute_H_global(transition_matrix: Dict[int, Dict[int, int]]) -> float:
    """
    Canonical H_global: Accumulated Markov chain entropy.
    Computes the expected entropy of the next state across the stationary distribution.
    """
    if not transition_matrix:
        return 0.0

    total_transitions = sum(sum(targets.values()) for targets in transition_matrix.values())
    if total_transitions == 0:
        return 0.0

    total_entropy = 0.0
    for src, targets in transition_matrix.items():
        src_total = sum(targets.values())
        if src_total > 0:
            state_probability = src_total / total_transitions
            state_entropy = _shannon_entropy(targets)
            total_entropy += state_probability * state_entropy

    return total_entropy


def compute_H_local(cluster_sequence: List[int]) -> float:
    """
    Canonical H_local: Window-induced transition entropy.
    Builds a temporary transition matrix from the recent sequence window.
    """
    if len(cluster_sequence) < 2:
        return 0.0

    window_transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(cluster_sequence) - 1):
        src = cluster_sequence[i]
        dst = cluster_sequence[i + 1]
        window_transitions[src][dst] += 1

    return compute_H_global(window_transitions)


def compute_A_active_load(cluster_count: int, anomaly_volume: float) -> float:
    """
    Canonical A: Active Cognitive Load.

    Formula (R3C-reconciled):
        A = cluster_count + anomaly_volume

    where ``anomaly_volume`` is the spatial volume of the quarantined anomaly
    cloud -- the trace of its covariance matrix (sum of per-dimension variances),
    as defined by :func:`validation.metrics.anomaly_spatial_volume`.

    This is byte-for-byte equivalent to
    :func:`validation.metrics.active_load` (the live A) when the caller passes
    the spatial volume already computed. The R3C canonical layer accepts the
    volume as a scalar to keep this function pure and dependency-free (it must
    not have to import the cluster engine to be reusable).

    Version history:
        v1 -- canonical definition was cluster_count + (anomaly_volume ** 1.5).
              Reconciled to the linear live formula during the R3C refactor after
              direct measurement confirmed both ``validation.metrics.active_load``
              and ``ReplayEngine._active_load`` use the linear form, and after
              user direction confirmed the live formula as the canonical target.
    """
    return float(cluster_count + anomaly_volume)
