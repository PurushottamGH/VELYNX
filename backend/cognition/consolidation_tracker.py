"""
backend/cognition/consolidation_tracker.py
============================================

C8 — Consolidation Pipeline Observability.

A strict, **pure-observability** state-machine recorder for the autonomous
memory-consolidation pipeline. It counts *how many times* each stage of the

    scheduler → propose → replay → commit

pipeline fires, plus the anomaly-quarantine lifecycle outcomes (absorbed vs.
retired), and stores a structured trace of every replay decision.

The contract is deliberately one-directional: nothing in this module is ever
read back by the cognitive path. It only *observes and counts*. Mutating a
counter can never change which proposals are generated, how a replay is
scored, or whether a merge is committed. That is what makes it safe to wire
into the frozen C8 logic without risk of perturbing behaviour.

Standard-library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ConsolidationTracker:
    """Aggregate counters + event traces for the C8 consolidation pipeline.

    All counters start at zero and only ever increase. They map one-to-one
    onto the discrete events of the consolidation state machine:

    * ``scheduler_triggers``   -- sleep cycles the scheduler signalled.
    * ``proposals_generated``  -- non-``None`` merge proposals produced.
    * ``replay_evaluations``   -- proposals rehearsed in the replay sandbox.
    * ``replay_accepted``      -- rehearsals whose verdict was *accept*.
    * ``replay_rejected``      -- rehearsals whose verdict was *reject*.
    * ``merges_committed``     -- accepted merges applied to the live engine.
    * ``queue_replayed``       -- total recent-vectors fed through the sandbox
      replay across every evaluation (cumulative validation-window volume).
    * ``quarantine_replayed``  -- total quarantined anomaly records re-checked
      against the reorganized clusters during post-commit queue drains (one
      increment per check, C8 immediate-replay mechanic).
    * ``anomalies_absorbed``   -- quarantined vectors later captured into a
      cluster.
    * ``anomalies_retired``    -- quarantined vectors aged out, never absorbed.
    """

    # ── The 10 aggregate counters ─────────────────────────────────────────
    scheduler_triggers: int = 0
    proposals_generated: int = 0
    replay_evaluations: int = 0
    replay_accepted: int = 0
    replay_rejected: int = 0
    merges_committed: int = 0
    queue_replayed: int = 0
    quarantine_replayed: int = 0
    anomalies_absorbed: int = 0
    anomalies_retired: int = 0

    # ── Running sums of accepted-merge vital deltas (Task 3) ──────────────
    #: Cumulative signed (before − after) improvement for each cognitive vital,
    #: summed over **accepted** merges only. Divided by ``replay_accepted`` they
    #: yield the mean Δ the AVERAGE ACCEPTED DELTAS dashboard reports. Positive
    #: means the accepted merges, on average, *improved* that vital (its value
    #: fell). Pure observability — never read back by cognition.
    sum_delta_prediction: float = 0.0
    sum_delta_entropy: float = 0.0
    sum_delta_load: float = 0.0
    sum_delta_energy: float = 0.0

    # ── Structured event traces (Task 2 / C8-final decision components) ───
    #: One entry per replay decision. Beyond the proposal targets and the tick
    #: it fired on, every component of the DecisionPolicy verdict is logged:
    #: the four cognitive-vital deltas (``delta_prediction`` ΔS,
    #: ``delta_entropy`` ΔH, ``delta_load`` ΔA, ``delta_energy`` ΔE), the
    #: before/after energy, the per-vital before/after snapshots, the
    #: ``decision_strategy`` in force, and the explicit structural ``reason``
    #: for the accept/reject judgement. Pure log — never read back by cognition.
    traces: List[Dict[str, Any]] = field(default_factory=list)

    # ── Increment helpers (the only way the pipeline talks to the tracker) ─

    def record_scheduler_trigger(self) -> None:
        """Count one scheduler-fired sleep cycle."""
        self.scheduler_triggers += 1

    def record_proposal(self) -> None:
        """Count one non-``None`` merge proposal."""
        self.proposals_generated += 1

    def record_replay_evaluation(self, queue_size: int = 0) -> None:
        """Count one sandbox rehearsal and the vectors it replayed.

        ``queue_size`` is the length of the recent-vector validation window
        replayed through both worlds for this evaluation; it accumulates into
        ``queue_replayed`` so the total replay volume stays measurable.
        """
        self.replay_evaluations += 1
        self.queue_replayed += int(queue_size)

    def record_quarantine_replay(self, count: int = 1) -> None:
        """Count ``count`` quarantined-record re-checks during a queue drain.

        Called once per quarantined :class:`AnomalyRecord` inspected when the
        runner drains the queue after a committed merge -- whether or not the
        record was successfully re-absorbed. Pure observability.
        """
        self.quarantine_replayed += int(count)

    def record_acceptance(
        self,
        delta_prediction: float = 0.0,
        delta_entropy: float = 0.0,
        delta_load: float = 0.0,
        delta_energy: float = 0.0,
    ) -> None:
        """Count one *accepted* replay verdict and bank its vital deltas.

        The four optional ``delta_*`` arguments are the signed (before − after)
        vital improvements of the accepted merge; they accumulate into the
        ``sum_delta_*`` running totals that back the AVERAGE ACCEPTED DELTAS
        dashboard (Task 3). They default to ``0.0`` so legacy no-argument calls
        still simply bump the acceptance counter.
        """
        self.replay_accepted += 1
        self.sum_delta_prediction += float(delta_prediction)
        self.sum_delta_entropy += float(delta_entropy)
        self.sum_delta_load += float(delta_load)
        self.sum_delta_energy += float(delta_energy)

    def record_rejection(self) -> None:
        """Count one *rejected* replay verdict."""
        self.replay_rejected += 1

    def record_commit(self) -> None:
        """Count one merge applied to the live engine."""
        self.merges_committed += 1

    def record_trace(self, trace: Dict[str, Any]) -> None:
        """Append a structured replay-decision trace (defensive copy)."""
        self.traces.append(dict(trace))

    def set_anomaly_outcomes(self, absorbed: int, retired: int) -> None:
        """Snapshot the anomaly-lifecycle outcomes at end of run.

        Absorption/retirement are decided inside the (frozen) cluster engine,
        not by the pipeline stages above, so they are read off the engine's
        records once rather than incremented event-by-event.
        """
        self.anomalies_absorbed = int(absorbed)
        self.anomalies_retired = int(retired)

    # ── Safe percentage metrics ───────────────────────────────────────────

    @staticmethod
    def _safe_pct(numerator: float, denominator: float) -> float:
        """Percentage that returns ``0.0`` instead of dividing by zero."""
        return (100.0 * numerator / denominator) if denominator else 0.0

    @property
    def proposal_success_rate(self) -> float:
        """% of scheduler triggers that yielded an actual merge proposal."""
        return self._safe_pct(self.proposals_generated, self.scheduler_triggers)

    @property
    def replay_efficiency(self) -> float:
        """% of replay evaluations whose verdict was *accept*."""
        return self._safe_pct(self.replay_accepted, self.replay_evaluations)

    @property
    def absorption_rate(self) -> float:
        """% of resolved anomalies that were absorbed (vs. retired)."""
        return self._safe_pct(
            self.anomalies_absorbed,
            self.anomalies_absorbed + self.anomalies_retired,
        )

    # ── Mean accepted-merge deltas (Task 3 dashboard) ─────────────────────

    @staticmethod
    def _safe_mean(total: float, count: int) -> float:
        """Mean that returns ``0.0`` instead of dividing by zero."""
        return (total / count) if count else 0.0

    @property
    def avg_delta_prediction(self) -> float:
        """Mean ΔS (prediction-error improvement) over accepted merges."""
        return self._safe_mean(self.sum_delta_prediction, self.replay_accepted)

    @property
    def avg_delta_entropy(self) -> float:
        """Mean ΔH (entropy improvement) over accepted merges."""
        return self._safe_mean(self.sum_delta_entropy, self.replay_accepted)

    @property
    def avg_delta_load(self) -> float:
        """Mean ΔA (active-load improvement) over accepted merges."""
        return self._safe_mean(self.sum_delta_load, self.replay_accepted)

    @property
    def avg_delta_energy(self) -> float:
        """Mean ΔE (free-energy improvement) over accepted merges."""
        return self._safe_mean(self.sum_delta_energy, self.replay_accepted)

    # ── Serialisation ─────────────────────────────────────────────────────

    def as_dict(self) -> Dict[str, Any]:
        """Render every counter + derived metric as a plain mapping."""
        return {
            "scheduler_triggers": self.scheduler_triggers,
            "proposals_generated": self.proposals_generated,
            "replay_evaluations": self.replay_evaluations,
            "replay_accepted": self.replay_accepted,
            "replay_rejected": self.replay_rejected,
            "merges_committed": self.merges_committed,
            "queue_replayed": self.queue_replayed,
            "quarantine_replayed": self.quarantine_replayed,
            "anomalies_absorbed": self.anomalies_absorbed,
            "anomalies_retired": self.anomalies_retired,
            "proposal_success_rate": self.proposal_success_rate,
            "replay_efficiency": self.replay_efficiency,
            "absorption_rate": self.absorption_rate,
            "sum_delta_prediction": self.sum_delta_prediction,
            "sum_delta_entropy": self.sum_delta_entropy,
            "sum_delta_load": self.sum_delta_load,
            "sum_delta_energy": self.sum_delta_energy,
            "avg_delta_prediction": self.avg_delta_prediction,
            "avg_delta_entropy": self.avg_delta_entropy,
            "avg_delta_load": self.avg_delta_load,
            "avg_delta_energy": self.avg_delta_energy,
        }


__all__ = ["ConsolidationTracker"]
