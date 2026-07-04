"""
research/proposals
==================

**Research Sprint R3 — the proposal layer of the Counterfactual Merge Market.**

A heterogeneous panel of :class:`ProposalSource` bidders nominates candidate
cluster merges (each capped at ``top-k = 2``) into a :class:`ProposalPool`,
where every candidate is a *self-contained, executable* :class:`RichProposal`
that can rehearse, score, counterfactually analyse and serialise itself against
a read-only :class:`MarketContext`.

Nothing in this package mutates any frozen cognition component; sources are
strictly read-only and proposals only ever mutate a ``deepcopy`` sandbox.

Standard library only. Python 3.11+.
"""

from __future__ import annotations

from research.proposals.base import (
    DEFAULT_TOP_K,
    MarketContext,
    ProposalSource,
)
from research.proposals.pool import ProposalPool
from research.proposals.proposal import (
    DEFAULT_ENERGY_WEIGHTS,
    RichProposal,
    energy_from_metrics,
    make_proposal_id,
)
from research.proposals.sources import (
    DEFAULT_SOURCE_ORDER,
    SOURCE_REGISTRY,
    GeometricSource,
    RandomSource,
    TemporalSource,
    UtilitySource,
    available_sources,
    build_default_panel,
    build_source,
)

__all__ = [
    "DEFAULT_TOP_K",
    "MarketContext",
    "ProposalSource",
    "RichProposal",
    "ProposalPool",
    "energy_from_metrics",
    "make_proposal_id",
    "DEFAULT_ENERGY_WEIGHTS",
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
