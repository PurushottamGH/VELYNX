"""Shared raw-document construction helpers for frontmatter tests."""

from __future__ import annotations

QUESTION_METADATA = """\
id: P1-Q000001
title: Example title
object_type: question
status: draft
schema_version: "1.0"
created: "2026-01-01T00:00:00Z"
last_reviewed: null
created_by: pi
provenance: []
selected: false
scope: "Explicit scope"
"""

QUESTION_BODY = """\
## Research Question
Text.

## Rationale
Text.

## Scope
Text.

## Selection Criteria
Text.
"""


def make_raw(
    metadata_yaml: str = QUESTION_METADATA, body: str = QUESTION_BODY, newline: str = "\n"
) -> bytes:
    """Build raw bytes with the given line-ending style.

    `metadata_yaml` and `body` must use bare "\\n" internally; this
    function performs a single, unambiguous conversion to CRLF so that
    "\\r\\n" sequences are never double-converted.
    """
    text = f"---\n{metadata_yaml}---\n{body}"
    if newline == "\r\n":
        text = text.replace("\n", "\r\n")
    elif newline != "\n":
        raise ValueError(f"Unsupported newline: {newline!r}")
    return text.encode("utf-8")
