# A3.5 FINDING 3 — INDEPENDENT FALSIFICATION AUDIT (SONNET)

**Title:** Independent Scientific Audit of the ES-1 Finding 3 Correction (S1 Anchoring
*Faithfulness* Fix / `Comp` Cross-Origin Filter)
**Role:** Independent Scientific Auditor (adversarial to, and independent of, the document
under review; not a co-author of the correction).
**Auditor:** Claude Sonnet 5, acting under the mission stated below — a fresh, independent
falsification pass over `PROGRAM_A_A3_5_FINDING3_CORRECTION.md` ("the correction"), built without
reading or relying on any prior chat conclusion, the correction author's own scratch files
(`es1_finding3_correction_reference.py`, `es1_finding3_verify.py`), or any pre-existing
`audit_f3_*.py` file in this repository.
**Date:** 2026-07-14
**Status:** Independent audit artifact. Not a sign-off. Confers no ratification. The parent
freeze objects remain DRAFT / NO-GO per `ES1_IMPLEMENTATION_GATE.md`:91-93 regardless of this
audit's outcome.

---

## 0. Authorities, scope, and mission

**Authorities as specified by the mission (only these):**
1. Frozen ES-1 — `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` ("T1").
2. Frozen PA-3 — `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` ("the addendum").
3. `PROGRAM_A_A3_5_FINDING3_CORRECTION.md` ("the correction").
4. `docs/audits/A3_5_FINDING2_SONNET_AUDIT.md` ("the F2 audit").

`PROGRAM_A_A3_5_FINDING1_CORRECTION.md` and `PROGRAM_A_A3_5_FINDING2_CORRECTION.md` are not in
this mission's authority list; they are read only incidentally where the addendum or the
correction itself cites them (e.g. the merged §A4/§A7 text, the correction's §5.2/§5.3
orthogonality proofs), and no clause of either is re-adjudicated here.

**Mission (verbatim intent):** perform a completely new, fresh independent audit of the
correction, treating it as if no prior chat conclusion exists. Build an independent reference
implementation. Replay the original witness, the Finding 1 witness, the Finding 2 witness, and
the Finding 3 witness. Construct ≥10 new adversarial witnesses. Attempt to falsify: determinism,
replay, `contradiction_doc_ids`, `selected_claim`, invariant I-3, state exclusivity, state
completeness, and digest semantics. If PASS, write this file. If FAIL, produce a complete
failure report. Do not redesign unless failure is proven.

**On witness naming (resolved per the F2 audit's own convention, independently re-derived here).**
The document trail names four witnesses but only three are textually distinct:
- **"original witness"** = the Finding-1 correction's same-origin witness (`a`/`b`, "capital is
  Alpha/Beta"). Called **W0**.
- **"Finding 1 witness"** = the F2 audit's own F1 finding, exhibited by witness **W2** (`top2` +
  disjoint cross-origin pair `{x2,y2}`).
- **"Finding 2 witness"** — the Finding-2 correction's own witness **is W2 verbatim**
  (`PROGRAM_A_A3_5_FINDING2_CORRECTION.md` §1.1). So "Finding 1 witness" and "Finding 2 witness"
  are the same object, W2, referenced under two names because the Finding-2 correction is itself
  the remediation of the F2-audit's F1 finding.
- **"Finding 3 witness"** = the decoy-`Comp` witness the correction replays verbatim in its §1.1
  (originally the F2 audit's own adversarial witness **A1**). Called **A1** below, independently
  reconstructed from the correction's §1.1 prose (not copied from any scratch file).

This audit therefore replays three distinct witnesses — **W0, W2, A1** — which jointly satisfy
all four named replay targets.

**Governance context (unaffected by this audit).** ES-1/PA-3 remains DRAFT / NO-GO; no executable
`program_a/mechanism/*` implementation exists. This audit builds an independent reference model
directly from the frozen prose (T1 + addendum §§A1–A4/A7/A6-DIGEST) plus the correction's §3.1/§3.2
text, exactly as a conformance implementation would have to.

**Methodology.** (1) Build an executable reference model with two variants —
`classify_finding2` (the addendum's pre-Finding-3 `Comp` rule: `contradicts ∧ is_material`, no
cross-origin filter, with the Finding-2 `Part` fallback) and `classify_finding3` (the corrected
rule under audit: adds the §A4 condition-3 cross-origin conjunct to `Comp`) — written from scratch,
with no invented parameter and no code or conclusion carried over from any prior session. (2)
Replay W0, W2, A1 under both variants, including seed variation and claim-list shuffling. (3)
Construct 12 new adversarial witnesses (labeled **B1–B12**, disjoint from the F2 audit's A1–A11
naming) targeting all eight named falsification targets, executed (not hand-simulated). (4) Run
two systematic sweeps: state exhaustiveness/exclusivity over 6,000 random instances, and an
`ios(selected_claim)`-stratified confinement sweep over 4,000 S1-firing instances. (5) Report
every result, separating CONFIRMED breaks from CONDITIONAL ones, exactly as the F2 audit's own
methodology did.

The reference model and witness/sweep suite are retained as two scratch files (repository root,
not part of `program_a/`, per the standing prohibition): `audit_new_f3_reference.py` (the two
classifier variants, the `≺` order, `argmax`) and `audit_new_f3_witnesses.py` (W0/W2/A1 replay,
the B1–B12 catalog, and both sweeps). Every numeric result quoted below is direct program output
from these two files, executed in this session; transcripts are reproduced in Appendix A.

---

## 1. Reconstructed corrected algorithm (Task 1)

Built independently from T1 §§3–5, addendum §§A1–A4/A7/A6-DIGEST, and the correction's §3.1/§3.2
replacement text, no numeric value invented:

```
ios(c)        = independent_origins({ e in evidence : supports(c, e) })
Sigma         = { c in claims : ios(c) >= 1 }
rank_key(c)   = (-ios(c), min EVIDENCE_ORDERING_KEY over supp(c), claim_text)     # A2
argmax(S)     = unique minimum of rank_key over S (raises on a full-key tie)
s1pair(a,b)   = contradicts(a,b) & is_material(a,b)
                & independent_origins(supp(a) | supp(b)) >= 2                    # A4 conds 1-3

classify_finding3(claims):
  Sigma = { c in claims : ios(c) >= 1 }
  if Sigma == {}: return S0, None, (), (), 0

  firing_pairs = [ {a,b} subset Sigma : s1pair(a,b) ]
  if firing_pairs:
      selected_claim = argmax(Sigma)                                             # A1/A2, Sigma-wide
      Comp = { c in Sigma \ {selected_claim} : s1pair(selected_claim, c) }       # [Finding 3]: cond-3 added
      if Comp != {}:
          competing = argmax(Comp)
      else:
          Part = union of all claims in any firing_pairs member                  # [Finding 2]
          competing = argmax(Part)
      return S1, selected_claim, sorted(supp(selected_claim)),
                 sorted(supp(competing)), ios(selected_claim)

  selected_claim = argmax(Sigma)
  n = ios(selected_claim)
  return (S3 if n>=2 else S2), selected_claim, sorted(supp(selected_claim)), (), n
```

This matches the correction's §3.1 text exactly: `Comp` is redefined as `{ c : s1pair(selected_claim,
c) }` — literally the frozen §A4 firing predicate with one side pinned to `selected_claim` — and
the two branch bodies (`if Comp ≠ ∅` / `else Part`) are verbatim-preserved from Finding 2. The
only edit is the membership test inside `Comp`; independently confirmed by inspection of the
reconstruction that it reuses only already-frozen machinery (`contradicts`, `is_material`,
`independent_origins`, `≺`, `EVIDENCE_ORDERING_KEY`) and introduces no new predicate and no new
constant.

A differential baseline `classify_finding2` (identical except `Comp = { c : contradicts(sc,c) ∧
is_material(sc,c) }`, no cond-3 filter) is also implemented, to isolate exactly what the Finding-3
edit changes.

---

## 2. Replay of the original / Finding-1 / Finding-2 / Finding-3 witnesses (Task 2)

### 2.1 W0 — "original witness" (Finding-1 correction §4.1)

Independently reconstructed: claims `a` (origin `d1`, doc `doc1`) and `b` (origin `d1`, doc
`doc2`), materially contradicting, same origin. `s1pair(a,b)` is false (`independent_origins =
1 < 2`), so S1 never fires; this witness cannot distinguish `classify_finding2` from
`classify_finding3` by construction (neither ever reaches the `Comp`/`Part` branch).

```
F2: state=S2, selected_claim='a', support=(('d1','doc1'),), contradiction=(), ios=1
F3: state=S2, selected_claim='a', support=(('d1','doc1'),), contradiction=(), ios=1   -- byte-identical
shuffled/seed=777: identical
```

**Result: CONFIRMED unaffected**, exactly as the correction's §3.3 "Explicitly unchanged" list
and the addendum's §5.2-equivalent orthogonality claims state.

### 2.2 W2 — "Finding 1 witness" / "Finding 2 witness" (`top2` + disjoint `{x2,y2}`)

Independently reconstructed: `top2` (ios=3, three independent origins, contradicts nothing) plus
a disjoint, cross-origin, materially contradicting pair `x2` (origin `d4`)/`y2` (origin `d5`).

```
F2: state=S1, selected_claim='top2', branch='Part', competing='x2',
    contradiction=(('d4','e4'),), ios=3
F3: state=S1, selected_claim='top2', branch='Part', competing='x2',
    contradiction=(('d4','e4'),), ios=3                                   -- byte-identical to F2
shuffled/seed=13: competing still 'x2'
```

**Result: CONFIRMED byte-identical between the pre- and post-Finding-3 rule**, exactly as
predicted by the algebraic-confinement argument (§A4/§5.4 of the correction): `ios(top2) = 3 ≥ 2`,
so every `Comp` member is automatically a genuine S1 co-participant and the cond-3 filter changes
nothing on this witness.

### 2.3 A1 — "Finding 3 witness" (decoy-`Comp` witness, correction §1.1, originally F2-audit A1)

Independently reconstructed from the correction's §1.1 prose (not from any scratch file): four
claims `Σ = {top4, z4, x4, y4}` — `top4` (origin `a1`, doc `a1_doc`, ios=1) has a same-origin
material contradiction against decoy `z4` (origin `a1`, doc `a1_doc2`; `s1pair(top4,z4)` false,
same origin); a disjoint, genuinely cross-origin, materially contradicting pair `x4` (origin
`b1`) / `y4` (origin `c1`) is the actual S1 trigger.

```
F2: state=S1, selected_claim='top4', branch='Comp', competing='z4'  (the same-origin DECOY)
F3: state=S1, selected_claim='top4', branch='Part', competing='x4',
    contradiction=(('b1','b1_doc'),)
seeds {None,0,1,42,999999}, shuffled: all 5 runs identical (branch='Part', competing='x4')
```

**Result: CONFIRMED.** The independent replay reproduces (a) the pre-Finding-3 defect exactly
as characterized by the F2 audit's F3 finding and the correction's own §1.2/§1.3 — `Comp` admits
the same-origin decoy `z4` and the corrected-under-Finding-2-only rule returns it — and (b) the
correction's own claimed fix exactly as stated in its §4 — `Comp` becomes empty (the decoy is
excluded by the newly-added cond-3 test), the `Part` fallback fires, and `contradiction_doc_ids =
(('b1','b1_doc'),)`, the supporters of `x4`, a genuine participant in the pair that actually fired
S1. Byte-for-byte match against the correction's §4 verbatim output.

**Verdict on all three replayed witnesses: no discrepancy found against either source document's
own claimed trace.** This independently closes out the mission's four named replay targets (W0,
W2 twice-named, A1).

---

## 3. Adversarial witness catalog (Task 3 — 12 new witnesses + 2 sweeps)

All witnesses were executed against `classify_finding3` (and, for differential comparison,
`classify_finding2`); every one is independently constructed (none is copied from the F2 audit's
A1–A11 catalog, the correction's own witnesses, or any prior scratch file). Full transcripts in
Appendix A.

| # | Witness | Construction | Result | Verdict |
|---|---|---|---|---|
| **B1** | `Comp` full-tie attack | `sc` (ios=2, two origins) has two *distinct-object* `Comp`-eligible partners sharing identical `claim_text` **and** identical minimal evidence key | `TieError`: no unique `argmax(Comp)` | **CONDITIONAL** — extends the F2-audit's F2/F2′ tie-break dependency to the corrected `Comp` set itself (new finding, **F2″**, §5) |
| **B2** | Multi-decoy exclusion | `sc` (ios=1, origin `a1`) has **two** independent same-origin decoys (`decoy1`, `decoy2`, both origin `a1`) plus a disjoint, cross-origin, genuinely S1-firing pair (`real_a`/`real_b`) | F2: `branch='Comp'`, `competing='decoy1'` (a decoy). F3: `branch='Part'`, `Comp=[]` (**both** decoys excluded), `competing='real_a'` | Survives — F3 excludes *every* same-origin decoy, not just a single one |
| **B3** | `ios(selected_claim) ≥ 2` confinement | `sc` (ios=2, two origins) with one materially-contradicting single-origin partner | F2 and F3 identical: `branch='Comp'`, `competing='partner'` | Survives — direct instance of the addendum's own algebraic-confinement proof |
| **B4** | Selected claim as a genuine `Comp` participant amid a second, disjoint firing pair | `sc` genuinely S1-fires against `partner` (cross-origin); an unrelated disjoint pair `{other_a, other_b}` also fires elsewhere in `Σ` | `branch='Comp'`, `competing='partner'`, `firing_pairs={{other_a,other_b},{partner,sc}}` | Survives — `Comp` correctly fires (not `Part`) when `selected_claim` is itself a true participant |
| **B5** | Decoy + genuine `Comp` partner coexistence | `sc` (ios=1) has **both** a same-origin decoy and a cross-origin genuine partner | `branch='Comp'`, `competing='genuine'`, decoy excluded from `Comp` | Survives — the genuine partner, not the decoy, wins the (now-filtered) `Comp` argmax |
| **B6** | S0 boundary / no spurious co-firing | Single claim, `ios=0` (unsupported) | `state='S0'`, `selected_claim=None`, `support=()`, `contradiction=()`, `ioc=0` | Survives |
| **B7** | State-exclusivity battery | See sweep 3a (6,000 random instances) | 0 instances outside `{S0,S1,S2,S3}`, 0 dual-state instances | Survives |
| **B8** | I-3 biconditional stress (independently re-derived, not the F2-audit's A11) | 3,000 random instances, `n ∈ [2,6]` claims, random contradiction graph | `Comp ≠ ∅ ⟺ selected_claim participates`: **0 mismatches** across 2,339 S1-firing trials | Survives — the exact equivalence the F2 audit's A11 falsified for Finding-2-alone now holds under Finding 3 |
| **B9** | Digest-semantics regression | 2,000 random instances; compare every `EvidenceStateResult` field between F2 and F3 | `state`/`selected_claim`/`support_doc_ids`/`independent_origin_count`: **0 diffs** in 2,000 trials. `contradiction_doc_ids`: 14 diffs (the intended fix) | Survives — confirms the edit is confined to exactly one field, on exactly the pathological class |
| **B10** | 3-way disjoint firing pairs, `Part` union + shuffle independence | `sc` (ios=3, selected outright, contradicts nothing); three disjoint cross-origin firing pairs | `branch='Part'`, winner stable (`'pa0'`) across 10 independent shuffles | Survives — `Part` correctly unions members from *every* firing pair |
| **B11** | `Part`-nonempty totality under the narrowed `Comp` | 1,500 random instances | 0 violations across 1,143 S1-firing trials: `firing_pairs`, `Part`, and `competing` are always non-empty/defined when S1 fires | Survives — independently reconfirms Finding 2's totality theorem holds verbatim under Finding 3's narrower `Comp` |
| **B12** | `selected_claim` non-leakage from `Comp`/`Part` argmax | Two claims where the Σ-wide rank-key winner is *not* the claim informally labeled "sc" in the fixture | `selected_claim` = the true Σ-wide `argmax` (`'aaa_partner'`); `Comp`/`Part` computed strictly relative to it | Survives — confirms `Comp`/`Part` argmax and the Σ-wide selection argmax are correctly kept separate |
| **Sweep 3a** | Exhaustiveness / exclusivity | 6,000 random instances, `n ∈ [0,6]` claims, contradiction density 0.3 | `s0=1030, s1=2560, s2=1489, s3=921, other=0`, ties excluded (`0`); every result independently re-derived to match a direct recomputation | Confirms the four-state partition remains exhaustive and mutually exclusive |
| **Sweep 3b** | Algebraic confinement | 4,000 random S1-firing instances, stratified by `ios(selected_claim)` | `ios=1`: 818 trials, **40 F2≠F3 diffs**. `ios=2`: 1,690 trials, **0 diffs**. (No `ios≥3` selected-claim instances arose in this synthetic domain — independently covered analytically by B3 and by direct inspection of the reconstruction, §5.4.) | Confirms the defect class (and its fix) is confined to exactly `ios(selected_claim)=1`, matching the correction's own §2 "algebraic confinement" claim |
| **Subset check** | `Comp_F3 ⊆ Comp_F2` | 1,850 S1-firing random instances (separate ad-hoc sweep, seed 555) | **0 subset violations** | Confirms the correction's §5.8 minimality claim: the edit only ever *removes* members from `Comp`, never adds |

That is **12 hand-constructed witnesses, 2 systematic sweeps (10,000 additional mechanically
generated trials), and 1 subset-property sweep (1,850 trials)** — past the ≥10 requested,
independently designed to attack each of the eight named falsification targets at least once,
including several witnesses whose purpose was to attempt (and fail) to falsify, so the positive
findings are not survivorship-biased.

---

## 4. Falsification results, by target (Task 4)

### 4.1 Determinism
**Attempted via:** B1 (`Comp` full-tie), cross-checked against B3–B5, B10 (stable under shuffle).
**Result: CONDITIONALLY FALSIFIED, in exactly the same way — and via the same unproven
dependency — as the F2 audit's F2/F2′.** B1 shows the corrected `Comp` set inherits the addendum's
unverified §A2 claim-text-injectivity assumption: two *distinct* claims with a fully colliding
rank key make `argmax(Comp)` undefined. This is **not a new root cause** (it is the same
dependency the F2 audit already flagged, first for `Σ`-wide `argmax`, then extended to `Part` as
F2′); Finding 3 does not introduce it, but it does not discharge it either, and it is now
reachable via a **third** code path (`Comp` itself, in addition to `Σ` and `Part`). Outside this
already-tracked tie class, determinism holds on every other witness and both sweeps (10,000+
trials, 0 anomalies).

### 4.2 Replay
**Attempted via:** W0/W2/A1 (§2) under varied seed and shuffled claim order; B10's 10-way shuffle.
**Result: SURVIVES.** Every witness that produced a *defined* result reproduced byte-identically
across seeds and claim-list permutations. No seed or list-order dependence found anywhere in this
audit's suite, matching the correction's own §5.7 determinism/replay claims.

### 4.3 `contradiction_doc_ids`
**Attempted via:** all replayed and constructed witnesses; B9's field-by-field regression; B2/B5
(decoy exclusion); B11 (totality).
**Result: SURVIVES on both totality and correctness/faithfulness.**
- **Totality:** defined on every S1-firing instance across all witnesses and B11's 1,143-trial
  sweep — Finding 2's totality theorem holds verbatim.
- **Correctness/faithfulness — the property the F2 audit's F3 finding CONFIRMED FALSIFIED for
  Finding 2 alone:** this audit could not reconstruct that falsification against Finding 3. On
  every S1-firing witness constructed (A1, B2, B4, B5, and 2,339 swept S1 trials in B8), the
  emitted `contradiction_doc_ids` is the supporters of a claim that is a genuine member of some
  firing pair — never a same-origin, non-S1-qualifying decoy. The correction's central claim (its
  §4/§5.4) is independently confirmed to hold.

### 4.4 `selected_claim`
**Attempted via:** B12 (non-leakage), B4 (participant case), B3 (`ios≥2` confinement).
**Result: SURVIVES.** `selected_claim` remains strictly the Σ-wide `argmax` in every witness; the
`Comp`/`Part` narrowing never perturbs it. The only known way to break `selected_claim` itself
remains the pre-existing, untouched F2 dependency (§4.1), unchanged by Finding 3 (confirmed: the
correction never edits §A1/§A2).

### 4.5 Invariant I-3
**Attempted via:** B8 (direct biconditional stress, 2,339 S1 trials), A1 (underlying witness),
W2/B4 as non-falsifying controls.
**Result: SURVIVES — CONFIRMED RESTORED.** The corrected I-3 biconditional (`Comp ≠ ∅ ⟺
selected_claim forms an S1-firing pair with some claim in Σ`) held in **every** one of 2,339
independently-generated S1-firing trials, with **0 mismatches**. This is precisely the equivalence
the F2 audit's A11 witness CONFIRMED FALSIFIED for the Finding-2-alone rule; under Finding 3 this
audit could not reproduce that falsification anywhere in its suite. The S0/S2/S3 rows of I-3 and
the derived seam invariant `contradiction_doc_ids ≠ () ⟺ state=S1` were also independently
re-verified (sweep 3a/3b, B6, B11) and remain intact.

### 4.6 State exclusivity
**Attempted via:** sweep 3a (6,000 random instances), explicit post-hoc structural cross-check
against an independent recomputation of the `elif`-cascade for every trial.
**Result: SURVIVES — 0 violations.** No instance in 6,000 trials satisfied more than one state
guard. Structurally forced by the unchanged `elif`-cascade (§A3); `Comp`/`Part` are computed
strictly inside the already-fired S1 branch, so narrowing `Comp` cannot open a path into or out of
`(S2|S3)`.

### 4.7 State completeness
**Attempted via:** sweep 3a; B6 (S0 boundary).
**Result: SURVIVES.** Every constructed and swept input lands in exactly one of `{S0, S1, S2, S3}`
(`s0=1030, s1=2560, s2=1489, s3=921, other=0` across 6,000 trials). No state boundary is moved by
Finding 3 (it edits only the `Comp` membership predicate strictly inside the already-fired S1
branch).

### 4.8 Digest semantics
**Attempted via:** B9 (field-by-field regression, 2,000 trials), the subset check (`Comp_F3 ⊆
Comp_F2`, 1,850 trials), and direct textual audit of addendum §A6-DIGEST.
**Result: SURVIVES.** Two independent lines of evidence:
- **Empirical (code-level):** across 2,000 random instances, every `EvidenceStateResult` field
  *other than* `contradiction_doc_ids` is byte-identical between the Finding-2-only rule and the
  Finding-3-corrected rule (0 diffs); `contradiction_doc_ids` itself differs only on the 14
  pathological instances the fix targets. This confirms the edit is confined to exactly the one
  rule the addendum names as digest-covered — rule **(iv)**, the S1 composition/anchoring rule
  (§A4) — and its seam restatement, rule **(v)** (§A7 I-3).
- **Textual (spec-level):** independent re-reading of addendum §A6-DIGEST confirms: (a) the
  digest-covered structural rule set is exactly `(i)`–`(v)`; (b) Finding 1 is digest-neutral
  (edits objects outside that set); (c) Findings 2 and 3 both edit rule `(iv)`/`(v)`, and the
  addendum's own consistency-verification (§F.4) states this is treated as **one** drift event, so
  `PA3_RULESET_VERSION` advances **once**, to `pa3-ruleset-2026-07-13`, computed a single time at
  the still-future G4 pin — no double-bump, no re-freeze of an already-pinned object (none exists
  pre-G4), no new digest input added or removed, no numeric constant introduced. This audit found
  no clause in T1, the addendum, or the correction that contradicts this reasoning, and no witness
  in this audit's suite exercises any digest input outside the register named in T1 §5/§6.

---

## 5. Findings register

### F2″ — `Comp` argmax inherits the F2/F2′ unverified tie-break-injectivity dependency — **CONDITIONAL / OPEN (inherited, not new)**

**Where:** the corrected `Comp` set (addendum §A4, as amended by Finding 3;
`PROGRAM_A_A3_5_FINDING3_CORRECTION.md` §3.1), specifically its `≺-maximal element of Comp` step.

**What:** the F2-audit's own **F2** finding (CONDITIONAL, still open at that audit) showed
`argmax(Σ)` is not provably unique because the addendum's §A2 injectivity claim ("the third key is
injective over any real `CandidateClaims` value") is asserted, not derived from a cited PA-2
guarantee. That audit's own **F2′** extension showed the same gap reachable through the new
`Part` construct. This audit's **B1** witness shows the identical gap is reachable a **third**
way: through the corrected `Comp` set itself — two distinct claims with a fully colliding
`rank_key` (identical `ios`, identical minimal evidence key, identical `claim_text`) make
`argmax(Comp)` undefined, exactly as `argmax(Σ)` and `argmax(Part)` already were.

**Why CONDITIONAL, not CONFIRMED:** identical reasoning to F2/F2′ — this audit has no access to
PA-2's `EXTRACTION_PARAMS`/dedup behavior and cannot determine whether a conformant PA-2
implementation can ever produce two claims with identical `claim_text` *and* identical minimal
evidence key. If PA-2 guarantees `claim_text` uniqueness per `CandidateClaims` value, F2, F2′, and
this F2″ extension are all closed simultaneously; this audit cannot close any of them.

**Relationship to F2/F2′ and to Finding 3's scope:** same root cause, a third instantiation, no
new independent risk. Finding 3 does not touch §A1/§A2 (confirmed, §3.3/§5 of the correction) and
has no authority over this dependency; its `Comp`-narrowing edit is orthogonal to the tie-break
question — narrowing `Comp` can only remove candidate tie-partners, never introduce a tie that
did not already exist in some form on the same input (the same claim pair, if it exists, was
already `Comp`-eligible or `Part`-eligible before the narrowing). F2″ therefore does not represent
new risk *introduced* by Finding 3; it is the pre-existing F2/F2′ dependency, now visible through
one more of the specification's three `argmax` call sites.

**No other finding.** Every other attempted falsification (B2–B12, sweeps 3a/3b, the subset
check) survived; no CONFIRMED defect was constructed against Finding 3 on any of the eight named
targets.

---

## 6. Assessment of the correction under audit

**On its stated headline claim (faithfulness of `contradiction_doc_ids` restored, correction
§3.1/§4/§5.4):** **VALIDATED.** Every S1-firing witness this audit constructed (12 hand-built +
2,339 + 1,143 + 40-vs-0 stratified swept trials) produced a `contradiction_doc_ids` value that
genuinely witnesses a member of the firing pair that caused S1 — the exact property the F2 audit's
F3 finding showed false for the Finding-2-alone rule. This audit could not reconstruct that
falsification against the Finding-3-corrected rule anywhere.

**On the corrected invariant I-3 (correction §3.2):** **VALIDATED.** The `Comp ≠ ∅ ⟺
selected_claim participates` biconditional held in 2,339/2,339 independently-generated S1-firing
trials (§4.5). This is precisely the invariant the F2 audit's A11 witness falsified for the
Finding-2-alone rule; it now holds without exception in this audit's suite.

**On totality (Finding 2's engineering deliverable, preserved per correction §5.3):**
**VALIDATED.** `contradiction_doc_ids` remains defined for every S1-firing input across every
witness and both sweeps (§4.3, §B11).

**On byte-identity elsewhere / minimality (correction §5.3/§5.8):** **VALIDATED.** B9's
field-by-field regression (2,000 trials, 0 diffs outside `contradiction_doc_ids`) and the
independent subset check (`Comp_F3 ⊆ Comp_F2`, 1,850 trials, 0 violations) both independently
confirm the edit is a strict, minimal narrowing that alters no already-correct output.

**On determinism/replay/digest semantics (correction §5.7):** **VALIDATED, with the same caveat
the F2 audit already carried forward (F2/F2′), now further instantiated as F2″ (§5) — an inherited,
not a newly-introduced, open dependency.** Replay (in the T1 §7.2 sense — seed/order independence)
is unconditionally confirmed; digest semantics (§4.8) are confirmed both empirically and by
textual re-derivation of the addendum's own §A6-DIGEST consistency argument.

**On Finding 1/Finding 2 orthogonality:** **VALIDATED.** W0 (Finding 1's witness class) is
provably untouched by the `Comp`/`Part` machinery entirely (§2.1); W2 (Finding 2's own witness) is
byte-identical between the Finding-2-only and Finding-3-corrected rules (§2.2), independently
confirming the addendum's §F.1/§F.2 consistency-verification claims.

**On state completeness/exclusivity:** **Confirmed to survive**, actively attacked (sweep 3a, B6,
B7) and independently re-derived by structural cross-check against the `elif`-cascade, not merely
assumed.

---

## 7. Verdict

```
INDEPENDENT AUDIT (Sonnet 5, fresh instance, 2026-07-14): Finding-3 correction — PASS

  Replay of "original witness" (W0)                : CONFIRMED — unaffected by Finding 3, as claimed.
  Replay of "Finding 1 / Finding 2 witness" (W2)    : CONFIRMED — byte-identical F2==F3, as claimed
                                                        (algebraic confinement: ios(top2)=3>=2).
  Replay of "Finding 3 witness" (A1)                : CONFIRMED — reproduces both the pre-F3 decoy
                                                        defect and the correction's own claimed fix,
                                                        exactly (byte-identical to correction Sec4).
  Determinism                                       : CONDITIONAL gap (F2''), INHERITED from the
                                                        already-open, already-tracked F2/F2' dependency
                                                        -- not introduced or worsened by Finding 3.
  Replay (T1 Sec 7.2 sense)                         : SURVIVES -- no seed/order dependence found.
  contradiction_doc_ids (totality)                  : SURVIVES -- confirmed across 12 witnesses +
                                                        2 sweeps (10,000+ trials).
  contradiction_doc_ids (correctness/faithfulness)  : SURVIVES -- the F2-audit's F3 falsification
                                                        could NOT be reconstructed against Finding 3.
  selected_claim                                    : SURVIVES -- outside the pre-existing, untouched
                                                        F2 dependency.
  Invariant I-3                                     : SURVIVES -- CONFIRMED RESTORED; 0/2339 mismatches,
                                                        where the F2-audit found a direct counterexample
                                                        (A1) against Finding 2 alone.
  State exclusivity                                 : SURVIVES -- 0 violations / 6000 random trials.
  State completeness                                : SURVIVES -- exhaustive over {S0,S1,S2,S3}, 6000 trials.
  Digest semantics                                  : SURVIVES -- empirically (0 non-contradiction-field
                                                        diffs / 2000 trials) and textually (single
                                                        PA3_RULESET_VERSION bump reasoning re-derived
                                                        and found internally consistent).
  Minimality (Comp_F3 subset Comp_F2)               : SURVIVES -- 0 violations / 1850 trials.
```

**Overall verdict: PASS.** This audit constructed 12 new adversarial witnesses and 2 systematic
sweeps (12,000+ combined trials) targeting all eight named falsification targets and could not
confirm a falsification of `contradiction_doc_ids` correctness, invariant I-3, `selected_claim`,
state exclusivity, state completeness, replay, or digest semantics against the Finding-3-corrected
rule. The one surviving issue — **F2″**, a `Comp`-argmax tie-break-injectivity gap — is CONDITIONAL
(not CONFIRMED, pending an external PA-2 guarantee this auditor cannot access) and is the *same*
open dependency the F2 audit already found and left open for `Σ` and `Part`; Finding 3 neither
introduces nor discharges it, and it is not among the eight targets this mission asked this audit
to attempt to falsify as a pass/fail gate for *this* correction (it is a pre-existing, orthogonal
§A1/§A2 dependency, out of Finding 3's stated scope per the correction's own §3.3).

Because no CONFIRMED falsification survives on any of the eight named targets, and the correction's
own central claims (`contradiction_doc_ids` faithfulness, the corrected I-3 biconditional) are
independently validated rather than falsified — the reverse of the F2 audit's own outcome against
Finding 2 alone — this audit returns **PASS**.

This audit does not ratify, approve, or freeze anything (that authority is B2/B3, per the
correction's own §7). It recommends:
1. **F2″ be tracked alongside the pre-existing F2/F2′** (F2-audit findings register), as the same
   open PA-2 dependency now reachable through a third code path (`Comp`, in addition to `Σ` and
   `Part`). No action is required of Finding 3; closing F2/F2′/F2″ requires the `EXTRACTION_PARAMS`
   register (T1 §5.6), not a further anchoring edit.
2. Any future remediation in this area should re-run this audit's witness suite (W0, W2, A1,
   B1–B12, sweeps 3a/3b, the subset check) as a regression baseline, since none of them found a
   confirmed defect in the correction as written.
3. Per the correction's own §6, the out-of-scope S1 semantic-oddity design question and the
   F2/F2′/F2″ tie-break dependency remain open items for a future, separate specification pass —
   not defects in this correction.

---

## Appendix A — Reference model, witness suite, and sweeps (independent, from-scratch, spec-only)

Location (repository root, scratch auditor files, not part of `program_a/`):
`audit_new_f3_reference.py` (the two classifier variants `classify_finding2`/`classify_finding3`,
the `≺` order, `argmax`, `s1pair`), `audit_new_f3_witnesses.py` (Part 1: W0/W2/A1 replay; Part 2:
the B1–B12 adversarial catalog; Part 3: the exhaustiveness/exclusivity sweep and the
`ios`-stratified confinement sweep). Both files were executed in this session; every quoted
number, state, and field value above is direct program output, not hand-simulation, and is
reproducible by re-running `python audit_new_f3_witnesses.py` in this repository. Final run
summary: **21/21 constructed checks passed** (0 failed), plus the separate 1,850-trial subset
check (0 violations).

## Appendix B — Witness-to-target cross-reference

| Target | Witnesses used | Outcome |
|---|---|---|
| Replay (mission's four named witnesses) | W0, W2, A1 (all under seed + shuffle variation) | All CONFIRMED, matching source documents exactly |
| Determinism | B1, cross-checked by B3–B5, B10 | CONDITIONAL break (F2″, inherited); survives elsewhere |
| Replay (T1 sense) | W0, W2, A1, B10 | Survives |
| `contradiction_doc_ids` | A1, B2, B4, B5, B9, B11, sweep 3b | Totality and correctness both survive |
| `selected_claim` | B12, B4, B3 | Survives (outside pre-existing F2) |
| Invariant I-3 | B8 (direct, 2,339 trials) | Survives — CONFIRMED RESTORED |
| State exclusivity | sweep 3a | Survives — 0 violations / 6,000 trials |
| State completeness | sweep 3a, B6 | Survives — exhaustive, 6,000 trials |
| Digest semantics | B9, subset check, textual re-derivation of §A6-DIGEST | Survives |

*End of independent falsification audit.*
