"""Identifier-namespace guard (§11 ¶3: identical names MUST NOT conceal
distinct types).

The repository carries several identifier registers that once overlapped:

  A-01..A-15   implemented advisory checks        scripts/governance/check_adoption.py
  DA-01..DA-63 proposed checks (Draft design)    governance/design/05_AUTOMATION_ARCHITECTURE.md
  G-1..G-10    change-D preflight gates          governance/activation/03_...MANIFEST.md
  DG-1..DG-13  proposed stack standards          governance/design/02_GOVERNANCE_STACK.md
  CD-x / CE-x  contents of change D / change E   governance/activation/03_...MANIFEST.md
  E-1..E-13    engineering tasks                 governance/activation/00_...PLAN.md
  X-1..X-7     external blockers                 governance/activation/05_...CHECKLIST.md
  DX-1..DX-15  extension points                  governance/design/07_EXTENSION_...md

This test fails if any of those registers leaks back into another's territory.
Validation artifact: no `A-xx` identifier, no verdict, no authority (§4 ¶4).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DESIGN = REPO / "governance" / "design"
ACTIVATION = REPO / "governance" / "activation"
SCRIPTS = REPO / "scripts" / "governance"
MANIFEST = ACTIVATION / "03_ADOPTION_CHANGE_MANIFEST.md"
PLAN = ACTIVATION / "00_MINIMUM_ACTIVATION_PLAN.md"
CHECKLIST = ACTIVATION / "05_RELEASE_CANDIDATE_CHECKLIST.md"


def _files(root: Path, suffixes=(".md", ".yaml", ".yml", ".py")):
    return [p for p in sorted(root.rglob("*")) if p.is_file() and p.suffix in suffixes]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _hits(text: str, pattern: str) -> list[str]:
    return re.findall(pattern, text)


# --------------------------------------------------------------------------
# The design register must not use a live activation identifier shape
# --------------------------------------------------------------------------
DESIGN_FORBIDDEN = {
    "A-dd (implemented check)": r"(?<![A-Za-z0-9])A-\d\d(?![0-9])",
    "G-d (preflight gate)": r"(?<![A-Za-z0-9])G-\d{1,2}(?![0-9])",
    "D-1..3 (change-D content)": r"(?<![A-Za-z0-9])D-[123](?![0-9])",
    "X-d (external blocker)": r"(?<![A-Za-z0-9])X-\d{1,2}(?![0-9])",
}

# The design set legitimately cites the amendment record's unpadded ids. The
# range is closed: `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md` defines
# A-1..A-7. An unpadded `A-8` is therefore not a citation of anything — it was a
# design proposal wearing a citation's clothes, and is re-keyed `DAM-8`.
DESIGN_ALLOWED_UNPADDED_A = re.compile(r"(?<![A-Za-z0-9])A-([1-7])(?![0-9])")
ANY_UNPADDED_A = re.compile(r"(?<![A-Za-z0-9])A-(\d)(?![0-9])")


def test_design_cites_no_amendment_id_that_does_not_exist():
    """The audit found six citations of "amendment A-8" resolving to nothing:
    the amendment record stops at A-7. An unpadded `A-n` in the design set is
    permitted only where the amendment record actually defines it."""
    record = REPO / "audits" / "CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md"
    defined = set(re.findall(r"^###\s+A-(\d+)\s", _read(record), re.MULTILINE))
    assert defined, "amendment record format changed; cannot verify citations"
    problems = []
    for p in _files(DESIGN):
        for n, line in enumerate(_read(p).splitlines(), 1):
            for m in ANY_UNPADDED_A.finditer(line):
                if m.group(1) not in defined:
                    problems.append(
                        f"{p.name}:{n}: cites A-{m.group(1)}, which the amendment "
                        f"record does not define (defines {sorted(defined)})"
                    )
    assert not problems, "\n".join(problems)


def test_design_unpadded_amendment_citations_are_disambiguated():
    """The only thing separating check `A-05` from amendment `A-5` is padding, so
    an unpadded citation must also carry a word that disambiguates it — any
    inflection of "amend", or a reference to the amendment record itself."""
    ok = re.compile(r"amend|AMENDMENT_RECORD", re.I)
    problems = []
    for p in _files(DESIGN):
        if p.name == "README.md":
            continue  # the disambiguation table names the ids to warn about them
        for n, line in enumerate(_read(p).splitlines(), 1):
            if DESIGN_ALLOWED_UNPADDED_A.search(line) and not ok.search(line):
                problems.append(
                    f"{p.name}:{n}: unpadded A-n with nothing to "
                    f"distinguish it from a check id: {line.strip()[:110]}"
                )
    assert not problems, "\n".join(problems)


def test_design_extension_point_range_is_stated_correctly():
    """`DX-15` was cited in the README while only DX-1..DX-14 exist — in the
    document written to fix identifier hygiene."""
    ext = _read(DESIGN / "07_EXTENSION_ARCHITECTURE.md")
    defined = {int(x) for x in re.findall(r"(?<![A-Za-z0-9])DX-(\d{1,2})(?![0-9])", ext)}
    assert defined, "no DX ids found"
    assert defined == set(range(1, max(defined) + 1)), f"gap: {sorted(defined)}"
    for p in _files(DESIGN):
        cited = {int(x) for x in re.findall(r"(?<![A-Za-z0-9])DX-(\d{1,2})(?![0-9])", _read(p))}
        dangling = sorted(cited - defined)
        assert not dangling, f"{p.name} cites undefined DX-{dangling}"


def test_design_register_uses_no_live_activation_identifier():
    problems = []
    for p in _files(DESIGN):
        # README.md carries the disambiguation table, which must name the live
        # ids in order to warn about them.
        if p.name == "README.md":
            continue
        text = _read(p)
        for label, pattern in DESIGN_FORBIDDEN.items():
            found = _hits(text, pattern)
            if found:
                problems.append(f"{p.name}: {label} -> {sorted(set(found))}")
    assert not problems, "design-space leak into the live namespace:\n" + "\n".join(problems)


def test_live_surface_uses_no_design_identifier():
    """`DA-`, `DG-`, `DD-`, `DX-`, `DF-` belong to governance/design/** only.
    The plan's and README's namespace registers name them on purpose, so those
    two documents are exempt as documentation of the boundary."""
    exempt = {PLAN.name, "README.md"}
    problems = []
    for root in (ACTIVATION, SCRIPTS):
        for p in _files(root):
            if p.name in exempt:
                continue
            found = _hits(_read(p), r"(?<![A-Za-z0-9])D[AGDXF]-\d{1,2}(?![0-9])")
            if found:
                problems.append(f"{p}: {sorted(set(found))}")
    assert not problems, "design identifier used in the live surface:\n" + "\n".join(problems)


# --------------------------------------------------------------------------
# The manifest's change contents are CD-/CE-, never D-/E-
# --------------------------------------------------------------------------
def test_manifest_change_contents_are_rekeyed():
    text = _read(MANIFEST)
    assert re.search(r"^\| CD-1 \|", text, re.MULTILINE), "CD-1 row missing"
    assert re.search(r"^\| CE-1 \|", text, re.MULTILINE), "CE-1 row missing"
    leaked = _hits(text, r"(?<![A-Za-z0-9C])E-[1-9](?![0-9])")
    assert not leaked, f"manifest still uses plan-task shaped ids: {sorted(set(leaked))}"


def test_no_document_cites_a_manifest_item_by_its_old_id():
    """Cross-references must follow the re-key, or a reader lands on the plan's
    engineering task of the same number."""
    problems = []
    for p in _files(ACTIVATION) + _files(REPO / "governance" / "checks"):
        text = _read(p)
        for m in re.finditer(r"manifest items? `(D|E)-(\d{1,2})`", text):
            problems.append(f"{p.name}: manifest item cited as {m.group(0)}")
        for m in re.finditer(r"manifest `(D|E)-(\d{1,2})`", text):
            problems.append(f"{p.name}: manifest item cited as {m.group(0)}")
    assert not problems, "\n".join(problems)


# --------------------------------------------------------------------------
# The check namespace is closed and honest
# --------------------------------------------------------------------------
def test_implemented_check_ids_are_exactly_the_ten_registered():
    text = _read(SCRIPTS / "check_adoption.py")
    names = set(re.findall(r'"(A-\d\d)":', text))
    assert names == {f"A-{i:02d}" for i in range(1, 11)}, names


def test_no_c_namespace_survives_as_a_check_citation():
    """`C-xx` is withdrawn. It may be named only as history — in a "Replaces"
    column or alongside a word marking it as withdrawn — never as an evidence
    route."""
    historical = re.compile(
        r"withdrawn|[Rr]eplaces|had no implementation|" r"^\| `P-A\d`|`C-4`, `C-7`"
    )
    for p in _files(ACTIVATION):
        for line in _read(p).splitlines():
            if re.search(r"(?<![A-Za-z0-9])C-\d{1,2}(?![0-9])", line):
                assert historical.search(
                    line.strip()
                ), f"{p.name}: live citation of a withdrawn C-xx id: {line.strip()[:120]}"


def test_plan_namespace_register_exists_and_is_not_the_old_false_claim():
    text = _read(PLAN)
    assert "**Identifier namespaces.**" in text
    assert (
        "That sentence was, until this revision, false." in text
    ), "the plan must record that its uniqueness claim was false, not silently drop it"
    assert "**One namespace.**" not in text


def test_checklist_records_the_namespace_finding():
    assert "AF-25" in _read(CHECKLIST)
