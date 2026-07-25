#!/usr/bin/env python3
"""Generate governance/LEGACY_INDEX.md.

Authority: none. This script produces a navigation index (Constitution section 11:
"README or index: navigation and non-normative description"). It classifies; it
does not strip authority — section 14 does that automatically at adoption.

Tiers are defined in governance/activation/04_LEGACY_DISPOSITION.md:
  T1  self-described as constitutional/canonical in a live path -> move + banner
  T2  imposes requirements in a live normative path             -> banner
  T3  everything else, by directory rule                        -> index entry only

Run:  python scripts/governance/generate_legacy_index.py
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "governance" / "LEGACY_INDEX.md"

# Section 1 paragraph 2's four named words are matched bare: canonical, absolute,
# frozen, authoritative. Keep identical to AUTHORITY_LEXEMES in
# scripts/governance/check_adoption.py — A-06 verifies banners against the index
# this ranking produces, so a divergence would silently change what A-06 assesses.
LEXEMES = re.compile(
    r"\b(absolute|canonical|frozen|authoritative|non-negotiable|"
    r"supersedes all|final authority|single source of truth|must not be violated)\b",
    re.IGNORECASE,
)

NORMATIVE_MODAL = re.compile(r"\b(MUST NOT|MUST|SHALL|REQUIRED|SHOULD NOT|SHOULD)\b")

TIER1 = {
    "theory/PROGRAM_D_CONSTITUTION.md": ("archive/legacy_normative/", "titled as a constitution; asserted program-wide authority"),
    "PROGRAM_D_CANONICAL.md": ("archive/legacy_normative/", "asserted canonical status for Program D content"),
    "PROGRAM_D_MASTER_ROADMAP.md": ("archive/legacy_normative/", "asserted frozen scope and sequencing"),
    "PROGRAM_D_RESEARCH_STATE_v0.1.md": ("archive/legacy_normative/", "asserted current research state as settled"),
    "RESEARCH_PROTOCOL.md": ("archive/legacy_normative/", "read as the governing research procedure"),
    "audits/CONSTITUTION_COMPLIANCE.md": ("archive/legacy_normative/", "asserted compliance against a superseded constitution"),
    "p1/specifications/milestone-1-gpt56.md": ("(stays in place)", "imposes PI-003/PI-004/PI-005; imported by p1/tooling, so moving it breaks working code for no compliance gain"),
}

# Live paths whose .md files are candidates for T2 (normative in character).
T2_PREFIXES = ("theory/", "experiments/", "p1/")

# T3 directory rules: (path prefix, statement)
TIER3_RULES = [
    ("archive/", "Inherited Programs A/B/C material and legacy documents. Retained for history; nothing depends on it."),
    ("docs/", "Documentation, sprint planning, migrations, and model-authored audits. Descriptive; imposes nothing."),
    ("audits/", "Audit and checklist reports. Under section 3 paragraph 5 an audit reports observations and MUST NOT create the requirement it audits."),
    ("evidence/", "Verification artifacts, certifications, traces, ledgers. Certification language here confers no authority."),
    ("artifacts/", "Nineteen exp_* execution outputs. Permanently exploratory working output: no Registered protocol preceded them (sections 2, 5 paragraph 3, 13 paragraph 4)."),
    ("research/", "Inherited research scaffolding and preregistration-shaped documents. Not Registered protocols."),
    ("reviews/", "Review-shaped records. Section 4 paragraph 4 bars automation from supplying independent review; these do not satisfy section 13 paragraph 2."),
    (".agents/", "Agent and skill configuration. Several define reviewer or auditor roles for models; none can supply human authority or independent review (section 4 paragraph 4)."),
    (".opencode/", "Agent configuration, as above."),
    (".commandcode/", "Agent configuration, as above."),
    ("backend/constitution/", "Model-behaviour prompt files. The directory name collides with the Constitution and carries no governance meaning (section 11 paragraph 3)."),
]

SKIP_PARTS = ("node_modules", ".venv", ".git", "P1.worktrees", "__pycache__",
              ".pytest_cache", ".hypothesis", "dist", ".kilo")

NEVER_LEGACY = {
    "REPOSITORY_CONSTITUTION.md",  # the artifact being adopted
    "README.md",                   # index, non-normative (section 11)
}


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")


def tier1_current(original: str, dest: str) -> str:
    """Resolve a Tier-1 entry's post-move path.

    A-06 checks the banner at this path. Emitting it is what stops a moved file
    from silently dropping out of verification once RE-2 runs: the check reports
    an entry that resolves to neither path, rather than skipping it.
    """
    if dest.endswith("/"):
        return dest + original.rsplit("/", 1)[-1]
    return original  # stays in place


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                           text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def find_tier2() -> list[tuple[int, str]]:
    out = []
    for p in ROOT.rglob("*.md"):
        r = rel(p)
        if any(s in r for s in SKIP_PARTS):
            continue
        if r in TIER1 or r in NEVER_LEGACY or r.startswith("governance/"):
            continue
        if not r.startswith(T2_PREFIXES):
            continue
        try:
            body = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        n = len(LEXEMES.findall(body))
        # Banner is required only where the artifact would read as Active: it either
        # asserts authority/frozenness, or it imposes requirements with a normative
        # modal. Descriptive prose in these directories falls to the Tier-3 rule.
        if n == 0 and not NORMATIVE_MODAL.search(body):
            continue
        out.append((n, r))
    return sorted(out, key=lambda t: (-t[0], t[1]))


def main() -> int:
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    head = git("rev-parse", "HEAD")
    tier2 = find_tier2()
    prereg = [r for _, r in tier2 if "preregistration" in r.lower()]

    L = []
    a = L.append
    a("# Legacy Index")
    a("")
    a("- **Status:** Draft (generated). Becomes the adoption-revision index when committed in change D.")
    a("- **Scope:** Every version-controlled artifact not activated in `GOVERNANCE_REGISTRY.yaml`")
    a("- **Responsibility:** Navigation. Identify Legacy artifacts and the basis of their classification")
    a("- **Authority source:** None. An index under section 11; it imposes no requirement and strips no authority.")
    a(f"- **Generated:** {now.isoformat(timespec='minutes')} at revision `{head}`")
    a("- **Generator:** `scripts/governance/generate_legacy_index.py`")
    a("")
    a("## 1. Basis")
    a("")
    a("Section 14: \"At adoption, every existing Normative artifact not activated in the "
      "Governance Registry becomes Legacy and has no normative authority. A Legacy artifact "
      "MUST satisfy Section 4 before later activation.\"")
    a("")
    a("Section 4 paragraph 5: Legacy content \"MUST remain distinguishable from Active requirements.\"")
    a("")
    a("Classification follows automatically from the Registry. This index records it so a "
      "reader need not derive it, and marks where a banner is required because the artifact "
      "would otherwise read as Active.")
    a("")
    a("## 2. What is Active")
    a("")
    a("`GOVERNANCE_REGISTRY.yaml` is the only answer. At adoption the Active set is "
      "**`REPOSITORY_CONSTITUTION.md` and nothing else** (`active_domain_standards: []`). "
      "Everything listed below, and everything not listed, is Legacy or non-normative.")
    a("")
    a("## 3. Tier 1 — moved and bannered")
    a("")
    a("`Current path` is where the banner is verified. Until change D moves the file it "
      "is the original path; afterwards it is the destination. The check resolves the "
      "current path first, then the original, and reports an entry that resolves to "
      "neither as **not verified** rather than skipping it — otherwise the moves would "
      "silently remove the Tier-1 files from banner verification.")
    a("")
    a("The moving commit is deliberately not recorded here. It is the revision that "
      "contains this index, so naming it inside the index would be self-referential; "
      "`git log --follow <current path>` recovers it after the fact.")
    a("")
    a("| Original path | Current path | Disposition | What it used to assert |")
    a("|---|---|---|---|")
    for path, (dest, why) in TIER1.items():
        cur = tier1_current(path, dest)
        a(f"| `{path}` | `{cur}` | {dest} | {why} |")
    a("")
    a("<!-- TIER1_BEGIN -->")
    for path, (dest, why) in TIER1.items():
        a(f"- `{path}` -> `{tier1_current(path, dest)}`")
    a("<!-- TIER1_END -->")
    a("")
    a("## 4. Tier 2 — banner required, in place")
    a("")
    a(f"{len(tier2)} artifacts in `theory/`, `experiments/`, and `p1/` that either assert "
      "authority or frozenness, or impose requirements with a normative modal (MUST, SHALL, "
      "REQUIRED, SHOULD) — that is, artifacts a reader could take as Active. Descriptive "
      "prose in the same directories falls to the Tier-3 rule and needs no banner. The count "
      "column is lexeme matches; it indicates how strongly the text reads as Active and is "
      "not a severity score.")
    a("")
    a("<!-- BANNER_REQUIRED_BEGIN -->")
    for n, r in tier2:
        a(f"- `{r}` ({n})")
    a("<!-- BANNER_REQUIRED_END -->")
    a("")
    if prereg:
        a("### 4.1 Preregistration-shaped artifacts")
        a("")
        a("These require the second banner paragraph in "
          "`governance/activation/04_LEGACY_DISPOSITION.md` section 3. None is a Registered "
          "protocol: section 2 requires the registration transition to have occurred before "
          "governed execution began, and section 13 paragraph 4 forbids supplying it "
          "retroactively.")
        a("")
        for r in prereg:
            a(f"- `{r}`")
        a("")
    a("## 5. Tier 3 — directory rules")
    a("")
    a("| Prefix | Statement |")
    a("|---|---|")
    for prefix, note in TIER3_RULES:
        a(f"| `{prefix}` | {note} |")
    a("")
    a("## 6. Completeness")
    a("")
    a("**Method.** Tier 1 is a hand-curated list of artifacts that describe themselves as "
      "constitutional or canonical in a live path. Tier 2 is every `.md` file under "
      "`theory/`, `experiments/`, and `p1/`, ranked by lexeme matches. Tier 3 is stated by "
      "directory rather than enumerated.")
    a("")
    a("**Scope.** Version-controlled Markdown only, at the revision above.")
    a("")
    a("**Known false negative.** A Normative artifact that imposes requirements without "
      "declaring authority and without matching the lexeme list is not detected — for "
      "example a YAML registry, a JSON schema, or a plainly-worded specification. "
      "`experiment_registry.yaml`, `parameter_registry.yaml`, and `reproducibility.yaml` are "
      "in that category and are Legacy on the same section 14 basis even though the scan "
      "does not surface them. This index therefore does not claim completeness, and a "
      "conformance claim citing it MUST carry that limitation (section 12 paragraph 3).")
    a("")
    a("**Not mechanically decidable.** Whether a document *reads* as authoritative is manual "
      "procedure `P-L1` in `04_LEGACY_DISPOSITION.md` section 5. A lexeme count does not "
      "answer it.")
    a("")
    a("## 7. Reactivation")
    a("")
    a("A Legacy artifact carries force again only by satisfying section 4: complete "
      "status/scope/responsibility/authority fields, a non-overlapping Registry jurisdiction, "
      "approval by a Registry-listed authority permitted for that jurisdiction, and an "
      "Independent reviewer attestation under section 13 — in one atomic change. Nothing "
      "here is activated by being read, cited, or relied upon.")
    a("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {rel(OUT)}: tier1={len(TIER1)} tier2={len(tier2)} "
          f"tier3_rules={len(TIER3_RULES)} prereg={len(prereg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
