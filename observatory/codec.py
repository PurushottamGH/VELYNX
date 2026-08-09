"""Event codec.

Responsibility: turn events into bytes and back without losing information.

JSON-lines is the canonical v1 encoding. It is chosen over a binary format for the
first milestone for one reason: an instrument whose output can only be read by its
own renderer cannot be audited. A JSONL stream is greppable, diffable, loadable
from a Python REPL, and readable in ten years with nothing but the standard
library. The binary framing described in the architecture document is an
*optimisation* layered on top, and both must decode to identical events.

Non-finite floats (NaN, +/-inf) are preserved via Python's JSON extension tokens.
They are real values in this domain -- `science.metrics.mean` deliberately produces
NaN for an unprobed task -- so silently coercing them to null would corrupt data.
`decode_line` therefore round-trips them exactly.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Iterator, Mapping

from observatory.schema import SCHEMA, ObsEvent, SchemaError


def encode_line(event: ObsEvent) -> str:
    """One event as one canonical JSON line, without the trailing newline.

    Keys are sorted so that two encodings of the same event are byte-identical,
    which is what allows segment files to be content-hashed.
    """
    return json.dumps(event.as_dict(), sort_keys=True, separators=(",", ":"))


def decode_line(line: str) -> ObsEvent:
    """Parse one JSON line back into an event."""
    text = line.strip()
    if not text:
        raise SchemaError("empty line")
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"not valid JSON: {exc}") from exc
    return from_mapping(raw)


def from_mapping(raw: Mapping[str, Any]) -> ObsEvent:
    """Build an event from a decoded mapping, validating the schema version."""
    if not isinstance(raw, Mapping):
        raise SchemaError(f"event must be a mapping, got {type(raw).__name__}")
    version = raw.get("v", SCHEMA)
    if version != SCHEMA:
        # Refuse rather than guess. A future migration table belongs here, keyed by
        # version, so that old segments stay readable instead of being reinterpreted.
        raise SchemaError(f"v: unsupported schema {version!r}, this build reads {SCHEMA!r}")
    for required in ("seq", "kind"):
        if required not in raw:
            raise SchemaError(f"{required}: missing")
    payload = raw.get("p") or {}
    if not isinstance(payload, Mapping):
        raise SchemaError(f"p: must be a mapping, got {type(payload).__name__}")
    t = raw.get("t")
    return ObsEvent(
        seq=int(raw["seq"]),
        kind=str(raw["kind"]),
        t=None if t is None else int(t),
        wall=float(raw.get("wall", 0.0)),
        p=dict(payload),
        v=str(version),
    )


def encode_stream(events: Iterable[ObsEvent]) -> str:
    """Encode many events as a newline-terminated JSONL document."""
    return "".join(encode_line(e) + "\n" for e in events)


def decode_stream(text: str, strict: bool = True) -> Iterator[ObsEvent]:
    """Decode a JSONL document.

    `strict=False` skips unparseable lines, which is what a tailer wants when it
    reads a file the flusher is still appending to and catches a torn last line.
    A strict reader is the default so that corruption in an archived segment is
    reported rather than quietly skipped.
    """
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            yield decode_line(line)
        except SchemaError:
            if strict:
                raise
            continue


def jsonable(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Coerce values JSON cannot represent, so encoding can never raise.

    Mirrors `experiments.engine.logs._jsonable`: an instrument that crashes while
    recording is worse than one that records `repr()` of an odd value.
    """
    out: Dict[str, Any] = {}
    for key, value in payload.items():
        try:
            json.dumps(value)
            out[str(key)] = value
        except (TypeError, ValueError):
            out[str(key)] = repr(value)
    return out
