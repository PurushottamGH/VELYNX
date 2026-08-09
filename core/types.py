"""Immutable records exchanged between components.

Responsibility: fix the shape of data crossing a component boundary, so that a
component can be replaced without touching the experiment loop.

Every record is frozen. A component that could mutate another component's
record could hide state, which would break reproducibility auditing.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class Observation:
    """One datum drawn from an environment.

    `context` and `target` are deliberately untyped: the engine never inspects
    them, it only routes them between environment, model and memory. For the v0
    Markov environments both are ints (previous symbol, observed symbol).
    """

    t: int  # global step index, 0-based
    task: int  # id of the generating task / regime
    context: Any
    target: Any

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StepRecord:
    """Outcome of one execution step.

    `loss` is the prequential (predict-before-learn) loss for this observation.
    Compute fields are counts *for this step only*; aggregation belongs to
    metrics, not to the loop.
    """

    t: int
    task: int
    loss: float
    replays: int  # replay updates performed at this step
    gate_fired: bool
    buffer_size: int
    updates: int  # total learn() calls at this step (online + replay)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProbeRecord:
    """Frozen-model evaluation at a checkpoint.

    losses[i]      -- mean loss on task i's held-out data
    oracle[i]      -- mean loss of the task-specific oracle on the same data
    excess[i]      -- losses[i] - oracle[i]; comparable across tasks of
                      differing intrinsic entropy, unlike raw loss

    `oracle` may be empty when a benchmark cannot compute a ground-truth
    predictor. Metrics that need it must declare the dependency explicitly
    rather than silently substituting zero.
    """

    t: int  # step index at which the probe was taken
    block: int  # 0-based checkpoint index
    trained_task: int  # task trained during the block just finished
    losses: Tuple[float, ...]
    oracle: Tuple[float, ...] = ()

    @property
    def excess(self) -> Tuple[float, ...]:
        if not self.oracle:
            return ()
        return tuple(l - o for l, o in zip(self.losses, self.oracle))

    def as_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out["excess"] = list(self.excess)
        return out


class RunStatus(str, Enum):
    """Lifecycle of a single run directory. Drives resume decisions."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    @property
    def is_terminal(self) -> bool:
        return self in (RunStatus.COMPLETED, RunStatus.FAILED)


@dataclass(frozen=True)
class RunResult:
    """What a completed run returns to its caller.

    Deliberately small: heavy per-step data stays on disk. A scheduler running
    hundreds of runs must not accumulate step records in memory.
    """

    run_id: str
    config_hash: str
    status: RunStatus
    metrics: Dict[str, Any] = field(default_factory=dict)
    compute: Dict[str, Any] = field(default_factory=dict)
    run_dir: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.status is RunStatus.COMPLETED

    def as_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out["status"] = self.status.value
        return out
