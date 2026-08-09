"""Observatory event schema.

Responsibility: fix the wire shape of everything the Observatory observes, and
nothing else. This module imports no engine code on purpose -- the schema must be
readable by an archival tool that has no P1 installed.

Design rules and their reasons:

  * **Closed kind set.** An unknown kind is an error, not a passthrough. A renderer
    that silently ignores an event it does not understand would show a state that
    never existed.
  * **Versioned.** `SCHEMA` is written into every event. A stored stream must be
    decodable years later by code that can recognise which rules applied to it.
  * **Frozen envelope.** Events are immutable, so a projector, a ring buffer and a
    codec can share one object without any of them being able to edit history.
  * **`seq` orders, `wall` does not.** `seq` is assigned by the tap and is
    reproducible; `wall` is diagnostic only. Sorting by a clock would make replay
    depend on machine speed, which would break deterministic playback.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

#: Schema identity, embedded in every event and every stored segment.
SCHEMA = "obs/1"

# --------------------------------------------------------------------------- #
# Kind registry
# --------------------------------------------------------------------------- #

#: Run lifecycle. Mirrors the kinds the engine's own `Logger` already emits.
LIFECYCLE: Tuple[str, ...] = ("run_start", "run_end", "truncated", "error")

#: Structural graph change. Never decimated: losing one desynchronises the client.
STRUCTURAL: Tuple[str, ...] = (
    "topology_init",
    "node_add",
    "node_remove",
    "edge_add",
    "edge_remove",
)

#: Sampled dynamics. Safe to decimate, because every payload carries absolute values.
DYNAMIC: Tuple[str, ...] = ("step", "edge_update", "activation", "replay_batch")

#: Memory (reservoir) churn.
MEMORY: Tuple[str, ...] = ("memory_admit", "memory_evict")

#: Measurement and bookkeeping. `stream_meta` reports the instrument's own losses.
MEASUREMENT: Tuple[str, ...] = ("probe", "metric_sample", "snapshot", "stream_meta")

KINDS: Tuple[str, ...] = LIFECYCLE + STRUCTURAL + DYNAMIC + MEMORY + MEASUREMENT

#: Stable numeric ids for the binary codec. Append only -- never renumber, or old
#: segments become unreadable.
KIND_IDS: Dict[str, int] = {name: i + 1 for i, name in enumerate(KINDS)}
ID_KINDS: Dict[int, str] = {v: k for k, v in KIND_IDS.items()}

#: Kinds that must survive every backpressure policy (see architecture doc, 3.4).
UNDROPPABLE = frozenset(LIFECYCLE + STRUCTURAL + ("probe", "stream_meta", "snapshot"))


class SchemaError(ValueError):
    """Raised for an event that violates the schema. Always names the field."""


# --------------------------------------------------------------------------- #
# Envelope
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ObsEvent:
    """One observation of engine state.

    `t` is the engine step index, or None for events that are not tied to a step
    (run lifecycle, transport bookkeeping). `p` is the payload; its shape is fixed
    per kind by the architecture document, and deliberately not enforced here --
    per-field validation on a hot path would cost more than it protects, and the
    codec round-trip test covers shape drift.
    """

    seq: int
    kind: str
    t: int | None = None
    wall: float = 0.0
    p: Dict[str, Any] = field(default_factory=dict)
    v: str = SCHEMA

    def __post_init__(self) -> None:
        if self.kind not in KIND_IDS:
            raise SchemaError(f"kind: unknown event kind {self.kind!r}")
        if self.seq < 0:
            raise SchemaError(f"seq: must be non-negative, got {self.seq}")
        if self.t is not None and self.t < 0:
            raise SchemaError(f"t: must be non-negative or None, got {self.t}")

    @property
    def droppable(self) -> bool:
        return self.kind not in UNDROPPABLE

    def as_dict(self) -> Dict[str, Any]:
        return {"v": self.v, "seq": self.seq, "kind": self.kind,
                "t": self.t, "wall": self.wall, "p": dict(self.p)}


# --------------------------------------------------------------------------- #
# Comparison
# --------------------------------------------------------------------------- #


def values_equal(a: Any, b: Any) -> bool:
    """Structural equality that treats NaN as equal to NaN.

    Needed because NaN is a legitimate payload value (an unprobed task's loss is
    NaN throughout `science/metrics`), and `NaN != NaN` would make every
    round-trip and fidelity assertion fail for the wrong reason.
    """
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return a == b
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        if set(a) != set(b):
            return False
        return all(values_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(values_equal(x, y) for x, y in zip(a, b))
    return bool(a == b) if type(a) is type(b) else a == b


def events_equal(a: ObsEvent, b: ObsEvent) -> bool:
    """Event equality with NaN-tolerant payload comparison."""
    return (
        a.v == b.v
        and a.seq == b.seq
        and a.kind == b.kind
        and a.t == b.t
        and values_equal(a.p, b.p)
    )
