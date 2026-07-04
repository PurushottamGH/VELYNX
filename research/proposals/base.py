"""
research/proposals/base.py
==========================

The shared contracts for Sprint R3's proposal layer: the read-only
:class:`MarketContext` and the abstract :class:`ProposalSource`.

Design contract
---------------
A *proposal source* answers exactly one question: *given the current world,
which cluster merges are worth considering?* It returns at most
:data:`DEFAULT_TOP_K` ( = 2) :class:`~research.proposals.proposal.RichProposal`
candidates, ranked by its own criterion. It never replays, scores, commits, or
mutates anything — generation and evaluation are cleanly separated, exactly as
the frozen :class:`~backend.cognition.candidate_generator.CandidateGenerator`
separates proposal from mutation.

Why a "market" context
-----------------------
The R3 evaluator is a *counterfactual merge market*: several heterogeneous
sources bid candidate merges into a pool, and an evaluator picks a winner. The
:class:`MarketContext` is the single read-only bundle of world state every
bidder (and every self-contained proposal) needs:

* ``core``            — the live prediction core / cluster engine (read-only).
* ``recent_vectors``  — the replay window used to measure every proposal
                        identically (the comparability guarantee).
* ``energy_weights``  — the ``{lam, mu, nu}`` free-energy coefficients.
* ``rng``             — the single seeded randomness source (stochastic sources
                        draw only from here, for reproducibility).
* ``tick``            — the dataset tick the bidding is happening at.
* ``held_out_vectors``— optional seed-disjoint window for replay-fidelity.

Standard library only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Tuple

import random

from research.proposals.proposal import RichProposal

#: Every source returns at most this many candidates (the R3 ``top-k`` cap).
DEFAULT_TOP_K = 2


@dataclass
class MarketContext:
    """Read-only world state handed to every proposal source and proposal.

    Attributes
    ----------
    core :
        The live prediction core (exposing ``.cluster_engine``) or a bare
        :class:`~backend.cognition.vector_prediction_core.ClusterEngine`.
        Treated as strictly read-only by sources; only a *deepcopy* clone is
        ever mutated downstream.
    recent_vectors :
        The recent-observation window every proposal is rehearsed against.
    energy_weights :
        ``{"lam", "mu", "nu"}`` free-energy coupling coefficients.
    rng :
        The single deterministic randomness source for stochastic sources.
    tick :
        The dataset tick at which proposals are being solicited.
    held_out_vectors :
        Optional held-out (seed-disjoint) window for replay-error measurement.
    """

    core: Any
    recent_vectors: List[List[float]] = field(default_factory=list)
    energy_weights: Dict[str, float] = field(
        default_factory=lambda: {"lam": 1.0, "mu": 2.0, "nu": 0.5}
    )
    rng: random.Random = field(default_factory=random.Random)
    tick: int = 0
    held_out_vectors: Optional[List[List[float]]] = None

    @property
    def engine(self) -> Any:
        """Resolve the backing cluster engine (``.cluster_engine`` or bare)."""
        engine = getattr(self.core, "cluster_engine", None)
        return engine if engine is not None else self.core

    def clusters(self) -> List[Any]:
        """The live clusters (read-only snapshot as a list)."""
        return list(getattr(self.engine, "clusters", []))


class ProposalSource(ABC):
    """A heterogeneous bidder that nominates candidate merges into the market.

    Concrete sources set the class attribute :attr:`name` and implement
    :meth:`rank_pairs`, returning ``(pair, distance, score)`` tuples in
    *best-first* order. The base class turns the top ``k`` of those into
    :class:`RichProposal` objects, so every source shares identical
    proposal-construction and ``top-k`` capping logic.
    """

    #: Registry key / strategy tag (e.g. ``"geometric"``). Set on subclasses.
    name: ClassVar[str] = "abstract"

    #: One-line human description, surfaced in manifests/logs.
    description: ClassVar[str] = "Abstract proposal source."

    #: Whether ranking consults the context RNG (only ``RandomSource``).
    is_stochastic: ClassVar[bool] = False

    @abstractmethod
    def rank_pairs(
        self, context: MarketContext
    ) -> List[Tuple[Tuple[int, int], float, float]]:
        """Rank candidate cluster pairs best-first.

        Returns
        -------
        list of ((target_a, target_b), distance, score)
            ``distance`` is the centroid Euclidean distance (trace metadata);
            ``score`` is this source's own ranking criterion (already sorted so
            the best candidate is first). May be empty when fewer than two
            clusters exist.
        """
        raise NotImplementedError

    def propose(
        self, context: MarketContext, *, top_k: int = DEFAULT_TOP_K
    ) -> List[RichProposal]:
        """Return up to ``top_k`` :class:`RichProposal` candidates, best-first."""
        ranked = self.rank_pairs(context)
        proposals: List[RichProposal] = []
        seen: set = set()
        for (a, b), distance, _score in ranked:
            if a == b:
                continue
            key = frozenset((a, b))
            if key in seen:
                continue
            seen.add(key)
            proposals.append(
                RichProposal.create(
                    a, b, self.name, distance=distance, context=context
                )
            )
            if len(proposals) >= top_k:
                break
        return proposals

    def describe(self) -> Dict[str, Any]:
        """JSON-safe self-description for the experiment manifest."""
        return {
            "name": self.name,
            "description": self.description,
            "class": type(self).__name__,
            "module": type(self).__module__,
            "stochastic": self.is_stochastic,
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"{type(self).__name__}(name={self.name!r})"


__all__ = [
    "DEFAULT_TOP_K",
    "MarketContext",
    "ProposalSource",
    "RichProposal",
]
