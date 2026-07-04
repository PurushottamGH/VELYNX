"""
VELYNX Milestone C7 — Vector Prediction Core.

Replaces discrete symbol-matching with continuous vector-matching.
Standard-library only: math, collections.

Core capabilities:
- Euclidean-distance surprisal with threshold-based [SURPRISE] events
- Online K-Means / dynamic distance-bounding cluster substrate
- Sequence-based next-vector prediction via Markovian cluster transitions
"""

import math
import statistics
from collections import deque, Counter, defaultdict
from dataclasses import dataclass
from typing import Optional


# ── Vector Math ───────────────────────────────────────────────────────

def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between two vectors of equal dimension."""
    s = 0.0
    for ai, bi in zip(a, b):
        d = ai - bi
        s += d * d
    return math.sqrt(s)


def mean_squared_error(a: list[float], b: list[float]) -> float:
    """Mean squared error between two vectors."""
    s = 0.0
    n = 0
    for ai, bi in zip(a, b):
        d = ai - bi
        s += d * d
        n += 1
    return s / n if n else 0.0


def vector_add(a: list[float], b: list[float]) -> list[float]:
    """Element-wise addition of two vectors."""
    return [ai + bi for ai, bi in zip(a, b)]


def vector_scale(v: list[float], scalar: float) -> list[float]:
    """Scale a vector by a scalar."""
    return [vi * scalar for vi in v]


def vector_mean(vectors: list[list[float]]) -> list[float]:
    """Element-wise mean of a list of same-dimension vectors."""
    if not vectors:
        return []
    n = len(vectors)
    dim = len(vectors[0])
    summed = [0.0] * dim
    for v in vectors:
        for i in range(dim):
            summed[i] += v[i]
    return [s / n for s in summed]


# ── Anomaly Record (observability) ────────────────────────────────────

@dataclass
class AnomalyRecord:
    """Temporal lifecycle record for a single quarantined anomaly vector.

    This is **pure observability**: opening, updating, or reading these
    records never alters how the :class:`ClusterEngine` assigns vectors,
    forms clusters, or predicts. A record only annotates *when* a vector
    was first quarantined, when it was last touched, and where it sits in
    its lifecycle — so the system's behaviour under pressure (e.g. when the
    ``max_clusters`` budget is exhausted) becomes measurable after the fact.

    Status transitions
    -------------------
    * ``active``   -- currently quarantined; not yet explained.
    * ``absorbed`` -- later captured into a (new or existing) cluster,
                      typically once a LatentCause absorber matched it.
    * ``retired``  -- aged out of quarantine without ever being absorbed.
    """

    id: int
    first_seen_tick: int
    last_seen_tick: int
    status: str = "active"


# ── Cluster (substrate atom) ──────────────────────────────────────────

class Cluster:
    """A single proximity cluster with an online-updated centroid."""

    __slots__ = ("id", "centroid", "count", "members")

    def __init__(self, cluster_id: int, centroid: list[float]):
        self.id = cluster_id
        self.centroid = centroid[:]  # copy
        self.count = 1
        self.members: list[list[float]] = [centroid[:]]

    def update(self, vector: list[float]) -> None:
        """Online centroid update: incremental weighted mean."""
        self.count += 1
        n = self.count
        self.centroid = [
            (c * (n - 1) + v) / n
            for c, v in zip(self.centroid, vector)
        ]
        self.members.append(vector[:])

    def distance_to(self, vector: list[float]) -> float:
        """Euclidean distance from centroid to vector."""
        return euclidean_distance(self.centroid, vector)

    def __repr__(self) -> str:
        c = [round(x, 4) for x in self.centroid]
        return f"Cluster({self.id}, centroid={c}, count={self.count})"


# ── Surprise Event ────────────────────────────────────────────────────

class SurpriseEvent:
    """Record of a [SURPRISE] event — prediction error exceeding threshold."""

    __slots__ = ("observed", "predicted", "error", "threshold",
                 "cluster_id", "is_anomaly", "timestamp")

    _counter = 0

    def __init__(self, observed: list[float], predicted: list[float],
                 error: float, threshold: float, cluster_id: int,
                 is_anomaly: bool = False):
        SurpriseEvent._counter += 1
        self.observed = observed[:]
        self.predicted = predicted[:]
        self.error = error
        self.threshold = threshold
        self.cluster_id = cluster_id
        self.is_anomaly = is_anomaly
        self.timestamp = SurpriseEvent._counter

    def __repr__(self) -> str:
        tag = "ANOMALY" if self.is_anomaly else "SURPRISE"
        return (
            f"[{tag} #{self.timestamp}] "
            f"error={self.error:.4f} (threshold={self.threshold:.4f}), "
            f"cluster={self.cluster_id}"
        )


# ── Cluster Engine (Online K-Means / Distance-Bounding) ──────────────

class ClusterEngine:
    """Lightweight online clustering substrate for sensory vectors.

    Each incoming vector is assigned to the nearest cluster centroid if
    within *proximity_threshold*.  If no cluster is close enough, the
    vector is quarantined as an anomaly and may optionally seed a new
    cluster via *auto_seed*.
    """

    def __init__(self, proximity_threshold: float = 0.25,
                 auto_seed: bool = True, max_clusters: int = 50,
                 policy_weights: Optional[dict] = None):
        self.proximity_threshold = proximity_threshold
        self.auto_seed = auto_seed
        self.max_clusters = max_clusters
        self.clusters: list[Cluster] = []
        self._next_id = 0
        self.anomaly_count = 0
        self.anomaly_vectors: list[list[float]] = []

        # ── Externalised free-energy coupling coefficients (C8 research) ──
        #: The ``(lam, mu, nu)`` energy weights resolved from the experiment's
        #: ``decision_policy`` config section (see
        #: :func:`backend.cognition.decision_policy.resolve_coefficients`).
        #: They are carried here purely so the live clustering substrate and
        #: the merge-time :class:`DecisionPolicy` share a *single* config-driven
        #: source of truth for ablation studies. **Pure metadata**: the cluster
        #: engine never reads these for assignment, seeding, or any acceptance
        #: decision — the Free-Energy acceptance logic is untouched.
        self.policy_weights: dict = dict(policy_weights) if policy_weights else {}

        # ── Anomaly lifecycle observability (pure bookkeeping) ────────
        #: Monotonic logical clock; advanced once per :meth:`assign` call so
        #: every quarantine event can be stamped with a tick. Never read by
        #: the cognitive path — only by the observability layer.
        self.tick: int = 0
        #: One :class:`AnomalyRecord` per *genuinely quarantined* vector
        #: (the budget-exhausted ``cluster_id == -1`` case). Kept for the
        #: engine's lifetime so anomaly lifetimes stay measurable.
        self.anomaly_records: list[AnomalyRecord] = []
        self._next_anomaly_id: int = 0
        #: Private quarantined-vector store keyed by record id, used solely
        #: to re-match a quarantined vector against an absorber's cause.
        self._quarantine_vectors: dict[int, list[float]] = {}

        # ── Top-down attention (C7 closed feedback loop) ──────────────
        #: Per-dimension weights warping the Euclidean metric once a
        #: LatentCause has been wired back in via ``apply_attention``.
        #: ``None`` ⇒ the raw, unweighted metric is in force.
        self.dim_weights: Optional[list[float]] = None
        #: Registered LatentCause absorbers. Each entry pins a discovered
        #: invariant to a *dedicated* cluster so that any future vector
        #: matching its axis-aligned bounds is captured by the predictor
        #: rather than being pushed back into the anomaly quarantine.
        #: Shape: ``[{"cause", "signature", "cluster_id"}]``.
        self._absorbers: list[dict] = []

    def assign(self, vector: list[float]) -> tuple[int, bool]:
        """Assign vector to nearest cluster or quarantine as anomaly.

        Returns ``(cluster_id, is_anomaly)``.
        ``cluster_id`` is -1 when the vector is quarantined.
        """
        # Advance the observability clock once per ingested vector. This is
        # bookkeeping only and does not influence assignment.
        self.tick += 1

        # ── Quarantine Freeze ─────────────────────────────────────────
        # Top-down attention takes priority over bottom-up proximity: a
        # vector that satisfies a registered LatentCause's bounds is
        # absorbed by its dedicated cluster and can never be quarantined,
        # regardless of the cluster budget. This is what closes the loop —
        # a discovered cause permanently reshapes what the predictor will
        # accept as "explained".
        absorbed = self._absorb(vector)
        if absorbed is not None:
            return absorbed, False

        if not self.clusters:
            return self._create_cluster(vector), False

        best_cluster, best_dist = self._nearest(vector)

        if best_dist <= self.proximity_threshold:
            best_cluster.update(vector)
            return best_cluster.id, False

        # Anomaly: outside proximity threshold
        self.anomaly_count += 1
        self.anomaly_vectors.append(vector[:])

        if self.auto_seed and len(self.clusters) < self.max_clusters:
            cid = self._create_cluster(vector)
            return cid, False

        # Budget exhausted (or auto-seed disabled): the vector is genuinely
        # quarantined. Open an active AnomalyRecord so the temporal lifecycle
        # of this limit-driven quarantine is observable. This does not change
        # the cognitive outcome — the vector is still quarantined (-1).
        self._open_quarantine(vector)
        return -1, True

    def assign_batch(self, vectors: list[list[float]]) -> list[tuple[int, bool]]:
        """Assign a batch of vectors in one call."""
        return [self.assign(v) for v in vectors]

    def _nearest(self, vector: list[float]) -> tuple[Optional[Cluster], float]:
        best: Optional[Cluster] = None
        best_dist = float("inf")
        for cl in self.clusters:
            d = self._distance(cl.centroid, vector)
            if d < best_dist:
                best_dist = d
                best = cl
        return best, best_dist

    def _distance(self, centroid: list[float], vector: list[float]) -> float:
        """Distance from a centroid to a vector under the current metric.

        Falls back to plain Euclidean until ``apply_attention`` installs a
        ``dim_weights`` vector, after which the metric is a weighted
        Euclidean that amplifies the invariant dimension(s) a discovered
        LatentCause flagged — so the substrate physically *perceives* the
        attended axis as dominating proximity.
        """
        w = self.dim_weights
        if w is None:
            return euclidean_distance(centroid, vector)
        s = 0.0
        for ci, vi, wi in zip(centroid, vector, w):
            d = ci - vi
            s += wi * d * d
        return math.sqrt(s)

    # --- attention-driven absorption (C7 closed feedback loop) ----------

    def register_attention(self, cause, weights: list[float]) -> None:
        """Install a LatentCause as a top-down attention controller.

        Two effects, both permanent for the engine's lifetime:

        1. The distance metric is re-weighted via ``weights`` so the
           invariant dimensions dominate every future proximity test.
        2. The cause is registered as an *absorber*: any subsequent vector
           matching its axis-aligned bounds is routed to a dedicated
           cluster instead of the quarantine (the Quarantine Freeze).

        Re-registering an equivalent cause (same predicate signature) is a
        no-op beyond refreshing the metric, so repeated mining of the same
        regime cannot spawn duplicate absorbers.
        """
        self.dim_weights = list(weights) if weights is not None else None
        signature = self._cause_signature(cause)
        for ab in self._absorbers:
            if ab["signature"] == signature:
                ab["cause"] = cause
                return
        self._absorbers.append(
            {"cause": cause, "signature": signature, "cluster_id": None}
        )

    @staticmethod
    def _cause_signature(cause) -> frozenset:
        """A hashable identity for a cause, tolerant of cause flavours."""
        variable = getattr(cause, "variable", None)
        preds = getattr(variable, "predicates", None) if variable else None
        if preds:
            return frozenset(
                (p.index, getattr(p, "op", "="), getattr(p, "threshold", 0.0))
                for p in preds
            )
        idx = getattr(cause, "index", None)
        return frozenset({(idx, "=", 0.0)}) if idx is not None else frozenset()

    def _absorb(self, vector: list[float]) -> Optional[int]:
        """Capture ``vector`` into an attention cluster if a cause matches.

        Returns the dedicated cluster id when the vector falls inside a
        registered cause's bounds (creating that cluster lazily on the
        first match), else ``None``. A dedicated cluster is allowed to be
        created even when the ``max_clusters`` budget is exhausted: the
        whole point of attention is that an *understood* regime always
        earns representation.
        """
        for ab in self._absorbers:
            cause = ab["cause"]
            try:
                matched = cause.matches(vector)
            except Exception:  # noqa: BLE001 - a malformed cause never blocks ingest
                matched = False
            if not matched:
                continue
            cluster = (
                self.get_cluster(ab["cluster_id"])
                if ab["cluster_id"] is not None
                else None
            )
            if cluster is None:
                ab["cluster_id"] = self._create_cluster(vector)
            else:
                cluster.update(vector)
            # Observability: any still-active anomalies that this same cause
            # now explains transition to 'absorbed' (their record is updated,
            # never deleted) — see :meth:`_absorb_quarantined`.
            self._absorb_quarantined(cause)
            return ab["cluster_id"]
        return None

    def _create_cluster(self, vector: list[float]) -> int:
        cid = self._next_id
        self._next_id += 1
        self.clusters.append(Cluster(cid, vector))
        return cid

    # --- anomaly lifecycle bookkeeping (pure observability) -------------

    def _open_quarantine(self, vector: list[float]) -> AnomalyRecord:
        """Open an ``active`` :class:`AnomalyRecord` for a quarantined vector.

        Called only from the genuine-quarantine branch of :meth:`assign`
        (budget exhausted / auto-seed off). The vector is stashed privately,
        keyed by record id, so it can later be re-matched against an
        absorber's cause without bloating the public record.
        """
        record = AnomalyRecord(
            id=self._next_anomaly_id,
            first_seen_tick=self.tick,
            last_seen_tick=self.tick,
            status="active",
        )
        self._next_anomaly_id += 1
        self.anomaly_records.append(record)
        self._quarantine_vectors[record.id] = vector[:]
        return record

    def _absorb_quarantined(self, cause) -> None:
        """Flip active anomalies that ``cause`` now explains to ``absorbed``.

        Pure bookkeeping invoked when an absorber captures a live vector:
        every still-``active`` quarantined vector that the same cause also
        matches is marked ``absorbed`` and stamped with the current tick.
        Records are updated in place — never deleted — so their lifetime
        (``last_seen_tick - first_seen_tick``) stays measurable.
        """
        for record in self.anomaly_records:
            if record.status != "active":
                continue
            vec = self._quarantine_vectors.get(record.id)
            if vec is None:
                continue
            try:
                matched = cause.matches(vec)
            except Exception:  # noqa: BLE001 - a malformed cause never blocks ingest
                matched = False
            if matched:
                record.status = "absorbed"
                record.last_seen_tick = self.tick

    def reingest_quarantined(self, record_id: int) -> bool:
        """Re-assign a quarantined vector to the *current* clusters (C8 drain).

        After a consolidation merge frees a slot in the ``max_clusters`` budget
        (and reshapes centroids), a previously-quarantined anomaly may now have
        a home. This method re-runs the assignment decision for the vector
        behind ``record_id`` against the live clusters:

        * If an attention absorber matches, or the nearest centroid is within
          ``proximity_threshold``, the vector *joins* that cluster (centroid
          updated).
        * Otherwise, if ``auto_seed`` is on and the budget now has room, the
          vector *seeds* a fresh cluster.

        On success the record is marked ``absorbed`` (resolved), stamped with
        the current tick, and dropped from the private quarantine store; the
        method returns ``True``. If the vector still cannot be placed (budget
        exhausted and nothing close enough) the record is left ``active`` and
        the method returns ``False``.

        Unlike :meth:`assign`, a failed re-ingest **never opens a new
        quarantine record** and never advances the logical clock, so draining
        the queue cannot create duplicate records or distort anomaly lifetimes.
        Only ``active`` records can be re-ingested; any other id is a no-op
        returning ``False``.
        """
        record = None
        for r in self.anomaly_records:
            if r.id == record_id and r.status == "active":
                record = r
                break
        if record is None:
            return False

        vector = self._quarantine_vectors.get(record_id)
        if vector is None:
            return False

        placed = False

        # Priority 1: a registered cause absorbs it (matches assign() order).
        if self._absorb(vector) is not None:
            placed = True
        elif not self.clusters:
            # Priority 2a: no clusters at all -> seed unconditionally.
            self._create_cluster(vector)
            placed = True
        else:
            best_cluster, best_dist = self._nearest(vector)
            if best_cluster is not None and best_dist <= self.proximity_threshold:
                # Priority 2b: close enough to an existing cluster -> join.
                best_cluster.update(vector)
                placed = True
            elif self.auto_seed and len(self.clusters) < self.max_clusters:
                # Priority 3: budget freed by the merge -> seed a new cluster.
                self._create_cluster(vector)
                placed = True

        if not placed:
            return False

        record.status = "absorbed"
        record.last_seen_tick = self.tick
        self._quarantine_vectors.pop(record_id, None)
        return True

    def retire_anomaly(self, record_id: int) -> bool:
        """Mark an active anomaly as ``retired`` (aged out, never absorbed).

        Returns ``True`` if a matching active record was retired. Retiring
        stamps ``last_seen_tick`` and counts toward resolved anomalies in
        :meth:`get_memory_summary`. Provided for callers that age out stale
        quarantines; the engine never retires records on its own.
        """
        for record in self.anomaly_records:
            if record.id == record_id and record.status == "active":
                record.status = "retired"
                record.last_seen_tick = self.tick
                return True
        return False

    def get_memory_summary(self) -> dict:
        """Summarise cluster memory and anomaly-quarantine lifecycles.

        Returns a dict with:

        * ``total_clusters``           -- live cluster count.
        * ``average_anomaly_lifetime`` -- mean ``last - first`` tick span over
          resolved (absorbed or retired) anomalies; ``0.0`` when none.
        * ``longest_anomaly_lifetime`` -- max tick span over resolved
          anomalies; ``0`` when none.
        * ``active_anomalies_count``   -- anomalies still quarantined.
        * ``resolved_anomalies_count`` -- anomalies absorbed or retired.
        """
        resolved = [
            r for r in self.anomaly_records
            if r.status in ("absorbed", "retired")
        ]
        active_count = sum(
            1 for r in self.anomaly_records if r.status == "active"
        )
        lifetimes = [r.last_seen_tick - r.first_seen_tick for r in resolved]
        avg_lifetime = (sum(lifetimes) / len(lifetimes)) if lifetimes else 0.0
        longest_lifetime = max(lifetimes) if lifetimes else 0
        return {
            "total_clusters": self.cluster_count,
            "average_anomaly_lifetime": avg_lifetime,
            "longest_anomaly_lifetime": longest_lifetime,
            "active_anomalies_count": active_count,
            "resolved_anomalies_count": len(resolved),
        }

    @property
    def cluster_count(self) -> int:
        return len(self.clusters)

    @property
    def total_vectors_observed(self) -> int:
        return sum(c.count for c in self.clusters) + self.anomaly_count

    def get_cluster(self, cluster_id: int) -> Optional[Cluster]:
        for c in self.clusters:
            if c.id == cluster_id:
                return c
        return None

    def __repr__(self) -> str:
        return (
            f"ClusterEngine(clusters={self.cluster_count}, "
            f"anomalies={self.anomaly_count}, "
            f"total={self.total_vectors_observed})"
        )


# ── Surprise Tracker ─────────────────────────────────────────────────

class SurpriseTracker:
    """Tracks prediction error and fires [SURPRISE] events.

    Uses running statistics (mean, std) of historical error to derive an
    *adaptive* threshold when no static threshold is provided.
    """

    def __init__(self, static_threshold: Optional[float] = None,
                 window: int = 100):
        self.static_threshold = static_threshold
        self.window = window
        self.events: list[SurpriseEvent] = []
        self._recent_errors: deque[float] = deque(maxlen=window)

    @property
    def adaptive_threshold(self) -> float:
        """Mean + 1.5 * sigma of recent errors, or 0.15 fallback."""
        if len(self._recent_errors) < 5:
            return 0.15
        mu = statistics.mean(self._recent_errors)
        sigma = (
            statistics.stdev(self._recent_errors)
            if len(self._recent_errors) > 1
            else 0.05
        )
        return mu + 1.5 * sigma

    @property
    def threshold(self) -> float:
        if self.static_threshold is not None:
            return self.static_threshold
        return self.adaptive_threshold

    def evaluate(self, observed: list[float], predicted: list[float],
                 cluster_id: int,
                 is_anomaly: bool = False) -> Optional[SurpriseEvent]:
        """Compute prediction error, log [SURPRISE] if threshold exceeded.

        Returns the SurpriseEvent if triggered, else None.
        """
        error = euclidean_distance(predicted, observed)
        self._recent_errors.append(error)

        if error > self.threshold:
            event = SurpriseEvent(observed, predicted, error,
                                  self.threshold, cluster_id, is_anomaly)
            self.events.append(event)
            return event
        return None

    @property
    def surprise_rate(self) -> float:
        """Fraction of evaluations that triggered surprise in the recent window."""
        if not self._recent_errors:
            return 0.0
        recent = list(self._recent_errors)
        t = self.threshold
        return sum(1 for e in recent if e > t) / len(recent)

    def __repr__(self) -> str:
        return (
            f"SurpriseTracker(threshold={self.threshold:.4f}, "
            f"events={len(self.events)}, "
            f"rate={self.surprise_rate:.3f})"
        )


# ── Prediction Engine (Markovian Cluster Transitions) ────────────────

class VectorPredictor:
    """Forecasts the next sensory vector from cluster transition history.

    Maintains a first-order Markov chain over cluster IDs.  Given a
    current cluster, it selects the most probable next cluster and
    returns that cluster's centroid as the prediction.  Falls back to
    the current-cluster centroid when no transitions are known.
    """

    def __init__(self, history_depth: int = 10):
        self.history_depth = history_depth
        self.cluster_sequence: list[int] = []
        self._transitions: dict[int, Counter] = defaultdict(Counter)

    def observe_cluster(self, cluster_id: int) -> None:
        """Record a cluster assignment into the sequence history."""
        if self.cluster_sequence:
            prev = self.cluster_sequence[-1]
            self._transitions[prev][cluster_id] += 1
        self.cluster_sequence.append(cluster_id)
        if len(self.cluster_sequence) > self.history_depth:
            self.cluster_sequence.pop(0)

    def predict_next(self, cluster_engine: ClusterEngine,
                     current_cluster_id: int) -> list[float]:
        """Predict the next sensory vector.

        Strategy:
        1. If transitions are known from *current_cluster_id*, pick the
           most likely next cluster and return its centroid.
        2. If no transitions exist, return the current cluster centroid.
        3. If the current cluster is anomalous (unknown), return a mean
           of the most recent known cluster centroids.
        """
        # 1 — Most likely next cluster
        if current_cluster_id in self._transitions:
            trans = self._transitions[current_cluster_id]
            if trans:
                most_likely = trans.most_common(1)[0][0]
                cluster = cluster_engine.get_cluster(most_likely)
                if cluster:
                    return cluster.centroid[:]

        # 2 — Current centroid
        cluster = cluster_engine.get_cluster(current_cluster_id)
        if cluster:
            return cluster.centroid[:]

        # 3 — Fallback: mean of last few known centroids
        recent = [
            cluster_engine.get_cluster(cid)
            for cid in self.cluster_sequence[-3:]
        ]
        recent = [c for c in recent if c is not None]
        if recent:
            return vector_mean([c.centroid for c in recent])
        return [0.0]

    def transition_matrix(self) -> dict[int, dict[int, int]]:
        """Return a copy of the transition matrix for inspection."""
        return {k: dict(v) for k, v in self._transitions.items()}

    @property
    def sequence_length(self) -> int:
        return len(self.cluster_sequence)

    def __repr__(self) -> str:
        total_trans = sum(len(v) for v in self._transitions.values())
        return (
            f"VectorPredictor(seq_len={self.sequence_length}, "
            f"transitions={total_trans})"
        )


# ── Core Orchestrator ─────────────────────────────────────────────────

class VectorPredictionCore:
    """Top-level cognitive prediction engine for continuous vector inputs.

    Integrates:
    - :class:`ClusterEngine` — online clustering substrate
    - :class:`SurpriseTracker` — prediction-error monitoring with events
    - :class:`VectorPredictor` — Markovian next-vector forecasting
    """

    def __init__(self, proximity_threshold: float = 0.25,
                 surprise_threshold: Optional[float] = None,
                 history_depth: int = 10,
                 auto_seed: bool = True,
                 max_clusters: int = 50,
                 focus_mult: float = 10.0,
                 suppress_floor: float = 0.05,
                 decision_policy_weights: Optional[dict] = None):
        self.cluster_engine = ClusterEngine(
            proximity_threshold=proximity_threshold,
            auto_seed=auto_seed,
            max_clusters=max_clusters,
            policy_weights=decision_policy_weights,
        )
        self.surprise_tracker = SurpriseTracker(
            static_threshold=surprise_threshold,
        )
        self.predictor = VectorPredictor(history_depth=history_depth)
        self.last_prediction: Optional[list[float]] = None
        self.last_cluster_id: int = -1
        #: Attention defaults — how hard ``apply_attention`` amplifies the
        #: invariant dimension(s) and how far it suppresses the rest.
        self.attention_focus_mult: float = focus_mult
        self.attention_suppress_floor: float = suppress_floor
        #: Live attention metric installed by ``apply_attention`` (or None).
        self.attention_weights: Optional[list[float]] = None
        #: Indices of the dimension(s) currently being attended to.
        self.attended_dimensions: list[int] = []
        #: Every LatentCause wired back into the predictor, in order.
        self.attention_causes: list = []

    def ingest(self, observation: list[float]) -> dict:
        """Process a raw sensor vector end-to-end.

        1. Generate a prediction (from the previous cluster state).
        2. Cluster-assign the observation.
        3. Compute surprisal / prediction error.
        4. Register a [SURPRISE] event if the threshold is breached.

        Returns a diagnostic dict.
        """
        # 1 — Predict (from previous cluster)
        if self.last_cluster_id >= 0:
            predicted = self.predictor.predict_next(
                self.cluster_engine, self.last_cluster_id,
            )
        else:
            predicted = observation[:]  # first observation: identity

        self.last_prediction = predicted[:]

        # 2 — Cluster assignment
        cluster_id, is_anomaly = self.cluster_engine.assign(observation)

        # 3 — Surprisal
        surprise = self.surprise_tracker.evaluate(
            observation, predicted, cluster_id, is_anomaly,
        )

        # 4 — Update predictor sequence
        if cluster_id >= 0:
            self.predictor.observe_cluster(cluster_id)
            self.last_cluster_id = cluster_id

        return {
            "observation": observation[:],
            "predicted": predicted[:],
            "error": euclidean_distance(predicted, observation),
            "cluster_id": cluster_id,
            "is_anomaly": is_anomaly,
            "cluster_count": self.cluster_engine.cluster_count,
            "surprise": surprise,
            "anomaly_count": self.cluster_engine.anomaly_count,
        }

    def ingest_batch(self, observations: list[list[float]]) -> list[dict]:
        """Process a batch of observations sequentially."""
        return [self.ingest(o) for o in observations]

    def apply_attention(self, cause, *,
                        focus_mult: Optional[float] = None,
                        suppress_floor: Optional[float] = None) -> Optional[list[float]]:
        """Wire a discovered LatentCause back into the prediction engine.

        This is the keystone of the C7 closed feedback loop
        (Discovery → Attention → Prediction Improvement). It reads the
        cause's axis-aligned predicates — the invariant dimensions the
        discovery layer flagged — and:

        1. **Re-weights the distance metric.** The attended dimension(s)
           are amplified by ``focus_mult`` while every other dimension is
           suppressed toward ``suppress_floor``, so the K-Means substrate's
           Euclidean proximity is now dominated by the invariant. (If
           "Sensor 1" is the invariant, a difference along Sensor 1 now
           counts for far more than the noisy dimensions.)
        2. **Freezes the quarantine.** The cause is registered as an
           absorber on the cluster engine: any future vector inside its
           bounds is captured into a dedicated cluster instead of being
           pushed back into the anomaly quarantine.

        Parameters
        ----------
        cause :
            A LatentCause exposing ``variable.predicates`` (each with an
            ``index``), or any object exposing an ``index`` attribute and a
            ``matches(vector)`` method.
        focus_mult, suppress_floor :
            Optional per-call overrides of the engine's attention defaults.

        Returns
        -------
        list[float] | None
            The installed weight vector, or ``None`` when the cause carries
            no usable dimensions / dimensionality cannot be determined.
        """
        fm = self.attention_focus_mult if focus_mult is None else focus_mult
        sf = self.attention_suppress_floor if suppress_floor is None else suppress_floor

        indices = self._cause_indices(cause)
        dim = self._infer_dim(indices)
        if dim <= 0 or not indices:
            return None

        weights = [sf] * dim
        for idx in indices:
            if 0 <= idx < dim:
                weights[idx] = fm

        self.cluster_engine.register_attention(cause, weights)
        self.attention_weights = weights
        self.attended_dimensions = sorted(i for i in indices if 0 <= i < dim)
        self.attention_causes.append(cause)
        return weights

    @staticmethod
    def _cause_indices(cause) -> list[int]:
        """Extract the attended dimension indices from a cause.

        Tolerant of both the predicate-based LatentCause (the discovery
        layer's ``variable.predicates``) and the lightweight single-index
        cause flavour used by the attention modulator.
        """
        variable = getattr(cause, "variable", None)
        preds = getattr(variable, "predicates", None) if variable else None
        if preds:
            return [p.index for p in preds]
        idx = getattr(cause, "index", None)
        return [idx] if idx is not None else []

    def _infer_dim(self, indices: list[int]) -> int:
        """Best-effort sensor-vector dimensionality for weight construction."""
        if self.cluster_engine.clusters:
            return len(self.cluster_engine.clusters[0].centroid)
        if self.last_prediction:
            return len(self.last_prediction)
        return (max(indices) + 1) if indices else 0

    def get_surprise_events(self, limit: int = 10) -> list[SurpriseEvent]:
        """Return the most recent surprise events."""
        return self.surprise_tracker.events[-limit:]

    def get_memory_summary(self) -> dict:
        """Cluster + anomaly-lifecycle observability for the whole core.

        Thin delegate to :meth:`ClusterEngine.get_memory_summary`, exposing
        the memory/anomaly vitals at the orchestrator's public surface.
        """
        return self.cluster_engine.get_memory_summary()

    @property
    def summary(self) -> dict:
        return {
            "clusters": self.cluster_engine.cluster_count,
            "anomalies": self.cluster_engine.anomaly_count,
            "total_observed": self.cluster_engine.total_vectors_observed,
            "surprise_events": len(self.surprise_tracker.events),
            "surprise_rate": self.surprise_tracker.surprise_rate,
            "threshold": self.surprise_tracker.threshold,
            "history_depth": self.predictor.sequence_length,
        }

    def __repr__(self) -> str:
        s = self.summary
        return (
            f"VectorPredictionCore("
            f"clusters={s['clusters']}, anomalies={s['anomalies']}, "
            f"surprises={s['surprise_events']}, "
            f"rate={s['surprise_rate']:.3f})"
        )


# ── Mock __main__ Demo ────────────────────────────────────────────────

def _generate_noisy_stream(
    base_period: float = 6.0,
    noise_scale: float = 0.08,
    drift_scale: float = 0.005,
    dim: int = 4,
    steps: int = 80,
    seed: int = 42,
) -> list[list[float]]:
    """Synthetic noisy sensor stream with underlying periodicity.

    Each dimension follows a sine-wave base with additive Gaussian noise
    and a slow random-walk drift.
    """
    import random as _random

    rng = _random.Random(seed)
    phases = [rng.random() * 2 * math.pi for _ in range(dim)]
    drifts = [0.0] * dim

    stream = []
    for t in range(steps):
        vec = []
        for d in range(dim):
            base = 0.55 + 0.25 * math.sin(
                2 * math.pi * t / base_period + phases[d]
            )
            drifts[d] += rng.gauss(0, drift_scale)
            drifts[d] = max(-0.2, min(0.2, drifts[d]))
            noise = rng.gauss(0, noise_scale)
            val = base + drifts[d] + noise
            val = max(0.0, min(1.0, val))
            vec.append(round(val, 4))
        stream.append(vec)
    return stream


def demo():
    """Demonstrate VectorPredictionCore on a synthetic noisy stream.

    Pure Python, no external dependencies.
    """
    print("=" * 68)
    print("  VELYNX — Vector Prediction Core Demo (Milestone C7)")
    print("  Standard-Library Prediction Engine")
    print("=" * 68)

    core = VectorPredictionCore(
        proximity_threshold=0.15,
        surprise_threshold=0.20,
        history_depth=8,
        auto_seed=True,
        max_clusters=30,
    )

    stream = _generate_noisy_stream(
        base_period=6.0,
        noise_scale=0.08,
        drift_scale=0.005,
        dim=4,
        steps=60,
        seed=42,
    )

    dim = len(stream[0])
    print(f"\nStream: {len(stream)} observations, dim={dim}")
    print()
    header = f"{'#':>3} | {'Obs (first 3 dims)':^26} | {'Pred (first 3 dims)':^26} | {'Error':>6} | {'Clst':>3} | Event"
    print(header)
    print("-" * len(header))

    for i, obs in enumerate(stream):
        result = core.ingest(obs)
        err = f"{result['error']:.4f}"
        cid = f"{result['cluster_id']}" if result["cluster_id"] >= 0 else "—"

        obs_s = f"[{', '.join(f'{x:.2f}' for x in obs[:3])}, ...]"
        pred_s = (
            f"[{', '.join(f'{x:.2f}' for x in result['predicted'][:3])}, ...]"
        )

        event = ""
        if result["surprise"]:
            event = str(result["surprise"])
        elif result["is_anomaly"]:
            event = "⛔ ANOMALY (quarantined)"

        print(f"{i:>3} | {obs_s:^26} | {pred_s:^26} | {err:>6} | {cid:>3} | {event}")

    s = core.summary
    print()
    print("=" * 68)
    print("  Final State")
    print("=" * 68)
    print(f"  Clusters formed:    {s['clusters']}")
    print(f"  Anomalies seen:     {s['anomalies']}")
    print(f"  Total observations: {s['total_observed']}")
    print(f"  Surprise events:    {s['surprise_events']}")
    print(f"  Surprise rate:      {s['surprise_rate']:.3f}")
    print(f"  Threshold:          {s['threshold']:.4f}")
    print(f"  History depth:      {s['history_depth']}")

    if core.surprise_tracker.events:
        print("\n  Recent [SURPRISE] Events:")
        for evt in core.get_surprise_events(5):
            print(f"    {evt}")

    print("\n  Clusters:")
    for cl in core.cluster_engine.clusters:
        print(f"    {cl}")

    print("\n  Transition Matrix:")
    tm = core.predictor.transition_matrix()
    for src, targets in sorted(tm.items()):
        print(f"    Cluster {src} -> {dict(targets)}")

    print("\n  [OK] Demo complete.")


if __name__ == "__main__":
    demo()
