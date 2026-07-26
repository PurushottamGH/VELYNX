"""
VELYNX — Milestone C7: The Latent-Cause Engine (Discovery Layer)
================================================================

Where the mind *invents its own words*.

The cognitive core (C1–C6) predicts the next sensory vector. When that
prediction fails repeatedly for the same kind of input, the anomalous vectors
are not absorbed — they are **quarantined**, exactly as C6 quarantines symbolic
anomalies as ``Exceptions``. A growing quarantine is a confession: *"there is
structure in the world that my current model cannot name."*

This module mines that quarantine. It scans the anomalous arrays for a
**LatentVariable** — a sub-space of sensor-space, expressed as an invariant
conjunction of axis-aligned constraints, e.g.::

    Sensor 2 > 0.80  AND  Sensor 3 < 0.20

A candidate is only worth keeping if it *earns its existence* against the
baseline (normal) stream. We score every candidate with three competing
pressures::

    Score = (alpha * PredictionGain)
          + (beta  * CompressionGain)
          + (gamma * Stability)

* **PredictionGain** — does firing on this sub-space explain the anomalies the
  old model could not? Operationally: coverage of the quarantine times
  distinctiveness from the baseline (it fires on anomalies, *not* on normalcy).
* **CompressionGain** — an MDL test. Is it cheaper to transmit the quarantine as
  "a rule + the free dimensions" than as raw floats? A latent cause that buys no
  bits is not a concept, it is overfitting.
* **Stability** — is the invariant *tight*? A cause whose constrained dimensions
  vary wildly across its members is a coincidence, not a regularity.

If ``Score > threshold`` the LatentVariable is **promoted** to a
``Latent_Cause`` — a first-class, brain-authored representation the predictor
may henceforth condition on. The mind has minted a new word for itself, derived
purely from continuous noisy measurement, with no human label anywhere in the
loop.

Pure standard library. Runnable directly::

    python latent_cause_engine.py
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

# Mirror the environment's type so the two modules speak the same language
# without importing each other (keeps the discovery layer dependency-free).
SensoryVector = Sequence[float]

_EPS = 1e-9


# ---------------------------------------------------------------------------
# The structural vocabulary of a latent variable
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Predicate:
    """A single axis-aligned constraint on one sensor dimension."""

    index: int
    op: str  # ">" or "<"
    threshold: float

    def satisfied_by(self, vector: SensoryVector) -> bool:
        value = vector[self.index]
        return value > self.threshold if self.op == ">" else value < self.threshold

    def __str__(self) -> str:
        return f"Sensor {self.index} {self.op} {self.threshold:0.2f}"


@dataclass(frozen=True)
class LatentVariable:
    """A candidate sub-space: a conjunction of predicates over sensor-space."""

    predicates: Tuple[Predicate, ...]

    @property
    def arity(self) -> int:
        """Number of constrained dimensions (the rule's description complexity)."""
        return len(self.predicates)

    def matches(self, vector: SensoryVector) -> bool:
        return all(p.satisfied_by(vector) for p in self.predicates)

    def describe(self) -> str:
        if not self.predicates:
            return "<universal>"
        return " AND ".join(str(p) for p in self.predicates)


@dataclass(frozen=True)
class ScoreBreakdown:
    """The three competing pressures and their weighted sum."""

    prediction_gain: float
    compression_gain: float
    stability: float
    total: float

    def __str__(self) -> str:
        return (
            f"score={self.total:0.3f} "
            f"(pred={self.prediction_gain:0.3f}, "
            f"comp={self.compression_gain:0.3f}, "
            f"stab={self.stability:0.3f})"
        )


@dataclass(frozen=True)
class LatentCause:
    """A promoted LatentVariable — a brain-authored representation."""

    cause_id: str
    variable: LatentVariable
    score: ScoreBreakdown
    support: int  # how many quarantined vectors it explains
    false_positives: int  # how many baseline vectors it wrongly fires on

    def matches(self, vector: SensoryVector) -> bool:
        return self.variable.matches(vector)

    def __str__(self) -> str:
        return (
            f"{self.cause_id}: [{self.variable.describe()}]  "
            f"{self.score}  support={self.support} fp={self.false_positives}"
        )


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------
class LatentCauseEngine:
    """Scans quarantined sensory vectors and discovers latent causes.

    The engine is *contrastive*: it always reasons about the quarantine relative
    to a baseline of normal readings, so a discovered invariant is forced to be
    something that distinguishes anomalies from business-as-usual rather than a
    property of the sensor stream in general.
    """

    def __init__(
        self,
        *,
        alpha: float = 0.50,  # weight on PredictionGain
        beta: float = 0.30,  # weight on CompressionGain
        gamma: float = 0.20,  # weight on Stability
        threshold: float = 0.50,  # promotion bar for Score
        bits_per_value: int = 8,  # MDL quantisation precision
        pin_std_max: float = 0.18,  # a dim is "pinned" only if this tight
        separation_min: float = 0.20,  # ...and this far from the baseline mean
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.threshold = threshold
        self.bits_per_value = bits_per_value
        self.pin_std_max = pin_std_max
        self.separation_min = separation_min

        self._promoted: List[LatentCause] = []
        self._serial: int = 0

    # --- public API ---------------------------------------------------------
    @property
    def latent_causes(self) -> Tuple[LatentCause, ...]:
        return tuple(self._promoted)

    def discover(
        self,
        quarantine: Sequence[SensoryVector],
        baseline: Sequence[SensoryVector] = (),
    ) -> Optional[LatentCause]:
        """Mine the quarantine for the single best latent cause.

        Returns the promoted :class:`LatentCause` if its score clears the
        threshold (and it is not a duplicate of an existing cause), else
        ``None``. Lower-level callers wanting the full ranking can use
        :meth:`rank_candidates`.
        """
        ranked = self.rank_candidates(quarantine, baseline)
        if not ranked:
            return None

        variable, breakdown = ranked[0]
        if breakdown.total <= self.threshold:
            return None
        if self._is_duplicate(variable):
            return None

        support = sum(1 for v in quarantine if variable.matches(v))
        fp = sum(1 for v in baseline if variable.matches(v))
        self._serial += 1
        cause = LatentCause(
            cause_id=f"Latent_Cause_{self._serial:02d}",
            variable=variable,
            score=breakdown,
            support=support,
            false_positives=fp,
        )
        self._promoted.append(cause)
        return cause

    def rank_candidates(
        self,
        quarantine: Sequence[SensoryVector],
        baseline: Sequence[SensoryVector] = (),
    ) -> List[Tuple[LatentVariable, ScoreBreakdown]]:
        """Generate and score every candidate, best score first."""
        if not quarantine:
            return []

        candidates = self._generate_candidates(quarantine, baseline)
        scored = [(var, self._score(var, quarantine, baseline)) for var in candidates]
        scored.sort(key=lambda pair: pair[1].total, reverse=True)
        return scored

    # --- candidate generation ----------------------------------------------
    def _generate_candidates(
        self,
        quarantine: Sequence[SensoryVector],
        baseline: Sequence[SensoryVector],
    ) -> List[LatentVariable]:
        """Propose latent variables from the *pinned* dimensions of the quarantine.

        A dimension is "pinned" when, across the quarantine, it is both tight
        (low variance) and separated from the baseline mean. Each pinned
        dimension becomes a directional predicate split at the midpoint between
        the quarantine and baseline means. We propose both the full conjunction
        of all pinned dimensions and each pinned dimension on its own, letting
        the scorer arbitrate between a precise-but-complex rule and a
        simple-but-leakier one.
        """
        dims = len(quarantine[0])
        predicates: List[Predicate] = []

        for d in range(dims):
            q_col = [float(v[d]) for v in quarantine]
            q_mean = statistics.fmean(q_col)
            q_std = statistics.pstdev(q_col) if len(q_col) > 1 else 0.0
            b_col = [float(v[d]) for v in baseline]
            b_mean = statistics.fmean(b_col) if b_col else 0.5

            tight = q_std <= self.pin_std_max
            separated = abs(q_mean - b_mean) >= self.separation_min
            if not (tight and separated):
                continue

            midpoint = (q_mean + b_mean) / 2.0
            op = ">" if q_mean > b_mean else "<"
            predicates.append(Predicate(index=d, op=op, threshold=round(midpoint, 2)))

        if not predicates:
            return []

        candidates: List[LatentVariable] = [LatentVariable(tuple(predicates))]
        if len(predicates) > 1:
            candidates.extend(LatentVariable((p,)) for p in predicates)
        return candidates

    # --- scoring ------------------------------------------------------------
    def _score(
        self,
        variable: LatentVariable,
        quarantine: Sequence[SensoryVector],
        baseline: Sequence[SensoryVector],
    ) -> ScoreBreakdown:
        pg = self._prediction_gain(variable, quarantine, baseline)
        cg = self._compression_gain(variable, quarantine)
        st = self._stability(variable, quarantine)
        total = self.alpha * pg + self.beta * cg + self.gamma * st
        return ScoreBreakdown(pg, cg, st, total)

    def _prediction_gain(
        self,
        variable: LatentVariable,
        quarantine: Sequence[SensoryVector],
        baseline: Sequence[SensoryVector],
    ) -> float:
        """Coverage of the anomalies x distinctiveness from normalcy, in [0, 1].

        A cause that fires on every quarantined vector but also on every normal
        vector explains nothing new; the ``(1 - false_positive_rate)`` factor
        punishes exactly that. Knowing the cause reduces future surprise only to
        the extent it carves out a region the old model called normal yet which
        in fact hosts the anomalies.
        """
        n_q = len(quarantine)
        coverage = sum(1 for v in quarantine if variable.matches(v)) / max(n_q, 1)
        if baseline:
            fp_rate = sum(1 for v in baseline if variable.matches(v)) / len(baseline)
        else:
            fp_rate = 0.0
        return coverage * (1.0 - fp_rate)

    def _compression_gain(
        self,
        variable: LatentVariable,
        quarantine: Sequence[SensoryVector],
    ) -> float:
        """MDL: fraction of bits saved by describing matches via the rule, [0, 1].

        Raw cost: every vector is ``D`` quantised floats. With the latent cause
        we transmit the rule once, then for each matched vector only the
        ``D - k`` *unconstrained* dimensions (the ``k`` constrained ones are
        implied by membership), plus one membership bit per vector. The cause is
        worth minting only if ``k * b`` saved per matched vector outweighs the
        one-off rule header and the per-vector membership overhead.
        """
        if not quarantine:
            return 0.0
        dims = len(quarantine[0])
        b = self.bits_per_value
        k = variable.arity
        n = len(quarantine)
        m = sum(1 for v in quarantine if variable.matches(v))

        cost_raw = n * dims * b
        rule_bits = k * (b + math.log2(max(dims, 2)))
        # savings = k*b reclaimed on each matched vector, minus rule + membership
        savings = m * k * b - rule_bits - n
        return max(0.0, savings) / max(cost_raw, _EPS)

    def _stability(
        self,
        variable: LatentVariable,
        quarantine: Sequence[SensoryVector],
    ) -> float:
        """Tightness of the constrained dimensions across matched members, [0, 1].

        For each constrained dimension we measure how concentrated the matched
        members are: zero spread -> 1.0, spread filling half the unit range -> 0.
        An invariant whose own constrained axes are noisy is not an invariant.
        """
        matched = [v for v in quarantine if variable.matches(v)]
        if not matched or variable.arity == 0:
            return 0.0

        ref_spread = 0.5  # half the [0, 1] sensor range
        tightnesses: List[float] = []
        for p in variable.predicates:
            col = [float(v[p.index]) for v in matched]
            spread = statistics.pstdev(col) if len(col) > 1 else 0.0
            tightnesses.append(max(0.0, 1.0 - spread / ref_spread))
        return statistics.fmean(tightnesses)

    # --- housekeeping -------------------------------------------------------
    def _is_duplicate(self, variable: LatentVariable) -> bool:
        existing = {c.variable.predicates for c in self._promoted}
        return variable.predicates in existing


# ---------------------------------------------------------------------------
# Standalone demo — full C7 transition, end to end
# ---------------------------------------------------------------------------
def _demo() -> None:  # pragma: no cover - illustrative only
    import random

    # We synthesise a baseline (normal) cloud and a quarantine cloud that lives
    # in a distinct sub-space — "high moisture, low light", i.e. the STORM
    # signature — without ever naming it for the engine.
    rng = random.Random(11)

    def cloud(center, n):
        return [
            tuple(min(1.0, max(0.0, c + rng.gauss(0.0, 0.05))) for c in center) for _ in range(n)
        ]

    baseline = cloud((0.85, 0.90, 0.25, 0.55), 60)  # calm/bright/dry
    quarantine = cloud((0.20, 0.18, 0.90, 0.42), 25)  # the un-named anomaly

    engine = LatentCauseEngine()

    print("VELYNX C7 — Latent-Cause discovery from quarantined vectors\n")
    print("Candidate ranking:")
    for var, score in engine.rank_candidates(quarantine, baseline):
        print(f"  [{var.describe():<45}] {score}")

    print("\nPromotion:")
    cause = engine.discover(quarantine, baseline)
    if cause is None:
        print("  no candidate cleared the threshold")
    else:
        print(f"  PROMOTED -> {cause}")
        print(
            "\n  The mind has minted a representation for an environmental"
            "\n  regime it was never told the name of."
        )


if __name__ == "__main__":  # pragma: no cover
    _demo()
