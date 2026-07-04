# Git Diff Summary — Sprint 1.1 Remediation

## Files Modified

### `experiments/E0/run.py`
- **F1**: Replaced `predictive_log_likelihood(probs, latent)` with `predictor.log_predictive_probability(obs_list, context)` at all 4 scoring sites (T, C1, C2, C3 condition runners)
- **W1**: Replaced `hash()` with `hashlib.sha256` in `SeedRegistry.agent_seed()` and condition RNG
- **W2**: Removed `_hypothetical_entropy_after_growth()` standalone function (duplicate of `predictor.hypothetical_entropy_after_growth()`)
- **W4**: Removed dead imports: `ArtifactStore`, `compute_held_out_log_likelihood`, `predictive_log_likelihood`, `scoring_loss`, `compute_lambda_model`, `mdl_gain`, `compute_nmi`
- **W4**: Removed unused `SeedRegistry.analysis_seed()` and `SeedRegistry.to_dict()` methods
- **Held-out**: Added `_evaluate_held_out()` helper, `test_steps` parameter to all condition runners, independent held-out evaluation after training
- Added `hashlib` to top-level imports

### `experiments/E0/analysis.py`
- **W4**: Removed dead imports: `sklearn.metrics.cluster.normalized_mutual_info_score`, `predictive_log_likelihood`, `scoring_loss`
- **Held-out**: Updated `analyze_conditions` to use `test_log_likelihoods` from condition results; added `held_out_type` and `n_test_steps` fields

### `experiments/E0/decision.py`
- **FWER**: Added `holm_bonferroni()` function, `_FWER_ALPHA` constant
- **M threshold**: Added `derive_m_margin()` function, `MIN_M_MARGIN` constant
- **Held-out**: Updated `_extract_mean_ll` to prefer `test_log_likelihoods`
- Updated `_evaluate_dv_a` to apply Holm-Bonferroni correction
- Updated `_evaluate_dv_b` to accept optional `margin` parameter
- Updated `evaluate_multi_seed` to derive M margin from per-seed data

### `core/predictors/dirichlet_markov.py`
- **Bugfix**: Fixed `_compute_stationary` fallback to use `trans_probs.shape[0]` instead of `self._k` (IndexError when computing hypothetical entropy for (k+1) matrices)

### `experiments/E0/dataset.py`
- Exposed `_transition_alpha` as stored attribute for held-out environment creation

## Sprint 1.1.1 — C2 Data Leakage Fix (Post-Audit)

### `experiments/E0/run.py`
- **C2 fix**: Added `test_steps=config.get("num_test_steps", 2000)` to `apply_growth_at_random_times` call in `run_single_seed` (was silently defaulting to 0)
- **C2 fix**: Added `test_steps=test_steps` to `run_fixed_capacity` fallback call in `apply_growth_at_random_times` when `growth_count <= 0`

### `experiments/E0/growth_diagnostics.py`
- **New file**: Script to extract per-step MDL check data from experiment results and format as diagnostic table (seed | step | H_before | H_after | G | lambda_model | Decision | Margin)

## Test Results
- **100 passed, 1 skipped, 3 warnings**
- Core canonical tests: 28 passed
- E0 unit tests: 56 passed
- E0 integration tests: 16 passed

## Production Run (Original)
- **5 seeds, 27.5s**, Verdict: **FAIL (DV-a)** — treatment did not beat both controls at Holm-Bonferroni-corrected p<0.01

## Production Run (Corrected — C2 Fix Applied)
- **5 seeds, 34.4s**, Verdict: **FAIL (DV-a)** — identical to original (T==C1==C2, δ=0, zero variance)
- **C2 verification**: test_n=1999 matches T for all seeds ✅
- **Growth diagnostics**: 90 MDL checks, 0 growth events, mean margin = −26.25
- **Effect size**: exactly zero — power analysis not applicable
