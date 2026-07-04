"""
VELYNX Milestone C8.2 / C8-final — The Replay Engine (pure sandbox simulator).

A safe, isolated sandbox in which the brain can rehearse a proposed memory
restructuring *before* committing it to the live cluster substrate.

Role (C8-final decoupling)
--------------------------
The engine's sole job is now to **simulate and measure** — never to decide. It

  1. clones the live clustering substrate into a ``deepcopy`` sandbox,
  2. applies the proposed merge to the clone only,
  3. measures the brain's native cognitive vitals (H, S, A) in *both* the live
     (pre-merge) and sandbox (post-merge) worlds against a recent-vector
     window, strictly read-only, and
  4. returns those two snapshots as a structured
     :class:`~backend.cognition.decision_policy.DecisionScore`.

The accept/reject judgement is made elsewhere, by the
:class:`~backend.cognition.decision_policy.DecisionPolicy`, which reads the
``DecisionScore``. This keeps the *measurement* (here) cleanly separated from
the *policy* (there).

Strict contract
---------------
* The live :class:`~cognition.vector_prediction_core.ClusterEngine` is **never**
  mutated by a simulation. Every structural change happens against the sandbox.
* Vital measurement is **read-only**: it never calls ``assign`` or otherwise
  advances any engine state (no centroid updates, no surprise tracking, no
  predictor mutation).
* :meth:`commit_proposal` is the *only* method that touches the live engine, and
  only the caller (after a positive policy verdict) may invoke it.

The vitals (lower-is-better, matching :mod:`validation.metrics`)
----------------------------------------------------------------
    S -- prediction_error : mean Markov forecast error over the window. For each
                            vector v_i the predictor's forecast (centroid of the
                            most-likely next cluster, given the previous
                            vector's nearest cluster id) is compared to v_i via
                            Euclidean distance; the per-window mean is returned.
                            Mirrors ``VectorPredictionCore.ingest`` line 772.
    H -- entropy          : conditional Shannon entropy of the cluster-transition
                            chain induced by replaying the window read-only.
    A -- active_load      : live clusters + spatial volume of the anomaly cloud.

Standard-library only: ``copy``, ``math`` + the sibling vector-math helpers and
the local :class:`DecisionScore` data contract.
"""

import copy
import math
from typing import Any, Optional

from .decision_policy import (
    ACTIVE_LOAD,
    ENTROPY,
    PREDICTION_ERROR,
    DecisionScore,
)
from .vector_prediction_core import Cluster, euclidean_distance


class ReplayEngine:
    """Sandboxed rehearsal of memory-restructuring proposals (pure simulator).

    Given a *live* prediction core, a structural *proposal*, and a window of
    *recent vectors*, the engine clones the core's clustering substrate, applies
    the proposal to the clone, and measures the cognitive vitals in both worlds.
    It returns a :class:`DecisionScore` and makes **no** acceptance decision.

    Nothing here touches the live execution state: the only object the live
    brain ever shares is the read-only data inspected to build the deepcopy.
    """

    def simulate_proposal(
        self,
        core: Any,
        proposal: Any,
        recent_vectors: list[list[float]],
    ) -> DecisionScore:
        """Rehearse ``proposal`` against ``recent_vectors`` and score both worlds.

        Parameters
        ----------
        core :
            The live prediction core. May be a
            :class:`~cognition.vector_prediction_core.VectorPredictionCore`
            (exposing ``.cluster_engine``) or a bare ``ClusterEngine``.
        proposal :
            A cluster-merge proposal exposing ``target_a`` and ``target_b`` (the
            ids of the two clusters to fuse). Accepts either a mapping
            (``{"target_a": 0, "target_b": 1}``) or an object with those
            attributes (and optionally ``strategy`` / ``distance`` metadata).
        recent_vectors :
            The validation window — recent observations replayed read-only
            through both worlds to measure the vitals.

        Returns
        -------
        DecisionScore
            ``metrics_before`` (live / pre-merge) and ``metrics_after``
            (sandbox / post-merge) snapshots, each holding ``prediction_error``,
            ``entropy`` and ``active_load``, plus the proposal metadata. The
            engine renders **no** verdict — that is the
            :class:`~backend.cognition.decision_policy.DecisionPolicy`'s job.
        """
        # Resolve the live clustering substrate (never mutated below).
        live_engine = self._resolve_engine(core)

        # ── Sandbox Simulation ────────────────────────────────────────────
        # Deepcopy so the live brain cannot be corrupted by the restructuring.
        sandbox_engine = copy.deepcopy(live_engine)
        self._apply_proposal(sandbox_engine, proposal)

        # ── Read-only vital measurement on both engines ───────────────────
        metrics_before = self._measure(core, live_engine, recent_vectors)
        metrics_after = self._measure(core, sandbox_engine, recent_vectors)

        return DecisionScore(
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            strategy=getattr(proposal, "strategy", None)
            if not isinstance(proposal, dict)
            else proposal.get("strategy"),
            target_a=self._proposal_targets(proposal)[0],
            target_b=self._proposal_targets(proposal)[1],
            distance=getattr(proposal, "distance", None)
            if not isinstance(proposal, dict)
            else proposal.get("distance"),
        )

    def commit_proposal(self, core: Any, proposal: Any) -> None:
        """Apply ``proposal`` to the **live** engine — the C8.3 Commit.

        Where :meth:`simulate_proposal` mutates only a ``deepcopy`` sandbox,
        this method applies the *very same* structural change to the live
        clustering substrate backing ``core``: the two targets are fused into a
        single new cluster (count-weighted centroid, unioned members and counts)
        and the originals are deleted. Because it delegates to the identical
        :meth:`_apply_proposal` used during rehearsal, the committed world is
        guaranteed to match the simulated sandbox exactly.

        Deleting the two originals in favour of one merged cluster frees a slot
        in the engine's ``max_clusters`` budget, which lets the next anomalous
        vector seed a fresh cluster (resolving a quarantine) on a later tick.

        Call this **only** after a positive policy verdict
        (``DecisionPolicy.evaluate_metrics(...)["accepted"] is True``). A
        rejected proposal must be left un-applied (the Rollback is simply doing
        nothing).
        """
        live_engine = self._resolve_engine(core)
        self._apply_proposal(live_engine, proposal)

    # ── Vital measurement (strictly read-only) ────────────────────────────

    def _measure(self, core: Any, engine: Any, recent_vectors: list[list[float]]) -> dict:
        """Snapshot the three native vitals (S, H, A) for ``engine``.

        All three are computed without mutating ``engine``: no ``assign`` call,
        no centroid update, no predictor or surprise-tracker advance. That is
        what keeps the measurement decoupled from live execution state.

        ``core`` is the live :class:`VectorPredictionCore` (or its
        ``ClusterEngine``), passed in addition to ``engine`` so the prediction
        vital can read the predictor's transitions and the bootstrap anchor
        (``last_cluster_id``) without mutating any state.
        """
        return {
            PREDICTION_ERROR: self._prediction_error(core, engine, recent_vectors),
            ENTROPY: self._entropy(engine, recent_vectors),
            ACTIVE_LOAD: self._active_load(engine),
        }

    def _prediction_error(
        self, core: Any, engine: Any, recent_vectors: list[list[float]]
    ) -> float:
        """S -- mean Markov forecast error (surprise) of ``engine`` over the window.

        For each vector v_i in the window we (a) read-only map v_{i-1} to its
        nearest cluster id, (b) call ``predictor.predict_next(engine, prev_id)``
        to obtain the forecast centroid, and (c) compute the Euclidean distance
        ``||forecast - v_i||``. The mean over the window is the per-observation
        vital on the same scale as :func:`validation.metrics.surprise`.

        Mathematically identical to the Online path
        (``VectorPredictionCore.ingest`` at line 772 of
        ``vector_prediction_core.py``), which uses the same forecast-then-distance
        pipeline. The canonical single-source-of-truth definition lives in
        :func:`validation.shared_metrics_v1.compute_S_surprise` (numpy form);
        this implementation uses the std-lib-only ``euclidean_distance`` helper
        to honour the cognition-layer's import discipline (no ``validation.*`` or
        ``numpy`` imports reach into ``backend.cognition``).

        Read-only contract: ``predict_next`` only reads the predictor's
        ``_transitions`` and ``cluster_sequence``, and calls the pure
        ``get_cluster`` reader on ``engine``; no centroid is updated, no
        transition is recorded, no surprise is tracked. The predictor's and
        engine's state before/after this call is byte-identical.

        Bootstrap: the very first vector has no "previous" observation in the
        window, so we anchor it on the live ``core.last_cluster_id`` when
        available (matching Online's first-observation bootstrap at line 747 of
        ``vector_prediction_core.py``). If no live anchor exists (bare
        ``ClusterEngine`` with no prior context) the first vector uses its own
        nearest cluster id as the predictor's current id, which causes
        ``predict_next`` to return that cluster's own centroid and yield S = 0
        for that single observation -- a degenerate but well-defined fallback.
        """
        clusters = getattr(engine, "clusters", [])
        if not recent_vectors:
            return 0.0

        # Locate the live predictor and bootstrap anchor on `core` (the predictor
        # lives on VectorPredictionCore, not on ClusterEngine). Falls back to a
        # bare ClusterEngine without a predictor if a caller passed one in.
        predictor = getattr(core, "predictor", None)
        if predictor is None:
            predictor = getattr(engine, "predictor", None)
        live_anchor = getattr(core, "last_cluster_id", -1)
        if not isinstance(live_anchor, int):
            live_anchor = -1

        def _nearest_id(vector: list[float]) -> Optional[int]:
            """Read-only nearest-cluster lookup matching the engine's metric."""
            if not clusters:
                return None
            best_id = None
            best_dist = float("inf")
            for cluster in clusters:
                dist = engine._distance(cluster.centroid, vector)
                if dist < best_dist:
                    best_dist = dist
                    best_id = cluster.id
            return best_id

        prev_id: int = live_anchor
        total_error = 0.0
        for vector in recent_vectors:
            # Predict from the previous cluster context.
            if predictor is not None and prev_id >= 0:
                try:
                    predicted = predictor.predict_next(engine, prev_id)
                except Exception:
                    predicted = [0.0] * len(vector)
            else:
                # Degenerate bootstrap: no predictor or no anchor. Use the
                # nearest-cluster centroid of the *current* vector as a
                # well-defined (if uninformative) forecast -- yields S = 0 for
                # this single observation, identical to Online's identity
                # fallback at line 752 of vector_prediction_core.py.
                nid = _nearest_id(vector)
                c = engine.get_cluster(nid) if nid is not None else None
                predicted = c.centroid[:] if c is not None else [0.0] * len(vector)

            total_error += euclidean_distance(predicted, vector)

            # Advance the read-only pointer: the current vector's nearest id
            # becomes the next step's "previous".
            next_id = _nearest_id(vector)
            if next_id is not None:
                prev_id = next_id

        return total_error / len(recent_vectors)

    def _entropy(self, engine: Any, recent_vectors: list[list[float]]) -> float:
        """H — conditional Shannon entropy of the cluster-transition chain.

        Read-only reconstruction of the Markov dynamics the window would induce:
        each vector is mapped to its nearest cluster id (no centroid update),
        consecutive assignments are counted as transitions, and the conditional
        entropy ``H(next | current)`` of that chain is returned in bits. Mirrors
        :func:`validation.metrics.transition_entropy` exactly, but built from a
        sandbox replay rather than the live predictor's history.
        """
        clusters = getattr(engine, "clusters", [])
        if not clusters or len(recent_vectors) < 2:
            return 0.0

        # Nearest-cluster id for each vector (read-only).
        sequence: list[int] = []
        for vector in recent_vectors:
            best_id = None
            best_dist = float("inf")
            for cluster in clusters:
                dist = engine._distance(cluster.centroid, vector)
                if dist < best_dist:
                    best_dist = dist
                    best_id = cluster.id
            if best_id is not None:
                sequence.append(best_id)

        if len(sequence) < 2:
            return 0.0

        # Build first-order transition counts {src: {dst: count}}.
        transitions: dict[int, dict[int, int]] = {}
        for src, dst in zip(sequence[:-1], sequence[1:]):
            row = transitions.setdefault(src, {})
            row[dst] = row.get(dst, 0) + 1

        # Visit-weighted conditional entropy H(next | current), in bits.
        weighted_sum = 0.0
        total_weight = 0.0
        for _src, targets in transitions.items():
            counts = [c for c in targets.values() if c > 0]
            row_total = sum(counts)
            if row_total <= 0:
                continue
            row_h = 0.0
            for c in counts:
                p = c / row_total
                row_h -= p * math.log2(p)
            weighted_sum += row_h * row_total
            total_weight += row_total

        if total_weight <= 0:
            return 0.0
        return weighted_sum / total_weight

    @staticmethod
    def _active_load(engine: Any) -> float:
        """A — structural load: live clusters + spatial volume of anomaly cloud.

        Mirrors :func:`validation.metrics.active_load`: the live cluster count
        plus the trace of the covariance of the quarantined anomaly cloud (the
        sum of per-dimension variances). A cloud of fewer than two vectors has
        no spread and contributes zero volume.
        """
        cluster_count = getattr(engine, "cluster_count", None)
        if cluster_count is None:
            cluster_count = len(getattr(engine, "clusters", []))
        anomaly_vectors = getattr(engine, "anomaly_vectors", []) or []

        volume = 0.0
        n = len(anomaly_vectors)
        if n >= 2:
            dim = min(len(v) for v in anomaly_vectors)
            for d in range(dim):
                column = [v[d] for v in anomaly_vectors]
                mean_d = sum(column) / n
                volume += sum((x - mean_d) ** 2 for x in column) / n

        return float(cluster_count) + volume

    # ── Structural internals ──────────────────────────────────────────────

    @staticmethod
    def _resolve_engine(core: Any):
        """Return the ClusterEngine backing ``core``.

        Accepts a full ``VectorPredictionCore`` (``.cluster_engine``) or a bare
        ``ClusterEngine`` (returned as-is).
        """
        engine = getattr(core, "cluster_engine", None)
        return engine if engine is not None else core

    @staticmethod
    def _proposal_targets(proposal: Any) -> tuple[Optional[int], Optional[int]]:
        """Extract ``(target_a, target_b)`` from a mapping or object proposal."""
        if isinstance(proposal, dict):
            return proposal.get("target_a"), proposal.get("target_b")
        return getattr(proposal, "target_a", None), getattr(proposal, "target_b", None)

    def _apply_proposal(self, engine: Any, proposal: Any) -> None:
        """Merge ``target_a`` and ``target_b`` into a new cluster in ``engine``.

        The two source clusters are fused into a single new cluster whose
        centroid is their count-weighted mean and whose members/count are the
        union, then both originals are removed. Operates on the (already
        sandboxed, or live-at-commit) ``engine`` only.

        Unknown or missing targets are treated as a no-op so a malformed
        proposal can never crash the rehearsal — it simply scores identically to
        the live brain (every vital delta is zero).
        """
        target_a, target_b = self._proposal_targets(proposal)
        if target_a is None or target_b is None or target_a == target_b:
            return

        cluster_a = engine.get_cluster(target_a)
        cluster_b = engine.get_cluster(target_b)
        if cluster_a is None or cluster_b is None:
            return

        count_a, count_b = cluster_a.count, cluster_b.count
        total = count_a + count_b
        if total <= 0:
            return

        merged_centroid = [
            (a * count_a + b * count_b) / total
            for a, b in zip(cluster_a.centroid, cluster_b.centroid)
        ]

        # Build the new merged cluster, preserving the combined evidence.
        new_id = engine._next_id
        engine._next_id += 1
        merged = Cluster(new_id, merged_centroid)
        merged.count = total
        merged.members = [m[:] for m in cluster_a.members] + [
            m[:] for m in cluster_b.members
        ]

        # Delete the originals, then install the merged cluster.
        engine.clusters = [
            c for c in engine.clusters if c.id not in (target_a, target_b)
        ]
        engine.clusters.append(merged)


__all__ = ["ReplayEngine"]
