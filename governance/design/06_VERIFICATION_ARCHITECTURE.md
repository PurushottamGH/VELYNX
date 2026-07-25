# Verification Architecture — the pipeline from proposal to ratification, audit, and reversal

- **Status:** Draft
- **Scope:** The verification pipeline for every governed change in Project P1, and the register of named manual review procedures
- **Responsibility:** Specify the stages, actors, entry and exit criteria, artifacts, and fail-closed behaviour of verification
- **Authority source:** None. This record has no normative authority. On activation its stages would be owned jointly by G-4, G-5, G-6, G-8, and G-11 within their declared jurisdictions.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. Invariants

Five rules constrain every stage. They come from §3, §4, and §12, and violating any one of them voids the verification regardless of how many stages passed.

**I-1 — No stage both produces and assesses the same artifact.** §3 ¶6: "validation MUST NOT alter the object it assesses"; "implementation MUST NOT validate itself merely by executing successfully." A reviewer who edits the change under review has become an author, and §2 removes their independence for that review.

**I-2 — Automation gates; it never approves.** §4 ¶4. Every automated stage emits findings and a verdict of `PASS` / `FAIL` / `NOT_VERIFIED`. None emits `APPROVED`.

**I-3 — Missing information fails closed.** §9 ¶3: "Missing information MUST cause the transition to fail closed." An absent check is `NOT_VERIFIED`, and `NOT_VERIFIED` blocks; it does not warn (§12 ¶1).

**I-4 — Independence is a property of the human, not the stage.** §2 and §12 ¶1: a self-review may find defects but MUST NOT be labelled independent or satisfy an Independent reviewer requirement. No accumulation of non-independent review satisfies §13.

**I-5 — Merge is not authorization.** §4 ¶5: repository access controls authorize incorporation into the default branch; they do not authorize a scientific transition. Acceptance and authorization are distinct events with distinct records.

---

## 2. The pipeline

```
                        ┌─────────────────────────────────────────────┐
                        │  V0  INTAKE & CLASSIFICATION                │
                        │  actor: proposer      output: change_set    │
                        └───────────────────┬─────────────────────────┘
                                            ▼
                        ┌─────────────────────────────────────────────┐
                        │  V1  AUTOMATED CONFORMANCE GATE             │
                        │  actor: automation    output: check runs    │  ── FAIL / NOT_VERIFIED ──┐
                        │  authority: none (I-2)                      │                           │
                        └───────────────────┬─────────────────────────┘                           │
                                            ▼                                                     │
      ┌──────────────────────┬──────────────┴───────────┬──────────────────────┐                 │
      ▼                      ▼                          ▼                      ▼                 │
┌───────────┐        ┌──────────────┐          ┌──────────────┐      ┌──────────────────┐         │
│ V2        │        │ V3           │          │ V4           │      │ V5               │         │
│ ARCHITECT │        │ ENGINEERING  │          │ ADVERSARIAL  │      │ VERIFICATION     │         │
│ REVIEW    │        │ REVIEW       │          │ REVIEW       │      │ REVIEW           │         │
│ jurisdic- │        │ correctness, │          │ attempts to  │      │ does the evidence│         │
│ tion,     │        │ material     │          │ refute, not  │      │ actually trace?  │         │
│ authority,│        │ state,       │          │ to improve   │      │ (§12 ¶1)         │         │
│ ontology  │        │ boundaries   │          │              │      │                  │         │
└─────┬─────┘        └──────┬───────┘          └──────┬───────┘      └────────┬─────────┘         │
      └─────────────────────┴─────────┬───────────────┴───────────────────────┘                   │
                                      ▼                                                           │
                        ┌─────────────────────────────────────────────┐                           │
                        │  V6  INDEPENDENT HUMAN ATTESTATION          │                           │
                        │  actor: identified human ≠ any author       │  ── REJECT ───────────────┤
                        │  output: attestation (§13 ¶2)               │                           │
                        │  NOT substitutable by automation (§4 ¶4)    │                           │
                        └───────────────────┬─────────────────────────┘                           │
                                            ▼                                                     │
                        ┌─────────────────────────────────────────────┐                           │
                        │  V7  AUTHORITY DECISION                     │                           │
                        │  actor: Registry-listed authority           │                           │
                        │  output: Decision (G-13) + transition rec.  │                           │
                        │  fails closed if no permitted authority     │                           │
                        └───────────────────┬─────────────────────────┘                           │
                                            ▼                                                     │
                        ┌─────────────────────────────────────────────┐                           │
                        │  V8  RATIFICATION (Atomic change accepted)  │                           │
                        │  every element in ONE revision (§2)         │                           │
                        └───────────────────┬─────────────────────────┘                           │
                                            ▼                                                     │
      ┌─────────────────────────────────────┼─────────────────────────────────────┐               │
      ▼                                     ▼                                     ▼               │
┌──────────────┐                  ┌──────────────────┐                  ┌──────────────────┐      │
│ V9  AUDIT    │                  │ V10  RELEASE     │                  │ V11  ROLLBACK    │      │
│ post-hoc, at │                  │ versioned, with  │                  │ new record;      │      │
│ a revision   │                  │ digests          │                  │ preserves prior  │      │
│ (§3 ¶5)      │                  │ (G-8)            │                  │ state (§8 ¶2)    │      │
└──────┬───────┘                  └──────────────────┘                  └──────────────────┘      │
       │                                                                                          │
       ▼                                                                                          │
┌──────────────────┐                                                                              │
│ V12 DEPRECATION  │◄─────────────────────────────────────────────────────────────────────────────┘
│ Superseded /     │                                              rejected proposals are retained,
│ Withdrawn (§9 ¶4)│                                              never deleted (§8 ¶2)
└──────────────────┘
```

V2–V5 run **concurrently**, not in sequence. They are different lenses on one change, and serialising them multiplies latency without improving coverage. They converge before V6 because an attestation must state what was examined (§13 ¶2), which requires the other reviews to be complete.

---

## 3. Stage specifications

### V0 — Intake and classification
**Actor:** proposer. **Authority:** none.
**Entry:** a proposed change exists.
**Activity:** declare the change class — `standard_activation`, `standard_amendment`, `constitutional_amendment`, `scientific_transition`, `implementation`, `validation`, `audit`, `containment`, `release`. Declare Affected requirements (§2): every requirement whose subject, condition, output, evidence, or enforcement can change because of this change.
**Exit:** class declared; Affected requirement list attached.
**Fails closed if:** class undeclared, or the Affected list is empty for a change touching normative or record paths.
**Must not:** narrow the Affected requirement definition. §2 fixes it, and understating it is the cheapest way to evade the whole pipeline — which is why `A-22` independently re-derives the class from the diff and `A-03` catches an undeclared activation.

### V1 — Automated conformance gate
**Actor:** automation. **Authority:** none (I-2).
**Entry:** V0 complete.
**Activity:** run every check in `automation/CHECK_REGISTER.yaml` whose scope includes the change. Emit per-check verdicts and findings.
**Exit:** every applicable Active check reports `PASS`; every Advisory check reports, with findings routed to V2–V5 rather than blocking.
**Fails closed if:** any Active check reports `FAIL`; any Active check reports `NOT_VERIFIED` (§12 ¶1); any check is registered but did not run; any check's target set is empty.
**Must not:** approve, or be cited as conformance beyond the criteria, revision, and Scope actually assessed (§12 ¶4).
**Note:** V1 is where the current repository's `|| true` pattern would be structurally impossible — suppression is a registration-time status (`Advisory`), never a runtime exit-code trick.

### V2 — Architect review
**Actor:** an identified human competent in the governance stack. **Authority:** none; produces findings.
**Entry:** V1 complete or Advisory-only findings outstanding.
**Activity:** the questions no check can answer:
- Does the declared jurisdiction actually match what the artifact does, or has it drifted?
- Is any authority asserted that no delegation chain supports (§4 ¶4)?
- Does the change enlarge a jurisdiction, or refine beyond what the cited clause delegates (§4 ¶4)?
- Does it introduce a synonym for an existing object type, or reuse a name for a distinct type (§11 ¶3)?
- Does it place a requirement in an informative section (§11 ¶2)?
- Does it create an irreversible state (§8 ¶2)?
**Procedures:** `MRP-14`, `MRP-15`, `MRP-16`, `MRP-19`.
**Exit:** findings recorded and dispositioned. **Must not:** edit the change (I-1).

### V3 — Engineering review
**Actor:** an identified human competent in the implementation.
**Activity:** correctness; Material state declarations (§10 ¶2); boundary and dependency conformance beyond static detection; determinism and seed recording (§10 ¶3); independent changeability of implementation and validation (§10 ¶4); whether shared code makes an assessor depend on the behaviour assessed (§10 ¶4).
**Procedures:** `MRP-19`, `MRP-20`.
**Exit:** findings recorded. **Must not:** report passing tests as scientific success (§3 ¶7).

### V4 — Adversarial review
**Actor:** any competent party, **including automated systems**. Output is a finding set, never an attestation (§4 ¶4).
**Mandate:** attempt to *refute*, not to improve. Specifically:
- construct the reading under which the artifact's requirement is unenforceable;
- find the Claim whose falsifier is stated but infeasible;
- find the Interpretation whose "strongest alternative" is a strawman;
- find the path by which authority could be asserted without a delegation;
- find the scope under which a Result's inference does not hold;
- attempt to satisfy every check while violating the requirement — the adversarial complement to §12 ¶3.
**Exit:** refutation attempts recorded with outcomes, including failed attempts. Failed refutations are evidence and are retained.
**Must not:** be counted as independent review (§4 ¶4, I-4). This is the stage where AI reviewers are most useful and where the temptation to over-credit them is highest. An LLM's adversarial finding is an *input*; the human reviewer at V6 states in the attestation which findings they examined (§13 ¶2, as amended by A-1).

### V5 — Verification review
**Actor:** an identified human, distinct from the change's authors.
**Activity:** the §12 ¶1 traceability test, executed literally. For every Affected requirement expressed as MUST or MUST NOT, confirm traceability to exactly one of: an automated check and its output; a manual inspection procedure and a version-controlled finding; a statement that the requirement is not applicable, with a **testable** reason.
**Output:** a conformance claim (G-5) identifying revision, Scope, checks performed, results, reviewer, unresolved violations, and limitations (§12 ¶1).
**Fails closed if:** any Affected requirement is untraceable, or a non-applicability statement is not testable.
**Must not:** redefine nonconformance away, or report an unavailable check as passed (§12 ¶1).

### V6 — Independent human attestation
**Actor:** an **Independent reviewer** per §2 — an identified human who is not an author of the reviewed change, did not produce the Evidence under review, and declares any material conflict of interest. A conflicted reviewer is not independent for that review.
**Entry:** V2–V5 complete; conformance claim available.
**Output:** an attestation (§13 ¶2) identifying: the reviewed revision; a declaration of non-authorship; whether the reviewer produced reviewed Evidence; conflict disclosures; the review procedure and conclusion; the reviewer's relevant competence; and the records, artifacts, or checks examined. The attestation is Repository evidence.
**Fails closed if:** no such human is available; the attestation omits any required element; the reviewer is an author; the revision moved after attestation.
**Must not:** be produced by an automated system, delegated to a role rather than a person, or satisfied by accumulating non-independent reviews.
**Current state:** **this stage cannot execute.** One identified human exists in the repository. Every activation and every amendment terminates here. No other part of this architecture can compensate, and no automation may substitute (§4 ¶4).

### V7 — Authority decision
**Actor:** a Registry-listed authority permitted for the specific transition.
**Output:** a Decision (G-13) plus a §9 ¶3 eight-element transition record.
**Fails closed if:** no authority permitted for that jurisdiction exists (§4 ¶2); the approver's assignment does not include the transition (`A-53`); the Decision embeds Evidence or Interpretation (§2, `A-52`).
**Must not:** be represented as scientific support (§3 ¶6); infer acceptance from evidence count, model confidence, test success, or elapsed time (§9 ¶3).

### V8 — Ratification
**Actor:** whoever holds merge rights, exercising §4 ¶5 incorporation authority only.
**Activity:** accept the Atomic change into the default branch — with every required artifact, Registry entry, approval, attestation, and transition record present in that one revision, and no intervening revision missing any element (§2).
**Exit:** the change is Active. For the Constitution and Registry, "Adoption or amendment becomes Active only when that complete change is accepted into the default branch" (§13 ¶3).
**Must not:** treat merge as scientific authorization (§4 ¶5, I-5).

### V9 — Repository audit
**Actor:** an auditor who is not the author of the audited content.
**Activity:** observe conformance at a stated revision and time (§3 ¶5), against Active registered requirements only.
**Output:** an immutable, revision-stamped audit report (G-6).
**Must not:** create or amend the requirement it audits (§3 ¶6); audit against an implicit or derived standard; alter the audited object. Material findings become Unknowns (S-3), not audit-internal to-do items.

### V10 — Version release
**Actor:** release authority under G-8.
**Activity:** version, build, digest, and record. Software release versioning is independent of Normative artifact versioning (G-2 vs G-8).
**Output:** a release record with source revision and artifact digests (`A-46`).
**Must not:** report build success as scientific success (§3 ¶7).

### V11 — Rollback
**Actor:** the authority permitted to reverse the original transition.
**Activity:** every scientific state change must be reversible by a later authorized Decision (§8 ¶2). Reversal preserves the previous state, rationale, supporting records, and transition history.
**Output:** a rollback record; a new Decision. Never a deletion, never a history rewrite.
**Fails closed if:** the original transition defined no reversal path — which is why G-13 requires every transition definition to name its reversal at design time.

### V12 — Deprecation
**Activity:** move a Normative artifact to Superseded (identifying its replacement) or Withdrawn (stating why no replacement applies), per §9 ¶4. Prior versions remain recoverable.
**Must not:** delete; leave Superseded content indistinguishable from Active requirements (§4 ¶5).

---

## 4. Named manual review procedures

§12 ¶4: "Requirements not mechanically decidable MUST have a named manual review procedure." Each procedure below names its requirement, its question, its method, and its recorded output. `A-39` verifies that every non-decidable MUST maps to one.

| Id | Requirement | Question | Method | Output |
|---|---|---|---|---|
| MRP-01 | §11 ¶2, G-2 | Did this version change a requirement while claiming to be a clarification? | Diff normative sentences, not lines; classify each as added, removed, strengthened, weakened, or unchanged; a PATCH with any non-unchanged classification fails | Requirement-diff finding |
| MRP-02 | §12 ¶1 | Does the conformance claim overstate what was assessed? | Sample three claimed traces; re-execute or re-inspect; verify the check's declared scope actually covers the requirement | Sampling finding |
| MRP-03 | §12 ¶2 | Was containment proportionate, and did it stay within deferral of recording? | Reconstruct the timeline; verify no other transition occurred under emergency cover | Post-incident finding |
| MRP-04 | §4 ¶4 | Do two Active requirements conflict semantically? | For each requirement pair flagged by `A-28`, and for each pair sharing a subject, construct a case satisfying one and violating the other | Conflict record or dismissal |
| MRP-05 | §3 ¶6 | Is governance approval being represented as scientific support? | Read every Decision citing scientific records; verify the Decision claims authorization only | Separation finding |
| MRP-06 | §5 ¶3 | Is the stopping rule specific enough to prevent optional stopping? | Attempt to construct two defensible stopping points consistent with the stated rule; if both are defensible the rule fails | Protocol finding |
| MRP-07 | §2 | Is this Question actually a Claim? | Test whether the text asserts a proposition assessable as supported or opposed | Object-kind finding |
| MRP-08 | §8 ¶1 | Has each of the five Unknown triggers been checked? | Walk the change for material missing information, unresolved contradiction, untested assumption, failed replication, unexplained anomaly; confirm each is either absent or represented as an Unknown | Unknown-intake finding |
| MRP-09 | §6 ¶3, §5 ¶7 | Was Evidence admitted or excluded because of the conclusion it favours? | Compare admission and exclusion rates for supporting vs opposing Observations on the same Claim; inspect every exclusion's stated ground; verify no admission rests solely on analogy, mechanism name, model confidence, performance, citation count, or authority | Admission-bias finding |
| MRP-10 | §2, §5 ¶2, §5 ¶7 | Are the operational terms sufficient, and is a mechanism claim distinguishable from prediction? | Attempt to apply each term to a borderline case using only the stated definition; for mechanism claims, identify the observation that would differ if only prediction held | Operationalization finding |
| MRP-11 | S-7 | Are two Hypotheses mutually distinguishable? | Enumerate observables under all registered protocols; if predictions coincide everywhere, force an Unknown and block independent support | Discrimination finding |
| MRP-12 | §5 ¶5, §7 ¶3 | Is the alternative genuinely the strongest, and is the scope honest? | Independently search for a stronger alternative; test the null's non-triviality; recompute the narrowest material limitation of the inputs and compare to the stated scope | Interpretation finding |
| MRP-13 | §2, §5 ¶6 | Is the Principle's scope identifiable and its falsifier feasible? | Test membership of three borderline cases against the stated population, environment, conditions, versions, and time interval; cost the falsifying experiment | Scope finding |
| MRP-14 | §4 ¶1, §11 ¶1 | Is the Scope identifiable and the responsibility single? | Apply §2's identifiability test; list the artifact's requirements and check they serve one responsibility | Declaration finding |
| MRP-15 | §4 ¶2 | Do two standards govern the same real activity under different type names? | Map each owned type to the concrete activity it governs; look for activity collisions across differently-named types | Semantic-overlap finding |
| MRP-16 | §1 ¶2 | Does any artifact assert precedence without saying "canonical"? | Read for precedence-shaped prose: "takes precedence", "wins", "binds all", "supersedes in authority", "derive from this" | Self-authority finding |
| MRP-17 | §7 ¶4 | Were any Results not recorded? | Reconcile execution evidence from logs, custody manifests, and compute records against recorded Results; interview the executor | Retention finding |
| MRP-18 | §3 ¶7 | Is test success being reported as scientific success by paraphrase? | Read scientific records for engineering-derived assertions lacking a protocol that makes them relevant Evidence | Success-conflation finding |
| MRP-19 | §10 | Are the declared boundaries real? | Trace three cross-boundary interactions end to end, including runtime coupling, shared stores, and environment dependencies | Boundary finding |
| MRP-20 | §10 ¶2-3 | Is Material state fully declared and is execution reproducible? | Re-execute from the declared inputs on a clean environment; compare outputs; identify any undeclared dependency | Reproducibility finding |

---

## 5. Fail-closed matrix

| Condition | Blocking stage | Behaviour |
|---|---|---|
| Required field absent from an artifact | V1 | Artifact has no authority (§4 ¶1); change blocked |
| Active check reports `FAIL` | V1 | Blocked |
| Active check reports `NOT_VERIFIED` | V1 | Blocked (§12 ¶1) — never downgraded to a warning |
| Registered check did not run | V1 | Blocked (`A-29`) |
| Jurisdiction overlap detected | V1 / V2 | Registry must reject (§4 ¶2) |
| No authority permitted for the transition | V7 | Activation fails closed (§4 ¶2) |
| No Independent reviewer available | V6 | Blocked; **no substitute exists** |
| Attestation incomplete | V6 | Blocked (§13 ¶2) |
| Transition record missing any of eight elements | V7 | Transition fails closed (§9 ¶3) |
| Atomic change split across revisions | V8 | Blocked (§2) |
| Open conflict record on an Affected requirement | V1 | Both requirements nonconforming; dependent transition blocked (§4 ¶4, §12 ¶2) |
| Non-applicability reason not testable | V5 | Blocked (§12 ¶1) |
| Reviewer is an author | V6 | Review is not independent (§2, §12 ¶1) |
| Transition has no defined reversal | V7 | Blocked (§8 ¶2) |

The pattern is uniform: **every unknown resolves to "blocked," never to "proceed with a note."** That is §9 ¶3 applied consistently, and it is the property that makes the pipeline safe to operate with few reviewers — it degrades to a halt rather than to silent acceptance.

---

## 6. Cost and the throughput problem

This pipeline is expensive by design, and pretending otherwise would be the design's worst failure. Honest accounting:

- V1 is cheap and fully automatable.
- V2–V5 require competent human attention; for a routine implementation change most reduce to short passes, but for a standard activation each is substantial.
- V6 requires an independent human and is **the binding constraint**. Twenty-four standard activations mean twenty-four attestations, and §13 permits no batching of attestations even where §4 permits batching of activations.
- V9 audit is periodic, not per-change.

Two mitigations are legitimate under the Constitution:

**Tiered application by change class.** §12 ¶1 scopes conformance to *Affected requirements*. A change touching only `software/` has a small Affected set and correspondingly small V2–V5 obligations. The pipeline is proportional by construction, provided the Affected set is honestly declared — which is why V0's declaration is independently re-derived by `A-22`.

**Batched activation with per-standard attestation.** §4 ¶2 requires each activation to be atomic, not solitary. Six mutually-dependent standards may activate in one change with six attestations. This reduces coordination overhead without reducing review.

What is **not** legitimate: reducing the reviewer count, treating AI review as independent, deferring attestation to a later revision, or lowering the standard for what counts as a review. Each of those trades the guarantee for the appearance of one. If the pipeline proves too expensive for the project's actual capacity, the correct response is to reduce the number of Active standards — governing less, but governing it properly — not to weaken verification. That trade-off is a human decision, recorded as H-11.
