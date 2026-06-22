"""
VELYNX Phase 55 — Working Memory Buffer
=======================================

VELYNX reasons over the *concepts* extracted from each user message. In
isolation that produces conversational amnesia: a follow-up like "where is it?"
or "who founded it?" carries no nameable concept of its own, so the symbolic
reasoner has nothing to traverse and the answer collapses to "unknown".

:class:`WorkingMemoryManager` is a small, in-process short-term store that
remembers the concepts discussed in the last few turns *per session*. When the
pipeline sees an unresolved pronoun, it pulls these active concepts back into
the query context so the reasoner can resolve "it" / "there" / "he" to whatever
the conversation was just about.

Design notes
------------
* **Per-session, rolling.** A ``dict[session_id] -> deque`` of per-turn concept
  lists, each deque capped at :data:`DEFAULT_MAX_TURNS` (~3). Old turns fall off
  the back automatically — this is *short-term* memory, not the durable graph.
* **Bounded sessions.** An :class:`OrderedDict` with LRU eviction caps the total
  number of tracked sessions so a long-running server can't leak memory.
* **Recency-ordered retrieval.** :meth:`get_active_concepts` flattens the buffer
  most-recent-turn-first and de-duplicates (case-insensitive), so the freshest
  topic is offered to the reasoner first.
* **Pure & deterministic.** No I/O, no model load, thread-light. Safe to call on
  every turn of every session.
"""
from __future__ import annotations

import threading
from collections import OrderedDict, deque
from typing import Deque, Dict, Iterable, List

# How many recent turns of concepts to retain per session.
DEFAULT_MAX_TURNS = 3
# Cap on simultaneously tracked sessions (LRU-evicted beyond this).
DEFAULT_MAX_SESSIONS = 512
# Default ceiling on concepts handed back for a single injection.
DEFAULT_MAX_ACTIVE = 8


class WorkingMemoryManager:
    """Short-term, per-session buffer of recently discussed concepts."""

    def __init__(
        self,
        max_turns: int = DEFAULT_MAX_TURNS,
        max_sessions: int = DEFAULT_MAX_SESSIONS,
    ) -> None:
        self._max_turns = max(1, int(max_turns))
        self._max_sessions = max(1, int(max_sessions))
        # session_id -> deque[ list[concept] ]  (one inner list per turn)
        self._buffers: "OrderedDict[str, Deque[List[str]]]" = OrderedDict()
        self._lock = threading.Lock()

    # ── Internals ───────────────────────────────────────────────────────────
    @staticmethod
    def _clean(concepts: Iterable[str]) -> List[str]:
        """Strip, drop empties, de-duplicate (case-insensitive), preserve order."""
        seen: set[str] = set()
        out: List[str] = []
        for c in concepts or []:
            label = str(c).strip()
            if not label:
                continue
            key = label.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(label)
        return out

    def _touch(self, session_id: str) -> Deque[List[str]]:
        """Return the session's deque, creating it and enforcing the LRU cap."""
        buf = self._buffers.get(session_id)
        if buf is None:
            buf = deque(maxlen=self._max_turns)
            self._buffers[session_id] = buf
            # Evict least-recently-used sessions beyond the cap.
            while len(self._buffers) > self._max_sessions:
                self._buffers.popitem(last=False)
        else:
            self._buffers.move_to_end(session_id)
        return buf

    # ── Public API ────────────────────────────────────────────────────────────
    def update(self, session_id: str, concepts: Iterable[str]) -> None:
        """Record the concepts discussed in the latest turn for ``session_id``.

        Empty/blank concepts are dropped; a turn that yields no concepts is not
        stored (so it can't push real context out of the rolling window).
        """
        sid = session_id or "default"
        cleaned = self._clean(concepts)
        if not cleaned:
            return
        with self._lock:
            self._touch(sid).append(cleaned)

    def get_active_concepts(
        self, session_id: str, limit: int = DEFAULT_MAX_ACTIVE
    ) -> List[str]:
        """Return recent concepts for ``session_id``, most-recent-turn-first.

        Concepts are flattened across the retained turns and de-duplicated
        (case-insensitive); the freshest turn's concepts come first. Returns at
        most ``limit`` concepts (``limit <= 0`` means no cap).
        """
        sid = session_id or "default"
        with self._lock:
            buf = self._buffers.get(sid)
            turns = list(buf) if buf else []
        seen: set[str] = set()
        out: List[str] = []
        # Iterate newest -> oldest so recent topics win the dedup race.
        for turn in reversed(turns):
            for c in turn:
                key = c.lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append(c)
                if limit and len(out) >= limit:
                    return out
        return out

    def clear(self, session_id: str | None = None) -> None:
        """Forget a single session, or all sessions when ``session_id`` is None."""
        with self._lock:
            if session_id is None:
                self._buffers.clear()
            else:
                self._buffers.pop(session_id, None)

    def turn_count(self, session_id: str) -> int:
        """Number of turns currently retained for ``session_id``."""
        with self._lock:
            buf = self._buffers.get(session_id or "default")
            return len(buf) if buf else 0


# Process-wide singleton shared by the pipeline's read (injection) and
# end-of-turn (update) paths.
working_memory_manager = WorkingMemoryManager()


__all__ = ["WorkingMemoryManager", "working_memory_manager"]
