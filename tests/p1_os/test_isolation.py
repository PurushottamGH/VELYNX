"""Import-isolation tests (spec section 22).

P1 tooling must not depend on backend, frontend, infra, VELYNX runtime
databases, remote APIs, or background services. These tests run the
import in a fresh subprocess so we observe a clean sys.modules, not one
already polluted by whatever else pytest itself has imported.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

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


def _run_isolated_import(tooling_dir: str, import_statement: str) -> set[str]:
    script = textwrap.dedent(
        f"""
        import sys
        sys.path.insert(0, {tooling_dir!r})
        {import_statement}
        print("\\n".join(sorted(sys.modules.keys())))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.split("\n"))


def test_importing_p1_os_top_level_does_not_load_forbidden_modules(tooling_dir):
    modules = _run_isolated_import(str(tooling_dir), "import p1_os")
    for forbidden in FORBIDDEN_MODULES:
        assert not any(
            m == forbidden or m.startswith(forbidden + ".") for m in modules
        ), f"{forbidden!r} was imported as a side effect of `import p1_os`"


def test_importing_schemas_does_not_load_forbidden_modules(tooling_dir):
    modules = _run_isolated_import(str(tooling_dir), "import p1_os.schemas")
    for forbidden in FORBIDDEN_MODULES:
        assert not any(
            m == forbidden or m.startswith(forbidden + ".") for m in modules
        ), f"{forbidden!r} was imported as a side effect of `import p1_os.schemas`"


def test_importing_frontmatter_does_not_load_forbidden_modules(tooling_dir):
    modules = _run_isolated_import(str(tooling_dir), "import p1_os.frontmatter")
    for forbidden in FORBIDDEN_MODULES:
        assert not any(
            m == forbidden or m.startswith(forbidden + ".") for m in modules
        ), f"{forbidden!r} was imported as a side effect of `import p1_os.frontmatter`"
