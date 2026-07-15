# REGISTER DERIVATION FINDING 2 — INDEPENDENT FALSIFICATION AUDIT (SONNET)

**Title:** Independent Scientific Audit of `PROGRAM_A_REGISTER_DERIVATION_FINDING2.md` ("F2-DERIV" /
"v2") — an adversarial attempt to falsify **E-SELECT v2**, the replacement Canonical Selection
Principle proposed in response to the prior Sonnet audit of E-SELECT v1.
**Role:** Independent Scientific Auditor. Did not author F2-DERIV, F1-DERIV, the method, or any of
the six-authority set. Adversarial by mandate.
**Auditor:** Claude Sonnet 5.
**Date:** 2026-07-14
**Status:** Independent audit artifact. Not a sign-off, not a B2/B3 record, confers no ratification
and chooses no register value. The parent freeze objects remain DRAFT / NO-GO per
`ES1_IMPLEMENTATION_GATE.md`:97-99 regardless of this audit's outcome.

---

## 0. Authorities and mission (as given)

Read in full: `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` ("the method"),
`PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` ("v1"),
`docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md` ("the prior audit"),
`PROGRAM_A_REGISTER_DERIVATION_FINDING2.md` ("F2-DERIV" / "v2", the object under review),
`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` ("T1"), `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` ("the
addendum").

**Mission tasks, verbatim intent:**
1. Replay every counterexample from the Finding 1 audit against v2.
2. Construct at least 10 new adversarial counterexamples against v2.
3. Attempt to falsify: CSP-c; exact structural realization; template skeleton uniqueness; uniqueness
   of canonical selection; determinism; replay; digest stability; ES-1 compatibility; PA-3
   compatibility.
4. Determine whether E-SELECT v2 is necessary, sufficient, minimal.
5. Return one verdict: PASS / FAIL / UNDECIDABLE.

**Nature of this audit.** As with the prior audit, the object under review is a methodology
document; there is no code to execute and no witness to replay. Falsification is textual and
logical: reconstruct each counterexample from the frozen types and stated constraints, and
adversarially stress-test v2's three changes (CSP-c, the re-anchored CSP-a, the template scope
correction) against v2's own stated bar for a valid CSP — a *discharged* existence-and-uniqueness
lemma, not a plausible-sounding axis (v1 §4.1; reaffirmed by v2 §0).

---

## 1. Task 1 — Replay of every Finding-1-audit counterexample against E-SELECT v2

### 1.1 CE-1 (always-`False` support) — replay: **excluded by v2, confirmed**

Under v2 Change B, the canonical `SUPPORT_TEST_PARAMS` element must equal the extension of the
frozen entity-presence predicate (a two-sided biconditional). The always-`False` relation
under-realizes that predicate on every pair where the claim's entities *are* present in the
evidence — it therefore fails the biconditional independently of CSP-c. It also fails CSP-c
directly (never fires ⇒ S1/S2/S3 all unreachable). **Independently re-confirmed: CE-1 is excluded
by v2, on two independent grounds (Change B and Change A).**

### 1.2 CE-2 (always-empty extractor) — replay: **excluded by v2, confirmed**

Symmetric to CE-1: the always-empty extractor under-realizes the candidate-boundary predicate
(Change B) and fails CSP-c directly (`Σ = ∅` always ⇒ S1/S2/S3 unreachable). **Independently
re-confirmed: CE-2 is excluded by v2.**

### 1.3 CE-3 (two S0 realization functions) — replay: **excluded for S0 as stated; the identical
defect re-opens one register-row later, at the S1 skeleton (see CE-9 below)**

For **S0** specifically, Change C's scope correction is defensible: the S0 answer binds no
`EvidenceStateResult` field (there is no `selected_claim`), so there is essentially no structural
freedom left once "assert no fact" is fixed — `f₀` ("I don't have enough information...") and `f₀′`
("The available evidence does not establish...") plausibly do collapse to one degenerate ("empty")
skeleton, and CE-3 as literally posed (an S0 pair) is closed.

However, replaying the **same construction one register-row later** — two structurally distinct
**S1** skeletons that both bind exactly the permitted fields (`selected_claim`,
`support_doc_ids`, `contradiction_doc_ids`), both honor the assert-nothing/represent-both force
marker (§A7 I-2), and both respect the `EVIDENCE_ORDERING_KEY`/§A2 slot order — shows the
skeleton/rendering line v2 draws is not actually load-bearing at S1's level of structural richness.
This is developed as **CE-9** below. **CE-3 is only partially closed: closed for the trivial state
(S0), reopened for the structurally rich state (S1).**

### 1.4 The fourth register (`CONTRADICTION_MATERIALITY_PARAMS`) — replay: **still no
counterexample supplied by v1/v2, but the underlying uniqueness lemma remains unproven and is
shown likely false below (CE-12)**

v2 reclassifies v1's existing floor as an instance of the now-general CSP-c and makes no other
change to this register. The prior audit already flagged the closure lemma ("closed under
intersection down to the non-triviality floor") as *asserted, not proven*. v2 does not discharge it
either. §2.12 below constructs a concrete obstruction to that closure claim.

---

## 2. Task 2 — Ten new adversarial counterexamples against E-SELECT v2

Each counterexample is a legal, deterministic, firewall-clean, type-conformant candidate — i.e., a
genuine member of the corrected `A_r` — that nonetheless defeats a specific claim v2 makes. Grouped
by the v2 mechanism they attack.

### Group A — Change B ("exact structural realization") does not produce a unique fixed point,
because the predicate it fixes to is itself not uniquely defined by T1/the addendum

**CE-4 — Evidence-scope ambiguity in "entity-presence" (`SUPPORT_TEST_PARAMS`).**
T1 §5.3 says support requires "the claim's entities be present **in the evidence text**." Nothing in
T1 or the addendum states whether "the evidence text" is scoped to a single `EvidenceItem` (the
natural reading, since `supports(c, e)` is defined per-pair, method §3.2) or to the **concatenation
of the whole `EvidenceSet`** for the query. Both are "entity-level, not topical" biconditional
fixed points of *a* version of the entity-presence predicate — both deterministic, total,
firewall-clean, 3-field-expressible. They diverge sharply on any query where a claim's entities are
scattered across multiple unrelated documents: item-scoped support never fires; set-scoped support
fires on every one of those documents simultaneously (inflating `ios` and, in the limit, threatening
S0 reachability the *other* direction). Change B's "equal to the extension of the frozen
entity-presence predicate" presupposes a single predicate; there are (at least) two,
non-equivalent, equally-licensed by T1 §5.3's text. **Falsifies: exact structural realization
(Change B) as a source of uniqueness.**

**CE-5 — Quantifier ambiguity: all-entities vs. head-entity vs. any-entity (`SUPPORT_TEST_PARAMS`).**
"The claim's entities" is plural without a stated quantifier. Three admissible readings — support
requires *all* named entities in the claim to be present, support requires *the head entity* only,
support requires *any* entity — are each "entity-level, not topical," each deterministic and total.
They produce different `supports` relations on any claim naming ≥2 entities where evidence mentions
only a subset (e.g. "Marie Curie won the Nobel Prize in Physics in 1903" against a document that
names Marie Curie but not the prize year). This is the same ambiguity the prior audit's Task 2
independently found when attempting to derive `SUPPORT_TEST_PARAMS` from the constraint layer alone
("a match requiring all claim entities present vs. only the head entity") — v2's Change B does not
resolve it, it only asserts a biconditional against an as-yet-unnamed predicate. **Falsifies: exact
structural realization.**

**CE-6 — Normalization ambiguity: exact-case vs. NFC-normalized case-insensitive match
(`SUPPORT_TEST_PARAMS`).** Exact byte substring match and NFC-normalized case-insensitive match are
both deterministic, entity-level, firewall-clean, and each is "equal to its own reading" of
entity-presence. They diverge on any evidence pair differing only in case or accenting (e.g.
"NASA" vs. "Nasa"; "café" vs. "cafe"). Both are structurally defensible; the method states no
normalization rule anywhere in §3.2, T1 §5.3, or the addendum. **Falsifies: exact structural
realization; independently confirms that "equal to the extension of the frozen entity-presence
predicate" is not, in fact, an equality against a unique object.**

**CE-7 — Candidate-boundary granularity: sentence-level vs. clause-level extraction
(`EXTRACTION_PARAMS`).** Both are deterministic, no-model-call, entity-level, and (by construction,
tagging `claim_text` with its span) can each independently satisfy the §A2 injectivity precondition.
On a single compound sentence carrying two entities and two distinct assertions ("Company X acquired
Company Y in 2019, and Company Y was later renamed Company Z in 2021"), sentence-level extraction
yields **one** conflated `CandidateClaim`; clause-level extraction yields **two**. Both
"equal their own reading" of the candidate-boundary predicate Change B invokes; nothing in T1 §5.6 or
method §5.2 chooses between them. This is the identical multiplicity the prior audit's Task 2
independently found ("sentence-level vs. clause-level candidate boundaries... satisfy all of
these"). **Falsifies: exact structural realization for `EXTRACTION_PARAMS`.**

**CE-8 — Maximal-span vs. minimal-span extraction on appositive constructions
(`EXTRACTION_PARAMS`).** On "Paris, the capital of France, hosted the 1900 Olympics," a
maximal-span extractor emits one claim spanning the whole appositive; a minimal-span extractor emits
two (the appositive identity claim and the hosting claim). Both are deterministic, entity-level, and
type-conformant; both can be made mutually injective. Both are "equal to a version of" the
candidate-boundary predicate. **Falsifies: exact structural realization**, and additionally
demonstrates that the residual "operationalization latitude" Change B says is "closed by minimal
operationalization latitude" is not actually closed — minimality of *what*, exactly, is left
unstated: minimal span-count per document, or minimal total claim count corpus-wide, or minimal
per-entity fragmentation? These give different winners on this exact example.

**CE-9 — Skeleton/rendering boundary ambiguity at S1 (`ANSWER_TEMPLATES`), reopening CE-3 one
level down.** Two S1 skeletons: (i) *"Sources disagree: `{selected_claim}` (per
`{support_doc_ids}`), while `{contradiction competing claim}` (per `{contradiction_doc_ids}`) is
also reported"* — with an explicit disagreement-framing clause; (ii) *"`{selected_claim}` (per
`{support_doc_ids}`); `{contradiction competing claim}` (per `{contradiction_doc_ids}`)"* — bare
juxtaposition, no framing clause. Both bind exactly the permitted `EvidenceStateResult` fields
(§A7 I-3), both assert neither claim (§A7 I-2 force = represent-both/assert-nothing), both respect
the §A2/`EVIDENCE_ORDERING_KEY` slot order Change C claims closes all residual ordering freedom.
They differ only in whether an explicit meta-level "this is a disagreement" framing clause is part
of the *skeleton* or merely *rendering*. §A6-DIGEST's "rendering niceties... Not mechanism-defining"
was written to classify wording style, not to adjudicate whether a whole clause of discourse
structure is skeleton or surface. Nothing in Change C's stated closure ("fields fixed by the rule,
force fixed by §A7 I-2, order fixed by §A2") pins this. **Falsifies: template skeleton uniqueness —
Change C's "uniquely defines... a unique fixed point per state" claim holds, at best, only for the
structurally trivial S0 row (§1.3 above), not for S1.**

### Group B — Structural/logical gaps in CSP-c itself (Change A)

**CE-10 — Compositional (joint) non-degeneracy gap: two individually-CSP-c-passing registers
whose composition is still S0-only.** CSP-c is stated and discharged **per register**: "there
exists admissible input under which the state fires" (v2 §4.1 Change A; §4.2 table). Nothing
requires that the witnessing input for one register's CSP-c lemma be reachable *given the other
three registers' selected values*. Construct: let the selected `SUPPORT_TEST_PARAMS` fire `True`
only when the evidence text contains the literal string `"ENTITY_ZERO_WITNESS"` (a synthetic
document exists under which this fires — CSP-c for support is discharged: S2/S3 are "reachable" in
isolation). Let the selected `EXTRACTION_PARAMS`, independently satisfying its own CSP-c via a
*different* synthetic witness (some document containing `"EXTRACTION_ZERO_WITNESS"`), never emit a
claim whose text contains `"ENTITY_ZERO_WITNESS"` on any real corpus document (nothing forces it
to — CSP-c only required the extractor's own witness to exist, not that the two witnesses
coincide). Composed as the actual PA-2 → PA-3 pipeline, `Σ` is empty on every input the real
mechanism will ever see: the support test's firing condition is never produced by the extractor.
**Both registers individually satisfy CSP-c as stated; their composition is S0-only — exactly the
disease CSP-c exists to cure.** This is not a defect of a specific pathological function; it is a
gap in the *general clause*: CSP-c is a per-register, existentially-quantified-over-the-rest
obligation, and per-register existential reachability does not entail joint reachability under a
fixed tuple of all four registers. **Falsifies: CSP-c (Change A) as a sufficient guarantee of
mechanism-level non-degeneracy; falsifies the "ES-1 compatibility: preserved" and "PA-3
compatibility: preserved" upgrades v2 claims in its §5 and §7 (both depend on S1/S2/S3 being
non-vacuously reachable in the *composed* mechanism, not per-register in isolation).**

**CE-11 — Abstract-input-space vs. actual-frozen-corpus scope mismatch (all three parametric
registers).** CSP-c's "there exists admissible input under which the state fires" is checked at
derivation time (pre-T2, before the CF-R4 leakage review and the corpus freeze, T1 §7.1). Nothing
ties the CSP-c witness to the space of documents the eventually-frozen `SnapshotStore` will actually
contain. A selected `SUPPORT_TEST_PARAMS`/`EXTRACTION_PARAMS` pair could satisfy CSP-c via a witness
document that is combinatorially possible under the abstract 3-field schema (e.g. a document whose
`origin_domain` is a specific pathological string, or whose text contains a rare token sequence) but
that never occurs anywhere in the actual frozen corpus — making the mechanism S0-only *in practice*
on the frozen dataset while remaining, on paper, "CSP-c compliant." Because CSP-c's reachability
quantifier is over the abstract input space and not over the corpus that will actually run, its
guarantee is weaker than "genuinely reachable" (v2's own phrase) suggests: it guarantees only
*analytic* non-vacuity, not *operational* non-vacuity on the frozen snapshot. **Falsifies: the
"genuinely reachable" reading of CSP-c as a real-world non-degeneracy guarantee, independent of any
specific pathological candidate function.**

**CE-13 — CSP-c's own stated inference is a non-sequitur for `EXTRACTION_PARAMS`: `Σ ≠ ∅` does not
entail S3 reachable.** v2's own table cell reads: "the selected extractor must emit ≥1 claim on ≥1
admissible input so `Σ ≠ ∅` **and S1/S2/S3 stay reachable**" (v2 §4.2, `EXTRACTION_PARAMS` row,
emphasis added). This inference is false as stated. Construct an "n-gram fragmentation" extractor:
every sliding token window of length *k* containing a named entity is emitted as its own candidate
claim, with `claim_text` tagged by its window offset to keep it injective (satisfying the §A2
precondition by construction). This extractor trivially satisfies CSP-c (`Σ` is large and non-empty
on almost every document — S0 essentially never fires). But because window boundaries are
offset-sensitive, two *documents* stating the same fact in slightly different phrasing almost never
produce byte-identical `claim_text` — so `ios(c)` (independent-origin support count, keyed on claim
identity) never exceeds 1 for any real claim, **even when the underlying fact is genuinely
corroborated by two independent documents.** `S3` (`ios ≥ MIN_INDEPENDENT_ORIGINS_FOR_S3 = 2`,
T1 §5.1/addendum §A3 step 3) is **permanently unreachable** under this extractor, on every input,
even though `Σ ≠ ∅` holds almost everywhere and S1/S2 remain reachable. `Σ ≠ ∅` guards against
*total* collapse to S0; it says nothing about whether claim-identity is stable enough across
documents for the corroboration count that S3 depends on to ever reach 2. This is a defect in the
document's own stated reasoning (a logical gap, not merely an adversarial function): the cited
justification for the `EXTRACTION_PARAMS` CSP-c cell does not entail the conclusion it is offered to
support. **Falsifies: CSP-c's discharge for `EXTRACTION_PARAMS` as stated in v2 §4.2; falsifies the
implicit claim that guarding `Σ ≠ ∅` is sufficient to keep *every* gated state (specifically S3)
reachable — the ordinality-by-construction backbone (T1 §3.3/§4) that CSP-c is grounded in requires
all four states reachable, not merely "not S0-only."**

### Group C — The materiality register's unproven closure lemma

**CE-12 — Antichain counterexample: two floor-respecting, ⊆-incomparable materiality boundaries
(`CONTRADICTION_MATERIALITY_PARAMS`).** v1's (and v2's unchanged) axis asserts admissible
materiality predicates are "closed under intersection down to the non-triviality floor," implying
a unique ⊆-least element exists above the floor. This closure is asserted, never proven, in either
v1 or v2. Construct two candidate predicates, both satisfying every stated constraint (determinism,
the §A5 precondition, symmetry, firewall-clean, distinctness from `contradicts`) and both
respecting the stated floor ("a genuine incompatibility must remain material"):

- **(i) Logical-incompatibility boundary:** material iff the two claims assert logically
  contradictory propositions about the same predicate slot (cannot both be true).
- **(ii) Polarity-boundary:** material iff the two claims differ in polarity (affirmation vs.
  negation) on the same entity-attribute pair; numeric claims differing only by degree
  (e.g., "the population is 5 million" vs. "the population is 5.2 million") are classified
  **non-material** (a rounding/precision variant, not an incompatibility) under (ii) but
  **material** under (i) (they cannot both be exactly true).

Both (i) and (ii) satisfy the floor: each still classifies *some* genuine incompatibility as
material (e.g., a direct factual negation), so neither collapses to always-`False`. Neither
predicate `⊆`-contains the other (each classifies at least one pair the other does not: the numeric
pair splits them; some other stylistic-negation pair could split the other way). Their **intersection**
(material only if *both* agree) reclassifies the numeric pair as non-material — consistent with (ii)
alone — but nothing prevents a third pair where *only* (i) respects the floor and (ii) does not,
in which case the intersection would violate the floor. **The "closed under intersection" claim is
therefore not free; it holds only if every admissible predicate agrees on which specific pairs are
floor-mandated — which is precisely what is not established anywhere in T1, the addendum, v1, or
v2.** The admissible family may not even be a lattice, in which case "⊆-minimal" may denote an
antichain of several incomparable minimal elements rather than one. **Falsifies: uniqueness of
canonical selection for `CONTRADICTION_MATERIALITY_PARAMS`; the CSP-b closure lemma this register
has always relied on (unchanged since v1) is unproven and, per this counterexample, plausibly
false.**

---

## 3. Task 3 — Systematic falsification attempts against the named targets

| Target | Result | Basis |
|---|---|---|
| **CSP-c (Change A)** | **FALSIFIED** as a sufficient non-degeneracy guarantee. | CE-10 (per-register existential reachability ≠ joint reachability under the composed mechanism); CE-11 (abstract-input-space witness ≠ operational reachability on the frozen corpus); CE-13 (the stated inference "`Σ≠∅` ⇒ S1/S2/S3 stay reachable" is a non-sequitur — S3 specifically can remain permanently unreachable). CSP-c *does* correctly exclude the two literal degenerate functions it was built to exclude (CE-1/CE-2, §1.1–1.2) — it is not vacuous, but it is materially weaker than v2 represents it to be. |
| **Exact structural realization (Change B)** | **FALSIFIED** as a source of uniqueness. | CE-4/CE-5/CE-6 (`SUPPORT_TEST_PARAMS`: scope, quantifier, and normalization ambiguity in "the entity-presence predicate"); CE-7/CE-8 (`EXTRACTION_PARAMS`: granularity and span ambiguity in "the candidate-boundary predicate"). In every case, "equal to the extension of the frozen role-predicate" only relocates v1's multiplicity into the choice of *which* predicate — the identical defect pattern the prior audit found in v1's `ANSWER_TEMPLATES` row ("apply one fixed function" presupposes the function already chosen), now reproduced for both parametric registers Change B was meant to fix. |
| **Template skeleton uniqueness (Change C)** | **FALSIFIED for S1; not falsified for S0.** | §1.3 (CE-3 replay) and CE-9: the skeleton/rendering line is defensible where there is no real structural freedom (S0), but is not established as a formal boundary, and fails to discriminate between two rule-conforming, field/force/order-identical S1 skeletons that differ in discourse framing. v2's claim ("uniquely defines... a unique fixed point per state") is stated for all four states without qualification and is not true of all four. |
| **Uniqueness of canonical selection (overall)** | **FALSIFIED for 3 of 4 registers; not established (unproven, not disproven) for the 4th.** | `SUPPORT_TEST_PARAMS`/`EXTRACTION_PARAMS`: relocated multiplicity (Group A) means `A_r` is still not a singleton. `ANSWER_TEMPLATES`: singleton only at S0, multi-element at S1 (CE-9). `CONTRADICTION_MATERIALITY_PARAMS`: the closure lemma it has always depended on is unproven and CE-12 constructs a concrete obstruction to it — this register survives only in the weaker sense that no full counterexample refutes it outright, not in the sense that uniqueness is established. |
| **Determinism** | Not falsified. | Every counterexample constructed above (CE-4 through CE-13) is a pure, deterministic function of frozen artifacts — no randomness, model call, or wall-clock. The defect in every case is *which* deterministic function/predicate is selected, never whether the selected object is deterministic. Consistent with the prior audit's finding on v1. |
| **Replay preservation** | Not falsified. | Same reasoning: all constructed candidates are pure functions of `(query_text, snapshot)`; byte-identical replay holds for each of them individually. |
| **Digest stability** | Not falsified. | v2 introduces no new register entry, no new numeric constant, and no new digest input (re-confirmed against T1 §6.1 / addendum §A6-DIGEST's exact input list, as in the prior audit). CSP-c and Change B/C are proof obligations on the *derivation*, not values, and add nothing to `frozen_constants_digest()`'s serialization. |
| **ES-1 compatibility** | **FALSIFIED back to "at risk"** — v2's claimed upgrade from the prior audit's "at risk" to "preserved" does not hold. | CE-10 (compositional gap: two per-register-non-degenerate registers can jointly collapse the mechanism to S0-only) and CE-13 (an extraction scheme can leave `Σ ≠ ∅` while permanently forbidding S3, silently degrading ES-1 to a 3-state mechanism) both show the ordinality-by-construction backbone (T1 §3.3/§4, which presupposes S1/S2/S3 — including S3 specifically — are reachable) can still be violated by a tuple of register values each individually certified non-degenerate under v2's own per-register CSP-c. |
| **PA-3 compatibility** | **FALSIFIED back to "at risk,"** on the same basis as ES-1 compatibility. | The `Comp`/`Part` totality theorem (Findings 2/3, addendum §A4/§A7 I-3) is proved "for all admissible values," which remains only vacuously true if the composed mechanism (CE-10) or the extraction scheme (CE-13) makes S1 non-vacuously unreachable or corroboration-count-dependent branches (S3) permanently dead. This is the identical "vacuous truth vs. genuine reachability" distinction the prior audit drew for v1 — v2's fixes do not close it at the compositional level. |

---

## 4. Task 4 — Necessity, sufficiency, minimality of E-SELECT v2

### 4.1 Necessity — SURVIVES

Nothing in this audit weakens the case that *some* explicit choice-function / non-degeneracy
obligation is required (the prior audit's Task 1–2 conclusions are untouched by anything found
here, and CE-1/CE-2/CE-3-at-S0 confirm v2's floor is a real, working improvement over v1's total
absence of one for two registers). **Necessity holds and is not falsified.**

### 4.2 Sufficiency — FALSIFIED

v2 states three specific completion claims (§4.3): "eliminates the degeneracy... makes uniqueness
reachable" (support, extraction), "uniquely defines" (templates), and upgrades ES-1/PA-3
compatibility from "at risk" to "preserved" (§5, §7). Every one of these four claims is falsified
above:

- Support/extraction: **not** merely "well-posed and reachable, lemma owed" — the axis itself
  (Change B) does not name a determinate predicate, so the residual multiplicity is not of the
  benign "final lemma not yet written" kind v2 characterizes it as; it is the same open multiplicity
  as before, one level down (CE-4–CE-8).
- Templates: "uniquely defines... per state" is false for S1 (CE-9).
- ES-1/PA-3 compatibility "preserved": false — the compositional gap (CE-10) and the
  `Σ≠∅ ⇏ S3-reachable` non-sequitur (CE-13) reopen exactly the reachability risk v2 claims to have
  closed, from directions v2's per-register CSP-c does not check.

**Sufficiency fails on a majority of v2's own stated deliverables, tested against v2's own stated
bar.**

### 4.3 Minimality — UNASSESSABLE against the stated content, for the same structural reason the
prior audit gave for v1

Minimality is only a meaningful property of a correction relative to a correction that actually
works. Since §4.2 shows v2 does not yet close the gaps it claims to close, comparing v2's size
against smaller/larger alternatives is premature. What can be said: an actually-sufficient
correction would need to be **strictly larger** than v2, specifically:

1. a **joint/compositional reachability clause** across all four registers simultaneously (not
   four independent per-register existentials) — CE-10;
2. **named, determinate predicates** for "entity-presence" and "candidate-boundary" (resolving
   scope, quantifier, normalization, and granularity) rather than an equality asserted against an
   as-yet-unnamed predicate — CE-4–CE-8;
3. either a **proof that the admissible materiality family is a lattice** with the claimed unique
   ⊆-least element, or an alternative selection principle for that register — CE-12;
4. a **template selection criterion that operates at the discourse-structure level**, not just the
   field/force/order level, for the non-trivial states (S1 in particular) — CE-9;
5. an explicit correction of the `Σ≠∅ ⇒ reachable` inference to the actually-needed claim (some
   claim identity achieves `ios ≥ 2` under some admissible input) — CE-13.

This is a strictly larger object than v2's three stated changes. **v2 is smaller than a working
correction, in the same sense v1 was smaller than v2 — it is an improvement in the same direction,
not a terminus.**

---

## 5. Verdict

```
INDEPENDENT AUDIT (Sonnet 5): Register Derivation Finding 2 — FAIL

  Replay of CE-1 (always-False support)         : Confirmed EXCLUDED by v2.
  Replay of CE-2 (always-empty extractor)        : Confirmed EXCLUDED by v2.
  Replay of CE-3 (S0 template pair)              : EXCLUDED at S0; REOPENED at S1 (new CE-9).
  Materiality register (no v1 counterexample)    : Still no full counterexample; closure lemma
                                                    unproven and shown likely FALSE (CE-12).

  10 new adversarial counterexamples (CE-4..CE-13): all legal, deterministic, constraint-satisfying
                                                    members of the corrected A_r; none requires any
                                                    fact outside the six authorities.

  CSP-c (Change A)                 : FALSIFIED as sufficient (CE-10, CE-11, CE-13) — correctly
                                      excludes CE-1/CE-2 but not the compositional or
                                      Σ≠∅-does-not-imply-S3-reachable failure modes.
  Exact structural realization (B) : FALSIFIED as a source of uniqueness (CE-4..CE-8) — relocates
                                      v1's multiplicity into an unnamed predicate rather than
                                      resolving it.
  Template skeleton uniqueness (C) : FALSIFIED for S1 (CE-9); holds only for the structurally
                                      trivial S0 row.
  Uniqueness of canonical selection: FALSIFIED for SUPPORT_TEST_PARAMS, EXTRACTION_PARAMS, and
                                      ANSWER_TEMPLATES (partially); UNPROVEN (not disproven) for
                                      CONTRADICTION_MATERIALITY_PARAMS, with a concrete obstruction
                                      to its relied-upon closure lemma (CE-12).
  Determinism                      : Not falsified.
  Replay preservation              : Not falsified.
  Digest stability                 : Not falsified.
  ES-1 compatibility                : FALSIFIED back to "at risk" (CE-10, CE-13) — v2's claimed
                                      upgrade to "preserved" does not hold.
  PA-3 compatibility                : FALSIFIED back to "at risk", same basis.

  Necessity                        : SURVIVES.
  Sufficiency                      : FALSIFIED (majority of v2's own stated deliverables fail
                                      against v2's own stated bar).
  Minimality                       : UNASSESSABLE against the stated content; the actual working
                                      fix is strictly larger (§4.3 lists five required additions).
```

**Overall verdict: FAIL.**

v2 is a genuine, correctly-reasoned improvement over v1: it accurately diagnoses v1's degenerate-
infimum defect (§0/§2/§3 of F2-DERIV), and its CSP-c floor does close the two literal degenerate
functions (always-`False` support, always-empty extraction) the prior audit used to falsify v1's
sufficiency. That diagnosis and that specific closure are **not** contested by this audit and are
independently reconfirmed in §1.1–1.2 above.

But v2's own stated deliverable is stronger than "closes the two counterexamples the prior audit
happened to name" — it claims to make support/extraction selection "well-posed and reachable,"
to "uniquely define" `ANSWER_TEMPLATES` selection for every state, and to upgrade ES-1/PA-3
compatibility from "at risk" to "preserved." Tested against v2's own stated bar (a *discharged*
existence-and-uniqueness lemma, and a *genuine*, not merely per-register, reachability guarantee),
each of these stronger claims fails: the re-anchored axis (Change B) relocates rather than resolves
the multiplicity for both parametric registers (CE-4–CE-8); the template scope correction (Change C)
resolves the multiplicity only at the state with no real structural freedom, not at S1 (CE-9); and
CSP-c's per-register, existentially-quantified reachability check does not entail — and in the
constructed n-gram-fragmentation case, is logically disconnected from — the actual mechanism-level
non-degeneracy property (specifically, S3 reachability) it is invoked to guarantee (CE-10, CE-13).

This audit cannot return PASS because sufficiency fails for a majority of v2's own worked
deliverables against v2's own stated standard. It is not UNDECIDABLE: every counterexample above is
built from already-frozen types and already-stated constraints, exactly as v2's own methodology
would require of a legitimate falsification, and several (CE-12, CE-13) are logical gaps in the
text's own stated reasoning rather than merely adversarial function constructions.

This audit does not ratify, approve, freeze, or choose any register value. It recommends:

1. **Retain CSP-c and the general Change-A obligation** — necessity is unaffected, and the floor is
   a real improvement over v1 for the two registers it was built to fix.
2. **Add a joint/compositional non-degeneracy clause**, discharged over the full four-register
   tuple (or at minimum the support × extraction pair), not four isolated per-register existentials
   (closes CE-10).
3. **Replace "equal to the extension of the frozen entity-presence / candidate-boundary predicate"
   with a fully named predicate** that fixes evidence scope, entity quantifier, normalization
   (`SUPPORT_TEST_PARAMS`), and span granularity (`EXTRACTION_PARAMS`) — an equality claim against
   an unnamed predicate cannot supply uniqueness (closes CE-4–CE-8).
4. **Correct the `EXTRACTION_PARAMS` CSP-c justification** from "`Σ≠∅` ⇒ S1/S2/S3 reachable" to the
   actually-required claim: some claim identity is stable enough across independent documents that
   `ios(c) ≥ MIN_INDEPENDENT_ORIGINS_FOR_S3` is achievable under some admissible input (closes
   CE-13).
5. **Either prove the admissible-materiality-family-is-a-lattice claim or replace the
   `CONTRADICTION_MATERIALITY_PARAMS` axis** with one that does not depend on it (closes CE-12).
6. **Extend Change C's closure below the field/force/order level** for states with real discourse
   structure (S1 in particular), or explicitly narrow the "uniquely defines" claim to the states
   where it actually holds (closes CE-9).
7. Any future remediation should re-run this audit's ten constructed counterexamples (CE-4–CE-13)
   as a regression check, in addition to the three inherited from the prior audit.

*End of independent falsification audit.*
