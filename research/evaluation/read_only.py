"""
research/evaluation/read_only.py
================================

Read-only, non-mutating evaluation of a trained monitor against an ordered
probe stream.

The central safety property (verified by ``test_read_only_nonmutation.py``)
is that scoring a probe stream **must not perturb the live model by a single
bit**. We achieve this by ``copy.deepcopy``-ing the monitor and feeding the
probe vectors through the *clone*; the live monitor is only ever read from,
never ticked.

Why a deepcopy (and not a fresh monitor)?
-----------------------------------------
Held-out predictive RMSE measures *the trained model's* generalization. The
clone must therefore carry the full consolidated state — clusters, transition
matrix, surprise thresholds, attention wiring — exactly as training left it.
A deepcopy is the only stdlib-only way to obtain an independent, identical
copy of that state. ``VectorMonitor`` and its wrapped ``VectorPredictionCore``
are plain in-memory object graphs (lists/dicts/dataclasses, no open handles),
so they deepcopy cleanly.

Standard library only.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from validation.interfaces import Vector


@dataclass(frozen=True)
class ProbeTrace:
    """The immutable record of one read-only probe-stream evaluation.

    Attributes
    ----------
    errors :
        The ordered per-tick prediction errors (Euclidean distance between the
        clone's prediction and the observed probe vector). Ticks that yield no
        numeric error are omitted, so ``len(errors)`` may be < the number of
        probe vectors.
    num_vectors :
        The number of probe vectors actually presented to the clone.
    seed :
        The seed of the held-out stream, when known (metadata only).
    """

    errors: tuple[float, ...]
    num_vectors: int
    seed: Optional[int] = None

    @property
    def num_scored(self) -> int:
        """How many ticks contributed a numeric prediction error."""
        return len(self.errors)

    @property
    def rmse(self) -> float:
        """Held-out predictive RMSE: root-mean-square of the per-tick errors.

        Returns ``0.0`` for an empty trace (no scored ticks), mirroring the
        in-sample ``prediction_rmse`` convention in
        :meth:`research.runner.ResearchRunner._measure`.
        """
        if not self.errors:
            return 0.0
        return (sum(e * e for e in self.errors) / len(self.errors)) ** 0.5

    @property
    def mean_error(self) -> float:
        """Mean per-tick prediction error (``0.0`` for an empty trace)."""
        if not self.errors:
            return 0.0
        return sum(self.errors) / len(self.errors)


class ReadOnlyEvaluator:
    """Score a probe stream against a deepcopied clone of a live monitor.

    The evaluator holds a *reference* to the live monitor but never ticks it.
    Each call to :meth:`evaluate` takes a fresh, independent ``deepcopy`` and
    rehearses the probe stream on that clone, so repeated evaluations are
    mutually independent and the live model is untouched.

    Parameters
    ----------
    monitor :
        A trained monitor exposing ``tick(vector) -> dict`` whose returned
        mapping carries a numeric ``"surprise"`` (the per-tick prediction
        error), matching the :class:`validation.monitor.VectorMonitor`
        contract.
    """

    def __init__(self, monitor: Any) -> None:
        self._monitor = monitor

    def _clone(self) -> Any:
        """Return an isolated deepcopy of the live monitor.

        Raises
        ------
        RuntimeError
            If the monitor's object graph cannot be deepcopied. This converts
            an opaque low-level failure into an actionable message, since a
            non-copyable monitor makes safe read-only evaluation impossible.
        """
        try:
            return copy.deepcopy(self._monitor)
        except Exception as exc:  # noqa: BLE001 - re-raised with context
            raise RuntimeError(
                "ReadOnlyEvaluator could not deepcopy the monitor; read-only "
                "held-out evaluation requires an isolatable model. Original "
                f"error: {exc!r}"
            ) from exc

    def evaluate(
        self,
        vectors: Sequence[Vector],
        *,
        seed: Optional[int] = None,
    ) -> ProbeTrace:
        """Rehearse ``vectors`` on a clone and return the per-tick error trace.

        The live monitor is never mutated: all ticks land on the deepcopied
        clone.

        Parameters
        ----------
        vectors :
            The ordered held-out probe stream.
        seed :
            Optional seed of the held-out stream, recorded on the trace.
        """
        clone = self._clone()
        errors: list[float] = []
        num_vectors = 0
        for vector in vectors:
            num_vectors += 1
            log = clone.tick([float(x) for x in vector])
            error = log.get("surprise")
            if error is not None:
                errors.append(float(error))
        return ProbeTrace(
            errors=tuple(errors), num_vectors=num_vectors, seed=seed
        )


__all__ = ["ProbeTrace", "ReadOnlyEvaluator"]
