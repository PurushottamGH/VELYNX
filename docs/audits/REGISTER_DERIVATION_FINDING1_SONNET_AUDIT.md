# REGISTER DERIVATION FINDING 1 — INDEPENDENT FALSIFICATION AUDIT (SONNET)

**Title:** Independent Scientific Audit of `PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` ("the
finding") — a methodological audit of the ES-1 register derivation methodology's claimed
uniqueness gap and its proposed E-SELECT correction.
**Role:** Independent Scientific Auditor. Not the author of the finding, the derivation method,
or any of the six-authority set. Adversarial by mandate.
**Auditor:** Claude Sonnet 5.
**Date:** 2026-07-14
**Status:** Independent audit artifact. Not a sign-off, not a B2/B3 record, confers no
ratification and chooses no register value. The parent freeze objects remain DRAFT / NO-GO per
`ES1_IMPLEMENTATION_GATE.md`:97-99 regardless of this audit's outcome.

---

## 0. Authorities and mission (as given)

Read in full, in this order: `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` ("T1"),
`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` ("the addendum"),
`PROGRAM_A_REGISTER_DERIVATION_METHOD.md` ("the method"), `PROGRAM_A_REGISTER_AUDIT.md` ("the
register audit"), `PROGRAM_A_G4_EXECUTION_PLAN.md` ("the G4 plan"), and
`PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` ("the finding" / "F1-DERIV", disambiguated from the
unrelated ES-1 state-definition "Finding 1" `[Finding 1]` referenced inside the addendum, which
is a different object entirely and is not re-adjudicated here).

**Mission tasks, verbatim intent:**
1. Determine whether the methodology truly lacks a unique choice function.
2. Attempt to derive the four deferred registers (`SUPPORT_TEST_PARAMS`,
   `CONTRADICTION_MATERIALITY_PARAMS`, `EXTRACTION_PARAMS`, `ANSWER_TEMPLATES`) without
   introducing any new methodological rule. Success falsifies the finding.
3. On failure, assess whether the proposed E-SELECT correction is necessary, sufficient, and
   minimal.
4. Attempt to falsify: uniqueness, determinism, replay preservation, digest stability, ES-1
   compatibility, PA-3 compatibility, and Findings 1–3 preservation.
5. Return one verdict: PASS / FAIL / UNDECIDABLE, with a written report.

**Nature of this audit.** Unlike the prior A3.5 Sonnet audits in this directory (which built
executable reference models against a mechanism specification), the object under review here is
itself a *methodology* document — there is no code to execute and no witness to replay. The
falsification method is therefore textual and logical: reconstruct the admissible-set structure
by hand from the six authorities, attempt an actual derivation, and stress-test the finding's own
proposed axes for soundness (existence and uniqueness of the claimed extremum) exactly as the
finding's own §4.1 CSP-b clause requires of any such axis.

---

## 1. Task 1 — Does the methodology truly lack a unique choice function?

Independently re-derived (not taken on the finding's authority): "canonical" is defined in
the method §2.5 as the conjunction of (1) per-register + universal constraints,
(2) invariant preservation, (3) a genuine B2 certification, (4) a ReleaseManager freeze. Items
(1)–(2) are predicates over a candidate value; (3)–(4) are operations that consume an
already-chosen candidate and test/transcribe it. A full read of method §§2–8 turns up no step of
the form "given the admissible set, compute/select the element" — §7 is explicitly a
*verification* of a *supplied* candidate ("Provenance separation (no proxy)... The candidate value
text... is supplied for the auditor to test"), and §8 is explicitly *transcription* of an
*already-certified* value ("The ReleaseManager introduces no value").

Cross-checking against the register audit (the independent 8-criterion grid, dated one day before
the method): Entries 5.3/5.4/5.6/5.7 are marked **FAIL (deferred)** on criterion 5 ("hidden tuning
freedom") for the three parametric registers and criterion 6 ("a-priori justification present, at
the value level") for all four — this is external, pre-existing confirmation (not authored by the
finding) that no value-level justification exists in the frozen authorities for any of the four,
which is consistent with — and independent evidence for — the finding's claim that no selector is
stated. The finding's contrast set (§2.2: `MIN_INDEPENDENT_ORIGINS_FOR_S3`, `SPEC_VERSION`,
`PA3_RULESET_VERSION`, `STATE_TIER_MAP`, `CONFIDENCE_TIERS`, `EVIDENCE_ORDERING_KEY`,
`INDEPENDENCE_RELATION`) is also independently verifiable: Entry 5.1's own register-audit text
states the constant is licensed by the structural-minimum argument "and **no other value**" —
i.e., that entry's own admissibility rests on an explicit, stated extremal argument, exactly the
species of selector the finding says is missing for the other four. This is accurate, not an
overstatement.

**Independent verdict on Task 1: CONFIRMED.** The methodology defines admissibility, not
derivability, for the four registers in scope. No choice function is stated anywhere in the six
authorities for any of the four.

---

## 2. Task 2 — Attempt to derive the four registers without a new methodological rule

Working strictly from the constraint layers already written (method §§3–6 part 2, T1 §5,
addendum §§A0–A7), I attempted to close each admissible set `A_r` to a singleton using only
already-stated a-priori arguments, with no new selection rule invented.

- **`SUPPORT_TEST_PARAMS`.** The stated constraints are: determinism, entity-level matching
  ("support requires the claim's entities be present in the evidence text, not mere topical
  proximity"), totality, firewall-clean, 3-field-schema-expressible, and ordering-stable.
  Multiple structurally distinct entity-level matchers satisfy every one of these clauses
  simultaneously — e.g., exact substring match on the claim's named entities vs. NFC-normalized
  match vs. a match requiring *all* claim entities present vs. only the head entity. No clause
  chooses among them. **Could not derive a unique value.**
- **`CONTRADICTION_MATERIALITY_PARAMS`.** Constraints: determinism, the §A5 precondition
  (defined only on `contradicts`-true pairs), symmetry, firewall-clean, distinctness from
  `contradicts`. Multiple materiality boundaries (e.g., "any semantic incompatibility is
  material" vs. "only incompatibilities on the queried predicate are material") satisfy all of
  these. **Could not derive a unique value.**
- **`EXTRACTION_PARAMS`.** Constraints: no model call, no randomness, entity-level, totality,
  output-type conformance, `claim_text` well-formedness. Multiple deterministic text-mechanics
  extractors (e.g., sentence-level vs. clause-level candidate boundaries) satisfy all of these.
  **Could not derive a unique value.**
- **`ANSWER_TEMPLATES`.** Constraints: one template per state, determinism, S0/S1 assert-no-fact,
  S2/S3 source-attributed (S2 hedged, S3 asserted), S1 represents both alternatives, slots bound
  only to permitted fields, firewall-clean. Indefinitely many distinct English strings satisfy
  every one of these clauses for a given state. **Could not derive a unique value.**

**Independent verdict on Task 2: FAILED to derive.** No new rule was invented; every constraint
already on the books was applied; in all four cases the admissible set remains multi-element
(strictly `|A_r| ≥ 2`, generally much larger). This independently reproduces the finding's own
Requirement-2 conclusion by a different route (direct attempted construction, rather than the
finding's proof-by-cases argument from evidence-class exhaustion).

**Consequence for Task 3.** Per the mission's own branching instruction: derivation failed, so
Finding 1's core claim (the gap exists) is **not falsified** by this task. Proceed to assess
necessity / sufficiency / minimality of the proposed E-SELECT correction.

---

## 3. Task 3 — Necessity, sufficiency, minimality of E-SELECT

### 3.1 Necessity — SURVIVES

Given Task 2's independently-confirmed result (`|A_r| ≥ 2` for all four, with no selector already
present), *some* explicit choice-function obligation is logically required to reach a singleton
without either (a) silently tightening the constraint/invariant layer (which the finding
correctly identifies at §4.1(iii) as a "disguised selection principle smuggled into the
constraint layer" — itself a real risk, since it would edit ES-1/PA-3 structure under cover of a
"constraint clarification") or (b) an ad-hoc, undocumented pick (barred by method §0.2 and by
T1's own B-13/CR-11 no-tuning mandate). E-SELECT's abstract shape — an a-priori, E-STRUCT-only
extremal axis plus a discharged uniqueness lemma — is a correct instance of "the smallest logical
object that converts a set into a point." **Necessity holds and I could not falsify it.**

### 3.2 Sufficiency — FALSIFIED for 3 of 4 concrete axes; the abstract obligation survives

This is where the finding does not survive scrutiny at the level of its own stated deliverable.
The finding's own general principle (§4.1, CSP-b) is explicit that an extremal axis is not enough
by itself: *"an extremal axis over a merely partial order can have several minimal elements;
without the lemma the selector may itself be multivalued and the gap is not closed."* The finding
then proposes four concrete axes (§4.2, restated with unqualified confidence in §7 as "the
minimum axes"). I tested each against the finding's own CSP-b bar — does the stated axis, in
fact, converge on a single well-defined element, or does it license a degenerate collapse or fail
to name a selector at all?

**(a) `SUPPORT_TEST_PARAMS` — least-permissive-admissible selector. FALSIFIED as stated.**
The finding's CSP-b for this row asks only to prove admissible support relations are "closed
under intersection and **bounded below by totality**." Totality, as used throughout the method
(§3.2: "defined for every `(claim, evidence)` pair"), is a claim about the relation being a
*total function* (it always returns `True` or `False`) — not a claim that it must classify a
non-empty set of pairs as `True`. Nothing in T1 §5.3 or method §3.2 states a floor excluding the
**always-`False`** relation (`supports(c, e) = False` for every `c, e`). That relation is
trivially deterministic, trivially "entity-level" (the entity-level clause is phrased as a
necessary condition — "support **requires** the claim's entities be present" — which the
always-`False` relation satisfies vacuously, since it never asserts support at all), trivially
total as a function, trivially firewall-clean, and trivially order-stable (its output never
varies). It is therefore a legal member of the ⊆-lattice's infimum and — being the unique
subset-minimal element of *any* ⊆-ordered family of relations that contains it — is very plausibly
**the** element the "least-permissive-admissible, ⊆-minimal" selector actually returns, unless an
explicit non-triviality floor is added. The finding's own "structural anchor" claim for this row
("the least-permissive test minimizes fabricated-claim false positives by construction, matching
the FM-1 guard") is one-sided: T1 §5.3's a-priori justification is written entirely in terms of
what the test must **not** do (admit fabrications, admit topical-but-non-supporting evidence) and
never states a positive floor (the test must actually recognize *some* genuine support). A
support test that never fires makes every query S0 by the §A3 cascade — the T1 §3.3 requirement
that "the S0 boundary... must remain exactly where the state table places it" is a one-directional
implication ("no support anywhere ⇒ S0") that this degenerate relation satisfies vacuously without
violating its letter, while plainly defeating the whole point of the mechanism. The only textual
guard against this in the six authorities is CF-R6 ("degenerate-tier probes may refute one that
makes a tier unreachable") — but that is explicitly framed in method §2.2/§3.1 as **E-DEV,
falsifying-only, dev-check evidence**, not an a-priori constraint usable inside a CSP-b proof. The
finding does not supply the missing floor, does not flag the omission, and its confident framing
("Directly serves CF-R2 dominance... matching the FM-1 guard the register exists to protect")
reads as settled rather than as an open lemma.

**(b) `EXTRACTION_PARAMS` — canonical-minimal-extraction selector. FALSIFIED as stated,
by the identical mechanism.** The proposed axis is "elect the admissible extraction yielding the
⊆-minimal claim set... subject to totality and the §A2 `claim_text`-injectivity precondition."
The always-empty extractor (`extract(doc) = ()` for every document) satisfies totality (as a
function), trivially satisfies injectivity of `claim_text` over an always-empty output (vacuously
— there are no two claims to collide), is trivially deterministic and entity-level (vacuously),
and is the global infimum of the ⊆-order on claim sets. Nothing in T1 §5.6 or method §5.2 states
a floor requiring the extractor to actually produce claims for non-degenerate input. Collapsing
`EXTRACTION_PARAMS` this way collapses `Σ` to `∅` for every query, which collapses ES-1 to
S0-only — a direct violation of the state-exhaustiveness *purpose* of the four-state design (T1
§3.3's exhaustiveness is a partition property that holds trivially over an all-S0 output, but
defeats the entire ordinality argument of T1 §4, which requires S1/S2/S3 to be reachable for the
per-tier semantic argument to mean anything). Same defect class as (a); same absence of an
explicit non-triviality floor in the finding's own CSP-b cell.

**(c) `ANSWER_TEMPLATES` — "canonical generator." FALSIFIED against the finding's own CSP-b
standard, on different grounds.** The finding itself concedes strings "carry no natural a-priori
order" and substitutes "selection by construction" for an extremal axis. But the finding's own
general principle (§4.1) requires CSP-b to prove that "that axis has exactly one
extremum/**representative**" — existence *and* uniqueness. The templates row's CSP-b only asks to
prove the realization function is "total... and single-valued" and that its *output* honors I-2
and CR-3. Totality and single-valuedness are properties every well-defined mathematical function
has *by definition*, once one particular function has already been picked — they say nothing
about which of the many distinct, equally rule-conforming realization functions is *the*
canonical one. Concretely: at minimum two realization functions — one producing "I don't have
enough information to answer this." for S0 and another producing "The available evidence does not
establish an answer to this question." for S0 — are both total, single-valued, assert no fact,
bind only to permitted fields, and honor CR-3/I-2. Nothing in the finding's proposed axis
distinguishes between them; "apply one fixed... realization function" begs the question of
*which* fixed function, which is exactly the multiplicity Finding 1's own §1 attacks in the base
methodology ("no a-priori rule that maps a multi-element admissible set to a *single* canonical
representative"). The templates row reproduces this identical defect one level down (from
"which string" to "which function") rather than resolving it.

**(d) `CONTRADICTION_MATERIALITY_PARAMS` — most-conservative-boundary selector. Comparatively
sound; not falsified, though the closure lemma remains genuinely unproven.** This is the one row
where the finding itself names an explicit floor — "closed under intersection **down to the
non-triviality floor** (a genuine incompatibility must remain material)" — which is at least
plausibly grounded in the §A5 precondition (materiality is defined as "the filter on a genuine
`contradicts` pair," which supports an argument that *some* contradicting pairs must be material
for the predicate not to collapse `is_material` into "always False," itself indistinguishable
from removing S1 entirely, in tension with the S1-vs-noise "frozen rule" language the register
audit and method both cite for this entry). I could not construct a clean degenerate
counterexample for this row the way I could for (a) and (b) — the finding's asymmetric treatment
(explicit floor here, no floor for the two parametric registers it structurally resembles) is
itself evidence the omission in (a)/(b) is a genuine oversight rather than an intentional
simplification.

### 3.3 Minimality — the abstract shape is minimal; the concrete deliverable is not yet correct,
so minimality cannot presently be assessed against a working target

The finding's argument for minimality (§4.1(i)–(iii)) is an argument about the *abstract*
component (§2.6: "adds nothing to the constraint/invariant layers... the smallest logical object
that can convert `|A_r| ≥ 2` to `|A_r| = 1`"). That argument is sound *given* a correct axis+lemma
pair exists for each register — minimality of a correction is only meaningful relative to a
correction that actually works. Since §3.2 above shows the concretely-proposed axes for three of
four registers do not close their admissible sets as claimed (they either license a degenerate
collapse or fail to name a selector), the finding has not yet exhibited a working correction to
compare for minimality; the true minimal fix is "§2.6, plus an explicit non-triviality floor for
`SUPPORT_TEST_PARAMS` and `EXTRACTION_PARAMS`, plus an actual selection criterion (not just
'construction') for `ANSWER_TEMPLATES`" — which is a strictly larger addition than what §4.2/§7
state.

---

## 4. Task 4 — Systematic falsification attempts

| Target | Result | Basis |
|---|---|---|
| **Uniqueness** | **FALSIFIED** for the concrete §4.2/§7 axes on 3 of 4 registers (§3.2 above); **SURVIVES** for the abstract §2.6 obligation and for the `CONTRADICTION_MATERIALITY_PARAMS` row. | Degenerate-collapse counterexamples (always-`False` support test; always-empty extractor) satisfy every stated constraint in T1/the method and are legal ⊆-infima; the templates axis never names a selector among realization functions. |
| **Determinism** | Not falsified. | E-SELECT is a meta-methodological obligation; it introduces no randomness, model call, or wall-clock dependency of its own. The degenerate counterexamples in §3.2 are themselves fully deterministic — the defect is about *which* deterministic function is picked, not about determinism per se. |
| **Replay preservation** | Not falsified. | Same reasoning; every candidate discussed (including the degenerate ones) is a pure function of frozen artifacts. |
| **Digest stability** | Not falsified. | §2.6 adds a methodology rule, not a register entry; it introduces no new input to `frozen_constants_digest()`. Independently re-confirmed against T1 §6.1 / addendum §A6-DIGEST's exact input list — §2.6 is not among the eight §5 entries, `PA3_RULESET_VERSION`, `STATE_TIER_MAP`, or `CONFIDENCE_TIERS`, and adding a *procedural* obligation about how those entries are chosen does not add a ninth input. |
| **ES-1 compatibility** | **At risk, not flatly falsified.** | The *abstract* §2.6 obligation does not touch any ES-1 object. But *adopting the concrete axes of §4.2 as written*, without first closing the gaps found in §3.2(a)/(b), carries a live risk of selecting a support test or extractor that collapses ES-1 to S0-only — which would violate the ordinality-by-construction backbone (T1 §4) that depends on S1/S2/S3 being reachable. This is a risk in the *unproven* lemma, not a proven violation, since a correctly-floored axis would not have this problem. |
| **PA-3 compatibility** | Same conditional status as ES-1 compatibility. | The `Comp`/`Part` totality theorem (Findings 2/3) is proved for "all admissible values," which is only meaningful if `A_r` is non-empty of *non-degenerate* values; a collapsed `Σ = ∅` extractor would make S1 (and hence `Comp`/`Part`) vacuously unreachable, not falsely computed — a different failure mode (vacuous truth) than an actual PA-3 contract breach, but still an undesirable degenerate outcome the finding's §5 preservation argument does not address. |
| **Findings 1–3 preservation** | **SURVIVES.** Not falsified. | The finding's §5 argument — that E-SELECT selects among values that are, by definition of "admissible," already invariant-preserving, and that no S2/S3 state definition, `Comp`/`Part` structure, or digest input is touched — is textually accurate against a direct re-check of addendum §§A0/A4/A7/A6-DIGEST. Even the degenerate counterexamples found in §3.2 do not falsify this specific claim: an always-`False` support test still leaves the S2/S3 *definitions* (Finding 1 of the addendum), the `Comp`/`Part` *formulas* (Findings 2/3), and the digest *input list* completely untouched — it just makes the S1/S2/S3 branches of those formulas unreachable in practice, which is an ES-1/PA-3-*compatibility* defect (above), not a Findings-1–3-*preservation* defect. This distinction is real and the finding's Requirement-5 argument holds up under it. |

---

## 5. Verdict

```
INDEPENDENT AUDIT (Sonnet 5): Register Derivation Finding 1 — FAIL (scoped)

  Task 1 (gap is real)                    : CONFIRMED — independently re-derived from the six
                                             authorities, not taken on the finding's word.
  Task 2 (derive without new rule)        : FAILED (as the finding predicts) — no selector
                                             exists in the current authorities for any of the
                                             four registers. Finding 1's core diagnosis SURVIVES.
  Necessity of E-SELECT (abstract §2.6)   : SURVIVES.
  Sufficiency of E-SELECT (concrete §4.2) : FALSIFIED for SUPPORT_TEST_PARAMS and
                                             EXTRACTION_PARAMS (missing non-triviality floor;
                                             degenerate always-reject/always-empty collapse is a
                                             legal member of the stated admissible set and the
                                             stated ⊆-minimal selector, absent further
                                             amendment, plausibly returns it); FALSIFIED for
                                             ANSWER_TEMPLATES (the axis never names a selector
                                             among realization functions — it relocates, rather
                                             than resolves, the multiplicity the finding itself
                                             defines as the disease). SURVIVES for
                                             CONTRADICTION_MATERIALITY_PARAMS (floor stated,
                                             closure lemma still unproven but plausible).
  Minimality                              : UNASSESSABLE against the stated §4.2 content, since
                                             that content is not yet a working correction; the
                                             actual minimal fix is strictly larger than what §4.2
                                             /§7 state (an added floor for two registers, an
                                             added selection criterion for the third).
  Determinism                             : Not falsified.
  Replay preservation                     : Not falsified.
  Digest stability                        : Not falsified.
  ES-1 compatibility                      : At risk (conditional on the unproven lemmas), not
                                             flatly falsified.
  PA-3 compatibility                      : At risk (conditional, same basis), not flatly
                                             falsified.
  Findings 1-3 preservation               : SURVIVES — not falsified, including under the
                                             degenerate counterexamples constructed above.
```

**Overall verdict: FAIL.** Finding 1's central diagnosis — that `PROGRAM_A_REGISTER_DERIVATION_
METHOD.md` specifies admissibility but not derivability for the four deferred registers, and that
this is by design rather than oversight — is **correct** and survives an independent, from-scratch
re-derivation attempt that introduced no new methodological rule and could not close any of the
four admissible sets to a singleton. Finding 1's Requirements 1–3 and its Requirements 6–8
boundary statement hold up entirely under this audit.

However, Finding 1's own stated deliverable — "the minimum scientific addition that **restores
uniqueness**" (§4 title), concretely instantiated as the four axes of §4.2 and restated with
unqualified confidence as "the minimum axes" in §7 — does not, in fact, restore uniqueness for
three of the four registers, when tested against the finding's *own* stated bar for a valid CSP
(§4.1's requirement of a *discharged* existence-and-uniqueness lemma, not merely a plausible-
sounding extremal description). `SUPPORT_TEST_PARAMS` and `EXTRACTION_PARAMS` both admit a
legal, fully-constraint-satisfying degenerate solution (the always-reject support test; the
always-empty extractor) that the stated "⊆-minimal" selector, absent an explicit non-triviality
floor the finding does not supply, plausibly returns — collapsing ES-1's four-state design to
S0-only, in tension with the ordinality-by-construction backbone the mechanism exists to
implement. `ANSWER_TEMPLATES`'s proposed "canonical generator" never actually names a selection
criterion among the many total, single-valued, semantically-conforming realization functions —
it restates the original multiplicity problem one level down rather than closing it. The finding
notably *does* supply the missing non-triviality floor for the fourth register
(`CONTRADICTION_MATERIALITY_PARAMS`) but not for the two structurally analogous parametric
registers, an unexplained asymmetry that is itself evidence the omission is a gap rather than a
deliberate simplification.

Because the mission specifically asked this audit to determine whether the proposed correction is
necessary, *sufficient*, and minimal, and because sufficiency fails for a majority of the
finding's own worked cases against the finding's own stated standard, this audit cannot return
PASS. It is not UNDECIDABLE either: the counterexamples in §3.2(a)–(b) are fully constructed from
already-frozen types and already-stated constraints, with no external or inaccessible fact
required, exactly as the finding's own methodology would demand of a legitimate falsification.

This audit does not ratify, approve, freeze, or choose any register value (that authority is
B2/B3/E4, per the finding's own §0 posture and the G4 plan). It recommends:

1. **The abstract §2.6 E-SELECT obligation be retained** — Task 1–2 and the necessity analysis
   found no defect in it, and no simpler correction was found during the independent derivation
   attempt.
2. **`SUPPORT_TEST_PARAMS` and `EXTRACTION_PARAMS` each be amended with an explicit
   non-triviality floor** in their CSP-a axis, symmetric to the one already present for
   `CONTRADICTION_MATERIALITY_PARAMS` (e.g., "the ⊆-minimal admissible relation subject to
   totality **and to classifying at least the evidence set demonstrating the E-STRUCT-cited
   design commitment as supporting/extracted**" or an equivalent E-STRUCT-grounded lower bound),
   before any CSP-b uniqueness lemma for these two registers is attempted, let alone certified.
3. **`ANSWER_TEMPLATES`'s CSP-a be replaced with an actual selection axis** over the space of
   realization functions (or the finding's own general principle be amended to explicitly permit
   a weaker "canonical form" standard for string-valued registers, argued and justified as its
   own exception to the CSP-b existence-and-uniqueness requirement — but the finding does not
   currently make or argue for that exception; it silently assumes it).
4. Any future remediation of this finding should re-run this audit's two constructed
   counterexamples (the always-`False` support relation; the always-empty extractor) as a
   regression check against any revised CSP-a floor, since both are legal, deterministic,
   firewall-clean, and satisfy every currently-stated constraint in T1 §5.3/§5.6 and method
   §§3.2/5.2 verbatim.

*End of independent falsification audit.*
