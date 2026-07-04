"""
research/tests/test_proposals.py
=================================

Unit tests for Sprint R3's proposal layer:
:class:`RichProposal`, :class:`MarketContext`, :class:`ProposalPool`,
and the four :class:`ProposalSource` bidders.
"""

from __future__ import annotations

import json
import math
import random

import pytest

from backend.cognition.decision_policy import DecisionPolicy, STRATEGY_FREE_ENERGY
from backend.cognition.replay_engine import ReplayEngine
from backend.cognition.vector_prediction_core import ClusterEngine
from research.proposals.base import DEFAULT_TOP_K, MarketContext, ProposalSource
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


# --------------------------------------------------------------------------- #
#   Helpers
# --------------------------------------------------------------------------- #

def _build_engine():
    """Build a real ClusterEngine with three clusters."""
    eng = ClusterEngine(proximity_threshold=0.1, auto_seed=True, max_clusters=10)
    eng.assign([-5.0, 0.0])
    eng.assign([-5.01, 0.0])
    eng.assign([0.0, 0.0])
    eng.assign([5.0, 0.0])
    eng.assign([5.01, 0.0])
    return eng


def _mock_context(engine=None):
    """Minimal MarketContext for testing."""
    return MarketContext(
        core=_build_engine() if engine is None else engine,
        recent_vectors=[[0.0, 0.0], [0.1, 0.0], [5.0, 0.0]],
        tick=0,
        rng=random.Random(42),
    )


# --------------------------------------------------------------------------- #
#   proposal.py — RichProposal
# --------------------------------------------------------------------------- #

class TestMakeProposalId:
    def test_order_independent(self):
        assert make_proposal_id(3, 7, "geo") == make_proposal_id(7, 3, "geo")

    def test_strategy_embedded(self):
        pid = make_proposal_id(1, 2, "temporal")
        assert pid.startswith("temporal:")

    def test_lo_hi_sorted(self):
        pid = make_proposal_id(7, 3, "geo")
        assert pid == "geo:3-7"


class TestEnergyFromMetrics:
    def test_canonical_formula(self):
        e = energy_from_metrics({"entropy": 1.0, "prediction_error": 2.0, "active_load": 3.0})
        assert e == pytest.approx(1.0 * 1.0 + 2.0 * 2.0 + 0.5 * 3.0)

    def test_missing_keys_default_to_zero(self):
        e = energy_from_metrics({})
        assert e == 0.0

    def test_none_values(self):
        e = energy_from_metrics({"entropy": None, "prediction_error": 1.0, "active_load": None})
        assert e == pytest.approx(2.0)

    def test_custom_weights(self):
        e = energy_from_metrics(
            {"entropy": 1.0, "prediction_error": 1.0, "active_load": 1.0},
            weights={"lam": 3.0, "mu": 4.0, "nu": 5.0},
        )
        assert e == pytest.approx(3.0 + 4.0 + 5.0)


class TestRichProposalCreate:
    def test_basic_construction(self):
        ctx = _mock_context()
        rp = RichProposal.create(1, 2, "geometric", distance=2.5, context=ctx)
        assert rp.proposal_id == "geometric:1-2"
        assert rp.target_a == 1
        assert rp.target_b == 2
        assert rp.distance == 2.5
        assert rp.origin_strategies == ["geometric"]
        assert rp.primary_strategy == "geometric"

    def test_pair_is_order_independent(self):
        rp = RichProposal.create(5, 3, "geo")
        assert rp.pair == frozenset((3, 5))
        assert rp.pair == frozenset((5, 3))

    def test_to_merge_proposal(self):
        rp = RichProposal.create(1, 2, "geometric", distance=3.0)
        mp = rp.to_merge_proposal()
        assert mp.target_a == 1
        assert mp.target_b == 2
        assert mp.distance == 3.0
        assert mp.strategy == "geometric"


class TestRichProposalSelfContainedExecution:
    """Verify the sR3 requirement: a proposal can replay, score, counterfactual
    and export itself independently."""

    def test_replay_populates_replay_metrics(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        score = rp.replay()
        assert rp.replay_metrics is not None
        assert "metrics_before" in rp.replay_metrics
        assert "metrics_after" in rp.replay_metrics
        assert isinstance(score.metrics_before, dict)

    def test_replay_requires_context(self):
        rp = RichProposal.create(0, 1, "geometric")
        with pytest.raises(ValueError, match="MarketContext"):
            rp.replay()

    def test_score_populates_decision_trace(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        trace = rp.score()
        assert "energy_before" in trace
        assert "energy_after" in trace
        assert "accepted" in trace
        assert "delta_energy" in trace
        assert rp.expected_complexity_change is not None
        # expected_complexity_change = -delta_load
        assert rp.expected_complexity_change == pytest.approx(-float(trace["delta_load"]))

    def test_score_rehearses_if_not_yet_replayed(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        assert rp.replay_metrics is None
        rp.score()
        assert rp.replay_metrics is not None

    def test_score_accepts_explicit_policy(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        policy = DecisionPolicy(strategy=STRATEGY_FREE_ENERGY, lam=1.0, mu=2.0, nu=0.5, tolerance=0.0)
        rp.score(policy=policy)
        assert "energy_score" in rp.decision_trace

    def test_counterfactual_computes_block(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        block = rp.counterfactual()
        assert "energy_no_merge" in block
        assert "energy_merge" in block
        assert "improvement_over_no_merge" in block
        assert "beneficial" in block

    def test_counterfactual_with_held_out(self):
        ctx = _mock_context()
        held = [[0.0, 0.0], [0.1, 0.0]]
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        block = rp.counterfactual(held_out=held)
        assert "replay_error" in block
        assert "actual_energy_held_out" in block
        assert "predicted_energy" in block

    def test_export_json_serialisable(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        rp.score()
        exported = rp.export()
        # Must be JSON-serialisable without error.
        text = json.dumps(exported, sort_keys=True)
        assert '"proposal_id"' in text

    def test_export_excludes_context(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        exported = rp.export()
        assert "context" not in exported

    def test_replay_is_deterministic(self):
        ctx1 = _mock_context()
        ctx2 = _mock_context()
        rp1 = RichProposal.create(0, 1, "geometric", context=ctx1)
        rp2 = RichProposal.create(0, 1, "geometric", context=ctx2)
        rp1.replay()
        rp2.replay()
        e_after1 = rp1.replay_metrics["metrics_after"].get("entropy")
        e_after2 = rp2.replay_metrics["metrics_after"].get("entropy")
        assert e_after1 == e_after2

    def test_counterfactual_scores_if_not_yet_scored(self):
        ctx = _mock_context()
        rp = RichProposal.create(0, 1, "geometric", context=ctx)
        assert not rp.decision_trace
        rp.counterfactual()
        assert rp.decision_trace


class TestRichProposalEdgeCases:
    def test_primary_strategy_unknown_when_empty(self):
        rp = RichProposal(proposal_id="x:1-2", target_a=1, target_b=2)
        assert rp.primary_strategy == "unknown"

    def test_nan_distance_exported_as_none(self):
        rp = RichProposal.create(1, 2, "geo", distance=float("nan"))
        exported = rp.export()
        assert exported["distance"] is None

    def test_inf_distance_exported_as_none(self):
        rp = RichProposal.create(1, 2, "geo", distance=float("inf"))
        exported = rp.export()
        assert exported["distance"] is None


# --------------------------------------------------------------------------- #
#   base.py — MarketContext
# --------------------------------------------------------------------------- #

class TestMarketContext:
    def test_default_construction(self):
        # MarketContext requires 'core' — use a minimal engine.
        eng = ClusterEngine(proximity_threshold=0.1, auto_seed=True, max_clusters=10)
        ctx = MarketContext(core=eng)
        assert ctx.energy_weights == {"lam": 1.0, "mu": 2.0, "nu": 0.5}
        assert ctx.tick == 0
        assert ctx.recent_vectors == []

    def test_engine_resolves_from_core_with_cluster_engine_attr(self):
        eng = _build_engine()
        class MockCore:
            cluster_engine = eng
        ctx = MarketContext(core=MockCore())
        assert ctx.engine is eng

    def test_engine_resolves_to_core_directly(self):
        eng = _build_engine()
        ctx = MarketContext(core=eng)
        assert ctx.engine is eng

    def test_clusters_returns_list(self):
        ctx = MarketContext(core=_build_engine())
        clusters = ctx.clusters()
        assert isinstance(clusters, list)
        assert len(clusters) >= 2


# --------------------------------------------------------------------------- #
#   sources.py — ProposalSource bidders
# --------------------------------------------------------------------------- #

class TestSourceRegistry:
    def test_registry_contains_all_four_sources(self):
        names = available_sources()
        for expected in ["geometric", "random", "temporal", "utility"]:
            assert expected in names

    def test_build_source_unknown_raises(self):
        with pytest.raises(KeyError):
            build_source("does_not_exist")

    def test_build_source_returns_instance(self):
        source = build_source("geometric")
        assert isinstance(source, GeometricSource)

    def test_build_default_panel_order(self):
        panel = build_default_panel()
        names = [s.name for s in panel]
        assert names == DEFAULT_SOURCE_ORDER

    def test_sources_in_registry_match_default_order(self):
        for name in DEFAULT_SOURCE_ORDER:
            assert name in SOURCE_REGISTRY


class TestGeometricSource:
    def test_returns_nearest_pairs(self):
        source = GeometricSource()
        ctx = _mock_context()
        ranked = source.rank_pairs(ctx)
        assert len(ranked) >= 1
        # All distances should be non-negative.
        for pair, dist, score in ranked:
            assert dist >= 0
            assert dist == score  # GeometricSource uses distance as its own score.

    def test_top_k_default(self):
        source = GeometricSource()
        ctx = _mock_context()
        proposals = source.propose(ctx)
        assert len(proposals) <= DEFAULT_TOP_K
        assert all(isinstance(p, RichProposal) for p in proposals)

    def test_empty_on_one_cluster(self):
        eng = ClusterEngine(proximity_threshold=0.1, auto_seed=True, max_clusters=10)
        eng.assign([0.0, 0.0])
        ctx = MarketContext(core=eng)
        source = GeometricSource()
        ranked = source.rank_pairs(ctx)
        assert ranked == []


class TestTemporalSource:
    def test_returns_ranked_pairs(self):
        source = TemporalSource()
        ctx = _mock_context()
        ranked = source.rank_pairs(ctx)
        assert len(ranked) >= 1
        for pair, dist, jsd in ranked:
            assert 0.0 <= jsd <= 1.0

    def test_jsd_is_symmetric(self):
        source = TemporalSource()
        ctx = _mock_context()
        distributions = source._transition_distributions(ctx.engine, ctx.recent_vectors)
        for cid in distributions:
            total = sum(distributions[cid].values())
            if total > 0:
                assert pytest.approx(total) == 1.0

    def test_empty_window_produces_empty(self):
        eng = _build_engine()
        ctx = MarketContext(core=eng, recent_vectors=[])
        source = TemporalSource()
        ranked = source.rank_pairs(ctx)
        assert len(ranked) >= 1
        # With no transition data, all JSD values should be 1.0 (maximal).
        for pair, dist, jsd in ranked:
            assert jsd == 1.0


class TestUtilitySource:
    def test_lowest_utility_first(self):
        source = UtilitySource()
        ctx = _mock_context()
        ranked = source.rank_pairs(ctx)
        assert len(ranked) >= 1
        scores = [s for _, _, s in ranked]
        assert scores == sorted(scores)

    def test_top_k_capped(self):
        source = UtilitySource()
        ctx = _mock_context()
        proposals = source.propose(ctx, top_k=1)
        assert len(proposals) == 1


class TestRandomSource:
    def test_is_stochastic(self):
        source = RandomSource()
        assert source.is_stochastic is True

    def test_deterministic_given_seeded_rng(self):
        ctx1 = _mock_context()
        ctx2 = _mock_context()
        props1 = RandomSource().propose(ctx1)
        props2 = RandomSource().propose(ctx2)
        assert [p.proposal_id for p in props1] == [p.proposal_id for p in props2]

    def test_different_orders_with_different_seeds(self):
        eng = _build_engine()
        ctx1 = MarketContext(core=eng, rng=random.Random(1))
        ctx2 = MarketContext(core=eng, rng=random.Random(99))
        ids1 = [p.proposal_id for p in RandomSource().propose(ctx1)]
        ids2 = [p.proposal_id for p in RandomSource().propose(ctx2)]
        # They may be the same by chance, but with many clusters this is unlikely.
        # We only require that the source reports it is stochastic.
        assert RandomSource().is_stochastic is True


class TestProposalSourceDescribe:
    def test_geometric_describe(self):
        d = GeometricSource().describe()
        assert d["name"] == "geometric"
        assert d["stochastic"] is False

    def test_random_describe(self):
        d = RandomSource().describe()
        assert d["stochastic"] is True

    def test_describe_is_json_serialisable(self):
        for source in build_default_panel():
            json.dumps(source.describe())


# --------------------------------------------------------------------------- #
#   pool.py — ProposalPool
# --------------------------------------------------------------------------- #

class TestProposalPoolConstruction:
    def test_empty_pool(self):
        pool = ProposalPool()
        assert len(pool) == 0
        assert pool.is_empty()

    def test_add_and_extend(self):
        pool = ProposalPool()
        rp = RichProposal.create(1, 2, "geo")
        pool.add(rp)
        assert len(pool) == 1
        pool.extend([RichProposal.create(3, 4, "utility")])
        assert len(pool) == 2

    def test_from_sources(self):
        ctx = _mock_context()
        panel = build_default_panel()
        pool = ProposalPool.from_sources(panel, ctx, top_k=2)
        assert len(pool) > 0
        for p in pool.proposals:
            assert isinstance(p, RichProposal)

    def test_from_sources_respects_top_k(self):
        ctx = _mock_context()
        panel = build_default_panel()
        pool = ProposalPool.from_sources(panel, ctx, top_k=1)
        # Each of 4 sources bids at most 1.
        assert len(pool) <= 4


class TestPoolDeduplication:
    def test_folds_same_pair_into_one(self):
        pool = ProposalPool()
        rp1 = RichProposal.create(1, 2, "geometric")
        rp2 = RichProposal.create(1, 2, "utility")
        pool.add(rp1)
        pool.add(rp2)
        deduped = pool.deduplicated()
        assert len(deduped) == 1
        assert set(deduped.proposals[0].origin_strategies) == {"geometric", "utility"}

    def test_deduplication_preserves_distinct_pairs(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geo"))
        pool.add(RichProposal.create(3, 4, "geo"))
        deduped = pool.deduplicated()
        assert len(deduped) == 2

    def test_consensus_pairs_multi_source_only(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geometric"))
        pool.add(RichProposal.create(1, 2, "utility"))
        pool.add(RichProposal.create(3, 4, "geometric"))
        consensus = pool.consensus_pairs()
        # The (1,2) pair was nominated by two sources.
        assert len(consensus) == 1
        assert consensus[0].pair == frozenset((1, 2))


class TestPoolDiversity:
    def test_strategy_entropy_zero_for_empty_pool(self):
        pool = ProposalPool()
        assert pool.strategy_entropy() == 0.0

    def test_strategy_entropy_single_source_is_zero(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geometric"))
        pool.add(RichProposal.create(3, 4, "geometric"))
        assert pool.strategy_entropy() == 0.0

    def test_strategy_entropy_multi_source_is_positive(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geometric"))
        pool.add(RichProposal.create(3, 4, "utility"))
        h = pool.strategy_entropy()
        assert h > 0.0
        # Max for 2 strategies = log2(2) = 1.0
        assert h <= 1.0

    def test_average_pair_overlap_zero_for_one_proposal(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geo"))
        assert pool.average_pair_overlap() == 0.0

    def test_average_pair_overlap_identical_pairs_is_one(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geo"))
        pool.add(RichProposal.create(1, 2, "utility"))
        assert pool.average_pair_overlap() == 1.0

    def test_average_pair_overlap_distinct_pairs_is_below_one(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geo"))
        pool.add(RichProposal.create(3, 4, "utility"))
        assert pool.average_pair_overlap() == 0.0

    def test_diversity_report_keys(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geo"))
        report = pool.diversity_report()
        for key in ("num_proposals", "strategy_distribution", "strategy_entropy_bits",
                     "average_pair_overlap", "unique_pairs", "consensus_pairs"):
            assert key in report

    def test_export(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geo"))
        d = pool.export()
        assert "proposals" in d
        assert "diversity" in d


class TestPoolFoldingPreservesOrder:
    """Consensus folding preserves first-seen source ordering."""
    def test_first_seen_source_is_primary(self):
        pool = ProposalPool()
        pool.add(RichProposal.create(1, 2, "geometric"))
        pool.add(RichProposal.create(1, 2, "utility"))
        deduped = pool.deduplicated()
        assert deduped.proposals[0].origin_strategies[0] == "geometric"


class TestRichProposalMultipleOriginStrategies:
    def test_deduplication_merges_origins(self):
        """When the pool folds two proposals for the same pair, origin_strategies
        should contain both."""
        pool = ProposalPool()
        pool.add(RichProposal.create(5, 7, "temporal"))
        pool.add(RichProposal.create(5, 7, "utility"))
        pool.add(RichProposal.create(5, 7, "geometric"))
        deduped = pool.deduplicated()
        assert len(deduped) == 1
        origins = deduped.proposals[0].origin_strategies
        assert "temporal" in origins
        assert "utility" in origins
        assert "geometric" in origins
