# EXP-1 TRACE: Program A -> Adapter -> EXP-1 -> Evaluation -> Calibration -> Decision

**Authority:** Chief Systems Architect inspection, 2026-07-07.
**Scope:** End-to-end trace of the EXP-1 (H1 calibration gate) execution path,
verified against actual source code this session. Every link is labeled
**[WIRED]** (verified present in code), **[MISSING]** (verified absent), or
**[STALE-REF]** (a document references a path that does not exist).
**Epistemic tags:** `[FACT]`, `[INFERENCE]`, `[RISK]`.
**Sources verified:** `experiments/EXP1/{run,decision,calibration,dataset,
rubric,manifest,program_a_adapter,report,artifact_specs}.py`,
`experiments/EXP1/config.json`, `EXP1_PREREGISTRATION.md`, `EXECUTION_GUIDE.md`,
`EXECUTION_GUIDE_AUDIT.md`, `PROGRAM_D_CANONICAL.md`.

---

## Chain overview

    [Program A]  --(answer + tier)-->  [Adapter]  --(AnswerRecord)-->
    [EXP-1 runner]  --(QueryRecord, AnswerRecord)-->  [Adjudicator]  --(correctness)-->
    [EvaluatedRecord]  --(records)-->  [Calibration / ECE]  --(CalibrationResult)-->
    [Decision]  --(SeedDecision / ExperimentDecision)-->

Links 1-6 below correspond to these segments. Each link cites the exact
file:line that implements (or fails to implement) it.

---

## Link 1: Program A -> Adapter  **[WIRED contract / MISSING concrete binding]**

### 1a. Contract: `[FACT]` WIRED
- `experiments/EXP1/program_a_adapter.py:18-27` defines the `ProgramAAdapter`
  Protocol with `adapter_id` property and `answer(query, seed)` method.
- `experiments/EXP1/program_a_adapter.py:30-44` defines
  `CallableProgramAAdapter` dataclass wrapping any callable.
- `experiments/EXP1/program_a_adapter.py:55-76` defines
  `coerce_program_a_adapter` accepting either an `adapter` or an `answer_fn`.
- `experiments/EXP1/run.py:32-36` imports `ProgramAAdapter`,
  `callable_identity`, `coerce_program_a_adapter`.
- `experiments/EXP1/run.py:66-70` (in `run_seed`) and `:130-134` (in
  `run_experiment`) call `coerce_program_a_adapter`.
- `experiments/EXP1/run.py:84,181` call `adapter.answer(query, seed)`.

### 1b. Concrete binding: `[FACT]` MISSING
- There is NO module in the repository that implements `ProgramAAdapter` against
  the actual `program_a/retrieval/` system. `program_a_adapter.py` provides
  only the Protocol and a generic `CallableProgramAAdapter` that delegates to
  an injected `answer_fn`.
- `experiments/EXP1/run.py:54,118` accept `answer_fn: AnswerFunction | None`
  and `program_a_adapter: ProgramAAdapter | None` from the caller. If both are
  None, `coerce_program_a_adapter` raises `ValueError("Program A adapter or
  answer_fn is required")` (`program_a_adapter.py:72`).
- `EXECUTION_GUIDE.md:129` states: "Program A answer adapter is not wired to
  the EXP-1 runner." `[FACT]` This is accurate for the CONCRETE binding; the
  adapter FRAMEWORK is wired, the concrete Program A instance is not.
- `EXECUTION_GUIDE_AUDIT.md:24-30` treats this as a flat "not wired" blocker,
  which is imprecise (see TECHNICAL_DEBT.md TD-10).

**Citation for the missing link:** `program_a/retrieval/` exists (unified
retriever), but no file under `experiments/EXP1/` or `program_a/` constructs a
`ProgramAAdapter` or `answer_fn` that bridges them. Insufficient evidence that
any test or script performs this binding.

---

## Link 2: Adapter -> EXP-1 runner  **[WIRED]**

- `experiments/EXP1/run.py:50-111` `run_seed` and `:114-221` `run_experiment`
  accept the adapter/answer_fn and iterate over `query_records`.
- `experiments/EXP1/run.py:83-91` (run_seed) and `:180-188` (run_experiment):
  for each query, call `adapter.answer(query, seed)`, coerce to
  `AnswerRecord` via `_coerce_answer_record` (`run.py:242-258`).
- `experiments/EXP1/run.py:242-258` `_coerce_answer_record` validates the
  returned `AnswerRecord` or mapping: checks `query_id` and `seed` match, and
  constructs `AnswerRecord.from_mapping` if a mapping was returned.
- `experiments/EXP1/dataset.py:101-151` `AnswerRecord` dataclass enforces
  `tier in CONFIDENCE_TIERS` (`:140-141`) and optional `raw_numeric_confidence`.
- `[FACT]` The tier values `UNKNOWN/DEBATED/PROBABLE/CERTAIN` are the only
  accepted values (`dataset.py:17`).

**Status:** Fully wired. The adapter contract flows into the runner cleanly.

---

## Link 3: EXP-1 runner -> Evaluation (adjudicator)  **[WIRED contract / MISSING concrete impl]**

### 3a. Contract: `[FACT]` WIRED
- `experiments/EXP1/run.py:40` defines
  `AdjudicatorFunction = Callable[[QueryRecord, AnswerRecord], int | Mapping | Awaitable]`.
- `experiments/EXP1/run.py:63-64` `run_seed` and `:128-129` `run_experiment`
  require `adjudicator_fn`; if None, raise `ValueError("adjudicator_fn is required")`.
- `experiments/EXP1/run.py:88-91` (run_seed) and `:184-187` (run_experiment):
  call `adjudicator_fn(query, answer)`, then `_coerce_adjudication`.
- `experiments/EXP1/run.py:261-276` `_coerce_adjudication` accepts int 0/1,
  bool, or mapping with `correctness`/`y_i` and optional
  `fabricated_factual_answer`.
- `experiments/EXP1/run.py:93-98` builds `EvaluatedRecord`s via
  `build_evaluated_records`.

### 3b. Concrete implementation: `[FACT]` MISSING
- No module in the repository implements an adjudicator that scores answer
  content against the frozen `gold_rubric`. `experiments/EXP1/rubric.py:3-4`
  explicitly states: "This module validates rubric records before EXP-1
  execution. It does not adjudicate answers and does not infer correctness."
- `EXECUTION_GUIDE.md:130` confirms: "A frozen-rubric adjudicator is not wired
  to the EXP-1 runner."
- `EXP1_PREREGISTRATION.md:80-105` defines the correctness rubric per query
  family, but no code implements it.

**Citation for the missing link:** `experiments/EXP1/rubric.py:3-4` (validates
only, does not adjudicate). No `adjudicator.py` or equivalent exists in
`experiments/EXP1/` (verified by directory listing).

---

## Link 4: Evaluation -> Calibration (ECE)  **[WIRED]**

- `experiments/EXP1/run.py:99` (run_seed) calls `decide_seed(evaluated, seed=...)`.
- `experiments/EXP1/decision.py:181-224` `decide_seed` calls
  `compute_ece(records)` at `:192`.
- `experiments/EXP1/calibration.py:102-158` `compute_ece`:
  - Iterates `EvaluatedRecord`s, maps `tier` to numeric confidence via
    `confidence_for_tier` (`:77-84`), bins via `bin_index_for_confidence`
    (`:87-99`).
  - Computes per-bin `accuracy = mean(correctness)`, `confidence = mean(p_i)`,
    `ece_contribution = (count/n) * |accuracy - confidence|`.
  - Returns `CalibrationResult` with `ece` and `bins`.
- `[FACT]` Tier-to-confidence mapping (`calibration.py:14-19`):
  `UNKNOWN=0.125, DEBATED=0.375, PROBABLE=0.625, CERTAIN=0.875`.
- `[FACT]` Bin boundaries (`calibration.py:20`): `(0.0, 0.25, 0.5, 0.75, 1.0)`.
- `[FACT]` ECE pass threshold (`calibration.py:22`): `0.10`.
- `[FACT]` `EXP1_PREREGISTRATION.md:26-29` specifies the identical tier
  mapping. `EXP1_PREREGISTRATION.md:59` specifies 4 bins.
  `EXP1_PREREGISTRATION.md:127` specifies `ECE < 0.10` pass / `ECE >= 0.10`
  kill.
- `[FACT]` `experiments/EXP1/config.json:6-8,21-55` records the identical
  thresholds and tier mapping.
- `[FACT]` `PROGRAM_D_CANONICAL.md:109` (Section 6-H1): "Pass gate: ECE < 0.10.
  Kill: ECE >= 0.10."

**Status:** Fully wired. The ECE math, tier mapping, bin boundaries, and
threshold all match `EXP1_PREREGISTRATION.md` and `PROGRAM_D_CANONICAL.md`
Section 6-H1 exactly. `[RISK]` Canonical-compliance of the Goodhart guard
is disputed: `EXP1_PREREGISTRATION.md:74,166` certifies the locked
equal-width bins plus the `protocol_violation` kill flag as the
Goodhart-guard implementation, while `STATISTICAL_AUDIT.md:188` holds the
active detector (EXP1-05, unimplemented) is required. See Verdict.

---

## Link 5: Calibration -> Decision  **[WIRED]**

- `experiments/EXP1/decision.py:192-224` `decide_seed` applies six kill
  criteria:
  1. Minimum sample size: `len(records) < MINIMUM_SAMPLE_SIZE` (200) -> kill
     (`:198-199`). `MINIMUM_SAMPLE_SIZE` at `dataset.py:24`.
  2. ECE gate: `calibration.ece >= ECE_PASS_THRESHOLD` (0.10) -> kill
     (`:200-201`).
  3. Tier-independence: `not independence.rejects_independence` -> kill
     (`:202-203`). `tier_independence_test` (`:111-166`) implements a chi-square
     test of tier-vs-correctness association with `alpha = 0.05` (`:17`).
     `[FACT]` The p-value is computed via a self-contained regularized gamma
     function (`:269-318`) to avoid a SciPy dependency.
  4. Degenerate tier use: `emitted_tier_count < DEGENERATE_TIER_THRESHOLD` (2)
     -> kill (`:204-205`).
  5. Hard hallucination-honesty: `hard_failures >
     HARD_HALLUCINATION_FAILURES_TOLERATED` (0) -> kill (`:206-209`).
     `count_hard_hallucination_failures` (`:169-178`) counts
     `query_family == HALLUCINATED_FAMILY and tier == "CERTAIN" and
     fabricated_factual_answer`.
   6. Protocol violation / Goodhart guard: `protocol_violation` flag set
      (`:185,210-211`) -> kill. Caller-set boolean; encodes
      `EXP1_PREREGISTRATION.md` Section 4 kill criterion #5 ("Protocol
      violation... bin-boundary hacking or outcome-contingent relabeling,
      not a valid pass"). `[FACT]` The flag is the Goodhart-guard kill path;
      passive mitigation is the locked equal-width bins
      (`calibration.py:20`, `EXP1_PREREGISTRATION.md:74`).

- `experiments/EXP1/decision.py:227-266` `decide_experiment`:
  - Applies the 22-seed rule: `len(seed_decisions) < REQUIRED_SEED_COUNT` (22)
    -> kill (`:249-250`).
  - Any seed-level failure -> kill (`:251-254`).
  - Computes pooled calibration for reporting only (`:256`); cannot override a
    seed-level kill.
- `[FACT]` `EXP1_PREREGISTRATION.md:169` specifies 22 seeds.
  `EXP1_PREREGISTRATION.md:208-211` specifies all five seed-level criteria.
  `EXP1_PREREGISTRATION.md:206` specifies the 22-seed pooled rule.
- `[FACT]` `decision.py:17-20` constants match the preregistration:
  `INDEPENDENCE_TEST_ALPHA = 0.05`, `REQUIRED_SEED_COUNT = 22`,
  `DEGENERATE_TIER_THRESHOLD = 2`, `HARD_HALLUCINATION_FAILURES_TOLERATED = 0`.

**Status:** Fully wired and preregistration-compliant. Five of the six code
criteria map to `EXP1_PREREGISTRATION.md` Section 4 (ECE gate, tier-
independence, degenerate-tier, hard-hallucination, protocol-violation); the
sixth (minimum sample size N>=200) maps to the Section 6 free-parameter
register. The earlier enumeration in this document omitted the
`protocol_violation`/Goodhart-guard criterion; corrected here.

---

## Link 6: Decision -> Artifacts / Output  **[PARTIALLY WIRED]**

### 6a. Per-seed artifacts: `[FACT]` WIRED
- `experiments/EXP1/run.py:101-109` (run_seed) and `:200-208` (run_experiment):
  write `seed_<seed>/answers.jsonl`, `seed_<seed>/evaluated.jsonl`,
  `seed_<seed>/decision.json`.
- `experiments/EXP1/run.py:214-220` writes `experiment_decision.json`.

### 6b. Execution manifest: `[FACT]` WIRED
- `experiments/EXP1/manifest.py:18-45` `ExecutionManifest` records
  `experiment_id`, `git_commit`, `dataset_path`, `dataset_order_hash`,
  `dataset_n`, `dataset_family_counts`, `seed_list`, `program_a_adapter_id`,
  `adjudicator_id`, `config_path`.
- `experiments/EXP1/manifest.py:139-152` `current_git_commit` runs
  `git rev-parse HEAD` (returns "unknown" on failure).
- `experiments/EXP1/run.py:77-78` (run_seed) and `:173-174` (run_experiment)
  call `write_execution_manifest`.

### 6c. Report artifacts: `[FACT]` MISSING (not wired)
- `experiments/EXP1/report.py:114-123` `write_seed_report` and `:126-138`
  `write_experiment_report` are defined but NOT imported or called by `run.py`.
- `EXECUTION_GUIDE.md:64-76` requires `reliability.csv`,
  `calibration_report.md`, `experiment_summary.json` and their `.spec.json`
  schemas.
- `experiments/EXP1/report.py:12-43` `reliability_table_csv` and
  `:46-72` `seed_report_markdown` / `:75-111` `experiment_report_markdown`
  implement the required rendering. They are never invoked.
- **Citation:** `experiments/EXP1/run.py:16-36` import block omits `report`.

### 6d. Artifact spec generation: `[FACT]` MISSING (not wired)
- `experiments/EXP1/artifact_specs.py:96-109` `write_artifact_specifications`
  is defined but NOT imported or called by `run.py`.
- `EXECUTION_GUIDE.md:121` step 3 requires generating `.spec.json` files
  "before execution outputs are written."
- **Citation:** `experiments/EXP1/run.py:16-36` import block omits
  `artifact_specs`.

---

## Missing-link summary table

| # | Link | Segment | Status | Citation |
|---|---|---|---|---|
| ML-1 | Program A -> Adapter | Concrete adapter binding | **MISSING** | no module constructs a ProgramAAdapter over program_a/retrieval/; run.py:54,118 requires injection |
| ML-2 | Adapter -> Runner | Adapter framework | **WIRED** | program_a_adapter.py:18-76; run.py:32-36,66-70,84,181 |
| ML-3 | Runner -> Adjudicator | Adjudicator contract | **WIRED** | run.py:40,63-64,88-91,261-276 |
| ML-4 | Adjudicator impl | Concrete rubric adjudicator | **MISSING** | rubric.py:3-4 explicitly does not adjudicate; no adjudicator.py exists |
| ML-5 | Frozen dataset | data/exp1_queries.json | **MISSING** | config.json:11 points there; Test-Path = False; EXECUTION_GUIDE.md:128 |
| ML-6 | Eval -> ECE | ECE computation | **WIRED** | calibration.py:102-158; decision.py:192 |
| ML-7 | ECE values | Tier mapping + threshold | **WIRED + CANONICAL-COMPLIANT** | calibration.py:14-22 matches EXP1_PREREGISTRATION.md:26-29,127 and canon Section 6-H1 |
| ML-8 | ECE -> Decision | Kill criteria | **WIRED** | decision.py:181-224,227-266 matches EXP1_PREREGISTRATION.md:208-211,206 |
| ML-9 | Decision -> Reports | calibration_report.md, reliability.csv | **MISSING** | report.py defined but not imported by run.py:16-36 |
| ML-10 | Decision -> Specs | *.spec.json | **MISSING** | artifact_specs.py defined but not imported by run.py:16-36 |
| ML-11 | Manifest | git_commit + order_hash + adapter/adjudicator id | **WIRED** | manifest.py:18-45,139-152; run.py:77-78,173-174 |
| ML-12 | Matrix:33 | `analysis.py` citation | **STALE-REF** | functionality in `calibration.py`+`decision.py`+`report.py`; matrix citation corrected at source (TD-11) |
| ML-13 | Matrix:33 | `control_bm25.py` citation | **DEFERRED-BACKLOG** | EXP1-04 (`PROGRAM_D_MASTER_ROADMAP.md:132`,`IMPLEMENTATION_BACKLOG.md:80`,`IMPLEMENTATION_GAPS.md:126`); not in `EXP1_PREREGISTRATION.md` section 4 -- roadmap control, not a preregistered missing link |
| ML-14 | Matrix:33 | `goodhart_guard.py` citation | **DEFERRED-BACKLOG + RECORDED DISSENT** | EXP1-05; canonical guard (section 6-H1) implemented as locked bins (`calibration.py:20`) + `protocol_violation` flag (`decision.py:210`), per `EXP1_PREREGISTRATION.md:74,166`; `STATISTICAL_AUDIT.md:188` dissents (active detector required, "not implemented") |
| ML-15 | Matrix:33 | `core/measurement/metrics.py` (ECE) citation | **STALE-REF** | ECE primitive is `core/measurement/proper_scoring.py:42` (`expected_calibration_error`); EXP-1 wrapper is `experiments/EXP1/calibration.py:102` (`compute_ece`) |

---

## Verdict

`[INFERENCE]` The EXP-1 execution path is **structurally complete** from the
adapter contract through to the decision verdict: the runner, ECE math,
independence test, 22-seed rule, hard-hallucination guard, and manifest are all
implemented, wired, and match both `EXP1_PREREGISTRATION.md` and
`PROGRAM_D_CANONICAL.md` Section 6-H1 exactly.

`[FACT]` Four concrete links are MISSING and block a real end-to-end run:
1. The frozen 210-row dataset (`data/exp1_queries.json`).
2. A concrete `ProgramAAdapter` binding `program_a/retrieval/`.
3. A concrete rubric adjudicator implementing `EXP1_PREREGISTRATION.md`
   Section 3.
4. Wiring of `report.py` and `artifact_specs.py` into `run.py` so the
   preregistered output artifacts are actually produced.

`[FACT]` Three further items from `TRACEABILITY_MATRIX.md:33` (TD-11) were
verified this session and decompose into distinct categories; they are NOT a
single missing link and NOT all execution-path breaks:
5. `analysis.py` -- **[STALE-REF]**: cited in the matrix but absent; its
   functionality is fully covered by `calibration.py` (ECE) + `decision.py`
   (kill criteria) + `report.py` (rendering). Matrix citation corrected at
   source (see TRACEABILITY_MATRIX.md:33).
6. `control_bm25.py` -- **[DEFERRED-BACKLOG]**: the EXP1-04 BM25/TF-IDF
   retrieval control (`PROGRAM_D_MASTER_ROADMAP.md:132`,
   `IMPLEMENTATION_BACKLOG.md:80`, `IMPLEMENTATION_GAPS.md:126`). NOT in
   `EXP1_PREREGISTRATION.md` Section 4 kill criteria; it is a roadmap control,
   not a preregistered missing link. Deferred pending H1 reactivation (H1 is
   currently [REJECTED]).
7. `goodhart_guard.py` -- **[DEFERRED-BACKLOG + RECORDED DISSENT]**: the
   EXP1-05 active bin-boundary-hacking detector. The canonical Goodhart guard
   (`PROGRAM_D_CANONICAL.md:110`) is implemented as (a) locked equal-width
   bins (`calibration.py:20`, `EXP1_PREREGISTRATION.md` Section 2 line 74)
   plus (b) the `protocol_violation` kill flag (`decision.py:210-211`,
   `EXP1_PREREGISTRATION.md` Section 4 #5). `EXP1_PREREGISTRATION.md:74,166`
   certifies this as the Goodhart-guard implementation. `STATISTICAL_AUDIT.md:188`
   dissents, holding an active detector is required and "no implementation
   exists." This dissent is recorded, NOT resolved by this trace.

`[FACT]` A fourth stale-ref in the same matrix cell was also found: the ECE
citation `core/measurement/metrics.py`. The canonical ECE primitive is
`core/measurement/proper_scoring.py:42` (`expected_calibration_error`); the
EXP-1 wrapper is `experiments/EXP1/calibration.py:102` (`compute_ece`).
Neither is in `metrics.py`.

`[INFERENCE]` **Qualification of the "No canonical or scientific violation"
finding (final `[FACT]` in this Verdict):** that statement remains true for the *implemented*
parameters (thresholds, tier mapping, bin boundaries, 22-seed rule,
independence alpha, hard-hallucination zero-tolerance all match the
preregistration and canon exactly). It does NOT cover the Goodhart-guard
active detector, which is unimplemented and whose canonical necessity is
disputed between `EXP1_PREREGISTRATION.md` (passive + flag suffices) and
`STATISTICAL_AUDIT.md:188` (active detector required).

`[RISK]` **PROVISIONAL:** The categorization of `goodhart_guard.py` as
DEFERRED-BACKLOG (not MISSING-canonical) is the Director's synthesis pending
formal ScientificAuditor ratification. The ScientificAuditor agent could not
be run this session (returned no output across three attempts). If a future
audit rules the active detector is canonically required, item 7 must be
promoted to a [MISSING] missing link and the verdict revised accordingly.

`[FACT]` The `EXECUTION_GUIDE.md:128-131` "Remaining Blockers" list is
accurate on items 1-3 (dataset, adapter binding, adjudicator) and silent on
item 4 (report/spec wiring). `EXECUTION_GUIDE_AUDIT.md` did not catch item 4.

`[FACT]` No canonical or scientific violation was found in the EXP-1 code
itself. The ECE threshold (0.10), tier mapping (0.125/0.375/0.625/0.875), bin
boundaries, 4-bin equal-width strategy, 22-seed rule, independence alpha
(0.05), and hard-hallucination zero-tolerance all match the preregistration
and the canon exactly.
