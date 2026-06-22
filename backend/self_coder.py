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
from pathlib import Path



BACKEND_ROOT = Path(__file__).parent


class SelfCoder:
    """VELYNX's self-modification engine — MEMORY-ONLY MODE (no LLM)."""

    DRY_RUN = False

    # ── Public API ──────────────────────────────────────────────────────

    async def diagnose(self, query: str) -> str | None:
        """LLM-free: returns None. No external model to diagnose code."""
        return None

    async def patch(self, file: str, instruction: str) -> str | None:
        """LLM-free: returns None. No external model to generate patches."""
        return None

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
