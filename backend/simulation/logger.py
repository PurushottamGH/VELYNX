"""
VELYNX Phase 63 — CausalLogger
==============================

Securely persists ``CounterfactualEvaluator`` results (``CausalDelta``) to an
append-only **JSON Lines** ledger for audit, replay, and downstream analysis.

The telemetry layer lives at the very edge of the simulation subsystem. Its one
job is *clean, safe I/O*: take a ``CausalDelta``, normalize it to JSON, and
write exactly one well-formed line to the ledger — atomically and
thread-safely — even when many counterfactual evaluations are running
concurrently.

Design
------
* **Structural typing, not imports.** The logger accepts any object that looks
  like a ``CausalDelta``. It never imports ``causal_evaluator``,
  ``reasoning_engine``, ``simulation_memory_context``, pydantic, or any database
  driver. This keeps the telemetry layer trivially unit-testable and impossible
  to entangle with pipeline lifecycles.
* **Robust serialization.** A recursive normalizer (``_to_jsonable``) handles
  dataclasses, enums, datetimes, ``Decimal``, ``UUID``, ``Path``, ``bytes``,
  sets/tuples, objects exposing ``to_dict()`` / ``model_dump()`` / ``as_tuple()``,
  and degrades gracefully to ``repr`` for anything else — it never raises.
* **Atomic, concurrent-safe appends.** A reentrant process lock serializes
  writes; the ledger is opened in append-binary mode (``O_APPEND``); every
  record is emitted as a single ``write()`` of ``line + "\\n"`` followed by
  ``flush`` + ``fsync``. No torn lines, no interleaving.
* **Self-healing.** If anything unexpected goes wrong mid-write, a tombstone
  record is appended so the event is never silently lost — and the caller is
  never crashed (unless ``strict=True``).

Ledger record shape
-------------------
::

    {
      "schema": "velynx.causal-delta/v1",
      "seq": 42,                       # monotonic per-logger sequence
      "ts": "2026-06-24T18:03:11.482341Z",
      "host": "workstation",           # platform.getnode() tag
      "pid": 12345,
      "payload": { ...full CausalDelta... },
      "extra": { "run_id": "...", ... }  # caller-supplied tags, optional
    }

Usage
-----
::

    from backend.simulation.logger import CausalLogger

    with CausalLogger() as ledger:           # default ledger path
        ledger.log(delta, extra={"run_id": "ab12"})

    # Async callers stay non-blocking:
    await ledger.alog(delta)

    # Replay for analysis:
    for record in CausalLogger.iter_records():
        ...

Strict isolation contract
-------------------------
This module imports **only** the Python standard library. Do not add imports
from ``backend.*`` or any third-party package.
"""

from __future__ import annotations

import base64
import dataclasses
import decimal
import enum
import json
import logging
import os
import platform
import threading
import uuid
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from types import TracebackType
from typing import Any, Dict, Iterator, List, Optional, Protocol, Set, Type, Union, runtime_checkable

__all__ = [
    "CausalLogger",
    "CausalDeltaLike",
    "DEFAULT_LEDGER_PATH",
    "LedgerError",
]

logger = logging.getLogger("velynx.simulation.logger")

# Schema stamp embedded in every record. Bump if the envelope shape changes
# in a backwards-incompatible way so readers can branch on it.
_LEDGER_SCHEMA = "velynx.causal-delta/v1"

# Default ledger location, resolved relative to *this* module so it is
# independent of the process's current working directory.
DEFAULT_LEDGER_PATH: Path = (
    Path(__file__).resolve().parent / "logs" / "counterfactual_ledger.jsonl"
)


# ══════════════════════════════════════════════════════════════════════════════
# Errors
# ══════════════════════════════════════════════════════════════════════════════


class LedgerError(RuntimeError):
    """Raised when the ledger cannot be written and ``strict=True``.

    In the default (non-strict) mode, write failures are logged and a
    tombstone record is appended instead of raising — the simulation that
    produced the delta must never be perturbed by a telemetry fault.
    """


# ══════════════════════════════════════════════════════════════════════════════
# Structural type — documents what the logger accepts without importing it
# ══════════════════════════════════════════════════════════════════════════════


@runtime_checkable
class CausalDeltaLike(Protocol):
    """Structural shape of a ``CausalDelta``.

    The real ``CausalDelta`` lives in :mod:`backend.simulation.causal_evaluator`
    and transitively imports the cognition + simulation stack. To preserve the
    strict isolation of this module, we accept it *structurally*: any object
    exposing these attributes serializes correctly. The Protocol is for
    documentation and static analysis only — it is never used to type-check at
    runtime.
    """

    answer_flipped: bool
    confidence_delta: float


# ══════════════════════════════════════════════════════════════════════════════
# Robust serializer — turns arbitrary Python into JSON-safe structures
# ══════════════════════════════════════════════════════════════════════════════

# Sentinel inserted in place of values that cannot be faithfully serialized,
# so the ledger always stays parseable.
_UNSERIALIZABLE = "<<unserializable>>"


def _to_jsonable(obj: Any, _seen: Optional[Set[int]] = None) -> Any:
    """Recursively normalize *obj* into a structure ``json.dumps`` accepts.

    The function is total: for every input it returns *something* JSON-safe.
    Unknown types fall back to ``repr`` rather than raising, so a single
    surprising field can never corrupt or abort a ledger write.

    Handles (in order of specificity):

    * primitives (``None``, ``bool``, ``int``, ``float``, ``str``)
    * non-finite floats (``NaN`` / ``±Infinity``) → faithful string form
    * ``bytes`` / ``bytearray`` → base64 ASCII
    * ``decimal.Decimal`` → string (preserves precision)
    * ``complex`` → ``{"real", "imag"}``
    * ``datetime`` / ``date`` / ``time`` → ISO 8601 string
    * ``timedelta`` → ISO 8601 duration string
    * ``enum.Enum`` → ``.value`` (recurse; fall back to ``.name``)
    * ``pathlib.Path`` / ``uuid.UUID`` → ``str``
    * dataclasses → dict of public fields
    * mappings / dict-likes → dict of recursed items
    * ``list`` / ``tuple`` / ``set`` / ``frozenset`` → list of recursed items
    * objects with ``to_dict()`` / ``model_dump()`` / ``dict()`` /
      ``as_tuple()`` → recurse the result
    * arbitrary objects → their public ``__dict__``, else ``repr``
    * reference cycles → ``"<<cycle>>"`` marker
    """
    # ── Primitives (json-native) ────────────────────────────────────────────
    if obj is None or isinstance(obj, (bool, str)):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        # json.dumps(allow_nan=False) rejects these; emit faithful strings so
        # the ledger stays valid JSON without losing information.
        if obj != obj:  # NaN
            return "NaN"
        if obj == float("inf"):
            return "Infinity"
        if obj == float("-inf"):
            return "-Infinity"
        return obj

    # ── Cycle guard for containers / compound objects ───────────────────────
    if _seen is None:
        _seen = set()
    obj_id = id(obj)
    try:
        hashable = obj_id
    except TypeError:  # pragma: no cover — id() is always hashable
        hashable = None
    if hashable in _seen:
        return "<<cycle>>"

    # ── Scalars with a known good string form ───────────────────────────────
    if isinstance(obj, (bytes, bytearray)):
        return base64.b64encode(bytes(obj)).decode("ascii")
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}

    # ── Temporal types ──────────────────────────────────────────────────────
    if isinstance(obj, datetime):
        # Collapse +00:00 to Z for a tidy, conventional UTC stamp.
        iso = obj.isoformat()
        return iso.replace("+00:00", "Z") if obj.utcoffset() == timedelta(0) else iso
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        try:
            return obj.isoformat()  # Python 3.11+
        except AttributeError:  # pragma: no cover
            return str(obj)

    # ── Enums ───────────────────────────────────────────────────────────────
    if isinstance(obj, enum.Enum):
        try:
            return _to_jsonable(obj.value, _seen)
        except Exception:
            return obj.name

    # ── Other value-objects with a string form ──────────────────────────────
    if isinstance(obj, (uuid.UUID, Path)):
        return str(obj)

    # ── Dataclasses (Fact, Contradiction, ReasoningTrace, CausalDelta…) ─────
    #    Checked before the generic attribute probes below so we serialize
    #    *every* declared field faithfully rather than a lossy helper view.
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        _seen.add(obj_id)
        try:
            return {
                f.name: _to_jsonable(getattr(obj, f.name), _seen)
                for f in dataclasses.fields(obj)
            }
        finally:
            _seen.discard(obj_id)

    # ── Containers ──────────────────────────────────────────────────────────
    if isinstance(obj, dict):
        _seen.add(obj_id)
        try:
            return {
                (k if isinstance(k, str) else _to_jsonable(k, _seen)):
                _to_jsonable(v, _seen)
                for k, v in obj.items()
            }
        finally:
            _seen.discard(obj_id)
    if isinstance(obj, (list, tuple, set, frozenset)):
        _seen.add(obj_id)
        try:
            return [_to_jsonable(item, _seen) for item in obj]
        finally:
            _seen.discard(obj_id)

    # ── Duck-typed serialization helpers (pydantic, Fact.as_tuple, …) ───────
    for method in ("to_dict", "model_dump", "dict"):
        fn = getattr(obj, method, None)
        if callable(fn):
            try:
                _seen.add(obj_id)
                try:
                    return _to_jsonable(fn(), _seen)
                finally:
                    _seen.discard(obj_id)
            except Exception:  # noqa: BLE001 — never let a helper raise
                continue
    as_tuple = getattr(obj, "as_tuple", None)
    if callable(as_tuple):
        _seen.add(obj_id)
        try:
            return _to_jsonable(list(as_tuple()), _seen)
        except Exception:  # noqa: BLE001
            _seen.discard(obj_id)

    # ── Last resort: instance namespace, then repr ──────────────────────────
    obj_dict = getattr(obj, "__dict__", None)
    if isinstance(obj_dict, dict) and obj_dict:
        _seen.add(obj_id)
        try:
            return {
                k: _to_jsonable(v, _seen)
                for k, v in obj_dict.items()
                if not k.startswith("_")
            }
        finally:
            _seen.discard(obj_id)

    try:
        return repr(obj)
    except Exception:  # pragma: no cover — repr basically never fails
        return _UNSERIALIZABLE


def _dumps(obj: Any) -> str:
    """Serialize *obj* to a single-line JSON string.

    ``ensure_ascii=False`` keeps human-readable Unicode in the ledger;
    ``allow_nan=False`` forces non-finite floats through ``_to_jsonable``'s
    faithful string mapping rather than emitting invalid JSON tokens. The
    output never contains a raw newline, so each record is exactly one line.
    """
    return json.dumps(
        _to_jsonable(obj),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=False,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CausalLogger
# ══════════════════════════════════════════════════════════════════════════════


class CausalLogger:
    """Thread-safe, atomic JSON Lines writer for ``CausalDelta`` results.

    A single ``CausalLogger`` instance is intended to be **shared** across all
    concurrent simulation evaluations in a process (e.g. as a singleton or via
    the context-manager form). Internally it serializes every append behind a
    reentrant lock, so it is safe to call :meth:`log` from many threads — and
    from asynchronous code via :meth:`alog`.

    Parameters
    ----------
    ledger_path
        Destination ``.jsonl`` file. Defaults to
        :data:`DEFAULT_LEDGER_PATH`. Parent directories are created lazily.
    append
        ``True`` (default) opens the ledger in append mode, preserving prior
        records. ``False`` truncates the file on first write — useful for tests.
    fsync
        ``True`` (default) calls ``os.fsync`` after every record so the line
        reaches durable storage before the call returns. Set ``False`` for
        high-throughput batch runs where you accept losing the tail on crash.
    strict
        ``False`` (default) swallows write errors after logging them and
        appending a tombstone, so a telemetry fault can never crash a
        simulation. ``True`` raises :class:`LedgerError` instead — useful in
        tests where silent data loss would hide bugs.
    include_traces
        ``True`` (default) serializes the full ``baseline_trace`` /
        ``simulated_trace`` objects. Set ``False`` to omit them (mirroring
        ``CausalDelta.to_dict``) for compact, high-volume ledgers.

    Concurrency model
    -----------------
    *In-process* concurrency (threads / asyncio tasks in one worker) is fully
    serialized by an ``RLock`` — this is the primary guarantee and is
    sufficient for VELYNX's evaluation model. *Cross-process* writes to the
    same ledger file are not locked here; if you run multiple worker
    processes, point each at its own ledger (e.g. suffixed by PID) and merge
    offline, or wrap the shared path in an external coordinator.
    """

    # ── Construction / lifecycle ────────────────────────────────────────────

    def __init__(
        self,
        ledger_path: Union[str, os.PathLike, None] = None,
        *,
        append: bool = True,
        fsync: bool = True,
        strict: bool = False,
        include_traces: bool = True,
    ) -> None:
        self._path: Path = Path(ledger_path) if ledger_path else DEFAULT_LEDGER_PATH
        self._append: bool = bool(append)
        self._fsync: bool = bool(fsync)
        self._strict: bool = bool(strict)
        self._include_traces: bool = bool(include_traces)

        # Reentrant so log() is safe even if a subclass re-enters internally.
        self._lock = threading.RLock()
        self._fh = None  # type: ignore[assignment]  # opened lazily
        self._closed = False

        # Monotonic per-instance sequence, incremented under the lock.
        self._seq = 0

        # Stable host tag, captured once (never raises — falls back to "").
        try:
            self._host = platform.node() or "unknown"
        except Exception:  # pragma: no cover
            self._host = "unknown"
        self._pid = os.getpid()

        self._ensure_dir()

    # Context-manager support: `with CausalLogger() as ledger: ...`
    def __enter__(self) -> "CausalLogger":
        self._open()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()

    # ── Public API ──────────────────────────────────────────────────────────

    def log(
        self,
        delta: CausalDeltaLike,
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """Serialize *delta* and append it as one atomic ledger line.

        Parameters
        ----------
        delta
            A ``CausalDelta`` (or any structurally compatible object).
        extra
            Optional caller-supplied metadata merged into the record's
            ``extra`` field (e.g. ``run_id``, ``evaluator_version``).
            It is normalized through the same robust serializer.

        Returns
        -------
        int or None
            The record's sequence number on success, or ``None`` if a
            non-strict write failed (in which case a tombstone was appended
            and the error was logged).
        """
        if self._closed:
            raise LedgerError("CausalLogger is closed — create a new instance.")

        record, seq = self._build_record(delta, extra)
        line = _dumps(record)
        ok = self._write_line(line)
        if not ok:
            if self._strict:
                raise LedgerError(
                    f"Failed to append CausalDelta record seq={seq} to {self._path}"
                )
            return None
        return seq

    async def alog(
        self,
        delta: CausalDeltaLike,
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """Async-friendly wrapper around :meth:`log`.

        Runs the (blocking, fsync'd) append in a worker thread so the event
        loop is never stalled by disk I/O. Stdlib only — uses
        ``asyncio.to_thread`` under the hood.
        """
        import asyncio

        return await asyncio.to_thread(self.log, delta, extra=extra)

    def log_many(
        self,
        deltas: List[CausalDeltaLike],
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> List[Optional[int]]:
        """Append a batch of deltas under a single lock acquisition.

        Each delta still becomes its own line (JSONL invariant), but the lock
        is taken once for the whole batch, reducing contention versus calling
        :meth:`log` in a tight loop. ``fsync`` is applied per record so a crash
        mid-batch preserves everything written so far.
        """
        results: List[Optional[int]] = []
        with self._lock:
            for delta in deltas:
                results.append(self.log(delta, extra=extra))
        return results

    def close(self) -> None:
        """Flush and close the underlying file handle. Idempotent."""
        with self._lock:
            if self._fh is not None:
                try:
                    self._fh.flush()
                    if self._fsync:
                        try:
                            os.fsync(self._fh.fileno())
                        except OSError:
                            pass
                finally:
                    try:
                        self._fh.close()
                    except Exception:  # noqa: BLE001
                        pass
                    self._fh = None
            self._closed = True

    # ── Read path (for replay / audit) ──────────────────────────────────────

    @classmethod
    def iter_records(
        cls,
        ledger_path: Union[str, os.PathLike, None] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Yield parsed ledger records, one dict per non-blank line.

        Robust to partial/corrupt lines: a line that fails to parse is skipped
        with a warning rather than aborting iteration, so audit tooling can
        always recover the surviving history.
        """
        path = Path(ledger_path) if ledger_path else DEFAULT_LEDGER_PATH
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as fh:
            for lineno, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    logger.warning(
                        "Skipping corrupt ledger line %d in %s: %s",
                        lineno, path, exc,
                    )
                    continue
                if isinstance(record, dict):
                    yield record

    # ── Internals ───────────────────────────────────────────────────────────

    def _ensure_dir(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            # Directory creation is the one setup step that can legitimately
            # fail (permissions, read-only FS). In strict mode surface it;
            # otherwise defer the error to the first write, which is itself
            # tolerant when strict=False.
            if self._strict:
                raise LedgerError(
                    f"Cannot create ledger directory {self._path.parent}: {exc}"
                ) from exc
            logger.warning("Could not create ledger dir %s: %s", self._path.parent, exc)

    def _open(self) -> None:
        """Open (or reopen) the ledger file handle under the lock."""
        with self._lock:
            if self._fh is not None:
                return
            mode = "ab" if self._append else "wb"
            try:
                self._fh = open(self._path, mode, buffering=0)
            except OSError as exc:
                if self._strict:
                    raise LedgerError(
                        f"Cannot open ledger {self._path}: {exc}"
                    ) from exc
                logger.error("Cannot open ledger %s: %s — writes will be dropped", self._path, exc)
                self._fh = None

    def _write_line(self, line: str) -> bool:
        """Append a single line atomically. Returns ``True`` on success."""
        data = (line + "\n").encode("utf-8")
        with self._lock:
            if self._fh is None:
                self._open()
            fh = self._fh
            if fh is None:
                # Open failed and strict=False; drop but record it.
                logger.error(
                    "Ledger %s unavailable — dropping %d-byte record", self._path, len(data),
                )
                return False
            try:
                fh.write(data)
                fh.flush()
                if self._fsync:
                    try:
                        os.fsync(fh.fileno())
                    except OSError as exc:
                        # fsync can fail on some FS / network drives; the data
                        # is still in the OS cache, so treat as soft failure.
                        logger.debug("fsync failed on %s: %s", self._path, exc)
                return True
            except OSError as exc:
                logger.error(
                    "Write failed on ledger %s: %s — attempting tombstone", self._path, exc,
                )
                self._write_tombstone(line, exc)
                return False

    def _write_tombstone(self, original_line: str, exc: BaseException) -> None:
        """Best-effort fallback: record that a write failed.

        The original line is base64-embedded so no data is silently lost even
        when the primary write path errors. Tombstone writes are deliberately
        unguarded against further failure — if *this* also breaks, there is
        nothing more the logger can do except shout into the log.
        """
        tombstone = {
            "schema": _LEDGER_SCHEMA,
            "kind": "tombstone",
            "ts": _utc_now_iso(),
            "host": self._host,
            "pid": self._pid,
            "error": f"{type(exc).__name__}: {exc}",
            "original_b64": base64.b64encode(original_line.encode("utf-8")).decode("ascii"),
        }
        try:
            payload = (_dumps(tombstone) + "\n").encode("utf-8")
            # Reopen transiently in append mode; do not disturb self._fh.
            with open(self._path, "ab") as tmp:
                tmp.write(payload)
                tmp.flush()
                try:
                    os.fsync(tmp.fileno())
                except OSError:
                    pass
        except OSError as final_exc:
            logger.critical(
                "Could not write tombstone to %s: %s — record LOST.",
                self._path, final_exc,
            )

    def _build_record(
        self,
        delta: CausalDeltaLike,
        extra: Optional[Dict[str, Any]],
    ) -> "tuple[Dict[str, Any], int]":
        """Assemble the full envelope dict and reserve a sequence number."""
        with self._lock:
            self._seq += 1
            seq = self._seq

        payload = _to_jsonable(delta)
        if not self._include_traces and isinstance(payload, dict):
            payload = {
                k: v for k, v in payload.items()
                if k not in ("baseline_trace", "simulated_trace")
            }

        record: Dict[str, Any] = {
            "schema": _LEDGER_SCHEMA,
            "seq": seq,
            "ts": _utc_now_iso(),
            "host": self._host,
            "pid": self._pid,
            "payload": payload,
        }
        if extra:
            record["extra"] = _to_jsonable(extra)
        return record, seq


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════


def _utc_now_iso() -> str:
    """Current UTC time as a tidy ISO 8601 stamp ending in ``Z``."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
