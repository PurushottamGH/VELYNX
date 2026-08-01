"""Structured event sinks.

Responsibility: record what happened during a run, without being able to change
what happens.

Loggers are the only components allowed to have side effects that are invisible to
results, which is why their registry lives here with the engine rather than in
`science`: choosing a sink is not a scientific decision.

Two sinks, composed by the engine:
    jsonl    machine-readable event stream, one JSON object per line
    console  human-readable progress on stderr

Per-step records do **not** go through the logger. They are bulk numeric data and
are written by the artifact writer in CSV or JSONL; sending 32,000 rows through a
logging call per run would dominate runtime for no benefit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, TextIO

from core.registry import Registry

LOGGERS: Registry[Any] = Registry("logger")

_LEVEL_ORDER = {"debug": 10, "info": 20, "warning": 30, "error": 40}

#: Events considered progress rather than milestones. Shown only at debug level.
_VERBOSE_EVENTS = frozenset({"probe", "step_batch"})


class JsonlLogger:
    """Append-only JSON-lines event log."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh: TextIO = self.path.open("w", encoding="utf-8")

    def event(self, kind: str, payload: Mapping[str, Any]) -> None:
        record = {"event": kind, **_jsonable(payload)}
        self._fh.write(json.dumps(record, sort_keys=True) + "\n")
        self._fh.flush()

    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()


class ConsoleLogger:
    """Single-line progress messages on stderr.

    stderr, not stdout, so that a caller can pipe machine-readable output from the
    CLI without log lines contaminating it.
    """

    def __init__(self, level: str = "info", stream: TextIO | None = None) -> None:
        if level not in _LEVEL_ORDER:
            raise ValueError(f"unknown log level {level!r}")
        self.level = level
        self._stream = stream if stream is not None else sys.stderr

    def event(self, kind: str, payload: Mapping[str, Any]) -> None:
        if kind in _VERBOSE_EVENTS and _LEVEL_ORDER[self.level] > _LEVEL_ORDER["debug"]:
            return
        if _LEVEL_ORDER[self.level] > _LEVEL_ORDER["info"] and kind != "error":
            return
        detail = " ".join(f"{k}={_short(v)}" for k, v in sorted(payload.items()))
        self._stream.write(f"[{kind}] {detail}\n")
        self._stream.flush()

    def close(self) -> None:
        return None


class MultiLogger:
    """Fan-out to several sinks. A failing sink must not abort a run."""

    def __init__(self, sinks: Sequence[Any]) -> None:
        self._sinks: List[Any] = list(sinks)

    def event(self, kind: str, payload: Mapping[str, Any]) -> None:
        for sink in self._sinks:
            try:
                sink.event(kind, payload)
            except Exception:  # noqa: BLE001 — logging must never break a run
                pass

    def close(self) -> None:
        for sink in self._sinks:
            try:
                sink.close()
            except Exception:  # noqa: BLE001
                pass


class NullLogger:
    """Discards everything. Default in tests, so test output stays readable."""

    def event(self, kind: str, payload: Mapping[str, Any]) -> None:
        return None

    def close(self) -> None:
        return None


@LOGGERS.register("jsonl")
def _jsonl(path: str) -> JsonlLogger:
    return JsonlLogger(path)


@LOGGERS.register("console")
def _console(level: str = "info") -> ConsoleLogger:
    return ConsoleLogger(level=level)


@LOGGERS.register("null")
def _null() -> NullLogger:
    return NullLogger()


def _jsonable(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Coerce values JSON cannot represent, so a log write can never raise."""
    out: Dict[str, Any] = {}
    for key, value in payload.items():
        try:
            json.dumps(value)
            out[key] = value
        except (TypeError, ValueError):
            out[key] = repr(value)
    return out


def _short(value: Any, width: int = 60) -> str:
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    return text if len(text) <= width else text[: width - 3] + "..."
