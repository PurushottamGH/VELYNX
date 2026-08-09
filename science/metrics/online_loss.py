"""Prequential (online) loss.

Responsibility: summarise the loss the model incurred while learning, before it
saw each target.

Reports the tail mean as well as the overall mean because the two answer
different questions: the overall mean mixes every learning regime, while the tail
describes the converged state. The M0 review notes that tail loss measures only
the last block's last window and is therefore not a general plasticity measure
(hidden assumption 16); adaptation cost after each switch is reported separately
by the `plasticity` metric.
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.types import StepRecord
from science.metrics.base import BaseMetric, mean
from science.registries import METRICS


class OnlineLoss(BaseMetric):
    name = "online_loss"

    def __init__(self, tail: int = 500) -> None:
        if tail < 1:
            raise ValueError("online_loss 'tail' must be >= 1")
        self.tail = tail
        self._losses: List[float] = []
        self._by_task: Dict[int, List[float]] = {}

    def on_step(self, rec: StepRecord) -> None:
        self._losses.append(rec.loss)
        self._by_task.setdefault(rec.task, []).append(rec.loss)

    def result(self) -> Dict[str, Any]:
        return {
            "steps": len(self._losses),
            "online_loss_mean": mean(self._losses),
            "online_loss_tail": mean(self._losses[-self.tail :]),
            "tail_window": self.tail,
            "online_loss_by_task": {
                str(task): mean(losses) for task, losses in sorted(self._by_task.items())
            },
        }


@METRICS.register("online_loss")
def _online_loss(tail: int = 500) -> OnlineLoss:
    return OnlineLoss(tail=tail)
