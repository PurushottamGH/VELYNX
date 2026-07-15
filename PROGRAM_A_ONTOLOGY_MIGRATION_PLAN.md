# PROGRAM A — ONTOLOGY MIGRATION PLAN

**Title:** Minimum repository migration to make every document consistent with
`PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md`.
**Authority basis:** `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md` (the authoritative
architectural foundation, per Research Director direction of 2026-07-15). This
plan consumes the ontology as fixed; it does not redesign it.
**Date:** 2026-07-15
**Status:** MIGRATION PLAN. This document migrates **document responsibilities
only**. It does not redesign ES-1, PA-3, the Findings, Governance, or G4; it
writes no semantic definition, derives no parameter value, implements no code,
performs no sign-off. The standing prohibition
(`ES1_IMPLEMENTATION_GATE.md`:97-99) is unchanged.

**Ontology layer key (used throughout):**
`L0 Reference → L1 Semantic Specification → L2 Freeze (Parameter/Derivation) →
L3 Implementation → L4 Verification → L5 Governance` (ontology §2). Object
classes and owners per ontology §3–§4; permitted references per §7.

**The four L1 slot identifiers used by this plan** (names for *slots*, not
definitions — authoring their content is future Architect work, expressly out
of scope here):

| Slot id | Missing L1 object | Class | Instantiating L2 parameter |
|---|---|---|---|
| `SEM-SUPPORT` | extensional semantics of `supports(claim, evidence)` | SemanticPredicate | `SUPPORT_TEST_PARAMS` (T1 §5.3) |
| `SEM-MATERIALITY` | extensional semantics of materiality (`is_material`) | SemanticPredicate | `CONTRADICTION_MATERIALITY_PARAMS` (T1 §5.4) |
| `SEM-EXTRACTION` | extensional semantics of the candidate-claim boundary | SemanticPredicate | `EXTRACTION_PARAMS` (T1 §5.6) |
| `SEM-TEMPLATE` | per-state answer-skeleton semantics | SemanticTemplate | `ANSWER_TEMPLATES` (T1 §5.7) |

These are exactly the objects the Root Cause Analysis identified as
"classified as deferred values" and the ontology's §9 historical replay
requires to exist at L1 before their parameters are inhabited
(`Parameter[definition_id]` inhabited only when its L1 definition exists and
is frozen — ontology §6).

---

## 1. Per-document object inventory

### 1.1 `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md`

| Field | Content |
|---|---|
| Objects created | `ONT-1` — the ontology itself: class table `K` (§3), authority matrix (§4), operation set (§5), type system (§6), interaction matrix (§7), closure proof (§8). One root object. |
| Objects consumed | None (root L1 `SemanticContract`, "no semantic predecessor" — §2). |
| Objects referenced | `PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md` (§1, motivation); historical failures (§9). |
| Class | `SemanticContract` (root subtype, §2). |
| Owner | Architect. |
| Lifecycle | drafted (self-declares "proposed", §0/§11) → needs **approved** before anything can lawfully consume it. |
| Migration required | **M1** (lifecycle/adoption record), **M2** (RCA citation is an L1→L4 upward edge; retype as L0 provenance). |

### 1.2 `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`

| Field | Content |
|---|---|
| Objects created | **L1:** S0–S3 state definitions + precedence (§3.1/§3.3); `STATE_TIER_MAP` coupling semantics (§3.2); per-tier semantic arguments (§4); per-state answer-construction rules (§3.1 answer column); input-restriction / Q7 read-scope contract (§8); identity-clause format (§9). **L2:** free-constant register rows 5.1–5.9 (§5); `frozen_constants_digest()` definition (§6). **L5:** blank B2/B3 sign-off blocks (§12); requested rulings B-10/B-11 (§10). |
| Objects consumed | G1/G2/T0 gate decisions (§0.2, L5 records); frozen types (`program_a/types.py`, via architecture docs); addendum §A6-DIGEST (row 5.9). |
| Objects referenced | `ES1_IMPLEMENTATION_GATE.md`, roadmap, correction plan, EXP-1 evaluation-layer symbols (§2, named-not-reproduced), §13 reference list. |
| Class | Mixed: SemanticProposition/Predicate/Contract/Template (L1) + Parameter/Derivation (L2) + Governance (L5) in one document. |
| Owner | Architect (L1 content); ScientificAuditor (L2 Parameter objects, per authority matrix); ReleaseManager/ScientificAuditor (L5 blocks). |
| Lifecycle | DRAFT (pre-B2/B3). |
| Migration required | **M3** (classify existing L1 content), **M4** (register rows split L1-role vs L2-value; Architect values become *candidates*, Parameter minted at B2), **M5** (the four deferred rows retyped to consume `SEM-*` slots — the root-cause repair), **M6** (single-owner resolution of `PA3_RULESET_VERSION` vs addendum), **M7** (gate/roadmap citations → L0), **M8** (§12 typed as L5 attestations). |

### 1.3 `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`

| Field | Content |
|---|---|
| Objects created | **L1:** rulings §A0–§A7 (claim selection, tie-break `≺`, S1 composition + `Comp`/`Part`, `is_material` contract, `contradicts` status, seam invariants I-1/I-2/I-3); digest-coverage rule set (i)–(v) (§A6-DIGEST). **L2:** `PA3_RULESET_VERSION` parameter. **L4-flavored:** §F consistency verification. **L5:** §D co-freeze block; §B reconciliation actions (transcription duties). |
| Objects consumed | T1 §3/§5/§6 (L1/L2); frozen types (§A grounding); the three A3.5 Finding corrections (merged, §E). |
| Objects referenced | `ES1_IMPLEMENTATION_GATE.md`; MODULE_SPEC/API_REFERENCE/FINAL_ARCHITECTURE (§B targets); tests (§B5). |
| Class | Mixed: SemanticPredicate/Contract (L1) + Parameter (L2) + Verification-like (§F) + Governance (§D). |
| Owner | Architect (Principal Architect, §A rules); ScientificAuditor (L2 tag value at B2); ReleaseManager (§D pin). |
| Lifecycle | DRAFT (co-freezes with T1 at G4). |
| Migration required | **M9** (classify §A rules as L1 objects), **M6** (owns creation of `PA3_RULESET_VERSION`; T1 row 5.9 becomes consuming registration), **M10** (§F demoted to informative self-check; L4 authority stays with independent audits), **M11** (gate citations → L0; §D typed as L5). |

### 1.4 `PROGRAM_A_REGISTER_DERIVATION_METHOD.md`

| Field | Content |
|---|---|
| Objects created | The derivation-procedure contract: evidence classes (§2.2), universal constraints/invariants (§2.3–§2.4), definition of "canonical" (§2.5), per-register procedures (§3–§6), auditor method (§7), freeze method (§8), re-derivation triggers (§9). |
| Objects consumed | T1 §5 register (L2 roles); addendum §A (L1 rules); G4 plan E1–E7 (L5). |
| Objects referenced | `PROGRAM_A_REGISTER_AUDIT.md` (§1 "Audit status today" column, §11) — an **L1→L4 upward edge**; `ES1_IMPLEMENTATION_GATE.md`. |
| Class | `SemanticContract` (a procedure contract; it types the L2 `DerivationArtifact` production). |
| Owner | Architect (semantic-class owner per authority matrix; currently attributed to "Chief Scientific Specification Author" — recorded as designated author under Architect ownership). |
| Lifecycle | DRAFT. |
| Migration required | **M12** (the abstraction-boundary migration: the four semantic definitions move off the "value side" — the method declares frozen `SEM-*` L1 inputs as preconditions of §3–§6), **M13** (audit citations → L0; consumes-G4-plan references → L0 identity pointers), plus ownership recording. |

### 1.5 `PROGRAM_A_REGISTER_AUDIT.md`

| Field | Content |
|---|---|
| Objects created | 11 per-entry admissibility verdicts + register-level verdict (VerificationArtifacts); the 8-criterion grid as applied. |
| Objects consumed | T1 §5/§3.2 (L1/L2); `program_a/constants.py` (L3); test evidence (L4). |
| Objects referenced | Addendum §C; gate item C1. |
| Class | `VerificationArtifact`. |
| Owner | ScientificAuditor (named verifier — conformant). |
| Lifecycle | executed → recorded. |
| Migration required | **M16** only: the four FAIL rows say "the frozen value does not yet exist" — an untyped absence. Re-express in typed form: `Parameter[SEM-*]` **uninhabited** because the required L1 definition is not frozen (ontology §6). Verdict unchanged. |

### 1.6 `PROGRAM_A_REGISTER_DERIVATION_FINDING1.md`

| Field | Content |
|---|---|
| Objects created | The uniqueness-gap finding (VerificationArtifact) **plus** E-SELECT v1 — a proposed methodology component (§4.1–§4.2/§7) with per-register selection axes. |
| Objects consumed | The derivation method; T1; addendum; register audit; G4 plan. |
| Objects referenced | `docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md` (falsified it). |
| Class | `VerificationArtifact` — **but E-SELECT v1 is semantic-class content created at L4**, which ontology §5 defines as an undefined operation ("L4/L5 creation of a semantic class … is an architectural error"). |
| Owner | Domain verifier (finding); no lawful owner exists for the embedded E-SELECT content. |
| Lifecycle | recorded → **superseded** (falsified by audit 1, replaced by Finding 2, then discarded by the RCA). |
| Migration required | **M14**: lifecycle → superseded; E-SELECT v1 declared non-normative (no semantic authority); retained as verification history. |

### 1.7 `PROGRAM_A_REGISTER_DERIVATION_FINDING2.md`

| Field | Content |
|---|---|
| Objects created | Counterexample replays CE-1/2/3 (VerificationArtifact) **plus** E-SELECT v2 (CSP-c, re-anchored CSP-a, skeleton scoping) — again semantic-class content created at L4. |
| Objects consumed | Finding 1; Sonnet audit 1; method; T1; addendum; register audit. |
| Objects referenced | `docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md` (falsified it). |
| Class | `VerificationArtifact` with unlawfully-placed semantic content (same defect class as 1.6). |
| Owner | Domain verifier (finding); none for E-SELECT v2. |
| Lifecycle | recorded → **superseded** (falsified by audit 2; the RCA diagnoses the whole selector layer as the wrong layer). |
| Migration required | **M14**: same treatment as Finding 1. |

### 1.8 `PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md`

| Field | Content |
|---|---|
| Objects created | The root-cause verdict (`C` — incorrect abstraction boundary) and the falsification-invariant analysis (§1–§5). |
| Objects consumed | Method, Finding 1, Finding 2, Sonnet audits 1–2 (all L4 or L1 — downward/same-layer, lawful). |
| Objects referenced | T1 §5 (control-group contrast). |
| Class | `VerificationArtifact` (diagnosis; explicitly no correction). |
| Owner | Domain verifier. |
| Lifecycle | executed → recorded. |
| Migration required | **M15** only: type it, record its verdict identity, and register its §6 implication ("the replacement is a definitional act owned by the specification authority") as the L0 pointer that seeds the future `SEM-*` authoring task. The ontology already consumes it as motivation (via M2's L0 retyping). |

### 1.9 `PROGRAM_A_G4_EXECUTION_PLAN.md`

| Field | Content |
|---|---|
| Objects created | Execution checklist E1–E11; dependency graph; review table (GovernanceArtifacts — process records, not semantic authority). |
| Objects consumed | T1 §1 inventory; addendum §C; register audit; gate criteria; repository state. |
| Objects referenced | The full E1 file manifest (L0-style locator list — conformant). |
| Class | `GovernanceArtifact`. |
| Owner | ReleaseManager (with ScientificAuditor/RepositoryVerifier steps). |
| Lifecycle | proposed → recorded (not yet effective; G4 not executed). |
| Migration required | **M17**: E4 currently assigns one step — "Author the remaining register values" — covering **both** the semantic definitions and the parameter values. Under the authority matrix the definitions are Architect-created L1 objects and the values are ScientificAuditor-created L2 objects. E4 splits into E4a (L1 definitions authored + frozen) and E4b (L2 values instantiating them). E1 manifest gains the ontology + the four frozen `SEM-*` artifacts. No gate criterion is redesigned; a mandated predecessor is inserted. |

### 1.10 `ES1_IMPLEMENTATION_GATE.md`

| Field | Content |
|---|---|
| Objects created | Gate condition (GO ⇔ A1–A4 ∧ B1–B3 ∧ C1–C3); NO-GO decision record; standing prohibition. |
| Objects consumed | G1/G2/T0 rulings; T1; addendum; enforcement tests. |
| Objects referenced | Correction plan; MASTER_SPEC §16. |
| Class | `GovernanceArtifact`. |
| Owner | Named governing roles per box (no proxy — conformant with §4). |
| Lifecycle | recorded → effective (NO-GO standing). |
| Migration required | **M18** only: B1's inventory description references the register informally; it must reference the typed identities — the L2 Parameter set **and** the frozen `SEM-*` L1 definitions those parameters instantiate. Gate condition text otherwise unchanged. |

**Also in scope as referenced artifacts (no migration beyond typing):**
`PROGRAM_A_FROZEN_REGISTER.md` is an L2 `DerivationArtifact`
(recorded, verification pending) whose header cites the register audit (L4)
and G4 plan (L5) as *authorities* — upward edges retyped to L0 provenance
(**M19**). The six `docs/audits/*_SONNET_AUDIT.md` files are conformant L4
`VerificationArtifacts` (recorded); no migration.

---

## 2. Repository dependency DAG (post-migration)

```
L0  REFERENCE
    └─ every document's References/citations section, retyped as typed
       locators (no authority): gate cites from L1 docs, audit cites from
       L1/L2 docs, RCA cite from the ontology, plan/audit cites from the
       frozen register.
            │  (consumed by all layers)
            ▼
L1  SEMANTIC SPECIFICATION                     owner: Architect
    ONT-1  PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md   (root; no predecessor)
      ├─► T1 semantic core        (§3 states/precedence, §4 tier args,
      │                            §3.1 answer rules, §8 input restriction,
      │                            §9 identity format)
      ├─► ADDENDUM §A0–§A7        (selection, ≺, S1 composition, is_material,
      │                            contradicts, seam invariants, digest-rule set)
      ├─► DERIVATION_METHOD       (procedure contract §2–§9)
      └─► [SEM-SUPPORT] [SEM-MATERIALITY] [SEM-EXTRACTION] [SEM-TEMPLATE]
                                  (declared slots — UNAUTHORED; the one
                                   remaining L1 gap, owned by Architect,
                                   scheduled at E4a)
            │
            ▼
L2  FREEZE (Parameter / Derivation)            owner: ScientificAuditor
    T1 §5 register rows 5.1–5.9  (values 5.1/5.2/5.5/5.8/5.9 = candidates
                                  pending B2; 5.3/5.4/5.6/5.7 = uninhabited
                                  until SEM-* frozen)
    PA3_RULESET_VERSION          (created by ADDENDUM §A6-DIGEST;
                                  registered in T1 §5.9)
    frozen_constants_digest() definition (T1 §6)
    PROGRAM_A_FROZEN_REGISTER.md (derivation record: 7 determined, 4 halted)
            │
            ▼
L3  IMPLEMENTATION                              owner: Builder
    program_a/constants.py (transcription target, E5)
    program_a/** (post-GO Wave-4 emission/binding — prohibited until E11)
            │
            ▼
L4  VERIFICATION                                owner: domain verifiers
    PROGRAM_A_REGISTER_AUDIT.md (recorded)
    FINDING1 → FINDING2 → ROOT_CAUSE_ANALYSIS (F1/F2 superseded; RCA recorded)
    docs/audits/*_SONNET_AUDIT.md (recorded)
    tests/program_a/**, tests/EXP1/** (planned/executed)
            │
            ▼
L5  GOVERNANCE                                  owner: named roles, no proxy
    PROGRAM_A_G4_EXECUTION_PLAN.md (E1→E2→E3→E4a→E4b→E5→E6→E7→E8→E9→E10→E11)
    ES1_IMPLEMENTATION_GATE.md (GO ⇔ A∧B∧C; NO-GO standing)
    T1 §12 / ADDENDUM §D sign-off blocks (attest identity only)
```

**Cycle analysis.** Pre-migration the repository contains five upward edges
and one document-level two-cycle; post-migration all are removed and every
remaining edge points downward or same-layer-acyclic:

| # | Offending edge (pre-migration) | Type | Resolution |
|---|---|---|---|
| 1 | ONTOLOGY (L1) → RCA (L4) | upward | M2: L0 provenance pointer. |
| 2 | T1 / ADDENDUM (L1) → GATE (L5) | upward | M7/M11: L0 locators (the prohibition is *governance over* T1, not a T1 dependency). |
| 3 | METHOD (L1) → REGISTER_AUDIT (L4) | upward | M13: L0 provenance ("audit status today" is informative). |
| 4 | FROZEN_REGISTER (L2) → AUDIT (L4), G4 PLAN (L5) | upward | M19: L0 provenance. |
| 5 | FINDING1/2 (L4) create E-SELECT semantic content | undefined op (ontology §5) | M14: supersede; no semantic authority. |
| 6 | T1 §5.9 ⇄ ADDENDUM §A6-DIGEST (document-level two-cycle) | same-layer cycle at doc granularity | M6: object granularity — addendum **creates** `PA3_RULESET_VERSION`; T1 row 5.9 **consumes** (registers) it. Acyclic at object level. |

No cycle remains. ∎

---

## 3. Migration table

Risk scale: LOW = wording/typing only, behavior-invariant by inspection;
MEDIUM = touches a freeze-object's text (behavior-neutral but under
change-control discipline); HIGH = repairs the root-cause boundary (highest
review scrutiny required). **No step changes any state definition, constant,
rule, threshold, verdict, or gate condition.**

| Step | Document | Section | Reason | Object class | Old responsibility | New responsibility | Dependencies | Risk |
|---|---|---|---|---|---|---|---|---|
| **M1** | ONTOLOGY | header, §11 | Nothing may consume a `drafted` L1 root; ontology must carry its own well-formed identity. | SemanticContract (L1) | "proposed", untyped | Root L1 `ONT-1` with explicit (id, class, origin, owner, lifecycle); lifecycle drafted → approved, recorded by genuine Architect approval (an L5 attestation of identity — not a new gate) | — | LOW |
| **M2** | ONTOLOGY | §1 | L1→L4 upward edge (RCA cited as ground). | ReferenceArtifact (L0) | RCA consumed as motivating dependency | RCA cited as typed L0 provenance pointer; no authority transfer | M1 | LOW |
| **M3** | T1 | §3, §4, §8, §9 | Existing semantic content is untyped; L2–L5 must consume typed L1 objects. | SemanticProposition / Predicate / Contract / Template (L1) | Prose sections with implicit authority | Same text, classified: state defs + precedence (Propositions/Predicates), tier arguments (Propositions), answer-construction rules (Templates), input restriction + identity clause (Contracts); ids assigned | M1 | LOW |
| **M4** | T1 | §5 preamble, rows 5.1–5.9 | Authority matrix: Parameter creator/owner = ScientificAuditor; the rows were Architect-authored. | Parameter (L2) + SemanticContract (L1) | Each row = one blob: role + justification + value, Architect-owned | Split per row: role + a-priori-justification form = L1 SemanticContract (Architect); "intended value" = **candidate**; the Parameter object is minted by the ScientificAuditor at B2/E4 (values unchanged) | M1, M3 | MEDIUM |
| **M5** | T1 | rows 5.3, 5.4, 5.6, 5.7 | **Root-cause repair.** The deferral token "exact parameters fixed at G4 from this register" classifies the *definition* as a deferred *value* — the exact defect of the RCA and ontology §1/§9. | Parameter (L2) consuming SemanticPredicate/Template (L1) | Semantic definition owned by nobody; bundled into "the value" | Each row typed `Parameter[SEM-*]`: value fixed at G4 **instantiating the frozen L1 definition** `SEM-SUPPORT` / `SEM-MATERIALITY` / `SEM-EXTRACTION` / `SEM-TEMPLATE` (slots declared, Architect-owned, unauthored). No definition is written here. | M1, M4 | **HIGH** |
| **M6** | T1 + ADDENDUM | T1 §5.9/§6.1; ADD §A6-DIGEST | Document-level two-cycle; ownership of `PA3_RULESET_VERSION` must be singular. | Parameter (L2) | Both documents appear to define it | Addendum §A6-DIGEST = creator (L1 rule set + L2 tag proposal); T1 §5.9/§6.1 = consuming registration | M1, M4 | LOW |
| **M7** | T1 | §0.1, §2, §7, §10, §13 | L1→L5 upward edges (gate, roadmap, correction plan cited as authorities). | ReferenceArtifact (L0) | Gate/roadmap consumed as dependencies | Typed L0 locators; the prohibition remains binding *as governance over* T1, not as a T1 input | M1 | LOW |
| **M8** | T1 | §12 | Sign-off blocks are L5 content inside an L1/L2 document. | GovernanceArtifact (L5) | Untyped blank blocks | Typed L5 attestations referencing the frozen identity only (interaction-matrix row Governance→Semantic, "identity only"); text unchanged, still blank | M1 | LOW |
| **M9** | ADDENDUM | §A0–§A7 | Same as M3 for the addendum's rules. | SemanticPredicate / Contract (L1) | Prose rulings with implicit authority | Same text, classified with ids: §A1 selection, §A2 `≺`, §A4 S1 composition + `Comp`/`Part`, §A5 `is_material` contract, §A6 `contradicts` status, §A7 I-1/I-2/I-3, §A6-DIGEST rule set (i)–(v) | M1 | LOW |
| **M10** | ADDENDUM | §F | An L1 document's author cannot hold L4 verification authority over their own object (authority matrix: named verifier). | EvidenceArtifact (informative) | §F reads as an authoritative verification PASS | §F marked informative author self-check; authoritative verification remains the independent L4 audits (`docs/audits/A3_5_*`) | M1, M9 | LOW |
| **M11** | ADDENDUM | header, §B, §D | Same upward-edge and L5-typing treatment as M7/M8. | ReferenceArtifact (L0) + GovernanceArtifact (L5) | Gate cited as dependency; §D untyped | Gate cites → L0; §D typed as L5 co-freeze attestation (identity only, still blank); §B items typed as L5-recorded transcription duties over L1 objects | M1, M9 | LOW |
| **M12** | METHOD | §0.2, §1, §10 | **The boundary migration the RCA mandates.** The method forbids itself from stating the four semantic definitions while filing them on the value side — leaving layer-4 semantics authored by nobody. | SemanticContract (L1) | "Deferred to G4" = role + prohibitions now, definition-and-value later, as one blob | The four frozen `SEM-*` L1 objects are declared **preconditions** of §3–§6: no derivation runs, and no candidate is admissible, until its `SEM-*` definition exists and is frozen (ontology §6 inhabitation rule). "Value side" retains only the L2 instantiation. No definition is authored in the method. | M1, M5 | **HIGH** |
| **M13** | METHOD | §1 table, §11 | L1→L4 upward edges (register-audit status consumed as input). | ReferenceArtifact (L0) | Audit verdicts consumed as authority | Audit citations retyped as L0 provenance (informative status snapshot); ownership of the method recorded under Architect | M1 | LOW |
| **M14** | FINDING1, FINDING2 | whole documents | Ontology §5: L4 creation of semantic content (E-SELECT v1/v2) is an undefined operation; both were falsified and the RCA discards the selector layer entirely. | VerificationArtifact (L4) | Findings read as pending methodology amendments (v1 proposes §2.6; v2 replaces it) | Lifecycle recorded → **superseded**; E-SELECT v1/v2 declared non-normative with no semantic authority; documents retained verbatim as verification history | M1 | LOW |
| **M15** | ROOT_CAUSE_ANALYSIS | whole document | Its diagnosis is the load-bearing input to M5/M12 and to the ontology; it must be a typed, recorded verdict. | VerificationArtifact (L4) | Untyped diagnosis | Typed L4 artifact, verdict recorded; §6 implication registered as the L0 pointer seeding the E4a `SEM-*` authoring task | M1 | LOW |
| **M16** | REGISTER_AUDIT | Summary; entries 5.3/5.4/5.6/5.7; Aggregate | L4 verdicts must reference typed objects; "the value does not exist" is an untyped absence. | VerificationArtifact (L4) | FAIL(deferred) = "un-transcribed placeholder; value does not exist" | Same verdicts, typed grounds: `Parameter[SEM-*]` **uninhabited** — required L1 definition not frozen (ontology §6). No verdict changes. | M1, M5 | LOW |
| **M17** | G4_EXECUTION_PLAN | §3 E1/E4, §4, §5, §7 | Authority matrix: semantic definitions are Architect-created L1 objects; parameter values are ScientificAuditor-created L2 objects. E4 currently merges both into one ScientificAuditor step. | GovernanceArtifact (L5) | E4 = "Author the remaining register values" (one step, one role, both kinds of object) | E4 → **E4a** (Architect authors + freezes `SEM-SUPPORT/-MATERIALITY/-EXTRACTION/-TEMPLATE`; ScientificAuditor approves — scientific/freeze-relevant per authority matrix) then **E4b** (ScientificAuditor authors the four L2 values instantiating the frozen definitions). E1 manifest adds ONTOLOGY + the four frozen `SEM-*` artifacts. Chain becomes E1→E2→E3→E4a→E4b→E5→…→E11; everything downstream unchanged. | M1, M5, M12 | MEDIUM |
| **M18** | ES1_IMPLEMENTATION_GATE | §B1 | L5 must reference frozen identities, not informal inventory prose. | GovernanceArtifact (L5) | B1 lists register contents informally | B1 references typed identities: the L2 Parameter set **and** the four frozen `SEM-*` L1 definitions those parameters instantiate. Gate condition (GO ⇔ A∧B∧C) unchanged. | M1, M5, M17 | LOW |
| **M19** | FROZEN_REGISTER | header, §0, §3, §4 | L2→L4/L5 upward edges; halt grounds untyped. | DerivationArtifact (L2) | Audit + plan cited as authorities; halt = "methodology §0.2+§1+§2.2 value-void" | Audit/plan cites → L0 provenance; halt grounds restated in typed form: `Parameter[SEM-*]` uninhabited until L1 definition frozen (identical conclusion, ontology-§6 grounds); lifecycle recorded → verification pending | M1, M5, M16 | LOW |

**Cross-cutting note (implicit in M3/M9, not separate steps):** each migrated
document carries a short object manifest (created / consumed / referenced with
class-owner-lifecycle) matching Section 1 above. That manifest is the entire
mechanism by which "typed objects" become checkable; it adds no content.

---

## 4. Critical path

```
M1 (adopt ONT-1 as approved root L1)
 └─► M4 (register rows split: L1 role vs L2 candidate value)
      └─► M5 (four deferred rows retyped to consume SEM-* slots)   ← root-cause repair
           └─► M12 (method boundary: SEM-* frozen = precondition of derivation)
                └─► M17 (G4 plan E4 → E4a/E4b; manifest gains ONT-1 + SEM-*)
                     └─► M18 (gate B1 references typed identities)
```

Everything else (M2, M3, M6–M11, M13–M16, M19) hangs off M1 and can proceed in
parallel with the critical path. The critical path is exactly the chain that
turns the RCA's diagnosis into enforced document responsibility: **root
adopted → parameters re-typed → deferral re-typed → derivation gated on L1 →
freeze plan sequenced → gate references typed identities.**

---

## 5. Blocking dependencies

1. **ONT-1 approval (M1) blocks every other step.** A `drafted` root cannot be
   consumed (ontology §3 lifecycle); the approval is a genuine Architect
   record, no proxy (§4). This is the single entry gate of the migration.
2. **M5 blocks M12, M16, M17, M18, M19.** Until the T1 rows are re-typed, the
   `SEM-*` slot identifiers do not exist and nothing downstream can reference
   them.
3. **M14 (supersede Findings 1–2) should land before M12** so the method's
   migrated text imports no E-SELECT obligation — otherwise M12 would have to
   simultaneously add the L1-precondition and adjudicate a live selector
   proposal, which is redesign, not migration.
4. **Out-of-migration blocker (declared, not performed):** the four `SEM-*` L1
   objects are **unauthored**. Authoring them is Architect L1 work scheduled
   at E4a (M17) — it is a semantic-definition act this plan is forbidden to
   perform. Until E4a completes and freezes them, `Parameter[SEM-*]` stays
   uninhabited, `CONSTANTS_HASH` stays `None`, and G4 stays inadmissible —
   exactly the load-bearing placeholder posture already on disk. The migration
   makes this blocker *typed and owned*; it cannot and does not discharge it.

---

## 6. Safe execution order

Ten stages; steps within a stage are independent and may run in any order or
in parallel. No stage begins before its predecessor completes.

| Stage | Steps | What lands |
|---|---|---|
| 1 | M1 | Ontology adopted as approved root L1 object. |
| 2 | M2, M3, M9 | Upward edge out of the ontology removed; existing L1 content in T1 and the addendum classified (pure typing, zero text change). |
| 3 | M14, M15 | Findings 1–2 superseded; RCA typed and recorded. (Before any method edit — see blocking dep. 3.) |
| 4 | M4, M6 | Register rows split L1/L2; `PA3_RULESET_VERSION` single-owner resolution. |
| 5 | M5 | The four deferred rows retyped to consume `SEM-*` (root-cause repair; highest-scrutiny review). |
| 6 | M12, M13 | Method boundary migrated; method's upward edges removed. |
| 7 | M7, M8, M10, M11 | Remaining T1/addendum reference retyping and L5-block typing (behavior-invariant; safe late). |
| 8 | M16, M19 | Audit FAIL rows and frozen-register halt re-expressed in typed form. |
| 9 | M17 | G4 plan E4 → E4a/E4b; E1 manifest extended. |
| 10 | M18 | Gate B1 references typed identities. Migration complete. |

Because T1 and the addendum are pre-G4 DRAFT with no minted `mechanism_id()`
and `CONSTANTS_HASH = None`, all edits above are pre-freeze document-
responsibility changes: **no re-freeze, no `SPEC_VERSION` movement, and no
`PA3_RULESET_VERSION` movement** is triggered (no rule (i)–(v) text changes;
per addendum §A6-DIGEST and method §8 step 5, typing/transcription actions are
not rule edits). The five transcribed register **values**, all verdicts, all
gate boxes, and the standing prohibition are byte-identical before and after.

---

## 7. Repository readiness score

Scored against the five ontology-closure obligations the mission states, per
document (2 = conformant, 1 = partially, 0 = non-conformant), max 50:

| Document | L1 before L2 | L2 consumes L1 | L3 consumes frozen L2 | L4 refs typed objects | L5 refs frozen identities | Now | After migration |
|---|---|---|---|---|---|---|---|
| ONTOLOGY | 2 | n/a | n/a | 0 (RCA edge) | 1 (unapproved) | 3/6 | 6/6 |
| T1 | 0 (four defs filed as L2 values) | 1 | 2 (prohibition holds) | n/a | 1 (§12 untyped) | 4/8 | 8/8 |
| ADDENDUM | 1 (§F mixed-in) | 2 | 2 | 1 | 1 | 7/10 | 10/10 |
| METHOD | 0 (boundary defect) | 1 | n/a | 0 (audit edge) | 2 | 3/8 | 8/8 |
| REGISTER_AUDIT | n/a | n/a | n/a | 1 (untyped absence) | 2 | 3/4 | 4/4 |
| FINDING1 | 0 (L4 creates semantics) | n/a | n/a | 2 | n/a | 2/4 | 4/4 |
| FINDING2 | 0 (same) | n/a | n/a | 2 | n/a | 2/4 | 4/4 |
| RCA | 2 | n/a | n/a | 2 | n/a | 4/4 | 4/4 |
| G4 PLAN | n/a | n/a | 2 | 2 | 1 (E4 merges L1+L2 authorship) | 5/6 | 6/6 |
| GATE | n/a | n/a | 2 | 2 | 1 (B1 informal) | 5/6 | 6/6 |

**Pre-migration: 38/60 ≈ 63%. Post-migration: 60/60 structural conformance**,
with one declared, typed, owned open slot set (`SEM-*` unauthored — L1
*content* gap, not a document-responsibility gap; owned by Architect at E4a
and mechanically enforced by the existing uninhabited-parameter posture).

---

## 8. Final verdict

# **PASS WITH MIGRATIONS**

- The repository requires the **19 migrations of Section 3** (M1–M19) to be
  consistent with `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md`. Every one is a
  document-responsibility change: typing, ownership, lifecycle, reference
  direction, or step-splitting. **Zero scientific content changes**: no state
  definition, constant, rule, threshold, verdict, verdict-ground conclusion,
  or gate condition moves.
- Post-migration, the dependency graph of Section 2 is acyclic with all edges
  same-or-earlier-layer; every L2 parameter names its L1 predecessor; L3
  remains prohibited pending GO; every L4 verdict references typed objects;
  every L5 record references frozen identities.
- The single remaining non-migration item — authoring the four `SEM-*` L1
  semantic definitions — is deliberately **not** in this plan (forbidden:
  "DO NOT write semantic definitions"). The migration's whole effect is that
  this work now has exactly one type (`SemanticPredicate`×3 +
  `SemanticTemplate`×1), one origin (L1), one owner (Architect), one approver
  (ScientificAuditor), one schedule slot (E4a, before E4b), and one mechanical
  enforcement (uninhabited `Parameter[SEM-*]` ⇒ `CONSTANTS_HASH = None` ⇒ G4
  inadmissible) — which is precisely the closure the ontology exists to
  provide.

---

*End of ontology migration plan. 19 migration steps, one critical path
(M1→M4→M5→M12→M17→M18), no cycles remaining, no scientific content changed,
no semantic definition written, no value derived, no governance performed.*
