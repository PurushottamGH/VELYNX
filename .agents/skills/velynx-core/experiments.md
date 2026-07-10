# Experiments

This document covers EXP-0, EXP-1, EXP-2, and E0 from repository evidence
only. It also identifies preregistration documents, frozen parameters, and
protected files. Experiment states come from `experiment_registry.yaml`;
parameters from `parameter_registry.yaml`; reproducibility from
`reproducibility.yaml`.

## 1. Experiment-to-hypothesis map

| Experiment | Hypothesis | Registry status   | Directory          | Implemented? |
|------------|------------|-------------------|--------------------|--------------|
| E0         | H* (central) | running         | `experiments/E0/`   | yes          |
| EXP-1      | H1         | planned           | `experiments/EXP1/` | yes (adapter) |
| EXP-2      | H2         | planned           | `experiments/EXP2/` | no (empty stub) |
| EXP-0      | (audit, see below) | not in registry | `experiments/EXP0/` | yes          |
| R1         | H* (archived) | archived (null, p=0.866) | `experiments/R1/` | no (stub) |
| R3F        | H* (archived) | archived (legacy benchmark) | `experiments/R3F/` | no (stub) |
| EXP-3      | H3 [REJECTED] | archived        | `experiments/EXP3/` | no (stub)   |
| EXP-4      | H3 [REJECTED] | archived        | `experiments/EXP4/` | no (stub)   |

Hypothesis mappings (HYPOTHESIS_REGISTER.md): H* -> E0, H1 -> EXP-1,
H2 -> EXP-2, H3 -> EXP-3 (and H3 is `[REJECTED]`, subsumed by H* per canon
Section 10 Issue-1). EXP-3 and EXP-4 must not be built or referenced as
live experiments. R1 and R3F must not be rebuilt.

## 2. E0 - Emergence-vs-Injection Discrimination (central, H*)

The experiment that decides H*. "Emergence vs injection on a nonlinear-
latent stream" (PROGRAM_D_CANONICAL.md Section 7).

- **Location:** `experiments/E0/` (`run.py`, `dataset.py`, `analysis.py`,
  `decision.py`, `growth_diagnostics.py`, `leakage_check.py`, `config.json`,
  `E0_IMPLEMENTATION_REPORT.md`, `E0_FINAL_IMPLEMENTATION_REPORT.md`).
- **Conditions:** `T` (treatment - error-gated growth ON via the MDL
  trigger), `C1` (fixed-capacity - no growth), `C2` (error-decoupled -
  capacity-matched growth at random times), `C3` (shuffled-input -
  temporal order destroyed, marginals preserved).
- **DV-a:** held-out predictive log-likelihood.
- **DV-b:** emergence statistic `M = NMI(learned, true) - NMI(learned,
  shuffled)` (canon Section 5.5; `E[M | H0] = 0`).
- **Kill:** T fails to beat both C1 and C2 on DV-a at `p < 0.01` across
  `>= 5` seeds, **or** DV-b within noise of the shuffled control, after
  two honest attempts -> H* falsified for this environment class.
- **Machinery:** `core.predictors.dirichlet_markov.DirichletMarkovPredictor`,
  `core.mdl.mdl_growth.should_grow`, `experiments.E0.dataset.NonlinearLatentEnvironment`,
  `experiments.E0.decision.E0Decider` / `M_STATISTIC_MARGIN`.
- **Frozen config** (`experiments/E0/config.json`): `seed 42`,
  `env_seed 101`, `num_train_steps 10000`, `num_test_steps 2000`,
  `num_latent_states 10`, `observation_dim 16`, `transition_alpha 1.0`,
  `noise_sigma 0.05`, `initial_capacity 2`, `alpha 1.0`, `b 1.0`,
  `evaluate_every 500`, `warmup_steps 1000`, `conditions [T,C1,C2,C3]`,
  `num_seeds 5`.

## 3. EXP-1 - Calibration Gate (H1)

The Program A product-honesty gate. "Program A produces confidence
estimates matching empirical correctness" (EXP1_PREREGISTRATION.md).

- **Location:** `experiments/EXP1/` (`run.py`, `dataset.py`, `decision.py`,
  `manifest.py`, `program_a_adapter.py`, `calibration.py`, `rubric.py`,
  `report.py`, `artifact_specs.py`, `config.json`).
- **Primary metric:** Expected Calibration Error (ECE). **Pass gate:
  `ECE < 0.10`. Kill: `ECE >= 0.10`** or tier-independence failure.
- **Tiers (locked, four equal-width bins over [0,1]):** UNKNOWN -> 0.125,
  DEBATED -> 0.375, PROBABLE -> 0.625, CERTAIN -> 0.875. The numeric
  confidence is the bin midpoint; the mapping is locked before execution
  and must not be fitted to outcomes.
- **Dataset:** `calibration_queries_v1` (`data/exp1_queries.json`),
  minimum 200 rows, planned balanced 210 (70 known factual / 70 ambiguous
  or debated / 70 hallucinated, unanswerable, or false-premise).
- **Replication:** 22 independent seeds; expected seed-level
  kill-relevant effect rate 0.1; miss-probability at seed count 0.0985
  (< 0.1 target).
- **Decision thresholds:** `ece_kill_threshold_gte 0.1`,
  `independence_test_alpha 0.05`, `degenerate_tier_use_threshold_less_than 2`,
  `hard_hallucination_honesty_failures_tolerated 0`.
- **Prohibited measurements (label-space guard against the E0 F1
  pattern):** tier labels vs query family labels; retrieval relevance as
  answer correctness; internal source confidence as answer confidence;
  correctness awarded from uncertainty expression; post-hoc tier
  remapping. `post_hoc_calibration_prohibited` and
  `equal_frequency_bins_prohibited` are both true.
- **Runner contract:** `run.py` is an **adapter** - callable orchestration
  only. It does not execute Program A at import time and does not own
  correctness adjudication; callers must inject both the Program A answer
  function and the frozen-rubric adjudicator (`AnswerFunction`,
  `AdjudicatorFunction`). Adapter identity is recorded via
  `callable_identity` for the execution manifest.

## 4. EXP-2 - Affective Indexing (H2)

The one possibly-novel research question (canon Section 3).

- **Location:** `experiments/EXP2/` - currently an **empty stub** (only
  `__init__.py`). Registry status: `planned`.
- **Hypothesis:** a learned affective-framing -> problem-solving-schema
  mapping improves objective task outcomes over an unframed baseline.
- **IV:** affective frame present vs absent (prompt-level).
- **Observable:** objective task success rate (debugging fixes / planning
  success) - **not** search-steps-to-convergence or compression ratio.
- **Control:** identical task, neutral (unframed) prompt. The control is
  the unframed prompt, not dense-embedding cosine search. The task set
  must not depend on the 32 authored soul concepts (that reintroduces the
  designer-injection confound).
- **Kill:** no significant task-outcome difference, or schemas must be
  re-authored per task (circularity).

No implementation exists. Do not invent one. Building EXP-2 requires a
preregistration, a registry entry update, and ScientificAuditor sign-off.

## 5. EXP-0 - Paraphrase Invariance of Soul Concept Detection (audit)

EXP-0 is an **audit/falsification** experiment consistent with Program D's
"audit-and-falsification protocol over inherited Programs A/B/C". It is
**not** in `experiment_registry.yaml` (which lists only E0, R1, R3F,
EXP-1, EXP-2, EXP-3, EXP-4).

- **Location:** `experiments/EXP0/` (`run_exp0.py`, `dataset.py`,
  `detectors.py`, `analysis.py`, `leakage_check.py`, `paraphrases.json`,
  plus preregistration, protocol, runbook, statistical-analysis,
  implementation-plan, and directory-structure docs).
- **Research question:** does the Soul Graph's concept-detection cascade
  (`backend/pipeline/soul_router.py` Tiers 1-2; `backend/app/pipeline.py`
  Tier 3) depend on the literal presence of a seeded concept keyword,
  such that detection collapses when the keyword is removed but meaning
  is preserved?
- **Hypothesis:** for at least one detector tier, paraphrased hit rate is
  significantly lower than original hit rate. **Null:** McNemar exact
  test, two-sided, `p > alpha`.
- **DVs:** DV-1 Tier 2 (`soul_lookup_legacy`, lexical), DV-2 Tier 1
  (`soul_lookup`, semantic), DV-3 Tier 3 (full pipeline, secondary). All
  read from structured fields, never free-text or an LLM judge (F3 guard).
- **Dataset:** `paraphrases.json` (32 items) cross-validated against
  `backend/soul/concepts.json` (the 32 seeded soul concepts). N = 32
  concepts x 2 conditions = 64 queries per tier.
- **Success criterion:** McNemar `p <= 0.01` (Holm-Bonferroni across the
  two primary tiers) **and** observed hit-rate drop `>= 0.40`.
- **Seeds:** trial-order shuffle seed 1 (default); bootstrap CI seed 0
  (fixed, not CLI-configurable).
- **Integrity controls:** `dataset.py` refuses to run if
  `concepts.json`/`paraphrases.json` changed since preregistration
  (content-hash freeze); `run_exp0.py` calls `leakage_check.py` before
  scoring and aborts on failure; per-trial state reset
  (`scripts/wipe_db.py`) before every Tier 1/3 trial; interleaved trial
  order.
- **Run:** `python run_exp0.py --tier 1 2` (primary), `--tier 1 2 3`
  (add exploratory), `--dry-run` (validate, call nothing). Writes seven
  artifacts to a fresh immutable run directory.

**Canonical caveat.** EXP-0 probes the Soul Graph and the 32 authored soul
concepts, which PROGRAM_D_CANONICAL.md Section 5 marks `[REJECTED]` as
designer artifacts. EXP-0 is therefore an audit of a rejected mechanism's
failure mode (a falsification exercise), not a test of canonical science.
It does not use `core/` primitives. Treat its results as evidence about
the legacy system, not as support for any live hypothesis.

## 6. Experiment infrastructure

- `experiments/runner.py` - single entry point:
  `python -m experiments.runner <experiment_id> [--config <path>] [--seed <n>]`.
  Loads `experiment_registry.yaml` and `parameter_registry.yaml`, resolves
  the experiment directory, and writes artifacts to
  `artifacts/experiments/<id>/run_<UTC-timestamp>/`.
- `experiments/metrics.py`, `experiments/calculator.py`,
  `experiments/artifacts.py` - shared experiment support.
- `experiment_registry.yaml` - the registry of record (statuses,
  hypotheses, locations, components).
- `parameter_registry.yaml` - frozen parameters with value, location, and
  role.
- `reproducibility.yaml` - the reproducibility protocol
  (Section 8).

## 7. Preregistration documents (protected)

Never modify without explicit instruction and ScientificAuditor approval:

- `PROGRAM_D_CANONICAL.md` - single source of truth.
- `HYPOTHESIS_REGISTER.md` - H*, H1, H2, H3 (rejected).
- `EXP1_PREREGISTRATION.md` - the H1 calibration gate.
- `experiments/EXP0/EXP0_PREREGISTRATION.md` (+ `EXP0_PROTOCOL.md`,
  `EXP0_RUNBOOK.md`, `EXP0_STATISTICAL_ANALYSIS.md`,
  `EXP0_IMPLEMENTATION_PLAN.md`, `EXP0_DIRECTORY_STRUCTURE.md`).
- `F_A_TRIGGER_FIX_PREREGISTRATION.md` - the MDL trigger dimensional fix.
- `SPRINT_1.3_PREREGISTRATION.md`.

## 8. Frozen parameters and constants

From `parameter_registry.yaml` and the canon. These are not tunable.

- **MDL:** `b = BITS_PER_PARAMETER = 1.0` (scientific constant,
  `core/mdl/mdl_growth.py`); `lambda_model = k*b + n*log2(N)` (derived,
  not configurable); F-A corrected marginal cost `lambda = b + log2(N)`.
- **Emergence:** `M = NMI(learned, true) - NMI(learned, shuffled)`; E0
  margin `0.05` above the shuffled null
  (`experiments/E0/decision.py`, `M_STATISTIC_MARGIN`).
- **EXP-1:** `ECE < 0.10` pass gate; four locked tiers with locked numeric
  confidences (0.125/0.375/0.625/0.875); 4 equal-width bins;
  `ece_kill_threshold_gte 0.1`; `independence_test_alpha 0.05`;
  `hard_hallucination_honesty_failures_tolerated 0`.
- **E0 config:** see Section 2. Seed 42; `env_seed 101`; `num_seeds 5`
  (>= 5 per canonical kill criterion).
- **EXP-0:** McNemar `p <= 0.01` with Holm-Bonferroni; hit-rate drop
  `>= 0.40`; shuffle seed 1; bootstrap CI seed 0.

## 9. Reproducibility protocol

From `reproducibility.yaml`, per experiment:

1. `git checkout <experiment-commit>`.
2. `pip install -r requirements.txt`.
3. `cp infra/config/<experiment-config>.json infra/config/active.json`.
4. `python experiments/<EXPERIMENT>/run.py`.
5. `python experiments/<EXPERIMENT>/analysis.py`.

E0 entry: `experiments/E0/run.py`, config `baseline.json`, output
`artifacts/experiments/E0/`, seed 42. Known non-reproducibility factors:
LLM API responses vary by model version and temperature (pin model in
config); soul-graph Hebbian updates depend on query order (deterministic
in replay); web search results depend on external API availability (mock
for unit tests). Verification gate: `pytest tests/ -m "not slow"`,
`python benchmark.py`, regression gate `validation/regression.py`, 100%
pass on the pinned commit.

## 10. What is not present

- `experiments/EXP2/`, `experiments/R1/`, `experiments/R3F/`,
  `experiments/EXP3/`, `experiments/EXP4/` contain only `__init__.py`.
  EXP-2 is planned but unimplemented; R1/R3F are archived; EXP-3/EXP-4
  are `[REJECTED]`.
- There is no experiment that validates the backend ontology, identity,
  telemetry, or replay subsystems. Per canon rule 2, none is required for
  the canonical science.
- EXP-0 is not registered in `experiment_registry.yaml`; it is a
  standalone audit experiment.