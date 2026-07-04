"""
research/attribution/runner.py
===============================

The :class:`AttributionRunner` — the R3 end-to-end experiment orchestrator.

Drives the same scheduler→propose→replay→commit loop as the production
runner and the :class:`~research.runner.ResearchRunner`, but interleaves
the proposal-market layer and the counterfactual evaluator at each
consolidation trigger:

1. Build the dataset and cognitive monitor (seeded, reproducible).
2. At each consolidation trigger:
   a. Solicit top-k=2 bids from every source into a :class:`ProposalPool`.
   b. Score and rank all proposals via :class:`CounterfactualMergeEvaluator`.
   c. Select the winner (``argmin energy_after`` among accepted) and commit
      it to the live engine.
   d. Run the :class:`CounterfactualEvaluator` on the scored pool (with an
      optional held-out window for replay-error measurement).
   e. Log the window record.
3. After all ticks, generate the manifest and export results.

The decision policy (``FreeEnergyPolicy``, the R3 treatment) is exercised
by the :class:`CounterfactualMergeEvaluator`'s selection rule, which is
**identical**: ``argmin energy_after`` among accepted proposals.

Standard library only.
"""

from __future__ import annotations

import os
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.cognition.decision_policy import resolve_coefficients
from backend.cognition.memory_scheduler import MemoryScheduler
from backend.cognition.replay_engine import ReplayEngine
from validation.datasets import build_dataset
from validation.monitor import VectorMonitor

from research.attribution.counterfactual import CounterfactualEvaluator
from research.attribution.evaluator import CounterfactualMergeEvaluator
from research.attribution.logger import AttributionLogger, WindowRecord
from research.attribution.metrics import top_k_accuracy
from research.proposals.base import DEFAULT_TOP_K, MarketContext
from research.proposals.pool import ProposalPool
from research.proposals.sources import DEFAULT_SOURCE_ORDER, build_default_panel
from research.proposals.base import ProposalSource

from research.runner import DEFAULT_REPLAY_HORIZON, MAX_MERGES_PER_CYCLE


@dataclass
class AttributionConfig:
    """The complete, reproducible specification of one attribution experiment.

    Attributes
    ----------
    noise_sigma : Sensor-noise std-dev.
    seed : Master seed (deterministic runs).
    num_ticks : Number of dataset ticks to drive.
    replay_horizon : Size of the recent-vector window (default 200).
    proximity_threshold : Cluster-engine proximity threshold.
    max_clusters : Max clusters before compression.
    dataset_name : Dataset key (default ``"environment"``).
    decision_policy : Free-energy coupling ``{"lam","mu","nu"}``.
    source_order : Which proposal sources to use and in what order.
    top_k : Max bids per source (default 2).
    held_out_seed : Optional separate seed for a held-out replay-accuracy
        window. When provided, the ``CounterfactualEvaluator`` computes
        ``replay_error`` for every proposal.
    held_out_ticks : Number of ticks in the held-out window (when applicable).
    output_dir : Directory for attribution artifacts.
    """

    noise_sigma: float = 0.05
    seed: int = 1
    num_ticks: int = 5000
    replay_horizon: int = DEFAULT_REPLAY_HORIZON
    proximity_threshold: float = 0.28
    max_clusters: int = 50
    dataset_name: str = "environment"
    decision_policy: Dict[str, float] = field(default_factory=dict)
    source_order: List[str] = field(default_factory=lambda: list(DEFAULT_SOURCE_ORDER))
    top_k: int = DEFAULT_TOP_K
    held_out_seed: Optional[int] = None
    held_out_ticks: int = 200
    output_dir: str = "research_artifacts"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "noise_sigma": self.noise_sigma,
            "seed": self.seed,
            "num_ticks": self.num_ticks,
            "replay_horizon": self.replay_horizon,
            "proximity_threshold": self.proximity_threshold,
            "max_clusters": self.max_clusters,
            "dataset_name": self.dataset_name,
            "decision_policy": dict(self.decision_policy),
            "source_order": list(self.source_order),
            "top_k": self.top_k,
            "held_out_seed": self.held_out_seed,
            "held_out_ticks": self.held_out_ticks,
            "output_dir": self.output_dir,
        }


@dataclass
class AttributionResult:
    """Everything an attribution experiment produces."""

    config: AttributionConfig
    logger: AttributionLogger
    num_windows: int = 0
    merges_committed: int = 0
    runtime_seconds: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)


class AttributionRunner:
    """Drive the R3 counterfactual merge evaluation experiment.

    Parameters
    ----------
    config : The experiment configuration.
    """

    def __init__(self, config: AttributionConfig) -> None:
        self.config = config
        self.energy_weights = resolve_coefficients(config.decision_policy)

    def run(self) -> AttributionResult:
        """Execute the full experiment and return the result."""
        cfg = self.config

        # -- build the world + mind -----------------------------------------
        dataset = build_dataset(
            cfg.dataset_name, seed=cfg.seed, noise_sigma=cfg.noise_sigma
        )
        monitor = VectorMonitor(
            proximity_threshold=cfg.proximity_threshold,
            max_clusters=cfg.max_clusters,
            decision_policy_weights=self.energy_weights,
        )
        scheduler = MemoryScheduler(monitor)
        replay = ReplayEngine()
        policy_rng = random.Random(cfg.seed)
        recent = deque(maxlen=cfg.replay_horizon)

        # -- build the proposal sources ------------------------------------
        sources: List[ProposalSource] = build_default_panel()
        # Filter to requested order if specified.
        if set(cfg.source_order) != set(DEFAULT_SOURCE_ORDER):
            from research.proposals.sources import build_source
            sources = [build_source(name) for name in cfg.source_order]

        # -- evaluators ----------------------------------------------------
        market_evaluator = CounterfactualMergeEvaluator(
            free_energy_weights=self.energy_weights,
        )

        # Build held-out window if requested.
        held_out_window: Optional[List[List[float]]] = None
        if cfg.held_out_seed is not None:
            held_dataset = build_dataset(
                cfg.dataset_name, seed=cfg.held_out_seed, noise_sigma=cfg.noise_sigma
            )
            held_out_window = [
                held_dataset.get_next_tick() for _ in range(cfg.held_out_ticks)
            ]

        counterfactual_eval = CounterfactualEvaluator(
            held_out_vectors=held_out_window,
        )

        # -- logger --------------------------------------------------------
        logger = AttributionLogger(
            output_dir=cfg.output_dir,
            config=cfg.as_dict(),
            sources=sources,
        )

        # -- main loop -----------------------------------------------------
        merges_committed = 0
        window_index = 0
        t_start = time.perf_counter()

        for tick_num in range(cfg.num_ticks):
            vector = dataset.get_next_tick()
            recent.append(vector)
            monitor.tick(vector)

            if scheduler.tick():
                # --- Phase 1: solicit proposals from all sources ----------
                context = MarketContext(
                    core=monitor.cluster_engine,
                    recent_vectors=list(recent),
                    energy_weights=self.energy_weights,
                    rng=policy_rng,
                    tick=tick_num,
                    held_out_vectors=held_out_window,
                )
                pool = ProposalPool.from_sources(sources, context, top_k=cfg.top_k)

                if pool.is_empty():
                    scheduler.reset()
                    continue

                # --- Phase 2: score, rank, select winner -----------------
                eval_result = market_evaluator.evaluate(pool)

                # --- Phase 3: post-hoc counterfactual evaluation ----------
                cf_result = counterfactual_eval.evaluate(pool.proposals)

                # --- Phase 4: compute top-K accuracy and Pareto check -----
                # Counterfactual ranking: proposals sorted best-first by
                # actual_energy_held_out (or energy_after fallback).
                ranked_ids = [
                    p.proposal_id
                    for p in sorted(
                        pool.proposals,
                        key=lambda p: (
                            (p.counterfactual_block or {}).get("actual_energy_held_out")
                            or (p.counterfactual_block or {}).get("energy_merge")
                            or float("inf")
                        ),
                    )
                ]

                winner_id = eval_result.winner_id()
                is_top_k = top_k_accuracy(winner_id, ranked_ids, k=3)
                is_pareto = (
                    eval_result.winner.decision_trace.get("is_pareto_optimal", False)
                    if eval_result.winner
                    else None
                )

                # --- Phase 5: commit the winner ---------------------------
                if eval_result.winner is not None:
                    winner = eval_result.winner
                    try:
                        replay.commit_proposal(
                            monitor.cluster_engine,
                            winner.to_merge_proposal(),
                        )
                        merges_committed += 1
                    except Exception:
                        # Commit may fail if targets no longer exist.
                        pass

                    # Drain quarantine (mirrors production loop).
                    engine = monitor.cluster_engine
                    records = getattr(engine, "anomaly_records", None)
                    reingest = getattr(engine, "reingest_quarantined", None)
                    if records and reingest:
                        active_ids = [
                            r.id
                            for r in list(records)
                            if getattr(r, "status", None) == "active"
                        ]
                        for rid in active_ids:
                            reingest(rid)

                # --- Phase 6: log the window ------------------------------
                record = WindowRecord(
                    window_index=window_index,
                    tick=tick_num,
                    evaluator=eval_result,
                    counterfactual=cf_result,
                    is_top_k_correct=is_top_k,
                    winner_is_pareto_optimal=is_pareto,
                )
                logger.log_window(record)
                window_index += 1

                scheduler.reset()

        # -- finalise -------------------------------------------------------
        runtime = time.perf_counter() - t_start
        logger.write_manifest()
        logger.close()

        # Build the summary.
        summary = {
            "num_windows": window_index,
            "merges_committed": merges_committed,
            "runtime_seconds": runtime,
            "output_dir": logger.run_dir,
        }

        return AttributionResult(
            config=cfg,
            logger=logger,
            num_windows=window_index,
            merges_committed=merges_committed,
            runtime_seconds=runtime,
            summary=summary,
        )


def run_attribution(
    *,
    noise_sigma: float = 0.05,
    seed: int = 1,
    num_ticks: int = 5000,
    held_out_seed: Optional[int] = None,
    output_dir: str = "research_artifacts",
    **kwargs: Any,
) -> AttributionResult:
    """Convenience: build and execute an attribution experiment."""
    config = AttributionConfig(
        noise_sigma=noise_sigma,
        seed=seed,
        num_ticks=num_ticks,
        held_out_seed=held_out_seed,
        output_dir=output_dir,
        **kwargs,
    )
    return AttributionRunner(config).run()


__all__ = [
    "AttributionConfig",
    "AttributionResult",
    "AttributionRunner",
    "run_attribution",
]
