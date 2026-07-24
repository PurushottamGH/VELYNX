"""Tests for canonical path and filename validation (spec section 19)."""

from __future__ import annotations

from pathlib import Path

import pytest

from p1_os.paths import (
    RECORD_DIR_BY_OBJECT_TYPE,
    InvalidPathError,
    expected_relative_path,
    validate_record_path,
)


@pytest.fixture
def root(tmp_path: Path) -> Path:
    records = tmp_path / "p1" / "records"
    for dirname in RECORD_DIR_BY_OBJECT_TYPE.values():
        (records / dirname).mkdir(parents=True)
    return tmp_path / "p1"


@pytest.mark.parametrize("object_type,dirname", list(RECORD_DIR_BY_OBJECT_TYPE.items()))
def test_canonical_path_for_every_object_type(root: Path, object_type, dirname):
    prefix = {
        "research_artifact": "P1-AR",
        "question": "P1-Q",
        "unknown": "P1-U",
        "claim": "P1-C",
        "source": "P1-S",
        "evidence": "P1-V",
        "hypothesis": "P1-H",
        "experiment": "P1-E",
        "result": "P1-R",
        "interpretation": "P1-I",
        "decision": "P1-D",
        "principle_candidate": "P1-P",
    }[object_type]
    identifier = f"{prefix}000001"
    path = root / "records" / dirname / f"{identifier}.md"
    resolved = validate_record_path(path, root, object_type, identifier)
    assert resolved == path.absolute()
    assert expected_relative_path(object_type, identifier).parts == ("records", dirname, f"{identifier}.md")


def test_wrong_directory_fails(root: Path):
    path = root / "records" / "questions" / "P1-C000001.md"
    with pytest.raises(InvalidPathError):
        validate_record_path(path, root, "claim", "P1-C000001")


def test_filename_not_matching_id_fails(root: Path):
    path = root / "records" / "claims" / "P1-C000002.md"
    with pytest.raises(InvalidPathError):
        validate_record_path(path, root, "claim", "P1-C000001")


def test_uppercase_extension_fails(root: Path):
    path = root / "records" / "claims" / "P1-C000001.MD"
    with pytest.raises(InvalidPathError):
        validate_record_path(path, root, "claim", "P1-C000001")


def test_title_slug_in_filename_fails(root: Path):
    path = root / "records" / "claims" / "P1-C000001-my-claim.md"
    with pytest.raises(InvalidPathError):
        validate_record_path(path, root, "claim", "P1-C000001")


def test_nested_subdirectory_fails(root: Path):
    path = root / "records" / "claims" / "nested" / "P1-C000001.md"
    with pytest.raises(InvalidPathError):
        validate_record_path(path, root, "claim", "P1-C000001")


def test_case_sensitive_directory_fails(root: Path):
    path = root / "records" / "Claims" / "P1-C000001.md"
    with pytest.raises(InvalidPathError):
        validate_record_path(path, root, "claim", "P1-C000001")


def test_path_outside_root_fails(tmp_path: Path, root: Path):
    outside = tmp_path.parent / "records" / "claims" / "P1-C000001.md"
    with pytest.raises(InvalidPathError):
        validate_record_path(outside, root, "claim", "P1-C000001")


def test_identifier_object_type_mismatch_fails(root: Path):
    path = root / "records" / "claims" / "P1-Q000001.md"
    with pytest.raises(InvalidPathError):
        validate_record_path(path, root, "claim", "P1-Q000001")


def test_validator_never_creates_or_moves_files(root: Path):
    path = root / "records" / "claims" / "P1-C000001.md"
    assert not path.exists()
    validate_record_path(path, root, "claim", "P1-C000001")
    assert not path.exists()
