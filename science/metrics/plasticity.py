"""Adaptation cost after task switches — the plasticity guardrail.

Responsibility: measure how expensive it is for the model to adapt when the
regime changes.

Experiments V0-2 and V0-3 declare a plasticity guardrail as a co-primary outcome:
a mechanism that improves retention by refusing to adapt has not solved anything.
Tail online loss cannot serve that role, because it describes only the final
block's last window (M0 hidden assumption 16).

Reported:
    adaptation_auc      mean online loss over the `window` steps following every
                        switch, averaged over switches. Area under the adaptation
                        curve: lower means faster, cheaper adaptation.
    adaptation_by_block one value per switch, so a mechanism that adapts well
                        early and badly late is visible.
    current_task_tail   mean loss over the final `window` steps, i.e. converged
                        performance on the task being trained.

Switches are detected from the task label on each step record, so this metric
works for any environment that labels its regimes and needs no knowledge of the
schedule.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.types import StepRecord
from science.metrics.base import BaseMetric, mean
from science.registries import METRICS


class Plasticity(BaseMetric):
    name = "plasticity"

    def __init__(self, window: int = 200) -> None:
        if window < 1:
            raise ValueError("plasticity 'window' must be >= 1")
        self.window = window
        self._blocks: List[List[float]] = []
        self._tail: List[float] = []
        self._prev_task: Optional[int] = None
        self._since_switch = 0

    def on_step(self, rec: StepRecord) -> None:
        if rec.task != self._prev_task:
            self._blocks.append([])
            self._prev_task = rec.task
            self._since_switch = 0
        if self._since_switch < self.window:
            self._blocks[-1].append(rec.loss)
        self._since_switch += 1

        self._tail.append(rec.loss)
        if len(self._tail) > self.window:
            self._tail.pop(0)

    def result(self) -> Dict[str, Any]:
        per_block = [mean(b) for b in self._blocks]
        # The first block is not a switch: there is no prior task to switch from.
        switches = per_block[1:]
        return {
            "window": self.window,
            "n_blocks": len(per_block),
            "adaptation_by_block": per_block,
            "adaptation_auc": mean(switches) if switches else float("nan"),
            "first_block_mean": per_block[0] if per_block else float("nan"),
            "current_task_tail": mean(self._tail),
        }


@METRICS.register("plasticity")
def _plasticity(window: int = 200) -> Plasticity:
    return Plasticity(window=window)
