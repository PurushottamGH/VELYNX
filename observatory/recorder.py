"""Tier A ingestion: rebuild an event stream from a run directory.

Responsibility: read what the engine already wrote and present it as an `ObsEvent`
stream, so the Observatory can inspect any run -- past, present, or someone else's --
without the engine knowing the Observatory exists.

This is the path with zero interference risk, and it is deliberately the first thing
built. It also stays the audit path forever: the engine's own artifacts are the
canonical scientific record (`manifest.json`, `steps.csv`, `probes.csv`, `run.log`,
plus the hash inventory), and a reader that depends only on them cannot be fooled by
a bug in the live tap.

Files consumed, all written by `experiments.engine.artifacts.ArtifactWriter`:

    manifest.json   run identity, config, seeds, components, status
    run.log         JSONL lifecycle events ({"event": kind, ...})
    steps.csv       t, task, loss, replays, gate_fired, buffer_size, updates
    steps.jsonl     same records, when `logging.step_format == "jsonl"`
    probes.csv      probe matrix in long form

Ordering rule: lifecycle start first, then every step-indexed event by `t` (step
before probe at the same `t`, which is the engine's own order in `_execute`), then
terminal lifecycle events. `seq` is assigned during this walk, so a Tier A stream is
gapless by construction.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Tuple

from observatory.schema import ObsEvent

#: Terminal lifecycle kinds, emitted after all step-indexed events.
_TERMINAL = ("truncated", "error", "run_end")

#: Sort key within one `t`: the engine writes the step, then the probe.
_ORDER = {"step": 0, "probe": 1}


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _coerce(value: str) -> Any:
    """CSV is untyped. Recover int, float, bool; otherwise keep the string."""
    text = value.strip()
    if text == "":
        return None
    low = text.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


class RunReader:
    """Read-only view of one engine run directory."""

    def __init__(self, run_dir: str | Path) -> None:
        self.run_dir = Path(run_dir)
        if not self.run_dir.is_dir():
            raise FileNotFoundError(f"not a run directory: {self.run_dir}")

    # ---------------------------------------------------------------- metadata
    def manifest(self) -> Dict[str, Any]:
        return _read_json(self.run_dir / "manifest.json")

    def status(self) -> Dict[str, Any]:
        return _read_json(self.run_dir / "status.json")

    def metrics(self) -> Dict[str, Any]:
        return _read_json(self.run_dir / "metrics.json")

    @property
    def run_id(self) -> str:
        manifest = self.manifest()
        if manifest.get("run_id"):
            return str(manifest["run_id"])
        status = self.status()
        return str(status.get("run_id") or self.run_dir.name)

    # ------------------------------------------------------------------ tables
    def lifecycle(self) -> List[Tuple[str, Dict[str, Any]]]:
        """Events from `run.log`, in file order."""
        path = self.run_dir / "run.log"
        out: List[Tuple[str, Dict[str, Any]]] = []
        if not path.is_file():
            return out
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return out
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                # A torn final line is expected while a run is still writing.
                continue
            if not isinstance(raw, Mapping) or "event" not in raw:
                continue
            payload = {k: v for k, v in raw.items() if k != "event"}
            out.append((str(raw["event"]), payload))
        return out

    def steps(self) -> Iterator[Dict[str, Any]]:
        """Per-step records from `steps.csv` or `steps.jsonl`."""
        csv_path = self.run_dir / "steps.csv"
        jsonl_path = self.run_dir / "steps.jsonl"
        if csv_path.is_file():
            yield from self._iter_csv(csv_path)
        elif jsonl_path.is_file():
            yield from self._iter_jsonl(jsonl_path)

    def probes(self) -> Iterator[Dict[str, Any]]:
        path = self.run_dir / "probes.csv"
        if path.is_file():
            yield from self._iter_csv(path)

    @staticmethod
    def _iter_csv(path: Path) -> Iterator[Dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    yield {k: _coerce(v if v is not None else "") for k, v in row.items() if k}
        except OSError:
            return

    @staticmethod
    def _iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(row, Mapping):
                        yield dict(row)
        except OSError:
            return

    # ------------------------------------------------------------------ stream
    def events(self, step_stride: int = 1) -> Iterator[ObsEvent]:
        """The reconstructed event stream. `seq` is assigned here, gaplessly."""
        stride = max(1, int(step_stride))
        lifecycle = self.lifecycle()
        seq = 0

        for kind, payload in lifecycle:
            if kind == "run_start":
                yield ObsEvent(seq=seq, kind="run_start", t=None, p=dict(payload))
                seq += 1

        indexed: List[Tuple[int, int, str, Dict[str, Any]]] = []
        for row in self.steps():
            t = row.get("t")
            if not isinstance(t, int):
                continue
            gate_fired = bool(row.get("gate_fired"))
            if not gate_fired and (t % stride) != 0:
                continue
            payload = {k: v for k, v in row.items() if k != "t"}
            indexed.append((t, _ORDER["step"], "step", payload))
        for row in self.probes():
            t = row.get("t") if isinstance(row.get("t"), int) else row.get("step")
            if not isinstance(t, int):
                continue
            payload = {k: v for k, v in row.items() if k != "t"}
            indexed.append((t, _ORDER["probe"], "probe", payload))
        for kind, payload in lifecycle:
            if kind != "probe":
                continue
            t = payload.get("step")
            if isinstance(t, int):
                indexed.append((t, _ORDER["probe"], "probe", dict(payload)))

        indexed.sort(key=lambda item: (item[0], item[1]))
        seen_probe: set[Tuple[int, str]] = set()
        for t, _order, kind, payload in indexed:
            if kind == "probe":
                # `probes.csv` and `run.log` both record probes; keep one per step.
                key = (t, "probe")
                if key in seen_probe:
                    continue
                seen_probe.add(key)
            yield ObsEvent(seq=seq, kind=kind, t=t, p=payload)
            seq += 1

        for kind, payload in lifecycle:
            if kind in _TERMINAL:
                yield ObsEvent(seq=seq, kind=kind, t=None, p=dict(payload))
                seq += 1


def discover_runs(root: str | Path) -> List[Path]:
    """Every run directory under `root`, identified by a `status.json`.

    Detection is by marker file rather than by depth, because the artifact layout is
    `<root>/<experiment>/<run_id>/` today and must be free to change.
    """
    base = Path(root)
    if not base.is_dir():
        return []
    return sorted({p.parent for p in base.rglob("status.json")})
