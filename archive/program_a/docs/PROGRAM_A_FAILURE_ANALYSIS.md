# PROGRAM A — FAILURE ANALYSIS

**Authority:** Chief Scientist / Chief Systems Architect design review,
2026-07-07. Two questions: (1) why does Program A not exist, and which
repository decisions caused the gap; (2) how can the future Program A fail,
mapped to the wired kill criteria. Tags: `[FACT]`, `[INFERENCE]`, `[RISK]`,
`[OPEN QUESTION]`.

---

## 1. Root-cause analysis: why Program A does not exist

### RC-1 — The redesign delegitimized the old answer path without commissioning a replacement
**[FACT]** The 2026-07-02 PI REDESIGN (canon §3) retired the old thesis and
marked the mechanisms the deployed answer path stands on — reasoning engine
type-lifting, thermodynamic state, soul concepts, self-model — permanently
`[REJECTED]` (canon `:90`). The only live answer-producing surface,
`AnswerSynthesizer`, consumes exactly those mechanisms
(`answer_synthesizer.py:106-165`) and emits a non-canonical 5-grade taxonomy
(`:32-47`).
**[INFERENCE]** The redesign therefore made the existing Program A
implementation unlawful for its own gate (EXP-1) without specifying a
successor. That is the primary cause.

### RC-2 — The §9-DeepSeek engineering split was ordered but never executed
**[FACT]** Canon §9 instructs the engineering layer to split `backend/` into
`program_a/`, `program_b/`, `program_c/`. On disk, only empty skeletons were
created: `program_a/{retrieval,nlp}/__init__.py` are 0-byte; `program_c/`'s
13 subpackages are all 0-byte (TD-13); the real code stayed in `backend/`
(`DEPENDENCY_GRAPH.md` §3.2).
**[INFERENCE]** The skeletons then generated documentation fiction —
`ARCHITECTURE_MAP.md:54` ("program_a LIVE"), `repository_v2.md`'s named-file
claims (TD-03) — which masked the gap until the 2026-07-07 audits re-verified
disk state.

### RC-3 — The preregistration lawfully foreclosed every shortcut
**[FACT]** All three cheap ways to fake a Program A were preregistered as
kills before implementation: retrieval-score→tier (prereg §5), 5→4 remap
(§4 #5), float-binning / post-hoc calibration (§6).
**[INFERENCE]** This is the system working as designed: the gap exists
*because* the guards held. The correct reading is not "the adapter task
failed" but "the preregistration prevented an invalid Program A from being
smuggled in through an adapter" (`PROGRAM_A_BINDING_SPEC.md` §11 FAIL
verdict, correctly issued).

### RC-4 — Constitutional gating + specialist runtime failure
**[FACT]** Constitutional rule: "No subsystem without a pre-registered
experiment that requires it" (canon `:33`); building the emission surface
requires its own preregistration + ScientificAuditor sign-off
(`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6). The Architect, Builder, Reviewer,
and ScientificAuditor agents returned no output across all invocation
attempts this session (BINDING_SPEC header; R8).
**[INFERENCE]** The authorization chain that could unblock construction was
unavailable, so the Director lawfully stopped at specification.

### RC-5 — Priority sequencing
**[FACT]** Sprint 1 was E0 (H\*); the Research Director's GO (2026-07-04)
authorized Sprint 2 = EXP-1 conditionally, with F-A trigger fix and EXP-0 as
tracked prerequisites (`RESEARCH_DIRECTOR_DECISION.md` §8;
`SPRINT2_EXECUTION_CHECKLIST.md` "Before EXP-1 Starts").
**[INFERENCE]** Program A construction simply had not reached the front of
the queue before this design review.

**Verdict:** the gap is a *governed* gap — created by RC-1/RC-2, held open by
RC-3/RC-4, and now the acknowledged scientific bottleneck.

---

## 2. Forward failure-mode analysis (FMEA) for the future Program A

Each mode is mapped to the wired detection (or its absence). "Detection"
cites code that fires today.

| FM | Failure mode | Cause class | Effect | Wired detection | Residual gap |
|---|---|---|---|---|---|
| FM-1 | Fabricated factual answer emitted `CERTAIN` on a hallucinated/false-premise row | tier mechanism overconfidence (historical Q6) | **hard kill**, zero tolerance | `decision.py` `count_hard_hallucination_failures`, tolerance 0 **[FACT]** | Detection depends on the adjudicator setting `fabricated_factual_answer` — adjudicator is MISSING (ML-4) |
| FM-2 | Non-canonical tier returned as an `AnswerRecord` instance | F-10 bypass | crash later (`KeyError` in `confidence_for_tier`) instead of a clean reject | `from_mapping` path only **[FACT]** | Fix F-10 (validate in `__post_init__` / re-validate in coercion) — roadmap T6 |
| FM-3 | One tier emitted for all 210 rows | over-conservative refusal policy | degenerate-tier kill | `decision.py` DEGENERATE_TIER_THRESHOLD=2 **[FACT]** | none — but note the lawful response is redesign+refreeze *before* observing outputs, never tuning after (prereg §4 #5) |
| FM-4 | ECE ≥ 0.10 on any seed | miscalibrated tier mechanism | seed kill → experiment kill | `decision.py` ECE gate **[FACT]** | none — this is H1 being falsified, a valid scientific outcome |
| FM-5 | Tiers carry no correctness signal | tier ⊥ correctness | independence-test kill | chi-square α=0.05, self-contained p-value (`decision.py:111-166`) **[FACT]** | none |
| FM-6 | Retrieval variance across seeds → some seeds pass, one kills | live-web drift (R-06) | experiment kill (any-seed rule) | 22-seed rule **[FACT]** | resolve Q2 (snapshot vs live) before freeze; a kill from infrastructure flakiness is still a kill — prereg has no flake exemption **[RISK]** |
| FM-7 | Frozen rows leak into prompt/tier tuning | process failure | freeze invalidated; pass claim void | none mechanical | leakage checks are human gates (`EXP1_DATASET_SPEC.md` §16.2) **[RISK]** |
| FM-8 | Bin/mapping/rubric edited after outputs observed | Goodhart pressure | protocol-violation kill | caller-set `protocol_violation` flag (`decision.py:210-211`) **[FACT]** | flag is *caller-set*; active detector EXP1-05 unimplemented; dissent recorded (`STATISTICAL_AUDIT.md:188`) **[RISK]** |
| FM-9 | Runner executed with <22 seeds or pooled results used to override a seed kill | shortcut pressure | invalid pass claim | `decide_experiment` REQUIRED_SEED_COUNT=22; pooled = report-only (`decision.py:227-266`) **[FACT]** | none |
| FM-10 | Report artifacts absent from the run record | TD-05 unwired generators | run is non-compliant with `EXECUTION_GUIDE.md` output contract even if decisions are correct | none (silent) | wire report/artifact_specs (roadmap T5) |
| FM-11 | Emission surface silently imports a `[REJECTED]` mechanism via a transitive dependency | TD-08, no import guard | canonical violation invisible at review | none | import-guard test (roadmap T7) |
| FM-12 | Adjudicator rewards uncertainty language as correctness | label-space confusion | inflated accuracy in low bins → fake calibration | rubric constraints (dataset spec §8: "MUST NOT award correctness because a response expresses uncertainty") | adjudicator is unbuilt; guard exists only as spec text **[RISK]** |

## 3. Failure-ordering note

**[INFERENCE]** The modes that can *invalidate* EXP-1 (FM-7, FM-8, FM-12)
are all process/human modes with weak mechanical detection; the modes with
strong mechanical detection (FM-1, FM-3, FM-4, FM-5, FM-9) are the honest
scientific outcomes. Engineering effort should therefore go to the weakly
detected modes first — which is exactly the ordering in
`PROGRAM_A_IMPLEMENTATION_ROADMAP.md` (mechanism freeze and dataset freeze
precede any execution).

## 4. What a kill means (pre-agreed interpretation)

**[FACT]** Canon §6-H1: ECE ≥ 0.10 or tier-independence → "the 'honest
uncertainty' claim is rejected." Canon §8: the honest publication path
already budgets for negative results. **[INFERENCE]** A killed EXP-1 is a
reportable outcome, not a project failure; the only unacceptable outcome is
an *invalid* run (FM-6 infrastructure kill, FM-7/FM-8/FM-12 contamination),
which wastes the frozen dataset version (`EXP1_DATASET_SPEC.md` §18: frozen
v1 cannot be repaired for a pass claim after outputs).
