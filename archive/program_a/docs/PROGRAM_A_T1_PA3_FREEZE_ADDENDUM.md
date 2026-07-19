# PROGRAM A — T1 FREEZE ADDENDUM: PA-3 SPECIFICATION CLOSURE (ES-1)

**Title:** PA-3 Freeze Contract Closure — Addendum to the T1 / G4 Freeze Object
**Authority:** Principal Architect. This addendum is a rider to
`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` (the T1/G4 freeze object). It does
not re-derive T1; it closes the residual PA-3 specification ambiguities so the
frozen T1 mechanism *completely determines* PA-3 behavior.
**Date:** 2026-07-13 (FINAL MERGED — supersedes the 2026-07-09 DRAFT)
**Status:** DRAFT — binds only when co-pinned with the T1 object at G4, under the
same B2 (ScientificAuditor) / B3 (ReleaseManager) sign-off. Until then the
standing prohibition (`ES1_IMPLEMENTATION_GATE.md`:91-93) is in force: no
emission-surface or binding code, no frozen-row output.

**MERGE PROVENANCE (this is the canonical merged ES-1 / PA-3 specification).**
This edition folds the three accepted A3.5 erratum-class corrections into the
addendum body, in place, with **no redesign and no wording change beyond what
each correction specifies**. This is a merge, not a new correction: no new
finding was sought, no new state / predicate / numeric constant is introduced.

| Finding | Source document | What it corrects | Where merged here |
|---|---|---|---|
| **Finding 1** | `PROGRAM_A_A3_5_FINDING1_CORRECTION.md` | ES-1 S2/S3 definitions: "no material contradiction" → "no material contradiction **across independent sources**" (conforms definitions to the frozen operational rule). | **§A0** (incorporated ES-1 §3.1/§4 text) + **§B6** (T1 transcription action). |
| **Finding 2** | `PROGRAM_A_A3_5_FINDING2_CORRECTION.md` | S1 anchoring **totality**: `contradiction_doc_ids` was undefined when the S1-triggering pair is disjoint from `selected_claim`. Adds the `Comp`/`Part` empty-set fallback. | **§A4** anchoring bullet + **§A7 I-3**. |
| **Finding 3** | `PROGRAM_A_A3_5_FINDING3_CORRECTION.md` | S1 anchoring **faithfulness**: refines Finding 2's `Comp` set by adding the §A4 condition-3 cross-origin conjunct, so `contradiction_doc_ids` provably carries a genuine S1 participant. | **§A4** `Comp` definition + **§A7 I-3** (supersedes Finding 2's wording in the same spot). |

Each merged clause is tagged inline `[Finding N]`. Findings 2 and 3 both edit
§A4/§A7; Finding 3 is a strict refinement of Finding 2's `Comp` set, so the
merged text carries Finding 2's `Comp`/`Part` structure with Finding 3's
`Comp` membership and Finding 3's I-3 wording — there is no residual conflict
(see the **Consistency Verification** at the end). Digest consequence: Finding 1
is digest-neutral; Findings 2 and 3 both edit digest-covered rules (iv)/(v) and
therefore advance `PA3_RULESET_VERSION` **once**, to `pa3-ruleset-2026-07-13`,
at the single (still-future) G4 pin (§A6-DIGEST).

**Posture (unchanged from T1 §0):** no evaluation-side probability constant, no
EXP-1 bin boundary, no ECE pass/kill logic, no tier→probability mapping. Every
rule below is purely ordinal/structural and introduces **zero new numeric
constant**. The only new frozen object is one structural rule-version tag
(§A6). CR-8/L8 firewall preserved by construction.

**Scope:** reviews only the unresolved PA-3 specification. Does not implement
code, does not redesign Program A, does not touch PA-1/PA-2/PA-4/PA-5 contracts
except where a PA-3 seam invariant is stated (§A7) or a wording drift must be
reconciled (§B).

---

## A. Final architectural rulings and deterministic rules

Grounding types (frozen, `program_a/types.py`, on disk):
`CandidateClaim = {claim_text: str, supporting_doc_ids: tuple[str,...]}`;
`CandidateClaims.claims` is an **ordered tuple** (PA-2 is deterministic);
`EvidenceItem` carries `origin_domain` + `doc_id` (no `score`, no timestamp);
`EVIDENCE_ORDERING_KEY` (T1 §5.5) = lexicographic on `(origin_domain, doc_id)`,
**already frozen**;
`EvidenceStateResult = {state, selected_claim|None, support_doc_ids,
contradiction_doc_ids, independent_origin_count}`.

### A0 — Incorporated ES-1 state-definition corrections `[Finding 1]`

**RULING (erratum, digest-neutral).** The ES-1 S2/S3 state definitions in the
T1 object (`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.1 rows and §4 semantic
openers) are conformed to the frozen operational rule of §A3/§A4 by narrowing
their materiality clause from the *unqualified* "no material contradiction" to
"no material contradiction **across independent sources**." S1 is tested before
S2/S3 in the frozen precedence (§A3) and already consumes exactly the
*cross-origin* material contradictions (§A4 cond. 3); the residual S2/S3 region
is therefore precisely "material contradictions confined to a single origin (or
none)." This changes **no operational behavior, no state boundary, no constant,
and no digest input** — it makes the definitions *state what the frozen rule
already computes*, closing the same-origin / lone-source exhaustiveness
contradiction (a same-origin self-contradiction fires S2/S3 by `ios`, yet the
un-narrowed definitions excluded it). The corrected canonical text (transcribed
into T1 §3.1/§4 at G4 per §B6):

**T1 §3.1 — S2 row (corrected) `[Finding 1]`:** "Support from exactly one
independent origin; **no material contradiction across independent sources**
(any material contradiction present is confined to a single origin and therefore
does not fire S1 — §A4 cond. 3)." → tier `PROBABLE`.

**T1 §3.1 — S3 row (corrected) `[Finding 1]`:** "Support from ≥2 independent
origins; **no material contradiction across independent sources** (any material
contradiction present is confined to a single origin and therefore does not fire
S1 — §A4 cond. 3)." → tier `CERTAIN`.

**T1 §4 — S2 semantic opener (corrected) `[Finding 1]`:** "When exactly one
independent origin supports the selected claim and there is **no material
contradiction across independent sources** (any contradiction present is
confined to a single origin and so does not fire S1 — §A4 cond. 3), the lawful
answer is a single hedged, source-attributed factual assertion." *(Remainder of
the S2 bullet unchanged.)*

**T1 §4 — S3 semantic opener (corrected) `[Finding 1]`:** "When ≥2 independent
origins support the selected claim and there is **no material contradiction
across independent sources** (any contradiction present is confined to a single
origin and so does not fire S1 — §A4 cond. 3), the lawful answer is a single
asserted, source-attributed factual assertion." *(Remainder of the S3 bullet
unchanged.)*

S0 and S1 definitions, `STATE_TIER_MAP`, `CONFIDENCE_TIERS`, the precedence
`S0 → S1 → (S2 | S3)`, and every constant are unchanged by Finding 1. This block
is digest-neutral: the S2/S3 definitions and tier arguments are **not** inputs to
`frozen_constants_digest()` and are outside the §A6-DIGEST (i)–(v) rule set, so
Finding 1 alone requires **no** `PA3_RULESET_VERSION` bump.

### A1 — Claim-selection rule (item 1)

**RULING.** When `CandidateClaims` contains more than one claim, PA-3 selects
exactly one claim, the **selected_claim**, by the frozen structural rule below.
Selection is anchored to *corroboration strength* — the same quantity the
S2/S3 decision already uses — never to retrieval rank or `score` (M10; the
`score` field is unrepresentable in the frozen types by construction).

Define, for each candidate claim `c` in `claims`, its **independent-origin
support count**
`ios(c) = independent_origins( { e ∈ evidence : supports(c, e) } )`
computed under the frozen `INDEPENDENCE_RELATION` (mirror/syndication domains
collapsed to one origin, T1 §5.2).

**Selection rule.** Restrict to the *supported set* `Σ = { c : ios(c) ≥ 1 }`.

- If `Σ` is empty, no claim is selected (`selected_claim = None`) → the state is
  **S0** by precedence (§A3). Selection terminates here.
- Otherwise the **selected_claim** is the element of `Σ` that is **maximal
  under the total order `≺` of §A2** — i.e. the best-corroborated claim, with
  ties broken deterministically and replay-safely by §A2.

This rule is total over every possible `CandidateClaims` value, deterministic,
and uses only already-frozen structural quantities (`ios` via
`INDEPENDENCE_RELATION`; the §A2 keys). It introduces **no new free constant**.

### A2 — Deterministic, replay-safe tie-break (item 2)

**RULING.** Claims are ranked by the following frozen **total order** `≺` on the
supported set `Σ`. The selected_claim is the `≺`-maximum. The three keys are
applied lexicographically; because the third key is injective over any real
`CandidateClaims` value, `≺` is a strict total order and the maximum is unique —
no residual nondeterminism survives.

Per claim `c`, the ranking key is the triple:

1. **Primary — corroboration (descending):** `ios(c)`, the independent-origin
   support count. Higher wins. (This is the quantity the tier is emitted about;
   selecting on it makes selection and state decision agree by construction.)
2. **Secondary — evidence position (ascending):** the **minimum
   `EVIDENCE_ORDERING_KEY`** over `c`'s supporting evidence items, i.e.
   `min{ (origin_domain, doc_id) : e ∈ evidence, supports(c, e) }`, compared
   lexicographically. Earlier evidence wins. `EVIDENCE_ORDERING_KEY` is already
   frozen (T1 §5.5), so this key is replay-stable.
3. **Tertiary — claim text (ascending):** `claim_text` compared by Unicode code
   point (byte order over its UTF-8/NFC form). This is the total-order
   guarantor for the (constructed) case of two claims sharing identical
   corroboration and identical minimum support key. `claim_text` is
   deterministic output of PA-2, so this key is replay-stable.

**Rationale for replay-safety.** Every key is a pure function of already-frozen
artifacts (the frozen snapshot, the frozen `EVIDENCE_ORDERING_KEY`, the
deterministic PA-2 output). No wall-clock, no hash-seed iteration order, no
`score`, no PA-2 *tuple position* (tuple position is **not** used, to avoid
coupling replay-safety to an unfrozen extraction-ordering detail). Identical
`(query_text, snapshot)` ⇒ identical `≺` ⇒ identical selected_claim, byte for
byte, across all 22 seeds (T1 §7.2).

### A3 — Precedence, restated with selection folded in

The frozen precedence `S0 → S1 → (S2 | S3)` (T1 §3.3) is unchanged. Selection
(§A1/§A2) is layered *inside* it as follows, and this ordering is itself frozen:

1. **S0 test first.** Compute `Σ`. If `Σ = ∅`, state = **S0**,
   `selected_claim = None`. Stop.
2. **S1 test next.** Evaluate the S1 composition (§A4) over `Σ`. If it fires,
   state = **S1**; the selected_claim is fixed by §A1/§A2 restricted to `Σ`.
   Stop.
3. **(S2 | S3) last.** selected_claim = §A1/§A2 winner over `Σ`. If
   `ios(selected_claim) ≥ MIN_INDEPENDENT_ORIGINS_FOR_S3` (=2, T1 §5.1) →
   **S3**, else (`ios == 1`) → **S2**.

Exactly one state fires per query (Tree 2 invariant, preserved).

### A4 — S1 contradiction composition (item 3)

**RULING.** S1 (`DEBATED`) fires **iff**, over the supported set `Σ` (so the S0
test has already failed), there exists an unordered pair of *distinct* claims
`{a, b} ⊆ Σ` such that **all three** hold:

1. `contradicts(a, b)` is true — the two claims assert incompatible content
   (§A5); **and**
2. `is_material(a, b)` is true — the incompatibility is material, not a trivial
   phrasing/stylistic variation (§A5, under
   `CONTRADICTION_MATERIALITY_PARAMS`); **and**
3. the disagreement is across **independent sources**: the origin(s) supporting
   `a` and the origin(s) supporting `b` are not one and the same single origin.
   Formally
   `independent_origins( supp(a) ∪ supp(b) ) ≥ 2`
   **with** at least one independent origin on each side, where
   `supp(c) = { e : supports(c, e) }`. (A lone source that self-contradicts is
   **not** S1 — S1 is *independent sources supporting incompatible claims*,
   T1 §3.1.)

Predicate evaluation order is fixed for determinism and cost: `contradicts`
first, then `is_material` (materiality is only defined for a genuine
contradiction; see §A5), then the independence check. `is_material` is
**never** consulted on a pair for which `contradicts` is false (its value there
is treated as vacuously false, never computed).

**S1 anchoring (which claim/docs the result carries).** When S1 fires:

- `selected_claim` = the §A1/§A2 winner over `Σ` (the best-corroborated
  supported claim). Non-`None`.
- `contradiction_doc_ids` = the supporters of the **competing claim**,
  tie-broken by §A2, its supporting evidence ordered by `EVIDENCE_ORDERING_KEY`,
  where the competing claim is defined by: `[Finding 2]` (the `Comp`/`Part`
  split and empty-set fallback) refined by `[Finding 3]` (the cond-3 conjunct on
  `Comp`):
  - let `Comp = { c ∈ Σ, c ≠ selected_claim :
                     contradicts(selected_claim, c)
                   ∧ is_material(selected_claim, c)
                   ∧ independent_origins(supp(selected_claim) ∪ supp(c)) ≥ 2,
                     with ≥1 independent origin on each side }`
    — i.e. `Comp = { c ∈ Σ, c ≠ selected_claim : {selected_claim, c} satisfies the
    §A4 S1-firing predicate (conditions 1–3) }`. This is the frozen §A4 firing
    test applied with one side pinned to `selected_claim`. `[Finding 3]` added
    condition 3 (cross-origin independence) to the earlier `{contradicts ∧
    is_material}` membership, and nothing else, so that `Comp` cannot admit a
    same-origin material contradiction that does not itself fire S1.
  - **if `Comp ≠ ∅`** (`selected_claim` forms an S1-firing pair with some claim
    in `Σ`): the competing claim is the `≺`-maximal element of `Comp`.
  - **else** (`Comp = ∅`: every S1-triggering pair is disjoint from
    `selected_claim`): the competing claim is the `≺`-maximal element of the
    **S1-participant set** `[Finding 2]`
    `Part = { c ∈ Σ : ∃ c' ∈ Σ, c' ≠ c,
              contradicts(c, c') ∧ is_material(c, c')
              ∧ independent_origins(supp(c) ∪ supp(c')) ≥ 2
                with ≥1 independent origin on each side }`
    — the claims that make the §A4 S1-firing predicate (conditions 1–3) true.
  Whenever S1 fires, `Part ≠ ∅` (that is what makes S1 fire), so the competing
  claim — hence `contradiction_doc_ids` — is **total** over every input on which
  S1 fires, and in **both** branches the competing claim is a member of an
  S1-firing pair (so `contradiction_doc_ids` faithfully witnesses the
  contradiction that caused S1). The fallback and the `Comp` filter reuse only
  frozen machinery (§A4 conds 1–3, the §A1/§A2 order, `EVIDENCE_ORDERING_KEY`):
  no new predicate, no new constant, no new input.
- `support_doc_ids` = the supporters of `selected_claim`, ordered by
  `EVIDENCE_ORDERING_KEY`.

This makes `support_doc_ids` / `contradiction_doc_ids` in S1 well-defined
"with respect to the selected claim," matching the frozen output-type contract,
and lets PA-4's `DEBATED` template *represent both alternatives with source
attribution while asserting neither* (§A7 assertion gate).

### A5 — `is_material` canonical contract (item 4)

**RULING.** The canonical public (package-internal) interface is the **two-claim
form**:

```
is_material(claim_a: CandidateClaim, claim_b: CandidateClaim) -> bool
```

parameterized by `CONTRADICTION_MATERIALITY_PARAMS` (T1 §5.4). Returns `True`
iff the contradiction between `claim_a` and `claim_b` is material (incompatible
in substance), `False` for trivial/stylistic variation.

- The single-argument form `is_material(contradiction)` (MODULE_SPEC §7) is
  **rejected**: no `Contradiction` type exists in the frozen `types.py`, and
  introducing one would be a redesign of the frozen leaf types. MODULE_SPEC §7
  is reworded to the two-claim form (§B1).
- **Precondition (frozen).** `is_material` is only meaningful when
  `contradicts(claim_a, claim_b)` is `True`. On a non-contradicting pair its
  result is defined as `False` and it is not invoked (§A4). Materiality is the
  *filter on a contradiction*, never a standalone similarity test.

### A6 — `contradicts` status: PACKAGE-INTERNAL, RETAINED (item 5)

**RULING.** `contradicts(claim_a, claim_b) -> bool` is **package-internal**, and
is **retained** (neither public nor removed).

- **Not public.** Program A's *public* surface is exactly the two callables
  `answer_query` and `mechanism_id` (T1 / FINAL_ARCHITECTURE PA-4). Everything
  in PA-1..PA-3, including all of `support_tests.py`, is package-internal. The
  word "public" in `PROGRAM_A_MODULE_SPEC.md` §7 ("Public names: the four
  predicates") means *module-level names within `program_a`*, **not** part of
  the two-callable external API. §B1 reconciles that wording to
  "package-internal predicate names" to remove the ambiguity.
- **Not removed.** `contradicts` has a distinct, non-redundant role in the S1
  composition (§A4 step 1): it is the *incompatibility* test, separate from
  `is_material`'s *materiality* filter. The two compose as
  `contradicts(a,b) ∧ is_material(a,b)`. Collapsing them into a single
  predicate would be a redesign and is out of scope; keeping them separate
  preserves the frozen four-predicate register of `support_tests.py`
  (`supports`, `contradicts`, `is_material`, `independent_origins`).
- **Consumers.** Only `program_a/mechanism/evidence_states.py` (`classify`) and
  `is_material`'s precondition consume `contradicts`. Nothing outside
  `program_a` may import it (deny-list unchanged).

### A7 — PA-3 → PA-4 seam: the `selected_claim` invariant (item 7)

**RULING.** The seam is governed by three frozen invariants over
`EvidenceStateResult`. Together they completely determine `selected_claim`,
`support_doc_ids`, `contradiction_doc_ids`, and `independent_origin_count` in
every state, and gate assertion by state rather than by nullity.

**I-1 (nullity).** `selected_claim = None` **⟺** `state = S0`. For S1, S2, and
S3, `selected_claim` is the non-`None` winner of the §A1/§A2 selection rule.

**I-2 (assertion gate).** PA-4 emits `selected_claim` as a *hedged or asserted
fact* **⟺** `state ∈ {S2, S3}` (→ `PROBABLE` / `CERTAIN`). In **S1**,
`selected_claim` is carried **for source-attribution of the alternatives only**;
the frozen `DEBATED` template represents both sides and asserts no single
resolution (CR-9 structural coupling — answer form and tier both derive from
the one `EvidenceStateResult`; there is no code path that asserts a claim
outside `{S2, S3}`). The FM-1 guard ("`CERTAIN` only with `state == S3`") is
therefore *tier-gated*, and is not weakened by S1 carrying a non-`None`
selected_claim.

**I-3 (anchoring & witnesses).** `support_doc_ids` is **always** computed with
respect to `selected_claim`. `contradiction_doc_ids` is computed with respect to
`selected_claim` **iff** `selected_claim` forms an S1-firing pair with some claim
in `Σ` — equivalently `Comp ≠ ∅` under the §A4-conds-1–3 definition of `Comp`
(§A4) — and otherwise with respect to the S1-triggering pair (the §A4 `Part`
fallback). `[Finding 2]` introduced the `Comp`/`Part` reconciliation; `[Finding 3]`
tightened the guard to the S1-firing biconditional above. Both are ordered by
`EVIDENCE_ORDERING_KEY`, and satisfy per state:

| State | `selected_claim` | `support_doc_ids` | `contradiction_doc_ids` | `independent_origin_count` |
|---|---|---|---|---|
| **S0** | `None` | `()` | `()` | `0` |
| **S1** | §A1/§A2 winner (non-`None`) | supporters of selected_claim | supporters of the §A4 competing claim — the `≺`-maximal claim **forming an S1-firing pair with** `selected_claim` (§A4 conds 1–3), or (if none) the `≺`-maximal S1-participant (§A4 `Part`). In either branch the competing claim is a member of an S1-firing pair. `[Finding 2/3]` | `ios(selected_claim)` (≥1) |
| **S2** | §A1/§A2 winner (non-`None`) | supporters of selected_claim | `()` | `1` |
| **S3** | §A1/§A2 winner (non-`None`) | supporters of selected_claim | `()` | `≥ MIN_INDEPENDENT_ORIGINS_FOR_S3` (=2) |

**Derived, mechanically-checkable seam invariants** (added to
`test_evidence_states.py` at build, per §B):

- `contradiction_doc_ids ≠ ()` **⟺** `state = S1`.
- `selected_claim = None` **⟺** `state = S0`.
- `independent_origin_count = ios(selected_claim)` in **every** state (`ios` over
  the empty support set `= 0`, so S0 reports `0`). Unconditional consequences:
  `independent_origin_count = 0` **⟺** `state = S0`, and
  `independent_origin_count ≥ 1` **⟺** `state ∈ {S1, S2, S3}`. The count alone
  does **not** discriminate S1 from S2/S3: S1's selected_claim may carry
  `ios = 1` (e.g. two single-origin claims from two *distinct* origins that
  materially contradict), because §A4 tests independence on the union
  `supp(a) ∪ supp(b) ≥ 2`, **not** on the selected claim individually. Count-based
  discrimination is valid only **after** excluding S1 — which the seam already
  detects structurally via `contradiction_doc_ids`: given
  `contradiction_doc_ids = ()` (**⟺** `¬S1`, §A3 precedence has S1 fire before the
  S2/S3 `ios` split), `independent_origin_count = 1` **⟺** `state = S2` and
  `≥ 2` **⟺** `state = S3`.
- an assertion-bearing answer co-occurs only with `state ∈ {S2, S3}` (CR-9).

---

## A6-DIGEST — Digest coverage: which PA-3 rules are mechanism-defining (item 6)

**RULING.** The **mechanism-defining PA-3 rule set** — the objects whose change
is a mechanism change (T1 §11) and which are therefore bound by the frozen
mechanism identity — is exactly:

**Parametric (numeric/structural constants; already in the T1 §5 register and
already serialized into `frozen_constants_digest()`, T1 §6.1):**
`MIN_INDEPENDENT_ORIGINS_FOR_S3`, `INDEPENDENCE_RELATION`,
`SUPPORT_TEST_PARAMS`, `CONTRADICTION_MATERIALITY_PARAMS`,
`EVIDENCE_ORDERING_KEY`, `EXTRACTION_PARAMS` (PA-2, feeds PA-3), plus the
structural `STATE_TIER_MAP` and `CONFIDENCE_TIERS`.

**Structural rules (prose decision rules, previously bound only by the document
commit-pin and by `evidence_states.py` under §11 change-control, but NOT by the
runtime digest):**
(i) the frozen precedence `S0 → S1 → (S2|S3)` (§A3);
(ii) the claim-selection rule (§A1);
(iii) the deterministic tie-break total order `≺` (§A2);
(iv) the S1 composition rule and its anchoring (§A4);
(v) the `selected_claim` seam invariants I-1/I-2/I-3 (§A7).

**Closure of the coverage gap.** Rules (i)–(v) introduce no new numeric
constant, so they were not previously reflected in the digest; a silent edit to
the *rule text* would not have tripped the runtime tripwire (only CI file-diff
under §11). To restore the "two independent drift detectors" property (T1 §9.2)
at runtime, the frozen-constant serialization input to `frozen_constants_digest()`
is **extended by one structural tag**:

```
PA3_RULESET_VERSION: str   # merged value: "pa3-ruleset-2026-07-13"
                           # (was "pa3-ruleset-2026-07-09" pre-merge)
```

- It carries **no probability, no numeric evaluation constant** — it is a pure
  identity string, in the same class as `SPEC_VERSION`.
- It is transcribed verbatim into `program_a/constants.py` at G4 and folded
  into the ordered serialization that `frozen_constants_digest()` hashes
  (T1 §6.1), alongside the eight existing register entries.
- Any edit to rules (i)–(v) requires bumping `PA3_RULESET_VERSION`, which
  changes the digest → fails the `CONSTANTS_HASH` equality test → forces a new
  `mechanism_id()` (T1 §9). Rule drift is now mechanically un-landable green,
  identically to constant drift.

**Merge consequence for the digest `[Findings 1–3]`.** Finding 1 edits the S2/S3
*state definitions* and *tier arguments* (T1 §3.1/§4, §A0) — objects **not** in
the digest-covered set (i)–(v) — so it is **digest-neutral** and requires no
bump. Findings 2 and 3 both edit rule **(iv)** (§A4 S1 anchoring) and its seam
restatement **(v)** (§A7 I-3): Finding 3 is a *strict subset edit* of the same
rule (iv) Finding 2 touches. By the contract above this is exactly one drift
event on rules (iv)/(v), so `PA3_RULESET_VERSION` advances **once** — to
`pa3-ruleset-2026-07-13` — and is computed a **single** time, at the still-future
G4 pin, over the fully-corrected §A4/§A7 ruleset (Finding 2's `Comp`/`Part`
split with Finding 3's cond-3 conjunct on `Comp`). There is no double-bump and no
re-freeze of an already-pinned object (ES-1/PA-3 is pre-G4 DRAFT; no
`mechanism_id()` has been minted). Only the *value* of an existing digest input
advances — no input is added or removed, and **no numeric constant** is
introduced; the CR-8/L8 firewall is intact.

**Not mechanism-defining (excluded from the identity, unchanged):** answer
*rendering* niceties above the frozen `ANSWER_TEMPLATES`, `seed` (unused,
T1 §7.2), and anything in the EXP-1 evaluation layer (T1 §2).

---

## B. Required T1 / spec wording updates (reconciliation, owned)

These are wording reconciliations that *follow from* the rulings above. They are
transcription/edit actions applied at (or before) the G4 pin; none reopens a
design question.

- **B1 — `PROGRAM_A_MODULE_SPEC.md` §7.** Change the predicate register to the
  canonical signatures: `is_material(claim_a: CandidateClaim, claim_b:
  CandidateClaim) -> bool` (was `is_material(contradiction)`); relabel "Public
  names" → "Package-internal names" for the four predicates. Closes the item-4
  signature ambiguity and the item-5 "public" ambiguity. (Reconciles the
  MODULE_SPEC ↔ API_REFERENCE conflict; API_REFERENCE §8 is already canonical.)
- **B2 — `PROGRAM_A_API_REFERENCE.md` §8 `EvidenceStateResult`.** Reword
  `selected_claim` doc from "…or `None` if the state is `S0`" to the I-1 form:
  "non-`None` for `S1`/`S2`/`S3` (the §A1/§A2 selected claim); `None` **iff**
  state is `S0`." Add the I-3 witness table semantics for `support_doc_ids` /
  `contradiction_doc_ids` per state.
- **B3 — `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §5.** Add the register row
  `PA3_RULESET_VERSION` (structural identity tag, §A6-DIGEST) with "transcribe
  verbatim at G4," and update §6.1 to list it among the digest inputs.
- **B4 — `PROGRAM_A_FINAL_ARCHITECTURE.md` §4 PA-3.** Add the one-line pointers
  to §A1 (selection), §A2 (tie-break), §A4 (S1 composition), §A7 (seam
  invariant); this is the DRF-04 field-name reconciliation neighborhood
  (`support_doc_ids`/`contradiction_doc_ids` already canonical in `types.py`).
- **B5 — `tests/program_a/test_evidence_states.py`.** Add the §A7 derived
  seam-invariant assertions and a selection/tie-break determinism case
  (multi-claim, equal-corroboration tie resolved by §A2). Post-GO, Wave 4;
  spec fixed here.
- **B6 — `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §3.1 and §4 `[Finding 1]`.**
  Transcribe the corrected S2/S3 state rows (§3.1) and S2/S3 semantic openers
  (§4) verbatim from §A0: "no material contradiction" → "no material
  contradiction **across independent sources**." Digest-neutral erratum (§A0,
  §A6-DIGEST): no `SPEC_VERSION` or `PA3_RULESET_VERSION` change follows from B6
  alone. Behavior-preserving — the corrected definitions state what §A3/§A4
  already compute.

No change to PA-1, PA-2, PA-4, or PA-5 *contracts*; no change to
`STATE_TIER_MAP`, the tier set, the precedence order, or any numeric value.

---

## C. Verdict

**PASS — PA-3 is fully specified.**

With rulings §A1–§A7 and the digest-coverage closure §A6-DIGEST, the frozen T1
mechanism now completely determines PA-3 behavior for every input:

- claim selection is total and deterministic (§A1),
- ties are broken by a frozen strict total order over already-frozen keys
  (§A2),
- S1 is a fully composed predicate over `contradicts` ∧ `is_material` ∧
  cross-origin independence, with anchoring that is **total and faithful** —
  `contradiction_doc_ids` is defined for every S1-firing input and always
  witnesses a genuine S1-firing pair (§A4, as merged from `[Finding 2]` totality
  + `[Finding 3]` faithfulness),
- `is_material` has one canonical signature (§A5),
- `contradicts` has a fixed status and role — package-internal, retained
  (§A6),
- the `selected_claim` seam is governed by three mechanically-checkable
  invariants across S0/S1/S2/S3 (§A7),
- and the mechanism-defining rule set is bound to the runtime identity via
  `PA3_RULESET_VERSION` (§A6-DIGEST).
- the S2/S3 state definitions are self-consistent with the frozen precedence:
  they exclude only material contradictions **across independent sources**, so a
  same-origin self-contradiction that fires S2/S3 by `ios` satisfies the state
  definition it fires (§A0, `[Finding 1]`); the four states are exhaustive and
  mutually exclusive with no residual contradiction-free region.

**No new numeric constant, no probability, no evaluation-side value introduced**
— CR-8/L8 firewall intact; ordinality-by-construction preserved.

**Conditions on this PASS (identical in kind to the parent T1 object — these are
ratification/transcription steps, not open design questions):**

1. Co-pinned with the T1 object at G4 under B2 (ScientificAuditor sign-off) and
   B3 (ReleaseManager freeze). Until then: DRAFT, standing prohibition in force.
2. `PA3_RULESET_VERSION` transcribed into `program_a/constants.py` at G4 and
   folded into `frozen_constants_digest()` (§A6-DIGEST / B3).
3. The wording reconciliations B1–B5 applied at the freeze commit.
4. The numeric *values* of `SUPPORT_TEST_PARAMS` and
   `CONTRADICTION_MATERIALITY_PARAMS` (which §A4 composes) are fixed at G4 from
   the T1 §5 register — this is the pre-existing T1 transcription duty, not a
   PA-3 ambiguity introduced or left open here.

**Remaining blockers to the *specification*: NONE.** (Execution-gate items
already tracked in T1 — the §7 power amendment adjudication before G6/T11, the
Q8 identity ruling before any PASS-claim, and the CF-R4 leakage review at T2 —
are unchanged by this addendum and are not PA-3 specification gaps.)

---

---

## D. Co-freeze ratification (BLANK — flips to FROZEN only at the G4 freeze step)

No approval is fabricated by this addendum's author. This addendum is a rider
to the T1 object; it becomes **FROZEN** if and only if the T1 object's B2
(ScientificAuditor) and B3 (ReleaseManager) sign-off blocks
(`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` Section 12) are completed at the
G4 freeze step. Until then this addendum remains **DRAFT** and the standing
prohibition (`ES1_IMPLEMENTATION_GATE.md`:91-93) is in force.

The single G4 co-freeze also ratifies the three merged A3.5 corrections
(`[Findings 1, 2, 3]`), which ride the same B2/B3 sign-off and open no separate
approval. At the pin the ReleaseManager applies the §A0/§B6 Finding-1 edits to
T1 §3.1/§4, the merged §A4/§A7 Finding-2+3 anchoring text, and transcribes the
**single** advanced `PA3_RULESET_VERSION = pa3-ruleset-2026-07-13` into
`program_a/constants.py` (§A6-DIGEST).

- **Co-freeze (rides T1 Section 12 B2/B3):**
  - ScientificAuditor (T1 Section 12 B2): ____________________ , date: __________
  - ReleaseManager (T1 Section 12 B3): ____________________ , pinned commit: ____________________ , `PA3_RULESET_VERSION`: ____________________ , date: __________
  - Addendum status on completion: DRAFT → FROZEN

---

## E. Merge summary (change log — every merged correction tagged to its Finding)

Editorial merge only. Each row is a clause edited *exactly* as its source
correction specifies; no clause was redesigned, reworded beyond the correction,
or newly discovered here.

| # | Clause (location in this addendum) | Before (frozen) | After (merged) | Finding | Behavior change? |
|---|---|---|---|---|---|
| 1 | **§A0 → T1 §3.1 S2 row** (via §B6) | "…no material contradiction." | "…no material contradiction **across independent sources** (confined to a single origin ⇒ not S1, §A4 cond. 3)." | **F1** | None (definition now matches §A3/§A4 behavior). |
| 2 | **§A0 → T1 §3.1 S3 row** (via §B6) | "…no material contradiction." | "…no material contradiction **across independent sources** (…§A4 cond. 3)." | **F1** | None. |
| 3 | **§A0 → T1 §4 S2 opener** (via §B6) | "…there is no material contradiction…" | "…no material contradiction **across independent sources**…" | **F1** | None. |
| 4 | **§A0 → T1 §4 S3 opener** (via §B6) | "…there is no material contradiction…" | "…no material contradiction **across independent sources**…" | **F1** | None. |
| 5 | **§A4 `contradiction_doc_ids` bullet** | `≺`-max of `{ c ∈ Σ : contradicts(sc,c) ∧ is_material(sc,c) }`; undefined when that set is empty. | `Comp`/`Part` split with empty-set `Part` fallback ⇒ **total** on every S1-firing input. | **F2** | Defines a previously-**undefined** field; no already-defined output changes. |
| 6 | **§A4 `Comp` membership** | `{ contradicts ∧ is_material }` (no cond-3 filter). | `{ contradicts ∧ is_material ∧ cross-origin (cond 3) }` ⇒ `Comp` ⊆ old `Comp`; competing claim is always a genuine S1 participant. | **F3** | Changes `contradiction_doc_ids` **only** on the ios=1 same-origin-decoy class; all other outputs byte-identical. |
| 7 | **§A7 I-3 preamble** | "`support_doc_ids` and `contradiction_doc_ids` **always** wrt `selected_claim`." | `contradiction_doc_ids` wrt `selected_claim` **iff** `Comp ≠ ∅` (S1-firing biconditional), else wrt the `Part` pair. | **F2 → F3** | None beyond rows 5–6; wording made total & faithful. |
| 8 | **§A7 I-3 table, S1 row** | "supporters of the material-incompatible competing claim (§A4)." | "supporters of the §A4 competing claim — `≺`-max forming an S1-firing pair with `selected_claim`, or (if none) `≺`-max S1-participant; a member of an S1-firing pair either way." | **F2/F3** | None beyond rows 5–6. |
| 9 | **§A6-DIGEST `PA3_RULESET_VERSION`** | `pa3-ruleset-2026-07-09` | `pa3-ruleset-2026-07-13` (single advance; rules (iv)/(v) edited by F2/F3; F1 digest-neutral). | **F2, F3** | Identity-tag value only; no numeric constant, no digest input added/removed. |

**Rule numbering (Task 5).** No renumbering was required. Findings 2 and 3 edit
*within* existing rules §A4 (rule iv) and §A7 (rule v); Finding 1 is captured in
the new **§A0** and reconciliation entry **§B6**. The §A-rule set (§A1–§A7),
§A6-DIGEST rule list (i)–(v), and Section B numbering are otherwise unchanged.
The only added identifiers are §A0 (incorporated ES-1 correction) and §B6
(its T1 transcription action).

**Unchanged by every Finding (spot-preserved):** S0/S1 state definitions;
`STATE_TIER_MAP` / `CONFIDENCE_TIERS`; precedence `S0 → S1 → (S2|S3)` (§A3);
claim selection §A1; tie-break `≺` §A2; the S1-firing predicate §A4 conds 1–3;
`is_material`/`contradicts` contracts (§A5/§A6); every T1 §5 register constant;
the digest algorithm and its input **list** (§A6-DIGEST); `support_doc_ids`,
`independent_origin_count`, `state`, and `selected_claim` on every input.

## F. Consistency verification (post-merge — Task 6)

**F.1 No conflicting clauses remain.** The three findings edit disjoint or
strictly-nested regions:
- **F1** edits ES-1 state *definitions* / tier *arguments* (§A0 → T1 §3.1/§4).
  **F2** and **F3** edit the addendum's S1 *anchoring* (§A4) and *seam invariant*
  (§A7). F1's region is disjoint from F2/F3's region — no overlap, no conflict.
- **F2 vs F3** touch the *same* §A4 anchoring bullet and §A7 I-3. F3 is a strict
  refinement of F2: it (a) narrows the `Comp` set by adding one already-frozen
  conjunct (cond 3) — `Comp_F3 ⊆ Comp_F2`, and (b) tightens the I-3 wording to
  the S1-firing biconditional. The merged text carries F2's `Comp`/`Part`
  structure with F3's `Comp` membership and F3's I-3 wording; F3's wording
  *supersedes* F2's in the one shared location. No clause asserts both the F2 and
  the F3 form simultaneously — verified by inspection of §A4 and §A7. **No
  residual contradiction.**

**F.2 Invariants preserved.**
- *Exactly one state fires* (§A3 / T1 §3.3): the §A3 cascade is untouched; F1
  edits only outcome definitions, F2/F3 only the S1 payload inside the
  already-fired S1 branch. Preserved.
- *Exhaustiveness & mutual exclusion*: the S0/S1/S2/S3 partition of inputs is
  unchanged (no state boundary moved). After F1 the corrected S2/S3 definitions
  now *label* that partition with no residual region. Preserved and repaired.
- *Derived seam invariant* `contradiction_doc_ids ≠ () ⟺ state = S1` (§A7): in
  both the `Comp` and `Part` branches the competing claim ∈ `Σ` ⇒ `ios ≥ 1` ⇒
  ≥1 supporting item ⇒ `contradiction_doc_ids ≠ ()`; it stays `()` in S0/S2/S3.
  Preserved without edit.
- *I-1 (nullity)*, *I-2 (assertion gate / FM-1)*, S0/S2/S3 rows of I-3: untouched.

**F.3 Totality & faithfulness (the two defects closed).**
- **Totality (F2):** S1 fires ⟹ `Part ≠ ∅` ⟹ the competing claim exists ⟹
  `contradiction_doc_ids` is defined for every S1-firing input. Narrowing `Comp`
  (F3) can only move an input from the `Comp` branch to the (provably non-empty)
  `Part` branch, so it cannot break totality — F2's totality theorem holds
  verbatim under the merged `Comp`.
- **Faithfulness (F3):** `Comp` now admits only claims that form an S1-firing
  pair with `selected_claim` (cond 3 added); `Part` members are S1 participants by
  definition. So in both branches the competing claim participates in the
  S1-triggering contradiction. The `Comp ≠ ∅ ⟺ selected_claim participates`
  biconditional (§A7 I-3) holds exactly.

**F.4 Determinism / replay / digest coherence.**
- *Determinism & replay*: every merged clause is a pure function of frozen
  artifacts (`ios`, §A1/§A2 order, §A4 predicates, `EVIDENCE_ORDERING_KEY`); no
  `seed`, wall-clock, or hash-iteration order enters. Seed-invariant across the
  22 seeds. No prior replay is invalidated — ES-1/PA-3 is pre-G4 DRAFT with no
  minted `mechanism_id()`.
- *Digest*: F1 is digest-neutral (edits objects outside (i)–(v)); F2+F3 edit
  rules (iv)/(v) and jointly advance `PA3_RULESET_VERSION` **once** to
  `pa3-ruleset-2026-07-13`, computed a single time at G4. Consistent with the
  §A6-DIGEST tripwire contract; no numeric constant introduced; CR-8/L8 firewall
  intact. **Verified consistent.**

**F.5 Out-of-scope items (carried forward, unchanged — not "fixed" here).**
The S1 semantic oddity (an S1 result carrying a strongly-corroborated
`selected_claim` that nobody debates) is a design question, deliberately not
addressed. The §A2 tie-break injectivity dependency on PA-2 `EXTRACTION_PARAMS`
(audit F2/F2′, CONDITIONAL) is orthogonal and untouched; the merged `Comp` is a
subset of the pre-merge set, introducing no new tie surface.

**Verification result: PASS — the merged specification is internally consistent,
behavior-preserving where required, and free of conflicting clauses.**

---

*End of PA-3 freeze addendum (FINAL MERGED, `[Findings 1–3]`). Co-freezes with
the T1/G4 object.*
