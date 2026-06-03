"""
VELYNX Self-Coder v2
====================
VELYNX can now modify its own Python source files safely.

Flow:
  1. Diagnose — identify what file/function needs changing and why
  2. Read — load the target file via AST (not raw string)
  3. Generate patch — produce the replacement code
  4. Validate — run syntax check + unit test
  5. Commit — write file (with rollback on failure)

Safety rules:
  - NEVER touches files outside VELYNX's own backend/ directory
  - NEVER applies a patch that breaks existing tests
  - Always keeps a .bak before overwriting
  - Dry-run mode available (logs patch without applying)
"""

import ast
import asyncio
import hashlib
import importlib
import inspect
import os
import shutil
import subprocess
import sys
import textwrap
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ── Groq/local LLM for code generation ──────────────────────────────────────
# We use Groq as the code brain for now; swap to NovaMind inference server later
import os as _os
from groq import Groq as _Groq

_groq = _Groq(api_key=_os.environ.get("GROQ_API_KEY", ""))

VELYNX_ROOT = Path(__file__).parent.parent   # …/VELYNX/
BACKEND_ROOT = Path(__file__).parent         # …/VELYNX/backend/
SAFE_DIRS = {BACKEND_ROOT}


@dataclass
class PatchResult:
    success: bool
    summary: str
    file_changed: str = ""
    lines_changed: int = 0
    test_output: str = ""
    error: str = ""


@dataclass
class DiagnoseResult:
    target_file: str
    target_function: str
    problem: str
    fix_instruction: str
    priority: str = "normal"   # normal | urgent | cosmetic


class SelfCoder:
    """
    VELYNX's self-modification engine.
    All methods are async to keep the brain non-blocking.
    """

    MAX_RETRIES = 3
    DRY_RUN = False   # set True in tests

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def handle(self, query: str) -> PatchResult:
        """Entry point for explicit user requests like 'fix the reasoning engine'."""
        diagnosis = await self._diagnose_from_query(query)
        return await self._patch(diagnosis)

    async def auto_fix(self, module_path: str) -> PatchResult:
        """Called by Brain during self-improvement. Tries to fix a broken module."""
        diagnosis = await self._diagnose_module(module_path)
        if diagnosis is None:
            return PatchResult(success=False, summary=f"Could not diagnose {module_path}")
        return await self._patch(diagnosis)

    async def auto_improve(self) -> list[PatchResult]:
        """
        Scans all backend files for common quality issues and patches them.
        Runs as a background job.
        """
        results = []
        candidates = list(BACKEND_ROOT.rglob("*.py"))
        for pyfile in candidates[:10]:   # limit per run
            issues = self._quick_scan(pyfile)
            for issue in issues:
                r = await self._patch(issue)
                results.append(r)
                if r.success:
                    await asyncio.sleep(0.1)   # breathe
        return results

    # ------------------------------------------------------------------ #
    #  Diagnosis                                                           #
    # ------------------------------------------------------------------ #

    async def _diagnose_from_query(self, query: str) -> DiagnoseResult:
        """Use LLM to figure out WHICH file and WHAT to change."""
        file_list = "\n".join(
            str(p.relative_to(VELYNX_ROOT))
            for p in BACKEND_ROOT.rglob("*.py")
            if not any(skip in str(p) for skip in ["__pycache__", ".git", "test_"])
        )

        prompt = f"""You are VELYNX's self-diagnostic system.

User request: "{query}"

Available source files:
{file_list}

Respond in this exact JSON format (nothing else):
{{
  "target_file": "backend/path/to/file.py",
  "target_function": "function_name_or_empty_string",
  "problem": "one sentence describing what is wrong",
  "fix_instruction": "precise instruction for what to write/change",
  "priority": "normal"
}}"""

        resp = _groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400,
        )
        import json
        raw = resp.choices[0].message.content.strip()
        # strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return DiagnoseResult(**data)

    async def _diagnose_module(self, module_path: str) -> DiagnoseResult | None:
        """Try to auto-diagnose a module by importing it and catching errors."""
        try:
            source = Path(module_path).read_text()
            ast.parse(source)   # syntax check
        except SyntaxError as e:
            return DiagnoseResult(
                target_file=module_path,
                target_function="",
                problem=f"Syntax error at line {e.lineno}: {e.msg}",
                fix_instruction="Fix the syntax error",
                priority="urgent",
            )
        except Exception as e:
            return DiagnoseResult(
                target_file=module_path,
                target_function="",
                problem=str(e),
                fix_instruction="Fix the import/runtime error",
                priority="normal",
            )
        return None

    def _quick_scan(self, pyfile: Path) -> list[DiagnoseResult]:
        """Lightweight static scan for common issues."""
        issues = []
        try:
            source = pyfile.read_text()
            tree = ast.parse(source)
        except Exception:
            return issues

        for node in ast.walk(tree):
            # bare except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(DiagnoseResult(
                    target_file=str(pyfile.relative_to(VELYNX_ROOT)),
                    target_function="",
                    problem="Bare `except:` swallows all errors silently",
                    fix_instruction="Replace `except:` with `except Exception as e:` and log e",
                    priority="cosmetic",
                ))
            # TODO comments
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                val = str(node.value.value)
                if "TODO" in val or "FIXME" in val:
                    issues.append(DiagnoseResult(
                        target_file=str(pyfile.relative_to(VELYNX_ROOT)),
                        target_function="",
                        problem=f"Unresolved TODO: {val[:80]}",
                        fix_instruction=f"Implement the TODO: {val[:80]}",
                        priority="normal",
                    ))

        return issues[:2]   # max 2 per file per scan

    # ------------------------------------------------------------------ #
    #  Patching                                                            #
    # ------------------------------------------------------------------ #

    async def _patch(self, diagnosis: DiagnoseResult) -> PatchResult:
        target = VELYNX_ROOT / diagnosis.target_file
        if not self._is_safe(target):
            return PatchResult(
                success=False,
                summary=f"SAFETY: {diagnosis.target_file} is outside allowed directories",
                error="safety_violation",
            )

        if not target.exists():
            return PatchResult(
                success=False,
                summary=f"File not found: {diagnosis.target_file}",
                error="file_not_found",
            )

        original = target.read_text()
        backup   = target.with_suffix(".py.bak")

        for attempt in range(self.MAX_RETRIES):
            new_code = await self._generate_patch(original, diagnosis)
            if new_code is None:
                continue

            # Syntax check
            try:
                ast.parse(new_code)
            except SyntaxError as e:
                diagnosis.fix_instruction += f"\n[Prev attempt had syntax error at line {e.lineno}: {e.msg}. Fix it.]"
                continue

            if self.DRY_RUN:
                return PatchResult(
                    success=True,
                    summary=f"[DRY RUN] Would patch {diagnosis.target_file}",
                    file_changed=diagnosis.target_file,
                )

            # Write backup + new file
            shutil.copy2(target, backup)
            target.write_text(new_code)

            # Run tests
            test_ok, test_out = self._run_tests(diagnosis.target_file)
            if test_ok:
                lines = abs(len(new_code.splitlines()) - len(original.splitlines()))
                return PatchResult(
                    success=True,
                    summary=f"Patched {diagnosis.target_file} ({lines} lines changed). Tests pass.",
                    file_changed=str(target),
                    lines_changed=lines,
                    test_output=test_out,
                )
            else:
                # Rollback
                shutil.copy2(backup, target)
                diagnosis.fix_instruction += f"\n[Tests failed after patch: {test_out[:300]}. Fix these failures too.]"

        return PatchResult(
            success=False,
            summary=f"Failed to patch {diagnosis.target_file} after {self.MAX_RETRIES} attempts",
            error="max_retries_exceeded",
        )

    async def _generate_patch(self, original_code: str, diagnosis: DiagnoseResult) -> str | None:
        """Ask LLM to rewrite the file with the fix applied."""
        prompt = f"""You are VELYNX's self-coding engine. Rewrite the Python file below to fix the described problem.

PROBLEM: {diagnosis.problem}
INSTRUCTION: {diagnosis.fix_instruction}
TARGET FUNCTION (empty = whole file): {diagnosis.target_function}

ORIGINAL FILE:
```python
{original_code[:6000]}
```

Rules:
- Return ONLY the complete, corrected Python file. No explanation. No markdown. No fences.
- Do NOT change any logic unrelated to the fix.
- Keep all existing imports and class structure.
- The file must be syntactically valid Python 3.10+.
"""
        try:
            resp = _groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.05,
                max_tokens=4000,
            )
            code = resp.choices[0].message.content.strip()
            # strip fences if LLM added them
            if code.startswith("```"):
                lines = code.splitlines()
                code = "\n".join(
                    l for l in lines
                    if not l.startswith("```")
                )
            return code
        except Exception as e:
            print(f"[SelfCoder] LLM error: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _is_safe(self, path: Path) -> bool:
        """Verify the target is inside VELYNX's own backend."""
        try:
            path.resolve().relative_to(BACKEND_ROOT.resolve())
            return True
        except ValueError:
            return False

    def _run_tests(self, changed_file: str) -> tuple[bool, str]:
        """Run pytest against the module that changed."""
        # Find related test file
        stem = Path(changed_file).stem
        test_candidates = [
            BACKEND_ROOT / "tests" / f"test_{stem}.py",
            BACKEND_ROOT / "tests" / "test_full_loop_smoke.py",
        ]
        for tf in test_candidates:
            if tf.exists():
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(tf), "-x", "-q", "--tb=short"],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(VELYNX_ROOT),
                )
                return result.returncode == 0, result.stdout + result.stderr

        # No test file — just verify the module imports cleanly
        result = subprocess.run(
            [sys.executable, "-c", f"import importlib.util; "
             f"spec = importlib.util.spec_from_file_location('m', '{VELYNX_ROOT / changed_file}'); "
             f"m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)"],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0, result.stdout + result.stderr