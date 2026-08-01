"""When the gate fired, and whether that timing is informative.

Responsibility: describe the gate's realised behaviour, and test the specific
alternative explanation the M0 review ranked as risk 1.

That alternative: surprise-triggered replay may work only because loss spikes
cluster just after task switches, making the gate an implicit change detector
rather than a surprise-driven mechanism. `boundary_fire_fraction` measures the
clustering directly — if most fires land in a short window after each switch, a
boundary-timed control at the same budget should match it, and the surprise
interpretation is unsupported.

`fires_by_task` and `fire_rate` support the equal-budget matching required by
V0-3: `n_fires` from a surprise run is the value to pin into a `matched_random`
gate for the paired comparison.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.types import StepRecord
from science.metrics.base import BaseMetric
from science.registries import METRICS


class GateActivity(BaseMetric):
    name = "gate_activity"

    def __init__(self, boundary_window: int = 50) -> None:
        if boundary_window < 1:
            raise ValueError("gate_activity 'boundary_window' must be >= 1")
        self.boundary_window = boundary_window
        self._steps = 0
        self._fires = 0
        self._replays = 0
        self._boundary_fires = 0
        self._fires_by_task: Dict[int, int] = {}
        self._fire_steps: List[int] = []
        self._prev_task: Optional[int] = None
        self._since_switch = 0
        self._first_block = True

    def on_step(self, rec: StepRecord) -> None:
        if rec.task != self._prev_task:
            if self._prev_task is not None:
                self._first_block = False
            self._prev_task = rec.task
            self._since_switch = 0

        self._steps += 1
        if rec.gate_fired:
            self._fires += 1
            self._replays += rec.replays
            self._fires_by_task[rec.task] = self._fires_by_task.get(rec.task, 0) + 1
            self._fire_steps.append(rec.t)
            # Only switches count: the run's start is not a switch.
            if not self._first_block and self._since_switch < self.boundary_window:
                self._boundary_fires += 1
        self._since_switch += 1

    def result(self) -> Dict[str, Any]:
        return {
            "steps": self._steps,
            "fired_steps": self._fires,
            "total_replays": self._replays,
            "fire_rate": (self._fires / self._steps) if self._steps else 0.0,
            "mean_batch_size": (self._replays / self._fires) if self._fires else 0.0,
            "fires_by_task": {str(k): v for k, v in sorted(self._fires_by_task.items())},
            "boundary_window": self.boundary_window,
            "boundary_fires": self._boundary_fires,
            "boundary_fire_fraction": (self._boundary_fires / self._fires) if self._fires else 0.0,
            "first_fire_step": self._fire_steps[0] if self._fire_steps else None,
            "last_fire_step": self._fire_steps[-1] if self._fire_steps else None,
        }


@METRICS.register("gate_activity")
def _gate_activity(boundary_window: int = 50) -> GateActivity:
    return GateActivity(boundary_window=boundary_window)
