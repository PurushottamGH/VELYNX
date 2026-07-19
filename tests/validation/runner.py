"""
validation/runner.py
=====================

Experiment execution harness for the VELYNX Cognitive Lab.

``BenchmarkRunner`` sits between a :class:`~validation.interfaces.Dataset`
(a tick-by-tick source of sensory vectors) and a duck-typed monitor (anything
with a ``tick(vector) -> dict`` interface that returns prediction/surprise/
regime information). It drives the loop, collects a structured log, and is
built for deterministic replay, memory safety at 10,000+ ticks, and graceful
degradation when the monitor is absent.

Design
------
* **Loop, not orchestration** -- this file owns the tight inner ``for _ in
  range(num_ticks)``. It does not decide *which* dataset or *which* monitor
  or *which* metrics to run; those are wired in by the caller.
* **Log, not DB** -- every tick produces a lean dict that is appended to
  :attr:`output_log`. The log is an ordinary Python ``list``, not a database,
  so it stays trivial to inspect, serialize, or pass to a
  :class:`~validation.interfaces.Metric`.
* **Bounded memory** -- :attr:`output_log` may be capped by
  ``max_log_size``. Above that cap the runner issues a warning and trims
  the oldest entries, keeping memory flat even on very long runs.
* **Safe defaults** -- a ``None`` monitor logs ``Vector`` fields and sets
  prediction/surprise/regime to ``None`` without crashing. A failed tick
  (exception in ``monitor.tick()``) is caught per-tick, logged as an error
  entry, and the loop continues.
"""

from __future__ import annotations

import json
import logging
import os
import time
import warnings
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from backend.cognition.candidate_generator import CandidateGenerator
from backend.cognition.consolidation_tracker import ConsolidationTracker
from backend.cognition.decision_policy import DecisionPolicy
from backend.cognition.memory_scheduler import MemoryScheduler
from backend.cognition.replay_engine import ReplayEngine
from validation.interfaces import Dataset, Vector

logger = logging.getLogger("velynx.runner")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_MAX_LOG_SIZE = 50_000
"""Hard cap on the number of log entries before the oldest are trimmed.

50 000 entries × ~500 bytes/entry ≈ 25 MB, which is well within comfortable
working memory for a research script. Tune via ``config["max_log_size"]``.
"""

_LOG_TRIM_TARGET = 40_000
"""When the log exceeds ``max_log_size``, trim back to this many entries."""

_MAX_MERGES_PER_CYCLE = 3
"""Structural merge budget per triggered sleep cycle (C8 control upgrade).

A single scheduler trigger may commit at most this many merges. Each committed
merge reorganizes memory and is immediately followed by a quarantine-queue
drain; once the budget is spent the cycle terminates and the scheduler resets.
Bounding committed merges keeps any one sleep cycle's structural churn (and the
drains it spawns) finite, regardless of how much pressure accumulated.
"""

_RECENT_VECTORS_MAXLEN = 200
"""Size of the short-term memory buffer (C8.3).

The :class:`~backend.cognition.replay_engine.ReplayEngine` validates a merge
proposal by replaying the most recent observations through both the live brain
and a sandbox. This rolling window of the last ``200`` vectors is that
validation set — large enough to be representative of the current regime, small
enough that the read-only replay stays cheap even on very long runs.
"""


# ---------------------------------------------------------------------------
# Log entry shape
# ---------------------------------------------------------------------------

_LOG_TEMPLATE = ("tick", "vector", "prediction", "surprise", "regime")
"""Every log entry will have at least these keys."""


def _build_entry(
    tick: int,
    vector: Vector,
    tick_result: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build a single log entry from the tick result.

    If ``tick_result`` is ``None`` (monitor absent or tick failed) the
    entry's prediction / surprise / regime fields are ``None`` so callers
    can distinguish a silent tick from a genuine zero-surprise event.
    """
    entry: Dict[str, Any] = {
        "tick": tick,
        "vector": vector,
        "prediction": None,
        "surprise": None,
        "regime": None,
    }
    if tick_result is not None:
        # Pull known keys from the monitor's dict; leave missing keys as None
        # so we never crash on a slightly different monitor shape.
        entry["prediction"] = tick_result.get("prediction")
        entry["surprise"] = tick_result.get("surprise")
        entry["regime"] = tick_result.get("regime")
    return entry


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


@dataclass
class BenchmarkRunner:
    """Drive a :class:`Dataset` through a cognitive monitor.

    Typical usage::

        runner = BenchmarkRunner(dataset=my_ds, monitor=my_monitor)
        summary = runner.run_experiment({"num_ticks": 5_000})
        for entry in runner.output_log:
            print(entry["tick"], entry["surprise"], entry["regime"])

    The same runner can be re-used for multiple experiments; each call to
    :meth:`run_experiment` resets the dataset and (optionally) clears the log.
    """

    dataset: Dataset
    """A reproducible tick source."""

    monitor: Any = None
    """A duck-typed monitor with a ``tick(vector) -> dict`` interface.

    The returned dict should contain at least ``"prediction"``,
    ``"surprise"``, and ``"regime"`` keys. If ``None``, the runner logs
    partial entries (those fields are ``None``) and does not call ``tick()``.
    """

    output_log: list = field(default_factory=list)
    """Collected log entries from the most recent experiment run.

    Each entry is a dict with keys ``tick``, ``vector``, ``prediction``,
    ``surprise``, and ``regime``.  Cleared at the start of every
    :meth:`run_experiment` call.
    """

    recent_vectors: "deque[Vector]" = field(
        default_factory=lambda: deque(maxlen=_RECENT_VECTORS_MAXLEN)
    )
    """Short-term memory buffer of the most recent observed vectors (C8.3).

    A bounded rolling window (``maxlen=200``) that every incoming vector is
    appended to during the tick loop. It is the validation set the
    :class:`~backend.cognition.replay_engine.ReplayEngine` replays through both
    the live brain and the sandbox when scoring a merge proposal, so the
    Commit/Rollback decision is made against the regime the brain is *currently*
    experiencing rather than its entire history.
    """

    consolidation_tracker: ConsolidationTracker = field(
        default_factory=ConsolidationTracker
    )
    """Pure-observability counters + traces for the C8 consolidation pipeline.

    Reset at the start of every :meth:`run_experiment` so each run's counts are
    independent. The runner increments these counters as it drives the
    scheduler → propose → replay → commit state machine, but the tracker never
    feeds back into any of those decisions — it only observes them.
    """

    policy_weights: Optional[Dict[str, float]] = None
    """Externalised free-energy coupling coefficients for the DecisionPolicy.

    A ``{"lam", "mu", "nu"}`` mapping resolved from the experiment's
    ``decision_policy`` config section by
    :func:`backend.cognition.decision_policy.resolve_coefficients`. When
    ``None`` the runner constructs a default :class:`DecisionPolicy`
    (``(1.0, 2.0, 0.5)``), preserving historical behaviour. This is the only
    knob the orchestrator turns to run an energy-coefficient ablation sweep.
    """

    decision_audit: list = field(default_factory=list)
    """Structured decision-trace log for the C8 *decision audit* artifact (Task 2).

    One entry is appended for **every** merge proposal evaluated during the run
    (accepted or rejected), each a JSON-safe dict with keys ``tick``,
    ``targets``, ``accepted``, ``prediction_delta``, ``entropy_delta``,
    ``load_delta``, ``energy_delta`` and ``reason``. Cleared at the start of
    every :meth:`run_experiment`. Persisted to ``decision_audit.json`` via
    :meth:`write_decision_audit`. Pure observability — never read back by the
    cognitive path.
    """

    # -- public API --------------------------------------------------------

    def run_experiment(
        self,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the monitor against every tick from the dataset.

        Parameters
        ----------
        config : dict or None
            Supported keys:

            * **num_ticks** (``int``, default ``1000``) --
              How many ticks to consume from the dataset.
            * **reset_dataset** (``bool``, default ``True``) --
              Call ``dataset.reset()`` before starting.
            * **max_log_size** (``int``, default ``50_000``) --
              Hard cap on ``output_log`` entries.
            * **clear_log** (``bool``, default ``True``) --
              Wipe ``output_log`` before the run.

        Returns
        -------
        dict
            A summary dict with keys:

            * ``ticks`` -- number of ticks processed
            * ``duration`` -- wall-clock seconds
            * ``ticks_per_second`` -- throughput
            * ``entries_collected`` -- final size of ``output_log``
            * ``errors`` -- number of ticks where ``monitor.tick()`` raised
            * ``regime_counts`` -- ``{regime_name: count}`` across the log
        """
        # -- resolve config ------------------------------------------------
        cfg = self._resolve_config(config)
        num_ticks: int = cfg["num_ticks"]
        max_log_size: int = cfg["max_log_size"]

        # -- reset state ---------------------------------------------------
        if cfg["clear_log"]:
            self.output_log.clear()
            # The short-term replay buffer is per-run state too: clearing it
            # keeps each experiment's Commit/Rollback decisions independent and
            # the replay deterministic.
            self.recent_vectors.clear()
            # Consolidation counters/traces are per-run observability state.
            self.consolidation_tracker = ConsolidationTracker()
            # The decision-audit trace log is per-run observability state too.
            self.decision_audit = []

        if cfg["reset_dataset"]:
            self.dataset.reset()

        # -- autonomous memory scheduling ----------------------------------
        # The scheduler reads memory telemetry through the monitor's
        # ``get_memory_summary()`` surface. It is only useful when a monitor
        # exposing that surface is present; otherwise scheduling is skipped.
        scheduler: Optional[MemoryScheduler] = None
        candidate_generator: Optional[CandidateGenerator] = None
        replay_engine: Optional[ReplayEngine] = None
        decision_policy: Optional[DecisionPolicy] = None
        if self.monitor is not None and hasattr(self.monitor, "get_memory_summary"):
            scheduler = MemoryScheduler(self.monitor)
            candidate_generator = CandidateGenerator()
            replay_engine = ReplayEngine()
            # The principled successor to the binary acceptance check: the
            # ReplayEngine now only *measures* (returns a DecisionScore), and the
            # DecisionPolicy renders the accept/reject verdict from the brain's
            # native cognitive vitals (default: Free Energy Minimization). This
            # is wholly independent of the external RegressionGate CI check.
            #
            # The (lam, mu, nu) energy coupling coefficients are no longer
            # hard-coded here: they are injected via ``policy_weights`` (resolved
            # from the experiment's ``decision_policy`` config section). When
            # absent, DecisionPolicy falls back to its (1.0, 2.0, 0.5) defaults.
            decision_policy = DecisionPolicy(**(self.policy_weights or {}))

        # -- run loop ------------------------------------------------------
        errors = 0
        start = time.perf_counter()

        for tick_num in range(num_ticks):
            # 1. Read the next sensory vector from the dataset.
            try:
                vector: Vector = self.dataset.get_next_tick()
            except Exception:
                # If the dataset itself fails, there is nothing to log.
                # Re-raise immediately -- a broken dataset cannot produce
                # meaningful results.
                raise RuntimeError(
                    f"Dataset.get_next_tick() failed at tick {tick_num}"
                ) from None

            # 1a. Record the vector in the short-term memory buffer. This
            #     rolling window is what the ReplayEngine rehearses a proposed
            #     merge against, so it must capture *every* observation.
            self.recent_vectors.append(vector)

            # 2. Forward the vector to the monitor (if present).
            tick_result: Optional[Dict[str, Any]] = None
            if self.monitor is not None:
                try:
                    tick_result = self.monitor.tick(vector)
                except Exception:
                    # A single tick failure is not fatal. Log what we can
                    # and continue.
                    errors += 1
                    tick_result = None

            # 3. Build and store the log entry.
            entry = _build_entry(tick_num, vector, tick_result)

            if len(self.output_log) >= max_log_size:
                # Trim oldest entries to keep memory bounded.
                self.output_log = self.output_log[-_LOG_TRIM_TARGET:]
                warnings.warn(
                    f"output_log reached {max_log_size} entries at tick "
                    f"{tick_num}; trimmed to {_LOG_TRIM_TARGET}."
                )

            self.output_log.append(entry)

            # 4. Ask the memory scheduler whether a sleep cycle is due. On a
            #    trigger we run a budgeted C8 consolidation cycle: repeatedly
            #    propose a merge, rehearse it in a sandbox against the
            #    short-term buffer, and Commit/Roll back on the verdict. Each
            #    committed merge is immediately followed by a quarantine-queue
            #    drain (re-ingesting anomalies into the reorganized clusters)
            #    *before* the next dataset vector is fetched. The cycle stops
            #    after _MAX_MERGES_PER_CYCLE commits, a rejection, or when no
            #    proposal remains, then the scheduler is reset (arming cooldown).
            if scheduler is not None and scheduler.tick():
                # OBSERVE: the scheduler signalled a sleep cycle.
                self.consolidation_tracker.record_scheduler_trigger()
                logger.info(
                    "SLEEP CYCLE TRIGGERED: Memory consolidation required"
                )
                live_cluster_engine = self.monitor.cluster_engine

                committed_this_cycle = 0
                while committed_this_cycle < _MAX_MERGES_PER_CYCLE:
                    proposal = candidate_generator.generate_merge_proposal(
                        live_cluster_engine
                    )
                    if proposal is None:
                        # Fewer than two clusters remain: nothing left to fuse.
                        break

                    # OBSERVE: a concrete merge proposal was produced.
                    self.consolidation_tracker.record_proposal()
                    logger.info(
                        "PROPOSAL GENERATED: Strategy=%s targets=(%s, %s) "
                        "distance=%.4f",
                        proposal.strategy,
                        proposal.target_a,
                        proposal.target_b,
                        proposal.distance,
                    )

                    # Rehearse the proposal in an isolated sandbox, measuring
                    # the brain's native cognitive vitals (H, S, A) in both the
                    # live (pre-merge) and sandbox (post-merge) worlds. The
                    # engine renders no verdict — it only returns a DecisionScore.
                    replay_window = list(self.recent_vectors)
                    score = replay_engine.simulate_proposal(
                        live_cluster_engine,
                        proposal,
                        replay_window,
                    )
                    # OBSERVE: one sandbox rehearsal + the vectors it replayed.
                    self.consolidation_tracker.record_replay_evaluation(
                        queue_size=len(replay_window)
                    )

                    # DECIDE: the DecisionPolicy judges the merge from the vitals
                    # (Free Energy Minimization by default). This is the
                    # principled replacement for the old binary
                    # ``sandbox_error <= original_error`` acceptance check, and
                    # is independent of the external RegressionGate CI compiler.
                    verdict = decision_policy.evaluate_metrics(
                        score.metrics_before, score.metrics_after
                    )
                    accepted = verdict["accepted"]
                    logger.info(
                        "REPLAY: accepted=%s strategy=%s "
                        "ΔPrediction=%+.4f ΔEntropy=%+.4f ΔLoad=%+.4f "
                        "ΔEnergy=%+.4f reason=%r",
                        accepted,
                        verdict["strategy"],
                        verdict["delta_prediction"],
                        verdict["delta_entropy"],
                        verdict["delta_load"],
                        verdict["delta_energy"],
                        verdict["reason"],
                    )

                    # OBSERVE: persist a structured trace of every decision
                    # component — the four vital deltas, the before/after energy,
                    # and the explicit structural reason for the verdict.
                    self.consolidation_tracker.record_trace(
                        {
                            "tick": tick_num,
                            "strategy": proposal.strategy,
                            "target_a": proposal.target_a,
                            "target_b": proposal.target_b,
                            "distance": proposal.distance,
                            "accepted": accepted,
                            "decision_strategy": verdict["strategy"],
                            "delta_prediction": verdict["delta_prediction"],
                            "delta_entropy": verdict["delta_entropy"],
                            "delta_load": verdict["delta_load"],
                            "delta_energy": verdict["delta_energy"],
                            "energy_before": verdict["energy_before"],
                            "energy_after": verdict["energy_after"],
                            "prediction_before": verdict["prediction_before"],
                            "prediction_after": verdict["prediction_after"],
                            "entropy_before": verdict["entropy_before"],
                            "entropy_after": verdict["entropy_after"],
                            "load_before": verdict["load_before"],
                            "load_after": verdict["load_after"],
                            "reason": verdict["reason"],
                            "queue_size": len(replay_window),
                            "merge_index": committed_this_cycle,
                        }
                    )

                    # AUDIT (Task 2): append a JSON-safe decision trace for
                    # *every* evaluated proposal — the exact schema the
                    # decision_audit.json artifact requires. ``targets`` is the
                    # ordered pair of fused cluster ids; the four ``*_delta``
                    # fields are the signed (before − after) vital improvements.
                    self.decision_audit.append(
                        {
                            "tick": tick_num,
                            "targets": [proposal.target_a, proposal.target_b],
                            "accepted": accepted,
                            "prediction_delta": verdict["delta_prediction"],
                            "entropy_delta": verdict["delta_entropy"],
                            "load_delta": verdict["delta_load"],
                            "energy_delta": verdict["delta_energy"],
                            "reason": verdict["reason"],
                        }
                    )

                    if not accepted:
                        # OBSERVE: rejected verdict.
                        self.consolidation_tracker.record_rejection()
                        # ── Rollback ────────────────────────────────────────
                        # The merge would have raised global free energy (or was
                        # strictly dominated); leave the live brain untouched.
                        # The CandidateGenerator deterministically re-proposes
                        # the same closest pair, so re-looping would spin forever
                        # — end the cycle here.
                        logger.info(
                            "ROLLBACK: proposal rejected (%s), ending cycle",
                            verdict["reason"],
                        )
                        break

                    # OBSERVE: accepted verdict. Fold this merge's signed vital
                    # deltas into the tracker's running sums so the final
                    # AVERAGE ACCEPTED DELTAS dashboard can report the mean ΔS,
                    # ΔH, ΔA and ΔE across every accepted merge (Task 3).
                    self.consolidation_tracker.record_acceptance(
                        delta_prediction=verdict["delta_prediction"],
                        delta_entropy=verdict["delta_entropy"],
                        delta_load=verdict["delta_load"],
                        delta_energy=verdict["delta_energy"],
                    )
                    # ── Commit ──────────────────────────────────────────────
                    # The DecisionPolicy judged the merge beneficial for global
                    # stability (lower/equal free energy, or not Pareto-
                    # dominated), so apply the identical merge to the live
                    # ClusterEngine. Fusing two clusters into one frees a
                    # slot in the max_clusters budget.
                    replay_engine.commit_proposal(live_cluster_engine, proposal)
                    # OBSERVE: merge applied to the live engine.
                    self.consolidation_tracker.record_commit()
                    committed_this_cycle += 1
                    logger.info(
                        "COMMIT: merged clusters (%s, %s) -> live engine "
                        "now holds %d clusters (merge %d/%d this cycle)",
                        proposal.target_a,
                        proposal.target_b,
                        live_cluster_engine.cluster_count,
                        committed_this_cycle,
                        _MAX_MERGES_PER_CYCLE,
                    )

                    # ── Immediate Quarantine Replay (drain the queue) ───────
                    # Do not advance to the next dataset vector yet: the merge
                    # just reorganized memory, so sweep the quarantine queue and
                    # try to re-home every still-active anomaly right now.
                    self._drain_quarantine(live_cluster_engine)

                # Cycle complete (budget spent, rejection, or no proposal):
                # terminate it and reset the scheduler, which arms the cooldown.
                scheduler.reset()

        duration = time.perf_counter() - start

        # -- snapshot anomaly-lifecycle outcomes (pure observability) ------
        # Absorption / retirement are decided inside the frozen cluster engine.
        # We read the final record statuses off the live engine once, so the
        # consolidation dashboard can report them without touching cognition.
        if scheduler is not None:
            engine = getattr(self.monitor, "cluster_engine", None)
            records = getattr(engine, "anomaly_records", []) if engine else []
            absorbed = sum(1 for r in records if getattr(r, "status", None) == "absorbed")
            retired = sum(1 for r in records if getattr(r, "status", None) == "retired")
            self.consolidation_tracker.set_anomaly_outcomes(absorbed, retired)

        # -- summarise -----------------------------------------------------
        regime_counts: Dict[str, int] = {}
        for entry in self.output_log:
            r = entry.get("regime")
            if r is not None:
                regime_counts[r] = regime_counts.get(r, 0) + 1

        return {
            "ticks": num_ticks,
            "duration": round(duration, 4),
            "ticks_per_second": round(num_ticks / duration, 2) if duration > 0 else 0.0,
            "entries_collected": len(self.output_log),
            "errors": errors,
            "regime_counts": regime_counts,
            "monitor_present": self.monitor is not None,
        }

    # -- helpers -----------------------------------------------------------

    def _drain_quarantine(self, engine: Any) -> None:
        """Re-ingest active quarantined anomalies into the reorganized clusters.

        Invoked immediately after a merge commits (C8 *immediate quarantine
        replay*). Instead of fetching the next dataset vector, we sweep the
        engine's ``anomaly_records`` and ask the engine to re-assign every
        still-active quarantined vector to the freshly reorganized clusters
        (which now have a free budget slot and reshaped centroids).

        For every record checked we increment the ``quarantine_replayed``
        counter; the engine marks any vector that now seeds or joins a cluster
        as resolved (``absorbed``). A failed re-ingest leaves the record active
        and -- by contract of :meth:`ClusterEngine.reingest_quarantined` --
        never spawns a duplicate record.

        Degrades gracefully: if the engine predates the re-ingest mechanic the
        sweep is skipped (the counter is left untouched) so older cores keep
        running unchanged.
        """
        records = getattr(engine, "anomaly_records", None)
        if not records:
            return
        reingest = getattr(engine, "reingest_quarantined", None)
        if reingest is None:
            return

        # Snapshot the active record ids first: re-ingesting one vector can,
        # via attention absorption, resolve sibling records as a side effect,
        # and we must not mutate the list we are iterating.
        active_ids = [
            r.id for r in list(records)
            if getattr(r, "status", None) == "active"
        ]
        for record_id in active_ids:
            # OBSERVE: one quarantine re-check against the reorganized clusters.
            self.consolidation_tracker.record_quarantine_replay()
            reingest(record_id)

    def write_decision_audit(self, artifacts_dir: os.PathLike) -> str:
        """Write the run's :attr:`decision_audit` list to ``decision_audit.json``.

        The C8 *decision audit* artifact (Task 2): a JSON array with one object
        per evaluated merge proposal, each carrying ``tick``, ``targets``,
        ``accepted``, ``prediction_delta``, ``entropy_delta``, ``load_delta``,
        ``energy_delta`` and ``reason``. The file is written into
        ``artifacts_dir`` (typically the ``exp_NNN`` directory just created by
        :meth:`ResultSerializer.save_experiment`), so the audit lives alongside
        that run's ``data.csv`` / ``metadata.json``.

        Returns
        -------
        str
            The absolute path of the written ``decision_audit.json`` file.
        """
        path = os.path.join(os.fspath(artifacts_dir), "decision_audit.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.decision_audit, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        return path

    @staticmethod
    def _resolve_config(
        overrides: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Merge caller-supplied overrides onto defaults."""
        config: Dict[str, Any] = {
            "num_ticks": 1000,
            "reset_dataset": True,
            "max_log_size": _DEFAULT_MAX_LOG_SIZE,
            "clear_log": True,
        }
        if overrides:
            config.update(overrides)
        return config


__all__ = ["BenchmarkRunner"]
