# Minimum Viable Constitutional Activation Plan

- **Status:** Draft
- **Scope:** Activation of `REPOSITORY_CONSTITUTION.md` v1.2.0 and the minimum standard set for lawful repository operation
- **Responsibility:** Define the smallest activation path consistent with the Constitution
- **Authority source:** None. This record has no normative authority and authorizes no transition.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft, not adopted)
- **Version:** 0.1.0

---

## 1. Result

**One Domain standard is sufficient for lawful research operation. Zero are required for adoption.**

| Object | Count | Note |
|---|---|---|
| Constitution | 1 | already written, v1.2.0, stable |
| Governance Registry | 1 | already exists, Draft |
| Domain standards required **before** adoption | **0** | §13 ¶3's list contains none |
| Domain standards required for lawful **research** operation | **1** | `RS-1`, governing six object types |
| Constitutional stewards | 1 (+1 successor) | §13 ¶3 |
| Attestations | 2 at adoption, 1 per later activation | §13 ¶2, §4 ¶2 |
| Non-normative records required at adoption | 3 | architecture record (§10 ¶1); Legacy index (§4 ¶5); adoption transition record (§2, §9 ¶3) |
| Automated checks | 10 implemented, 5 specified | §12 ¶3 is SHOULD, not MUST — these are cheap, not obligatory. A cited check must exist (§12 ¶1) |

Down from twenty-four standards to one. The reduction is textual, not a relaxation.

---

## 2. Why one standard suffices

Three clauses do the work.

### 2.1 §13 ¶3 requires no Domain standard at adoption

> "The same atomic change MUST activate this Constitution, create or activate the Governance Registry, and assign at least one constitutional steward authorized to amend, supersede, or withdraw this Constitution and to activate Domain standards."

The list is exhaustive: Constitution, Registry, steward. Plus two attestations by two identified humans. **No Domain standard appears.** Adoption with `active_domain_standards: []` is a valid Active state.

The same clause is also the reason the adoption change may lawfully contain objects no standard owns. §13 ¶3 *requires* attestations at adoption, while §4 ¶2 makes activating a standard that could own `attestation` require an attestation. Reading §9 ¶1 to demand an owning standard for them would make adoption impossible, so that reading is unavailable; see dossier interpretation 4.5.

### 2.2 §9 ¶1 carves Domain standards out of the per-type ownership rule

> "**Except for this Constitution and the Governance Registry, whose initial activation is governed by Section 13, and Domain standards, whose activation is governed by Section 4,** every subordinate scientific or governance object type MUST have exactly one Active Domain standard…"

Three exceptions, and the third is decisive: **Domain standards need no governing standard.** Their lifecycle comes from §9 ¶4 directly (`Draft → Active → Superseded or Withdrawn`), their required fields from §4 ¶1, their activation procedure from §4 ¶2, and their amendment from §9 ¶4 plus §4 ¶2.

Consequences:
- A "Normative Artifact Standard" / "Governance Standard" is **never required**. Not deferred — unnecessary.
- This also removes the project's exposure to the previously-recorded delegation defect, which arose only from trying to refine §9 ¶4's "minimum lifecycle." Nothing refines it, so nothing depends on it.
- A "Registry Specification" is likewise not required: §2 fixes the Registry's responsibility and §4 ¶1–2 fix its required fields. A schema is an engineering convenience under §12 ¶3's SHOULD.

### 2.3 §9 ¶2 permits one standard to own many types

> "A Domain standard … MAY govern subordinate Registered protocols, Decisions, and scientific records; it MUST NOT require or authorize another Domain standard for its own object type."

§9 ¶1 requires exactly one *owner per type*. It does not require one *type per owner*. §9 ¶2 explicitly names the combination — protocols, Decisions, and scientific records in one standard — so a single standard covering the whole research loop is the arrangement the Constitution contemplates, not a workaround.

§11 ¶1 is satisfied because §11's own list defines the responsibility as "domain scientific standard: **one domain's method, object definitions, and scientific lifecycle**" — plural objects, one domain, one responsibility.

### 2.4 Why the other twenty-two are not required

| Proposed standard | Why not required |
|---|---|
| Ontology | §5 ¶6 requires an ontology to be governed by "a revisable domain standard or registered protocol." RS-1 is one. A separate ontology standard prevents cross-standard drift, and with one standard there is none. |
| Authority & Delegation | §4 ¶1 requires an authority source to identify jurisdiction and permitted transitions; the Registry does that. With one steward and no delegation, there is nothing further to govern. |
| Review & Attestation | §13 ¶2 fully specifies attestation content. §12 ¶4 requires a *named manual review procedure* — nameable inside RS-1's verification mapping, not requiring a standard. |
| Conformance | §12 ¶1 states the traceability test directly. A conformance claim is a record, not a governed object type in use. |
| Audit | §3 ¶5 and §11 fix what an audit is and may not do. No audit is required to exist. |
| Custody & Retention | §6 ¶2 delegates the digest algorithm to "the applicable Domain standard **or Registered protocol**." RS-1 or the protocol specifies it. |
| Change & Release | §4 ¶5 already covers incorporation; software release governance is needed only when P1 releases software as a governed artifact. |
| Decision | Folded into RS-1 by explicit §9 ¶2 permission. |
| Architecture | §10 ¶1 requires architecture **records**, not a standard governing them. See §4.2 below. |
| Automation & Tooling | §12 ¶3 is SHOULD. Required only if check output is cited as conformance evidence under a formal claim. |
| Emergency, Conflict | §12 ¶2 and §4 ¶4 are self-executing. Records become useful when there is something to contain or a conflict to track. |
| The nine remaining scientific standards | Their object types are either owned by RS-1 or not yet in use. §9 ¶1 binds types that exist in the governance system. |

---

## 3. The minimum standard: RS-1

**`RS-1` — P1 Research Standard.** One document, one domain, six owned object types. Skeleton in `RS-1_RESEARCH_STANDARD.draft.md`.

| # | Owned type | Why in the minimum set |
|---|---|---|
| 1 | `registered_protocol` | §2 defines a Registered protocol as one registered *before* governed execution. Without it, every execution is exploratory forever (§5 ¶3), and §13 ¶4 forbids relabelling later. This is the type whose absence is permanently costly. |
| 2 | `observation` | §2 makes Observation a distinct kind and forbids substituting another kind for it. Any measurement must land somewhere. |
| 3 | `result` | §7 requires a defined transition from working output to Result, and §7 ¶2 delegates completion criteria and recording authority to a Domain standard or protocol. |
| 4 | `unknown` | §8 ¶1 makes Unknown a permanent first-class kind, and material uncertainty MUST be recorded as one. This obligation triggers immediately and unavoidably. |
| 5 | `decision` | §4 ¶5: a scientific transition MUST be authorized by a Decision approved by the Registry-listed authority. Without it no transition above is lawful. |
| 6 | `interpretation` | §2 defines Interpretation as inference "from identified Evidence **or Results**" — Results suffice, so inference is reachable without Claim or Evidence machinery. This is what makes an experiment conclude rather than merely record. |

**Deliberately excluded from the minimum:** `question`, `source`, `evidence`, `claim`, `hypothesis`, `principle`.

Excluding Claim and Evidence is the plan's sharpest economy and deserves to be stated plainly. §2's Interpretation definition permits inference directly from Results, so a complete lawful cycle runs `protocol → observation → result → interpretation`, with Unknowns and Decisions throughout. Findings are expressed as scoped Interpretations rather than as Claims.

The cost is real: until Claim and Evidence exist, P1 cannot say "Evidence E supports Claim C," cannot register a Hypothesis (§2 defines one as a Claim plus an operational test), and cannot accept a Principle. Those capabilities arrive as an RS-1 MINOR amendment when first needed — one steward approval and one attestation — rather than being paid for before the first experiment runs.

---

## 4. Non-standard artifacts required at adoption

Three constitutional MUSTs become binding the moment the Constitution is Active. None requires a Domain standard.

### 4.1 Legacy distinguishability — §4 ¶5

§14 makes every unregistered Normative artifact Legacy automatically. But §4 ¶5 requires: "Historical, superseded, rejected, withdrawn, archived, generated, legacy, and Draft artifacts have no normative authority. **Their content MUST remain distinguishable from Active requirements.**"

A file titled `PROGRAM_D_CONSTITUTION.md` asserting "Its authority is absolute" is not distinguishable to a reader who has not read §14. Minimum compliant action, in the adoption change:

- Move the six artifacts that assert supremacy in live paths to `archive/legacy_normative/`: `theory/PROGRAM_D_CONSTITUTION.md`, `PROGRAM_D_CANONICAL.md`, `PROGRAM_D_MASTER_ROADMAP.md`, `PROGRAM_D_RESEARCH_STATE_v0.1.md`, `RESEARCH_PROTOCOL.md`, `audits/CONSTITUTION_COMPLIANCE.md`.
- Add `archive/legacy_normative/LEGACY_INDEX.md` listing every Legacy artifact with the §14 basis.
- Add a one-line Legacy banner to remaining artifacts that carry a "Canonical" status line.

This is engineering, not authority: moving a file is not a scientific transition, and §8 ¶2 is satisfied because git history preserves the content. No Decision required.

### 4.2 Architecture record — §10 ¶1

> "Software architecture and repository layout are not constitutional. They MUST be defined in versioned architecture records with explicit boundaries, dependencies, and rationale. A directory name MUST NOT be treated as proof of separation."

The MUST attaches to the **record**, not to a standard governing records. Minimum compliant action: one versioned, **descriptive** architecture record with boundaries, dependencies, and rationale, at Level 4 (implementation and explanatory documentation).

Keeping it descriptive rather than normative is what keeps it cheap: a descriptive record imposes no requirements, so it is not a Normative artifact under §2, needs no Registry entry, and needs no activation. Enforcement of its boundaries is optional under §12 ¶3's SHOULD. If P1 later wants the boundaries *enforceable*, that is when an architecture standard becomes worth activating.

`governance/design/01_REPOSITORY_ARCHITECTURE_RECORD.md` can serve as the source, reduced to the current tree plus the six directories RS-1 needs, with its normative phrasing removed.

### 4.3 Adoption conformance dossier — §12 ¶1

This is the single largest burden-reducer in the plan and is easy to overlook.

§12 ¶1 requires an Independent reviewer to trace every **Affected** requirement expressed as MUST or MUST NOT to one of three things — and the third is "a statement that the requirement is not applicable, **with a testable reason**."

At adoption the repository contains no scientific records. So the majority of the Constitution's MUSTs and MUST NOTs — the whole of §5, §6, §7, most of §8 and §9 — discharge as *not applicable, with a testable reason*: "no object of this kind exists at revision X; verified by the absence of records of that type." That is a mechanical, honest, reviewable discharge, not a loophole.

The previously-recorded concern that conformance "cannot be fully claimed at ratification" because no Domain standard exists resolves differently, and the difference matters. It is **not** true that no object type is in use at adoption: change D creates two attestations, a conformance claim, an authority assignment, an architecture record, and a transition record, and no Active Domain standard owns any of them. §9 ¶1 is satisfied because none of those types is *subordinate* — each is specified by the Constitution itself — not because the set is empty. The argument is recorded as the dossier's interpretation 4.5, which is where a reviewer should test it.

Template: `ADOPTION_CONFORMANCE_DOSSIER.template.md`.

### 4.4 Adoption transition record — §2, §9 ¶3

§2 defines an Atomic change as one containing "every required artifact, Registry entry, approval, attestation, **and transition record**". §9 ¶3 then fixes what a transition record is: eight elements — object, prior state, new state, criteria applied, evidence considered, authority, time, rationale — and missing information fails the transition closed.

The Constitution's own `Draft → Active` is a transition of a Normative artifact, and §9 ¶3 is unqualified as to object type. §9 ¶1's exception is about *needing a Domain standard*, which is a different rule; it does not exempt anything from the transition-record requirement. So D contains one, and E contains a second for RS-1.

This is cheap and worth not litigating: two small files whose absence would leave the repository's most consequential transition as the only one without a §9 ¶3 record, and would make a dossier row that discharges §9 ¶3 as not applicable simply false.

Template: `templates/NORMATIVE_TRANSITION_RECORD.template.md`. At E it is required *in addition to* the approving Decision `D-0001`: an approval authorizes a transition, it is not a record that the transition occurred (RS-1 §2.1).

---

## 5. Implementation dependency graph

```
                    ┌─────────────────────────────────────────┐
                    │  A0  SECOND IDENTIFIED HUMAN            │  HUMAN — blocks everything
                    │  §13 ¶3 · §2 · §4 ¶4                    │
                    └────────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │  no authority needed — all four may proceed now, in parallel    │
        ▼                    ▼                    ▼                    ▼
  ┌───────────┐      ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │ B1 RS-1   │      │ B2 ARCH      │    │ B3 LEGACY    │    │ B4 HYGIENE   │
  │ draft     │      │ RECORD       │    │ MOVES+INDEX  │    │ secrets, CI, │
  │ (ENG)     │      │ (ENG)        │    │ (ENG)        │    │ signing,     │
  └─────┬─────┘      └──────┬───────┘    └──────┬───────┘    │ timestamping │
        │                   │                   │            │ (ENG)        │
        │                   │                   │            └──────┬───────┘
        │                   └─────────┬─────────┘                   │
        │                             │                             │
        │                             ▼                             │
        │            ┌────────────────────────────────┐             │
        │            │ C1 ADOPTION CONFORMANCE DOSSIER│◄────────────┘
        │            │ §12 ¶1 · mostly N/A rows (ENG) │
        │            └────────────────┬───────────────┘
        │                             ▼
        │            ┌────────────────────────────────────────────┐
        │            │ D  ADOPTION ATOMIC CHANGE          §13 ¶3  │
        │            │ Constitution → Active                      │
        │            │ Registry → Active, steward + successor      │
        │            │ adopter attestation      (HUMAN)            │
        │            │ independent attestation  (HUMAN)            │
        │            │ + arch record + legacy index + dossier      │
        │            └────────────────┬───────────────────────────┘
        │                             │
        └─────────────────────────────┤
                                      ▼
                     ┌────────────────────────────────────────────┐
                     │ E  RS-1 ACTIVATION ATOMIC CHANGE    §4 ¶2  │
                     │ RS-1 → Active + Registry entry             │
                     │ steward approval         (HUMAN)           │
                     │ independent attestation  (HUMAN)           │
                     └────────────────┬───────────────────────────┘
                                      ▼
                     ┌────────────────────────────────────────────┐
                     │ F  FIRST LAWFUL RESEARCH CYCLE             │
                     │ register protocol → observe → Result →     │
                     │ Interpretation, with Unknowns + Decisions  │
                     │ each transition: Decision (HUMAN) + §9 ¶3  │
                     └────────────────┬───────────────────────────┘
                                      ▼
                     ┌────────────────────────────────────────────┐
                     │ G  ON-DEMAND ONLY — activate nothing until  │
                     │ a specific constitutional need arises      │
                     │ (see 01_STANDARD_CLASSIFICATION.md)        │
                     └────────────────────────────────────────────┘
```

**Critical path:** `A0 → D → E → F`. Everything in B and C is parallel, needs no authority, and can be finished before A0 resolves.

**Why D and E are separate changes.** §13 ¶3 says bootstrap authority "ends upon adoption," so whether a steward assigned *within* the adoption change may also approve a standard activation *in that same change* is contestable. §4 ¶2 makes activation fail closed if no permitted authority exists. Two sequential changes remove the ambiguity at the cost of one extra merge — the attestation count is 3 either way, since §4 ¶2 requires RS-1 its own attestation regardless. Not worth the interpretive risk.

---

## 6. Activation roadmap

### Stage 0 — Unblock *(human; blocks all)*
Identify the second human, who must be a human, must not be an author of the adoption change, and must declare conflicts (§2, §4 ¶4, §13 ¶3). Record their competence and the records they examine (§13 ¶2).

### Stage 1 — Preparation *(engineering; no authority; start now, run in parallel)*
1. Draft RS-1 from the skeleton: nine §9 ¶1 lifecycle elements for each of six types.
2. Reduce the architecture record to a descriptive §10 ¶1 record covering the current tree plus RS-1's six record directories.
3. Legacy moves + `LEGACY_INDEX.md` + banners.
4. Hygiene: rotate credentials if `gcp-key.json.json` or `.env` ever entered history; remove `|| true` and the PowerShell-on-Ubuntu syntax from `ci.yml`; enable commit signing and branch protection on record paths; enable external timestamping.
5. Build the twelve checks (§8) as advisory.
6. Fill the adoption conformance dossier.

**Do item 4's timestamping before Stage 4.** It cannot retroactively secure past commits, and it is the only mechanism that makes §2's registration-before-execution verifiable from outside the repository.

### Stage 2 — Adoption *(one atomic change)*
Per §13 ¶3 and §2's atomicity rule: Constitution → Active; Registry → Active with steward and successor; adopter attestation; Independent reviewer attestation; architecture record; Legacy index; conformance dossier. `active_domain_standards: []`.

**Exit test:** an Independent reviewer can trace every Affected MUST to a check, a finding, or a testable N/A statement (§12 ¶1).

### Stage 3 — RS-1 activation *(one atomic change)*
Per §4 ¶2: reviewed RS-1, its Registry entry, steward approval, Independent reviewer attestation. Jurisdiction declared as owned types and transitions so §4 ¶2's overlap test is trivially satisfied against an empty field.

### Stage 4 — First lawful research cycle
Register the protocol first. Then observe, record the Result, record Unknowns, and infer. Each transition needs a Decision (§4 ¶5) and a §9 ¶3 eight-element record; missing information fails closed.

**Accept before starting:** no pre-adoption execution can become a confirmatory Result, because no Registered protocol preceded it. The nineteen existing `artifacts/exp_*` outputs remain exploratory working output permanently (§2, §5 ¶3, §13 ¶4). `theory/preregistrations/EXPERIMENT_ZERO_PREREGISTRATION.md` must be re-registered under RS-1 before its execution begins.

### Stage 5 — Growth on demand only
Activate nothing until a specific constitutional need arises. Each activation costs one steward approval and one independent attestation — the project's scarcest resource. Triggers are in `01_STANDARD_CLASSIFICATION.md`.

---

## 7. Task classification

### 7.1 Human authority — irreducible

Cannot be delegated to engineering or automation. §4 ¶4: "Automated systems MAY propose, check, or apply an already-authorized transition; they MUST NOT supply human authority or independent review."

| # | Task | Clause | Who |
|---|---|---|---|
| H-1 | Be the second identified human | §13 ¶3, §2 | new party |
| H-2 | Adopter attestation | §13 ¶2 | adopter |
| H-3 | Independent reviewer attestation for adoption | §13 ¶2 | reviewer |
| H-4 | Assign constitutional steward + named successor | §13 ¶3 | adopter |
| H-5 | Approve RS-1 activation | §4 ¶2 | steward |
| H-6 | Independent reviewer attestation for RS-1 | §4 ¶2 | reviewer |
| H-7 | Approve each Decision authorizing a scientific transition | §4 ¶5 | steward or delegate |
| H-8 | Decide which Legacy scientific content P1 still stands behind | §14 | steward |
| H-9 | Record the §13 adoption-path interpretation in the dossier | §13 | adopter |

H-9 is a recorded interpretation, not an amendment: the Constitution is Draft and has never been Active, so §13 ¶3 initial adoption applies rather than §13 ¶4 amendment — the amendment path presupposes a Registry-listed steward, and none exists. Recording the reasoning costs a paragraph and forecloses a later challenge.

### 7.2 Engineering — no authority required

| # | Task | Clause | Blocks |
|---|---|---|---|
| E-1 | Draft RS-1 to §4 ¶1 fields and §9 ¶1 nine elements × six types | §4 ¶1, §9 ¶1 | Stage 3 |
| E-2 | Descriptive architecture record | §10 ¶1 | Stage 2 |
| E-3 | Legacy moves, index, banners | §4 ¶5, §14 | Stage 2 |
| E-4 | Compose the atomic changes so no intervening revision lacks an element | §2 | Stages 2, 3 |
| E-5 | Adoption conformance dossier | §12 ¶1 | Stage 2 |
| E-6 | Record templates for six types incl. §9 ¶3 eight-element transition record | §9 ¶3 | Stage 4 |
| E-7 | Credential remediation incl. full history | §10 ¶5 | now |
| E-8 | CI honesty: no `\|\| true`, correct shell, non-empty target assertions | §12 ¶1 | now |
| E-9 | Branch protection on record paths; commit signing | §7 ¶1, §8 ¶2 | Stage 4 |
| E-10 | External timestamping | §2, §5 ¶3 | Stage 4 |
| E-11 | Registry entry for RS-1 with machine-readable jurisdiction | §4 ¶1-2 | Stage 3 |
| E-12 | Adoption transition record `T-0001`; RS-1 activation transition record `T-0002` | §2, §9 ¶3 | Stages 2, 3 |
| E-13 | Registry authority assignment covering every RS-1 transition | §4 ¶1, §4 ¶5 | Stage 3 |

### 7.3 Automated verification — ten implemented checks

§12 ¶3 is SHOULD, so none is obligatory. Each declares its scope, limitations, and false negatives, and emits findings only — never approval (§4 ¶4). An unavailable check reports **not verified**, never passed (§12 ¶1).

**Identifier namespaces.** Checks are `A-xx`, and `A-xx` means exactly one thing: a check implemented in `scripts/governance/check_adoption.py`. The `C-xx` numbering that earlier drafts of this plan, the dossier, and RS-1 used is withdrawn. It described a *planned* set, and five of its members were cited as evidence routes while having no implementation — which §12 ¶1 forbids, since citing a check makes that check's existence load-bearing for the claim it supports.

That sentence was, until this revision, false. `A-01`…`A-63` were also spent by the Draft design register in `governance/design/05_AUTOMATION_ARCHITECTURE.md` on a *different* set of checks, so fifteen identifiers carried two meanings — and four other prefixes carried two or three. §11 ¶3 forbids identical names concealing distinct types, and `AUT-4` was scheduled to build `A-11`…`A-15` into the very file whose design register had already spent those ids. The register below is the corrected state; the collisions are recorded as `AF-25` in `05_RELEASE_CANDIDATE_CHECKLIST.md`.

| Prefix | Meaning | Owner artifact |
|---|---|---|
| `A-01`…`A-15` | implemented advisory checks (`A-11`…`A-15` specified, unbuilt) | `scripts/governance/check_adoption.py`; specified in this plan §7.3 and RS-1 §9 |
| `P-1`…`P-15` | RS-1's manual review procedures | `RS-1_RESEARCH_STANDARD.draft.md` §9.1 |
| `P-A1`…`P-A4` | adoption-scope manual procedures | this plan §7.4 |
| `P-L1` | Legacy disposition manual procedure | `04_LEGACY_DISPOSITION.md` §5 |
| `G-1`…`G-10` | change-D preflight gates | `03_ADOPTION_CHANGE_MANIFEST.md` §2 |
| `CD-1`…`CD-11` / `CE-1`…`CE-9` | contents of change D / change E | `03_ADOPTION_CHANGE_MANIFEST.md` §3–§4 |
| `HG-`, `RE-`, `SEC-`, `DOC-`, `VER-`, `AUT-`, `AF-`, `X-`, `V-` | task, blocker, and finding registers | `05_RELEASE_CANDIDATE_CHECKLIST.md`, `02_PREADOPTION_VERIFICATION.md` |
| `E-1`…`E-13`, `H-1`…`H-9` | engineering and human-authority tasks | this plan §7.1–7.2 |
| `T-0001`, `T-0002` | normative-artifact transition records | `governance/transitions/` |
| `D-0001` | the RS-1 activation Decision | `governance/decisions/` |
| `U-a`…`U-f` | standing Unknowns | `02_PREADOPTION_VERIFICATION.md` §6 |
| `DA-`, `DG-`, `DD-`, `DX-`, `DF-`, `DAM-`, `M-`, `N-`, `O-`, `R-`, `S-`, `I-`, `MRP-` | **Draft design-space only** — checks, stack standards, defects, extension points, redesign forces, a design-proposed amendment, milestones, nonconformances, ontology standards, risks, standards, interfaces, manual review procedures | `governance/design/**`, which has no authority (§4 ¶7) and is cited by no conformance row |
| `A-1`…`A-7`, `D-1`…`D-2`, `F-xx`, `L-xx` (**unpadded**) | proposed amendments, derived amendments, findings, and limitations of the v1.2.0 amendment record | `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md` |

The last two rows are the residual hazard and are stated rather than renamed. The amendment record is an audit record of one revision (§3 ¶5); re-keying its identifiers after the fact would rewrite an audit. It is distinguished by **zero-padding**: a check is always written `A-05`, an amendment always `A-5`, and an amendment is always cited with a form of the word "amend". `tests/governance/test_identifier_namespaces.py` enforces the separation mechanically, including that the design set cites no amendment id the amendment record actually lacks — an independent audit of this sprint found six citations of a non-existent "amendment `A-8`", now re-keyed `DAM-8` because it was a design proposal rather than a citation.

| # | Check | Clause | Note |
|---|---|---|---|
| A-01 | Artifact header completeness: status, scope, responsibility, authority source | §4 ¶1 | absent field ⇒ no authority. Presence, not correctness |
| A-02 | Registry ↔ Constitution consistency | §4 ¶1 | version and Active-status only; scope and responsibility are **not** diffed |
| A-03 | Adoption element completeness, incl. presence of a transition record | §2, §13 ¶3 | presence only; the eight elements are `P-A2` |
| A-04 | Absence of scientific records under `p1/records/**` | §9 ¶1 | underwrites the §5–§7 N/A discharges |
| A-05 | Authority and certainty lexemes in live paths | §1 ¶2, §8 ¶3 | all four §1 ¶2 words matched bare; false positives expected, dispositioned by `VER-4` |
| A-06 | Legacy index and banner coverage, with post-move path resolution | §4 ¶5, §14 | an entry resolving to no file is **not verified**, never skipped |
| A-07 | Credentials across full history, not HEAD | §10 ¶5 | proves presence, never absence. Permanently FAIL by construction |
| A-08 | Check honesty in CI: no suppressed exit codes, no shell mismatch | §12 ¶1 | the check that keeps the others truthful |
| A-09 | Identified humans available for attestation | §13 ¶3 | never returns PASS; git identity is not identity (§4 ¶4) |
| A-10 | Attestation field completeness, dispatched by declared document kind: the eight §13 ¶2 elements for an Independent reviewer attestation, the §13 ¶3-derived set for an adopter attestation; no unfilled placeholders and no unticked declarations | §13 ¶2, §13 ¶3 | NOT_VERIFIED until attestations exist, which is before change D, and for any file whose kind it cannot determine. Fixture-tested against both shipped templates (`tests/governance/test_check_adoption.py`) |

**Specified and not implemented.** `A-11` … `A-15` are RS-1's checks, listed in `RS-1_RESEARCH_STANDARD.draft.md` §9 and built under `AUT-4` before change E. Until then each is reported not verified and MUST NOT be cited as passed (§12 ¶1).

Four things remain undetectable from inside the repository and are the reason §13 wants two humans: backdated timestamps, history rewriting before the first check run, forged records absent signing, and work performed and discarded outside version control. E-9 and E-10 close the first three; the fourth is closed only by people.

### 7.4 Named manual review procedures — adoption scope

§12 ¶4: a requirement that is not mechanically decidable MUST have a named manual review procedure. These four cover the adoption change; each records a finding per review.

**Identifier scheme.** `P-A*` applies to change D, `P-L*` to Legacy disposition (`04_LEGACY_DISPOSITION.md` §5), and RS-1's `P-1` … `P-15` apply only to objects RS-1 governs, and therefore only after change E — except `P-15`, which binds only on an amendment to RS-1 itself. A procedure is never cited outside its scope.

| Id | Question | Method | Replaces |
|---|---|---|---|
| `P-A1` | Is each attestation's named party an identified human who is not an author of the change? | Confirm the name resolves to a person outside the repository, that the contact is routable, and that the git identity used to commit maps to that person. Compare authorship of every artifact in the change against the reviewer's non-authorship declaration. A-10 checks that the declaration is present; only this procedure assesses whether it is true (§4 ¶4) | — |
| `P-A2` | Does the transition record carry all eight §9 ¶3 elements? | For `T-0001` (and `T-0002` at E), confirm object, prior state, new state, criteria applied, evidence considered, authority, time, and rationale are each present and non-empty. A placeholder is an absence and fails the transition closed | `C-4` |
| `P-A3` | Did this change delete or edit a governed record? | Diff the change over `p1/records/**` and the Legacy paths; confirm no record file is deleted and that Legacy content is moved, not rewritten (§8 ¶2, §12 ¶2). At D the expected finding is "no such record exists", which is itself the evidence for the §14 row | `C-7`, `C-8` |
| `P-A4` | Is registration-before-execution claimed anywhere in this change? | Confirm no artifact in D represents a pre-adoption execution as confirmatory. Advisory only: commit timestamps are author-controlled and §5 ¶3's trigger is unblinded access, which may leave no trace. After E this becomes RS-1's `P-11` | `C-10` |

---

## 8. What this plan gives up

Stated so the trade is deliberate.

- **No Claims, Evidence, Hypotheses, or Principles** until RS-1 is amended. Findings are scoped Interpretations over Results.
- **No formal conformance claims or audits** as governed objects. §12 ¶1 traceability is still performed at each change; it is just not itself a registered artifact type.
- **No enforceable architecture boundaries.** The architecture record is descriptive; §10 ¶1 is satisfied, but §10's warning that a directory name is not proof of separation is answered by review rather than by machine.
- **No delegation.** All authority sits with one steward, so H-7 is a real throughput constraint and the successor requirement is load-bearing.
- **No emergency or conflict machinery.** §12 ¶2 and §4 ¶4 apply directly; there is no tracked object during a conflict interval.

Each is recoverable by one activation when the need is concrete. None is recoverable retroactively for records created in the meantime — which is why `registered_protocol` is in the minimum set and Claim is not: the first is permanently costly to omit, the second is not.
