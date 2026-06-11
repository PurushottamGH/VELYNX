from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGRESSION_DIR: Path = Path("data") / "regressions"
HEALTH_LOG_PATH: Path = Path("data") / "system_health.json"
FAILURE_WINDOW_SECONDS: int = 10 * 60
MAX_FAILURES_PER_WINDOW: int = 3
MAX_HEALTH_EVENTS: int = 20


class HealthSentinel:
    def __init__(
        self,
        regression_dir: Path | str | None = None,
        health_log_path: Path | str | None = None,
        failure_window_seconds: int = FAILURE_WINDOW_SECONDS,
        max_failures_per_window: int = MAX_FAILURES_PER_WINDOW,
        max_health_events: int = MAX_HEALTH_EVENTS,
    ) -> None:
        self._regression_dir = Path(
            regression_dir if regression_dir is not None else REGRESSION_DIR
        )
        self._health_log_path = Path(
            health_log_path if health_log_path is not None else HEALTH_LOG_PATH
        )
        self._failure_window_seconds = failure_window_seconds
        self._max_failures_per_window = max_failures_per_window
        self._max_health_events = max_health_events
        self._health_buffer: list[dict[str, Any]] = []
        self._load_health_log()

    def check_failure_rate(self, file_path: str) -> dict[str, Any]:
        target = Path(file_path).resolve()
        safe_name = target.name
        now = time.time()
        cutoff = now - self._failure_window_seconds
        count = 0

        if not self._regression_dir.exists():
            return {"status": "OK", "message": "No regression data found."}

        try:
            for entry in self._regression_dir.iterdir():
                if not entry.is_file():
                    continue
                if safe_name not in entry.name:
                    continue
                if ".pre_patch" not in entry.name:
                    continue
                try:
                    mtime = entry.stat().st_mtime
                except OSError:
                    continue
                if mtime >= cutoff:
                    count += 1
        except OSError as exc:
            return {
                "status": "ERROR",
                "message": f"Could not scan regression dir: {exc}",
            }

        if count > self._max_failures_per_window:
            return {
                "status": "CRITICAL",
                "message": (
                    f"High failure rate detected for {safe_name}: "
                    f"{count} patches in the last "
                    f"{self._failure_window_seconds // 60} minutes. "
                    f"Manual intervention required."
                ),
            }

        return {
            "status": "OK",
            "message": f"Failure rate normal: {count} patches in window.",
        }

    def log_event(self, event_type: str, status: str) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "event_type": event_type,
            "status": status,
        }
        self._health_buffer.append(event)
        if len(self._health_buffer) > self._max_health_events:
            self._health_buffer = self._health_buffer[
                -self._max_health_events :
            ]
        self._persist_health_log()

    def is_system_stable(self) -> bool:
        for event in self._health_buffer:
            if event.get("status") == "CRITICAL":
                return False
        return True

    def _load_health_log(self) -> None:
        if not self._health_log_path.exists():
            return
        try:
            raw = self._health_log_path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if isinstance(data, list):
                self._health_buffer = data[-self._max_health_events :]
        except (json.JSONDecodeError, OSError):
            self._health_buffer = []

    def _persist_health_log(self) -> None:
        try:
            self._health_log_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._health_log_path.with_suffix(
                self._health_log_path.suffix + ".tmp"
            )
            payload = json.dumps(
                self._health_buffer, indent=2, ensure_ascii=False
            )
            with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(payload)
                fh.flush()
            os.replace(tmp, self._health_log_path)
        except OSError:
            pass
