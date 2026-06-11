from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TYPE_CHECKING

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

if TYPE_CHECKING:
    from models.llm_client import LLMClient

ALLOWED_DIR: str = os.path.abspath("experiments")

SYSTEM_PROMPT_CODE_GEN = (
    "You are a Senior Software Engineer. "
    "You MUST write complete, functional implementation logic. "
    "DO NOT output boilerplate stubs, placeholder comments, "
    "or print statements repeating the user's prompt. "
    "Provide only the raw, executable Python code. "
    "No explanations, no markdown fences, no commentary."
)


class CodeWriter:
    def __init__(self, allowed_dir: str | None = None, llm_client: "LLMClient | None" = None) -> None:
        self.ALLOWED_DIR: str = (
            os.path.abspath(allowed_dir) if allowed_dir else ALLOWED_DIR
        )
        self._llm_client = llm_client
        try:
            os.makedirs(self.ALLOWED_DIR, exist_ok=True)
        except OSError as exc:
            print(
                f"[CodeWriter] Warning: could not create sandbox {self.ALLOWED_DIR}: {exc}"
            )

        if _RICH_AVAILABLE:
            self._console: Console | None = Console(
                stderr=True, force_terminal=True
            )
        else:
            self._console = None

    def _is_safe_path(self, target_path: str) -> str:
        if not isinstance(target_path, str) or not target_path.strip():
            raise PermissionError(
                "Sandbox Violation: Attempted to write outside the experiments directory."
            )
        try:
            resolved = os.path.realpath(os.path.abspath(target_path))
        except (TypeError, ValueError) as exc:
            raise PermissionError(
                "Sandbox Violation: Attempted to write outside the experiments directory."
            ) from exc

        allowed_real = os.path.realpath(self.ALLOWED_DIR)
        allowed_with_sep = allowed_real if allowed_real.endswith(
            os.sep
        ) else allowed_real + os.sep

        if resolved == allowed_real or resolved.startswith(allowed_with_sep):
            return resolved

        raise PermissionError(
            "Sandbox Violation: Attempted to write outside the experiments directory."
        )

    def propose_code_write(
        self, filepath: str, code_content: str, reason: str
    ) -> str:
        safe_path = self._is_safe_path(filepath)

        snippet = self._build_snippet(code_content, lines=10)
        warning = (
            f"[⚠ CODE WRITE OVERRIDE]\n"
            f"Target: {safe_path}\n"
            f"Reason: {reason}\n"
            f"Snippet: {snippet}"
        )

        if self._console is not None:
            self._console.print(
                Panel(
                    Text(warning, style="bold yellow"),
                    title="[bold red] CODE SANDBOX OVERRIDE [/bold red]",
                    border_style="bold red",
                    padding=(1, 2),
                )
            )
        else:
            print("\n" + "=" * 64)
            print("!! CODE SANDBOX OVERRIDE !!")
            print(warning)
            print("=" * 64 + "\n")

        try:
            choice = input("Authorize code write? [Y/n]: ").strip().lower()
        except EOFError:
            return "Code write aborted by user."

        if choice != "y":
            return "Code write aborted by user."

        try:
            target = Path(safe_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code_content, encoding="utf-8")
        except PermissionError as exc:
            return f"[ERROR] Permission denied writing file: {exc}"
        except OSError as exc:
            return f"[ERROR] Filesystem error writing file: {exc}"
        except Exception as exc:
            return f"[ERROR] Unexpected failure: {type(exc).__name__}: {exc}"

        return f"[SUCCESS] Code written to {safe_path}"

    async def generate_code(self, query: str) -> str:
        """Generate a complete Python script via LLM."""
        if self._llm_client is None:
            raise RuntimeError("CodeWriter has no LLM client — cannot generate code")
        if not self._llm_client.available:
            raise RuntimeError("LLM client unavailable — cannot generate code")
        from models.llm_client import LLMMessage

        prompt = (
            f"Write a complete, functional Python program based on this request:\n\n"
            f"\"{query}\"\n\n"
            "Requirements:\n"
            "- Write COMPLETE implementation — no stubs, no 'pass', no 'TODO' placeholders.\n"
            "- Include proper error handling and edge case coverage.\n"
            "- Use only standard library modules unless the request explicitly requires otherwise.\n"
            "- Output ONLY raw Python code. No markdown fences, no explanations."
        )
        resp = await self._llm_client.chat(
            [LLMMessage(role="system", content=SYSTEM_PROMPT_CODE_GEN),
             LLMMessage(role="user", content=prompt)],
            temperature=0.05,
        )
        code = resp.content.strip()
        if code.startswith("```"):
            lines = code.splitlines()
            code = "\n".join(l for l in lines if not l.startswith("```"))
        return code

    async def infer_filename(self, query: str) -> str:
        """Infer a .py filename from the user query via LLM."""
        if self._llm_client is None:
            raise RuntimeError("CodeWriter has no LLM client — cannot infer filename")
        if not self._llm_client.available:
            raise RuntimeError("LLM client unavailable — cannot infer filename")
        from models.llm_client import LLMMessage

        prompt = (
            "Extract a sensible Python filename from this user request. "
            "Return ONLY the filename (e.g. 'system_logger.py'), nothing else. "
            "Use snake_case. Prefer names that describe the tool's purpose.\n\n"
            f"Request: \"{query}\""
        )
        resp = await self._llm_client.chat(
            [LLMMessage(role="system", content=SYSTEM_PROMPT_CODE_GEN),
             LLMMessage(role="user", content=prompt)],
            temperature=0.1,
        )
        import re
        name = resp.content.strip().strip("`\"'").rstrip(".py") + ".py"
        name = re.sub(r"[^\w\-.]", "_", name)
        if not name.endswith(".py"):
            name += ".py"
        return name

    def _build_snippet(self, code_content: str, lines: int = 10) -> str:
        if not isinstance(code_content, str):
            code_content = str(code_content)
        split = code_content.splitlines()
        head = split[:lines]
        body = "\n".join(head)
        if len(split) > lines:
            body += "\n..."
        return body
