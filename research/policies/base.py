"""
research/policies/base.py
=========================

The abstract :class:`ConsolidationPolicy` contract and the shared, *policy-free*
selection helpers every concrete policy is built from.

Design contract (Sprint R1, Task 1)
-----------------------------------
A *consolidation policy* answers two — and only two — questions during a
sleep-cycle consolidation step:

1. **Which** two clusters (if any) should be fused? -> :meth:`select_candidate`
2. **Should** that fusion be committed? -> :meth:`accept`

This split is the whole reason the family is comparable. The
:class:`~research.runner.ResearchRunner` always *measures* a proposed merge the
same way (a read-only :class:`~backend.cognition.replay_engine.ReplayEngine`
rehearsal producing a before/after :class:`DecisionScore`), regardless of which
policy produced it. Only the two questions above differ between policies, so any
difference in outcome is attributable to the policy, not the measurement.

Invariants enforced by this module
----------------------------------
* **No policy depends on another policy.** Concrete policies import only this
  module and frozen *cognition* components (``CandidateGenerator`` etc.) — never
  a sibling policy. The shared selection strategies live here as free functions
  so two policies can share *selection logic* without importing each other.
* **The frozen FreeEnergyPolicy is wrapped, never modified.** The
  :class:`~research.policies.free_energy.FreeEnergyPolicy` adapter composes the
  unchanged :class:`~backend.cognition.decision_policy.DecisionPolicy`.
* **Selection is read-only.** Helpers here inspect ``engine.clusters`` and never
  mutate the engine; the only mutation point in the whole pipeline remains
  :meth:`ReplayEngine.commit_proposal`, invoked by the runner after a positive
  verdict.

Standard library only.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Tuple

# Frozen cognition components — wrapped, never modified.
from backend.cognition.candidate_generator import CandidateGenerator, MergeProposal
from backend.cognition.decision_policy import DecisionScore
from backend.cognition.vector_prediction_core import euclidean_distance

# An accept verdict is a (committed?, human-readable reason) pair.
AcceptVerdict = Tuple[bool, str]


@dataclass
class PolicyContext:
    """Per-step context handed to a policy by the runner.

    Carries only what a policy is *allowed* to use to make its decision, so the
    policy stays a pure function of (engine state, context). In particular the
    shared :attr:`rng` is the single deterministic randomness source — a policy
    must never reach for the global ``random`` module, or reproducibility breaks.

    Attributes
    ----------
    rng :
        A seeded :class:`random.Random`. The runner owns one per experiment and
        threads the *same* instance through every step, so a stochastic policy
        is fully reproducible from the experiment seed.
    tick :
        The dataset tick at which this consolidation step is happening.
    energy_weights :
        The ``{"lam", "mu", "nu"}`` free-energy coupling coefficients in force
        for this experiment. Provided so an energy-aware policy reads the same
        weights the audit scorer uses; energy-agnostic policies ignore them.
    merge_index :
        How many merges have already been committed in the current sleep cycle
        (0-based). Lets a policy reason about cycle budget if it wishes.
    """

    rng: random.Random
    tick: int = 0
    energy_weights: Dict[str, float] = field(default_factory=dict)
    merge_index: int = 0


class ConsolidationPolicy(ABC):
    """A hot-swappable memory-consolidation strategy.

    Concrete subclasses set the class attribute :attr:`name` (the config key
    used to select them) and implement :meth:`select_candidate` and
    :meth:`accept`. The default :meth:`describe` reflects the constructor params
    captured in :attr:`params` into the ``policy.json`` artifact.
    """

    #: Registry key (e.g. ``"free_energy"``). Set on every concrete subclass.
    name: ClassVar[str] = "abstract"

    #: One-line human description, surfaced in artifacts and the report.
    description: ClassVar[str] = "Abstract consolidation policy."

    def __init__(self, **params: Any) -> None:
        # Captured verbatim so ``policy.json`` can fully reconstruct the policy.
        self.params: Dict[str, Any] = dict(params)

    # -- the two questions -------------------------------------------------

    @abstractmethod
    def select_candidate(
        self, engine: Any, context: PolicyContext
    ) -> Optional[MergeProposal]:
        """Choose which two clusters to fuse, or ``None`` to consolidate nothing.

        Must treat ``engine`` as read-only. Returning ``None`` ends the current
        sleep cycle's consolidation loop (the runner commits no merge).
        """
        raise NotImplementedError

    @abstractmethod
    def accept(self, score: DecisionScore, context: PolicyContext) -> AcceptVerdict:
        """Decide whether a measured proposal should be committed.

        Parameters
        ----------
        score :
            The before/after vital snapshots produced by the (uniform) read-only
            replay rehearsal of the proposal this policy selected.
        context :
            The same :class:`PolicyContext` passed to :meth:`select_candidate`.

        Returns
        -------
        (bool, str)
            ``(accepted, reason)``. A policy that always commits its own
            proposals returns ``(True, ...)``; the FreeEnergy adapter defers to
            the frozen :class:`DecisionPolicy`.
        """
        raise NotImplementedError

    # -- introspection -----------------------------------------------------

    def describe(self) -> Dict[str, Any]:
        """JSON-safe self-description for the ``policy.json`` artifact."""
        return {
            "name": self.name,
            "description": self.description,
            "class": type(self).__name__,
            "module": type(self).__module__,
            "params": dict(self.params),
            "deterministic": self.is_deterministic,
        }

    @property
    def is_deterministic(self) -> bool:
        """Whether the policy's *selection* is free of the context RNG.

        ``True`` for every policy except :class:`RandomPolicy`. Reported in
        artifacts so a reader knows whether seed variation alone changes which
        clusters this policy chooses (it always changes the *world*).
        """
        return True

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"{type(self).__name__}(name={self.name!r}, params={self.params!r})"


# ---------------------------------------------------------------------------
# Shared, policy-free selection helpers
# ---------------------------------------------------------------------------
# These free functions are the *only* place selection logic is shared. Two
# policies may both call ``nearest_pair`` without importing each other, which is
# how the "no policy depends on another policy" rule is upheld while still
# avoiding copy-pasted geometry.


# A single reusable nearest-pair selector — the exact frozen C8.1 behaviour.
_NEAREST = CandidateGenerator()


def make_proposal(
    engine: Any, target_a: int, target_b: int, strategy: str
) -> MergeProposal:
    """Build a :class:`MergeProposal`, annotating it with the centroid distance.

    The distance is recomputed (read-only) purely as trace metadata so the
    decision audit can report how far apart the fused clusters were under *any*
    selection strategy, not just the nearest-pair one.
    """
    a = engine.get_cluster(target_a)
    b = engine.get_cluster(target_b)
    if a is not None and b is not None:
        distance = euclidean_distance(a.centroid, b.centroid)
    else:
        distance = float("nan")
    return MergeProposal(
        target_a=target_a, target_b=target_b, distance=distance, strategy=strategy
    )


def nearest_pair(engine: Any) -> Optional[MergeProposal]:
    """The two clusters with the minimum centroid distance (frozen C8.1 logic).

    Delegates to the unchanged :class:`CandidateGenerator` so Similarity and
    FreeEnergy share *identical* selection without either importing the other.
    The returned proposal's ``strategy`` is re-tagged by the calling policy.
    """
    return _NEAREST.generate_merge_proposal(engine)


def random_pair(engine: Any, rng: random.Random, strategy: str) -> Optional[MergeProposal]:
    """Two distinct clusters chosen uniformly at random via the seeded ``rng``."""
    clusters = list(engine.clusters)
    if len(clusters) < 2:
        return None
    a, b = rng.sample(clusters, 2)
    return make_proposal(engine, a.id, b.id, strategy)


def oldest_pair(engine: Any, strategy: str) -> Optional[MergeProposal]:
    """The two oldest surviving clusters (lowest monotonic ids).

    Cluster ids are assigned from a monotonic counter, so the two smallest ids
    are the two earliest-created clusters still alive — a FIFO-by-birth rule.
    """
    clusters = sorted(engine.clusters, key=lambda c: c.id)
    if len(clusters) < 2:
        return None
    return make_proposal(engine, clusters[0].id, clusters[1].id, strategy)


def lowest_utility_pair(engine: Any, strategy: str) -> Optional[MergeProposal]:
    """The two least-used clusters (lowest access-frequency ``count``).

    ``Cluster.count`` is the number of vectors that have been assigned to the
    cluster — a direct proxy for its utility / activation frequency. Ties are
    broken by id (older first) so selection stays deterministic.
    """
    clusters = sorted(engine.clusters, key=lambda c: (c.count, c.id))
    if len(clusters) < 2:
        return None
    return make_proposal(engine, clusters[0].id, clusters[1].id, strategy)


__all__ = [
    "AcceptVerdict",
    "PolicyContext",
    "ConsolidationPolicy",
    "MergeProposal",
    "DecisionScore",
    "make_proposal",
    "nearest_pair",
    "random_pair",
    "oldest_pair",
    "lowest_utility_pair",
]
