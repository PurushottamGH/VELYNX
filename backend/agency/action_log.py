from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_DIR = Path("data")
LOG_PATH = LOG_DIR / "agency_history.json"
SNIPPET_LIMIT = 500
MAX_BACKUPS = 5


class ActionLogger:
    def __init__(self, log_path: Path | str = LOG_PATH) -> None:
        self._log_path = Path(log_path)
        self._log_dir = self._log_path.parent
        self._entry_count = self._count_existing_entries()
        self._ensure_storage()

    def record_action(
        self,
        command: str,
        reason: str,
        approved: bool,
        exit_code: int | None = None,
        output: str | None = None,
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "id": self._next_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(
                timespec="milliseconds"
            ),
            "command": command,
            "reason": reason,
            "approved": bool(approved),
        }
        if approved:
            entry["exit_code"] = exit_code
            entry["output_snippet"] = self._truncate_snippet(output)
        else:
            entry["exit_code"] = None
            entry["output_snippet"] = None

        self._append_entry(entry)
        return entry

    def read_history(self) -> list[dict[str, Any]]:
        if not self._log_path.exists():
            return []
        try:
            data = json.loads(self._log_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(data, list):
            return []
        return data

    def _next_id(self) -> int:
        self._entry_count += 1
        return self._entry_count

    def _count_existing_entries(self) -> int:
        if not self._log_path.exists():
            return 0
        try:
            data = json.loads(self._log_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return 0
        if not isinstance(data, list):
            return 0
        return len(data)

    def _truncate_snippet(self, output: str | None) -> str | None:
        if output is None:
            return None
        if not isinstance(output, str):
            output = str(output)
        if len(output) <= SNIPPET_LIMIT:
            return output
        return "..." + output[-SNIPPET_LIMIT:]

    def _ensure_storage(self) -> None:
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise OSError(
                f"ActionLogger could not create log directory {self._log_dir}: {exc}"
            ) from exc

        if not self._log_path.exists():
            self._atomic_write([])
            return

        try:
            raw = self._log_path.read_text(encoding="utf-8")
        except OSError:
            return

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(
                f"[ActionLogger] Corrupted log detected ({exc.msg} at pos {exc.pos}). "
                f"Backing up to {self._backup_path()} and starting fresh."
            )
            self._rotate_corrupted()
            self._atomic_write([])
            return

        if not isinstance(data, list):
            print(
                "[ActionLogger] Log root is not a list. "
                f"Backing up to {self._backup_path()} and resetting."
            )
            self._rotate_corrupted()
            self._atomic_write([])
            return

        try:
            self._atomic_write(data)
        except OSError:
            pass

    def _rotate_corrupted(self) -> None:
        if not self._log_path.exists():
            return
        backup = self._backup_path()
        try:
            shutil.copy2(self._log_path, backup)
        except OSError as exc:
            print(f"[ActionLogger] Could not create backup: {exc}")
            try:
                self._log_path.unlink()
            except OSError as exc2:
                print(f"[ActionLogger] Could not remove corrupted log: {exc2}")

    def _backup_path(self) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        return self._log_dir / f"agency_history.corrupt.{stamp}.bak"

    def _append_entry(self, entry: dict[str, Any]) -> None:
        try:
            current = self.read_history()
        except (json.JSONDecodeError, OSError):
            current = []
        current.append(entry)
        self._atomic_write(current)

    def _atomic_write(self, data: list[dict[str, Any]]) -> None:
        tmp_path = self._log_path.with_suffix(self._log_path.suffix + ".tmp")
        payload = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
        try:
            with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(payload)
                fh.flush()
                import os

                os.fsync(fh.fileno())
            os.replace(tmp_path, self._log_path)
        except OSError:
            try:
                with open(self._log_path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(payload)
                    fh.flush()
            except OSError as exc:
                print(
                    f"[ActionLogger] Failed to persist log at {self._log_path}: {exc}"
                )
