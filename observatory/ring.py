"""Bounded event ring with an explicit drop ledger.

Responsibility: absorb events at engine speed in bounded memory, and account for
everything it could not keep.

The whole design turns on one requirement: **the engine must never block, and the
instrument must never lie.** Those two pull in opposite directions -- a bounded
buffer under a fast producer must lose data. The resolution is that loss is legal
but never silent: every dropped event increments a counter and the `seq` range of
the loss is recorded, so a viewer can render a gap instead of an interpolation.

This is the specific reason `backend/runtime/event_bus.py` is not used as the
Observatory spine: it drops above a queue depth and only logs a warning, so a
consumer cannot tell a quiet period from a lost one.

Structural events (`node_add`, `edge_add`, run lifecycle, probes) are protected:
when the ring is full it prefers to drop a droppable event from the front, and only
sacrifices a protected one if the buffer holds nothing else. Losing a sample costs
a pixel; losing a topology change desynchronises the client permanently.
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Iterator, List

from observatory.schema import ObsEvent


class EventRing:
    """Fixed-capacity FIFO of events with drop accounting."""

    __slots__ = ("capacity", "_buf", "_dropped", "_first_dropped_seq",
                 "_last_dropped_seq", "_dropped_by_kind", "_accepted")

    def __init__(self, capacity: int = 65_536) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = int(capacity)
        self._buf: Deque[ObsEvent] = deque()
        self._dropped = 0
        self._first_dropped_seq: int | None = None
        self._last_dropped_seq: int | None = None
        self._dropped_by_kind: Dict[str, int] = {}
        self._accepted = 0

    # ------------------------------------------------------------------ write
    def append(self, event: ObsEvent) -> None:
        """Add an event, evicting to stay within capacity. Never raises, never blocks."""
        if len(self._buf) >= self.capacity:
            self._evict_one()
        self._buf.append(event)
        self._accepted += 1

    def extend(self, events: List[ObsEvent]) -> None:
        for event in events:
            self.append(event)

    def _evict_one(self) -> None:
        """Drop the oldest droppable event, else the oldest event."""
        victim_index = None
        for i, candidate in enumerate(self._buf):
            if candidate.droppable:
                victim_index = i
                break
        if victim_index is None:
            victim = self._buf.popleft()
        elif victim_index == 0:
            victim = self._buf.popleft()
        else:
            # Rotating is O(k) in the scan depth, not in capacity. It only happens
            # when the front of the buffer is entirely protected events, which is
            # rare by construction: protected kinds are a small minority.
            self._buf.rotate(-victim_index)
            victim = self._buf.popleft()
            self._buf.rotate(victim_index)
        self._record_drop(victim)

    def _record_drop(self, victim: ObsEvent) -> None:
        self._dropped += 1
        if self._first_dropped_seq is None:
            self._first_dropped_seq = victim.seq
        self._last_dropped_seq = victim.seq
        self._dropped_by_kind[victim.kind] = self._dropped_by_kind.get(victim.kind, 0) + 1

    # ------------------------------------------------------------------- read
    def drain(self) -> List[ObsEvent]:
        """Remove and return everything currently buffered, oldest first."""
        out = list(self._buf)
        self._buf.clear()
        return out

    def peek(self, since_seq: int | None = None) -> List[ObsEvent]:
        """Non-destructive view, optionally limited to `seq > since_seq`."""
        if since_seq is None:
            return list(self._buf)
        return [e for e in self._buf if e.seq > since_seq]

    def __len__(self) -> int:
        return len(self._buf)

    def __iter__(self) -> Iterator[ObsEvent]:
        return iter(list(self._buf))

    # ------------------------------------------------------------------ stats
    @property
    def dropped(self) -> int:
        return self._dropped

    def stats(self) -> Dict[str, object]:
        """The ledger. Emitted as a `stream_meta` event so viewers can show gaps."""
        return {
            "capacity": self.capacity,
            "buffered": len(self._buf),
            "accepted": self._accepted,
            "dropped": self._dropped,
            "first_dropped_seq": self._first_dropped_seq,
            "last_dropped_seq": self._last_dropped_seq,
            "dropped_by_kind": dict(self._dropped_by_kind),
        }
