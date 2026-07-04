"""
research/proposals/sources.py
=============================

The four concrete :class:`~research.proposals.base.ProposalSource` bidders for
Sprint R3's counterfactual merge market. Each ranks candidate cluster pairs by
a *different* notion of "mergeable" and bids its top ``k = 2``:

* :class:`GeometricSource` — nearest centroid pairs (Euclidean proximity). This
  is the criterion the frozen production
  :class:`~backend.cognition.candidate_generator.CandidateGenerator` uses.
* :class:`TemporalSource`  — pairs whose *cluster-transition dynamics* are most
  alike, measured by the **Jensen-Shannon divergence** (JSD) between their
  outgoing-transition distributions over the recent window. Low JSD ⇒ the two
  clusters behave the same temporally ⇒ a natural merge.
* :class:`UtilitySource`   — the two *least-utilised* clusters (lowest combined
  access count); folding rarely-visited clusters frees representational budget.
* :class:`RandomSource`    — uniformly random distinct pairs drawn from the
  context RNG (a control bidder; the only stochastic source).

Every source is read-only: it inspects ``context.engine.clusters`` and the
recent window, and never mutates anything.

Standard library only.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from backend.cognition.vector_prediction_core import euclidean_distance
from research.proposals.base import MarketContext, ProposalSource

# A ranked candidate: ((a, b), centroid_distance, source_score).
RankedPair = Tuple[Tuple[int, int], float, float]


def _ordered(a: int, b: int) -> Tuple[int, int]:
    """Canonical ascending ordering of a target pair (for stable ids/sorting)."""
    return (a, b) if a <= b else (b, a)


def _centroid_distance(engine, a: int, b: int) -> float:
    """Euclidean centroid distance between two clusters, or ``nan`` if missing."""
    ca = engine.get_cluster(a)
    cb = engine.get_cluster(b)
    if ca is None or cb is None:
        return float("nan")
    return euclidean_distance(ca.centroid, cb.centroid)


class GeometricSource(ProposalSource):
    """Bid the nearest centroid pairs (the frozen C8.1 proximity criterion)."""

    name = "geometric"
    description = "Nearest centroid pairs by Euclidean distance (proximity)."

    def rank_pairs(self, context: MarketContext) -> List[RankedPair]:
        clusters = context.clusters()
        if len(clusters) < 2:
            return []
        ranked: List[RankedPair] = []
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                a, b = _ordered(clusters[i].id, clusters[j].id)
                dist = euclidean_distance(clusters[i].centroid, clusters[j].centroid)
                ranked.append(((a, b), dist, dist))
        # Nearest first; tie-break on the canonical pair for determinism.
        ranked.sort(key=lambda r: (r[2], r[0]))
        return ranked


class TemporalSource(ProposalSource):
    """Bid pairs with the most similar transition dynamics (lowest JSD).

    For each cluster we build its *outgoing-transition distribution*: replay the
    recent window read-only into the nearest-cluster id sequence, then count how
    often each cluster is followed by each other cluster. Two clusters that hand
    off to the same successors in the same proportions have a low Jensen-Shannon
    divergence and are strong temporal-merge candidates.
    """

    name = "temporal"
    description = (
        "Pairs with the most similar outgoing cluster-transition distributions, "
        "by Jensen-Shannon divergence over the recent window."
    )

    def rank_pairs(self, context: MarketContext) -> List[RankedPair]:
        engine = context.engine
        clusters = context.clusters()
        if len(clusters) < 2:
            return []
        distributions = self._transition_distributions(engine, context.recent_vectors)

        ranked: List[RankedPair] = []
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                ca, cb = clusters[i], clusters[j]
                a, b = _ordered(ca.id, cb.id)
                jsd = _jensen_shannon_divergence(
                    distributions.get(ca.id, {}), distributions.get(cb.id, {})
                )
                dist = euclidean_distance(ca.centroid, cb.centroid)
                ranked.append(((a, b), dist, jsd))
        # Lowest divergence first; tie-break on the canonical pair.
        ranked.sort(key=lambda r: (r[2], r[0]))
        return ranked

    @staticmethod
    def _transition_distributions(
        engine, window: List[List[float]]
    ) -> Dict[int, Dict[int, float]]:
        """Normalised outgoing-transition distributions, keyed by cluster id.

        Read-only: maps each window vector to its nearest cluster id (no
        centroid update), counts first-order transitions, and normalises each
        cluster's outgoing counts into a probability distribution.
        """
        clusters = list(getattr(engine, "clusters", []))
        if not clusters or len(window) < 2:
            return {}

        sequence: List[int] = []
        for vector in window:
            best_id = None
            best_dist = float("inf")
            for cluster in clusters:
                d = engine._distance(cluster.centroid, vector)
                if d < best_dist:
                    best_dist = d
                    best_id = cluster.id
            if best_id is not None:
                sequence.append(best_id)

        counts: Dict[int, Dict[int, int]] = {}
        for src, dst in zip(sequence[:-1], sequence[1:]):
            row = counts.setdefault(src, {})
            row[dst] = row.get(dst, 0) + 1

        distributions: Dict[int, Dict[int, float]] = {}
        for src, row in counts.items():
            total = sum(row.values())
            if total > 0:
                distributions[src] = {k: v / total for k, v in row.items()}
        return distributions


class UtilitySource(ProposalSource):
    """Bid the two least-utilised clusters (lowest combined access count)."""

    name = "utility"
    description = "Least-utilised pairs by lowest combined cluster access count."

    def rank_pairs(self, context: MarketContext) -> List[RankedPair]:
        engine = context.engine
        clusters = context.clusters()
        if len(clusters) < 2:
            return []
        ranked: List[RankedPair] = []
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                ca, cb = clusters[i], clusters[j]
                a, b = _ordered(ca.id, cb.id)
                combined = float(ca.count + cb.count)
                dist = euclidean_distance(ca.centroid, cb.centroid)
                ranked.append(((a, b), dist, combined))
        # Lowest combined utility first; tie-break on the canonical pair.
        ranked.sort(key=lambda r: (r[2], r[0]))
        return ranked


class RandomSource(ProposalSource):
    """Bid uniformly random distinct pairs (the stochastic control bidder)."""

    name = "random"
    description = "Uniformly random distinct cluster pairs (control)."
    is_stochastic = True

    def rank_pairs(self, context: MarketContext) -> List[RankedPair]:
        clusters = context.clusters()
        if len(clusters) < 2:
            return []
        all_pairs: List[Tuple[int, int]] = []
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                all_pairs.append(_ordered(clusters[i].id, clusters[j].id))
        # Deterministic given the seeded context RNG: shuffle a copy.
        ordered = list(all_pairs)
        context.rng.shuffle(ordered)
        engine = context.engine
        ranked: List[RankedPair] = []
        for rank, (a, b) in enumerate(ordered):
            dist = _centroid_distance(engine, a, b)
            ranked.append(((a, b), dist, float(rank)))
        return ranked


# ---------------------------------------------------------------------------
# Jensen-Shannon divergence (bits)
# ---------------------------------------------------------------------------


def _kl_divergence(p: Dict[int, float], m: Dict[int, float]) -> float:
    """KL(P || M) in bits over the support of ``p`` (``0 log 0 = 0``)."""
    total = 0.0
    for key, p_i in p.items():
        if p_i <= 0.0:
            continue
        m_i = m.get(key, 0.0)
        if m_i <= 0.0:
            # Should not occur (M is the mixture of P and Q), but guard anyway.
            continue
        total += p_i * math.log2(p_i / m_i)
    return total


def _jensen_shannon_divergence(
    p: Dict[int, float], q: Dict[int, float]
) -> float:
    """Jensen-Shannon divergence between two distributions, in bits ``[0, 1]``.

    ``JSD(P, Q) = 0.5*KL(P||M) + 0.5*KL(Q||M)`` with ``M = 0.5*(P + Q)``.

    Convention for missing evidence: if *either* cluster has no observed
    outgoing transitions (an empty distribution), the divergence is the maximal
    ``1.0`` — with no temporal evidence the pair is *not* a confident temporal
    merge and is deprioritised, rather than spuriously appearing identical.
    """
    if not p or not q:
        return 1.0
    support = set(p) | set(q)
    m = {k: 0.5 * (p.get(k, 0.0) + q.get(k, 0.0)) for k in support}
    jsd = 0.5 * _kl_divergence(p, m) + 0.5 * _kl_divergence(q, m)
    # Clamp tiny negative/over-unity values from floating-point error.
    if jsd < 0.0:
        return 0.0
    if jsd > 1.0:
        return 1.0
    return jsd


#: Registry of proposal sources, mirroring the policy-registry pattern.
SOURCE_REGISTRY: Dict[str, type] = {
    GeometricSource.name: GeometricSource,
    TemporalSource.name: TemporalSource,
    UtilitySource.name: UtilitySource,
    RandomSource.name: RandomSource,
}

#: The default bidding panel (deterministic sources first, control last).
DEFAULT_SOURCE_ORDER: List[str] = ["geometric", "temporal", "utility", "random"]


def available_sources() -> List[str]:
    """All registered source names, sorted for stable display."""
    return sorted(SOURCE_REGISTRY)


def build_source(name: str) -> ProposalSource:
    """Construct a proposal source by its registry ``name``."""
    try:
        cls = SOURCE_REGISTRY[name]
    except KeyError:
        valid = ", ".join(available_sources()) or "(none registered)"
        raise KeyError(
            f"Unknown proposal source {name!r}. Registered: {valid}."
        ) from None
    return cls()


def build_default_panel() -> List[ProposalSource]:
    """Instantiate the default bidding panel in :data:`DEFAULT_SOURCE_ORDER`."""
    return [build_source(name) for name in DEFAULT_SOURCE_ORDER]


__all__ = [
    "GeometricSource",
    "TemporalSource",
    "UtilitySource",
    "RandomSource",
    "SOURCE_REGISTRY",
    "DEFAULT_SOURCE_ORDER",
    "available_sources",
    "build_source",
    "build_default_panel",
]
