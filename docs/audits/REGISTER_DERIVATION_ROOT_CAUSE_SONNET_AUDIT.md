# REGISTER DERIVATION ROOT-CAUSE ANALYSIS — INDEPENDENT AUDIT (SONNET)

**Title:** Independent Scientific Audit of `PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md`
("the diagnosis") — is its verdict (root cause = **C**, incorrect abstraction boundary) correct?
**Role:** Independent Scientific Auditor. Not the author of the diagnosis, the method, either
Finding, or either prior audit. Adversarial by mandate.
**Auditor:** Claude Sonnet 5.
**Date:** 2026-07-14
**Status:** Independent audit artifact. Not a sign-off, not a B2/B3 record, confers no
ratification, chooses no register value, proposes no correction, and redesigns no part of the
methodology. The parent freeze objects remain DRAFT / NO-GO per `ES1_IMPLEMENTATION_GATE.md`:97-99
regardless of this audit's outcome.

---

## 0. Authorities and mission (as given)

Read in full: `PROGRAM_A_REGISTER_DERIVATION_METHOD.md`, `PROGRAM_A_REGISTER_DERIVATION_FINDING1.md`,
`PROGRAM_A_REGISTER_DERIVATION_FINDING2.md`, `PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md`
(the object under review), `docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md`,
`docs/audits/REGISTER_DERIVATION_FINDING2_SONNET_AUDIT.md`. Cross-checked against
`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §5 and `PROGRAM_A_REGISTER_AUDIT.md` Entries 5.1–5.9,
which the diagnosis quotes and which are independently re-read here rather than taken on the
diagnosis's word.

**Mission (verbatim intent):** determine whether the diagnosis's root-cause verdict is correct —
specifically whether the recurring failure is fundamentally **A** (missing selector), **B**
(missing semantic definitions), **C** (incorrect abstraction boundary), or **D** (another cause).
Do not propose a correction, redesign the methodology, or derive values. Return one verdict:
PASS / FAIL / UNDECIDABLE.

**Nature of this audit.** The object under review is itself a diagnosis, not a correction, so the
correct adversarial method is not "construct a counterexample that defeats a proposed axis" (as in
the two prior audits) but **"test the diagnosis's own claims against the evidence it cites."** The
diagnosis builds its verdict from a table of thirteen falsified items (v1-a/b/c, CE-4…CE-13) drawn
from the two prior audits and asserts a single invariant holds across all thirteen ("not one …
turns on … a selector defect … They all turn on the same thing: an undefined semantic"). That
invariant claim, and the minimality adjudication built on it, are directly checkable against the
source audits already in evidence. This audit checks them.

---

## 1. What independently re-verifies as correct

Before testing the verdict, the following load-bearing claims were independently re-derived (not
taken on the diagnosis's authority) and confirmed accurate:

1. **The T1 §5 value-column asymmetry (§2 of the diagnosis).** Read directly against
   `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §5: entry 5.5 (`EVIDENCE_ORDERING_KEY`) states its
   semantics inline — *"lexicographic on `(origin_domain, doc_id)`"* — a concrete extensional rule,
   not a placeholder. Entry 5.1 (`MIN_INDEPENDENT_ORIGINS_FOR_S3`) likewise states its semantics
   inline — *"2 is the smallest count that is corroboration at all"* — with the value `2` given
   directly in the table. By contrast, entries 5.3/5.6/5.7 give only *"the frozen deterministic …
   parameters (… exact parameters fixed at G4 from this register)"* — role, a prohibition list, and
   a deferral token, with no extensional rule of any kind. This is exactly what the diagnosis
   claims at §2, and it is independently confirmed against the primary text, not merely against the
   diagnosis's quotation of it.
2. **The PASS/FAIL split tracks this exactly.** `PROGRAM_A_REGISTER_AUDIT.md` confirms 5.1/5.2/5.5/
   5.8/5.9/§3.2 entries PASS and 5.3/5.4/5.6/5.7 FAIL (deferred) on criterion 8, with criterion 6
   ("a-priori justification present, value-level") marked FAIL specifically for the four in
   question. This is a genuine, pre-existing (not diagnosis-authored) control-group split, and it
   correlates with "semantics stated inline" vs. "semantics deferred," not with "selector present"
   vs. "selector absent" — `EVIDENCE_ORDERING_KEY` has no selector of any kind (nothing to select
   among; the rule already names one key) and still PASSes. This is real, independent evidence
   against a pure-`A` diagnosis and is correctly used by the diagnosis at §2.
3. **`D` collapsing into `C` (§4.4 of the diagnosis).** T1 is, in fact, a preregistration that
   explicitly defers these four values (T1 §5, "exact parameters fixed at G4 from this register").
   The defect is not that preregistration is missing but where its completeness boundary was drawn.
   This sub-argument is correct as stated and is not contested here.
4. **`E` (the regress) as a mechanism-of-`C` framing, not a fifth independent cause.** The
   value → function → predicate escalation across v1 → v2 → (v3?) is an accurate compression of the
   two prior audits' own findings (v1's degenerate infimum was closed by v2's CSP-c/Change-B pair
   only to have Change B's "exact structural realization" reopen the identical multiplicity one
   level down at the predicate — CE-4 through CE-9). This regress is real and correctly documented.

These four points are the strongest parts of the diagnosis and each independently re-verifies.

---

## 2. Where the diagnosis's own evidence contradicts its verdict

### 2.1 The claimed invariant is false for at least one of its own thirteen cited items

The diagnosis's central inferential move (§1, "The invariant") is: *"Every falsified item — without
exception — is a legal, deterministic, firewall-clean, type-conformant candidate that the
correction cannot exclude or cannot uniquely pin, **because some term in the register's own
definition carries no specified meaning.**"* This is the premise every later section (§2–§5) is
built on. It is checkable directly against the source audit, and it does not hold for **CE-13**.

Audit 2 (§2, Group B, CE-13) is explicit about what CE-13 actually is: *"This is a defect in the
document's own stated reasoning (**a logical gap, not merely an adversarial function**): the cited
justification for the `EXTRACTION_PARAMS` CSP-c cell does not entail the conclusion it is offered to
support."* Concretely: v2's own text asserts *"the selected extractor must emit ≥1 claim on ≥1
admissible input so `Σ ≠ ∅` **and S1/S2/S3 stay reachable**"* — an inference from `Σ ≠ ∅` to
S3-reachability that is simply invalid (the n-gram-fragmentation counterexample satisfies `Σ ≠ ∅`
everywhere while making `ios(c)` never exceed 1, so S3 is permanently unreachable). Every term in
this inference is already precisely defined: `Σ`, `ios(c)`, `MIN_INDEPENDENT_ORIGINS_FOR_S3 = 2`,
and S3-reachability are all fixed, unambiguous quantities under T1 §5.1/addendum §A3. **Nothing is
semantically undefined here.** The flaw is a non-sequitur in v2's own written proof, not an
undefined term. Authoring the missing layer-4 semantics for `SUPPORT_TEST_PARAMS`/
`EXTRACTION_PARAMS` — the diagnosis's own prescription (§6) — would not touch this defect at all:
CE-13's fallacious inference is present regardless of how precisely "entity-presence" or
"candidate-boundary" are eventually defined.

This one item is sufficient to falsify the diagnosis's stated invariant ("without exception … They
all turn on the same thing"), which is a false universal, not merely an approximation with one
outlier — the diagnosis nowhere qualifies or excepts CE-13.

### 2.2 CE-10 does not reduce to the boundary the diagnosis names in §4.1–4.2

The diagnosis locates `C` precisely: *"the boundary between 'methodology … contains no value' and
'canonical value (deferred to G4)' is drawn through the middle of the register's semantic
definition"* (§0), i.e., a **methodology-vs-value** boundary that misfiles layer-4 semantics onto
the wrong side. When §4.3 reaches CE-10 (the compositional/joint-reachability gap — two
individually-CSP-c-passing registers whose composition is still S0-only), it explains it with:
*"The **joint semantics of the composed mechanism** … is a layer-4 fact about the whole PA-2→PA-3
pipeline. The boundary partitions the registers into **four independently-deferred 'values'**, so
no layer owns the composition."*

This silently substitutes a **different** boundary — the methodology's register-by-register
partitioning of §§3–6, treating each of the four registers as an independently closeable slot —
for the methodology-vs-value boundary named in §4.1–4.2. These are not the same object: the first is
about *what kind of content* (semantics vs. value) may be stated; the second is about *how many
things at once* a single selector clause is required to quantify over. Confirmation that they are
distinct: audit 2's own recommendation for closing CE-10 (§5, rec. 2) is *"Add a joint/compositional
non-degeneracy clause, discharged over the full four-register tuple … not four isolated per-register
existentials"* — a pure change to CSP-c's **quantifier scope**, stated entirely in selector-layer
terms, naming no new semantic content and crossing no methodology/value boundary. It is, in the
diagnosis's own taxonomy, an instance of `A` (a differently-shaped selector), not `B`/`C`.

It is also independently checkable that authoring layer-4 semantics on the "correct" side of the
diagnosis's boundary would **not by itself** prevent CE-10: two fully, precisely, extensionally
defined predicates (an exact entity-presence rule and an exact candidate-boundary rule) can still
have an empty practical intersection on the frozen corpus unless a *separate* cross-register
joint-consistency property is checked. Moving semantics across the boundary is necessary for CE-4…
CE-9/CE-12; it is not sufficient for CE-10, and the diagnosis does not show otherwise — §4.3 asserts
the connection without demonstrating it.

### 2.3 Consequence: the flat rejection of `A` as pure misdiagnosis is overstated

§3.1 of the diagnosis states, without qualification: *"A choice function therefore presupposes
exactly the object that is missing. Adding a selector cannot supply a definition; it can only
assume one. This is why `A` is not merely insufficient but **category-mismatched** to the defect."*
And §5: *"Would supplying `A` (a selector) have prevented the failures? No … `A` cannot be the root
because adding it is the observed failure mode."*

This is contradicted by the diagnosis's own cited evidence. CSP-c — a pure selector-layer,
non-degeneracy obligation, containing no new semantic content whatsoever — is confirmed by audit 2
(§1.1–1.2) to have **successfully and permanently excluded** CE-1 (always-`False` support) and CE-2
(always-empty extractor): *"CE-1 is excluded by v2, on two independent grounds"*; *"CE-2 is excluded
by v2."* These exclusions are not reopened by any later counterexample in audit 2 — CE-4 through
CE-9 attack a *different* mechanism (Change B, the re-anchored extremal axis), and CE-10/CE-11/CE-13
attack CSP-c's *scope and internal inference*, not its ability to exclude the original degenerate
elements. A selector-layer object that permanently closes two of the three original counterexamples
is, by direct construction, **not** "ill-typed" or "category-mismatched" to those particular
defects. The diagnosis's §3.1 argument is a valid general point about selectors that presuppose
individuation over an undefined set (this is correctly why Change B fails against CE-4…CE-9), but it
is stated as if it covered every instance of `A`, and CSP-c is a direct, cited counterexample to that
universal framing within the diagnosis's own source material.

---

## 3. Net assessment against the diagnosis's own minimality test

The diagnosis's adjudication (§5) applies a specific test: *"the smallest condition whose removal
would have prevented **every** failed audit and stopped the recurrence."* It answers "yes" for `C`
without individually checking that answer against CE-10 and CE-13. §2.1–§2.2 above show that answer
does not hold for those two items:

- **CE-13** is a logical non-sequitur in a written proof. No placement of layer-4 semantics — on
  either side of any boundary — repairs an invalid inference. Correcting `C` does not prevent CE-13.
- **CE-10** is a quantifier-scope defect in the selector clause (per-register existential vs. joint).
  Audit 2's own remedy for it is selector-layer only. Correcting `C` is not shown to be necessary or
  sufficient to prevent CE-10, and a plausible construction (fully-defined predicates with empty
  joint intersection) shows it is not sufficient.

Both are drawn from the diagnosis's own evidence table (§1) and are asserted there, without
exception, to fit the "undefined semantic" pattern. They do not. Because the diagnosis's stated
method for identifying the *minimal* root cause is exactly this all-of-the-evidence test, and two of
its thirteen cited items fail that test on inspection, the verdict `C` is not established as the
complete, minimal explanation the diagnosis claims — even though it is, on the corrected reading
below, the dominant one.

**What survives independent re-verification:** `C` is a real, well-evidenced, independently
confirmable defect (§1 above) and is the correct explanation for the majority of the cited evidence
— the original v1-a/v1-b/v1-c pattern as re-diagnosed, and CE-4 through CE-9 and CE-12 (nine of
thirteen items: scope, quantifier, normalization, granularity, span, and discourse-level ambiguity,
plus the materiality antichain), all of which genuinely trace to an unauthored layer-4 semantic that
no selector, however well-shaped, can substitute for. `B` is correctly identified as downstream of
`C` for that majority. But `C` does not explain CE-10 or CE-13, and the diagnosis's blanket
dismissal of `A` ("category-mismatched," "the misdiagnosis") is directly contradicted by CSP-c's
confirmed, permanent exclusion of CE-1/CE-2 within the diagnosis's own cited source. A correct
statement of the evidence is closer to: **`C` is the dominant root cause for the register-definition
family of failures; a distinct, secondary defect — internal to the selector construct itself
(mis-scoped quantification and an unrigorous discharge step, arguably `D`) — independently accounts
for the compositional and inferential failures (CE-10, CE-13) and is not resolved by relocating
layer-4 semantics.** The diagnosis presents a single, unqualified cause where the evidence it itself
assembled supports a dominant cause plus an unacknowledged residual one.

---

## 4. Verdict

```
INDEPENDENT AUDIT (Sonnet 5): Register Derivation Root-Cause Analysis — FAIL

  Contrast-group evidence (T1 §5.1/§5.5 vs §5.3/§5.4/§5.6/§5.7)  : CONFIRMED, independently
                                                                     re-read against T1 directly.
  PASS/FAIL correlates with semantics-inline vs semantics-deferred,
  not with selector-present vs selector-absent                   : CONFIRMED.
  D collapses into C                                              : CONFIRMED, not contested.
  E (regress) as mechanism-of-C, not a fifth cause                : CONFIRMED, accurate compression
                                                                     of the two prior audits.

  Stated invariant ("every falsified item … an undefined semantic",
  no exceptions)                                                  : FALSIFIED by CE-13 (a logical
                                                                     non-sequitur in v2's own CSP-c
                                                                     discharge; every term involved
                                                                     is already precisely defined).
  C fully explains CE-10 (compositional/joint reachability)       : FALSIFIED — CE-10 is a
                                                                     quantifier-scope defect in the
                                                                     selector clause itself; audit
                                                                     2's own remedy is selector-layer
                                                                     only and names no new semantic
                                                                     content; fully-authored layer-4
                                                                     semantics does not by
                                                                     construction prevent it.
  A is "category-mismatched"/pure misdiagnosis (§3.1, §5)         : FALSIFIED — CSP-c, a pure
                                                                     selector-layer, no-new-semantics
                                                                     object, permanently excludes
                                                                     CE-1 and CE-2 per the
                                                                     diagnosis's own cited source
                                                                     (audit 2 §1.1-1.2).
  Minimality test ("would correcting C have prevented every
  failure") applied to the full evidence set                      : FAILS on CE-10 and CE-13.

  Dominant-cause reading (C explains 9 of 13 cited items,
  B is its correct downstream manifestation for those 9)          : SURVIVES and is well-supported.
```

**Overall verdict: FAIL.**

The diagnosis's central identification of `C` — an incorrect abstraction boundary that files the
four registers' semantic definitions onto the deferred-value side — is genuinely insightful,
independently reverifiable against the primary T1 text (not merely against the diagnosis's own
quotation of it), and correctly explains the majority of the evidence assembled across both prior
audits: the original degenerate-collapse pattern as re-read, and the nine scope/quantifier/
normalization/granularity/span/discourse/antichain counterexamples (CE-4 through CE-9, CE-12). The
control-group argument (§2 of the diagnosis, contrasting `EVIDENCE_ORDERING_KEY`/`MIN_ORIGINS`
against the four deferred entries) is the strongest part of the document and survives scrutiny.

However, the diagnosis's own stated method for certifying a *minimal, exception-free* root cause —
"every falsified item... without exception... turns on... an undefined semantic," tested by
"would correcting `C` have prevented every failure" — does not survive contact with two items drawn
from its own evidence table. **CE-13** is an invalid inference in v2's own written proof, involving
no undefined term; relocating semantics across any boundary does not touch it. **CE-10** is a
quantifier-scope defect internal to the selector clause (per-register existential vs. joint
reachability), for which the cited source's own recommended fix is a selector-layer change that
introduces no new semantic content — placing it in the diagnosis's own taxonomy under `A`, not `C`.
Because CSP-c (a pure, no-new-semantics selector object) is independently confirmed to have
permanently closed two of the three original counterexamples, the diagnosis's flat characterization
of `A` as "category-mismatched" and "the misdiagnosis" is an overstatement contradicted by its own
cited material.

This audit does not propose a correction, does not redesign the methodology, and chooses no register
value. It recommends, for whoever next revises the diagnosis:

1. Retain the `C` finding as the dominant, well-evidenced explanation for the register-definition
   family of failures (CE-4…CE-9, CE-12, and the reread v1-a/b/c pattern).
2. Withdraw or qualify the exception-free "every falsified item" claim in §1 and the unqualified
   rejection of `A` in §3.1/§5; both are falsified by items already in the diagnosis's own evidence
   table.
3. Separately acknowledge CE-10 and CE-13 as a distinct, secondary defect class — internal to the
   selector construct's scope and rigor, not resolved by relocating semantics — rather than folding
   them into `C` without demonstrating the connection.

*End of independent root-cause audit.*
