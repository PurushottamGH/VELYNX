# PROGRAM A — REGISTER DERIVATION ROOT-CAUSE ANALYSIS

**Title:** Why successive selector corrections for the four deferred ES-1
registers continue to fail — a root-cause analysis, not a correction.
**Objects analysed (the failure history, not re-adjudicated):**
`PROGRAM_A_REGISTER_DERIVATION_METHOD.md` ("the method"),
`PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` ("v1"),
`PROGRAM_A_REGISTER_DERIVATION_FINDING2.md` ("v2"),
`docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md` ("audit 1"),
`docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md` ("audit 2").
**Registers in scope:** `SUPPORT_TEST_PARAMS` (T1 §5.3),
`CONTRADICTION_MATERIALITY_PARAMS` (§5.4), `EXTRACTION_PARAMS` (§5.6),
`ANSWER_TEMPLATES` (§5.7).
**Posture.** This document performs **root-cause analysis only**. It proposes
**no correction**, writes **no Finding 3**, adds **no selector**, mints **no
constant**, and redesigns **no part of ES-1**. It names the single minimal
defect that explains every failed audit and stops there. The standing
prohibition (`ES1_IMPLEMENTATION_GATE.md`:97-99) is unchanged.
**Date:** 2026-07-14
**Status:** DIAGNOSIS. Binds no value, records no sign-off, pins no commit.

---

## 0. Verdict (one line, then the mapping)

> **The true defect is `C` — an incorrect abstraction boundary.** The method's
> boundary between "methodology (specifies procedure; contains no value)" and
> "canonical value (deferred to G4)" is drawn **through the middle of the
> register's semantic definition**, assigning that definition to the
> deferred-value side where no methodology-layer actor may write it. This
> **manifests as `B`** (the semantic definitions are missing) and is
> **persistently misdiagnosed as `A`** (a selector is missing). Because every
> correction so far has treated the defect as `A`, every correction has added a
> selector on top of an undefined set — and an audit has then exhibited a legal
> member of that undefined set which the selector cannot pin. `A` is not the
> defect; supplying `A` is *why the corrections fail*.

| Option | Verdict | Role in the failure |
|---|---|---|
| **A. Missing selector** | **Rejected as root — it is the misdiagnosis.** | Every correction (v1, v2) supplied selector machinery. Each was falsified. Adding `A` is the treadmill, not the exit. |
| **B. Missing semantic definitions** | **True, but downstream — this is the *manifestation*.** | Every single audit counterexample exploits an undefined semantic term. `B` is *what is missing*; it does not by itself explain why the gap *recurs under correction*. |
| **C. Incorrect abstraction boundary** | **ROOT CAUSE.** | The boundary files semantic content under "deferred value," which (i) starves the constraint layer to pure prohibitions and (ii) confines every correction to the selector layer. This is the smallest cause that explains *both* the individual failures *and* their recurrence. |
| **D. Missing scientific preregistration** | **Collapses into C.** | The apparatus *is* preregistered (T1). The defect is not absence of preregistration but that the preregistration drew its completeness boundary in the wrong place — i.e., `C`. |
| **E. Something else** | **Names the *mechanism* of C, not a separate cause.** | The "something else" worth naming is the **meta-level regress**: a selector presupposes a defined set, so a fix at the selector layer can only push the undefinedness up one level (value → function → predicate → predicate-parameterisation). The regress is how `C` produces repeated failure. |

---

## 1. The evidence: what the two audits actually falsified

Root-cause analysis begins from the invariant across the failures, not from any
one failure. Tabulating every falsified item from both audits:

| # | Audit item | Register | The thing the counterexample exploited |
|---|---|---|---|
| v1-a | always-`False` support is admissible | `SUPPORT_TEST_PARAMS` | "supports" is bounded only by *prohibitions*; no positive definition forces it to ever fire. |
| v1-b | always-empty extractor is admissible | `EXTRACTION_PARAMS` | "extract" is bounded only by prohibitions; nothing forces it to ever emit a claim. |
| v1-c | two S0 realisation functions, no discriminator | `ANSWER_TEMPLATES` | "the template" has no semantic content beyond "assert no fact"; multiplicity relocates value→function. |
| CE-4 | "the evidence text": item-scoped vs set-scoped | `SUPPORT_TEST_PARAMS` | the *scope* of the entity-presence predicate is undefined. |
| CE-5 | "the claim's entities": all / head / any | `SUPPORT_TEST_PARAMS` | the *quantifier* of the predicate is undefined. |
| CE-6 | exact vs NFC-normalised match | `SUPPORT_TEST_PARAMS` | the *normalisation* of the predicate is undefined. |
| CE-7 | sentence- vs clause-level boundary | `EXTRACTION_PARAMS` | the *granularity* of the candidate-boundary predicate is undefined. |
| CE-8 | maximal- vs minimal-span extraction | `EXTRACTION_PARAMS` | the *span rule* of the predicate is undefined. |
| CE-9 | two S1 skeletons differing in discourse framing | `ANSWER_TEMPLATES` | "represents both alternatives" is undefined at the discourse-structure level. |
| CE-10 | two per-register-non-degenerate registers compose to S0-only | support × extraction | the *joint* semantics of the composed mechanism is owned by no layer. |
| CE-11 | CSP-c witness exists abstractly but never on the frozen corpus | all parametric | "reachable" is undefined over *which input space*. |
| CE-12 | two floor-respecting, ⊆-incomparable materiality boundaries | `CONTRADICTION_MATERIALITY_PARAMS` | "genuine incompatibility" is undefined; the admissible family may not even be a lattice. |
| CE-13 | `Σ≠∅` extractor that permanently forbids S3 | `EXTRACTION_PARAMS` | the semantics linking extraction to *claim-identity stability* (hence `ios`) is undefined. |

**The invariant.** Every falsified item — without exception — is a legal,
deterministic, firewall-clean, type-conformant candidate that the correction
cannot exclude or cannot uniquely pin, **because some term in the register's own
definition carries no specified meaning.** Not one counterexample turns on
determinism, replay, the digest, or a genuine ES-1/PA-3 contract edit. They all
turn on the same thing: an *undefined semantic*.

That is the fact any root cause must explain. `B` (missing semantic
definitions) names it. The remaining sections show why `B` is the
*manifestation* of `C`, and why `A` is a misdiagnosis.

---

## 2. The confirming asymmetry — why five registers passed and four did not

The method (§1) and audit 1 (§1) both note that five sibling registers are
audited **PASS** while these four are **FAIL (deferred)**. The passing set is
the control group, and it isolates the variable exactly.

Read the T1 §5 register's own "canonical value" column:

- **§5.5 `EVIDENCE_ORDERING_KEY` (PASS):** value column gives the **semantics
  inline** — *"lexicographic on `(origin_domain, doc_id)`."* A concrete
  extensional definition. The set of admissible values is a **singleton by
  construction**, so no selector is needed and none is missing.
- **§5.1 `MIN_INDEPENDENT_ORIGINS_FOR_S3` (PASS):** value column gives the
  semantics inline — *the smallest count that is corroboration at all* → `2`,
  "and no other value."
- **§5.3 / §5.4 / §5.6 / §5.7 (FAIL):** value column gives **role + prohibition
  + a deferral token** — *"the frozen deterministic claim-support test
  parameters (entity-level matching; **exact parameters fixed at G4 from this
  register**). No probability numbers."* No extensional definition. The word
  "parameters" is a placeholder for a meaning that is never stated.

**The whole difference between PASS and FAIL is the presence or absence of the
semantic definition in the specification.** The five passing registers carry
their layer-4 semantics; the four failing registers defer it as "the value." No
selector distinguishes the two groups — `EVIDENCE_ORDERING_KEY` has no selector
either, and needs none. This is direct, pre-existing, independent evidence that
the missing object is a **definition**, not a **choice function**.

v1 itself mis-read this control group (v1 §2.2): it attributed the passing
registers' uniqueness to an *implicit selector* ("a minimality argument," "an
identity convention," "a structural-uniqueness argument"). But
`EVIDENCE_ORDERING_KEY` has no minimality or extremal argument at all — it is
simply **defined**. v1 saw selectors where there were definitions, and so
diagnosed a missing selector. That misreading is the first move of the
treadmill.

---

## 3. Why `A` (missing selector) is a misdiagnosis, not the root

### 3.1 A selector is ill-typed over an undefined set

A canonical selection principle is a choice function
`select_r : 𝒫(A_r) → A_r` with `select_r(A_r) ∈ A_r` unique. For this to be so
much as **well-typed**, two things must already exist:

1. a well-defined universe `A_r` of candidate values, and
2. individuation of its elements — the ability to tell two candidates apart.

Both (1) and (2) require the register's **layer-4 semantics** — the extensional
definition of what a support relation / materiality predicate / extractor /
answer skeleton *is* as a function from inputs to outputs. Without it:

- `A_r` is defined only by the prohibition layer (§2.3/§3–§6 part 2 of the
  method are all *"must not"* clauses), so it is a **one-sided, downward-closed
  family with a degenerate infimum** — the always-`False`/always-empty element
  is a legal member (v1-a, v1-b).
- Its elements are **not individuated**: two admissible support relations differ
  only in their layer-4 semantics, and that is precisely what is unstated, so
  "which element" is a question the universe cannot answer (CE-4…CE-8).

A choice function therefore **presupposes exactly the object that is missing.**
Adding a selector cannot supply a definition; it can only assume one. This is
why `A` is not merely insufficient but *category-mismatched* to the defect.

### 3.2 The regress this forces (option `E`, named)

Because each correction is required (by the boundary — §4) to live at the
selection layer and forbidden from stating semantics, each correction can only
**relocate the undefinedness up one meta-level**:

```
 method    : multiplicity of  VALUES              (|A_r| ≥ 2)
   → v1     : adds a selector over values;
             audit finds multiplicity of the SELECTED value is degenerate,
             and for templates a multiplicity of FUNCTIONS         (value → function)
   → v2     : re-anchors the selector to "equal to the extension of
             the frozen role-PREDICATE";
             audit finds multiplicity of the PREDICATE itself       (function → predicate)
             (scope? quantifier? normalisation? granularity? span?)
   → (v3?)  : would name the predicate; an audit would then find
             multiplicity in the predicate's PARAMETERISATION        (predicate → parameterisation)
```

Each step is a faithful, competent correction of the *previous* audit's named
counterexample, and each step is punctured by the *next* audit descending one
level. The sequence does not converge because **at no level is the semantic
content actually supplied** — it is only ever pushed to a level not yet
examined. This is the regress. It is not evidence that the corrections were
sloppy (they were not — audit 2 explicitly certifies v2 as "a genuine,
correctly-reasoned improvement"). It is evidence that the corrections are
**aimed at the wrong layer**.

A selector-shaped fix can never terminate a regress whose engine is a missing
definition. That is the precise sense in which "successive selector corrections
continue to fail."

---

## 4. `C` — the incorrect abstraction boundary that produces the regress

### 4.1 Where the boundary is drawn

The method draws one primary boundary, restated across §0.1, §0.2, §2.5, §7,
§8, and §10:

> **On the "methodology" side:** role, type, constraints (prohibitions),
> invariants, the auditor's *verification* method (§7), the ReleaseManager's
> *transcription* method (§8). The method may state all of these. It may state
> **no value** (§0.2 "Choose any value"; §10 "It contains no value").
>
> **On the "value" side:** the concrete canonical constant, authored later by
> the ScientificAuditor at G4/E4 and transcribed by the ReleaseManager.
> Everything the method defers is called **"the value."**

The four registers' **semantic definitions were placed on the value side** — as
the T1 §5.3/§5.6/§5.7 phrasing shows, the meaning of "supports/extract/template"
is bundled into "exact parameters fixed at G4 from this register." So the
methodology may not state it (it is "a value"), and the constraint layer does
not state it (it is not a prohibition).

### 4.2 Why this placement is *incorrect*

A support relation's **semantics** and its **frozen value** are not the same
object at different times; they are different *kinds* of object:

- The **semantics** (layer 4) is a *definition*: "supports(c,e) ⟺ …". It is the
  content that individuates candidates and gives `A_r` a two-sided boundary.
- The **value** (layer 5) is a *serialization*: the concrete frozen constant
  the digest hashes. It is what §8 transcribes.

For `EVIDENCE_ORDERING_KEY` the two coincide trivially because the semantics is
itself a short constant ("lexicographic on `(origin_domain, doc_id)`"), so
bundling them is harmless. For the four registers the semantics is a
**definition of a function**, not a constant, and bundling it into "the value"
commits a category error: it treats *the meaning of the register* as if it were
*a number to be filled in later*.

The boundary therefore runs **through the middle of layer 4**, splitting an
indivisible object:

```
    layer 1  ROLE            ─┐
    layer 2  TYPE/CONTRACT    ├─ method may state  (methodology side)
    layer 3  PROHIBITIONS    ─┘
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ← boundary drawn HERE, cutting layer 4
    layer 4  SEMANTICS       ─┐   ← belongs on the methodology/spec side,
                              │      but is assigned to the value side
    layer 5  VALUE           ─┴─ deferred to G4  (value side)
```

Layer 4 belongs with layers 1–3 (it is *definitional*, authored before any
value is meaningful), but the boundary assigns it to layer 5. Because no actor
on either side owns it — the methodology is forbidden to state it, and the
"value" author at G4 is handed a selector/verification pipeline that assumes it
already exists — layer 4 is **authored by nobody**. Every audit counterexample
is a probe into that unowned layer.

### 4.3 How the misplaced boundary produces each observed symptom

- **Degenerate infima (v1-a, v1-b).** With layer 4 removed, the constraint layer
  is *all prohibition*, so `A_r` is one-sided and its extremum is the "do
  nothing" element. The boundary caused the one-sidedness.
- **Relocated multiplicity (CE-4…CE-9).** v2's "equal to the extension of the
  frozen role-predicate" is an attempt to *reach across the boundary* and cite
  layer 4 — but layer 4 was never written, so "the frozen role-predicate" names
  no single object. The equality is against an undefined term.
- **Compositional and reachability gaps (CE-10, CE-11, CE-13).** The *joint*
  semantics of the composed mechanism, and the semantics of "reachable over the
  frozen corpus," are layer-4 facts about the whole PA-2→PA-3 pipeline. The
  boundary partitions the registers into four independently-deferred "values,"
  so no layer owns the composition. CSP-c, living on the methodology side, can
  only quantify per-register and existentially — it cannot state a joint
  semantic property it is forbidden to author.
- **Non-lattice materiality (CE-12).** Whether the admissible materiality family
  is even a lattice is a layer-4 question about the meaning of "genuine
  incompatibility." Undefined layer 4 ⇒ the family's order structure is
  unknown ⇒ "⊆-least" may denote an antichain.

One misplaced boundary; every symptom.

### 4.4 Why `D` (missing preregistration) collapses into `C`

One might argue the registers were never properly preregistered. But T1 *is* a
preregistration, and it *did* preregister these four — it preregistered their
**role, type, and prohibitions**, and preregistered a **decision to defer their
value to G4**. The defect is not that preregistration is absent; it is that the
preregistration's **completeness boundary** was drawn to exclude layer 4,
deferring definitional content under the label "value." That is a statement
about *where the boundary sits*, i.e. `C`. `D` is `C` seen from the calendar
instead of from the architecture.

---

## 5. Adjudication: the minimal root cause

**Minimality test.** The root cause is the smallest condition whose removal
would have prevented *every* failed audit and stopped the recurrence.

- **Would supplying `A` (a selector) have prevented the failures?** No. Both
  corrections supplied selectors; both were falsified. `A` cannot be the root
  because adding it is the observed failure mode.
- **Would supplying `B` (the semantic definitions) have prevented the
  failures?** Yes for the *individual* counterexamples — a defined `supports`
  excludes always-`False`; a defined candidate boundary excludes the granularity
  ambiguity. But `B` alone does **not** explain the *recurrence*: it does not say
  why two competent corrections both declined to write definitions and reached
  for selectors instead. Left at `B`, a third correction could again mis-file the
  definitions and add a third selector. `B` is the missing content; it is not the
  cause of the pattern.
- **Would correcting `C` (the boundary) have prevented the failures *and* the
  recurrence?** Yes. If layer 4 were placed on the specification side — where
  the register's *meaning* is authored before any value or selector — then (i)
  `A_r` becomes two-sided and individuated, so the degenerate infima and the
  relocated multiplicities never arise, and (ii) corrections are no longer
  *structurally forced* into the selector layer, so the regress has no engine.
  `C` is upstream of both `A` (it is why the fix is always selector-shaped) and
  `B` (it is why the definitions are unwritten and unowned).

**Therefore the minimal root cause is `C`.** `B` is its necessary manifestation
(the content that is missing); `A` is the misdiagnosis it induces (the
wrong-layer fix); `E`/the regress is the mechanism by which it yields repeated
failure; `D` is the same defect described temporally.

Stated once, precisely:

> **The four deferred registers were specified by role, type, and prohibition,
> with their defining semantics classified as a "value" to be fixed at G4. This
> abstraction boundary places definitional content on the deferred-value side,
> where the methodology may not author it and the constraint layer does not
> contain it. Consequently `A_r` is defined by prohibitions alone — one-sided
> and with un-individuated elements — and no choice function over it can be
> well-typed. Every correction, confined by the boundary to the selection layer,
> can only add a selector that presupposes the missing definition, so each
> correction relocates the undefinedness one meta-level up and is falsified by
> the next audit descending to that level. The failures are not defects of the
> selectors; they are the boundary asserting that you cannot select from a set
> you were forbidden to define.**

---

## 6. What the root cause implies (diagnosis only — not a remedy)

Per mission, this section states *where the defect lives*, not how to fix it. It
adds no selector, no value, no constant, and no redesign.

- The missing object is a **definition**, not a **choice function**. It is
  layer-4 semantics: the extensional meaning of `supports`,
  `is_material`/materiality, `extract`/candidate-boundary, and the per-state
  answer skeleton — including their **scope, quantifier, normalisation,
  granularity, span, discourse level, composition, and corpus of quantification**
  (the eight axes the audits probed).
- That object belongs on the **specification side of the boundary**, alongside
  role/type/prohibition, authored **before** any value is transcribed or any
  selector is defined — exactly as `EVIDENCE_ORDERING_KEY`'s semantics is
  authored inline today.
- Once layer 4 is present and owned, the "selector" question largely dissolves:
  the passing registers demonstrate that a **defined** register needs no
  selection principle (`EVIDENCE_ORDERING_KEY` has none), and where a residual
  ordered family survives, its extremum is being taken over a *two-sided,
  individuated* set rather than a prohibition-only lattice.
- No `E-SELECT` layer (v1/v2), no floor, no non-degeneracy clause, and no
  fixed-point re-anchoring is at the correct layer for this defect. Each is a
  competent operation on the wrong object. This analysis does **not** author the
  replacement; it identifies that the replacement is a *definitional*, not a
  *selectional*, act — and that authoring it is owned by the specification
  authority, not by another methodology correction.

Whether the boundary should be redrawn, and by whom, is a governance question
for the T1/method authorities and is **out of scope for this analysis**. This
document ends at the diagnosis.

---

## 7. Boundary statement (what this document did and did not do)

- **No correction proposed.** No `E-SELECT v3`, no amended axis, no floor, no
  clause. The analysis stops at naming the root cause and the layer it lives in.
- **No Finding 3 written.** The recurrence is diagnosed, not continued.
- **No selector, constant, value, or state added.** Nothing in `A_r`, the
  constraint layer, the invariant layer, the digest input list, ES-1, or PA-3 is
  touched. `SPEC_VERSION`/`PA3_RULESET_VERSION` do not move; the four
  placeholders stand and `frozen_constants_digest()` still raises on pending.
- **No redesign.** T1 §3–§9 and addendum §A are consumed as fixed context. The
  claim is about *where a boundary was drawn in the specification*, not about the
  mechanism the specification describes.

---

## 8. References (read-only grounding)

- `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` — §0.1/§0.2 (boundary and non-goals),
  §1 (the four vs the five; "deferral is an instruction"), §2.2 (evidence
  classes — all constraining/prohibiting), §2.3–§2.5 (constraints/invariants/
  "canonical"), §7 (verification of a *supplied* candidate), §8 (transcription).
- `PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` — §1 (gap named as missing choice
  function), §2.2 (control-group registers read as *implicit selectors*), §4
  (the four axes).
- `PROGRAM_A_REGISTER_DERIVATION_FINDING2.md` — §0/§3 (v1's degenerate-infimum
  diagnosis), §4 (CSP-c + re-anchored CSP-a + skeleton scope).
- `docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md` — §2 (independent
  from-scratch derivation attempt fails identically), §3.2 (v1-a/v1-b/v1-c
  degenerate collapses), §5 (FAIL scoped).
- `docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md` — §1–§2 (CE-4…CE-13),
  §3 (targets table), §4 (necessity survives / sufficiency falsified / an
  actually-working fix is strictly larger), §5 (FAIL).
- `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` — §5 register: §5.1/§5.5 (PASS
  siblings carrying semantics inline), §5.3/§5.4/§5.6/§5.7 (the four, value
  column = role + prohibition + "fixed at G4 from this register").

---

*End of root-cause analysis. The minimal root cause of every failed audit is an
incorrect abstraction boundary (`C`): the four registers' defining semantics
were classified as deferred values, which starves the constraint layer to
prohibitions and confines every correction to the selector layer, so each
correction adds a choice function over a set it was forbidden to define and is
falsified one meta-level down. `B` is the manifestation, `A` the misdiagnosis,
`E` the regress mechanism, `D` the same defect on the calendar. No correction is
proposed; no value, selector, or constant is added; ES-1 and PA-3 are untouched.*
