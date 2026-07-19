"""
VELYNX — Milestone C7: The Sensorium (Physics & Sensor Layer)
=============================================================

The strict separation of *world* from *mind*.

Until C6 the cognitive core was fed hand-labelled discrete symbols — ``"day"``,
``"night"``, ``"storm"``. Those labels were a leak: a human had already done the
perceptual work of carving the world into named categories. The brain never had
to *discover* that "storm" was a thing; it was handed the concept pre-packaged.

C7 closes that leak. The world is now a continuous dynamical system with a
**hidden state** the mind can never observe directly. All the brain ever
receives is a vector of **noisy, real-valued sensor measurements** —

    [0.14, 0.93, 0.88, 0.41]

— and never the same numbers twice, because :func:`random.gauss` corrupts every
reading. There are no words anywhere in this file that the brain is allowed to
see. The regime names (``CALM``, ``STORM`` …) exist *only* as instrumentation
for us, the experimenters, to score whether the mind later re-derives them on
its own. They are returned exclusively through :meth:`Environment.ground_truth`,
which the cognitive core must never call.

Architecture
------------
``Environment``
    Owns the hidden physical state (atmosphere / light / moisture) and a latent
    *regime* that biases that state. The regime drifts via a Markov process; the
    continuous variables relax toward the regime's attractor with momentum, so
    the world has both abrupt structure (regime switches) and smooth dynamics.

``SensorArray``
    A fixed bank of imperfect transducers. Each sensor is a linear projection of
    the hidden state plus Gaussian noise, squashed into ``[0, 1]``. This is the
    *only* interface the brain is permitted to touch. Swap the brain's input
    from ``str`` to ``SensoryVector`` and the representation-learning problem
    becomes real: structure must be *inferred*, never *read off a label*.

This module is pure standard library and runnable directly::

    python environment.py
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

# A single instantaneous reading from the sensor bank. This — and only this —
# is what the cognitive core consumes from C7 onward.
SensoryVector = Tuple[float, ...]


# ---------------------------------------------------------------------------
# Hidden physical state
# ---------------------------------------------------------------------------
@dataclass
class HiddenState:
    """The world's true latent variables — *invisible* to any observer.

    All three live on ``[0, 1]``. The brain never sees these; it only ever sees
    noisy projections of them through the :class:`SensorArray`.
    """

    atmosphere: float = 0.5  # barometric "pressure" proxy
    light: float = 0.5       # ambient illumination
    moisture: float = 0.5    # humidity / water content

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.atmosphere, self.light, self.moisture)


# ---------------------------------------------------------------------------
# Latent regimes — the ground-truth "causes" the mind must rediscover
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Regime:
    """A latent attractor over the hidden state plus its self-persistence.

    ``name`` is *experimenter-only* metadata. It is never emitted on the sensor
    channel and exists purely so we can later measure whether a discovered
    ``Latent_Cause`` aligns with a real generative regime.
    """

    name: str
    target: Tuple[float, float, float]  # (atmosphere, light, moisture) attractor
    dwell: float                        # probability of staying next step, [0, 1]


# The default generative world. Each regime pins the hidden state toward a
# distinct corner of the cube, giving the sensor stream separable structure that
# a representation learner can — in principle — recover without any labels.
DEFAULT_REGIMES: Tuple[Regime, ...] = (
    #        name        atmosphere  light  moisture   dwell
    Regime("CALM_DAY",   (0.70,      0.90,  0.25),     0.90),
    Regime("CALM_NIGHT", (0.65,      0.10,  0.30),     0.90),
    Regime("STORM",      (0.15,      0.20,  0.92),     0.80),
    Regime("FOG",        (0.50,      0.45,  0.85),     0.75),
)


class Environment:
    """A continuous, stochastic world with a hidden state and latent regimes.

    The mind is forbidden from reading :attr:`_state` or :meth:`ground_truth`.
    Its sole legitimate interface is to hand this object to a
    :class:`SensorArray` and observe the resulting noisy vector.
    """

    def __init__(
        self,
        regimes: Sequence[Regime] = DEFAULT_REGIMES,
        *,
        relaxation: float = 0.25,
        drift_sigma: float = 0.03,
        seed: Optional[int] = None,
    ) -> None:
        if not regimes:
            raise ValueError("Environment requires at least one regime.")
        self._regimes: Tuple[Regime, ...] = tuple(regimes)
        #: How fast the hidden state relaxes toward the active regime's attractor
        #: each step (0 = frozen, 1 = teleport). Momentum < 1 gives smooth physics.
        self._relaxation = relaxation
        #: Std-dev of the random walk applied to hidden variables every step, so
        #: even *within* a regime the world is never perfectly stationary.
        self._drift_sigma = drift_sigma
        self._rng = random.Random(seed)

        self._regime: Regime = self._rng.choice(self._regimes)
        self._state = HiddenState(*self._regime.target)
        self._tick: int = 0

    # --- world dynamics -----------------------------------------------------
    def step(self) -> HiddenState:
        """Advance the world one tick and return the new (hidden) state.

        Two processes compose: a Markov regime transition (abrupt, structural)
        and a momentum relaxation + random walk of the continuous variables
        (smooth, noisy). Together they yield a stream that is neither i.i.d. nor
        deterministic — exactly the regime the mind must model.
        """
        self._maybe_switch_regime()

        tx, ty, tz = self._regime.target
        a, l, m = self._state.as_tuple()
        r = self._relaxation
        # Relax toward the attractor, then jitter with a bounded random walk.
        a = self._clamp(a + r * (tx - a) + self._rng.gauss(0.0, self._drift_sigma))
        l = self._clamp(l + r * (ty - l) + self._rng.gauss(0.0, self._drift_sigma))
        m = self._clamp(m + r * (tz - m) + self._rng.gauss(0.0, self._drift_sigma))
        self._state = HiddenState(a, l, m)

        self._tick += 1
        return self._state

    def _maybe_switch_regime(self) -> None:
        if self._rng.random() < self._regime.dwell:
            return  # regime persists
        # Transition to a *different* regime, uniformly among the alternatives.
        alternatives = [r for r in self._regimes if r.name != self._regime.name]
        if alternatives:
            self._regime = self._rng.choice(alternatives)

    @staticmethod
    def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return lo if x < lo else hi if x > hi else x

    # --- legitimate read for sensors ---------------------------------------
    @property
    def state(self) -> HiddenState:
        """The current hidden state. Intended for :class:`SensorArray` only."""
        return self._state

    # --- experimenter-only instrumentation ---------------------------------
    def ground_truth(self) -> str:
        """The true active regime name. **Never** call this from the brain.

        This exists solely so an external evaluator can score a discovered
        ``Latent_Cause`` against the world's real generative structure.
        """
        return self._regime.name


# ---------------------------------------------------------------------------
# Sensor bank — the brain's only window onto the world
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Sensor:
    """One noisy transducer: a biased linear projection of the hidden state."""

    weights: Tuple[float, float, float]  # over (atmosphere, light, moisture)
    bias: float

    def transduce(self, state: HiddenState, noise: float) -> float:
        a, l, m = state.as_tuple()
        wa, wl, wm = self.weights
        raw = self.bias + wa * a + wl * l + wm * m + noise
        return 0.0 if raw < 0.0 else 1.0 if raw > 1.0 else raw


class SensorArray:
    """Reads the environment and emits a noisy continuous :data:`SensoryVector`.

    Every reading is corrupted by :func:`random.gauss`, guaranteeing the brain
    never sees the exact same numbers twice even when the world is in an
    identical hidden state. Discovering that two *different* vectors share a
    latent cause is precisely the representation-learning problem of C7.
    """

    # A 4-sensor bank. The projections deliberately *entangle* the hidden
    # variables so no single sensor is a clean label for any one latent factor —
    # the mind has to disentangle them.
    _DEFAULT_SENSORS: Tuple[_Sensor, ...] = (
        _Sensor(weights=(0.10, 0.95, 0.05), bias=0.00),   # mostly light
        _Sensor(weights=(0.90, 0.05, 0.10), bias=0.00),   # mostly atmosphere
        _Sensor(weights=(0.05, 0.10, 0.95), bias=0.00),   # mostly moisture
        _Sensor(weights=(0.45, 0.50, 0.30), bias=-0.10),  # entangled mixture
    )

    def __init__(
        self,
        sensors: Sequence[_Sensor] = _DEFAULT_SENSORS,
        *,
        noise_sigma: float = 0.05,
        seed: Optional[int] = None,
    ) -> None:
        self._sensors: Tuple[_Sensor, ...] = tuple(sensors)
        self._noise_sigma = noise_sigma
        self._rng = random.Random(seed)

    @property
    def dimensions(self) -> int:
        return len(self._sensors)

    def read(self, env: Environment) -> SensoryVector:
        """Take one noisy snapshot of the environment's hidden state."""
        state = env.state
        return tuple(
            sensor.transduce(state, self._rng.gauss(0.0, self._noise_sigma))
            for sensor in self._sensors
        )


# ---------------------------------------------------------------------------
# Convenience: a labelled-for-us stream that the brain consumes label-free
# ---------------------------------------------------------------------------
def stream(
    steps: int,
    *,
    seed: Optional[int] = None,
    noise_sigma: float = 0.05,
) -> Iterator[Tuple[SensoryVector, str]]:
    """Yield ``(vector, hidden_regime)`` pairs.

    The cognitive core consumes only ``vector``; the ``hidden_regime`` tag rides
    alongside purely for offline scoring and **must be discarded** before the
    array reaches the brain.
    """
    env = Environment(seed=seed)
    sensors = SensorArray(noise_sigma=noise_sigma, seed=None if seed is None else seed + 1)
    for _ in range(steps):
        env.step()
        yield sensors.read(env), env.ground_truth()


# ---------------------------------------------------------------------------
# Standalone demo
# ---------------------------------------------------------------------------
def _demo() -> None:  # pragma: no cover - illustrative only
    print("VELYNX C7 — Sensorium stream (brain sees only the vector)\n")
    print(f"{'tick':>4}  {'sensory_vector':<34}  {'[hidden regime]'}")
    print("-" * 60)
    for tick, (vector, regime) in enumerate(stream(20, seed=7)):
        pretty = "[" + ", ".join(f"{v:0.2f}" for v in vector) + "]"
        print(f"{tick:>4}  {pretty:<34}  ({regime})")


if __name__ == "__main__":  # pragma: no cover
    _demo()
