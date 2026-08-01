"""The observation tap.

Responsibility: receive engine events, turn them into `ObsEvent`s, and buffer them.
Nothing else. In particular it never computes a scientific quantity, never touches
the model except through `state_dict()`, and never raises.

It satisfies `core.protocols.Logger` (`event(kind, payload)` and `close()`), which is
the engine's designated seam for components that "may not change what happens". Two
extra hooks, `on_step` and `on_state`, are additive: the engine calls them only if
the proposed Tier B patch is approved, and the tap works without them (the Tier A
recorder reconstructs the same stream from artifacts).

Non-interference is enforced structurally, not by discipline:

  * **Every public method has a blanket except.** A bug in the Observatory records a
    fault counter and returns; it cannot propagate into a multi-hour run. This is the
    same trade `experiments.engine.logs.MultiLogger` already makes.
  * **No blocking.** Writes go to an in-memory ring (`observatory.ring`). No socket,
    no disk, no lock is touched on the engine's thread during a step.
  * **No formatting on the hot path.** Payloads stay as Python objects; JSON encoding
    happens at flush time. `experiments/engine/logs.py` documents why: serialising
    tens of thousands of step records inline would dominate run time.
  * **Read-only state access.** `CountModel.state_dict()` returns copied rows, so the
    projector cannot alias live state.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Mapping

from observatory import codec
from observatory.graph import GraphProjector
from observatory.ring import EventRing
from observatory.schema import ObsEvent, SchemaError

#: Engine logger kinds that map straight onto Observatory kinds.
_PASSTHROUGH = frozenset({"run_start", "run_end", "truncated", "error", "probe"})


class ObservatoryTap:
    """A non-interfering observer of one engine run.

    Parameters
    ----------
    run_id:
        Identity used for every event of this run. Defaults to the value seen in the
        `run_start` payload.
    capacity:
        Ring size in events.
    step_stride:
        Emit one `step` event every `step_stride` steps. Steps where the replay gate
        fired are always emitted regardless of stride, because gate firings are rare,
        causally important, and cheap to keep. The effective policy is reported in the
        closing `stream_meta` event so a reader knows the sampling.
    epsilon:
        Edge-liveness threshold for graph projection. Zero (the default) keeps
        projection exact and reconstruction bit-faithful.
    sink_path:
        Optional JSONL file. Written by `flush()`/`close()`, never during a step.
    """

    __slots__ = ("run_id", "ring", "projector", "step_stride", "_seq", "_t0",
                 "_faults", "_emitted", "_sink_path", "_steps_seen", "_closed",
                 "_unmapped")

    def __init__(
        self,
        run_id: str = "",
        capacity: int = 65_536,
        step_stride: int = 1,
        epsilon: float = 0.0,
        sink_path: str | Path | None = None,
    ) -> None:
        self.run_id = run_id
        self.ring = EventRing(capacity=capacity)
        self.projector = GraphProjector(epsilon=epsilon)
        self.step_stride = max(1, int(step_stride))
        self._seq = 0
        self._t0 = time.monotonic()
        self._faults = 0
        self._emitted = 0
        self._steps_seen = 0
        self._closed = False
        self._unmapped: Dict[str, int] = {}
        self._sink_path = Path(sink_path) if sink_path is not None else None

    # ------------------------------------------------------------------ Logger
    def event(self, kind: str, payload: Mapping[str, Any]) -> None:
        """`core.protocols.Logger.event`. Never raises."""
        try:
            if kind == "run_start" and not self.run_id:
                self.run_id = str(payload.get("run_id", ""))
            if kind in _PASSTHROUGH:
                self._emit(kind, dict(payload), t=_opt_int(payload.get("step")))
            else:
                # An engine kind this schema does not model is recorded as
                # bookkeeping rather than dropped: an unobserved event should be
                # visible as a known unknown.
                self._unmapped[kind] = self._unmapped.get(kind, 0) + 1
                self._emit("stream_meta", {"unmapped_kind": kind, **dict(payload)})
        except Exception:  # noqa: BLE001 -- see module docstring: I1 over completeness
            self._faults += 1

    def close(self) -> None:
        """Emit the ledger, flush if configured, and stop accepting events."""
        try:
            if self._closed:
                return
            self._emit("stream_meta", {"closing": True, **self.stats()})
            if self._sink_path is not None:
                self.flush()
            self._closed = True
        except Exception:  # noqa: BLE001
            self._faults += 1

    # -------------------------------------------------------- optional hooks
    def on_step(self, rec: Any) -> None:
        """Observe one `core.types.StepRecord`. Never raises."""
        try:
            self._steps_seen += 1
            t = int(getattr(rec, "t", 0))
            gate_fired = bool(getattr(rec, "gate_fired", False))
            if not gate_fired and (t % self.step_stride) != 0:
                return
            self._emit(
                "step",
                {
                    "task": int(getattr(rec, "task", 0)),
                    "loss": float(getattr(rec, "loss", float("nan"))),
                    "replays": int(getattr(rec, "replays", 0)),
                    "gate_fired": gate_fired,
                    "buffer_size": int(getattr(rec, "buffer_size", 0)),
                    "updates": int(getattr(rec, "updates", 0)),
                },
                t=t,
            )
            if gate_fired:
                self._emit(
                    "replay_batch",
                    {"k": int(getattr(rec, "replays", 0))},
                    t=t,
                )
        except Exception:  # noqa: BLE001
            self._faults += 1

    def on_state(self, model: Any, t: int | None = None) -> None:
        """Project model state into graph deltas. Read-only. Never raises."""
        try:
            state_fn = getattr(model, "state_dict", None)
            if not callable(state_fn):
                return
            state = state_fn()
            for kind, payload in self.projector.project(state, t=t):
                self._emit(kind, payload, t=t)
        except Exception:  # noqa: BLE001
            self._faults += 1

    def on_activation(self, context: Any, distribution: Any, t: int | None = None) -> None:
        """Observe one predictive distribution. Read-only. Never raises."""
        try:
            self._emit("activation", {"context": context, "dist": list(distribution)}, t=t)
        except Exception:  # noqa: BLE001
            self._faults += 1

    # ------------------------------------------------------------------ output
    def drain(self) -> List[ObsEvent]:
        """Take everything buffered. Used by the flusher and by tests."""
        try:
            return self.ring.drain()
        except Exception:  # noqa: BLE001
            self._faults += 1
            return []

    def flush(self) -> int:
        """Append buffered events to `sink_path` as JSONL. Returns events written.

        Called off the hot path (from `close()` or a flusher thread), because this is
        where JSON encoding and disk IO happen.
        """
        if self._sink_path is None:
            return 0
        try:
            events = self.drain()
            if not events:
                return 0
            self._sink_path.parent.mkdir(parents=True, exist_ok=True)
            with self._sink_path.open("a", encoding="utf-8") as fh:
                fh.write(codec.encode_stream(events))
            return len(events)
        except Exception:  # noqa: BLE001
            self._faults += 1
            return 0

    def stats(self) -> Dict[str, Any]:
        """Instrument self-report: what it saw, kept, lost, and failed on."""
        out: Dict[str, Any] = {
            "run_id": self.run_id,
            "emitted": self._emitted,
            "steps_seen": self._steps_seen,
            "step_stride": self.step_stride,
            "faults": self._faults,
            "unmapped_kinds": dict(self._unmapped),
        }
        try:
            out.update(self.ring.stats())
        except Exception:  # noqa: BLE001
            self._faults += 1
        return out

    # ------------------------------------------------------------------ internal
    def _emit(self, kind: str, payload: Dict[str, Any], t: int | None = None) -> None:
        if self._closed:
            return
        if t is None:
            t = _opt_int(payload.get("t"))
        payload.pop("t", None)
        try:
            event = ObsEvent(
                seq=self._seq,
                kind=kind,
                t=t,
                wall=time.monotonic() - self._t0,
                p=codec.jsonable(payload),
            )
        except SchemaError:
            self._faults += 1
            return
        self._seq += 1
        self._emitted += 1
        self.ring.append(event)


def _opt_int(value: Any) -> int | None:
    """Best-effort int, or None. Used for payload fields that may be absent."""
    if value is None:
        return None
    try:
        out = int(value)
    except (TypeError, ValueError):
        return None
    return out if out >= 0 else None
