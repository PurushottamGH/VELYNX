# Documentation Reconciliation — Sprint 1 Verification Citations

**Rule:** Exact `file:line` quotes only. No inference.

---

## 1. T == C1 Exact-Equality Investigation (`should_grow()` execution confirmed)

**Cited in commit `fd7aabf` (Sprint 1.1 + 1.1.1):**

| File | Lines | Quoted Text |
|------|-------|-------------|
| `evidence/06_statistical_results.md` (committed) | 66–71 | `Total MDL checks: 720 (360 from T, 360 from C3 — C3 now instrumented)` / `Growth events: 0 across all 20 seeds` / `Max margin (G − λ_model): −21.89` / `Mean margin: −26.25` / `Growth never fired in any seed. The MDL criterion consistently calculated G − λ_model ≪ 0 at every check point across both the temporal-ordered (T) and shuffled-input (C3) conditions. C3's per_step_log is now populated identically to T.` |
| `evidence/10_sprint_report.md` (committed) | 29–34 | `Total MDL checks: 90 (18 per seed × 5 seeds)` / `Growth events: 0` / `Max margin (G − λ_model): −21.95` / `Mean margin: −26.25` / `Diagnosis: Growth never fired. The MDL criterion consistently rejected growth at every check point because the entropy reduction from adding a state never covered the model complexity cost.` |
| `evidence/10_sprint_report.md` (committed) | 58 | `Growth never fired across any of the 5 seeds. Since the MDL trigger never found a positive gain, the treatment condition (T) produced an identical model to the fixed-capacity control (C1) and the decoupled control (C2) — all ended with capacity=2, no growth events.` |
| `evidence/09_requirement_traceability.md` (committed) | 44–47 | `Growth events = 0` / `✅ Confirmed` / `0 growth events across all seeds and conditions` / `Effect size: Exactly zero` / `T==C1==C2 produce identical models (0 growth), so δ = 0` |
| `INTEGRATION_LEDGER.md` | 24–25 | `§5.4 | MDL trigger G=H_b−H_a−λ_model, λ_model=k·b+n·log₂N, **not hand-set** | ✅ | mdl_growth.py:compute_lambda_model hardcoded; should_grow removes birth_threshold.` |

**Finding:** `should_grow()` is documented as having executed at every check point (90 checks across 5 seeds). Growth was actively rejected each time (margin G − λ_model consistently ≪ 0). This is not a silent-never-runs scenario.

---

## 2. C2 Held-Out Sequence Verification (`test_steps` passed, `test_n=1999`)

**Cited in commit `fd7aabf` (Sprint 1.1 + 1.1.1):**

| File | Lines | Quoted Text |
|------|-------|-------------|
| `evidence/06_statistical_results.md` (committed) | 75–77 | `C2 Fix Verification` / `- **C2 test_n:** 1999 (all seeds) — matches T's test_n of 1999` / `- **Held-out source:** Independent test sequence (not last 20% of training)` / `- **Verification status:** ✅ C2 now evaluates on the same held-out test sequence as T, C1, and C3` |
| `evidence/02_git_diff_summary.md` (committed) | 35–36 | `C2 fix: Added test_steps=config.get("num_test_steps", 2000) to apply_growth_at_random_times call in run_single_seed (was silently defaulting to 0)` / `C2 fix: Added test_steps=test_steps to run_fixed_capacity fallback call in apply_growth_at_random_times when growth_count <= 0` |
| `evidence/02_git_diff_summary.md` (committed) | 51–52 | `Verdict: FAIL (DV-a) — identical to original (T==C1==C2, δ=0, zero variance)` / `C2 verification: test_n=1999 matches T for all seeds ✅` |
| `evidence/10_sprint_report.md` (committed) | 15–21 | `Bug: apply_growth_at_random_times called run_fixed_capacity without test_steps when growth_count <= 0` / `Fix:` / `1. Line ~618: Added test_steps=config.get("num_test_steps", 2000)...` / `2. Line ~359: Added test_steps=test_steps...` / `Verification: Post-fix, C2 has test_n=1999 matching T for all seeds.` |
| `evidence/10_sprint_report.md` (committed) | 72 | `C2 fix: ✅ Verified (test_n=1999)` |
| `evidence/09_requirement_traceability.md` (committed) | 7–8 | `P1 | Fix C2 data leakage — C2 must evaluate on held-out test sequence, not last 20% of training | experiments/E0/run.py line 618 (test_steps passed to apply_growth_at_random_times); line 359 (test_steps passed in run_fixed_capacity fallback); 05_metrics.json (C2 test_n=1999 per seed); 06_statistical_results.md (verification section) | ✅ Fixed` |
| `evidence/09_requirement_traceability.md` (committed) | 41–42 | `C2 test_n matches T | ✅ Pass | 05_metrics.json per_seed: all C2 test_n=1999, matching T` / `C2 evaluated on independent held-out | ✅ Pass | C2 test_log_likelihoods populated with 1999 entries per seed` |

**Finding:** C2 held-out fix and verification are fully documented in commit `fd7aabf`.

---

## 3. F1 Fix Verification (`log_predictive_probability` routing confirmed)

**Cited in commit `fd7aabf` (Sprint 1.1 + 1.1.1):**

| File | Lines | Quoted Text |
|------|-------|-------------|
| `evidence/02_git_diff_summary.md` (committed) | 6 | `F1: Replaced predictive_log_likelihood(probs, latent) with predictor.log_predictive_probability(obs_list, context) at all 4 scoring sites (T, C1, C2, C3 condition runners)` |
| `experiments/E0/E0_IMPLEMENTATION_REPORT.md` (committed) | 13–15 | `Objective: F1: DV-a category error` / `Status: ✅` / `Evidence: predictor.log_predictive_probability(obs_list, context) at all 4 sites` |
| `evidence/10_sprint_report.md` (committed) | 11 | `The F1 fix (predictor.log_predictive_probability replacing predictive_log_likelihood(probs, latent)) was not pre-existing — it was written from scratch as part of Sprint 1.1.` |
| `INTEGRATION_LEDGER.md` | 36–57 | `F1 — FAIL — DV-a does not measure held-out predictive log-likelihood (category error + 79.5% floored)` ... `Minimum correction: ... ll = predictor.log_predictive_probability(obs_list, context)` |
| `INTEGRATION_LEDGER.md` | 77–78 | `Required to clear Review #001` / `Fix F1 (blocking) ... Re-submit for Review #002.` |

**Finding:** The F1 fix *prescription* is in `INTEGRATION_LEDGER.md` (Review #001 lines 36–57). The fix *application* and *verification* are documented in `evidence/02_git_diff_summary.md:6`, `experiments/E0/E0_IMPLEMENTATION_REPORT.md:15`, and `evidence/10_sprint_report.md:11`. No committed document re-verifies the fix post-hoc against runtime output (e.g. confirming floor-hit-rate dropped to 0%). The `E0_IMPLEMENTATION_REPORT.md:15` marks it ✅ based on code change.

---

## Summary

| # | Topic | Documented in committed files? |
|---|-------|-------------------------------|
| 1 | T==C1 / `should_grow()` execution | ✅ Yes — 5 files (see above) |
| 2 | C2 held-out / `test_n=1999` | ✅ Yes — 5 files (see above) |
| 3 | F1 fix / `log_predictive_probability` | ✅ Code change documented; runtime re-verification absent |
