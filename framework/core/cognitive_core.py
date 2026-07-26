"""
VELYNX — Cognitive Milestones C1-C3 + C6: Predictive, Causal & Stable Belief
============================================================================

A pure, self-contained implementation of a Predictive Processing / Active
Inference cognitive loop. No LLMs. No embeddings. No external databases. No
network. Just the mathematics of *prediction*, *surprise*, and *adaptation* —
extended with *causal explanation* and *failure-driven hypothesis generation*.

Milestones
----------
* **C1 — Predictive Understanding.** The engine always holds a prediction of
  the next symbol; reality collides with it to produce surprise, which drives
  attention, learning, and concept formation.
* **C2 — Explain Prediction.** Every standing forecast carries a *rationale*
  ("observed 'Day -> Night' 4 times previously"), and every tick exposes the
  *localized world model* for its context: the dominant rule plus the
  exceptions that rule has had to tolerate.
* **C3 — Prediction Failure Analysis.** When surprise breaches a threshold the
  engine does not merely re-weight beliefs — it authors a ``causal_hypothesis``
  (a curiosity trigger) positing the missing intermediate cause behind the
  dissonance.
* **C6 — Stable Belief Revision.** Beliefs become *multidimensional*. Each rule
  tracks not just a confidence but a *stability* (how much accumulated history
  protects it) plus raw ``support_count`` / ``contradiction_count`` ledgers.
  Learning obeys an **Inertia Law**: ``effective_rate = base_rate * (1 -
  stability)``, so a mature rule barely flinches at an anomaly. Anomalies are
  not allowed to overwrite the rule — they are *quarantined* as ``Exceptions``
  filed inside the parent belief. A core rule only **fractures** once its
  contradictions approach its support, at which point the dominant exception is
  promoted to the new rule. This is what cures the catastrophic forgetting of
  the flat-probability substrate, where a single ``storm`` could collapse a
  well-established ``day -> night`` rule from 0.84 to 0.31.


Core thesis
-----------
A mind is not a query engine. It is a continuous generative simulation that
*always* holds a prediction of what comes next. When reality arrives it is
collided with that prediction. The residual — the **prediction error**, a.k.a.
*surprise* — is the universal currency of the system:

    * It drives attention (surprising things demand focus).
    * It drives learning (large errors trigger large belief updates).
    * It drives concept formation (contexts whose predictions crystallise into
      near-determinism become latent concepts).

Formally we maintain a variable-context categorical generative model with a
symmetric Dirichlet prior. For a context ``c`` the predictive distribution is

    P(s | c) = (n(c, s) + alpha) / (N(c) + alpha * |support|)

Surprise is Shannon surprisal in bits:  I(s) = -log2 P(s | c).
Attention is precision of the residual:  a(s) = 1 - P(s | c)  in [0, 1].
Belief shift is the KL divergence between the context's predictive
distribution before and after assimilating the observation.
Learning is *precision-weighted*: the count increment grows with attention, so
the system learns surprising things faster — the hallmark of active inference.

This module is runnable directly as a cognitive monitor REPL:

    python cognitive_core.py

Type tokens; watch ``prediction_error`` spike when you surprise the engine and
collapse toward zero as it internalises your patterns.
"""

from __future__ import annotations

import asyncio
import math
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Mapping, MutableMapping, Optional, Protocol, Sequence, Tuple

# ---------------------------------------------------------------------------
# Probationary Concept Pipeline — optional integration of the Free-Energy
# Cognitive Health monitor and the MDL Concept-Birth arbiter. Imported
# defensively so this core still runs standalone if the siblings are absent.
# ---------------------------------------------------------------------------
try:  # pragma: no cover - exercised by environment, not by unit tests
    from framework.core.cognitive_health import HealthReport, Regime
    from framework.core.cognitive_health import LAMBDA, MU, NU
    from concept_birth import ConceptBirthDecision, evaluate_concept_birth

    _PIPELINE_AVAILABLE = True
except Exception:  # noqa: BLE001 - any import failure degrades gracefully
    HealthReport = None  # type: ignore[assignment,misc]
    Regime = None  # type: ignore[assignment,misc]
    LAMBDA, MU, NU = 1.0, 2.0, 0.5  # fallback defaults
    ConceptBirthDecision = None  # type: ignore[assignment,misc]
    evaluate_concept_birth = None  # type: ignore[assignment]
    _PIPELINE_AVAILABLE = False

__all__ = [
    "Symbol",
    "Context",
    "Prediction",
    "InternalModelView",
    "Experience",
    "GenerativeModel",
    "DirichletMarkovModel",
    "BeliefException",
    "Belief",
    "StableBeliefModel",
    "ProbationaryConcept",
    "PipelineTick",
    "CognitiveEngine",
    "SensoriumMonitor",
    "SensoriumVitals",
    "run_monitor",
]

# ---------------------------------------------------------------------------
# Type aliases & sentinels
# ---------------------------------------------------------------------------

Symbol = str
Context = Tuple[Symbol, ...]

#: Reserved category representing "a symbol I have never observed before".
#: Holding explicit probability mass for the unknown is what lets the system be
#: surprised by genuine novelty rather than silently clamping it to zero.
NOVEL: Symbol = "<novel>"

#: Beginning-of-stream padding so an order-k model has a defined context from
#: the very first tick.
BOS: Symbol = "<bos>"

_LOG2 = math.log(2.0)


def _safe_log2(x: float) -> float:
    """``log2`` guarded against domain errors; probabilities here are > 0."""
    return math.log(x) / _LOG2 if x > 0.0 else 0.0


def _kl_divergence(p: Mapping[Symbol, float], q: Mapping[Symbol, float]) -> float:
    """KL(P || Q) in bits over the shared support of ``p`` and ``q``.

    Both distributions are assumed to be defined over the *same* keys (the
    caller guarantees this by constructing them over an identical support).
    Terms where ``p[s] == 0`` contribute nothing, per the convention
    ``0 * log(0/q) = 0``.
    """
    total = 0.0
    for symbol, p_s in p.items():
        if p_s <= 0.0:
            continue
        q_s = q.get(symbol, 0.0)
        if q_s <= 0.0:
            # Should not happen given Dirichlet smoothing keeps all mass > 0.
            continue
        total += p_s * _safe_log2(p_s / q_s)
    return max(total, 0.0)


# ---------------------------------------------------------------------------
# Prediction — the standing expectation held *before* reality arrives
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Prediction:
    """An immutable snapshot of what the engine expects to observe next.

    The engine always carries one of these. It is generated *before* any input
    is read, embodying the principle that cognition is a continuous simulation
    rather than a reactive lookup.
    """

    context: Context
    #: Full predictive distribution as a tuple of (symbol, probability),
    #: sorted by descending probability. Includes the :data:`NOVEL` category.
    distribution: Tuple[Tuple[Symbol, float], ...]
    predicted_symbol: Symbol
    predicted_probability: float
    #: Shannon entropy of the predictive distribution, in bits. High entropy
    #: means the engine is genuinely uncertain about the future.
    entropy: float
    #: Probability mass reserved for never-before-seen symbols.
    novelty_mass: float
    #: Literal number of times the predicted transition (context -> predicted
    #: symbol) has actually been witnessed. This is the raw evidence behind the
    #: forecast — the substance of the causal "because" explanation (C2).
    predicted_support: float = 0.0
    #: Human-readable causal justification for the standing expectation, e.g.
    #: "observed 'Day -> Night' 4 times previously." (C2: Explain Prediction).
    rationale: str = ""

    def probability_of(self, symbol: Symbol) -> float:
        """Probability the engine assigned to ``symbol``.

        Unknown symbols collapse onto the reserved :data:`NOVEL` mass.
        """
        for candidate, prob in self.distribution:
            if candidate == symbol:
                return prob
        return self.novelty_mass

    def top(self, k: int = 5) -> Tuple[Tuple[Symbol, float], ...]:
        """The ``k`` most probable expected symbols."""
        return self.distribution[:k]


# ---------------------------------------------------------------------------
# InternalModelView — the localized world model around a single context (C2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InternalModelView:
    """A snapshot of the localized world model the engine holds for one context.

    Where :class:`Prediction` is the engine's *forecast*, this is the engine's
    *theory*: the dominant causal rule it has distilled for a context, together
    with the catalogued exceptions that rule has had to tolerate. It is the
    structure the REPL surfaces under ``[Current Internal Model]`` so the human
    can read the engine's causal model directly rather than inferring it from
    probabilities (C2: Explain Prediction).
    """

    context: Context
    #: The dominant successor for this context — the consequent of the rule.
    #: ``None`` when no real symbol has been observed for the context yet.
    rule_consequent: Optional[Symbol]
    #: Smoothed P(rule_consequent | context); how strongly the rule is believed.
    rule_confidence: float
    #: Literal count of times the rule's transition has been witnessed.
    rule_support: float
    #: Catalogued deviations from the rule as (symbol, empirical_frequency),
    #: sorted by descending frequency. These are the "exceptions" the rule must
    #: eventually explain — the seeds of C3 hypothesis generation.
    exceptions: Tuple[Tuple[Symbol, float], ...]
    #: (C6) Historical resistance of the rule to change, in [0, 1). Scales
    #: logarithmically with ``support_count``: the more often the rule has held,
    #: the more inertia it has and the less a fresh anomaly can move it.
    stability: float = 0.0
    #: (C6) Raw episodic tally of confirmations — times the rule actually held.
    support_count: int = 0
    #: (C6) Raw episodic tally of anomalies quarantined against this rule.
    contradiction_count: int = 0

    @property
    def has_rule(self) -> bool:
        """True once a dominant successor has actually been observed."""
        return self.rule_consequent is not None and self.rule_consequent != NOVEL

    @property
    def fracture_ratio(self) -> float:
        """(C6) How close the rule is to fracturing: contradictions / support.

        At 0.0 the rule is unchallenged; as it approaches 1.0 the accumulated
        anomalies rival the accumulated confirmations and the rule is a
        candidate for revision (promotion of its dominant exception).
        """
        if self.support_count <= 0:
            return 1.0 if self.contradiction_count > 0 else 0.0
        return self.contradiction_count / self.support_count

    def rule_str(self) -> str:
        """Render the rule as ``Day -> Night (confidence 0.86)``."""
        ctx_repr = " ".join(self.context) if self.context else "(empty)"
        if not self.has_rule:
            return f"{ctx_repr} -> ? (insufficient evidence)"
        return f"{ctx_repr} -> {self.rule_consequent} (confidence {self.rule_confidence:.2f})"

    def stability_str(self) -> str:
        """Render stability with a qualitative maturity tag (C6)."""
        if self.support_count <= 0:
            tier = "unformed"
        elif self.stability >= 0.66:
            tier = "mature/protected"
        elif self.stability >= 0.40:
            tier = "consolidating"
        else:
            tier = "fragile"
        return f"{self.stability:.2f} ({tier})"

    def evidence_str(self) -> str:
        """Render the raw episodic ledgers and fracture risk (C6)."""
        return (
            f"support={self.support_count}  vs  "
            f"contradictions={self.contradiction_count}  "
            f"(fracture risk {self.fracture_ratio:.2f})"
        )

    def exceptions_str(self) -> str:
        """Render exceptions as ``Eclipse (frequency 0.12)`` lists."""
        if not self.exceptions:
            return "(none)"
        return ", ".join(f"{sym} (frequency {freq:.2f})" for sym, freq in self.exceptions)


# ---------------------------------------------------------------------------
# Experience — the atom of cognition, one per tick of the loop
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Experience:
    """A single, immutable quantum of lived experience.

    Every tick of the cognitive loop emits exactly one ``Experience``. It is the
    permanent record of a collision between expectation and reality, and it
    carries everything needed to reconstruct *why* the system felt what it felt.
    """

    timestamp: float
    #: What the system expected before the observation arrived.
    prediction: Prediction
    #: The reality that actually occurred.
    observation: Symbol
    #: Surprise in bits: -log2 P(observation | context). The universal currency.
    prediction_error: float
    #: Focus demanded by this event, in [0, 1]; scales with prediction error.
    attention_weight: float
    #: Temporary structural patterns detected on this tick (concept formation).
    latent_concepts: Tuple[str, ...]
    #: Magnitude of the belief shift this observation caused (KL, in bits).
    confidence_delta: float
    #: Post-update snapshot of the localized world model for this context: the
    #: dominant rule and its catalogued exceptions (C2: Internal Model view).
    internal_model: Optional[InternalModelView] = None
    #: A curiosity trigger / causal question generated when surprise spikes past
    #: the engine's threshold — the engine flagging cognitive dissonance and
    #: positing a missing intermediate cause (C3: Prediction Failure Analysis).
    causal_hypothesis: Optional[str] = None

    @property
    def was_surprising(self) -> bool:
        """True when reality meaningfully diverged from expectation."""
        return self.attention_weight >= 0.5

    @property
    def expectation_met(self) -> bool:
        """True when the single most likely prediction matched reality."""
        return self.prediction.predicted_symbol == self.observation

    def as_dict(self) -> Dict[str, object]:
        """Plain, JSON-friendly view for logging or inspection."""
        return {
            "timestamp": self.timestamp,
            "context": list(self.prediction.context),
            "predicted_symbol": self.prediction.predicted_symbol,
            "predicted_probability": round(self.prediction.predicted_probability, 6),
            "observation": self.observation,
            "prediction_error_bits": round(self.prediction_error, 6),
            "attention_weight": round(self.attention_weight, 6),
            "confidence_delta_bits": round(self.confidence_delta, 6),
            "prediction_entropy_bits": round(self.prediction.entropy, 6),
            "rationale": self.prediction.rationale,
            "latent_concepts": list(self.latent_concepts),
            "internal_model": (
                {
                    "rule": self.internal_model.rule_str(),
                    "rule_support": self.internal_model.rule_support,
                    "stability": round(self.internal_model.stability, 6),
                    "support_count": self.internal_model.support_count,
                    "contradiction_count": self.internal_model.contradiction_count,
                    "fracture_ratio": round(self.internal_model.fracture_ratio, 6),
                    "exceptions": [
                        {"symbol": s, "frequency": round(f, 6)}
                        for s, f in self.internal_model.exceptions
                    ],
                }
                if self.internal_model is not None
                else None
            ),
            "causal_hypothesis": self.causal_hypothesis,
        }


# ---------------------------------------------------------------------------
# Generative model — the swappable belief substrate
# ---------------------------------------------------------------------------


class GenerativeModel(Protocol):
    """Contract for any belief substrate the engine can reason with.

    The engine is agnostic to *how* predictions are produced; it only needs
    something that can predict and assimilate evidence. This keeps the cognitive
    loop (predict -> collide -> adapt) independent of the representation, so the
    Markov substrate below can later be swapped for a richer generative model
    without touching :class:`CognitiveEngine`.
    """

    def predict(self, context: Context) -> Prediction:  # pragma: no cover
        """Return the predictive distribution over the next symbol."""
        ...

    def assimilate(
        self, context: Context, observation: Symbol, learning_rate: float
    ) -> Tuple[float, Tuple[str, ...]]:  # pragma: no cover
        """Update beliefs; return (confidence_delta, latent_concepts)."""
        ...

    def model_view(self, context: Context) -> InternalModelView:  # pragma: no cover
        """Return the localized world model (rule + exceptions) for a context."""
        ...


@dataclass
class DirichletMarkovModel:
    """A variable-order Markov model with a symmetric Dirichlet prior.

    Each distinct context (the last ``order`` symbols) owns a ``Counter`` of
    successor symbols. The predictive distribution applies additive (Laplace /
    Dirichlet) smoothing so that *every* symbol — including the reserved
    :data:`NOVEL` category — keeps strictly positive probability. Positive
    probability everywhere is what makes surprisal finite and well defined.

        P(s | c) = (n(c, s) + alpha) / (N(c) + alpha * |support|)

    The model is open-vocabulary: the symbol set grows as observations arrive,
    and unseen successors are absorbed by the :data:`NOVEL` slot until they are
    witnessed for the first time.
    """

    order: int = 1
    alpha: float = 0.5
    crystallize_threshold: float = 0.80
    crystallize_min_count: float = 3.0
    motif_threshold: float = 3.0

    _counts: Dict[Context, Counter] = field(default_factory=dict)
    _symbols: set = field(default_factory=set)
    #: Literal, unweighted transition tallies (incremented by exactly 1 per
    #: observation). Distinct from ``_counts``, which holds precision-weighted
    #: Dirichlet mass for probability estimation. ``_occurrences`` is the honest
    #: "how many times did this actually happen" ledger that backs the causal
    #: "observed 'Day -> Night' 4 times previously" explanation (C2).
    _occurrences: Dict[Context, Counter] = field(default_factory=dict)

    # --- distribution machinery --------------------------------------------

    def _support(self, context: Context, extra: Sequence[Symbol] = ()) -> Tuple[Symbol, ...]:
        """Candidate symbols considered for a context.

        Predictive mass is spread over the *entire* known vocabulary (not just
        successors seen after this particular context) plus the NOVEL slot, so
        an unfamiliar context yields a meaningful high-entropy prediction rather
        than collapsing to certainty about novelty.
        """
        support = set(self._symbols)
        support.update(self._counts.get(context, ()))
        support.update(extra)
        support.add(NOVEL)
        return tuple(sorted(support))

    def _distribution(self, context: Context, extra: Sequence[Symbol] = ()) -> Dict[Symbol, float]:
        """Smoothed predictive distribution P(. | context) over the support."""
        counter = self._counts.get(context)
        support = self._support(context, extra)
        total = float(sum(counter.values())) if counter else 0.0
        denom = total + self.alpha * len(support)
        dist: Dict[Symbol, float] = {}
        for symbol in support:
            raw = 0.0 if (symbol == NOVEL or counter is None) else float(counter.get(symbol, 0.0))
            dist[symbol] = (raw + self.alpha) / denom
        return dist

    # --- GenerativeModel API ------------------------------------------------

    def predict(self, context: Context) -> Prediction:
        dist = self._distribution(context)
        ordered = tuple(sorted(dist.items(), key=lambda kv: (-kv[1], kv[0])))
        predicted_symbol, predicted_probability = ordered[0]
        entropy = -sum(p * _safe_log2(p) for _, p in ordered)
        support = float(self._occurrences.get(context, Counter()).get(predicted_symbol, 0.0))
        return Prediction(
            context=context,
            distribution=ordered,
            predicted_symbol=predicted_symbol,
            predicted_probability=predicted_probability,
            entropy=entropy,
            novelty_mass=dist[NOVEL],
            predicted_support=support,
            rationale=self._rationale(context, predicted_symbol, support),
        )

    def _rationale(self, context: Context, symbol: Symbol, support: float) -> str:
        """Compose the causal "because" explanation for a forecast (C2).

        The explanation is grounded in the literal occurrence ledger, so it
        states what the engine has actually *witnessed* rather than its smoothed
        belief — making the justification auditable.
        """
        ctx_repr = " ".join(context) if context else "(empty)"
        if symbol == NOVEL:
            return f"no successor has ever followed [{ctx_repr}]; bracing for novelty."
        if support <= 0.0:
            return (
                f"no direct evidence for '{ctx_repr} -> {symbol}'; "
                f"this is a prior-driven guess, not a learned transition."
            )
        times = "time" if support == 1 else "times"
        return f"observed '{ctx_repr} -> {symbol}' {support:g} {times} previously."

    def model_view(self, context: Context) -> InternalModelView:
        """Distil the localized world model for ``context`` (C2: Internal Model).

        The dominant real successor becomes the *rule*; its smoothed probability
        is the rule's *confidence*. Every other witnessed successor is logged as
        an *exception* with its empirical relative frequency — the deviations the
        rule has so far failed to account for.
        """
        dist = self._distribution(context)
        real = [(s, p) for s, p in dist.items() if s != NOVEL]
        if real:
            rule_consequent, rule_confidence = max(real, key=lambda kv: (kv[1], kv[0]))
        else:
            rule_consequent, rule_confidence = None, 0.0

        occ = self._occurrences.get(context, Counter())
        total_occ = float(sum(occ.values()))
        rule_support = float(occ.get(rule_consequent, 0.0)) if rule_consequent else 0.0

        exceptions = []
        if total_occ > 0.0:
            for sym, count in sorted(occ.items(), key=lambda kv: (-kv[1], kv[0])):
                if sym == rule_consequent:
                    continue
                exceptions.append((sym, float(count) / total_occ))

        return InternalModelView(
            context=context,
            rule_consequent=rule_consequent,
            rule_confidence=rule_confidence,
            rule_support=rule_support,
            exceptions=tuple(exceptions),
        )

    def assimilate(
        self, context: Context, observation: Symbol, learning_rate: float
    ) -> Tuple[float, Tuple[str, ...]]:
        """Fold an observation into beliefs and report the consequences.

        The update is a Dirichlet count increment of magnitude ``learning_rate``.
        The engine sets that rate from precision-weighted prediction error, so a
        surprising observation moves the beliefs further than a routine one —
        active inference's core learning signal.

        Returns
        -------
        confidence_delta : float
            KL(posterior || prior) in bits for this context's predictive
            distribution. As a context's counts accumulate, a single increment
            perturbs the distribution less and less, so this naturally decays
            toward zero — the signature of a stabilising belief.
        latent_concepts : tuple of str
            Structural patterns detected on this tick (see below).
        """
        is_novel_symbol = observation not in self._symbols

        # Prior and posterior are evaluated over an identical support (both
        # include ``observation`` and NOVEL) so the KL is exactly defined.
        prior = self._distribution(context, extra=(observation,))

        counter = self._counts.setdefault(context, Counter())
        counter[observation] += learning_rate
        self._symbols.add(observation)

        # Literal tally: this transition happened exactly once more, regardless
        # of how strongly precision-weighting nudged the belief. Backs the
        # auditable "observed N times" causal explanation (C2).
        self._occurrences.setdefault(context, Counter())[observation] += 1

        posterior = self._distribution(context, extra=(observation,))
        confidence_delta = _kl_divergence(posterior, prior)

        concepts = self._detect_concepts(context, observation, is_novel_symbol)
        return confidence_delta, concepts

    # --- concept formation --------------------------------------------------

    def _detect_concepts(
        self, context: Context, observation: Symbol, is_novel_symbol: bool
    ) -> Tuple[str, ...]:
        """Surface temporary structural patterns implied by the latest tick.

        Three kinds of latent structure are reported:

        * ``novel``      — a symbol never seen anywhere before (vocabulary growth).
        * ``crystallize``— a context whose successor distribution has collapsed
          toward near-determinism: an emergent rule / concept.
        * ``motif``      — a context->successor transition seen often enough to
          count as a recurring pattern.
        """
        concepts = []
        if is_novel_symbol:
            concepts.append(f"novel::{observation}")

        counter = self._counts[context]
        total = float(sum(counter.values()))
        ctx_repr = " ".join(context) if context else "(empty)"

        observed_count = counter.get(observation, 0.0)
        if observed_count >= self.motif_threshold:
            concepts.append(f"motif::({ctx_repr})->{observation} x{observed_count:g}")

        if total >= self.crystallize_min_count:
            best_symbol, best_count = max(counter.items(), key=lambda kv: kv[1])
            best_prob = (best_count + self.alpha) / (
                total + self.alpha * len(self._support(context))
            )
            if best_prob >= self.crystallize_threshold:
                concepts.append(f"crystallize::({ctx_repr})=>{best_symbol}~{best_prob:.2f}")

        return tuple(concepts)

    # --- introspection ------------------------------------------------------

    @property
    def vocabulary_size(self) -> int:
        """Number of distinct symbols witnessed so far (excludes NOVEL/BOS)."""
        return len({s for s in self._symbols if s not in (NOVEL, BOS)})

    @property
    def context_count(self) -> int:
        """Number of distinct contexts the model has formed beliefs about."""
        return len(self._counts)

    # --- Probationary Concept Pipeline introspection -----------------------

    @property
    def rule_count(self) -> int:
        """Number of contexts that have witnessed at least one real transition.

        Each such context contributes one dominant *rule* to the engine's
        Internal Model — the headcount of general rules the Free-Energy health
        monitor charges as structural load ``A``.
        """
        return len(self._occurrences)

    @property
    def exception_count(self) -> int:
        """Total non-dominant transition *events* across every context.

        For each context the dominant successor is the rule; every event that
        landed on some *other* successor is an un-absorbed anomaly. Summed over
        all contexts this is the quarantine backlog the health monitor penalises
        super-linearly — and the magnitude of the "pile-up" that drives the
        engine toward EXHAUSTION.
        """
        total = 0
        for occ in self._occurrences.values():
            if len(occ) > 1:
                dominant = max(occ.values())
                total += int(sum(occ.values()) - dominant)
        return total

    def fragmented_contexts(self) -> List[Context]:
        """Contexts carrying >= 2 isolated exceptions, worst-fragmented first.

        These are the regimes whose anomalies might be compressible behind a
        single latent concept — the hunting ground for concept birth.
        """
        ranked = []
        for ctx, occ in self._occurrences.items():
            distinct_exceptions = max(0, len(occ) - 1)
            if distinct_exceptions >= 2:
                ranked.append((ctx, distinct_exceptions))
        ranked.sort(key=lambda kv: kv[1], reverse=True)
        return [ctx for ctx, _ in ranked]


# ---------------------------------------------------------------------------
# C6 — Stable Belief Revision: the multidimensional belief substrate
# ---------------------------------------------------------------------------

#: Support count at which a rule's stability crosses 0.5. Because stability
#: rises logarithmically, this is a "half-maturity" knob: smaller -> rules earn
#: protection faster. Tuned so a rule confirmed a handful of times already
#: resists single anomalies, while a rule seen once is still plastic.
STABILITY_HALF_MATURITY: float = 4.0

#: Fraction at which ``contradiction_count / support_count`` is deemed to have
#: "approached" support, licensing the core rule to fracture and be revised.
FRACTURE_THRESHOLD: float = 0.85


def _stability_of(support_count: int) -> float:
    """Logarithmic stability curve in [0, 1) as a function of support.

    ``stability(n) = ln(1 + n) / (ln(1 + n) + ln(1 + HALF_MATURITY))``

    The ``ln(1 + HALF_MATURITY)`` denominator term is exactly the numerator
    when ``n == HALF_MATURITY``, so stability passes through 0.5 there and then
    saturates ever more slowly — diminishing returns on additional evidence,
    the hallmark of a logarithmic confidence-in-history measure.
    """
    if support_count <= 0:
        return 0.0
    s = math.log1p(float(support_count))
    return s / (s + math.log1p(STABILITY_HALF_MATURITY))


@dataclass
class BeliefException:
    """A single quarantined anomaly filed against a parent :class:`Belief`.

    Exceptions are *not* allowed to rewrite the rule on contact. They accrue
    their own episodic tally here, in isolation, so the engine can recognise a
    genuine regime shift (a persistent, growing exception) and distinguish it
    from transient noise (a one-off ``storm``) — without the noise ever touching
    the core rule's confidence beyond the tiny inertia-scaled erosion.
    """

    symbol: Symbol
    count: int = 0
    first_tick: int = 0
    last_tick: int = 0


@dataclass
class Belief:
    """A multidimensional belief about the dominant rule for one context.

    Where the flat substrate held only a smoothed probability — and so let a
    burst of anomalies wash a mature rule away — a ``Belief`` carries the
    structure needed to *defend* itself:

    * ``confidence``         — P(the rule holds), in [0, 1].
    * ``stability``          — derived, in [0, 1): resistance to change, rising
                               logarithmically with ``support_count``.
    * ``support_count``      — raw episodic confirmations.
    * ``contradiction_count``— raw episodic anomalies (sum over exceptions).
    * ``exceptions``         — the quarantine: anomalies filed by symbol.
    """

    consequent: Optional[Symbol] = None
    confidence: float = 0.0
    support_count: int = 0
    contradiction_count: int = 0
    exceptions: Dict[Symbol, BeliefException] = field(default_factory=dict)

    @property
    def stability(self) -> float:
        """Inertia of this belief — see :func:`_stability_of`."""
        return _stability_of(self.support_count)

    @property
    def fracture_ratio(self) -> float:
        """``contradiction_count / support_count`` (1.0 if unsupported)."""
        if self.support_count <= 0:
            return 1.0 if self.contradiction_count > 0 else 0.0
        return self.contradiction_count / self.support_count

    @property
    def is_fractured(self) -> bool:
        """True once contradictions have *approached* support (C6 trigger)."""
        return self.fracture_ratio >= FRACTURE_THRESHOLD

    def dominant_exception(self) -> Optional[BeliefException]:
        """The most-witnessed quarantined anomaly, if any."""
        if not self.exceptions:
            return None
        return max(self.exceptions.values(), key=lambda e: (e.count, e.symbol))


@dataclass
class StableBeliefModel:
    """A belief substrate that resists catastrophic forgetting (C6).

    Implements the same :class:`GenerativeModel` contract as
    :class:`DirichletMarkovModel`, so it slots into :class:`CognitiveEngine`
    unchanged — but the mechanics are fundamentally different. Instead of one
    Dirichlet counter per context it holds one :class:`Belief` per context, and
    folds evidence in under two laws:

    **The Inertia Learning Law.** The effective learning rate scales *inversely*
    with stability::

        effective_rate = base_rate * (1 - stability)

    A young rule (stability ~0) moves at the full ``base_rate``; a mature rule
    (stability -> 1) is almost frozen, so an anomaly is absorbed with only a
    sliver of confidence lost. This is the precise inverse of the precision-
    weighted law that caused forgetting, where surprise *amplified* the update.

    **Exception Quarantine.** A contradicting observation is filed as a
    :class:`BeliefException` inside the parent belief rather than diluting the
    rule's mass. The rule only *fractures* — promoting its dominant exception to
    the new rule — once ``contradiction_count`` approaches ``support_count``
    (:data:`FRACTURE_THRESHOLD`). Sustained evidence revises the model; noise
    does not.
    """

    order: int = 1
    base_rate: float = 0.20
    bootstrap_confidence: float = 0.50
    #: Small uniform floor mass keeping every symbol's probability strictly
    #: positive (so surprisal stays finite), analogous to Dirichlet smoothing.
    epsilon: float = 0.02
    crystallize_threshold: float = 0.80
    motif_threshold: float = 3.0

    _beliefs: Dict[Context, Belief] = field(default_factory=dict)
    _symbols: set = field(default_factory=set)
    _tick: int = 0

    # --- distribution machinery --------------------------------------------

    def _support(self, context: Context, extra: Sequence[Symbol] = ()) -> Tuple[Symbol, ...]:
        support = set(self._symbols)
        support.update(extra)
        support.add(NOVEL)
        belief = self._beliefs.get(context)
        if belief is not None and belief.consequent is not None:
            support.add(belief.consequent)
            support.update(belief.exceptions.keys())
        return tuple(sorted(support))

    def _distribution(self, context: Context, extra: Sequence[Symbol] = ()) -> Dict[Symbol, float]:
        """Predictive distribution synthesised from the context's belief.

        The rule's consequent receives mass equal to its ``confidence``; the
        residual ``1 - confidence`` is split across the quarantined exceptions
        in proportion to their counts (or parked on NOVEL if there are none). A
        uniform ``epsilon`` floor over the whole support keeps every symbol
        strictly positive so surprisal is always defined.
        """
        support = self._support(context, extra)
        dist: Dict[Symbol, float] = {s: self.epsilon for s in support}

        belief = self._beliefs.get(context)
        if belief is None or belief.consequent is None:
            # Uninformed prior: structured mass spread uniformly.
            share = 1.0 / len(support)
            for s in support:
                dist[s] += share
        else:
            dist[belief.consequent] += belief.confidence
            leftover = max(0.0, 1.0 - belief.confidence)
            total_exc = sum(e.count for e in belief.exceptions.values())
            if total_exc > 0:
                for sym, exc in belief.exceptions.items():
                    dist[sym] += leftover * (exc.count / total_exc)
            else:
                dist[NOVEL] += leftover

        normaliser = sum(dist.values())
        return {s: v / normaliser for s, v in dist.items()}

    # --- GenerativeModel API ------------------------------------------------

    def predict(self, context: Context) -> Prediction:
        dist = self._distribution(context)
        ordered = tuple(sorted(dist.items(), key=lambda kv: (-kv[1], kv[0])))
        predicted_symbol, predicted_probability = ordered[0]
        entropy = -sum(p * _safe_log2(p) for _, p in ordered)
        belief = self._beliefs.get(context)
        support = (
            float(belief.support_count)
            if belief is not None and belief.consequent == predicted_symbol
            else 0.0
        )
        return Prediction(
            context=context,
            distribution=ordered,
            predicted_symbol=predicted_symbol,
            predicted_probability=predicted_probability,
            entropy=entropy,
            novelty_mass=dist[NOVEL],
            predicted_support=support,
            rationale=self._rationale(context, belief),
        )

    def _rationale(self, context: Context, belief: Optional[Belief]) -> str:
        """Explain the forecast in terms of accumulated, defended evidence (C2)."""
        ctx_repr = " ".join(context) if context else "(empty)"
        if belief is None or belief.consequent is None:
            return f"no rule has formed for [{ctx_repr}] yet; bracing for novelty."
        times = "time" if belief.support_count == 1 else "times"
        tail = ""
        if belief.contradiction_count > 0:
            tail = (
                f", holding firm against {belief.contradiction_count} "
                f"contradiction(s) via stability {belief.stability:.2f}"
            )
        return (
            f"rule '{ctx_repr} -> {belief.consequent}' confirmed "
            f"{belief.support_count} {times}{tail}."
        )

    def model_view(self, context: Context) -> InternalModelView:
        belief = self._beliefs.get(context)
        if belief is None or belief.consequent is None:
            return InternalModelView(
                context=context,
                rule_consequent=None,
                rule_confidence=0.0,
                rule_support=0.0,
                exceptions=(),
                stability=0.0,
                support_count=0,
                contradiction_count=0,
            )

        total_events = float(belief.support_count + belief.contradiction_count)
        exceptions: list = []
        for sym, exc in sorted(belief.exceptions.items(), key=lambda kv: (-kv[1].count, kv[0])):
            freq = (exc.count / total_events) if total_events > 0 else 0.0
            exceptions.append((sym, freq))

        return InternalModelView(
            context=context,
            rule_consequent=belief.consequent,
            rule_confidence=belief.confidence,
            rule_support=float(belief.support_count),
            exceptions=tuple(exceptions),
            stability=belief.stability,
            support_count=belief.support_count,
            contradiction_count=belief.contradiction_count,
        )

    def assimilate(
        self, context: Context, observation: Symbol, learning_rate: float
    ) -> Tuple[float, Tuple[str, ...]]:
        """Fold an observation in under the Inertia Law + Exception Quarantine.

        ``learning_rate`` is interpreted as the *base* rate; the inertia law
        applies the ``(1 - stability)`` factor here, where the belief's history
        lives. Confirmations reinforce the rule and raise stability;
        contradictions are quarantined and erode confidence only feebly when the
        rule is mature.
        """
        self._tick += 1
        is_novel_symbol = observation not in self._symbols

        prior = self._distribution(context, extra=(observation,))

        belief = self._beliefs.get(context)
        if belief is None or belief.consequent is None:
            # Bootstrap the rule from its first real observation.
            belief = Belief(
                consequent=observation,
                confidence=self.bootstrap_confidence,
                support_count=1,
            )
            self._beliefs[context] = belief
        elif observation == belief.consequent:
            # CONFIRMATION — the rule held. Reinforce toward certainty. The
            # inertia factor means an already-mature rule barely needs the nudge.
            belief.support_count += 1
            effective_rate = learning_rate * (1.0 - belief.stability)
            belief.confidence += effective_rate * (1.0 - belief.confidence)
        else:
            # CONTRADICTION — quarantine, do NOT overwrite the rule.
            belief.contradiction_count += 1
            exc = belief.exceptions.get(observation)
            if exc is None:
                exc = BeliefException(symbol=observation, first_tick=self._tick)
                belief.exceptions[observation] = exc
            exc.count += 1
            exc.last_tick = self._tick

            # Inertia Law: erosion scales inversely with stability. A mature
            # rule (high stability) loses only a sliver of confidence; this is
            # the direct antidote to catastrophic forgetting.
            effective_rate = learning_rate * (1.0 - belief.stability)
            belief.confidence += effective_rate * (0.0 - belief.confidence)

            # The rule fractures only once contradictions approach support.
            if belief.is_fractured:
                self._refracture(belief)

        self._symbols.add(observation)

        posterior = self._distribution(context, extra=(observation,))
        confidence_delta = _kl_divergence(posterior, prior)
        concepts = self._detect_concepts(context, observation, is_novel_symbol, belief)
        return confidence_delta, concepts

    def _refracture(self, belief: Belief) -> None:
        """Revise a fractured belief by promoting its dominant exception.

        Only fires once :attr:`Belief.is_fractured` and the dominant exception
        has genuinely *overtaken* the incumbent rule's support. The old rule is
        demoted into the quarantine rather than discarded, so the engine can
        re-promote it if the regime shifts back — belief revision, not amnesia.
        """
        dominant = belief.dominant_exception()
        if dominant is None or dominant.count <= belief.support_count:
            return

        old_consequent = belief.consequent
        old_support = belief.support_count

        # Promote the dominant exception to the new rule.
        del belief.exceptions[dominant.symbol]
        belief.consequent = dominant.symbol
        belief.support_count = dominant.count

        # Demote the former rule into the quarantine.
        if old_consequent is not None:
            demoted = belief.exceptions.get(old_consequent)
            if demoted is None:
                demoted = BeliefException(symbol=old_consequent, first_tick=self._tick)
                belief.exceptions[old_consequent] = demoted
            demoted.count += old_support
            demoted.last_tick = self._tick

        belief.contradiction_count = sum(e.count for e in belief.exceptions.values())
        denom = belief.support_count + belief.contradiction_count
        belief.confidence = belief.support_count / denom if denom > 0 else self.bootstrap_confidence

    # --- concept formation --------------------------------------------------

    def _detect_concepts(
        self,
        context: Context,
        observation: Symbol,
        is_novel_symbol: bool,
        belief: Belief,
    ) -> Tuple[str, ...]:
        """Surface structural patterns, now including stability milestones (C6)."""
        concepts = []
        ctx_repr = " ".join(context) if context else "(empty)"

        if is_novel_symbol:
            concepts.append(f"novel::{observation}")

        if belief.consequent == observation and belief.support_count >= self.motif_threshold:
            concepts.append(f"motif::({ctx_repr})->{observation} x{belief.support_count}")

        if belief.consequent is not None and belief.confidence >= self.crystallize_threshold:
            concepts.append(
                f"crystallize::({ctx_repr})=>{belief.consequent}~{belief.confidence:.2f}"
            )

        # C6: a belief that has earned protection, and one under genuine threat.
        if belief.stability >= 0.66:
            concepts.append(
                f"protected::({ctx_repr})->{belief.consequent}@stab{belief.stability:.2f}"
            )
        if belief.is_fractured:
            concepts.append(
                f"fracture::({ctx_repr}) contra{belief.contradiction_count}>="
                f"{FRACTURE_THRESHOLD:g}*supp{belief.support_count}"
            )

        return tuple(concepts)

    # --- introspection ------------------------------------------------------

    @property
    def vocabulary_size(self) -> int:
        """Number of distinct symbols witnessed so far (excludes NOVEL/BOS)."""
        return len({s for s in self._symbols if s not in (NOVEL, BOS)})

    @property
    def context_count(self) -> int:
        """Number of distinct contexts the model has formed beliefs about."""
        return len(self._beliefs)

    # --- Probationary Concept Pipeline introspection -----------------------

    @property
    def rule_count(self) -> int:
        """Number of contexts holding a formed dominant rule.

        Feeds the Free-Energy health monitor's structural-load term as the
        count of general rules currently compressing the world.
        """
        return sum(1 for b in self._beliefs.values() if b.consequent is not None)

    @property
    def exception_count(self) -> int:
        """Total quarantined anomaly *events* across every belief.

        Counts the raw contradiction tally each belief is holding — i.e. how
        many times reality has defied a rule and been parked in its quarantine
        — not merely the number of distinct exception symbols. This is the true
        "pile-up" the task cares about: a context contradicted ten times is far
        more exhausting than one contradicted twice, even if both quarantine the
        same two symbols. When this backlog outpaces the rules, the health
        monitor tips into EXHAUSTION — the trigger for concept birth.
        """
        return sum(b.contradiction_count for b in self._beliefs.values())

    def fragmented_contexts(self) -> List[Context]:
        """Contexts whose quarantine holds >= 2 exceptions, worst first.

        Ranked by raw contradiction count then exception multiplicity, so the
        most strained regime is offered to the concept-birth arbiter first.
        """
        ranked = []
        for ctx, belief in self._beliefs.items():
            n_exc = len(belief.exceptions)
            if n_exc >= 2:
                ranked.append((ctx, belief.contradiction_count, n_exc))
        ranked.sort(key=lambda kv: (kv[1], kv[2]), reverse=True)
        return [ctx for ctx, _, _ in ranked]


# ---------------------------------------------------------------------------
# Probationary Concept Pipeline — Stage 0 hypothesis lifecycle
# ---------------------------------------------------------------------------

#: Minimum number of *deviation* ticks (observations in a context that are NOT
#: the dominant rule) a probationary concept must witness before its verdict is
#: rendered. We only score deviations because that is precisely the regime the
#: abstraction exists to compress — the rule holding is no test of it.
PROBATION_MIN_TRIALS: int = 3

#: Fraction of deviation ticks that must land *inside* the concept's member set
#: for it to be judged a genuine latent structure rather than a coincidence. If
#: anomalies keep diversifying beyond the concept, coverage falls and it fails.
PROBATION_CONFIRM_HIT_RATE: float = 0.60


@dataclass
class ProbationaryConcept:
    """A candidate concept living in Stage 0 — injected, watched, not committed.

    A birthed :class:`concept_birth.LatentConcept` is *not* written into the
    belief substrate. Instead it is wrapped here as a temporary overlay on the
    engine: a hypothesis that the quarantined exceptions of one context are in
    fact a single latent thing. The engine then watches future deviations in
    that context to see whether the abstraction *actually* keeps capturing the
    anomalies (``CONFIRMED``) or whether reality keeps inventing fresh ones the
    concept cannot hold (``REJECTED``). Nothing is ever persisted from here;
    promotion to a real rule is a later milestone's job.
    """

    label: str  #: Human handle, e.g. ``"Concept_01"``.
    context: Context  #: The context whose quarantine it abstracts.
    members: frozenset  #: Exception symbols the concept absorbs.
    rule_symbol: Optional[Symbol]  #: The incumbent rule at birth (a non-deviation).
    promised_bits: float  #: Predictive bits the birth math promised to save.
    born_tick: int  #: Engine tick at which probation opened.
    trials: int = 0  #: Deviation ticks witnessed since birth.
    hits: int = 0  #: Deviations that fell inside ``members``.
    realized_bits: float = 0.0  #: Bits actually re-confirmed at verdict time.
    verdict: str = "PROBATION"  #: PROBATION | CONFIRMED | REJECTED.

    @property
    def coverage(self) -> float:
        """Share of deviation ticks the concept successfully absorbed."""
        return self.hits / self.trials if self.trials else 0.0

    @property
    def is_active(self) -> bool:
        return self.verdict == "PROBATION"


@dataclass
class PipelineTick:
    """The Probationary Concept Pipeline's output for a single observation.

    Bundles the per-tick Free-Energy vitals with any alert lines the pipeline
    wishes the monitor to surface (candidate births, probation verdicts).
    """

    health: Optional["HealthReport"]
    alerts: List[str] = field(default_factory=list)


def _render_candidate_banner(pc: ProbationaryConcept, decision: "ConceptBirthDecision") -> str:
    """Render the massive ``[!] CANDIDATE HYPOTHESIS GENERATED`` alert."""
    members = ", ".join(sorted(pc.members))
    ctx = " ".join(pc.context) if pc.context else "(empty)"
    width = 70
    bar = "=" * width
    return "\n".join(
        [
            "",
            bar,
            f"  [!] CANDIDATE HYPOTHESIS GENERATED: {pc.label}",
            bar,
            "  trigger     : COGNITIVE EXHAUSTION — quarantined exceptions piling up",
            f"  context     : [{ctx}]",
            f"  absorbs     : {{{members}}}  ({len(pc.members)} isolated exceptions)",
            f"  promises    : {decision.bits_eliminated:.4f} bits of predictive "
            f"uncertainty reduced",
            f"                H_before {decision.h_before:.3f} -> H_after "
            f"{decision.h_after:.3f} bits  "
            f"(gain {decision.gain_bits:+.3f} > threshold {decision.threshold_bits:.2f})",
            "  status      : PROBATION (Stage 0) — injected as a TEMPORARY rule,",
            "                NOT committed. Watching future deviations to confirm it",
            "                truly cuts surprise before any permanent promotion.",
            bar,
        ]
    )


def _render_probation_verdict(pc: ProbationaryConcept) -> str:
    """Render the resolution line when a probationary concept matures."""
    if pc.verdict == "CONFIRMED":
        return (
            f"  [probation] {pc.label} CONFIRMED after {pc.trials} deviation "
            f"trials (coverage {pc.coverage:.2f}, realized {pc.realized_bits:.4f} "
            f"bits). The temporary rule earned its keep — eligible for promotion."
        )
    return (
        f"  [probation] {pc.label} REJECTED after {pc.trials} deviation trials "
        f"(coverage {pc.coverage:.2f}). The abstraction failed to keep cutting "
        f"future surprise — temporary rule withdrawn, nothing committed."
    )


# ---------------------------------------------------------------------------
# CognitiveEngine — the continuous predict / collide / adapt loop
# ---------------------------------------------------------------------------


class CognitiveEngine:
    """A continuous predictive-processing loop, not a linear pipeline.

    The engine *always* holds a standing prediction (:meth:`predict_next_state`)
    generated before any input arrives. When an observation lands
    (:meth:`process_observation`) it is collided with that standing prediction
    to compute surprise, then beliefs are updated (:meth:`adapt`) and the next
    prediction is immediately regenerated. The simulation never idles waiting
    for input — it is perpetually anticipating.
    """

    def __init__(
        self,
        model: Optional[GenerativeModel] = None,
        *,
        order: int = 1,
        precision_gain: float = 3.0,
        base_learning_rate: float = 0.20,
        surprise_threshold: float = 2.0,
    ) -> None:
        # C6: the default substrate is now the StableBeliefModel, whose
        # multidimensional beliefs resist catastrophic forgetting. Pass an
        # explicit ``DirichletMarkovModel`` to fall back to the flat C1-C3
        # substrate for comparison.
        self.model: GenerativeModel = (
            model
            if model is not None
            else StableBeliefModel(order=order, base_rate=base_learning_rate)
        )
        self.order: int = order
        #: Retained for surprise/attention *reporting* only. Under C6 it no
        #: longer modulates the learning rate (that is governed by stability).
        self.precision_gain: float = precision_gain
        self.base_learning_rate: float = base_learning_rate
        #: Surprise (bits) above which the engine stops merely re-weighting and
        #: starts positing causal hypotheses — the C3 dissonance trigger.
        self.surprise_threshold: float = surprise_threshold

        self._context: Deque[Symbol] = deque([BOS] * max(order, 1), maxlen=max(order, 1))
        self._history: list[Experience] = []
        self._tick: int = 0
        self._cumulative_surprise: float = 0.0

        # Probationary Concept Pipeline state. Candidate concepts birthed under
        # cognitive exhaustion live here as temporary overlays — never written
        # into ``self.model`` — until probation confirms or rejects them.
        self._probation: List[ProbationaryConcept] = []
        self._concept_serial: int = 0

        # The engine is born already predicting (everything is novelty at t=0).
        self._standing_prediction: Prediction = self.model.predict(self._current_context())

    # --- context helpers ----------------------------------------------------

    def _current_context(self) -> Context:
        return tuple(self._context)

    # --- the loop -----------------------------------------------------------

    def predict_next_state(self) -> Prediction:
        """The expectation the engine currently holds about the next symbol.

        Always available, by construction — this is the standing simulation.
        """
        return self._standing_prediction

    def process_observation(self, observation: Symbol) -> Experience:
        """Collide reality with expectation and emit a single ``Experience``.

        This is one full tick of cognition: measure surprise against the
        standing prediction, adapt beliefs in proportion to it, advance the
        context, and regenerate the next standing prediction.
        """
        prediction = self._standing_prediction
        context = prediction.context

        probability = prediction.probability_of(observation)
        prediction_error = -_safe_log2(probability)  # surprisal, in bits
        attention_weight = 1.0 - probability  # precision of the residual, [0, 1]

        confidence_delta, latent_concepts = self.adapt(context, observation, attention_weight)

        # C2: read back the localized world model *after* assimilation, so the
        # REPL shows the engine's current theory of this context.
        internal_model = self._model_view(context)

        # C3: a sufficiently large surprise is not just a weight update — it is
        # a failure of the engine's causal theory. Flag the dissonance and posit
        # a missing intermediate cause rather than silently absorbing it.
        causal_hypothesis: Optional[str] = None
        if prediction_error > self.surprise_threshold:
            causal_hypothesis = self._generate_hypothesis(prediction, observation, internal_model)

        experience = Experience(
            timestamp=time.time(),
            prediction=prediction,
            observation=observation,
            prediction_error=prediction_error,
            attention_weight=attention_weight,
            latent_concepts=latent_concepts,
            confidence_delta=confidence_delta,
            internal_model=internal_model,
            causal_hypothesis=causal_hypothesis,
        )

        # Advance the continuous simulation: shift context, regenerate forecast.
        self._context.append(observation)
        self._tick += 1
        self._cumulative_surprise += prediction_error
        self._history.append(experience)
        self._standing_prediction = self.model.predict(self._current_context())

        return experience

    def adapt(
        self, context: Context, observation: Symbol, attention_weight: float
    ) -> Tuple[float, Tuple[str, ...]]:
        """Update internal beliefs under the C6 Inertia Learning Law.

        The learning rate is **no longer precision-weighted**. That old law —
        ``base_rate * (1 + precision_gain * attention)`` — amplified the update
        for surprising observations, which is exactly what let a couple of
        anomalies (``storm``, ``clouds``) collapse a well-established rule: the
        more shocking the anomaly, the harder the engine over-wrote its history.

        Instead the engine passes the *base* rate to the substrate, which scales
        it inversely with the belief's own stability::

            effective_rate = base_rate * (1 - stability)

        so a mature rule barely moves. ``attention_weight`` is still computed and
        reported (it drives surprise and the C3 hypothesis trigger), but it no
        longer touches learning.
        """
        return self.model.assimilate(context, observation, self.base_learning_rate)

    def _model_view(self, context: Context) -> Optional[InternalModelView]:
        """Read the localized world model, tolerating substrates lacking it."""
        view = getattr(self.model, "model_view", None)
        return view(context) if callable(view) else None

    def _generate_hypothesis(
        self,
        prediction: Prediction,
        observation: Symbol,
        internal_model: Optional[InternalModelView],
    ) -> str:
        """Author a causal question in response to a surprising failure (C3).

        Two flavours of dissonance are distinguished:

        * **Violated rule** — the engine held a confident expectation that was
          contradicted. It asks why the expected consequent failed and frames
          the actual observation as a candidate *intermediate event* (a missing
          link in its causal chain).
        * **Pure novelty** — there was no real expectation to violate. The
          engine instead fires a curiosity trigger about an unmodelled cause.
        """
        ctx_repr = " ".join(prediction.context) if prediction.context else "the current context"
        expected = prediction.predicted_symbol

        if expected not in (NOVEL,) and expected != observation:
            note = ""
            if internal_model is not None and internal_model.has_rule:
                note = (
                    f" My rule '{internal_model.rule_str()}' just failed; "
                    f"'{observation}' may be a hidden cause it does not model."
                )
            return (
                f"Why did {expected} not follow {ctx_repr}? "
                f"What is the intermediate event '{observation}'?{note}"
            )

        return (
            f"Unprecedented event '{observation}' in context [{ctx_repr}]. "
            f"What latent cause or regime shift could explain its sudden appearance?"
        )

    # --- introspection ------------------------------------------------------

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def mean_surprise(self) -> float:
        """Average surprise per tick so far, in bits."""
        return self._cumulative_surprise / self._tick if self._tick else 0.0

    @property
    def history(self) -> Tuple[Experience, ...]:
        return tuple(self._history)

    def belief_summary(self) -> Dict[str, object]:
        """A compact snapshot of the engine's internal state."""
        vocab = getattr(self.model, "vocabulary_size", None)
        contexts = getattr(self.model, "context_count", None)
        summary: Dict[str, object] = {
            "tick": self._tick,
            "context": list(self._current_context()),
            "vocabulary_size": vocab,
            "contexts_learned": contexts,
            "mean_surprise_bits": round(self.mean_surprise, 4),
            "current_expectation": self._standing_prediction.predicted_symbol,
            "expectation_confidence": round(self._standing_prediction.predicted_probability, 4),
            "expectation_entropy_bits": round(self._standing_prediction.entropy, 4),
            "expectation_rationale": self._standing_prediction.rationale,
        }
        # C6: surface the stability / support / contradiction of the rule the
        # engine currently holds for its live context.
        view = self._model_view(self._current_context())
        if view is not None and view.has_rule:
            summary.update(
                {
                    "rule": view.rule_str(),
                    "rule_stability": round(view.stability, 4),
                    "rule_support_count": view.support_count,
                    "rule_contradiction_count": view.contradiction_count,
                    "rule_fracture_ratio": round(view.fracture_ratio, 4),
                }
            )
        return summary

    # --- Probationary Concept Pipeline -------------------------------------

    @property
    def probation(self) -> Tuple[ProbationaryConcept, ...]:
        """All probationary concepts ever opened this session (any verdict)."""
        return tuple(self._probation)

    def active_probation(
        self, context: Optional[Context] = None
    ) -> Tuple[ProbationaryConcept, ...]:
        """Probationary concepts still under test, optionally for one context."""
        items = [pc for pc in self._probation if pc.is_active]
        if context is not None:
            items = [pc for pc in items if pc.context == context]
        return tuple(items)

    def vitals(self, recent_surprise: float) -> Optional["HealthReport"]:
        """Build the Free-Energy :class:`HealthReport` for the current state.

        Maps the engine's live state onto the health monitor's inputs:

        * ``H`` (entropy)   — uncertainty of the *current* standing prediction.
        * ``S`` (surprise)  — the prediction error of the tick just lived.
        * ``rules``         — count of dominant rules in the Internal Model.
        * ``exceptions``    — count of quarantined, un-absorbed anomalies.

        Returns ``None`` when the health module is unavailable.
        """
        if not _PIPELINE_AVAILABLE or HealthReport is None:
            return None
        rules = int(getattr(self.model, "rule_count", 0) or 0)
        exceptions = int(getattr(self.model, "exception_count", 0) or 0)
        return HealthReport(
            entropy=self._standing_prediction.entropy,
            surprise=max(0.0, recent_surprise),
            rules=rules,
            exceptions=exceptions,
            label=f"tick {self._tick}",
        )

    def pipeline_tick(self, experience: Experience) -> PipelineTick:
        """Run one pass of the Probationary Concept Pipeline for ``experience``.

        Order of operations:

        1. Score the just-lived observation against every active probationary
           concept and resolve any that have matured (CONFIRM / REJECT).
        2. Compute the Free-Energy vitals for display.
        3. If the engine has tipped into EXHAUSTION, ask the concept-birth
           arbiter to abstract the most fragmented context, opening a fresh
           probation (Stage 0) and emitting the candidate-hypothesis alert.
        """
        alerts: List[str] = []
        alerts.extend(self._score_probation(experience))

        health = self.vitals(experience.prediction_error)

        if (
            _PIPELINE_AVAILABLE
            and health is not None
            and Regime is not None
            and health.regime is Regime.EXHAUSTION
        ):
            alerts.extend(self._attempt_concept_birth())

        return PipelineTick(health=health, alerts=alerts)

    def _score_probation(self, experience: Experience) -> List[str]:
        """Update and resolve probationary concepts against one observation.

        Only *deviation* ticks (observations that are not the incumbent rule)
        count as trials — the rule holding is no test of an anomaly abstraction.
        A matured concept is CONFIRMED only if its coverage clears the bar *and*
        a fresh birth evaluation of the live world model still earns positive
        gain; otherwise it is REJECTED. Nothing is written to the substrate.
        """
        alerts: List[str] = []
        if not self._probation:
            return alerts

        context = experience.prediction.context
        observation = experience.observation

        for pc in self._probation:
            if not pc.is_active or pc.context != context:
                continue
            if observation == pc.rule_symbol:
                continue  # the rule held; not a probative deviation
            pc.trials += 1
            if observation in pc.members:
                pc.hits += 1

        for pc in self._probation:
            if not pc.is_active or pc.trials < PROBATION_MIN_TRIALS:
                continue
            live_gain = 0.0
            if _PIPELINE_AVAILABLE and evaluate_concept_birth is not None:
                view = self._model_view(pc.context)
                if view is not None:
                    decision = evaluate_concept_birth(view)
                    if decision.born:
                        live_gain = decision.bits_eliminated
            if pc.coverage >= PROBATION_CONFIRM_HIT_RATE and live_gain > 0.0:
                pc.verdict = "CONFIRMED"
                pc.realized_bits = live_gain
            else:
                pc.verdict = "REJECTED"
            alerts.append(_render_probation_verdict(pc))

        return alerts

    def _attempt_concept_birth(self) -> List[str]:
        """Try to birth one probationary concept from the most strained context.

        Walks the substrate's fragmented contexts worst-first, asking the MDL
        arbiter (``evaluate_concept_birth``) whether grouping that context's
        quarantine behind a single pointer reduces predictive entropy by more
        than the birth threshold (G > 0.5 bits). The first context that earns a
        birth — and is not already on probation — opens a Stage-0 probation and
        produces the candidate alert. At most one birth per exhaustion tick keeps
        the monitor legible.
        """
        alerts: List[str] = []
        if not _PIPELINE_AVAILABLE or evaluate_concept_birth is None:
            return alerts

        candidates = getattr(self.model, "fragmented_contexts", None)
        contexts = candidates() if callable(candidates) else []

        for ctx in contexts:
            # Skip a context that already has a live or vindicated hypothesis;
            # only contexts whose prior concept was REJECTED may be retried.
            if any(
                pc.context == ctx and pc.verdict in ("PROBATION", "CONFIRMED")
                for pc in self._probation
            ):
                continue
            view = self._model_view(ctx)
            if view is None:
                continue
            decision = evaluate_concept_birth(view)
            if not decision.born or decision.concept is None:
                continue

            self._concept_serial += 1
            pc = ProbationaryConcept(
                label=f"Concept_{self._concept_serial:02d}",
                context=tuple(ctx),
                members=frozenset(decision.concept.member_symbols),
                rule_symbol=view.rule_consequent,
                promised_bits=decision.bits_eliminated,
                born_tick=self._tick,
            )
            self._probation.append(pc)
            alerts.append(_render_candidate_banner(pc, decision))
            break

        return alerts


# ---------------------------------------------------------------------------
# Presentation — rendering the cognitive state for a human monitor
# ---------------------------------------------------------------------------


def _bar(value: float, width: int = 20) -> str:
    """A simple unicode meter for a value in [0, 1]."""
    value = max(0.0, min(1.0, value))
    filled = int(round(value * width))
    return "#" * filled + "-" * (width - filled)


def render_prediction(
    prediction: Prediction,
    probation: Sequence["ProbationaryConcept"] = (),
) -> str:
    """Human-readable view of the engine's standing expectation."""
    ctx = " ".join(prediction.context) if prediction.context else "(empty)"
    top = prediction.top(4)
    forecast = ", ".join(f"{s}={p:.2f}" for s, p in top)
    base = (
        f"  context : [{ctx}]\n"
        f"  expects : {prediction.predicted_symbol}  "
        f"(p={prediction.predicted_probability:.2f}, "
        f"H={prediction.entropy:.2f} bits)\n"
        f"  because : {prediction.rationale}\n"
        f"  forecast: {forecast}"
    )
    # Stage-0 overlay: any probationary concept covering this context is acting
    # as a TEMPORARY rule, grouping its quarantined exceptions behind one pointer.
    overlay = [
        f"  probation: {pc.label} overlays {{{', '.join(sorted(pc.members))}}} "
        f"as one temporary rule (promised {pc.promised_bits:.2f} bits, "
        f"coverage {pc.coverage:.2f} over {pc.trials} deviations)"
        for pc in probation
    ]
    if overlay:
        base = base + "\n" + "\n".join(overlay)
    return base


def render_experience(
    exp: Experience,
    health: Optional["HealthReport"] = None,
    probation: Sequence["ProbationaryConcept"] = (),
) -> str:
    """Human-readable view of a single lived tick."""
    verdict = "EXPECTED" if exp.expectation_met else ("SURPRISE" if exp.was_surprising else "shift")
    concepts = ("  " + " ".join(exp.latent_concepts)) if exp.latent_concepts else ""

    lines = [
        f"  [{verdict}] expected '{exp.prediction.predicted_symbol}' "
        f"-> observed '{exp.observation}'",
        f"    surprise (prediction_error): {exp.prediction_error:6.3f} bits",
        f"    attention_weight          : {exp.attention_weight:5.3f}  {_bar(exp.attention_weight)}",
    ]

    # C2/C6: the localized world model the engine now holds for this context.
    if exp.internal_model is not None:
        im = exp.internal_model
        lines.append("    [Current Internal Model]")
        lines.append(f"      Rule      : {im.rule_str()}")
        lines.append(f"      Stability : {im.stability_str()}  {_bar(im.stability)}")
        lines.append(f"      Evidence  : {im.evidence_str()}")
        lines.append(f"      Exceptions: {im.exceptions_str()}")

    # Probationary Concept Pipeline: the Free-Energy vitals rendered right next
    # to the Internal Model so the operator reads the system's Energy/Regime in
    # the same glance as its current theory of the world.
    if health is not None:
        lines.append("    [Cognitive Vitals]")
        lines.append(
            f"      Energy E  : {health.energy:7.2f}  "
            f"(H {health.entropy:.2f} | S {health.surprise:.2f} | "
            f"A {health.active:.2f})"
        )
        lines.append(
            f"      Regime    : {health.regime.glyph} {health.regime.value}  "
            f"[rules {health.rules}, exceptions {health.exceptions}]"
        )

    # Note any temporary probationary concept that just absorbed this deviation.
    for pc in probation:
        if (
            pc.context == exp.prediction.context
            and exp.observation in pc.members
            and exp.observation != pc.rule_symbol
        ):
            lines.append(
                f"    [probation] {pc.label} absorbed deviation "
                f"'{exp.observation}' (coverage {pc.coverage:.2f} "
                f"over {pc.trials} deviations)"
            )

    lines.append(f"    confidence_delta (belief shift): {exp.confidence_delta:6.3f} bits")
    lines.append(f"    latent_concepts           :{concepts or '  (none)'}")

    # C3: surprise spiked past threshold — surface the engine's causal question.
    if exp.causal_hypothesis is not None:
        lines.append(f"    [!] causal_hypothesis     : {exp.causal_hypothesis}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Milestone C7 — The Sensorium Monitor: fusing world, predictor & discovery
# ---------------------------------------------------------------------------
#
# From C7 onward the cognitive monitor no longer ingests hand-typed symbols.
# It is wired directly to a continuous, noisy *world*. Every tick:
#
#   1. environment.Environment advances its hidden physical state.
#   2. environment.SensorArray.read() projects that state into a noisy
#      real-valued SensoryVector — the ONLY thing the brain may consume.
#   3. vector_prediction_core.VectorPredictionCore.ingest() clusters the
#      vector, forecasts the next one via its Markov chain, and measures the
#      Euclidean prediction error (surprise).
#   4. A Free-Energy style vitals model tracks surprise breaches and the
#      pile-up of quarantined anomalies. When surprise is *repeatedly*
#      breached AND the quarantine swells, the engine tips into EXHAUSTION.
#   5. Under EXHAUSTION the quarantined anomaly vectors are handed to
#      latent_cause_engine.LatentCauseEngine.discover(). If it mines an
#      invariant whose Score clears the promotion threshold, a new
#      Latent_Cause is announced — the mind minting its own word for a
#      regime nobody ever labelled for it.
#
# The hidden regime name (Environment.ground_truth) is *never* fed to any
# cognitive component. It is surfaced only as a dim, observer-only annotation
# so a human can verify a discovered Latent_Cause aligns with real generative
# structure — exactly the offline scoring role environment.py reserves for it.

import sys

try:  # The C7 sensorium trio. Imported defensively so the C1-C6 library above
    # still imports even when the sensorium modules are absent.
    from framework.core.environment import Environment, SensorArray
    from framework.core.latent_cause_engine import LatentCause, LatentCauseEngine
    from backend.cognition.vector_prediction_core import VectorPredictionCore

    _SENSORIUM_AVAILABLE = True
except Exception:  # noqa: BLE001 - any import failure degrades gracefully
    Environment = SensorArray = None  # type: ignore[assignment,misc]
    LatentCause = LatentCauseEngine = None  # type: ignore[assignment,misc]
    VectorPredictionCore = None  # type: ignore[assignment]
    _SENSORIUM_AVAILABLE = False


# --- C7 vitals tuning -------------------------------------------------------

#: Cluster-join radius in sensor space. Comfortably larger than the within-
#: regime sensor noise (~0.1) yet far below the inter-regime separation (~0.5+),
#: so each genuine regime condenses into one stable cluster.
SENSORIUM_PROXIMITY: float = 0.25

#: Static Euclidean surprise bar. A forecast error above this fires a
#: [SURPRISE] event — reliably tripped whenever the world switches regime.
SENSORIUM_SURPRISE_THRESHOLD: float = 0.30

#: Deliberately *fewer* clusters than there are latent regimes: a bounded
#: working memory. Once the budget is spent on the commonest regimes, a rarer
#: one can no longer earn a cluster and is forced into the quarantine — the
#: structural pressure that ultimately drives EXHAUSTION and concept discovery.
SENSORIUM_MAX_CLUSTERS: int = 3

#: Rolling window over which surprise breaches are counted.
BREACH_WINDOW: int = 12
#: Breaches-within-window that qualifies as "repeatedly breached".
BREACH_LIMIT: int = 4
#: New quarantined anomalies required to (re)attempt a discovery — throttles
#: mining so the monitor does not spam the same exhaustion every tick.
QUARANTINE_GROWTH: int = 5
#: Ring-buffer cap on the "normal" vectors retained as a contrastive baseline.
BASELINE_CAP: int = 240

# Free-Energy coupling coefficients imported from framework.core.cognitive_health (→ validation.metrics)
# E = λ·H + μ·S + ν·A. Single source of truth — do not redefine.


def _occupancy_entropy(counts: Sequence[float]) -> float:
    """Shannon entropy (bits) of the cluster-occupancy distribution.

    A world that keeps visiting one cluster is predictable (low H); a world
    smeared evenly across many clusters is uncertain (high H). This is the C7
    analogue of the symbolic engine's predictive entropy.
    """
    total = float(sum(counts))
    if total <= 0.0:
        return 0.0
    h = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        h -= p * _safe_log2(p)
    return h


@dataclass
class SensoriumVitals:
    """The Free-Energy vitals computed for a single sensorium tick."""

    error: float  #: Euclidean prediction error (surprise) this tick.
    threshold: float  #: The surprise bar in force.
    breached: bool  #: Did this tick fire a [SURPRISE] event?
    breaches_in_window: int  #: Breaches across the last ``BREACH_WINDOW`` ticks.
    entropy: float  #: H — uncertainty over cluster occupancy.
    energy: float  #: E = lam*H + mu*S + nu*A — the headline budget.
    clusters: int  #: Distinct regimes the predictor has named.
    quarantine: int  #: Total vectors the predictor refused to cluster.
    pending: int  #: Un-mined anomalies since the last discovery.
    regime: str  #: OPTIMAL | LEARNING | EXHAUSTION.

    @property
    def glyph(self) -> str:
        return {"OPTIMAL": "[~]", "LEARNING": "[^]", "EXHAUSTION": "[!]"}.get(self.regime, "[?]")


class SensoriumMonitor:
    """Fuses the C7 trio into one continuous predict / surprise / discover loop.

    Owns the world (:class:`Environment` + :class:`SensorArray`), the predictor
    (:class:`VectorPredictionCore`) and the discovery layer
    (:class:`LatentCauseEngine`). Each :meth:`tick` pulls one noisy vector,
    ingests it, scores the vitals, and — under cognitive exhaustion — mines the
    quarantine for a latent cause.
    """

    def __init__(
        self,
        *,
        seed: Optional[int] = 0,
        proximity: float = SENSORIUM_PROXIMITY,
        surprise_threshold: float = SENSORIUM_SURPRISE_THRESHOLD,
        max_clusters: int = SENSORIUM_MAX_CLUSTERS,
    ) -> None:
        if not _SENSORIUM_AVAILABLE:
            raise RuntimeError(
                "C7 sensorium modules unavailable (environment / "
                "vector_prediction_core / latent_cause_engine)."
            )
        self.env = Environment(seed=seed)
        self.sensors = SensorArray(noise_sigma=0.05, seed=None if seed is None else seed + 1)
        self.core = VectorPredictionCore(
            proximity_threshold=proximity,
            surprise_threshold=surprise_threshold,
            auto_seed=True,
            max_clusters=max_clusters,
        )
        self.latent_engine = LatentCauseEngine()

        self._tick: int = 0
        self._breaches: Deque[bool] = deque(maxlen=BREACH_WINDOW)
        #: The quarantine: vectors the predictor refused to cluster (cid == -1).
        self._quarantine: List[List[float]] = []
        #: Observer-only hidden labels, parallel to ``_quarantine``. NEVER read
        #: by any cognitive component — only by the human scoring discoveries.
        self._quarantine_truth: List[str] = []
        #: A contrastive cloud of "normal" vectors for the discovery engine.
        self._baseline: Deque[List[float]] = deque(maxlen=BASELINE_CAP)
        self._last_mined: int = 0
        self.causes: List["LatentCause"] = []
        #: (sensor_index, op) signatures already announced, so threshold drift
        #: across re-mines cannot spam the monitor with near-duplicate causes.
        self._announced_signatures: set = set()

    # --- the loop -----------------------------------------------------------

    def tick(
        self,
        observation: Optional[Sequence[float]] = None,
        interactive: bool = False,
    ) -> Dict[str, object]:
        """Advance the world one step and process the resulting sensor vector.

        Two input modes, one identical return contract:

        * ``interactive=True`` — block on ``input()`` for a hand-typed vector
          (the original DEBUG behaviour), falling back to a fresh sensor read on
          empty input.
        * ``interactive=False`` (default, autonomous) — never blocks. If
          ``observation`` is provided it is used verbatim as the sensory input;
          otherwise a vector is read from the sensors. This is the path the
          validation ``runner.py`` drives via ``tick(observation=vec,
          interactive=False)``.
        """
        self._tick += 1
        clusters_before = self.core.cluster_engine.cluster_count

        # 1-2. World advances; the brain receives only the noisy projection.
        self.env.step()
        if interactive:
            user_input = input("\n[DEBUG] Enter sensory vector (e.g., 0.1 0.9 0.2 0.1): ")
            if user_input.strip():
                vector = [float(x) for x in user_input.split()]
            else:
                vector = list(self.sensors.read(self.env))  # Fallback to normal if you press Enter
        elif observation is not None:
            # Autonomous mode: caller supplies the sensory input directly.
            vector = [float(x) for x in observation]
        else:
            # Autonomous mode with no injected observation: read the world.
            vector = list(self.sensors.read(self.env))

        # 3. Predict / cluster / measure surprise.
        result = self.core.ingest(vector)
        error = float(result["error"])
        threshold = self.core.surprise_tracker.threshold
        breached = result["surprise"] is not None
        self._breaches.append(breached)

        # Route the vector: rejected -> quarantine; clean & unsurprising ->
        # baseline (the contrastive "normalcy" the discovery engine needs).
        if result["is_anomaly"]:
            self._quarantine.append(vector)
            self._quarantine_truth.append(self.env.ground_truth())  # observer-only
        elif not breached:
            self._baseline.append(vector)

        clusters_after = self.core.cluster_engine.cluster_count
        new_cluster = clusters_after > clusters_before and result["cluster_id"] >= 0

        # 4. Vitals + regime.
        vitals = self._vitals(error, threshold)

        # 5. Under exhaustion, mine the quarantine for a latent cause.
        discovery: Optional["LatentCause"] = None
        if vitals.regime == "EXHAUSTION":
            discovery = self._mine()

        return {
            "tick": self._tick,
            "vector": vector,
            "result": result,
            "new_cluster": new_cluster,
            "vitals": vitals,
            "discovery": discovery,
            "truth": self.env.ground_truth(),  # observer-only annotation
        }

    # --- vitals -------------------------------------------------------------

    def _vitals(self, error: float, threshold: float) -> SensoriumVitals:
        engine = self.core.cluster_engine
        counts = [c.count for c in engine.clusters]
        H = _occupancy_entropy(counts)
        clusters = engine.cluster_count
        pending = max(0, len(self._quarantine) - self._last_mined)
        # Active load A: clean rules are cheap; un-absorbed anomalies are
        # penalised super-linearly, exactly as the symbolic health monitor does.
        active = float(clusters) + float(pending) ** 1.5
        energy = LAMBDA * H + MU * error + NU * active
        breaches = sum(1 for b in self._breaches if b)
        regime = self._classify(breaches, pending, H)
        return SensoriumVitals(
            error=error,
            threshold=threshold,
            breached=error > threshold,
            breaches_in_window=breaches,
            entropy=H,
            energy=energy,
            clusters=clusters,
            quarantine=len(self._quarantine),
            pending=pending,
            regime=regime,
        )

    @staticmethod
    def _classify(breaches: int, pending: int, entropy: float) -> str:
        """Partition the state into the three cognitive regimes.

        EXHAUSTION fires only when BOTH the task's conditions hold: surprise has
        been *repeatedly* breached AND anomalies have *piled up* in quarantine.
        """
        if breaches >= BREACH_LIMIT and pending >= QUARANTINE_GROWTH:
            return "EXHAUSTION"
        if breaches >= 1 or pending >= 1 or entropy >= 1.5:
            return "LEARNING"
        return "OPTIMAL"

    # --- discovery ----------------------------------------------------------

    def _mine(self) -> Optional["LatentCause"]:
        """Hand the quarantine + baseline to the latent-cause engine.

        Records the quarantine size so the same exhaustion is not re-mined every
        tick, and discharges the breach window. Returns a promoted
        :class:`LatentCause` only when one clears the engine's Score threshold.
        """
        cause = self.latent_engine.discover(self._quarantine, list(self._baseline))
        self._last_mined = len(self._quarantine)
        self._breaches.clear()
        if cause is None:
            return None
        # Collapse threshold drift: announce one cause per structural signature.
        signature = frozenset((p.index, p.op) for p in cause.variable.predicates)
        if signature in self._announced_signatures:
            return None
        self._announced_signatures.add(signature)
        self.causes.append(cause)

        # ── Closed Feedback Loop (C7) ─────────────────────────────────
        # The cause is no longer a dead end. Wire it straight back into the
        # prediction engine: re-weight the K-Means distance metric toward
        # the invariant dimension(s) and freeze the quarantine so future
        # vectors matching the cause's bounds are absorbed as a dedicated
        # cluster instead of re-quarantined. Discovery now *improves
        # prediction* — the loop is closed.
        try:
            self.core.apply_attention(cause)
        except Exception:  # noqa: BLE001 - feedback must never break the tick loop
            pass

        return cause

    def alignment(self, cause: "LatentCause") -> Tuple[Optional[str], float]:
        """Observer-only: which hidden regime do the cause's matches belong to?

        Pure instrumentation for the human — proves a brain-authored invariant
        tracks a real generative regime. It never influences cognition.
        """
        labels = [
            truth
            for vec, truth in zip(self._quarantine, self._quarantine_truth)
            if cause.matches(vec)
        ]
        if not labels:
            return None, 0.0
        name, n = Counter(labels).most_common(1)[0]
        return name, n / len(labels)


# ---------------------------------------------------------------------------
# Presentation — rendering the sensorium for a human monitor
# ---------------------------------------------------------------------------


def _fmt_vector(vector: Sequence[float]) -> str:
    """Render a sensory vector as ``[0.18, 0.21, 0.90, 0.43]``."""
    return "[" + ", ".join(f"{x:0.2f}" for x in vector) + "]"


def render_tick(record: Mapping[str, object]) -> str:
    """Two clean lines per tick: the raw vector + cluster, then the vitals."""
    vitals: SensoriumVitals = record["vitals"]  # type: ignore[assignment]
    result: Mapping[str, object] = record["result"]  # type: ignore[assignment]
    cid = int(result["cluster_id"])  # type: ignore[arg-type]

    if cid >= 0:
        cluster_s = f"cluster {cid:>2}" + (" (new)" if record["new_cluster"] else "")
    else:
        cluster_s = "cluster -- (quarantined)"

    if result["surprise"] is not None:
        tag = " [SURPRISE]"
    elif result["is_anomaly"]:
        tag = " [quarantine]"
    else:
        tag = ""

    line1 = (
        f"tick {int(record['tick']):>4} | {_fmt_vector(record['vector']):<30} | "  # type: ignore[arg-type]
        f"{cluster_s:<24} | err {vitals.error:0.3f} vs thr {vitals.threshold:0.3f}{tag}"
    )
    line2 = (
        f"          vitals: E={vitals.energy:6.2f}  {vitals.glyph} "
        f"{vitals.regime:<10} | clusters {vitals.clusters}  "
        f"quarantine {vitals.quarantine} (pending {vitals.pending})  "
        f"breaches {vitals.breaches_in_window}/{BREACH_WINDOW}  "
        f"[obs: {record['truth']}]"
    )
    return line1 + "\n" + line2


def render_latent_cause_banner(
    cause: "LatentCause",
    threshold: float,
    align_name: Optional[str] = None,
    align_frac: float = 0.0,
) -> str:
    """The massive alert announcing a newly discovered Latent_Cause."""
    width = 74
    bar = "=" * width
    sb = cause.score
    bound_lines = [f"      - {str(p)}" for p in cause.variable.predicates]

    lines = [
        "",
        bar,
        "  ***  NEW LATENT_CAUSE DISCOVERED  ***",
        bar,
        f"  id            : {cause.cause_id}",
        "  trigger       : COGNITIVE EXHAUSTION -- surprise repeatedly breached",
        "                  while quarantined anomaly vectors piled up unexplained.",
        "  invariant     : a mathematically valid sub-space of raw sensor-space",
        "                  the predictor could never name on its own:",
        f"                  [ {cause.variable.describe()} ]",
        "  physical bounds:",
        *bound_lines,
        "  predictive gain:",
        f"      Score          {sb.total:0.3f}   (> promotion threshold {threshold:0.2f})",
        f"      PredictionGain {sb.prediction_gain:0.3f}   "
        f"CompressionGain {sb.compression_gain:0.3f}   Stability {sb.stability:0.3f}",
        f"  evidence      : explains {cause.support} quarantined vectors; "
        f"{cause.false_positives} false-positive(s) on the normal baseline",
    ]
    if align_name is not None:
        lines.append(
            f"  [observer]    : aligns with hidden regime '{align_name}' in "
            f"{align_frac * 100:0.0f}% of matched anomalies (never seen by the brain)"
        )
    lines += [
        "  meaning       : the mind has minted its own word for a regime no human",
        "                  ever labelled -- derived purely from noisy measurement.",
        bar,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# The autonomous cognitive monitor (REPL)
# ---------------------------------------------------------------------------

_C7_BANNER = """\
============================================================
 VELYNX // C7 Sensorium — Predict / Surprise / Discover
============================================================
This monitor is wired to a world, not a keyboard. Each tick a
noisy sensor vector is pulled from the environment and fed to the
Vector Prediction Core. Watch:

  * the raw vector arriving and the cluster it is assigned to,
  * the Euclidean prediction_error (surprise) vs the threshold,
  * the [Cognitive Vitals]: Free-Energy (Energy E) and Regime
    (Optimal / Learning / Exhaustion),
  * anomalies the predictor cannot cluster piling into quarantine.

When surprise is repeatedly breached AND the quarantine swells,
the engine tips into EXHAUSTION and hands the quarantined vectors
to the Latent-Cause Engine. If a mathematically valid invariant
clears the Score threshold, a [!] NEW LATENT_CAUSE is announced --
the mind minting its own word for a regime nobody labelled.

The hidden regime tag shown as [obs: ...] is observer-only: it is
NEVER fed to the brain, only printed so you can score discoveries.

  (Ctrl+C to stop early.)
============================================================
"""


async def run_monitor(
    steps: int = 200,
    *,
    delay: float = 0.05,
    seed: Optional[int] = 0,
    monitor: Optional["SensoriumMonitor"] = None,
) -> None:
    """Run the autonomous sensorium monitor for ``steps`` ticks (or until Ctrl+C).

    The loop pulls one noisy :class:`SensorArray` vector per tick — it never
    reads typed input — ingests it into the predictive core, prints the tick's
    vector / cluster / error / vitals, and surfaces any latent cause discovered
    under exhaustion.
    """
    if not _SENSORIUM_AVAILABLE:
        print(
            "[monitor] C7 sensorium modules unavailable (environment / "
            "vector_prediction_core / latent_cause_engine). Cannot start."
        )
        return

    mon = monitor or SensoriumMonitor(seed=seed)
    print(_C7_BANNER)

    try:
        for _ in range(steps):
            record = mon.tick()
            print(render_tick(record))
            cause = record["discovery"]
            if cause is not None:
                name, frac = mon.alignment(cause)  # type: ignore[arg-type]
                print(
                    render_latent_cause_banner(
                        cause, mon.latent_engine.threshold, name, frac  # type: ignore[arg-type]
                    )
                )
            if delay:
                await asyncio.sleep(delay)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[monitor] interrupted -- shutting down.")

    engine = mon.core.cluster_engine
    print("\n" + "-" * 74)
    print(
        f"[monitor] {mon._tick} ticks processed | clusters {engine.cluster_count} | "
        f"quarantine {len(mon._quarantine)} | latent causes discovered "
        f"{len(mon.causes)}"
    )
    for c in mon.causes:
        print(f"   * {c.cause_id}: [{c.variable.describe()}]  score {c.score.total:0.3f}")
    print("[monitor] Goodbye.")


def main() -> None:
    """Console entrypoint. Optional argv[1] sets the tick budget."""
    # Legacy Windows consoles default to cp1252; make stdout tolerant so the
    # box-drawing and arrows in the monitor can never crash rendering.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

    steps = 200
    if len(sys.argv) > 1:
        try:
            steps = int(sys.argv[1])
        except ValueError:
            pass

    try:
        asyncio.run(run_monitor(steps=steps))
    except KeyboardInterrupt:  # pragma: no cover - interactive
        pass


if __name__ == "__main__":
    main()
