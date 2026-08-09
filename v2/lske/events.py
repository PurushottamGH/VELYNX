"""Durable LSKE lifecycle and evidence event writer."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from v2.lske.errors import OntologyError, SchemaViolation
from v2.lske.schema import allocate_event_id, canonical_json

_EVENT_KEYS = frozenset(
    {"kind", "at", "by", "authority", "target", "record_id", "from", "to", "cause"}
)
_EVENT_KINDS = frozenset({"lifecycle", "evidence"})


def append_event(root: Path, event: Mapping[str, Any]) -> str:
    """Append one canonical event line and return its content-addressed identifier."""
    keys = set(event)
    failures = []
    if _EVENT_KEYS - keys:
        failures.append(("", "", "required", False))
    if keys - _EVENT_KEYS:
        failures.append(("", "", "additionalProperties", False))
    if failures:
        raise SchemaViolation("event body has an invalid key set", failures)
    if event["kind"] not in _EVENT_KINDS:
        raise OntologyError(f"unknown LSKE event kind: {event['kind']}")
    event_id = allocate_event_id(event)
    target = root / ".ros" / "lske_events.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    line = canonical_json({**dict(event), "event_id": event_id}) + b"\n"
    with target.open("ab") as handle:
        handle.write(line)
    return event_id


__all__ = ["append_event"]
