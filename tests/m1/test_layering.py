"""The one-way dependency rule, enforced mechanically.

    core  <-  science  <-  benchmarks  <-  experiments/engine  <-  scripts

Architecture documents describe intent; this test is what keeps intent true. A
single convenient import from `core` into the engine would make `core` untestable
in isolation and let engine concerns leak into contracts — and it would not be
noticed by any other test in the suite.

Implemented by parsing imports with `ast` rather than by importing modules, so a
violation is reported as a violation instead of as an ImportError or a cycle.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Iterator, List, Set

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

#: What each layer is allowed to import from, inside this repository.
ALLOWED: Dict[str, Set[str]] = {
    "core": set(),
    "science": {"core", "p1v0"},
    "benchmarks": {"core", "science", "p1v0"},
    "experiments": {"core", "science", "benchmarks", "p1v0", "experiments"},
}

#: Only these top-level names are considered P1 layers; anything else is a
#: third-party or standard-library import and is not this test's business.
LAYER_NAMES = {"core", "science", "benchmarks", "experiments", "p1v0", "scripts", "tests"}

#: Legacy VELYNX packages that predate M1 and share the `experiments/` and
#: `benchmarks/` namespaces. They are outside the M1 platform and are scheduled for
#: migration in M2; excluding them keeps this test about M1's own boundaries.
M1_ROOTS = {
    "core": ["core"],
    "science": ["science"],
    "benchmarks": ["benchmarks/retention", "benchmarks/testing"],
    "experiments": ["experiments/engine"],
}


def python_files(relative: str) -> Iterator[Path]:
    root = REPO_ROOT / relative
    if not root.exists():
        return
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def imported_layers(path: Path) -> Set[str]:
    """Top-level P1 packages a module imports, from both `import` forms."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                head = alias.name.split(".")[0]
                if head in LAYER_NAMES:
                    found.add(head)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import: same package, not a layer crossing
                continue
            if node.module:
                head = node.module.split(".")[0]
                if head in LAYER_NAMES:
                    found.add(head)
    return found


@pytest.mark.parametrize("layer", sorted(ALLOWED))
def test_layer_imports_only_what_it_may(layer: str):
    allowed = ALLOWED[layer] | {layer}
    violations: List[str] = []
    for relative in M1_ROOTS[layer]:
        for path in python_files(relative):
            illegal = imported_layers(path) - allowed
            if illegal:
                violations.append(
                    f"{path.relative_to(REPO_ROOT).as_posix()} imports {sorted(illegal)}"
                )
    assert not violations, f"{layer}/ may only import {sorted(allowed)}:\n" + "\n".join(violations)


def test_core_is_self_contained():
    """`core` must import nothing from P1 at all — that is what makes it a contract
    layer rather than a utility grab-bag."""
    for path in python_files("core"):
        assert imported_layers(path) <= {"core"}, path


def test_core_performs_no_io():
    """No file, path or process access in the contract layer."""
    banned = {"open", "pathlib", "os", "shutil", "subprocess", "json", "csv"}
    offenders: List[str] = []
    for path in python_files("core"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in banned:
                        offenders.append(f"{path.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in banned:
                    offenders.append(f"{path.name}: from {node.module}")
    assert not offenders, "core must not perform IO:\n" + "\n".join(offenders)


def test_engine_never_names_a_mechanism():
    """The engine must not branch on a component name.

    If a mechanism name appeared in the loop, adding a mechanism would mean editing
    the loop — which is the exact coupling the protocols exist to prevent.
    """
    mechanism_names = [
        "surprise",
        "count_model",
        "reservoir",
        "buffer_sample",
        "markov",
        "historical_only",
        "task_balanced",
        "matched_random",
    ]
    engine_source = (REPO_ROOT / "experiments" / "engine" / "engine.py").read_text(encoding="utf-8")
    code_lines = [
        line
        for line in engine_source.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    body = "\n".join(code_lines)
    # Strip docstrings: prose may discuss mechanisms, code may not reference them.
    tree = ast.parse(engine_source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            doc = ast.get_docstring(node)
            if doc:
                docstrings.add(doc)
    for doc in docstrings:
        body = body.replace(doc, "")
    for name in mechanism_names:
        assert name not in body, f"engine.py references mechanism {name!r}"


def test_science_does_not_import_the_engine():
    """A mechanism that needed the runner could not be tested in isolation."""
    for relative in ("science", "benchmarks/retention", "benchmarks/testing"):
        for path in python_files(relative):
            assert "experiments" not in imported_layers(path), path
