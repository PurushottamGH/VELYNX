# `governance/design/` — Constitutional Ecosystem Design Set

- **Status:** Draft
- **Scope:** Navigation and non-normative description of this directory
- **Responsibility:** Index only
- **Authority source:** None. Nothing in this directory has normative authority, registers anything, activates anything, or authorizes any transition.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft, not adopted)

---

## What this is

A design for the artifact ecosystem required to operate Project P1 under Repository Constitution v1.2.0. It proposes twenty-four Domain standards, a repository architecture record, sixty-three automated checks, twenty manual review procedures, a nine-stage verification pipeline, and a phased activation roadmap.

## What this is not

It is **not** a set of standards. Under Constitution §4 ¶1, an artifact acquires authority only through a Governance Registry entry, an approving Registry-listed authority, and an Independent reviewer attestation, delivered as one Atomic change. No file here satisfies any of those conditions, and each declares `Authority source: None` accordingly.

Where these documents use MUST or MUST NOT, they describe a requirement a *proposed* artifact would impose once activated. They impose nothing now.

## Identifiers in this directory are design-space only

Every identifier this directory **owns** is prefixed `D` so that no token means two things repository-wide (§11 ¶3). This was not always so: until the final engineering sprint, this directory's check register spent `A-01`…`A-63` on checks different from the ten implemented in `scripts/governance/check_adoption.py`, and `G-`, `D-`, `X-`, `F-` were likewise doubly used. That is recorded as `AF-25` in `governance/activation/05_RELEASE_CANDIDATE_CHECKLIST.md`.

| Prefix here | Denotes | Do not confuse with |
|---|---|---|
| `DA-01`…`DA-63` | proposed automated checks (`05_AUTOMATION_ARCHITECTURE.md`) | `A-01`…`A-15`, the checks that actually exist in `scripts/governance/check_adoption.py` |
| `DG-1`…`DG-13` | proposed governance-stack standards (`02_GOVERNANCE_STACK.md`) | `G-1`…`G-10`, the change-D preflight gates in `03_ADOPTION_CHANGE_MANIFEST.md` §2 |
| `DD-1`…`DD-3` | ecosystem defects (`00_ECOSYSTEM_OVERVIEW.md` §8) | `CD-1`…`CD-11`, the contents of change D; and `D-1`/`D-2`, derived amendments in the amendment record |
| `DX-1`…`DX-14` | extension points (`07_EXTENSION_ARCHITECTURE.md`) | `X-1`…`X-7`, the external blockers in `05_RELEASE_CANDIDATE_CHECKLIST.md` §5 |
| `DF-1`…`DF-5` | conditions that would force redesign (`07_EXTENSION_ARCHITECTURE.md`) | `F-xx`, findings of the v1.2.0 amendment record |
| `DAM-8` | the General Delegation Clause **amendment this design set proposes**. It is design-owned, not a citation: the amendment record defines `A-1`…`A-7` and stops, so the unpadded label this proposal previously carried pointed at nothing | `A-1`…`A-7`, which exist; and the padded check id of the same number, which is a different kind of object entirely |
| `S-`, `O-`, `M-`, `N-`, `R-`, `I-`, `MRP-` | proposed scientific standards, ontology standards, roadmap milestones, current nonconformances, risks, interfaces, manual review procedures | nothing — these prefixes are used nowhere else |
| `H-01`…`H-14` | matters requiring human constitutional judgment (`10_HUMAN_JUDGMENT_REGISTER.md`) | `H-1`…`H-9`, the plan's human-authority tasks. Distinguished by **zero-padding**; always written two-digit here |
| `A-1`…`A-7`, `F-6`/`F-9`/`F-19`, `L-4` | **citations**, not design-owned ids: proposed amendments, findings, and a limitation of `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md` | the padded check ids `A-01`…`A-15`. An amendment is always unpadded and always cited with the word "amendment" |

The last two rows are deliberately not renamed: re-keying a citation breaks the reference, and re-keying an audit record's own identifiers after the fact would rewrite an audit (§3 ¶5). `tests/governance/test_identifier_namespaces.py` enforces the separation mechanically, so a regression is a failing test rather than a silent ambiguity.

## Read in this order

| File | Contents |
|---|---|
| `00_ECOSYSTEM_OVERVIEW.md` | **Start here.** Verified starting state; the authority-vs-dependency distinction; the jurisdiction partition rule; the Constitution's delegation map; artifact hierarchy; dependency graph; Pre-Adoption Operating Mode; the three contradictions that prevent implementation |
| `01_REPOSITORY_ARCHITECTURE_RECORD.md` | Repository tree; per-directory purpose, authority, ownership, dependencies, lifecycle; boundary declarations; rejected alternatives; ten current nonconformances |
| `02_GOVERNANCE_STACK.md` | O-1 and DG-1 … DG-13, each with purpose, authority, inputs, outputs, constraints, lifecycle, verification, failure modes |
| `03_SCIENTIFIC_STACK.md` | S-1 … S-10, each with ontology, lifecycle, required fields, relationships, validation rules, failure cases, migration rules; the confirmatory chain |
| `04_DOMAIN_STANDARD_INTERFACE.md` | How future domains enter without constitutional change; required declarations; activation dossier; candidate domains |
| `05_AUTOMATION_ARCHITECTURE.md` | Sixty-three proposed checks `DA-01`…`DA-63` with inputs, outputs, algorithm, limitations, false positives, false negatives; what automation cannot do |
| `06_VERIFICATION_ARCHITECTURE.md` | Stages V0–V12; twenty named manual review procedures; the fail-closed matrix; cost accounting |
| `07_EXTENSION_ARCHITECTURE.md` | Ten growth axes; fourteen extension points `DX-x`; six conditions that would force redesign `DF-x` |
| `08_IMPLEMENTATION_ROADMAP.md` | Phases M-0 … M-9, gates, critical path, sequencing guidance |
| `09_RISK_ASSESSMENT.md` | Twenty-four risks with mechanism, severity, detection, mitigation, residual. Nine already realized |
| `10_HUMAN_JUDGMENT_REGISTER.md` | Fourteen matters requiring human constitutional judgment, with options and recommendations |
| `REGISTRY_TARGET_STATE.example.yaml` | The machine-readable jurisdiction form. **Example only — not the Governance Registry** |

## The three things worth knowing before reading further

1. **Nothing in P1 is currently Active.** The Constitution is Draft; the Registry is Draft with zero Active standards, zero stewards, and both attestations `null`.

2. **One identified human exists in the repository's entire history.** Constitution §13 ¶3 requires two for initial adoption, and §4 ¶4 forbids automated systems from supplying independent review. Adoption — and therefore every activation — currently fails closed. This is judgment item **H-01**, and no part of this design works around it.

3. **Repository layout is deliberately not constitutional.** §10 ¶1 says so explicitly, and adds that "a directory name MUST NOT be treated as proof of separation." The tree in `01_` is therefore a Level-4 architecture record, revisable without amendment, paired with machine-readable boundary declarations rather than relying on folder names.

## Three actions that need no authority and get more expensive with delay

Drawn from `08_IMPLEMENTATION_ROADMAP.md` M-1 and `09_RISK_ASSESSMENT.md`:

- **Credentials** (R-28) — `gcp-key.json.json` and a populated `.env` are in the working tree. Verify they are ignored, verify no historical revision contains them, rotate if uncertain.
- **CI honesty** (R-05) — `.github/workflows/ci.yml` uses PowerShell syntax on `ubuntu-latest` and ends steps with `|| true`; several jobs cannot fail. Under §12 ¶1 their green status means "not verified," not "passed."
- **External timestamping** (R-08, H-14) — the preregistration guarantee cannot be verified from inside the repository, and timestamping cannot retroactively secure past commits. Its value strictly decreases with delay.
