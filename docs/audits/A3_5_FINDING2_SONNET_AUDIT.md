# A3.5 FINDING 2 — INDEPENDENT FALSIFICATION AUDIT (SONNET)

**Title:** Independent Scientific Audit of the ES-1 Finding 2 Correction (S1 Anchoring
Totality Gap / `contradiction_doc_ids` Fallback)
**Role:** Independent Scientific Auditor (adversarial to, and independent of, the document
under review; not a co-author of the correction).
**Auditor:** Claude Sonnet 5, acting under the mission stated below — a second, independent
falsification pass over `PROGRAM_A_A3_5_FINDING2_CORRECTION.md` ("the correction"), on the
same model family as, but a fresh instance from, `docs/audits/A3_5_FINDING1_SONNET_AUDIT.md`
("the prior audit").
**Date:** 2026-07-13
**Status:** Independent audit artifact. Not a sign-off. Confers no ratification. The parent
freeze objects remain DRAFT / NO-GO per `ES1_IMPLEMENTATION_GATE.md`:91-93 regardless of this
audit's outcome.

---

## 0. Authorities, scope, and mission

**Authorities as specified by the mission (only these):**
1. Frozen ES-1 — `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` ("T1").
2. Frozen PA-3 — `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` ("the addendum").
3. `docs/audits/A3_5_FINDING1_SONNET_AUDIT.md` ("the prior audit").
4. `PROGRAM_A_A3_5_FINDING2_CORRECTION.md` ("the correction").

Note: `PROGRAM_A_A3_5_FINDING1_CORRECTION.md` (the Finding-1 correction document itself) is
**not** in this mission's authority list. It is read here only incidentally, insofar as the
correction's own §5.2 orthogonality proof cites it and the prior audit quotes it; no clause of
it is re-adjudicated by this audit.

**Mission (verbatim intent):** attempt to falsify the Finding 2 correction. Replay the
original witness, the Finding-1 witness, and the Finding-2 witness. Construct ≥10 additional
adversarial witnesses. Attempt to falsify: determinism, replay, state completeness, state
exclusivity, `selected_claim`, `contradiction_doc_ids`, and invariant I-3. Return
PASS / FAIL / UNDECIDABLE, and, if FAIL, a complete audit artifact.

**On witness naming.** The document trail names witnesses inconsistently across documents, so
this audit resolves the mission's three replay targets explicitly:
- **"original witness"** = the Finding-1 correction's witness (`PROGRAM_A_A3_5_FINDING1_CORRECTION.md`
  §4.1: same-origin material contradiction, "capital is Alpha/Beta"). Called **W0** below.
- **"Finding 1 witness"** = the prior audit's own finding, labeled **F1** in its findings
  register (§5) and exhibited by its witness **W2** (the S1-anchoring-gap witness).
- **"Finding 2 witness"** = the correction's own witness, which **is W2 verbatim**
  (`PROGRAM_A_A3_5_FINDING2_CORRECTION.md` §1.1: "the witness (verbatim from the audit, W2 /
  F1)"). The prior audit's "Finding 1" (its F1 findings-register entry) and the correction's
  "Finding 2" (its title) are the **same witness, same defect**, referenced by two names because
  the correction is itself the remediation of the prior audit's F1. This audit therefore
  replays **W0** and **W2** — both, satisfying all three named replay targets.

**Governance context (unaffected by this audit).** ES-1/PA-3 remains DRAFT / NO-GO; no
executable `program_a/mechanism/*` implementation exists. This audit builds an independent
reference model from the frozen prose plus the correction's proposed §3.1 fallback, exactly as
a conformance implementation would have to.

**Methodology.** (1) Build an executable reference model implementing T1 + the addendum +
the correction's corrected D1 anchoring rule (§3.1), with no invented parameters, as two
variants: `classify_pre_finding2` (frozen, unmodified D1 — reproduces the undefined result) and
`classify_post_finding2` (the corrected D1 with the Comp/Part fallback). (2) Replay W0 and W2
under both variants. (3) Construct ≥10 adversarial witnesses targeting the seven named
falsification targets, executed (not hand-simulated) against the reference model, including
seed variation, claim-list-order shuffling, and one systematic sweep to test whether any
confirmed defect is a knife-edge point or a reachable, systematic class. (4) Report every
result, separating CONFIRMED breaks from CONDITIONAL ones.

The reference model, witness suite, and sweep are retained as three scratch files (not part of
`program_a/`, per the standing prohibition): `es1_finding2_audit_reference.py`,
`es1_finding2_audit_witnesses.py`, `es1_finding2_audit_sweep.py` (repository root). Every
numeric result quoted below was produced by executing them; the full transcripts are
reproduced in Appendix A.

---

## 1. Reconstructed corrected algorithm (Task 1)

Built from T1 §§3–5, addendum §§A1–A4/A7, and the correction's §3.1 replacement text, no
numeric value invented:

```
ios(c)  = independent_origins({e in evidence : supports(c,e)})
Sigma   = {c in claims : ios(c) >= 1}
rank_key(c) = (-ios(c), min EVIDENCE_ORDERING_KEY over supp(c), claim_text)   # A2
argmax(S)   = unique minimum of rank_key over S (raises if S has a full-key tie)

classify(claims):
  Sigma = {c in claims : ios(c) >= 1}
  if Sigma == {}: return S0, None, (), (), 0

  firing_pairs = [{a,b} subset Sigma : contradicts(a,b) & is_material(a,b)
                      & independent_origins(supp(a) | supp(b)) >= 2]        # A4 conds 1-3
  if firing_pairs:
      selected_claim = argmax(Sigma)                                        # A1/A2, Sigma-wide
      Comp = {c in Sigma \ {selected_claim} :
                 contradicts(selected_claim,c) & is_material(selected_claim,c)}   # D1, UNCHANGED
      if Comp != {}:
          competing = argmax(Comp)                          # ORIGINAL frozen branch, verbatim
      else:
          Part = union of all claims in any firing_pairs member              # NEW, Finding-2 §3.1
          competing = argmax(Part)                           # the correction's fallback
      return S1, selected_claim, sorted(supp(selected_claim)),
                 sorted(supp(competing)), ios(selected_claim)

  selected_claim = argmax(Sigma)
  n = ios(selected_claim)
  return (S3 if n>=2 else S2), selected_claim, sorted(supp(selected_claim)), (), n
```

This matches the correction's §3.1 text exactly: the `Comp ≠ ∅` branch is verbatim-preserved
("the original frozen rule, unchanged"); only the `else` branch (`Part`) is new. No new
predicate, no new numeric constant — confirmed by inspection of the reconstruction (it reuses
only `contradicts`, `is_material`, `independent_origins`, `≺`, all already frozen).

---

## 2. Replay of the original / Finding-1 / Finding-2 witnesses (Task 2)

### 2.1 W0 — "original witness" (Finding-1 correction §4.1)

Same-origin material contradiction (`a`/`b`, both evidenced only from origin `d1`). S1 never
fires here (§A4 cond. 3 fails — same origin), so Finding 2 (which only edits the S1 branch)
cannot touch this witness. Replayed under both variants, plus seed=999 and a shuffled claim
order:

```
pre-F2  : state=S2, selected_claim='a', support=(('d1','doc1'),), contradiction=(), ios=1
post-F2 : state=S2, selected_claim='a', support=(('d1','doc1'),), contradiction=(), ios=1
post-F2(seed=999)   : identical
post-F2(shuffled)   : identical
```

**Result: CONFIRMED unaffected by Finding 2**, exactly as the correction's §3.3 "Explicitly
unchanged" list and §5.2 orthogonality proof claim. This witness cannot distinguish the two
rule versions by construction (it never reaches the edited branch) — it is included for
completeness, not because it stresses Finding 2.

### 2.2 W2 — "Finding 1 witness" / "Finding 2 witness" (prior audit F1 = correction's own witness)

`top2` (ios=3, contradicts nothing) plus a disjoint, cross-origin, materially contradicting
pair `{x2, y2}` (each ios=1). Replayed under both variants, plus seed=42 and a shuffled order:

```
pre-F2  : state=S1, selected_claim='top2', support=supporters(top2) [3 items],
          contradiction_doc_ids = UNDEFINED (argmax over empty Comp), ios=3
post-F2 : state=S1, selected_claim='top2', support=supporters(top2) [3 items],
          contradiction_doc_ids=(('d4','e4'),) [supporters of x2], competing_claim='x2',
          branch='Part', comp_nonempty=False, ios=3
post-F2(seed=42)     : identical
post-F2(shuffled)    : identical (firing_pairs re-derived identically regardless of list order)
```

**Result: the pre-F2 replay independently reproduces the exact falsification the prior audit
reported (F1) — `contradiction_doc_ids` genuinely undefined by the frozen rule.** The post-F2
replay independently reproduces the correction's own claimed fix (§4 of the correction) exactly:
Comp is empty, the Part fallback fires, `competing_claim ∈ {x2, y2}` (this run picked `x2`, tied
on `ios=1`, decided by the §A2 secondary key — `x2`'s evidence key `('d4','e4')` sorts before
`y2`'s `('d5','e5')`, matching the correction's own §4 trace), and the result is
order/seed-independent.

**Verdict on the two replayed witnesses: both CONFIRM the documents' own claimed traces
exactly.** No discrepancy found in either replay. This closes out the mission's three named
replay targets.

---

## 3. Adversarial witness catalog (Task 3 — 11 constructed witnesses + 1 sweep)

All witnesses were executed against `classify_post_finding2` (Appendix A). Each is stated in
full for independent re-verification.

| # | Witness | Construction | Result | Verdict |
|---|---|---|---|---|
| **A1** | **Decoy-Comp witness** (headline finding) | `top4` (ios=1, origin `a1`) has a same-origin material contradiction with a decoy `z4` (also origin `a1` — NOT S1-qualifying on its own, cond. 3 fails); *disjoint*, genuinely S1-firing cross-origin pair `{x4,y4}` (origins `b1`/`c1`) fires S1 | `state=S1`, `selected_claim='top4'`, **branch='Comp'**, `competing_claim='z4'` (the decoy), `firing_pairs=[('x4','y4')]`, `selected_is_true_s1_participant=False` | **CONFIRMED FALSIFICATION** — see Finding **F3**, §5 |
| **A2** | Part tie-break, 4 participants across 2 firing pairs | `topB` (ios=2, wins selection outright); two disjoint firing pairs `{p1,q1}`,`{p2,q2}`, all ios=1, secondary-key ordering decides the Part winner | `S1`, `branch='Part'`, winner=`p1` (lexicographically earliest evidence key among all 4 Part members) | Survives — Part resolves via the frozen §A2 order exactly like Σ-wide selection |
| **A3** | **Part full-tie (F2-class) attack** | Comp empty; two Part members (`r1`,`r2`) share **identical** `claim_text` **and** identical minimal evidence key (full 3-key collision) | `TieError`: no unique `argmax(Part)` | **CONDITIONAL FALSIFICATION** — extends the prior audit's **F2** to the new `Part` construct (**F2′**, §5) |
| **A4** | Multiple disjoint firing pairs, Part aggregation | `topD` (ios=3); two disjoint firing pairs `{u1,u2}`,`{v1,v2}` — the *second* pair is textually later but its members are not the Part winner | `S1`, `branch='Part'`, `firing_pairs=[('u1','u2'),('v1','v2')]`, winner=`u1` (global min evidence key across the **union** of both pairs) | Survives — confirms Part unions participants from *every* firing pair, not just one |
| **A5** | Order-independence / shuffle | W2 and A1 witnesses, claim list shuffled 3–4 ways each | All permutations produce identical core output | Survives — A1/A2 are pure functions of `Σ` content, not list position |
| **A6** | Seed-independence replay on the A1 decoy | A1 witness, `seed ∈ {None,0,1,42,999999}` | Identical output across all seeds | Survives — the A1 **defect is not a nondeterminism defect**: the wrong-per-intent answer is reproducibly, deterministically wrong |
| **A7** | State-exclusivity attack | All witnesses above, checked post-hoc: does any input reach S1 *and* satisfy the `(S2\|S3)` ios-split, or vice versa, now that Comp/Part exist? | 0 violations across 5 distinct witness families | Survives — `elif`-cascade structurally forecloses this; Comp/Part are computed only *inside* an already-fired S1 branch |
| **A8** | `selected_claim` integrity | A1 and A4: confirm Part's argmax (evaluated over a *different*, smaller set than `Σ`) never overwrites or leaks into `selected_claim` | `selected_claim` = `Σ`-wide `argmax` in every case (`top4`, `topD`) | Survives — the two argmax computations are correctly kept separate |
| **A9** | Empty-Part impossibility attempt | Deliberate attempt, across every witness constructed, to find an S1-firing input with `Part = ∅` | No such input found; `Part` is by construction the member-set of the firing pairs, hence never empty when `firing_pairs ≠ ∅` | Survives — independently reconfirms the correction's §5.1 algebraic proof |
| **A10** | Derived invariant stress test | `contradiction_doc_ids ≠ () ⟺ state=S1`, checked across all witnesses incl. the A1 decoy and A2 Part-tie cases | Holds in every case, including A1 | Survives |
| **A11** | **I-3 restated-preamble literal check** | For every S1-firing witness (W2, A1, A2, A4): does `Comp ≠ ∅` (the correction's §3.2 proxy) coincide with "`selected_claim` is a genuine member of some firing pair" (the actual property the §3.2 preamble claims `Comp ≠ ∅` to *mean*)? | **Mismatch found: A1** — `Comp ≠ ∅` is `True`, but `selected_claim` participates in **zero** firing pairs | **CONFIRMED FALSIFICATION** of the corrected I-3 preamble — same root defect as F3 |
| **Sweep** | Systematicity of A1's defect class | Part 1: vary `ios(selected_claim) ∈ {1,2,3,4}` with a forced decoy edge, 300 trials each, measure conditional pathology rate among S1-firing trials. Part 2: fix `ios=1`, randomize decoy-edge presence (p=0.5) and a random trigger-graph among 5 peripherals (edge p=0.30), 2000 trials | Part 1: **100% pathological at `ios=1` (296/296 fired)**, **0% at `ios∈{2,3,4}` (0/900 fired)**. Part 2: **48.1% of S1-firing trials pathological (928/1928)** | Confirms **F3 is exactly the `ios(selected_claim)=1` regime**, and — within that regime — a **systematic**, not knife-edge, class |

That is **11 hand-constructed witnesses plus 1 systematic sweep (2,300 additional mechanically
generated trials across the sweep's two parts)** — past the ≥10 requested, deliberately
including several witnesses whose purpose was to attempt (and fail) to falsify, so the positive
findings are not survivorship-biased.

---

## 4. Falsification results, by target (Task 4)

### 4.1 Determinism
**Attempted via:** A3 (Part full-tie), A6 (seed replay on the decoy).
**Result: CONDITIONALLY FALSIFIED, in exactly the same way the prior audit's F2 already was —
now extended to a new construct.** A3 shows the corrected rule's *new* `Part` fallback inherits
the same unresolved dependency the prior audit flagged for the *original* `Σ`-wide `argmax`
(F2: unverified `claim_text`-uniqueness assumption, addendum §A2). This is not a new root cause,
but it is a **new attack surface** the correction introduces (`Part` did not exist before
Finding 2) without discharging the dependency. Outside the F2/F2′ tie class, and outside the
A1/F3 class, determinism (as pure-function reproducibility) holds — confirmed on every other
witness plus 2,300 swept trials.

### 4.2 Replay
**Attempted via:** W0/W2 (§2) plus A1, A5, A6, all run under varied `seed` and shuffled claim
order.
**Result: SURVIVES.** Every witness that produced a *defined* result (including the A1 decoy,
which is semantically wrong but not undefined) reproduced byte-identically across seeds and
claim-list permutations. Replay in the T1 §7.2 narrow sense is not falsified by anything in
this audit, matching the correction's own §5.4 claim and the prior audit's finding that
`seed` never enters any comparison.

### 4.3 State completeness
**Attempted via:** direct S0-boundary check (empty `Σ`, and claims present but all `ios=0`);
A7's cross-check; every witness's state landing.
**Result: SURVIVES.** Every constructed input, including the F3 decoy class, lands in exactly
one of `{S0, S1, S2, S3}` at the state-*label* level. The Finding-2 correction changes no state
boundary (§3.3 of the correction, independently reconfirmed: `firing_pairs` truth value alone
still gates the `elif` cascade). Totality of the *payload* (Task per §5.1 of the correction) is
also independently reconfirmed for `contradiction_doc_ids` specifically — see §4.6 below — it is
now always *defined*; the F3 finding is about *correctness*, not *definedness*.

### 4.4 State exclusivity
**Attempted via:** A7, explicit post-hoc check across 5 witness families.
**Result: SURVIVES — 0 violations.** Structurally forced by the unchanged `elif`-cascade;
Comp/Part computation happens strictly inside the already-fired S1 branch, so it cannot open a
path into or out of `(S2|S3)`. This target was actively attacked and could not be broken,
matching the prior audit's finding for the pre-Finding-2 rule (§4.5 of the prior audit).

### 4.5 `selected_claim`
**Attempted via:** A8 (integrity check against Part's separate argmax), A1, A4.
**Result: SURVIVES.** `selected_claim` remains strictly the `Σ`-wide `argmax` in every
witness; the correction's claim (§3.3: "the fallback deliberately does not move it") is
independently reconfirmed. The prior audit's F2 (tie-break injectivity) remains the only known
way to break `selected_claim` itself, and it is unchanged/untouched by Finding 2 (confirmed:
Finding 2 never edits §A1/§A2).

### 4.6 `contradiction_doc_ids`
**Attempted via:** all 11 witnesses.
**Result: split.**
- **Totality: SURVIVES.** `contradiction_doc_ids` is defined (non-`UNDEFINED`) in every
  S1-firing witness constructed, including W2, A1–A4 — independently reconfirming the
  correction's §5.1 proof. The prior audit's F1 (the totality gap) is genuinely closed for every
  witness this audit could construct.
- **Correctness / faithfulness: CONFIRMED FALSIFIED.** The correction's own §4 closing claim —
  that the fixed field "carries the actual S1 debate (... the contradiction that *caused* S1 to
  fire)" — is false for the A1 witness class. There, `contradiction_doc_ids` is defined, unique,
  and deterministic, but it points to a same-origin, non-S1-qualifying decoy contradiction
  (`z4`) that has **nothing to do** with the pair that actually fired S1 (`{x4,y4}`). This is
  **Finding F3** (§5).

### 4.7 Invariant I-3
**Attempted via:** A11 directly; A1 is the underlying witness; W2/A2/A4 as non-falsifying
controls.
**Result: CONFIRMED FALSIFIED for the corrected preamble.** The correction's §3.2 restated I-3
preamble asserts: "`contradiction_doc_ids` is computed with respect to `selected_claim` **when**
`selected_claim` participates in the S1-triggering contradiction (`Comp ≠ ∅`)" — i.e., it
equates `Comp ≠ ∅` with "`selected_claim` participates in the S1-triggering contradiction." The
A1 witness is a legal input, unambiguous under every other frozen rule, on which `Comp ≠ ∅` is
`True` while `selected_claim` participates in **zero** firing pairs (`A1` result:
`selected_is_true_s1_participant=False`). The equivalence the corrected preamble asserts is
**false**. The S0/S2/S3 rows and the derived seam invariant
(`contradiction_doc_ids ≠ () ⟺ state=S1`) remain confirmed-total in every witness tried (A10).

---

## 5. Findings register

### F3 — Corrected I-3 preamble / `contradiction_doc_ids` correctness: `Comp ≠ ∅` does **not**
imply `selected_claim` participates in the S1-triggering contradiction — **CONFIRMED**

**Where:** `PROGRAM_A_A3_5_FINDING2_CORRECTION.md` §3.1 (the parenthetical "if `Comp ≠ ∅` (the
S1-triggering contradiction involves `selected_claim`)"), §3.2 (the corrected I-3 preamble,
same equivalence), and §4 (the closing claim that the fixed field "carries the actual S1
debate").

**What:** `Comp = { c ∈ Σ : contradicts(selected_claim, c) ∧ is_material(selected_claim, c) }`
(D1, **unchanged by Finding 2** — "This is the original frozen rule, unchanged") carries **no
independence/cross-origin filter**. It is populated by *any* material contradiction against
`selected_claim`, including a same-origin one that — exactly like the addendum's own "lone
source that self-contradicts is not S1" exclusion (§A4) — does **not** itself satisfy the
S1-firing predicate. Witness **A1** constructs exactly this: `selected_claim` (`top4`, `ios=1`)
has a same-origin material contradiction against a decoy (`z4`), populating `Comp`, while a
*disjoint*, unrelated, genuinely cross-origin pair (`{x4,y4}`) is what actually fires S1. The
corrected rule takes the `Comp`-branch (unchanged, by design) and returns the decoy's evidence
as `contradiction_doc_ids` — silently discarding the real S1 debate, which sits, unused, in
`Part`.

This directly falsifies two textual claims made **by the correction itself** (not inherited
from the addendum):
1. §3.1's parenthetical gloss on the `Comp ≠ ∅` branch — asserted as an explanation, not merely
   a label, and shown false by direct construction.
2. §3.2's corrected I-3 preamble, which promotes that same gloss into the invariant text itself.

**Relationship to Finding 1 / F1 / F2:** F3 lives in a code path (`Comp ≠ ∅`) that Finding 2
explicitly does **not** edit — it is a **pre-existing gap in the original frozen D1 rule**,
structurally analogous to how the prior audit's F1 was a pre-existing gap in the same addendum,
surfaced while exercising machinery Finding 2 depends on. It is **not** introduced by Finding
2's code change. It **is**, however, newly falsified by Finding 2's own **new prose** (§3.1/§3.2),
which makes an explanatory claim about the `Comp`-branch's meaning that was never asserted (and
so never falsifiable) in the original, pre-Finding-2 addendum text (which only made the
already-known-false blanket claim that I-3 holds "always," per the prior audit's F1).

**Algebraic characterization (sweep §3, Part 1 — 100%/0% split, not incidental):** the defect
is possible **if and only if** `ios(selected_claim) = 1`. Proof sketch: if `ios(selected_claim)
≥ 2`, then `supp(selected_claim)` alone already spans ≥2 distinct origins, so for *any* `c` with
`contradicts(selected_claim,c) ∧ is_material(selected_claim,c)`,
`independent_origins(supp(selected_claim) ∪ supp(c)) ≥ ios(selected_claim) ≥ 2` automatically —
i.e. every `Comp` member is automatically a genuine S1 co-participant with `selected_claim`
whenever `ios(selected_claim) ≥ 2`. The gap exists exactly in the `ios(selected_claim) = 1`
regime, which is also precisely the regime the original W0 (same-origin, lone-source
contradiction, Finding 1's own witness) lives in — F3 is what happens when **that** legal input
class **co-occurs** with a **second, unrelated, genuinely S1-firing pair** elsewhere in `Σ`.
Sweep Part 2 shows this co-occurrence is not rare when both conditions are independently
plausible: 48.1% of S1-firing trials in a synthetic 5-peripheral domain, given a 50% chance of
an unrelated same-origin decoy on the selected claim.

**Severity characterization:** this is **not** a determinism, replay, totality, state-label
completeness, state-exclusivity, or `selected_claim` defect — all of those were independently
attacked (§4) and survive. It is a **correctness/faithfulness defect in the corrected
`contradiction_doc_ids` value**, and a **direct falsification of the corrected I-3 invariant's
own restated text**, for a input class that is legal, reachable, deterministic, and — per the
sweep — not a measure-zero pathology.

**Suggested remediation direction (non-binding, outside this auditor's authority):** the
`Comp` set itself needs the same cross-origin/independence filter `Part` already correctly
carries — e.g. `Comp = { c ∈ Σ : contradicts(selected_claim,c) ∧ is_material(selected_claim,c) ∧
independent_origins(supp(selected_claim) ∪ supp(c)) ≥ 2 }`. Under this fix, A1's `Comp` becomes
empty (the `z4` pair is correctly excluded as non-S1-qualifying), the `Part` fallback
correctly fires, and `competing_claim` becomes a true S1 co-participant — restoring the
correction's own §3.1/§3.2/§4 claims to actually being true. This is a **strict subset edit** of
the same rule (iv) Finding 2 already touches, so it carries the same `PA3_RULESET_VERSION`
consequence Finding 2 already accepts (§5.5 of the correction) — it does not open a new class of
re-freeze cost.

### F2′ — `Part` argmax inherits F2's unverified tie-break-injectivity dependency — **CONDITIONAL / OPEN**

**Where:** `PROGRAM_A_A3_5_FINDING2_CORRECTION.md` §3.1, the `Part` fallback's `≺-maximal
element of Part` step.

**What:** The prior audit's **F2** (CONDITIONAL, still open) showed `argmax(Σ)` is not
provably unique because the addendum's §A2 injectivity claim ("the third key is injective over
any real `CandidateClaims` value") is asserted, not derived from any cited PA-2 guarantee.
`Part` is a **new** set the correction introduces, ranged over by the **same** `argmax`/`≺`
machinery. Witness **A3** constructs two `Part` members with fully colliding rank keys
(identical `claim_text` *and* identical minimal evidence key) and the reference model correctly
raises a tie error — `argmax(Part)` is exactly as undefined, on the same unverified assumption,
as `argmax(Σ)` already was.

**Why CONDITIONAL, not CONFIRMED:** identical to the prior audit's own F2 reasoning — this
audit has no access to PA-2's `EXTRACTION_PARAMS`/dedup behavior and cannot determine whether
such a duplicate is producible by a conformant PA-2 implementation. If PA-2 guarantees
`claim_text` uniqueness per `CandidateClaims` value, F2 (and its F2′ extension here) are both
closed; this audit cannot close it either way.

**Relationship to F2:** same root cause, new attack surface. Not a new open dependency — an
existing one, now doubly-instantiated. Finding 2's own §6 explicitly declares F2 "not addressed
... this correction does not have authority over and does not touch [it]" — that scope statement
remains accurate; F2′ shows the *scope* of what F2 leaves open grew slightly wider as an
unavoidable consequence of adding `Part`, without Finding 2 having introduced any new
independent risk.

---

## 6. Assessment of the correction under audit

**On its stated headline claim (totality of `contradiction_doc_ids` restored, §5.1):**
**VALIDATED.** Every S1-firing witness this audit constructed (11 hand-built + 2,300 swept)
produced a *defined* `contradiction_doc_ids`, confirming the fallback closes the prior audit's
F1 gap exactly as claimed, for every witness where the tie-break itself is well-posed (i.e.,
outside F2′).

**On Finding-1 orthogonality (§5.2):** **VALIDATED.** Independently reconfirmed — W0 is
provably untouched (§2.1), and no witness in this audit's suite exercises any C1–C4 clause.

**On determinism / replay / digest semantics (§5.3–§5.5), narrowly scoped to "does this edit
introduce new nondeterminism / break replay / silently drift the digest":** **VALIDATED**,
with the caveat (F2′) that the correction's `Part` construct inherits — rather than introduces —
a pre-existing open conditional dependency. `PA3_RULESET_VERSION`'s advancement (§5.5) remains
correctly reasoned: this audit's F3 finding, if remediated per the suggestion in §5, would live
in the *same* rule (iv) already flagged for the bump, so it changes no conclusion about digest
mechanics.

**On the correction's own explanatory and I-3-restatement text (§3.1 parenthetical, §3.2
preamble, §4 closing claim):** **FALSIFIED.** These are not narrow "does this specific edit
work" proofs (which is the mode in which §5.1–§5.5 survive) — they are affirmative claims about
what the *corrected rule as a whole* guarantees, and Finding F3 is a direct, constructed
counterexample to each of them.

**On state completeness/exclusivity, `selected_claim` integrity:** **Confirmed to survive**,
independently re-derived and actively attacked (§4.3–§4.5), matching the correction's implicit
assumptions.

**Net effect on the original W2/F1 witness:** unaffected by F3 — W2's own `top2` has `ios=3`, so
by the algebraic characterization above, W2's `Comp` is *correctly* empty and its `Part` result
is *correctly* the true debate. F3 is a **different, adjacent** input class from W2, not a
regression on W2 itself.

---

## 7. Verdict

```
INDEPENDENT AUDIT (Sonnet 5): Finding-2 correction — FAIL (scoped)

  Replay of "original witness" (W0)      : CONFIRMED — reproduces Finding 1's own trace; unaffected by Finding 2.
  Replay of "Finding 1 / Finding 2 witness" (W2) : CONFIRMED — reproduces both the pre-F2 undefined
                                            result and the correction's own claimed post-F2 fix, exactly.
  Totality (contradiction_doc_ids defined
    whenever S1 fires, Sec 5.1)          : SURVIVES — confirmed across 11 witnesses + 2300 swept trials.
  Determinism (Sec 5.3)                  : CONDITIONAL gap (F2', open) -- inherits, does not introduce, F2.
  Replay (T1 Sec 7.2 sense, Sec 5.4)     : SURVIVES -- no seed/order dependence found anywhere.
  Finding-1 orthogonality (Sec 5.2)      : SURVIVES -- independently reconfirmed.
  Digest semantics (Sec 5.5)             : SURVIVES -- PA3_RULESET_VERSION bump remains correctly reasoned.
  State exclusivity                      : SURVIVES -- actively attacked (A7), no counterexample.
  State completeness (state-label level) : SURVIVES -- S0 boundary + all witnesses checked.
  selected_claim                         : SURVIVES outside the pre-existing, untouched F2.
  contradiction_doc_ids (definedness)    : SURVIVES.
  contradiction_doc_ids (correctness / "carries the actual S1 debate", Sec 4) : FALSIFIED -- F3, CONFIRMED.
  Invariant I-3 (Sec 3.2 restated preamble) : FALSIFIED -- F3, CONFIRMED. Comp!=empty does NOT
                                            imply selected_claim participates in the S1-triggering
                                            contradiction; A1 is a direct, legal, reproducible counterexample.
  F2 (inherited, prior audit, still open): CONDITIONAL -- now also instantiable via the new Part
                                            construct (F2', witness A3).
```

**Overall verdict: FAIL**, scoped precisely as above. The correction's central engineering
claim — totality of `contradiction_doc_ids` — **holds**, and its determinism/replay/digest/
orthogonality proofs **hold** as narrowly stated. But the correction's own characterization of
*what the fixed value means* (§3.1 parenthetical, §3.2 restated I-3 preamble, §4 closing claim)
is **false** for a legal, deterministic, non-rare (`ios(selected_claim)=1`, 48.1%-of-fired in
this audit's synthetic domain) input class exhibited by witness **A1**. Because the mission
specifically named **invariant I-3** as a falsification target, and I-3's corrected text is the
locus of the false claim, this audit cannot return PASS. It is not UNDECIDABLE either: F3 is
CONFIRMED (fully constructed from frozen types and stated rules, no external unverified
assumption required), unlike F2/F2′ which remain genuinely CONDITIONAL pending PA-2 register
values this auditor cannot access.

This audit does not ratify, approve, or freeze anything (that authority is B2/B3, per the
correction's own §7). It recommends:
1. **F3 be tracked as a new, confirmed PA-3 specification defect**, adjacent to and structurally
   caused by the same root gap class as the prior audit's F1, requiring a further, small
   amendment to the `Comp` definition (suggested direction, §5) before Finding 2's I-3 restatement
   can be honestly asserted as total-and-correct.
2. **F2′ be tracked alongside the pre-existing F2**, as the same open dependency now also
   reachable through `Part`.
3. Any future remediation of F3 should re-run this audit's witness suite (`A1`, `A11`,
   `Sweep`) as a regression check, since W2 itself is unaffected and must remain so.

---

## Appendix A — Reference model, witness suite, and sweep (independent, from-scratch, spec-only)

Location (repository root, scratch auditor files, not part of `program_a/`):
`es1_finding2_audit_reference.py` (the two classifier variants), `es1_finding2_audit_witnesses.py`
(replays W0/W2 + 11 adversarial witnesses A1–A11), `es1_finding2_audit_sweep.py` (the
`ios(selected_claim)` sweep and the conditional-rate sweep). All were executed; every quoted
number, state, and field value above (including the 296/300, 0/300×3, and 928/1928 sweep
counts) is direct program output, not hand-simulation, and is reproducible by re-running the
three files in this repository against the witness constructions listed verbatim in §3.

## Appendix B — Witness-to-target cross-reference

| Target | Witnesses used | Outcome |
|---|---|---|
| Replay (mission's 3 named witnesses) | W0, W2 (both variants, seed + order varied) | Both CONFIRMED, matching source documents exactly |
| Determinism | A3, A6, plus all others as controls | Conditional break (F2′); survives elsewhere |
| Replay (T1 sense) | W0, W2, A1, A5, A6 | Survives |
| State completeness | S0-boundary check, A7, all witnesses | Survives |
| State exclusivity | A7 | Survives |
| `selected_claim` | A8, A1, A4 | Survives (outside pre-existing F2) |
| `contradiction_doc_ids` | W2, A1–A4, A9, A10 | Definedness survives; correctness FALSIFIED (F3) |
| Invariant I-3 | A11 (direct), A1 (underlying witness) | FALSIFIED — corrected preamble's equivalence is false |

*End of independent falsification audit.*
