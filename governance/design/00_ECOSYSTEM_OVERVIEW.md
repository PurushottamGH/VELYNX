# P1 Constitutional Ecosystem — Overview, Hierarchy, and Delegation Map

- **Status:** Draft
- **Scope:** Design of the artifact ecosystem required to operate Project P1 under `REPOSITORY_CONSTITUTION.md` v1.2.0
- **Responsibility:** Define the artifact hierarchy, the dependency graph, the constitutional delegation surface, and the jurisdiction partition
- **Authority source:** None. This record has no normative authority, activates nothing, and authorizes no transition.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft, not adopted)
- **Version:** 0.1.0
- **Document set:** `governance/design/` — see `README.md` in this directory for the index

---

## 0. Reading this document

This is a **design record**, not a standard. It proposes artifacts; it does not create them, activate them, or grant them authority. Under Constitution §4, an artifact acquires authority only through a Governance Registry entry, an approving Registry-listed authority, and an Independent reviewer attestation, delivered as one Atomic change. Nothing in this directory satisfies any of those conditions.

Where this document uses MUST, MUST NOT, SHOULD, or MAY, it is **describing a requirement that a proposed artifact would impose once activated**, not imposing one now. Section 8 records the one place where the Constitution appears to contradict itself in a way that prevents implementation.

---

## 1. Starting state (verified 2026-07-25, revision `66e3e2a` + working tree)

The design must begin from the real state, not the intended one.

| Fact | Source | Consequence |
|---|---|---|
| Constitution status is `Draft; proposed for activation under Section 13` | `REPOSITORY_CONSTITUTION.md` line 3 | Under §4, Draft artifacts have no normative authority. **The Constitution does not currently bind anything.** |
| `GOVERNANCE_REGISTRY.yaml` is `status: Draft`, `active_domain_standards: []`, `constitutional_steward: []`, both attestations `null` | `GOVERNANCE_REGISTRY.yaml` | No authority exists to activate any Domain standard. §4: "If no such authority exists, activation fails closed." |
| Exactly one identified human appears in the entire git history | Repository survey | §13 initial adoption requires **two** identified humans. §4: automated systems "MUST NOT supply human authority or independent review." **Adoption is structurally unsatisfiable today.** |
| ~13 artifacts declare themselves canonical, absolute, frozen, or authoritative | Repository survey | Each is prohibited by §1 and §14. All become Legacy at adoption under §14. |
| A second constitution exists: `theory/PROGRAM_D_CONSTITUTION.md` ("Its authority is absolute") | Repository survey | Direct jurisdictional collision with the Repository Constitution. |
| No architecture record satisfying §10 exists | Repository survey | §10 requires layout to be defined in versioned architecture records. This is a standing nonconformance, not a gap in the Constitution. |
| No CI check validates the Registry, artifact headers, attestations, or jurisdiction overlap | `.github/workflows/` | Every §12 mechanically-decidable governance requirement is currently unverified. |

**Design consequence.** The ecosystem must be designed so that it is *correct while dormant*. Every artifact must be able to sit in Draft indefinitely, accumulate review, and activate later in a defined order, without any interim artifact claiming authority it does not have. This is the **Pre-Adoption Operating Mode** in Section 7.

---

## 2. The two orderings: authority is not dependency

The most common failure mode in a governance stack of this size is conflating *"A depends on B"* with *"A is subordinate to B."* Constitution §4 fixes a four-level authority order and nothing else. Everything this design proposes below the Constitution — every governance standard, every scientific standard, the ontology — sits at **the same authority level: Level 2, Active Domain standard.**

**Authority order (§4, fixed, not designable):**

```
Level 1   REPOSITORY_CONSTITUTION.md
Level 2   Active Domain standard          <-- ALL proposed G-* , S-* , O-1 live here, as peers
Level 3   Active Registered protocol; Decision authorized by a Level-2 standard
Level 4   Implementation and explanatory documentation
```

`GOVERNANCE_REGISTRY.yaml` has **no assigned rank** in this order. That is a real defect (see §8, finding D-2).

**Dependency order (designed, acyclic, carries no authority).** A Level-2 standard may *reference* definitions owned by a peer Level-2 standard. It gains no precedence by doing so. Because §4 states that conflicting requirements at the same level are *both nonconforming* until the common parent authority resolves them, peer dependency must be constrained:

> **Peer Reference Rule (proposed architectural invariant).** A Domain standard MUST reference a peer's owned definitions by identifier and MUST NOT restate, paraphrase, extend, or narrow them. Restating a peer's requirement creates two same-level requirements on one subject, which §4 renders mutually nonconforming the moment they drift.

This single rule is what makes 24 peer standards tractable instead of quadratically fragile.

---

## 3. Jurisdiction partition — the disjointness discipline

Constitution §4: "The Governance Registry MUST reject overlapping normative jurisdictions unless one entry explicitly delegates a non-conflicting refinement to the other." Constitution §9: "every subordinate scientific or governance object type MUST have exactly one Active Domain standard within a given Scope."

Together these force a **partition**, not a taxonomy. The partition is defined by one rule:

> **Jurisdiction Rule (proposed architectural invariant).** A jurisdiction is the triple *(owned object types, owned transitions, scope)*. A transition belongs to the standard that owns **the object type whose state changes**. Where a transition creates object B from object A, the transition belongs to B's standard; B's standard states input admissibility conditions on A by reference, and never imposes requirements on A itself.

Worked examples of the rule resolving otherwise-ambiguous boundaries:

| Ambiguous transition | Naive owner | Correct owner under the Jurisdiction Rule | Why |
|---|---|---|---|
| Admitting an Observation as Evidence for a Claim | Observation Standard | **S-5 Evidence Standard** | The Evidence record is created; the Observation is unchanged. §6 independently delegates admission to "the applicable Domain standard." |
| Escalating a Question to an Unknown | Question Standard | **S-3 Unknown Standard** | An Unknown is created. S-2 records the referral only. |
| Recording working output as a Result | Research/Protocol Standard | **S-8 Result Standard** | The Result is created. §7 delegates the *time and authority* to "an applicable Domain standard or Registered protocol"; S-8 owns the object, the protocol supplies the criteria. |
| Changing a Claim's state on new Evidence | Evidence Standard | **S-6 Claim Standard** | The Claim's state changes. Evidence is an input. |
| Approving a scientific transition | The scientific standard | **G-13 Decision Standard** owns the *Decision record*; the scientific standard owns the *transition* | §4: a scientific transition is "specified by an Active Domain standard and authorized by a Decision." Specification and authorization are different objects. |
| Declaring a check's scope and known false negatives | Conformance Standard | **G-11 Automation Standard** | The check is the object. G-5 owns the conformance *claim* that cites the check. |
| Retaining an external artifact by digest | Evidence Standard | **G-7 Custody Standard** | The custody record is the object. §6's digest-algorithm delegation is assigned to G-7 to keep it single-homed. |

Every governed object type appears in exactly one row of the "owns lifecycle" column across `02_GOVERNANCE_STACK.md` and `03_SCIENTIFIC_STACK.md`. That table is the machine-checkable statement of §9 compliance, and check `A-04` in `05_AUTOMATION_ARCHITECTURE.md` verifies it.

---

## 4. Constitutional delegation map

Constitution §4 permits refinement **only where the higher level explicitly delegates it**, and requires a delegation to identify five elements: delegated subject, Scope, recipient artifact or role, permitted transitions, and limits.

Auditing the Constitution clause by clause yields the following delegation surface. This table is the sole legitimate basis for every proposed artifact; an artifact with no row here has no constitutional justification and is not proposed.

### 4.1 Explicit delegations (usable)

| Clause | Delegated subject | Recipient | Assigned to |
|---|---|---|---|
| §2 *Registered protocol* | Registration-before-execution condition | Domain standard | S-1 |
| §2 *Active* | Entry to Active state for non-normative objects | "the applicable Domain standard" | each type's standard |
| §5 ¶3 | Preregistration element set (sampling frame, stopping rule, exclusions, assignment, controls, outcomes, analysis population, decision rule, multiplicity, model selection, randomness plan) | Registered protocol | S-1 |
| §5 ¶6 | Governance of constants, thresholds, models, ontologies, hypothesis sets, conclusions | "a revisable domain standard or registered protocol" | O-1, S-10, S-1 |
| §6 ¶2 | Collision-resistant digest algorithm and version | Domain standard or Registered protocol | G-7 |
| §6 ¶4 | Authority, criteria, and recorded procedure for admitting, excluding, or revising Evidence | Domain standard or Registered protocol | S-5 |
| §7 ¶2 | When a governed execution is complete; time and authority for recording working output as Result / Invalid Result / abandoned execution | Domain standard or Registered protocol | S-8 |
| §7 ¶4 | Validity rule permitting exclusion of an Invalid Result from inference | Registered protocol | S-1 (form), S-8 (application) |
| §9 ¶1 | Nine-element lifecycle definition for every subordinate object type | "exactly one Active Domain standard within a given Scope" | every G-* and S-* |
| §10 ¶1 | Software architecture and repository layout | "versioned architecture records" | G-12 |
| §10 ¶5 | Whether a safe reproducible fixture may be version-controlled | "a domain standard explicitly requires" | G-12, G-7 |
| §12 ¶4 | Named manual review procedure for non-mechanically-decidable requirements | unnamed recipient | G-4, G-5 |

### 4.2 Reserved to the Constitution (not delegable; no artifact may refine)

§1 normative force · §2 object-kind distinctions and the prohibition on substitution · §3 separation of responsibilities · §4 authority ordering, overlap rejection, activation preconditions, the prohibition on self-activation · §5 the eight Claim requirements and the pre-access fixing requirement · §6 the nine Evidence identification items and the prohibition on conclusion-driven promotion · §7 Result immutability and Negative Result retention · §8 Unknown permanence and universal reversibility · §9 the eight-element transition record and fail-closed rule · §11 the one-primary-responsibility rule and terminology reuse · §12 conformance traceability and the prohibition on redefining nonconformance · §13 the amendment dossier and attestation content.

**Design consequence.** Roughly two-thirds of the governance burden is already discharged by the Constitution itself. The proposed standards are therefore mostly *procedural and ontological*, not substantive. Any proposed standard that restates a §4.2 item is redundant and is rejected by this design.

### 4.3 Delegations that are relied upon but under-specified

Three delegations are load-bearing yet do not satisfy §4's own five-element requirement. They are recorded here and escalated in §8.

| Clause | What is missing |
|---|---|
| §9 ¶4 "Normative artifacts use the **minimum** lifecycle Draft → Active → Superseded or Withdrawn" | "Minimum" implies extension is permitted, but no recipient, permitted transitions, or limits are identified. G-2 depends on this. |
| §12 ¶4 "Requirements not mechanically decidable MUST have a named manual review procedure" | No recipient artifact or role is identified. G-4/G-5 depend on this. |
| §10 ¶1 "versioned architecture records" | Recipient artifact kind is named, but permitted transitions and limits are not. G-12 depends on this. |

---

## 5. Artifact hierarchy

```
TIER 0  CONSTITUTIONAL
        REPOSITORY_CONSTITUTION.md .................. Level 1 authority
        GOVERNANCE_REGISTRY.yaml .................... rank unassigned (defect D-2)

TIER 1  ONTOLOGICAL                                   Level 2, peer
        O-1  Ontology Standard ...................... object-type register, identifiers, relationships

TIER 2  GOVERNANCE DOMAIN STANDARDS                   Level 2, peers
        G-1  Registry Specification
        G-2  Normative Artifact Standard             (subsumes: Governance Std, Version, Change, Release-of-normative-artifacts)
        G-3  Authority & Delegation Standard         (subsumes: Authority, Delegation, Steward policies)
        G-4  Review & Attestation Standard
        G-5  Conformance Standard
        G-6  Audit Standard
        G-7  Records Custody & Retention Standard    (the governance half of "Evidence Policy")
        G-8  Change & Release Standard               (change sets and software releases)
        G-9  Emergency & Containment Standard
        G-10 Conflict Resolution Standard
        G-11 Automation & Tooling Standard
        G-12 Architecture Standard
        G-13 Decision Standard

TIER 3  SCIENTIFIC DOMAIN STANDARDS                   Level 2, peers
        S-1  Research Standard        (Investigation, Registered protocol)
        S-2  Question Standard
        S-3  Unknown Standard
        S-4  Observation & Source Standard
        S-5  Evidence Standard
        S-6  Claim Standard
        S-7  Hypothesis Standard
        S-8  Result Standard
        S-9  Interpretation Standard
        S-10 Principle Standard

TIER 4  INSTRUMENTS                                   Level 3
        Registered protocols · preregistrations · Decisions

TIER 5  REALIZATION                                   Level 4
        Implementation · checks · fixtures · architecture records · README / indices
```

### 5.1 Consolidations against the brief, with justification

The brief lists artifacts that cannot coexist as separate Registry entries without violating §4's overlap rejection. Each consolidation below is forced, not stylistic.

| Brief artifact | Disposition | Constitutional reason |
|---|---|---|
| Governance Standard | Merged into **G-2** | A standard governing Domain standards *is* a Normative Artifact Standard. Two entries would own the same object type, violating §9's "exactly one." |
| Version Policy | Split: normative-artifact versions → **G-2**; software/release versions → **G-8** | These are different object types. A single "Version Policy" would own two unrelated types and overlap both. |
| Change Policy · Release Policy | Merged into **G-8** | Both own the change-set/release object; §11 one-primary-responsibility permits one document, and separate entries would overlap. |
| Authority Policy · Delegation Policy · Steward Policy | Merged into **G-3** | All three own *authority assignment records*. Three entries = three owners of one object type. |
| Evidence Policy | Split: scientific admission → **S-5**; custody, retention, digests → **G-7** | §2 makes Evidence a scientific record kind; §6 delegates admission separately from external-artifact identification. |
| Conflict Resolution Policy | Retained as **G-10**, narrowed to the *conflict record* object | §4 already fixes the substantive resolution rule. G-10 may own only the record and escalation procedure; owning the rule would enlarge jurisdiction, prohibited by §4. |
| Emergency Policy | Retained as **G-9**, narrowed to *containment action records* | §12 delegates only post-hoc recording of security containment. G-9 MUST NOT create authority to bypass §13 or any scientific transition. |
| Phase 4 "domain framework" | Merged into **G-2** as the Domain Standard Interface | A framework imposing requirements on future Domain standards owns the Domain standard object type — G-2's jurisdiction. |
| Observation Standard | Extended to **S-4 Observation & Source** | §2 defines Source as a distinct referenced object with no other candidate owner; leaving it unowned violates §9. |

Net: 25 brief artifacts + ontology → **24 Registry entries** with a provably disjoint partition.

---

## 6. Dependency graph

Edges denote *reference dependency* (A reads definitions owned by B). No edge confers authority. The graph is acyclic; acyclicity is check `A-33`.

```
                        REPOSITORY_CONSTITUTION.md  (Level 1)
                                     |
                        GOVERNANCE_REGISTRY.yaml
                                     |
                                   O-1  Ontology Standard
                                     |
      +-----------+---------+--------+--------+---------+-----------+
      |           |         |        |        |         |           |
    G-1         G-2       G-3      G-7     G-11      G-12         S-2
  Registry   Normative  Authority Custody Automation Architecture Question
   Spec       Artifact  Delegation                                   |
                |          |        |                                |
                |        G-4        |                              S-3  Unknown
                |     Review &      |                                |
                |    Attestation    |                                |
                |        |          |                                |
                |      G-13 <-------+                                |
                |     Decision                                       |
                |        |                                           |
      +---------+--------+---------+                                 |
      |         |        |         |                                 |
    G-8       G-5      G-10      S-1  Research  <--------------------+
   Change  Conformance Conflict   (Investigation, Registered protocol)
      |         |                   |
    G-9       G-6                   +---------------+
  Emergency  Audit                  |               |
                                  S-4  Observation & Source
                                    |               |
                                  S-5  Evidence   S-8  Result
                                    |               |
                                    +-------+-------+
                                            |
                                  S-6  Claim        S-9  Interpretation
                                            |               |
                                          S-7  Hypothesis   |
                                            |               |
                                            +-------+-------+
                                                    |
                                                 S-10  Principle
```

**Critical-path reading.** O-1 gates everything. G-3 gates every authorized transition. G-4 gates every attestation, and therefore gates activation of all 22 remaining standards. G-13 gates every scientific state change. Nothing scientific can move before `O-1 → G-3 → G-4 → G-13` are Active.

---

## 7. Pre-Adoption Operating Mode

Because adoption is blocked on a second identified human (§1 of this document; `10_HUMAN_JUDGMENT_REGISTER.md` item H-01), the ecosystem needs a defined way to accumulate value while binding nothing. This mode is a *description of restraint*, not a governance instrument — it grants nothing and therefore needs no authority.

While the Constitution is Draft:

1. Every artifact in `governance/design/` and every proposed standard carries `Status: Draft` and `Authority source: None`.
2. No artifact asserts canonical, absolute, frozen, definitive, supreme, or authoritative status. Existing artifacts that do are catalogued for Legacy disposition, not repaired in place (repair would imply an authority to repair).
3. Automated checks may run and report, and are labelled **advisory**. Under §12 an unavailable or advisory check is "not verified," never "passed."
4. Scientific work may proceed as **working output** (§2), which explicitly "MUST NOT be cited as Evidence." No Result, Evidence record, Claim state change, or Principle is created, because the standards defining those transitions are not Active and §9 requires transitions to fail closed on missing information.
5. Preregistrations may be written and committed. Their §2 status as *Registered protocols* is deferred until S-1 is Active; until then they are Draft protocols and any execution against them is exploratory under §2's confirmatory/exploratory definition.

Point 5 is the expensive one and should be understood plainly: **work executed before S-1 is Active cannot later be relabelled confirmatory.** §5 fixes the pre-access requirement and §13 forbids amendments that retroactively alter a prior record's meaning. This is the strongest practical argument for prioritising adoption over further design.

---

## 8. Contradictions that prevent implementation

The brief permits constitutional change only where a direct contradiction prevents implementation. Three qualify. Each is stated as a defect with a minimal proposed remedy; none is applied, and each is escalated to `10_HUMAN_JUDGMENT_REGISTER.md`.

**D-1 — Delegation clauses do not satisfy the Constitution's own delegation requirement.**
§4 requires every delegation of refinement to identify subject, Scope, recipient, permitted transitions, and limits. The three delegations in §4.3 above identify at most two of the five. A strict reader concludes that G-2, G-4, G-5, and G-12 cannot legitimately refine anything, which leaves the Normative artifact lifecycle, manual review procedures, and architecture records permanently unrefinable — and §10 simultaneously *requires* architecture records to exist. That is a contradiction that prevents implementation.
*Minimal remedy:* a single new §4 paragraph — a General Delegation Clause enumerating the delegations of §4.1 and §4.3 in the five-element form. Additive; changes no existing requirement.

**D-2 — The Governance Registry has no rank in the precedence order.**
§4 orders four levels and omits the Registry. §2 makes the Registry the sole determinant of what is Active, so a Registry/standard conflict is unresolvable: the standard's authority depends on the Registry entry, and the Registry entry's correctness depends on the standard. Already recorded as finding F-6 in `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md`.
*Minimal remedy:* state in §4 that the Registry is determinative of identity, status, jurisdiction, and authority assignment, and that on conflict the artifact is nonconforming until reconciled — i.e. the Registry decides *whether* an artifact has authority, never *what* it requires.

**D-3 — §2 fixes a repository path while §10 declares layout non-constitutional.**
§2 hardcodes `GOVERNANCE_REGISTRY.yaml`; §10 states "repository layout are not constitutional" and "MUST be defined in versioned architecture records." The Registry's location is therefore simultaneously constitutional and prohibited from being constitutional. Practical effect: the Registry can never be relocated without a constitutional amendment, and any architecture record that specifies its location exceeds its authority.
*Minimal remedy:* in §2, identify the Registry by role and require the architecture record to bind exactly one path to that role; or accept the pin and note the exception explicitly in §10. This one is low-severity and may reasonably be left as-is with the exception documented.

No other contradiction was found that prevents implementation. In particular, the two-human adoption requirement of §13 is **not** a contradiction — it is a deliberate, coherent constraint that the project currently cannot satisfy. Amending it to accommodate a single researcher would dissolve the Independent reviewer guarantee that §2, §12, and §13 jointly depend on, and is recorded as a human decision (H-01), not an engineering defect.

---

## 9. Deliverable index

| Output required by the brief | Location |
|---|---|
| 1. Complete constitutional ecosystem | this document §5, plus `02_` and `03_` |
| 2. Dependency graph | this document §6 |
| 3. Artifact hierarchy | this document §5 |
| 4. Repository tree | `01_REPOSITORY_ARCHITECTURE_RECORD.md` |
| 5. Governance architecture | `02_GOVERNANCE_STACK.md` |
| 6. Scientific architecture | `03_SCIENTIFIC_STACK.md` |
| — Domain extensibility framework | `04_DOMAIN_STANDARD_INTERFACE.md` |
| 7. Automation architecture | `05_AUTOMATION_ARCHITECTURE.md` |
| 8. Verification architecture | `06_VERIFICATION_ARCHITECTURE.md` |
| 11. Future expansion plan | `07_EXTENSION_ARCHITECTURE.md` |
| 9. Implementation roadmap | `08_IMPLEMENTATION_ROADMAP.md` |
| 10. Risk assessment | `09_RISK_ASSESSMENT.md` |
| Human constitutional judgment | `10_HUMAN_JUDGMENT_REGISTER.md` |
| Machine-readable jurisdiction form | `REGISTRY_TARGET_STATE.example.yaml` |
