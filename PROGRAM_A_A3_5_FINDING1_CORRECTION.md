# PROGRAM A — A3.5 FINDING 1 CORRECTION (ES-1)

**Title:** ES-1 Finding 1 Correction — Same-Origin Material Contradiction Definitional Conflict
**Authority:** Lead Scientific Author, ES-1. Erratum-class rider to the T1/G4 freeze object
(`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`) and its PA-3 addendum
(`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`).
**Date:** 2026-07-13
**Status:** DRAFT — this document is a **specification correction only**. It removes one internal
contradiction from the frozen ES-1 specification and changes **no operational behavior**. It does not
redesign ES-1, does not improve ES-1, and introduces no new architecture, no new state, no new
predicate, and no new numeric constant. It rides the same B2 (ScientificAuditor) / B3 (ReleaseManager)
sign-off as the parent freeze object; until co-ratified, the standing prohibition
(`ES1_IMPLEMENTATION_GATE.md`:91-93) remains in force.

**Authorities used (only these):**
1. `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` (the T1/G4 freeze object).
2. `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` (the PA-3 closure rider).
3. The accepted Finding 1 counterexample (the same-origin / lone-source material-contradiction
   witness; the witness class named at addendum §A4: *"A lone source that self-contradicts is not
   S1"*), restated verbatim in §1 and §4 below.

---

## 1. The contradiction (Task 1)

ES-1 asserts, as a frozen invariant, that its four corroboration states are **exhaustive and mutually
exclusive** and that **exactly one state fires per query**
(`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.3, "Exactly one state fires per query (Tree 2
invariant: *state exhaustiveness and mutual exclusion*)"; reaffirmed at addendum §A3, "Exactly one
state fires per query (Tree 2 invariant, preserved)").

The specification contains two independent descriptions of when S2 and S3 fire, and they disagree on
one class of inputs:

- **The state definitions (T1 §3.1)** gate S2 and S3 on the *unqualified* clause **"no material
  contradiction."** S2 = "Support from exactly one independent origin; **no material contradiction**."
  S3 = "Support from ≥2 independent origins; **no material contradiction**." The per-tier semantic
  argument (T1 §4) repeats the same unqualified clause for both S2 and S3.

- **The operational precedence + S1 composition (T1 §3.3 / addendum §A3, §A4)** gate S1 on a
  *qualified* contradiction: a material contradiction fires S1 **only when it is across independent
  sources** — `independent_origins(supp(a) ∪ supp(b)) ≥ 2` with at least one independent origin on
  each side (addendum §A4 condition 3). A **same-origin** material contradiction ("a lone source that
  self-contradicts") is explicitly **not S1** (addendum §A4). The residual branch (§A3 step 3) then
  routes to S2 or S3 **by `ios(selected_claim)` alone, with no materiality check whatsoever.**

**The contradiction.** Consider an input in which the supported set `Σ` is non-empty (so not S0) and
contains a **material contradiction all of whose evidence comes from a single independent origin**.
Then:

- It is **not S0** (support exists: `Σ ≠ ∅`).
- It is **not S1** — the contradiction is not across independent sources (§A4 condition 3 fails).
- Operationally, §A3 step 3 routes it to **S2** (if `ios(selected_claim) = 1`) or **S3** (if `≥ 2`),
  because the S2/S3 split consults only `ios`.
- But **S2's and S3's own frozen definitions require "no material contradiction,"** and a material
  contradiction **is present**.

So the state the mechanism *fires* (S2 or S3) is a state whose *definition the input fails*. Read
literally, this witness satisfies **none** of the four state-definition predicates: S0 (excluded — has
support), S1 (excluded — not cross-origin), S2 (excluded — has a material contradiction), S3 (excluded
— has a material contradiction). The four definitions are therefore **not exhaustive**, and the frozen
"exactly one state fires" / "state exhaustiveness and mutual exclusion" invariant is **internally
contradicted by the very state definitions it ranges over**. Equivalently: the precedence rule assigns
S2/S3 to a region that the S2/S3 definitions exclude.

This is a pure **specification defect** — a disagreement between two frozen clauses of the *same*
freeze object about the same input — not a behavioral defect: the operational rule (§A3) is
unambiguous and total. The correction below conforms the **definitions** to the **operational rule**,
which is the unique fix that removes the contradiction without changing behavior (§3, §5.6).

---

## 2. The exact conflicting clauses (Task 2)

| # | Clause | Location | Text (frozen) | Role in the conflict |
|---|---|---|---|---|
| C1 | **S2 definition** | `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.1, S2 row (line 149) | "Support from exactly one independent origin; **no material contradiction**." | Excludes the witness from S2 via an *unqualified* materiality clause. |
| C2 | **S3 definition** | `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.1, S3 row (line 150) | "Support from ≥2 independent origins; **no material contradiction**." | Excludes the witness from S3 via an *unqualified* materiality clause. |
| C3 | **S2 semantic argument** | `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §4, S2 bullet (lines 241–247) | "When exactly one independent origin supports the selected claim and **there is no material contradiction**, …" | Repeats the unqualified clause in the CR-2 argument. |
| C4 | **S3 semantic argument** | `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §4, S3 bullet (lines 252–261) | "When ≥2 independent origins support the selected claim and **there is no material contradiction**, …" | Repeats the unqualified clause in the CR-2 argument. |
| R1 | **S1 independence condition** | `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A4, condition 3 (lines 122–130) | "`independent_origins(supp(a) ∪ supp(b)) ≥ 2` … (A lone source that self-contradicts is **not** S1 …)" | Qualifies S1 to *cross-origin* contradictions only. |
| R2 | **Residual S2/S3 split** | `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A3, step 3 (lines 107–108) | "selected_claim = §A1/§A2 winner over `Σ`. If `ios(selected_claim) ≥ MIN_INDEPENDENT_ORIGINS_FOR_S3` → **S3**, else (`ios == 1`) → **S2**." | Routes the residual **by `ios` only**, with no materiality check. |

**The precise inconsistency:** {C1, C2, C3, C4} say S2/S3 require the *global* absence of a material
contradiction; {R1, R2} together admit a same-origin material contradiction into S2/S3 while excluding
it from S1. C1–C4 are the defective clauses; R1 and R2 are frozen operational rules that must be
preserved (they carry determinism, selection, and the FM-1 tier gate). The defect is therefore in the
**definitional wording C1–C4**, and only there.

---

## 3. Corrected replacement text (Task 3)

**Correction principle (minimal, behavior-preserving):** narrow the S2/S3 "no material contradiction"
clause to **"no material contradiction across independent sources"** — equivalently, "no
S1-qualifying material contradiction." Because S1 is tested *before* S2/S3 in the frozen precedence
(§3.3 / §A3) and S1 already consumes exactly the *cross-origin* material contradictions (R1), the
residual S2/S3 region is precisely "material contradictions that are **not** across independent
sources (or none at all)." The corrected clause states that residual exactly. No other frozen clause
changes.

### 3.1 Replace T1 §3.1, the S2 and S3 rows (C1, C2)

**From (frozen):**

| **S2** | Support from exactly one independent origin; no material contradiction. | Single answer, hedged, source-attributed. | `PROBABLE` |
| **S3** | Support from ≥2 independent origins; no material contradiction. | Single answer, asserted, source-attributed. | `CERTAIN` |

**To (corrected):**

| **S2** | Support from exactly one independent origin; **no material contradiction across independent sources** (any material contradiction present is confined to a single origin and therefore does not fire S1 — addendum §A4 cond. 3). | Single answer, hedged, source-attributed. | `PROBABLE` |
| **S3** | Support from ≥2 independent origins; **no material contradiction across independent sources** (any material contradiction present is confined to a single origin and therefore does not fire S1 — addendum §A4 cond. 3). | Single answer, asserted, source-attributed. | `CERTAIN` |

### 3.2 Replace T1 §4, the S2 and S3 semantic-argument opening clauses (C3, C4)

**S2 → PROBABLE — from:** "When exactly one independent origin supports the selected claim and there
is no material contradiction, the lawful answer is a single hedged, source-attributed factual
assertion."

**S2 → PROBABLE — to:** "When exactly one independent origin supports the selected claim and there is
**no material contradiction across independent sources** (any contradiction present is confined to a
single origin and so does not fire S1 — addendum §A4 cond. 3), the lawful answer is a single hedged,
source-attributed factual assertion." *(Remainder of the S2 bullet unchanged.)*

**S3 → CERTAIN — from:** "When ≥2 independent origins support the selected claim and there is no
material contradiction, the lawful answer is a single asserted, source-attributed factual assertion."

**S3 → CERTAIN — to:** "When ≥2 independent origins support the selected claim and there is **no
material contradiction across independent sources** (any contradiction present is confined to a single
origin and so does not fire S1 — addendum §A4 cond. 3), the lawful answer is a single asserted,
source-attributed factual assertion." *(Remainder of the S3 bullet unchanged.)*

### 3.3 Explicitly unchanged

- **S0 and S1 definitions** (T1 §3.1): unchanged.
- **`STATE_TIER_MAP`, `CONFIDENCE_TIERS`** (T1 §3.2): unchanged.
- **Precedence `S0 → S1 → (S2 | S3)`** (T1 §3.3 / addendum §A3): unchanged, including the bullet
  "(S2 | S3) last: otherwise the state is S2 (exactly one independent origin) or S3 (≥2 independent
  origins)," which is already consistent with the corrected definitions.
- **S1 composition and anchoring** (addendum §A4), **claim selection** (§A1), **tie-break `≺`**
  (§A2), **seam invariants I-1/I-2/I-3** (§A7): unchanged.
- **Every register constant** (T1 §5.1–§5.9), the **digest definition** (§6), **identity format**
  (§9), and **`PA3_RULESET_VERSION`** (§A6-DIGEST): unchanged.

The correction is confined to four descriptive prose clauses (C1–C4). It adds the qualifier
"across independent sources," which is the wording that makes the definitions *state what the frozen
operational rule already computes*.

---

## 4. Why the original witness now succeeds (Task 4)

### 4.1 The accepted Finding 1 counterexample (restated)

Frozen snapshot with a single independent origin `d1`. Two documents from `d1`:
`doc1@d1` supporting claim `a` ("the capital is Alpha"), `doc2@d1` supporting claim `b` ("the capital
is Beta"), with `contradicts(a, b) = True` and `is_material(a, b) = True`. Both claims are supported,
so `Σ = {a, b}`; all supporting evidence is from the one origin `d1`.

### 4.2 Trace under the frozen operational rules (unchanged by this correction)

1. **S0 test (§A3 step 1):** `Σ = {a, b} ≠ ∅` → not S0.
2. **S1 test (§A3 step 2 / §A4):** `contradicts(a, b)` true, `is_material(a, b)` true, but
   `independent_origins(supp(a) ∪ supp(b)) = independent_origins({doc1@d1, doc2@d1}) = 1 < 2`
   (mirror/same-origin collapse, T1 §5.2) → §A4 condition 3 **fails** → **not S1** (exactly the
   "lone source that self-contradicts" exclusion).
3. **(S2 | S3) split (§A3 step 3):** `selected_claim` = the `≺`-winner over `Σ` (§A1/§A2), non-`None`;
   `ios(selected_claim) = 1` (one independent origin) → **S2 → PROBABLE**.

The mechanism fires **exactly one** state, S2, and emits the S2 answer form (single, hedged,
source-attributed) — as it always did operationally.

### 4.3 Why it now succeeds definitionally

- **Before the correction:** S2 fired, but S2's definition (C1) demanded "no material contradiction,"
  which is **false** for this witness (a material contradiction is present). The witness satisfied
  **no** state definition → exhaustiveness violated → internal contradiction.
- **After the correction:** S2's definition demands "no material contradiction **across independent
  sources**." For this witness the only material contradiction (`a` vs `b`) is **confined to origin
  `d1`** — it is **not** across independent sources. Hence "no material contradiction across
  independent sources" is **true**, and the witness now **satisfies the S2 definition**. The state the
  mechanism fires (S2) and the state whose definition the input satisfies (S2) **coincide**. The
  contradiction is gone; the emitted behavior is byte-for-byte identical.

The symmetric S3 case (same construction but the selected claim carries `ios ≥ 2` while the material
contradiction remains confined to a single origin on the losing side) is resolved identically by the
corrected S3 clause.

---

## 5. Proofs (Task 5)

Let `Σ = { c ∈ CandidateClaims.claims : ios(c) ≥ 1 }` (addendum §A1), where `ios(c)` is the
independent-origin support count under the frozen `INDEPENDENCE_RELATION` (T1 §5.2). All symbols below
are the frozen ones; the correction changes only the descriptive predicates of S2/S3, not any computed
quantity.

### 5.1 Exactly one state fires

The frozen classifier is the total decision procedure of §A3, unchanged by this correction:

```
if Σ = ∅:                                        → S0        (§A3 step 1)
elif ∃{a,b}⊆Σ: contradicts ∧ is_material ∧ cross-origin-independence(§A4): → S1  (§A3 step 2)
elif ios(selected_claim) ≥ MIN_INDEPENDENT_ORIGINS_FOR_S3 (=2):           → S3  (§A3 step 3)
else (ios(selected_claim) = 1):                   → S2        (§A3 step 3)
```

The three guards are evaluated in fixed order and are mutually exclusive by `elif`-cascade: the first
true guard fires and terminates (§A1 "Selection terminates here"; §A3 "Stop."). Exactly one branch is
reached for every input. The correction edits only the *English definitions* attached to the S2 and S3
outcomes; it does not add, remove, or reorder a guard. Therefore **exactly one state fires per query**
is preserved (T1 §3.3 / §A3 invariant), and — new after correction — the fired state's definition is
now satisfied by the input (§5.2), which was the property the defect had broken.

### 5.2 S0–S3 remain exhaustive

Every input lands in exactly one leaf of the §A3 cascade, so the *operational* partition is total and
disjoint. It remains to show the **corrected definitions** exactly label that partition (this is what
the defect violated and the correction restores):

- **S0** ⟺ `Σ = ∅` ⟺ no retrieved content supports any candidate claim (T1 §3.1 S0, unchanged).
- **S1** ⟺ `Σ ≠ ∅` ∧ ∃ a *cross-origin* material contradiction in `Σ` (T1 §3.1 S1 + §A4, unchanged).
- **S2** ⟺ `Σ ≠ ∅` ∧ ¬S1 ∧ `ios(selected_claim) = 1`. Under ¬S1, no material contradiction in `Σ` is
  across independent sources; hence "no material contradiction **across independent sources**" holds —
  which is exactly the **corrected** S2 clause (§3.1). And `ios(selected_claim) = 1` is "exactly one
  independent origin." So the corrected S2 definition is satisfied ⟺ this leaf.
- **S3** ⟺ `Σ ≠ ∅` ∧ ¬S1 ∧ `ios(selected_claim) ≥ 2`, matching the corrected S3 clause identically.

Because `selected_claim ∈ Σ` and `Σ = {c : ios(c) ≥ 1}`, in the ¬S0 ∧ ¬S1 branch we always have
`ios(selected_claim) ≥ 1`, so `ios ∈ {1} ∪ {≥2}` is a complete split — no third case. The four
corrected definitions thus **cover all inputs and overlap on none** (they are the labels of a total,
disjoint partition). In particular the Finding 1 witness (`Σ ≠ ∅`, same-origin material contradiction,
`ios(selected_claim) = 1`) now lands in S2 and **satisfies** the S2 definition (§4.3). Exhaustiveness
holds with no residual, contradiction-free region — which is precisely what was violated before.

### 5.3 Determinism preserved

Determinism depends only on the computed quantities `ios`, the §A1/§A2 selection and tie-break, the
§A4 predicates, and the §A3 cascade. The correction introduces **no new predicate, no new input, no
new constant**, and does not alter any of these — it edits descriptive prose only. The classifier
computes the identical function of `(query_text, snapshot)` before and after. Every key remains a pure
function of frozen artifacts (frozen snapshot, frozen `EVIDENCE_ORDERING_KEY`, deterministic PA-2
output; addendum §A2 rationale). Therefore identical `(query_text, snapshot)` ⇒ identical state,
selected_claim, and answer, exactly as before. **Determinism is preserved.**

### 5.4 Replay preserved

Replay integrity (T1 §7.2) requires the 22 seeds to yield byte-identical output and the manifest
identity-equality check (T1 §9.2) to hold. The correction changes no digest input (§5.5), so
`mechanism_id()` is unchanged; it changes no computed output (§5.3), so all 22 replicates remain
byte-identical to their pre-correction values. `adapter_id == mechanism_id()` still holds on replay,
and no manifest mismatch is introduced. The `seed` argument remains accepted-and-unused (T1 §7.2).
**Byte-identical replay is preserved.**

### 5.5 Digest semantics preserved

`frozen_constants_digest()` is SHA-256 over the ordered serialization of the T1 §5 register
(`MIN_INDEPENDENT_ORIGINS_FOR_S3`, `INDEPENDENCE_RELATION`, `SUPPORT_TEST_PARAMS`,
`CONTRADICTION_MATERIALITY_PARAMS`, `EVIDENCE_ORDERING_KEY`, `EXTRACTION_PARAMS`, `ANSWER_TEMPLATES`,
`SPEC_VERSION`, `PA3_RULESET_VERSION`) together with `STATE_TIER_MAP` and `CONFIDENCE_TIERS`
(T1 §6.1 / §A6-DIGEST). **None of these objects is edited by this correction** (§3.3). The corrected
clauses C1–C4 are *descriptive state definitions and semantic prose*, which are **not** digest inputs.

Moreover, `PA3_RULESET_VERSION` binds the mechanism-defining structural rules §A6-DIGEST (i)–(v):
precedence (§A3), selection (§A1), tie-break (§A2), S1 composition/anchoring (§A4), and seam
invariants (§A7). **All five are textually and operationally unchanged** — the correction touches none
of them; it only makes the S2/S3 *definitions* agree with rule (i)/(iv) as they already stand.
Therefore:

- the digest **inputs** are unchanged ⇒ `frozen_constants_digest()` yields the **same** hex string;
- `CONSTANTS_HASH` asserted-equality (T1 §6.1) stays **green**;
- **no `SPEC_VERSION` bump and no `PA3_RULESET_VERSION` bump** is required, because no digest-covered
  object and no §A6-DIGEST (i)–(v) rule changed.

This is exactly why Finding 1 qualifies as a **specification correction / erratum** and **not** a
CR-6/§11 mechanism change: §11 predicates a re-freeze on a change to a constant, to `support_tests.py`,
to `evidence_states.py`, to the templates, to the snapshot, or to the PA-1 ordering rule — the
operational objects. The corrected function over inputs is identical (§5.3), and a conformant
implementation of §A3 already emits the corrected behavior (§4.2), so **no such object changes**.
**Digest semantics are preserved.**

### 5.6 Minimality / uniqueness of the correction (why this is a correction, not a redesign)

Two candidate resolutions exist. (a) **Narrow S2/S3 definitions** to "no material contradiction across
independent sources" — the present correction: it leaves S1, precedence, selection, and every constant
untouched and preserves all operational behavior (§5.1–§5.5). (b) **Broaden S1** to fire on same-origin
material contradictions — this would *change* frozen behavior, because §A4 condition 3 explicitly
excludes them ("A lone source that self-contradicts is **not** S1"), so it would move the witness from
S2 to S1, alter emitted output, break replay, and force a `PA3_RULESET_VERSION` bump and re-freeze.
Option (b) is a **redesign** of a frozen rule and is out of scope by the mission and by CR-6. Option
(a) is therefore the **unique** behavior-preserving removal of the contradiction, and it is what this
document specifies.

---

## 6. Scope, non-scope, and out-of-scope observations

- **In scope (done):** removal of the C1–C4 vs {R1, R2} internal contradiction by conforming the S2/S3
  definitions and semantic arguments to the frozen operational precedence and S1 composition.
- **Not changed:** any state other than the S2/S3 *definitional wording*; any constant, digest input,
  identity string, precedence, selection, tie-break, S1 composition, or seam invariant.
- **Out of scope (explicitly not addressed here, by mission):** whether emitting `PROBABLE`/`CERTAIN`
  on a same-origin self-contradiction is the *desirable* honesty behavior is a **design question**.
  Changing it would alter frozen behavior and is a redesign/improvement — **forbidden by this
  mission**. The frozen mechanism's behavior on the witness (S2/S3 by `ios`) is preserved exactly; this
  document only makes the specification *self-consistent* about that behavior. No future improvement is
  proposed or implied.

---

## 7. Ratification (BLANK — rides the parent T1/G4 B2/B3)

This correction is an erratum to the T1/G4 freeze object's prose (C1–C4). It is digest-neutral,
identity-neutral, and replay-neutral (§5.4–§5.5), and therefore does not open a new `SPEC_VERSION` or
`PA3_RULESET_VERSION`. It becomes binding only when co-ratified under the parent object's sign-off
blocks (`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` Section 12). No approval is fabricated here.

- **B2 — ScientificAuditor (erratum concurrence, rides T1 §12 B2):** ____________________ , date: __________
- **B3 / G4 — ReleaseManager (applies C1–C4 edits at the pinned commit, rides T1 §12 B3):** ____________________ , pinned commit: ____________________ , date: __________

---

*End of A3.5 Finding 1 correction. Specification correction only — no implementation, no redesign, no
future improvements. Removes exactly one internal contradiction; every other frozen behavior preserved.*
