"""
research/tests/test_attribution.py
===================================

Unit tests for Sprint R3's attribution layer:
:class:`CounterfactualMergeEvaluator`, :class:`CounterfactualEvaluator`,
:class:`AttributionLogger`, :class:`AttributionRunner`, and
:mod:`research.attribution.metrics`.
"""

from __future__ import annotations

import json
import math
import os
import random

import pytest

from research.attribution.counterfactual import CounterfactualEvaluator, CounterfactualResult
from research.attribution.evaluator import CounterfactualMergeEvaluator, EvaluatorResult
from research.attribution.logger import AttributionLogger, WindowRecord
from research.attribution.metrics import (
    aggregate_attribution,
    strategy_attribution_counts,
    top_k_accuracy,
)
from research.attribution.runner import (
    AttributionConfig,
    AttributionRunner,
    run_attribution,
)
from research.proposals.base import MarketContext
from research.proposals.pool import ProposalPool
from research.proposals.proposal import RichProposal
from research.proposals.sources import (
    build_default_panel,
    GeometricSource,
    UtilitySource,
)


# --------------------------------------------------------------------------- #
#   Helpers
# --------------------------------------------------------------------------- #

from backend.cognition.vector_prediction_core import ClusterEngine


def _build_engine():
    """Build a real ClusterEngine with three clusters."""
    eng = ClusterEngine(proximity_threshold=0.1, auto_seed=True, max_clusters=10)
    eng.assign([-5.0, 0.0])
    eng.assign([-5.01, 0.0])
    eng.assign([0.0, 0.0])
    eng.assign([5.0, 0.0])
    eng.assign([5.01, 0.0])
    return eng


def _context_with_proposals(engine=None):
    """Build a market context and a scored pool of proposals."""
    eng = engine or _build_engine()
    ctx = MarketContext(
        core=eng,
        recent_vectors=[[-5.0, 0.0], [0.0, 0.0], [5.0, 0.0]],
        tick=42,
        rng=random.Random(42),
    )

    geo = GeometricSource()
    util = UtilitySource()
    pool = ProposalPool()
    for source in [geo, util]:
        props = source.propose(ctx, top_k=2)
        pool.extend(props)

    # Score every proposal.
    for p in pool.proposals:
        p.score()

    return ctx, pool


# --------------------------------------------------------------------------- #
#   evaluator.py — CounterfactualMergeEvaluator
# --------------------------------------------------------------------------- #

class TestMergeEvaluator:
    def test_evaluates_pool_and_returns_winner(self):
        _, pool = _context_with_proposals()
        evaluator = CounterfactualMergeEvaluator()
        result = evaluator.evaluate(pool)
        assert result.total_scored > 0
        assert result.accepted_count >= 0
        assert isinstance(result.pool_diversity, dict)

    def test_winner_is_among_accepted(self):
        _, pool = _context_with_proposals()
        evaluator = CounterfactualMergeEvaluator()
        result = evaluator.evaluate(pool)
        if result.winner is not None:
            assert result.winner.decision_trace["accepted"] is True

    def test_rankings_annotated_with_rank_and_margin(self):
        _, pool = _context_with_proposals()
        evaluator = CounterfactualMergeEvaluator()
        result = evaluator.evaluate(pool)
        for p in result.rankings:
            assert "rank" in p.decision_trace
            assert "margin" in p.decision_trace
            assert "energy_score" in p.decision_trace
            assert p.decision_trace["rank"] >= 1
            if p.decision_trace["rank"] < result.total_scored:
                assert p.decision_trace["margin"] is not None

    def test_rankings_sorted_by_energy_ascending(self):
        _, pool = _context_with_proposals()
        evaluator = CounterfactualMergeEvaluator()
        result = evaluator.evaluate(pool)
        energies = [
            p.decision_trace["energy_after"] for p in result.rankings
        ]
        assert energies == sorted(energies)

    def test_empty_pool_returns_no_winner(self):
        evaluator = CounterfactualMergeEvaluator()
        result = evaluator.evaluate(ProposalPool())
        assert result.winner is None
        assert result.total_scored == 0
        assert result.accepted_count == 0

    def test_evaluator_result_as_dict(self):
        _, pool = _context_with_proposals()
        evaluator = CounterfactualMergeEvaluator()
        result = evaluator.evaluate(pool)
        d = result.as_dict()
        assert "rankings" in d
        assert "winner_id" in d
        json.dumps(d)  # must be serialisable.

    def test_rankings_are_deterministic(self):
        eng1 = _build_engine()
        eng2 = _build_engine()
        ctx1, pool1 = _context_with_proposals(eng1)
        ctx2, pool2 = _context_with_proposals(eng2)
        r1 = CounterfactualMergeEvaluator().evaluate(pool1)
        r2 = CounterfactualMergeEvaluator().evaluate(pool2)
        ids1 = [p.proposal_id for p in r1.rankings]
        ids2 = [p.proposal_id for p in r2.rankings]
        assert ids1 == ids2


# --------------------------------------------------------------------------- #
#   counterfactual.py — CounterfactualEvaluator
# --------------------------------------------------------------------------- #

class TestCounterfactualEvaluator:
    def test_evaluates_pool_and_identifies_best(self):
        _, pool = _context_with_proposals()
        evaluator = CounterfactualEvaluator()
        result = evaluator.evaluate(pool.proposals)
        assert result.proposals_evaluated == len(pool.proposals)
        assert result.counterfactual_best is not None
        assert result.no_merge_energy is not None

    def test_every_proposal_has_counterfactual_block(self):
        _, pool = _context_with_proposals()
        CounterfactualEvaluator().evaluate(pool.proposals)
        for p in pool.proposals:
            assert p.counterfactual_block is not None
            assert "energy_no_merge" in p.counterfactual_block
            assert "energy_merge" in p.counterfactual_block

    def test_every_proposal_has_pareto_annotation(self):
        _, pool = _context_with_proposals()
        CounterfactualEvaluator().evaluate(pool.proposals)
        for p in pool.proposals:
            assert "is_pareto_optimal" in p.decision_trace
            assert isinstance(p.decision_trace["is_pareto_optimal"], bool)

    def test_pareto_frontier_non_empty(self):
        _, pool = _context_with_proposals()
        result = CounterfactualEvaluator().evaluate(pool.proposals)
        assert len(result.pareto_frontier) >= 1

    def test_empty_proposals_returns_empty(self):
        result = CounterfactualEvaluator().evaluate([])
        assert result.proposals_evaluated == 0
        assert result.counterfactual_best is None

    def test_with_held_out_computes_replay_error(self):
        _, pool = _context_with_proposals()
        held = [[0.0, 0.0], [0.1, 0.0], [5.0, 0.0]]
        evaluator = CounterfactualEvaluator(held_out_vectors=held)
        result = evaluator.evaluate(pool.proposals)
        for p in pool.proposals:
            ct = p.counterfactual_block or {}
            assert "replay_error" in ct
            assert ct["replay_error"] is not None

    def test_counterfactual_result_as_dict(self):
        _, pool = _context_with_proposals()
        result = CounterfactualEvaluator().evaluate(pool.proposals)
        d = result.as_dict()
        assert "counterfactual_best_id" in d
        assert "pareto_frontier" in d
        json.dumps(d)

    def test_counterfactual_is_deterministic(self):
        eng1 = _build_engine()
        eng2 = _build_engine()
        ctx1, pool1 = _context_with_proposals(eng1)
        ctx2, pool2 = _context_with_proposals(eng2)
        r1 = CounterfactualEvaluator().evaluate(pool1.proposals)
        r2 = CounterfactualEvaluator().evaluate(pool2.proposals)
        assert r1.best_id() == r2.best_id()
        assert r1.pareto_frontier == r2.pareto_frontier


# --------------------------------------------------------------------------- #
#   metrics.py — Top-K accuracy and attribution stats
# --------------------------------------------------------------------------- #

class TestTopKAccuracy:
    def test_in_top_k(self):
        assert top_k_accuracy("geo:1-2", ["geo:1-2", "util:3-4", "temp:5-6"], k=3) is True

    def test_not_in_top_k(self):
        assert top_k_accuracy("geo:1-2", ["a", "b", "c"], k=3) is False

    def test_none_selected_returns_none(self):
        assert top_k_accuracy(None, ["a", "b", "c"]) is None

    def test_empty_ranking(self):
        assert top_k_accuracy("id", []) is False

    def test_ranking_shorter_than_k(self):
        assert top_k_accuracy("geo:1-2", ["geo:1-2"], k=3) is True


class TestStrategyAttributionCounts:
    def test_counts_per_strategy(self):
        ids = ["geo:1-2", "geo:3-4", "util:5-6"]
        counts = strategy_attribution_counts(ids)
        assert counts["geo"] == 2
        assert counts["util"] == 1

    def test_empty_list(self):
        assert strategy_attribution_counts([]) == {}

    def test_unknown_no_colon(self):
        counts = strategy_attribution_counts(["something"])
        assert counts["unknown"] == 1


class TestAggregateAttribution:
    def test_basic_aggregation(self):
        windows = [
            {
                "winner_id": "geo:1-2",
                "counterfactual_best_id": "geo:1-2",
                "counterfactual_ranking": ["geo:1-2", "util:3-4", "temp:5-6"],
                "winner_is_pareto_optimal": True,
                "avg_replay_error": 0.1,
            },
            {
                "winner_id": "geo:3-4",
                "counterfactual_best_id": "util:1-2",
                "counterfactual_ranking": ["util:1-2", "geo:3-4"],
                "winner_is_pareto_optimal": False,
                "avg_replay_error": 0.2,
            },
        ]
        summary = aggregate_attribution(windows)
        assert summary.num_windows == 2
        assert summary.top_k_hit_count == 2  # first is position 0, second is position 1 (both < 3)
        assert summary.top_k_hit_rate == 1.0
        assert summary.avg_replay_error == pytest.approx(0.15)
        assert summary.pareto_coverage_rate == 0.5

    def test_empty_windows(self):
        summary = aggregate_attribution([])
        assert summary.num_windows == 0
        assert summary.top_k_hit_rate is None

    def test_summary_as_dict(self):
        windows = [{
            "winner_id": "geo:1-2",
            "counterfactual_best_id": "geo:1-2",
            "counterfactual_ranking": ["geo:1-2"],
            "winner_is_pareto_optimal": True,
            "avg_replay_error": None,
        }]
        summary = aggregate_attribution(windows)
        d = summary.as_dict()
        json.dumps(d)  # serialisable.
        assert d["num_windows"] == 1


# --------------------------------------------------------------------------- #
#   logger.py — AttributionLogger
# --------------------------------------------------------------------------- #

class TestAttributionLogger:
    def test_writes_jsonl_and_manifest(self, tmp_path):
        out = str(tmp_path / "attribution")
        logger = AttributionLogger(output_dir=out, config={"seed": 42})
        assert os.path.isdir(logger.run_dir)

        # Log a window.
        _, pool = _context_with_proposals()
        me = CounterfactualMergeEvaluator()
        ce = CounterfactualEvaluator()
        eval_result = me.evaluate(pool)
        cf_result = ce.evaluate(pool.proposals)
        record = WindowRecord(
            window_index=0,
            tick=100,
            evaluator=eval_result,
            counterfactual=cf_result,
            is_top_k_correct=True,
            winner_is_pareto_optimal=True,
        )
        logger.log_window(record)
        logger.write_manifest()
        logger.close()

        # Verify JSONL exists and has one line.
        with open(logger.jsonl_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        assert len(lines) == 1
        obj = json.loads(lines[0])
        assert obj["window_index"] == 0
        assert obj["tick"] == 100

        # Verify manifest.
        with open(logger.manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        assert manifest["sprint"] == "R3"
        assert "reproducibility" in manifest
        assert "git_commit" in manifest["reproducibility"]
        assert "python_version" in manifest["reproducibility"]
        assert "platform" in manifest["reproducibility"]
        assert "config_hash" in manifest["reproducibility"]
        assert "code_hash" in manifest["reproducibility"]
        assert "summary" in manifest
        assert manifest["num_windows"] == 1

    def test_logger_context_manager(self, tmp_path):
        out = str(tmp_path / "ctx")
        _, pool = _context_with_proposals()
        me = CounterfactualMergeEvaluator()
        ce = CounterfactualEvaluator()
        eval_result = me.evaluate(pool)
        cf_result = ce.evaluate(pool.proposals)

        with AttributionLogger(output_dir=out, config={}) as logger:
            logger.log_window(WindowRecord(
                window_index=0, tick=0,
                evaluator=eval_result,
                counterfactual=cf_result,
            ))
        # After __exit__, manifest should exist.
        assert os.path.isfile(logger.manifest_path)

    def test_empty_log_manifest(self, tmp_path):
        out = str(tmp_path / "empty")
        logger = AttributionLogger(output_dir=out, config={})
        logger.write_manifest()
        logger.close()
        with open(logger.manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        assert manifest["num_windows"] == 0

    def test_source_descriptions_in_manifest(self, tmp_path):
        out = str(tmp_path / "sources")
        panel = build_default_panel()
        logger = AttributionLogger(output_dir=out, config={}, sources=panel)
        logger.write_manifest()
        logger.close()
        with open(logger.manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
        assert len(manifest["source_panel"]) == len(panel)
        for entry in manifest["source_panel"]:
            assert "name" in entry
            assert "class" in entry


# --------------------------------------------------------------------------- #
#   runner.py — AttributionRunner
# --------------------------------------------------------------------------- #

class TestAttributionRunner:
    def test_runs_small_experiment(self, tmp_path):
        """Run a small-scale experiment (fast) and verify output."""
        out = str(tmp_path / "runner")
        config = AttributionConfig(
            noise_sigma=0.01,
            seed=1,
            num_ticks=2000,
            replay_horizon=200,
            proximity_threshold=0.28,
            max_clusters=50,
            output_dir=out,
        )
        runner = AttributionRunner(config)
        result = runner.run()
        assert result.num_windows >= 0
        assert result.runtime_seconds > 0
        assert os.path.isdir(result.logger.run_dir)
        assert os.path.isfile(result.logger.manifest_path)

    def test_result_contains_summary(self, tmp_path):
        out = str(tmp_path / "summary")
        config = AttributionConfig(
            noise_sigma=0.01, seed=2, num_ticks=2000,
            replay_horizon=200, max_clusters=50, output_dir=out,
        )
        result = AttributionRunner(config).run()
        assert "num_windows" in result.summary
        assert "merges_committed" in result.summary
        assert "runtime_seconds" in result.summary

    def test_config_as_dict_roundtrip(self):
        config = AttributionConfig(seed=7, noise_sigma=0.1)
        d = config.as_dict()
        assert d["seed"] == 7
        assert d["noise_sigma"] == 0.1
        json.dumps(d)

    def test_run_attribution_convenience(self, tmp_path):
        out = str(tmp_path / "conv")
        result = run_attribution(
            noise_sigma=0.01, seed=5, num_ticks=2000,
            replay_horizon=200, max_clusters=50, output_dir=out,
        )
        assert result.num_windows >= 0

    def test_deterministic_given_same_config(self, tmp_path):
        out1 = str(tmp_path / "det1")
        out2 = str(tmp_path / "det2")
        config = AttributionConfig(
            noise_sigma=0.01, seed=42, num_ticks=2000,
            replay_horizon=200, max_clusters=50, output_dir=out1,
        )
        r1 = AttributionRunner(config).run()
        config2 = AttributionConfig(
            noise_sigma=0.01, seed=42, num_ticks=2000,
            replay_horizon=200, max_clusters=50, output_dir=out2,
        )
        r2 = AttributionRunner(config2).run()
        assert r1.num_windows == r2.num_windows
        assert r1.merges_committed == r2.merges_committed

    def test_with_held_out_seed(self, tmp_path):
        out = str(tmp_path / "held")
        config = AttributionConfig(
            noise_sigma=0.15, seed=1, num_ticks=2000,
            replay_horizon=200, max_clusters=50,
            held_out_seed=1000001, held_out_ticks=50,
            output_dir=out,
        )
        result = AttributionRunner(config).run()
        assert os.path.isfile(result.logger.manifest_path)
        # If windows were produced, the JSONL should include replay errors.
        if result.num_windows > 0:
            with open(result.logger.jsonl_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    obj = json.loads(line)
                    errors = obj.get("replay_errors_per_proposal", {})
                    if errors:
                        assert any(v is not None for v in errors.values())
                        break


# --------------------------------------------------------------------------- #
#   WindowRecord
# --------------------------------------------------------------------------- #

class TestWindowRecord:
    def test_to_jsonl_roundtrip(self):
        _, pool = _context_with_proposals()
        me = CounterfactualMergeEvaluator()
        ce = CounterfactualEvaluator()
        eval_result = me.evaluate(pool)
        cf_result = ce.evaluate(pool.proposals)
        record = WindowRecord(
            window_index=5, tick=200,
            evaluator=eval_result,
            counterfactual=cf_result,
            is_top_k_correct=True,
            winner_is_pareto_optimal=False,
        )
        j = record.to_jsonl()
        assert j["window_index"] == 5
        assert j["tick"] == 200
        assert "counterfactual_ranking_ids" in j
        assert "replay_errors_per_proposal" in j
        json.dumps(j)


# --------------------------------------------------------------------------- #
#   Integration: Full pipeline
# --------------------------------------------------------------------------- #

class TestAttributionPipeline:
    """Smoke-tests the complete R3 pipeline: sources -> pool -> evaluator ->
    counterfactual -> logger."""

    def test_full_pipeline_via_runner(self, tmp_path):
        out = str(tmp_path / "full")
        result = run_attribution(
            noise_sigma=0.01, seed=99, num_ticks=2000,
            replay_horizon=200, max_clusters=50, output_dir=out,
        )
        # Read back a line of JSONL if any windows were produced.
        if result.num_windows > 0:
            with open(result.logger.jsonl_path, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
            if lines:
                first = json.loads(lines[0])
                assert "evaluator_result" in first
                assert "counterfactual_result" in first
                assert "pool_diversity" in first
                assert "strategy_entropy_bits" in first["pool_diversity"]
                assert "winner_id" in first["evaluator_result"]
                assert "counterfactual_best_id" in first
        else:
            # At minimum, the manifest must exist.
            assert os.path.isfile(result.logger.manifest_path)

    def test_manifest_has_all_required_fields(self, tmp_path):
        out = str(tmp_path / "manifest")
        result = run_attribution(
            noise_sigma=0.01, seed=1, num_ticks=100,
            replay_horizon=40, max_clusters=10, output_dir=out,
        )
        with open(result.logger.manifest_path, "r", encoding="utf-8") as fh:
            m = json.load(fh)
        for key in ("sprint", "experiment", "schema_version", "reproducibility",
                     "configuration", "source_panel", "summary", "num_windows",
                     "artifacts"):
            assert key in m, f"Missing key: {key}"
        for rkey in ("git_commit", "python_version", "platform", "config_hash", "code_hash"):
            assert rkey in m["reproducibility"], f"Missing reproducibility key: {rkey}"
