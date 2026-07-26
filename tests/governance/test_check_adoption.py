"""Fixture tests for the advisory governance checks in
`scripts/governance/check_adoption.py`.

Why these exist: A-10 (attestation field completeness) was written against the
Constitution's section 13 paragraph 2 element list and then pointed at a
directory holding two document kinds, with literal regexes that had never been
run against the shipped templates. The result was a check that could not pass
against the very artifacts the adoption revision is required to contain, and
nothing detected that. These tests close that class of defect: every element
matcher is exercised against the real template text, and each negative fixture
asserts that removing an element actually fails.

These tests validate the *check*, not the repository. They do not assert that
the repository is conforming and confer no authority (Constitution section 4
paragraph 4).
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CHECK_PATH = REPO / "scripts" / "governance" / "check_adoption.py"
TEMPLATES = REPO / "governance" / "activation" / "templates"
ADOPTER_TEMPLATE = TEMPLATES / "ADOPTER_ATTESTATION.template.md"
REVIEWER_TEMPLATE = TEMPLATES / "INDEPENDENT_REVIEWER_ATTESTATION.template.md"


def _load_module():
    spec = importlib.util.spec_from_file_location("p1_check_adoption", CHECK_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ca():
    return _load_module()


def _complete(text: str) -> str:
    """Turn a template into a completed attestation.

    Fills every `[COMPLETE ...]` placeholder and ticks every declaration
    checkbox, which is what an identified human does before committing one.
    """
    text = re.sub(r"\[COMPLETE[^\]]*\]", "recorded-value", text)
    text = re.sub(r"^([ \t]*[-*][ \t]+)\[[ \t]\]", r"\1[x]", text, flags=re.MULTILINE)
    return text


@pytest.fixture
def attestations(tmp_path, ca, monkeypatch):
    """Point the checks at a temporary repository root and return its
    attestation directory."""
    att = tmp_path / "governance" / "attestations"
    att.mkdir(parents=True)
    monkeypatch.setattr(ca, "ROOT", tmp_path)
    return att


# --------------------------------------------------------------------------
# The defect this suite exists to prevent
# --------------------------------------------------------------------------
def test_both_shipped_templates_pass_when_completed(ca, attestations):
    """A-10 must PASS against the completed form of both shipped templates.

    This is the assertion the manifest's expected post-merge result depends on
    ("A-10 attestation completeness | pass"). Before schema dispatch, the
    adopter document was missing six of the eight reviewer elements and the
    reviewer document failed on markdown emphasis, so this expectation was
    unreachable.
    """
    (attestations / "ADOPTER_ATTESTATION.md").write_text(
        _complete(ADOPTER_TEMPLATE.read_text(encoding="utf-8")), encoding="utf-8"
    )
    (attestations / "INDEPENDENT_REVIEWER_ATTESTATION.md").write_text(
        _complete(REVIEWER_TEMPLATE.read_text(encoding="utf-8")), encoding="utf-8"
    )

    r = ca.check_attestations()
    assert r.status == "PASS", r.items
    assert r.check == "A-10"


def test_adopter_is_not_held_to_reviewer_only_elements(ca, attestations):
    """The adopter is the author of the change; requiring a non-authorship
    declaration of them is the schema-dispatch defect, not a real element."""
    (attestations / "ADOPTER_ATTESTATION.md").write_text(
        _complete(ADOPTER_TEMPLATE.read_text(encoding="utf-8")), encoding="utf-8"
    )

    r = ca.check_attestations()
    assert r.status == "PASS", r.items
    assert "non-authorship declaration" not in " ".join(r.items)
    assert "non-authorship declaration" not in ca.ADOPTER_ELEMENTS
    assert "non-authorship declaration" in ca.REVIEWER_ELEMENTS


@pytest.mark.parametrize(
    "written",
    [
        "I am **not** an author of the reviewed change.",
        "I am not an author of the reviewed change.",
        "I am *not* an author of the reviewed change.",
        "I am __not__ an author of the reviewed change.",
    ],
)
def test_non_authorship_matcher_survives_markdown_emphasis(ca, written):
    """The shipped reviewer template writes `**not** an author`. A bare literal
    `not an author` does not match it, which made the reviewer document fail
    too — a defect the first independent review did not detect."""
    assert ca.REVIEWER_ELEMENTS["non-authorship declaration"].search(written)


# --------------------------------------------------------------------------
# Negative fixtures — each element must actually be load-bearing
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "element,line",
    [
        ("non-authorship declaration", r".*not[\W_]{0,6}an[\W_]{1,6}author.*"),
        ("competence", r".*[Cc]ompetence.*"),
        ("conflict disclosure", r".*[Cc]onflict.*"),
    ],
)
def test_removing_a_reviewer_element_fails(ca, attestations, element, line):
    text = _complete(REVIEWER_TEMPLATE.read_text(encoding="utf-8"))
    stripped = "\n".join(l for l in text.splitlines() if not re.fullmatch(line, l))
    assert stripped != text, "fixture did not remove anything"
    (attestations / "INDEPENDENT_REVIEWER_ATTESTATION.md").write_text(stripped, encoding="utf-8")

    r = ca.check_attestations()
    assert r.status == "FAIL"
    assert element in " ".join(r.items)


def test_unfilled_placeholder_fails(ca, attestations):
    text = _complete(REVIEWER_TEMPLATE.read_text(encoding="utf-8"))
    text = text.replace("recorded-value", "[COMPLETE]", 1)
    (attestations / "INDEPENDENT_REVIEWER_ATTESTATION.md").write_text(text, encoding="utf-8")

    r = ca.check_attestations()
    assert r.status == "FAIL"
    assert "unfilled [COMPLETE] placeholder" in " ".join(r.items)


def test_unticked_declaration_fails(ca, attestations):
    """An unticked box is not a declaration. Section 13 paragraph 2 requires the
    reviewer to *declare* non-authorship, not to be presented with the option."""
    text = _complete(REVIEWER_TEMPLATE.read_text(encoding="utf-8"))
    text = text.replace("- [x]", "- [ ]", 1)
    (attestations / "INDEPENDENT_REVIEWER_ATTESTATION.md").write_text(text, encoding="utf-8")

    r = ca.check_attestations()
    assert r.status == "FAIL"
    assert "unticked declaration" in " ".join(r.items)


# --------------------------------------------------------------------------
# Fail-closed behaviour (section 12 paragraph 1)
# --------------------------------------------------------------------------
def test_empty_directory_is_not_verified_never_pass(ca, attestations):
    r = ca.check_attestations()
    assert r.status == "NOT_VERIFIED"


def test_unclassifiable_file_is_not_verified_never_pass(ca, attestations):
    """A file matching no element set was not assessed. Reporting PASS would
    claim conformance for a criterion nothing evaluated."""
    (attestations / "SOMETHING.md").write_text("# no kind marker\n", encoding="utf-8")

    r = ca.check_attestations()
    assert r.status == "NOT_VERIFIED"
    assert "document kind not declared" in " ".join(r.items)


def test_declared_kind_marker_overrides_filename(ca, attestations):
    """Dispatch is by declared kind first, so renaming a file cannot silently
    change which element set applies to it."""
    text = _complete(ADOPTER_TEMPLATE.read_text(encoding="utf-8"))
    (attestations / "REVIEWER_LOOKING_NAME.md").write_text(text, encoding="utf-8")

    r = ca.check_attestations()
    assert r.status == "PASS", r.items
    assert "=adopter" in r.detail


def test_shipped_templates_declare_their_kind(ca):
    for p in (ADOPTER_TEMPLATE, REVIEWER_TEMPLATE):
        text = p.read_text(encoding="utf-8")
        assert ca.attestation_kind(p, text) is not None
        assert ca.KIND_MARKER.search(text), f"{p.name} has no declared kind marker"


def test_uncompleted_templates_would_fail(ca, attestations):
    """Guard against the opposite error: the raw templates must not pass. They
    are templates, not attestations."""
    (attestations / "ADOPTER_ATTESTATION.md").write_text(
        ADOPTER_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (attestations / "INDEPENDENT_REVIEWER_ATTESTATION.md").write_text(
        REVIEWER_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8"
    )

    r = ca.check_attestations()
    assert r.status == "FAIL"
    assert "unfilled [COMPLETE] placeholder" in " ".join(r.items)
