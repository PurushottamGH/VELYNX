"""P1 Observatory -- scientific instrumentation for the P1 engine.

The Observatory observes; it never participates. Three invariants hold, and the
suite in `tests/unit/test_observatory.py` exists to keep them holding:

    I1  Non-interference   attaching, configuring, or crashing the Observatory
                           cannot change any number the engine reports.
    I2  Identity neutrality enabling it must not change `config_hash` / `run_id`.
                           Achieved by attaching only through `logging`, which
                           `RunConfig.identity_dict()` already excludes.
    I3  Provenance         every rendered element traces to a real engine event,
                           identified by `(run_id, seq, t)`. Nothing is synthesised.

Architecture: `docs/architecture/OBSERVATORY_ARCHITECTURE.md`.

This package does not import `backend/`, and it does not import the engine. It
depends only on the Python standard library, so an archived event stream stays
readable with no P1 installation.
"""

from __future__ import annotations

from observatory.codec import decode_line, decode_stream, encode_line, encode_stream
from observatory.graph import GraphProjector, GraphView
from observatory.recorder import RunReader, discover_runs
from observatory.ring import EventRing
from observatory.schema import KINDS, SCHEMA, ObsEvent, SchemaError, events_equal
from observatory.tap import ObservatoryTap

__version__ = "0.1.0"

__all__ = [
    "EventRing",
    "GraphProjector",
    "GraphView",
    "KINDS",
    "ObsEvent",
    "ObservatoryTap",
    "RunReader",
    "SCHEMA",
    "SchemaError",
    "__version__",
    "decode_line",
    "decode_stream",
    "discover_runs",
    "encode_line",
    "encode_stream",
    "events_equal",
]
