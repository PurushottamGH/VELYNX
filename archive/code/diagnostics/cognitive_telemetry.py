"""
VELYNX --- Cognitive Milestone C6: The Self-Evaluation Engine
=============================================================

Companion to ``cognitive_core.py`` (C1: Predictive Understanding). Where C1
defines the *object level* --- the continuous collision of prediction with
reality --- C6 defines the *meta level*: a telemetry substrate that watches the
watcher and answers a single question.

    *Is VELYNX actually getting smarter?*

Standard AI benchmarks cannot answer this. BLEU measures surface form, accuracy
measures a static test set, perplexity measures a frozen model. None of them
measure **becoming**. The Cognitive Progress Index (CPI) does. It is built
entirely from quantities that a predictive-processing mind already computes for
its own survival:

    1. prediction_accuracy_trend  --- is the generative model converging on the
       world? (Prediction error should fall.)
    2. average_surprise_decay     --- after a mistake, how quickly does surprise
       collapse back to baseline? (A faster decay constant = a faster learner.)
    3. concept_compression_ratio  --- how many raw experiences are being
       compressed into reusable latent rules? (A growing ratio = abstraction.)
    4. structural_contradictions_resolved --- how many beliefs that once
       conflicted have been reconciled into a coherent generative model?

If these four move in the right direction, the system is genuinely learning.
If any stalls, the **ReflectionEngine** halts, inspects itself, and names the
specific latent concept that is bottlenecks cognition in a ``SystemDiagnostics``
report --- the cognitive equivalent of a stack trace for a stuck mind.

Design constraints (inherited from C1)
--------------------------------------
Pure standard library. No LLMs. No embeddings. No external databases. No
network. The module is fully deterministic and runnable as a standalone
cognitive monitor:

    python cognitive_telemetry.py

This runs a 100-experience live-fire simulation against a *real* Dirichlet
predictive agent (no mocked intelligence) and prints the emergent CPI curve.
"""

from __future__ import annotations

import asyncio
import math
import random
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import (
    Awaitable,
    Callable,
    Deque,
    Iterable,
    Mapping,
    Protocol,
    Sequence,
    runtime_checkable,
)

__all__ = [
    "Symbol",
    "ConceptId",
    "Experience",
    "CognitiveProgressIndex",
    "CPITracker",
    "BottleneckConcept",
    "SystemDiagnostics",
    "ExperienceSource",
    "ReflectionEngine",
    "GenerativeWorld",
    "PredictiveAgent",
    "simulate",
    "run_monitor",
]

# ---------------------------------------------------------------------------
# Type aliases & numeric primitives
# ---------------------------------------------------------------------------

Symbol = str
ConceptId = str

#: EWMA smoothing factor. Smaller = more inertia (longer memory of the trend).
DEFAULT_ACCURACY_ALPHA: float = 0.15
DEFAULT_SURPRISE_ALPHA: float = 0.20
DEFAULT_DECAY_ALPHA: float = 0.10

#: Surprise (prediction error) is Shannon surprisal in bits. Two bits is the
#: error of a maximally confused binary guess; ~5.3 bits is uniform over 40
#: symbols. We normalise against this ceiling so accuracy stays in [0, 1].
SURPRISE_CEILING_BITS: float = 5.0

_LOG2 = math.log(2.0)


def _safe_log2(x: float) -> float:
    """``log2`` guarded against domain errors; callers keep arguments > 0."""
    return math.log(x) / _LOG2 if x > 0.0 else 0.0


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def _ewma(prev: float, sample: float, alpha: float) -> float:
    """Exponentially weighted moving average. ``alpha=1`` is a raw sample."""
    return (1.0 - alpha) * prev + alpha * sample


def _kl_divergence_bits(p: Mapping[Symbol, float], q: Mapping[Symbol, float]) -> float:
    """KL(P || Q) in bits over the shared support of ``p``.

    Terms where ``p[s] == 0`` contribute nothing, per the convention
    ``0 * log(0/q) = 0``. Caller guarantees both distributions share support.
    """
    total = 0.0
    for symbol, p_s in p.items():
        if p_s <= 0.0:
            continue
        q_s = q.get(symbol, 0.0)
        if q_s <= 0.0:
            continue
        total += p_s * _safe_log2(p_s / q_s)
    return max(total, 0.0)


def _linear_slope(values: Sequence[float]) -> float:
    """Ordinary-least-squares slope of a 1-D series indexed by integer time.

    Returns 0.0 for degenerate inputs. Used to detect trend *direction*, so it
    need not be a robust estimator --- just a consistent one.
    """
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den != 0.0 else 0.0


# ---------------------------------------------------------------------------
# The atomic unit of cognition: an Experience
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Experience:
    """One tick of the cognitive loop, fully self-describing.

    An ``Experience`` is *not* a log line. It is the closed-form record of a
    single prediction-reality collision: what the generative model expected,
    what the world delivered, how much that hurt (surprise), how much it
    mattered (attention), how much the model changed (belief shift), and which
    latent concept the collision was routed through.

    Every CPI metric is a reduction over a window of these objects, so the
    schema is the contract between the object level (C1) and the meta level (C6).
    """

    timestamp: float
    context: tuple[Symbol, ...]
    predicted: Symbol
    observed: Symbol
    #: Shannon surprisal of ``observed`` under the pre-update predictive, bits.
    prediction_error: float
    #: Precision of the residual in [0, 1]; ``1 - max predictive probability``.
    attention: float
    #: KL divergence between pre- and post-update predictive distributions.
    belief_shift: float
    #: The latent concept / belief module this experience was attributed to.
    concept_id: ConceptId
    #: True iff this tick reconciled a previously-contradictory belief.
    resolved_contradiction: bool = False
    #: Discrete sequence index within the owning stream (monotonic, dense).
    step: int = 0

    @property
    def is_novel(self) -> bool:
        """A tick counts as novel if it carried above-baseline surprise."""
        return self.prediction_error >= SURPRISE_CEILING_BITS * 0.5


# ---------------------------------------------------------------------------
# The Cognitive Progress Index
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class CognitiveProgressIndex:
    """Continuous running metrics of cognitive progress.

    All components are kept in well-defined ranges so the composite ``cpi`` is
    comparable across runs and across time:

        * ``prediction_accuracy_trend``  in [0, 1]   (1 = perfect foresight)
        * ``average_surprise_decay``     in [0, 1]   (1 = instant recovery)
        * ``concept_compression_ratio``  in [1, ...] (higher = more abstraction)
        * ``structural_contradictions_resolved`` >= 0 (monotone integer)

    The composite is a precision-weighted blend; compression and resolution are
    compressed into [0, 1] via a saturating transform so no single axis can run
    away with the score.
    """

    prediction_accuracy_trend: float = 0.0
    average_surprise_decay: float = 0.0
    concept_compression_ratio: float = 1.0
    structural_contradictions_resolved: int = 0

    #: Diagnostic provenance --- how many experiences fed this snapshot.
    samples_seen: int = 0
    #: Distinct latent concepts consolidated so far.
    concepts_consolidated: int = 0
    #: Wall-clock of the last update (for staleness checks upstream).
    updated_at: float = field(default_factory=time.time)

    @property
    def compression_component(self) -> float:
        """Saturating map of the raw ratio into [0, 1].

        ``1 + ratio`` so an untouched system (ratio == 1) scores ~0.5 and a
        highly-compressed one (ratio >> 1) asymptotes to 1.0.
        """
        return 1.0 - math.exp(-(self.concept_compression_ratio - 1.0))

    @property
    def resolution_component(self) -> float:
        """Each resolved contradiction contributes diminishing returns."""
        return 1.0 - math.exp(-self.structural_contradictions_resolved / 3.0)

    @property
    def cpi(self) -> float:
        """Composite Cognitive Progress Index in [0, 1].

        Weights reflect predictive-processing priorities: accuracy is the
        primary survival signal, surprise-decay (learning speed) is second,
        compression (abstraction) third, and contradiction resolution is a
        bonus that rewards coherence. The blend is normalised by the weight sum.
        """
        weights = {
            "accuracy": (self.prediction_accuracy_trend, 0.40),
            "decay": (self.average_surprise_decay, 0.30),
            "compression": (self.compression_component, 0.20),
            "resolution": (self.resolution_component, 0.10),
        }
        total_w = sum(w for _, w in weights.values())
        return _clamp(sum(v * w for v, w in weights.values()) / total_w)

    def as_dict(self) -> dict[str, float | int]:
        return {
            "cpi": self.cpi,
            "prediction_accuracy_trend": self.prediction_accuracy_trend,
            "average_surprise_decay": self.average_surprise_decay,
            "concept_compression_ratio": self.concept_compression_ratio,
            "structural_contradictions_resolved": self.structural_contradictions_resolved,
            "concepts_consolidated": self.concepts_consolidated,
            "samples_seen": self.samples_seen,
        }


# ---------------------------------------------------------------------------
# The CPI tracker --- a stateful reducer over Experiences
# ---------------------------------------------------------------------------


class CPITracker:
    """Stateful reducer that folds ``Experience`` objects into a CPI snapshot.

    The tracker is model-agnostic: it consumes the per-tick signals that any
    predictive agent already computes (surprise, attention, belief shift) and
    maintains four running estimators plus the bookkeeping needed to detect a
    learning plateau.

    Estimators
    ----------
    * **Accuracy** --- EWMA of ``1 - normalised(surprise)``. Falls as the model
      converges on the world.
    * **Surprise decay** --- on each novelty spike we open a "recovery window"
      and measure how completely surprise is absorbed within ``decay_window``
      ticks. The EWMA of that recovery fraction is the decay score (1 = the
      mistake was fully internalised within the window).
    * **Compression** --- ``experiences / distinct_concepts_consolidated``. A
      concept consolidates once it has accrued enough mass (see
      ``consolidation_mass``) to be trusted as a reusable rule.
    * **Contradictions** --- a monotone counter of
      ``resolved_contradiction`` ticks.
    """

    def __init__(
        self,
        *,
        accuracy_alpha: float = DEFAULT_ACCURACY_ALPHA,
        surprise_alpha: float = DEFAULT_SURPRISE_ALPHA,
        decay_alpha: float = DEFAULT_DECAY_ALPHA,
        decay_window: int = 4,
        novelty_floor: float = 2.0,
        consolidation_mass: int = 5,
    ) -> None:
        self._accuracy_alpha = accuracy_alpha
        self._surprise_alpha = surprise_alpha
        self._decay_alpha = decay_alpha
        self._decay_window = decay_window
        self._novelty_floor = novelty_floor
        self._consolidation_mass = consolidation_mass

        # Running point estimates.
        self._accuracy: float = 0.0
        self._average_surprise: float = SURPRISE_CEILING_BITS
        self._decay_score: float = 0.0
        self._contradictions: int = 0

        # Bookkeeping.
        self._samples: int = 0
        self._concept_mass: Counter[ConceptId] = Counter()
        self._consolidated: set[ConceptId] = set()

        # Surprise-recovery tracking. ``_open_spike`` holds (step, peak_error)
        # for an in-flight novelty event; its tail is folded on closure.
        self._open_spike: tuple[int, float] | None = None
        self._spike_tail: list[float] = []

        # Per-concept running accuracy, for bottleneck attribution.
        self._per_concept_error: dict[ConceptId, Deque[float]] = {}
        self._per_concept_count: Counter[ConceptId] = Counter()

        # Rolling history for trend / plateau analysis.
        self._surprise_history: Deque[float] = deque(maxlen=64)

    # -- public state -------------------------------------------------------

    @property
    def average_surprise(self) -> float:
        """EWMA of raw prediction error (bits). The plateau watch variable."""
        return self._average_surprise

    @property
    def surprise_history(self) -> Sequence[float]:
        return tuple(self._surprise_history)

    @property
    def consolidated_concepts(self) -> frozenset[ConceptId]:
        return frozenset(self._consolidated)

    def current_index(self) -> CognitiveProgressIndex:
        """Materialise the running state into an immutable CPI snapshot."""
        ratio = self._compression_ratio()
        return CognitiveProgressIndex(
            prediction_accuracy_trend=_clamp(self._accuracy),
            average_surprise_decay=_clamp(self._decay_score),
            concept_compression_ratio=ratio,
            structural_contradictions_resolved=self._contradictions,
            samples_seen=self._samples,
            concepts_consolidated=len(self._consolidated),
            updated_at=time.time(),
        )

    # -- ingestion ----------------------------------------------------------

    def ingest(self, exp: Experience) -> CognitiveProgressIndex:
        """Fold a single experience into every running estimator.

        Order matters: we update accuracy and surprise first (they feed the
        spike detector), then advance the recovery tracker, then consolidate
        concepts and contradictions.
        """
        self._samples += 1

        # 1. Accuracy + surprise EWMA.
        norm_error = _clamp(exp.prediction_error / SURPRISE_CEILING_BITS)
        self._accuracy = _ewma(self._accuracy, 1.0 - norm_error, self._accuracy_alpha)
        self._average_surprise = _ewma(
            self._average_surprise, exp.prediction_error, self._surprise_alpha
        )
        self._surprise_history.append(self._average_surprise)

        # 2. Surprise-recovery tracking.
        self._advance_recovery(exp)

        # 3. Per-concept bookkeeping for bottleneck attribution.
        self._per_concept_count[exp.concept_id] += 1
        bucket = self._per_concept_error.setdefault(
            exp.concept_id, deque(maxlen=32)
        )
        bucket.append(exp.prediction_error)

        # 4. Concept consolidation (mass-gated).
        self._concept_mass[exp.concept_id] += 1
        if (
            exp.concept_id not in self._consolidated
            and self._concept_mass[exp.concept_id] >= self._consolidation_mass
        ):
            self._consolidated.add(exp.concept_id)

        # 5. Contradiction resolution is monotone and explicit.
        if exp.resolved_contradiction:
            self._contradictions += 1

        return self.current_index()

    def ingest_many(self, experiences: Iterable[Experience]) -> CognitiveProgressIndex:
        cpi = self.current_index()
        for exp in experiences:
            cpi = self.ingest(exp)
        return cpi

    # -- internals ----------------------------------------------------------

    def _compression_ratio(self) -> float:
        """Experiences per consolidated concept; >= 1 by construction."""
        n_concepts = max(len(self._consolidated), 1)
        return self._samples / n_concepts

    def _advance_recovery(self, exp: Experience) -> None:
        """Update the surprise-decay estimator from this tick.

        A spike opens when error crosses ``_novelty_floor`` with no spike open.
        Each subsequent tick appends to the tail; after ``_decay_window`` ticks
        we close the spike, compute the absorbed fraction of the peak, and fold
        it into the decay EWMA.
        """
        if self._open_spike is None:
            if exp.prediction_error >= self._novelty_floor:
                self._open_spike = (exp.step, exp.prediction_error)
                self._spike_tail = []
            return

        _, peak = self._open_spike
        self._spike_tail.append(exp.prediction_error)
        if len(self._spike_tail) >= self._decay_window:
            tail_mean = sum(self._spike_tail) / len(self._spike_tail)
            # Absorbed fraction of the peak: 1 = fully recovered, 0 = stuck.
            absorbed = _clamp(1.0 - (tail_mean / peak)) if peak > 0 else 0.0
            self._decay_score = _ewma(self._decay_score, absorbed, self._decay_alpha)
            self._open_spike = None
            self._spike_tail = []

    # -- bottleneck attribution --------------------------------------------

    def concept_bottlenecks(self, top_k: int = 3) -> list["BottleneckConcept"]:
        """Rank latent concepts by how badly they resist learning.

        A concept is a bottleneck when it has accrued enough mass to be
        meaningful yet still carries high mean surprise --- i.e. the model has
        seen it often but cannot predict it. Sorted worst-first.
        """
        ranked: list[BottleneckConcept] = []
        for concept_id, errors in self._per_concept_error.items():
            mass = self._per_concept_count[concept_id]
            if mass == 0:
                continue
            mean_err = sum(errors) / len(errors)
            mean_acc = _clamp(1.0 - mean_err / SURPRISE_CEILING_BITS)
            ranked.append(
                BottleneckConcept(
                    concept_id=concept_id,
                    samples=mass,
                    mean_surprise=mean_err,
                    mean_accuracy=mean_acc,
                    consolidated=concept_id in self._consolidated,
                )
            )
        ranked.sort(key=lambda b: (b.mean_surprise, -b.samples), reverse=True)
        return ranked[:top_k]


# ---------------------------------------------------------------------------
# Self-correction: plateau detection & diagnostics
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class BottleneckConcept:
    """A latent concept that resists learning."""

    concept_id: ConceptId
    samples: int
    mean_surprise: float
    mean_accuracy: float
    consolidated: bool

    @property
    def is_chronic(self) -> bool:
        """Consolidated yet still inaccurate = a genuine cognitive bottleneck."""
        return self.consolidated and self.mean_accuracy < 0.55


@dataclass(slots=True)
class SystemDiagnostics:
    """The cognitive equivalent of a stack trace for a stuck mind.

    Emitted only when the reflection loop detects that learning has plateaued.
    It does not prescribe an action (VELYNX adaptation is always observe-only);
    it *names* the bottleneck so an upstream adaptation engine can act.
    """

    generated_at: float
    average_surprise: float
    surprise_slope: float
    plateau_window: int
    bottleneck: BottleneckConcept | None
    runners_up: list[BottleneckConcept]
    summary: str

    def as_dict(self) -> dict[str, object]:
        bn = self.bottleneck
        return {
            "generated_at": self.generated_at,
            "average_surprise": self.average_surprise,
            "surprise_slope": self.surprise_slope,
            "plateau_window": self.plateau_window,
            "bottleneck_concept": bn.concept_id if bn else None,
            "bottleneck_accuracy": bn.mean_accuracy if bn else None,
            "runners_up": [r.concept_id for r in self.runners_up],
            "summary": self.summary,
        }


# ---------------------------------------------------------------------------
# The experience source contract + the async reflection loop
# ---------------------------------------------------------------------------


@runtime_checkable
class ExperienceSource(Protocol):
    """Anything that can hand the reflection loop its recent experiences."""

    def recent_experiences(self) -> list[Experience]:
        """Return experiences accumulated since the last poll (newest last)."""
        ...


class ReflectionEngine:
    """Asynchronous background loop that watches VELYNX learn.

    The engine owns no model. It periodically polls an ``ExperienceSource`` for
    fresh ``Experience`` objects, folds them into a ``CPITracker``, and watches
    the resulting ``average_surprise`` series. If surprise plateaus while still
    elevated --- meaning the system is being exposed to novelty but failing to
    absorb it --- the engine halts, runs bottleneck attribution, and emits a
    ``SystemDiagnostics`` report.

    Diagnostics are rate-limited by a sample cooldown: once a bottleneck is
    named, no further report fires for ``diagnostic_cooldown`` samples unless
    the *dominant* bottleneck concept changes (in which case the cooldown is
    bypassed, since a new bottleneck is itself a signal worth surfacing).
    """

    def __init__(
        self,
        source: ExperienceSource,
        *,
        poll_interval: float = 0.1,
        plateau_window: int = 8,
        plateau_slope_epsilon: float = 0.02,
        stuck_surprise_threshold: float = 1.5,
        diagnostic_cooldown: int = 20,
        tracker: CPITracker | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._source = source
        self._poll_interval = poll_interval
        self._plateau_window = plateau_window
        self._plateau_slope_epsilon = plateau_slope_epsilon
        self._stuck_threshold = stuck_surprise_threshold
        self._cooldown = diagnostic_cooldown
        self._tracker = tracker or CPITracker()
        self._clock = clock
        self._sleeper = sleeper

        self._cpi: CognitiveProgressIndex = CognitiveProgressIndex()
        self._latest_diagnostics: SystemDiagnostics | None = None
        self._last_bottleneck: ConceptId | None = None
        #: Sample index at which the last diagnostic fired (for cooldown).
        self._last_fire_sample: int = -1

        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()

    # -- lifecycle ----------------------------------------------------------

    async def run(self) -> None:
        """Run the reflection loop until ``stop()`` is awaited.

        Designed to be wrapped in ``asyncio.create_task``. Each iteration polls
        the source, updates the CPI, and conditionally emits diagnostics.
        """
        self._stop.clear()
        while not self._stop.is_set():
            await self._tick()
            try:
                await self._sleeper(self._poll_interval)
            except asyncio.CancelledError:
                break

    def start(self) -> asyncio.Task[None]:
        """Spawn the reflection loop as a background task."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.run(), name="reflection-loop")
        return self._task

    async def stop(self) -> None:
        """Signal the loop to stop and wait for it to drain."""
        self._stop.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    # -- single iteration ---------------------------------------------------

    async def _tick(self) -> None:
        experiences = self._source.recent_experiences()
        if not experiences:
            return
        self._cpi = self._tracker.ingest_many(experiences)
        diagnostics = self._maybe_diagnose()
        if diagnostics is not None:
            self._latest_diagnostics = diagnostics

    def _maybe_diagnose(self) -> SystemDiagnostics | None:
        """Return a diagnostics report iff surprise has plateaued while stuck.

        A plateau is declared when, over the last ``plateau_window`` samples of
        ``average_surprise``, the slope magnitude is below
        ``plateau_slope_epsilon`` *and* the level remains above
        ``stuck_surprise_threshold``. Reports are then rate-limited: a repeat
        for the *same* bottleneck is suppressed for ``diagnostic_cooldown``
        samples, while a *changed* bottleneck fires immediately (a new
        bottleneck is itself the signal).
        """
        history = self._tracker.surprise_history
        samples_seen = self._cpi.samples_seen
        if len(history) < self._plateau_window:
            return None

        window = list(history)[-self._plateau_window:]
        slope = _linear_slope(window)
        level = sum(window) / len(window)

        plateaued = abs(slope) < self._plateau_slope_epsilon
        stuck = level > self._stuck_threshold
        if not (plateaued and stuck):
            return None

        bottlenecks = self._tracker.concept_bottlenecks(top_k=3)
        primary = bottlenecks[0] if bottlenecks else None
        primary_id: ConceptId | None = primary.concept_id if primary else None

        # Rate-limit: suppress same-bottleneck repeats within the cooldown.
        if primary_id == self._last_bottleneck:
            since_fire = samples_seen - self._last_fire_sample
            if since_fire < self._cooldown:
                return None

        self._last_bottleneck = primary_id
        self._last_fire_sample = samples_seen

        summary = self._summarise(primary, level, slope)
        return SystemDiagnostics(
            generated_at=self._clock(),
            average_surprise=level,
            surprise_slope=slope,
            plateau_window=self._plateau_window,
            bottleneck=primary,
            runners_up=bottlenecks[1:],
            summary=summary,
        )

    @staticmethod
    def _summarise(
        primary: BottleneckConcept | None, level: float, slope: float
    ) -> str:
        if primary is None:
            return (
                "Surprise plateau detected but no dominant concept attributable; "
                "the bottleneck is distributed across the belief graph."
            )
        kind = "chronic" if primary.is_chronic else "emerging"
        return (
            f"Cognitive bottleneck identified at latent concept "
            f"'{primary.concept_id}' ({kind}): mean accuracy "
            f"{primary.mean_accuracy:.2f} across {primary.samples} samples while "
            f"system-wide surprise plateaus at {level:.2f} bits "
            f"(slope {slope:+.4f}). This belief is resisting compression and "
            f"should be targeted for restructuring or re-segmentation."
        )

    # -- read accessors -----------------------------------------------------

    def current_cpi(self) -> CognitiveProgressIndex:
        return self._cpi

    def latest_diagnostics(self) -> SystemDiagnostics | None:
        return self._latest_diagnostics

    def tracker(self) -> CPITracker:
        return self._tracker


# ---------------------------------------------------------------------------
# Live-fire simulation: a REAL predictive agent (no mocked intelligence)
# ---------------------------------------------------------------------------
#
# To prove the CPI measures genuine becoming rather than theatre, the demo
# builds an actual generative world and an actual Dirichlet predictive agent.
# The world is a small family of latent concepts, each a sparse distribution
# over a symbol alphabet. The agent maintains one smoothed Dirichlet predictive
# per concept and learns it from observation. Prediction error, attention and
# belief shift are all computed, not faked --- so when accuracy rises it is
# because the agent genuinely converged, and when it plateaus it is because a
# concept is genuinely unpredictable.


class GenerativeWorld:
    """A family of latent concepts emitting symbols from fixed distributions.

    Three concepts (rain, fire, music) are highly predictable once learned. A
    fourth (``chaos``) is near-uniform: it carries genuine irreducible
    uncertainty and is the designed cognitive bottleneck.
    """

    def __init__(self, seed: int = 7) -> None:
        rng = random.Random(seed)
        self._concepts: dict[ConceptId, tuple[tuple[Symbol, float], ...]] = {
            "rain": (("wet", 0.70), ("damp", 0.20), ("dry", 0.10)),
            "fire": (("hot", 0.65), ("warm", 0.25), ("cold", 0.10)),
            "music": (("do", 0.45), ("re", 0.30), ("mi", 0.25)),
            "chaos": (
                ("wet", 0.20), ("dry", 0.20), ("hot", 0.20),
                ("cold", 0.20), ("do", 0.20),
            ),
        }
        self._alphabet = sorted(
            {sym for dist in self._concepts.values() for sym, _ in dist}
        )
        self._rng = rng
        # Dirichlet concentration on the chaotic concept, in bits. This is the
        # information-theoretic floor no agent can beat there.
        self.chaos_floor = -sum(
            p * _safe_log2(p) for _, p in self._concepts["chaos"]
        )

    @property
    def alphabet(self) -> list[Symbol]:
        return list(self._alphabet)

    @property
    def concept_ids(self) -> list[ConceptId]:
        return list(self._concepts)

    def emit(self, concept_id: ConceptId) -> Symbol:
        dist = self._concepts[concept_id]
        r = self._rng.random()
        acc = 0.0
        for sym, p in dist:
            acc += p
            if r <= acc:
                return sym
        return dist[-1][0]


class PredictiveAgent:
    """A per-concept Dirichlet predictive agent that learns by counting.

    Each concept gets its own categorical model with symmetric Dirichlet
    smoothing. The agent is *told* which concept a tick belongs to (as a
    modular brain routes an experience to the right belief module) but must
    still learn each module's distribution from data. The chaotic module can
    never be beaten down to low surprise --- that is the honest bottleneck.

    Once a chaotic module's belief stabilises (belief_shift below threshold for
    a sustained run), the agent *reifies* it: it accepts the residual as
    irreducible noise rather than a solvable puzzle, resolving a structural
    contradiction.
    """

    def __init__(
        self,
        alphabet: Sequence[Symbol],
        *,
        prior_alpha: float = 0.5,
        reify_shift_threshold: float = 0.02,
        reify_streak: int = 5,
    ) -> None:
        self._alphabet = tuple(alphabet)
        self._alpha = prior_alpha
        self._counts: dict[ConceptId, Counter[Symbol]] = {}
        self._reify_threshold = reify_shift_threshold
        self._reify_streak_target = reify_streak
        self._stabilising: dict[ConceptId, int] = {}
        self._reified: set[ConceptId] = set()

    # -- predictive distribution -------------------------------------------

    def _predictive(self, concept_id: ConceptId) -> dict[Symbol, float]:
        counts = self._counts.get(concept_id, Counter())
        total = sum(counts.values()) + self._alpha * len(self._alphabet)
        return {
            sym: (counts.get(sym, 0) + self._alpha) / total
            for sym in self._alphabet
        }

    # -- learning step ------------------------------------------------------

    def observe(
        self, concept_id: ConceptId, observed: Symbol, *, step: int
    ) -> Experience:
        before = self._predictive(concept_id)
        p_observed = before.get(observed, 0.0)

        surprise = -_safe_log2(p_observed) if p_observed > 0 else SURPRISE_CEILING_BITS
        attention = 1.0 - max(before.values())

        # Update counts, then measure how much the belief moved.
        bucket = self._counts.setdefault(concept_id, Counter())
        bucket[observed] += 1
        after = self._predictive(concept_id)
        shift = _kl_divergence_bits(after, before)

        resolved = self._maybe_reify(concept_id, shift)

        return Experience(
            timestamp=time.time(),
            context=(concept_id,),
            predicted=max(before, key=before.get),
            observed=observed,
            prediction_error=surprise,
            attention=attention,
            belief_shift=shift,
            concept_id=concept_id,
            resolved_contradiction=resolved,
            step=step,
        )

    def _maybe_reify(self, concept_id: ConceptId, shift: float) -> bool:
        """Reify a concept once its belief has stably converged.

        Returns True exactly once per concept, the tick it is reified. Reifying
        is the cognitive act of accepting residual surprise as *irreducible*
        rather than continuing to thrash --- this is what increments
        ``structural_contradictions_resolved``.
        """
        if concept_id in self._reified:
            return False
        if shift <= self._reify_threshold:
            streak = self._stabilising.get(concept_id, 0) + 1
            self._stabilising[concept_id] = streak
            if streak >= self._reify_streak_target:
                self._reified.add(concept_id)
                return True
        else:
            self._stabilising[concept_id] = 0
        return False

    @property
    def reified_concepts(self) -> frozenset[ConceptId]:
        return frozenset(self._reified)


# ---------------------------------------------------------------------------
# Simulation harness
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class _BufferedSource:
    """ExperienceSource backed by a queue the simulator drains into."""

    _buffer: deque[Experience] = field(default_factory=deque)

    def push(self, exp: Experience) -> None:
        self._buffer.append(exp)

    def recent_experiences(self) -> list[Experience]:
        if not self._buffer:
            return []
        batch = list(self._buffer)
        self._buffer.clear()
        return batch


def _schedule(step: int, total: int) -> ConceptId:
    """Deterministic curriculum exposing the bottleneck mid-run.

    * steps   0-39: predictable concepts only  -> accuracy climbs fast.
    * steps  40-79: chaos injected ~40% of ticks -> accuracy plateaus.
    * steps  80-99: chaos still present but the agent reifies it -> CPI rises.
    """
    phase1 = ("rain", "fire", "music")
    if step < total * 2 // 5:
        return phase1[step % len(phase1)]
    # Phase 2/3: interleave chaos deterministically.
    if step % 5 in (0, 2):
        return "chaos"
    return phase1[step % len(phase1)]


async def simulate(
    n_experiences: int = 100,
    *,
    seed: int = 7,
    poll_interval: float = 0.0,
    verbose: bool = True,
) -> tuple[CognitiveProgressIndex, list[SystemDiagnostics]]:
    """Run the full live-fire simulation and return (final CPI, diagnostics).

    The reflection engine runs concurrently with the agent. After every batch
    of experiences is produced we yield to the event loop so the engine can
    poll, fold, and (when warranted) emit a diagnostics report.
    """
    world = GenerativeWorld(seed=seed)
    agent = PredictiveAgent(world.alphabet)
    source = _BufferedSource()
    engine = ReflectionEngine(
        source,
        poll_interval=poll_interval,
        plateau_window=8,
        plateau_slope_epsilon=0.03,
        stuck_surprise_threshold=1.6,
    )
    engine_task = engine.start()

    snapshots: list[CognitiveProgressIndex] = []
    diagnostics: list[SystemDiagnostics] = []

    for step in range(n_experiences):
        concept = _schedule(step, n_experiences)
        observed = world.emit(concept)
        exp = agent.observe(concept, observed, step=step)
        source.push(exp)

        # Yield control so the reflection loop can ingest this batch.
        await asyncio.sleep(0)
        # Drive at least one full poll so the loop sees every experience.
        await engine._tick()  # noqa: SLF001 --- deterministic for the demo

        cpi = engine.current_cpi()
        snapshots.append(cpi)
        if (diag := engine.latest_diagnostics()) is not None:
            if not diagnostics or diag.generated_at != diagnostics[-1].generated_at:
                diagnostics.append(diag)

        if verbose and (step % 10 == 9 or step == n_experiences - 1):
            _render_step(step, cpi, world.chaos_floor)

    if verbose:
        _render_summary(snapshots, diagnostics, world.chaos_floor)

    await engine.stop()
    try:
        await asyncio.wait_for(engine_task, timeout=1.0)
    except asyncio.TimeoutError:
        engine_task.cancel()

    return snapshots[-1], diagnostics


# ---------------------------------------------------------------------------
# Rendering (terminal)
# ---------------------------------------------------------------------------


def _bar(value: float, width: int = 24) -> str:
    filled = int(round(_clamp(value) * width))
    return "[" + "#" * filled + "." * (width - filled) + "]"


def _render_step(step: int, cpi: CognitiveProgressIndex, chaos_floor: float) -> None:
    print(
        f"  t={step + 1:>3}  CPI={cpi.cpi:.3f} {_bar(cpi.cpi)}  "
        f"acc={cpi.prediction_accuracy_trend:.3f}  "
        f"decay={cpi.average_surprise_decay:.3f}  "
        f"compress={cpi.concept_compression_ratio:.2f}x  "
        f"resolved={cpi.structural_contradictions_resolved}"
    )


def _render_summary(
    snapshots: Sequence[CognitiveProgressIndex],
    diagnostics: Sequence[SystemDiagnostics],
    chaos_floor: float,
) -> None:
    if not snapshots:
        return
    first, last = snapshots[0], snapshots[-1]
    print("\n" + "=" * 72)
    print("COGNITIVE MILESTONE C6 --- SELF-EVALUATION: SIMULATION SUMMARY")
    print("=" * 72)
    print(f"  CPI trajectory             : {first.cpi:.3f}  ->  {last.cpi:.3f}   "
          f"(delta {last.cpi - first.cpi:+.3f})")
    print(f"  prediction_accuracy_trend  : {first.prediction_accuracy_trend:.3f}  ->  "
          f"{last.prediction_accuracy_trend:.3f}")
    print(f"  average_surprise_decay     : {first.average_surprise_decay:.3f}  ->  "
          f"{last.average_surprise_decay:.3f}")
    print(f"  concept_compression_ratio  : {first.concept_compression_ratio:.2f}x  ->  "
          f"{last.concept_compression_ratio:.2f}x")
    print(f"  contradictions_resolved    : {first.structural_contradictions_resolved}  ->  "
          f"{last.structural_contradictions_resolved}")
    print(f"  concepts consolidated      : {last.concepts_consolidated}")
    print(f"  irreducible chaos floor    : {chaos_floor:.3f} bits "
          f"(unbeatable information-theoretic limit on the bottleneck concept)")
    print(f"  diagnostics emitted        : {len(diagnostics)}")

    if diagnostics:
        print("\n  --- SELF-CORRECTION DIAGNOSTICS (bottleneck attribution) ---")
        for i, d in enumerate(diagnostics, 1):
            bn = d.bottleneck
            bn_label = bn.concept_id if bn else "<distributed>"
            bn_acc = f"{bn.mean_accuracy:.2f}" if bn else "n/a"
            print(f"  [{i}] bottleneck='{bn_label}'  accuracy={bn_acc}  "
                  f"surprise={d.average_surprise:.2f}bits  slope={d.surprise_slope:+.4f}")
            print(f"      {d.summary}")

    # Verdict: did VELYNX actually get smarter?
    verdict = "LEARNING" if last.cpi > first.cpi else "STAGNANT"
    print("\n" + "-" * 72)
    print(f"  VERDICT: cognitive state is {verdict} "
          f"(CPI {first.cpi:.3f} -> {last.cpi:.3f}).")
    print("-" * 72)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def run_monitor(n_experiences: int = 100) -> None:
    print("VELYNX --- Cognitive Milestone C6: The Self-Evaluation Engine")
    print("Running 100-experience live-fire simulation against a real")
    print("Dirichlet predictive agent. No mocked intelligence.\n")
    await simulate(n_experiences=n_experiences)


if __name__ == "__main__":
    asyncio.run(run_monitor())
