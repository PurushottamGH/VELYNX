"""
research/runner.py
==================

The :class:`ResearchRunner` — a research-grade re-implementation of the C8
sleep-cycle consolidation loop with a **pluggable consolidation policy** and a
**configurable replay horizon**.

Why a parallel runner (and not a modified ``validation/runner.py``)
-------------------------------------------------------------------
Sprint R1 forbids changing production behaviour. ``validation/runner.py`` hard-
wires the nearest-pair :class:`CandidateGenerator` and the free-energy
:class:`DecisionPolicy`; making it pluggable would change that file. So this
runner re-expresses the *same* loop structure (scheduler -> propose -> replay ->
commit, budgeted at three merges per cycle) against the frozen components, but
takes the candidate selection and accept/reject decisions from an injected
:class:`~research.policies.base.ConsolidationPolicy`.

Uniform measurement (the comparability guarantee)
--------------------------------------------------
*Every* proposal a policy selects is measured identically: a read-only
:class:`~backend.cognition.replay_engine.ReplayEngine` rehearsal yields the
before/after vital snapshots, and a single shared free-energy *scorer* turns
those into the four signed deltas recorded in the decision audit. The scorer's
verdict is used **only** for the audit's energy bookkeeping; whether the merge
is actually committed is decided solely by the policy. Thus a Random or FIFO
merge is logged with the *same* free-energy deltas a FreeEnergy merge would be,
which is exactly what makes the policies comparable after the fact.

Determinism
-----------
Given ``(policy, replay_horizon, noise_sigma, seed, num_ticks)`` the run is fully
reproducible: the dataset is seeded, the cognitive core is RNG-free, and the one
stochastic policy (Random) draws only from a seeded :class:`random.Random`
derived from the experiment seed.

Standard library only.
"""

from __future__ import annotations

import time
import tracemalloc
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.cognition.decision_policy import (
    STRATEGY_FREE_ENERGY,
    DecisionPolicy,
    resolve_coefficients,
)
from backend.cognition.memory_scheduler import MemoryScheduler
from backend.cognition.replay_engine import ReplayEngine
from validation.datasets import build_dataset
from validation.metrics import (
    active_load,
    cognitive_energy,
    transition_entropy,
)
from validation.monitor import VectorMonitor
from research.policies import ConsolidationPolicy, PolicyContext, build_policy
import random

#: Structural merge budget per triggered sleep cycle. Matches the production
#: ``validation.runner._MAX_MERGES_PER_CYCLE`` so research runs share the same
#: cycle dynamics as the system under study.
MAX_MERGES_PER_CYCLE = 3

#: Default replay horizon (recent-vector window). Matches production's
#: ``_RECENT_VECTORS_MAXLEN`` so the default behaves like the live system.
DEFAULT_REPLAY_HORIZON = 200

#: Measurement keys that are inherently non-deterministic across reruns of the
#: *same* config (wall-clock timings, peak heap, on-disk size). The scientific
#: measurements are reproducible; these are not, so the artifact integrity hash
#: and reproducibility checks deliberately exclude them.
NON_DETERMINISTIC_MEASUREMENTS = frozenset(
    {"runtime_seconds", "replay_seconds", "peak_memory_bytes", "artifact_size_bytes"}
)


@dataclass(frozen=True)
class RunConfig:
    """The complete, reproducible specification of one experiment run."""

    policy: str = "free_energy"
    replay_horizon: int = DEFAULT_REPLAY_HORIZON
    noise_sigma: float = 0.05
    seed: int = 1
    num_ticks: int = 1000
    dataset_name: str = "environment"
    proximity_threshold: float = 0.25
    max_clusters: int = 50
    #: Free-energy coupling section ``{"lambda","mu","nu"}`` (audit scorer + the
    #: FreeEnergy policy share this single source of truth).
    decision_policy: Dict[str, float] = field(default_factory=dict)
    #: Extra keyword arguments forwarded to the policy constructor.
    policy_params: Dict[str, Any] = field(default_factory=dict)
    #: Optional R2A held-out evaluation hook. When set, the runner calls its
    #: ``finalize(monitor)`` after the training loop and merges the returned
    #: held-out metric(s) into the measurement record. Deliberately *excluded*
    #: from :meth:`as_dict` (and therefore from the reproducibility/content
    #: hash and artifact serialization): it is a runtime evaluation hook, not
    #: part of the reproducible run specification, and is not JSON-serializable.
    evaluation_protocol: Optional[Any] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "policy": self.policy,
            "replay_horizon": self.replay_horizon,
            "noise_sigma": self.noise_sigma,
            "seed": self.seed,
            "num_ticks": self.num_ticks,
            "dataset_name": self.dataset_name,
            "proximity_threshold": self.proximity_threshold,
            "max_clusters": self.max_clusters,
            "decision_policy": dict(self.decision_policy),
            "policy_params": dict(self.policy_params),
        }


@dataclass
class RunResult:
    """Everything one run produces, ready to be serialized into artifacts."""

    config: RunConfig
    measurements: Dict[str, Optional[float]]
    counters: Dict[str, int]
    decision_audit: List[Dict[str, Any]]
    policy_description: Dict[str, Any]
    seed_info: Dict[str, Any]
    summary: Dict[str, Any]


class ResearchRunner:
    """Drive one experiment: a dataset through a core under a pluggable policy."""

    def __init__(self, config: RunConfig) -> None:
        self.config = config
        self.energy_weights = resolve_coefficients(config.decision_policy)
        # The shared, read-only free-energy scorer used ONLY to compute the
        # audit's signed vital deltas — never to gate a commit (that is the
        # policy's job). Free-energy strategy + the resolved coefficients.
        self._scorer = DecisionPolicy(
            strategy=STRATEGY_FREE_ENERGY, **self.energy_weights
        )

    # -- public API --------------------------------------------------------

    def run(self) -> RunResult:
        """Execute the run and return a fully-populated :class:`RunResult`."""
        cfg = self.config

        # -- build the world + mind (seeded, reproducible) -----------------
        dataset = build_dataset(
            cfg.dataset_name, seed=cfg.seed, noise_sigma=cfg.noise_sigma
        )
        monitor = VectorMonitor(
            proximity_threshold=cfg.proximity_threshold,
            max_clusters=cfg.max_clusters,
            decision_policy_weights=self.energy_weights,
        )
        policy: ConsolidationPolicy = build_policy(cfg.policy, **cfg.policy_params)

        # The single deterministic randomness source for stochastic policies.
        policy_rng = random.Random(cfg.seed)

        scheduler = MemoryScheduler(monitor)
        replay = ReplayEngine()

        recent = deque(maxlen=cfg.replay_horizon)
        errors: List[float] = []
        audit: List[Dict[str, Any]] = []
        replay_window_sizes: List[int] = []

        counters = {
            "scheduler_triggers": 0,
            "proposals": 0,
            "replay_evaluations": 0,
            "merges_accepted": 0,
            "merges_rejected": 0,
            "merges_committed": 0,
            "quarantine_replays": 0,
        }
        replay_seconds = 0.0

        tracemalloc.start()
        start = time.perf_counter()

        for tick_num in range(cfg.num_ticks):
            vector = dataset.get_next_tick()
            recent.append(vector)

            result = monitor.tick(vector)
            err = result.get("surprise")
            if err is not None:
                errors.append(float(err))

            if scheduler.tick():
                counters["scheduler_triggers"] += 1
                replay_seconds += self._consolidation_cycle(
                    monitor=monitor,
                    policy=policy,
                    replay=replay,
                    rng=policy_rng,
                    tick_num=tick_num,
                    recent=recent,
                    audit=audit,
                    counters=counters,
                    replay_window_sizes=replay_window_sizes,
                )
                scheduler.reset()

        duration = time.perf_counter() - start
        _current, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        measurements = self._measure(
            monitor=monitor,
            errors=errors,
            counters=counters,
            replay_window_sizes=replay_window_sizes,
            duration=duration,
            replay_seconds=replay_seconds,
            peak_bytes=peak_bytes,
        )

        # -- R2A: optional read-only held-out validation -------------------
        # If an evaluation protocol is attached, score the *trained* monitor on
        # a held-out, seed-disjoint probe stream and merge the resulting
        # metric(s). The protocol evaluates a deepcopy, so ``monitor`` (and
        # every measurement already taken above) is left untouched.
        if cfg.evaluation_protocol is not None:
            measurements.update(cfg.evaluation_protocol.finalize(monitor))

        summary = self._summarize(monitor, counters, measurements)

        return RunResult(
            config=cfg,
            measurements=measurements,
            counters=counters,
            decision_audit=audit,
            policy_description=policy.describe(),
            seed_info={
                "master_seed": cfg.seed,
                "sensor_seed": (cfg.seed + 1) if cfg.seed is not None else None,
                "policy_rng_seed": cfg.seed,
                "deterministic_selection": policy.is_deterministic,
            },
            summary=summary,
        )

    # -- consolidation cycle ----------------------------------------------

    def _consolidation_cycle(
        self,
        *,
        monitor: VectorMonitor,
        policy: ConsolidationPolicy,
        replay: ReplayEngine,
        rng: random.Random,
        tick_num: int,
        recent: deque,
        audit: List[Dict[str, Any]],
        counters: Dict[str, int],
        replay_window_sizes: List[int],
    ) -> float:
        """Run one budgeted sleep cycle; return seconds spent in replay.

        Mirrors the production state machine: propose -> measure -> decide ->
        (commit + drain | rollback). The single behavioural seam is that
        *proposal selection* and the *accept verdict* come from ``policy``
        instead of the hard-wired generator + free-energy policy.
        """
        engine = monitor.cluster_engine
        window = list(recent)
        replay_seconds = 0.0
        committed = 0

        while committed < MAX_MERGES_PER_CYCLE:
            context = PolicyContext(
                rng=rng,
                tick=tick_num,
                energy_weights=self.energy_weights,
                merge_index=committed,
            )

            proposal = policy.select_candidate(engine, context)
            if proposal is None:
                break
            counters["proposals"] += 1

            # Uniform read-only measurement of the selected proposal.
            t0 = time.perf_counter()
            score = replay.simulate_proposal(engine, proposal, window)
            replay_seconds += time.perf_counter() - t0
            counters["replay_evaluations"] += 1
            replay_window_sizes.append(len(window))

            # Policy decides commit/rollback.
            accepted, reason = policy.accept(score, context)

            # Uniform free-energy delta bookkeeping (audit only).
            verdict = self._scorer.evaluate_metrics(
                score.metrics_before, score.metrics_after
            )
            audit.append(
                {
                    "tick": tick_num,
                    "policy": policy.name,
                    "strategy": proposal.strategy,
                    "targets": [proposal.target_a, proposal.target_b],
                    "distance": proposal.distance,
                    "accepted": bool(accepted),
                    "prediction_delta": verdict["delta_prediction"],
                    "entropy_delta": verdict["delta_entropy"],
                    "load_delta": verdict["delta_load"],
                    "energy_delta": verdict["delta_energy"],
                    "energy_before": verdict["energy_before"],
                    "energy_after": verdict["energy_after"],
                    "reason": reason,
                }
            )

            if not accepted:
                counters["merges_rejected"] += 1
                # Deterministic selectors re-propose the same pair, so looping
                # would spin forever — end the cycle on a rejection, as in prod.
                break

            counters["merges_accepted"] += 1
            replay.commit_proposal(engine, proposal)
            counters["merges_committed"] += 1
            committed += 1
            counters["quarantine_replays"] += self._drain_quarantine(engine)

        return replay_seconds

    @staticmethod
    def _drain_quarantine(engine: Any) -> int:
        """Re-ingest active quarantined anomalies; return how many were swept.

        Mirrors the production immediate-quarantine-replay step so a research
        run's post-merge dynamics match the live system.
        """
        records = getattr(engine, "anomaly_records", None)
        reingest = getattr(engine, "reingest_quarantined", None)
        if not records or reingest is None:
            return 0
        active_ids = [
            r.id for r in list(records) if getattr(r, "status", None) == "active"
        ]
        for record_id in active_ids:
            reingest(record_id)
        return len(active_ids)

    # -- measurement -------------------------------------------------------

    def _measure(
        self,
        *,
        monitor: VectorMonitor,
        errors: List[float],
        counters: Dict[str, int],
        replay_window_sizes: List[int],
        duration: float,
        replay_seconds: float,
        peak_bytes: int,
    ) -> Dict[str, Optional[float]]:
        """Reduce the finished run to the flat measurement record metrics read."""
        snap = monitor.snapshot()
        final_entropy = transition_entropy(snap.get("transitions", {}) or {})
        final_load = active_load(
            int(snap.get("cluster_count", 0) or 0),
            snap.get("anomaly_vectors", []) or [],
        )
        mean_err = (sum(errors) / len(errors)) if errors else 0.0
        rmse = (
            (sum(e * e for e in errors) / len(errors)) ** 0.5 if errors else 0.0
        )
        final_energy = cognitive_energy(
            final_entropy, mean_err, final_load,
            lam=self.energy_weights["lam"],
            mu=self.energy_weights["mu"],
            nu=self.energy_weights["nu"],
        )

        mem = monitor.get_memory_summary()
        evals = counters["replay_evaluations"]

        return {
            # primary (only PredictionRMSE is measurable)
            "prediction_rmse": rmse,
            "mean_prediction_error": mean_err,
            # secondary
            "replay_efficiency": (
                100.0 * counters["merges_committed"] / evals if evals else None
            ),
            "merge_acceptance_rate": (
                counters["merges_accepted"] / evals if evals else None
            ),
            "avg_replay_cost": (
                sum(replay_window_sizes) / len(replay_window_sizes)
                if replay_window_sizes else None
            ),
            "final_cluster_count": float(snap.get("cluster_count", 0) or 0),
            "final_entropy": final_entropy,
            "final_active_load": final_load,
            "final_energy": final_energy,
            "avg_anomaly_lifetime": float(mem.get("average_anomaly_lifetime", 0.0)),
            # engineering
            "runtime_seconds": duration,
            "replay_seconds": replay_seconds,
            "peak_memory_bytes": float(peak_bytes),
            "merges_committed": float(counters["merges_committed"]),
            # ArtifactSize is filled in by the artifact writer post-hoc.
            "artifact_size_bytes": None,
        }

    @staticmethod
    def _summarize(
        monitor: VectorMonitor,
        counters: Dict[str, int],
        measurements: Dict[str, Optional[float]],
    ) -> Dict[str, Any]:
        """A compact human-readable run summary (the ``summary.json`` payload)."""
        return {
            "final_cluster_count": measurements["final_cluster_count"],
            "final_energy": measurements["final_energy"],
            "prediction_rmse": measurements["prediction_rmse"],
            "scheduler_triggers": counters["scheduler_triggers"],
            "proposals": counters["proposals"],
            "merges_committed": counters["merges_committed"],
            "merges_rejected": counters["merges_rejected"],
            "memory": monitor.get_memory_summary(),
        }


def run_single(config: RunConfig) -> RunResult:
    """Convenience: build and execute a :class:`ResearchRunner` for ``config``."""
    return ResearchRunner(config).run()


__all__ = [
    "MAX_MERGES_PER_CYCLE",
    "DEFAULT_REPLAY_HORIZON",
    "NON_DETERMINISTIC_MEASUREMENTS",
    "RunConfig",
    "RunResult",
    "ResearchRunner",
    "run_single",
]
