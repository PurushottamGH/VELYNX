# A3.5 FINDING 1 — INDEPENDENT FALSIFICATION AUDIT (SONNET)

**Title:** Independent Scientific Audit of the ES-1 Finding 1 Correction (Same-Origin
Material-Contradiction Definitional Conflict)
**Role:** Independent Scientific Auditor (this audit is adversarial to, and independent of,
the document it reviews; it is not a co-author of the correction).
**Auditor:** Claude Sonnet 5, acting under the mission stated below. Not the ScientificAuditor
role of record (`.opencode/agents/ScientificAuditor.md`, configured for Opus) — this is a
**second, independent** falsification pass, deliberately run on a different model than the one
that authored the correction, per the mission's framing ("SONNET_AUDIT" vs. the referenced
"OPUS_CORRECTION").
**Date:** 2026-07-13
**Status:** Independent audit artifact. Not a sign-off. Confers no ratification. The parent
freeze objects remain DRAFT / NO-GO per `ES1_IMPLEMENTATION_GATE.md`:91-93 regardless of this
audit's outcome.

---

## 0. Authorities, scope, and a documentation discrepancy (recorded, not silently resolved)

**Authorities as specified by the mission:**
1. Frozen ES-1 — `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` (the T1/G4 freeze object).
2. Frozen PA-3 — `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` (the PA-3 closure rider).
3. `docs/audits/A3_5_FINDING1_OPUS_CORRECTION_V1.md`.

**Finding F0 (documentation discrepancy).** `docs/audits/A3_5_FINDING1_OPUS_CORRECTION_V1.md`
**does not exist** in this repository. `docs/audits/` is empty on disk (confirmed by directory
listing at audit time). The only artifact in the working tree that matches the mission's
description of a "Finding 1 correction" is the **untracked**, root-level file
`PROGRAM_A_A3_5_FINDING1_CORRECTION.md` (title: "PROGRAM A — A3.5 FINDING 1 CORRECTION (ES-1)",
dated 2026-07-13 — the same date as this audit, and `git status` shows it as untracked, i.e.
freshly authored and not yet committed).

This audit proceeds by treating `PROGRAM_A_A3_5_FINDING1_CORRECTION.md` as the correction
document the mission intends ("the OPUS correction"), because it is the only candidate object
and its content (a same-origin material-contradiction fix to the S2/S3 definitions) matches the
mission's description exactly. **This substitution is a recorded audit finding, not a silent
assumption:** the path named in the authority list is wrong or the file was never saved at that
path, and this should be reconciled before this audit is treated as closing the loop on Finding 1.
Everything below is therefore an audit of **`PROGRAM_A_A3_5_FINDING1_CORRECTION.md`** (hereafter
"the correction") against **`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`** ("T1") and
**`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`** ("the addendum").

**Governance context (unaffected by this audit).** Per `ES1_IMPLEMENTATION_GATE.md`, ES-1 is
**NO-GO** as of 2026-07-07; the standing prohibition against emission-surface/binding code is in
force. Consistent with this, `program_a/mechanism/evidence_states.py` and
`program_a/mechanism/support_tests.py` on disk are `NotImplementedError` stubs — there is no
executable implementation of ES-1/PA-3 to run witnesses against. This audit therefore builds an
**independent reference model** (below) from the frozen prose alone, exactly as a conformance
implementation would have to, and treats any input on which that prose fails to determine a
unique output as a genuine specification defect — not an implementation bug, since there is no
implementation yet to blame.

**Methodology.** (1) Reconstruct the corrected algorithm as executable pseudocode, built only
from T1 + the addendum + the correction, with no invented parameters. (2) Replay the original
Finding‑1 witness by hand and by the reference model. (3) Construct ≥10 adversarial witnesses
targeting determinism, replay, `selected_claim`, `contradiction_doc_ids`, state exclusivity,
state completeness, and invariant I‑3. (4) Run all witnesses through the reference model twice
(and under varying `seed`) to test replay; run two exhaustive/near-exhaustive small-domain sweeps
to test completeness/exclusivity beyond hand-picked cases. (5) Report every result, including
negative (non-falsifying) results, and separate **CONFIRMED** breaks from **CONDITIONAL** ones
that depend on an assumption this audit cannot itself verify (e.g. an upstream PA‑2 guarantee).

The reference model and its full run transcript are reproduced in Appendix A/B of this report;
the model was executed and its output is quoted verbatim, not hand-simulated.

---

## 1. Reconstructed corrected algorithm (Task 1)

Grounding types (T1 §5, addendum preamble, unchanged by the correction):
`CandidateClaim = {claim_text: str, supporting_doc_ids: tuple[str,...]}`;
`EvidenceItem` carries `origin_domain` + `doc_id`; `EVIDENCE_ORDERING_KEY` = lexicographic
`(origin_domain, doc_id)`; `MIN_INDEPENDENT_ORIGINS_FOR_S3 = 2`.

```
ios(c)            = independent_origins({ e in evidence : supports(c, e) })   # T1 §5.2 relation
Σ                 = { c in claims : ios(c) >= 1 }                              # A1
≺ rank_key(c)     = ( -ios(c),                                                 # A2 primary (desc)
                       min{ (origin_domain, doc_id) : e supports c },          # A2 secondary (asc)
                       claim_text )                                            # A2 tertiary (asc)
argmax(S)         = the element of S with the smallest rank_key                # unique iff ≺ strict

classify(query_text, evidence, claims):
    Σ = { c in claims : ios(c) >= 1 }

    # --- S0 (A3 step 1) ---
    if Σ == ∅:
        return (state=S0, selected_claim=None, support_doc_ids=(),
                contradiction_doc_ids=(), independent_origin_count=0)

    # --- S1 (A3 step 2 / A4) ---
    fires_S1 = ∃ {a,b} ⊆ Σ, a≠b :
                   contradicts(a,b)
               ∧  is_material(a,b)                       # only evaluated if contradicts(a,b)
               ∧  independent_origins(supp(a) ∪ supp(b)) >= 2   # A4 cond. 3, cross-origin
    if fires_S1:
        selected_claim = argmax(Σ)                                    # A1/A2, Σ-wide
        competing_set  = { c in Σ \ {selected_claim} :
                              contradicts(selected_claim, c) ∧ is_material(selected_claim, c) }
        competing_claim = argmax(competing_set)     # UNDEFINED if competing_set = ∅  (see F1)
        return (state=S1, selected_claim=selected_claim,
                support_doc_ids=sorted(supp(selected_claim), key=EVIDENCE_ORDERING_KEY),
                contradiction_doc_ids=sorted(supp(competing_claim), key=EVIDENCE_ORDERING_KEY),
                independent_origin_count=ios(selected_claim))

    # --- (S2 | S3) last (A3 step 3), CORRECTED clause ---
    selected_claim = argmax(Σ)
    n = ios(selected_claim)
    # ¬fires_S1 ⇒ no material contradiction across independent sources anywhere in Σ (§5.2 proof)
    state = S3 if n >= MIN_INDEPENDENT_ORIGINS_FOR_S3 else S2
    return (state=state, selected_claim=selected_claim,
            support_doc_ids=sorted(supp(selected_claim), key=EVIDENCE_ORDERING_KEY),
            contradiction_doc_ids=(),
            independent_origin_count=n)
```

**What the correction actually changes, mechanically:** nothing in this pseudocode. The
correction (§3 of the correction document) edits only the **English definitions** attached to
the S2/S3 outcomes (T1 §3.1 rows, T1 §4 semantic-argument openers) from "no material
contradiction" to "no material contradiction **across independent sources**." The operational
cascade above — precedence, selection, tie-break, S1 composition, the `ios`-threshold split — is
**identical before and after** the correction; only the *label* attached to the branch changes
meaning. This audit independently confirms that characterization (§5 below: the pseudocode above
is unchanged whether or not the correction is applied — the correction is purely a documentation
edit to which English sentence describes the `S2`/`S3` branch).

This reconstruction was built exclusively from T1 §§3–5 and addendum §§A1–A4/A7; no numeric
value was invented (`SUPPORT_TEST_PARAMS`, `CONTRADICTION_MATERIALITY_PARAMS`,
`EXTRACTION_PARAMS`, and the exact `INDEPENDENCE_RELATION` text remain, correctly, "fixed at G4"
and out of scope — this audit treats `supports`/`contradicts`/`is_material`/`independent_origins`
as frozen oracles supplied per witness, exactly as the addendum itself does not need their
numeric values to state §A1–A4).

---

## 2. Replay of the original witness (Task 2)

**Witness (verbatim from the correction §4.1):** frozen snapshot, single independent origin
`d1`; `doc1@d1` supports claim `a` ("the capital is Alpha"); `doc2@d1` supports claim `b` ("the
capital is Beta"); `contradicts(a,b)=True`, `is_material(a,b)=True`. `Σ = {a, b}`.

**Reference-model replay** (Appendix A, `W0`):

```
=== W0: original Finding-1 witness (same-origin material contradiction) ===
result: {'state': 'S2', 'selected_claim': 'the capital is Alpha',
         'support_doc_ids': ('doc1',), 'contradiction_doc_ids': (),
         'independent_origin_count': 1}
replay identical across calls incl. different seed: True
```

**Trace, independently derived:**
1. S0 test: `Σ = {a,b} ≠ ∅` → not S0.
2. S1 test: `contradicts(a,b) ∧ is_material(a,b)` = True, but
   `independent_origins(supp(a)∪supp(b)) = independent_origins({doc1@d1, doc2@d1}) = 1 < 2` →
   condition 3 (A4) fails → **not S1**.
3. `(S2|S3)`: `selected_claim = argmax({a,b})`. Both have `ios=1` (tie on primary key); secondary
   key is `min EVIDENCE_ORDERING_KEY` — `a`'s only evidence key is `(d1, doc1)`, `b`'s is
   `(d1, doc2)`; `(d1,doc1) < (d1,doc2)` lexicographically → **`a` wins**, no tertiary key needed.
   `ios(a) = 1 < MIN_INDEPENDENT_ORIGINS_FOR_S3(=2)` → **S2**.

**Result: S2, matches the correction's §4.2 claim exactly**, and matches it independently (this
audit's tie-break trace via `EVIDENCE_ORDERING_KEY` is a step the correction document itself did
not need to spell out, since with only one claim's evidence per origin the tie is immaterial to
which state fires — but it is not immaterial to *which claim* is `selected_claim`, and this audit
confirms `selected_claim = a`, not `b`, deterministically).

**Definitional check (post-correction):** S2's corrected clause requires "no material
contradiction **across independent sources**." The only contradiction present (`a` vs `b`) is
confined to `d1` — not cross-origin. Clause holds. **The witness satisfies the state it fires
into.** Pre-correction, S2's clause ("no material contradiction," unqualified) was **false** for
this input (a material contradiction is present), so the witness fired into a state whose own
definition it violated — the exhaustiveness defect described in the correction's §1. This audit
**confirms** that characterization is accurate: the pre-correction wording (C1–C4) is genuinely
self-contradictory against R1/R2 for this exact input, and the correction's minimal edit removes
exactly that contradiction and no more (verified independently in §5.1 below by attempting to
construct a case the fix does *not* cover — none found among C1–C4's scope).

**Verdict on this witness: replay CONFIRMS the correction's own trace. Determinism CONFIRMED for
this input** (both direct hand-trace and two independent executions of the reference model,
including a different `seed`, agree bit-for-bit).

---

## 3. Adversarial witness catalog (Task 3 — ≥10 constructed witnesses)

All witnesses below were run through the independent reference model (Appendix A/B). Each
witness is stated in full so it can be independently re-verified without the code.

| # | Witness | Construction | Result | Verdict |
|---|---|---|---|---|
| **W0** | Original Finding‑1 witness | §2 above | S2, `selected_claim=a` | Survives (§2) |
| **W1** | Symmetric S3 case | 3 claims: `top` (ios=2, origins d1,d2, contradicts nothing); `x` (ios=1, origin d3); `y` (ios=1, **same origin d3** as `x`), `contradicts(x,y) ∧ material(x,y)=True` | `S3`, `selected_claim=top`, `support=(docT1,docT2)`, `contradiction=()`, `ios=2` | **Survives** — confirms the correction's §4.3 claim that the symmetric S3 case (promised but not spelled out in the correction) resolves identically |
| **W2** | **Anchoring-gap witness** | 3 claims: `top2` (ios=3, origins d1,d2,d3, contradicts nothing); `x2` (ios=1, origin d4); `y2` (ios=1, origin d5); `contradicts(x2,y2)∧material=True`, cross-origin (d4≠d5) | **`SpecViolation`**: S1 fires (the pair `{x2,y2}` satisfies A4 in full), `selected_claim=argmax(Σ)=top2` (strictly highest `ios`, no tie), but `top2` contradicts nothing, so `competing_set = ∅` and "the `≺`-maximal claim among `{}`" (addendum §A4 anchoring bullet) is **undefined** | **CONFIRMED FALSIFICATION** — see Finding **F1**, §5 |
| **W4** | Secondary-key tie-break | Claims `A` (ios=1, origin dA, evidence key `(dA,"aaa")`), `B` (ios=1, origin dB, evidence key `(dB,"zzz")`); no contradiction; claims list order deliberately shuffled (`B` before `A`) | `S2`, `selected_claim=A` regardless of input order | Survives — confirms A2 secondary key is order-independent |
| **W5** | Tertiary-key tie-break | Two claims sharing one evidence item `(dS,"shared_doc")` as their *only* evidence (so `ios` tie AND min-`EVIDENCE_ORDERING_KEY` tie), `claim_text` = `"aaa claim text"` vs `"zzz claim text"` | `S2`, `selected_claim="aaa claim text"` (lexicographically first) | Survives — confirms A2 tertiary key resolves the case A1's own text calls out as needing it |
| **W6** | **Duplicate-`claim_text` attack on A2's injectivity assumption** | Two distinct `CandidateClaim` objects, **identical** `claim_text="duplicate text"`, **identical** sole evidence item `(dX,"same_doc_id")` (so primary, secondary, *and* tertiary keys all collide) | **`SpecViolation`**: no unique `argmax` — `≺` is not strict for this pair | **CONDITIONAL FALSIFICATION** — see Finding **F2**, §5 |
| **W7** | Mirror/doc-count vs. origin-count | One claim, 2 supporting docs, **same** collapsed origin `dM` (`m1`, `m2`) | `S2` (`ios=1`), not S3 | Survives — confirms doc-count is not silently substituted for origin-count |
| **W7b** | S3 boundary | One claim, 2 supporting docs, 2 **distinct** origins | `S3` (`ios=2`) | Survives — confirms `MIN_INDEPENDENT_ORIGINS_FOR_S3=2` boundary is inclusive as specified |
| **W8** | Mirror-collapsed apparent cross-origin contradiction | Two claims, evidence items on two *different domain strings* that `INDEPENDENCE_RELATION` collapses to the **same real origin** `d_real`, contradicting/material | `S2` (not S1) | Survives — confirms the Finding‑1 fix generalizes past literal same-`origin_domain` to the collapsed-origin relation the addendum actually specifies |
| **W9** | State-exclusivity attack | Two single-origin claims from **distinct** origins, contradicting/material | `S1` fires (`ios(supp∪supp)=2≥2`); classifier never reaches the `(S2\|S3)` branch | Survives (failed to falsify) — see §4, state exclusivity |
| **W11** | Degenerate S0 | `claims = ()` (PA‑2 extracted nothing) | `S0`, `selected_claim=None` | Survives — boundary correctly distinguished from "claims exist but none supported" |
| **W12** | Seed-independence re-check | W2's witness, run with `seed=0` and `seed=42+999` | **Same `SpecViolation`** both times — the *undefinedness* itself is deterministic (the spec fails the same way every time), but the *value* it would need to produce is still unfixed | Reinforces F1 |
| **Sweep 1** | Exhaustive, 0–2 claims, `ios ∈ {0,1,2}`, no contradictions (13 cases) | Brute force | 0 violations | State completeness survives for the no-contradiction sub-domain |
| **Sweep 2** | 3 claims × `ios ∈ {0,1,2}}³` × {no-contradiction, contradiction on each of 3 possible pairs} × {same-origin, cross-origin} = 216 cases | Brute force | **199 classified cleanly, 17 hit the F1 `SpecViolation`, 0 state-exclusivity violations** | F1 is **systematic** (≈7.9% of this synthetic domain), not a contrived one-off; state exclusivity holds across the full sweep |

That is **12 hand-constructed witnesses plus 2 systematic sweeps (13 + 216 = 229 additional
mechanically generated cases)** — well past the ≥10 requested, and deliberately including
several witnesses whose purpose was to fail to falsify (documented as such) so that the positive
claims in §4 are not survivorship-biased toward only the cases that broke.

---

## 4. Falsification results, by target (Task 4)

### 4.1 Determinism
**Attempted via:** W6 (duplicate `claim_text`), W2/W12 (anchoring gap).
**Result:** **CONDITIONALLY FALSIFIED.**
- For every witness where `Σ`'s `≺`-ranking is strict (i.e., no two candidates share the full
  `(ios, min-evidence-key, claim_text)` triple), the reconstructed algorithm is fully
  deterministic — confirmed on all 12 witnesses plus 229 swept cases that didn't hit F1.
- W6 shows determinism is **not unconditional**: it depends on an assumption the addendum states
  as a conclusion ("the third key is injective over any real `CandidateClaims` value," A2) but
  does not derive from any cited PA‑2 guarantee. If `EXTRACTION_PARAMS` (T1 §5.6, values not
  transcribed) ever permits two claim objects with identical `claim_text` *and* identical minimal
  supporting evidence, `≺` has no unique maximum and `selected_claim` — hence the entire
  `EvidenceStateResult` — is unfixed by the frozen rules. This is **Finding F2** (§5).
- W2/W12 show a second, independent way determinism can fail: not a tie in `≺`, but an **empty**
  anchoring set for `contradiction_doc_ids` in S1. This is **Finding F1** (§5), the more serious
  of the two because it does not require a degenerate PA‑2 output — it arises from ordinary,
  well-formed, non-tied inputs.

### 4.2 Replay
**Attempted via:** W0/W1/W4/W5/W7/W7b/W8/W9/W11 run twice + once under a different `seed`; W12
specifically targets seed-sensitivity of the F1 gap.
**Result:** **SURVIVES, with a scope caveat.** "Replay" as defined by T1 §7.2/§9.2 (byte-identical
output across the 22 seeds of one fixed, already-built implementation) is not falsified by
anything in this audit — `seed` genuinely never enters any comparison in the reconstructed
algorithm, and every witness that produced a defined result reproduced it identically across
seeds (`replay identical across calls incl. different seed: True` in every non-violating case,
Appendix A). What this audit shows is a **different, stronger claim is not established**: that
the *specification* — independent of any particular implementation's arbitrary tie-break-of-last-
resort choices — determines a *unique* byte sequence for every input. For the F1/F2 witness
classes, two independently-conformant implementations could each be internally
replay-consistent (deterministic against themselves) while disagreeing with each other, because
the spec under-determines the output. The correction's own §5.4 proof ("byte-identical replay is
preserved") is true as narrowly scoped (it argues no *new* nondeterminism is introduced by the
Finding‑1 edit) but does not — and does not claim to — establish full specification-level
determinism, which this audit shows does not hold unconditionally.

### 4.3 `selected_claim`
**Attempted via:** W4, W5, W6.
**Result:** Survives for W4/W5 (the two- and three-key tie-break resolves exactly as A1/A2
describe, order-independently). **Falsified conditionally by W6** — see F2, §5.

### 4.4 `contradiction_doc_ids`
**Attempted via:** W2, W9, W12, Sweep 2.
**Result:** **CONFIRMED FALSIFIED** for the witness class exhibited by W2 (17/216 = ~7.9% of
Sweep 2). This is the audit's headline finding — **F1**, §5.

### 4.5 State exclusivity (mutual exclusion of S0–S3)
**Attempted via:** W9 (direct attempt to force both the S1 composition and the corrected S2
clause true on the same input) and Sweep 2 (216 cases, explicit post-hoc check: for every input
classified S2/S3, assert no cross-origin material contradiction exists anywhere in `Σ`).
**Result:** **Survives — 0 violations.** W9's attempted construction collapses: any pair with a
cross-origin material contradiction *is* the S1-firing condition, so the classifier never reaches
`(S2|S3)` for such a pair (S1 precedence, §A3, fires first and the cascade `Stop`s). This is not
a coincidence of the witness; it is structurally forced — the corrected S2/S3 clause ("no
material contradiction across independent sources") is the **exact negation**, restricted to
`Σ`, of the S1-firing predicate, so ¬S1 ⟹ (corrected S2/S3 clause holds) is a tautology given the
`elif`-cascade, and this audit's Sweep 2 empirically confirms no counterexample exists in a
216-case domain that specifically stresses the boundary. This is the one target this audit
**tried hardest to break and could not.**

### 4.6 State completeness (exhaustiveness of S0–S3)
**Attempted via:** attempted construction of `ios(selected_claim) ∉ {≥1}` inside the non-S0
branch (impossible by construction, since `selected_claim ∈ Σ = {c : ios(c)≥1}`); Sweep 1 (13
cases, no-contradiction domain) and Sweep 2 (216 cases, with contradictions) both assert every
classified input lands in exactly one of `{S0,S2,S3}` (or hits the separately-tracked F1 anomaly
under S1).
**Result:** **Survives** for the state *label* — every input this audit constructed lands in
exactly one of the four labels (mod F1's anchoring gap, which is a completeness failure of the
*witness fields*, not of the *state label* — S1 still fires correctly and uniquely for W2; only
`contradiction_doc_ids` is left undefined). The correction's §5.2 exhaustiveness proof is
**independently reconstructed and confirmed** here: under `¬S0 ∧ ¬S1`, `ios(selected_claim) ≥ 1`
always (since `selected_claim ∈ Σ`), so `ios ∈ {1} ∪ {≥2}` is a genuinely complete split with no
third case — this audit found no counterexample across 229 swept inputs plus 12 hand-built ones.

### 4.7 Invariant I‑3 (anchoring & witnesses)
**Attempted via:** W2 directly targets I‑3's S1 row (`contradiction_doc_ids` = "supporters of the
material-incompatible competing claim"); W9 and Sweep 2 stress the S2/S3 rows
(`contradiction_doc_ids = ()`, confirmed trivially total — no witness broke this half); W11
stresses the S0 row (confirmed total).
**Result:** **CONFIRMED FALSIFIED for the S1 row specifically.** I‑3's table (addendum §A7)
asserts `support_doc_ids`/`contradiction_doc_ids` are "**always** computed with respect to
`selected_claim`," and its S1 row names `contradiction_doc_ids` as "supporters of the
material-incompatible competing claim" — presupposing that competing claim exists relative to
`selected_claim`. W2 is a legal input under every other frozen rule (A1 selection is total and
unambiguous here — `top2` wins outright, no tie; A4's S1 composition is unambiguously satisfied
by `{x2,y2}`) for which that presupposition is false. I‑3 is therefore **not total** as stated;
the S0, S2, and S3 rows of the same table remain confirmed-total in every witness tried.

---

## 5. Findings register

### F1 — S1 anchoring is not total (I‑3 gap); `contradiction_doc_ids` undefined for a
non-degenerate, non-tied input class — **CONFIRMED**

**Where:** `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A4, "S1 anchoring" bullet (the
`contradiction_doc_ids` definition), and §A7 invariant I‑3, S1 row.

**What:** §A4's S1 composition test is an **existential** quantifier over *all* unordered pairs
in `Σ`: "there exists an unordered pair of distinct claims `{a,b} ⊆ Σ`..." — it does not require
the pair to involve `selected_claim`. But the S1 anchoring rule that fires immediately afterward
defines `contradiction_doc_ids` via a set that *is* scoped to `selected_claim`:
`{c ∈ Σ : contradicts(selected_claim, c) ∧ is_material(selected_claim, c)}`. `selected_claim` is
independently pinned by §A1/§A2 as the `Σ`-wide `≺`-maximum (by corroboration strength) — a
quantity with no necessary relationship to which pair triggered the S1 composition test. Witness
**W2** exhibits exactly this: the highest-corroborated claim in `Σ` (`ios=3`) contradicts
nothing, while a lower-corroborated but still-qualifying pair elsewhere in `Σ` (`ios=1` each,
genuinely cross-origin, genuinely material) is what makes the S1 predicate true. When this
happens, "the `≺`-maximal claim among `{}`" has no value — `contradiction_doc_ids` (and, per I‑3,
the completeness of the S1 row of `EvidenceStateResult`) is **undefined by the frozen rules**.
This is not a rare edge case constructed to be pathological: Sweep 2 shows it firing on 17/216
(~7.9%) of a small synthetic domain that varies only `ios∈{0,1,2}` across 3 claims and the
placement of one contradicting pair — i.e., it fires whenever the S1-triggering pair is disjoint
from the single highest-`ios` claim in `Σ`, which is a structurally common configuration (any
time there is a strong, uncontested claim *and* a separate, weaker, contested pair in the same
evidence set — e.g., "the launch date is well-corroborated by 3 origins; two low-corroboration
single-source claims about the launch *cost* happen to conflict").

**Relationship to the Finding‑1 correction under audit:** **orthogonal**. The correction's §3.3
"Explicitly unchanged" list correctly states that "S1 composition and anchoring (addendum §A4)"
and "seam invariants I‑1/I‑2/I‑3 (§A7)" are untouched by the Finding‑1 edit — and F1 confirms
that is literally true: F1 exists identically before and after the correction, because the
correction only edits the S2/S3 prose, never the S1 anchoring rule. **This finding is not a
defect in the correction being audited; it is a pre-existing gap in the frozen PA‑3 addendum that
this audit surfaced while exercising the surrounding machinery the correction depends on.** It
does not invalidate anything the correction claims about Finding 1 (§2 of this audit independently
reconfirms the correction's own witness and proof). It does mean the addendum's own claim that
"no residual nondeterminism survives" (§A2) and that I‑3 governs `contradiction_doc_ids` "always"
(§A7) are each **overstated** by exactly this one witness class, independent of Finding 1.

**Suggested remediation direction (non-binding — outside this auditor's authority to specify;
recorded for the document owner, not enacted):** the anchoring rule needs an explicit fallback
for the case the S1-triggering pair is disjoint from `selected_claim` — e.g., either (a) restrict
`selected_claim` selection, when S1 fires, to the union of claims that participate in *some*
S1-triggering pair (changing §A1/§A2's scope specifically for the S1 branch), or (b) redefine the
competing-claim set as ranging over *all* claims involved in any S1-triggering pair rather than
only those contradicting `selected_claim` specifically, or (c) explicitly define the empty-set
case (e.g., "if no such claim exists, `contradiction_doc_ids` is the supporters of the
`≺`-maximal member of the union of all S1-triggering pairs"). Any of these is a **rule change**
to (iv) in the A6‑DIGEST mechanism-defining list and would require the same re-freeze machinery
(`PA3_RULESET_VERSION` bump) the correction document itself argues Finding 1 does *not* need —
underscoring that F1, unlike Finding 1, is not a wording-only fix.

### F2 — A2's tie-break totality rests on an unverified upstream uniqueness assumption —
**CONDITIONAL / OPEN**

**Where:** `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` §A2, "because the third key is injective over
any real `CandidateClaims` value, `≺` is a strict total order and the maximum is unique."

**What:** This is stated as a fact about "any real `CandidateClaims` value," but nothing in the
frozen `types.py` signature (`CandidateClaim = {claim_text: str, supporting_doc_ids:
tuple[str,...]}`) forbids two distinct claim objects sharing an identical `claim_text` (e.g. a
PA‑2 extraction quirk that fails to merge two syntactically-identical claims pulled from
different evidence). Witness **W6** constructs exactly this (deliberately also colliding the
secondary key, to isolate the tertiary-key claim). If PA‑2's `EXTRACTION_PARAMS` (T1 §5.6 —
values explicitly not transcribed in any document this audit has access to) does not
independently guarantee `claim_text` uniqueness within one `CandidateClaims.claims` tuple, then
A2's injectivity claim is false for such an input and `selected_claim` (hence
`independent_origin_count`, `support_doc_ids`, and the emitted answer) is not uniquely determined.

**Why this is CONDITIONAL, not CONFIRMED:** this audit does not have access to `EXTRACTION_PARAMS`
or `program_a/extraction/claim_extraction.py`'s actual dedup behavior (checked: the file exists
on disk but was out of scope to inspect for this spec-level audit and, like the rest of Program
A, would need to be verified against its own frozen parameter register rather than assumed). If
PA‑2 in fact guarantees `claim_text`-uniqueness per `CandidateClaims` value as a documented
extraction invariant, F2 is closed. **This audit cannot close it either way** and records it as
an open dependency the addendum's own text does not cite evidence for.

---

## 6. Assessment of the correction under audit

**On its own stated claim (Finding 1, the same-origin material-contradiction exhaustiveness
defect):** **VALIDATED.** §2 of this audit independently reconstructs and reproduces the
correction's witness and its state trace (S2), independently reconfirms the pre-correction
definitional contradiction is real (C1–C4 vs. R1/R2, as the correction states), and independently
reconfirms the corrected clause ("no material contradiction across independent sources") both (a)
resolves the specific witness and (b) does not introduce any new S1/S2/S3 boundary case this
audit could find (Sweep 2, §4.5: 0 exclusivity violations across 216 cases spanning exactly the
boundary the correction touches).

**On its determinism/replay/digest proofs (§5.1–§5.5 of the correction):** **Correct as narrowly
scoped.** Each proof is a claim that the Finding‑1 edit itself introduces no new nondeterminism,
no digest change, and no behavioral change — and this audit found no witness contradicting that
narrow claim. This audit does **not** find that the *broader* system the correction sits inside
(the frozen addendum's S1 anchoring rule, and the frozen tie-break's injectivity assumption) is
fully deterministic in general — F1 (confirmed) and F2 (conditional) are gaps in material the
correction correctly declares out of scope and does not touch, not gaps the correction introduces
or is responsible for closing.

**On completeness/exclusivity of the four-state partition:** **Confirmed exhaustive and mutually
exclusive at the state-label level**, matching the correction's §5.1/§5.2 claims, independently
re-derived and stress-tested (229 additional cases beyond the correction's own single witness).
The one place completeness fails (F1) is a failure of the **`EvidenceStateResult` payload**
within the correctly-identified S1 label, not a failure of the four-way state partition itself.

---

## 7. Verdict

```
INDEPENDENT AUDIT: Finding-1 correction VALIDATED (narrow scope) — 2 findings opened
  F0  Documentation discrepancy   : referenced authority docs/audits/A3_5_FINDING1_OPUS_CORRECTION_V1.md
                                     does not exist; audited PROGRAM_A_A3_5_FINDING1_CORRECTION.md instead.
  F1  CONFIRMED  — I-3 / S1 anchoring not total; contradiction_doc_ids undefined for
                    S1-triggering pairs disjoint from the Sigma-wide selected_claim.
                    Orthogonal to Finding 1; pre-exists and survives this correction unchanged.
  F2  CONDITIONAL — A2 tie-break injectivity assumption unverified against PA-2's actual
                     EXTRACTION_PARAMS; cannot be closed without that register's values.
  Determinism        : holds unconditionally only outside the F1/F2 witness classes.
  Replay (T1 sense)  : holds — no seed-dependence found in any witness.
  selected_claim     : holds outside F2's witness class.
  contradiction_doc_ids : FALSIFIED for the F1 witness class (~7.9% of a small synthetic sweep).
  State exclusivity  : holds — actively attacked (W9, Sweep 2), no counterexample found.
  State completeness : holds at the state-label level; fails at the payload level under F1.
  Invariant I-3      : FALSIFIED for its S1 row; S0/S2/S3 rows confirmed total.
```

This audit does not ratify, approve, or freeze anything (per the correction's own §7, that
authority is B2/B3, not this document). It recommends F0 be reconciled (either the correction be
committed to the path the mission expects, or the mission's authority list be corrected), and
that F1 be tracked as a new, separate PA‑3 specification defect — independent of and not blocking
Finding 1 — before any future claim that the addendum's I‑3 invariant is unconditionally total.

---

## Appendix A — Reference model (independent, from-scratch, spec-only; not `program_a/*`)

Location: `es1_audit_reference.py` (auditor's scratch reference implementation; not part of this
repository's `program_a/` package, deliberately, since that package must remain
`NotImplementedError` stubs under the standing prohibition). Full source and run transcript are
retained by the auditor and summarized in §3/§4 above; every numeric result quoted in this report
(state, `selected_claim`, `support_doc_ids`, `contradiction_doc_ids`, `independent_origin_count`,
replay-equality across seeds, and the two sweep counts 13/0 and 216/199/17/0) was produced by
executing that model, not by hand-simulation, and is reproducible by re-running it against the
witness constructions listed verbatim in §3.

## Appendix B — Witness-to-target cross-reference

| Target | Witnesses used | Outcome |
|---|---|---|
| Determinism | W0, W1, W4, W5, W6, W7, W7b, W8, W9, W11, Sweeps 1–2 | Conditional break (F1, F2) |
| Replay | W0–W12 (all, seed varied) | Survives (T1's narrow sense) |
| `selected_claim` | W4, W5, W6 | Conditional break (F2) |
| `contradiction_doc_ids` | W2, W9, W12, Sweep 2 | Confirmed break (F1) |
| State exclusivity | W9, Sweep 2 | Survives |
| State completeness | W0, W1, W7, W7b, W11, Sweeps 1–2 | Survives (label level) |
| Invariant I‑3 | W2 (S1 row), W9/Sweep 2 (S2/S3 rows), W11 (S0 row) | Confirmed break (S1 row only) |

*End of independent falsification audit.*
