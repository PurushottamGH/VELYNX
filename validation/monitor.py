"""
validation/monitor.py
======================

The bridge between the :class:`~validation.runner.BenchmarkRunner` (which speaks
*tick logs*) and the scoring/dashboard layer (which speaks *cognitive-state
snapshots* -- transitions, predicted centroid, observed vector, cluster count,
anomaly cloud).

``BenchmarkRunner`` drives a dataset against any object exposing
``tick(vector) -> dict``. The metric classes in :mod:`validation.metrics` and the
``HealthReport`` in :mod:`validation.report`, however, consume a single
*snapshot* mapping, not a per-tick log. ``VectorMonitor`` reconciles the two:

* :meth:`tick` adapts the runner's per-tick call onto
  :meth:`VectorPredictionCore.ingest`, returning the
  ``prediction`` / ``surprise`` / ``regime`` keys the runner records.
* :meth:`snapshot` reads the core's live internal state into the exact mapping
  the metrics and the vitals dashboard expect.
* :meth:`score` reduces that snapshot to a ``{metric_name: value}`` dict via any
  iterable of :class:`~validation.interfaces.Metric` objects.

All the bridging logic lives here so the orchestrator (``benchmark.py``) only
wires components together and never computes anything itself.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from validation.interfaces import Metric, Vector


def _build_core(**core_kwargs: Any) -> Any:
    """Construct a ``VectorPredictionCore`` (imported lazily, std-lib only).

    The core lives under ``backend.cognition`` and is pure standard library,
    so importing it is cheap and side-effect free. We import inside the
    function to keep import errors local and actionable rather than failing the
    whole ``validation`` package at import time.
    """
    from backend.cognition.vector_prediction_core import VectorPredictionCore

    return VectorPredictionCore(**core_kwargs)


class VectorMonitor:
    """Adapt a ``VectorPredictionCore`` to the runner + scoring contracts.

    Parameters
    ----------
    core : object or None
        A duck-typed prediction core exposing ``ingest(list) -> dict``,
        ``predictor.transition_matrix()``, ``cluster_engine.cluster_count`` and
        ``cluster_engine.anomaly_vectors`` (and optionally ``last_prediction``).
        When ``None`` a fresh :class:`VectorPredictionCore` is built from
        ``core_kwargs``.
    **core_kwargs :
        Forwarded to the core constructor (e.g. ``proximity_threshold``).
    """

    def __init__(self, core: Optional[Any] = None, **core_kwargs: Any) -> None:
        self._core = core if core is not None else _build_core(**core_kwargs)
        self._last_observed: Optional[List[float]] = None
        self._ticks: int = 0

    # -- runner contract ---------------------------------------------------

    def tick(self, vector: Vector) -> Dict[str, Any]:
        """Process one sensory vector and return the runner's log fields.

        Maps the rich diagnostic dict from :meth:`VectorPredictionCore.ingest`
        onto the ``prediction`` / ``surprise`` / ``regime`` keys the
        ``BenchmarkRunner`` records (extra keys are ignored by the runner but
        kept here for richer logs).
        """
        observation = [float(x) for x in vector]
        self._last_observed = observation
        self._ticks += 1

        result = self._core.ingest(observation)
        return {
            "prediction": result.get("predicted"),
            # ``ingest`` returns the numeric prediction error under "error";
            # its "surprise" key is an Optional[SurpriseEvent] object (not
            # JSON-serializable), so we log the scalar error as the surprise.
            "surprise": result.get("error"),
            # Per-tick regime tag: a coarse, cheap label for the runner's
            # ``regime_counts``. The dashboard's full Optimal/Learning/Exhaustion
            # classification is computed separately by HealthReport.
            "regime": "anomaly" if result.get("is_anomaly") else "stable",
            "cluster_id": result.get("cluster_id"),
        }

    # -- scoring / dashboard contract -------------------------------------

    def snapshot(self, label: str = "snapshot") -> Dict[str, Any]:
        """Read the core's live state into the metric/dashboard snapshot shape.

        Returns a mapping with exactly the keys consumed by
        :mod:`validation.metrics` and :class:`validation.report.HealthReport`:
        ``transitions``, ``predicted_centroid``, ``observed_vector``,
        ``cluster_count``, ``anomaly_vectors``, ``label``.
        """
        core = self._core
        observed = self._last_observed if self._last_observed is not None else [0.0]
        predicted = getattr(core, "last_prediction", None)
        if predicted is None:
            predicted = list(observed)

        return {
            "transitions": core.predictor.transition_matrix(),
            "predicted_centroid": list(predicted),
            "observed_vector": list(observed),
            "cluster_count": core.cluster_engine.cluster_count,
            "anomaly_vectors": [list(v) for v in core.cluster_engine.anomaly_vectors],
            "label": label,
        }

    def get_memory_summary(self) -> Dict[str, Any]:
        """Expose the core's cluster + anomaly-lifecycle vitals.

        Thin passthrough to ``VectorPredictionCore.get_memory_summary`` so the
        orchestrator can render the memory/anomaly dashboard without reaching
        into the wrapped core directly.
        """
        return self._core.get_memory_summary()

    @property
    def cluster_engine(self) -> Any:
        """Expose the core's live ``ClusterEngine`` for memory restructuring.

        Lets consumers (e.g. the C8.1 ``CandidateGenerator``) inspect cluster
        state without reaching into the wrapped core's private attribute.
        """
        return self._core.cluster_engine

    def score(
        self,
        metrics: Iterable[Metric],
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, float]:
        """Reduce the run to ``{metric_name: value}`` for the regression gate.

        Each metric is keyed by its class name (e.g. ``"CognitiveEnergyMetric"``)
        so the :class:`~validation.regression.RegressionGate` can compare runs
        metric-for-metric.
        """
        snap = snapshot if snapshot is not None else self.snapshot()
        return {type(m).__name__: float(m.calculate(snap)) for m in metrics}


__all__ = ["VectorMonitor"]
