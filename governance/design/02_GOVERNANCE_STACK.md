# Governance Stack — O-1 and G-1 … G-13

- **Status:** Draft
- **Scope:** Design of the ontological and governance Domain standards for Project P1
- **Responsibility:** Specify purpose, authority, inputs, outputs, constraints, lifecycle, verification, and failure modes for each proposed governance Domain standard
- **Authority source:** None. This record has no normative authority and activates nothing.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 0. Common frame

Every artifact below is a **Domain standard** in the sense of Constitution §2, sits at **authority Level 2** (§4), and would be activated by the procedure in §4 ¶2: one Atomic change containing the reviewed standard, its Registry entry, approval by a Registry-listed authority permitted to activate that jurisdiction, and an Independent reviewer attestation satisfying §13. **No standard may authorize its own activation** (§4 ¶2).

Every standard must state, in its own header, its status, Scope, responsibility, and authority source, and the Registry must carry the same values without contradiction; otherwise "the artifact has no authority" (§4 ¶1).

Every standard must define the nine lifecycle elements of §9 ¶1 for each object type it owns: permitted states, initial state, entry and exit criteria, permitted transitions, transition authority, required transition evidence, reversal and correction procedure, retention rules.

Two invariants from `00_ECOSYSTEM_OVERVIEW.md` apply throughout:
- **Peer Reference Rule** — reference a peer's owned definitions by identifier; never restate them.
- **Jurisdiction Rule** — a transition belongs to the standard owning the object type whose state changes.

Where a field below says *"(reserved)"*, the matter is fixed by the Constitution under §4.2 of the overview and the standard MUST NOT refine it.

---

## O-1 — Ontology Standard

**Purpose.** Register the governed object types, their identifiers, and the permitted relationships among them, so that every other standard refers to one shared type system. Without it, twenty-four standards will each grow a private vocabulary and §11's terminology-reuse rule becomes unenforceable.

**Authority.** §5 ¶6 ("No scientific constant, threshold, model, **ontology**… is constitutional. Such objects MUST be governed by a revisable domain standard"); §11 ¶3 (terminology reuse; synonyms must not create distinct types; identical names must not conceal distinct types); §9 ¶1 (per-type lifecycles presuppose an enumerated type set).

**Jurisdiction (owned).** Object types: `object_type_registration`, `identifier_allocation`, `relationship_kind`. Transitions: register type, deprecate type, allocate identifier namespace, register relationship kind, retire relationship kind. Scope: all version-controlled governed records in P1.

**Explicitly not owned.** Any type's states, entry/exit criteria, or transitions — those belong to that type's standard. O-1 says *what exists and how it connects*; it never says *how it moves*. This is the single most important boundary in the stack.

**Inputs.** Constitution §2 kind definitions (reused unchanged, never redefined); proposals from type-owning standards; the existing `p1/tooling/p1_os/enums.py` type set, as material for reconciliation.

**Outputs.** `ontology/TYPE_REGISTER.yaml`, `ontology/RELATIONSHIPS.yaml`, `ontology/IDENTIFIERS.yaml`, `ontology/schemas/*`.

**Constraints.**
- MUST reuse Constitution §2 terms unchanged within their Scope (§11 ¶3). A domain-specific redefinition MUST use a different term.
- MUST NOT register a type whose lifecycle no Active standard owns — that would violate §9 ¶1's "exactly one."
- MUST NOT treat Observation, Evidence, Interpretation, Decision, and Principle as interchangeable (§2 final ¶).
- Identifiers MUST be stable and never reused after retirement; reuse would silently re-point historical references and breach §8's preservation rule.

**Lifecycle.** Draft → Active → Superseded/Withdrawn. Type addition: minor version. Type removal or identifier-grammar change: major version plus a migration record naming every affected record.

**Verification.** `A-09` identifier uniqueness and grammar · `A-10` record-frontmatter conformance to the registered type · `A-11` relationship referential integrity · `A-27` terminology drift against §2 · `A-04` every registered type has exactly one owning standard.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Type registered with no owner | §9 violation invisible until a transition is attempted, then fails closed mid-work | `A-04` blocks activation of a type without an owner |
| Silent redefinition of a §2 term | Every downstream standard inherits the drift; historical records change meaning | `A-27`; §13 ¶4 forbids retroactive meaning change |
| Identifier reuse after retirement | Historical citations resolve to the wrong object; undetectable by link-checking | Grammar reserves retired identifiers permanently |
| Ontology reconciliation deferred | The 12-type Research OS and the 11-kind Constitution diverge in code and prose | Roadmap M-3 gates O-1 activation on reconciliation |

---

## G-1 — Registry Specification

**Purpose.** Define the form, schema, and integrity constraints of `GOVERNANCE_REGISTRY.yaml`, including the machine-readable jurisdiction representation that makes §4's overlap rejection decidable.

**Authority.** §2 (Registry definition and sole responsibility); §4 ¶1-2 (Registry must carry identity, status, Scope, responsibility, authority, jurisdiction without contradiction; must reject overlapping jurisdictions); §12 ¶3.

**Jurisdiction (owned).** Object types: `registry_schema`, `jurisdiction_declaration`, `registry_transition_record`. Transitions: publish schema version, register jurisdiction declaration, record registry transition.

**Explicitly not owned.** *Which* artifacts are Active and *who* holds authority — that is the Registry's own content, and assigning it is G-3's and the steward's business. G-1 governs the container's form, never its contents' truth.

**Inputs.** Constitution §2 and §4; O-1 identifiers; activation dossiers from each standard.

**Outputs.** `registry/schema/governance_registry.schema.json`; the jurisdiction tuple format; `registry/transitions/*`.

**Constraints.**
- MUST NOT extend the Registry's responsibility beyond §2's three items. A Registry that also carries rationale, roadmap, or narrative violates §2 and §11.
- MUST require jurisdiction as a structured tuple *(owned object types, owned transitions, scope)*. Prose jurisdictions are not mechanically comparable and make §4 ¶2 unenforceable — this is the design decision that makes the whole stack checkable.
- MUST fail closed: any required field absent ⇒ the artifact has no authority (§4 ¶1), and the check MUST report "no authority," not "warning."
- MUST NOT define precedence between the Registry and a Domain standard — that gap is defect D-2 and is a matter for §13, not for G-1. A subordinate standard resolving its own precedence would enlarge jurisdiction, prohibited by §4 ¶4.

**Lifecycle.** Draft → Active → Superseded/Withdrawn. Schema versions are additive within a major version; a field becoming required is a major version and requires migrating every existing entry in one Atomic change.

**Verification.** `A-01` schema validation · `A-03` Registry↔artifact field consistency · `A-04` jurisdiction overlap · `A-05` authority-exists-for-declared-transition · `A-22` atomic-change completeness.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Prose jurisdictions accepted | Overlap becomes a matter of opinion; §4 ¶2 silently unenforced | Schema rejects non-tuple jurisdictions |
| Registry/artifact drift | An artifact appears Active while its own header disagrees; §4 ¶1 says it has no authority, but nothing detects it | `A-03` on every change |
| Registry corruption or loss | Every Active artifact's authority becomes unverifiable simultaneously | Append-only transitions in `registry/transitions/` permit reconstruction; risk R-10 |
| Schema permits an entry with no authority assignment | Activation appears to succeed but §4 ¶2 requires fail-closed | `A-05` blocks |

---

## G-2 — Normative Artifact Standard

**Purpose.** Govern the object type *Normative artifact*: how a standard is drafted, versioned, activated, amended, superseded, and withdrawn; and what a Domain standard must contain to be reviewable at all. Subsumes the brief's Governance Standard, Version Policy (normative artifacts), Change Policy (normative artifacts), Release Policy (normative artifacts), and Phase 4's domain framework.

**Authority.** §9 ¶4 (minimum Normative artifact lifecycle — see caveat); §4 ¶1-2 (required fields, activation procedure); §11 ¶1-2 (one primary responsibility; informative sections).

**Caveat — depends on an under-specified delegation.** §9 ¶4's "minimum lifecycle" implies extension is permitted but does not identify recipient, permitted transitions, or limits as §4 ¶4 requires. G-2's legitimacy therefore rests on defect **D-1**. Until D-1 is resolved by human judgment, G-2 should be drafted but **not activated**, or activated only in a form that adds procedure without adding states.

**Jurisdiction (owned).** Object types: `normative_artifact`, `domain_standard`, `standard_version`, `activation_dossier`, `legacy_disposition`. Transitions: draft, submit for activation, activate, amend, supersede, withdraw, classify as Legacy, re-activate from Legacy.

**Self-reference.** G-2 owns the type `domain_standard`, and G-2 is one. This is permitted: §9's "exactly one Active Domain standard per object type" is satisfied, and §4 ¶2's prohibition on self-activation is honoured by requiring the constitutional steward to activate G-2 directly under §13. G-2 MUST state that it does not authorize its own activation.

**Inputs.** Constitution §4, §9, §11, §13, §14; drafts; review records from G-4; Registry entries from G-1.

**Outputs.** The Domain Standard Interface (see `04_DOMAIN_STANDARD_INTERFACE.md`); the activation dossier template; the versioning scheme; the Legacy disposition procedure discharging §14.

**Constraints.**
- MUST NOT permit an artifact to acquire authority other than through §4 ¶2's Atomic change.
- MUST NOT permit a standard to authorize its own activation (§4 ¶2), nor to require another Domain standard for its own object type (§9 ¶2).
- MUST preserve prior versions as recoverable (§9 ¶4).
- MUST keep Draft, Superseded, Withdrawn, Legacy, and generated content distinguishable from Active requirements (§4 ¶5).
- MUST NOT allow informative text to introduce requirements (§11 ¶2).
- Amendments MUST NOT retroactively alter the meaning or reported outcome of a prior scientific record (§13 ¶4) — so a version bump must state its effect on records created under the prior version.

**Lifecycle.** Draft → Active → Superseded/Withdrawn (§9 ¶4). Versioning: MAJOR for a changed or removed requirement, or a jurisdiction change; MINOR for an added requirement that no existing record violates; PATCH for non-normative clarification only, which MUST be verifiable as non-normative.

**Verification.** `A-02` header completeness · `A-06` RFC-2119 usage in Draft/Legacy/informative text · `A-07` prohibited self-authority lexemes · `A-30` Legacy/Draft authority-claim detection · `A-22` atomic-change completeness · manual: `MRP-01` requirement-diff review.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| D-1 unresolved but G-2 activated anyway | The whole stack's lifecycle machinery rests on a delegation the Constitution does not grant; an adversarial reviewer can void every activation | Gate G-2 activation on H-03 |
| PATCH used to smuggle a requirement | Requirements change without review | `MRP-01` diffs normative sentences, not lines |
| Legacy corpus never dispositioned | §14 makes ~13 artifacts Legacy at adoption while live work still cites them | Roadmap phase M-6; risk R-02 |
| Batch activation misread as one approval | Several standards activate on one reviewer's attestation without per-standard review | Dossier requires per-standard attestation even in a batched Atomic change |

---

## G-3 — Authority & Delegation Standard

**Purpose.** Govern authority assignment records, delegation records, steward appointment, succession, and revocation. Subsumes the brief's Authority Policy, Delegation Policy, and Steward Policy.

**Authority.** §4 ¶1 (every authority source must identify jurisdiction and permitted transitions); §4 ¶4 (delegation must identify five elements); §13 ¶3 (steward assignment at adoption).

**Jurisdiction (owned).** Object types: `authority_assignment`, `delegation_record`, `role_definition`, `conflict_of_interest_declaration`. Transitions: assign, delegate, sub-delegate, revoke, expire, transfer on succession, declare conflict.

**The central constraint.** G-3 **records and lifecycles** authority; it never **creates** it. §4 ¶4: "A refinement MUST NOT create authority over a transition, object type, or jurisdiction not expressly delegated." All authority in P1 originates at §13's constitutional steward assignment and flows downward through recorded delegations. A G-3 that could mint authority would invert the Constitution.

**Inputs.** The adoption dossier's steward assignment; delegation proposals; conflict declarations; Registry entries.

**Outputs.** `governance/authority/*` (assignments, steward roster with succession), `governance/delegations/*`.

**Constraints.**
- Every delegation record MUST state subject, Scope, recipient, permitted transitions, and limits (§4 ¶4). A record missing any element is void, not merely defective.
- Sub-delegation MUST NOT exceed the parent delegation's transitions or Scope.
- MUST NOT assign authority to an automated system (§4 ¶4: automation "MUST NOT supply human authority or independent review").
- MUST require succession for every role: a role with one holder and no successor is a single point of governance failure over a twenty-year horizon (risk R-17).
- Revocation MUST preserve the record and every transition authorized while it was Active (§8 ¶2).
- An expired or revoked authority MUST NOT retroactively invalidate transitions it validly authorized; §13 ¶4's non-retroactivity principle applies by analogy and should be stated explicitly.

**Lifecycle.** Proposed → Active → Revoked / Expired / Succeeded. Never deleted. Time-bounded assignments SHOULD be preferred over indefinite ones, with renewal as a reviewed transition.

**Verification.** `A-05` every declared transition has a living authority · `A-23` reviewer ≠ author · `A-24` self-review detection · `A-36` delegation five-element completeness · `A-37` sub-delegation containment.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Sole steward becomes unavailable | No activation, amendment, or reversal is possible; the repository freezes permanently | Mandatory successor; escalated as H-08 |
| Delegation drafted in prose without the five elements | Void under §4 but treated as valid in practice; every dependent transition is nonconforming | `A-36` blocks |
| Role name used as authority ("the Research Director approved") | Authority asserted without a Registry-backed assignment — the current repository's dominant pattern | `A-05` requires resolution to a Registry entry |
| Conflict of interest undeclared | The reviewer is not independent, so §13 attestations are void (§2) | `A-23`/`A-24` plus mandatory declaration in the attestation |

---

## G-4 — Review & Attestation Standard

**Purpose.** Govern review records and Independent reviewer attestations: how review is requested, conducted, evidenced, and attested, including the named manual review procedures §12 ¶4 requires.

**Authority.** §12 ¶1 (traceability to an automated check, a manual inspection procedure, or a testable non-applicability statement); §12 ¶4 (named manual review procedure); §13 ¶2 (attestation content); §2 (Independent reviewer definition).

**Jurisdiction (owned).** Object types: `review_request`, `review_record`, `attestation`, `manual_review_procedure`. Transitions: request, assign reviewer, conduct, attest, reject, withdraw attestation.

**Inputs.** Change sets from G-8; authority and conflict records from G-3; check outputs from G-11; the artifact under review.

**Outputs.** `governance/reviews/*`; `constitution/attestations/*`; the register of named manual review procedures `MRP-xx`.

**Constraints.**
- An attestation MUST identify the reviewed revision, declare non-authorship, state whether the reviewer produced reviewed Evidence, disclose conflicts, state the review procedure and conclusion, state the reviewer's relevant competence, and identify the records, artifacts, or checks examined (§13 ¶2, as amended by A-1 in the v1.2.0 record).
- A self-review MAY find defects but MUST NOT be labelled independent or satisfy an Independent reviewer requirement (§12 ¶1).
- An automated reviewer MUST NOT produce an attestation (§4 ¶4). AI review output is an input to a human reviewer, recorded as such, and carries no attestation force.
- Every non-mechanically-decidable MUST in every Active standard MUST map to a named `MRP-xx` (§12 ¶4). An unmapped requirement is unverifiable and the standard is not review-complete.
- A check that did not run MUST be reported as not verified, never as passed (§12 ¶1).

**Lifecycle.** Requested → In review → Attested / Rejected / Withdrawn. Attestations are immutable once signed; defects are corrected by a superseding attestation that identifies the defect.

**Verification.** `A-23` non-authorship · `A-24` self-review · `A-38` attestation field completeness · `A-39` every MUST maps to a check or an `MRP-xx` or a recorded non-applicability · `A-29` unavailable-check reporting.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| **No second human exists** | No attestation can be produced; every activation path is closed; the entire stack is inert | The blocking item H-01. No engineering mitigation exists. |
| Reviewer pool too small for genuine independence | Attestations become formalities; §2's guarantee hollows out | External reviewers; recorded as risk R-14 and limitation L-4 in the v1.2.0 record |
| AI review treated as independent review | §4 ¶4 violated at the root; every downstream activation void | `A-38` requires an identified human; attestations record competence |
| Attestation cites a revision that later changes | Review no longer covers the accepted content | Revision pinning; re-attestation required if the change set moves |

---

## G-5 — Conformance Standard

**Purpose.** Govern the conformance claim: the record asserting that a stated revision conforms to stated requirements within a stated Scope.

**Authority.** §12 ¶1 (a conformance claim must identify revision, Scope, checks performed, results, reviewer, unresolved violations, limitations); §12 ¶2-3.

**Jurisdiction (owned).** Object types: `conformance_claim`, `nonconformance_record`, `non_applicability_statement`. Transitions: assert, verify, publish, revoke, close nonconformance.

**Explicitly not owned.** The checks themselves (G-11), the review that supports the claim (G-4), and audit reports about conformance (G-6). G-5 owns the *assertion*.

**Inputs.** Check outputs (G-11); review records (G-4); the requirement inventory extracted from Active standards.

**Outputs.** Conformance claims per change set and per release; the nonconformance register.

**Constraints.**
- Every Affected requirement expressed as MUST or MUST NOT MUST trace to a check output, a manual inspection finding, or a testable non-applicability statement (§12 ¶1). "Affected requirement" is defined in §2 and MUST NOT be narrowed.
- A claim MUST list unresolved violations and limitations. A claim that omits known violations is itself a nonconformance.
- Tools and audits MUST report nonconformance and MUST NOT redefine it away (§12 ¶1).
- Nonconforming content MAY be retained for diagnosis or migration but MUST be labelled and MUST NOT authorize a dependent transition (§12 ¶2).
- A check is evidence only for the criteria, revision, and Scope it actually assessed (§12 ¶4) — claims MUST NOT generalize a check beyond its declared scope.

**Lifecycle.** Asserted → Verified → Published → Revoked. Revocation on discovering the claim was false; the claim is retained with its refutation (§8 ¶2).

**Verification.** `A-39` requirement-to-evidence coverage · `A-29` unavailable-check reporting · `A-40` non-applicability statements are testable · manual `MRP-02` conformance claim review.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Green CI read as conformance | The most likely institutional failure: passing tests reported as compliance, contrary to §3 ¶3 and §12 ¶4 | Claims must enumerate criteria actually assessed; `A-29` |
| Non-applicability used as an escape hatch | Requirements silently disabled | `A-40` requires a *testable* reason |
| Coverage decays as standards grow | New MUSTs land with no mapped check or `MRP` | `A-39` fails the change set that adds an unmapped MUST |

---

## G-6 — Audit Standard

**Purpose.** Govern audit reports: observations about conformance at one identified revision and time.

**Authority.** §3 ¶5 ("Audit records report observed conformance at a stated revision and time"); §3 ¶6 ("an audit MUST NOT create or amend the requirement it audits"); §11 (audit report = one revision's observations).

**Jurisdiction (owned).** Object types: `audit_report`, `audit_finding`, `audit_response`. Transitions: commission, conduct, publish, respond, close finding.

**Inputs.** The repository at a pinned revision; Active standards; conformance claims (G-5); check outputs (G-11).

**Outputs.** `audit/*` reports, each revision-stamped and immutable.

**Constraints.**
- MUST NOT create, amend, or imply a requirement (§3 ¶6). The existing `audits/CONSTITUTION_COMPLIANCE.md` violates this by inventing "Constitutional Rule: No submission until Gates 1–5 pass" and then auditing against it; that pattern is prohibited.
- MUST NOT audit against an unregistered or "implicit" standard. The requirement basis MUST be an Active artifact identified by Registry entry and version.
- MUST identify the revision and time with §2's timezone-qualified precision.
- MUST NOT alter the audited object (§3 ¶6, by analogy with the validation rule).
- Findings are observations; closing a finding requires a Decision (G-13) or a conformance change, not an audit edit.

**Lifecycle.** Commissioned → Conducted → Published (immutable) → Responded. Superseded by a later audit; never edited.

**Verification.** `A-41` audit basis resolves to an Active registered artifact · `A-42` audit reports contain no RFC-2119 requirement-creating sentences · `A-14` immutability.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Audit invents its own standard | Governance forks; the audited party cannot conform to an unpublished rule | `A-41` |
| Audit edited after publication to soften findings | Record of nonconformance destroyed, breaching §8 ¶2 | Immutability + append-only |
| Audit findings never responded to | Nonconformance accumulates silently | Findings tracked as Unknowns under S-3 when material |

---

## G-7 — Records Custody & Retention Standard

**Purpose.** Govern the custody of Repository evidence that cannot live in Git: external artifact manifests, digest algorithms, retention schedules, and recovery procedures. This is the governance half of the brief's Evidence Policy; the scientific half is S-5.

**Authority.** §2 (Repository evidence includes "a content-addressed external artifact whose identity, provenance, and recovery procedure are version-controlled"); §6 ¶2 (collision-resistant digest algorithm and version MUST be specified); §6 ¶4-5 (inputs that cannot be retained must have absence, reason, expected effect, and recovery status recorded); §10 ¶5 (excluded material needed for reproduction MUST have a version-controlled manifest).

**Jurisdiction (owned).** Object types: `custody_manifest`, `digest_algorithm_registration`, `retention_schedule`, `recovery_procedure`. Transitions: register artifact, register digest algorithm, deprecate digest algorithm, schedule retention, record loss, record recovery.

**Inputs.** External artifacts; digest computations; storage-system facts.

**Outputs.** `custody/*` manifests; the digest algorithm register.

**Constraints.**
- The registered digest algorithm MUST be collision-resistant and versioned (§6 ¶2).
- Deprecating a digest algorithm MUST NOT invalidate historical manifests; re-digesting under a new algorithm MUST be recorded as a new manifest linked to the prior one, never as an edit. Over twenty years this will happen at least once (risk R-09).
- Loss of a retained artifact MUST be recorded as an Unknown or limitation under §6 ¶5 — never silently dropped.
- Credentials and private keys MUST NOT be committed (§10 ¶5); custody manifests MUST NOT embed secrets.
- Retention for Results, Negative Results, and Unknowns is permanent (§7 ¶4, §8 ¶1); G-7 MUST NOT schedule their expiry.

**Lifecycle.** Manifest: Registered → Verified → Degraded → Lost/Recovered. All states retained.

**Verification.** `A-31` external references have manifests · `A-25` secret scanning · `A-43` digest algorithm is registered and non-deprecated · `A-44` periodic digest re-verification.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Digest algorithm becomes broken | Historical identity claims weaken; §6 ¶2 no longer satisfied for old manifests | Versioned algorithm register; linked re-digest procedure |
| Silent bit rot in external storage | Evidence unverifiable when needed, years later | `A-44` scheduled re-verification; Degraded state |
| Storage cost pressure vs permanent retention | Institutional temptation to delete Negative Results — prohibited by §7 ¶4 | Retention schedule cannot expire permanent classes; risk R-16 |

---

## G-8 — Change & Release Standard

**Purpose.** Govern change sets and software releases: how a proposed default-branch revision is composed, reviewed, accepted, released, and rolled back. Owns the §4 "Atomic change" composition rules.

**Authority.** §2 (Atomic change definition); §4 ¶5 (repository access controls authorize incorporation, not scientific transitions); §12; §10.

**Jurisdiction (owned).** Object types: `change_set`, `release`, `rollback_record`, `deprecation_record`. Transitions: propose, review, accept, reject, release, roll back, deprecate.

**Inputs.** Proposed revisions; review records (G-4); conformance claims (G-5); check outputs (G-11).

**Outputs.** Accepted revisions; release records; rollback records.

**Constraints.**
- An Atomic change MUST contain every required artifact, Registry entry, approval, attestation, and transition record, with no intervening default-branch revision in which any required element is absent (§2). This forbids the common "merge the standard now, register it next" pattern.
- Merge permission MUST NOT be represented as scientific authorization (§4 ¶5). A merged Result is not an accepted Result.
- Rollback MUST preserve the previous state, rationale, supporting records, and transition history (§8 ¶2).
- Force-push, history rewriting, and branch deletion affecting `results/`, `evidence/`, `observations/`, `decisions/`, `unknowns/`, `constitution/attestations/`, or `registry/transitions/` MUST be prohibited at the platform level, not merely by policy (§7 ¶1, §8 ¶2).
- Release versioning of software is independent of Normative artifact versioning (G-2); the two MUST NOT share a version number, because their change semantics differ.

**Lifecycle.** Proposed → Under review → Accepted / Rejected → Released → Deprecated. Rollback creates a new record; it never erases.

**Verification.** `A-22` atomic-change completeness · `A-15` scientific-record deletion detection · `A-45` protected-path history integrity · `A-46` release artifact digests.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Split activation across two commits | §2's atomicity breached; there exists a revision where an artifact is Active with no Registry entry | `A-22` on the merge |
| History rewrite on a protected path | Prior Results concealed, breaching §7 ¶1 — undetectable after the fact without an external anchor | Platform-level protection + `A-45` + external timestamp anchor |
| Rollback implemented as revert-and-forget | Prior state and rationale lost, breaching §8 ¶2 | Rollback record required |

---

## G-9 — Emergency & Containment Standard

**Purpose.** Govern records of security containment actions taken before the normal record-creation sequence.

**Authority.** §12 ¶2, in full: "Security containment MAY precede record creation when delay would materially increase harm; the action and rationale MUST be recorded immediately afterward and remains subject to review."

**Jurisdiction (owned).** Object type: `containment_action_record`. Transitions: record action, review action, ratify or reverse.

**The narrowness is the point.** §12 ¶2 is the *only* constitutional emergency provision, and it authorizes exactly one thing: deferring a record. It does not authorize deferring review, bypassing §13, altering a scientific record, activating a standard, or granting temporary authority. G-9 MUST state this explicitly, because "emergency policy" is the classic vector by which governance systems acquire an unbounded override.

**Inputs.** The containment event; the acting party's identity; the harm assessment.

**Outputs.** `governance/containment/*`.

**Constraints.**
- MUST NOT authorize any transition other than deferral of the containment record itself.
- MUST NOT permit a scientific transition, a standard activation, an amendment, or an authority assignment under emergency conditions.
- The record MUST follow "immediately afterward" and MUST state the harm rationale; a delayed record is itself a nonconformance to be reported, not excused.
- Every containment action remains subject to review (§12 ¶2) — G-9 MUST NOT create a ratification path that terminates review.

**Lifecycle.** Action taken → Recorded → Reviewed → Ratified / Reversed. Always retained.

**Verification.** `A-47` containment record exists within the declared window · `A-48` no containment record authorizes a non-containment transition · manual `MRP-03` post-incident review.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Emergency scope creep | Becomes a general override of §13 and §4 — the most dangerous failure in the stack | `A-48`; jurisdiction owns exactly one object type |
| Containment used to delete records | §8 ¶2 breached under cover of urgency | Deletion is never containment; `A-15` |
| Record never filed | The exception swallows the rule | `A-47` |

---

## G-10 — Conflict Resolution Standard

**Purpose.** Govern the conflict record: the tracked object representing a same-level requirement conflict during the interval §4 leaves open.

**Authority.** §4 ¶4: "Conflicting requirements at the same level are both nonconforming until the authority for their common parent jurisdiction resolves the conflict; recency alone MUST NOT decide precedence."

**Jurisdiction (owned).** Object type: `conflict_record`. Transitions: open, escalate to common parent authority, resolve, withdraw.

**Explicitly not owned.** The resolution *rule* — §4 fixes it, and G-10 restating it would create a same-level duplicate of a Level-1 requirement, which §4 ¶4 itself prohibits enlarging. G-10 owns tracking and escalation only.

**Inputs.** Detected conflicts (from `A-28`, review, or audit); the Registry's jurisdiction map, used to compute the common parent authority.

**Outputs.** `governance/conflicts/*`.

**Constraints.**
- MUST mark both conflicting requirements nonconforming for the conflict's duration, and MUST NOT allow either to authorize a dependent transition meanwhile (§12 ¶2).
- MUST NOT resolve by recency, by seniority, or by tool output (§4 ¶4).
- MUST identify the common parent jurisdiction from the Registry; where no common parent exists below the Constitution, the conflict escalates to the constitutional steward.
- Resolution MUST be effected by amending one or both artifacts, not by annotating the conflict record.

**Lifecycle.** Open → Escalated → Resolved / Withdrawn. Retained permanently as governance history.

**Verification.** `A-28` contradiction detection (partial; see limitations) · `A-49` open conflicts block dependent transitions.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Conflicts detected only by humans, rarely | Contradictory requirements coexist for years — the repository's current condition (N-7, N-9) | `A-28` catches lexical and jurisdictional cases; `MRP-04` for semantic ones |
| No common parent identifiable | Escalation stalls | Default escalation to constitutional steward |
| Conflict record used as a resolution | Nonconformance persists while appearing handled | Resolution requires an amendment, verified by `A-49` |

---

## G-11 — Automation & Tooling Standard

**Purpose.** Govern registered checks: their declared scope, algorithm, limitations, false-positive and false-negative characteristics, and operational status.

**Authority.** §12 ¶3 ("CI, tests, schemas, and linters SHOULD enforce every mechanically decidable requirement"); §12 ¶4 ("A check is evidence of conformance only for the criteria, revision, and Scope it actually assessed"); §4 ¶4 (automation may propose, check, or apply an already-authorized transition, but MUST NOT supply human authority or independent review).

**Jurisdiction (owned).** Object types: `check_registration`, `check_run_record`. Transitions: propose, activate, mark advisory, mark broken, retire.

**Inputs.** Requirements extracted from Active standards; the repository; O-1 schemas.

**Outputs.** `automation/CHECK_REGISTER.yaml`; check implementations; run records.

**Constraints.**
- Every registered check MUST declare inputs, outputs, algorithm, limitations, known false positives, and known false negatives (this is also the brief's Phase 5 requirement, discharged in `05_AUTOMATION_ARCHITECTURE.md`).
- A check MUST NOT approve, authorize, or attest. Its output is a finding (§4 ¶4).
- An unavailable, erroring, or skipped check MUST be reported as **not verified**, never as passed (§12 ¶1). Constructions such as `|| true` are therefore prohibited in any check claiming conformance relevance — the current `ci.yml` violates this (N-6).
- A check's evidentiary reach MUST NOT be generalized beyond its declared criteria, revision, and Scope (§12 ¶4).
- Checks that mutate the repository MUST be separated from checks that assess it (§3 ¶6: validation must not alter the object it assesses).

**Lifecycle.** Proposed → Active → Advisory → Broken → Retired. A Broken check is loudly Broken; silence is prohibited.

**Verification.** `A-29` unavailable-check reporting · `A-50` check register completeness · `A-51` no check emits an approval · self-test fixtures per check (checks are themselves validated).

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Check silently stops matching (renamed paths) | Zero findings misread as conformance — present today: `ci.yml` lints `core/`, `validation/`, which no longer exist | Checks assert their target set is non-empty |
| False negatives undisclosed | Conformance claims overstate coverage | Mandatory FP/FN disclosure at registration |
| Automation drifts into authority | "CI approved the merge" | `A-51`; G-5 claims cite checks as evidence, never as approval |

---

## G-12 — Architecture Standard

**Purpose.** Govern architecture records: repository layout, module boundaries, dependency rules, and Material state declarations.

**Authority.** §10 ¶1 (architecture and layout MUST be defined in versioned architecture records with explicit boundaries, dependencies, and rationale); §10 ¶2 (Material state declarations); §10 ¶4 (independent changeability of implementation and validation); §10 ¶5 (fixtures).

**Caveat.** §10 ¶1 names the recipient artifact kind but not permitted transitions or limits, so G-12 partially depends on defect **D-1**. It is the least affected of the four, because §10 states the required content directly.

**Jurisdiction (owned).** Object types: `architecture_record`, `boundary_declaration`, `material_state_declaration`, `architecture_decision`. Transitions: draft, activate, supersede, withdraw.

**Inputs.** Engineering proposals; `01_REPOSITORY_ARCHITECTURE_RECORD.md` as the initial draft.

**Outputs.** The Active architecture record; per-directory `_BOUNDARY.yaml`; Material state declarations per stateful component.

**Constraints.**
- Every stateful component MUST declare ownership, representation, initialization, permitted transitions, persistence, reset, recovery, and concurrency behaviour for its Material state (§10 ¶2).
- Material state MUST NOT depend on an undocumented global, cache, service, environment value, mutable default, clock, random source, or local file (§10 ¶2).
- A directory name MUST NOT be treated as proof of separation (§10 ¶1) — hence machine-readable boundary declarations.
- Changing implementation MUST NOT silently change acceptance criteria (§10 ¶4).
- Generated, cached, secret, personal, and runtime-only material MUST be separated from canonical records and excluded from version control unless G-12 explicitly requires a safe reproducible fixture (§10 ¶5).
- MUST NOT relocate `GOVERNANCE_REGISTRY.yaml` (pinned by §2) or purport to authorize doing so.

**Lifecycle.** Draft → Active → Superseded/Withdrawn, versioned. Layout changes are ordinary revisions, not constitutional events.

**Verification.** `A-34` boundary and dependency conformance · `A-32` Material state declaration presence · `A-26` generated/cached material in VCS · `A-25` secrets · `A-35` assessor/assessed shared-code independence.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Layout drifts from the record | The record describes a repository that no longer exists — the current condition | `A-34` runs on every change |
| Boundary declarations become decorative | §10's warning realized exactly | Declarations are executable inputs to `A-34`, not prose |
| Undeclared Material state | Irreproducible executions; §10 ¶3 breached | `A-32` plus determinism testing in `validation/` |

---

## G-13 — Decision Standard

**Purpose.** Govern the Decision: the governance record authorizing declared transitions or actions.

**Authority.** §2 (Decision definition); §3 ¶1-2 (governance records define authority, required process, lifecycle, acceptance); §4 ¶5 ("A scientific transition MUST be specified by an Active Domain standard and authorized by a Decision approved by the Registry-listed authority for that transition"); §8 ¶2 (every scientific state change reversible by a later authorized Decision); §11 (one Decision authorizes one transition or one atomic set of explicitly coupled transitions).

**Placement note.** The brief lists Decision Standard under the scientific stack. It is placed here because §2 and §3 ¶2 classify a Decision as a *governance* record. The classification matters: it keeps §3's separation intact and prevents a scientific standard from owning the object that authorizes its own transitions.

**Jurisdiction (owned).** Object types: `decision`. Transitions: propose, approve, execute, reverse, supersede.

**Inputs.** The proposed transition; the specifying Domain standard; the authority assignment (G-3); the Evidence and Interpretations cited (by reference only).

**Outputs.** `decisions/*`.

**Constraints.**
- A Decision references but does not contain Evidence or Interpretations, and it does not make its rationale true (§2). This sentence should appear verbatim in G-13.
- A Decision MUST NOT alter an Observation or Result (§3 ¶6).
- Governance approval MUST NOT be represented as scientific support (§3 ¶6).
- One Decision authorizes one transition or one atomic set of explicitly coupled transitions (§11).
- Every scientific state change MUST be reversible by a later authorized Decision, and reversal MUST preserve the previous state, rationale, supporting records, and transition history (§8 ¶2).
- A Decision MUST identify the specifying standard, the authorizing authority, and the §9 eight-element transition record it produces. Missing information causes the transition to fail closed (§9 ¶3).
- Tools MUST NOT infer acceptance from evidence count, model confidence, test success, or elapsed time (§9 ¶3).

**Lifecycle.** Proposed → Approved → Executed → Reversed / Superseded. Append-only; never deleted.

**Verification.** `A-12` transition record completeness · `A-13` illegal transition detection · `A-52` Decision contains no embedded Evidence or Interpretation · `A-53` approving authority is Registry-listed and permitted for that transition.

**Failure modes.**
| Mode | Effect | Mitigation |
|---|---|---|
| Decision embeds its evidence | §2 breached; the Decision becomes self-justifying and the evidence escapes S-5's admission rules | `A-52` |
| Decision approved by an unlisted role | Transition void under §4 ¶5, but recorded as valid | `A-53` fails closed |
| Approval read as scientific support | The most consequential §3 violation available to a research institution | Mandatory disclaimer clause; `MRP-05` review |
| Irreversible transition designed in | §8 ¶2 breached structurally | Every transition definition must name its reversal |
