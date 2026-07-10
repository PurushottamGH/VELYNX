"""Hidden-state / mutable-global tripwires for program_a.mechanism.emission.

``emission.py`` carries the ONE sanctioned mutable global in the whole
program_a package: ``_DEFAULT_INSTANCE``, set via the module-private
``_configure()`` setter (PROGRAM_A_MODULE_SPEC.md Section 9: "No mutable
global state beyond the one-time configured snapshot handle."). Every public
function/method in this module is still a phase-9 stub, so these tests cannot
yet exercise real answer-construction behavior -- they instead pin the
*shape* of the sanctioned global today, so that:

1. a future implementation that adds a SECOND mutable global, or that starts
   mutating _DEFAULT_INSTANCE from an unexpected call site, is caught, and
2. cross-test isolation is asserted explicitly rather than assumed: module
   state set by ``_configure()`` in one test must not leak into another test
   via Python's module-import cache.

Scope: tests only, no production-code changes.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from program_a.mechanism import emission

EMISSION_MODULE_PATH = Path(emission.__file__)


# --------------------------------------------------------------------------- #
# Static sweep: exactly one module-level `global` statement in the whole file
# --------------------------------------------------------------------------- #


def _global_statements(tree: ast.Module) -> list[ast.Global]:
    found: list[ast.Global] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            found.append(node)
    return found


def test_emission_module_declares_exactly_one_global_name() -> None:
    tree = ast.parse(EMISSION_MODULE_PATH.read_text(encoding="utf-8-sig"), filename=str(EMISSION_MODULE_PATH))
    global_stmts = _global_statements(tree)
    all_names = {name for stmt in global_stmts for name in stmt.names}
    assert all_names == {"_DEFAULT_INSTANCE"}, (
        f"expected exactly one sanctioned mutable global (_DEFAULT_INSTANCE); "
        f"found {all_names!r}. A new module-level mutable global was added "
        "without an accompanying spec change (PROGRAM_A_MODULE_SPEC.md "
        "Section 9 forbids more than the one sanctioned handle)."
    )


def test_only_one_function_in_the_module_declares_global() -> None:
    tree = ast.parse(EMISSION_MODULE_PATH.read_text(encoding="utf-8-sig"), filename=str(EMISSION_MODULE_PATH))
    mutating_functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(isinstance(n, ast.Global) for n in ast.walk(node)):
                mutating_functions.append(node.name)
    assert mutating_functions == ["_configure"], (
        f"expected only _configure() to mutate module state via `global`; "
        f"found: {mutating_functions!r}. Any other function reassigning "
        "_DEFAULT_INSTANCE is a hidden-state / process-order-dependence risk "
        "(PROGRAM_A_FINAL_ARCHITECTURE.md Section 4 PA-4: 'stateless across "
        "calls ... no caches that observe call order')."
    )


def test_no_other_module_level_mutable_containers_besides_the_sanctioned_global() -> None:
    # Sweep for module-level list/dict/set literals bound to a name -- these
    # are the classic "hidden shared mutable state" shape (a cache dict, an
    # accumulator list) that would violate PA-4's statelessness guarantee.
    # `__all__` (and other dunders) are excluded: a module export list is not
    # a hidden-state risk, it's the public-surface declaration every module
    # in this package uses.
    tree = ast.parse(EMISSION_MODULE_PATH.read_text(encoding="utf-8-sig"), filename=str(EMISSION_MODULE_PATH))
    suspicious: list[str] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            if not (name.startswith("__") and name.endswith("__")) and isinstance(
                stmt.value, (ast.List, ast.Dict, ast.Set)
            ):
                suspicious.append(name)
        elif isinstance(stmt, ast.Assign):
            if isinstance(stmt.value, (ast.List, ast.Dict, ast.Set)):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and not (
                        target.id.startswith("__") and target.id.endswith("__")
                    ):
                        suspicious.append(target.id)
    assert suspicious == [], (
        f"found module-level mutable container literal(s) {suspicious!r} in "
        "emission.py -- these are hidden shared-state risks distinct from "
        "the one sanctioned _DEFAULT_INSTANCE handle."
    )


# --------------------------------------------------------------------------- #
# Runtime behavior of the sanctioned global (shape available today)
# --------------------------------------------------------------------------- #


def test_default_instance_starts_none_at_fresh_import() -> None:
    # Reload to get a truly fresh module state, independent of whatever other
    # test modules in this same pytest session may have imported/mutated
    # program_a.mechanism.emission before this test ran.
    import importlib

    fresh = importlib.reload(emission)
    assert fresh._DEFAULT_INSTANCE is None


def test_configure_mutates_module_global_in_place(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(emission, "_DEFAULT_INSTANCE", None, raising=True)
    sentinel = object()
    emission._configure(sentinel)  # type: ignore[arg-type]
    assert emission._DEFAULT_INSTANCE is sentinel
    # monkeypatch restores _DEFAULT_INSTANCE to None on teardown, so this
    # mutation does not leak into subsequent tests.


def test_configure_overwrites_rather_than_accumulates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(emission, "_DEFAULT_INSTANCE", None, raising=True)
    first, second = object(), object()
    emission._configure(first)  # type: ignore[arg-type]
    emission._configure(second)  # type: ignore[arg-type]
    # A single scalar slot, not an accumulating list/registry -- calling
    # _configure twice must silently replace, not grow hidden state.
    assert emission._DEFAULT_INSTANCE is second


def test_default_instance_mutation_does_not_leak_across_test_boundary() -> None:
    # This test intentionally runs AFTER the two _configure tests above (test
    # collection order within a module is source order) without monkeypatch,
    # to prove their monkeypatch-based cleanup actually worked and the
    # process-global did not leak between tests.
    assert emission._DEFAULT_INSTANCE is None, (
        "_DEFAULT_INSTANCE leaked a non-None value across test boundaries -- "
        "either a prior test failed to clean up via monkeypatch, or "
        "_configure() has a hidden additional mutation path."
    )


# --------------------------------------------------------------------------- #
# Stub-contract cross-check (still true today; documents WHY the global is
# inert right now -- both convenience wrappers ignore it and always raise)
# --------------------------------------------------------------------------- #


def test_module_level_wrappers_do_not_yet_read_default_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    # Once phase-9 lands, answer_query()/mechanism_id() are specced to
    # delegate to _DEFAULT_INSTANCE. Today they must raise regardless of
    # whether _DEFAULT_INSTANCE is configured -- proving the global is
    # currently inert (not silently half-wired).
    monkeypatch.setattr(emission, "_DEFAULT_INSTANCE", object(), raising=True)
    with pytest.raises(NotImplementedError):
        emission.answer_query("q", seed=1)
    with pytest.raises(NotImplementedError):
        emission.mechanism_id()
