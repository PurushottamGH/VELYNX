"""Artifact pipeline: everything a run leaves behind.

Responsibility: own the on-disk layout of a run and write every file in it. No
other module touches the filesystem for results, so the layout can be changed in
one place.

Layout, one directory per run:

    <root>/<experiment>/<run_id>/
        config.yaml       exact configuration snapshot (re-runnable as-is)
        manifest.json     provenance: git, runtime, seeds, timing, compute
        metrics.json      every metric's result, keyed by metric name
        steps.csv         per-step records (or steps.jsonl, or omitted)
        probes.csv        probe matrix in long form, with oracle and excess
        plots/*.png       online loss and retention curves
        run.log           JSON-lines event log
        status.json       lifecycle state, read by the scheduler to resume
        inventory.json    size and SHA-256 of every artifact

Two decisions worth stating:

  * **Step records stream to disk.** They are written as they are produced and
    never accumulated in a list, so a 32,000-step run costs constant memory and a
    scheduler can hold hundreds of runs.
  * **`status.json` is written before and after execution.** A crashed run leaves
    `running`, which is how resume distinguishes "finished" from "interrupted"
    without guessing from file presence.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, TextIO

from core.types import ProbeRecord, RunStatus, StepRecord
from experiments.engine.manifest import utc_now

STEP_FIELDS = ("t", "task", "loss", "replays", "gate_fired", "buffer_size", "updates")

#: Target number of points kept in memory for plotting. A 32,000-step run is
#: decimated to this many buckets, which is more than a plot can resolve anyway.
_PLOT_POINTS = 1500


class ArtifactWriter:
    """Writes one run directory. Not reusable across runs, by design."""

    def __init__(self, run_dir: str | Path, step_format: str = "csv") -> None:
        self.run_dir = Path(run_dir)
        self.step_format = step_format
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._steps_fh: Optional[TextIO] = None
        self._steps_writer: Any = None
        self._probes: List[ProbeRecord] = []
        # Decimated loss series for plotting, plus the task-switch positions.
        self._bucket_size = 1
        self._bucket_sum = 0.0
        self._bucket_n = 0
        self._loss_points: List[tuple[int, float]] = []
        self._switches: List[int] = []
        self._last_task: Optional[int] = None

    # ------------------------------------------------------------- lifecycle
    def start(self, total_steps: int) -> None:
        self._bucket_size = max(1, total_steps // _PLOT_POINTS)
        if self.step_format == "none":
            return
        name = "steps.csv" if self.step_format == "csv" else "steps.jsonl"
        self._steps_fh = (self.run_dir / name).open("w", encoding="utf-8", newline="")
        if self.step_format == "csv":
            self._steps_writer = csv.writer(self._steps_fh)
            self._steps_writer.writerow(STEP_FIELDS)

    def write_step(self, rec: StepRecord) -> None:
        if self._steps_fh is not None:
            if self.step_format == "csv":
                self._steps_writer.writerow(
                    [
                        rec.t,
                        rec.task,
                        rec.loss,
                        rec.replays,
                        int(rec.gate_fired),
                        rec.buffer_size,
                        rec.updates,
                    ]
                )
            else:
                self._steps_fh.write(json.dumps(rec.as_dict()) + "\n")

        if rec.task != self._last_task:
            if self._last_task is not None:
                self._switches.append(rec.t)
            self._last_task = rec.task

        self._bucket_sum += rec.loss
        self._bucket_n += 1
        if self._bucket_n >= self._bucket_size:
            self._loss_points.append((rec.t, self._bucket_sum / self._bucket_n))
            self._bucket_sum = 0.0
            self._bucket_n = 0

    def write_probe(self, rec: ProbeRecord) -> None:
        self._probes.append(rec)

    def finish_steps(self) -> None:
        if self._bucket_n:
            last_t = (
                self._loss_points[-1][0] + self._bucket_n if self._loss_points else self._bucket_n
            )
            self._loss_points.append((last_t, self._bucket_sum / self._bucket_n))
            self._bucket_sum = 0.0
            self._bucket_n = 0
        if self._steps_fh is not None:
            self._steps_fh.close()
            self._steps_fh = None

    # ----------------------------------------------------------------- files
    def write_config(self, config_yaml: str) -> None:
        (self.run_dir / "config.yaml").write_text(config_yaml, encoding="utf-8")

    def write_json(self, name: str, payload: Any) -> Path:
        path = self.run_dir / name
        path.write_text(
            json.dumps(sanitise(payload), indent=2, sort_keys=True, default=_fallback),
            encoding="utf-8",
        )
        return path

    def write_status(
        self,
        status: RunStatus,
        config_hash: str,
        run_id: str,
        error: str = "",
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        payload = {
            "status": status.value,
            "run_id": run_id,
            "config_hash": config_hash,
            "updated_at": utc_now(),
            "error": error,
        }
        payload.update(dict(extra or {}))
        self.write_json("status.json", payload)

    def write_probes_csv(self) -> Optional[Path]:
        """Long form: one row per (checkpoint, task). Long rather than wide so a
        varying task count needs no schema change."""
        if not self._probes:
            return None
        path = self.run_dir / "probes.csv"
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["block", "step", "trained_task", "task", "loss", "oracle", "excess"])
            for rec in self._probes:
                excess = rec.excess
                for task, loss in enumerate(rec.losses):
                    writer.writerow(
                        [
                            rec.block,
                            rec.t,
                            rec.trained_task,
                            task,
                            loss,
                            rec.oracle[task] if rec.oracle else "",
                            excess[task] if excess else "",
                        ]
                    )
        return path

    def write_plots(self) -> List[str]:
        """Online-loss and retention figures. Returns the filenames written.

        matplotlib is imported here, not at module level, and with the Agg backend:
        importing it costs ~200 ms, which matters when a sweep launches hundreds of
        runs with plots disabled. A missing matplotlib degrades to "no plots"
        rather than failing a completed run.
        """
        if not self._loss_points and not self._probes:
            return []
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except Exception:  # noqa: BLE001 — plots are never load-bearing
            return []

        plots_dir = self.run_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        written: List[str] = []

        if self._loss_points:
            fig, ax = plt.subplots(figsize=(8, 4))
            xs = [p[0] for p in self._loss_points]
            ys = [p[1] for p in self._loss_points]
            ax.plot(xs, ys, linewidth=1.0)
            for switch in self._switches:
                ax.axvline(switch, color="grey", linestyle=":", linewidth=0.8)
            ax.set_xlabel("step")
            ax.set_ylabel("online loss (nats)")
            ax.set_title("Prequential loss (dotted lines: task switches)")
            fig.tight_layout()
            fig.savefig(plots_dir / "online_loss.png", dpi=120)
            plt.close(fig)
            written.append("plots/online_loss.png")

        if self._probes:
            fig, ax = plt.subplots(figsize=(8, 4))
            n_tasks = len(self._probes[0].losses)
            blocks = [rec.block for rec in self._probes]
            use_excess = bool(self._probes[0].oracle)
            for task in range(n_tasks):
                series = [
                    (rec.excess[task] if use_excess else rec.losses[task]) for rec in self._probes
                ]
                ax.plot(blocks, series, marker="o", markersize=3, label=f"task {task}")
            ax.set_xlabel("checkpoint (block)")
            ax.set_ylabel("excess loss (nats)" if use_excess else "loss (nats)")
            ax.set_title("Per-task probe loss after each block")
            ax.legend(fontsize="small", ncol=2)
            fig.tight_layout()
            fig.savefig(plots_dir / "retention.png", dpi=120)
            plt.close(fig)
            written.append("plots/retention.png")

        return written

    def write_inventory(self) -> Path:
        """Size and SHA-256 of every file in the run directory.

        Makes tampering and truncation detectable after the fact, which the M0
        review's artifact-preservation requirement needs. `inventory.json` itself
        is excluded, since it cannot contain its own hash.
        """
        entries: Dict[str, Any] = {}
        for path in sorted(self.run_dir.rglob("*")):
            if not path.is_file() or path.name == "inventory.json":
                continue
            digest = hashlib.sha256()
            with path.open("rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    digest.update(chunk)
            entries[path.relative_to(self.run_dir).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
        return self.write_json("inventory.json", {"generated_at": utc_now(), "files": entries})


# --------------------------------------------------------------------------- #
# Resume support
# --------------------------------------------------------------------------- #


def read_status(run_dir: str | Path) -> Optional[Dict[str, Any]]:
    """Parse `status.json`, or None if absent or unreadable."""
    path = Path(run_dir) / "status.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def is_complete(run_dir: str | Path, config_hash: str) -> bool:
    """True only for a completed run of *this* configuration.

    The hash check matters: a run directory whose config changed is not a
    completed run of the new config, and skipping it would silently report stale
    numbers.
    """
    status = read_status(run_dir)
    if not status:
        return False
    return (
        status.get("status") == RunStatus.COMPLETED.value
        and status.get("config_hash") == config_hash
    )


def sanitise(payload: Any) -> Any:
    """Replace non-finite floats with None, recursively.

    `json.dumps` emits bare `NaN` and `Infinity`, which are not valid JSON: strict
    parsers (including many R, Java and Go readers) reject the file outright, so a
    single un-probed task could make a whole result unreadable.

    NaN is a legitimate value here — a task that was never probed has no loss — so
    it maps to `null` rather than to a number, which would fabricate data. The
    engine applies this to metric results before returning them, so the in-memory
    result and the file on disk always agree.
    """
    if isinstance(payload, float):
        if payload != payload or payload in (float("inf"), float("-inf")):
            return None
        return payload
    if isinstance(payload, Mapping):
        return {key: sanitise(value) for key, value in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [sanitise(item) for item in payload]
    return payload


def _fallback(obj: Any) -> Any:
    """Last-resort JSON encoder: never lose a result to a serialisation error."""
    if isinstance(obj, (set, frozenset, tuple)):
        return list(obj)
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    return repr(obj)


def collect_metrics(root: str | Path) -> List[Dict[str, Any]]:
    """Gather every completed run's metrics under `root`, for cross-run analysis."""
    out: List[Dict[str, Any]] = []
    for status_path in sorted(Path(root).rglob("status.json")):
        run_dir = status_path.parent
        status = read_status(run_dir)
        if not status or status.get("status") != RunStatus.COMPLETED.value:
            continue
        metrics_path = run_dir / "metrics.json"
        manifest_path = run_dir / "manifest.json"
        if not metrics_path.is_file():
            continue
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            manifest = (
                json.loads(manifest_path.read_text(encoding="utf-8"))
                if manifest_path.is_file()
                else {}
            )
        except (OSError, json.JSONDecodeError):
            continue
        out.append(
            {
                "run_dir": str(run_dir),
                "run_id": status.get("run_id", run_dir.name),
                "config_hash": status.get("config_hash", ""),
                "seeds": manifest.get("seeds", {}),
                "config": manifest.get("config", {}),
                "compute": manifest.get("compute", {}),
                "metrics": metrics,
            }
        )
    return out
