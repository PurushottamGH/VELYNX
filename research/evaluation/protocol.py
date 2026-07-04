"""
research/evaluation/protocol.py
===============================

The :class:`EvaluationProtocol` hook — the single object the
:class:`~research.runner.ResearchRunner` calls to turn a *trained* monitor into
a held-out predictive RMSE measurement.

It ties the R2A pieces together:

1. derive a held-out evaluation seed from the run's training seed
   (:func:`research.evaluation.split.probe_seed`);
2. assert that seed is disjoint from training
   (:func:`research.evaluation.split.assert_disjoint`);
3. build the held-out sensory stream from that seed
   (:func:`validation.datasets.build_dataset`);
4. score it read-only against a ``deepcopy`` of the monitor
   (:class:`research.evaluation.read_only.ReadOnlyEvaluator`);
5. return the measurement(s) for the runner to merge into its record.

The protocol never mutates the live monitor (the evaluator guarantees that) and
never touches any frozen production component beyond *reading* the existing
dataset factory.

Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from research.evaluation.read_only import ReadOnlyEvaluator
from research.evaluation.split import assert_disjoint, probe_seed
from validation.datasets import build_dataset

#: Measurement-record key under which the held-out RMSE is published. Kept in
#: sync with the ``HeldOutPredictiveRMSE`` extractor in :mod:`research.metrics`.
HELD_OUT_RMSE_KEY = "held_out_predictive_rmse"

#: Default number of held-out probe ticks. Large enough for a stable RMSE,
#: small enough to keep ``finalize`` cheap relative to a full training run.
DEFAULT_PROBE_TICKS = 200


@dataclass(frozen=True)
class EvaluationProtocol:
    """A read-only, held-out predictive-RMSE evaluation hook.

    Parameters
    ----------
    train_seed :
        The seed the run was trained under. The held-out stream is drawn from a
        seed deterministically derived from (and provably disjoint from) it.
    dataset_name :
        Dataset to draw the held-out stream from (must match the registry in
        :mod:`validation.datasets`).
    noise_sigma :
        Sensor-noise std-dev of the held-out stream. Defaults to the same value
        used by the training run for a like-for-like generalization measurement.
    num_probe_ticks :
        Number of held-out vectors to score.
    probe_index :
        Offset within the training seed's evaluation block, for drawing a
        distinct held-out stream (see :func:`probe_seed`).
    """

    train_seed: int
    dataset_name: str = "environment"
    noise_sigma: float = 0.05
    num_probe_ticks: int = DEFAULT_PROBE_TICKS
    probe_index: int = 0

    def held_out_seed(self) -> int:
        """The reproducible, training-disjoint seed of the held-out stream."""
        return probe_seed(self.train_seed, self.probe_index)

    def finalize(self, monitor: Any) -> Dict[str, float]:
        """Score ``monitor`` on the held-out stream; return measurement(s).

        Parameters
        ----------
        monitor :
            The trained monitor (the run's live model). It is **not** mutated:
            :class:`ReadOnlyEvaluator` evaluates a deepcopy.

        Returns
        -------
        dict
            ``{HELD_OUT_RMSE_KEY: <held-out predictive RMSE>}``, ready for the
            runner to merge into its measurement record.
        """
        eval_seed = self.held_out_seed()

        # Independence guard: the held-out stream must share no seed lineage
        # with training. This is the scientific crux of "held-out".
        assert_disjoint([self.train_seed], [eval_seed])

        dataset = build_dataset(
            self.dataset_name, seed=eval_seed, noise_sigma=self.noise_sigma
        )
        vectors = [dataset.get_next_tick() for _ in range(self.num_probe_ticks)]

        trace = ReadOnlyEvaluator(monitor).evaluate(vectors, seed=eval_seed)
        return {HELD_OUT_RMSE_KEY: trace.rmse}


__all__ = ["EvaluationProtocol", "HELD_OUT_RMSE_KEY", "DEFAULT_PROBE_TICKS"]
