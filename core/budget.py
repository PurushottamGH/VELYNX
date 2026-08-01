"""Compute accounting and hard limits.

Responsibility: count the resources a run actually consumed, and stop it if a
declared ceiling is crossed.

This exists because the M0 review found the headline v0 contrast confounded
with 32,000 extra learning updates (risk 6, experiment V0-2). A resource-matched
comparison is impossible unless the resources are counted, so counting is part
of the engine rather than an optional metric.

`updates_total` is the accounting unit the review calls "learning updates". For
the v0 `CountModel` each update also applies one row decay, so update parity
implies decay parity for that model; a model where that does not hold must
report its own counters through `state_dict()`.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


class BudgetExceeded(RuntimeError):
    """Raised when a declared compute ceiling is crossed. Not an error state:
    the engine records it as a completed, truncated run."""


@dataclass
class Limits:
    """Declared ceilings. `None` means unbounded."""

    max_steps: Optional[int] = None
    max_updates: Optional[int] = None
    max_wall_seconds: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Budget:
    """Mutable counters for one run. The only mutable object in `core`."""

    steps: int = 0
    predictions: int = 0
    online_updates: int = 0
    replay_updates: int = 0
    replay_batches: int = 0
    replay_shortfall: int = 0  # budget asked for, minus items actually returned
    probe_evaluations: int = 0
    probe_predictions: int = 0
    limits: Limits = field(default_factory=Limits)
    wall_seconds: float = 0.0
    process_seconds: float = 0.0
    truncated_by: str = ""
    _wall_start: float = field(default=0.0, repr=False)
    _process_start: float = field(default=0.0, repr=False)

    @property
    def updates_total(self) -> int:
        return self.online_updates + self.replay_updates

    def start(self) -> None:
        self._wall_start = time.perf_counter()
        self._process_start = time.process_time()

    def stop(self) -> None:
        if self._wall_start:
            self.wall_seconds = time.perf_counter() - self._wall_start
            self.process_seconds = time.process_time() - self._process_start

    def check(self) -> None:
        """Raise `BudgetExceeded` if a ceiling is crossed. Called once per step."""
        lim = self.limits
        if lim.max_steps is not None and self.steps >= lim.max_steps:
            self.truncated_by = "max_steps"
        elif lim.max_updates is not None and self.updates_total >= lim.max_updates:
            self.truncated_by = "max_updates"
        elif (
            lim.max_wall_seconds is not None
            and self._wall_start
            and (time.perf_counter() - self._wall_start) >= lim.max_wall_seconds
        ):
            self.truncated_by = "max_wall_seconds"
        else:
            return
        raise BudgetExceeded(self.truncated_by)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "steps": self.steps,
            "predictions": self.predictions,
            "online_updates": self.online_updates,
            "replay_updates": self.replay_updates,
            "updates_total": self.updates_total,
            "replay_batches": self.replay_batches,
            "replay_shortfall": self.replay_shortfall,
            "probe_evaluations": self.probe_evaluations,
            "probe_predictions": self.probe_predictions,
            "wall_seconds": round(self.wall_seconds, 6),
            "process_seconds": round(self.process_seconds, 6),
            "limits": self.limits.as_dict(),
            "truncated_by": self.truncated_by,
        }
