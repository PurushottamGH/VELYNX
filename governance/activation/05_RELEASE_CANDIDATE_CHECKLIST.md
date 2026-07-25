# Activation Checklist — release candidate for first constitutional adoption

- **Status:** Draft
- **Scope:** Every task required to reach change D (adoption of `REPOSITORY_CONSTITUTION.md` v1.2.0) and change E (activation of RS-1), at observed repository state 2026-07-25
- **Responsibility:** Enumerate, order, classify, and status every activation task; identify the critical path, the external blockers, and measured readiness
- **Authority source:** None. This record is a work register. It authorizes no transition, closes no gate, and creates no requirement.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft, not adopted)
- **Version:** 0.1.0

Derived from `00_MINIMUM_ACTIVATION_PLAN.md` §5–§7, `03_ADOPTION_CHANGE_MANIFEST.md` §2–§5, and `04_LEGACY_DISPOSITION.md`. It introduces no standard, no object type, and no requirement. Where those documents and this one disagree, they govern and this is stale.

---

## 1. Observed state at the time of writing

Verified, not assumed:

| Observation | Command / path | Value |
|---|---|---|
| HEAD | `git log -1` | `66e3e2a` |
| Working tree | `git status --porcelain` | 3 modified, 11 untracked paths; Constitution and Registry **uncommitted** |
| Constitution | `REPOSITORY_CONSTITUTION.md` | `Status: Draft; proposed for activation under Section 13`, v1.2.0 |
| Registry | `GOVERNANCE_REGISTRY.yaml` | `status: Draft`, `constitutional_steward: []`, both attestations `null`, `active_domain_standards: []` |
| Scientific records | `p1/records/**` | 12 directories, **0 files** |
| Check run | `python scripts/governance/check_adoption.py` | `PASS=5, FINDINGS=3, FAIL=1, NOT_VERIFIED=1`; blocking: `A-07`, `A-10`. Ten checks; `A-10` is `NOT_VERIFIED` by construction until attestations exist, which is change D |
| Identities in history | `git log` authors | 1 — `Purushottam <purushottam@local>` |
| Commit signatures | `git log --pretty=%G?` | `N` on every commit inspected |
| Legacy banners | index vs tree | 42 banner-required paths, **0 applied** |
| Tier-1 moves | `archive/legacy_normative/` | does not exist; all 6 move candidates still in live paths |
| Adoption artifact paths | `governance/{attestations,conformance,standards,decisions}` | none exist |
| Registry target | `GOVERNANCE_REGISTRY.target.yaml` | blocks D and E drafted; 8 `[COMPLETE …]` placeholders requiring humans |

Two states are complete and load-bearing: `p1/records/` is empty (the dossier's §5–§7 not-applicable discharge is mechanically true), and `AR-1_REPOSITORY_ARCHITECTURE_RECORD.md` exists with boundaries, dependency direction, rationale, and declared weaknesses.

---

## 2. Task register, ordered by dependency

Seven waves. Every task inside a wave is parallel-safe. No task may start before its prerequisite is closed. `State` is measured: **done**, **partial** (with what remains), **open**.

### Wave 0 — start immediately; two items have the longest external lead time

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| SEC-1 | Security | Rotate the `gcp-key.json.json` credential at the provider | none | operator (outside repo) | provider rotation confirmation, referenced by identifier and timestamp in the dossier's unresolved-violations field | old key rejected by the provider; the fact is recorded, not the secret | open |
| HG-1 | Human gov | Establish a routable, verifiable identity for the existing human (replaces `purushottam@local`) | none | `git config user.email` set to a routable address; identity mapping recorded in the adopter attestation | `A-09`'s identity note is answerable by something other than a local handle | open |
| RE-1 | Repo eng | Commit the Draft baseline: Constitution v1.2.0 (Draft), Registry (Draft), `governance/**`, `scripts/governance/**`, `theory/**` additions | none | commit SHA; `git show --stat` | working tree clean for those paths **and** `A-03` still reports "Constitution is Draft, adoption not attempted" | open |
| AUT-1 | Automation | Keep or revert the `ci.yml` honesty fix (PowerShell-on-ubuntu, three `\|\| true`, non-existent coverage targets, advisory mypy) | none | committed `ci.yml`; first post-commit run URL | no CI step can report an unassessed criterion as passed (§12 ¶1); a red run is an acceptable outcome | partial — fixed in working tree, uncommitted |

`RE-1` invariant, from `02_PREADOPTION_VERIFICATION.md` §5: every intermediate commit keeps `status: Draft`, `constitutional_steward: []`, attestations `null`. A commit that violates this is a nonconforming partial adoption.

### Wave 1A — adoption engineering; no authority required; runs in parallel with Wave 0

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| RE-2 | Repo eng | Move the 6 Tier-1 supremacy-asserting artifacts to `archive/legacy_normative/`; update `README.md` cross-references in the same change | RE-1 | `git log --follow` on each path; README diff | no live path contains an artifact titled or self-described as constitutional/canonical, except `p1/specifications/milestone-1-gpt56.md` which stays by design | open |
| RE-3 | Repo eng | Apply Tier-1 Legacy banners (7 files, including the one that stays in place) | RE-2 | banner text present in each file | `A-06` reports 0 Tier-1 paths lacking a banner **and 0 unresolvable entries**. The second clause is what makes the first non-vacuous: before it was added, moving a Tier-1 file silently removed it from the check | open |
| RE-4 | Repo eng | Apply Tier-2 one-line banners (35 files), with the preregistration banners stating explicitly that no registration transition occurred | RE-1 | banner text present | `A-06` reports 0 banner-required paths lacking a banner | open |
| RE-5 | Repo eng | Regenerate `governance/LEGACY_INDEX.md` after the moves, with its own completeness statement | RE-2, RE-3, RE-4 | `python scripts/governance/generate_legacy_index.py` output; index diff | index paths resolve against the tree; Tier-3 directory rules cover the remainder | partial — generated pre-move; must be regenerated |
| VER-3 | Verification | Manual completeness sweep of the index against the tree (procedure P-L1), performed by someone who did not generate it | RE-5 | signed sweep note naming the method and what it could not cover | a reader can determine Active vs not-Active for any artifact via Registry + index (§4 ¶5) | open |
| VER-4 | Verification | Disposition the 665 `A-05` lexeme matches in 102 files: Tier assignment, or manual `P-L1` judgement, or recorded as accepted false positive. Scope is **all** live-path files, not only the Tier-2 directories — `docs/`, `evidence/`, and `audits/` carry matches and fall to Tier-3 directory rules | RE-4 | disposition table referenced by the dossier | every `A-05` file is dispositioned; none is silently ignored (§12 ¶1) | open |
| DOC-1 | Documentation | Freeze `AR-1` as a descriptive Level-4 record; confirm no normative phrasing crept in | RE-1 | `A-01` header pass; reviewer note | boundaries, dependencies, and rationale present; the record imposes no requirement, so it needs no Registry entry (§10 ¶1) | **done** |
| RE-6 | Repo eng | Prepare the Registry D-block edits from `GOVERNANCE_REGISTRY.target.yaml` (human-valued fields left as placeholders) | RE-1 | staged diff, not committed | every non-human field final; only `[COMPLETE …]` values outstanding | partial — target drafted, 8 placeholders |
| VER-1 | Verification | Build and record an advisory check run at the pre-D revision | RE-1 | `governance/checks/RUN_2026-07-25_B.md` at the current ten-check set; `RUN_2026-07-25.md` retained as the earlier nine-check run, superseded for currency only | output recorded verbatim, each check stating its own limitation, `NOT_VERIFIED` never reported as passed | **done** |
| VER-2 | Verification | Verify gate G-7: zero record files under `p1/records/**` | none | `A-04` PASS | the dossier's §5–§7 not-applicable discharge rests on a verified empty set | **done** |
| SEC-3 | Security | Enable commit signing and verify signatures on new commits | HG-1 | `git log --pretty=%G?` showing `G` on new commits | adoption-revision commits verify; unsigned history disclosed as-is | open — all inspected commits `N` |
| SEC-4 | Security | Enable branch protection on the default branch and record paths; require review on merge | none | platform settings export or screenshot referenced by the dossier | a record path cannot be force-updated by a single unreviewed push (§7 ¶1, §8 ¶2) | open — platform-side |
| AUT-2 | Automation | Wire `check_adoption.py` into CI as an advisory job that emits findings and cannot report an unavailable check as passed | AUT-1 | workflow diff; run output | `A-08` PASS with the new job included | open |
| AUT-3 | Automation | Broaden the history secret scan (`A-07`) beyond the two known path shapes | RE-1 | scan output recorded | scan runs over full history and states plainly that it proves presence, never absence | partial — `A-07` scans history, narrow patterns |


### Wave 1B — RS-1 preparation; no authority required; parallel with Wave 1A, gates only change E

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| RE-7 | Repo eng | Reconcile `p1/tooling/p1_os` to RS-1: settle `experiment` vs `registered_protocol` to one term, align state names, add a validation profile restricted to the six owned types | none | `enums.py` / profile diff; a failing attempt to create an unowned record type | no tool can create a record of a type no Active standard owns (§9 ¶1, §11 ¶3) | open |
| RE-8 | Repo eng | Finish RS-1: close its own §11 pre-activation checklist (8 items) and confirm every MUST appears in the §9 verification mapping | RE-7 | RS-1 diff with all 8 boxes closed | no unchecked item remains; each MUST maps to a check or a named manual procedure (§12 ¶1, ¶4) | partial — draft complete, 8 items unchecked |
| DOC-4 | Documentation | Write procedures `P-1`…`P-11`, `P-A1`…`P-A4`, and `P-L1` so a reviewer who did not author the change can execute them | RE-8 | procedure text inside RS-1, the plan, and the Legacy disposition record | each procedure states inputs, steps, and what it cannot determine (§12 ¶4) | **done** — `P-1`…`P-11` in RS-1 §9.1 (including `P-8`…`P-11` for the decidable requirements with no implemented check), `P-A1`…`P-A4` in plan §7.4, `P-L1` in `04_LEGACY_DISPOSITION.md` §5 |
| DOC-5 | Documentation | Record templates for the six owned types, including the §9 ¶3 eight-element transition record | RE-7 | templates under `p1/templates/`; one worked example outside `p1/records/` | a transition missing any of the eight elements fails closed | partial — 11 legacy templates exist; the **Normative-artifact** transition record template exists at `governance/activation/templates/NORMATIVE_TRANSITION_RECORD.template.md` (used for `T-0001`/`T-0002`); the six owned-type record templates and the RS-1 §2.1 scientific transition-record template are absent |
| DOC-3 | Documentation | Draft standing Unknowns `U-a`…`U-f` as records for the E revision | RE-8, DOC-5 | draft files staged for `p1/records/unknowns/` | each has statement, reason, expected effect, and resolution criterion (§6 ¶5, §8 ¶1) | partial — drafted as a table in `02_PREADOPTION_VERIFICATION.md` §6 |
| SEC-5 | Security | Name an external timestamp anchor, or record the exposure as the standing Unknown `U-b` | none | anchor configuration, or `U-b` | RS-1 §3.2 is answered one way or the other; anchoring cannot be retroactive, so this precedes the first governed execution | open |
| AUT-4 | Automation | Build RS-1's checks `A-11`…`A-15` as advisory, in `scripts/governance/check_adoption.py`, and remove their `[NOT IMPLEMENTED]` marks from RS-1 §9 in the same change | RE-8 | check output recorded | each emits findings only, never approval (§4 ¶4); until built, each is reported not verified and MUST NOT be cited as passed (§12 ¶1) | open — specified in RS-1 §9, unbuilt |

### Wave 2 — the dossier join point

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| DOC-2 | Documentation | Complete `governance/conformance/ADOPTION_CONFORMANCE_DOSSIER.md` from the template: trace every Affected MUST / MUST NOT to a check, a named manual procedure, or a not-applicable statement with a testable reason | RE-5, VER-3, VER-4, VER-1, SEC-1 | completed dossier; every row cites a revision-pinned artifact | no Affected requirement is untraced; the unresolved-violations field lists V-1 and the unsigned-history and non-routable-identity residuals (§12 ¶1) | partial — template only, 8 placeholders |
| HG-7 | Human gov | Record the §13 adoption-path interpretation: this is initial adoption under §13 ¶3, not an amendment under §13 ¶4, because no Constitution has ever been Active and no Registry-listed steward exists | DOC-2 started | dossier interpretation section, signed by the adopter | the reasoning is recorded before adoption, not asserted after a challenge | partial — reasoned in plan §7.1 (H-9) and the dossier template |

`DOC-2` is the single join point of all adoption engineering. Everything in Waves 0–1A exists to make one of its rows citable.

**`DOC-2` is completed in two passes, and this is not a cycle.** Every substantive row is written before the candidate revision exists (`RE-9a`). Two fields cannot be: the candidate SHA with its tree hash, and the citation of the check run at that revision (`VER-1b`). Both are filled in on the candidate branch, in the same commit that becomes the candidate — so the dossier is complete *within* the revision it assesses, and nothing is added after the merge. The earlier arrangement, in which the dossier cited a post-merge run, is what produced the `DOC-2 → RE-9 → RE-10 → VER-5 → DOC-2` cycle; `03_ADOPTION_CHANGE_MANIFEST.md` §6 and the dossier §1.1 remove it, and `VER-5` is now a separate re-verification record.

### Wave 3 — human governance; blocked, and the block is absolute

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| HG-2 | Human gov | A second identified human accepts the Independent reviewer role, is not an author of D, and declares conflicts | HG-1 | named identity with contact, conflict declaration, competence statement | §2's "identified human" is satisfied by more than a git handle; §4 ¶4 forbids any automated substitute | **open — hard blocker** |
| HG-3 | Human gov | Independent review of D against the completed dossier | HG-2, DOC-2 | review record naming competence, the records examined, and the limits of the review (§13 ¶2) | the reviewer can trace every Affected MUST unaided; disagreements are recorded, not resolved by the adopter | open |
| HG-4 | Human gov | Assign the constitutional steward and a named successor | HG-3 | Registry `authority_assignments` populated in the D revision only | exactly one steward with the four permitted transitions, plus a named successor (§13 ¶3) | open |
| HG-5 | Human gov | Adopter attestation | HG-3 | `governance/attestations/ADOPTER_ATTESTATION.md` | all §13 ¶2 fields populated by an identified human; no tool output substitutes | partial — template exists |
| HG-6 | Human gov | Independent reviewer attestation for adoption | HG-3 | `governance/attestations/INDEPENDENT_REVIEWER_ATTESTATION.md` | as above, by the second human, in the same revision as HG-5 | partial — template exists |

### Wave 4 — change D, one revision

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| RE-9a | Repo eng | Commit the **candidate** revision: the 11 manifest items `D-1`…`D-11` **except** the two attestations — Constitution → Active, Registry → Active with steward, AR-1, Legacy index, dossier, Tier-1 banners, check output, `T-0001`, `governance/**` as Draft. Record its SHA and tree hash | all of Waves 0–2, HG-3 | candidate SHA and `git rev-parse <SHA>^{tree}`, recorded in the dossier §1 and both attestation drafts | no element absent except the attestations; no unrelated change present; `active_domain_standards: []` | open |
| RE-9b | Repo eng | Assemble D: add both attestations, written against the candidate SHA (`HG-5`, `HG-6`) | RE-9a, HG-5, HG-6, gates G-1…G-10 closed | staged revision; preflight gate table with every gate closed or disclosed | every one of `D-1`…`D-11` present, including `T-0001` with all eight §9 ¶3 elements | open |
| RE-10 | Repo eng | Merge D as exactly one accepted default-branch revision — **squash merge, mandatory** | RE-9b | merge SHA; `git diff <candidate> <merge>` showing only the attestation files | no intervening default-branch revision lacks a required element (§2). `--no-ff` is **not** permitted: it leaves the candidate revision — which sets `Active` and populates the steward — reachable from the default branch, which is what `G-3` forbids and `VER-6` tests for (manifest §1) | open |

### Wave 5 — post-D verification

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| VER-1b | Verification | Run the checks at the **candidate** revision and record that run as the dossier's cited evidence | RE-9a | `governance/checks/RUN_<date>_CANDIDATE.md` at the candidate SHA | the dossier cites a run that exists at review time and assesses the exact content the reviewer read (dossier §1.1 step 2, manifest §5 step 11) | open |
| VER-5 | Verification | Re-run the checks at the merged revision and record the output as a **separate post-merge re-verification record** | RE-10 | `governance/checks/RUN_<date>_POST_D.md` at the merge SHA | expected shape is "conforming with listed violations": headers, Registry consistency, adoption completeness, empty records, and check honesty pass; `A-05`/`A-06` dispositioned; `A-06` reports **zero unresolvable entries**; `A-07` **FAIL, disclosed**; `A-10` moves from not-verified to pass. This record is **not** the dossier's cited evidence — a dossier committed inside a revision cannot cite a run performed after that revision exists (manifest §6); it modifies nothing, and any divergence from `VER-1b` other than `A-10` is itself a finding | open |
| VER-6 | Verification | Audit §2 atomicity of the merge: confirm no earlier commit set `Active` or populated a steward | RE-10 | `git log -S` on the status and steward lines | the first revision in which any adoption element appears is the D revision | open |

### Wave 6 — change E, RS-1 activation

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| HG-8 | Human gov | Steward approves the RS-1 activation transition | VER-5, RE-8, DOC-4 | `governance/decisions/D-0001-activate-rs1.md` | approved by the steward named in the Registry, before the merge (§4 ¶2) | open |
| HG-9 | Human gov | Independent reviewer attestation for RS-1 | HG-8 | `governance/attestations/RS-1_INDEPENDENT_REVIEWER_ATTESTATION.md` | a second, separate attestation; the adoption attestation does not carry forward (§4 ¶2) | open |
| DOC-6 | Documentation | RS-1 conformance record: §12 ¶1 traceability for RS-1's own MUSTs | RE-8, DOC-4 | `governance/conformance/RS-1_CONFORMANCE_RECORD.md` | every RS-1 MUST traced to a check or a named procedure | open |
| RE-11 | Repo eng | Assemble and merge E as one revision (squash): the 9 manifest items `E-1`…`E-9` — RS-1 → Active at 1.0.0 under `governance/standards/`, Registry entry with the 21 jurisdiction tuples, `D-0001`, attestation, standing Unknowns, restricted `p1_os` profile, conformance record, **`T-0002` transition record**, and the **`authority_assignments` extension so the steward is permitted every RS-1 transition** | HG-9, DOC-6, RE-7, DOC-3, DOC-5, AUT-4 | merge SHA | one revision contains every element; the §4 ¶2 overlap test runs against an empty `active_domain_standards`. Omitting `E-9` activates a standard that authorizes nothing: §4 ¶1 voids an authority whose permitted transitions are inconsistent, and every research transition then fails closed under §9 ¶3. Omitting `T-0002` leaves RS-1's activation with no §9 ¶3 record, which RS-1 §2.1 requires in addition to `D-0001` | open |
| VER-7 | Verification | Post-E verification: overlap test recorded, six owned types validate, six unowned types fail closed | RE-11 | check output at the merge SHA; a failed unowned-type creation attempt | a record of an unowned type cannot be created; owned-type transitions require the §9 ¶3 eight elements | open |

### Instrument corrections — cross-wave; from the Constitutional Systems Audit

Not a wave. This set has no position in the dependency order because it does not add work to the change; it corrects the instruments the other waves use. Each `done` item was closed before the wave that depends on it, and the three open items are hardening that gates the D merge, not the engineering ahead of it.

These are corrections to Draft *instruments*, not unexecuted tasks. The audit's finding was that executing the register as written would have produced an adoption a competent reviewer must refuse — because the defects were in the dossier, the manifest, the Registry target, RS-1, and the checks, and were therefore invisible to a task register that did not contain them. They are recorded here so they are visible, and so this register's readiness figures cover them.

Numbering follows the audit's `AF-xx`. No item amends the Constitution; v1.2.0 is unchanged and no amendment is proposed.

| ID | Blocks | Defect | Fix | Artifacts | State |
|---|---|---|---|---|---|
| AF-1 | D | The §9 ¶1 discharge asserted "no object type is in use", which is false at the D revision: D creates six governance objects of five kinds and no Active standard owns any of them | Recorded interpretation 4.5 — constitutionally specified object types are not *subordinate* under §9 ¶1 — with the rejected alternative reading and a falsification test | dossier §3 and §4.5, plan §4, `GOVERNANCE_REGISTRY.target.yaml` D-block | **done** |
| AF-2 | D | Five cited checks (`C-4`, `C-7`, `C-8`, `C-9`, `C-10`) had no implementation, and two namespaces were in use; §12 ¶1 forbids citing an unavailable check as passed | One namespace `A-xx`; `C-xx` withdrawn; `A-10` attestation completeness **built**; the other four converted to named manual procedures `P-A1`…`P-A4`; RS-1's `A-11`…`A-15` marked `[NOT IMPLEMENTED]` and relied on by no row | plan §7.3–7.4, dossier, RS-1 §9, `check_adoption.py`, 02, this register | **done** |
| AF-3 | D | Five fields demanded the commit SHA of the revision containing them, and the dossier was told to cite a post-merge run — an unsatisfiable cycle | Attest the reviewed **pre-merge candidate** revision; post-merge run becomes a separate re-verification record; the two self-referential Registry SHA fields removed | dossier §1 and §1.1, manifest §1/§5/§6, both attestation templates, Registry target, `RE-9a`/`RE-9b`/`VER-1b`/`VER-5` | **done** |
| AF-4 | D, E | No adoption transition record, though §2 enumerates one and §9 ¶3 is unqualified as to object type | `NORMATIVE_TRANSITION_RECORD.template.md`; `T-0001` at D (`D-11`), `T-0002` at E (`E-8`); `A-03` now fails when `governance/transitions/` is empty; gate `G-10` | template, manifest, plan `E-12`, Registry target, `check_adoption.py`, dossier | **done** |
| AF-5 | D | The lexeme check omitted `authoritative`, one of §1 ¶2's four named words, and matched `absolute` only in fixed phrases | All four words matched bare in both the check and the index generator, with a two-way keep-in-sync note. Measured effect: 632 → 665 matches, 94 → 102 files | `check_adoption.py`, `generate_legacy_index.py` | **done** — re-disposition is `VER-4` |
| AF-6 | D | The banner check silently skipped index entries whose paths stopped resolving, so `RE-3`'s criterion became true by construction once `RE-2` moved the files | Index carries resolved `original -> current` Tier-1 paths; an entry resolving to neither is reported `NOT_VERIFIED`, never skipped | `generate_legacy_index.py`, `LEGACY_INDEX.md`, `check_adoption.py`, `RE-3` | **done** |
| AF-7 | E | RS-1 §2.2 required a Decision to authorize creating a Decision — an infinite regress, so no first Decision was creatable | §2.2 scoped to types other than `decision`; §2.2.1 exempts the decision lifecycle as a §3 ¶2 governance transition; §7.3 separates self-authorization from self-reference | RS-1 §2.2, §2.2.1, §7, Registry target E-block | **done** |
| AF-8 | E | The steward's `permitted_transitions` omitted every RS-1 transition, so E would activate a standard authorizing nothing | E-block `permitted_transitions` extended with the RS-1 tuples in mapping form; manifest `E-9`; `RE-11` completion criterion | Registry target, manifest §4, plan `E-13`, this register | **done** |
| AF-9 | E | RS-1 granted recording authority to "the executing actor" and opening authority to "any contributor", enlarging what §4 ¶5 reserves | Authority rows name the Registry-listed authority; authorship separated from authority throughout; the throughput exposure recorded as an activation Unknown rather than engineered away; §2.2.2 permits explicitly coupled transitions | RS-1 §4, §5, §6.3, §2.2.2 | **done** |
| AF-10 | E | Two dangling exits and one missing abandonment path; §9 ¶3 fails an unlisted transition closed, so those records could be created and never disposed of | Three tuples added — `registered_protocol draft → withdrawn`, `decision proposed → withdrawn`, `interpretation draft → withdrawn` — with entry criteria; jurisdiction is 21 tuples in both RS-1 §1 and the Registry target | RS-1 §1, §3, §7, §8, Registry target | **done** |
| AF-11 | E | Inverted modals: "No record MUST be physically deleted" and "No record MUST use proven…" prohibited nothing on their face | Rewritten as "A record MUST NOT …" in both clauses | RS-1 §2.5, §2.8 | **done** |
| AF-13 | D (hardening) | `AR-1` declares `Status: Active`, a term §2 defines for Registry-listed Normative artifacts and for standard-governed objects; `AR-1` is deliberately neither, so §11 ¶3 is breached and `A-01` passes because it checks presence only | Choose a status word defined for a descriptive Level-4 record and update the dossier's §11 ¶3 row | `governance/AR-1_REPOSITORY_ARCHITECTURE_RECORD.md` | open |
| AF-15 | D (hardening) | The dossier's scale claim, "roughly 112 MUSTs and 44 MUST NOTs", overstates the MUST count; this is the number that justifies the N/A strategy to the reviewer | Recount and correct | dossier §0 | open |
| AF-19 | D (hardening) | `G-9` is closable by an unsigned commit from a non-routable identity: `SEC-3` and `SEC-4` are non-gating and every inspected commit is `%G? = N` | Fold commit signing of the D revision and routable identities for both humans into `G-9`; make `SEC-3` a prerequisite of `HG-5`/`HG-6`, since signing cannot be applied retroactively to a committed attestation | manifest §2, `SEC-3`, `HG-5`, `HG-6` | open |

Out of scope of this register by the audit's own recommendation, and unchanged: `AF-12`, `AF-14`, `AF-16` (closed in passing — squash is now mandatory), `AF-17`, `AF-18`, `AF-20`, `AF-21`, `AF-22`. `AF-17` (assign two stewards rather than one plus an inert successor) is an operational decision for `HG-4`, not an engineering task, and is the only action available today that forecloses the single unrecoverable state the Constitution contains.

### Not gating, deliberately deferred

| ID | Cat | Task | Why deferred |
|---|---|---|---|
| HG-10 | Human gov | Steward decides which Legacy scientific content P1 still stands behind (§14) | Post-adoption. §14 removes authority automatically; re-endorsement is a later Decision, not an adoption prerequisite |
| — | Repo eng | Rewriting history to purge the credential | Recommended against as part of adoption. It invalidates every recorded commit reference and digest, adds nothing to §10 ¶5 compliance once the key is rotated, and requires its own approval |
| — | Governance | Any other Domain standard | `01_STANDARD_CLASSIFICATION.md`: 15 Optional and 8 Future, each with a named trigger. Activating beyond review capacity manufactures nonconformance under §12 ¶1 |


---

## 3. Category roll-up

| Category | IDs | Count | D-gating | Complete | What the category owns |
|---|---|---|---|---|---|
| Human governance | HG-1…HG-10 | 10 | 7 | 0 | Everything §4 ¶4 forbids automation from supplying: identity, review, attestation, steward assignment, approval |
| Repository engineering | RE-1…RE-8, RE-9a, RE-9b, RE-10, RE-11 | 12 | 9 | 0 | Legacy disposition, atomic-change assembly, Registry mechanics, tooling reconciliation |
| Security | SEC-1…SEC-5 | 5 | 1 | 0 | Credential rotation, signing, branch protection, external timestamping |
| Documentation | DOC-1…DOC-6 | 6 | 2 | 2 | Architecture record, conformance dossier, procedures, templates, Unknowns |
| Verification | VER-1, VER-1b, VER-2…VER-7 | 8 | 7 | 2 | Recorded check runs, manual sweeps, atomicity audit, post-merge confirmation |
| Automation | AUT-1…AUT-4 | 4 | 0 | 0 | Advisory checks and CI honesty. §12 ¶3 is SHOULD; none of it is obligatory and none of it confers authority |
| Instrument correction | AF-1…AF-11, AF-13, AF-15, AF-19 | 14 | 14 | 11 | Correctness of the adoption instruments themselves — the axis the register previously did not carry |
| **Total** | | **59** | **40** | **15** | |

D-gating = mapped to a preflight gate G-1…G-10 in `03_ADOPTION_CHANGE_MANIFEST.md` §2, or, for the instrument-correction set, load-bearing for a gate's evidence. Automation is deliberately zero-gating: no check output closes a gate (§4 ¶4).

The instrument-correction row is counted separately and deliberately. Eleven of its fourteen items were defects in Draft instruments rather than unexecuted tasks, which is why they were absent from the register until the audit found them; folding them into the six functional categories would hide that distinction again.

---

## 4. The critical path

One path, thirteen nodes. Every other task is off it, provided it finishes before `HG-3` begins.

```
HG-1  routable identity
  ↓
HG-2  second identified human accepts, declares conflicts        ← hard blocker
  ↓
HG-3  independent review against the completed dossier           ← requires DOC-2 closed
  ↓
HG-4  steward assignment (Registry D-block)
  ↓
RE-9a commit the CANDIDATE revision; note SHA and tree hash
  ↓
VER-1b run the checks at the candidate; record as the dossier's cited evidence
  ↓
HG-5 + HG-6   both attestations, written against the candidate SHA
  ↓
RE-9b assemble D (candidate + attestations)
  ↓
RE-10 squash-merge D as one revision
  ↓
VER-5 post-merge re-verification recorded separately
  ↓
HG-8  steward Decision D-0001
  ↓
HG-9  RS-1 independent reviewer attestation
  ↓
RE-11 merge E as one revision
  ↓
VER-7 post-E verification
```

`RE-9a` and `VER-1b` are on the path because of the self-reference constraint, not because of added work: the attestations must name a revision that already exists, and the dossier must cite a run against exactly that revision (dossier §1.1).

Two properties worth stating:

**The path is almost entirely human.** Eight of thirteen nodes are human governance; of the five that are not, three exist only to satisfy the self-reference constraint. No amount of engineering shortens it, and §4 ¶4 forecloses substituting tooling for any node.

**`DOC-2` is the join that can put engineering onto the path.** All of Waves 0–1A feed the dossier. If the second human becomes available before the dossier is complete, the critical path silently extends through `DOC-2` and its prerequisites. The scheduling instruction is therefore: finish Waves 0, 1A, and 2 now, while `HG-2` is open, so that the human's availability is never spent waiting on engineering. `SEC-1` shares this property — it gates the merge, not the review, but an unrotated credential blocks `RE-10` regardless of how ready everything else is.

---

## 5. Blockers that cannot be solved inside the repository

Six, plus one residual class. None is closable by editing files.

| # | Blocker | Blocks | Why the repository cannot close it | What closes it |
|---|---|---|---|---|
| X-1 | **A second identified human** | D and E entirely — `HG-2`…`HG-9`, therefore `RE-10` and `RE-11` | §13 ¶3 requires two identified humans and §4 ¶4 bars automation from supplying human authority or independent review. 23 of 23 commits are one identity. No file, script, or check can create a person | a person accepting the role, not an author of D, with declared conflicts |
| X-2 | **Credential rotation at the provider** | gate G-2, therefore `RE-10` | `A-07` proves `gcp-key.json.json` was added in 9 commits under 2 paths. Deletion and `.gitignore` do not reduce exposure; the key's validity lives at the provider | operator rotating the key; the repository can only record that it happened |
| X-3 | **Exposure-window determination** (`SEC-2`, Unknown `U-a`) | nothing — permanently unresolvable inside | the disclosure window and any use of the key are not observable from version control | provider audit logs; otherwise it stays an open Unknown |
| X-4 | **A routable, verifiable identity** (`HG-1`) | `HG-2`, and the quality of every attestation | `purushottam@local` is not routable. Git identity is self-asserted and is not identity | an identity that exists outside the repository |
| X-5 | **Branch protection and required review** (`SEC-4`) | not D; the credibility of §7 ¶1 and §8 ¶2 afterwards | these are hosting-platform settings, not version-controlled content | platform configuration, referenced by the dossier |
| X-6 | **External timestamp anchor** (`SEC-5`) | the first governed execution, not D | commit timestamps are author-controlled, so registration-before-execution is not provable from inside. Anchoring cannot be applied retroactively | a third-party anchoring service, or `U-b` recorded and accepted |
| X-7 | **The undetectable class** | the honesty of everything | backdated timestamps, history rewritten before the first check run, forged records absent signing, and work performed and discarded outside version control leave no repository evidence | `SEC-3` and `SEC-4` narrow three of them; the fourth closes only by people. This is why §13 wants two humans |

`A-07` is the one check that fails and will still fail after remediation: once a secret is in history, presence is permanent and provable while absence is not. The conforming end state is not a green check — it is a rotated key, a disclosed violation in the dossier, and `U-a` open. A dossier reporting `A-07` as passing would itself be the nonconformance (§12 ¶1).

---

## 6. Constitutional readiness

Measured as gating tasks complete over gating tasks total, crediting partial work fractionally. Percentages of a task register, not of confidence.

| Scope | Complete | Total | Readiness |
|---|---|---|---|
| Change D — adoption | 5.5 | 26 | **21%** |
| Change E — RS-1 activation | 2.75 | 12 | **23%** |
| Combined D + E | 8.25 | 38 | **22%** |
| Instrument correctness | 11 | 14 | **79%** |

Credit awarded for D: `DOC-1` 1.0, `VER-1` 1.0, `VER-2` 1.0, `RE-6` 0.75, `HG-7` 0.5, `RE-5` 0.5, `DOC-2` 0.25, `HG-5` 0.25, `HG-6` 0.25. For E: `DOC-4` 1.0, `RE-8` 0.75, `DOC-3` 0.5, `DOC-5` 0.5. For instrument correctness: `AF-1`…`AF-11` closed; `AF-13`, `AF-15`, `AF-19` open.

The D denominator rose from 24 to 26 because `RE-9` split into `RE-9a` and `RE-9b` and `VER-1b` was added — both consequences of the self-reference fix, not new scope. D readiness therefore reads slightly *lower* than before while the repository is strictly more ready: the register got more honest, not the work less complete. E rose from 13% to 23% on RS-1 becoming functional (`AF-7`…`AF-11`) and the manual procedures being written.

**Instrument correctness is the axis that changed, and it is the one that decides whether the register can be executed at all.** At the audit it stood near 55%: the design was complete and frozen, but the D revision could not be assembled as specified, its conformance instrument cited five checks that did not exist, its largest discharge was asserted rather than argued, and it omitted an element §2 enumerates. All four are now closed, along with the five defects that made RS-1 non-functional. The three that remain are hardening, not blockers to assembly: a status word (`AF-13`), a recount (`AF-15`), and folding signing and routable identity into `G-9` (`AF-19`).

Three further numbers matter more than the headline:

**Specification readiness: high.** All seven activation objectives are answered, RS-1 is drafted in full and is now internally executable, both attestation templates and the transition-record template exist, the Registry target carries both blocks, and ten checks run and report honestly. The design is frozen and nothing in this checklist proposes changing it. The gap is not knowledge; it is execution.

**In-repository ceiling: 54% of D.** Fourteen of the 26 D-gating tasks are completable without a second human — `RE-1`…`RE-6`, `DOC-1`, `DOC-2`, `VER-1`…`VER-4`, `HG-7`, and `SEC-1` by the operator. The remaining twelve require `HG-2`. So the maximum honest readiness reachable by work alone is 54%, and 33 points of that are currently unclaimed engineering.

**Adoption-possible readiness: 0%.** Readiness is not the fraction that matters for the merge decision. Gates G-1 and G-2 are binary, both open, and either one open means adoption MUST NOT proceed. At 54% the repository would be fully prepared and still unable to adopt.

Gate status, which is the decision-relevant view: G-3 pending `RE-1`, G-4 **closed**, G-7 **closed**, G-1 open (X-1), G-2 open (X-2), G-5 open, G-6 open, G-8 open, G-9 open, G-10 open — the transition-record template exists but `T-0001` itself is written at assembly step 7. **Two of ten closed.**

---

## 7. Release-candidate recommendation

Prepare, do not adopt. Close Waves 0, 1A, 1B, and 2 — that is 33 points of readiness, all of it unblocked, none of it requiring authority — and hold at the gate table. `RE-1` first, since committing the Draft baseline costs nothing (§4 ¶5, §9 ¶4) and protects the work; keep `status: Draft` and empty steward and attestation fields in every intermediate commit.

Close the three open instrument-correction items (`AF-13`, `AF-15`, `AF-19`) in the same window. None takes long, all three are inside the repository, and `AF-19` cannot be retrofitted after the attestations are committed.

The repository is not the constraint. Two people and one provider action are.
