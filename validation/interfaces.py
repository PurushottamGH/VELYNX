"""
validation/interfaces.py
========================

Interface-First contracts for the VELYNX ``validation`` subsystem.

This module defines the three abstract base classes that every component of
the validation harness must implement. Nothing in the harness is permitted to
talk to a concrete dataset, metric or regression gate directly -- it only ever
talks to these interfaces. That indirection is the whole point: it guarantees
that any future cognitive-research module plugs into the same, unchanging
contract, so experiments stay comparable across phases.

The three roles
---------------
``Dataset``
    A reproducible source of world-ticks. Mirrors the ``Environment`` /
    ``SensorArray`` split in ``environment.py``: the only thing the mind is
    ever handed is a noisy real-valued sensory ``Vector``. A ``Dataset`` must
    be resettable so an experiment can be replayed deterministically.

``Metric``
    A scoring function over a run's ``logs``. Returns a single scalar
    ``score`` (lower-is-better or higher-is-better is defined per concrete
    metric and documented there). This is the home the existing
    ``cognitive_health.py`` Free-Energy / Cognitive Energy logic migrates into.

``Regression``
    A gate that compares a candidate run's metrics against a baseline and
    decides whether the candidate is a genuine improvement. This is the
    mechanism that enforces the project's "Freeze" rule: no new cognitive
    module ships unless a ``Regression`` confirms it improves the relevant
    metric (e.g. the Cognitive Progress Index).

Design notes
------------
* Pure standard library (``abc`` + ``typing``). No third-party dependencies,
  consistent with ``environment.py`` and ``cognitive_health.py``.
* ``Vector`` is aliased to match the ``SensoryVector`` used elsewhere in the
  codebase: an immutable tuple of floats.
* Concrete subclasses that fail to implement an abstract method cannot be
  instantiated -- ``abc`` raises ``TypeError`` at construction time, which is
  exactly the strict contract enforcement we want.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

# A single instantaneous sensory reading. Kept structurally identical to
# ``environment.SensoryVector`` so datasets and the cognitive core speak the
# same language without a conversion layer.
Vector = Tuple[float, ...]


class Dataset(ABC):
    """A reproducible, tick-by-tick source of sensory vectors.

    A ``Dataset`` is the *world* side of the world/mind separation. It owns
    whatever hidden state drives its dynamics and exposes exactly two
    operations to the harness: rewind to a known starting point, and advance
    one tick to emit the next observation.

    Contract:
        * :meth:`reset` must return the dataset to a well-defined initial
          state such that a subsequent sequence of :meth:`get_next_tick`
          calls is reproducible (given the same seed / configuration).
        * :meth:`get_next_tick` must return a :data:`Vector` -- the only
          information the cognitive core is permitted to observe. Ground-truth
          labels, if any, must be exposed through a separate channel, never
          through this method.
    """

    @abstractmethod
    def reset(self) -> None:
        """Rewind the dataset to its initial, reproducible state.

        Implementations should re-seed any internal RNG and restore hidden
        state so that the tick stream that follows is deterministic with
        respect to the dataset's configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def get_next_tick(self) -> Vector:
        """Advance the world by one step and emit the next sensory vector.

        Returns:
            Vector: the next noisy, real-valued observation. This is the sole
            channel the mind may read from.
        """
        raise NotImplementedError


class Metric(ABC):
    """A scoring function over the logs produced by a validation run.

    A ``Metric`` reduces an entire run -- the sequence of observations,
    predictions, internal-state snapshots, etc. captured in ``logs`` -- down
    to a mapping of named, comparable scalars.

    Contract:
        * :meth:`calculate` must be a pure function of ``logs``: same logs in,
          same scores out, with no hidden side effects.
        * Each concrete metric must document its directionality
          (higher-is-better vs lower-is-better) and its units per key, since
          the :class:`Regression` gate relies on that convention.
    """

    @abstractmethod
    def calculate(self, logs: Any) -> Dict[str, float]:
        """Reduce a run's logs to a mapping of named scalar scores.

        Args:
            logs: The recorded artifacts of a validation run. The concrete
                shape (e.g. a sequence of records, a structured report object)
                is defined by the harness and consumed by the metric.

        Returns:
            Dict[str, float]: metric-name -> score for this run.
        """
        raise NotImplementedError


class Regression(ABC):
    """A gate deciding whether a candidate run improves on a baseline.

    A ``Regression`` is the enforcement point for the project's "Freeze" rule.
    Given the metric scores of a current (candidate) run and a baseline run, it
    answers a single yes/no question: is the candidate a genuine improvement?

    Contract:
        * :meth:`is_improvement` must return ``True`` only when ``current``
          represents a real, intended improvement over ``baseline`` according
          to the metric semantics the implementation encodes (including any
          tolerance / noise margin).
        * The method must be side-effect free; it observes scores and returns
          a verdict.
    """

    @abstractmethod
    def is_improvement(
        self,
        current_metrics: Any,
        baseline_metrics: Any,
    ) -> bool:
        """Decide whether ``current_metrics`` improves on ``baseline_metrics``.

        Args:
            current_metrics: The metric score(s) for the candidate run. May be
                a single score or a mapping of metric-name -> score, as defined
                by the concrete gate.
            baseline_metrics: The metric score(s) for the baseline run, in the
                same shape as ``current_metrics``.

        Returns:
            bool: ``True`` if the candidate is an improvement, else ``False``.
        """
        raise NotImplementedError


__all__ = ["Dataset", "Metric", "Regression", "Vector"]
