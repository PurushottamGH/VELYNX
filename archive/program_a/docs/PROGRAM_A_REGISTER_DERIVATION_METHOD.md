# PROGRAM A — REGISTER DERIVATION METHOD (ES-1)

**Title:** Derivation Methodology for the Four Deferred ES-1 Free-Constant
Registers — how a canonical value is *produced*, not what it is.
**Authority:** Chief Scientific Specification Author. This document is a
methodology rider to `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` (the T1/G4
freeze object) and its co-frozen `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md`. It
supplies the one thing those authorities deliberately left open for four of
the register entries: the **procedure by which a deferred value becomes
canonical** at G4.
**Date:** 2026-07-14
**Status:** DRAFT — methodology only. Binds no value, mints no constant,
records no sign-off, pins no commit. The standing prohibition
(`ES1_IMPLEMENTATION_GATE.md`:97-99) remains in force unchanged: no
emission-surface or binding code, no frozen-row output.

---

## 0. Purpose, non-goals, and binding firewall

### 0.1 Purpose
The T1 register (`PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` §5) fixes the
**role, a-priori justification form, and structural type** of every free
constant the ES-1 mechanism needs. For four of those entries —
`SUPPORT_TEST_PARAMS` (§5.3), `CONTRADICTION_MATERIALITY_PARAMS` (§5.4),
`EXTRACTION_PARAMS` (§5.6), and `ANSWER_TEMPLATES` (§5.7) — the register
records only the structural form and marks the concrete value **"fixed at G4
from this register."** `PROGRAM_A_REGISTER_AUDIT.md` confirms these four stand
today as placeholder `{}` entries in `_FREEZE_PENDING_ENTRIES`, each a
**FAIL (deferred)** blocker to an admissible G4 freeze.

What the authorities specify is the *destination* (a frozen, admissible
value). What they do not specify is the *road*: the repeatable, auditable
procedure that turns "fixed at G4 from this register" into a specific
canonical value that the ScientificAuditor can certify and the ReleaseManager
can pin. **This document defines only that road.** It is the missing
derivation methodology and nothing more.

### 0.2 Non-goals (hard boundaries on this document)
This document does **not**, and no reader may treat it as if it does:

- **Choose any value.** No value for any of the four registers appears here.
  Where a value would otherwise be named, this document names the *procedure*
  that would produce it and stops.
- **Invent any constant.** No new free constant, threshold, weight, boundary,
  template string, or numeric default is introduced. The register of §5
  remains the sole inventory (T1 §5; addendum §A6-DIGEST); this document adds
  no entry to it.
- **Implement code.** No implementation of the support test, materiality rule,
  extractor, templates, `frozen_constants_digest()`, or any test is written or
  prototyped. The standing prohibition (`ES1_IMPLEMENTATION_GATE.md`:97-99)
  and the pre-GO code ban (T1 §2) are unchanged and re-affirmed.
- **Perform governance.** No sign-off is given or fabricated; no commit is
  pinned; no gate box is checked; no B2/B3 record is completed. This document
  describes the ScientificAuditor's and ReleaseManager's *methods*; it does
  not act in either role. Their sign-off blocks live in T1 §12 and addendum
  §D and remain blank.
- **Redesign ES-1.** No state, predicate, precedence rule, tier mapping, or
  seam invariant is altered. The mechanism of T1 §3–§9 and addendum §A is
  consumed as fixed context, never re-derived.

### 0.3 Binding firewall (CR-8/L8) — restated for methodology
Every procedure specified here conforms to the CR-8/L8 firewall **by
construction**. No derivation step may read, import, mirror, or be fitted to
any evaluation-side object: no EXP-1 tier→probability mapping
(`experiments/EXP1/calibration.py:TIER_TO_CONFIDENCE`), no EXP-1 bin boundary
(`BIN_BOUNDARIES`), no ECE pass/kill logic or threshold
(`experiments/EXP1/decision.py`), and no EXP-1 outcome, frozen row, or
adjudicator signal (T1 §2). A derivation method that consulted any of these
would produce an inadmissible value **regardless of the value produced**;
firewall conformance is a property of the *procedure*, and this document
makes it one.

---

## 1. Scope: the four deferred registers and why their values are deferred

| Register | T1 role (consumed, not re-derived) | Consumed by | Audit status today |
|---|---|---|---|
| `SUPPORT_TEST_PARAMS` | Parameters of the deterministic, entity-level claim-support test that decides "supports"/"does-not-support" a claim (T1 §5.3). | PA-3 `supports`; drives S0 vs {S1/S2/S3}; dominates CF-R2. | FAIL (deferred) — BLOCKER (load-bearing). |
| `CONTRADICTION_MATERIALITY_PARAMS` | Parameters of the materiality rule separating a material contradiction (S1) from trivial/stylistic variation (T1 §5.4; addendum §A5). | PA-3 `is_material`; gates S1 firing. | FAIL (deferred) — BLOCKER. |
| `EXTRACTION_PARAMS` | Parameters of PA-2's deterministic, entity-level candidate-claim extraction — pure text mechanics, no model calls (T1 §5.6). | PA-2; feeds every downstream PA-3 quantity (`ios`, `≺`, S1). | FAIL (deferred) — HIGH. |
| `ANSWER_TEMPLATES` | The frozen per-state answer-text template, one per `{S0,S1,S2,S3}` (T1 §5.7; addendum §A7 I-2). | PA-4; the rubric-facing wording coupled to each tier. | FAIL (deferred) — MEDIUM. |

**Why these four are deferred and the other five register entries are not.**
`MIN_INDEPENDENT_ORIGINS_FOR_S3` (§5.1), `INDEPENDENCE_RELATION` (§5.2),
`EVIDENCE_ORDERING_KEY` (§5.5), `SPEC_VERSION` (§5.8), and
`PA3_RULESET_VERSION` (addendum §5.9) each carry a value (or a
value-generating rule) whose canonical form is *already determined by a
structural-necessity argument or an identity convention* in the authorities,
and each is audited PASS. The four in scope share a different property: their
role is fixed but their *concrete internal parameterization* admits more than
one structurally-defensible instantiation, so the authorities correctly
refused to invent one and deferred it to G4. Deferral is therefore not an
omission to be patched by guessing a default — it is an explicit instruction
that a **derivation procedure** must run first. This document is that
procedure's specification.

**Placeholder posture is load-bearing.** The `{}` placeholders and the
`frozen_constants_digest()`-raises-on-pending behavior
(`PROGRAM_A_REGISTER_AUDIT.md` Entry 5.3) are a *feature*: they make an
admissible freeze mechanically impossible while any of the four is underived.
No step in this methodology weakens that; the methodology is the sanctioned
way to *retire* a placeholder, and it retires one only by producing a value
that satisfies §3–§6 below and passes §7.

---

## 2. Common derivation frame (applies to all four registers)

Each register is derived by the same six-part procedure. Sections §3–§6
specialize this frame per register; this section fixes what is common so the
per-register sections state only what differs.

### 2.1 The six questions every derivation must answer
For each register the derivation record MUST answer, in order:

1. **Evidence** — what admissible evidence *determines* the value.
2. **Constraints** — what the value must satisfy to be well-formed.
3. **Invariants** — what mechanism properties the value must preserve.
4. **Auditor verification** — how the ScientificAuditor tests (1)–(3).
5. **ReleaseManager freeze** — how the certified value becomes canonical.
6. **Re-derivation** — what conditions void the value and re-open (1).

### 2.2 Admissible evidence classes (the only inputs a derivation may cite)
A derivation is a *justification-first* activity: the value is chosen because
an a-priori argument licenses it, never because an outcome rewarded it. The
**only** evidence classes a derivation may cite are:

- **(E-STRUCT) Structural-necessity argument.** A derivation of the value from
  the definitional structure of the ES-1 states, the corroboration semantics,
  or the frozen types (`program_a/types.py`) — the same class of argument that
  licenses `MIN_INDEPENDENT_ORIGINS_FOR_S3 = 2` as "the smallest count that is
  corroboration at all" (T1 §5.1). This is the strongest class; prefer it.
- **(E-DETERM) Determinism/replay requirement.** A derivation forced by the L6
  determinism and byte-identical-replay requirement (T1 §7.2; addendum §A2):
  the value must be whatever makes identical `(query_text, snapshot)` yield
  identical output across the 22 seeds.
- **(E-TYPE) Frozen-type/contract compatibility.** A derivation forced by the
  frozen leaf types and seam contracts (addendum §A0–§A7): the value must be
  expressible over `{origin_domain, title, text}` documents and
  `CandidateClaim`/`EvidenceStateResult` fields, and must feed the PA-3 rules
  those contracts assume.
- **(E-PRIOR) Named a-priori design commitment.** A design choice fixed in the
  authorities and named as a-priori (e.g. "entity-level, not topic-level"
  matching; "no model calls"; "asserts no fact for S0/S1") — the value must be
  the instantiation that honors that commitment.
- **(E-DEV) Pre-freeze synthetic mechanics evidence, mechanics-only.** Results
  of the T10 dry run / PA-6 conformance corpora **within the B-11 scope
  limits** (T1 §10.2): they may show that a *candidate* parameterization has
  the right mechanical shape (e.g. a fabricated-entity probe yields no claim),
  and may **falsify** a candidate. They may **never** *select among
  admissible candidates by an observed score*, and never touch a frozen row.
  E-DEV is corroborating/falsifying evidence for an E-STRUCT/E-TYPE argument,
  never a substitute for one.

**Inadmissible evidence (any of these voids the derivation):** any EXP-1
outcome, frozen-row output, adjudicator signal, calibration/ECE result, bin
boundary, or tier probability; any in-place tuning loop over observed output;
any wall-clock, network, env-var, or mutable-store read (T1 §8.3); any value
back-solved to hit a target metric (Goodhart). The distinction that makes
E-DEV lawful and tuning unlawful is fixed by B-11 (T1 §10.2): mechanics
verification and candidate falsification are lawful; *value selection by
observed performance* is not.

### 2.3 The two universal constraints (bind every register)
Beyond per-register constraints (§3–§6), every derived value MUST satisfy:

- **(C-APRIORI) A-priori-only.** The value is entailed by a stated
  E-STRUCT/E-DETERM/E-TYPE/E-PRIOR argument written *before* the value is
  fixed and *without* reference to any inadmissible evidence. The written
  argument is part of the derivation record and is what the auditor certifies
  (audit criterion 6).
- **(C-FIREWALL) Firewall-clean.** No component of the value equals or is
  fitted to any EXP-1 probability, bin boundary, or ECE threshold, and nothing
  in the derivation imports `experiments.EXP1.calibration` (T1 §5 "Forbidden
  in constants.py"; audit criteria 2–4).

### 2.4 The universal invariant set (every register must preserve)
No derived value may disturb any of:

- **Ordinality-by-construction** (T1 §4): more/stronger corroboration ⇒ higher
  tier, with no numeric constant drawn from the evaluation side.
- **Determinism & byte-identical replay** across the 22 seeds (T1 §7.2;
  addendum §A2/§F.4).
- **Exactly-one-state-fires**, exhaustiveness, and mutual exclusion of
  S0–S3 under precedence `S0 → S1 → (S2|S3)` (T1 §3.3; addendum §A3/§F.2).
- **CR-9 answer–tier coupling** and the **FM-1 tier gate** ("`CERTAIN` only
  with `state == S3`"; assertion only in `{S2,S3}`) (T1 §3.2; addendum §A7
  I-2).
- **CR-3 input restriction** (surface reads only `query.query` [+ `query_id`
  echo]; rubric/family/metadata invisible) (T1 §8).
- **Digest integrity**: the value is a serialized input to
  `frozen_constants_digest()` (T1 §6.1; addendum §A6-DIGEST), so once frozen it
  is under the drift tripwire and the `mechanism_id()` identity binding.

### 2.5 What "canonical" means here
A value is **canonical** when, and only when, all four hold:

1. it satisfies its per-register constraints (§3–§6, part 2) and the universal
   constraints (§2.3);
2. it preserves the invariants (§2.4 and per-register part 3);
3. the ScientificAuditor has certified (1)–(2) by the method of §7 and
   recorded a genuine B2 sign-off; and
4. the ReleaseManager has transcribed it and pinned it into the frozen digest
   by the method of §8 (E4–E7 of `PROGRAM_A_G4_EXECUTION_PLAN.md`).

Absent any one, the value is a *candidate*, not canonical, and the placeholder
stands. This document produces neither (3) nor (4); it specifies the method
by which the ScientificAuditor and ReleaseManager produce them.

---

## 3. `SUPPORT_TEST_PARAMS` — derivation method

*Role (consumed from T1 §5.3): parameters of the deterministic, entity-level
claim-support test. Load-bearing; dominates CF-R2.*

**3.1 Evidence that determines the value.**
Primary: **E-STRUCT + E-PRIOR** — the value is entailed by the frozen design
commitment that support is *entity-level, not topic-level, and deterministic*
(T1 §5.3), so that (a) topically-related-but-non-supporting evidence yields
**no** claim (the S0-defining behavior, T1 §3.1 S0 row) and (b) a fabricated
claim gains no support unless the fabricated entity is literally present
(CF-R2 first line). **E-TYPE**: the parameters must be computable over the
3-field `{origin_domain, title, text}` document schema alone (T1 §7.1) and
produce the `supports(claim, evidence)` boolean the PA-3 rules consume
(addendum §A1/§A4). **E-DEV (falsifying only)**: T10 fabricated-entity probes
may *refute* a candidate parameterization that admits a fabricated claim, and
degenerate-tier probes may refute one that makes a tier unreachable (CF-R6);
neither may *select* the value by an observed score (T1 §10.2).

**3.2 Constraints the value must satisfy.**
Determinism (no randomness, no model call, no wall-clock); entity-level
matching (support requires the claim's entities be present in the evidence
text, not mere topical proximity); totality (defined for every
`(claim, evidence)` pair, including empty/junk/near-miss inputs from the
never-fail retriever); firewall-clean (C-FIREWALL); expressible over the
3-field schema only; and stability under `EVIDENCE_ORDERING_KEY`
(the same evidence set in the frozen order yields the same support set).

**3.3 Invariants it must preserve.**
All of §2.4, with these load-bearing specializations: the **S0 boundary**
(no support anywhere ⇒ S0) must remain exactly where the state table places
it; `ios(c)` (independent-origin support count) must remain well-defined for
§A1 selection and the §A3 S2/S3 split; and the **FM-1 guard** must not be
weakened — a value that lets the support test false-positive on a fabricated
claim is inadmissible because it converts CF-R2 from residual risk into
design permission (T1 §3.2).

**3.4 How ScientificAuditor verifies it.**
By the §7 method against the 8-criterion grid, with emphasis (given
load-bearing status) on criterion 8 and on an explicit written E-STRUCT/E-PRIOR
argument that licenses *these* parameters and excludes topic-level or
probabilistic variants. The auditor confirms the CF-R2 argument is present and
that any cited T10 evidence is falsifying/mechanics-only, never selecting.

**3.5 How ReleaseManager freezes it.**
By the §8 method: transcribe the ScientificAuditor-supplied value text
verbatim into `program_a/constants.py` (E4), retire it from
`_FREEZE_PENDING_ENTRIES`, and include it in the single E6 digest computation
so it falls under the `CONSTANTS_HASH` tripwire and `mechanism_id()` binding.

**3.6 Conditions that would require re-derivation.**
Any change to the support-test *contract* (entity-level ⇄ other; determinism
relaxed); any change to the 3-field document schema it reads; any change to
the S0 definition or the `supports` signature; or discovery (post-freeze, via
the §9 triggers) that the frozen parameters admit a CF-R2 false-positive.
Re-derivation is a full Wave-2 mechanism-change event (§9), never an in-place
edit.

---

## 4. `CONTRADICTION_MATERIALITY_PARAMS` — derivation method

*Role (consumed from T1 §5.4; addendum §A5): parameters of `is_material`,
separating a material contradiction (S1) from trivial/stylistic variation.*

**4.1 Evidence that determines the value.**
Primary: **E-STRUCT + E-PRIOR** — the value is entailed by the frozen
commitment that *only substantively incompatible claims are material*, a
trivial phrasing variation is not (T1 §5.4; addendum §A5), and that freezing
the materiality threshold is precisely what makes S1-vs-noise a *frozen rule*
rather than a runtime judgment. **E-TYPE**: parameters must operate on the
two-claim canonical form `is_material(claim_a, claim_b)` (addendum §A5) and
respect its precondition — materiality is a *filter on a genuine
`contradicts` pair*, never a standalone similarity test, and is never invoked
when `contradicts` is false (addendum §A4/§A5). **E-DEV (falsifying only)**:
synthetic pairs may refute a candidate that classifies an obvious
phrasing-variant as material or an obvious incompatibility as immaterial.

**4.2 Constraints the value must satisfy.**
Determinism; the §A5 precondition (defined and consulted only on
`contradicts`-true pairs; defined `False` elsewhere); symmetry consistent with
S1's unordered-pair composition (addendum §A4); firewall-clean; expressible
over the frozen claim/evidence types; and coherence with `contradicts` as a
*separate* predicate (materiality must not silently re-implement or collapse
`contradicts` — addendum §A6 retains them as distinct).

**4.3 Invariants it must preserve.**
All of §2.4, plus: the **S1 firing predicate** (conds 1–3 of addendum §A4)
must keep its meaning — materiality is exactly cond 2, composed with
`contradicts` (cond 1) and cross-origin independence (cond 3); the
**exactly-one-state** guarantee must hold (a materiality value that made S1
fire on same-origin self-contradiction would break the addendum §A0/§F.2
exhaustiveness repair); and the S1 **anchoring totality/faithfulness**
(`Comp`/`Part`, Findings 2/3) must remain well-defined, since `Comp`
membership invokes materiality (addendum §A4).

**4.4 How ScientificAuditor verifies it.**
By §7, confirming a written E-STRUCT argument for the material/immaterial
boundary that is independent of any EXP-1 outcome, that the §A5 precondition is
honored, and that `is_material` remains distinct from `contradicts`. The
auditor checks that S1-vs-noise is now a *frozen rule* (the value removes the
runtime-judgment freedom the placeholder left open — audit criterion 5,
hidden tuning freedom).

**4.5 How ReleaseManager freezes it.**
By §8: verbatim transcription (E4), placeholder retirement, inclusion in the
single E6 digest. Because §A4/§A7 (rules iv/v) *compose* this value, no
separate `PA3_RULESET_VERSION` movement is caused by *supplying the value*
(the rule text is unchanged; only a pending value is filled) — the freeze is a
transcription, not a rule edit (addendum §A6-DIGEST; §C condition 4).

**4.6 Conditions that would require re-derivation.**
Any change to the `is_material` contract or its §A5 precondition; any change to
the S1 composition (addendum §A4) or the `contradicts`/`is_material` split
(§A6); or a demonstrated S1 mis-fire class traceable to the materiality
parameters. Full Wave-2 event (§9).

---

## 5. `EXTRACTION_PARAMS` — derivation method

*Role (consumed from T1 §5.6): parameters of PA-2's deterministic,
entity-level candidate-claim extraction — pure text mechanics, no model calls.*

**5.1 Evidence that determines the value.**
Primary: **E-PRIOR + E-DETERM** — the value is entailed by the frozen
commitments that extraction is *pure text mechanics with no model calls* (M8
unlawful), *no randomness*, and *entity-level* so fabricated-entity probes
yield no claim (CF-R2 first line; T1 §5.6). **E-TYPE**: parameters must produce
the frozen `CandidateClaims.claims` **ordered tuple** with
`CandidateClaim = {claim_text, supporting_doc_ids}` (addendum §A grounding
types), reading only `query_text` and the 3-field documents. **E-DETERM is
decisive here**: PA-2's output feeds `ios`, the §A2 tie-break, and S1, and
addendum §A2 explicitly *refuses* to couple replay-safety to PA-2 tuple
position — so the extraction parameters must yield a *stable* claim set/order
under fixed `(query_text, snapshot)`.

**5.2 Constraints the value must satisfy.**
Determinism (no model call, no randomness, no wall-clock); entity-level
extraction; totality over any document text (including empty/junk);
output-type conformance (ordered tuple of the frozen `CandidateClaim` shape);
`claim_text` well-formed for the §A2 tertiary key (Unicode-code-point
comparison over its UTF-8/NFC form must be a valid total-order tie-breaker);
and firewall-clean.

**5.3 Invariants it must preserve.**
All of §2.4, plus the **§A2 injectivity dependency**: the tie-break's third
key is injective "over any real `CandidateClaims` value" (addendum §A2), and
this property *depends on* `EXTRACTION_PARAMS` producing distinct
`claim_text` for distinct claims. The derived value must preserve that
dependency (it is the standing audit F2/F2′ CONDITIONAL item, addendum §F.5) —
i.e. extraction must not emit colliding `claim_text` that would defeat the
total order and reintroduce nondeterminism.

**5.4 How ScientificAuditor verifies it.**
By §7, confirming: no model call / no randomness (criteria 1); the entity-level
+ CF-R2-first-line argument (criterion 6/8); output-type conformance; and
explicitly the **§A2 injectivity precondition** — the auditor records whether
the derived extraction parameters discharge the F2/F2′ CONDITIONAL or leave it
open (addendum §F.5). E-DEV probes may be cited only as falsifying evidence.

**5.5 How ReleaseManager freezes it.**
By §8: verbatim transcription (E4), placeholder retirement, single-pass E6
digest inclusion. As with §4.5, supplying a pending *value* is a transcription
and does not itself move `PA3_RULESET_VERSION` (no rule text changes).

**5.6 Conditions that would require re-derivation.**
Any change to the PA-2 contract (no-model-call, entity-level, ordered-tuple
output); any change to the frozen `CandidateClaim` type or the §A2 keys that
consume `claim_text`; or a demonstrated determinism/replay break or §A2
injectivity failure traced to extraction. Full Wave-2 event (§9).

---

## 6. `ANSWER_TEMPLATES` — derivation method

*Role (consumed from T1 §5.7; addendum §A7 I-2): one frozen answer-text
template per state `{S0,S1,S2,S3}` — the rubric-facing wording coupled to each
tier.*

**6.1 Evidence that determines the value.**
Primary: **E-PRIOR + E-STRUCT** — each template is entailed by the frozen
answer-construction rule for its state (T1 §3.1 answer column): S0 = explicit
unsupported/unknown/false-premise, **asserts no fact**; S1 = qualified answer
that **represents the alternatives** and asserts no single resolution; S2 =
single **hedged, source-attributed** assertion; S3 = single **asserted,
source-attributed** assertion. **E-TYPE**: templates must be renderable from
`EvidenceStateResult` fields *only* — `selected_claim`, `support_doc_ids`,
`contradiction_doc_ids` (addendum §A7 I-3) — and must honor the §A7 I-2
assertion gate. **CR-3 evidence bound**: templates may reference `query.query`
echo but never rubric/family/metadata (T1 §8), so their wording cannot be a
channel that leaks a forbidden field.

**6.2 Constraints the value must satisfy.**
One template per state, total over `{S0,S1,S2,S3}`; determinism (fixed strings
/ fixed structural slots, not runtime-improvised prose — T1 §5.7); the S0/S1
templates **assert no fact**; the S2/S3 templates are **source-attributed**
(and S2 hedged, S3 asserted); the S1 template **represents both alternatives**
with source attribution while asserting neither (addendum §A7 I-2); slots
bind only to permitted `EvidenceStateResult` fields; firewall-clean; and the
templates sit *at* the frozen wording layer — "rendering niceties above the
frozen templates" are explicitly *not* mechanism-defining (addendum §A6-DIGEST
"Not mechanism-defining"), so the derivation fixes exactly the frozen layer and
no more.

**6.3 Invariants it must preserve.**
All of §2.4, with emphasis on **CR-9 / FM-1** (the S0/S1 templates must make an
assertion structurally impossible outside `{S2,S3}` — addendum §A7 I-2) and on
**CR-3** (no template slot may surface a forbidden input field). The
sentinel-substitution guarantee (C1 test, T1 §8.2) must remain satisfiable:
templates must not vary with rubric/family, so byte-identical output holds
under sentinel substitution.

**6.4 How ScientificAuditor verifies it.**
By §7, checking per-state template↔answer-rule conformance (the S0/S1
no-assertion property and S2/S3 attribution property are the load-bearing
checks), the §A7 I-2 assertion gate, and CR-3 slot-provenance (no template
reads a forbidden field). Because this register is MEDIUM severity, the
auditor also confirms the C1 sentinel test remains consistent with the frozen
templates (`PROGRAM_A_REGISTER_AUDIT.md` Entry 5.7).

**6.5 How ReleaseManager freezes it.**
By §8: verbatim transcription of the four template strings (E4), placeholder
retirement, single-pass E6 digest inclusion under `CONSTANTS_HASH`.

**6.6 Conditions that would require re-derivation.**
Any change to a state's answer-construction rule (T1 §3.1); any change to the
§A7 I-2 assertion gate or the `EvidenceStateResult` fields templates render
from; or a demonstrated CR-3 leak or FM-1 breach via template wording. A pure
*rendering* refinement strictly above the frozen template layer is **not** a
re-derivation (addendum §A6-DIGEST); anything touching the frozen layer is a
full Wave-2 event (§9).

---

## 7. ScientificAuditor verification method (how any derived value is certified)

The ScientificAuditor certifies a *candidate* value by re-running the existing
**8-criterion admissibility grid** (`PROGRAM_A_REGISTER_AUDIT.md`) against the
candidate plus its written derivation record. This document does not replace
that grid; it specifies how the four deferred entries move from
**FAIL (deferred)** to a defensible PASS under it.

| # | Criterion (from REGISTER_AUDIT) | What the auditor checks against the derivation record |
|---|---|---|
| 1 | Deterministic? | The value induces no randomness, model call, wall-clock, or ordering nondeterminism (E-DETERM constraints, §3–§6 part 2). |
| 2 | Contains any probability? | No component is a probability; the value is structural/ordinal (C-FIREWALL). |
| 3 | Calibration leakage? | No component equals/derives from a bin boundary or ECE threshold; `calibration.py` not imported. |
| 4 | EXP-1 leakage? | No EXP-1 outcome, frozen row, or adjudicator signal appears in the evidence cited (§2.2 inadmissible list). |
| 5 | Hidden tuning freedom? | The value closes the freedom the placeholder left open (e.g. S1-vs-noise now a frozen rule); no in-place tuning dial remains. |
| 6 | A-priori justification present? | A written E-STRUCT/E-DETERM/E-TYPE/E-PRIOR argument (C-APRIORI) licenses *this* value and *excludes* the inadmissible variants; E-DEV appears only as falsifying/mechanics evidence. |
| 7 | Amendment rule defined? | The §3–§6 part 6 re-derivation conditions are recorded and route to Wave-2 (§9), never in-place. |
| 8 | Scientifically admissible? | The conjunction of 1–7 holds, and the per-register invariants (§3–§6 part 3) are preserved. |

**Method properties the auditor enforces on the *procedure*, not just the
value:**

- **Provenance separation (no proxy).** The candidate value text and its
  a-priori argument are supplied for the auditor to *test*; the auditor's PASS
  is the auditor's own, recorded directly (E3/E4 role split,
  `PROGRAM_A_G4_EXECUTION_PLAN.md`; T1 §12 no-proxy rule). This methodology
  document supplies neither the value nor the PASS.
- **Falsification-first reading of E-DEV.** Any cited T10/PA-6 result is
  admitted only in its lawful role — refuting a candidate or confirming
  mechanics — and is rejected as evidence if it functions as value *selection
  by observed score* (B-11, T1 §10.2).
- **Firewall re-check at the value level.** Even a structurally-argued value is
  re-checked numerically/textually against the EXP-1 constants it must not
  equal (criteria 2–4), because firewall conformance is asserted by test at
  G4, not assumed.

A candidate that fails any criterion is returned to derivation (§2.2); it does
**not** get a conditional or proxy PASS. The auditor's output is a genuine B2
sign-off (T1 §12 B2; addendum §D) — produced by the auditor, not here.

---

## 8. ReleaseManager freeze method (how a certified value becomes canonical)

Freeze is the ReleaseManager's execution of the existing G4 freeze steps
(`PROGRAM_A_G4_EXECUTION_PLAN.md` E1–E7), specialized to retiring a deferred
register. The ReleaseManager introduces **no value** (it transcribes the
auditor-certified text) and makes **no admissibility judgment** (that is B2).

1. **Precondition.** A genuine B2 sign-off (§7) exists for the candidate value,
   referring to the same freeze object (E2/E3). Absent it, freeze does not
   proceed and the placeholder stands.
2. **Transcribe verbatim (E4).** Copy the certified value text into
   `program_a/constants.py`, replacing the `{}` placeholder and removing the
   entry from `_FREEZE_PENDING_ENTRIES`. No transformation, rounding, or
   re-wording of the certified text; the ScientificAuditor owns the frozen
   value text, the ReleaseManager owns its faithful execution record
   (`PROGRAM_A_G4_EXECUTION_PLAN.md` E4 role split).
3. **All-four precondition for a valid digest.** The freeze of the *register
   set* is admissible only when **none** of the four remains pending
   (`PROGRAM_A_REGISTER_AUDIT.md` §criterion 5;
   `frozen_constants_digest()` raises while any is `{}`). The ReleaseManager
   therefore computes the digest only after all deferred entries are
   transcribed.
4. **Single-pass digest generation and pin (E6/E7).** Compute the SHA-256
   `frozen_constants_digest()` once over the completed ordered serialization
   (the eight §5 register entries + `PA3_RULESET_VERSION` + `STATE_TIER_MAP` +
   `CONFIDENCE_TIERS`; T1 §6.1, addendum §A6-DIGEST), record it as
   `CONSTANTS_HASH`, and pin the commit (B3/G4). From this point each frozen
   value is under the **drift tripwire** and the `mechanism_id()` identity
   binding (T1 §6.1/§9.2).
5. **Identity ratification.** At the same pin, `SPEC_VERSION` and
   `PA3_RULESET_VERSION` take their final frozen values (T1 §5.8; addendum
   §A6-DIGEST). *Supplying a deferred value is a transcription, not a rule
   edit*, so filling `SUPPORT_TEST_PARAMS`/`CONTRADICTION_MATERIALITY_PARAMS`/
   `EXTRACTION_PARAMS`/`ANSWER_TEMPLATES` does not by itself advance
   `PA3_RULESET_VERSION` (which tracks edits to rule *text* i–v); it does
   change the digest, exactly as a completed register input should.

The ReleaseManager's outputs are the E4 transcription record, the E6 digest,
and the B3/G4 pin (T1 §12 B3; addendum §D). This document produces none of
them; it specifies the method by which they are produced.

---

## 9. Re-derivation triggers (what voids a canonical value)

A frozen register value is canonical only for the mechanism identity it was
frozen under. It must be re-derived — by returning to §2 and re-running the
full per-register procedure — under any of the following, which are the
existing change-control conditions (T1 §11; addendum §A6-DIGEST) specialized
to these four registers:

- **Contract change.** Any change to the role/contract the register
  parameterizes: the support-test contract (§3.6), the `is_material` contract
  or its §A5 precondition (§4.6), the PA-2 extraction contract (§5.6), or a
  state's answer-construction rule / §A7 I-2 gate (§6.6).
- **Consumed-type or consumed-rule change.** Any change to the frozen types
  (`program_a/types.py`), the 3-field document schema, `EVIDENCE_ORDERING_KEY`,
  the §A2 keys, or the S0–S3 definitions/precedence that the value feeds.
- **Invariant breach discovered.** Any demonstrated CF-R2 false-positive (§3),
  S1 mis-fire (§4), determinism/§A2-injectivity failure (§5), or FM-1/CR-3
  breach via wording (§6) traced to the frozen value.
- **Firewall breach discovered.** Any later finding that a frozen value equals
  or was fitted to an EXP-1 constant (criteria 2–4).

**Re-derivation is always a Wave-2 mechanism-change event**: T1 revision +
re-freeze + new `SPEC_VERSION` + new `mechanism_id()`, **before** any
frozen-row output is observed, and flatly prohibited after (T1 §11; §10.2
B-11). It is **never** an in-place edit and **never** routed through a
dev-check tuning loop. Dev-check findings (E-DEV) may *trigger* re-derivation
but may not *perform* it in place (B-11 scope limit, T1 §10.2). The
`frozen_constants_digest()` tripwire (T1 §6.1) and the manifest
identity-equality check (T1 §9.2) mechanically enforce that a re-derived value
cannot land silently.

---

## 10. What this document is and is not (closing boundary)

- It **defines** the procedure — evidence classes, constraints, invariants,
  auditor method, freeze method, re-derivation triggers — by which the four
  deferred ES-1 registers acquire canonical values.
- It **contains no value** for any of the four registers, **invents no
  constant**, **implements no code**, **performs no governance**, and
  **redesigns no part of ES-1**.
- Running this procedure is future work owned by named roles: the derivation
  argument and candidate value by the specification/architecture authors, the
  certification (B2) by the ScientificAuditor, the transcription-and-pin
  (B3/G4) by the ReleaseManager. Until they act, the four placeholders stand
  and the standing prohibition holds.

---

## 11. References (read-only grounding)

- `PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` — §2 (firewall boundary), §3
  (states/coupling/precedence), §4 (per-tier semantic argument), §5 (the free-
  constant register incl. §5.3/§5.4/§5.6/§5.7), §6 (digest + SPEC_VERSION), §7
  (Q2/Q3 determinism), §8 (input restriction / C1), §11 (change control),
  §12 (B2/B3 sign-off blocks).
- `PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md` — §A0 (Finding 1 state defs), §A1/§A2
  (selection/tie-break), §A4 (S1 composition + `Comp`/`Part`), §A5
  (`is_material` contract), §A6 (`contradicts` status), §A6-DIGEST (digest
  coverage / `PA3_RULESET_VERSION`), §A7 (seam invariants I-1/I-2/I-3), §C
  (freeze conditions), §D (co-freeze block), §F (consistency verification).
- `PROGRAM_A_REGISTER_AUDIT.md` — the 8-criterion admissibility grid; Entries
  5.1–5.2 (PASS exemplars), 5.3/5.4/5.6/5.7 (the four FAIL-deferred blockers).
- `PROGRAM_A_G4_EXECUTION_PLAN.md` — E1–E7 freeze steps and the
  ScientificAuditor/ReleaseManager role split (no-proxy).
- `ES1_IMPLEMENTATION_GATE.md` — gate boxes A1–A4/B1–B3/C1–C3; standing
  prohibition (:97-99).

---

*End of register derivation method. This document defines HOW canonical values
are produced for `SUPPORT_TEST_PARAMS`, `CONTRADICTION_MATERIALITY_PARAMS`,
`EXTRACTION_PARAMS`, and `ANSWER_TEMPLATES`. It contains none of those values.*
