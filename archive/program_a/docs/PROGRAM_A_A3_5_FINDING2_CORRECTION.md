# PROGRAM A — A3.5 FINDING 2 CORRECTION (ES-1)

**Title:** ES-1 Finding 2 Correction — S1 Anchoring Totality Gap (`contradiction_doc_ids`
undefined when the S1-triggering pair is disjoint from `selected_claim`)
**Authority:** Original ES-1 author. Erratum-class rider to the T1/G4 freeze object
(`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`) and its PA-3 addendum
(`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`), sibling to and independent of
`PROGRAM_A_A3_5_FINDING1_CORRECTION.md` (Finding 1, **CLOSED — not modified by this document**).
**Date:** 2026-07-13
**Status:** DRAFT — this document is a **specification correction only**. It closes one totality
gap in the frozen ES-1 specification by *defining a previously-undefined output field* on a class
of inputs the frozen rules currently leave unfixed. It does not redesign ES-1, does not change the
four-state partition, does not change which state fires for any input, introduces no new state, no
new predicate, and **no new numeric constant**. It rides the same B2 (ScientificAuditor) / B3
(ReleaseManager) sign-off as the parent freeze object; until co-ratified, the standing prohibition
(`ES1_IMPLEMENTATION_GATE.md`:91-93) remains in force.

**Authorities used (only these):**
1. `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` (the T1/G4 freeze object; "T1").
2. `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` (the PA-3 closure rider; "the addendum").
3. `docs/audits/A3_5_FINDING1_SONNET_AUDIT.md` (the independent audit; the new witness is its
   **W2 / Finding F1**, restated verbatim in §1 and §4 below).

**Relationship to Finding 1 (recorded up front).** Finding 1 corrected the S2/S3 *definitional
prose* (T1 §3.1 rows, T1 §4 semantic openers) and is CLOSED. This correction is **orthogonal**:
it touches only the addendum's S1-anchoring rule (§A4) and the S1 row of the seam invariant (§A7).
No clause edited by Finding 1 is read, moved, or altered here (proof: §5.2). The audit that
surfaced Finding 2 states this orthogonality explicitly (`A3_5_FINDING1_SONNET_AUDIT.md` §5, F1:
"orthogonal … F1 exists identically before and after the [Finding-1] correction, because the
correction only edits the S2/S3 prose, never the S1 anchoring rule").

---

## 1. Replay of the new witness (Task 1)

### 1.1 The witness (verbatim from the audit, W2 / F1)

A frozen snapshot yielding three supported claims (`Σ = {top2, x2, y2}`):

- `top2` — `ios = 3`, supported across three independent origins `d1, d2, d3`; **contradicts
  nothing** in `Σ`.
- `x2` — `ios = 1`, single origin `d4`.
- `y2` — `ios = 1`, single origin `d5`, with `d4 ≠ d5`.
- `contradicts(x2, y2) = True` and `is_material(x2, y2) = True`; the pair is **cross-origin**
  (`independent_origins(supp(x2) ∪ supp(y2)) = 2`).

This is a structurally ordinary configuration — "one strongly-corroborated, uncontested claim,
plus a separate weaker single-source pair that conflicts" (the audit's example: *"the launch date
is well-corroborated by 3 origins; two low-corroboration single-source claims about the launch
cost happen to conflict"*). The audit's Sweep 2 shows the class is **systematic**, not contrived:
17 / 216 (~7.9%) of a small synthetic domain lands in it.

### 1.2 Trace under the frozen operational rules

1. **S0 test (§A3 step 1):** `Σ = {top2, x2, y2} ≠ ∅` → not S0.
2. **S1 test (§A3 step 2 / §A4):** the unordered pair `{x2, y2} ⊆ Σ` satisfies **all three** §A4
   conditions — `contradicts(x2, y2)` (cond. 1), `is_material(x2, y2)` (cond. 2), and
   `independent_origins(supp(x2) ∪ supp(y2)) = 2 ≥ 2` with one independent origin on each side
   (cond. 3). The §A4 firing predicate is an **existential over all pairs in `Σ`**, so it is
   satisfied → **state = S1**. Stop.
3. **S1 anchoring (§A4):**
   - `selected_claim` = §A1/§A2 `≺`-maximum over `Σ`. `top2` has `ios = 3`, strictly greater than
     `x2` and `y2` (`ios = 1`); the primary key alone decides it, **no tie** → `selected_claim =
     top2`, uniquely and deterministically. **(defined)**
   - `support_doc_ids` = supporters of `top2`, ordered by `EVIDENCE_ORDERING_KEY`. **(defined)**
   - `independent_origin_count = ios(top2) = 3`. **(defined)**
   - `contradiction_doc_ids` = supporters of "the `≺`-maximal claim among
     `{ c ∈ Σ : contradicts(top2, c) ∧ is_material(top2, c) }`" (§A4 anchoring bullet). But `top2`
     **contradicts nothing**, so this set is **`∅`**, and "the `≺`-maximal claim among `∅`" **has
     no value**. → `contradiction_doc_ids` is **UNDEFINED**.

### 1.3 Replay result

```
=== W2: anchoring-gap witness (S1-triggering pair disjoint from selected_claim) ===
state:                    S1        (defined, unique)
selected_claim:          'top2'     (defined, unique — ios=3, no tie)
support_doc_ids:          supporters(top2), EVIDENCE_ORDERING_KEY-ordered   (defined)
independent_origin_count: 3         (defined)
contradiction_doc_ids:    UNDEFINED — argmax over the empty set
```

The classifier reaches a **single, correctly-identified state label (S1)** with **four of five
result fields fully determined**, and exactly **one field left unfixed by the frozen rules**. This
is not seed-sensitivity (the audit's W12 confirms the *undefinedness itself* is deterministic — it
fails the same way under every seed); it is a **totality gap in the anchoring rule**. Replay in the
T1 §7.2 sense (byte-identity across the 22 seeds) is not the failure — the failure is that the
*specification does not determine the bytes* of one field for this input class.

**This correction changes only that one undefined field, on only that one input class (§3).**

---

## 2. Root cause (Task 2)

The defect is a **scope mismatch between two frozen rules that were each independently correct**:

- **The S1-firing predicate (§A4 conditions 1–3) is an existential over *all* unordered pairs in
  `Σ`.** S1 fires iff *there exists some* cross-origin material contradiction anywhere in `Σ`. The
  triggering pair need not involve any particular claim.

- **`selected_claim` (§A1/§A2) is the `Σ`-wide `≺`-maximum** — the single best-corroborated claim
  in `Σ`, chosen by corroboration strength (`ios`), then evidence position, then `claim_text`.
  This quantity has **no necessary relationship** to which pair triggered S1.

- **The `contradiction_doc_ids` anchoring rule (§A4) scopes the "competing claim" to
  `selected_claim`:** `{ c ∈ Σ : contradicts(selected_claim, c) ∧ is_material(selected_claim, c) }`.

When the S1-triggering pair is **disjoint from `selected_claim`** — i.e. `selected_claim` is a
strong, uncontested claim while the contradiction lives among *other, weaker* claims — that scoped
set is **empty**, its `≺`-maximum is **undefined**, and therefore `contradiction_doc_ids` (and, per
I-3, the completeness of the entire `EvidenceStateResult` for S1) is **undefined by the frozen
rules**.

The seam invariant §A7 I-3 inherits the same gap: it asserts `support_doc_ids` and
`contradiction_doc_ids` are "**always** computed with respect to `selected_claim`," and its S1 row
names `contradiction_doc_ids` as "supporters of the material-incompatible competing claim" —
presupposing such a claim exists *relative to `selected_claim`*. W2 is a legal input, unambiguous
under every other frozen rule, for which that presupposition is **false**. So I-3 is **not total**
as stated; its S0/S2/S3 rows remain total (the audit confirms this — only the S1 row breaks).

**Where the defect lives (frozen text):**

| # | Clause | Location | Text (frozen) | Role in the gap |
|---|---|---|---|---|
| G1 | **S1 firing predicate** | addendum §A4, conds. 1–3 (lines 114–130) | "there exists an unordered pair of *distinct* claims `{a, b} ⊆ Σ` such that all three hold…" | Existential over `Σ`; the triggering pair is **not** anchored to `selected_claim`. **Correct as-is — preserved.** |
| G2 | **Σ-wide selection** | addendum §A1/§A2 (lines 52–94) | "`selected_claim` = the element of `Σ` maximal under `≺`" | Picks the best-corroborated claim, **independent of the triggering pair**. **Correct as-is — preserved.** |
| **D1** | **S1 anchoring bullet** | addendum §A4 (lines 142–146) | "`contradiction_doc_ids` = … the `≺`-maximal claim among `{ c ∈ Σ : contradicts(selected_claim, c) ∧ is_material(selected_claim, c) }`" | **Defective:** the scoped set is **empty** whenever the S1-triggering pair is disjoint from `selected_claim`; `≺`-max(∅) is undefined. |
| **D2** | **I-3 S1 row + preamble** | addendum §A7 (lines 220–222, 227) | "`contradiction_doc_ids` … **always** computed with respect to `selected_claim`"; S1 row: "supporters of the material-incompatible competing claim" | **Defective (inherited):** presupposes a competing claim relative to `selected_claim` always exists in S1. |

The gap is **G1 ∧ G2 ⟹ D1 undefined**. G1 and G2 are each individually correct and carry frozen
behavior (S1 detection; deterministic selection with the FM-1 tier gate); they **must be
preserved**. The defect is confined to the **anchoring rule D1** and its **seam restatement D2**,
which fail to define an output when the (correct) existential firing and the (correct) `Σ`-wide
selection point at different claims.

---

## 3. The smallest correction (Task 3)

**Correction principle (minimal, defined-behavior-preserving):** add an **explicit fallback to the
D1 anchoring rule for exactly the empty-set case**, and reconcile the D2 seam wording to match. The
fallback fires **only** when the current scoped competing set is empty — i.e. **only** on the input
class the frozen rules currently leave undefined. On every input where `contradiction_doc_ids` is
already defined, the rule is **byte-for-byte unchanged**.

### 3.1 Replace the D1 anchoring bullet (addendum §A4)

**From (frozen, addendum §A4, lines 142–146):**

```
- `contradiction_doc_ids` = the supporters of the **materially-incompatible
  competing claim** — i.e. the `≺`-maximal claim among
  `{ c ∈ Σ : contradicts(selected_claim, c) ∧ is_material(selected_claim, c) }`,
  tie-broken by §A2. Its supporting evidence, ordered by
  `EVIDENCE_ORDERING_KEY`.
```

**To (corrected):**

```
- `contradiction_doc_ids` = the supporters of the **competing claim**,
  tie-broken by §A2, its supporting evidence ordered by `EVIDENCE_ORDERING_KEY`,
  where the competing claim is defined by:
  - let `Comp = { c ∈ Σ : contradicts(selected_claim, c)
                          ∧ is_material(selected_claim, c) }`;
  - **if `Comp ≠ ∅`** (the S1-triggering contradiction involves `selected_claim`):
    the competing claim is the `≺`-maximal element of `Comp`. *(This is the
    original frozen rule, unchanged.)*
  - **else** (`Comp = ∅`: every S1-triggering pair is disjoint from
    `selected_claim`): the competing claim is the `≺`-maximal element of the
    **S1-participant set**
    `Part = { c ∈ Σ : ∃ c' ∈ Σ, c' ≠ c,
              contradicts(c, c') ∧ is_material(c, c')
              ∧ independent_origins(supp(c) ∪ supp(c')) ≥ 2
                with ≥1 independent origin on each side }`
    — the claims that make the §A4 S1-firing predicate (conditions 1–3) true.
  Whenever S1 fires, `Part ≠ ∅` (that is what makes S1 fire), so the competing
  claim — hence `contradiction_doc_ids` — is now **total** over every input on
  which S1 fires.
```

The fallback reuses **only frozen machinery**: `Part` is defined by §A4's own firing predicate
(conditions 1–3, verbatim), and the `≺`-maximum and `EVIDENCE_ORDERING_KEY` ordering are the
already-frozen §A1/§A2 order. **No new predicate, no new constant, no new input** is introduced.

### 3.2 Reconcile the D2 seam wording (addendum §A7, I-3)

**From (frozen, addendum §A7, lines 220–222):**

```
**I-3 (anchoring & witnesses).** `support_doc_ids` and `contradiction_doc_ids`
are **always** computed with respect to `selected_claim`, ordered by
`EVIDENCE_ORDERING_KEY`, and satisfy per state:
```

**To (corrected):**

```
**I-3 (anchoring & witnesses).** `support_doc_ids` is **always** computed with
respect to `selected_claim`. `contradiction_doc_ids` is computed with respect to
`selected_claim` when `selected_claim` participates in the S1-triggering
contradiction (`Comp ≠ ∅`), and otherwise with respect to the S1-triggering
pair (the §A4 `Part` fallback). Both are ordered by `EVIDENCE_ORDERING_KEY`, and
satisfy per state:
```

**From (frozen, addendum §A7, I-3 table, S1 row, line 227):**

```
| **S1** | §A1/§A2 winner (non-`None`) | supporters of selected_claim | supporters of the material-incompatible competing claim (§A4) | `ios(selected_claim)` (≥1) |
```

**To (corrected):**

```
| **S1** | §A1/§A2 winner (non-`None`) | supporters of selected_claim | supporters of the §A4 competing claim — the `≺`-maximal claim materially contradicting `selected_claim`, or (if none) the `≺`-maximal S1-participant (§A4 `Part`) | `ios(selected_claim)` (≥1) |
```

The **derived invariant** `contradiction_doc_ids ≠ () ⟺ state = S1` (addendum §A7, line 234) is
**preserved without edit**: in the fallback branch the competing claim is a member of `Σ`, so
`ios ≥ 1`, so it has at least one supporting evidence item, so `contradiction_doc_ids ≠ ()` still
holds in S1 (and remains `()` in S0/S2/S3). I-1, I-2, and the S0/S2/S3 rows of I-3 are untouched.

### 3.3 Explicitly unchanged

- **The S1-firing predicate** (addendum §A4 conditions 1–3): unchanged. S1 fires for **exactly the
  same inputs** as before — the four-state partition and its boundaries are untouched.
- **Claim selection §A1 and tie-break `≺` §A2:** unchanged. `selected_claim` is the same value for
  every input (in W2 it stays `top2` — the fallback deliberately does **not** move it; see §5.6).
- **`support_doc_ids`, `independent_origin_count`, `state`:** unchanged in every state.
- **`contradiction_doc_ids` on every input where `Comp ≠ ∅`:** unchanged (first branch is the
  verbatim frozen rule).
- **S0, S1, S2, S3 state definitions** (T1 §3.1, incl. the Finding 1 corrected clauses), **the
  per-tier semantic argument** (T1 §4), **`STATE_TIER_MAP`/`CONFIDENCE_TIERS`** (T1 §3.2),
  **precedence** (T1 §3.3 / §A3), **`is_material`/`contradicts` contracts** (§A5/§A6): unchanged.
- **Every register constant** (T1 §5), the **digest algorithm and inputs list** (T1 §6.1 /
  §A6-DIGEST): unchanged. (`PA3_RULESET_VERSION` advances as the *correct consequence* of editing a
  mechanism-defining rule — see §5.5; this is the tripwire functioning, not a machinery change.)
- **Finding 1** (`PROGRAM_A_A3_5_FINDING1_CORRECTION.md`) and all four clauses it edits (C1–C4):
  unread and unmodified by this correction (§5.2).

---

## 4. Re-replay: the witness now succeeds (Task 4 / Task 1 confirm)

Re-run W2 (§1.1) under the corrected §A4:

1. **S0:** `Σ ≠ ∅` → not S0. *(unchanged)*
2. **S1:** pair `{x2, y2}` satisfies §A4 conds. 1–3 → **S1**. *(unchanged)*
3. **Anchoring (corrected):**
   - `selected_claim = top2` (`ios = 3`, no tie). *(unchanged — a defined output, preserved)*
   - `support_doc_ids` = supporters(`top2`), `EVIDENCE_ORDERING_KEY`-ordered. *(unchanged)*
   - `independent_origin_count = 3`. *(unchanged)*
   - `Comp = { c ∈ Σ : contradicts(top2, c) ∧ is_material(top2, c) } = ∅` (`top2` contradicts
     nothing) → **fallback fires**. `Part = {x2, y2}` (both participate in the triggering pair).
     `competing_claim = ≺-max({x2, y2})`: `ios(x2) = ios(y2) = 1` (primary tie) → secondary key
     `min EVIDENCE_ORDERING_KEY`: `x2`'s key `(d4, …)` vs `y2`'s `(d5, …)`; `d4 ≠ d5` so one is
     strictly first → **unique winner** (tertiary `claim_text` guards any residual tie). →
     `contradiction_doc_ids` = supporters of that winner, `EVIDENCE_ORDERING_KEY`-ordered.
     **DEFINED, UNIQUE, seed-independent.**

```
=== W2 (corrected): ===
state:                    S1        (unchanged)
selected_claim:          'top2'     (unchanged)
support_doc_ids:          supporters(top2)          (unchanged)
independent_origin_count: 3         (unchanged)
contradiction_doc_ids:    supporters(≺-max{x2,y2})  (NOW DEFINED — was UNDEFINED)
replay identical across calls incl. different seed: True
```

The single previously-undefined field is now defined, uniquely and deterministically, and it
carries the **actual S1 debate** (the `x2`/`y2` contradiction that *caused* S1 to fire) — which is
exactly what the `DEBATED` template needs to "represent both alternatives with source attribution
while asserting neither" (§A4 / §A7 I-2). Every other field is byte-for-byte what the frozen rules
already produced.

---

## 5. Proofs (Task 5)

Symbols are the frozen ones. `Σ = { c : ios(c) ≥ 1 }` (§A1). `s1pair(a,b) :=` §A4 conditions 1–3
on the pair `{a,b}`. `Comp`, `Part` as defined in §3.1.

### 5.1 Totality restored (the gap is closed)

**Claim.** After the correction, `contradiction_doc_ids` is defined for every input on which S1
fires.

**Proof.** S1 fires ⟺ `∃ {a,b} ⊆ Σ, a≠b : s1pair(a,b)` (§A4). Any such `a` (and `b`) is, by
definition, a member of `Part`. Hence **S1 fires ⟹ `Part ≠ ∅`.** The corrected rule sets the
competing claim to `≺-max(Comp)` if `Comp ≠ ∅`, else `≺-max(Part)`. In the first branch `Comp ≠ ∅`
by guard; in the second `Comp = ∅` but `Part ≠ ∅` (just shown). In both branches the argument set
is non-empty, so its `≺`-maximum exists. `≺` is the §A2 strict total order, so the maximum is
unique (modulo the separate, out-of-scope F2 injectivity dependency — §6). Therefore
`contradiction_doc_ids` is defined and unique whenever S1 fires. `∎`

Corollary: the audit's W2 class (17/216 of Sweep 2) and every input in it now produce a defined
result; no S1-firing input is left unfixed.

### 5.2 Finding 1 preserved (Task 4 of the mission)

Finding 1 edits exactly four clauses (C1–C4): the T1 §3.1 **S2 row** and **S3 row**, and the T1 §4
**S2 semantic bullet** and **S3 semantic bullet** (`PROGRAM_A_A3_5_FINDING1_CORRECTION.md` §2–§3).
This correction edits exactly D1 (addendum §A4 anchoring bullet) and D2 (addendum §A7 I-3 preamble
+ S1 row). **The two edit sets are disjoint** — C1–C4 live in T1 §3.1/§4 (state *definitions* and
*tier arguments*); D1/D2 live in addendum §A4/§A7 (S1 *anchoring* and *seam invariant*). This
document does not read, cite for modification, move, or re-word any of C1–C4.

Finding 1's own §3.3 states that "S1 composition and anchoring (addendum §A4) … seam invariants
I-1/I-2/I-3 (§A7) [are] unchanged **by the Finding-1 edit**." That scope statement remains **true**:
§A4/§A7 are changed **by this Finding-2 edit**, not by Finding 1. The two are independent riders on
the same parent, exactly as the audit found them to be (§F1, "orthogonal").

Finding 1's substantive results are also preserved, not merely its text:
- **State exhaustiveness/exclusivity (Finding 1 §5.1–§5.2)** concerns *which state fires* over the
  `S0/S1/(S2|S3)` cascade. This correction changes **no state boundary** — the S1-firing predicate
  is untouched (§3.3), so the partition of inputs into `{S0,S1,S2,S3}` is identical. Finding 1's
  exhaustiveness/exclusivity proof is unaffected.
- This correction touches **only the S1-state payload** (`contradiction_doc_ids`), never the
  `S2/S3` region Finding 1 repaired. The audit records this precisely: the gap is "a completeness
  failure of the *witness fields*, not of the *state label*."

### 5.3 Determinism preserved (Task 6)

The fallback is a pure function of frozen artifacts: `Part` from §A4's frozen firing predicate;
the winner by §A2's frozen `≺` (primary `ios`, secondary `min EVIDENCE_ORDERING_KEY`, tertiary
`claim_text`); the emitted evidence ordered by the frozen `EVIDENCE_ORDERING_KEY`. No wall-clock,
no hash-seed iteration order, no `score`, no PA-2 tuple position, no `seed` enters. For identical
`(query_text, snapshot)` the corrected classifier computes an identical `EvidenceStateResult`.
Determinism holds **unconditionally on the S1 branch** now — including the exact W2 class that
previously had no determined value (the audit's determinism break for this class is closed; its
separate F2 tie-break dependency is untouched and out of scope, §6). `∎`

### 5.4 Replay preserved (Task 5)

Replay (T1 §7.2/§9.2) requires the 22 seeds to yield byte-identical output for a frozen
implementation, and the manifest identity check `adapter_id == mechanism_id()` to hold.

- The fallback introduces **no seed dependence** (§5.3), so for the corrected mechanism every input
  — including the W2 class — yields output invariant across all 22 seeds. The 22-seed byte-identity
  property is **satisfied by the corrected rule**.
- **No existing replay is invalidated,** because none exists yet: under the standing prohibition
  ES-1/PA-3 is DRAFT / NO-GO, `program_a/mechanism/evidence_states.py` and `support_tests.py` are
  `NotImplementedError` stubs, `frozen_constants_digest()` is "implemented post-GO in Wave 4"
  (T1 §6.3), and no `mechanism_id()` has ever been minted or pinned (the audit confirms: "there is
  no executable implementation of ES-1/PA-3 to run witnesses against"). This correction lands in the
  **pre-G4 DRAFT**, so there are no frozen artifacts, no pinned digest, and no prior identity to
  break. Replay is preserved **prospectively** (the rule that G4 will freeze is seed-stable) and
  **vacuously for the past** (nothing was frozen to replay). `∎`

### 5.5 Digest semantics preserved (Task 7)

This is where Finding 2 **differs in kind from Finding 1**, and the difference must be stated
honestly rather than papered over.

- Finding 1 was **digest-neutral**: it edited the S2/S3 *state definitions* (T1 §3.1) and *tier
  arguments* (T1 §4), which are **not** in the digest-covered mechanism-defining set §A6-DIGEST
  (i)–(v). So it required no `PA3_RULESET_VERSION` bump.
- Finding 2 edits the **S1 anchoring rule (§A4 = rule (iv))** and the **seam invariant (§A7 = rule
  (v))** — **both are explicitly in the digest-covered set** §A6-DIGEST (iv)/(v). By the frozen
  contract, "Any edit to rules (i)–(v) requires bumping `PA3_RULESET_VERSION`." **This correction
  therefore advances `PA3_RULESET_VERSION`** (e.g. `pa3-ruleset-2026-07-09` →
  `pa3-ruleset-2026-07-13`).

**Advancing the tag is preservation of digest *semantics*, not a violation of them.** The digest's
semantics is precisely the "two independent drift detectors" tripwire (T1 §9.2): a change to a
mechanism-defining rule **must** change the digest and force a new `mechanism_id()`. Suppressing the
bump while editing rule (iv)/(v) — treating Finding 2 as a no-op erratum like Finding 1 — would be
exactly the silent rule drift §A6-DIGEST exists to make un-landable. Honoring the bump is the
tripwire doing its job.

What is preserved, concretely:
- The digest **algorithm** (SHA-256 over the ordered §5 register + `STATE_TIER_MAP` +
  `CONFIDENCE_TIERS`) and its **input list** are unchanged; `PA3_RULESET_VERSION` was **already** a
  digest input (T1 §6.1 / §A6-DIGEST), so only its *value* advances — no input is added or removed.
- **No numeric constant, no probability, no evaluation-side value** is introduced.
  `PA3_RULESET_VERSION` remains a pure identity string in the class of `SPEC_VERSION` (§A6-DIGEST).
  The CR-8/L8 firewall and ordinality-by-construction are intact.
- Because the change is pre-G4 (§5.4), the tag simply takes its corrected value at the **single**,
  still-future G4 pin — there is no re-freeze of an already-pinned object, no invalidated
  `CONSTANTS_HASH`, no minted `mechanism_id()` to retire. The digest is computed **once**, at G4,
  over the **corrected** ruleset.

So: digest **machinery, inputs, and firewall** are preserved; the digest **value** correctly
reflects the corrected rule (iv)/(v), as §A6-DIGEST mandates. `∎`

### 5.6 Minimality / uniqueness of the correction

The audit lists three remediation directions; this correction is option (c), and it is the
**strictly smallest**:

- **(a) Restrict `selected_claim`, when S1 fires, to S1-participants.** Rejected: `selected_claim`
  is **already defined** for W2 (`= top2`, uniquely). Option (a) would *change a defined output*
  from `top2` to `≺-max{x2,y2}`, and cascade into `support_doc_ids` (→ supporters of a different
  claim) and `independent_origin_count` (`3 → 1`). It edits **two** rules (§A1 and §A2 scope) and
  alters behavior far beyond the undefined field. Larger and behavior-changing.
- **(b) Redefine the competing set to range over all S1-participants in *every* S1 case.**
  Rejected: this would change `contradiction_doc_ids` even where it is **already defined**
  (`Comp ≠ ∅` cases with an additional disjoint triggering pair), altering a defined output. Not
  minimal.
- **(c) Explicit empty-set fallback (this correction).** Fires **only** when `Comp = ∅` — i.e.
  **only** on the input class the frozen rules leave undefined. On every already-defined input the
  rule is verbatim unchanged (the `Comp ≠ ∅` branch is the original text). It changes **exactly one
  field** (`contradiction_doc_ids`) on **exactly the undefined region**, and preserves `state`,
  `selected_claim`, `support_doc_ids`, `independent_origin_count`, and all `Comp ≠ ∅` values of
  `contradiction_doc_ids`.

Option (c) is the **unique** change that (i) restores totality (§5.1), (ii) alters no
already-defined output, and (iii) reuses only frozen machinery. It is therefore the smallest
correction. `∎`

---

## 6. Scope, non-scope, and out-of-scope observations

- **In scope (done):** define `contradiction_doc_ids` for the S1 input class where the triggering
  pair is disjoint from `selected_claim` (audit W2 / F1), by adding the §A4 empty-set fallback and
  reconciling the §A7 I-3 S1 row. Totality of the `EvidenceStateResult` payload is restored for S1.
- **Not changed:** any state boundary; which state fires for any input; `selected_claim`;
  `support_doc_ids`; `independent_origin_count`; `contradiction_doc_ids` wherever it was already
  defined; any numeric constant; the digest algorithm/inputs; Finding 1's clauses.
- **Out of scope — the semantic oddity (a design question, deliberately not "fixed").** W2 emits
  `state = S1` (`DEBATED`) while carrying `selected_claim = top2`, a strongly-corroborated claim
  that **nobody debates**, with the debate (`x2`/`y2`) surfaced only through
  `contradiction_doc_ids`. Whether that is the *desirable* honesty behavior — versus, say, having a
  strong uncontested claim suppress an unrelated weak contradiction — is a **redesign question**
  about the §A4 firing predicate and §A1 selection. Changing it would move inputs between states,
  alter frozen behavior, and force a genuine mechanism redesign. **Forbidden by this mission and by
  CR-6.** This correction only makes the specification *total and self-consistent* about the
  behavior the frozen rules already fix (S1, `selected_claim = top2`); it proposes no improvement.
- **F2 (audit, CONDITIONAL) — not addressed.** The §A2 tie-break injectivity assumption (unique
  `≺`-maximum for any real `CandidateClaims`) is an open dependency on PA-2's `EXTRACTION_PARAMS`
  dedup behavior, which this correction does not have authority over and does not touch. The `∎` in
  §5.1/§5.3 is "unique modulo F2" — if PA-2 can emit two claims with identical `(claim_text, minimal
  support)`, `≺-max(Part)` inherits the same conditional non-uniqueness as `≺-max(Σ)` already has.
  That is a **pre-existing, orthogonal** finding; closing it requires the `EXTRACTION_PARAMS`
  register, not an anchoring edit.
- **F0 (audit, documentation) — noted.** The audit records that its mission named a correction path
  (`docs/audits/A3_5_FINDING1_OPUS_CORRECTION_V1.md`) that does not exist, and that it audited the
  root-level `PROGRAM_A_A3_5_FINDING1_CORRECTION.md` instead. This Finding-2 document is likewise
  placed at repository root as `PROGRAM_A_A3_5_FINDING2_CORRECTION.md`, matching the sibling
  Finding-1 file's location. Reconciling the audit's path convention is a governance action for the
  document owner, outside this correction's authority.

---

## 7. Ratification (BLANK — rides the parent T1/G4 B2/B3)

This correction is an erratum to the **frozen PA-3 addendum's** S1-anchoring rule (§A4) and seam
invariant (§A7). Unlike Finding 1 it is **not** digest-neutral: it edits mechanism-defining rules
§A6-DIGEST (iv)/(v) and therefore **advances `PA3_RULESET_VERSION`** at the (still-future) G4 pin —
this is the digest tripwire functioning as specified (§5.5), and it breaks no existing replay
because ES-1/PA-3 is not yet frozen (§5.4). It becomes binding only when co-ratified under the
parent object's sign-off blocks (`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` Section 12). No
approval is fabricated here.

- **B2 — ScientificAuditor (erratum concurrence, rides T1 §12 B2):** ____________________ , date: __________
- **B3 / G4 — ReleaseManager (applies the §A4 D1 + §A7 D2 edits and transcribes the advanced
  `PA3_RULESET_VERSION` into `program_a/constants.py` at the pinned commit, rides T1 §12 B3):**
  ____________________ , pinned commit: ____________________ , `PA3_RULESET_VERSION`: ____________________ , date: __________

---

*End of A3.5 Finding 2 correction. Specification correction only — defines one previously-undefined
output field on one input class, via the smallest fallback that reuses only frozen machinery.
Finding 1 preserved (orthogonal), replay preserved (seed-free; pre-G4), determinism restored on the
S1 branch, digest semantics preserved (the (iv)/(v) rule edit correctly advances
`PA3_RULESET_VERSION`). No redesign, no new constant, no future improvement.*
