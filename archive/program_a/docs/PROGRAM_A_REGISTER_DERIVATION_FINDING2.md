# PROGRAM A — REGISTER DERIVATION FINDING 2

**Title:** Response to the independent Sonnet audit of E-SELECT v1 — replay of the
three degenerate-collapse counterexamples, the underlying methodological defect
they share, and the smallest correction (**E-SELECT v2**) that closes all three.
**Object audited (the thing being corrected):** the concrete Canonical Selection
Principle of `PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` §§4.1–4.2/§7 ("E-SELECT
v1") — **not** the derivation method's constraint/invariant layers, and **not**
ES-1 or PA-3.
**Authorities (as given, read in full):** `PROGRAM_A_REGISTER_DERIVATION_METHOD.md`
("the method"), `PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` ("F1-DERIV" / "v1"),
`docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md` ("the audit").
Read-only grounding: `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` ("T1"),
`PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` ("the addendum"),
`PROGRAM_A_REGISTER_AUDIT.md` ("the register audit").
**Posture.** This is a *methodological* correction. It **derives no register
value**, invents no constant, redesigns no part of ES-1, and modifies no
scientific claim. Per the mission, every confirmed counterexample in the audit is
accepted as valid against v1 and is **not** contested; the response is to repair
the selector so those counterexamples no longer bite. This document does **not**
defend E-SELECT v1 — it discards v1's three broken axes.
**Date:** 2026-07-14
**Status:** DRAFT — methodology only. Binds no value, mints no constant, records
no sign-off, pins no commit. The standing prohibition
(`ES1_IMPLEMENTATION_GATE.md`:97-99) remains in force unchanged.

---

## 0. One-line finding

E-SELECT v1 tried to force uniqueness by **extremizing a one-sided objective
(⊆-minimal "output extension") over a lattice whose extremum in that direction is
the *degenerate* element** — and, for the string register, by invoking an extremum
over a domain carrying no order at all. The audit's three counterexamples are all
instances of that single defect. The smallest correction keeps v1's *abstract*
obligation (a choice function is required — the audit confirmed this and it is not
in dispute), discards v1's three concrete axes, and replaces them with **E-SELECT
v2**: (i) a mandatory third discharged clause **CSP-c (non-degeneracy)**, grounded
in the *already-frozen* ordinality-by-construction invariant; (ii) a re-anchoring
of the selection axis from "minimize the output extension" to "the **exact
structural realization** of the register's frozen role-predicate"; and (iii) a
scope correction fixing `A_r` for `ANSWER_TEMPLATES` to the **frozen skeleton
layer** the addendum already defines, not surface rendering strings. Nothing in
the constraint layer, the invariant layer, ES-1, PA-3, or Findings 1–3 moves.

---

## 1. Task 1 — Replay of every counterexample

The objects here are methodology documents; per the audit's own note there is "no
code to execute and no witness to replay," so replay is the logical
re-construction of each counterexample from the frozen types and stated
constraints — exactly the method the audit used. Each is replayed against
**E-SELECT v1 as written** and, per mission, taken as **valid**.

### CE-1 — `SUPPORT_TEST_PARAMS`: the always-`False` support relation
Define `supports(c, e) = False` for every `(claim, evidence)` pair.
Replay against v1's stated constraints (method §3.2) and v1's axis
(§4.2 "least-permissive-admissible, ⊆-minimal"):

- **Deterministic** — yes (constant function; no randomness, model call,
  wall-clock).
- **Entity-level** — yes, *vacuously*: method §3.2 phrases the clause as a
  **necessary condition** ("support **requires** the claim's entities be
  present"); a relation that never asserts support satisfies every necessary
  condition on support with no witness.
- **Total** — yes, as a *function* (method §3.2 "defined for every
  `(claim, evidence)` pair"); totality bounds nothing about the `True`-set.
- **Firewall-clean / 3-field-expressible / order-stable** — yes (its output never
  varies with anything).
- **⊆-position** — it is the global **infimum** of the ⊆-order on support
  relations; v1's "⊆-minimal" selector, absent any floor, returns it.
- **Consequence** — every query resolves S0 by the §A3 cascade; S1/S2/S3 become
  unreachable. T1 §3.3's "no support anywhere ⇒ S0" is a one-directional
  implication satisfied vacuously.

**Replay verdict: CE-1 valid against v1.** The only textual guard is CF-R6, and
that is **E-DEV / dev-check, falsifying-only** (T1 §10.2(b): "≥2 tiers reachable
… the degenerate-tier guard" is a *dry-run* target, not an a-priori constraint),
so it cannot appear inside a CSP-b uniqueness proof. Accepted.

### CE-2 — `EXTRACTION_PARAMS`: the always-empty extractor
Define `extract(doc) = ()` for every document.
Replay against v1's axis (§4.2 "canonical-minimal-extraction, ⊆-minimal claim
set"):

- **Total** — yes (as a function). **`claim_text`-injective** — yes, *vacuously*
  (no two claims exist to collide, so the §A2 injectivity precondition holds
  trivially). **Deterministic / entity-level / no-model-call** — yes, vacuously.
- **⊆-position** — global infimum of the ⊆-order on claim sets; v1's "⊆-minimal"
  selector returns it.
- **Consequence** — `Σ = ∅` for every query ⇒ ES-1 collapses to S0-only ⇒
  S1/S2/S3 unreachable; the `Comp`/`Part` machinery (Findings 2/3) becomes
  *vacuously* unreachable.

**Replay verdict: CE-2 valid against v1.** Identical defect class to CE-1.
Accepted.

### CE-3 — `ANSWER_TEMPLATES`: multiplicity of realization functions
Take two S0 realization functions — `f₀` producing "I don't have enough
information to answer this." and `f₀′` producing "The available evidence does not
establish an answer to this question." Replay against v1's axis (§4.2 "canonical
generator … selection by construction"):

- Both are **total** over `{S0,S1,S2,S3}`, **single-valued**, **assert no fact**,
  **bind only permitted `EvidenceStateResult` fields**, and honor **CR-3 / §A7
  I-2**.
- v1's axis asks only that the realization function be "total and single-valued"
  and that its *output* honor I-2/CR-3 — properties **every** well-defined
  function has once one has already been picked. It names **no criterion** that
  separates `f₀` from `f₀′`.

**Replay verdict: CE-3 valid against v1.** v1 relocates the multiplicity from
"which string" to "which function" and closes nothing. Accepted.

### The fourth register — no counterexample
`CONTRADICTION_MATERIALITY_PARAMS` is the one register for which the audit could
construct **no** degenerate collapse, because v1 (only here) stated an explicit
lower bound — "closed under intersection **down to the non-triviality floor** (a
genuine incompatibility must remain material)" (v1 §4.2, row d). This asymmetry —
a floor for one register and none for its two structural analogues — is itself the
fingerprint of the defect (§3). No counterexample to replay; carried forward as
the register that already satisfies the corrected clause.

---

## 2. Task 2 — Why E-SELECT v1 fails

v1's necessity survives (the audit confirmed it; §3.1 of the audit: *some* explicit
choice-function obligation is logically required, and no simpler correction was
found). **v1's sufficiency fails**, and it fails the same way three times:

1. **Support and Extraction (CE-1, CE-2): extremization toward a degenerate
   infimum.** Every constraint the method states on these two registers is a
   **prohibition** — a one-sided *upper* bound (support must **not** admit
   fabrications or topical-only matches; extraction must **not** call a model,
   must **not** emit colliding `claim_text`). The ⊆-least element "does nothing,"
   so it satisfies every prohibition vacuously and sits at the lattice bottom. v1
   then *minimizes toward that bottom*. An axis that rewards "certify/extract the
   fewest pairs" is optimized by the empty relation. v1's CSP-b demanded only
   **existence + uniqueness** of the extremum; the extremum both exists and is
   unique — it is simply **degenerate**, a property CSP-b never tested.

2. **Templates (CE-3): an extremum over a non-order.** v1 conceded strings "carry
   no natural a-priori order" and substituted "selection by construction" for an
   axis. But a "generator" is not a selector: "apply one fixed realization
   function" presupposes the fixed function already chosen. v1's CSP-b for this
   row proves *totality and single-valuedness of a given function*, which is
   silent on *which* function — the exact multiplicity v1 §1 defines as the
   disease. The string register is the limiting case of defect (1): where the
   parametric registers had an order oriented the wrong way, the template register
   had **no orientation at all**.

**Common failure statement.** v1 supplied an *optimization* (CSP-a) and a
*well-posedness check on the optimum* (CSP-b existence+uniqueness), but never a
guarantee that the optimum is the element the register **exists to be**. Where the
objective points at vacuity (support, extraction) or is absent (templates), the
optimum is the wrong element or is undefined.

---

## 3. Task 3 — The underlying methodological defect

The three failures reduce to **one root cause**, stated three ways from most
concrete to most general:

> **DEFECT (concrete).** v1 minimized the register's **output extension** (the set
> of supported pairs / extracted claims / — for templates — took the string
> domain, which has no extension order). The infimum of an output-extension order
> is always the **vacuous** element, because the method's constraints bound only
> the false-positive direction. Minimizing extension therefore drives true
> positives to zero alongside false positives, optimizing a one-sided objective
> whose optimum is emptiness.

> **DEFECT (structural).** A sound canonical axis must be **two-sided**: pinned
> *below* by the structural mandate the register exists to honor (the states its
> role gates must remain reachable) and *above* by the prohibitions. v1 supplied
> only the upper (prohibition) side and an unbounded-below extremal direction. It
> is the exact analogue of selecting `MIN_INDEPENDENT_ORIGINS_FOR_S3` by
> "minimize the count" while **dropping the floor "that is corroboration at
> all"** — which would return `0`, not `2`. `MIN_ORIGINS` is legitimate precisely
> because it minimizes *above a structural floor*; v1 kept the minimization and
> lost the floor for two of the three parametric registers, and never had an order
> for the fourth.

> **DEFECT (in v1's own terms).** v1's CSP-b required a *discharged
> existence-and-uniqueness lemma* but **not a discharged non-degeneracy lemma**.
> Existence + uniqueness are satisfied by the degenerate infimum (CE-1/CE-2); they
> are vacuously satisfiable by any single realization function (CE-3). The missing
> obligation is exactly **non-degeneracy**: the selected element must realize the
> register's role *non-vacuously*.

### 3.1 Why v1 supplied the floor for materiality and nowhere else
The materiality row (§1, register d) reads "a genuine incompatibility must remain
material" — a **lower** bound. v1's author reached for it there because collapsing
`is_material` to always-`False` visibly removes S1, so the vacuity was salient. The
same vacuity for support/extraction is *hidden behind vacuous satisfaction of
necessary-condition clauses* (CE-1/CE-2 above), so v1 did not notice it and stated
no floor. The asymmetry is not a design decision; it is the defect showing through
in the one place it was obvious.

### 3.2 Why the audit's own recommended fix is larger than necessary — and risks
### deriving the value
The audit (rec 2) suggests amending support/extraction with a floor of the form
"classify **at least the evidence set demonstrating the E-STRUCT-cited design
commitment** as supporting/extracted." That phrasing lower-bounds `A_r` by
**naming a concrete set of pairs/claims** — which is perilously close to
*transcribing a value into the methodology*, the very act §0.2 of the method and
v1 §4.1(iii) prohibit ("a disguised selection principle smuggled into the
constraint layer"). The correct floor must be a **structural property**, not an
enumerated set — the same species of object as `MIN_ORIGINS`'s "is corroboration
at all." That is what makes the fix below *smaller* than the audit's own
recommendation: it lower-bounds `A_r` by a **reachability predicate already
entailed by a frozen invariant**, naming no pair, no claim, and no string.

---

## 4. Task 4 — The smallest correction: **E-SELECT v2**

The correction touches only the *selection* layer (v1 §§4.1–4.2/§7 / the method's
§2.6 slot). It adds one clause, re-anchors one axis, and corrects one scope. It
adds **no** constant, **no** state, **no** rule text, and **no** digest input.

### 4.1 The three changes (stated once, generally)

**Change A — add CSP-c (non-degeneracy), mandatory and discharged.**
Every register whose role gates an ES-1 state MUST carry a discharged lemma that
the selected element keeps that state **genuinely reachable** — i.e., there exists
admissible input under which the state fires. Ground: **ordinality-by-construction**
(T1 §3.3 line 263; §4), whose per-tier semantic argument *presupposes* S1/S2/S3
are reachable — an all-S0 mechanism makes the per-tier claims of T1 §4 vacuous.
CSP-c **promotes the existing CF-R6 degenerate-tier guard** (T1 §10.2(b)) from an
E-DEV/dev-check falsifier to an **a-priori selection clause**. It is placed in the
*selector*, not the constraint layer, so `A_r`'s definition and every §2.3/§2.4
invariant are left exactly as written (see §5). CSP-c is E-STRUCT-only (it cites
only ES-1 state structure and the frozen tier order), hence firewall-clean by
construction.

**Change B — re-anchor CSP-a from "minimize extension" to "exact structural
realization."** For a register whose role-predicate is fixed a-priori, the
canonical element is the **fixed point** "the rule *equals* the extension /
normal-form entailed by that frozen predicate" — a **two-sided** characterization
(it may neither under- nor over-realize the predicate), not a one-sided infimum.
Where a residual ordered family survives, it is closed by **minimality of the
rule's operationalization** (its descriptive latitude), **never** by minimality of
its output extension. This is the generalization of `MIN_ORIGINS` ("smallest
*operationalization* — the count — above the corroboration floor"), applied
correctly.

**Change C — scope correction for `A_r` of `ANSWER_TEMPLATES`.** `A_r` ranges over
the **frozen template skeletons** — the mechanism-defining layer — **not** surface
rendering strings. The addendum already fixes this boundary: "**Not
mechanism-defining** … answer *rendering* niceties above the frozen
`ANSWER_TEMPLATES`" (§A6-DIGEST, lines 413–414). Two strings that differ only in
surface wording realize the **same** skeleton and are therefore the **same element
of `A_r`**, not two.

### 4.2 The corrected per-register axes, and elimination of each counterexample

| Register | Corrected CSP-a axis (E-STRUCT, a-priori — names a principle, not a value) | CSP-c (non-degeneracy) | Counterexample eliminated |
|---|---|---|---|
| **`SUPPORT_TEST_PARAMS`** | Canonical = the support relation **equal to the extension of the frozen entity-presence predicate** (`supports(c,e) ⟺` the claim's entities are present in `e` under the 3-field schema), i.e. the fixed point that neither under- nor over-realizes entity-presence; residual operationalization freedom closed by minimal operationalization latitude subject to CSP-c. | The selected relation must fire support on ≥1 admissible input so S2/S3 stay reachable. | **CE-1 eliminated.** always-`False` fails the biconditional (it false-negatives every entity-present pair, so it is *not equal* to the entity-presence extension) **and** fails CSP-c (S2/S3 unreachable). |
| **`EXTRACTION_PARAMS`** | Canonical = the extractor **equal to the extension of the frozen entity-level candidate-boundary predicate**, residual freedom closed by minimal operationalization latitude subject to totality, the §A2 `claim_text`-injectivity precondition, and CSP-c. | The selected extractor must emit ≥1 claim on ≥1 admissible input so `Σ ≠ ∅` and S1/S2/S3 stay reachable. | **CE-2 eliminated.** always-empty fails the biconditional (extracts nothing the boundary predicate marks) **and** fails CSP-c (`Σ=∅` ⇒ S0-only). |
| **`CONTRADICTION_MATERIALITY_PARAMS`** | Unchanged in substance. v2 **reclassifies** v1's existing floor ("a genuine incompatibility must remain material") as an *instance* of the now-mandatory CSP-c, closing the §3.1 asymmetry. | Already present as v1's floor; keeps S1 reachable. | No counterexample existed; now covered by the *general* clause rather than an ad-hoc one. |
| **`ANSWER_TEMPLATES`** | `A_r` = **frozen skeletons** (Change C). Canonical = the **minimal faithful skeleton** per state: the unique skeleton realizing exactly the frozen answer-construction rule (T1 §3.1) with **exactly** the permitted `EvidenceStateResult` fields the rule requires and the state's **assertion-force marker** (assert / hedge / represent-both / assert-nothing — §A7 I-2), and nothing above the frozen layer; slot **order pinned by the already-frozen `EVIDENCE_ORDERING_KEY` / §A2**, leaving no residual ordering freedom. | Total over `{S0,S1,S2,S3}`; each state's skeleton realizable ⇒ every state renders. | **CE-3 eliminated.** `f₀` and `f₀′` differ only in surface rendering ⇒ same skeleton ⇒ **one** element of `A_r`. The minimal-faithful skeleton is a unique fixed point per state; the multiplicity is dissolved, not relocated. |

### 4.3 What v2 discharges vs. what it still leaves owed
Per the mission's own wording — "**eliminate** the degenerate support selector,
**eliminate** the degenerate extraction selector, **uniquely define**
`ANSWER_TEMPLATES` selection":

- For **support** and **extraction**, v2 **eliminates the degeneracy** (CSP-c +
  the two-sided exact-extension axis provably exclude the infimum) and **makes
  uniqueness reachable** (the axis is now over a two-sided, non-degenerate,
  ordered family). The final CSP-b uniqueness lemma — proving the *minimal
  operationalization* of entity-presence / the candidate-boundary predicate is
  itself unique — remains the register-specific lemma the authorized actor
  authors and the ScientificAuditor certifies (method §7), exactly as the method
  intends. v2 does not, and must not, discharge it here (that would derive the
  value).
- For **templates**, v2 **uniquely defines** the selection: the minimal-faithful
  skeleton with fields fixed by the rule, force fixed by §A7 I-2, and order fixed
  by §A2 is a unique fixed point. The surface string sits *above* the frozen layer
  and is chosen by rendering, out of scope — so uniqueness of the *frozen object*
  is achieved without naming any string.

This division is deliberate and honors "derive no value": v2 fixes the **selector's
form** so the degenerate elements are provably gone and uniqueness is either
achieved (templates) or well-posed and reachable (support, extraction); the
value-level lemma and the value itself remain with §7/§8.

---

## 5. Preservation proof — the correction disturbs nothing frozen

v2 is still a *choice function over admissible values*, now correctly floored and
scoped. Every element of `A_r` already satisfies every ES-1/PA-3 invariant (that
is what "admissible" means), so the selected element inherits them a fortiori. Item
by item, with the two items the audit flagged "at risk" for v1 shown **improved**:

- **Preserves every §2.3/§2.4 invariant.** CSP-c is placed in the *selector*, not
  the constraint layer: it does **not** redefine `A_r` and does **not** edit
  `§2.4`'s ordinality-by-construction clause (which, as stated, is a material
  conditional the vacuous element satisfies vacuously — CE-1). v2 leaves that
  invariant's *text* untouched and merely refuses to *select* a value that renders
  its per-tier argument vacuous. No state, tier, precedence, or numeric constant
  is added.
- **Preserves ES-1 (improves the audit's "at risk").** The audit rated ES-1
  compatibility "at risk" for v1 because v1's axes could select an all-S0 support
  test / extractor, defeating ordinality-by-construction's reachability
  presupposition. **CSP-c removes exactly that risk**: reachability of S1/S2/S3 is
  now an a-priori selection requirement. ES-1's mechanism (T1 §3–§9) is consumed
  as fixed; nothing is redesigned.
- **Preserves PA-3 (improves the audit's "at risk").** The audit noted the
  always-empty extractor made `Comp`/`Part` (Findings 2/3) *vacuously* unreachable.
  CSP-c forbids selecting it, so the `Comp`/`Part` machinery stays non-vacuously
  reachable. The corrected axes range over the same §A1–§A7 objects and select
  values that already satisfy §A4 (S1 composition), §A5 (`is_material`
  precondition, two-claim signature), §A6 (`contradicts` retained/distinct), and
  §A2 (tie-break keys). No rule text moves.
- **Preserves Finding 1 (addendum §A0).** F1 edits the S2/S3 *state definitions*
  ("no material contradiction **across independent sources**"). v2 touches none of
  those objects; they are outside `A_r` and outside the digest set. Digest-neutral
  to F1, exactly as §A6-DIGEST classifies it.
- **Preserves Finding 2 (addendum §A4 / §A7 I-3).** F2's `Comp`/`Part` **totality**
  theorem holds for *all* admissible values (it depends only on `Σ`, the §A1/§A2
  order, and `EVIDENCE_ORDERING_KEY`). v2 selects an admissible value, so
  `Part ≠ ∅` whenever S1 fires and `contradiction_doc_ids` stays total — and, under
  CSP-c, this now holds **non-vacuously** (S1 is reachable), strengthening rather
  than disturbing F2.
- **Preserves Finding 3 (addendum §A4 `Comp` cond-3 / §A7 I-3 biconditional).**
  F3's cross-origin `Comp` refinement is a definition on the anchoring set,
  upstream-independent of which admissible support/materiality/extraction value is
  selected. The `Comp ⊆ Part` structure and the `Comp ≠ ∅ ⟺ selected_claim
  participates` biconditional (§A7 I-3) are untouched.
- **Preserves digest / firewall / identity.** v2 introduces **no new register
  entry, no new numeric constant, and no new digest input** — it is a rule about
  *how* the existing four entries are chosen. `frozen_constants_digest()`'s input
  list is unchanged; `PA3_RULESET_VERSION` does **not** advance (no edit to rule
  text (i)–(v); §A6-DIGEST); CR-8/L8 holds because CSP-a and CSP-c are E-STRUCT-only.
  Supplying the eventual value remains a §8 **transcription**, not a rule edit.

---

## 6. Minimality — v2 is smaller than the audit's own recommendation

- **It adds one clause, not a family of floors.** CSP-c is a *single* general
  obligation grounded in *one existing invariant* (ordinality-by-construction),
  discharged per register by pointing at the state the register's role gates. The
  audit proposed *per-register enumerated floors* (rec 2) — strictly more
  material, and, as §3.2 shows, at risk of transcribing a value. v2's floor names
  **no** pair, claim, or string.
- **It reuses, not invents.** CSP-c is the CF-R6 guard (already in T1 §10.2(b))
  moved from E-DEV to a-priori — no new guard is created. The templates fix is the
  §A6-DIGEST frozen/rendering boundary already in the addendum — no new layer is
  created.
- **It is the smallest object that closes all three counterexamples.** Any smaller
  correction omits one of the three changes and reopens a counterexample: drop
  CSP-c → CE-1/CE-2 return; drop Change B → uniqueness for support/extraction is
  well-posed only up to the degenerate element; drop Change C → CE-3 returns. The
  three changes are jointly necessary and individually minimal.
- **The only alternative is larger.** Tightening the constraint/invariant layer
  until the filter alone excludes the degenerate elements would **edit ES-1/PA-3
  structure** (e.g. strengthen §2.4's conditional to a non-vacuous form) — a
  larger change the mission forbids ("preserve every existing invariant"; "do not
  redesign ES-1"). Placing non-degeneracy in the *selector* is the minimal
  placement that leaves the invariant layer verbatim.

---

## 7. Boundary statement (mission constraints)

- **Derives no register value.** v2 names *selection principles* and the *lemmas
  they owe*; it computes, guesses, and transcribes **no** support relation,
  materiality boundary, extracted claim, or template string. `A_r` is left to be
  collapsed by the authorized actor under the unchanged §7 (B2) / §8 (freeze)
  pipeline. (§3.2 explicitly rejects the audit's value-naming floor to stay inside
  this boundary.)
- **Does not redesign ES-1.** No state, predicate, precedence, tier map, seam
  invariant, or type is added or altered. CSP-c *cites* ordinality-by-construction
  as its ground; it does not modify it. The mechanism of T1 §3–§9 and addendum §A
  is consumed as fixed.
- **Modifies no scientific claim.** The per-tier semantic argument (T1 §4),
  hypothesis H1, the corroboration semantics, and every firewall claim are
  unchanged. CSP-c enforces the *non-vacuous reading* T1 §4 already presupposes; it
  asserts no new empirical fact.
- **Preserves ES-1, PA-3, and Findings 1, 2, 3** — proven item-by-item in §5, with
  ES-1 and PA-3 compatibility *upgraded* from the audit's "at risk (v1)" to
  "preserved (v2)."

---

## 8. The correction, stated once

> **Replace E-SELECT v1's CSP (F1-DERIV §§4.1–4.2/§7) with E-SELECT v2.** v2 keeps
> the abstract obligation that every non-singleton register carry an a-priori,
> E-STRUCT-only choice function with a discharged uniqueness lemma, and makes three
> minimal changes:
> **(A) CSP-c (non-degeneracy), mandatory and discharged** — the selected element
> must keep every ES-1 state its role gates *genuinely* reachable; grounded in
> ordinality-by-construction (T1 §3.3/§4) and promoting the CF-R6 degenerate-tier
> guard (T1 §10.2(b)) from E-DEV to an a-priori selection clause, placed in the
> selector so no invariant text or `A_r` definition changes.
> **(B) Re-anchor CSP-a** from "⊆-minimal output extension" (one-sided, degenerate)
> to "the element **equal to the extension / normal-form of the register's frozen
> role-predicate**" (two-sided fixed point), with any residual freedom closed by
> minimal *operationalization* latitude — never minimal extension.
> **(C) Scope `A_r` for `ANSWER_TEMPLATES` to frozen skeletons**, not surface
> strings (§A6-DIGEST "rendering niceties … Not mechanism-defining"); the canonical
> element is the minimal-faithful skeleton per state, fields fixed by the T1 §3.1
> rule, force fixed by §A7 I-2, order fixed by §A2.
>
> This eliminates the always-`False` support selector and the always-empty
> extraction selector (CSP-c + Change B), uniquely defines `ANSWER_TEMPLATES`
> selection (Change C), adds no constant, moves no ES-1/PA-3/Finding-1/2/3 object,
> and leaves value authorship to the unchanged §7 (B2) and §8 (freeze) steps.

---

## 9. References (read-only grounding)

- `PROGRAM_A_REGISTER_DERIVATION_FINDING1.md` — v1 §§4.1–4.2 (the four axes, CSP-a/
  CSP-b), §7 (restated axes), §5 (preservation frame reused here).
- `docs/audits/REGISTER_DERIVATION_FINDING1_SONNET_AUDIT.md` — §3.2(a)–(d)
  (CE-1/CE-2/CE-3 and the materiality non-counterexample), §4 (falsification
  table), §5 (verdict + recommendations 2–4 answered in §§3.2/4/6 here).
- `PROGRAM_A_REGISTER_DERIVATION_METHOD.md` — §2.2 (evidence classes; E-DEV
  falsifying-only), §2.3/§2.4 (universal constraints/invariants preserved), §3.2/
  §5.2 (support/extraction constraints), §6.1–§6.3 (templates), §7/§8 (auditor/
  freeze pipeline left unchanged).
- `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` — §3.1 (state/answer-rule table),
  §3.3/§4 line 263 (ordinality-by-construction — CSP-c ground), §5.1
  (`MIN_ORIGINS` "smallest count … corroboration at all" — the correct floored
  extremal exemplar), §10.2(b) (CF-R6 degenerate-tier guard — promoted by CSP-c).
- `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` — §A2 (ordering/tie-break — pins template
  slot order), §A4/§A5 (S1 composition, `is_material`), §A6-DIGEST lines 413–414
  ("rendering niceties … Not mechanism-defining" — Change C ground) and the
  mechanism-defining rule set (i)–(v), §A7 I-2/I-3 (assertion gate / anchoring —
  template force + Findings 2/3).
- `PROGRAM_A_REGISTER_AUDIT.md` — Entries 5.1 (`MIN_ORIGINS` exemplar), 5.3/5.4/
  5.6/5.7 (the four FAIL-deferred blockers).

---

*End of Register Derivation Finding 2. Replays the three degenerate-collapse
counterexamples (accepted as valid against E-SELECT v1), identifies their single
root defect — one-sided extremization toward a degenerate infimum, with CSP-b
lacking a non-degeneracy clause and `A_r` mis-scoped for the string register — and
returns the smallest correction, E-SELECT v2 (CSP-c + two-sided re-anchoring +
skeleton scoping). No register value is derived; ES-1, PA-3, and Findings 1–3 are
preserved.*
