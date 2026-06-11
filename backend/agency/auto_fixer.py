from __future__ import annotations

import logging
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .code_writer import CodeWriter

PATCH_PROMPT_TEMPLATE: str = (
    "The following code failed verification: [Error Details].\n"
    "Rewrite the code to fix the issue while maintaining the original "
    "functionality.\n\n"
    "ORIGINAL CODE:\n{original_code}\n\n"
    "ERROR DETAILS:\n{error_details}\n\n"
    "REWRITTEN CODE:"
)

REGRESSION_LOG_DIR: Path = Path("data") / "regressions"


class AutoFixer:
    def __init__(
        self,
        code_writer: CodeWriter | None = None,
        regression_log_dir: Path | str | None = None,
    ) -> None:
        self._code_writer = code_writer or CodeWriter()
        self._regression_log_dir = Path(
            regression_log_dir if regression_log_dir is not None else REGRESSION_LOG_DIR
        )
        self._logger = logging.getLogger("velynx.auto_fixer")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
                )
            )
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def generate_patch(
        self, file_path: str, qa_report: dict[str, Any]
    ) -> str:
        target = Path(file_path)
        try:
            original_code = (
                target.read_text(encoding="utf-8") if target.exists() else ""
            )
        except OSError as exc:
            self._logger.error(
                "Could not read %s while generating patch: %s", file_path, exc
            )
            original_code = ""

        error_details = self._format_error_details(qa_report)
        prompt = PATCH_PROMPT_TEMPLATE.format(
            original_code=original_code or "<empty>",
            error_details=error_details,
        )

        self._logger.info(
            "Generated patch prompt for %s (prompt length=%d chars).",
            file_path,
            len(prompt),
        )
        self._logger.debug("Patch prompt:\n%s", prompt)

        try:
            fixed_code = self._call_llm(prompt, original_code, error_details)
        except Exception as exc:
            self._logger.exception(
                "LLM call failed during patch generation: %s", exc
            )
            return self._fallback_patch(original_code, error_details)

        if not isinstance(fixed_code, str) or not fixed_code.strip():
            self._logger.warning(
                "LLM returned empty patch; using fallback for %s.", file_path
            )
            return self._fallback_patch(original_code, error_details)

        return fixed_code

    def apply_patch(self, file_path: str, fixed_code: str) -> str:
        try:
            result = self._code_writer.propose_code_write(
                filepath=file_path,
                code_content=fixed_code,
                reason=(
                    "AutoFixer is patching a file that failed QA verification. "
                    "Approve only if the diff looks correct."
                ),
            )
        except PermissionError as exc:
            self._logger.error(
                "Sandbox rejected patch for %s: %s", file_path, exc
            )
            return f"[ERROR] Sandbox rejected patch: {exc}"
        except Exception as exc:
            self._logger.exception(
                "Unexpected error while applying patch to %s: %s", file_path, exc
            )
            return f"[ERROR] apply_patch failed: {type(exc).__name__}: {exc}"

        self._logger.info(
            "apply_patch result for %s: %s", file_path, result
        )
        return result

    def attempt_repair(
        self, file_path: str, qa_report: dict[str, Any]
    ) -> str:
        target = Path(file_path)
        self._logger.info(
            "attempt_repair invoked for %s (success=%s, lint_status=%s).",
            file_path,
            qa_report.get("success"),
            qa_report.get("lint_status"),
        )

        try:
            self._snapshot_pre_patch(file_path, qa_report)
        except Exception as exc:
            self._logger.exception(
                "Could not snapshot pre-patch state of %s: %s", file_path, exc
            )

        try:
            fixed_code = self.generate_patch(file_path, qa_report)
        except Exception as exc:
            self._logger.exception(
                "generate_patch raised for %s: %s", file_path, exc
            )
            return (
                f"[ERROR] generate_patch failed for {file_path}: "
                f"{type(exc).__name__}: {exc}"
            )

        try:
            apply_result = self.apply_patch(file_path, fixed_code)
        except Exception as exc:
            self._logger.exception(
                "apply_patch raised for %s: %s", file_path, exc
            )
            return (
                f"[ERROR] apply_patch failed for {file_path}: "
                f"{type(exc).__name__}: {exc}"
            )

        if "aborted" in apply_result.lower():
            return (
                f"[ABORTED] Fix NOT applied to {file_path}. "
                f"User rejected the patch. Original file preserved."
            )

        if apply_result.startswith("[ERROR]"):
            return (
                f"[FAILED] Could not patch {file_path}: {apply_result}"
            )

        return (
            f"[FIX ATTEMPTED] {file_path} was repaired and written. "
            f"Re-run QA to confirm. apply_patch said: {apply_result}"
        )

    def _call_llm(
        self, prompt: str, original_code: str, error_details: str
    ) -> str:
        if not original_code.strip():
            return (
                "# AutoFixer fallback: original file was empty.\n"
                "# Provide initial implementation when the LLM is wired in.\n"
            )

        if "Syntax Error" in error_details:
            return self._syntax_only_fix(original_code, error_details)

        if "Test Timeout" in error_details or "Timeout" in error_details:
            return self._wrap_in_timeout_guard(original_code)

        return (
            "# AutoFixer fallback: LLM not yet integrated.\n"
            + original_code
        )

    def _fallback_patch(self, original_code: str, error_details: str) -> str:
        if "Syntax Error" in error_details and original_code:
            return self._syntax_only_fix(original_code, error_details)
        if "Test Timeout" in error_details and original_code:
            return self._wrap_in_timeout_guard(original_code)
        return original_code

    def _syntax_only_fix(self, original_code: str, error_details: str) -> str:
        match = re.search(
            r"line\s+(\d+).*?col\s+(\d+)", error_details, re.IGNORECASE
        )
        if not match:
            return original_code
        line_no = int(match.group(1))
        col_no = int(match.group(2))
        lines = original_code.splitlines(keepends=True)
        if not (1 <= line_no <= len(lines)):
            return original_code
        line_idx = line_no - 1
        line = lines[line_idx]
        stripped = line.rstrip("\r\n")
        if stripped.endswith(":"):
            new_line = stripped + " pass" + (line[len(stripped):] or "\n")
        else:
            new_line = stripped + "\n" + " " * max(0, col_no - 1) + "pass\n"
        lines[line_idx] = new_line
        return "".join(lines)

    def _wrap_in_timeout_guard(self, original_code: str) -> str:
        guard = (
            "import signal as _velynx_signal\n"
            "def _velynx_timeout_handler(signum, frame):\n"
            "    raise TimeoutError('AutoFixer: execution exceeded time budget')\n"
            "_velynx_signal.signal(_velynx_signal.SIGALRM, _velynx_timeout_handler)\n"
            "_velynx_signal.alarm(4)\n"
        )
        return guard + original_code

    def _format_error_details(self, qa_report: dict[str, Any]) -> str:
        if not isinstance(qa_report, dict):
            return f"Invalid QA report (type={type(qa_report).__name__})."
        lint_status = qa_report.get("lint_status", "unknown")
        test_output = qa_report.get("test_output", "")
        success = qa_report.get("success", False)
        return (
            f"success={success}\n"
            f"lint_status={lint_status}\n"
            f"test_output={test_output}"
        )

    def _snapshot_pre_patch(
        self, file_path: str, qa_report: dict[str, Any]
    ) -> None:
        target = Path(file_path)
        try:
            self._regression_log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._logger.error(
                "Could not create regression log dir %s: %s",
                self._regression_log_dir,
                exc,
            )
            return

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%f"
        )
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", target.name)
        snapshot_path = (
            self._regression_log_dir
            / f"{safe_name}.{timestamp}.pre_patch.txt"
        )

        try:
            if target.exists():
                original = target.read_text(encoding="utf-8")
            else:
                original = "<file did not exist>"
        except OSError as exc:
            original = f"<could not read original: {exc}>"

        header = (
            f"--- PRE-PATCH SNAPSHOT ---\n"
            f"file: {target.resolve()}\n"
            f"timestamp_utc: {datetime.now(timezone.utc).isoformat()}\n"
            f"qa_report:\n{qa_report!r}\n"
            f"--- ORIGINAL CODE ---\n"
        )
        try:
            snapshot_path.write_text(
                header + original + "\n", encoding="utf-8"
            )
            self._logger.info(
                "Wrote pre-patch snapshot to %s", snapshot_path
            )
        except OSError as exc:
            self._logger.error(
                "Failed to write pre-patch snapshot %s: %s",
                snapshot_path,
                exc,
            )
        self._logger.debug(
            "Pre-patch traceback for %s:\n%s",
            file_path,
            traceback.format_stack(),
        )
