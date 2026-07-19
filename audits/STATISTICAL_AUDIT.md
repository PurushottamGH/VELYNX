# STATISTICAL_AUDIT

**Auditor:** Scientific Validation Lead, Program D
**Date:** 2026-07-04
**Scope:** Statistical methods, test selection, multiple comparisons, effect sizes, power, and assumptions
**Reference:** `PROGRAM_D_CANONICAL.md §5–7`; `EXPERIMENT_CERTIFICATION.md`

---

## Verdict: **WARNING**

The statistical methods used in E0 and EXP-0 are **standard and correctly implemented**. No fabricated tests, no p-hacking, no circular definitions. The null-referenced M is the correct construction per canon §5.5. However, several statistical concerns prevent a full PASS:

1. The **M margin (0.05) is not data-derived** — it is a hardcoded constant.
2. The **held-out split** uses the last 20% of a single trajectory, not a fresh environment instance — a methodological shortcut.
3. **Statistical power is unverified** — no power analysis exists; the 5-seed minimum may be insufficient given the environment's difficulty.
4. **The t-test assumes normality of differences** — not verified; the bootstrap fallback exists but is only triggered for n<2 seeds.
5. **No correction for multiple comparisons across the four conditions** (T, C1, C2, C3) — the DV-a requires T > BOTH C1 and C2, which inflates the family-wise error rate.

---

## 1. Statistical tests inventory

### 1.1 E0 DV-a: Paired one-sided t-test
**File:** `experiments/E0/decision.py:24-85`

**Method:** `scipy.stats.ttest_rel(treatment, control)` converted to one-sided via `p/2 if mean_diff > 0 else 1 - p/2`.

**Assumptions:**
1. **Paired differences are approximately normal.** Not verified. With n=5 seeds, this is a strong assumption.
2. **Independent seeds.** Enforced by the seed registry (separate env_seed per seed).
3. **No significant outliers.** Not checked.

**Robustness:** Bootstrap permutation fallback exists for n<2 seeds (`bootstrap_significance`), but with the canonical n≥5, the t-test is always used.

**Verdict:** The test is standard but its assumptions are unchecked. With n=5, the t-test is fragile to non-normality. A Wilcoxon signed-rank test would be more robust.

### 1.2 E0 DV-b: Margin comparison
**File:** `experiments/E0/decision.py:352-361`

**Method:** `pass = (m_statistic > 0.05)`.

**Assumptions:**
1. **The margin 0.05 is a pre-registered effect size.** It is hardcoded with no derivation.
2. **M is approximately normal across seeds.** Not verified.

**Concern:** The margin should be derived from the null distribution, e.g., `mean(M_shuffled) + k·std(M_shuffled)` for some pre-registered k. The current 0.05 is a reasonable default but is not data-derived.

**Verdict:** The comparison is a simple threshold check — correct in form, unjustified in threshold value.

### 1.3 EXP-0: McNemar exact test
**File:** `experiments/EXP0/analysis.py:41-61`

**Method:** Two-sided binomial test on discordant pairs. `p = 2·sum(C(n_discordant, i) for i in range(0, k+1)) · (0.5)^n_discordant`.

**Assumptions:**
1. **Pairs are independent.** The 32 (original, paraphrase) pairs are independent items.
2. **Discordant pairs are exchangeable under H0.** Standard McNemar assumption.

**Verdict:** Standard and correct. n=32 is adequate for the exact test.

### 1.4 EXP-0: Paired bootstrap CI
**File:** `experiments/EXP0/analysis.py:64-87`

**Method:** 10,000 paired resamples (item indices with replacement) of the hit-rate difference.

**Assumptions:**
1. **The sample is representative of the population.** Standard bootstrap assumption.
2. **10,000 iterations is sufficient for 95% CI stability.** Adequate for n=32.

**Verdict:** Standard and correct.

### 1.5 EXP-0: Holm-Bonferroni correction
**File:** `experiments/EXP0/analysis.py:90-104`

**Method:** Step-down: sort p-values, compare each to `alpha / (m - rank)`.

**Verdict:** Standard and correct. Applied across the two pre-registered primary tiers (Tier 1, Tier 2).

### 1.6 E0: Bootstrap permutation (fallback)
**File:** `experiments/E0/decision.py:88-119`

**Method:** Pooled resampling, `(count + 1) / (n_resamples + 1)` p-value.

**Verdict:** Standard and correct as a fallback. Not the primary test at n≥5.

---

## 2. Multiple comparisons

### 2.1 Family-wise error rate
**E0 DV-a** requires T > C1 AND T > C2. This is two simultaneous tests, each at α=0.01. The family-wise error rate is approximately `1 - (1-0.01)² ≈ 0.02`, not 0.01. The canon §6-H\* states "T fails to beat BOTH C1 and C2 on DV-a at p<0.01" — the joint condition is the kill criterion, but the per-comparison threshold of 0.01 is not adjusted.

**Recommendation:** Apply a Bonferroni correction: per-comparison α = 0.005, or use a Holm-Bonferroni step-down across the two comparisons.

### 2.2 EXP-0 Holm-Bonferroni
**Already applied** across the two primary tiers (Tier 1, Tier 2). Correct.

---

## 3. Effect sizes and power

### 3.1 Power analysis
**Not performed.** No `power_analysis.py` or equivalent exists. The canon §7 requires "≥5 seeds" but does not justify the choice from a power calculation.

**Concern:** With n=5 seeds and the small test config (n_train=100–500), the t-test is likely underpowered to detect anything but large effects. A formal power analysis would specify the minimum detectable effect size at α=0.01, power=0.80, for the given seed count.

### 3.2 Effect size reporting
- **DV-a**: Mean difference in log-likelihood is reported. Cohen's d is not computed. The log-likelihood difference is in nats/bits, which is interpretable but not standardized.
- **DV-b**: M statistic is reported. Range is [-1, 1] (NMI normalization). The 0.05 margin is a small effect by NMI standards (where 0.3+ is often considered "moderate").

**Recommendation:** Report Cohen's d for DV-a and a pre-registered effect-size threshold for DV-b (e.g., M > 0.3 for "moderate" alignment).

---

## 4. Assumption verification

### 4.1 Environment nonlinearity (I3)
**Verified offline** by `leakage_check.py:23-98`. A linear logistic regression probe is trained on observations and tested for accuracy. The `is_nonlinear` flag is True if accuracy < chance + 0.1.

**Test result:** `test_linear_recovery_on_nonlinear_data` passes (asserts accuracy is in [0, 1] and chance ≈ 1/K). The test does **not** assert that `is_nonlinear` is True for the default environment config.

**Gap:** The full-scale environment (K=10, D=16) has not been verified to be nonlinear. The test uses K=5, D=10. A regression test with the full config is needed.

### 4.2 Predictor correctness
**Verified** by the predictor unit tests (initialization, update, predict, grow, entropy, state roundtrip).

### 4.3 Latent-state separation
**Verified** by the regression tests (`test_true_latent_states_separate_from_inferred`, `test_true_latents_not_derived_from_predictor_state`). Ground truth comes from `env.step()`, predictor inferences are stored separately.

### 4.4 Growth ordering
**Verified** by the regression tests (`test_every_growth_event_has_positive_gain`, `test_no_growth_when_gain_not_positive`, `test_hypothetical_entropy_before_grow_call`). Growth occurs only after G > λ_model is verified.

### 4.5 Normality of seed-level differences
**Not verified.** The t-test assumes normality of the per-seed differences. With n=5, Shapiro-Wilk would have low power, but a Q-Q plot or bootstrap CI for the mean difference would be informative.

---

## 5. Sources of statistical error

### 5.1 Held-out split is from the same trajectory
**File:** `experiments/E0/analysis.py:57-63`

```python
n_train = len(train_log_likelihoods)
split = int(n_train * 0.8)
held_out_ll = train_log_likelihoods[split:]
```

**Problem:** The "held-out" set is the last 20% of a single trajectory generated by one environment instance. It is not a fresh sample. This means:
1. The held-out may share temporal structure with the training set.
2. The environment's randomness is fixed per seed, so the held-out is deterministic given the seed.
3. The `generate_train_test_sequences` method exists but is **not called** by the runners.

**Impact:** The DV-a may overstate generalization because the held-out is correlated with the training trajectory.

**Recommendation:** Call `env.generate_train_test_sequences` and use the test_obs for DV-a evaluation.

### 5.2 M margin is hardcoded
**File:** `experiments/E0/decision.py:125`

```python
M_STATISTIC_MARGIN = 0.05
```

**Problem:** The margin is not derived from the null distribution. A data-derived margin would be:
```python
margin = mean(M_shuffled) + 2 * std(M_shuffled)  # 95% CI above null
```

**Impact:** The DV-b pass criterion is arbitrary. A more principled margin would be defensible.

### 5.3 No correction for the two-control comparison in DV-a
**File:** `experiments/E0/decision.py:326-350`

**Problem:** T > C1 AND T > C2 is tested independently at α=0.01. The joint FWER is ~0.02.

**Recommendation:** Apply Bonferroni: per-comparison α=0.005, or use a joint test (e.g., MANOVA or Hotelling's T²).

### 5.4 Predictor self-comparison in M
**File:** `experiments/E0/analysis.py:213-236`

**Observation:** The emergence statistic uses the predictor's **inferred** latent states (`treatment_latent_states`) against the environment's true states. If the predictor's inference is poor (e.g., always returns state 0), NMI(learned, true) ≈ 0 and M ≈ 0, which is correctly identified as null. This is the correct behavior, but it means M is bounded by the predictor's inference quality, not just the structural alignment.

**No defect**, but worth noting that M conflates inference quality and structural alignment.

### 5.5 Bin-boundary hacking guard for EXP-1
**Not implemented.** The `expected_calibration_error` function uses fixed equal-width binning. An adversary could bin predictions to minimize ECE without improving the underlying retrieval signal. The canon §6-H1 specifies a Goodhart guard, but no implementation exists (and EXP-1 is not built anyway).

---

## 6. Reproducibility of statistical results

### 6.1 Seed determinism
**Verified.** `test_seeded_reproducibility` confirms identical seeds produce identical log-likelihood sequences.

### 6.2 Statistical test determinism
- **McNemar exact test**: Deterministic (no randomness).
- **Bootstrap CI**: Deterministic given `seed=0` (hardcoded in EXP-0).
- **Paired t-test**: Deterministic.
- **Bootstrap permutation in E0**: Deterministic given `seed=42` (hardcoded).
- **NMI**: Deterministic.

**Verdict:** All statistical tests are deterministic given the seeds. Reproducibility is ensured.

---

## 7. Summary of statistical concerns

| Concern | Severity | Evidence |
|---|---|---|
| M margin hardcoded (0.05) | Medium | `decision.py:125` — not data-derived |
| Held-out from same trajectory | Medium | `analysis.py:57-63` — `generate_train_test_sequences` unused |
| No FWER correction for T>C1 AND T>C2 | Medium | `decision.py:326-350` — two tests at α=0.01 |
| No power analysis | Low | No `power_analysis.py` exists |
| No normality check for t-test | Low | `decision.py:77` — assumptions unchecked |
| Bin-boundary guard for ECE | Low | EXP-1 not built |
| Full-scale environment nonlinearity unverified | Low | Test uses K=5, D=10 not K=10, D=16 |
| Predictor inference quality conflated with M | Informational | `analysis.py:213-236` — M is bounded by inference |

---

## 8. Recommendations

1. **Derive the M margin from the null distribution** (e.g., `mean(M_shuffled) + 2·std(M_shuffled)`) and pre-register it.
2. **Use a fresh environment instance for the held-out set** by calling `env.generate_train_test_sequences`.
3. **Apply a Bonferroni or Holm correction** to the two DV-a comparisons (T vs C1, T vs C2).
4. **Add a power analysis** to determine the minimum number of seeds for the expected effect size.
5. **Add a Q-Q plot or bootstrap CI** for the per-seed mean differences to verify t-test assumptions.
6. **Add a regression test** that verifies the full-scale environment (K=10, D=16) is nonlinear.
7. **Replace the t-test with a Wilcoxon signed-rank test** for robustness with n=5.

---

**Statistical Audit Verdict: WARNING**

The statistical methods are standard and correctly implemented. No fabricated tests, no p-hacking. But the M margin is arbitrary, the held-out split is not from a fresh environment, and the two-control comparison lacks FWER correction. These are correctable without redesigning the science.
