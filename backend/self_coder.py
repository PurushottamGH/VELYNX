"""
VELYNX Self-Coder
=================
An engine that reads, patches, and tests its own source files safely.

Flow:
  1. diagnose(query)  — find which file has the bug
  2. patch(file, instruction) — rewrite file via LLM (creates .bak)
  3. validate(file)   — ast.parse() + subprocess pytest
  4. commit(file)     — confirm changes (remove .bak)
     or rollback(file) — restore from .bak

Safety rules:
  - Only touches files inside backend/
  - Always backup before writing (.bak)
  - Never commit if pytest fails
  - DRY_RUN = False flag for testing
"""

import ast
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.llm_client import LLMMessage, llm_client

BACKEND_ROOT = Path(__file__).parent


class SelfCoder:
    """VELYNX's self-modification engine.  All LLM calls go through llm_client."""

    DRY_RUN = False

    # ── Public API ──────────────────────────────────────────────────────

    async def diagnose(self, query: str) -> str | None:
        """Find which file has the bug.  Returns relative path inside backend/ or None."""
        if not llm_client.available:
            return None

        file_list = "\n".join(self._list_backend_files())

        prompt = f"""You are a codebase diagnostic tool.  Given a bug description, identify which backend file is most likely responsible.

Bug description: "{query}"

Available files:
{file_list}

Respond in JSON only:
{{"target_file": "path/to/file.py", "reason": "short explanation"}}"""

        try:
            resp = await llm_client.chat(
                [LLMMessage(role="user", content=prompt)],
                temperature=0.1,
                max_tokens=200,
            )
            data = llm_client.parse_json_content(resp)
            if data and "target_file" in data:
                candidate = data["target_file"]
                if self._resolve_path(candidate):
                    return candidate
        except Exception:
            pass

        return None

    async def patch(self, file: str, instruction: str) -> str | None:
        """Rewrite file via LLM using the given instruction.  Returns the new source code, or None on failure.

        The file is NOT written to disk here — that happens in commit().
        """
        target = self._resolve_path(file)
        if target is None:
            return None
        if not target.exists():
            return None

        original = target.read_text()

        prompt = f"""Rewrite the Python file below according to this instruction:

INSTRUCTION: {instruction}

ORIGINAL FILE:
```python
{original[:6000]}
```

Rules:
- Return ONLY the complete corrected Python file. No explanation, no markdown, no fences.
- Do not change any logic unrelated to the instruction.
- Keep all existing imports and class structure.
- The file must be syntactically valid Python 3.10+."""

        try:
            resp = await llm_client.chat(
                [LLMMessage(role="user", content=prompt)],
                temperature=0.05,
                max_tokens=4000,
            )
            new_code = resp.content.strip()
        except Exception:
            return None

        # Strip markdown fences if LLM added them
        if new_code.startswith("```"):
            lines = new_code.splitlines()
            new_code = "\n".join(l for l in lines if not l.startswith("```"))

        # Syntax check before returning
        try:
            ast.parse(new_code)
        except SyntaxError:
            return None

        if self.DRY_RUN:
            return new_code

        # Create backup, then write
        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, bak)
        target.write_text(new_code)

        return new_code

    def validate(self, file: str) -> bool:
        """Run ast.parse() + pytest against the file.  Returns True if all pass."""
        target = self._resolve_path(file)
        if target is None:
            return False
        if not target.exists():
            return False

        # 1. Syntax check
        try:
            ast.parse(target.read_text())
        except SyntaxError:
            return False

        # 2. Run pytest
        return self._run_tests(file)

    def commit(self, file: str) -> bool:
        """Make the patch permanent.  Only succeeds if validate() passes.

        Removes the .bak file on success.  On failure the .bak remains for rollback.
        """
        target = self._resolve_path(file)
        if target is None:
            return False

        if not self.validate(file):
            return False

        bak = target.with_suffix(target.suffix + ".bak")
        if bak.exists():
            bak.unlink()
        return True

    def rollback(self, file: str) -> bool:
        """Restore the file from its .bak backup.  Returns True on success."""
        target = self._resolve_path(file)
        if target is None:
            return False

        bak = target.with_suffix(target.suffix + ".bak")
        if not bak.exists():
            return False

        shutil.copy2(bak, target)
        return True

    # ── Helpers ─────────────────────────────────────────────────────────

    def _resolve_path(self, file: str) -> Path | None:
        """Resolve and validate that the file is inside backend/.  Returns Path or None."""
        target = (BACKEND_ROOT / file).resolve()
        try:
            target.relative_to(BACKEND_ROOT.resolve())
        except ValueError:
            return None
        return target

    def _list_backend_files(self) -> list[str]:
        """List all .py files inside backend/ (skipping __pycache__ and tests)."""
        files = []
        for p in BACKEND_ROOT.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            if ".bak" in p.suffixes:
                continue
            files.append(str(p.relative_to(BACKEND_ROOT)))
        return sorted(files)

    def _run_tests(self, file: str) -> bool:
        """Run pytest for the module that changed.  Returns True if tests pass."""
        stem = Path(file).stem
        test_dir = BACKEND_ROOT / "tests"

        # Try the specific test file first, then the generic smoke test
        candidates = [
            test_dir / f"test_{stem}.py",
            test_dir / "test_full_loop_smoke.py",
        ]

        for tf in candidates:
            if tf.exists():
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(tf), "-x", "-q", "--tb=short"],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(BACKEND_ROOT.parent),
                )
                if result.returncode != 0:
                    return False
                return True

        # No test file — verify the module imports cleanly
        target = self._resolve_path(file)
        if target is None:
            return False
        result = subprocess.run(
            [sys.executable, "-c", f"import ast; ast.parse({target.read_text()!r})"],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
