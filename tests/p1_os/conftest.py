"""Shared pytest configuration for the P1 Research OS Milestone 1 tests.

`p1_os` is an installable package (p1/tooling/pyproject.toml, Milestone
1.1 task 5): `pip install -e p1/tooling` puts it on the interpreter's
import path like any other dependency, so it needs no pytest-only
sys.path insertion here. Only the local test-helper modules
(helpers.py, payloads.py), which are not part of the installable
package, still need their directory added explicitly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOLING_DIR = _REPO_ROOT / "p1" / "tooling"
_TESTS_P1_OS_DIR = Path(__file__).resolve().parent

if str(_TESTS_P1_OS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_P1_OS_DIR))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return _REPO_ROOT


@pytest.fixture(scope="session")
def tooling_dir() -> Path:
    return _TOOLING_DIR


@pytest.fixture(scope="session")
def templates_dir() -> Path:
    return _REPO_ROOT / "p1" / "templates"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return _REPO_ROOT / "tests" / "fixtures" / "p1_os"


@pytest.fixture(scope="session")
def records_root() -> Path:
    return _REPO_ROOT / "p1" / "records"


@pytest.fixture(scope="session")
def all_template_names() -> tuple[str, ...]:
    return (
        "research_artifact",
        "question",
        "unknown",
        "claim",
        "source",
        "evidence",
        "hypothesis",
        "experiment",
        "result",
        "interpretation",
        "decision",
        "principle_candidate",
    )
