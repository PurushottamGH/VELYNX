"""
research/tests/test_read_only_nonmutation.py
============================================

BLOCKING STEP 6.0 — the deepcopy safety spike.

These tests establish the load-bearing invariant of the entire R2A slice:
:class:`research.evaluation.read_only.ReadOnlyEvaluator` scores a probe stream
on a ``deepcopy`` of the monitor and therefore leaves the **live model
bit-identical** before and after.

The suite proves two things, in order:

1. *The fingerprint is sensitive.* A single direct ``monitor.tick`` mutates the
   deep state fingerprint. Without this, a "non-mutation" assertion could pass
   vacuously against a fingerprint too coarse to see any change.
2. *Read-only evaluation does not mutate.* Running the evaluator over a probe
   stream leaves that same fingerprint unchanged — bit-for-bit.
"""

from __future__ import annotations

import json
from collections import deque
from typing import Any

from research.evaluation.read_only import ProbeTrace, ReadOnlyEvaluator
from validation.datasets import build_dataset
from validation.monitor import VectorMonitor


# ---------------------------------------------------------------------------
# Deep state fingerprint
# ---------------------------------------------------------------------------

def _fingerprint(obj: Any, _memo: set[int] | None = None) -> Any:
    """Recursively reduce an object graph to a JSON-comparable structure.

    Walks ``__dict__``/containers down to primitives so that *any* change in
    the monitor's nested state (cluster centroids, transition counts, surprise
    history, attention wiring, tick counters, ...) shows up as a difference.
    An id-keyed memo breaks reference cycles.
    """
    if _memo is None:
        _memo = set()

    if isinstance(obj, (str, int, bool, type(None))):
        return obj
    if isinstance(obj, float):
        # Round-trip via repr to keep float identity exact and comparable.
        return repr(obj)

    oid = id(obj)
    if oid in _memo:
        return "<cycle>"

    if isinstance(obj, (list, tuple, set, frozenset, deque)):
        _memo.add(oid)
        return [_fingerprint(v, _memo) for v in obj]
    if isinstance(obj, dict):
        _memo.add(oid)
        return {repr(k): _fingerprint(v, _memo) for k, v in sorted(
            obj.items(), key=lambda kv: repr(kv[0])
        )}

    state = getattr(obj, "__dict__", None)
    if state is not None:
        _memo.add(oid)
        return {type(obj).__name__: _fingerprint(state, _memo)}

    slots = getattr(obj, "__slots__", None)
    if slots:
        _memo.add(oid)
        return {
            type(obj).__name__: {
                s: _fingerprint(getattr(obj, s, None), _memo) for s in slots
            }
        }

    return repr(obj)


def _fingerprint_str(obj: Any) -> str:
    """Stable JSON serialization of :func:`_fingerprint` for equality/messages."""
    return json.dumps(_fingerprint(obj), sort_keys=True)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _trained_monitor(seed: int = 1, ticks: int = 300) -> VectorMonitor:
    """Build and train a monitor on a seeded stream so it has real state."""
    monitor = VectorMonitor(proximity_threshold=0.25, max_clusters=50)
    dataset = build_dataset("environment", seed=seed, noise_sigma=0.05)
    for _ in range(ticks):
        monitor.tick(dataset.get_next_tick())
    return monitor


def _probe_vectors(seed: int = 1_001_000, ticks: int = 150) -> list[list[float]]:
    """Draw a held-out probe stream from a disjoint seed."""
    dataset = build_dataset("environment", seed=seed, noise_sigma=0.05)
    return [dataset.get_next_tick() for _ in range(ticks)]


# ---------------------------------------------------------------------------
# 1. Fingerprint sensitivity (guards against a vacuous non-mutation pass)
# ---------------------------------------------------------------------------

def test_fingerprint_detects_a_single_direct_tick():
    monitor = _trained_monitor()
    before = _fingerprint_str(monitor)

    # A single real ingest MUST change the deep state fingerprint.
    monitor.tick(_probe_vectors(ticks=1)[0])
    after = _fingerprint_str(monitor)

    assert before != after, (
        "Fingerprint is too coarse to detect a direct tick; the non-mutation "
        "test below would be vacuous."
    )


# ---------------------------------------------------------------------------
# 2. Read-only evaluation leaves the live monitor bit-identical
# ---------------------------------------------------------------------------

def test_evaluate_does_not_mutate_live_monitor():
    monitor = _trained_monitor()
    probe = _probe_vectors()

    before = _fingerprint_str(monitor)
    trace = ReadOnlyEvaluator(monitor).evaluate(probe, seed=1_001_000)
    after = _fingerprint_str(monitor)

    assert after == before, "ReadOnlyEvaluator mutated the live monitor!"
    assert isinstance(trace, ProbeTrace)


def test_evaluate_returns_meaningful_trace():
    monitor = _trained_monitor()
    probe = _probe_vectors(ticks=120)

    trace = ReadOnlyEvaluator(monitor).evaluate(probe, seed=1_001_000)

    assert trace.num_vectors == 120
    assert trace.num_scored == 120  # every tick yields a numeric error
    assert trace.rmse > 0.0
    assert trace.mean_error > 0.0
    assert trace.seed == 1_001_000


def test_repeated_evaluations_are_independent_and_identical():
    # Each evaluate() re-clones from the (unchanged) live monitor, so two calls
    # over the same probe stream must yield identical traces.
    monitor = _trained_monitor()
    probe = _probe_vectors()

    ev = ReadOnlyEvaluator(monitor)
    first = ev.evaluate(probe)
    second = ev.evaluate(probe)

    assert first.errors == second.errors
    assert first.rmse == second.rmse


def test_empty_probe_stream_yields_zero_rmse():
    monitor = _trained_monitor()
    trace = ReadOnlyEvaluator(monitor).evaluate([])
    assert trace.num_vectors == 0
    assert trace.num_scored == 0
    assert trace.rmse == 0.0
    assert trace.mean_error == 0.0
