"""Excess log loss against the task oracle.

Responsibility: report retention on a scale that is comparable across tasks and
does not reward failure to learn.

`excess[i] = model_loss(i) - oracle_loss(i)` on the same probe pairs. Zero means
the model matched the achievable floor; larger is worse. The M0 review requires
this family of numbers rather than the `retention` scalar (recommendation 7):

    final_prior_excess_mean   final loss on tasks other than the one just
                              trained — "how much competence is left", which
                              unlike change-from-learned cannot be improved by
                              learning less in the first place.
    final_prior_excess_worst  worst-case task, because a mean over tasks hides
                              catastrophic loss on one of them (assumption 14).
    degradation_*             paired change from each task's own post-training
                              probe. This is the primary dependent variable of
                              V0-1 and is reported alongside `learned_excess` so
                              initial mastery is always visible next to it.
    retention_auc             mean prior-task excess across all checkpoints, not
                              only the last one (review control 13).
    backward_transfer         -mean(degradation), sign-conventional: higher is
                              better.

`requires_oracle` is True, so configuring this metric against a benchmark that
cannot supply ground truth fails before the run starts.
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.types import ProbeRecord
from science.metrics.base import BaseMetric, mean
from science.registries import METRICS


class ExcessLoss(BaseMetric):
    name = "excess_loss"
    requires_oracle = True

    def __init__(self) -> None:
        self._records: List[ProbeRecord] = []

    def on_probe(self, rec: ProbeRecord) -> None:
        self._records.append(rec)

    def result(self) -> Dict[str, Any]:
        if not self._records:
            return {"available": False, "reason": "no probe records"}

        excess = [list(rec.excess) for rec in self._records]
        trained = [rec.trained_task for rec in self._records]
        n_tasks = len(excess[0])
        final = excess[-1]
        last_trained = trained[-1]

        # Reference block for each task: the last block that trained it. With
        # cycles > 1 a task is trained repeatedly; the last one is the
        # conservative choice, matching p1v0.metrics.forgetting.
        ref_block: Dict[int, int] = {}
        for block, task in enumerate(trained):
            ref_block[task] = block

        learned = [float("nan")] * n_tasks
        for task, block in ref_block.items():
            if task < n_tasks:
                learned[task] = excess[block][task]

        degradation = [
            final[i] - learned[i] if learned[i] == learned[i] else float("nan")
            for i in range(n_tasks)
        ]
        prior = [i for i in range(n_tasks) if i != last_trained]
        prior_degradation = [degradation[i] for i in prior]
        prior_final = [final[i] for i in prior]

        # Retention curve: at each checkpoint, mean excess over tasks already
        # trained but not being trained now.
        curve: List[float] = []
        for block, row in enumerate(excess):
            seen = {t for t in trained[: block + 1]}
            others = [row[t] for t in sorted(seen) if t != trained[block] and t < n_tasks]
            curve.append(mean(others) if others else float("nan"))

        finite_degradation = [v for v in prior_degradation if v == v]
        return {
            "available": True,
            "n_tasks": n_tasks,
            "excess_matrix": excess,
            "block_tasks": trained,
            "learned_excess": learned,
            "final_excess": final,
            "final_prior_excess_mean": mean(prior_final),
            "final_prior_excess_worst": max(prior_final) if prior_final else float("nan"),
            "degradation": degradation,
            "degradation_prior_mean": mean(prior_degradation),
            "degradation_prior_worst": (
                max(finite_degradation) if finite_degradation else float("nan")
            ),
            "backward_transfer": -mean(prior_degradation),
            "retention_curve": curve,
            "retention_auc": mean(curve),
            "primary_outcome_eligible": True,
        }


@METRICS.register("excess_loss")
def _excess_loss() -> ExcessLoss:
    return ExcessLoss()
