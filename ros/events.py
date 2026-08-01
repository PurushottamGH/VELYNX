"""P1 Research Operating System — self-instrumentation.

The ROS measures the laboratory. This module measures the ROS, so that claims
about it ("the propagation gate saves time", "registration is the bottleneck")
can be checked against a record instead of asserted.

**This telemetry is not evidence.** It is engineering observability about the
operating system, not measurement of the system under study. Article L-8 keeps
those apart, and the separation is enforced structurally here: events are written
to :data:`EVENT_LOG` — outside ``science/`` and outside the store — and nothing in
:mod:`ros` reads them back into a scientific computation. The event log may be
deleted at any time without affecting any scientific claim. If deleting it would
change a claim, the separation has been violated.

The format is append-only JSONL, one object per line, mirroring the shape of the
Observatory's own streams so that familiar tooling works on it. Append-only
because an event log that can be edited measures nothing.
"""

from __future__ import annotations

import json
import os
import platform
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from . import __version__

#: Engineering telemetry location. Deliberately not under ``science/``.
EVENT_LOG = Path(".ros/events.jsonl")

#: Event kinds the ROS emits. A kind not in this set is a programming error, not
#: a new event type: adding one should be a deliberate edit here.
KINDS: frozenset[str] = frozenset(
    {
        "gate_run",
        "store_check",
        "propagation_audit",
        "protocol_lint",
        "protocol_freeze",
        "projection_render",
        "authority_refusal",
        "agent_action",
        "escalation",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Event:
    """One ROS event."""

    kind: str
    actor: str
    outcome: str
    detail: dict[str, Any] = field(default_factory=dict)
    at: str = ""

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"unknown event kind {self.kind!r}; add it to ros.events.KINDS")
        if not self.at:
            self.at = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "at": self.at,
            "kind": self.kind,
            "actor": self.actor,
            "outcome": self.outcome,
            "ros_version": __version__,
            "detail": self.detail,
        }


def emit(event: Event, root: Path | str = ".") -> Path:
    """Append one event. Creates the log directory on first use."""
    path = Path(root) / EVENT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    return path


def read(root: Path | str = ".") -> Iterator[dict[str, Any]]:
    """Yield events oldest first. A malformed line is skipped, not fatal:
    telemetry must never be able to break a gate."""
    path = Path(root) / EVENT_LOG
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def summarise(root: Path | str = ".") -> dict[str, dict[str, int]]:
    """Counts of outcome per kind — the minimum needed to see a trend."""
    summary: dict[str, dict[str, int]] = {}
    for record in read(root):
        kind = str(record.get("kind", "unknown"))
        outcome = str(record.get("outcome", "unknown"))
        summary.setdefault(kind, {}).setdefault(outcome, 0)
        summary[kind][outcome] += 1
    return summary


def environment() -> dict[str, str]:
    """Environment fingerprint attached to events that need one.

    Not a run manifest. A run manifest is a scientific artifact produced by the
    engine; this is enough to tell one CI machine from another when debugging why
    a gate behaved differently.
    """
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "ci": os.environ.get("CI", ""),
    }


__all__ = ["EVENT_LOG", "Event", "KINDS", "emit", "environment", "read", "summarise"]
