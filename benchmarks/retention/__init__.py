"""Retention-under-non-stationarity benchmarks.

Responsibility: measure whether competence acquired on earlier regimes survives
later training.

    markov_retention  piecewise-stationary Markov blocks, held-out per-task probes,
                      exact oracle. Works with any environment in the family that
                      exposes its true generators.

Importing this package registers the benchmarks it contains.
"""

from __future__ import annotations

from benchmarks.retention import markov_retention  # noqa: F401  (registration)
from benchmarks.retention.markov_retention import MarkovRetention

__all__ = ["MarkovRetention", "markov_retention"]
