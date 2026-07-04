"""
research/proposals/pool.py
==========================

The :class:`ProposalPool` — the collected bids of every
:class:`~research.proposals.base.ProposalSource` for one consolidation step,
plus the **quantitative diversity** measures the R3 spec requires.

Two diversity numbers describe how heterogeneous a pool is:

* **Strategy entropy** ``H(strategy)`` — the Shannon entropy (bits) of the
  distribution of proposals across originating strategies. ``0`` when every
  proposal came from one source; maximal (``log2 k``) when the ``k`` sources are
  evenly represented. High entropy ⇒ the market is considering structurally
  different ideas, not ``k`` restatements of the same heuristic.

* **Average pair overlap** — the mean Jaccard overlap of the ``{a, b}`` target
  sets across every unordered pair of proposals. ``1.0`` when all proposals name
  the same cluster pair (total redundancy); ``0.0`` when no two proposals share
  a cluster (maximally spread). The complement of diversity.

When two sources independently nominate the *same* cluster pair, the pool can
fold them into a single proposal whose ``origin_strategies`` lists both — that
consensus is itself a useful signal, surfaced by :meth:`consensus_pairs`.

Standard library only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from research.proposals.proposal import RichProposal


@dataclass
class ProposalPool:
    """A collection of :class:`RichProposal` bids with diversity diagnostics."""

    proposals: List[RichProposal] = field(default_factory=list)

    # -- construction ------------------------------------------------------

    def add(self, proposal: RichProposal) -> None:
        """Append a single proposal to the pool."""
        self.proposals.append(proposal)

    def extend(self, proposals: Iterable[RichProposal]) -> None:
        """Append many proposals to the pool."""
        self.proposals.extend(proposals)

    @classmethod
    def from_sources(
        cls, sources: Iterable[Any], context: Any, *, top_k: int = 2
    ) -> "ProposalPool":
        """Build a pool by soliciting ``top_k`` bids from each source."""
        pool = cls()
        for source in sources:
            pool.extend(source.propose(context, top_k=top_k))
        return pool

    # -- size --------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.proposals)

    def is_empty(self) -> bool:
        """Whether the pool holds no proposals."""
        return not self.proposals

    # -- consensus folding -------------------------------------------------

    def deduplicated(self) -> "ProposalPool":
        """A new pool with same-pair proposals folded into one.

        The surviving proposal keeps the union of ``origin_strategies`` (in
        first-seen order) so a consensus pair records every source that backed
        it. Distance metadata is taken from the first occurrence.
        """
        by_pair: Dict[frozenset, RichProposal] = {}
        for p in self.proposals:
            existing = by_pair.get(p.pair)
            if existing is None:
                merged = RichProposal.create(
                    p.target_a,
                    p.target_b,
                    p.primary_strategy,
                    distance=p.distance,
                    context=p.context,
                )
                merged.origin_strategies = list(p.origin_strategies)
                by_pair[p.pair] = merged
            else:
                for strat in p.origin_strategies:
                    if strat not in existing.origin_strategies:
                        existing.origin_strategies.append(strat)
        return ProposalPool(proposals=list(by_pair.values()))

    def consensus_pairs(self) -> List[RichProposal]:
        """Folded proposals nominated by more than one source (best consensus)."""
        deduped = self.deduplicated().proposals
        consensus = [p for p in deduped if len(p.origin_strategies) > 1]
        consensus.sort(key=lambda p: (-len(p.origin_strategies), p.proposal_id))
        return consensus

    # -- quantitative diversity -------------------------------------------

    def strategy_distribution(self) -> Dict[str, int]:
        """Count of proposals contributed per originating strategy.

        Each proposal contributes one count to *every* strategy in its
        ``origin_strategies``, so a folded consensus proposal is counted once
        under each of its backing sources.
        """
        counts: Dict[str, int] = {}
        for p in self.proposals:
            for strat in (p.origin_strategies or ["unknown"]):
                counts[strat] = counts.get(strat, 0) + 1
        return counts

    def strategy_entropy(self) -> float:
        """Shannon entropy ``H(strategy)`` of the strategy distribution, in bits.

        ``0.0`` for an empty pool or a pool drawn from a single strategy.
        """
        counts = self.strategy_distribution()
        total = sum(counts.values())
        if total <= 0:
            return 0.0
        entropy = 0.0
        for c in counts.values():
            if c <= 0:
                continue
            p = c / total
            entropy -= p * math.log2(p)
        # Guard tiny negative floating-point noise.
        return entropy if entropy > 0.0 else 0.0

    def average_pair_overlap(self) -> float:
        """Mean Jaccard overlap of target sets across all proposal pairs.

        Returns ``0.0`` when the pool holds fewer than two proposals (no pair to
        compare). A pool of identical pairs yields ``1.0``.
        """
        n = len(self.proposals)
        if n < 2:
            return 0.0
        total = 0.0
        count = 0
        for i in range(n):
            set_i = self.proposals[i].pair
            for j in range(i + 1, n):
                set_j = self.proposals[j].pair
                union = set_i | set_j
                if not union:
                    overlap = 0.0
                else:
                    overlap = len(set_i & set_j) / len(union)
                total += overlap
                count += 1
        return total / count if count else 0.0

    def diversity_report(self) -> Dict[str, Any]:
        """JSON-safe bundle of the pool's diversity diagnostics."""
        return {
            "num_proposals": len(self.proposals),
            "strategy_distribution": self.strategy_distribution(),
            "strategy_entropy_bits": self.strategy_entropy(),
            "average_pair_overlap": self.average_pair_overlap(),
            "unique_pairs": len({p.pair for p in self.proposals}),
            "consensus_pairs": [p.proposal_id for p in self.consensus_pairs()],
        }

    # -- serialisation -----------------------------------------------------

    def export(self) -> Dict[str, Any]:
        """A JSON-safe snapshot of every proposal plus the diversity report."""
        return {
            "proposals": [p.export() for p in self.proposals],
            "diversity": self.diversity_report(),
        }


__all__ = ["ProposalPool"]
