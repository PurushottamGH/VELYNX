# PROGRAM A — SEMANTIC AUTHORING METHODOLOGY (SAM)

**Title:** The scientific methodology by which the four L1 semantic
definitions — `SEM-SUPPORT`, `SEM-MATERIALITY`, `SEM-EXTRACTION`,
`SEM-TEMPLATE` — will later be authored, falsified, and made freeze-eligible.
How a semantic definition is *produced and certified*, never what it says.
**Object identity:** `SAM-1` — class `SemanticContract`, origin L1, owner
Architect, lifecycle **drafted**. A procedure contract in the same ontology
position as `PROGRAM_A_REGISTER_DERIVATION_METHOD.md`: that document types the
production of L2 values (E4b); this document types the production of the L1
definitions those values instantiate (E4a).
**Authority basis:** `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md` (ONT-1, consumed as
fixed); `PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md` (slot identifiers, class
assignments, E4a/E4b split per M17); the falsification history is consumed as
L0 provenance only (`PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md` and
the CE catalogue of the two Sonnet audits).
**Date:** 2026-07-15
**Status:** DRAFT — methodology only. This document **authors no semantic
definition, chooses no parameter value, redesigns no part of ES-1 or PA-3,
implements no code, and performs no governance.** The standing prohibition
(`ES1_IMPLEMENTATION_GATE.md`:97-99) is unchanged. Every occurrence of a
semantic term below (entity, span, materiality, skeleton, …) names a **question
the future definition must answer**, never an answer.

---

## 0. Purpose, position, and hard boundaries

### 0.1 Purpose

The Root Cause Analysis established that the recurring failure of the register
program is `C` — an abstraction boundary that filed definitional content
("layer 4 semantics") on the deferred-value side, where no actor could author
it. The migration plan repaired the *ownership* of that layer: the four
definitions are now typed slots (`SemanticPredicate`×3, `SemanticTemplate`×1),
L1-origin, Architect-owned, ScientificAuditor-approved, scheduled at E4a.

What no existing document supplies is the **scientific process** by which
those definitions are authored so that the result is objective rather than
stipulative: so that a definition, once frozen, provably terminates the
v1→v2 regress instead of relocating it one meta-level up. The
`PROGRAM_A_REGISTER_DERIVATION_METHOD.md` cannot serve, because it governs
values and is constitutively value-free (§0.2/§10); it *presupposes* frozen
definitions (post-migration M12 precondition). This document is the missing
companion: **the E4a methodology.**

### 0.2 Non-goals (hard boundaries on this document)

This document does **not**, and no reader may treat it as if it does:

- **Author any semantics.** No extension, predicate clause, quantifier choice,
  normalization rule, granularity, span rule, materiality boundary, or
  template skeleton appears here. Where semantic content would otherwise be
  stated, this document states the *obligation to state it* and stops.
- **Choose any value.** No parameter, threshold, string, or constant is named.
  The L2 value layer remains entirely governed by the derivation method.
- **Redesign ES-1 or PA-3.** Every state definition, precedence rule, tier
  coupling, seam invariant, contract, and type of T1 §3–§9 and addendum §A is
  consumed as fixed context. A definition candidate that would require
  changing any of them is *rejected by this methodology* (§10), not
  accommodated.
- **Implement code or perform governance.** No test, prototype, sign-off,
  freeze, or pin. All sign-off blocks remain blank; the pre-GO code ban holds.

### 0.3 Binding firewall (CR-8/L8), restated for definition authoring

Firewall conformance is a property of the *authoring procedure*, exactly as
the derivation method makes it a property of the value procedure. No step of
this methodology — question formulation, drafting, probe construction,
falsification, adjudication — may read, import, mirror, or be fitted to any
evaluation-side object: no EXP-1 tier→probability mapping, bin boundary, ECE
logic, outcome, frozen row, or adjudicator signal. A definition authored with
any such input is inadmissible **regardless of its content** (§10, R-6).

### 0.4 Object manifest

| Field | Content |
|---|---|
| Objects created | `SAM-1` (this contract); the per-object protocol schemas SQ-*/PO-*/F-*/J-* of §5–§9 (obligation schemas, not semantics); the requirement register SAM-R1–SAM-R14 (§11). |
| Objects consumed | ONT-1 (class/authority/operation rules); migration plan slot table and E4a/E4b split; T1 §3–§9 + addendum §A as fixed context; frozen types (`program_a/types.py`). |
| Objects referenced (L0 provenance, no authority) | RCA; Findings 1–2 (superseded); the two Sonnet audits (CE catalogue); `PROGRAM_A_REGISTER_AUDIT.md`; `ES1_IMPLEMENTATION_GATE.md`; `PROGRAM_A_G4_EXECUTION_PLAN.md`. |
| Class / owner / lifecycle | `SemanticContract` / Architect / drafted → requires approval before E4a may consume it. |

---

## 1. The scientific object this methodology produces

### 1.1 Deliverable form: what a frozen `SEM-*` must be

Each `SEM-*` artifact, when authored under this methodology, is a
**five-part scientific object**. Absence of any part makes the candidate
ill-formed before any content is examined:

1. **Declared universe `U`** — the exact input space the definition is total
   over, stated in terms of the frozen types only (e.g. all well-typed pairs,
   all `(query_text, snapshot)` inputs). "Reachable/defined over *which*
   space" (CE-11) is answered here, in the definition, not litigated later.
2. **Defining rule `D`** — the extensional content: a biconditional
   ("… ⟺ …") or constructive rule that, for every element of `U`, entails
   exactly one output. `D` must contain **positive** conditions (what forces
   the predicate to fire / the extractor to emit / the skeleton to take a
   given form), not prohibitions alone. This is the two-sidedness repair
   (v1-a, v1-b: degenerate infima existed because the constraint layer was
   all-prohibition).
3. **Declared parameter surface `P`** — the explicit, finite, typed list of
   degrees of freedom the definition *deliberately* leaves to the L2 value,
   each with (a) its admissible set defined extensionally by `D`, and (b) its
   **selection ground** (§3.5). An undeclared degree of freedom discovered
   later is a rejection ground, not a patch site.
4. **Axis-closure table `X`** — one row per required scientific question
   (§5–§8 item 1 for the object), each row citing the clause of `D` (or slot
   of `P`) that answers it. No row may be empty.
5. **Proof pack `Π`** — the written discharge of every proof obligation
   (§5–§8 item 4), each proof citing only allowed evidence (item 2).

### 1.2 Ontology placement (fixed, consumed)

| Slot | Class | Origin | Owner (creator) | Approver | Schedule |
|---|---|---|---|---|---|
| `SEM-SUPPORT` | SemanticPredicate | L1 | Architect | ScientificAuditor | E4a |
| `SEM-MATERIALITY` | SemanticPredicate | L1 | Architect | ScientificAuditor | E4a |
| `SEM-EXTRACTION` | SemanticPredicate | L1 | Architect | ScientificAuditor | E4a |
| `SEM-TEMPLATE` | SemanticTemplate | L1 | Architect | ScientificAuditor | E4a |

Lifecycle per ontology §3: drafted → approved → frozen. `Parameter[SEM-*]`
(the four L2 registers) is inhabited only after freeze (ontology §6). Each
`SEM-*` may reference only L0/L1 objects, acyclically (§9, J-6).

---

## 2. The nine guarantees, made operational

Each mission guarantee is bound to a checkable obligation, an enforcement
point in the pipeline (§4), and an evidence artifact. A guarantee with no
artifact is not granted.

| # | Guarantee | Operational obligation | Enforced at | Evidence artifact |
|---|---|---|---|---|
| G-1 | Determinism | `D` entails a *function* on `U`: one output per input; no randomness, model call, wall-clock, env, or mutable-store term may appear in `D` (T1 §8.3 vocabulary ban lifted into the definition language). | PO-DET (each object) | proof-pack entry + falsification probe class F-2 |
| G-2 | Reproducibility | The Unique Extension criterion (§3.1) holds: two independent readers of the frozen text compute identical outputs on every probe (§3.2). The *process* is also reproducible: every stage output is a written artifact re-runnable by a third party. | S4 audit | TRR trial record (L4) |
| G-3 | Minimality | Clause-deletion test (§3.6): every clause of `D` is load-bearing; every slot of `P` is necessary; nothing in the definition is decorative. | S3 + S4 | minimality record in `Π` |
| G-4 | Falsifiability | Acceptance is never "no counterexample found yet" by the author; it is survival of the independent adversarial protocol F-1…F-5 (§3, §5–§8 item 7), whose probe classes are preregistered before drafting (S0). Each definition states what observation would refute it (its POs are its refutation surface). | S0 + S4 | falsification verdict (L4) |
| G-5 | Ontology compatibility | The candidate is a well-formed ontology object (§1.2): right class, origin, owner, lifecycle, references same-or-earlier layer only, acyclic. | S2 gate + S6 | manifest check record |
| G-6 | Replay compatibility | The induced extension is a function of `(query_text, snapshot)` content only; invariant under everything byte-identical replay across the 22 seeds must ignore (T1 §7.2; addendum §A2). Order-stability obligations per object. | PO-REPLAY | proof-pack entry + F-2 probes |
| G-7 | Firewall compatibility | §0.3: no evaluation-side input to any stage; no component of `D` or of `P`'s admissible sets equals or is fitted to any EXP-1 probability, bin boundary, or ECE threshold. | every stage; re-checked at S4 | firewall check record (audit criteria 2–4 form) |
| G-8 | Implementation independence | `D` is stated over frozen *types*, never over code: no reference to any module, function, file, or interim default (the `claim_extraction.py` defaults are explicitly non-evidence, per REGISTER_AUDIT 5.6). Conformance of any future implementation is decidable by hand-evaluating `D` on probes, without running `program_a/`. | S2 gate + S4 | implementation-independence check in `Π` |
| G-9 | Governance independence | Acceptance is a *function of the recorded evidence*, not of role occupancy: any third party can recompute the accept/reject verdict from the artifacts alone (§11.3). No role may accept by fiat, waive a PO, or proxy another role's record (T1 §12 no-proxy, generalized). | S6 | adjudication record listing artifact-by-artifact satisfaction |

---

## 3. Core instruments (common to all four objects)

### 3.1 UE — the Unique Extension criterion (acceptance semantics)

> A definition candidate is **complete** iff, for every element of its
> declared universe `U`, the frozen text of `D` (plus the frozen types and any
> frozen L1 objects it lawfully references) entails **exactly one** output,
> derivable by a competent reader **with zero discretion**.

UE is the level-independent replacement for the selector program. The v1→v2
regress descended level by level (value → function → predicate →
parameterisation) because each fix quantified at one level. UE quantifies over
*readings*: if any two type-conformant readings of the text disagree anywhere
on `U`, the candidate is incomplete — at whatever level the disagreement
lives, including levels no axis list anticipated. UE is what makes the
axis enumeration (§3.3) safe to use without a completeness proof for the
enumeration itself.

### 3.2 TRR — the Two-Reader Reproducibility protocol (UE's operational test)

UE is tested, not assumed:

1. **Readers.** Two evaluators, each independent of the author and of each
   other (no shared drafts, no communication during the trial). Role
   occupancy is irrelevant; independence of *person and channel* is what is
   recorded.
2. **Inputs.** Each reader receives only: the frozen candidate text
   (`U, D, P, X`), the frozen types, and the probe battery — never the proof
   pack, never the author's intent, never each other's answers.
3. **Probes.** The battery (§3.7) is a set of concrete well-typed inputs;
   for each, the reader computes the output `D` entails (or writes
   `UNDERDETERMINED` with the ambiguous term named).
4. **Verdict.** Any divergence between readers, or any `UNDERDETERMINED`,
   **falsifies the candidate** and localizes the undefined term. Agreement on
   the full battery is necessary-but-not-sufficient evidence for UE
   (it feeds S4; it does not by itself accept — §10).

TRR is the direct scientific descendant of the audits' strongest instrument
(audit 1 §2: "independent from-scratch derivation attempt fails identically").
It converts "is the semantics defined?" from a debate into an experiment.

### 3.3 AXC — axis closure

The audits empirically exposed the ambiguity surface of these four objects:
**scope, quantifier, normalization, granularity, span, discourse level,
composition, corpus of quantification** (RCA §6), plus object-specific axes
(identity/individuation, order structure, positive-firing conditions). §5–§8
item 1 instantiates these as per-object question sets. AXC requires the
axis-closure table `X` to answer **every** listed question by citation into
`D` or `P`. AXC is deliberately *not* claimed complete; the open-ended residue
is caught by UE/TRR, which quantify over all readings. (Honest limitation
recorded in §12.)

### 3.4 TSC — two-sidedness

`D` must contain, for each behavior it defines, at least one **positive
entailment clause** (a condition under which the predicate fires / the
extractor emits / the skeleton takes a required form) and at least one
**negative entailment clause**. A candidate whose content is prohibitions
only is rejected *structurally*, before falsification (this excludes the
degenerate-infimum family v1-a/v1-b by construction, and the degenerate
supremum — e.g. an always-true relation — symmetrically).

### 3.5 UHO — the uniqueness handoff obligation (definition ⇄ parameter boundary)

The boundary rule that repairs `C` permanently:

> **A content item belongs to `D` iff varying it varies the extension over
> `U` in a way the mechanism's consumers can distinguish. A content item may
> be left to `P` only if `D` makes its admissible set (a) individuated —
> distinct members provably differ, (b) two-sided — degenerate members
> excluded by positive clauses, and (c) *dischargeable* — equipped with a
> declared selection ground of class E-STRUCT or E-PRIOR (derivation-method
> §2.2 classes) that the E4b author can execute to a unique value.**

Two lawful discharge modes for each slot of `P`:

- **(UHO-a) Singleton:** `D` entails exactly one admissible value; the L2
  step is transcription-shaped (the `EVIDENCE_ORDERING_KEY` pattern).
- **(UHO-b) Inert residual + convention ground:** `D` proves that all
  admissible values are **extensionally equivalent for every consumer and
  every proof obligation** (the residual freedom is semantically inert), and
  names an identity-convention selection ground (E-PRIOR class, the
  `SPEC_VERSION` pattern) by which E4b pins one. This is the anticipated mode
  for exact template wording, where many strings can satisfy a fully-fixed
  skeleton semantics — *whether that is so is for the definition to prove,
  not for this document to assert.*

A slot satisfying neither mode means the definition has smuggled semantics
into the value layer — the exact root-cause defect — and the candidate is
**rejected** (§10, R-4). UHO is also the discharge of the derivation method's
recorded insufficiency: post-freeze, its §2.2 "no value-selecting class"
gap is closed *by construction*, because every surviving L2 freedom carries
its selecting argument form.

### 3.6 MIN — the clause-deletion minimality test

For every clause `c` of `D` (and every slot of `P`), the proof pack must
exhibit either (i) a proof obligation that fails without `c`, or (ii) a
concrete candidate reading admitted by `D − {c}` that reopens an axis row or
violates a PO. A clause with neither is unnecessary content and must be
removed before submission; a definition is **minimal** when every clause has
its witness. Minimality is verified independently at S4 (the auditor attempts
to delete clauses and finds every deletion punished).

### 3.7 W — the witness/probe universe

All falsification and TRR trials run over a **declared probe universe**:

- **Composition.** Synthetic, well-typed inputs only (documents over the
  frozen 3-field schema, claims over the frozen `CandidateClaim` shape,
  `EvidenceStateResult` values over frozen fields), constructed a priori.
- **Firewall.** No EXP-1 item, frozen row, rubric, family, or
  adjudicator-derived text may seed a probe.
- **Sequencing (anti-teaching-to-the-test).** A **preregistered core battery**
  is authored at S0 by the auditor side (not the definition author) from the
  question sets of §5–§8 and the CE catalogue *before drafting begins*; an
  **adversarial extension** is authored at S4 after reading the candidate.
  The author never sees the core battery before submission; the auditor may
  extend without limit.
- **Role.** Probes are falsifying/discriminating instruments only. They may
  never *select* semantic content by observed niceness of outcome — the B-11
  discipline (T1 §10.2) lifted from values to definitions.
- **Joint witnesses.** W includes composed-pipeline witnesses for the §9
  joint obligations (inputs designed to traverse extraction → support →
  materiality → template jointly), because CE-10/CE-11/CE-13 proved
  per-object probing insufficient.

---

## 4. The authoring pipeline (stages, actors, artifacts, gates)

| Stage | Name | Actor | Output artifact (class, layer) | Gate to next stage |
|---|---|---|---|---|
| **S0** | Preregistration | Auditor side authors probes; Architect registers question sets | Instantiated per-object question sets (this document's §5–§8, checked complete against the CE catalogue); core probe battery; joint witness set; all recorded before drafting (L4-planned VerificationArtifacts + L0 registrations) | Question sets and battery recorded and hash-identified |
| **S1** | Drafting | Architect (definition author) | Candidate `(U, D, P, X)` per object — drafted L1 object | Structural well-formedness: five parts present; TSC holds; ontology manifest valid (G-5); no forbidden vocabulary (G-1, G-7, G-8) |
| **S2** | Self-consistency proof pack | Architect | `Π`: written discharge of every PO, each citing allowed evidence only; minimality record (§3.6) | Every PO has a written discharge; every axis row cited |
| **S3** | Independent falsification | Independent auditor(s) ≠ author | F-1…F-5 execution records; TRR trial record; adversarial probe extension; verdict per object (L4 VerificationArtifact) | Verdict `NO-COUNTEREXAMPLE` on all five instruments |
| **S4** | Cross-object round | Independent auditor(s), all four candidates jointly | J-1…J-7 execution records (§9); joint TRR on composed witnesses (L4) | All joint obligations pass; runs **only after** all four pass S3 individually |
| **S5** | Adjudication | ScientificAuditor (approver of scientific/freeze-relevant L1, per authority matrix) | Acceptance/rejection record mapping each §10 criterion to its evidence artifact (L5 GovernanceArtifact, identity-only references) | Acceptance = every criterion satisfied by a named artifact; anything else = rejection with cause |
| **S6** | Freeze | Architect freeze at stated freeze point; recorded per ontology §5 | Frozen `SEM-*` identity; E4a complete; `Parameter[SEM-*]` becomes inhabitable and E4b (derivation method) may begin | Ontology freeze rules; no governance performed by this document |

**Role discipline.** Author ≠ falsifier ≠ approver, with no channel between
author and probe authorship (S0) or falsification (S3). Any breach voids the
affected stage's artifacts (not the candidate's text) and the stage re-runs
with clean roles. A rejected candidate returns to S1 as a **new revision**
(ontology: post-approval change is a new object, never mutation); its
falsification record is retained permanently (the Finding-1/-2 lesson:
falsified attempts are history, not authority).

**Determinism of the process itself.** Every stage consumes and produces only
written, hash-identifiable artifacts; re-running any stage from its recorded
inputs must reproduce its verdict. No stage may cite an unrecorded
conversation, judgment call, or authority.

---

## 5. `SEM-SUPPORT` — authoring protocol

*Slot: extensional semantics of `supports(claim, evidence)`
(SemanticPredicate). Instantiated later by `SUPPORT_TEST_PARAMS` (T1 §5.3).
Fixed context consumed: T1 §3.1 (S0 row), §5.3 role, addendum §A1/§A4,
CF-R2.*

### 5.1 Required scientific questions (all must be answered by `X` citing `D`/`P`)

| Id | Question (provenance) |
|---|---|
| SQ-SUP-1 | Over exactly which universe is `supports` total — which set of well-typed `(claim, evidence)` inputs, and is the second argument an evidence *item* or an evidence *set*? (CE-4, scope) |
| SQ-SUP-2 | What is "an entity of the claim": how are a claim's entities individuated, enumerated, and typed — and is this notion defined here or imported from `SEM-EXTRACTION`? (v1-a; J-1) |
| SQ-SUP-3 | Which of the claim's entities must stand in the required relation to the evidence — what is the quantifier? (CE-5) |
| SQ-SUP-4 | What is the matching relation between an entity and evidence content — what normalization/equivalence (case, Unicode form, whitespace, tokenization) does it use, and is it decidable? (CE-6) |
| SQ-SUP-5 | Over which evidence fields does matching range (`origin_domain`, `title`, `text` — which, and why those)? (E-TYPE) |
| SQ-SUP-6 | Does support require anything beyond entity presence (relational/assertive content of the evidence), and if so, what — stated as a decidable condition? |
| SQ-SUP-7 | What positively forces `supports = true` — the exhibited class of inputs on which the predicate must fire? (TSC; excludes v1-a) |
| SQ-SUP-8 | What positively forces `supports = false` — including the fabricated-entity class (CF-R2) and the topically-related-but-non-supporting class (S0 row)? |
| SQ-SUP-9 | How is the extension invariant under evidence-set order, so that `ios(c)` and the §A1 selection consume a well-defined quantity? (G-6) |
| SQ-SUP-10 | Which degrees of freedom, if any, are deliberately left to `SUPPORT_TEST_PARAMS`, and under which UHO mode is each dischargeable? (§3.5) |

### 5.2 Allowed evidence

E-STRUCT, E-TYPE, E-PRIOR, E-DETERM arguments (derivation-method §2.2 classes,
lifted to definitional use) grounded **only** in: T1 §3.1/§3.3/§4/§5.3, addendum
§A0–§A7, the frozen types, ONT-1, and the CE catalogue *as constraint
provenance* (a CE may motivate an obligation; it may not smuggle content).
E-DEV synthetic mechanics results: falsifying/discriminating only, within
B-11 limits.

### 5.3 Forbidden evidence

Any EXP-1 outcome, probability, bin boundary, ECE artifact, frozen row,
rubric, family, adjudicator signal; any corpus statistic used to *select*
semantic content; any observed-score preference among candidate meanings; any
implementation default or behavior of existing code; any unrecorded expert
intuition ("it obviously means…") — intuition must be converted into a cited
E-STRUCT/E-PRIOR argument or discarded.

### 5.4 Proof obligations (`Π` must discharge all, in writing)

| Id | Obligation |
|---|---|
| PO-SUP-1 (TOTAL) | `D` entails an output for every element of `U`, including empty, junk, and near-miss inputs from the never-fail retriever. |
| PO-SUP-2 (DET) | The output is a function of the input content alone (G-1). |
| PO-SUP-3 (UE) | Unique extension: no two type-conformant readings of `D` disagree on any input (argued in `Π`; tested by TRR). |
| PO-SUP-4 (POS/NEG) | The SQ-SUP-7 and SQ-SUP-8 witness classes are exhibited and provably classified — always-false and always-true relations are excluded *by `D`*, not by audit vigilance. |
| PO-SUP-5 (CF-R2) | A claim containing an entity absent from all evidence gains no support — proved from `D`, converting CF-R2 from residual risk into entailed property. |
| PO-SUP-6 (S0-BOUND) | The S0 boundary sits exactly where T1 §3.1 places it: `D` neither widens nor narrows "no support anywhere ⇒ S0". |
| PO-SUP-7 (IOS) | `ios(c)` is well-defined over `D`'s extension and consumable by §A1/§A3 unchanged. |
| PO-SUP-8 (ORDER) | Extension invariant under evidence permutation; stability under the frozen `EVIDENCE_ORDERING_KEY` (G-6). |
| PO-SUP-9 (FIRE) | No clause of `D`, and no admissible set of `P`, contains or is fitted to an evaluation-side quantity (G-7). |
| PO-SUP-10 (UHO) | Every slot of `P` satisfies UHO-a or UHO-b (§3.5). |

### 5.5 Boundary conditions

`D` must not: alter the `supports` signature or the S0–S3 definitions,
precedence, or tier coupling; absorb or re-implement `is_material`,
`contradicts`, or extraction semantics; read beyond the 3-field document
schema and frozen claim types; reference any L2/L3/L4/L5 object as authority.
It must be expressible and hand-evaluable without any implementation (G-8).

### 5.6 Minimality criteria

§3.6 applied clause-by-clause; additionally, `P` is minimal: a slot whose
admissible set `D` could collapse to a singleton by an already-available
E-STRUCT argument must be so collapsed (freedom is never left open as a
courtesy).

### 5.7 Independent falsification protocol

The auditor executes, over the S0 core battery plus an adversarial extension:
**F-1 extensional-ambiguity search** — attempt to construct two distinct
type-conformant relations both satisfying `D` verbatim (the CE-4/5/6 move,
re-aimed at the new text); **F-2 degeneracy/determinism search** — attempt to
exhibit an admissible degenerate, non-total, or input-external-dependent
member; **F-3 axis descent** — attempt to find ambiguity one level below `P`
(the parameterisation-of-the-parameterisation move that killed v2);
**F-4 TRR trial** (§3.2); **F-5 structural check** — TSC, MIN, boundary and
firewall conformance. Any success on F-1–F-3, any F-4 divergence, or any F-5
violation ⇒ FAIL with the counterexample recorded as an L4 artifact.

### 5.8 Cross-object consistency hooks (consumed by §9)

Shared entity notion and normalization with `SEM-EXTRACTION` (J-1, J-2);
coherence of `supporting_doc_ids` with `supports` (J-5); joint reachability
contribution (J-3); claim-identity stability dependency (J-4).

### 5.9 Acceptance criteria

All of: five-part deliverable well-formed; `X` complete over SQ-SUP-1…10;
PO-SUP-1…10 discharged in `Π` from allowed evidence only; S3 verdict
NO-COUNTEREXAMPLE on F-1…F-5; S4 joint round passed; adjudication record maps
every criterion to its artifact. Only then freeze-eligible.

### 5.10 Rejection criteria

Any one of: an unanswered SQ row; an undischarged or evidence-violating PO;
any F-1…F-3 counterexample; any TRR divergence or `UNDERDETERMINED`; TSC
failure (prohibition-only content); a `P` slot failing UHO; any boundary
breach (would-be ES-1/PA-3 edit); any forbidden-evidence citation; any
role-separation breach in the record (voids stage, forces re-run); any clause
failing MIN left unresolved. Rejection is recorded with cause; the candidate
returns to S1 as a new revision.

---

## 6. `SEM-MATERIALITY` — authoring protocol

*Slot: extensional semantics of `is_material` (SemanticPredicate).
Instantiated later by `CONTRADICTION_MATERIALITY_PARAMS` (T1 §5.4). Fixed
context: addendum §A4 (S1 composition), §A5 (contract + precondition), §A6
(`contradicts` distinct).*

### 6.1 Required scientific questions

| Id | Question (provenance) |
|---|---|
| SQ-MAT-1 | Over exactly which universe is `is_material` defined — confirmed as the `contradicts`-true pairs per §A5, with behavior elsewhere stated (defined `False`), and over which representation of the pair does it operate? |
| SQ-MAT-2 | What is the extensional meaning of "substantively incompatible" — the decidable condition separating material from immaterial, stated positively? (CE-12: "genuine incompatibility is undefined") |
| SQ-MAT-3 | Which dimensions of inter-claim variation are classified immaterial, by what decidable test — and is that class closed under the normalization of SQ-MAT-6? |
| SQ-MAT-4 | What is the order structure of the admissible boundary family — is it a lattice; is the frozen boundary unique; if a family survives into `P`, over what individuated set? (CE-12: ⊆-incomparable boundaries) |
| SQ-MAT-5 | Is `is_material` symmetric, and how does that cohere with S1's unordered-pair composition (§A4)? |
| SQ-MAT-6 | What normalization does the materiality test use, and is it the same object as SQ-SUP-4 / SQ-EXT-6 or explicitly related? (J-2) |
| SQ-MAT-7 | What class of pairs is `contradicts`-true ∧ immaterial — exhibited, so that `is_material` provably does not collapse into `contradicts`? (§A6 distinctness) |
| SQ-MAT-8 | What positively forces `is_material = true` — the exhibited material class? (TSC) |
| SQ-MAT-9 | Which degrees of freedom are left to `CONTRADICTION_MATERIALITY_PARAMS`, under which UHO mode? |

### 6.2 Allowed evidence — as §5.2, with primary grounding in addendum §A4/§A5/§A6 and T1 §5.4.

### 6.3 Forbidden evidence — as §5.3; additionally, no appeal to runtime judgment ("a human would know") — the placeholder's runtime-judgment freedom is precisely what the definition exists to close (audit criterion 5).

### 6.4 Proof obligations

| Id | Obligation |
|---|---|
| PO-MAT-1 (PRECOND) | Defined and consulted only on `contradicts`-true pairs; defined `False` elsewhere; never a standalone similarity test (§A5). |
| PO-MAT-2 (DET/TOTAL) | Deterministic and total over the declared universe. |
| PO-MAT-3 (UE) | Unique extension (argued; TRR-tested). |
| PO-MAT-4 (SYM) | Symmetry (or its stated, S1-coherent alternative) proved compatible with §A4's unordered composition. |
| PO-MAT-5 (POS/NEG) | Both witness classes exhibited: material pairs and immaterial-though-contradicting pairs — degenerate all-material and all-immaterial boundaries excluded by `D`. |
| PO-MAT-6 (DISTINCT) | `is_material` provably does not re-implement or collapse `contradicts` (§A6). |
| PO-MAT-7 (S1) | The S1 firing predicate (§A4 conds 1–3) keeps its meaning; exactly-one-state and the §A0 exhaustiveness repair are preserved; `Comp`/`Part` anchoring totality remains well-defined. |
| PO-MAT-8 (ORDER-STRUCT) | The SQ-MAT-4 answer is proved: whatever order structure `D` claims for the admissible family is demonstrated, so no later "⊆-least denotes an antichain" surprise survives. |
| PO-MAT-9 (FIRE) | Firewall-clean (G-7). |
| PO-MAT-10 (UHO) | Every `P` slot dischargeable (§3.5). |

### 6.5 Boundary conditions — must not alter `contradicts`, §A4 composition, §A5 contract, exactly-one-state, or any state definition; expressible over frozen claim types only; hand-evaluable (G-8).

### 6.6 Minimality — §3.6; additionally, `D` may not enumerate immaterial-variation dimensions beyond those needed to discharge PO-MAT-5/PO-MAT-8 (no speculative taxonomy).

### 6.7 Falsification protocol — F-1…F-5 as §5.7, with the adversarial emphasis on: constructing two ⊆-incomparable boundaries both satisfying `D` (the CE-12 replay); constructing a pair classified differently by the two readers (TRR); and probing the `contradicts`/`is_material` seam for collapse or gap.

### 6.8 Cross-object hooks — J-2 (shared normalization), J-3 (S1 reachability requires composed extraction+support+materiality witnesses), J-6 (definitional dependency on the claim notion is declared and acyclic).

### 6.9 / 6.10 Acceptance / rejection — the §5.9/§5.10 schema applied to SQ-MAT-* and PO-MAT-*.

---

## 7. `SEM-EXTRACTION` — authoring protocol

*Slot: extensional semantics of the candidate-claim boundary
(SemanticPredicate over PA-2's input space). Instantiated later by
`EXTRACTION_PARAMS` (T1 §5.6). Fixed context: T1 §5.6 (pure text mechanics,
no model calls), addendum §A2 (tie-break, injectivity), frozen
`CandidateClaim` types, CF-R2 first line.*

### 7.1 Required scientific questions

| Id | Question (provenance) |
|---|---|
| SQ-EXT-1 | Over exactly which universe is extraction defined — `(query_text, snapshot)` with the 3-field document schema — and what is its output type, confirmed as the frozen ordered tuple? |
| SQ-EXT-2 | What is the candidate-claim boundary's granularity — at what textual unit do candidates individuate? (CE-7: sentence vs clause) |
| SQ-EXT-3 | What is the span rule — which extent of the unit becomes `claim_text`? (CE-8: maximal vs minimal span) |
| SQ-EXT-4 | What is claim identity — when are two extracted candidates *the same claim*, within one run and across replays — and how does that identity semantics keep `ios` well-defined and S3 reachable in principle? (CE-13) |
| SQ-EXT-5 | What positively forces a non-empty output — the exhibited input class on which extraction must emit? (v1-b; TSC) |
| SQ-EXT-6 | How is `claim_text` constructed — under what normalization — such that the §A2 tertiary key (Unicode code-point order over its UTF-8/NFC form) is a valid total-order tie-breaker? |
| SQ-EXT-7 | What guarantees `claim_text` distinctness for distinct claims — discharging or explicitly leaving open the §A2 injectivity CONDITIONAL (F2/F2′), stated either way? |
| SQ-EXT-8 | What determines tuple order — from input content alone? (§A2 refuses replay-coupling to tuple position; the definition must still fix the order deterministically) |
| SQ-EXT-9 | What is the entity notion anchoring extraction ("entity-level, no model calls"), and is it the single-sourced notion shared with `SEM-SUPPORT`? (J-1) |
| SQ-EXT-10 | What is the semantics of `supporting_doc_ids` on emission — which documents count, and how does that cohere with `supports`? (J-5) |
| SQ-EXT-11 | Which degrees of freedom are left to `EXTRACTION_PARAMS`, under which UHO mode? |

### 7.2 Allowed evidence — as §5.2, primary grounding T1 §5.6, addendum §A2, frozen types; E-DETERM is expected to be load-bearing (extraction feeds `ios`, `≺`, S1).

### 7.3 Forbidden evidence — as §5.3; **explicitly**: the interim `claim_extraction.py` behavior is not evidence of any kind (REGISTER_AUDIT 5.6); no model-call or corpus-frequency argument may select granularity or span.

### 7.4 Proof obligations

| Id | Obligation |
|---|---|
| PO-EXT-1 (TOTAL) | Defined for every input, including empty/junk documents and empty snapshots. |
| PO-EXT-2 (DET) | Pure text mechanics: no model call, randomness, wall-clock; output a function of input content (G-1). |
| PO-EXT-3 (UE) | Unique extension (argued; TRR-tested — two readers extract identical ordered tuples on every probe). |
| PO-EXT-4 (POS/NEG) | Non-empty witness class exhibited (SQ-EXT-5) and fabricated-entity inputs provably yield no claim (CF-R2 first line) — always-empty and indiscriminate extractors both excluded by `D`. |
| PO-EXT-5 (TYPE) | Output conforms to the frozen `CandidateClaims` ordered-tuple shape with `{claim_text, supporting_doc_ids}`. |
| PO-EXT-6 (INJ) | The SQ-EXT-7 answer is proved: either §A2 injectivity is entailed, or the residual CONDITIONAL is explicitly declared with its closure obligation assigned (never silently inherited). |
| PO-EXT-7 (IDENT) | Claim identity (SQ-EXT-4) is proved stable under replay and under evidence-order permutation, so `ios` and the §A2 keys consume well-defined objects, and no `Σ≠∅`-but-S3-unreachable pathology (CE-13) is admissible. |
| PO-EXT-8 (ORDER) | Tuple order deterministic from content (SQ-EXT-8). |
| PO-EXT-9 (FIRE) | Firewall-clean (G-7). |
| PO-EXT-10 (UHO) | Every `P` slot dischargeable (§3.5). |

### 7.5 Boundary conditions — must not alter the PA-2 contract (no-model-call, entity-level, ordered tuple), the frozen types, the §A2 keys, or any downstream rule; reads only `query_text` + 3-field documents; hand-evaluable (G-8).

### 7.6 Minimality — §3.6; the boundary/span/identity clauses may fix no more than the POs require (e.g. no typographic micro-rules without a PO witness).

### 7.7 Falsification protocol — F-1…F-5 as §5.7, adversarial emphasis: two readings differing in granularity or span on the same probe (CE-7/CE-8 replay); a `D`-conformant extractor breaking §A2 injectivity or claim-identity stability (CE-13 replay); an order ambiguity across readers.

### 7.8 Cross-object hooks — J-1 (entity notion source), J-2 (normalization), J-3 (joint reachability: extraction must emit what support can support), J-4 (identity stability is the load-bearing input to composed reachability), J-5 (`supporting_doc_ids`/`supports` coherence).

### 7.9 / 7.10 Acceptance / rejection — the §5.9/§5.10 schema applied to SQ-EXT-* and PO-EXT-*.

---

## 8. `SEM-TEMPLATE` — authoring protocol

*Slot: per-state answer-skeleton semantics (SemanticTemplate). Instantiated
later by `ANSWER_TEMPLATES` (T1 §5.7). Fixed context: T1 §3.1 answer column,
§8 (CR-3), addendum §A7 I-2/I-3, FM-1.*

### 8.1 Required scientific questions

| Id | Question (provenance) |
|---|---|
| SQ-TPL-1 | Over exactly which universe is the template semantics defined — `{S0,S1,S2,S3} × EvidenceStateResult` — and what is the output type (a byte string)? |
| SQ-TPL-2 | What is a *skeleton* — the formal object (fixed-text regions + typed slot regions + their order/discourse structure) that individuates templates — such that "two S0 realisation functions with no discriminator" (v1-c) cannot recur? |
| SQ-TPL-3 | What are the slot inventory and binding rules — which `EvidenceStateResult` fields may bind which slots, with what deterministic rendering for each field type (including collection-valued fields such as doc-id sets)? (§A7 I-3) |
| SQ-TPL-4 | What is the decidable **assertion criterion** — the test by which a rendered string does or does not "assert a fact" — required before S0/S1 no-assertion can be *proved* rather than eyeballed? |
| SQ-TPL-5 | What is the decidable hedged-vs-asserted distinction separating the S2 form from the S3 form? |
| SQ-TPL-6 | What is the S1 discourse-structure semantics of "represents both alternatives" — order, framing, and attribution of the alternatives — at the level CE-9 exhibited as undefined? |
| SQ-TPL-7 | What is the attribution form for S2/S3 (and for S1's alternatives) — what counts as "source-attributed," bound to which fields? |
| SQ-TPL-8 | Which lexical classes are excluded from any template (e.g. probability/quantifier language per the REGISTER_AUDIT 5.7 G4 screen), by what decidable test? |
| SQ-TPL-9 | Where exactly does the frozen layer end — which properties are mechanism-defining versus "rendering niceties above the frozen templates" (§A6-DIGEST) — stated as a boundary inside the definition? |
| SQ-TPL-10 | What residual freedom (exact wording) is left to `ANSWER_TEMPLATES`, and how is it proved **extensionally inert** and pinned by an identity-convention ground (UHO-b), or else collapsed (UHO-a)? |

### 8.2 Allowed evidence — as §5.2, primary grounding T1 §3.1/§5.7/§8, addendum §A7; E-PRIOR (the frozen per-state answer-construction commitments) is expected to be primary.

### 8.3 Forbidden evidence — as §5.3; additionally, no rubric-derived or family-derived wording input of any kind (CR-3 is an input restriction on the *definition process* too), and no aesthetic preference among wordings presented as if it were evidence — wording preferences live only inside a UHO-b convention ground.

### 8.4 Proof obligations

| Id | Obligation |
|---|---|
| PO-TPL-1 (TOTAL) | One skeleton per state, total over the universe, including degenerate `EvidenceStateResult` values. |
| PO-TPL-2 (DET) | Byte-determinism: given `(state, result)`, `D` entails exactly one output string (G-1/G-6). |
| PO-TPL-3 (UE) | Unique skeleton reading (argued; TRR-tested — two readers produce byte-identical renderings on every probe). |
| PO-TPL-4 (NO-ASSERT) | Under the SQ-TPL-4 criterion, the S0 and S1 skeletons provably assert no fact, for **all** slot bindings, making assertion structurally impossible outside `{S2,S3}` (FM-1, §A7 I-2). |
| PO-TPL-5 (ASSERT/HEDGE) | The S3 skeleton asserts and the S2 skeleton hedges under the SQ-TPL-5 criterion; both are source-attributed under SQ-TPL-7. |
| PO-TPL-6 (ALTERNATIVES) | The S1 skeleton represents both alternatives with attribution while asserting neither, under the SQ-TPL-6 discourse semantics — proved, not asserted. |
| PO-TPL-7 (CR-3) | Every slot binds only permitted `EvidenceStateResult` fields (+ `query.query` echo where licensed); output provably invariant under rubric/family/metadata sentinel substitution (C1 satisfiability preserved). |
| PO-TPL-8 (LEX) | The SQ-TPL-8 exclusion test is decidable and the skeletons' fixed regions pass it. |
| PO-TPL-9 (FIRE) | Firewall-clean; no template component encodes an evaluation-side quantity (G-7). |
| PO-TPL-10 (UHO) | The SQ-TPL-10 residual is proved inert and convention-pinned (UHO-b) or collapsed (UHO-a); any wording freedom that is *not* provably inert is semantic content and must move into `D`. |

### 8.5 Boundary conditions — must not alter any state's answer-construction rule (T1 §3.1), the §A7 I-2 gate, `EvidenceStateResult`, or the tier coupling; fixes exactly the frozen layer and no more (SQ-TPL-9); hand-evaluable (G-8).

### 8.6 Minimality — §3.6; fixed-text regions contain nothing not required by a PO (no ornamental prose inside the frozen layer).

### 8.7 Falsification protocol — F-1…F-5 as §5.7, adversarial emphasis: constructing two `D`-conformant skeletons for one state differing in discourse structure (CE-9/v1-c replay); constructing a slot binding under which an S0/S1 rendering asserts a fact under the SQ-TPL-4 criterion; sentinel-substitution divergence; a wording pair in the declared-inert residual that consumers can in fact distinguish (UHO-b refutation).

### 8.8 Cross-object hooks — J-3 (each state's skeleton must be reachable jointly: a state no composed input can produce makes its template untestable — flagged at the joint round); J-6 (template semantics consumes claim/attribution notions only via `EvidenceStateResult`, never directly from extraction/support internals).

### 8.9 / 8.10 Acceptance / rejection — the §5.9/§5.10 schema applied to SQ-TPL-* and PO-TPL-*.

---

## 9. Cross-object consistency protocol (the joint round, S4)

Run only after all four candidates individually pass S3. CE-10, CE-11, and
CE-13 proved that per-object soundness does not compose; this round owns the
composition.

| Id | Joint obligation | Refutation form |
|---|---|---|
| J-1 | **Single-sourced shared terms.** Every term used by more than one definition (entity, claim, normalization form, attribution unit, …) is defined in exactly one of the four (or in an existing frozen L1 object) and imported by reference. A shared-term registry is produced listing each term, its owner definition, and its importers. | The same term defined in two places, or defined nowhere, or imported with drift. |
| J-2 | **Normalization coherence.** The matching/normalization relations of SQ-SUP-4, SQ-MAT-6, SQ-EXT-6 are the same object or their differences are explicitly stated and proved harmless to every PO that crosses objects. | Two readers derive different cross-object behavior from normalization mismatch. |
| J-3 | **Joint reachability.** Over the declared witness universe `W` (§3.7 — synthetic, a-priori, firewall-clean, with its quantification space stated: the CE-11 repair), each state S0, S1, S2, S3 is attained by the composed pipeline extraction → support → (contradicts∘materiality) → state → template, exhibited by concrete witnesses in the record. This excludes the CE-10 pathology (per-object non-degenerate, jointly S0-only) and the CE-13 pathology (S3 permanently unreachable). | Any state with no witness; or a witness that requires an input outside the declared universe. |
| J-4 | **Identity-stability composition.** The claim-identity semantics (SQ-EXT-4) provably makes `ios`, the §A2 tie-break, and §A1 selection well-defined end-to-end on `W`. | A composed probe where two readers individuate claims differently downstream. |
| J-5 | **`supporting_doc_ids` / `supports` coherence.** The emission-time semantics (SQ-EXT-10) and the predicate semantics (`SEM-SUPPORT`) are proved consistent (identical, or explicitly related with the relation proved harmless to S0/§A1/§A3 consumers). | A probe where the two notions disagree in a consumer-visible way. |
| J-6 | **Acyclic definitional DAG.** The four definitions' mutual references form a declared DAG (each import listed with direction); no cycle; no reference to any object later than L1. | Any cycle or upward reference. |
| J-7 | **Joint TRR.** The two-reader protocol re-run on composed witnesses: readers compute the full pipeline result (final state and rendered answer) independently; byte-level agreement required. | Any divergence anywhere in the composed trace. |

Failure of any joint obligation rejects **the specific candidate(s) whose
text the counterexample exploits** (localized by the auditor), returns them to
S1, and re-runs S4 in full after revision — joint verdicts are never patched
incrementally.

---

## 10. Adjudication: global acceptance and rejection

### 10.1 Acceptance (all conjuncts required; each maps to a named artifact)

| # | Criterion | Evidence artifact |
|---|---|---|
| A-1 | Five-part deliverable (`U, D, P, X, Π`) well-formed for each object | S1 structural-gate record |
| A-2 | Axis closure: every SQ row answered by citation | `X` tables |
| A-3 | Every PO discharged from allowed evidence only | `Π` proof packs |
| A-4 | Independent falsification NO-COUNTEREXAMPLE (F-1…F-5, incl. TRR) per object | S3 L4 verdicts |
| A-5 | Joint round J-1…J-7 passed | S4 L4 verdicts |
| A-6 | Minimality records complete (every clause witnessed) | MIN records in `Π`, checked at S3 |
| A-7 | UHO discharged for every `P` slot (post-freeze, the derivation method's §2.2 insufficiency is thereby closed: E4b has a selecting ground for every surviving freedom) | UHO table per object |
| A-8 | Ontology well-formedness and role/no-proxy discipline intact across all stages | manifests + stage records |
| A-9 | ScientificAuditor approval recorded, referencing artifacts A-1…A-8 by identity | S5 L5 record |

Upon A-1…A-9: the definitions are freeze-eligible at E4a. Freeze itself, E4b
value derivation, transcription, digest, and gate movement remain governed by
the existing documents and are **not performed or altered here**.

### 10.2 Rejection (any single disjunct suffices; recorded with cause)

R-1 any empty or evasive `X` row (an axis "answered" by restating the role or
by a prohibition is empty); R-2 any undischarged PO, or a PO discharged from
forbidden evidence; R-3 any F-1…F-3 counterexample, TRR divergence, or
`UNDERDETERMINED`; R-4 any `P` slot failing UHO (silent semantic freedom —
the root-cause defect re-presenting); R-5 any boundary breach: a candidate
that entails a change to any frozen T1/addendum/type content is rejected as a
definition and, if the author maintains the change is necessary, routed to
change control as a *separate* Wave-2 proposal — never absorbed; R-6 any
firewall contamination of any stage; R-7 any role or sequencing breach
(author-seen probes, author-run falsification, proxy approval) — voids the
stage record; R-8 TSC failure; R-9 unresolved MIN failure; R-10 joint-round
failure (per §9 localization). A rejected candidate's falsification record is
permanent history; the revision is a new L1 draft (ontology §5).

---

## 11. Auditability of the methodology itself

### 11.1 Requirement register

Every normative requirement of this methodology carries an identifier; an
audit of an E4a execution checks each row against its artifact. A row without
a checkable artifact would itself be a methodology defect.

| Id | Requirement | Checked by |
|---|---|---|
| SAM-R1 | Five-part deliverable form (§1.1) | inspection of the candidate |
| SAM-R2 | Question sets instantiated and probe battery preregistered before drafting (§3.7, S0) | timestamps/hashes of S0 artifacts vs S1 |
| SAM-R3 | Probe battery authored independently of the definition author (§3.7) | S0 role record |
| SAM-R4 | TSC: positive clauses present (§3.4) | S1 gate record |
| SAM-R5 | Axis closure per object (§5–§8 item 1) | `X` tables |
| SAM-R6 | Proof packs cite allowed evidence only (§5–§8 items 2–4) | `Π` citation check |
| SAM-R7 | Independent falsification executed in full (F-1…F-5) by non-authors (§5–§8 item 7) | S3 records |
| SAM-R8 | TRR run with reader independence (§3.2) | S3 trial record |
| SAM-R9 | Joint round executed only after four individual passes; J-1…J-7 complete (§9) | S4 records |
| SAM-R10 | MIN witnessed per clause (§3.6) | MIN records |
| SAM-R11 | UHO discharged per slot (§3.5) | UHO tables |
| SAM-R12 | Adjudication maps every criterion to an artifact; no fiat acceptance (§10.1) | S5 record |
| SAM-R13 | All stage artifacts hash-identified, re-runnable, and typed per ontology | repository inspection |
| SAM-R14 | No stage read any evaluation-side object (§0.3) | firewall check records |

### 11.2 The methodology's own falsification conditions (meta-falsifiability)

This methodology makes a refutable claim: **a definition accepted under
A-1…A-9 admits no extensional ambiguity, no degenerate member, and no
axis-descent counterexample.** It is therefore itself falsified if any of the
following is ever exhibited for an accepted definition:

- **MF-1** a post-acceptance two-reader divergence or `UNDERDETERMINED` on a
  well-typed input;
- **MF-2** a post-acceptance CE-style counterexample (two conformant readings;
  a degenerate admissible member; parameterisation-level ambiguity);
- **MF-3** a `P` slot whose E4b derivation stalls for want of a selecting
  ground despite a recorded UHO discharge;
- **MF-4** a joint pathology (CE-10/-11/-13 class) on inputs inside the
  declared universes.

Upon any MF event: the accepted definition's status reverts per ontology
change control (a new revision, never in-place edit), **and** this methodology
is defective and must be revised — the specific instrument that failed to
catch the counterexample is identified and strengthened — *before* any
re-authoring proceeds. The methodology may not be quietly bypassed after a
failure; that is the v1→v2 treadmill's governance signature, and it is
prohibited by construction.

### 11.3 Governance independence, mechanically

The accept/reject verdict is a computable function of the artifact set
(A-1…A-9 / R-1…R-10). Consequences: (i) any third party, holding only the
artifacts, can recompute the verdict — disagreement between the recomputation
and the recorded verdict is itself an MF-class event; (ii) no role can accept
without the artifacts existing, and no role can reject artifacts that satisfy
the criteria without recording the failing row; (iii) role substitutions
(different individuals occupying Architect/auditor/reader positions) cannot
change any verdict, because no criterion references a person — only
independence relations, which are recorded facts.

### 11.4 Change control for this document

`SAM-1` follows the ontology lifecycle: drafted → approved (Architect
ownership; ScientificAuditor approval as scientific/freeze-relevant) → frozen
before E4a consumes it. Any revision after approval is a new revision with a
recorded delta; an E4a execution cites the exact `SAM-1` revision it ran
under, so every acceptance is reproducible against a fixed methodology text.

---

## 12. Why this terminates the regress (argument and honest limits)

**The regress engine (RCA §3.2):** corrections confined to the selector layer
over prohibition-only, non-individuated candidate sets could only relocate
undefinedness one meta-level up per iteration.

**Removal of the engine, point by point:**

1. **The layer is now authored.** The deliverable *is* layer-4 content
   (`D` with positive clauses over a declared `U`), owned and scheduled — the
   `C` boundary no longer files it as a value (migration M5/M12 made the slot;
   this methodology fills it lawfully).
2. **Two-sidedness by construction (TSC)** deletes the degenerate-infimum
   family (v1-a/v1-b) structurally, before any audit.
3. **UE/TRR is level-independent.** Every prior falsification succeeded by
   descending to an unexamined level. TRR does not enumerate levels; it
   quantifies over *readings*. Any ambiguity at any depth — value, function,
   predicate, parameterisation, or deeper — surfaces as reader divergence on
   some probe. The acceptance semantics therefore has no "next level down"
   to flee to.
4. **UHO closes the boundary permanently.** Every degree of freedom is either
   inside `D` (defined), or in `P` with an individuated, two-sided, selection-
   grounded admissible set. "Undefined semantics filed as a deferred value"
   is no longer expressible in the deliverable format.
5. **Composition is owned (J-1…J-7).** The joint round is a first-class gate,
   so the CE-10/-11/-13 class — probes into the layer no per-register document
   owned — now has a named owner and a named verdict.

**Honest limitations (recorded, not hidden):**

- **AXC is not provably complete.** No enumeration of ambiguity axes can be
  known exhaustive a priori. The methodology therefore does *not* rest
  acceptance on AXC; AXC is a floor, and the load-bearing criterion is
  UE/TRR plus adversarial search — operational tests, not enumerations.
- **TRR is an experiment, not a proof.** Two readers agreeing on a finite
  battery is evidence, not entailment; that is why acceptance also requires
  the written UE argument in `Π` (PO-*-3) and unrestricted adversarial
  extension of the battery, and why §11.2 keeps the methodology itself
  falsifiable in perpetuity.
- **Independence is recorded, not metaphysical.** Reader/auditor independence
  is enforced as documented channel separation; a covert channel would weaken
  TRR. This is a known residual risk of any human-executed protocol and is
  mitigated by re-runnability (any later party can re-run TRR with fresh
  readers — MF-1 stays open forever).

---

## 13. References (read-only grounding; L0 provenance, no authority transfer)

- `PROGRAM_A_ARCHITECTURAL_ONTOLOGY.md` — ONT-1: classes, authority matrix,
  operations, type system, interaction matrix (consumed as fixed).
- `PROGRAM_A_ONTOLOGY_MIGRATION_PLAN.md` — SEM-* slot table; M5/M12/M17
  (E4a/E4b split); class/owner/approver assignments.
- `PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md` — verdict `C`; the
  eight ambiguity axes; the regress mechanism (provenance for §3.3, §12).
- `docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md`,
  `docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md` — v1-a…v1-c,
  CE-4…CE-13 (provenance for the SQ-*/F-*/J-* instruments).
- `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` — §2.2 evidence classes (lifted to
  definitional use), §7 grid, §8 freeze method; the E4b counterpart whose
  §2.2 insufficiency UHO renders dischargeable.
- `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3–§9,
  `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A0–§A7 — fixed semantic context the
  definitions must preserve, never alter.
- `PROGRAM_A_REGISTER_AUDIT.md` — 8-criterion grid; FAIL-deferred grounds.
- `PROGRAM_A_G4_EXECUTION_PLAN.md`, `ES1_IMPLEMENTATION_GATE.md` — the
  governance frame this methodology slots into without altering.

---

*End of semantic authoring methodology. This document defines HOW
`SEM-SUPPORT`, `SEM-MATERIALITY`, `SEM-EXTRACTION`, and `SEM-TEMPLATE` will be
scientifically authored, falsified, and accepted. It contains none of their
content: no semantics written, no value chosen, no part of ES-1 or PA-3
redesigned, no code implemented, no governance performed. The four slots
remain unauthored, `Parameter[SEM-*]` remains uninhabited, `CONSTANTS_HASH`
remains `None`, and the standing prohibition holds.*
