"""Traceability guard for RS-1's own verification mapping.

RS-1 §11 carries the item "Every MUST in this document appears in the §9
mapping". That claim decays the moment a requirement is added without a mapping
row, and nothing detected it before. This test derives the set of RS-1 sections
carrying a MUST or MUST NOT and asserts each one is cited in the §9 mapping
table.

This is a validation artifact, not a governance check: it has no `A-xx`
identifier, produces no conformance verdict, and confers no authority
(Constitution §4 ¶4). It exists so the §11 claim is reproducible.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RS1 = REPO / "governance" / "activation" / "RS-1_RESEARCH_STANDARD.draft.md"

# Sections deliberately outside the mapping, each with a testable reason.
EXCLUDED = {
    # The Draft notice describes what the MUSTs below would do; it states none.
    "(header)",
    # §9 is the mapping itself and §9.1 the procedures: mapping the mapping is
    # circular. Their MUSTs are statements about how citation works.
    "§9",
    "§9.1",
    # §11 is the pre-activation checklist: a work register, not a requirement.
    "§11",
    # §10.2 is the versioning scheme; it states no MUST.
    "§10.2",
}

HEADING = re.compile(r"^##\s+(\d+)\.\s")
SUBHEADING = re.compile(r"^###\s+(\d+\.\d+)\s")
BOLD_CLAUSE = re.compile(r"^\*\*(\d+(?:\.\d+)+)\s")
MUST = re.compile(r"\bMUST\b")


def _sections_with_musts(lines: list[str]) -> dict[str, int]:
    section = "(header)"
    found: dict[str, int] = {}
    for n, line in enumerate(lines, 1):
        h = HEADING.match(line)
        if h:
            section = f"§{h.group(1)}"
        s = SUBHEADING.match(line)
        if s:
            section = f"§{s.group(1)}"
        b = BOLD_CLAUSE.match(line)
        if b:
            section = f"§{b.group(1)}"
        if MUST.search(line):
            found.setdefault(section, n)
    return found


def _mapping_sections(text: str) -> set[str]:
    """Section ids cited in the left-hand column of the §9 mapping table."""
    start = text.index("## 9. Verification mapping")
    end = text.index("### 9.1 Named manual review procedures")
    body = text[start:end]
    cited = set()
    for row in re.findall(r"^\|\s*(§[\d.]+)", body, re.MULTILINE):
        cited.add(row.rstrip("."))
    return cited


def test_every_rs1_must_section_is_in_the_section_9_mapping():
    text = RS1.read_text(encoding="utf-8")
    with_musts = _sections_with_musts(text.splitlines())
    cited = _mapping_sections(text)

    unmapped = {
        sec: line for sec, line in with_musts.items() if sec not in EXCLUDED and sec not in cited
    }
    assert not unmapped, "RS-1 sections carrying a MUST with no §9 mapping row: " + ", ".join(
        f"{s} (first at line {l})" for s, l in sorted(unmapped.items())
    )


def test_mapping_cites_no_section_that_does_not_exist():
    text = RS1.read_text(encoding="utf-8")
    cited = _mapping_sections(text)
    assert cited, "no mapping rows parsed — the table format changed"
    for sec in cited:
        num = sec.lstrip("§")
        top = num.split(".")[0]
        assert re.search(
            rf"^##\s+{top}\.\s", text, re.MULTILINE
        ), f"mapping cites {sec} but no section {top} exists"
        if "." in num:
            assert re.search(rf"\*\*{re.escape(num)}\s", text) or re.search(
                rf"^###\s+{re.escape(num)}\s", text, re.MULTILINE
            ), f"mapping cites {sec} but no such clause exists"


def test_mapping_cites_no_procedure_that_does_not_exist():
    """§12 ¶1's rule for checks applies equally to procedures: citing one makes
    its existence load-bearing for the claim it supports."""
    text = RS1.read_text(encoding="utf-8")
    start = text.index("## 9. Verification mapping")
    end = text.index("### 9.1 Named manual review procedures")
    cited = set(re.findall(r"`(P-\d{1,2})`", text[start:end]))
    defined = set(re.findall(r"^\|\s*`(P-\d{1,2})`\s*\|", text[end:], re.MULTILINE))
    assert cited, "no procedures cited — the mapping format changed"
    missing = sorted(cited - defined)
    assert not missing, f"mapping cites undefined procedures: {missing}"


def test_every_defined_procedure_is_used():
    """A procedure defined and never cited is dead weight that a reviewer would
    have to guess the scope of."""
    text = RS1.read_text(encoding="utf-8")
    end = text.index("### 9.1 Named manual review procedures")
    defined = set(re.findall(r"^\|\s*`(P-\d{1,2})`\s*\|", text[end:], re.MULTILINE))
    body = text[:end] + text[end:]
    unused = sorted(p for p in defined if len(re.findall(rf"`{p}`", body)) < 2)
    assert not unused, f"procedures defined but never cited: {unused}"


def test_mapping_marks_unbuilt_checks_and_cites_no_other_namespace():
    """Every A-11..A-15 citation must carry [NOT IMPLEMENTED]; no C-xx or DA-xx
    identifier may appear in RS-1 (§11 ¶3, §12 ¶1)."""
    text = RS1.read_text(encoding="utf-8")
    for cid in ("A-11", "A-12", "A-13", "A-14", "A-15"):
        for line in text.splitlines():
            if cid in line and line.lstrip().startswith("|"):
                assert (
                    "[NOT IMPLEMENTED]" in line
                ), f"{cid} cited without the unbuilt marker: {line.strip()[:120]}"
    assert not re.search(r"(?<![A-Za-z])C-\d\d", text), "C-xx namespace is withdrawn"
    assert (
        not re.search(r"(?<![A-Za-z])DA-\d\d(?!.*segregated)", text)
        or "segregated `DA-xx` namespace" in text
    ), "RS-1 must not cite design-register identifiers as checks"
