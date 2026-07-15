# PROGRAM A — REGISTER DERIVATION FINDING 1

**Title:** Methodological audit of `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` — the
uniqueness gap for the four deferred ES-1 registers, and the minimum correction.
**Object audited:** `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` (ES-1 register
derivation methodology).
**Registers in scope:** `SUPPORT_TEST_PARAMS` (§3), `CONTRADICTION_MATERIALITY_PARAMS`
(§4), `EXTRACTION_PARAMS` (§5), `ANSWER_TEMPLATES` (§6).
**Posture:** This is a *methodological* finding. It chooses **no** register value,
invents **no** constant, redesigns **no** part of ES-1, and modifies **no**
scientific claim. It returns only the correction to the methodology.
**Grounding (read-only):** T1 preregistration; PA-3 freeze addendum (incl.
`[Findings 1–3]`); the derivation method; the register audit; the G4 execution
plan.

---

## 0. One-line finding

`PROGRAM_A_REGISTER_DERIVATION_METHOD.md` specifies an **admissibility filter**
(constraints + invariants) plus a **certification/freeze pipeline** (§7/§8), but
it specifies **no choice function** — no a-priori rule that maps a
multi-element admissible set to a *single* canonical representative. For any
register whose admissible set is not already a singleton, the method therefore
returns a **set, not a value**, and uniqueness is unreachable *by the structure
of the method itself*. The four deferred registers are exactly the registers
whose admissible set the authorities declared (and intended) to be non-singleton.

---

## 1. The exact methodological gap (Requirement 1)

### 1.1 The method defines *admissibility*, not *derivability*

`PROGRAM_A_REGISTER_DERIVATION_METHOD.md` defines "canonical" (§2.5) as the
conjunction of four things:

1. **constraints** hold (§2.3 universal + §3–§6 part 2 per-register);
2. **invariants** preserved (§2.4 universal + §3–§6 part 3 per-register);
3. a genuine **B2** certification of (1)–(2) exists (§7);
4. a **ReleaseManager freeze** pins the value (§8).

Items (1) and (2) are **predicates**: each is a test a candidate either passes or
fails. Their conjunction defines, for a register `r`, an **admissible set**

```
A_r = { v : v satisfies all constraints(r) ∧ preserves all invariants(r) }.
```

Items (3) and (4) are **operations on an already-chosen candidate**: §7 *tests* a
supplied candidate for membership in `A_r`; §8 *transcribes and pins* it. Neither
generates a candidate.

**Nowhere in §2–§8 is there a function `A_r → v`.** The methodology contains a
membership test for `A_r` and a pipeline that consumes an element *already in
hand*, but no rule that **elects** one element of `A_r` when `|A_r| > 1`.

### 1.2 The gap named precisely

> **GAP.** The methodology conflates *admissibility* (a predicate over candidate
> values) with *derivability* (a function that yields one value). Derivation of a
> **unique** value requires a **choice function** (a selection principle)
> `select_r : 𝒫(candidates) → candidates` with `select_r(A_r) ∈ A_r` and
> `select_r(A_r)` unique. The method supplies the domain-defining predicate for
> `A_r` and the downstream pipeline, but **omits `select_r`** — and §0.2 forbids
> supplying an ad-hoc element in its place. Where `|A_r| = 1` this omission is
> invisible (the filter already yields a point); where `|A_r| > 1` the omission
> is the whole defect.

This is a single, locatable hole: **the absence of an a-priori selection
principle that closes a multi-element admissible set to a singleton.**

---

## 2. Why uniqueness fails (Requirement 2)

### 2.1 Formal statement

Let `r ∈ { SUPPORT_TEST_PARAMS, CONTRADICTION_MATERIALITY_PARAMS,
EXTRACTION_PARAMS, ANSWER_TEMPLATES }`. Then:

1. **The admissible set is multi-element.** By DERIVATION_METHOD §1, each of the
   four "share a … property: their role is fixed but their *concrete internal
   parameterization* admits **more than one structurally-defensible
   instantiation**." Formally `|A_r| ≥ 2`.
2. **The available evidence classes are constraint-only, not selecting.** The
   admissible evidence classes (§2.2) are E-STRUCT, E-DETERM, E-TYPE, E-PRIOR,
   E-DEV. The first four *constrain* `A_r` (they carve its boundary — determinism,
   entity-level form, type conformance, honored design commitments). E-DEV is
   explicitly **falsifying-only**: it "may **never** *select among admissible
   candidates by an observed score*" (§2.2 E-DEV; reinforced by §7
   "Falsification-first reading of E-DEV" and B-11, T1 §10.2). So **no evidence
   class in the method's own inventory can pick among the survivors** in `A_r`.
3. **Ad-hoc election is prohibited.** §0.2 ("Choose any value") forbids naming an
   element of `A_r`; §2.2 inadmissible list forbids any outcome-driven or
   Goodhart selection.

From (1)–(3): the method produces `A_r` with `|A_r| ≥ 2` and possesses no
admissible operator that reduces `A_r` to a singleton. Therefore the value is
**not uniquely determined**. ∎

### 2.2 Why the seven *other* registers do **not** exhibit this failure

The contrast is the proof that the gap is real and specific. Each determinable
entry already carries an **inline, register-specific selection principle** that
happens to make `|A_r| = 1`:

- `MIN_INDEPENDENT_ORIGINS_FOR_S3`: the selector is a **minimality argument** —
  "the *smallest* count that is corroboration at all" (T1 §5.1). Over the
  admissible set `{2, 3, 4, …}` this extremal rule elects `2` and, per AUDIT
  Entry 5.1, "**no other value**." The uniqueness comes from the *selection
  principle* (least element of a well-ordered set), not from the filter.
- `SPEC_VERSION`, `PA3_RULESET_VERSION`: the selector is an **identity
  convention** (a naming function of the freeze date/rule-set), which is itself a
  choice function with a single output.
- `STATE_TIER_MAP`, `CONFIDENCE_TIERS`, `EVIDENCE_ORDERING_KEY`,
  `INDEPENDENCE_RELATION`: the selector is a **structural-uniqueness argument**
  (the one order-preserving bijection; the one total order forced by L6 replay;
  the one origin-dedup relation) that *proves* `|A_r| = 1` directly.

The four deferred registers are precisely those for which **no such selection
principle was ever stated**. The methodology inherited an implicit,
per-entry selector for the seven and left the four with the filter alone. That
asymmetry *is* the gap of §1.

---

## 3. Proof that the current methodology *intentionally* yields multiple admissible values (Requirement 3)

This is not an accident to be patched by tightening a constraint; the method is
**designed** to output a non-singleton for these four. Four textual proofs:

1. **Deferral is defined as an instruction, not an omission.** §1: "Deferral is
   therefore **not an omission** to be patched by guessing a default — it is an
   explicit instruction that a **derivation procedure** must run first." The
   authorities *chose* to leave `|A_r| > 1` and route closure to a later,
   role-owned step.
2. **The document is constitutively value-free.** §0.2 ("Choose any value",
   "Invent any constant") and §10 ("It **contains no value** … It contains none
   of those values"). A method that forbids itself from naming an element of
   `A_r` cannot, by its own rule, collapse `A_r` to a point.
3. **The placeholder non-singleton is load-bearing.** §1 "Placeholder posture is
   load-bearing": the `{}` entries + `frozen_constants_digest()`-raises-on-pending
   make an admissible freeze mechanically impossible *while `A_r` is still a
   set*. The multiplicity is a **safety feature**, deliberately retained until an
   authorized selection occurs (AUDIT Entry 5.3; §8 step 3).
4. **Certification tests membership, presupposing multiplicity.** §7 audits a
   *supplied* candidate against the 8-criterion grid — an architecture that only
   makes sense if candidates are authored *outside* the method (E4 of the G4 plan)
   and then filtered. If the method itself yielded a unique value, §7's
   "provenance separation (no proxy)" and the E3→E4 role split would be vacuous.

**Conclusion (Requirement 3).** The methodology produces `|A_r| ≥ 2` for the four
registers **by construction and by intent**: it defines the admissible set, then
*hands the choice off* to a later authorized actor (ScientificAuditor authorship
at G4/E4), rather than encoding the choice as an a-priori rule. The multiplicity
is the intended output of the method as written. ∎

---

## 4. The minimum scientific addition that restores uniqueness (Requirement 4)

The correction is the **smallest object that turns a set into a point without
touching the set's definition**: an explicit, a-priori **Canonical Selection
Principle**. Nothing in the constraint layer, the invariant layer, ES-1, or PA-3
changes; only a *choice function over the already-admissible set* is added.

### 4.1 The general correction — add one methodological component: **§2.6 Canonical Selection Principle (E-SELECT)**

Insert, as a new subsection of the common derivation frame (§2), a sixth
component obligating every register whose admissible set is not provably a
singleton to carry a **Canonical Selection Principle (CSP)** with two parts:

- **(CSP-a) An a-priori extremal/canonical axis.** A rule, of evidence class
  **E-STRUCT only** (so firewall-clean by construction, §2.3 C-FIREWALL), that
  imposes a well-order or a canonical normal form on `A_r` and names its unique
  extremum/representative. It may cite **only** ES-1 structural semantics,
  corroboration structure, the frozen types, and the already-frozen
  determinism/replay requirements — never any observed outcome, score, or E-DEV
  measurement (that would reintroduce the §2.2 inadmissible / B-11 violation).
- **(CSP-b) A discharged uniqueness lemma.** A written proof that the axis of
  (CSP-a) has **exactly one** extremum/representative over `A_r` (existence +
  uniqueness). This is mandatory because an extremal axis over a merely *partial*
  order can have several minimal elements; without the lemma the "selector" may
  itself be multivalued and the gap is not closed.

**Why this is the *minimum*.** (i) It adds **nothing** to the constraint or
invariant layers, so every element of `A_r` — and therefore the selected one — is
still admissible and still invariant-preserving; no ES-1/PA-3 contract moves.
(ii) It is the *smallest* logical object that can convert `|A_r| ≥ 2` to `|A_r|=1`
(a choice function is exactly this and nothing more). (iii) The only alternative —
tightening constraints until the filter alone yields a point — is strictly larger
(it edits admissibility, i.e. ES-1/PA-3 structure) and, since §1 certifies the
surviving candidates as *genuinely* defensible, any such tightening would be a
**disguised selection principle smuggled into the constraint layer** — the same
correction, less honestly placed, at greater risk to the preservation
requirements. Hence an explicit E-SELECT principle is both necessary and minimal.

E-SELECT is the *generalization of the argument the method already uses* for
`MIN_INDEPENDENT_ORIGINS_FOR_S3` (§5.1's "smallest count" is a CSP with a trivial
uniqueness lemma over a well-ordered set). The correction merely makes that
existing, implicit device **mandatory and explicit** for every non-singleton
register.

### 4.2 The minimum per-register CSP axis (form only — no value chosen)

For each deferred register the correction names *which* a-priori axis the CSP must
use and *which* uniqueness lemma is then owed. It states the **selection
principle**, not the resulting value; the value still falls out only after the
unchanged §7 authorship/certification and §8 freeze.

| Register | Minimum CSP axis to add (E-STRUCT, a-priori) | Uniqueness lemma owed (CSP-b) | Structural anchor already in the authorities |
|---|---|---|---|
| **`SUPPORT_TEST_PARAMS`** (§3) | **Least-permissive-admissible** selector: among admissible support tests, elect the one whose "supports" relation is ⊆-minimal (certifies the *fewest* claim/evidence pairs) subject to totality. | Prove admissible support relations are closed under intersection and bounded below by totality, so a unique ⊆-least element exists. | Directly serves CF-R2 dominance (§3.3): the least-permissive test minimizes fabricated-claim false positives by construction, matching the FM-1 guard the register exists to protect. |
| **`CONTRADICTION_MATERIALITY_PARAMS`** (§4) | **Most-conservative-boundary** selector: elect the admissible materiality partition that is ⊆-minimal in the pairs labelled *material*, subject to the §A5 precondition (defined only on `contradicts`-true pairs) and S1 exhaustiveness. | Prove admissible materiality predicates are closed under intersection down to the non-triviality floor (a genuine incompatibility must remain material), giving a unique ⊆-least material set. | Honors §4.4 "S1-vs-noise now a frozen rule": the conservative extremum removes exactly the runtime-judgment latitude the placeholder left open. |
| **`EXTRACTION_PARAMS`** (§5) | **Canonical-minimal-extraction** selector: elect the admissible extraction yielding the ⊆-minimal claim set in a fixed normal form, subject to totality and the §A2 `claim_text`-injectivity precondition. | Prove existence and uniqueness of that normal form (a canonicalization theorem) and that it discharges — not merely preserves — the §A2 F2/F2′ injectivity CONDITIONAL (§5.3). | Matches §5.1/§5.3: entity-level, no-model-call, deterministic; the minimal canonical form is the E-DETERM-forced replay-stable output. |
| **`ANSWER_TEMPLATES`** (§6) | **Template normal form (canonical generator):** replace "author a string per state" with "apply one fixed, deterministic *realization function* from (the frozen per-state answer-construction rule, §6.1) × (the permitted `EvidenceStateResult` fields, §6.1) → a canonical template string." Selection is by **construction**, not by extremum (strings carry no natural a-priori order). | Prove the realization function is total over `{S0,S1,S2,S3}` and single-valued, and that its output honors the §A7 I-2 assertion gate and CR-3 slot-provenance for every state. | Matches §6.2–§6.3: the templates sit *at* the frozen wording layer; a generator fixes exactly that layer and nothing above it ("rendering niceties … Not mechanism-defining", addendum §A6-DIGEST). |

The three parametric registers close via an **extremal selector** over an ordered
admissible set; the template register closes via a **canonical generator** (the
string-domain form of a choice function). Both are instances of the single §2.6
E-SELECT component; both name a *principle*, and neither names a value.

---

## 5. Preservation proof — the correction disturbs nothing frozen (Requirement 5)

The addition is a *choice function over admissible values*. Since every element of
`A_r` already satisfies every ES-1/PA-3 invariant (that is what "admissible"
means), the **selected** element inherits every such property a fortiori. Item by
item:

- **Preserves ES-1.** E-SELECT adds no state, tier, precedence, or numeric
  constant; it selects among values that already preserve §2.4
  (ordinality-by-construction, determinism/replay, exactly-one-state-fires, CR-9/
  FM-1, CR-3, digest integrity). The tier semantics of T1 §4 are untouched — no
  scientific claim about `P(answer passes rubric)` is altered.
- **Preserves PA-3.** The CSP axes range over the *same* §A1–§A7 machinery and
  select values that already satisfy §A4 (S1 composition), §A5 (`is_material`
  precondition and two-claim signature), §A6 (`contradicts` retained/distinct),
  and §A2 (tie-break keys). Selecting one admissible support/materiality/
  extraction value moves none of these rules.
- **Preserves Finding 1.** F1 edits only the S2/S3 *state definitions*/tier
  arguments ("no material contradiction **across independent sources**", §A0).
  E-SELECT touches none of those objects; they are outside the (i)–(v) digest set
  and outside `A_r`. Digest-neutral to F1, exactly as §A6-DIGEST classifies F1.
- **Preserves Finding 2.** F2's `Comp`/`Part` **totality** theorem is proved for
  *all* admissible values (it depends only on `Σ`, the §A1/§A2 order, and
  `EVIDENCE_ORDERING_KEY`). A least-permissive support test or conservative
  materiality boundary is still an admissible value, so `Part ≠ ∅` whenever S1
  fires and `contradiction_doc_ids` stays total. Selection cannot break a
  property that holds set-wide.
- **Preserves Finding 3.** F3's `Comp` cond-3 (cross-origin) refinement is a
  definition on the anchoring set, upstream-independent of which admissible
  support/materiality value is selected; the E-SELECT extremum leaves the `Comp ⊆
  Part` structure and the S1-firing biconditional (§A7 I-3) intact.
- **Preserves the digest / firewall / identity.** E-SELECT introduces **no new
  register entry, no new numeric constant, and no new digest input** — it is a
  methodology rule about *how* the existing four entries are chosen. Therefore
  `frozen_constants_digest()`'s input **list** is unchanged, `PA3_RULESET_VERSION`
  does **not** advance (no rule-text edit to (i)–(v)), and CR-8/L8 stays intact by
  construction (CSP-a is E-STRUCT-only). Supplying the eventual value remains a
  §8 *transcription*, not a rule edit (§5.5 / §4.5).

---

## 6. Boundary statement (Requirements 6, 7, 8)

- **No value chosen (Req 6).** This finding names selection *principles* and the
  *lemmas they owe*; it computes, guesses, and transcribes **no** value for any of
  the four registers. `A_r` is left to be collapsed by the authorized actor under
  the unchanged §7/§8 pipeline.
- **No ES-1 redesign (Req 7).** No state, predicate, precedence, tier map, seam
  invariant, or type is added or altered. The correction lives entirely in the
  *methodology's* §2 frame as a new selection component; the mechanism of T1
  §3–§9 and addendum §A is consumed as fixed.
- **No scientific claim modified (Req 8).** The per-tier semantic argument
  (T1 §4), hypothesis H1, the corroboration semantics, and every firewall claim
  are unchanged. E-SELECT asserts no new empirical fact; it is a purely logical
  choice-function obligation over values the science already deems admissible.

---

## 7. The correction, stated once

> **Add to `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` §2 a new component §2.6
> "Canonical Selection Principle (E-SELECT)":** every register whose admissible
> set `A_r` is not *proven* to be a singleton MUST carry (a) an a-priori,
> E-STRUCT-only extremal axis or canonical-generator over `A_r`, citing only ES-1
> structure / frozen types / determinism requirements and never any observed
> outcome; and (b) a discharged uniqueness lemma proving that axis has exactly one
> extremum/representative. For the four deferred registers the minimum axes are:
> least-permissive-admissible support (§3), most-conservative materiality boundary
> (§4), canonical-minimal extraction normal form (§5), and a fixed per-state
> template realization function (§6). This is the smallest addition that converts
> the method from an **admissibility filter** into a **derivation** — it supplies
> the missing choice function, adds no constant, moves no ES-1/PA-3/Finding-1/2/3
> object, and leaves value authorship to the unchanged §7 (B2) and §8 (freeze)
> steps.

---

*End of Register Derivation Finding 1. Returns only the methodological
correction: the missing a-priori selection principle (E-SELECT) and its
per-register minimum form. No value is chosen; ES-1, PA-3, and Findings 1–3 are
preserved.*
