"""Canonical path and filename validation (spec section 19).

Validation only: this module never moves, creates, or otherwise touches
files on disk. Every function takes an explicit root; no path is
hard-coded.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from .identifiers import object_type_for_id

RECORD_DIR_BY_OBJECT_TYPE: dict[str, str] = {
    "research_artifact": "research_artifacts",
    "question": "questions",
    "unknown": "unknowns",
    "claim": "claims",
    "source": "sources",
    "evidence": "evidence",
    "hypothesis": "hypotheses",
    "experiment": "experiments",
    "result": "results",
    "interpretation": "interpretations",
    "decision": "decisions",
    "principle_candidate": "principle_candidates",
}


class InvalidPathError(ValueError):
    """Raised when a record's on-disk location violates Milestone 1 path rules."""


def expected_relative_path(object_type: str, identifier: str) -> PurePosixPath:
    try:
        dirname = RECORD_DIR_BY_OBJECT_TYPE[object_type]
    except KeyError as exc:
        raise InvalidPathError(f"Unknown object type: {object_type!r}") from exc
    return PurePosixPath("records") / dirname / f"{identifier}.md"


def validate_record_path(path: Path, root: Path, object_type: str, identifier: str) -> Path:
    """Validate that `path` is the canonical location for `identifier`/`object_type`.

    Returns the resolved absolute path on success.
    """
    root = Path(root)
    path = Path(path)

    resolved_id_type = object_type_for_id(identifier)
    if resolved_id_type != object_type:
        raise InvalidPathError(
            f"Identifier {identifier!r} belongs to object type {resolved_id_type!r}, "
            f"not {object_type!r}"
        )

    if path.name != f"{identifier}.md":
        raise InvalidPathError(
            f"Filename {path.name!r} must equal '<ID>.md' for identifier {identifier!r}"
        )

    if path.suffix != ".md":
        raise InvalidPathError(f"File extension must be lowercase '.md': {path.name!r}")

    # Lexical (non-filesystem-touching) resolution: `.resolve()` can silently
    # normalize case on case-insensitive filesystems, which would defeat the
    # case-sensitivity rule. `.absolute()` only prepends the cwd and never
    # queries the filesystem.
    try:
        relative = path.absolute().relative_to(root.absolute())
    except ValueError as exc:
        raise InvalidPathError(f"Path {path} is not inside root {root}") from exc

    expected = expected_relative_path(object_type, identifier)
    actual_parts = relative.parts
    expected_parts = expected.parts

    if actual_parts != expected_parts:
        raise InvalidPathError(
            f"Path {PurePosixPath(*actual_parts)} does not match canonical location "
            f"{expected} for object type {object_type!r}"
        )

    return path.absolute()
