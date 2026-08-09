"""P1 science — what components *mean*, not how they are executed.

Responsibility: hold every choice that a scientific reviewer must be able to
audit: which mechanisms exist, how a measurement is defined, what the oracle
is, and how contrasts are inferred.

Layout:
    registries.py   the seven component tables
    mechanisms/     hypotheses under test, plus the controls that isolate them
    metrics/        measurement definitions, one metric per module
    oracle.py       ground-truth predictors, for excess-loss reporting
    stats.py        paired inference at the environment-seed level

`science` imports `core` and nothing else from P1. In particular it does not
import the engine: a mechanism that needed the runner would be untestable in
isolation.

The frozen `p1v0` package is imported read-only by `mechanisms/v0.py`. It is the
version-pinned M0 artifact and must not be edited; adapters add the protocol
surface around it instead.
"""

from science.registries import (
    ALL,
    BENCHMARKS,
    ENVIRONMENTS,
    GATES,
    MEMORIES,
    METRICS,
    MODELS,
    REPLAYS,
)

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
