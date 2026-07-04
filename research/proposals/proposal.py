"""
research/proposals/proposal.py
==============================

The :class:`RichProposal` — Sprint R3's **self-contained, executable** merge
proposal.

Where the frozen :class:`~backend.cognition.candidate_generator.MergeProposal`
is a tiny inert ``(target_a, target_b, distance, strategy)`` record, a
``RichProposal`` is a *thick* object that carries its full provenance and can —
on its own, with no global loop — rehearse, score, counterfactually analyse and
serialise itself against a :class:`~research.proposals.base.MarketContext`:

* :meth:`replay`        — read-only sandbox rehearsal via the frozen
                          :class:`~backend.cognition.replay_engine.ReplayEngine`,
                          populating :attr:`replay_metrics`.
* :meth:`score`         — free-energy verdict via the frozen
                          :class:`~backend.cognition.decision_policy.DecisionPolicy`,
                          populating :attr:`decision_trace` and
                          :attr:`expected_complexity_change`.
* :meth:`counterfactual`— the single-proposal counterfactual (merge vs the
                          *no-merge* baseline, plus an optional replay-fidelity
                          ``replay_error``), populating :attr:`counterfactual`.
* :meth:`export`        — a JSON-safe snapshot of all metadata (sans the live
                          runtime context).

This "a single proposal can be executed, evaluated and serialised independently
of the global loop" property is a hard requirement of the R3 spec: it lets an
attribution study treat each candidate as a first-class, replayable experiment.

The class **wraps** the frozen cognition components and never modifies them; the
only state-mutating call any code path here makes is to a *deepcopy* sandbox.

Standard library only. Python 3.11+.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.cognition.candidate_generator import MergeProposal
from backend.cognition.decision_policy import (
    ACTIVE_LOAD,
    ENTROPY,
    PREDICTION_ERROR,
    STRATEGY_FREE_ENERGY,
    DecisionPolicy,
    DecisionScore,
)
from backend.cognition.replay_engine import ReplayEngine

#: Default free-energy coupling used when a context carries no explicit weights.
DEFAULT_ENERGY_WEIGHTS: Dict[str, float] = {"lam": 1.0, "mu": 2.0, "nu": 0.5}

#: A sentinel "do nothing" proposal: equal (and invalid) targets make the frozen
#: ReplayEngine treat it as a no-op, so its sandbox equals the live world. Used
#: to *measure* an already-committed clone without applying any further merge.
_NOOP_PROPOSAL = {"target_a": -1, "target_b": -1, "strategy": "noop"}


def energy_from_metrics(
    metrics: Dict[str, float], weights: Optional[Dict[str, float]] = None
) -> float:
    """Cognitive free-energy ``E = lam*H + mu*S + nu*A`` from a vitals snapshot.

    This is the *published* C8 energy formula (see
    :mod:`backend.cognition.decision_policy`), recomputed here over a metric
    mapping so a proposal can score itself without reaching into the policy's
    private helpers. ``weights`` defaults to the canonical ``(1.0, 2.0, 0.5)``.
    """
    w = weights or DEFAULT_ENERGY_WEIGHTS
    h = float(metrics.get(ENTROPY, 0.0) or 0.0)
    s = float(metrics.get(PREDICTION_ERROR, 0.0) or 0.0)
    a = float(metrics.get(ACTIVE_LOAD, 0.0) or 0.0)
    return w.get("lam", 1.0) * h + w.get("mu", 2.0) * s + w.get("nu", 0.5) * a


def make_proposal_id(target_a: int, target_b: int, strategy: str) -> str:
    """Deterministic id for a proposal: ``"<strategy>:<lo>-<hi>"``.

    Order-independent in the targets (``lo``/``hi`` are sorted) so the same
    unordered pair from the same source always yields the same id.
    """
    lo, hi = sorted((int(target_a), int(target_b)))
    return f"{strategy}:{lo}-{hi}"


@dataclass
class RichProposal:
    """A self-contained, executable cluster-merge proposal with full provenance.

    Attributes
    ----------
    proposal_id :
        Stable, order-independent identifier (see :func:`make_proposal_id`).
    target_a, target_b :
        The ids of the two clusters this proposal would fuse.
    origin_strategies :
        Every proposal source that nominated this pair (e.g. ``["geometric"]``
        or, after a pool merge, ``["geometric", "utility"]``).
    distance :
        Centroid distance metadata (Euclidean), recorded for the audit. ``nan``
        when not computable.
    expected_complexity_change :
        Signed structural-complexity change predicted by the replay (active-load
        *after* − *before*); negative means the merge is expected to *simplify*
        the substrate. Populated by :meth:`score`.
    replay_metrics :
        The before/after vitals snapshots from the sandbox rehearsal. Populated
        by :meth:`replay`.
    decision_trace :
        The free-energy verdict (energies, signed deltas, acceptance, ranking
        fields). Populated by :meth:`score` and annotated by the evaluator.
    counterfactual_block :
        The single-proposal counterfactual block (merge vs no-merge, optional
        ``replay_error``). Populated by :meth:`counterfactual`.
    context :
        The live :class:`~research.proposals.base.MarketContext` (runtime only;
        excluded from :meth:`export` and from equality/repr).
    """

    proposal_id: str
    target_a: int
    target_b: int
    origin_strategies: List[str] = field(default_factory=list)
    distance: float = float("nan")
    expected_complexity_change: Optional[float] = None
    replay_metrics: Optional[Dict[str, Any]] = None
    decision_trace: Dict[str, Any] = field(default_factory=dict)
    counterfactual_block: Optional[Dict[str, Any]] = None
    context: Optional[Any] = field(default=None, repr=False, compare=False)

    # -- construction helpers ---------------------------------------------

    @classmethod
    def create(
        cls,
        target_a: int,
        target_b: int,
        strategy: str,
        *,
        distance: float = float("nan"),
        context: Optional[Any] = None,
    ) -> "RichProposal":
        """Build a fresh proposal for one ``(target_a, target_b)`` pair."""
        return cls(
            proposal_id=make_proposal_id(target_a, target_b, strategy),
            target_a=int(target_a),
            target_b=int(target_b),
            origin_strategies=[strategy],
            distance=float(distance),
            context=context,
        )

    # -- identity ----------------------------------------------------------

    @property
    def primary_strategy(self) -> str:
        """The first (originating) source strategy, or ``"unknown"``."""
        return self.origin_strategies[0] if self.origin_strategies else "unknown"

    @property
    def pair(self) -> frozenset:
        """The unordered target pair as a hashable :class:`frozenset`."""
        return frozenset((self.target_a, self.target_b))

    def to_merge_proposal(self) -> MergeProposal:
        """Render the frozen :class:`MergeProposal` the ReplayEngine consumes."""
        return MergeProposal(
            target_a=self.target_a,
            target_b=self.target_b,
            distance=self.distance,
            strategy=self.primary_strategy,
        )

    # -- self-contained execution -----------------------------------------

    def _resolve_context(self, context: Optional[Any]) -> Any:
        ctx = context if context is not None else self.context
        if ctx is None:
            raise ValueError(
                "RichProposal requires a MarketContext to execute; pass one to "
                "the method or set .context."
            )
        return ctx

    def replay(
        self,
        context: Optional[Any] = None,
        *,
        engine: Optional[ReplayEngine] = None,
    ) -> DecisionScore:
        """Rehearse this merge read-only and store its before/after vitals.

        Delegates to the frozen :class:`ReplayEngine`, which clones the core
        into a deepcopy sandbox — the live core backing the context is never
        mutated.
        """
        ctx = self._resolve_context(context)
        replay = engine if engine is not None else ReplayEngine()
        score = replay.simulate_proposal(
            ctx.core, self.to_merge_proposal(), ctx.recent_vectors
        )
        self.replay_metrics = {
            "metrics_before": dict(score.metrics_before),
            "metrics_after": dict(score.metrics_after),
        }
        return score

    def score(
        self,
        context: Optional[Any] = None,
        *,
        policy: Optional[DecisionPolicy] = None,
    ) -> Dict[str, Any]:
        """Produce the free-energy verdict and populate :attr:`decision_trace`.

        Rehearses first if :meth:`replay` has not yet been called. The verdict
        is rendered verbatim by the frozen :class:`DecisionPolicy` (free-energy
        strategy); this method adds the ``energy_score`` (the post-merge energy
        used for ranking) and the expected complexity change.
        """
        ctx = self._resolve_context(context)
        if self.replay_metrics is None:
            self.replay(ctx)

        weights = getattr(ctx, "energy_weights", None) or DEFAULT_ENERGY_WEIGHTS
        judge = policy if policy is not None else DecisionPolicy(
            strategy=STRATEGY_FREE_ENERGY,
            lam=weights.get("lam", 1.0),
            mu=weights.get("mu", 2.0),
            nu=weights.get("nu", 0.5),
        )
        before = self.replay_metrics["metrics_before"]
        after = self.replay_metrics["metrics_after"]
        verdict = judge.evaluate_metrics(before, after)

        # active-load after − before (negative ⇒ structurally simpler).
        self.expected_complexity_change = -float(verdict["delta_load"])

        self.decision_trace.update(
            {
                "proposal_id": self.proposal_id,
                "strategy": self.primary_strategy,
                "origin_strategies": list(self.origin_strategies),
                "targets": [self.target_a, self.target_b],
                "accepted": bool(verdict["accepted"]),
                "reason": str(verdict["reason"]),
                "energy_before": float(verdict["energy_before"]),
                "energy_after": float(verdict["energy_after"]),
                "energy_score": float(verdict["energy_after"]),
                "delta_energy": float(verdict["delta_energy"]),
                "delta_prediction": float(verdict["delta_prediction"]),
                "delta_entropy": float(verdict["delta_entropy"]),
                "delta_load": float(verdict["delta_load"]),
                "expected_complexity_change": self.expected_complexity_change,
            }
        )
        return self.decision_trace

    def counterfactual(
        self,
        context: Optional[Any] = None,
        *,
        held_out: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        """Compute this proposal's counterfactual block (merge vs no-merge).

        The *no-merge baseline* is the live pre-merge energy (the cost of doing
        nothing). ``improvement = energy_no_merge − energy_merge``; a positive
        value means committing this merge lowers free energy.

        When a held-out window is available (passed here or carried on the
        context as ``held_out_vectors``), ``replay_error`` is also computed: the
        absolute divergence between the energy the sandbox *predicted* and the
        energy actually realised by committing the merge on an isolated clone
        and re-measuring on the held-out stream. This quantifies how faithful
        the read-only rehearsal was.
        """
        ctx = self._resolve_context(context)
        if not self.decision_trace:
            self.score(ctx)

        weights = getattr(ctx, "energy_weights", None) or DEFAULT_ENERGY_WEIGHTS
        energy_no_merge = float(self.decision_trace["energy_before"])
        energy_merge = float(self.decision_trace["energy_after"])

        block: Dict[str, Any] = {
            "proposal_id": self.proposal_id,
            "energy_no_merge": energy_no_merge,
            "energy_merge": energy_merge,
            "improvement_over_no_merge": energy_no_merge - energy_merge,
            "beneficial": (energy_no_merge - energy_merge) >= 0.0,
            "replay_error": None,
        }

        window = held_out
        if window is None:
            window = getattr(ctx, "held_out_vectors", None)
        if window:
            actual_energy = self._measure_committed_energy(ctx.core, window, weights)
            block["actual_energy_held_out"] = actual_energy
            block["predicted_energy"] = energy_merge
            block["replay_error"] = abs(energy_merge - actual_energy)

        self.counterfactual_block = block
        return block

    def _measure_committed_energy(
        self,
        core: Any,
        window: List[List[float]],
        weights: Dict[str, float],
    ) -> float:
        """Energy of the *committed* merge, measured on a window via a clone.

        Deepcopies ``core``, applies the merge with the frozen
        :meth:`ReplayEngine.commit_proposal` (the only sanctioned mutation, here
        confined to the clone), then measures the committed clone's vitals by
        rehearsing a no-op proposal (whose sandbox equals the live clone).
        """
        clone = copy.deepcopy(core)
        replay = ReplayEngine()
        replay.commit_proposal(clone, self.to_merge_proposal())
        committed = replay.simulate_proposal(clone, dict(_NOOP_PROPOSAL), window)
        return energy_from_metrics(committed.metrics_before, weights)

    # -- serialisation -----------------------------------------------------

    def export(self) -> Dict[str, Any]:
        """A JSON-safe snapshot of every metadata field (sans live context)."""
        return {
            "proposal_id": self.proposal_id,
            "target_a": self.target_a,
            "target_b": self.target_b,
            "origin_strategies": list(self.origin_strategies),
            "distance": _json_float(self.distance),
            "expected_complexity_change": _json_float(
                self.expected_complexity_change
            ),
            "replay_metrics": _json_safe(self.replay_metrics),
            "decision_trace": _json_safe(self.decision_trace),
            "counterfactual": _json_safe(self.counterfactual_block),
        }


def _json_float(value: Optional[float]) -> Optional[float]:
    """Coerce a float to a JSON-safe value (``nan``/``inf`` -> ``None``)."""
    if value is None:
        return None
    f = float(value)
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def _json_safe(obj: Any) -> Any:
    """Recursively coerce a structure to JSON-safe primitives."""
    if obj is None:
        return None
    if isinstance(obj, (bool, int)):
        return obj
    if isinstance(obj, float):
        return _json_float(obj)
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    # Unknown type: convert to string.
    return str(obj)


__all__ = [
    "RichProposal",
    "energy_from_metrics",
    "make_proposal_id",
    "DEFAULT_ENERGY_WEIGHTS",
]
