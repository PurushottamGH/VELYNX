"""Tests for the 12 canonical templates (spec section 21)."""

from __future__ import annotations

from pathlib import Path

import pytest

from p1_os.frontmatter import parse_document, serialize_document


@pytest.fixture
def template_path(templates_dir: Path, request) -> Path:
    return templates_dir / f"{request.param}.md"


@pytest.mark.parametrize(
    "template_path",
    [
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
    ],
    indirect=True,
)
class TestTemplate:
    def test_exists(self, template_path: Path):
        assert template_path.is_file()

    def test_uses_lf_only(self, template_path: Path):
        raw = template_path.read_bytes()
        assert b"\r\n" not in raw

    def test_ends_with_exactly_one_lf(self, template_path: Path):
        raw = template_path.read_bytes()
        assert raw.endswith(b"\n")
        assert not raw.endswith(b"\n\n")

    def test_no_bom(self, template_path: Path):
        raw = template_path.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf")

    def test_parses_and_validates(self, template_path: Path):
        raw = template_path.read_bytes()
        doc = parse_document(raw, source_path=template_path)
        assert doc.record.status.value == "draft"
        assert doc.record.schema_version == "1.0"
        assert doc.record.created_by == "pi"
        assert doc.record.created.tzinfo is not None

    def test_round_trips_deterministically(self, template_path: Path):
        raw = template_path.read_bytes()
        doc = parse_document(raw, source_path=template_path)
        once = serialize_document(doc)
        doc2 = parse_document(once.encode("utf-8"))
        twice = serialize_document(doc2)
        assert once == twice


def test_exactly_twelve_templates_exist(templates_dir: Path):
    templates = sorted(p.name for p in templates_dir.glob("*.md"))
    assert templates == [
        "claim.md",
        "decision.md",
        "evidence.md",
        "experiment.md",
        "hypothesis.md",
        "interpretation.md",
        "principle_candidate.md",
        "question.md",
        "research_artifact.md",
        "result.md",
        "source.md",
        "unknown.md",
    ]
