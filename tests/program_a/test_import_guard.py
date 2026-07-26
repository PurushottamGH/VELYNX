"""Import-boundary / dependency-graph conformance guard for program_a/.

Statically parses (via ``ast``, not ``import``) every module under
``program_a/`` and asserts it does not import anything on the deny-list from
``PROGRAM_A_FINAL_ARCHITECTURE.md`` Section 7:

    program_a.**            deny  backend.cognition.answer_synthesizer
    program_a.**            deny  backend.cognition.reasoning_engine
    program_a.**            deny  backend.cognition.dream_state
    program_a.**            deny  backend.soul.*
    program_a.**            deny  backend.self_model.*
    program_a.**            deny  research.policies.free_energy
    program_a.**            deny  experiments.EXP1.calibration
    program_a.**            deny  experiments.EXP1.decision
    program_a.**            deny  experiments.EXP1.run
    program_a.{PA-1..PA-4}  deny  experiments.* (only PA-5/binding may import it)
    experiments.EXP1.*      deny  program_a.*    (runner stays injection-only)
    experiments.EXP1.*      deny  backend.*

Static AST parsing (not live import) is deliberate: ``snapshot_builder.py``
legitimately contains a *deferred* (function-body) import of
``backend.retrieval.unified_retriever`` that must not execute at module
import time (so the module stays importable without the unpackaged backend
present); asserting on the syntax tree lets this test tell "top-level import"
apart from "deferred import inside a function body" without needing to
actually import backend at all.

Scope: tests only, no production-code changes.

Reference: PROGRAM_A_FINAL_ARCHITECTURE.md Section 2, Section 7;
PROGRAM_A_MODULE_SPEC.md (per-module allow/deny lists).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM_A_ROOT = REPO_ROOT / "archive" / "program_a" / "program_a"
EXP1_ROOT = REPO_ROOT / "experiments" / "EXP1"

# The single sanctioned seam: only this module may import experiments.EXP1.*.
BINDING_MODULE = PROGRAM_A_ROOT / "binding" / "exp1_binding.py"

# The single sanctioned (deferred-only) seam for the backend retriever.
SNAPSHOT_BUILDER_MODULE = PROGRAM_A_ROOT / "evidence" / "snapshot_builder.py"

DENY_PREFIXES_ALWAYS = (
    "backend.cognition.answer_synthesizer",
    "backend.cognition.reasoning_engine",
    "backend.cognition.dream_state",
    "backend.soul",
    "backend.self_model",
    "research.policies.free_energy",
    "experiments.EXP1.calibration",
    "experiments.EXP1.decision",
    "experiments.EXP1.run",
)

# backend.retrieval.unified_retriever is allow-listed ONLY as a deferred
# (function-body) import inside snapshot_builder.py -- never at module level,
# and never anywhere else.
BACKEND_RETRIEVAL_PREFIX = "backend.retrieval"


def _iter_program_a_modules() -> list[Path]:
    return sorted(PROGRAM_A_ROOT.rglob("*.py"))


def _iter_exp1_modules() -> list[Path]:
    return sorted(EXP1_ROOT.glob("*.py"))


def _imported_names(node: ast.AST) -> list[tuple[str, int, bool]]:
    """Return (dotted_module_name, line_number, is_top_level) for every import
    in the module. ``is_top_level`` is True only for imports at column 0
    inside module-level statements (not inside a function/class body), so a
    deferred import can be told apart from a real module-level dependency.
    """
    results: list[tuple[str, int, bool]] = []

    def walk(body: list[ast.stmt], top_level: bool) -> None:
        for stmt in body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    results.append((alias.name, stmt.lineno, top_level))
            elif isinstance(stmt, ast.ImportFrom):
                module = stmt.module or ""
                results.append((module, stmt.lineno, top_level))
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                walk(stmt.body, top_level=False)
            elif hasattr(stmt, "body"):
                # if/try/with/for at module level are still "top level" in the
                # sense that they execute at import time.
                nested_top_level = top_level
                walk(getattr(stmt, "body", []), nested_top_level)
                if hasattr(stmt, "orelse"):
                    walk(stmt.orelse, nested_top_level)
                if hasattr(stmt, "finalbody"):
                    walk(stmt.finalbody, nested_top_level)

    walk(node.body, top_level=True)
    return results


def _parse(path: Path) -> ast.Module:
    # utf-8-sig: some program_a modules are saved with a UTF-8 BOM; plain
    # utf-8 decoding leaves a literal U+FEFF as the first source character,
    # which ast.parse rejects as a SyntaxError before any import is even
    # inspected. That's a real-but-irrelevant encoding wrinkle, not an import
    # violation -- utf-8-sig strips the BOM if present and is a no-op if not.
    return ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))


@pytest.mark.parametrize(
    "module_path", _iter_program_a_modules(), ids=lambda p: str(p.relative_to(PROGRAM_A_ROOT))
)
def test_program_a_module_never_imports_always_denied_targets(module_path: Path) -> None:
    tree = _parse(module_path)
    for name, lineno, _top_level in _imported_names(tree):
        for denied in DENY_PREFIXES_ALWAYS:
            assert not (name == denied or name.startswith(denied + ".")), (
                f"{module_path.relative_to(REPO_ROOT)}:{lineno} imports "
                f"deny-listed module {name!r} (matches {denied!r})"
            )


@pytest.mark.parametrize(
    "module_path", _iter_program_a_modules(), ids=lambda p: str(p.relative_to(PROGRAM_A_ROOT))
)
def test_only_binding_module_imports_experiments(module_path: Path) -> None:
    tree = _parse(module_path)
    imports_experiments = any(
        name == "experiments" or name.startswith("experiments.")
        for name, _lineno, _top_level in _imported_names(tree)
    )
    if module_path == BINDING_MODULE:
        assert imports_experiments, (
            "binding/exp1_binding.py is the sanctioned experiments.EXP1 seam "
            "and is expected to import experiments.EXP1.*; if this changed, "
            "the binding module was refactored -- update this test's premise."
        )
    else:
        assert not imports_experiments, (
            f"{module_path.relative_to(REPO_ROOT)} imports experiments.* but "
            "is not binding/exp1_binding.py -- only the sanctioned PA-5 seam "
            "may import experiments.EXP1 types (PROGRAM_A_FINAL_ARCHITECTURE.md "
            "Section 7)."
        )


@pytest.mark.parametrize(
    "module_path", _iter_program_a_modules(), ids=lambda p: str(p.relative_to(PROGRAM_A_ROOT))
)
def test_backend_retrieval_only_imported_deferred_in_snapshot_builder(module_path: Path) -> None:
    tree = _parse(module_path)
    for name, lineno, top_level in _imported_names(tree):
        if name == BACKEND_RETRIEVAL_PREFIX or name.startswith(BACKEND_RETRIEVAL_PREFIX + "."):
            assert module_path == SNAPSHOT_BUILDER_MODULE, (
                f"{module_path.relative_to(REPO_ROOT)}:{lineno} imports "
                f"{name!r}; only evidence/snapshot_builder.py may import "
                "backend.retrieval.unified_retriever (builder-side only)."
            )
            assert not top_level, (
                f"{module_path.relative_to(REPO_ROOT)}:{lineno} imports "
                f"{name!r} at module level; it must be deferred to a function "
                "body so the module stays importable without the (unpackaged) "
                "backend present."
            )


@pytest.mark.parametrize(
    "module_path", _iter_program_a_modules(), ids=lambda p: str(p.relative_to(PROGRAM_A_ROOT))
)
def test_no_program_a_module_imports_other_forbidden_backend_subsystems(module_path: Path) -> None:
    # Broader sweep: no program_a module may import ANY backend.* other than
    # the one sanctioned, deferred backend.retrieval seam.
    tree = _parse(module_path)
    for name, lineno, _top_level in _imported_names(tree):
        if name == "backend" or name.startswith("backend."):
            allowed = module_path == SNAPSHOT_BUILDER_MODULE and (
                name == BACKEND_RETRIEVAL_PREFIX or name.startswith(BACKEND_RETRIEVAL_PREFIX + ".")
            )
            assert allowed, (
                f"{module_path.relative_to(REPO_ROOT)}:{lineno} imports "
                f"{name!r}; program_a/ may only import backend.retrieval.* "
                "and only (deferred) from snapshot_builder.py."
            )


@pytest.mark.parametrize("module_path", _iter_exp1_modules(), ids=lambda p: p.name)
def test_experiments_exp1_never_imports_program_a(module_path: Path) -> None:
    tree = _parse(module_path)
    for name, lineno, _top_level in _imported_names(tree):
        assert not (name == "program_a" or name.startswith("program_a.")), (
            f"experiments/EXP1/{module_path.name}:{lineno} imports "
            f"{name!r} -- the runner must stay injection-only "
            "(PROGRAM_A_FINAL_ARCHITECTURE.md Section 2/7)."
        )


@pytest.mark.parametrize("module_path", _iter_exp1_modules(), ids=lambda p: p.name)
def test_experiments_exp1_never_imports_backend(module_path: Path) -> None:
    tree = _parse(module_path)
    for name, lineno, _top_level in _imported_names(tree):
        assert not (name == "backend" or name.startswith("backend.")), (
            f"experiments/EXP1/{module_path.name}:{lineno} imports "
            f"{name!r} -- experiments.EXP1.* must never import backend.* "
            "(standing boundary rule)."
        )


def test_deferred_import_detection_correctly_classifies_top_level_vs_function_body() -> None:
    # Meta-test: pins that _imported_names' top_level classification actually
    # distinguishes "import at module level" from "import inside a function
    # body," using a synthetic snippet (not depending on snapshot_builder.py
    # already containing a deferred import -- build_snapshot() is still a
    # phase-6 stub as of this writing, so asserting against live production
    # code here would make the guard's correctness depend on unrelated
    # implementation progress). A bug in this classifier would otherwise
    # silently make test_backend_retrieval_only_imported_deferred_* pass for
    # the wrong reason once snapshot_builder.py's real import lands.
    source = (
        "import top_level_module\n"
        "\n"
        "def f():\n"
        "    import deferred_module\n"
        "    return deferred_module\n"
    )
    tree = ast.parse(source, filename="<synthetic>")
    imports = {name: top_level for name, _lineno, top_level in _imported_names(tree)}
    assert imports["top_level_module"] is True
    assert imports["deferred_module"] is False


def test_snapshot_builder_backend_retrieval_import_not_yet_present_is_expected() -> None:
    # build_snapshot() is a phase-6 stub today: it raises NotImplementedError
    # without an actual backend.retrieval import anywhere in its body. This
    # documents that fact (rather than silently having zero coverage of the
    # "no import yet" state) and will start failing loudly -- signalling
    # "come update the guard's expectations" -- the moment build_snapshot is
    # implemented and does add the deferred import described in its own
    # docstring, at which point this test should be deleted in favor of
    # asserting the import IS present and deferred.
    tree = _parse(SNAPSHOT_BUILDER_MODULE)
    imports = _imported_names(tree)
    backend_retrieval_imports = [
        name for name, _lineno, _top_level in imports if name.startswith(BACKEND_RETRIEVAL_PREFIX)
    ]
    assert backend_retrieval_imports == [], (
        "snapshot_builder.py now contains a backend.retrieval import -- "
        "build_snapshot() appears to have been implemented. Delete this test "
        "and restore/rely on test_backend_retrieval_only_imported_deferred_* "
        "to assert the import is present AND deferred to a function body."
    )
