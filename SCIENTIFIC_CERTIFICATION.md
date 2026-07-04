# SCIENTIFIC_CERTIFICATION

**Auditor:** Scientific Validation Lead, Program D
**Date:** 2026-07-04
**Subject:** Sprint 1 Deliverables — Scientific Audit
**Reference:** `PROGRAM_D_CANONICAL.md` (frozen)

---

## Verdict: **WARNING**

Sprint 1 successfully delivers a **canon-exact E0 implementation** with verified mathematics, correct null-referenced M, non-speculative MDL growth, and all regression tests passing. The scientific core is sound.

However, the audit finds **structural gaps that block full PASS**:
- **EXP-0** is implemented but **has never been run** against the legacy deployed system (no artifact exists).
- **EXP-1** (H1/Program A calibration gate) and **EXP-2** (H2/affective indexing) are **not implemented** — only E0 is.
- Only **E0** has been executed; the other three pre-registered experiments (EXP-0, EXP-1, EXP-2) are unrun.
- The 100/100 tests are scoped to the **E0/core path only** and do not cover EXP-0, EXP-1, or EXP-2 implementations.
- The existing `EXPERIMENT_CERTIFICATION.md` from the prior pass still marks EXP-1 and EXP-2 as "Blocked" and E0 as "Scientifically invalid" — that file is now stale (E0 is now valid; EXP-1/2 still not built).
- The prior audit's R-1 (core cognitive claim null) is **not falsified by E0**: E0 is the keystone gate, not a refutation of R1.

---

## 1. Scientific correctness

### 1.1 Keystone assumption I2 — null-referenced M
**Status: CORRECT**

`core/emergence/emergence_statistic.py:11-51` implements NMI using the standard symmetric normalization `2·I(X;Y)/(H(X)+H(Y))`. The `compute_emergence_statistic` function in `experiments/E0/analysis.py:87-169` correctly constructs `M = NMI(learned, true) − NMI(learned, shuffled)` so that `E[M|H₀] = 0` by construction. The shuffled baseline is taken from C3 (the shuffled-input control) — the correct null reference per canon §5.5.

**Evidence:**
- `experiments/E0/analysis.py:147-157` — `shuffled_latents = conditions["C3"].get("latent_states", [])`
- `tests/unit/test_core_canonical.py:160-175` — `test_nmi_zero_for_independent_partitions` passes; `test_null_referenced_centering` passes with |M| < 0.3 for random data.
- The graph-isomorphism form is **not present** in `core/` (matches canon §10 Issue-2 fix).

### 1.2 E ≠ λH+μS+νA
**Status: CORRECT (in core/)**

`core/measurement/proper_scoring.py:75-107` implements `predictive_log_likelihood = log P_θ(x_{t+1}|x_≤t)` with eps-clipped probs. This is the canonical log score, replacing the rejected `E` proxy.

**Evidence:** `core/measurement/proper_scoring.py:80-82` docstring explicitly cites Bernardo 1979 uniqueness and canon §5.3.

**Caveat:** The `E` proxy may persist in `backend/` legacy code (not audited in this sprint). The sprint scope (`core/` + `experiments/E0/`) is clean.

### 1.3 Three foundational assumptions I1, I2, I3
- **I1** (prediction-error as sufficient signal): not directly tested by E0; the predictor class is implemented and the proper-scoring loss wires prediction error into the MDL gain — consistent.
- **I2** (emergence distinguishable from injection): **operationalized** by the null-referenced M. First-ever test wired to this gate. This is the keystone fix.
- **I3** (nonlinear learnable environment): **verified offline** by `experiments/E0/leakage_check.py:23-98` using a linear logistic-regression probe. `test_environment_nonlinearity_check` and `test_nonlinearity_certificate_generation` pass.

### 1.4 Latent-state ground truth integrity
**Status: CORRECT (regression-tested)**

The `test_true_latents_come_from_env_not_predictor` and `test_analyze_conditions_rejects_missing_true_latents` tests guarantee that `M` is computed against **environment ground truth**, not predictor-derived states. This is the latent-leakage fix described in the DeepSeek report. `analyze_conditions` raises `KeyError` if `true_latent_states` is missing for T — a hard guard.

### 1.5 Growth ordering — no speculative growth
**Status: CORRECT (regression-tested)**

`experiments/E0/run.py:230-273` computes the hypothetical entropy **before** calling `predictor.grow()`. `tests/unit/test_e0_components.py:896-961` verify that every recorded `grew=True` event has `gain > 0`, that no growth occurs when gain ≤ 0, and that `_hypothetical_entropy_after_growth` does not mutate the predictor's capacity. The growth-ordering fix is verified.

### 1.6 Capacity-matched C2
**Status: CORRECT (regression-tested)**

`run_single_seed` in `experiments/E0/run.py:549-588` runs T first to get `t_growth_count`, then passes it to `apply_growth_at_random_times` for C2. `test_c2_has_same_growth_count_as_t`, `test_c2_has_same_final_capacity_as_t`, and `test_c2_growth_timing_is_random` all pass. C2 is genuinely decoupled from prediction error.

---

## 2. Mathematical correctness

### 2.1 λ_model = k·b + n·log₂N
**Status: CORRECT**

`core/mdl/mdl_growth.py:35-76` implements the exact formula `λ_model = k·b + n·log₂N`. Tested against 5 reference triples in `test_lambda_formula_matches_canonical` with `rel=1e-9` tolerance. The formula is **not** exposed as configurable — the only adjustable parameter is `b` (default 1.0), which is documented as a scientific constant.

**Critique:** The derivation in `literature/program_d_mathematical_provenance.md §2` is cited but not included in this audit. The `b=1.0` choice (bits per parameter) is **not derived from the ledger**; it is a unit choice. This is a minor concern — the formula is correct, but `b` is a unit constant, not a fitted parameter. The canon §5.4 pins the full formula including `b`; the implementation matches.

### 2.2 G = H_before − H_after − λ_model
**Status: CORRECT**

`core/mdl/mdl_growth.py:82-109` implements `mdl_gain(entropy_before, entropy_after, lambda_model) = entropy_before - entropy_after - lambda_model`. `should_grow` returns `(gain > 0, gain, lam)`. `test_mdl_gain_formula` and `test_mdl_gain_negative` pass.

### 2.3 Proper scoring log loss
**Status: CORRECT**

`predictive_log_likelihood` uses `max(min(p, 1-eps), eps)` clipping to prevent log(0). Tested against perfect prediction, uniform distribution, and out-of-range indices. `test_log_score_matches_reference` passes with `abs=1e-9`.

### 2.4 NMI computation
**Status: CORRECT (with one implementation note)**

`compute_nmi` uses `n * n_tp / (n_t * n_p) + 1e-15` inside the log to avoid log(0). Tested for perfect alignment (≈ 1.0), independence (< 0.3), zero entropy (0.0), and empty input. Passes all five emergence tests.

**Implementation note:** The canonical NMI formula is `2·I(X;Y)/(H(X)+H(Y))` (Strehl & Ghosh 2002 normalization). The implementation matches. The `+1e-15` epsilon inside the mutual-information log is a numerical guard, not a methodological deviation.

### 2.5 Stationary distribution & entropy
**Status: CORRECT (with a robustness note)**

`DirichletMarkovPredictor.entropy()` and `_hypothetical_entropy_after_growth` compute the stationary distribution via eigendecomposition of the transposed transition matrix, with a uniform fallback on `LinAlgError` or NaN. The fallback is acceptable for numerical robustness but means the entropy can silently fall back to a uniform-distribution value (max entropy). This is **not** a defect in E0's small-config tests but is worth noting for larger environments.

### 2.6 Statistical tests
**Status: CORRECT**

`paired_one_sided_ttest` uses `scipy.stats.ttest_rel` and converts to a one-sided p-value via `p/2 if mean_diff > 0 else 1 - p/2`. The `bootstrap_significance` uses pooled-resampling permutation with `(count+1)/(n+1)` as the p-value (avoids zero). Both match standard references (Efron & Tibshirani 1993; doc/scipy.stats.ttest_rel).

**Caveat:** With n=5 seeds and 1e-4 noise, the t-test may be underpowered. The canon §6 requires p<0.01 across ≥5 seeds; the implementation supports this but does not guarantee it will be reached.

---

## 3. Statistical correctness

### 3.1 Held-out log-likelihood split
**Status: MINOR CONCERN**

`compute_held_out_log_likelihood` in `experiments/E0/analysis.py:25-81` uses the last 20% of the training sequence as a held-out set when no explicit test data is provided. The same split is used in the `E0Decider._extract_mean_ll` method (`decision.py:368-371`).

**Concern:** When `num_test_steps=2000` is set in the config but never used (the runner generates its own train sequence and the held-out is the last 20% of train), the explicit test split is silently ignored. This is a **methodological shortcut** — the held-out is from the same trajectory, not a fresh environment instance. The dataset's `generate_train_test_sequences` method is implemented but **not called** by the runners. This is a WARNING, not a FAIL, but should be addressed before publication.

### 3.2 McNemar test in EXP-0
**Status: CORRECT**

`experiments/EXP0/analysis.py:41-61` implements the exact two-sided McNemar test via the binomial distribution on discordant pairs. No continuity correction. Tested for n=32 paired items.

### 3.3 Holm-Bonferroni correction
**Status: CORRECT**

`experiments/EXP0/analysis.py:90-104` implements the step-down Holm-Bonferroni procedure. Step-down: once a test fails, all remaining are marked non-significant.

### 3.4 Bootstrap CI in EXP-0
**Status: CORRECT**

`experiments/EXP0/analysis.py:64-87` implements paired-resample bootstrap (resamples item indices with replacement) for the hit-rate difference. Uses `random.Random(seed)` for determinism.

### 3.5 Multi-seed aggregation
**Status: CORRECT**

`E0Decider.evaluate_multi_seed` collects per-seed mean LLs for T, C1, C2 and per-seed M for T, then runs paired t-tests across seeds for DV-a and mean-M for DV-b. Insufficient seeds (< min_seeds=5) triggers INCONCLUSIVE.

### 3.6 Sufficient seeds for canon compliance
**Status: WARNING**

`DEFAULT_CONFIG["num_seeds"] = 5` matches the canon §7 minimum. The integration test runs `num_seeds=3` in its test config (smaller for CI speed). The sprint's 100 tests are mostly unit/component tests at small scale; the **full 5-seed end-to-end run has not been executed in this sprint** (no `aggregated_results.json` artifact exists).

---

## 4. Reproducibility

### 4.1 Seed management
**Status: CORRECT**

`SeedRegistry` in `experiments/E0/run.py:88-116` separates env seeds from agent seeds. `test_seeded_reproducibility` in the integration test (`tests/integration/test_e0_pipeline.py:259-273`) verifies identical seeds produce identical log-likelihood sequences.

### 4.2 Frozen config
**Status: PARTIAL**

`DEFAULT_CONFIG` is hardcoded in `experiments/E0/run.py:56-80`. The config is not externally frozen (no hash), but it is centralized.

### 4.3 Artifact immutability
**Status: CORRECT**

`run.py:77-84` allocates a timestamped run directory and refuses to overwrite. The aggregated results are written to `aggregated_results.json`. The script never modifies `backend/soul/concepts.json` or any production source.

**Caveat:** The EXP-0 runner uses `scripts/wipe_db.py` for state reset, which is the **only DB-touching** reset path. EXP-0 has not been run, so this path is unverified in practice.

### 4.4 Environment determinism
**Status: CORRECT**

`test_environment_deterministic_with_seed` verifies same seed → same sequence. `test_environment_different_seeds_different` verifies different seeds → different sequences.

### 4.5 Predictor state roundtrip
**Status: CORRECT**

`test_predictor_state_dict_roundtrip` verifies that `state_dict` → `load_state_dict` preserves capacity and n_observations. However, the **transition counts are not asserted to be identical** in the test — only capacity and n_observations. A strict check would be stronger.

---

## 5. Kill criteria implementation

### 5.1 DV-a: T > C1 AND T > C2 at p<0.01 across ≥5 seeds
**Status: WIRED**

`E0Decider._evaluate_dv_a` runs paired t-tests against C1 and C2 separately. The decider requires `vs_c1["significant"] AND vs_c2["significant"]` for pass. With < 2 seeds, falls back to bootstrap. With < `min_seeds`, verdict is `INCONCLUSIVE`.

### 5.2 DV-b: M exceeds pre-registered margin
**Status: WIRED**

`M_STATISTIC_MARGIN = 0.05` is hardcoded. `_evaluate_dv_b` returns `pass = (m_statistic > m_margin)`. `test_decider_honors_m_static_margin` verifies the threshold behavior.

**Concern:** The margin of 0.05 is **arbitrary** — it is not derived from the null distribution's variance or a pre-registered effect size. A more defensible margin would be `mean(M_shuffled) + k·std(M_shuffled)` for some k. The current value is a reasonable default but is not data-derived.

### 5.3 Two-attempt falsification
**Status: WIRED**

`E0Decider.should_falsify` returns `(True, reason)` after two non-pass attempts. `test_e0_decider_falsification_two_attempts` and `test_kill_criteria_two_attempts` verify the protocol.

**Concern:** If either attempt is `INCONCLUSIVE` (insufficient seeds), `should_falsify` returns `(False, "Inconclusive due to insufficient seeds; retry")`. This means an inconclusive attempt does **not** count toward falsification. This is the right behavior but it means a "two honest attempts" can be 4 actual runs if the first two are inconclusive.

### 5.4 Kill criteria summary
All canonical H\* kill criteria are wired and regression-tested. The decider is **machine-checked** — pass/fail is computed from the artifacts, not by hand.

---

## 6. Experiment correctness

### 6.1 E0 (H\*) — IMPLEMENTED AND TESTED
**Status: VALID**

All four conditions (T, C1, C2, C3) are implemented in `experiments/E0/run.py` with regression tests for:
- Capacity-matched C2 (3 tests)
- Growth ordering (4 tests)
- Latent-state correctness (5 tests)
- Multi-seed runner (5 tests)
- Decision module (8 tests)
- Core canon-exactness (24 tests)
- Integration (15 tests)

The implementation matches canon §7 E0 specification. The environment is nonlinear (polynomial + sinusoidal + cross-terms in `dataset.py:205-244`). The offline linearity check passes.

**Gap:** The full 5-seed E0 run with the default config (10,000 train steps, 16-dim obs) has **not been executed**. The 100 tests run at much smaller scale. The full-decision verdict (PASS/FAIL on H\*) is not yet produced.

### 6.2 EXP-0 (paraphrase precondition) — IMPLEMENTED, NOT RUN
**Status: READY BUT UNEXERCISED**

`experiments/EXP0/` has a complete harness:
- `dataset.py` — 32 paired items, SHA-256 integrity check against `concepts.json`
- `leakage_check.py` — substring + Porter-stem leakage validator (conservative)
- `detectors.py` — three tiers (V2 semantic, legacy lexical, full pipeline)
- `analysis.py` — McNemar exact test, bootstrap CI, Holm-Bonferroni
- `run_exp0.py` — main runner with state reset via `scripts/wipe_db.py`

**Critical observation:** The pre-registered `paraphrases.json` file is **not present** in the repository (I searched the `experiments/EXP0/` directory; no JSON file exists there beyond `__init__.py` and Python files). The runner will fail at `dataset.load_items()` with `FileNotFoundError`. EXP-0 is **not runnable** until the paraphrases dataset is committed.

**This blocks the immediate next action** specified in canon §11.

### 6.3 EXP-1 (H1 calibration) — NOT IMPLEMENTED
**Status: MISSING**

The `experiments/EXP1/` directory exists with only an `__init__.py`. There is no query set, no ECE harness, no reliability diagram generator, no BM25/TF-IDF baseline. The existing `EXPERIMENT_CERTIFICATION.md` from a prior pass confirms this: "Missing... Status: Blocked."

### 6.4 EXP-2 (H2 affective indexing) — NOT IMPLEMENTED
**Status: MISSING**

The `experiments/EXP2/` directory exists with only an `__init__.py`. There is no third-party task battery, no framed/unframed measurement, no objective task scorer. The existing `EXPERIMENT_CERTIFICATION.md` confirms: "Missing... Status: Blocked."

### 6.5 EXP-3, EXP-4 — correctly absent
**Status: COMPLIANT**

These are [REJECTED]/archived per canon §10 Issue-1. The `experiments/EXP3/` and `experiments/EXP4/` directories exist as empty `__init__.py` only. This is correct — they are not in the live program.

---

## 7. Publication readiness

### 7.1 Novelty verdict
**Status: NOT AUDITED IN THIS SPRINT**

The publication cluster (`GRANT_PACKAGE.md`, `RELATED_WORK.md`, `PUBLICATION_CHECKLIST.md`, `REVIEWER_OBJECTIONS.md`, `CONSTITUTION_COMPLIANCE.md`) is not addressed in this sprint. Per the DeepSeek report, these documents were not part of Sprint 1 scope.

### 7.2 Reproducibility bundle
**Status: NOT AUDITED**

No Dockerized run environment, no pinned dependency file in the canonical sense, no data management plan execution. This is M6 in the master roadmap, which is downstream of M2–M5.

### 7.3 E0 as a publication artifact
**Status: PROMISING BUT INCOMPLETE**

The E0 implementation is clean, well-tested, and produces JSON-serializable results. The analysis module generates a markdown report with `[FACT]` tags. The decision module emits machine-checked verdicts. However:
- No full 5-seed run artifact exists
- No publication-ready figures are generated
- The held-out split is not from a fresh environment instance (minor methodological concern)
- The nonlinearity certificate is generated but the environment may be too easy (K=3, D=4 in tests) to actually require growth

---

## 8. Summary of findings

| Area | Status | Evidence |
|---|---|---|
| λ_model derivation | PASS | `core/mdl/mdl_growth.py:35-76`; 5 unit tests |
| Log score | PASS | `core/measurement/proper_scoring.py:75-107`; 5 unit tests |
| Null-referenced M | PASS | `experiments/E0/analysis.py:87-169`; 6 unit tests |
| Non-speculative growth | PASS | `experiments/E0/run.py:230-273`; 4 regression tests |
| Capacity-matched C2 | PASS | `experiments/E0/run.py:549-588`; 3 regression tests |
| True-latent separation | PASS | `experiments/E0/analysis.py:219-225`; 5 regression tests |
| Environment nonlinearity | PASS | `experiments/E0/leakage_check.py`; 3 tests |
| Multi-seed runner | PASS | `experiments/E0/run.py:610-694`; 5 tests |
| Kill decision module | PASS | `experiments/E0/decision.py`; 8 tests |
| Banned symbols in core/ | SKIPPED | `test_no_banned_symbols_in_core` is `@pytest.mark.skip` |
| EXP-0 dataset present | **FAIL** | `paraphrases.json` not in repo |
| EXP-0 executed | **FAIL** | No artifact, never run |
| EXP-1 implemented | **FAIL** | Only `__init__.py` |
| EXP-2 implemented | **FAIL** | Only `__init__.py` |
| Full 5-seed E0 run | **FAIL** | No `aggregated_results.json` |
| Held-out from fresh env | WARNING | Uses last 20% of train, not fresh seq |
| M margin derivation | WARNING | 0.05 is hardcoded, not data-derived |
| Banned-symbols test | WARNING | Test exists but is skipped |

---

## 9. Recommendations (non-redesign)

1. **Commit `experiments/EXP0/paraphrases.json`** before claiming EXP-0 is ready.
2. **Execute EXP-0** to produce the paraphrase-collapse artifact (canon §11 immediate next action).
3. **Execute a full 5-seed E0 run** with the default config and publish the aggregated results to produce the H\* verdict.
4. **Implement EXP-1 and EXP-2** or explicitly defer them to subsequent sprints with a clear status update to the stale `EXPERIMENT_CERTIFICATION.md`.
5. **Un-skip `test_no_banned_symbols_in_core`** and run it in CI to catch regressions.
6. **Use a fresh environment instance for the held-out set** in E0 to strengthen the generalization claim.
7. **Derive the M margin from the null distribution** (e.g., `mean(M_shuffled) + 2·std(M_shuffled)`) rather than hardcoding 0.05.
8. **Update `EXPERIMENT_CERTIFICATION.md`** to reflect Sprint 1 status (E0 now valid; EXP-0 ready but unrun; EXP-1/2 still not built).

---

**Scientific Certification Verdict: WARNING**

The E0 keystone gate is implemented correctly and tested. The 100/100 unit and integration tests are genuine. But the sprint delivers **one of four pre-registered experiments** (E0 only), the EXP-0 dataset is missing from the repo, and no full end-to-end experimental result has been produced. This is a strong foundation but not a complete scientific deliverable.
