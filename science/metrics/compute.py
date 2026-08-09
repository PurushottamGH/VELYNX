"""Learning-update accounting.

Responsibility: report how much learning a run actually performed, so that two
conditions can be shown to be resource-matched rather than assumed to be.

The M0 review found the headline contrast confounded with roughly 32,000 extra
learning updates and an equal number of extra row decays (risk 6, experiment
V0-2). Any comparison that does not report these counts side by side cannot
support a causal claim about replay content.

`replay_shortfall` matters for budget-matched controls: `historical_only` returns
nothing until a prior-task item exists, so its realised budget can be lower than
the gate requested. A control that under-spends without saying so is not matched.

This metric derives everything from step records. It does not read the engine's
`Budget`, so it stays a pure observer and can be tested from synthetic records.
"""

from __future__ import annotations

from typing import Any, Dict

from core.types import StepRecord
from science.metrics.base import BaseMetric
from science.registries import METRICS


class Compute(BaseMetric):
    name = "compute"

    def __init__(self) -> None:
        self._steps = 0
        self._updates = 0
        self._replay_updates = 0
        self._replay_batches = 0
        self._gate_requests = 0

    def on_step(self, rec: StepRecord) -> None:
        self._steps += 1
        self._updates += rec.updates
        self._replay_updates += rec.replays
        if rec.gate_fired:
            self._replay_batches += 1

    def result(self) -> Dict[str, Any]:
        online = self._updates - self._replay_updates
        return {
            "steps": self._steps,
            "online_updates": online,
            "replay_updates": self._replay_updates,
            "updates_total": self._updates,
            "replay_batches": self._replay_batches,
            "replay_updates_per_step": (self._replay_updates / self._steps) if self._steps else 0.0,
            "update_multiplier": (self._updates / online) if online else float("nan"),
        }


@METRICS.register("compute")
def _compute() -> Compute:
    return Compute()
