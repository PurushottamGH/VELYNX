from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False


class SystemBridge:
    def read_file(self, filepath: str) -> str:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if not path.is_file():
            raise IsADirectoryError(f"Path is a directory, not a file: {filepath}")
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise UnicodeDecodeError(
                exc.encoding,
                exc.object,
                exc.start,
                exc.end,
                f"File is not valid UTF-8: {filepath}",
            ) from exc
        except PermissionError as exc:
            raise PermissionError(f"Permission denied reading: {filepath}") from exc

    def get_git_status(self, repo_path: str = ".") -> str:
        target = Path(repo_path)
        if not target.exists():
            raise FileNotFoundError(f"Path not found: {repo_path}")
        if not target.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {repo_path}")
        try:
            result = subprocess.run(
                ["git", "status", "-s"],
                cwd=str(target),
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError("git executable not found on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise subprocess.TimeoutExpired(
                exc.cmd,
                exc.timeout,
                output=exc.output,
                stderr=exc.stderr,
            ) from exc
        except PermissionError as exc:
            raise PermissionError(
                f"Permission denied executing git in: {repo_path}"
            ) from exc

        if result.returncode != 0:
            error_msg = (result.stderr or "").strip() or "git status failed"
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                output=result.stdout,
                stderr=result.stderr,
            )
        return result.stdout

    def list_directory(self, path: str = ".") -> list[dict[str, Any]]:
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not target.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        entries: list[dict[str, Any]] = []
        try:
            children = list(target.iterdir())
        except PermissionError as exc:
            raise PermissionError(
                f"Permission denied listing: {path}"
            ) from exc

        for entry in sorted(children, key=lambda p: (not p.is_dir(), p.name.lower())):
            try:
                stat = entry.stat()
                if entry.is_dir():
                    entries.append(
                        {
                            "name": entry.name,
                            "type": "directory",
                            "size": None,
                            "path": str(entry),
                            "modified": stat.st_mtime,
                        }
                    )
                elif entry.is_file():
                    entries.append(
                        {
                            "name": entry.name,
                            "type": "file",
                            "size": stat.st_size,
                            "path": str(entry),
                            "modified": stat.st_mtime,
                        }
                    )
                else:
                    entries.append(
                        {
                            "name": entry.name,
                            "type": "other",
                            "size": stat.st_size,
                            "path": str(entry),
                            "modified": stat.st_mtime,
                        }
                    )
            except OSError as exc:
                entries.append(
                    {
                        "name": entry.name,
                        "type": "error",
                        "size": None,
                        "path": str(entry),
                        "error": str(exc),
                    }
                )
        return entries


class ExecutionQuarantine:
    def __init__(self) -> None:
        self._console: Console | None
        if _RICH_AVAILABLE:
            self._console = Console(stderr=True, force_terminal=True)
        else:
            self._console = None

    def propose_command(self, command: str, reason: str) -> str:
        warning = (
            f"[⚠ AGENCY OVERRIDE] VELYNX proposes: {command}\n"
            f"Reason: {reason}"
        )

        if self._console is not None:
            self._console.print(
                Panel(
                    Text(warning, style="bold yellow"),
                    title="[bold red] EXECUTION QUARANTINE [/bold red]",
                    border_style="bold red",
                    padding=(1, 2),
                )
            )
        else:
            print("\n" + "=" * 64)
            print("!! EXECUTION QUARANTINE !!")
            print(warning)
            print("=" * 64 + "\n")

        try:
            choice = input("Authorize execution? [Y/n]: ").strip().lower()
        except EOFError:
            return "Execution aborted by user."

        if choice != "y":
            return "Execution aborted by user."

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return (
                f"[TIMEOUT] Command exceeded {exc.timeout}s\n"
                f"Command: {command}\n"
                f"Partial stdout: {exc.stdout or ''}\n"
                f"Partial stderr: {exc.stderr or ''}"
            )
        except FileNotFoundError as exc:
            return f"[ERROR] Shell or command not found: {exc}"
        except PermissionError as exc:
            return f"[ERROR] Permission denied executing command: {exc}"
        except Exception as exc:
            return f"[ERROR] Execution failed: {type(exc).__name__}: {exc}"

        return (
            f"[STDOUT]\n{result.stdout}"
            f"[STDERR]\n{result.stderr}"
            f"[EXIT_CODE] {result.returncode}"
        )
