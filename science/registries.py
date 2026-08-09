"""The seven scientific component tables.

Responsibility: hold the name -> factory mapping for every component whose
choice is a scientific decision. Nothing registers itself here; modules under
`science/mechanisms/`, `science/metrics/` and `benchmarks/` do, and
`experiments/engine/plugins.py` imports them once at start-up.

`Logger` is absent on purpose: which sink receives events is an engineering
choice with no effect on results, so its table lives with the engine.
"""

from __future__ import annotations

from core.protocols import Benchmark, Environment, Gate, Memory, Metric, Model, Replay
from core.registry import Registry

MODELS: Registry[Model] = Registry("model")
MEMORIES: Registry[Memory] = Registry("memory")
GATES: Registry[Gate] = Registry("gate")
REPLAYS: Registry[Replay] = Registry("replay")
ENVIRONMENTS: Registry[Environment] = Registry("environment")
METRICS: Registry[Metric] = Registry("metric")
BENCHMARKS: Registry[Benchmark] = Registry("benchmark")

#: Every table, keyed by the config section it serves. Used by the CLI to print
#: what is available and by tests to assert nothing is registered twice.
ALL: dict[str, Registry] = {
    "model": MODELS,
    "memory": MEMORIES,
    "gate": GATES,
    "replay": REPLAYS,
    "environment": ENVIRONMENTS,
    "metric": METRICS,
    "benchmark": BENCHMARKS,
}

__all__ = [
    "ALL",
    "BENCHMARKS",
    "ENVIRONMENTS",
    "GATES",
    "MEMORIES",
    "METRICS",
    "MODELS",
    "REPLAYS",
]
