"""Test doubles for engine verification.

Responsibility: provide benchmarks with no randomness and no scientific content,
so engine behaviour can be tested in isolation from mechanisms.

Nothing here may be used to produce reportable evidence.
"""

from __future__ import annotations

from benchmarks.testing import deterministic  # noqa: F401  (registration)
from benchmarks.testing.deterministic import CyclicEnvironment, DeterministicBenchmark

__all__ = ["CyclicEnvironment", "DeterministicBenchmark", "deterministic"]
