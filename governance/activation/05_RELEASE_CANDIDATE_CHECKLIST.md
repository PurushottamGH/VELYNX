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

### 1.1 Observed state after the final engineering sprint

§1 above is retained unedited as the observation it was, at the revision it names. This subsection records the state at the later revision rather than rewriting the earlier one, because an observation record that is updated in place stops being evidence of anything.

| Observation | Command / path | Value |
|---|---|---|
| Revision | `git rev-parse HEAD` | `234454c47bfb67bc28f3be12da633112ef443748`, plus the sprint's uncommitted working-tree changes |
| Check run | `python scripts/governance/check_adoption.py` | `PASS=5, FINDINGS=3, FAIL=1, NOT_VERIFIED=1`; exit 1; blocking `A-07`, `A-10`. Recorded verbatim in `governance/checks/RUN_2026-07-25_C.md` |
| `A-05` lexeme scope | check output | 670 matches in 104 live-path files (was 665 in 102 at `RUN_2026-07-25_B.md`). Decomposed in `RUN_2026-07-25_C.md`: three of the five added matches arose between revisions and not from this sprint, and **6 of the 670 are the check reading its own recorded output** — `governance/checks/` is inside the live surface and every run record quotes `A-05`'s limitation line. `VER-4` should disposition that directory as a class |
| Governance test guards | `python -m pytest tests/governance -q` | **39 passed** — A-10 schema dispatch and fixtures, RS-1 §9 mapping and procedure-citation completeness, Registry authority 21-of-21, identifier-namespace segregation including amendment-citation validity |
| Whole-repository tests | `python -m pytest -q --continue-on-collection-errors` | 780 passed, 3 skipped, **15 pre-existing collection errors** under `tests/p1_os/` — recorded as `AUT-5`, not caused by this sprint |
| Constitution | `REPOSITORY_CONSTITUTION.md` | unchanged: `Status: Draft`, v1.2.0. No amendment was made or proposed |
| Registry | `GOVERNANCE_REGISTRY.yaml` | unchanged: `status: Draft`, `constitutional_steward: []`, both attestations `null` |
| Registry target | `GOVERNANCE_REGISTRY.target.yaml` | block E now grants **all 21** RS-1 transition tuples plus the four constitutional transitions; 8 `[COMPLETE …]` placeholders still require humans |
| Identifiers | `tests/governance/test_identifier_namespaces.py` | no design-space identifier appears in the live surface and no live identifier in the design set |

---

## 2. Task register, ordered by dependency

Seven waves. Every task inside a wave is parallel-safe. No task may start before its prerequisite is closed. `State` is measured: **done**, **partial** (with what remains), **open**.

### Wave 0 — start immediately; two items have the longest external lead time

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| SEC-1 | Security | Rotate the `gcp-key.json.json` credential at the provider | none | operator (outside repo) | provider rotation confirmation, referenced by identifier and timestamp in the dossier's unresolved-violations field | old key rejected by the provider; the fact is recorded, not the secret | open |
| SEC-2 | Security | Determine the credential's exposure window and whether the key was used, or record the exposure as the standing Unknown `U-a` | SEC-1 | provider audit logs referenced by identifier, or `U-a` | either the window is bounded from provider-side evidence, or `U-a` records that it is unbounded and why (§6 ¶5, §8 ¶1) | open — **permanently unresolvable inside the repository** (`X-3`). Added here because the roll-up counted `SEC-1`…`SEC-5` as five while only four rows existed, and `X-3` cited this identifier with nothing to point at |
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
| VER-4 | Verification | Disposition the `A-05` lexeme matches — **670 in 104 files** as measured at `RUN_2026-07-25_C.md`; the earlier figure of 665 in 102 was measured at an earlier tree: Tier assignment, or manual `P-L1` judgement, or recorded as accepted false positive. Scope is **all** live-path files, not only the Tier-2 directories — `docs/`, `evidence/`, and `audits/` carry matches and fall to Tier-3 directory rules | RE-4 | disposition table referenced by the dossier | every `A-05` file is dispositioned; none is silently ignored (§12 ¶1) | open |
| DOC-1 | Documentation | Freeze `AR-1` as a descriptive Level-4 record; confirm no normative phrasing crept in | RE-1 | `A-01` header pass; reviewer note | boundaries, dependencies, and rationale present; the record imposes no requirement, so it needs no Registry entry (§10 ¶1) | **done** |
| RE-6 | Repo eng | Prepare the Registry D-block edits from `GOVERNANCE_REGISTRY.target.yaml` (human-valued fields left as placeholders) | RE-1 | staged diff, not committed | every non-human field final; only `[COMPLETE …]` values outstanding | partial — target drafted, 8 placeholders |
| VER-1 | Verification | Build and record an advisory check run at the pre-D revision | RE-1 | `governance/checks/RUN_2026-07-25_B.md` at the current ten-check set; `RUN_2026-07-25.md` retained as the earlier nine-check run, superseded for currency only | output recorded verbatim, each check stating its own limitation, `NOT_VERIFIED` never reported as passed | **done** |
| VER-2 | Verification | Verify gate G-7: zero record files under `p1/records/**` | none | `A-04` PASS | the dossier's §5–§7 not-applicable discharge rests on a verified empty set | **done** |
| SEC-3 | Security | Enable commit signing and verify signatures on new commits | HG-1 | `git log --pretty=%G?` showing `G` on new commits | adoption-revision commits verify; unsigned history disclosed as-is | open — all inspected commits `N` |
| SEC-4 | Security | Enable branch protection on the default branch and record paths; require review on merge | none | platform settings export or screenshot referenced by the dossier | a record path cannot be force-updated by a single unreviewed push (§7 ¶1, §8 ¶2) | open — platform-side |
| AUT-2 | Automation | Wire `check_adoption.py` into CI as an advisory job that emits findings and cannot report an unavailable check as passed | AUT-1 | workflow diff; run output | `A-08` PASS with the new job included | open |
| AUT-3 | Automation | Broaden the history secret scan (`A-07`) beyond the two known path shapes | RE-1 | scan output recorded | scan runs over full history and states plainly that it proves presence, never absence | partial — `A-07` scans history, narrow patterns |
| AUT-5 | Automation | Repair whole-repository `pytest` collection: `tests/p1_os/` shadows the real package at `p1/tooling/p1_os/`, so a single session raises 15 `ImportError`s and, without `--continue-on-collection-errors`, executes nothing | none | a whole-repository run that collects cleanly | `python -m pytest -q` collects and runs without collection errors | open — **pre-existing, not introduced by the final engineering sprint** (reproduced with `--ignore=tests/governance`, which removes every file the sprint added). Non-gating: no governance artifact cites `pytest` output as conformance evidence, and the affected suites pass when invoked directly (`tests/p1_os` → 382 passed). `--import-mode=importlib` is not a fix: it trades these 15 errors for 8 others. Evidence in `governance/checks/RUN_2026-07-25_C.md` |


### Wave 1B — RS-1 preparation; no authority required; parallel with Wave 1A, gates only change E

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| RE-7 | Repo eng | Reconcile `p1/tooling/p1_os` to RS-1: settle `experiment` vs `registered_protocol` to one term, align state names, add a validation profile restricted to the six owned types | none | `enums.py` / profile diff; a failing attempt to create an unowned record type | no tool can create a record of a type no Active standard owns (§9 ¶1, §11 ¶3) | open |
| RE-8 | Repo eng | Finish RS-1: close its own §11 pre-activation checklist and confirm every MUST appears in the §9 verification mapping | RE-7 | RS-1 §11 with a measured state and evidence per item | each MUST maps to a check or a named manual procedure (§12 ¶1, ¶4); no item is ticked without repository evidence | partial — 3 of 9 §11 items closed (procedures `P-1`…`P-15` written, Registry target jurisdiction drafted at 21 tuples, §9 mapping complete and test-enforced); item 7 partial (target complete, live Registry not); 5 open: timestamp anchor, activation Unknowns, `A-11`…`A-15`, six record templates, Constitution Active |
| DOC-4 | Documentation | Write procedures `P-1`…`P-15`, `P-A1`…`P-A4`, and `P-L1` so a reviewer who did not author the change can execute them | RE-8 | procedure text inside RS-1, the plan, and the Legacy disposition record | each procedure states inputs, steps, and what it cannot determine (§12 ¶4) | **done** — `P-1`…`P-15` in RS-1 §9.1 (`P-8`…`P-12` for the decidable requirements with no implemented check, `P-13`/`P-14` for tooling honesty and representation limits, `P-15` for an RS-1 amendment), `P-A1`…`P-A4` in plan §7.4, `P-L1` in `04_LEGACY_DISPOSITION.md` §5 |
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
| HG-5 | Human gov | Adopter attestation | HG-3, **SEC-3**, HG-1 | `governance/attestations/ADOPTER_ATTESTATION.md` | all fields populated by an identified human with a routable contact; the commit carrying it is signed and verifies; no tool output substitutes (gate `G-9`) | partial — template exists |
| HG-6 | Human gov | Independent reviewer attestation for adoption | HG-3, **SEC-3**, HG-1 | `governance/attestations/INDEPENDENT_REVIEWER_ATTESTATION.md` | as above, by the second human, in the same revision as HG-5. Signing cannot be applied retroactively to a committed attestation, which is why `SEC-3` precedes rather than parallels this | partial — template exists |

### Wave 4 — change D, one revision

| ID | Cat | Task | Prerequisite | Owner | Expected evidence | Completion criterion | State |
|---|---|---|---|---|---|---|---|
| RE-9a | Repo eng | Commit the **candidate** revision: the 11 manifest items `CD-1`…`CD-11` **except** the two attestations — Constitution → Active, Registry → Active with steward, AR-1, Legacy index, dossier, Tier-1 banners, check output, `T-0001`, `governance/**` as Draft. Record its SHA and tree hash | all of Waves 0–2, HG-3 | candidate SHA and `git rev-parse <SHA>^{tree}`, recorded in the dossier §1 and both attestation drafts | no element absent except the attestations; no unrelated change present; `active_domain_standards: []` | open |
| RE-9b | Repo eng | Assemble D: add both attestations, written against the candidate SHA (`HG-5`, `HG-6`) | RE-9a, HG-5, HG-6, gates G-1…G-10 closed | staged revision; preflight gate table with every gate closed or disclosed | every one of `CD-1`…`CD-11` present, including `T-0001` with all eight §9 ¶3 elements | open |
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
| RE-11 | Repo eng | Assemble and merge E as one revision (squash): the 9 manifest items `CE-1`…`CE-9` — RS-1 → Active at 1.0.0 under `governance/standards/`, Registry entry with the 21 jurisdiction tuples, `D-0001`, attestation, standing Unknowns, restricted `p1_os` profile, conformance record, **`T-0002` transition record**, and the **`authority_assignments` extension so the steward is permitted every RS-1 transition** | HG-9, DOC-6, RE-7, DOC-3, DOC-5, AUT-4 | merge SHA | one revision contains every element; the §4 ¶2 overlap test runs against an empty `active_domain_standards`. Omitting `CE-9` activates a standard that authorizes nothing: §4 ¶1 voids an authority whose permitted transitions are inconsistent, and every research transition then fails closed under §9 ¶3. Omitting `T-0002` leaves RS-1's activation with no §9 ¶3 record, which RS-1 §2.1 requires in addition to `D-0001` | open |
| VER-7 | Verification | Post-E verification: overlap test recorded, six owned types validate, six unowned types fail closed | RE-11 | check output at the merge SHA; a failed unowned-type creation attempt | a record of an unowned type cannot be created; owned-type transitions require the §9 ¶3 eight elements | open |

### Instrument corrections — cross-wave; from the Constitutional Systems Audit

Not a wave. This set has no position in the dependency order because it does not add work to the change; it corrects the instruments the other waves use. Each `done` item was closed before the wave that depends on it, and the three open items are hardening that gates the D merge, not the engineering ahead of it.

These are corrections to Draft *instruments*, not unexecuted tasks. The audit's finding was that executing the register as written would have produced an adoption a competent reviewer must refuse — because the defects were in the dossier, the manifest, the Registry target, RS-1, and the checks, and were therefore invisible to a task register that did not contain them. They are recorded here so they are visible, and so this register's readiness figures cover them.

Numbering follows the audit's `AF-xx`. No item amends the Constitution; v1.2.0 is unchanged and no amendment is proposed.

| ID | Blocks | Defect | Fix | Artifacts | State |
|---|---|---|---|---|---|
| AF-1 | D | The §9 ¶1 discharge asserted "no object type is in use", which is false at the D revision: D creates six governance objects of five kinds and no Active standard owns any of them | Recorded interpretation 4.5 — constitutionally specified object types are not *subordinate* under §9 ¶1 — with the rejected alternative reading and a falsification test | dossier §3 and §4.5, plan §4, `GOVERNANCE_REGISTRY.target.yaml` D-block | **done** |
| AF-2 | D | Five cited checks (`C-4`, `C-7`, `C-8`, `C-9`, `C-10`) had no implementation, and two namespaces were in use; §12 ¶1 forbids citing an unavailable check as passed | One namespace `A-xx`; `C-xx` withdrawn; `A-10` attestation completeness **built**; the other four converted to named manual procedures `P-A1`…`P-A4`; RS-1's `A-11`…`A-15` marked `[NOT IMPLEMENTED]` and relied on by no row. **Reopened and re-closed by independent verification:** `A-10` applied the §13 ¶2 reviewer element set to every file in `governance/attestations/`, so it could not pass against either shipped template — the adopter document was missing six of eight elements and the reviewer document's `**not** an author` defeated a literal matcher. `A-10` now dispatches by declared document kind, carries a separate adopter element set, tolerates markdown emphasis, rejects unticked declarations, and reports `NOT_VERIFIED` for a file it cannot classify. Fixture tests assert PASS on both completed templates and FAIL on each element's removal | plan §7.3–7.4, dossier, RS-1 §9, `check_adoption.py`, both attestation templates, `tests/governance/test_check_adoption.py`, 02, this register | **done** |
| AF-3 | D | Five fields demanded the commit SHA of the revision containing them, and the dossier was told to cite a post-merge run — an unsatisfiable cycle | Attest the reviewed **pre-merge candidate** revision; post-merge run becomes a separate re-verification record; the two self-referential Registry SHA fields removed | dossier §1 and §1.1, manifest §1/§5/§6, both attestation templates, Registry target, `RE-9a`/`RE-9b`/`VER-1b`/`VER-5` | **done** |
| AF-4 | D, E | No adoption transition record, though §2 enumerates one and §9 ¶3 is unqualified as to object type | `NORMATIVE_TRANSITION_RECORD.template.md`; `T-0001` at D (`CD-11`), `T-0002` at E (`CE-8`); `A-03` now fails when `governance/transitions/` is empty; gate `G-10` | template, manifest, plan `E-12`, Registry target, `check_adoption.py`, dossier | **done** |
| AF-5 | D | The lexeme check omitted `authoritative`, one of §1 ¶2's four named words, and matched `absolute` only in fixed phrases | All four words matched bare in both the check and the index generator, with a two-way keep-in-sync note. Measured effect: 632 → 665 matches, 94 → 102 files | `check_adoption.py`, `generate_legacy_index.py` | **done** — re-disposition is `VER-4` |
| AF-6 | D | The banner check silently skipped index entries whose paths stopped resolving, so `RE-3`'s criterion became true by construction once `RE-2` moved the files | Index carries resolved `original -> current` Tier-1 paths; an entry resolving to neither is reported `NOT_VERIFIED`, never skipped | `generate_legacy_index.py`, `LEGACY_INDEX.md`, `check_adoption.py`, `RE-3` | **done** |
| AF-7 | E | RS-1 §2.2 required a Decision to authorize creating a Decision — an infinite regress, so no first Decision was creatable | §2.2 scoped to types other than `decision`; §2.2.1 exempts the decision lifecycle from the **prior-decision** requirement as a §3 ¶2 governance transition, while leaving §4 ¶1's Registry-listed-authority requirement in force; §7.3 separates self-authorization from self-reference; §7.2.1 states how the check applies to the decision lifecycle | RS-1 §2.2, §2.2.1, §7, §7.2.1, §7.3, §9 mapping, `P-9`, Registry target E-block | **done** |
| AF-8 | E | The steward's `permitted_transitions` omitted every RS-1 transition, so E would activate a standard authorizing nothing | E-block `permitted_transitions` carries **all 21** RS-1 tuples in mapping form plus the four constitutional strings; manifest `CE-9`; `RE-11` completion criterion. **Reopened and re-closed by independent verification:** the first fix granted 19 of 21, omitting `{decision, none → proposed}` and `{decision, proposed → withdrawn}`, while RS-1 §11, plan `E-13`, manifest `CE-9`, and this register all asserted coverage of every transition — one artifact against four. Resolved by completing the Registry (Route A) rather than by narrowing the four claims, because "any contributor" as the authority for two tuples was an authority assignment made outside the Registry, which §2 reserves to it and §4 ¶1 voids. Verified 21-of-21 mechanically | Registry target, RS-1 §2.2.1/§7/§11, manifest §4, plan `E-13`, `tests/governance/test_registry_authority_coverage.py`, this register | **done** |
| AF-9 | E | RS-1 granted recording authority to "the executing actor" and opening authority to "any contributor", enlarging what §4 ¶5 reserves | Authority rows name the Registry-listed authority; authorship separated from authority throughout; the throughput exposure recorded as an activation Unknown rather than engineered away; §2.2.2 permits explicitly coupled transitions. **Extended:** independent verification observed that §7's `decision` row still named "any contributor" as an authority — the same enlargement, one type later. The AF-8 Route A resolution removes it, so the authorship/authority separation is now uniform across all six owned types | RS-1 §2.2.1, §4, §5, §6.3, §7, §2.2.2 | **done** |
| AF-10 | E | Two dangling exits and one missing abandonment path; §9 ¶3 fails an unlisted transition closed, so those records could be created and never disposed of | Three tuples added — `registered_protocol draft → withdrawn`, `decision proposed → withdrawn`, `interpretation draft → withdrawn` — with entry criteria; jurisdiction is 21 tuples in both RS-1 §1 and the Registry target | RS-1 §1, §3, §7, §8, Registry target | **done** |
| AF-11 | E | Inverted modals: "No record MUST be physically deleted" and "No record MUST use proven…" prohibited nothing on their face | Rewritten as "A record MUST NOT …" in both clauses | RS-1 §2.5, §2.8 | **done** |
| AF-13 | D (hardening) | `AR-1` declares `Status: Active`, a term §2 defines for Registry-listed Normative artifacts and for standard-governed objects; `AR-1` is deliberately neither, so §11 ¶3 is breached and `A-01` passes because it checks presence only | Status word changed to `Current — descriptive Level-4 record`, with the reason stated in the header: `Active` is constitutional terminology for a different type. `A-01` still passes, because the field is present; the dossier's §11 ¶3 row now has a true subject to verify | `governance/AR-1_REPOSITORY_ARCHITECTURE_RECORD.md`, dossier §2 §11 row | **done** |
| AF-15 | D (hardening) | The dossier's scale claim, "roughly 112 MUSTs and 44 MUST NOTs", overstates the MUST count; this is the number that justifies the N/A strategy to the reviewer | Recounted mechanically: **115** MUST-family occurrences — **44** `MUST NOT`, **71** bare `MUST`. The template now carries the measured figures, the command that reproduces them, and the statement that these are occurrences rather than distinct requirements | dossier §0 | **done** |
| AF-19 | D (hardening) | `G-9` is closable by an unsigned commit from a non-routable identity: `SEC-3` and `SEC-4` are non-gating and every inspected commit is `%G? = N` | `G-9` now requires routable contact addresses **and** that the commits carrying the attestations are signed and verify; the manifest states why, and `SEC-3` plus `HG-1` are prerequisites of `HG-5`/`HG-6` rather than parallel hygiene, because signing cannot be applied retroactively | manifest §2, `SEC-3`, `HG-1`, `HG-5`, `HG-6` | **done** |
| AF-23 | E | RS-1 §2.6 required "Every state change MUST be reversible" while §3 stated "registration is not reversible" — a flat internal contradiction. Constitution §8 ¶2 says "Every **scientific** state change", so RS-1 had over-broadened the clause it was citing | §2.6 narrowed to §8 ¶2's own scope word; new §2.6.1 defines reversal as annulling the *effect* by a later authorized `decision` while retaining every record, never by edit or deletion; §3 restated as "registration is not **undone**, and its §8 ¶2 reversal route is supersession", which removes the contradiction without weakening §8 ¶2 | RS-1 §2.6, §2.6.1, §3, §9 mapping | **done** — raised in independent verification, not in the original audit |
| AF-24 | E | RS-1's own verification apparatus contradicted its own §2.2.1 exemption: §7.2 and procedure `P-9` instructed the reviewer to locate an approving `decision` for **every** transition record, with no decision-lifecycle carve-out. Executed as written, `P-9` would have failed closed every Decision creation the standard expressly permits — defeating the exemption at the point of verification rather than in its text | `P-9` dispatches on object type: for a non-`decision` type it locates the approving `decision` and resolves the approver against the Registry; for a `decision` transition it confirms the recorded authority is Registry-listed and permitted for the tuple and requires no approving decision. New §7.2.1 states the two branches; the §9 mapping carries rows for §2.2.1 and §7.2/§7.2.1 | RS-1 §7.2.1, §9 mapping, §9.1 `P-9` | **done** — found in adjudication; reported by neither the audit nor the first independent verification |
| AF-25 | D, E | Identifier namespace collisions beyond the withdrawn `C-xx`: the Draft design register spent `A-01`…`A-63` on different checks than the implemented `A-01`…`A-15`; `G-1`…`G-12` denoted both governance-stack standards and the manifest's preflight gates; `D-1`…`D-3` denoted design defects, amendment-record derived amendments, **and** the manifest's change-D contents; `X-1`…`X-7` denoted both extension points and external blockers; `E-1`…`E-9` denoted both plan engineering tasks and the manifest's change-E contents. Plan §7.3's claim that "`A-xx` means exactly one thing" was false across fifteen identifiers | Design register re-keyed to a segregated namespace — `DA-xx` checks, `DG-x` stack standards, `DD-x` defects, `DX-x` extension points, `DF-x` redesign forces; live-shaped tokens in `governance/design/**` fell from 665 to 12, and the 12 remaining are the disambiguation table that must name them. Manifest change contents re-keyed to `CD-x`/`CE-x` (23 rewrites) and every cross-reference updated. Plan §7.3 restated truthfully with the full namespace register. Citations of another artifact's ids (amendments `A-1`…`A-7`, amendment-record findings `F-xx`, limitation `L-4`) deliberately not renamed, since renaming a citation breaks it; the padding convention that distinguishes them is documented. **Reopened once more by an independent audit of this sprint:** "amendment `A-8`" was cited six times and does not exist — the amendment record stops at `A-7` — so it was a design proposal, not a citation, and is re-keyed into the design namespace; the design README's extension-point range was also cited one past its end. Both fixed, and both now enforced by tests that parse the amendment record's own headings and assert the extension-point range is contiguous with nothing cited beyond it | `governance/design/**`, manifest §3–§5, plan §7.3, `governance/design/README.md`, RS-1 §9, this register, `tests/governance/test_identifier_namespaces.py` | **done** — understated by the audit, measured in adjudication, completed after independent audit |

Out of scope of this register by the audit's own recommendation, and unchanged: `AF-12`, `AF-14`, `AF-16` (closed in passing — squash is now mandatory), `AF-17`, `AF-18`, `AF-20`, `AF-21`, `AF-22`. `AF-17` (assign two stewards rather than one plus an inert successor) is an operational decision for `HG-4`, not an engineering task, and is the only action available today that forecloses the single unrecoverable state the Constitution contains.

**Three review rounds, three sets of findings in work already marked done.** Independent verification reopened `AF-2` and `AF-8`. Adjudication found `AF-23`, `AF-24`, `AF-25`. An independent audit of the final engineering sprint then found nine further defects — including a fabricated before/after figure inside the sprint's own check-run record, a dangling `A-8` identifier that left `AF-25` incomplete, a namespace guard that was dead code, two stale test counts, a missing `SEC-2` row, and a scratch file left at the repository root that would have ridden into the candidate revision. All nine are fixed, and each is recorded in `audits/AF_RESOLUTION_DOSSIER.md` §12 with the evidence that found it. The severity is falling — this round produced no authority defect, no false ticked box, and no arithmetic error in this register — but the rate is not zero, and no figure in this document should be read as evidence that it has reached zero.

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
| Security | SEC-1…SEC-5 | 5 | 1 | 0 | Credential rotation, exposure-window determination, signing, branch protection, external timestamping. `SEC-2` had no row until an independent audit noticed the count claimed five and the register defined four |
| Documentation | DOC-1…DOC-6 | 6 | 2 | 2 | Architecture record, conformance dossier, procedures, templates, Unknowns |
| Verification | VER-1, VER-1b, VER-2…VER-7 | 8 | 7 | 2 | Recorded check runs, manual sweeps, atomicity audit, post-merge confirmation |
| Automation | AUT-1…AUT-5 | 5 | 0 | 0 | Advisory checks and CI honesty. §12 ¶3 is SHOULD; none of it is obligatory and none of it confers authority |
| Instrument correction | AF-1…AF-11, AF-13, AF-15, AF-19, AF-23, AF-24, AF-25 | 17 | 17 | 17 | Correctness of the adoption instruments themselves — the axis the register previously did not carry |
| **Total** | | **63** | **43** | **21** | |

D-gating = mapped to a preflight gate G-1…G-10 in `03_ADOPTION_CHANGE_MANIFEST.md` §2, or, for the instrument-correction set, load-bearing for a gate's evidence. Automation is deliberately zero-gating: no check output closes a gate (§4 ¶4).

The instrument-correction row is counted separately and deliberately. Its items were defects in Draft instruments rather than unexecuted tasks, which is why they were absent from the register until the audit found them; folding them into the six functional categories would hide that distinction again.

The row grew from fourteen items to seventeen across two rounds of external scrutiny, and that history is the point. `AF-1`…`AF-11` came from the Constitutional Systems Audit. `AF-13`, `AF-15`, `AF-19` were left open by it as hardening. `AF-2` and `AF-8` were then **reopened** by independent verification, which found that both had been closed on evidence that did not hold — `A-10` could not pass against either shipped attestation template, and the Registry target granted 19 of the 21 transitions that four artifacts claimed it granted. `AF-23`, `AF-24`, and `AF-25` were found afterwards, in adjudication: a reversibility contradiction inside RS-1, a verification procedure that contradicted the normative section it was written to verify, and identifier collisions across five prefixes. Two of the three were reported by neither the audit nor the first independent verification. A register that reads "all done" after one review round is a register that has not been reviewed twice.

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
| Instrument correctness | 17 | 17 | **100%** |

Credit awarded for D: `DOC-1` 1.0, `VER-1` 1.0, `VER-2` 1.0, `RE-6` 0.75, `HG-7` 0.5, `RE-5` 0.5, `DOC-2` 0.25, `HG-5` 0.25, `HG-6` 0.25. For E: `DOC-4` 1.0, `RE-8` 0.75, `DOC-3` 0.5, `DOC-5` 0.5. For instrument correctness: all seventeen closed.

**D and E readiness did not move in the final engineering sprint, and should not have.** The sprint corrected instruments; it executed no task. `RE-8` keeps 0.75 rather than rising, because RS-1's §11 still has five open items — the timestamp anchor, the activation Unknowns, `A-11`…`A-15`, the six record templates, and an Active Constitution — none of which this sprint touched. Awarding credit for instrument repair inside the D and E figures is exactly the conflation the instrument-correction row exists to prevent.

The D denominator rose from 24 to 26 because `RE-9` split into `RE-9a` and `RE-9b` and `VER-1b` was added — both consequences of the self-reference fix, not new scope. D readiness therefore reads slightly *lower* than before while the repository is strictly more ready: the register got more honest, not the work less complete. E rose from 13% to 23% on RS-1 becoming functional (`AF-7`…`AF-11`) and the manual procedures being written.

**Instrument correctness is the axis that changed, and it is the one that decides whether the register can be executed at all.** At the audit it stood near 55%: the design was complete and frozen, but the D revision could not be assembled as specified, its conformance instrument cited five checks that did not exist, its largest discharge was asserted rather than argued, and it omitted an element §2 enumerates. It then read 79% with three hardening items open — and that figure was itself too generous, because two of the eleven "closed" items were closed on evidence that did not hold: `A-10` could not pass against either attestation template it must validate, and the Registry target granted 19 of 21 transitions while four artifacts said 21. Both are now repaired and mechanically verified, the three hardening items are closed, and three further defects found in adjudication (`AF-23`, `AF-24`, `AF-25`) are closed.

**100% here means every accepted engineering defect is closed with cited evidence — not that no defect remains.** The figure was 79% before an independent verifier and an adjudicator read the same artifacts and found five more. The honest reading is that this axis is complete *against the findings raised so far*, which is why one more independent verification is the next step rather than adoption.

Three further numbers matter more than the headline:

**Specification readiness: high.** All seven activation objectives are answered, RS-1 is drafted in full and is now internally executable, both attestation templates and the transition-record template exist, the Registry target carries both blocks, and ten checks run and report honestly. The design is frozen and nothing in this checklist proposes changing it. The gap is not knowledge; it is execution.

**In-repository ceiling: 54% of D.** Fourteen of the 26 D-gating tasks are completable without a second human — `RE-1`…`RE-6`, `DOC-1`, `DOC-2`, `VER-1`…`VER-4`, `HG-7`, and `SEC-1` by the operator. The remaining twelve require `HG-2`. So the maximum honest readiness reachable by work alone is 54%, and 33 points of that are currently unclaimed engineering.

**Adoption-possible readiness: 0%.** Readiness is not the fraction that matters for the merge decision. Gates G-1 and G-2 are binary, both open, and either one open means adoption MUST NOT proceed. At 54% the repository would be fully prepared and still unable to adopt.

Gate status, which is the decision-relevant view: G-3 pending `RE-1`, G-4 **closed**, G-7 **closed**, G-1 open (X-1), G-2 open (X-2), G-5 open, G-6 open, G-8 open, G-9 open, G-10 open — the transition-record template exists but `T-0001` itself is written at assembly step 7. **Two of ten closed.**

---

## 7. Release-candidate recommendation

Prepare, do not adopt. Close Waves 0, 1A, 1B, and 2 — that is 33 points of readiness, all of it unblocked, none of it requiring authority — and hold at the gate table. `RE-1` first, since committing the Draft baseline costs nothing (§4 ¶5, §9 ¶4) and protects the work; keep `status: Draft` and empty steward and attestation fields in every intermediate commit.

Close the three open instrument-correction items (`AF-13`, `AF-15`, `AF-19`) in the same window. None takes long, all three are inside the repository, and `AF-19` cannot be retrofitted after the attestations are committed.

**Update after the final engineering sprint.** All seventeen instrument-correction items are now closed, including those three and three found later (`AF-23`, `AF-24`, `AF-25`). The recommendation is unchanged: **prepare, do not adopt.** Nothing in this sprint moved a gate, and nothing in it could: `G-1` needs a person and `G-2` needs a provider action. What changed is that the instruments the register executes are now internally consistent and their acceptance claims are backed by reproducible evidence rather than by assertion. The next step is one more independent verification of the instruments, not adoption — the previous two review rounds each found defects in items already marked done.

The repository is not the constraint. Two people and one provider action are.
