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

## Read in this order

| File | Contents |
|---|---|
| `00_ECOSYSTEM_OVERVIEW.md` | **Start here.** Verified starting state; the authority-vs-dependency distinction; the jurisdiction partition rule; the Constitution's delegation map; artifact hierarchy; dependency graph; Pre-Adoption Operating Mode; the three contradictions that prevent implementation |
| `01_REPOSITORY_ARCHITECTURE_RECORD.md` | Repository tree; per-directory purpose, authority, ownership, dependencies, lifecycle; boundary declarations; rejected alternatives; ten current nonconformances |
| `02_GOVERNANCE_STACK.md` | O-1 and G-1 … G-13, each with purpose, authority, inputs, outputs, constraints, lifecycle, verification, failure modes |
| `03_SCIENTIFIC_STACK.md` | S-1 … S-10, each with ontology, lifecycle, required fields, relationships, validation rules, failure cases, migration rules; the confirmatory chain |
| `04_DOMAIN_STANDARD_INTERFACE.md` | How future domains enter without constitutional change; required declarations; activation dossier; candidate domains |
| `05_AUTOMATION_ARCHITECTURE.md` | Sixty-three checks with inputs, outputs, algorithm, limitations, false positives, false negatives; what automation cannot do |
| `06_VERIFICATION_ARCHITECTURE.md` | Stages V0–V12; twenty named manual review procedures; the fail-closed matrix; cost accounting |
| `07_EXTENSION_ARCHITECTURE.md` | Ten growth axes; fourteen extension points; six conditions that would force redesign |
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
