# PROGRAM A — CONFIDENCE-EMISSION REQUIREMENTS

**Authority:** Chief Scientific Architect review, 2026-07-07. This register
binds **any** Program A confidence-emission mechanism, including but not
limited to the recommended ES-1 (`PROGRAM_A_CONFIDENCE_MECHANISM.md` §7).
Each requirement states its source; none is invented. Verification column
names the check that must exist before a pass claim. Tags: `[FACT]`,
`[INFERENCE]`, `[RISK]`, `[OPEN QUESTION]`.

---

## CR register

### CR-1 — Output contract
**[FACT]** Per frozen query row, emit exactly one record with `answer: str`
(the text shown to a user: answer, refusal, or uncertainty response) and
`tier ∈ {UNKNOWN, DEBATED, PROBABLE, CERTAIN}`; exactly one record per row,
all 210 rows per seed.
*Source:* prereg §1; `dataset.py:17,101-151,327-349`.
*Verification:* `validate_answer_records` (exists, `dataset.py:327`).

### CR-2 — Tier semantics
**[FACT]** The tier is the mechanism's estimate of the probability that
`answer_i` is empirically correct under the frozen gold rubric — not the
probability of a query type, document relevance, source existence, or a
latent internal state.
*Source:* prereg §1 ("Interpretation" paragraph), §5.
*Verification:* T1 preregistration must contain the explicit semantic
argument per tier value (for ES-1: MECHANISM doc §7.2). **[INFERENCE]** A
mechanism without this argument is a category error before execution.

### CR-3 — Input restriction (new; closes a structural cheat channel)
**[FACT]** `adapter.answer(query, seed)` receives the full `QueryRecord`,
which carries `gold_rubric`, `query_family`, and `metadata`
(`dataset.py:33-41`; `run.py:84,181`).
**[INFERENCE — requirement]** The emission surface MUST read only
`query.query` (and `query.query_id` for echo). Reading `gold_rubric`,
`query_family`, or `metadata` at answer time invalidates the run as
held-out-discipline violation (`EXP1_DATASET_SPEC.md` §12.3).
*Verification:* required test — drive the surface with `gold_rubric` and
`query_family` replaced by sentinels and assert byte-identical output.
**[RISK]** No existing document names this channel; no existing test covers
it (registered as CF-R1).
*Verification status (2026-07-07):* CR-3 verification test implemented at
`tests/EXP1/test_cheat_channel_guard.py` -- sentinel-substitution guardrail at
the adapter boundary (`CallableProgramAAdapter.answer`), green against a
conforming stub adapter; structured to accept the eventual ES-1 adapter as a
drop-in `answer_fn` parameter. The redacted-view production change remains
optional and out of scope (needs its own Reviewer + ScientificAuditor
sign-off).

### CR-4 — Determinism and statelessness
**[FACT]** Identical output for identical `(query, seed)`; no hidden state;
stateless across queries; no cross-query learning during execution.
*Source:* `PROGRAM_A_BINDING_SPEC.md` §4; `PROGRAM_A_MASTER_SPECIFICATION.md`
§8, §12.
*Verification:* existing test pattern
`test_answer_is_deterministic_and_side_effect_free`
(`tests/EXP1/test_program_a_adapter.py`), applied to the real surface.

### CR-5 — Purity
**[FACT]** No DB writes, no telemetry perturbation of the run, no mutation of
the `QueryRecord`.
*Source:* BINDING_SPEC §4; MASTER_SPEC §10–§11.
*Verification:* side-effect assertions in the surface's test suite.

### CR-6 — Freeze before observation
**[FACT]** The mechanism (rule, constants, retrieval mode, claim-support
test) is committed and frozen before any frozen-row output is observed; any
post-output change is the protocol-violation kill.
*Source:* prereg §4 kill #5; canon §7 line 130; roadmap T1/G4.
*Verification:* pinned commit recorded at G4; manifest identity (CR-12).

### CR-7 — No outcome coupling, no frozen-row exposure
**[FACT]** No threshold, band, prompt, or refusal behavior may be fitted to
EXP-1 outcomes or tuned on frozen rows; frozen rows are held out from all
development after freeze.
*Source:* prereg §6; `EXP1_DATASET_SPEC.md` §12.2–12.3.
**[OPEN QUESTION]** Pre-freeze fitting on a disjoint dev corpus (M13) is
unruled; prohibited until the ScientificAuditor rules otherwise.

### CR-8 — No evaluation-constant coupling
**[FACT]** The mechanism must not implement, mirror, or fit to
`TIER_TO_CONFIDENCE` (0.125/0.375/0.625/0.875) or `BIN_BOUNDARIES`
(`calibration.py:14-20`); these are evaluation constants owned by
`experiments/EXP1/`.
*Source:* MASTER_SPEC §7 item 3; `EXP1_DATASET_SPEC.md` §4.
**[OPEN QUESTION]** Whether discretizing an a-priori internal probability at
the locked boundaries counts as "mirroring" is unresolved (MECHANISM §7.3);
ES-1 sidesteps it by containing no probability numbers.

### CR-9 — Answer–tier consistency (load-bearing for the FM-1 kill)
**[INFERENCE]** (from prereg §3/§4 jointly) The answer form and the tier must
be produced from the same evidence state, such that: a factual assertion
never co-occurs with `UNKNOWN`/`DEBATED`; `CERTAIN` is only reachable when
the mechanism's strongest evidence condition holds for the emitted claim; the
`UNKNOWN` path emits an explicit unsupported/unknown/false-premise response
and asserts no fact. Rationale: the zero-tolerance kill is the *conjunction*
"fabricated factual answer AND tier CERTAIN" (prereg §4;
`decision.py:20`); coupling makes that conjunction structurally hard instead
of behaviorally lucky.
*Verification:* required test — for every emitted record, assert the
answer-form invariant of its tier's state.

### CR-10 — Dependency deny-list
**[FACT]** The transitive import closure of the emission surface must contain
no `[REJECTED]` mechanism: reasoning engine / ReasoningTrace, thermodynamic
state, knowledge graph, soul graph, self-model, free-energy policy, and the
other canon `:90` items. `AnswerSynthesizer` and `ConfidenceGrade` are
excluded from the lawful path.
*Source:* canon `:90`; BINDING_SPEC R4; `PROGRAM_A_PUBLIC_API.md` §4.
*Verification:* import-guard test (roadmap T7 — does not exist yet; TD-08).

### CR-11 — Free-constant register (I2-analogue)
**[INFERENCE]** (from MASTER_SPEC §17 and the canon §8 uncited-constant
anchor) Every constant the mechanism uses — corroboration thresholds,
independence relation, materiality rule, support-test parameters — must be
named in the T1 preregistration with an a-priori justification, and none may
be data-fitted. A constant that cannot be justified except "it worked" is the
designer-injection pattern and disqualifies the mechanism.
*Verification:* T1 document review (ScientificAuditor).

### CR-12 — Stable identity and versioning
**[FACT]** The surface carries a stable `program_a_adapter_id` recorded in
the manifest (`manifest.py:29`); **[INFERENCE]** the id must change whenever
the frozen mechanism spec changes, so replay can detect mechanism drift
(**[OPEN QUESTION Q8]** — binding of id to spec commit is undecided; until
ruled, encode the T1 spec version in the id string).
*Source:* BINDING_SPEC §4; OPEN_QUESTIONS Q8.

### CR-13 — Record construction path
**[FACT]** Until F-10 is fixed, the surface/binding must return mappings or
construct via `AnswerRecord.from_mapping` — never direct construction —
because direct construction bypasses tier validation
(`dataset.py:113-141`; `PROGRAM_A_ADAPTER_AUDIT.md` §7; R-07).
*Verification:* roadmap T6 inverts the bypass test.

### CR-14 — Tier coverage without tuning
**[FACT]** Fewer than two distinct emitted tiers across the full set is a
kill (`decision.py:19`).
**[INFERENCE — requirement]** The mechanism must make ≥2 tiers *reachable by
design* (distinct evidence structures across the three families), and the
lawful response to a coverage concern is redesign + refreeze **before**
observing frozen-row outputs — never adjustment after (prereg §4 #5;
`PROGRAM_A_FAILURE_ANALYSIS.md` FM-3).

### CR-15 — Retrieval-mode declaration (Q2) and seed-variance declaration (Q3)
**[FACT]** The mechanism spec must record the resolved Q2 decision (frozen
snapshot vs live web) and identify what the seed varies. **[INFERENCE]** If
the resolved design is fully deterministic, prereg §7's amendment clause must
be invoked before execution — all 22 replicates being identical implies a
seed-level effect rate below the powered 10% and the preregistration's own
text mandates amendment.
*Source:* OPEN_QUESTIONS Q2/Q3; prereg §7 final sentence; R-13.

### CR-16 — Refusal-path honesty symmetry
**[FACT]** Refusal is not a safe harbor: a refusal on a known-factual row
whose answer is available in the allowed source set is `y=0` (prereg §3 row
1), and an `UNKNOWN` tier on a fabricated answer is still incorrect (prereg
§3 adjudication note). **[INFERENCE — requirement]** The mechanism may not
buy hallucination-honesty by blanket refusal; its S0-equivalent state must be
entered only on evidence absence, not on query-surface heuristics (which
would also be the M5 family-echo error).

### CR-17 — Governance
**[FACT]** The mechanism requires its own preregistration and
ScientificAuditor sign-off before implementation (`PROGRAM_A_ADAPTER_AUDIT.md`
§6 item 6; roadmap T1/G4); the binding location requires the Architect ruling
(Q4); no pass claim without real specialist sign-off (R-08 — fabricated
approvals are themselves a named threat, MASTER_SPEC §16).

---

## Requirement → kill-criterion map

| Requirement violated | Preregistered consequence |
|---|---|
| CR-2, CR-3, CR-16 | category error / invalid run before results considered (prereg §5) |
| CR-6, CR-7, CR-8 | protocol-violation kill (prereg §4 #5) |
| CR-9 | hard hallucination-honesty kill, zero tolerance (prereg §4 #4) |
| CR-14 | degenerate-tier kill (prereg §4 #3) |
| CR-4, CR-15 | replay/power invalidity; amendment duty (prereg §7) |
| CR-10 | canonical violation (canon `:90`) — run unlawful regardless of ECE |
