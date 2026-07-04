# Sprint 1.1.1 — Final Reconciliation Report

## Overview

Reconciliation of Sprint 1.1 following an independent GLM 5.2 audit. Four priorities: artifact provenance (P0), C2 data leakage fix (P1), growth diagnostics (P2), corrected re-run (P3), and conditional power analysis (P4).

## P0 — Artifact Provenance (Answered)

1. **Commit hash:** `57516757451518c823bf594a20e6c68119829055` (Phase 62.4)
2. **Timing:** Made BEFORE Sprint 1.1 remediation began (July 3, 2026)
3. **Pre-existing vs new:** The committed version of `experiments/E0/run.py` is the old `math.sin` stub. The F1 fix (`predictor.log_predictive_probability` replacing `predictive_log_likelihood(probs, latent)`) was **not** pre-existing — it was written from scratch as part of Sprint 1.1. The GLM 5.2 audit found the F1 fix present because Sprint 1.1 had already applied it to the working tree before the audit.

## P1 — C2 Data Leakage (Fixed)

**Bug:** `apply_growth_at_random_times` called `run_fixed_capacity` without `test_steps` when `growth_count <= 0`, and `run_single_seed` did not pass `test_steps` to `apply_growth_at_random_times`. This caused C2 to evaluate on `last_20%_train` instead of the independent held-out test sequence.

**Fix:** Two one-line changes in `experiments/E0/run.py`:
1. Line ~618: Added `test_steps=config.get("num_test_steps", 2000)` to the `apply_growth_at_random_times` call in `run_single_seed`
2. Line ~359: Added `test_steps=test_steps` to the `run_fixed_capacity` fallback call

**Verification:** Post-fix, C2 has `test_n=1999` matching T for all seeds.

## P2 — Growth Diagnostics (Generated)

Created `experiments/E0/growth_diagnostics.py` to extract per-step MDL check data. Diagnostics run on the corrected experiment:

| Metric | Value |
|--------|-------|
| Total MDL checks | 90 (18 per seed × 5 seeds) |
| Growth events | 0 |
| Max margin (G − λ_model) | −21.95 |
| Mean margin | −26.25 |

**Diagnosis:** Growth never fired. The MDL criterion consistently rejected growth at every check point because the entropy reduction from adding a state never covered the model complexity cost.

## P3 — Corrected Re-run (Completed)

5-seed production run (base_seed=42, 34.4s):

| Seed | T LL | C1 LL | C2 LL | C3 LL | Growth |
|------|------|-------|-------|-------|--------|
| 42 | −0.9272 | −0.9272 | −0.9272 | −0.7619 | 0 |
| 43 | −0.6937 | −0.6937 | −0.6937 | −0.6914 | 0 |
| 44 | −0.7297 | −0.7297 | −0.7297 | −0.6957 | 0 |
| 45 | −0.6722 | −0.6722 | −0.6722 | −0.6697 | 0 |
| 46 | −0.7318 | −0.7318 | −0.7318 | −0.7373 | 0 |

**DV-a:** FAIL — T did not beat BOTH C1 and C2 (all identical, δ=0, zero variance)
**DV-b:** PASS — M=0.301 > margin=0.051
**Floor hit rate:** 0%

The FAIL verdict is **unchanged and robust** to the C2 fix.

## P4 — Power Analysis (Conditional — Not Applicable)

**Effect size is exactly zero; no seed count improves detection of a null effect. Power analysis is not applicable here.**

**Explanation:** Growth never fired across any of the 5 seeds. Since the MDL trigger never found a positive gain, the treatment condition (T) produced an identical model to the fixed-capacity control (C1) and the decoupled control (C2) — all ended with capacity=2, no growth events. The mean held-out log-likelihoods are identical within each seed, giving a Cohen's d of exactly 0 with zero variance. Power analysis computes the sample size needed to detect a specified effect size; when the observed effect is exactly zero, no amount of additional seeds will make it non-zero. The question is not statistical power but whether the MDL trigger can ever fire on this environment class — and the evidence from 90 independent MDL checks across 5 seeds consistently shows it cannot.

## C2 Fix Impact

The C2 data leakage fix **does not change the FAIL verdict**. Before the fix, C2 evaluated on last_20%_train (≈2000 steps). After the fix, C2 evaluates on the independent 1999-step test sequence. Since T and C2 produced identical models (both had 0 growth), the held-out LLs are identical regardless of which held-out set is used.

## Summary

| Metric | Value |
|--------|-------|
| Verdict | FAIL (DV-a) |
| DV-a pass | No |
| DV-b pass | Yes |
| Growth events | 0 |
| C2 fix | ✅ Verified (test_n=1999) |
| Effect size | Zero |
| Power analysis | Not applicable |

**Awaiting Integration Review #002.**
