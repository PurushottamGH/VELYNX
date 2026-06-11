from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

TEST_TIMEOUT_SECONDS: int = 5


class QAEngine:
    def run_lint(self, file_path: str) -> tuple[bool, str]:
        target = Path(file_path)
        if not target.exists():
            return False, f"Lint Error: file not found: {file_path}"
        if not target.is_file():
            return False, f"Lint Error: not a regular file: {file_path}"
        try:
            source = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return False, "Lint Error: file is not valid UTF-8"
        except OSError as exc:
            return False, f"Lint Error: could not read file: {exc}"

        try:
            ast.parse(source, filename=str(target))
        except SyntaxError as exc:
            line = exc.lineno or 0
            col = exc.offset or 0
            msg = exc.msg or "invalid syntax"
            return False, f"Syntax Error: {msg} (line {line}, col {col})"
        except ValueError as exc:
            return False, f"Syntax Error: {exc}"
        except RecursionError as exc:
            return False, f"Syntax Error: {exc}"

        return True, "Lint Passed"

    def run_test(self, file_path: str) -> tuple[bool, str]:
        target = Path(file_path).resolve()
        if not target.exists():
            return False, f"Test Error: file not found: {file_path}"
        if not target.is_file():
            return False, f"Test Error: not a regular file: {file_path}"

        isolated_cwd = self._make_isolated_cwd(target.parent)

        try:
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-S", str(target)],
                cwd=str(isolated_cwd),
                env=self._isolated_env(),
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT_SECONDS,
                check=False,
                stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired as exc:
            partial_stdout = exc.stdout or ""
            partial_stderr = exc.stderr or ""
            return (
                False,
                f"Test Timeout: exceeded {TEST_TIMEOUT_SECONDS}s "
                f"in sandbox {isolated_cwd}\n"
                f"[STDOUT]\n{partial_stdout}\n"
                f"[STDERR]\n{partial_stderr}",
            )
        except FileNotFoundError as exc:
            return False, f"Test Error: python interpreter not found: {exc}"
        except PermissionError as exc:
            return False, f"Test Error: permission denied: {exc}"
        except OSError as exc:
            return False, f"Test Error: could not launch subprocess: {exc}"

        output = (
            f"[EXIT_CODE] {result.returncode}\n"
            f"[STDOUT]\n{result.stdout or ''}\n"
            f"[STDERR]\n{result.stderr or ''}"
        )

        if result.returncode == 0:
            return True, output

        return False, output

    def verify_and_report(self, file_path: str) -> dict[str, Any]:
        lint_ok, lint_status = self.run_lint(file_path)
        if not lint_ok:
            return {
                "success": False,
                "lint_status": lint_status,
                "test_output": "Test skipped: lint failed.",
            }

        test_ok, test_output = self.run_test(file_path)
        return {
            "success": bool(lint_ok and test_ok),
            "lint_status": lint_status,
            "test_output": test_output,
        }

    def _isolated_env(self) -> dict[str, str]:
        env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "HOME": os.environ.get("HOME", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUNBUFFERED": "1",
            "PYTHONIOENCODING": "utf-8",
        }
        for key in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
            env[key] = ""
        return env

    def _make_isolated_cwd(self, script_dir: Path) -> Path:
        isolated = script_dir / ".velynx_qa_sandbox"
        try:
            isolated.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeError(
                f"QAEngine could not create isolated cwd: {exc}"
            ) from exc
        return isolated
