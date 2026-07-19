# PROGRAM A — CONFIDENCE-EMISSION MECHANISM ANALYSIS

**Authority:** Chief Scientific Architect review, 2026-07-07.
**Method:** Every claim verified against the file on disk this session and
cited to `file:line` or document section. Epistemic tags binding:
`[FACT]` (verified), `[INFERENCE]` (derived from verified facts), `[RISK]`,
`[OPEN QUESTION]`. No scientific assumption is invented; where the repository
does not determine a behavior, it is tagged `[OPEN QUESTION]`.
**Governance status:** This document is the scientific input to roadmap task
T1 (`PROGRAM_A_IMPLEMENTATION_ROADMAP.md` Phase 1). It does **not**
self-authorize. Q1's decider remains the ScientificAuditor via the T1
mechanism preregistration (`PROGRAM_A_OPEN_QUESTIONS.md` Q1;
`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6). No specialist sign-off is claimed.
**Companion deliverables:** `PROGRAM_A_CONFIDENCE_DECISION_TREE.md`,
`PROGRAM_A_CONFIDENCE_REQUIREMENTS.md`, `PROGRAM_A_CONFIDENCE_RISKS.md`.

---

## 1. Problem statement

**[FACT]** Program A must emit, per frozen query row, exactly one
`(answer, tier)` with `tier ∈ {UNKNOWN, DEBATED, PROBABLE, CERTAIN}`
(`experiments/EXP1/dataset.py:17`; `EXP1_PREREGISTRATION.md` §1). Every other
EXP-1 component exists and is tested (`EXP1_TRACE.md`; `PROGRAM_A_MASTER_
SPECIFICATION.md` §3). The internal rule mapping evidence state → tier is
specified by **no repository document** (`PROGRAM_A_MASTER_SPECIFICATION.md`
§7: "the rule itself. No document specifies it"). This document enumerates
every candidate rule class, rejects the unlawful ones with citations, compares
the lawful survivors, and identifies the best.

## 2. The lawfulness constraint set (summary; full register in REQUIREMENTS doc)

| # | Constraint | Source |
|---|---|---|
| L1 | Tier semantics pinned: `p_i` = "the predictor's estimated probability that `answer_i` is empirically correct under the frozen EXP-1 answer rubric." Any mechanism whose tier does not mean *that* is a category error before execution. | **[FACT]** prereg §1; `PROGRAM_A_OPEN_QUESTIONS.md` Q1 |
| L2 | Not retrieval relevance rebadged; not source-existence confidence. | **[FACT]** prereg §1 line 33, §5; R-01 |
| L3 | Not a 5→4 remap of the synthesizer grades; not any post-hoc tier remapping. | **[FACT]** prereg §4 kill #5; R-02 |
| L4 | No post-hoc calibration; no fitting of the rule, thresholds, or mapping to EXP-1 outcomes or frozen rows. | **[FACT]** prereg §6 ("Prohibited"), §4 kill #5; `EXP1_DATASET_SPEC.md` §12.2–12.3; R-03/R-05 |
| L5 | No `[REJECTED]` mechanism in the path (ReasoningTrace, thermodynamic state, kg, soul graph, self-model, free-energy). | **[FACT]** `PROGRAM_D_CANONICAL.md:90`; R-04 |
| L6 | Deterministic per `(query, seed)`, stateless across queries, side-effect-free, replay-compatible. | **[FACT]** `PROGRAM_A_BINDING_SPEC.md` §4 |
| L7 | Frozen and committed before any frozen-row output is observed. | **[FACT]** prereg §4 kill #5; canon §7 line 130 |
| L8 | Must not implement, mirror, or fit to the EXP-1 evaluation constants (0.125/0.375/0.625/0.875 mapping, bins). | **[FACT]** `PROGRAM_A_MASTER_SPECIFICATION.md` §7 item 3; `EXP1_DATASET_SPEC.md` §4 — *scope of "mirror" is disputed; see §7.3 below* |
| L9 | Must in practice emit ≥2 tiers (degenerate-tier kill) and never emit `CERTAIN` on a fabricated factual answer (zero tolerance). | **[FACT]** prereg §4; `experiments/EXP1/decision.py:19-20` |
| L10 | Building the surface is constitutionally permitted: EXP-1 is the pre-registered experiment that requires it. | **[FACT]** canon §1 rule 2; canon §3 deliverable 1 |

**[FACT]** One further constraint no prior document names: the runner passes
the **entire `QueryRecord`** — including `gold_rubric` and `query_family` —
into `adapter.answer(query, seed)` (`experiments/EXP1/dataset.py:33-41`;
`experiments/EXP1/run.py:84,181`). **[INFERENCE]** A mechanism that reads
`query.gold_rubric` or `query.query_family` can trivially fake calibration;
any lawful mechanism must read **only** `query.query` (and `query.query_id`
for echo). This is constraint **L11** (new; registered as CR-11 in the
REQUIREMENTS deliverable and risk CF-R1 in the RISKS deliverable).

## 3. What a tier lawfully means (the semantic keystone)

**[FACT]** Prereg §1: the tier is a point forecast of `P(C_i = 1)` where
`C_i` = "Program A's answer to query *i* is correct under the EXP-1 gold
rubric." The rubric event includes qualified-answer and refusal correctness:
an ambiguous row is correct iff the answer *represents the ambiguity*; a
hallucination row is correct iff the answer *marks the query unsupported*
(prereg §3 table).

**[INFERENCE — the central scientific distinction]** Therefore the tier is
confidence in **the emitted answer text passing its rubric**, not confidence
that "a single fact is true" and not a description of the *topic's* epistemic
status. Two category errors follow directly:

1. **Family-echo error:** emitting `DEBATED` because the *topic* is debated,
   or `UNKNOWN` because the query *looks* unanswerable, is predicting the
   query family, not answer correctness — the exact label-space substitution
   prereg §3/§5 and `EXP1_DATASET_SPEC.md` §5 forbid. A system that reliably
   produces a *good qualified answer* on a debated topic should, if honest,
   emit a **high** tier for that answer.
2. **Fact-probability error:** scoring "probability the asserted proposition
   is true" is only aligned with L1 when the answer *asserts* a proposition.
   For refusals and qualified answers, the correctness event is behavioral
   (did the answer satisfy the rubric's required elements), and the tier must
   estimate *that*.

**[INFERENCE]** Consequently the mechanism must be a function of
**(evidence state, chosen answer form) → estimated rubric-correctness**, and
the answer-construction rule and the tier rule cannot be designed
independently. This coupling is load-bearing for the zero-tolerance FM-1 kill
(`PROGRAM_A_FAILURE_ANALYSIS.md` FM-1) and is formalized as CR-9.

## 4. Exhaustive mechanism enumeration

Candidate classes are enumerated by their information source. Verdicts:
**UNLAWFUL** (violates a preregistered kill or canon), **CATEGORY ERROR**
(violates L1 semantics before execution), **CONDITIONALLY LAWFUL** (lawful
only under an unresolved ruling), **LAWFUL** (violates nothing in the corpus).

### Class I — rebadging existing numeric signals

- **M1. Retrieval-relevance thresholding** — map `RetrievalSource.score`
  (`backend/retrieval/unified_retriever.py:30`, default 0.5, heuristic) to
  tiers. **UNLAWFUL.** The preregistration names this exact move: "scoring
  retrieval relevance as answer correctness … Rejected" (prereg §5); R-01
  CRITICAL; `PROGRAM_A_BINDING_SPEC.md` R1. Also a category error: relevance
  is not `P(answer correct)`.
- **M2. Synthesizer 5→4 grade remap** — map `ConfidenceGrade` `{CERTAIN,
  PROBABLE, UNCERTAIN, SPECULATIVE, INSUFFICIENT}`
  (`backend/cognition/answer_synthesizer.py:32-47`) onto the four tiers.
  **UNLAWFUL.** Post-hoc tier remapping is kill #5 (prereg §4); R-02. The
  synthesizer additionally consumes `[REJECTED]` mechanisms (ReasoningTrace,
  thermodynamic state, kg — canon `:90`; R-04), violating L5 independently.
- **M3. Binning any internal confidence float through hand-set bands** —
  e.g. the synthesizer's 0.90/0.70/0.50/0.25 bands or new ones. **UNLAWFUL.**
  "Use of post-hoc calibration: Prohibited" (prereg §6); R-03. The float's
  semantics are also not `P(rubric-correct)` (L1).

### Class II — outcome- or label-coupled rules

- **M4. Fitting the rule/thresholds to EXP-1 outcomes or frozen rows.**
  **UNLAWFUL.** Protocol-violation kill (prereg §4 #5); leakage invalidates
  the frozen version (`EXP1_DATASET_SPEC.md` §12.2–12.3); R-03/R-05.
- **M5. Query-family classification → tier** — classify the query as
  factual/ambiguous/hallucination-inducing and emit the "matching" tier.
  **CATEGORY ERROR** (and therefore unlawful before execution). Tier would
  predict the stratification label, not answer correctness — the direct
  label-space substitution guard (prereg §3 "Label-Space Guard", §5 row 1;
  `EXP1_DATASET_SPEC.md` §5). Note the distinction from lawful *evidence*
  sensitivity: a mechanism may respond to evidence structure that correlates
  with family; it may not target the family label.
- **M6. Constant or near-constant tier policy** (always `UNKNOWN`; always
  `PROBABLE`). **UNLAWFUL/SELF-KILLING.** Degenerate-tier kill (prereg §4
  #3; `decision.py:19` `DEGENERATE_TIER_THRESHOLD = 2`) and tier-independence
  kill; also not a confidence estimator at all.
- **M7. Reading `QueryRecord.gold_rubric` / `query_family` at answer time.**
  **UNLAWFUL.** Equivalent to adjudicator contamination in reverse; violates
  L11 and the held-out discipline (`EXP1_DATASET_SPEC.md` §12.3). Named here
  because the type system currently *permits* it (L11, CF-R1).

### Class III — external or program-external estimators

- **M8. Run-time LLM confidence elicitation** (ask a hosted model for answer
  + confidence). **UNLAWFUL AS SCOPED.** Violates L6 determinism/replay
  (provider output is not a function of `(query, seed)`); collides with the
  reproducibility posture of `EXP1_DATASET_SPEC.md` §15 ("static files, not
  generated by an LLM provider at run time" — pinned for dataset/rubrics;
  answer-time is Q2's domain, but replay `PROGRAM_A_MASTER_SPECIFICATION.md`
  §9 requires re-run reproduction either way). A frozen *local* model with
  pinned weights and seed would be deterministic, but its tier rule is not
  auditable as a frozen rule and would require its own preregistration; no
  such asset exists in the repository. **[OPEN QUESTION]** only in the
  frozen-local variant; the hosted variant is flatly unlawful.
- **M9. Predictive-core reuse** — score the answer with the Dirichlet–Markov
  predictor / MDL / `M` statistic (`core/`). **CATEGORY ERROR.** Those
  primitives score next-observation prediction on observation streams for
  H\*/E0 (canon §5), not rubric-correctness of a QA answer; pressing them
  into confidence duty is unit-incommensurate mathematics and novelty
  inflation, both prohibited constructs (canon §1 rule 5). The canon also
  walls Program A off from the research center (canon `:42`;
  `PROGRAM_A_MASTER_SPECIFICATION.md` §14).

### Class IV — evidence-structural rules (the lawful class)

All Class-IV mechanisms share the shape: retrieve evidence for the query,
construct the answer from the evidence, and emit the tier from the **support/
contradiction structure of the evidence with respect to the emitted answer**,
by a rule frozen a priori.

- **M10. Evidence-state partition ("ES rule").** Define a small exhaustive
  set of ordered evidence states from the corroboration structure (see §7),
  couple the answer form to the state, and emit one fixed tier per state.
  **LAWFUL.** Violates no preregistered kill: it is not retrieval relevance
  (the input is claim support, not source rank), not a remap, not post-hoc
  (frozen before outputs), not `[REJECTED]`-dependent, deterministic given a
  fixed retrieval corpus, and its semantics target rubric-correctness through
  an explicit a-priori argument (§7.2).
- **M11. Independent-derivation agreement.** Run k independent deterministic
  extraction pipelines (e.g., per-source answer extraction) and emit the tier
  from cross-pipeline agreement. **LAWFUL** — but on inspection this is M10
  with "agreement count" as the corroboration statistic; it is a refinement
  of the ES rule's support detector, not a rival mechanism.
- **M12. A-priori probabilistic evidence model + boundary discretization.**
  Posit per-source error rates ε fixed a priori, compute
  `P(correct | n support, m contradict)` by likelihood, and emit the tier
  whose locked interval `[0,.25)/[.25,.5)/[.5,.75)/[.75,1]` contains it.
  **CONDITIONALLY LAWFUL**, blocked by two unresolved questions:
  (a) ε has no lawful data source — hand-set ε is an uncited constant of the
  designer-injection pattern the canon exists to kill (canon §8 anchors:
  ~150 constants, zero data-derived), and (b) discretizing at the locked
  boundaries may violate L8's "must not implement, mirror" reading — see
  §7.3. **[OPEN QUESTION]**
- **M13. Dev-set-calibrated rule (pre-freeze, disjoint data).** Fit the
  state→tier map (or M12's ε) on a *non-frozen* development corpus before
  freeze. **CONDITIONALLY LAWFUL.** It is not post-hoc calibration by the
  preregistration's own definition (nothing is fitted after outputs are
  observed; `EXP1_DATASET_SPEC.md` §12.2 anticipates "prior calibration
  examples" existing outside the frozen set, and roadmap T10 already
  contemplates a synthetic non-frozen corpus). But it is Goodhart-adjacent
  (the H1 Goodhart guard, canon §6-H1), no such corpus exists today, and
  whether pre-freeze fitting preserves the "honest a-priori mechanism"
  property is a scientific ruling for the ScientificAuditor, not an
  engineering default. **[OPEN QUESTION]**

**[INFERENCE]** The enumeration is exhaustive at the class level: any tier
rule must draw its information from (I) existing numeric signals, (II) the
evaluation's own labels/outcomes, (III) a program-external estimator, or
(IV) the structure of the evidence Program A itself gathers. Classes I–III
are eliminated above; Class IV is the only lawful class.

## 5. Rejection register (one line each, with the killing citation)

| Mechanism | Verdict | Killing citation |
|---|---|---|
| M1 retrieval-score rebadge | UNLAWFUL | prereg §5; R-01 |
| M2 5→4 remap | UNLAWFUL | prereg §4 #5; R-02; canon `:90` |
| M3 float binning | UNLAWFUL | prereg §6; R-03 |
| M4 outcome/frozen-row fitting | UNLAWFUL | prereg §4 #5; dataset spec §12.3 |
| M5 family classification | CATEGORY ERROR | prereg §3, §5; dataset spec §5 |
| M6 constant tier | SELF-KILLING | prereg §4 #3; decision.py:19 |
| M7 rubric/family peeking | UNLAWFUL | L11; dataset spec §12.3 |
| M8 hosted-LLM elicitation | UNLAWFUL | BINDING_SPEC §4 determinism; MASTER_SPEC §9 |
| M9 predictive-core reuse | CATEGORY ERROR | canon §1 rule 5, §5; MASTER_SPEC §14 |
| M12 a-priori probability model | CONDITIONAL | ε provenance (canon §8); L8 scope (§7.3) |
| M13 dev-set calibration | CONDITIONAL | Goodhart guard canon §6-H1; auditor ruling absent |
| **M10/M11 evidence-state partition** | **LAWFUL** | violates nothing found in the corpus |

## 6. Scientific comparison of the survivors

Criteria: (C1) fidelity to the pinned `p_i` semantics; (C2) freedom from
unjustified hand-set constants (the I2-analogue named in
`PROGRAM_A_MASTER_SPECIFICATION.md` §17: the mechanism must be
distinguishable from a hand-tuned artifact); (C3) determinism/replay under
L6; (C4) structural protection against the zero-tolerance FM-1 kill;
(C5) degenerate-tier risk; (C6) auditability/freezability as a short rule;
(C7) independence from unresolved rulings.

| | M10 ES rule | M12 probability model | M13 dev-calibrated |
|---|---|---|---|
| C1 semantics | state→tier map is an explicit a-priori estimate of rubric-correctness per state **[INFERENCE]** | numerically explicit, *if* ε were meaningful | empirically grounded, *if* corpus is clean |
| C2 constants | few, structural (independence definition, corroboration count); all preregistered and named as untested | ε is exactly the uncited-constant pattern canon §8 indicts | constants are fitted, not hand-set — but fitted on data whose lawfulness is unruled |
| C3 determinism | full, given Q2 snapshot | full | full |
| C4 FM-1 guard | structural: `CERTAIN` requires multi-source support *for the emitted claim*; fabricated claims lack it unless the support detector false-positives | same, weaker (probability can drift high) | depends on corpus coverage of fabrication pressure |
| C5 degenerate risk | low: three query families are designed to induce different evidence states **[INFERENCE]** | low | low |
| C6 auditability | a one-page rule table; freezable verbatim | model + constants; freezable | requires freezing corpus + fitting procedure + result |
| C7 independence | needs only Q2 resolution | blocked on ε ruling + L8-scope ruling | blocked on auditor ruling + corpus that doesn't exist |

**[INFERENCE — verdict]** **M10, the evidence-state partition rule, dominates.**
M12 loses on C2/C7 (its one free parameter reintroduces the designer-injection
pattern, and its discretization needs an L8-scope ruling). M13 is not
currently executable (no lawful dev corpus exists) and needs a ruling M10
does not. M11 folds into M10 as its support-detector implementation. If the
ScientificAuditor later rules that structural states are insufficiently tied
to `p_i` semantics, M12-with-M13-fitted-ε (dev-fitted, pre-freeze, disjoint)
is the designated fallback, in that order.

## 7. The recommended mechanism (ES-1), specified for the T1 preregistration

### 7.1 Inputs and outputs

**[INFERENCE]** (assembled entirely from existing contracts) ES-1 reads
`query.query` only (L11), drives the retrieval substrate in the Q2-resolved
mode (frozen snapshot strongly recommended — see RISKS CF-R4), and computes:

- a set of **candidate claims** extracted deterministically from retrieved
  content answering the query;
- for the selected answer content, the **support set** (sources whose content
  supports the claim under a deterministic claim-support test) and the
  **contradiction set** (sources supporting a materially incompatible claim);
- a source-**independence** relation (e.g., distinct provenance domains), so
  corroboration counts independent origins, not mirrors.

### 7.2 Evidence states, answer coupling, and tier map

| State | Definition (frozen, ordinal) | Answer-construction rule | Tier |
|---|---|---|---|
| S0 | No retrieved content supports any candidate claim | explicit unsupported/unknown/false-premise response; no factual assertion | `UNKNOWN` |
| S1 | Material contradiction: independent sources support incompatible claims | qualified answer that represents the alternatives and does not assert one resolution | `DEBATED` |
| S2 | Support from exactly one independent origin; no material contradiction | single answer, hedged, source-attributed | `PROBABLE` |
| S3 | Support from ≥2 independent origins; no material contradiction | single answer, asserted, source-attributed | `CERTAIN` |

**[INFERENCE — semantic justification, the part L1 demands]** The tier is
Program A's estimate of `P(answer passes its rubric)`, and corroboration
structure is the *only* lawful information Program A has about that event:
S0's refusal is most likely rubric-correct precisely when nothing supports
any claim, but the estimate must stay low because refusing is wrong whenever
the answer *was* available (prereg §3 row 1, refusal-despite-availability is
`y=0`) — the designer's a-priori estimate for S0 is therefore genuinely
uncertain, matching the lowest interval. S1's qualified answer has moderate
a-priori rubric-correctness (it can still omit required alternatives). S2/S3
assert facts whose correctness rises with independent corroboration. The
ordinal structure (more corroboration → higher tier) matches the tier order
by construction, with **no numeric constant taken from the evaluation side**.

**[RISK — declared, not hidden]** Whether the four states' empirical
accuracies land near enough to the locked midpoints for aggregate ECE < 0.10
is exactly H1 and is untested. In particular the S1→`DEBATED` cell carries
the family-echo tension from §3: if well-constructed qualified answers turn
out highly rubric-correct, the `DEBATED` bin over-performs its 0.375 midpoint
and contributes ECE. This is the honest exposure the experiment exists to
measure; a kill here is a valid scientific outcome (FM-4,
`PROGRAM_A_FAILURE_ANALYSIS.md`). The full risk analysis is in
`PROGRAM_A_CONFIDENCE_RISKS.md`.

### 7.3 The L8 boundary question, resolved for ES-1

**[FACT]** `PROGRAM_A_MASTER_SPECIFICATION.md` §7 item 3 forbids Program A to
"implement, mirror, or fit to" the tier→probability mapping and bins.
**[INFERENCE]** ES-1 complies by construction: it contains no probability
number at all — only ordinal structural states. The disputed reading (whether
an internal probability *discretized at the locked boundaries* is forbidden
"mirroring" or is the most faithful possible implementation of the tier
semantics) therefore does not need to be resolved to adopt ES-1; it must be
resolved only if the M12 fallback is ever taken. **[OPEN QUESTION]** —
flagged for the ScientificAuditor in the T1 preregistration.

### 7.4 Free-constant register for ES-1 (I2-analogue discipline)

Every constant the rule needs, named before freeze, none data-fitted:

| Constant | Role | Status |
|---|---|---|
| Corroboration threshold "≥2 independent origins" for S3 | separates S2/S3 | a-priori structural (the smallest count that is corroboration at all); **[RISK]** hand-set in the F2 sense — must be preregistered and defended in T1, never tuned |
| Source-independence relation | prevents mirror-counting | a-priori structural; definition frozen in T1 |
| Claim-support test | decides "supports" / "contradicts" | the load-bearing sub-component; must be deterministic and frozen; its failure modes dominate the risk register (CF-R2) |
| Materiality rule for contradiction | separates S1 from noise | frozen in T1 |

## 8. What this document cannot decide

1. **[OPEN QUESTION — Q1]** Adoption of ES-1 itself: ScientificAuditor
   sign-off via the T1 preregistration is the only lawful authorization
   (`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6; roadmap G2/T1/G4).
2. **[OPEN QUESTION — Q2]** Snapshot vs live retrieval. ES-1 is compatible
   with both; replay (L6) and CF-R4 argue for a frozen snapshot whose
   construction passes leakage review.
3. **[OPEN QUESTION — Q3]** Seed variance: ES-1 on a frozen snapshot is fully
   deterministic, so all 22 replicates are byte-identical and prereg §7's own
   amendment clause **must be invoked before execution** ("this
   preregistration is underpowered and must be amended before outputs are
   observed"). This is a hard consequence, not a choice.
4. **[OPEN QUESTION]** Whether M13-style pre-freeze dev-corpus sanity checks
   of the state→tier map are permitted, and under what documentation duty.

## 9. Conclusion

**[INFERENCE]** At least one lawful mechanism exists, so no impossibility
proof is required: the **evidence-state partition rule (ES-1)** — ordinal
corroboration states, answer-form coupling, one fixed tier per state, zero
evaluation-side constants — is the unique surviving mechanism class under
the full constraint set, and the recommended content of the T1
preregistration. Lawful is not the same as passing: ES-1's calibration is
untested by design, and EXP-1 retains full authority to kill it.
