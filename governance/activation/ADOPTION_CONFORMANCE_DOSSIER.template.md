# Adoption Conformance Dossier — template

- **Status:** Draft (template)
- **Scope:** Constitutional conformance of the §13 ¶3 adoption atomic change, at one identified revision
- **Responsibility:** Provide the §12 ¶1 traceability record the Independent reviewer needs
- **Authority source:** None. This template records conformance; it does not create, confer, or certify authority.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0
- **Version:** 0.1.0

---

## 0. How this reduces burden

§12 ¶1 requires an Independent reviewer to trace every **Affected** requirement expressed as MUST or MUST NOT to one of exactly three things:

1. an automated check and its output;
2. a manual inspection procedure and a version-controlled finding;
3. **a statement that the requirement is not applicable, with a testable reason.**

At adoption the repository contains no scientific records and no Active Domain standard. The whole of §5, §6, and §7, and most of §8 and §9, therefore discharge under route 3 — verifiably, because "no record of this kind exists at revision X" is checkable by inspecting an empty directory.

This is the difference between a reviewable adoption and an unreviewable one. It is not a loophole: §12 ¶1 names route 3 explicitly, and each N/A below states the condition that would make the requirement applicable, so the discharge expires the moment the condition changes.

**Scale.** Of roughly 112 MUSTs and 44 MUST NOTs, the applicable set at adoption is confined to §1–§4 and §10–§14. Everything else is N/A with a testable reason.

---

## 1. Claim identification (§12 ¶1)

| Field | Value |
|---|---|
| Repository revision | `[COMPLETE]` full commit SHA of the **reviewed pre-merge revision** — the branch commit carrying the complete change *except* the attestations |
| Tree hash of that revision | `[COMPLETE]` `git rev-parse <SHA>^{tree}` |
| Accepted revision | Not recorded here. See §1.1 |
| Scope assessed | The adoption atomic change and the repository state it produces |
| Date and time | `[COMPLETE]` timezone-qualified, precision identified (§2) |
| Checks performed | `[COMPLETE]` `A-xx` ids and outputs, at the revision named above |
| Reviewer | `[COMPLETE]` identified human; not an author of this change (§2) |
| Unresolved violations | `[COMPLETE]` — **must be listed, not omitted.** A claim that omits known violations is itself a nonconformance |
| Limitations | `[COMPLETE]` — including anything not verified |

### 1.1 Why this dossier names a pre-merge revision

A commit cannot contain its own SHA. If this dossier, the two attestations, and the Registry all named "the adoption revision", none of them could be written until after the revision existed — and the revision cannot exist until they are written. The same loop runs through the check output: a dossier citing a post-merge run cannot be *in* the revision that run assesses.

The loop is broken by reviewing content that already exists:

1. **Candidate revision.** One branch commit carries everything in §3 of the manifest except the attestations. It has a SHA and a tree hash; both are named above.
2. **Review.** The reviewer assesses that revision, runs the checks against it, and records the output. That run is this dossier's cited evidence.
3. **Attestations.** Written against the candidate revision, naming its SHA — a revision that is not their own.
4. **Acceptance.** The branch is **squash-merged**, producing exactly one default-branch revision containing every element, with no intervening revision missing any (§2). The reviewer confirms `git diff <candidate> <merge>` shows only the attestation files.
5. **Re-verification.** The checks are run again at the accepted revision and recorded as a separate record. It is *not* this dossier's cited evidence, and it does not modify this dossier.

The merge method is not free choice here. A `--no-ff` merge leaves the candidate revision reachable from the default branch, and the candidate sets `Status: Active` — which is exactly what `VER-6` tests for and what gate `G-3` forbids. **Squash is required**; see `03_ADOPTION_CHANGE_MANIFEST.md` §1.

---

## 2. Applicable requirements — traced individually

These sections bind at adoption and require route 1 or route 2. Every row must be completed; none may be discharged as N/A.

### §1 Normative force

| Requirement | Route | Evidence |
|---|---|---|
| No artifact overrides the Constitution by declaring itself canonical, absolute, frozen, or authoritative | check | `A-05` output, which matches all four §1 ¶2 words bare. **Expect findings** against Legacy artifacts; each must be dispositioned by `VER-4` before this claim is asserted |
| Constitution is the highest repository governance standard | manual | `[COMPLETE]` — `P-L1`; confirm no artifact asserts precedence over it, including by paraphrase |

### §2 Operational definitions

| Requirement | Route | Evidence |
|---|---|---|
| Governance Registry is `GOVERNANCE_REGISTRY.yaml` | check | path exists at the repository root |
| Atomic change contains every required artifact, Registry entry, approval, attestation, **and transition record** | check + manual | `A-03` for element presence, including `governance/transitions/`; `P-A2` for the eight §9 ¶3 elements of `T-0001`; `VER-6` for the no-intervening-revision property after merge |
| Recorded time is timezone-qualified with precision identified | manual | `[COMPLETE]` — `A-01` checks header field presence only, not time formatting. Read the attestation, Registry, and transition-record time fields directly |
| Object kinds are not substituted for one another | N/A at adoption | testable reason: no record of any **scientific** kind exists — see §3 below. The governance objects this change does create are addressed in interpretation 4.5 |

### §3 Separation of responsibilities

| Requirement | Route | Evidence |
|---|---|---|
| Each artifact has one primary responsibility | manual | `[COMPLETE]` — assess the five artifacts in this change: Constitution, Registry, architecture record, Legacy index, transition record |
| Governance approval not represented as scientific support | manual | `[COMPLETE]` — confirm the dossier and the transition record claim authority only, and assert nothing scientific |
| Test success not reported as scientific success | manual | `[COMPLETE]` — `P-A4`; confirm no artifact in this change represents a test result or a pre-adoption execution as scientific support. `A-08` assesses CI honesty, which is a different question |

### §4 Authority and precedence

| Requirement | Route | Evidence |
|---|---|---|
| Every Normative artifact states status, Scope, responsibility, authority source | check | `A-01` — presence of each field, not its correctness |
| Registry carries the same values without contradiction | check + manual | `A-02` compares **version and Active-status only**; its own limitation line says so. Scope, responsibility, authority, and jurisdiction must be diffed by hand: `[COMPLETE]` |
| Registry rejects overlapping jurisdictions | manual | `[COMPLETE]` — **trivially satisfied**: `active_domain_standards: []`, so there is no second jurisdiction to overlap. No implemented check assesses overlap; `A-02` does not |
| Every authority source identifies jurisdiction and permitted transitions | check + manual | `A-01` for field presence; `[COMPLETE]` confirm the steward's `permitted_transitions` are present and consistent, since §4 ¶1 voids the authority otherwise |
| Automated systems do not supply human authority or independent review | manual | `[COMPLETE]` — `P-A1`; confirm both attestations name identified humans and no tool output substitutes for either |
| Legacy artifacts remain distinguishable from Active requirements | check + manual | `A-06`, which reports an index entry resolving to no file as **not verified**; plus `P-L1` on whether the result reads as Active to a first-time reader |
| A standard does not authorize its own activation | N/A | testable reason: no Domain standard is activated in this change; `active_domain_standards: []` is verifiable in the Registry |

### §9 Lifecycles and transitions

§9 ¶1 is discharged in §3 below, by interpretation 4.5. §9 ¶3 and §9 ¶4 are **not** discharged there: this change performs a transition of a Normative artifact, so both bind here.

| Requirement | Route | Evidence |
|---|---|---|
| A transition is valid only with a record identifying object, prior state, new state, criteria applied, evidence considered, authority, time, and rationale | check + manual | `A-03` confirms a transition record exists; `P-A2` confirms all eight elements of `T-0001` are present and non-empty |
| Missing information causes the transition to fail closed | manual | `[COMPLETE]` — confirm no field of `T-0001` is a placeholder. A `[COMPLETE]` left in place is missing information, and the transition is blocked rather than qualified |
| Tools MUST NOT infer maturity, acceptance, or rejection from evidence count, model confidence, test success, or elapsed time | manual | `[COMPLETE]` — `P-A4`; confirm nothing in this change treats a check result or elapsed time as acceptance. `A-09` is the pointed case: it never returns PASS regardless of author count |
| Normative artifacts use `Draft → Active → Superseded or Withdrawn`; prior versions remain recoverable | manual | `[COMPLETE]` — confirm the Constitution moves `Draft → Active` and no other state is introduced, and that v1.1.0 remains recoverable in history (§9 ¶4) |

### §10 Software and material state

| Requirement | Route | Evidence |
|---|---|---|
| Architecture and layout defined in versioned architecture records with boundaries, dependencies, rationale | manual | `[COMPLETE]` — cite the architecture record and confirm all three elements are present |
| Credentials and private keys not committed | check | `A-07` across **full history**, not HEAD alone. Expected **FAIL, disclosed** — see §1's unresolved-violations field. `A-07` proves presence, never absence |
| Generated, cached, secret, personal, runtime-only material separated and excluded | manual | `[COMPLETE]` |
| Material state declarations for stateful components | N/A at adoption | testable reason: this change adds no software. Becomes applicable at the first `software/` change |

### §11 Document responsibilities

| Requirement | Route | Evidence |
|---|---|---|
| Registry contains active Normative artifacts, jurisdictions, and authority assignments **only** | manual | `[COMPLETE]` — confirm no rationale, roadmap, or narrative has crept in |
| README is navigation and non-normative description | manual | `[COMPLETE]` — `P-L1`; confirm no requirement is introduced. `A-06` assesses banner coverage, not README content |
| Terminology from a higher artifact reused unchanged | manual | `[COMPLETE]` — §11 ¶3. Check in particular that no artifact in this change uses `Active` of an object that is neither Registry-listed nor standard-governed |

### §12 Conformance and enforcement

| Requirement | Route | Evidence |
|---|---|---|
| Every Affected MUST traced to check, procedure, or testable N/A | this dossier | self-referential and intended: the dossier *is* the discharge |
| Unavailable check reported as not verified, never passed | check + manual | `A-08` for CI honesty; plus `[COMPLETE]` confirm that no row above cites a check that does not exist. The implemented set is `A-01` … `A-10`; `A-11` … `A-15` are specified and unbuilt, and no row rests on them |
| Self-review not labelled independent | manual | `[COMPLETE]` — `P-A1`; confirm the reviewer is not an author |
| Tools and audits report nonconformance and do not redefine it away | manual | `[COMPLETE]` — confirm known findings appear in §1's unresolved-violations field |

### §13 Amendments and adoption

| Requirement | Route | Evidence |
|---|---|---|
| Attestations by two identified humans, adopter and Independent reviewer | manual | `[COMPLETE]` — `P-A1`; both files, both humans named, both resolvable outside the repository |
| Attestation identifies reviewed revision, non-authorship, Evidence production, conflicts, procedure, conclusion, competence, records examined | check | `A-10` — all eight elements present and no unfilled placeholder. Whether the declarations are *true* is `P-A1` |
| Same atomic change activates Constitution, creates or activates Registry, assigns ≥1 steward | check | `A-03` |
| Adoption becomes Active only when the complete change is accepted to the default branch | manual | `[COMPLETE]` — confirmed at merge by `VER-6`, and recorded in the post-merge re-verification record, not here (§1.1) |
| Amendments do not retroactively alter prior scientific records | N/A | testable reason: this is an initial adoption, not an amendment, and no prior record's meaning is altered — see §4 |

### §14 Adoption

| Requirement | Route | Evidence |
|---|---|---|
| Every non-activated Normative artifact becomes Legacy | manual | `[COMPLETE]` — `VER-3`; cite the Legacy index and its own completeness statement, which declares the known false negative rather than claiming completeness |
| Existing scientific records preserved | manual | `[COMPLETE]` — `P-A3`; confirm no record file is deleted and Legacy content is moved rather than rewritten. At this revision the expected finding is that no scientific record exists to preserve, which `A-04` verifies |

---

## 3. Not applicable at adoption — with testable reasons

Each row states the condition under which the requirement becomes applicable. The discharge expires when that condition is met.

| Clause group | Requirements | Testable reason | Becomes applicable when |
|---|---|---|---|
| **§5** Scientific claims | Claim Scope and falsifier; the eight §5 ¶2 fields; pre-access protocol fixing; Interpretation null and alternatives; Principle falsifiability | No Claim, Hypothesis, Interpretation, or Principle record exists at this revision. Verifiable: no record store for these kinds exists, and no record declares these object types | The first record of any of these kinds is created — which cannot occur before a Domain standard owns the kind (§9 ¶1) |
| **§6** Evidence and provenance | The nine identification items; admission and exclusion procedure; digest algorithm; derived-summary linkage | No Evidence record exists. Verifiable by the same means | An Active standard owns `evidence` and the first record is created |
| **§7** Results, interpretations, negative findings | Result immutability; completion and recording authority; Interpretation content; Negative Result retention; Invalid Result exclusion | No Result or Interpretation record exists. Verifiable by the same means | RS-1 activates and the first Result is recorded |
| **§8 ¶1** Unknowns | Unknown permanence; the five mandatory intake triggers | No Unknown record exists, and no governed scientific transition has occurred that could generate one | The first governed scientific work begins |
| **§8 ¶2** Reversibility | Every scientific state change reversible; records not deleted | No scientific state change has occurred | The first scientific transition |
| **§8 ¶3** Certainty labels | Prohibited labels for empirical Claims | No empirical Claim exists. **Note:** the lexical check `A-05` still runs against all artifacts under §1 ¶2, so this is a narrow N/A | The first Claim |
| **§9 ¶1** Per-type lifecycles | Exactly one Active Domain standard per **subordinate** object type, defining nine elements | **No subordinate object type is in use.** Not: no object type is in use — this change creates six governance objects of five kinds, and no Active standard owns any of them. Each is specified directly by the Constitution, so none is subordinate. The argument, and the reading it rejects, are recorded as **interpretation 4.5**; `A-04` verifies separately that no *scientific* record exists | RS-1 activates — at which point RS-1 supplies the nine elements for its six types, and the requirement is satisfied positively rather than by interpretation |
| **§10 ¶2-4** Material state, execution recording, implementation/validation independence | Declarations, seed recording, independent changeability | This change adds no software and records no execution | The first `software/` or execution change |

**Reviewer note.** Every reason above is checkable in under a minute by confirming the absence of records of the named kind. If any is false — if a record of one of these kinds exists anywhere in the change — the corresponding N/A is void and that clause group must be traced individually before this claim may be asserted.

---

## 4. Recorded interpretations

Not amendments. Recorded so the reasoning is inspectable rather than inferred, and so a later reviewer need not reconstruct it.

**4.1 Initial adoption, not amendment.** The Constitution is Draft and has never been Active. §13 ¶4's amendment path presupposes a Registry-listed constitutional steward, and none exists; treating this as an amendment would require an authority that the change itself creates. §14's language — "Upon adoption, this Constitution supersedes the prior `REPOSITORY_CONSTITUTION.md`" — also fits an adoption event. This change proceeds under **§13 ¶3 initial adoption**.

**4.2 Zero Domain standards at adoption is conforming.** §13 ¶3's list is Constitution, Registry, steward, two attestations. No Domain standard appears, and §9 ¶1 excepts Domain standards from per-type ownership. `active_domain_standards: []` is therefore a valid Active state, and §9 ¶1 is satisfied vacuously because no subordinate object type is in use.

**4.3 The architecture record is descriptive.** §10 ¶1 requires layout to be *defined in* versioned architecture records; it does not require those records to be normative. Kept descriptive, the record imposes no requirements, is therefore not a Normative artifact under §2, and needs no Registry entry. Enforcement of its boundaries is optional under §12 ¶3's SHOULD.

**4.4 Legacy disposition is engineering, not authority.** §14 strips authority automatically. §4 ¶5's remaining duty is distinguishability, discharged by file placement and labelling. Moving a file is not a scientific transition, and content is preserved in history, satisfying §8 ¶2. No Decision is required.

**4.5 Constitutionally specified object types are not "subordinate" under §9 ¶1.** This is the interpretation the §9 ¶1 discharge rests on, and it is the largest single load-bearing claim in this dossier. It is stated here so that a reviewer can test it rather than have to reconstruct it — and so that a later challenge meets a recorded argument rather than an assumption.

*The problem.* §9 ¶1 requires every **subordinate** scientific or governance object type to have exactly one Active Domain standard defining nine elements. This change creates six governance objects of five kinds:

| Object created in this change | Count | Specified by |
|---|---|---|
| Attestation (adopter, Independent reviewer) | 2 | §13 ¶2, which fixes the required content exactly |
| Conformance claim (this dossier) | 1 | §12 ¶1, which fixes the required content exactly |
| Authority assignment (constitutional steward) | 1 | §4 ¶1 and §13 ¶3, which fix its required fields and permitted transitions |
| Architecture record (`AR-1`) | 1 | §10 ¶1, which fixes boundaries, dependencies, rationale |
| Transition record (`T-0001`) | 1 | §9 ¶3, which fixes all eight elements |

`active_domain_standards: []`, so **no Active Domain standard owns any of them**. An earlier draft of this dossier discharged §9 ¶1 by asserting that "no subordinate scientific or governance object type is in use". That assertion is false as stated, and an attentive reviewer would find it in minutes.

*The interpretation.* These five types are not subordinate. For each, the Constitution itself supplies what §9 ¶1 would otherwise delegate — the states, the entry criteria, the required content, and the authority. They are constitutional instruments, not objects governed *under* a standard, and "subordinate" is the word in §9 ¶1 that carries this distinction. §9 ¶1 binds the object types a Domain standard would govern; it does not bind the instruments by which the Constitution is adopted and operated.

*Why the alternative reading is unavailable.* Suppose "subordinate" were read to include them. Then adoption would require an Active Domain standard owning `attestation`. Activating any Domain standard requires, under §4 ¶2, an Independent reviewer attestation — so an attestation would have to exist before any standard could own attestations, and the standard would have to be activated before the attestation could exist. §13 ¶3 nonetheless *requires* two attestations at adoption. That reading therefore makes §13 ¶3 impossible to satisfy, and an interpretation that makes an express requirement unsatisfiable is not available. The regress is structurally identical to the one RS-1 §2.2.1 resolves for its own `decision` lifecycle.

*What this interpretation does not do.* It does not exempt these objects from any other clause: §13 ¶2 still fixes attestation content, §12 ¶1 still fixes this dossier's content, §9 ¶3 still requires all eight transition-record elements, and each is traced individually in §2 above. It creates no new object type and confers no authority. It is also not an amendment — §13 ¶1's amendment elements are not engaged, and the Constitution's text is unchanged.

*How to falsify it.* If a reviewer concludes that "subordinate" reaches these types, the consequence is not that this dossier needs a different reason — it is that adoption is impossible without a §13 amendment, and the correct action is to stop and say so (§12 ¶1). That is the test this interpretation must survive.

---

## 5. Reviewer's declaration

To be completed by the Independent reviewer. This is not the §13 ¶2 attestation, which is a separate artifact; this is the conformance conclusion the attestation will cite.

- [ ] I traced every Affected MUST and MUST NOT to a check output, a manual finding, or a testable N/A statement
- [ ] I verified each N/A reason by confirming the absence of records of the named kind
- [ ] I tested interpretation 4.5 and either accept it or have recorded my disagreement in §1's unresolved-violations field
- [ ] I confirmed that `T-0001` carries all eight §9 ¶3 elements, none left as a placeholder (`P-A2`)
- [ ] I am not an author of this change
- [ ] I did not produce Evidence under review
- [ ] I have disclosed all material conflicts of interest
- [ ] Every check I relied on actually ran; none reported as passed while unavailable
- [ ] **No row above cites a check that does not exist.** The implemented set is `A-01` … `A-10`; I confirmed each cited id is in it
- [ ] The revision I reviewed is the one named in §1, and I confirmed the merge adds only the attestation files
- [ ] Unresolved violations are listed in §1, not omitted
- [ ] I state my relevant competence and the records, artifacts, and checks I examined

**Conclusion:** `[COMPLETE]` — conforming / conforming with listed violations / nonconforming.

A reviewer who cannot complete every box should say so and stop. §9 ¶3's fail-closed rule and §12 ¶1's prohibition on reporting an unavailable check as passed both point the same way: an incomplete review is a blocked adoption, not a qualified approval.
