#!/usr/bin/env python3
"""Advisory constitutional checks for Project P1 adoption readiness.

Authority: none. This script produces findings only. Under
REPOSITORY_CONSTITUTION.md section 4 paragraph 4 an automated system may
propose or check, but MUST NOT supply human authority or independent review.
Under section 12 paragraph 1 an unavailable check is reported as NOT_VERIFIED,
never as passed.

Standard library only, so it runs without installing anything.

Statuses:
  PASS          criterion assessed and satisfied
  FAIL          criterion assessed and violated
  FINDINGS      criterion assessed, items require human disposition
  NOT_VERIFIED  criterion NOT assessed (missing input, unavailable tool)

Exit code 1 if any check is FAIL or NOT_VERIFIED; 0 otherwise. FINDINGS alone
does not fail: dispositioning them is a human judgement, not a check result.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Paths excluded from the "live" surface: archived, generated, tooling state.
EXCLUDED = (
    "archive/", "node_modules/", ".venv", ".git/", "P1.worktrees/", "dist/",
    ".kilo/", ".opencode/", ".agents/", ".commandcode/", ".claude/", ".codex/",
    ".hypothesis/", ".pytest_cache/", "__pycache__/", "governance/design/",
    "governance/activation/",
)

# Section 1 paragraph 2 names exactly four words a document MUST NOT use to
# override the Constitution: canonical, absolute, frozen, authoritative. All four
# are matched bare. The remaining alternatives are paraphrases that assert the
# same supremacy without using one of the four words.
#
# Keep in sync with LEXEMES in scripts/governance/generate_legacy_index.py. The
# Legacy index ranks Tier-2 candidates with that copy, and A-06 verifies banners
# against the index, so a divergence would silently change what A-06 assesses.
AUTHORITY_LEXEMES = re.compile(
    r"\b(absolute|canonical|frozen|authoritative|non-negotiable|"
    r"supersedes all|final authority|single source of truth|must not be violated)\b",
    re.IGNORECASE,
)

REQUIRED_HEADER_FIELDS = ("status", "scope", "responsibility", "authority source")

LEGACY_BANNER_FIRST = "> **LEGACY — no normative authority.**"


@dataclass
class Result:
    check: str
    clause: str
    status: str
    detail: str
    items: list = field(default_factory=list)
    limitation: str = ""


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")


def is_live(p: Path) -> bool:
    r = rel(p)
    return not any(x in r for x in EXCLUDED)


def read(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def git(*args: str) -> tuple[bool, str]:
    try:
        out = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=120
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    if out.returncode != 0:
        return False, out.stderr.strip()
    return True, out.stdout


# --------------------------------------------------------------------------
# A-01  Normative-artifact header completeness  (section 4 paragraph 1)
# --------------------------------------------------------------------------
def check_headers() -> Result:
    targets = [
        ROOT / "REPOSITORY_CONSTITUTION.md",
        ROOT / "governance" / "AR-1_REPOSITORY_ARCHITECTURE_RECORD.md",
    ]
    targets += sorted((ROOT / "governance" / "activation").glob("*.md"))
    targets += sorted((ROOT / "governance" / "standards").glob("*.md"))
    missing = []
    checked = 0
    for t in targets:
        text = read(t)
        if text is None:
            missing.append(f"{rel(t)}: unreadable")
            continue
        head = text[:2500].lower()
        checked += 1
        absent = [f for f in REQUIRED_HEADER_FIELDS if f not in head]
        if absent:
            missing.append(f"{rel(t)}: missing {', '.join(absent)}")
    if not checked:
        return Result("A-01", "S4p1", "NOT_VERIFIED", "no target artifacts found")
    status = "FAIL" if missing else "PASS"
    return Result("A-01", "S4p1", status,
                  f"{checked} artifacts checked for status/scope/responsibility/authority source",
                  missing,
                  "Presence of a field is checked, not its correctness.")


# --------------------------------------------------------------------------
# A-02  Registry <-> Constitution consistency  (section 4 paragraph 1)
# --------------------------------------------------------------------------
def check_registry_consistency() -> Result:
    reg = read(ROOT / "GOVERNANCE_REGISTRY.yaml")
    con = read(ROOT / "REPOSITORY_CONSTITUTION.md")
    if reg is None or con is None:
        return Result("A-02", "S4p1", "NOT_VERIFIED",
                      "GOVERNANCE_REGISTRY.yaml or REPOSITORY_CONSTITUTION.md not readable")
    problems = []
    m_con = re.search(r"^\-?\s*\*?\*?Version:?\*?\*?:?\s*([0-9]+\.[0-9]+\.[0-9]+)",
                      con, re.MULTILINE | re.IGNORECASE)
    m_reg = re.search(r'version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?', reg)
    if not m_con or not m_reg:
        problems.append("version not parseable in one or both artifacts")
    elif m_con.group(1) != m_reg.group(1):
        problems.append(f"version mismatch: artifact {m_con.group(1)} vs registry {m_reg.group(1)}")

    con_active = bool(re.search(r"^\-?\s*\*?\*?Status:?\*?\*?:?\s*Active", con,
                                re.MULTILINE | re.IGNORECASE))
    reg_con_active = bool(re.search(r"constitution:(?:.|\n)*?status:\s*Active", reg))
    if con_active != reg_con_active:
        problems.append(
            f"status disagreement: artifact Active={con_active}, registry Active={reg_con_active}")
    status = "FAIL" if problems else "PASS"
    return Result("A-02", "S4p1", status, "version and status compared", problems,
                  "Textual comparison only; scope and responsibility wording is not diffed.")


# --------------------------------------------------------------------------
# A-03  Adoption element completeness  (section 13 paragraph 3, section 2)
# --------------------------------------------------------------------------
def check_adoption_elements() -> Result:
    reg = read(ROOT / "GOVERNANCE_REGISTRY.yaml")
    con = read(ROOT / "REPOSITORY_CONSTITUTION.md")
    if reg is None or con is None:
        return Result("A-03", "S13p3", "NOT_VERIFIED", "inputs not readable")

    con_active = bool(re.search(r"^\-?\s*\*?\*?Status:?\*?\*?:?\s*Active", con,
                                re.MULTILINE | re.IGNORECASE))
    steward_empty = bool(re.search(r"constitutional_steward:\s*\[\s*\]", reg))
    adopter_null = bool(re.search(r"adopter_attestation:\s*null", reg))
    reviewer_null = bool(re.search(r"independent_reviewer_attestation:\s*null", reg))

    if not con_active:
        # Pre-adoption. The conforming pre-adoption state is: Draft everywhere,
        # empty steward, null attestations.
        drift = []
        if not steward_empty:
            drift.append("steward populated while Constitution is Draft")
        if not (adopter_null and reviewer_null):
            drift.append("attestation field populated while Constitution is Draft")
        status = "FAIL" if drift else "PASS"
        return Result("A-03", "S13p3", status,
                      "pre-adoption state: Constitution is Draft, adoption not attempted",
                      drift,
                      "Cannot detect intent; only that no partial adoption is committed.")

    missing = []
    if steward_empty:
        missing.append("no constitutional steward assigned")
    if adopter_null:
        missing.append("adopter attestation absent")
    if reviewer_null:
        missing.append("independent reviewer attestation absent")
    att_dir = ROOT / "governance" / "attestations"
    if not att_dir.is_dir() or not any(att_dir.glob("*.md")):
        missing.append("governance/attestations/ contains no attestation file")
    # Section 2 lists a transition record among the elements an atomic change must
    # contain, and section 9 paragraph 3 is unqualified as to object type: the
    # Constitution's own Draft -> Active transition needs one.
    tr_dir = ROOT / "governance" / "transitions"
    if not tr_dir.is_dir() or not any(tr_dir.glob("*.md")):
        missing.append("governance/transitions/ contains no transition record (S2, S9p3)")
    status = "FAIL" if missing else "PASS"
    return Result("A-03", "S13p3", status, "adoption elements checked", missing,
                  "Presence only. Whether an attestation names an identified human "
                  "who is not an author is not mechanically decidable (see P-A1). "
                  "Presence of a transition record is checked; its eight section 9 "
                  "paragraph 3 elements are assessed by manual procedure P-A2.")


# --------------------------------------------------------------------------
# A-04  No scientific records exist  (underwrites the dossier N/A discharges)
# --------------------------------------------------------------------------
def check_no_records() -> Result:
    rec = ROOT / "p1" / "records"
    if not rec.is_dir():
        return Result("A-04", "S9p1", "NOT_VERIFIED", "p1/records/ not found")
    files = [rel(p) for p in rec.rglob("*") if p.is_file() and p.name != ".gitkeep"]
    if files:
        return Result("A-04", "S9p1", "FINDINGS",
                      f"{len(files)} record files exist under p1/records/",
                      files[:20],
                      "Each existing record voids the corresponding dossier N/A row "
                      "and must be traced individually.")
    return Result("A-04", "S9p1", "PASS",
                  "p1/records/ contains no record files; sections 5, 6, 7 discharge as "
                  "not applicable with a testable reason", [],
                  "Only this path is checked. Records stored elsewhere are not detected.")


# --------------------------------------------------------------------------
# A-05  Authority and certainty lexemes in live paths  (section 1 paragraph 2)
# --------------------------------------------------------------------------
def check_authority_lexemes() -> Result:
    hits = []
    for p in ROOT.rglob("*.md"):
        if not p.is_file() or not is_live(p):
            continue
        text = read(p)
        if text is None:
            continue
        n = len(AUTHORITY_LEXEMES.findall(text))
        if n:
            hits.append((n, rel(p)))
    hits.sort(reverse=True)
    if not hits:
        return Result("A-05", "S1p2", "PASS", "no authority or certainty lexemes in live paths")
    return Result("A-05", "S1p2", "FINDINGS",
                  f"{sum(n for n, _ in hits)} matches in {len(hits)} live-path files",
                  [f"{n:>4}  {path}" for n, path in hits[:25]],
                  "Lexical only. It cannot tell whether a document reads as authoritative; "
                  "that is manual procedure P-L1. False positives are expected where the "
                  "word appears in a quotation or a prohibition.")


# --------------------------------------------------------------------------
# A-06  Legacy index and banner coverage  (section 4 paragraph 5, section 14)
# --------------------------------------------------------------------------
def check_legacy_index() -> Result:
    idx = ROOT / "governance" / "LEGACY_INDEX.md"
    text = read(idx)
    if text is None:
        return Result("A-06", "S4p5", "NOT_VERIFIED",
                      "governance/LEGACY_INDEX.md absent; required in the adoption revision. "
                      "Generate with scripts/governance/generate_legacy_index.py")
    t2 = re.search(r"<!-- BANNER_REQUIRED_BEGIN -->(.*?)<!-- BANNER_REQUIRED_END -->",
                   text, re.DOTALL)
    t1 = re.search(r"<!-- TIER1_BEGIN -->(.*?)<!-- TIER1_END -->", text, re.DOTALL)
    if not t2:
        return Result("A-06", "S4p5", "NOT_VERIFIED",
                      "LEGACY_INDEX.md has no BANNER_REQUIRED block to assess")
    if not t1:
        # Without the resolved-path block a moved Tier-1 file cannot be located,
        # and skipping it would make the criterion true by construction.
        return Result("A-06", "S4p5", "NOT_VERIFIED",
                      "LEGACY_INDEX.md has no TIER1 block carrying resolved post-move "
                      "paths; Tier-1 banner coverage cannot be assessed. Regenerate with "
                      "scripts/governance/generate_legacy_index.py")

    # Tier 1: `original` -> `current`. Tier 2 stays in place, so current == original.
    entries = [(o, c) for o, c in
               re.findall(r"^\s*-\s*`([^`]+\.md)`\s*->\s*`([^`]+\.md)`", t1.group(1),
                          re.MULTILINE)]
    entries += [(p, p) for p in re.findall(r"`([^`]+\.md)`", t2.group(1))]
    # The Constitution and the README are never Legacy and must never carry a banner.
    entries = [(o, c) for o, c in entries
               if o not in ("REPOSITORY_CONSTITUTION.md", "README.md")]

    missing_banner, unresolvable, moved = [], [], 0
    for original, current in sorted(set(entries)):
        # Accept the listed post-move path first, then the pre-move path. An entry
        # that resolves to neither is reported, never skipped (S12p1).
        target = None
        for cand in (current, original):
            if (ROOT / cand).is_file():
                target = cand
                break
        if target is None:
            unresolvable.append(f"{original} -> {current} (neither path exists)")
            continue
        if target != original:
            moved += 1
        body = read(ROOT / target) or ""
        if LEGACY_BANNER_FIRST not in body[:600]:
            missing_banner.append(target)

    limitation = (
        "Verifies banner presence on Tier-1/Tier-2 entries only. It cannot prove "
        "the index is complete against the tree; see the index's own completeness "
        "statement and manual procedure P-L1. Banners are applied in the adoption "
        "revision, so findings here are expected before then."
    )
    if unresolvable:
        return Result("A-06", "S4p5", "NOT_VERIFIED",
                      f"{len(unresolvable)} index entr(y/ies) resolve to no file in the "
                      f"tree; banner coverage for them is NOT assessed",
                      unresolvable[:15],
                      limitation + " An unresolvable entry means the index is stale "
                      "against the tree: regenerate it before relying on this check.")
    status = "FINDINGS" if missing_banner else "PASS"
    return Result("A-06", "S4p5", status,
                  f"{len(set(entries))} banner-required paths listed by the index "
                  f"({moved} resolved at a post-move path); "
                  f"{len(missing_banner)} lack the banner",
                  missing_banner[:15],
                  limitation)


# --------------------------------------------------------------------------
# A-07  Credentials in history  (section 10 paragraph 5)
# --------------------------------------------------------------------------
def check_secret_history() -> Result:
    patterns = ["*gcp-key*", "*.pem", "*.p12", "*id_rsa*", "*credentials*.json",
                "*service-account*.json", ".env"]
    ok, out = git("log", "--all", "--diff-filter=A", "--name-only",
                  "--pretty=format:", "--", *patterns)
    if not ok:
        return Result("A-07", "S10p5", "NOT_VERIFIED", f"git unavailable or failed: {out}")
    found = sorted({line.strip() for line in out.splitlines() if line.strip()})
    if found:
        return Result("A-07", "S10p5", "FAIL",
                      f"{len(found)} credential-shaped path(s) added in history",
                      found,
                      "Presence is proven; absence is not. A secret committed under an "
                      "unrecognised name is not detected. Deletion does not remediate: "
                      "rotate at the provider.")
    return Result("A-07", "S10p5", "PASS", "no credential-shaped path added in history", [],
                  "Absence is not proven; only these name patterns were searched.")


# --------------------------------------------------------------------------
# A-08  Check honesty  (section 12 paragraph 1)
# --------------------------------------------------------------------------
def check_ci_honesty() -> Result:
    problems = []
    wf = ROOT / ".github" / "workflows"
    if not wf.is_dir():
        return Result("A-08", "S12p1", "NOT_VERIFIED", ".github/workflows not found")
    for p in sorted(wf.glob("*.yml")):
        text = read(p) or ""
        for i, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue  # comments are not executed
            if "|| true" in line:
                problems.append(f"{rel(p)}:{i}: suppressed failure (`|| true`)")
        if "runs-on: ubuntu" in text and "Test-Path" in text:
            problems.append(f"{rel(p)}: PowerShell `Test-Path` in a step running on ubuntu")
    status = "FAIL" if problems else "PASS"
    return Result("A-08", "S12p1", status,
                  "workflow files scanned for suppressed failures and shell mismatch",
                  problems,
                  "A step that cannot fail reports an unavailable check as passed, which "
                  "section 12 paragraph 1 prohibits.")


# --------------------------------------------------------------------------
# A-09  Independent-human plausibility  (section 2, section 13 paragraph 3)
# --------------------------------------------------------------------------
def check_identified_humans() -> Result:
    ok, out = git("log", "--format=%an <%ae>")
    if not ok:
        return Result("A-09", "S13p3", "NOT_VERIFIED", f"git unavailable: {out}")
    authors = {line.strip() for line in out.splitlines() if line.strip()}
    nonroutable = sorted(a for a in authors if "@local" in a or "@" not in a)
    detail = f"{len(authors)} distinct git author identit(y/ies) in history"
    items = sorted(authors)
    if len(authors) < 2:
        return Result("A-09", "S13p3", "FINDINGS", detail + " — section 13 paragraph 3 "
                      "requires two identified humans at adoption", items,
                      "Git identity is not identity. A second git author would not by "
                      "itself satisfy section 2's 'identified human', and this check "
                      "cannot establish that any author is human (section 4 paragraph 4).")
    return Result("A-09", "S13p3", "FINDINGS", detail, items,
                  "Non-routable identities present: " + (", ".join(nonroutable) or "none") +
                  ". Whether a reviewer is independent is not mechanically decidable.")


# --------------------------------------------------------------------------
# A-10  Attestation field completeness  (section 13 paragraph 2)
# --------------------------------------------------------------------------
# governance/attestations/ holds two document kinds, and section 13 gives them
# different required content. Applying one element set to both is what made this
# check unsatisfiable against the shipped templates, so the element set is
# dispatched by declared document kind.
#
#   Independent reviewer attestation — section 13 paragraph 2 fixes its content
#   exactly; each REVIEWER_ELEMENTS entry is one of its clauses.
#
#   Adopter attestation — section 13 paragraph 3 requires it but does not
#   enumerate its content. ADOPTER_ELEMENTS therefore derives from what that
#   paragraph makes the adopter responsible for (adoption of this Constitution,
#   assignment of at least one steward) plus the attested revision and the
#   conclusion, which are what make it reviewable at all. Notably it does NOT
#   include the non-authorship declaration: the adopter IS the author, and
#   requiring that declaration of them was the schema-dispatch defect.
#
# Presence of an element is mechanically decidable; whether the named party is
# an identified human who is not an author is not (section 4 paragraph 4) ->
# procedure P-A1.

# "not an author" survives markdown emphasis: the shipped reviewer template
# writes "I am **not** an author", which a bare literal does not match.
_NOT_AN_AUTHOR = re.compile(r"not[\W_]{0,6}an[\W_]{1,6}author", re.I)
_CONCLUSION = re.compile(r"^#+.*conclusion|conclusion\b", re.I | re.MULTILINE)
_ATTESTED_REVISION = re.compile(r"revision (reviewed|attested)", re.I)

REVIEWER_ELEMENTS = {
    "reviewed revision": _ATTESTED_REVISION,
    "non-authorship declaration": _NOT_AN_AUTHOR,
    "evidence production": re.compile(r"produce[d]? (any )?evidence", re.I),
    "conflict disclosure": re.compile(r"conflict", re.I),
    "review procedure": re.compile(r"review procedure|procedure actually used", re.I),
    "conclusion": _CONCLUSION,
    "competence": re.compile(r"competence", re.I),
    "records examined": re.compile(r"records,? (artifacts,? )?(and )?checks examined|"
                                   r"artifacts? examined", re.I),
}

ADOPTER_ELEMENTS = {
    "attested revision": _ATTESTED_REVISION,
    "identified human": re.compile(r"identified human", re.I),
    "adoption declaration": re.compile(r"\bI adopt\b", re.I),
    "authorship disclosure": re.compile(r"author of this change", re.I),
    "steward assignment": re.compile(r"constitutional steward", re.I),
    "acknowledged limitations": re.compile(r"limitation", re.I),
    "conclusion": _CONCLUSION,
}

ATTESTATION_SCHEMAS = {
    "independent_reviewer": REVIEWER_ELEMENTS,
    "adopter": ADOPTER_ELEMENTS,
}

# The kind is declared in the document, so dispatch does not depend on a
# filename convention. The filename is a fallback only; a file matching neither
# is reported NOT_VERIFIED, never passed (section 12 paragraph 1).
KIND_MARKER = re.compile(r"<!--\s*attestation-kind:\s*(adopter|independent_reviewer)\s*-->",
                         re.I)

PLACEHOLDER = re.compile(r"\[COMPLETE[^\]]*\]")
# A declaration left unticked is not a declaration. Matches markdown task-list
# items only, not `[ ]` inside a table cell.
UNTICKED = re.compile(r"^[ \t]*[-*][ \t]+\[[ \t]\]", re.MULTILINE)


def attestation_kind(path: Path, text: str) -> str | None:
    m = KIND_MARKER.search(text)
    if m:
        return m.group(1).lower()
    name = path.name.upper()
    if "ADOPTER" in name:
        return "adopter"
    if "REVIEWER" in name:
        return "independent_reviewer"
    return None


def check_attestations() -> Result:
    att_dir = ROOT / "governance" / "attestations"
    files = sorted(att_dir.glob("*.md")) if att_dir.is_dir() else []
    if not files:
        # Not "passed": the criterion was not assessed, because its subject does
        # not exist yet. Section 12 paragraph 1 requires NOT_VERIFIED here.
        return Result("A-10", "S13p2", "NOT_VERIFIED",
                      "no attestation exists at this revision; section 13 paragraph 2 "
                      "completeness cannot be assessed before the adoption revision",
                      [],
                      "Expected before change D. This check reports PASS only against a "
                      "non-empty set of attestation files.")
    problems = []
    unclassified = []
    kinds = []
    for f in files:
        text = read(f)
        if text is None:
            problems.append(f"{rel(f)}: unreadable")
            continue
        kind = attestation_kind(f, text)
        if kind is None:
            # Not assessed: no element set applies. Reporting PASS here would
            # assess nothing and claim conformance (section 12 paragraph 1).
            unclassified.append(
                f"{rel(f)}: document kind not declared and not inferable from the "
                f"filename; expected an `<!-- attestation-kind: adopter | "
                f"independent_reviewer -->` marker")
            continue
        kinds.append(f"{rel(f)}={kind}")
        absent = [name for name, pat in ATTESTATION_SCHEMAS[kind].items()
                  if not pat.search(text)]
        if absent:
            problems.append(f"{rel(f)} [{kind}]: missing {', '.join(absent)}")
        left = len(PLACEHOLDER.findall(text))
        if left:
            problems.append(f"{rel(f)} [{kind}]: {left} unfilled [COMPLETE] placeholder(s)")
        unticked = len(UNTICKED.findall(text))
        if unticked:
            problems.append(f"{rel(f)} [{kind}]: {unticked} unticked declaration "
                            f"checkbox(es); an unticked box is not a declaration")

    detail = (f"{len(files)} attestation file(s) checked against the element set for "
              f"their declared kind ({'; '.join(kinds) if kinds else 'none classified'}), "
              f"and for unfilled placeholders and unticked declarations")
    limitation = ("Lexical presence only. That an element appears does not make its "
                  "content true, and whether the named party is an identified human who "
                  "is not an author is not mechanically decidable (section 4 paragraph "
                  "4) — that is procedure P-A1. The adopter element set is derived from "
                  "section 13 paragraph 3, which does not enumerate content the way "
                  "paragraph 2 does for the reviewer; it is a floor, not a closed list.")
    if unclassified:
        return Result("A-10", "S13p2", "NOT_VERIFIED",
                      "one or more attestation files could not be matched to an element "
                      "set, so their completeness was NOT assessed",
                      unclassified + problems, limitation)
    status = "FAIL" if problems else "PASS"
    return Result("A-10", "S13p2", status, detail, problems, limitation)


CHECKS = [
    check_headers, check_registry_consistency, check_adoption_elements,
    check_no_records, check_authority_lexemes, check_legacy_index,
    check_secret_history, check_ci_honesty, check_identified_humans,
    check_attestations,
]

NAMES = {
    "A-01": "Normative-artifact header completeness",
    "A-02": "Registry / Constitution consistency",
    "A-03": "Adoption element completeness",
    "A-04": "Absence of scientific records",
    "A-05": "Authority and certainty lexemes in live paths",
    "A-06": "Legacy index and banner coverage",
    "A-07": "Credentials in history",
    "A-08": "Check honesty in CI",
    "A-09": "Identified humans available for attestation",
    "A-10": "Attestation field completeness",
}


def main() -> int:
    print("P1 adoption readiness checks — advisory only, no authority (S4p4)")
    print(f"repository: {ROOT}")
    ok, head = git("rev-parse", "HEAD")
    print(f"revision:   {head.strip() if ok else 'UNKNOWN (git unavailable)'}")
    print("=" * 78)

    results = []
    for fn in CHECKS:
        try:
            results.append(fn())
        except Exception as exc:  # a crashed check is NOT_VERIFIED, never passed
            results.append(Result(fn.__name__, "-", "NOT_VERIFIED", f"check raised: {exc!r}"))

    for r in results:
        print(f"\n[{r.status:<12}] {r.check}  {NAMES.get(r.check, r.check)}  (S{r.clause[1:]})"
              if r.clause.startswith("S") else
              f"\n[{r.status:<12}] {r.check}")
        print(f"    {r.detail}")
        for item in r.items:
            print(f"      - {item}")
        if r.limitation:
            print(f"    limitation: {r.limitation}")

    counts = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    print("\n" + "=" * 78)
    print("summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    blocking = [r.check for r in results if r.status in ("FAIL", "NOT_VERIFIED")]
    if blocking:
        print("blocking (FAIL or NOT_VERIFIED): " + ", ".join(blocking))
        print("Under S12p1 a NOT_VERIFIED check MUST NOT be reported as passed.")
        return 1
    print("no FAIL or NOT_VERIFIED. FINDINGS, if any, require human disposition.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
