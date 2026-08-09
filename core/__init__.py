"""P1 core — mechanism-agnostic contracts and deterministic primitives.

Responsibility: define *what* a component must do, never *what* it means
scientifically and never *how* an experiment is run.

Import direction is one-way and enforced by review:

    core  <-  science  <-  benchmarks  <-  experiments.engine  <-  scripts

`core` therefore imports nothing from P1 outside itself, performs no IO, and
contains no mechanism, metric, or experiment logic. Anything that would make
`core` depend on a scientific choice belongs in `science/`.

Modules:
    types      -- immutable records exchanged between components
    protocols  -- the eight replaceable component contracts
    registry   -- name -> factory lookup, the only plugin wiring mechanism
    seeds      -- independent, reproducible random substreams
    budget     -- compute accounting (updates, predictions, decay ops, time)
"""

from core.budget import Budget
from core.protocols import (
    Benchmark,
    Environment,
    Gate,
    Logger,
    Memory,
    Metric,
    Model,
    Replay,
)
from core.registry import Registry, Spec
from core.seeds import SeedSet
from core.types import Observation, ProbeRecord, RunStatus, StepRecord

__all__ = [
    "Benchmark",
    "Budget",
    "Environment",
    "Gate",
    "Logger",
    "Memory",
    "Metric",
    "Model",
    "Observation",
    "ProbeRecord",
    "Registry",
    "Replay",
    "RunStatus",
    "SeedSet",
    "Spec",
    "StepRecord",
]

__version__ = "1.0.0"
