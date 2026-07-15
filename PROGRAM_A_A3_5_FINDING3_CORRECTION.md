# PROGRAM A — A3.5 FINDING 3 CORRECTION (ES-1)

**Title:** ES-1 Finding 3 Correction — S1 Anchoring *Faithfulness* Gap (`Comp ≠ ∅` does not
guarantee that `selected_claim` participates in the actual S1-triggering contradiction; the
`Comp` set lacks the §A4 cross-origin filter that S1-firing itself requires)
**Authority:** Chief Scientific Architect. Erratum-class rider to the T1/G4 freeze object
(`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`; "T1") and its PA-3 addendum
(`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`; "the addendum"), sibling to and dependent-upon
`PROGRAM_A_A3_5_FINDING2_CORRECTION.md` ("Finding 2", which introduced the `Comp`/`Part` split this
document refines), and independent of `PROGRAM_A_A3_5_FINDING1_CORRECTION.md` (Finding 1, **CLOSED —
not read or modified by this document**).
**Date:** 2026-07-13
**Status:** DRAFT — this document is a **specification correction only**. It closes one *faithfulness*
gap in the S1 anchoring rule: it adds a **single already-frozen conjunct** (the §A4 condition-3
cross-origin test) to the `Comp` set defined by Finding 2, so that the emitted
`contradiction_doc_ids` provably carries a claim that participates in the S1-triggering
contradiction. It does not redesign ES-1, does not change the four-state partition, does not change
which state fires for any input, introduces no new state, **no new predicate, and no new numeric
constant**. It rides the same B2 (ScientificAuditor) / B3 (ReleaseManager) sign-off as the parent
freeze object; until co-ratified, the standing prohibition (`ES1_IMPLEMENTATION_GATE.md`:91-93)
remains in force.

**Authorities used (only these):**
1. Frozen ES-1 — `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` (T1).
2. Frozen PA-3 — `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` (the addendum).
3. `docs/audits/A3_5_FINDING2_SONNET_AUDIT.md` (the independent audit; the new witness is its
   **A1 / Finding F3**, replayed verbatim in §1 and §4 below).
4. `PROGRAM_A_A3_5_FINDING2_CORRECTION.md` (Finding 2; the document whose `Comp`/`Part` anchoring
   rule this correction refines — §3.1/§3.2).

**Relationship to Findings 1 and 2 (recorded up front).**
- **Finding 1** corrected the S2/S3 *definitional prose* (T1 §3.1 rows, T1 §4 openers) and is CLOSED.
  It is **orthogonal** to this correction (proof: §5.2); no clause it edits (C1–C4) is read or
  altered here.
- **Finding 2** closed the S1 *totality* gap by defining `contradiction_doc_ids` on the input class
  where the triggering pair is disjoint from `selected_claim`, via the `Comp`-empty → `Part`
  fallback. Finding 3 is a **refinement of the same §A4 rule Finding 2 edited**: it does not undo
  Finding 2's fix (the `Part` fallback and its totality guarantee are preserved verbatim, §5.3), it
  **corrects the guard** (`Comp`) that decides *when* the fallback fires, so that the `Comp` branch
  can no longer emit a claim unrelated to the S1 trigger. The audit found Finding 2's totality claim
  **VALIDATED** but its *faithfulness* claim (§3.1 parenthetical, §3.2 I-3 preamble, §4 closing
  claim) **FALSIFIED** by witness A1; this correction makes exactly those three claims true.

---

## 1. Replay of the auditor's witness (Task 1)

### 1.1 The witness (verbatim from the audit, A1 / Finding F3)

The auditor's headline witness (`A3_5_FINDING2_SONNET_AUDIT.md` §3 row A1, §5 F3), a snapshot with
four supported claims (`Σ = {top4, z4, x4, y4}`):

- `top4` — `ios = 1`, single origin `a1` (evidence `a1_doc`).
- `z4` — `ios = 1`, **same origin `a1`** (evidence `a1_doc2`); `contradicts(top4, z4) = True`,
  `is_material(top4, z4) = True`. This pair is **same-origin** — a "lone source that self-contradicts"
  — so it is **not** S1-qualifying (§A4 condition 3 fails: `independent_origins(supp(top4) ∪ supp(z4))
  = independent_origins({a1_doc, a1_doc2}) = 1 < 2`).
- `x4` — `ios = 1`, origin `b1`.
- `y4` — `ios = 1`, origin `c1`; `contradicts(x4, y4) = True`, `is_material(x4, y4) = True`, and the
  pair is **cross-origin** (`independent_origins = 2`). This is the **genuine S1 trigger**, disjoint
  from `top4`.

This is the Finding-1 same-origin class (W0) **co-occurring** with the Finding-2 disjoint-trigger
class (W2) in one snapshot — both already accepted as legal, in-scope inputs by the prior two
corrections. The audit's Sweep (Part 1: 296/296 pathological at `ios(selected_claim)=1`, 0/900 at
`ios ≥ 2`; Part 2: 928/1928 ≈ 48.1% of S1-firing trials) shows the class is **systematic and confined
to `ios(selected_claim)=1`**, not contrived.

### 1.2 Trace under the Finding-2-corrected rule (reproduces F3)

1. **S0 (§A3 step 1):** `Σ ≠ ∅` → not S0.
2. **S1 (§A4):** the cross-origin pair `{x4, y4}` satisfies §A4 conds. 1–3 → **state = S1**. Stop.
3. **Anchoring (Finding 2 §3.1):**
   - `selected_claim` = `≺`-max over `Σ`. All four claims have `ios = 1` (primary tie); the secondary
     key `min EVIDENCE_ORDERING_KEY` decides: `top4`'s key `(a1, a1_doc)` sorts first → **`selected_claim
     = top4`**, unique. **(defined)**
   - `Comp = { c ∈ Σ : contradicts(top4, c) ∧ is_material(top4, c) } = {z4}` — because Finding 2's
     `Comp` **carries no cross-origin filter**, the same-origin, non-S1-qualifying decoy `z4`
     populates it. `Comp ≠ ∅` → **`Comp` branch taken** → `competing_claim = ≺-max({z4}) = z4`.
   - `contradiction_doc_ids` = supporters of `z4` = `(('a1', 'a1_doc2'),)`.

### 1.3 Replay result (executed, not hand-simulated)

Reproduced by executing the auditor's own retained scratch model
(`es1_finding2_audit_witnesses.py`, witness A1) — output verbatim:

```
=== A1: decoy-Comp witness (F3) ===
state:                    S1        (defined, unique)
selected_claim:          'top4'     (defined, unique — ios=1, secondary key)
support_doc_ids:          (('a1','a1_doc'),)          (defined)
independent_origin_count: 1         (defined)
branch:                  'Comp'      (Comp = {z4}, non-empty)
competing_claim:         'z4'        (the SAME-ORIGIN DECOY)
firing_pairs:            [('x4','y4')]   (the ACTUAL S1 trigger — disjoint from top4)
contradiction_doc_ids:    (('a1','a1_doc2'),)   ← supporters of z4, NOT of the real debate {x4,y4}
selected_is_true_s1_participant: False
```

`contradiction_doc_ids` is **defined, unique, deterministic, and seed/order-independent** (the audit's
A5/A6 confirm) — so this is **not** a totality, determinism, or replay defect. It is a
**faithfulness** defect: the field points at a same-origin contradiction (`top4` vs `z4`) that has
**nothing to do** with the pair (`{x4, y4}`) that actually fired S1. The real debate sits, unused, in
`Part`. This directly falsifies Finding 2's own §3.1 parenthetical gloss ("`if Comp ≠ ∅` (the
S1-triggering contradiction involves `selected_claim`)"), its §3.2 restated I-3 preamble, and its §4
closing claim that the field "carries the actual S1 debate."

**This correction changes only the membership predicate of `Comp`, on only that pathological input
class (§3).**

---

## 2. The mechanism, reconstructed formally (Task 2)

Frozen symbols. `Σ = { c : ios(c) ≥ 1 }` (§A1). For a pair `{a,b}`, write

```
s1pair(a,b) :=  contradicts(a,b) ∧ is_material(a,b)
              ∧ independent_origins(supp(a) ∪ supp(b)) ≥ 2, with ≥1 independent
                origin on each side                                    (§A4 conds 1–3)
```

`s1pair` is **the frozen S1-firing predicate itself** — the exact test §A4 already applies to decide
whether S1 fires. Define the frozen selection `selected_claim = ≺-max(Σ)` (§A1/§A2), and the
S1-participant set `Part = { c ∈ Σ : ∃ c'≠c, s1pair(c,c') }` (Finding 2 §3.1).

**Finding 2's anchoring (as it stands):**

```
Comp_F2 = { c ∈ Σ \ {selected_claim} : contradicts(selected_claim, c)
                                        ∧ is_material(selected_claim, c) }     (no cond-3 filter)
competing = ≺-max(Comp_F2)          if Comp_F2 ≠ ∅          (the "Comp" branch)
          = ≺-max(Part)             if Comp_F2 = ∅          (the "Part" fallback)
```

**The three frozen facts in tension:**

- **F-a (firing is cross-origin).** S1 fires iff `∃{a,b}⊆Σ : s1pair(a,b)` — the incompatibility must
  be **across independent sources** (§A4 cond 3). A same-origin material contradiction ("a lone source
  that self-contradicts") is **explicitly not S1** (§A4; T1 §3.1). **Frozen — preserved.**

- **F-b (`Comp_F2` is *not* cross-origin).** `Comp_F2` filters only on `contradicts ∧ is_material`
  (conds 1–2). It **omits condition 3**. So `Comp_F2` admits any material contradiction against
  `selected_claim`, **including same-origin ones that cannot fire S1** — precisely the class §A4
  excludes. This is the frozen D1 wording, carried unchanged into Finding 2's `Comp` branch ("This is
  the original frozen rule, unchanged", Finding 2 §3.1).

- **F-c (the branch guard is mislabelled).** Finding 2's §3.1 parenthetical, §3.2 I-3 preamble, and §4
  closing claim all read `Comp ≠ ∅` as meaning "`selected_claim` participates in the S1-triggering
  contradiction." That reading is the property of `s1pair(selected_claim, ·)`, **not** of
  `contradicts ∧ is_material` alone.

**The defect (formal).** Because `Comp_F2` drops condition 3 (F-b) while the label asserts condition-3
participation (F-c),

```
Comp_F2 ≠ ∅   ⇏   ∃ c : s1pair(selected_claim, c)
```

Whenever `selected_claim` has a **same-origin** material contradiction `z` (so `z ∈ Comp_F2`) **and**
the actual S1 trigger is a **disjoint cross-origin pair** elsewhere in `Σ`, the `Comp` branch fires and
returns `≺-max(Comp_F2)` — a claim (`z`) that is **not** a participant in any S1-firing pair. The
emitted `contradiction_doc_ids` is defined but **unfaithful**: it does not witness the contradiction
that caused S1.

**Algebraic confinement (independently reconfirmed, §5.4).** The gap exists **iff
`ios(selected_claim) = 1`.** If `ios(selected_claim) ≥ 2`, then `supp(selected_claim)` alone spans ≥2
independent origins, so for *any* `c` with `contradicts ∧ is_material` against `selected_claim`,
`independent_origins(supp(selected_claim) ∪ supp(c)) ≥ ios(selected_claim) ≥ 2` and there is ≥1
independent origin on each side automatically — i.e. every `Comp_F2` member is **already** an
S1-co-participant. Condition 3 is only non-vacuous, and the decoy only admissible, at
`ios(selected_claim) = 1`. (Audit Sweep Part 1: 0% pathological at `ios ≥ 2`, 100% of the *possible*
region at `ios = 1`.)

**Where the defect lives (frozen text, as amended by Finding 2):**

| # | Clause | Location | Role in the gap |
|---|---|---|---|
| G1 | **S1 firing predicate `s1pair`** | addendum §A4 conds 1–3 (lines 114–130) | Existential over `Σ`; **carries** cond 3. **Correct — preserved and reused.** |
| G2 | **`Part` fallback** | Finding 2 §3.1 (lines 170–181) | Defined from `s1pair`; already faithful. **Correct — preserved.** |
| **D3** | **`Comp` membership** | addendum §A4 D1 anchoring bullet (line 144), carried into Finding 2 §3.1 (line 165) | **Defective:** `{contradicts ∧ is_material}` **without cond 3**; admits same-origin decoys ⇒ `Comp ≠ ∅` without S1-participation. |
| **D4** | **I-3 S1 row + preamble** | addendum §A7 (lines 220–227), as reworded by Finding 2 §3.2 | **Defective (inherited):** equates `Comp ≠ ∅` with "`selected_claim` participates in the S1-triggering contradiction"; false under D3. |

The defect is **F-b ∧ F-c ⟹ D3 unfaithful, D4 false**. G1 and G2 are correct and carry frozen
behaviour; they **must be preserved**. The defect is confined to the **`Comp` membership predicate
D3** and its **seam restatement D4** — the auditor's F3, root cause identified exactly (Task 3).

---

## 3. The smallest correction (Task 4)

**Correction principle (minimal, faithfulness-restoring).** Add to the `Comp` set the **one frozen
conjunct it is missing** — §A4 condition 3, the cross-origin independence test — so that `Comp`
becomes *exactly* "the claims that form an S1-firing pair **with** `selected_claim`," using the frozen
firing predicate `s1pair` verbatim. This is a **strict subset edit** of `Comp`: the corrected `Comp` ⊆
`Comp_F2`. It reuses **only frozen machinery** (`contradicts`, `is_material`, `independent_origins`,
`supp` — the four frozen `support_tests.py` predicates; §A6). **No new predicate, no new constant, no
new input.** It is the auditor's own suggested remediation direction (`A3_5_FINDING2_SONNET_AUDIT.md`
§5, F3), independently reconstructed and verified here (§5).

### 3.1 Amend the `Comp` definition (addendum §A4 D1 / Finding 2 §3.1)

**From (Finding 2 §3.1, the `Comp` let-binding, line 165):**

```
  - let `Comp = { c ∈ Σ : contradicts(selected_claim, c)
                          ∧ is_material(selected_claim, c) }`;
```

**To (corrected):**

```
  - let `Comp = { c ∈ Σ, c ≠ selected_claim :
                     contradicts(selected_claim, c)
                   ∧ is_material(selected_claim, c)
                   ∧ independent_origins(supp(selected_claim) ∪ supp(c)) ≥ 2,
                     with ≥1 independent origin on each side }`;
    — i.e. `Comp = { c ∈ Σ, c ≠ selected_claim : {selected_claim, c} satisfies the
      §A4 S1-firing predicate (conditions 1–3) }`. This is the frozen §A4 firing
      test applied with one side pinned to `selected_claim`; it adds condition 3
      (cross-origin independence) to the previous `{contradicts ∧ is_material}`
      membership, and nothing else.
```

The two branch bodies of Finding 2 §3.1 are **unchanged verbatim**: `if Comp ≠ ∅` → `≺-max(Comp)`;
`else` → `≺-max(Part)`. Only the *definition of the set `Comp`* is tightened. Because the corrected
`Comp` now contains **only** claims that form an S1-firing pair with `selected_claim`:

- Finding 2's §3.1 parenthetical — "`if Comp ≠ ∅` (the S1-triggering contradiction involves
  `selected_claim`)" — becomes **true by construction** and needs no prose edit.
- On witness A1, `Comp = ∅` (the same-origin `z4` is now excluded by cond 3), so the **`Part` fallback
  correctly fires** and `competing_claim ∈ {x4, y4}` — a genuine S1 participant (§4).

### 3.2 Reconcile the D4 seam wording (addendum §A7 I-3, as reworded by Finding 2 §3.2)

**From (Finding 2 §3.2, corrected I-3 preamble):**

```
… `contradiction_doc_ids` is computed with respect to `selected_claim` when
`selected_claim` participates in the S1-triggering contradiction (`Comp ≠ ∅`), and
otherwise with respect to the S1-triggering pair (the §A4 `Part` fallback). …
```

This text is now **correct as written** — under §3.1 the parenthetical equivalence `«participates in
the S1-triggering contradiction» ⟺ «Comp ≠ ∅»` holds exactly (proof §5.5). To make the equivalence
*explicit* rather than parenthetical, the phrase is tightened to:

```
… `contradiction_doc_ids` is computed with respect to `selected_claim` **iff**
`selected_claim` forms an S1-firing pair with some claim in `Σ` — equivalently
`Comp ≠ ∅` under the §A4-conds-1–3 definition of `Comp` (§3.1) — and otherwise with
respect to the S1-triggering pair (the §A4 `Part` fallback). …
```

**From (Finding 2 §3.2, corrected I-3 table, S1 row):**

```
| **S1** | … | supporters of selected_claim | supporters of the §A4 competing claim — the `≺`-maximal claim materially contradicting `selected_claim`, or (if none) the `≺`-maximal S1-participant (§A4 `Part`) | `ios(selected_claim)` (≥1) |
```

**To (corrected):**

```
| **S1** | … | supporters of selected_claim | supporters of the §A4 competing claim — the `≺`-maximal claim **forming an S1-firing pair with** `selected_claim` (§A4 conds 1–3), or (if none) the `≺`-maximal S1-participant (§A4 `Part`). In either branch the competing claim is a member of an S1-firing pair. | `ios(selected_claim)` (≥1) |

```

The **derived invariant** `contradiction_doc_ids ≠ () ⟺ state = S1` (addendum §A7 line 234) is
**preserved without edit**: the competing claim is a member of `Σ` in both branches (corrected `Comp` ⊆
`Part`-participants ⊆ `Σ`; `Part` ⊆ `Σ`), so `ios ≥ 1`, so it has ≥1 supporting evidence item, so
`contradiction_doc_ids ≠ ()` still holds in S1 and remains `()` in S0/S2/S3 (verified, §5.6). I-1, I-2,
and the S0/S2/S3 rows of I-3 are untouched.

### 3.3 Explicitly unchanged

- **The S1-firing predicate** (addendum §A4 conds 1–3): unchanged and now **reused** as the `Comp`
  membership test. S1 fires for **exactly the same inputs** as before — the four-state partition and
  its boundaries are untouched.
- **Claim selection §A1, tie-break `≺` §A2, `Part` fallback (Finding 2 §3.1):** unchanged.
  `selected_claim` is the same value for every input (on A1 it stays `top4`); `Part` is the same set;
  the `else` branch is verbatim.
- **`support_doc_ids`, `independent_origin_count`, `state`:** unchanged in every state and on every
  input (§5.3).
- **`contradiction_doc_ids` on every input where the Finding-2 `Comp_F2` already held only genuine
  S1-participants:** unchanged. That is **every** input with `ios(selected_claim) ≥ 2`, and every
  `ios(selected_claim) = 1` input with no same-origin decoy on `selected_claim` (§5.4). The change is
  confined to the pathological class.
- **S0/S1/S2/S3 state definitions** (T1 §3.1, incl. Finding 1's C1–C4), **per-tier semantic argument**
  (T1 §4), **`STATE_TIER_MAP`/`CONFIDENCE_TIERS`** (T1 §3.2), **precedence** (§A3),
  **`is_material`/`contradicts` contracts** (§A5/§A6): unchanged.
- **Every register constant** (T1 §5), the **digest algorithm and input list** (T1 §6.1 / §A6-DIGEST):
  unchanged. (`PA3_RULESET_VERSION` takes its corrected value at the single G4 pin as the correct
  consequence of editing rule (iv)/(v) — §5.7; tripwire functioning, not machinery change.)
- **Finding 1** (C1–C4) and **Finding 2's totality fix** (the `Part` fallback and its §5.1 proof):
  preserved (§5.2, §5.3).

---

## 4. Re-replay: the witness now succeeds (Task 4 confirm)

Re-run A1 (§1.1) under the corrected §A4 `Comp`. Executed against an independent reference
(`es1_finding3_correction_reference.py`, `classify_post_finding3`) built by adding **only** the cond-3
conjunct to the auditor's own model — output verbatim:

```
=== A1 (corrected): ===
state:                    S1        (unchanged)
selected_claim:          'top4'     (unchanged — ios=1, secondary key)
support_doc_ids:          (('a1','a1_doc'),)          (unchanged)
independent_origin_count: 1         (unchanged)
Comp = { c : {top4,c} fires S1 } = ∅   (z4 excluded: same-origin, cond 3 fails) → Part fallback
Part = {x4, y4}                        (the genuine S1 trigger)
competing_claim:         'x4'        (≺-max{x4,y4}: ios tie → key (b1,b1_doc) < (c1,c1_doc))
contradiction_doc_ids:    (('b1','b1_doc'),)   ← supporters of x4  (NOW the actual S1 debate)
competing is a true S1 participant:  True
replay identical across seeds {None,0,1,42,999999} and shuffled claim order: True
```

`contradiction_doc_ids` is now defined, unique, deterministic **and faithful** — it carries the
`{x4, y4}` contradiction that *caused* S1 to fire, exactly what the `DEBATED` template needs to
"represent both alternatives with source attribution while asserting neither" (§A4 / §A7 I-2). Every
other field is byte-for-byte what Finding 2 already produced.

**Finding 2's headline witness W2 is unaffected** (audit §6 confirms, and re-verified here): `top2` has
`ios = 3`, so by the algebraic confinement its `Comp` is *correctly* empty under both F2 and F3, the
`Part` fallback fires identically, and `contradiction_doc_ids = supporters(x2)` is unchanged. F3 is an
**adjacent** input class, not a regression on W2.

---

## 5. Proofs (Task 6)

Symbols are the frozen ones (§2). All numeric results below are direct program output from the two
retained scratch models (the auditor's `es1_finding2_audit_*.py` and this correction's
`es1_finding3_correction_reference.py` / `es1_finding3_verify.py`), not hand-simulation.

### 5.1 One state fires (Task 6a)

The decision procedure is the §A3 cascade, **unchanged** by this correction:

```
if Σ = ∅:                                        → S0     (§A3 step 1)
elif ∃{a,b}⊆Σ, a≠b : s1pair(a,b):                → S1     (§A3 step 2 / §A4)
elif ios(selected_claim) ≥ 2:                     → S3     (§A3 step 3)
else (ios(selected_claim) = 1):                   → S2     (§A3 step 3)
```

The three guards are evaluated in fixed order, mutually exclusive by `elif`-cascade; the first true
guard fires and terminates. This correction edits **only the `Comp` membership predicate inside the
already-fired S1 branch** — it adds, removes, and reorders **no guard**. The S1-firing guard is
`s1pair` over pairs, textually and operationally untouched. Therefore **exactly one state fires per
query** (T1 §3.3 / §A3 invariant) is preserved. `∎`

### 5.2 Finding 1 preserved (Task 5)

Finding 1 edits exactly C1–C4 (T1 §3.1 S2/S3 rows, T1 §4 S2/S3 openers). This correction edits exactly
D3 (the §A4 `Comp` membership, via Finding 2 §3.1) and D4 (§A7 I-3 preamble + S1 row, via Finding 2
§3.2). The two edit sets are **disjoint**: C1–C4 are state *definitions* / *tier arguments*; D3/D4 are
S1 *anchoring* / *seam invariant*. This document does not read, move, or re-word any of C1–C4. Finding
1's substantive results are also preserved: it concerns *which state fires* over `S0/S1/(S2|S3)`; this
correction changes **no state boundary** (§5.1), so the input→state partition is identical and Finding
1's exhaustiveness/exclusivity proof is unaffected. Independently reconfirmed: witness W0 (Finding 1's
own same-origin witness) is byte-identical under F2 and F3 — S1 never fires there, so the edited branch
is never reached (`es1_finding3_verify.py`, "W0: S2, identical F2==F3 OK"). `∎`

### 5.3 Finding 2 preserved (Task 5)

Finding 2's engineering deliverable — **totality of `contradiction_doc_ids`** (its §5.1) — is
preserved and, in fact, strengthened from "always defined" to "always defined *and faithful*":

- **Totality.** After this correction, `contradiction_doc_ids` is defined for every S1-firing input.
  Proof: S1 fires ⟹ `∃{a,b}⊆Σ : s1pair(a,b)` ⟹ `Part ≠ ∅`. The corrected rule sets the competing
  claim to `≺-max(Comp)` if `Comp ≠ ∅`, else `≺-max(Part)`. If `Comp ≠ ∅`, `≺-max(Comp)` exists. If
  `Comp = ∅`, `Part ≠ ∅` (just shown), so `≺-max(Part)` exists. In both branches the argument set is a
  non-empty subset of the §A2 strict total order `≺`, so its maximum exists and is unique (modulo the
  separate, untouched F2/F2′ injectivity dependency — §6). Tightening `Comp` from `Comp_F2` to
  `Comp_F2 ∩ {cond 3}` cannot break this: it only ever moves an input from the `Comp` branch to the
  `Part` branch, and `Part` is provably non-empty on exactly those inputs. **Finding 2's §5.1
  totality theorem holds verbatim under the corrected `Comp`.** `∎`
- **The `Part` fallback** (Finding 2 §3.1 `else` branch) is unchanged, and now fires on a **superset**
  of the inputs it fired on before (it additionally catches the ex-pathological `Comp`-branch inputs).
  On W2 — Finding 2's own witness — `Comp = ∅` under both versions, so the `Part` branch fires
  identically and the emitted value is unchanged (`es1_finding3_verify.py`, "W2: S1/Part, F2==F3").
- **Byte-identity elsewhere.** On every input where `Comp_F2` contained only genuine S1-participants,
  corrected `Comp = Comp_F2`, so the output is byte-identical to Finding 2 (§5.4). A 4,000-trial
  randomized sweep confirms every F2≠F3 difference is **strictly** the pathological class (F2 took the
  `Comp` branch with a non-participant `selected_claim`; F3 fixes it), and that in **every** such
  difference **only** `contradiction_doc_ids` changes — `state`, `selected_claim`, `support_doc_ids`,
  `independent_origin_count` are identical (`es1_finding3_verify.py`: "SWEEP: checked=4000, S1=3725,
  F2!=F3 diffs=660, every diff strictly the pathological class=True"). `∎`

### 5.4 `contradiction_doc_ids` correctness (Task 6d)

**Claim.** After the correction, whenever S1 fires, the competing claim (hence
`contradiction_doc_ids`) is a member of some S1-firing pair — i.e. it genuinely participates in the
S1-triggering contradiction.

**Proof.** Two branches.
- **`Comp` branch** (`Comp ≠ ∅`): by the corrected definition, every `c ∈ Comp` satisfies
  `s1pair(selected_claim, c)`, so `{selected_claim, c}` **is** an S1-firing pair. `competing = ≺-max(Comp)
  ∈ Comp`, hence `competing` is a member of the S1-firing pair `{selected_claim, competing}`. ✔
- **`Part` branch** (`Comp = ∅`): `competing = ≺-max(Part)`, and `Part` is by definition the union of
  members of S1-firing pairs, so `competing` is a member of some S1-firing pair. ✔

In both branches the competing claim participates in an S1-firing contradiction. **This is exactly the
faithfulness property witness A1 falsified for Finding 2 and that this correction restores.** `∎`

Independently confirmed by execution: over 4,000 randomized S1-firing inputs (including the ios=1
decoy regime that produced the defect), the number of cases where the emitted competing claim is **not**
a true S1 participant is **0** under F3 (`es1_finding3_verify.py`: "CORRECTNESS: … = 0"), versus 48.1%
of S1 trials under F2 (audit Sweep Part 2). The auditor's own A1 witness now returns `x4` (a genuine
`{x4,y4}` participant) instead of the decoy `z4` (§4). The audit's severity note — that F3 is a
"correctness/faithfulness defect … for an input class that is legal, reachable, deterministic, and …
not a measure-zero pathology" — is discharged: the class still occurs, but on it the emitted value is
now correct.

### 5.5 Invariant I-3 correctness (Task 6e)

The corrected §3.2 preamble asserts the biconditional

```
selected_claim participates in the S1-triggering contradiction   ⟺   Comp ≠ ∅.
```

**Proof.** (⟸) If `Comp ≠ ∅`, pick `c ∈ Comp`; then `s1pair(selected_claim, c)` holds (corrected
definition), so `selected_claim` is a member of the S1-firing pair `{selected_claim, c}` —
participation holds. (⟹) If `selected_claim` participates, then `∃ c : s1pair(selected_claim, c)`; that
`c ∈ Σ`, `c ≠ selected_claim`, and satisfies conds 1–3, so `c ∈ Comp` — hence `Comp ≠ ∅`. `∎`

This is precisely the equivalence witness A1 **falsified** for Finding 2 (`Comp_F2 ≠ ∅` while
`selected_claim` participated in **zero** firing pairs). Under the corrected `Comp` it holds
**exactly**. Executed check: over 3,842 S1-firing witnesses in a randomized sweep spanning the decoy
regime, the number of mismatches between `Comp ≠ ∅` and true participation is **0**
(`es1_finding3_verify.py` companion run: "A11 biconditional mismatches under F3 = 0"), versus the
auditor's A11 mismatch on A1 for F2. The S0/S2/S3 rows of I-3 and the derived seam invariant
`contradiction_doc_ids ≠ () ⟺ state = S1` are unaffected (§5.6). Thus **the corrected I-3 text is
now total *and* correct**, closing the mission's named I-3 falsification target. `∎`

### 5.6 Exclusivity and the derived seam invariant (Task 6c)

- **State exclusivity.** `Comp`/`Part` are computed strictly **inside** the already-fired S1 branch of
  the `elif`-cascade; tightening `Comp` cannot open a path into or out of `(S2|S3)`. No input can
  satisfy the S1-firing guard and also reach the `ios`-split. Reconfirmed across all witness families
  (audit A7; re-run here) — **0 violations**. `∎`
- **Derived seam invariant `contradiction_doc_ids ≠ () ⟺ state = S1`.** In S1 the competing claim is a
  member of `Σ` (§5.4), so `ios ≥ 1`, so `contradiction_doc_ids` has ≥1 item (`≠ ()`); in S0/S2/S3 it
  remains `()` (those branches are untouched). Executed check over 3,000 randomized inputs: holds in
  every case (`es1_finding3_verify.py`: "SEAM INVARIANT … holds = True"). `∎`

### 5.7 Determinism, replay, and digest semantics preserved (Task 5 / Task 6f)

- **Determinism.** The corrected `Comp` is a pure function of frozen artifacts: `s1pair` from §A4's
  frozen predicate (`contradicts`, `is_material`, `independent_origins`, `supp`), the winner by §A2's
  frozen `≺`, evidence ordered by the frozen `EVIDENCE_ORDERING_KEY`. No wall-clock, hash-seed, `score`,
  PA-2 tuple position, or `seed` enters. For identical `(query_text, snapshot)` the classifier computes
  an identical `EvidenceStateResult`. Reconfirmed: A1 output is byte-identical across seeds
  `{None,0,1,42,999999}` and shuffled claim order (§4). `∎`
- **Replay (T1 §7.2 / §9.2).** The edit introduces no seed dependence, so every input — including the
  A1 class — yields output invariant across the 22 seeds; the byte-identity property is satisfied by
  the corrected rule. No existing replay is invalidated because none exists: ES-1/PA-3 is DRAFT /
  NO-GO, `evidence_states.py`/`support_tests.py` are `NotImplementedError` stubs, no `mechanism_id()`
  has been minted or pinned. Replay is preserved **prospectively** (the rule G4 will freeze is
  seed-stable) and **vacuously for the past** (nothing frozen to replay). `∎`
- **Digest semantics.** Like Finding 2, this correction edits mechanism-defining rule **(iv)** (§A4 S1
  anchoring) and its seam restatement **(v)** (§A7 I-3) — both in the digest-covered set §A6-DIGEST.
  By the frozen contract, "Any edit to rules (i)–(v) requires bumping `PA3_RULESET_VERSION`."
  Advancing the tag is **preservation of digest *semantics***: the two-independent-drift-detectors
  tripwire (T1 §9.2) exists precisely to force a new `mechanism_id()` when a mechanism-defining rule
  changes; suppressing the bump would be the silent rule drift §A6-DIGEST makes un-landable. The
  digest **algorithm** (SHA-256 over the ordered §5 register + `STATE_TIER_MAP` + `CONFIDENCE_TIERS`)
  and its **input list** are unchanged; `PA3_RULESET_VERSION` was **already** a digest input, so only
  its *value* advances — no input added or removed, **no numeric constant** introduced, CR-8/L8
  firewall intact.
  - **Composition with Finding 2's bump.** Finding 2 already advances `PA3_RULESET_VERSION` for its
    §A4/§A7 edit. Findings 2 and 3 are **co-pending pre-G4 corrections that both land at the single G4
    pin**. There is no re-freeze of an already-pinned object and no double-bump: the digest is computed
    **once**, at G4, over the **fully-corrected** §A4/§A7 ruleset (Finding 2's `Comp`/`Part` split with
    Finding 3's cond-3 conjunct on `Comp`), and `PA3_RULESET_VERSION` takes its single corrected value
    reflecting that final rule (e.g. `pa3-ruleset-2026-07-13`). The auditor anticipated exactly this:
    F3's fix "is a **strict subset edit** of the same rule (iv) Finding 2 already touches, so it carries
    the same `PA3_RULESET_VERSION` consequence Finding 2 already accepts … it does not open a new class
    of re-freeze cost" (`A3_5_FINDING2_SONNET_AUDIT.md` §5, F3). `∎`

### 5.8 Minimality / uniqueness of the correction

The audit's suggested remediation (§5, F3) is a single edit: give `Comp` "the same
cross-origin/independence filter `Part` already correctly carries." This correction is exactly that,
and it is the **strictly smallest** faithfulness fix:

- **It changes exactly one set-builder** (`Comp`), by **adding one already-frozen conjunct** (§A4 cond
  3). It edits no other rule, introduces no predicate, no constant, no input.
- **It alters no already-correct output.** Corrected `Comp` ⊆ `Comp_F2`; the two coincide on every
  input where `Comp_F2` held only S1-participants (all `ios(selected_claim) ≥ 2`, and all `ios = 1`
  without a same-origin decoy). On those, output is byte-identical to Finding 2 (§5.3, §5.4). Only the
  pathological class — where `Comp_F2` admitted a non-participant — changes, and only in
  `contradiction_doc_ids`.
- **Alternatives are larger or behaviour-changing.** (a) *Move `selected_claim` to an S1-participant
  when S1 fires* — changes a **defined, correct** output (`selected_claim`, `support_doc_ids`,
  `independent_origin_count`) and edits §A1/§A2; rejected (this was already rejected for Finding 2,
  §5.6(a)). (b) *Range the competing set over `Part` in every S1 case* — changes
  `contradiction_doc_ids` even where the `Comp` branch was already faithful (`ios ≥ 2` cross-origin
  cases), altering correct outputs; not minimal. (c) *Add cond 3 to `Comp`* (this correction) — fires
  the `Part` fallback **only** where `Comp` previously admitted a non-participant, i.e. **only** on the
  unfaithful region, and reuses the exact frozen firing predicate. Option (c) is the **unique** change
  that (i) restores faithfulness (§5.4) and the I-3 biconditional (§5.5), (ii) alters no already-correct
  output, (iii) preserves Finding 2's totality theorem verbatim (§5.3), and (iv) reuses only frozen
  machinery. It is therefore the smallest correction. `∎`

---

## 6. Scope, non-scope, and out-of-scope observations

- **In scope (done):** restore *faithfulness* of `contradiction_doc_ids` on the S1 class where
  `selected_claim` carries a same-origin (non-S1-qualifying) material contradiction while the real
  trigger is a disjoint cross-origin pair (audit A1 / F3), by adding the §A4 condition-3 conjunct to
  the `Comp` set and reconciling the §A7 I-3 wording. Correctness of the S1 payload is restored;
  totality (Finding 2) is preserved.
- **Not changed:** any state boundary; which state fires for any input; `selected_claim`;
  `support_doc_ids`; `independent_origin_count`; the `Part` fallback; `contradiction_doc_ids` wherever
  the `Comp` branch was already faithful; any numeric constant; the digest algorithm/inputs; Finding
  1's clauses; Finding 2's totality theorem.
- **Out of scope — the semantic oddity (a design question, deliberately not "fixed").** As Finding 2
  noted, an S1 result can carry `selected_claim = ` a strongly-corroborated claim nobody debates, with
  the debate surfaced only through `contradiction_doc_ids`. Whether that is the *desirable* honesty
  behaviour is a **redesign** of the §A4 firing predicate / §A1 selection; it would move inputs between
  states and is **forbidden** by this mission and CR-6. This correction only makes the specification
  *faithful and self-consistent* about the behaviour the frozen rules already fix.
- **F2 / F2′ (audit, CONDITIONAL) — not addressed.** The §A2 tie-break injectivity assumption (unique
  `≺`-maximum) is an open dependency on PA-2's `EXTRACTION_PARAMS` dedup behaviour, applying to
  `≺-max(Σ)`, `≺-max(Comp)`, and `≺-max(Part)` alike. This correction neither closes nor worsens it:
  the corrected `Comp` is a **subset** of `Comp_F2`, so it introduces no new tie surface (a full-key
  tie within corrected `Comp` was already a tie within `Comp_F2`). The `∎` in §5.3/§5.4 is "unique
  modulo F2." Closing F2/F2′ requires the `EXTRACTION_PARAMS` register, not an anchoring edit.
- **Regression guard.** Any future remediation must keep W0, W2, A1, A11, and the audit's Sweep as
  regression checks. This correction's own scratch verifier (`es1_finding3_verify.py`) already runs
  them and asserts: W0/W2 byte-identical F2↔F3, A1 fixed to a true participant, every F2↔F3 difference
  strictly the pathological class, 0 correctness failures, 0 I-3 biconditional mismatches, seam
  invariant holds.

---

## 7. Ratification (BLANK — rides the parent T1/G4 B2/B3)

This correction is an erratum to the S1-anchoring `Comp` membership rule (§A4, as amended by Finding 2)
and its seam restatement (§A7 I-3). Like Finding 2 it is **not** digest-neutral: it edits
mechanism-defining rules §A6-DIGEST (iv)/(v) and therefore contributes to the single corrected
`PA3_RULESET_VERSION` value pinned at the (still-future) G4 step — the digest tripwire functioning as
specified (§5.7), breaking no existing replay because ES-1/PA-3 is not yet frozen (§5.7). It becomes
binding only when co-ratified under the parent object's sign-off blocks
(`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` Section 12). No approval is fabricated here.

- **B2 — ScientificAuditor (erratum concurrence, rides T1 §12 B2):** ____________________ , date: __________
- **B3 / G4 — ReleaseManager (applies the §A4 `Comp` cond-3 edit + §A7 I-3 reconciliation together with
  the Finding-2 `Comp`/`Part` edit, and transcribes the single corrected `PA3_RULESET_VERSION` into
  `program_a/constants.py` at the pinned commit, rides T1 §12 B3):**
  ____________________ , pinned commit: ____________________ , `PA3_RULESET_VERSION`: ____________________ , date: __________

---

*End of A3.5 Finding 3 correction. Specification correction only — adds one already-frozen conjunct
(§A4 condition 3) to the `Comp` set so `contradiction_doc_ids` provably carries a claim that
participates in the S1-triggering contradiction. Finding 1 preserved (orthogonal), Finding 2's totality
theorem preserved verbatim (the `Part` fallback is untouched and now correctly reached), replay
preserved (seed-free; pre-G4), determinism preserved, exclusivity preserved, invariant I-3 now total
AND correct, digest semantics preserved (the (iv)/(v) edit correctly advances `PA3_RULESET_VERSION` at
the single G4 pin). No redesign, no new constant, no future improvement.*
