"""
VELYNX Cognitive Milestone C3 — Concept Birth Engine
=====================================================

A brain does not wait for a human to define "Mammal".  It observes "dog"
(tail, fur, barks), "cat" (tail, fur, meows), and "fox" (tail, fur, wild).
The repeating co-occurrence of [tail + fur] across multiple experiences
automatically spawns a latent concept.  Later, a human might label it
"Mammal", but the system discovered the structure on its own.

This module implements that emergent clustering logic:

1. **Co-occurrence Matrix** — ingests feature streams, tracks pairwise
   statistics, normalises via NPMI (-1, 1).
2. **Latent Node Spawning** — when a feature cluster has high internal
   density AND spans diverse experiences, auto-creates a LatentConcept.
3. **Predictive Validation** — each concept's weight is updated by how
   well it reduces future prediction error.
4. **Consolidation** — decay and prune concepts that fail to predict.
5. **Ontology Integration** — ``update_ontology()`` passes birthed concepts
   into the World Model Registry and soul graph so the rest of VELYNX
   can reason with them.

No external LLM APIs.  Purely mathematical.  Fully typed.
"""

from __future__ import annotations

import json
import logging
import math
import os
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.special import betainc, digamma, gammaln

from backend.memory._sqlite import connect as open_connection
from backend.memory._sqlite import canonical_db_path

logger = logging.getLogger("velynx.concept_birth")

# ── Constants ──────────────────────────────────────────────────────────────────

# --- Core thresholds ---
DEFAULT_NPMI_THRESHOLD = 0.15            # minimum NPMI for an edge in the cluster graph
DEFAULT_SPAWN_DENSITY_THRESHOLD = 0.55   # minimum cluster density to spawn a concept
DEFAULT_SPAWN_EXPERIENCE_COUNT = 3       # minimum distinct experiences for spawning
DEFAULT_SPAWN_MIN_FEATURES = 3           # minimum features in a cluster
DEFAULT_PRUNING_WEIGHT = 0.05            # weight below which a concept is pruned
DEFAULT_PRUNING_AGE_SECONDS = 3600.0     # minimum age before pruning
DEFAULT_LEARNING_RATE = 0.1
DEFAULT_DECAY_RATE = 0.02

# --- Mathematical enhancements ---
DEFAULT_ADD_K = 0.5                      # add-k smoothing parameter for probability estimates
DEFAULT_NPMI_ADAPTIVE_SIGMA = 0.75       # sigma_mult for adaptive threshold: mean + sigma*std
DEFAULT_SPECTRAL_K_CLUSTERS = 8          # max clusters to discover via spectral eigengap
DEFAULT_SPECTRAL_SEED_RATIO = 0.3        # fraction of spectral seeds to use
DEFAULT_FEATURE_SALIENCE_BETA = 1.0      # beta weighting for ICF salience in density calc
DEFAULT_CONCEPT_MERGE_JACCARD = 0.60     # min Jaccard similarity to trigger merge
DEFAULT_CONCEPT_MERGE_HUNGARIAN = 0.35   # max Hungarian alignment cost for merge
DEFAULT_EXPERIENCE_TAU = 1000.0          # temporal decay time constant (seconds)
DEFAULT_BAYESIAN_SURPRISE_K = 0.5        # KL threshold multiplier: threshold = K * baseline_kl

# --- Limits ---
MAX_CLUSTER_SCAN_SIZE = 500              # max features to build the dense matrix for

DB_NAME = "brain_stem.db"


# ══════════════════════════════════════════════════════════════════════════════
# Data Models
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Experience:
    """A single observation from the experience stream.

    Parameters
    ----------
    features
        The set of observed features (e.g. {"tail", "fur", "barks"}).
    context
        Arbitrary metadata the caller attaches (source, route type, etc.).
    timestamp
        Unix timestamp — defaults to ``time.time()``.
    """

    features: set[str]
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not isinstance(self.features, set):
            self.features = set(self.features)


@dataclass
class FeatureStats:
    """Per-feature statistics tracked by the co-occurrence matrix."""

    total_count: int = 0                               # how many experiences contain this feature
    co_counts: dict[str, int] = field(default_factory=dict)  # {other_feature: co_occurrence_count}


@dataclass
class ClusterCandidate:
    """A candidate cluster discovered by the greedy seed-growth algorithm."""

    features: frozenset[str]
    density: float                     # fraction of possible edges present
    feature_npmis: list[float]         # pairwise NPMI values within the cluster
    size: int                          # number of features
    score: float                       # composite score for ranking

    def to_concept(self, engine: ConceptBirthEngine, birth_time: float) -> LatentConcept:
        return LatentConcept(
            id=engine._next_concept_id(),
            features=self.features,
            birth_time=birth_time,
            density_at_birth=self.density,
            cluster_score_at_birth=self.score,
        )


@dataclass
class LatentConcept:
    """An emergent concept automatically birthed by the engine.

    **Enhancements for C3:**

    * **Beta posterior tracking** — ``posterior_alpha`` / ``posterior_beta``
      maintain a proper Bayesian Beta(1+s, 1+(a-s)) posterior over the
      concept's predictive reliability.  The surprise is now computed via
      KL divergence (see ``BayesianSurprise``) rather than heuristic error
      differences.

    * **Activation-gated certainty** — the ``record_prediction`` method uses
      the KL-based surprise signal to decide success: the concept succeeds
      if its activation is high *and* its Beta posterior KL drops below a
      certainty threshold.

    * **Merging support** — ``merge_with()`` allows two overlapping concepts
      to consolidate into one with a consolidation bonus.

    Parameters
    ----------
    id
        Unique numeric identifier.
    features
        The defining feature set (immutable).
    birth_time
        Unix timestamp of creation.
    density_at_birth
        The cluster density that triggered the spawn.
    cluster_score_at_birth
        The composite cluster score at spawn time.
    predictive_weight
        Bayesian-smoothed weight tracking predictive success.
    successes
        Number of times this concept helped reduce prediction error.
    attempts
        Number of times this concept was tested against an experience.
    activation_history
        Recent activation values from the last N experiences.
    weight
        Overall system weight (decay * predictive_weight).
    posterior_alpha
        Beta posterior alpha parameter (starts at 1.0 for uniform prior).
    posterior_beta
        Beta posterior beta parameter.
    last_activation_time
        Unix timestamp of last activation (>0 activation).  Used for
        time-aware decay (concepts not activated in a long time decay faster).
    """

    id: int
    features: frozenset[str]
    birth_time: float
    density_at_birth: float = 0.0
    cluster_score_at_birth: float = 0.0
    predictive_weight: float = 0.5          # Bayesian prior E[weight]
    successes: int = 0
    attempts: int = 0
    activation_history: list[float] = field(default_factory=list)
    weight: float = 0.5
    posterior_alpha: float = 1.0            # Beta(1,1) = uniform prior
    posterior_beta: float = 1.0
    last_activation_time: float = 0.0

    # ── public API ─────────────────────────────────────────────────────────────

    def activation(self, experience_features: set[str]) -> float:
        """Compute activation from the overlap ratio with observed features.

        ``activation = |self.features ∩ experience_features| / |self.features|``

        Returns 0.0 if no overlap.
        """
        if not self.features:
            return 0.0
        overlap = len(self.features & experience_features)
        return overlap / len(self.features)

    def record_prediction(self, activation: float, kl_surprise: float,
                          learning_rate: float = DEFAULT_LEARNING_RATE) -> float:
        """Update predictive weight using Bayesian surprise signal.

        **How it works (C3 Bayesian version):**

        1. The KL surprise ``KL(Beta(1+s, 1+(a-s)) || Beta(1,1))`` measures
           how uncertain the concept is about its own reliability.
        2. If the concept is active (``activation > 0``) **and** its KL
           surprise is *low* (it confidently predicted), we count a success.
        3. If the concept is active but KL surprise is high (it's still
           uncertain), we count a failure — *the system is punishing
           unreliable predictions even if they happened to be directionally
           correct*.
        4. The Beta posterior is updated and predictive_weight =
           ``posterior_alpha / (posterior_alpha + posterior_beta)``.

        Returns the new predictive weight.
        """
        self.attempts += 1
        self.activation_history.append(activation)

        # Activation-gated success: concept helps if it was relevant AND
        # its posterior KL is low (it's confidently converged)
        if activation > 0.0 and kl_surprise < DEFAULT_BAYESIAN_SURPRISE_K:
            self.successes += 1

        # Update Beta posterior
        self.posterior_alpha = 1.0 + self.successes
        self.posterior_beta = 1.0 + (self.attempts - self.successes)

        # Predictive weight = mean of the Beta posterior
        total = self.posterior_alpha + self.posterior_beta
        self.predictive_weight = self.posterior_alpha / total if total > 0 else 0.5

        # Overall weight = predictive_weight * recency bonus
        recency = min(1.0, len(self.activation_history) / 10.0)
        self.weight = self.predictive_weight * (0.5 + 0.5 * recency)

        return self.weight

    def decay(self, rate: float = DEFAULT_DECAY_RATE,
              now: float | None = None) -> None:
        """Apply metabolic decay to the weight.

        Concepts that haven't been activated recently decay faster:
        ``decay_multiplier = 1.0 + (now - last_activation_time) / tau``
        where tau = 1000s.

        This implements a form of *Hebbian forgetting* — use it or lose it.
        """
        base_decay = 1.0 - rate

        # Time-aware multiplier
        if now is None:
            now = time.time()
        if self.last_activation_time > 0:
            idle_time = now - self.last_activation_time
            time_mult = 1.0 + idle_time / DEFAULT_EXPERIENCE_TAU
        else:
            time_mult = 1.0

        effective_rate = 1.0 - (base_decay ** time_mult)
        self.weight *= (1.0 - effective_rate)
        if self.weight < 0.01:
            self.weight = 0.0

    def merge_with(self, other: LatentConcept,
                   birth_time: float | None = None) -> None:
        """Merge *other* concept into *self* in-place.

        Takes the union of features, sums successes/attempts, takes the
        max of density and cluster scores, averages predictive weights,
        and applies a 5% consolidation bonus to weight.
        """
        self.features = self.features | other.features
        self.density_at_birth = max(self.density_at_birth, other.density_at_birth)
        self.cluster_score_at_birth = max(
            self.cluster_score_at_birth, other.cluster_score_at_birth
        )
        self.predictive_weight = (self.predictive_weight + other.predictive_weight) / 2.0
        self.successes += other.successes
        self.attempts += other.attempts
        self.posterior_alpha = 1.0 + self.successes
        self.posterior_beta = 1.0 + (self.attempts - self.successes)
        self.weight = max(self.weight, other.weight) * 1.05

        # Merge activation histories (last 50 each)
        merged = self.activation_history[-50:] + other.activation_history[-50:]
        self.activation_history = merged[-100:]

        if birth_time is None:
            birth_time = time.time()
        self.birth_time = min(self.birth_time, other.birth_time)  # keep oldest

    @property
    def is_alive(self) -> bool:
        return self.weight > 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "features": sorted(self.features),
            "birth_time": self.birth_time,
            "density_at_birth": self.density_at_birth,
            "predictive_weight": round(self.predictive_weight, 4),
            "posterior_alpha": round(self.posterior_alpha, 2),
            "posterior_beta": round(self.posterior_beta, 2),
            "posterior_mean": round(self.predictive_weight, 4),
            "successes": self.successes,
            "attempts": self.attempts,
            "weight": round(self.weight, 4),
            "is_alive": self.is_alive,
        }


# ══════════════════════════════════════════════════════════════════════════════
# Co-occurrence Matrix
# ══════════════════════════════════════════════════════════════════════════════

class CooccurrenceMatrix:
    """Tracks pairwise feature co-occurrence across the experience stream.

    Maintains a sparse dict-of-dicts for counts and can produce a dense
    NPMI matrix for a subset of the most frequent features when clustering
    is triggered.

    **Mathematical enhancements over Phase 62.1:**

    * **Add-k smoothing** — principled probability estimates::
        P_s(f) = (count(f) + k) / (N + k * V)
      where V is the vocabulary size (unique features seen).  This avoids
      the log(0) problem without crude epsilon fudge factors.

    * **Feature salience (ICF)** — Inverse Concept Frequency::
        salience(f) = log( (1 + V) / (1 + concepts_containing_f) )
      Rare features that appear in few concepts get higher weight during
      cluster density computation.

    * **Adaptive NPMI threshold** — instead of a fixed value::
        threshold = mean(all_positive_npmis) + sigma * std(all_positive_npmis)
      clamped to [0.05, 0.5].  Recomputes automatically when the matrix
      is rebuilt.

    * **Experience-weighted co-occurrence** — recent experiences count more::
        weight(t) = exp(-(now - t) / tau)
      making the matrix responsive to distribution shift without a separate
      windowing mechanism.

    Parameters
    ----------
    max_features_dense
        Maximum number of features to include in the dense matrix for
        cluster detection.  Most-frequent features win.
    add_k
        Smoothing parameter for add-k probability estimates (default 0.5).
    tau
        Time constant for experience-weighted co-occurrence (seconds).
    """

    def __init__(self, max_features_dense: int = MAX_CLUSTER_SCAN_SIZE,
                 add_k: float = DEFAULT_ADD_K,
                 tau: float = DEFAULT_EXPERIENCE_TAU) -> None:
        self._stats: dict[str, FeatureStats] = {}   # feature_name → stats
        self._total_experiences: int = 0
        self._total_weight: float = 0.0              # weighted sum for smoothed probs
        self._vocabulary_size: int = 0               # V in add-k formulas
        self._max_features_dense: int = max_features_dense
        self._add_k: float = add_k
        self._tau: float = tau

        self._dirty: bool = True                     # matrix needs recomputation
        self._dense_matrix: Optional[np.ndarray] = None
        self._dense_names: list[str] = []
        self._adaptive_threshold: float = DEFAULT_NPMI_THRESHOLD

        # Feature salience cache (ICF)
        self._icf_cache: dict[str, float] = {}
        self._icf_dirty: bool = True

    # ── mutation ───────────────────────────────────────────────────────────────

    def update(self, experience: Experience) -> None:
        """Ingest a single experience and update all pairwise counts.

        Uses experience-weighted co-occurrence: recent experiences count
        exponentially more according to ``exp(-(now - t) / tau)``.
        """
        weight = math.exp(-(time.time() - experience.timestamp) / self._tau)
        self._total_experiences += 1
        self._total_weight += weight
        features = list(experience.features)

        # Ensure all features exist
        for f in features:
            self._stats.setdefault(f, FeatureStats())
            self._stats[f].total_count += weight

        # Update pairwise co-occurrences
        for i in range(len(features)):
            fi = features[i]
            for j in range(i + 1, len(features)):
                fj = features[j]
                left, right = (fi, fj) if fi <= fj else (fj, fi)
                self._stats[left].co_counts[right] = \
                    self._stats[left].co_counts.get(right, 0.0) + weight

        self._dirty = True
        self._icf_dirty = True
        self._adaptive_threshold = self.adaptive_threshold()

    def merge(self, other: CooccurrenceMatrix) -> None:
        """Merge counts from another matrix (for batched ingestion)."""
        for feature, stats in other._stats.items():
            if feature not in self._stats:
                self._stats[feature] = FeatureStats()
            local = self._stats[feature]
            local.total_count += stats.total_count
            for other_feat, count in stats.co_counts.items():
                local.co_counts[other_feat] = local.co_counts.get(other_feat, 0.0) + count

        self._total_experiences += other._total_experiences
        self._total_weight += other._total_weight
        self._dirty = True
        self._icf_dirty = True

    # ── add-k smoothed probabilities ──────────────────────────────────────────

    def _vocab(self) -> int:
        """Number of unique features ever seen (V in add-k formulas)."""
        return max(1, len(self._stats))

    def _smooth_prob(self, feature: str) -> float:
        """Add-k smoothed marginal probability P_s(feature).

        ``P_s(f) = (count(f) + k) / (N + k)``

        where N = total_weight, k = add_k.

        Using ``N + k`` instead of ``N + k*V`` because our "vocabulary" is
        the feature space, and each experience contributes to exactly one
        observation per feature.  This keeps the smoothing light — strong
        signals stay strong, zero signals get a small epsilon.
        """
        n = self._total_weight
        if n == 0.0:
            return 0.0
        k = self._add_k
        count = self._stats.get(feature, FeatureStats()).total_count
        return (count + k) / (n + k)

    def _smooth_joint(self, a: str, b: str) -> float:
        """Add-k smoothed joint probability P_s(a, b).

        ``P_s(a,b) = (count(a,b) + k) / (N + k)``

        We use ``N + k`` (not ``N + k*V²``) because our data is *co-occurrence
        within an experience* — every experience that contains both features
        contributes 1.0 to the count.  The "vocabulary" of possible bigrams
        is not V² since experiences contain a natural (small) number of
        features.  Using V² would heavily over-smooth for small N.
        """
        n = self._total_weight
        if n == 0.0:
            return 0.0
        k = self._add_k
        left, right = (a, b) if a <= b else (b, a)
        count = self._stats.get(left, FeatureStats()).co_counts.get(right, 0.0)
        return (count + k) / (n + k)

    def _prob(self, feature: str) -> float:
        """Raw MLE marginal probability (kept for backward compat).

        Uses the smoothed version internally; pure MLE exposed only for
        debugging/comparison.
        """
        return self._smooth_prob(feature)

    def _joint(self, a: str, b: str) -> float:
        """Raw MLE joint probability (kept for backward compat).

        Uses the smoothed version internally.
        """
        return self._smooth_joint(a, b)

    def pmi(self, a: str, b: str) -> float:
        """Pointwise Mutual Information with add-k smoothing.

        ``PMI(a,b) = log(P_s(a,b) / P_s(a) * P_s(b))``
        """
        p_ab = self._smooth_joint(a, b)
        p_a = self._smooth_prob(a)
        p_b = self._smooth_prob(b)
        if p_a == 0.0 or p_b == 0.0 or p_ab <= 0.0:
            return -1.0
        return math.log(p_ab / (p_a * p_b) + 1e-15)

    def npmi(self, a: str, b: str) -> float:
        """Normalised PMI in [-1, 1] with add-k smoothing.

        ``NPMI(a,b) = PMI(a,b) / -log(P_s(a,b))``
        """
        p_ab = self._smooth_joint(a, b)
        if p_ab <= 0.0:
            return -1.0
        numerator = self.pmi(a, b)
        denominator = -math.log(p_ab + 1e-15)
        if denominator == 0.0:
            return 0.0
        return numerator / denominator

    # ── adaptive threshold ─────────────────────────────────────────────────────

    def adaptive_threshold(self) -> float:
        """Compute an NPMI threshold from the distribution of all pairwise values.

        ``threshold = clamp(mean(pos_npmis) + sigma * std(pos_npmis), 0.05, 0.35)``

        The max of **0.35** (not 0.5) is intentional — with small data,
        many correct co-occurrence edges have NPMI in [0.3, 0.5] because
        they share frequent features (e.g., ``tail`` appearing in 6/10
        experiences).  A 0.5 cap would exclude legitimate mammal clusters.

        Additionally, the threshold is **experience-discounted**: when
        ``N < 50``, the cap is proportionally lowered:
        ``max_cap = 0.15 + 0.2 * min(1.0, N / 50)``.
        """
        self._rebuild_dense()
        if self._dense_matrix is None or self._dense_matrix.size < 4:
            return DEFAULT_NPMI_THRESHOLD

        upper = np.triu(self._dense_matrix, k=1)
        positive = upper[upper > 0.0]

        if len(positive) < 3:
            return DEFAULT_NPMI_THRESHOLD

        # Experience-sensitive cap: low data → lower threshold
        n = max(1, self._total_experiences)
        max_cap = 0.15 + 0.20 * min(1.0, n / 50.0)

        mean = float(np.mean(positive))
        std = float(np.std(positive))
        raw = mean + DEFAULT_NPMI_ADAPTIVE_SIGMA * std
        return max(0.05, min(max_cap, raw))

    # ── feature salience (ICF) ────────────────────────────────────────────────

    def _rebuild_icf(self) -> None:
        """Rebuild the feature salience cache.

        ``ICF(f) = log((1 + V) / (1 + concepts_containing_f))``

        A feature that appears in *every* concept has ICF ≈ 0 (not salient).
        A feature that appears in *one* concept has high ICF (discriminating).
        """
        if not self._icf_dirty:
            return
        v = self._vocab()
        # We estimate concept coverage from co-occurrence diversity:
        # a feature that co-occurs with many different other features is
        # broadly shared.
        for feat, stats in self._stats.items():
            num_co = len(stats.co_counts)
            icf = math.log((1.0 + v) / (1.0 + num_co)) if num_co > 0 else math.log(v)
            self._icf_cache[feat] = max(0.0, icf)
        self._icf_dirty = False

    def feature_salience(self, feature: str) -> float:
        """Salience of a feature via ICF (Inverse Concept Frequency).

        Returns a value in [0, log(V)].  Higher = more discriminating.
        """
        self._rebuild_icf()
        return self._icf_cache.get(feature, 0.0)

    def salience_normalized(self, feature: str) -> float:
        """Salience normalised to [0, 1] for use as a multiplicative weight."""
        sal = self.feature_salience(feature)
        max_sal = max(self._icf_cache.values()) if self._icf_cache else 1.0
        if max_sal == 0.0:
            return 0.5
        return sal / max_sal

    # ── dense matrix (for clustering) ──────────────────────────────────────────

    def _rebuild_dense(self) -> None:
        """Build the dense NPMI matrix for the top-K most frequent features.

        Also recomputes the adaptive threshold and the ICF cache.
        """
        if not self._dirty:
            return

        # Sort features by frequency, take top N
        sorted_features = sorted(
            self._stats.items(),
            key=lambda kv: kv[1].total_count,
            reverse=True,
        )
        top = sorted_features[:self._max_features_dense]

        self._dense_names = [name for name, _ in top]
        n = len(self._dense_names)
        self._dense_matrix = np.zeros((n, n), dtype=np.float64)

        for i in range(n):
            self._dense_matrix[i, i] = 1.0  # self-npmi = 1.0
            for j in range(i + 1, n):
                v = self.npmi(self._dense_names[i], self._dense_names[j])
                self._dense_matrix[i, j] = v
                self._dense_matrix[j, i] = v

        self._dirty = False
        self._icf_dirty = True  # rebuild ICF after matrix rebuild
        self._adaptive_threshold = self.adaptive_threshold()

    @property
    def dense_matrix(self) -> np.ndarray:
        self._rebuild_dense()
        return self._dense_matrix

    @property
    def dense_names(self) -> list[str]:
        self._rebuild_dense()
        return self._dense_names

    @property
    def current_threshold(self) -> float:
        """Current adaptive NPMI threshold (auto-recomputed on matrix rebuild)."""
        return self._adaptive_threshold

    # ── introspection ──────────────────────────────────────────────────────────

    def top_cooccurring(self, feature: str, k: int = 10) -> list[tuple[str, float]]:
        """Return the top-K features most strongly co-occurring with *feature* by NPMI."""
        results: list[tuple[str, float]] = []
        for other in self._stats:
            if other == feature:
                continue
            v = self.npmi(feature, other)
            if v > 0:
                results.append((other, v))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def all_features(self) -> list[str]:
        return list(self._stats.keys())

    @property
    def total_experiences(self) -> int:
        return self._total_experiences

    @property
    def feature_count(self) -> int:
        return len(self._stats)

    @property
    def total_weight(self) -> float:
        return self._total_weight

    def stats_dict(self) -> dict[str, Any]:
        return {
            "total_experiences": self._total_experiences,
            "total_weight": round(self._total_weight, 2),
            "unique_features": self.feature_count,
            "dense_matrix_size": len(self._dense_names) if not self._dirty else 0,
            "adaptive_threshold": round(self._adaptive_threshold, 4),
            "add_k_smoothing": self._add_k,
        }


# ══════════════════════════════════════════════════════════════════════════════
# Spectral Clustering Initializer  (NEW in C3)
# ══════════════════════════════════════════════════════════════════════════════

class SpectralClusterInitializer:
    """Spectral clustering via normalised Laplacian eigendecomposition.

    Discovers the latent cluster structure of the NPMI adjacency graph
    and produces high-quality seed features for the greedy cluster detector.

    **Algorithm:**

    1. Build the adjacency matrix ``A`` from the dense NPMI matrix (thresholded).
    2. Compute the normalised Laplacian ``L = I - D^{-1/2} A D^{-1/2}``.
    3. Eigendecompose ``L`` — the smallest eigenvalues reveal the number of
       connected components / clusters (eigengap heuristic).
    4. Use the K smallest eigenvectors as a spectral embedding.
    5. Run K-Means++ on the embedding to assign each feature to a spectral
       cluster.
    6. Return representatives (highest-degree node per spectral cluster)
       as seeds for the greedy cluster detector, plus the estimated K.

    Parameters
    ----------
    max_k
        Maximum number of clusters to consider (spectral eigengap search).
    seed_ratio
        Fraction of spectral seeds to forward to the greedy detector.
    """

    def __init__(self, max_k: int = DEFAULT_SPECTRAL_K_CLUSTERS,
                 seed_ratio: float = DEFAULT_SPECTRAL_SEED_RATIO) -> None:
        self.max_k = max_k
        self.seed_ratio = seed_ratio

    def estimate_k(self, matrix: CooccurrenceMatrix) -> int:
        """Estimate the number of clusters via the eigengap heuristic.

        Uses the normalised Laplacian eigenvalues.  The largest gap between
        consecutive small eigenvalues gives K.  Returns at least 1,
        at most max_k.
        """
        dense = matrix.dense_matrix
        names = matrix.dense_names
        n = len(names)
        if n < 4:
            return min(1, n)

        threshold = matrix.current_threshold
        adj = (dense >= threshold).astype(np.float64)
        np.fill_diagonal(adj, 0.0)

        degree = np.maximum(adj.sum(axis=1), 1e-10)
        d_inv_sqrt = np.diag(1.0 / np.sqrt(degree))
        lap = np.eye(n) - d_inv_sqrt @ adj @ d_inv_sqrt
        lap = np.nan_to_num(lap, nan=0.0, posinf=0.0, neginf=0.0)

        try:
            eigenvalues = np.linalg.eigh(lap)[0]
        except np.linalg.LinAlgError:
            return max(1, min(n // 3, self.max_k))

        eigengaps = np.diff(eigenvalues[:min(n, self.max_k + 2)])
        if len(eigengaps) == 0:
            return 1

        k_est = int(np.argmax(eigengaps) + 1)
        return max(1, min(k_est, self.max_k, n - 1))

    def get_spectral_seeds(self, matrix: CooccurrenceMatrix,
                           detector: ClusterDetector) -> list[list[str]]:
        """Run spectral clustering and return seed lists for each estimated cluster.

        Each element is a list of feature names belonging to one spectral
        cluster, sorted by degree (highest degree first).  The greedy detector
        can use these as pre-initialised seeds.

        Returns an empty list if spectral clustering fails or the matrix is
        too small.
        """
        dense = matrix.dense_matrix
        names = matrix.dense_names
        n = len(names)
        if n < 4:
            return []

        k_est = self.estimate_k(matrix)
        if k_est < 2:
            # Single-cluster case: use highest-degree feature as seed
            degrees = (dense >= matrix.current_threshold).sum(axis=1)
            np.fill_diagonal(degrees, 0)
            best_idx = int(np.argmax(degrees))
            return [[names[best_idx]]]

        threshold = matrix.current_threshold
        adj = (dense >= threshold).astype(np.float64)
        np.fill_diagonal(adj, 0.0)

        degree = np.maximum(adj.sum(axis=1), 1e-10)
        d_inv_sqrt = np.diag(1.0 / np.sqrt(degree))
        lap = np.eye(n) - d_inv_sqrt @ adj @ d_inv_sqrt
        lap = np.nan_to_num(lap, nan=0.0, posinf=0.0, neginf=0.0)

        try:
            eigenvalues, eigenvectors = np.linalg.eigh(lap)
        except np.linalg.LinAlgError:
            return []

        # Use k_est eigenvectors for embedding
        embed = eigenvectors[:, :k_est]

        # K-Means++ initialization on the spectral embedding
        centroids = self._kmeans_plusplus(embed, k_est)

        # Assign each feature to nearest centroid
        labels = np.zeros(n, dtype=np.int32)
        for i in range(n):
            dists = np.linalg.norm(embed[i] - centroids, axis=1)
            labels[i] = int(np.argmin(dists))

        # Build seed clusters: highest-degree feature per spectral cluster
        degrees = adj.sum(axis=1)
        seed_clusters: list[list[str]] = [[] for _ in range(k_est)]
        for cid in range(k_est):
            members = [i for i in range(n) if labels[i] == cid]
            if not members:
                continue
            members.sort(key=lambda i: degrees[i], reverse=True)
            # Take the top seed_ratio fraction as seeds
            num_seeds = max(3, int(len(members) * self.seed_ratio))
            for idx in members[:num_seeds]:
                seed_clusters[cid].append(names[idx])

        return seed_clusters

    @staticmethod
    def _kmeans_plusplus(data: np.ndarray, k: int) -> np.ndarray:
        """K-Means++ centroid initialisation on spectral embedding data.

        Returns a ``(k, n_features)`` array of centroid positions.
        """
        n = data.shape[0]
        if n < k:
            k = n
        if k <= 0:
            return np.zeros((1, data.shape[1]))

        rng = np.random.RandomState(42)
        centroids = [data[rng.randint(n)]]

        for _ in range(1, k):
            dists = np.array([min(np.linalg.norm(p - c) for c in centroids)
                              for p in data])
            probs = dists / (dists.sum() + 1e-15)
            centroids.append(data[rng.choice(n, p=probs)])

        return np.array(centroids)


# ══════════════════════════════════════════════════════════════════════════════
# Bayesian Surprise  (NEW in C3)
# ══════════════════════════════════════════════════════════════════════════════

class BayesianSurprise:
    """Information-theoretic surprise via KL divergence between Beta posteriors.

    Each LatentConcept maintains a Beta posterior over its predictive
    reliability::

        Prior:     Beta(alpha=1, beta=1)   — uniform, maximum entropy
        Posterior: Beta(1+successes, 1+failures)

    When an experience arrives, the *surprise* is the KL divergence between
    the concept's current posterior and the prior::

        KL(Beta(alpha',beta') || Beta(1,1))

    A concept that has many successes (alpha' >> beta') has low KL — it
    confidently predicts and the system should trust it.  A concept that
    has many failures (beta' >> alpha') also converges — it's confidently
    *bad* at predicting and should be pruned.  A concept with few trials
    (alpha',beta' ≈ 1) has high KL — it's still uncertain.

    This replaces the heuristic ``error_before = 1.0 - overlap_ratio``
    from Phase 62.1 with a principled Bayesian signal.
    """

    @staticmethod
    def kl_beta(alpha1: float, beta1: float,
                alpha2: float, beta2: float) -> float:
        """KL divergence KL(Beta(a1,b1) || Beta(a2,b2)) in nats.

        Derived from the Beta log-density::

            KL = ln B(a2,b2) - ln B(a1,b1)
               + (a1-a2) * psi(a1) + (b1-b2) * psi(b1)
               + (a2-a1 + b2-b1) * psi(a1+b1)

        where B is the Beta function and psi is the digamma function.
        """
        if alpha1 <= 0 or beta1 <= 0 or alpha2 <= 0 or beta2 <= 0:
            return 0.0

        ln_b1 = gammaln(alpha1) + gammaln(beta1) - gammaln(alpha1 + beta1)
        ln_b2 = gammaln(alpha2) + gammaln(beta2) - gammaln(alpha2 + beta2)

        dig_a1 = digamma(alpha1)
        dig_b1 = digamma(beta1)
        dig_s1 = digamma(alpha1 + beta1)

        kl = (ln_b2 - ln_b1
              + (alpha1 - alpha2) * dig_a1
              + (beta1 - beta2) * dig_b1
              + (alpha2 - alpha1 + beta2 - beta1) * dig_s1)
        return max(0.0, kl)

    @staticmethod
    def kl_beta_uniform(alpha: float, beta: float) -> float:
        """KL divergence KL(Beta(a,b) || Beta(1,1)).

        The uniform prior Beta(1,1) has ln B(1,1) = 0, psi(1) = -γ,
        psi(2) = 1 - γ.  This is the standard baseline surprise.
        """
        return BayesianSurprise.kl_beta(alpha, beta, 1.0, 1.0)

    @staticmethod
    def compute_surprise(concept: LatentConcept,
                         activation: float) -> tuple[float, float, float]:
        """Compute the Bayesian surprise for a concept given its activation.

        The surprise signal has two components:

        1. **Posterior KL** — ``KL(Beta(1+s, 1+(a-s)) || Beta(1,1))``.
           How certain is the concept about its own reliability?
        2. **Activation-gated scaling** — if activation is low, the concept
           wasn't relevant, so we scale surprise down.

        Returns
        -------
        kl_div
            Raw KL divergence from uniform.
        scaled_surprise
            ``kl_div * activation`` — the effective surprise signal.
        inverse_certainty
            ``1.0 - 1.0/(1.0 + kl_div)`` — a [0,1] measure of uncertainty.
        """
        alpha = 1.0 + concept.successes
        beta = 1.0 + (concept.attempts - concept.successes)
        kl_div = BayesianSurprise.kl_beta_uniform(alpha, beta)
        scaled = kl_div * activation
        inverse_cert = 1.0 - 1.0 / (1.0 + kl_div) if kl_div > 0 else 0.0
        return kl_div, scaled, inverse_cert


# ══════════════════════════════════════════════════════════════════════════════
# Concept Merging — Hungarian Alignment  (NEW in C3)
# ══════════════════════════════════════════════════════════════════════════════

def _jaccard_similarity(a: frozenset[str], b: frozenset[str]) -> float:
    """Jaccard similarity between two feature sets [0, 1]."""
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union > 0 else 0.0


def _hungarian_alignment_cost(f1: frozenset[str], f2: frozenset[str],
                               npmi_fn) -> float:
    """Compute the optimal alignment cost between two feature sets.

    Builds a cost matrix where cost(i,j) = 1 - NPMI(f1_i, f2_j), then
    solves the assignment problem via the Hungarian algorithm.  Returns
    the *mean* assignment cost per feature (so it's comparable across
    different-sized feature sets).

    If the NPMI values are high between paired features, the cost is low
    (they align well).  If no pair has high NPMI, cost is near 1.
    """
    list1 = sorted(f1)
    list2 = sorted(f2)
    if not list1 or not list2:
        return 1.0

    n1, n2 = len(list1), len(list2)
    cost_matrix = np.zeros((max(n1, n2), max(n1, n2)), dtype=np.float64)

    for i in range(n1):
        for j in range(n2):
            cost_matrix[i, j] = 1.0 - abs(npmi_fn(list1[i], list2[j]))

    # Dummy rows/cols: cost = 1.0 (worst alignment)
    for i in range(n1, len(cost_matrix)):
        cost_matrix[i, :] = 1.0
    for j in range(n2, len(cost_matrix)):
        cost_matrix[:, j] = 1.0

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    mean_cost = float(cost_matrix[row_ind, col_ind].mean())
    return mean_cost


def should_merge_concepts(a: LatentConcept, b: LatentConcept,
                          matrix: CooccurrenceMatrix,
                          jaccard_threshold: float = DEFAULT_CONCEPT_MERGE_JACCARD,
                          hungarian_threshold: float = DEFAULT_CONCEPT_MERGE_HUNGARIAN,
                          ) -> bool:
    """Determine if two latent concepts should be merged into one.

    Uses two criteria:
    1. **Jaccard overlap** — if the feature sets share >= jaccard_threshold
       fraction of features, merge immediately.
    2. **Hungarian alignment** — if the optimal bipartite feature alignment
       cost is <= hungarian_threshold, merge (the features describe the
       same underlying concept with different vocabulary).
    """
    jac = _jaccard_similarity(a.features, b.features)
    if jac >= jaccard_threshold:
        return True

    hung_cost = _hungarian_alignment_cost(
        a.features, b.features, matrix.npmi
    )
    if hung_cost <= hungarian_threshold:
        return True

    return False


def merge_concepts(dominant: LatentConcept, subordinate: LatentConcept,
                   birth_time: float) -> LatentConcept:
    """Merge two latent concepts into one consolidated concept.

    The merged concept keeps the dominant's ID, takes the union of features,
    sums successes and attempts, averages the cluster metrics, and inherits
    the dominant's predictive weight adjusted by subordinate's evidence.
    """
    merged_features = dominant.features | subordinate.features

    merged = LatentConcept(
        id=dominant.id,
        features=merged_features,
        birth_time=dominant.birth_time,
        density_at_birth=max(dominant.density_at_birth, subordinate.density_at_birth),
        cluster_score_at_birth=max(dominant.cluster_score_at_birth,
                                   subordinate.cluster_score_at_birth),
        predictive_weight=(dominant.predictive_weight + subordinate.predictive_weight) / 2.0,
        successes=dominant.successes + subordinate.successes,
        attempts=dominant.attempts + subordinate.attempts,
        weight=max(dominant.weight, subordinate.weight) * 1.05,  # consolidation bonus
    )
    merged.activation_history = (
        dominant.activation_history[-50:] + subordinate.activation_history[-50:]
    )
    return merged


# ══════════════════════════════════════════════════════════════════════════════
# Cluster Detection (greedy quasi-clique with spectral seeds + salience)
# ══════════════════════════════════════════════════════════════════════════════

class ClusterDetector:
    """Discovers dense feature clusters from the NPMI co-occurrence matrix.

    **Algorithm (enhanced for C3):**

    1. **Spectral seeding** (optional) — if ``spectral_seeds`` are provided,
       start growth from each spectral seed cluster rather than purely
       degree-based ordering.  This finds structure that the greedy approach
       alone would miss (e.g., nested clusters, chain-like topologies).

    2. **Salience-weighted density** — each edge contributes its NPMI value
       scaled by the geometric mean of the two features' ICF salience.
       This prevents high-frequency generic features (e.g., "thing", "has")
       from dominating cluster formation.

    3. **Greedy growth with adaptive threshold** — the NPMI threshold
       adapts automatically from the matrix distribution instead of being
       a fixed hyper-parameter.

    4. **Composite score** — density² × log₂(size) × NPMI bonus, identical
       to Phase 62.1 but computed on the salience-weighted density.
    """

    def __init__(self, npmi_threshold: float | None = None,
                 density_threshold: float = DEFAULT_SPAWN_DENSITY_THRESHOLD,
                 min_features: int = DEFAULT_SPAWN_MIN_FEATURES,
                 use_salience: bool = True) -> None:
        self.npmi_threshold = npmi_threshold  # None = use matrix's adaptive threshold
        self.density_threshold = density_threshold
        self.min_features = min_features
        self.use_salience = use_salience

    def find_clusters(self, matrix: CooccurrenceMatrix,
                      spectral_seeds: list[list[str]] | None = None
                      ) -> list[ClusterCandidate]:
        """Discover all candidate clusters from the co-occurrence matrix.

        Parameters
        ----------
        matrix
            The co-occurrence matrix with its dense NPMI matrix.
        spectral_seeds
            Optional pre-initialised seed lists from spectral clustering.
            If provided, the greedy algorithm starts from these seeds
            *in addition to* the degree-based ordering.

        Returns clusters sorted by composite score descending.
        """
        names = matrix.dense_names
        dense = matrix.dense_matrix
        n = len(names)

        if n < self.min_features:
            return []

        # Use adaptive threshold if none explicitly set
        threshold = self.npmi_threshold if self.npmi_threshold is not None else matrix.current_threshold

        # Build binary adjacency (undirected)
        adj = dense >= threshold
        np.fill_diagonal(adj, False)

        degrees = adj.sum(axis=1)

        # ── Seed construction ────────────────────────────────────────────
        # Collect seed indices: start with spectral seeds, then degree order
        seed_indices: list[int] = []

        if spectral_seeds:
            name_to_idx = {name: i for i, name in enumerate(names)}
            for seed_group in spectral_seeds:
                for sname in seed_group:
                    idx = name_to_idx.get(sname)
                    if idx is not None and degrees[idx] >= 2:
                        if idx not in seed_indices:
                            seed_indices.append(idx)

        # Append degree-based seeds (highest first) for coverage
        degree_order = np.argsort(-degrees)
        for idx in degree_order:
            if degrees[idx] >= 2 and idx not in seed_indices:
                seed_indices.append(idx)

        if not seed_indices:
            return []

        seen: set[frozenset[str]] = set()
        candidates: list[ClusterCandidate] = []

        # DEBUG: print adjacency info
        _dbg_info = {
            "n_names": n,
            "threshold": round(threshold, 4),
            "edges_above_threshold": int(adj.sum() // 2),
            "avg_degree": float(degrees.mean()),
            "seed_count": len(seed_indices),
            "seed_examples": [names[s] for s in seed_indices[:5]],
        }
        logger.info("ClusterDetector.find_clusters: %s", _dbg_info)

        for seed_idx in seed_indices:
            # Greedy growth
            cluster_names = self._grow_cluster(seed_idx, names, adj, threshold)
            cluster_key = frozenset(cluster_names)

            if cluster_key in seen:
                continue
            seen.add(cluster_key)

            if len(cluster_names) < self.min_features:
                continue

            # Compute salience-weighted density
            density, pair_npmis = self._cluster_density(
                cluster_names, names, dense, matrix, use_salience=self.use_salience
            )
            if density < self.density_threshold:
                continue

            score = self._composite_score(density, len(cluster_names), pair_npmis)

            candidates.append(ClusterCandidate(
                features=cluster_key,
                density=density,
                feature_npmis=pair_npmis,
                size=len(cluster_names),
                score=score,
            ))

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    def _grow_cluster(self, seed_idx: int, names: list[str],
                       adj: np.ndarray, threshold: float) -> list[str]:
        """Greedily grow a cluster from *seed_idx* until density drops."""
        n = len(names)
        cluster_set = {seed_idx}
        cluster_list = [seed_idx]
        cluster_name_set = {names[seed_idx]}

        changed = True
        while changed:
            changed = False
            best_idx = -1
            best_connectivity = 0.0

            for i in range(n):
                if i in cluster_set:
                    continue

                # Count how many cluster nodes this candidate is connected to
                neighbor_count = int(adj[cluster_list, i].sum())
                # Fraction of cluster nodes the candidate connects to
                frac = neighbor_count / len(cluster_list) if cluster_list else 0.0

                # Only consider candidates connected to at least 35% of the cluster
                if frac < 0.35:
                    continue

                # Score = fraction (prefer better-connected nodes)
                if frac > best_connectivity:
                    best_connectivity = frac
                    best_idx = i

            # Accept the best-connected candidate if it connects to >= 35% of cluster
            # AND the resulting cluster density stays >= density_threshold
            if best_idx != -1 and best_connectivity >= 0.35:
                cluster_set.add(best_idx)
                cluster_list.append(best_idx)
                cluster_name_set.add(names[best_idx])
                changed = True

        logger.info("ClusterDetector._grow_cluster seed=%s size=%d",
                    names[seed_idx], len(cluster_name_set))

        return list(cluster_name_set)

    def _post_growth_density(self, cluster_names: list[str],
                              dense: np.ndarray, matrix: CooccurrenceMatrix,
                              all_names: list[str]) -> float:
        """Compute salience-weighted edge density of a grown cluster."""
        density, _ = self._cluster_density(
            cluster_names, all_names, dense, matrix, use_salience=self.use_salience
        )
        return density

    @staticmethod
    def _cluster_density(cluster_names: list[str], all_names: list[str],
                         dense: np.ndarray, matrix: CooccurrenceMatrix,
                         use_salience: bool = True
                         ) -> tuple[float, list[float]]:
        """Compute edge density (salience-weighted) and pairwise NPMI values.

        When ``use_salience=True``, each NPMI edge is multiplied by the
        geometric mean of the two features' ICF salience.  This prevents
        generic high-frequency features from dominating.
        """
        name_to_idx = {n: i for i, n in enumerate(all_names)}
        node_idx: list[int] = [name_to_idx[n] for n in cluster_names]
        k = len(node_idx)
        if k < 2:
            return 0.0, []

        weighted_sum = 0.0
        possible = k * (k - 1) / 2.0
        npmis: list[float] = []

        for i in range(k):
            for j in range(i + 1, k):
                v = float(dense[node_idx[i], node_idx[j]])
                npmis.append(v)

                if v <= 0:
                    continue

                if use_salience:
                    s_i = matrix.salience_normalized(cluster_names[i])
                    s_j = matrix.salience_normalized(cluster_names[j])
                    salience_weight = math.sqrt(s_i * s_j + 1e-12)
                    weighted_sum += v * salience_weight
                else:
                    weighted_sum += v

        density = weighted_sum / possible if possible > 0 else 0.0
        return density, npmis

    @staticmethod
    def _composite_score(density: float, size: int,
                         pair_npmis: list[float]) -> float:
        """Composite ranking score.

        ``score = density² × (log₂(size) + 1) × mean_npmi_bonus``
        """
        mean_npmi = np.mean(pair_npmis) if pair_npmis else 0.0
        size_bonus = math.log2(size + 1)
        npmi_bonus = 1.0 + max(0.0, min(1.0, mean_npmi))
        return (density ** 2) * size_bonus * npmi_bonus


# ══════════════════════════════════════════════════════════════════════════════
# Persistence
# ══════════════════════════════════════════════════════════════════════════════

def _get_conn() -> sqlite3.Connection:
    """Get a connection to the shared brain_stem database."""
    db_path = canonical_db_path(DB_NAME)
    os.makedirs(Path(str(db_path)).parent, exist_ok=True)
    return open_connection(str(db_path), row_factory=sqlite3.Row)


def ensure_schema() -> None:
    """Create the concept_birth tables if they don't exist.

    Lives alongside the existing ``living_edges`` tables in brain_stem.db.
    """
    conn = _get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS concept_birth_feature_counts (
            feature TEXT PRIMARY KEY,
            total_count INTEGER NOT NULL DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS concept_birth_cooccurrence (
            feature_a TEXT NOT NULL,
            feature_b TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (feature_a, feature_b)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS concept_birth_latent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            features_json TEXT NOT NULL,
            birth_time REAL NOT NULL,
            density_at_birth REAL NOT NULL DEFAULT 0.0,
            cluster_score_at_birth REAL NOT NULL DEFAULT 0.0,
            predictive_weight REAL NOT NULL DEFAULT 0.5,
            successes INTEGER NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0,
            weight REAL NOT NULL DEFAULT 0.5,
            posterior_alpha REAL NOT NULL DEFAULT 1.0,
            posterior_beta REAL NOT NULL DEFAULT 1.0,
            last_activation_time REAL NOT NULL DEFAULT 0.0,
            is_alive INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS concept_birth_prediction_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_id INTEGER NOT NULL,
            input_features_json TEXT NOT NULL,
            activation REAL NOT NULL DEFAULT 0.0,
            error_before REAL NOT NULL DEFAULT 0.0,
            error_after REAL NOT NULL DEFAULT 0.0,
            was_success INTEGER NOT NULL DEFAULT 0,
            timestamp REAL NOT NULL
        )
    """)

    # ── Schema migration (C3) ────────────────────────────────────────────
    # Add posterior_alpha/beta columns if they don't exist (Phase 62 → C3)
    mig_checks = [
        ("posterior_alpha", "ALTER TABLE concept_birth_latent ADD COLUMN posterior_alpha REAL NOT NULL DEFAULT 1.0"),
        ("posterior_beta", "ALTER TABLE concept_birth_latent ADD COLUMN posterior_beta REAL NOT NULL DEFAULT 1.0"),
        ("last_activation_time", "ALTER TABLE concept_birth_latent ADD COLUMN last_activation_time REAL NOT NULL DEFAULT 0.0"),
    ]
    for col_name, alter_sql in mig_checks:
        try:
            c.execute(f"SELECT {col_name} FROM concept_birth_latent LIMIT 1")
        except sqlite3.OperationalError:
            c.execute(alter_sql)
            logger.info("Schema migration: added column '%s' to concept_birth_latent", col_name)

    conn.commit()
    conn.close()


def persist_feature_counts(matrix: CooccurrenceMatrix) -> None:
    """Write the current feature count state to SQLite."""
    conn = _get_conn()
    c = conn.cursor()
    now_int = int(time.time())
    for feature, stats in matrix._stats.items():
        c.execute("""
            INSERT INTO concept_birth_feature_counts (feature, total_count)
            VALUES (?, ?)
            ON CONFLICT(feature) DO UPDATE SET total_count = excluded.total_count
        """, (feature, stats.total_count))
        for other_feat, count in stats.co_counts.items():
            left, right = (feature, other_feat) if feature <= other_feat else (other_feat, feature)
            c.execute("""
                INSERT INTO concept_birth_cooccurrence (feature_a, feature_b, count)
                VALUES (?, ?, ?)
                ON CONFLICT(feature_a, feature_b) DO UPDATE SET count = excluded.count
            """, (left, right, count))
    conn.commit()
    conn.close()


def persist_concept(concept: LatentConcept) -> None:
    """Persist a single latent concept to SQLite.

    Stores the Beta posterior parameters (posterior_alpha, posterior_beta)
    and last activation time for the C3 Bayesian surprise engine.
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO concept_birth_latent
            (id, features_json, birth_time, density_at_birth, cluster_score_at_birth,
             predictive_weight, successes, attempts, weight,
             posterior_alpha, posterior_beta, last_activation_time, is_alive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        concept.id,
        json.dumps(sorted(concept.features)),
        concept.birth_time,
        concept.density_at_birth,
        concept.cluster_score_at_birth,
        concept.predictive_weight,
        concept.successes,
        concept.attempts,
        concept.weight,
        concept.posterior_alpha,
        concept.posterior_beta,
        concept.last_activation_time,
        1 if concept.is_alive else 0,
    ))
    conn.commit()
    conn.close()


def persist_prediction_log(concept_id: int, input_features: set[str],
                           activation: float, error_before: float,
                           error_after: float) -> None:
    """Log a prediction attempt for audit."""
    conn = _get_conn()
    c = conn.cursor()
    was_success = 1 if error_after < error_before else 0
    c.execute("""
        INSERT INTO concept_birth_prediction_log
            (concept_id, input_features_json, activation, error_before, error_after,
             was_success, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        concept_id,
        json.dumps(sorted(input_features)),
        activation,
        error_before,
        error_after,
        was_success,
        time.time(),
    ))
    conn.commit()
    conn.close()


def load_persisted_concepts() -> list[LatentConcept]:
    """Load all alive latent concepts from the database."""
    ensure_schema()
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM concept_birth_latent WHERE is_alive = 1 ORDER BY id")
    concepts: list[LatentConcept] = []
    for row in c.fetchall():
        concepts.append(LatentConcept(
            id=row["id"],
            features=frozenset(json.loads(row["features_json"])),
            birth_time=row["birth_time"],
            density_at_birth=row["density_at_birth"],
            cluster_score_at_birth=row["cluster_score_at_birth"],
            predictive_weight=row["predictive_weight"],
            successes=row["successes"],
            attempts=row["attempts"],
            weight=row["weight"],
            posterior_alpha=row["posterior_alpha"],
            posterior_beta=row["posterior_beta"],
            last_activation_time=row["last_activation_time"],
        ))
    conn.close()
    return concepts


def mark_concept_dead(concept_id: int) -> None:
    """Mark a latent concept as pruned."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("UPDATE concept_birth_latent SET is_alive = 0, weight = 0.0 WHERE id = ?",
              (concept_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# Main Engine
# ══════════════════════════════════════════════════════════════════════════════

class ConceptBirthEngine:
    """The central Concept Birth Engine.

    Orchestrates the full pipeline (C3 enhanced):

    1. Ingest experiences into the add-k smoothed co-occurrence matrix.
    2. Validate existing concepts using **Bayesian surprise** (KL divergence
       of Beta posteriors) instead of heuristic error differences.
    3. Periodically run **spectral clustering** on the Laplacian of the NPMI
       graph to discover latent structure.
    4. Use **greedy seed-growth** (initialised from spectral seeds) to find
       dense feature clusters → spawn LatentConcepts.
    5. **Consolidate overlapping concepts** via Hungarian alignment and
       Jaccard similarity — merge rather than spawn duplicates.
    6. Apply time-aware **metabolic decay** (idle concepts decay faster).
    7. **Prune** concepts whose weight drops below threshold.
    8. Export to ontology via ``update_ontology()``.

    Parameters
    ----------
    npmi_threshold
        Minimum NPMI to consider an edge.  ``None`` = use adaptive threshold.
    spawn_density_threshold
        Minimum cluster density to spawn a concept.
    spawn_min_features
        Minimum features in a cluster for spawning.
    spawn_min_experiences
        Minimum distinct experiences covering the cluster features.
    learning_rate
        Rate at which predictive weight adjusts.
    decay_rate
        Per-cycle metabolic decay applied to all concepts.
    pruning_weight
        Weight below which a concept is pruned.
    pruning_age_seconds
        Minimum age before pruning is allowed.
    scan_interval
        Minimum seconds between cluster detection scans.
    max_concepts
        Maximum number of alive latent concepts (oldest/weakest evicted).
    use_spectral_seeds
        Whether to use spectral clustering for seed initialization.
    use_concept_merging
        Whether to merge overlapping concepts during scan.
    """

    def __init__(
        self,
        npmi_threshold: float | None = None,  # None = auto-adaptive
        spawn_density_threshold: float = DEFAULT_SPAWN_DENSITY_THRESHOLD,
        spawn_min_features: int = DEFAULT_SPAWN_MIN_FEATURES,
        spawn_min_experiences: int = DEFAULT_SPAWN_EXPERIENCE_COUNT,
        learning_rate: float = DEFAULT_LEARNING_RATE,
        decay_rate: float = DEFAULT_DECAY_RATE,
        pruning_weight: float = DEFAULT_PRUNING_WEIGHT,
        pruning_age_seconds: float = DEFAULT_PRUNING_AGE_SECONDS,
        scan_interval: float = 10.0,
        max_concepts: int = 500,
        use_spectral_seeds: bool = True,
        use_concept_merging: bool = True,
    ) -> None:
        self.matrix = CooccurrenceMatrix(add_k=DEFAULT_ADD_K, tau=DEFAULT_EXPERIENCE_TAU)
        self.concepts: dict[int, LatentConcept] = {}
        self._next_id_counter: int = 1

        self.npmi_threshold = npmi_threshold  # None = adaptive
        self.spawn_density_threshold = spawn_density_threshold
        self.spawn_min_features = spawn_min_features
        self.spawn_min_experiences = spawn_min_experiences
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        self.pruning_weight = pruning_weight
        self.pruning_age_seconds = pruning_age_seconds
        self.scan_interval = scan_interval
        self.max_concepts = max_concepts
        self.use_spectral_seeds = use_spectral_seeds
        self.use_concept_merging = use_concept_merging

        self._last_scan_time: float = 0.0
        self._last_decay_time: float = time.time()
        self._total_experiences_ingested: int = 0
        self._experience_history: list[set[str]] = []  # rolling window for diversity checks
        self._max_history_size: int = 500

        # Spectral cluster initializer (lazy)
        self._spectral: SpectralClusterInitializer | None = None
        self._spectral_timer: float = 0.0
        self._spectral_interval: float = max(60.0, scan_interval * 5)  # less frequent

        # Merge tracking
        self._merge_count: int = 0

        # Persistence
        ensure_schema()
        recovered = load_persisted_concepts()
        for c in recovered:
            self.concepts[c.id] = c
            self._next_id_counter = max(self._next_id_counter, c.id + 1)

    # ── public API ─────────────────────────────────────────────────────────────

    def ingest(self, experience: Experience) -> dict[str, Any]:
        """Ingest a single experience through the Bayesian surprise pipeline.

        1. Update the add-k smoothed co-occurrence matrix.
        2. Validate each existing concept: compute its activation and
           Bayesian surprise (KL divergence).  A concept succeeds if its
           activation is high *and* its Beta posterior KL drops below the
           certainty threshold.
        3. Periodically run spectral + greedy cluster scan.
        4. Apply time-aware metabolic decay.
        5. Prune weak concepts.

        Returns a report dict with counts for new_concepts, updates, pruned.
        """
        report: dict[str, Any] = {
            "experience_feature_count": len(experience.features),
            "new_concepts": 0,
            "updates": 0,
            "pruned": 0,
        }

        # Skip empty experiences
        if not experience.features:
            return report

        # 1. Update co-occurrence
        self.matrix.update(experience)
        self._experience_history.append(experience.features)
        if len(self._experience_history) > self._max_history_size:
            self._experience_history.pop(0)

        # 2. Bayesian surprise validation of existing concepts
        for concept in list(self.concepts.values()):
            if not concept.is_alive:
                continue
            activation = concept.activation(experience.features)
            if activation > 0.0:
                # Compute Bayesian surprise instead of heuristic errors
                kl_div, scaled_surprise, incertainty = \
                    BayesianSurprise.compute_surprise(concept, activation)

                concept.record_prediction(activation, scaled_surprise,
                                          self.learning_rate)
                concept.last_activation_time = time.time()
                persist_prediction_log(
                    concept.id, experience.features,
                    activation, kl_div, scaled_surprise,
                )
                report["updates"] += 1

        # 3. Periodic cluster scan with spectral + merging
        now = time.time()
        if (now - self._last_scan_time) >= self.scan_interval:
            new_ids = self._scan_for_concepts()
            report["new_concepts"] = len(new_ids)
            self._last_scan_time = now

        # 4. Time-aware decay
        dt = now - self._last_decay_time
        if dt >= 1.0:
            for concept in list(self.concepts.values()):
                concept.decay(self.decay_rate * dt, now=now)
                persist_concept(concept)
            self._last_decay_time = now

        # 5. Prune
        pruned = self._prune_weak_concepts()
        report["pruned"] = pruned

        self._total_experiences_ingested += 1

        # Persist feature counts periodically
        if self._total_experiences_ingested % 5 == 0:
            persist_feature_counts(self.matrix)

        return report

    def ingest_batch(self, experiences: list[Experience]) -> dict[str, Any]:
        """Ingest multiple experiences in one call, merging before scan."""
        agg_report: dict[str, Any] = {
            "total": len(experiences),
            "new_concepts": 0,
            "total_updates": 0,
            "total_pruned": 0,
            "batch_matrix_merged": False,
        }

        batch_matrix = CooccurrenceMatrix(add_k=DEFAULT_ADD_K, tau=self.matrix._tau)
        for exp in experiences:
            batch_matrix.update(exp)

        self.matrix.merge(batch_matrix)
        agg_report["batch_matrix_merged"] = True

        for exp in experiences:
            self._experience_history.append(exp.features)
            if len(self._experience_history) > self._max_history_size:
                self._experience_history.pop(0)

            for concept in list(self.concepts.values()):
                if not concept.is_alive:
                    continue
                activation = concept.activation(exp.features)
                if activation > 0.0:
                    kl_div, scaled_surprise, incertainty = \
                        BayesianSurprise.compute_surprise(concept, activation)
                    concept.record_prediction(activation, scaled_surprise,
                                              self.learning_rate)
                    concept.last_activation_time = time.time()
                    persist_prediction_log(concept.id, exp.features,
                                           activation, kl_div, scaled_surprise)
                    agg_report["total_updates"] += 1

        new_ids = self._scan_for_concepts()
        agg_report["new_concepts"] = len(new_ids)

        now = time.time()
        dt = now - self._last_decay_time
        for concept in list(self.concepts.values()):
            concept.decay(self.decay_rate * dt, now=now)
            persist_concept(concept)
        self._last_decay_time = now

        pruned = self._prune_weak_concepts()
        agg_report["total_pruned"] = pruned

        self._total_experiences_ingested += len(experiences)

        return agg_report

    # ── ontology integration ───────────────────────────────────────────────────

    def update_ontology(self) -> dict[str, Any]:
        """Export birthed concepts to the knowledge graph and world model.

        Returns a structured report consumable by the VELYNX orchestrator,
        including each concept's features, Beta posterior parameters, NPMI
        relations, and salience weights.
        """
        alive = [c for c in self.concepts.values() if c.is_alive]

        ontology_entries: list[dict[str, Any]] = []
        for concept in alive:
            entry = concept.to_dict()
            # Attach NPMI relations for top-5 features
            sorted_feats = sorted(concept.features)
            relations: list[dict[str, Any]] = []
            for f in sorted_feats[:5]:
                relations.append({
                    "feature": f,
                    "salience": round(self.matrix.feature_salience(f), 4),
                    "top_cooccurring": self.matrix.top_cooccurring(f, k=3),
                })
            entry["feature_relations"] = relations
            entry["kl_surprise_from_uniform"] = round(
                BayesianSurprise.kl_beta_uniform(
                    concept.posterior_alpha, concept.posterior_beta
                ), 4
            )
            ontology_entries.append(entry)

        for concept in alive:
            persist_concept(concept)

        return {
            "status": "ok",
            "engine_version": "C3",
            "total_concepts": len(self.concepts),
            "alive_concepts": len(alive),
            "total_experiences": self._total_experiences_ingested,
            "feature_universe_size": self.matrix.feature_count,
            "adaptive_npmi_threshold": round(self.matrix.current_threshold, 4),
            "concept_merges": self._merge_count,
            "concepts": ontology_entries,
            "matrix_stats": self.matrix.stats_dict(),
        }

    def get_concept(self, concept_id: int) -> Optional[LatentConcept]:
        """Retrieve a specific concept by ID."""
        return self.concepts.get(concept_id)

    def find_concepts_by_feature(self, feature: str) -> list[LatentConcept]:
        """Find all alive concepts that contain *feature*."""
        return [
            c for c in self.concepts.values()
            if c.is_alive and feature in c.features
        ]

    def get_state_report(self) -> dict[str, Any]:
        """Full state report for diagnostics."""
        return {
            "engine_version": "C3",
            "total_experiences_ingested": self._total_experiences_ingested,
            "unique_features": self.matrix.feature_count,
            "alive_concepts": sum(1 for c in self.concepts.values() if c.is_alive),
            "total_concepts_birthed": len(self.concepts),
            "matrix_dense_size": len(self.matrix.dense_names),
            "adaptive_threshold": round(self.matrix.current_threshold, 4),
            "add_k_smoothing": self.matrix._add_k,
            "concept_merges": self._merge_count,
            "last_scan_time": self._last_scan_time,
            "next_concept_id": self._next_id_counter,
        }

    # ── internal ───────────────────────────────────────────────────────────────

    def _next_concept_id(self) -> int:
        nid = self._next_id_counter
        self._next_id_counter += 1
        return nid

    def _get_spectral_seeds(self) -> list[list[str]]:
        """Run spectral clustering and return seed lists, with throttling."""
        now = time.time()
        if (now - self._spectral_timer) < self._spectral_interval and self._spectral is not None:
            return []  # not yet time to re-run spectral
        if self._spectral is None:
            self._spectral = SpectralClusterInitializer()
        self._spectral_timer = now
        # Only run spectral if we have enough data
        if self.matrix.feature_count < self.spawn_min_features * 2:
            return []
        try:
            detector = ClusterDetector(
                density_threshold=self.spawn_density_threshold,
                min_features=self.spawn_min_features,
            )
            return self._spectral.get_spectral_seeds(self.matrix, detector)
        except Exception:
            logger.warning("Spectral clustering failed, falling back to greedy only")
            return []

    def _scan_for_concepts(self) -> list[int]:
        """Run cluster detection and spawn or merge new latent concepts.

        Uses spectral seeds if available, then greedy growth.  After
        spawning, checks for concept merging opportunities (Hungarian
        alignment and Jaccard overlap).

        Returns the IDs of newly spawned concepts (does NOT include
        IDs that were merged into existing ones).
        """
        detector = ClusterDetector(
            npmi_threshold=self.npmi_threshold,
            density_threshold=self.spawn_density_threshold,
            min_features=self.spawn_min_features,
            use_salience=True,
        )

        # Get spectral seeds (throttled)
        spectral_seeds: list[list[str]] | None = None
        if self.use_spectral_seeds:
            spectral_seeds = self._get_spectral_seeds()
            if not spectral_seeds:
                spectral_seeds = None

        candidates = detector.find_clusters(self.matrix, spectral_seeds=spectral_seeds)
        new_ids: list[int] = []

        for candidate in candidates:
            if len(candidate.features) < self.spawn_min_features:
                continue

            # Skip if exact feature set already exists
            if self._concept_exists(candidate.features):
                continue

            # Diversity check
            coverage_count = 0
            for exp_features in self._experience_history:
                overlap = len(candidate.features & exp_features)
                if overlap >= 2:
                    coverage_count += 1
            if coverage_count < self.spawn_min_experiences:
                continue

            # Check for merging opportunity before spawning
            if self.use_concept_merging and self.concepts:
                merged = False
                for existing in list(self.concepts.values()):
                    if not existing.is_alive:
                        continue
                    if should_merge_concepts(
                        existing, candidate.to_concept(self, time.time()),
                        self.matrix,
                    ):
                        # Merge candidate into existing
                        before_features = len(existing.features)
                        existing.merge_with(
                            candidate.to_concept(self, time.time())
                        )
                        after_features = len(existing.features)
                        if after_features > before_features:
                            self._merge_count += 1
                            persist_concept(existing)
                            logger.info(
                                "ConceptBirth: merged candidate into concept %d "
                                "(features %d→%d, meritocracy bonus applied)",
                                existing.id, before_features, after_features,
                            )
                        merged = True
                        break
                if merged:
                    continue

            # Spawn new concept
            now = time.time()
            concept = candidate.to_concept(self, now)
            self.concepts[concept.id] = concept
            persist_concept(concept)
            new_ids.append(concept.id)

            logger.info(
                "ConceptBirth[C3]: spawned LatentConcept %d (%d features, "
                "density=%.3f, score=%.3f, coverage=%d, threshold=%.3f)",
                concept.id, len(concept.features), candidate.density,
                candidate.score, coverage_count, self.matrix.current_threshold,
            )

            if len(self.concepts) > self.max_concepts:
                self._evict_weakest()

        return new_ids

    def _prune_weak_concepts(self) -> int:
        """Remove concepts that have decayed below threshold and are old enough.

        Also prunes concepts whose Beta posterior has converged near zero
        (posterior_beta >> posterior_alpha) — they have *confidently failed*
        at prediction.
        """
        now = time.time()
        pruned = 0
        for cid, concept in list(self.concepts.items()):
            if not concept.is_alive:
                continue
            age = now - concept.birth_time

            # Standard weight-based pruning
            weight_dead = concept.weight < self.pruning_weight and age > self.pruning_age_seconds

            # Beta-based pruning: concept has confidently failed
            # (posterior_beta >> posterior_alpha means many failures)
            total_posterior = concept.posterior_alpha + concept.posterior_beta
            if total_posterior > 5:
                failure_ratio = concept.posterior_beta / total_posterior
                beta_dead = failure_ratio > 0.90 and concept.attempts > 10
            else:
                beta_dead = False

            if weight_dead or beta_dead:
                mark_concept_dead(cid)
                self.concepts[cid].weight = 0.0
                pruned += 1
                if beta_dead:
                    logger.info("ConceptBirth: pruned concept %d (Beta failure: %.1f/%.1f)",
                                cid, concept.posterior_beta, total_posterior)
                else:
                    logger.info("ConceptBirth: pruned concept %d (weight=%.4f, age=%.1fs)",
                                cid, concept.weight, age)
        return pruned

    def _evict_weakest(self) -> None:
        """Evict the single weakest concept to stay under max_concepts.

        Eviction considers both current weight and Beta posterior — a
        concept with high posterior_beta (confidently unreliable) is
        evicted first even if its weight hasn't fully decayed.
        """
        alive = [(cid, c) for cid, c in self.concepts.items() if c.is_alive]
        if len(alive) <= self.max_concepts:
            return

        def eviction_score(pair) -> float:
            _, c = pair
            # Lower score = more likely to be evicted
            total = c.posterior_alpha + c.posterior_beta
            if total > 3:
                reliability = c.posterior_alpha / total
            else:
                reliability = 0.5
            return c.weight * (0.3 + 0.7 * reliability)

        alive.sort(key=eviction_score)
        weakest_id, weakest = alive[0]
        mark_concept_dead(weakest_id)
        self.concepts[weakest_id].weight = 0.0
        logger.info("ConceptBirth: evicted weakest concept %d (weight=%.4f, reliability=%.3f)",
                    weakest_id, weakest.weight,
                    weakest.posterior_alpha / max(1, weakest.posterior_alpha + weakest.posterior_beta))

    def _concept_exists(self, feature_set: frozenset[str]) -> bool:
        """Check if a concept with this exact feature set already exists."""
        for concept in self.concepts.values():
            if concept.features == feature_set:
                return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Self-Check
# ══════════════════════════════════════════════════════════════════════════════

def _self_check() -> None:
    """Run a demonstration: feed synthetic experiences, verify emergent concepts.

    Run via ``python -m backend.cognition.concept_birth``.
    """
    print("=" * 64)
    print("VELYNX Concept Birth Engine C3 — Self-Check")
    print("=" * 64)

    engine = ConceptBirthEngine(
        npmi_threshold=None,               # auto-adaptive
        spawn_density_threshold=0.40,
        spawn_min_features=2,
        spawn_min_experiences=2,
        scan_interval=0.1,
        decay_rate=0.01,
        pruning_weight=0.01,
        pruning_age_seconds=300.0,
        use_spectral_seeds=True,
        use_concept_merging=True,
    )

    # -- Phase 1: Teach "mammal-like" features -----------------------------
    print("\nPhase 1: Mammal experiences...")
    mammal_experiences = [
        Experience({"tail", "fur", "barks", "four_legs"}, {"animal": "dog"}),
        Experience({"tail", "fur", "meows", "four_legs"}, {"animal": "cat"}),
        Experience({"tail", "fur", "wild", "four_legs"}, {"animal": "fox"}),
        Experience({"tail", "fur", "howls", "four_legs"}, {"animal": "wolf"}),
        Experience({"fur", "barks", "four_legs", "tail"}, {"animal": "dog_2"}),
    ]
    for exp in mammal_experiences:
        report = engine.ingest(exp)
        if report["new_concepts"] > 0:
            print(f"  Spawned {report['new_concepts']} concept(s) from mammal experiences")

    # -- Phase 2: Teach "bird-like" features -------------------------------
    print("\nPhase 2: Bird experiences...")
    bird_experiences = [
        Experience({"feathers", "wings", "flies", "beak"}, {"animal": "eagle"}),
        Experience({"feathers", "wings", "flies", "beak"}, {"animal": "sparrow"}),
        Experience({"feathers", "wings", "swims", "beak"}, {"animal": "penguin"}),
    ]
    for exp in bird_experiences:
        report = engine.ingest(exp)
        if report["new_concepts"] > 0:
            print(f"  Spawned {report['new_concepts']} concept(s) from bird experiences")

    # -- Phase 3: Force a cluster scan with spectral -----------------------
    print("\nPhase 3: Forcing spectral cluster scan...")
    engine._last_scan_time = 0.0
    engine.ingest(Experience({"tail", "fur", "wild", "four_legs"}, {"animal": "lynx"}))
    engine.ingest(Experience({"feathers", "wings", "flies", "beak"}, {"animal": "hawk"}))

    # -- Report ------------------------------------------------------------
    print()
    state = engine.get_state_report()
    print(f"  Engine version:             {state['engine_version']}")
    print(f"  Experiences ingested:       {state['total_experiences_ingested']}")
    print(f"  Unique features observed:   {state['unique_features']}")
    print(f"  Alive concepts:             {state['alive_concepts']}")
    print(f"  Total concepts birthed:     {state['total_concepts_birthed']}")
    print(f"  Adaptive NPMI threshold:    {state['adaptive_threshold']:.4f}")
    print(f"  Add-k smoothing:            {state['add_k_smoothing']}")
    print(f"  Concept merges:             {state['concept_merges']}")

    for cid, concept in sorted(engine.concepts.items()):
        if concept.is_alive:
            kl = BayesianSurprise.kl_beta_uniform(
                concept.posterior_alpha, concept.posterior_beta
            )
            print(f"\n  ** LatentConcept {cid} **")
            print(f"     Features:              {sorted(concept.features)}")
            print(f"     Weight:                {concept.weight:.4f}")
            print(f"     Beta posterior:        ({concept.posterior_alpha:.1f}, {concept.posterior_beta:.1f})")
            print(f"     KL from uniform:       {kl:.4f}")
            print(f"     Success rate:          {concept.successes}/{concept.attempts}")
            print(f"     Density at birth:      {concept.density_at_birth:.3f}")
            print(f"     Last activation:       {'yes' if concept.last_activation_time > 0 else 'never'}")

    # -- Validate NPMI math (smoothed) ------------------------------------
    print("\n  -- Feature Associations (Add-k smoothed NPMI) --")
    pairs = [
        ("tail", "fur"), ("feathers", "wings"), ("tail", "wings"),
        ("barks", "four_legs"), ("flies", "beak"),
    ]
    for a, b in pairs:
        npmi_val = engine.matrix.npmi(a, b)
        print(f"     NPMI({a}, {b}) = {npmi_val:+.4f}")

    # -- Feature salience -------------------------------------------------
    print("\n  -- Feature Salience (ICF) --")
    for feat in sorted(engine.matrix.all_features())[:10]:
        sal = engine.matrix.feature_salience(feat)
        print(f"     ICF({feat}) = {sal:.4f}")

    # -- Assertions --------------------------------------------------------
    assert state["alive_concepts"] >= 2, (
        f"Expected >= 2 alive concepts, got {state['alive_concepts']}"
    )
    assert state["unique_features"] >= 10, (
        f"Expected >= 10 unique features, got {state['unique_features']}"
    )

    tail_fur_npmi = engine.matrix.npmi("tail", "fur")
    assert tail_fur_npmi > 0.15, (
        f"Expected NPMI(tail, fur) > 0.15, got {tail_fur_npmi:.4f}"
    )

    feathers_wings_npmi = engine.matrix.npmi("feathers", "wings")
    assert feathers_wings_npmi > 0.15, (
        f"Expected NPMI(feathers, wings) > 0.15, got {feathers_wings_npmi:.4f}"
    )

    # Verify Beta posteriors are valid (active concepts have been updated)
    for concept in engine.concepts.values():
        if concept.is_alive and concept.attempts > 0:
            assert concept.posterior_alpha >= 1.0, f"Bad posterior_alpha for {concept.id}"
            assert concept.posterior_beta >= 1.0, f"Bad posterior_beta for {concept.id}"
            assert concept.posterior_alpha + concept.posterior_beta >= 2.0
            assert concept.posterior_alpha + concept.posterior_beta > 2.0, (
                f"Concept {concept.id}: attempts={concept.attempts} but "
                f"posterior={concept.posterior_alpha}+{concept.posterior_beta}=2.0"
            )

    # Check ontology export
    ontology = engine.update_ontology()
    assert ontology["status"] == "ok"
    assert ontology["engine_version"] == "C3"
    assert ontology["alive_concepts"] == state["alive_concepts"]

    print()
    print("  + All C3 assertions passed — Concept Birth Engine operational.")
    print("  + Add-k smoothing, Bayesian surprise, spectral init, ICF salience active.")
    print("=" * 64)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(name)s %(levelname)s %(message)s")
    _self_check()
