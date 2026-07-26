"""Package-installation and import-outside-pytest tests (Milestone 1.1 task 5).

`p1_os` is installed editable into the environment from
`p1/tooling/pyproject.toml` (`pip install -e p1/tooling`); these tests
confirm the installation is real package metadata, not just a pytest
sys.path trick, and that importing `p1_os` works from a plain
interpreter with no repository-specific sys.path manipulation.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
import tomllib
from importlib import metadata
from pathlib import Path

FORBIDDEN_MODULES = (
    "backend",
    "frontend",
    "infra",
    "framework",
    "research",
    "sqlalchemy",
    "redis",
    "chromadb",
    "fastapi",
    "requests",
)


def test_p1_os_is_an_installed_distribution():
    dist = metadata.distribution("p1-os")
    assert dist.version == "0.1.0"


def test_imported_p1_os_is_the_real_package_not_a_shadow(tooling_dir: Path):
    """In-process guard against `tests/p1_os/` shadowing `p1/tooling/p1_os/`.

    A whole-repository pytest session puts `tests/` on sys.path, at which
    point the bare directory `tests/p1_os/` is a candidate namespace
    package named `p1_os`. `PathFinder` runs before the editable install's
    meta-path finder, so without `p1/tooling` on sys.path the namespace
    portion wins, `p1_os.__file__` becomes None, and `p1_os.schemas`
    resolves to the empty `tests/p1_os/schemas/` directory. These
    assertions run in the collecting session itself, so they fail in a
    whole-repository run even though the isolated suite would pass.
    """
    import p1_os
    import p1_os.schemas

    expected_root = tooling_dir / "p1_os"

    assert p1_os.__file__ is not None, (
        "p1_os resolved to a namespace package; the real package at "
        f"{expected_root} was shadowed. __path__={list(p1_os.__path__)}"
    )
    assert Path(p1_os.__file__).resolve() == (expected_root / "__init__.py").resolve()

    assert p1_os.schemas.__file__ is not None, (
        "p1_os.schemas resolved to a namespace package; expected the real "
        f"subpackage at {expected_root / 'schemas'}. "
        f"__path__={list(p1_os.schemas.__path__)}"
    )
    assert (
        Path(p1_os.schemas.__file__).resolve()
        == (expected_root / "schemas" / "__init__.py").resolve()
    )


def test_p1_os_declares_pinned_pydantic_and_pyyaml_dependencies():
    requires = metadata.requires("p1-os") or []
    normalized = {req.split(";")[0].strip() for req in requires}
    assert "pydantic==2.13.4" in normalized
    assert "PyYAML==6.0.3" in normalized


def test_pyproject_declares_p1_os_package(tooling_dir: Path):
    pyproject = tooling_dir / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["name"] == "p1-os"
    assert data["project"]["version"] == "0.1.0"
    assert data["build-system"]["build-backend"] == "setuptools.build_meta"


def test_importable_outside_pytest_with_no_sys_path_insertion(tmp_path: Path):
    """A plain interpreter, cwd outside the repo, no sys.path tricks."""
    script = "import p1_os\nimport p1_os.frontmatter\nimport p1_os.schemas\nprint(p1_os.__file__)\n"
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "p1_os" in result.stdout


def test_importing_installed_p1_os_does_not_load_forbidden_modules(tmp_path: Path):
    script = textwrap.dedent(
        """
        import sys
        import p1_os
        import p1_os.frontmatter
        import p1_os.schemas
        print("\\n".join(sorted(sys.modules.keys())))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    modules = set(result.stdout.split("\n"))
    for forbidden in FORBIDDEN_MODULES:
        assert not any(
            m == forbidden or m.startswith(forbidden + ".") for m in modules
        ), f"{forbidden!r} was imported as a side effect of the installed p1_os package"
