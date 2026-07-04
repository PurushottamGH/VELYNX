# Statistical Reporting Template — Program D Experiments

**Standard:** APA 7th / NeurIPS 2026 / ICML 2026 / Nature Portfolio
**Program:** D (E0, EXP-1, EXP-2, EXP-3)

---

## 1. Universal Reporting Fields (All Experiments)

### 1.1 Experiment Metadata
| Field | Value | Source |
|-------|-------|--------|
| Experiment ID | E0 / EXP-1 / EXP-2 / EXP-3 | `experiments/{ID}/protocol.md` |
| Hypothesis Tested | H* / H1 / H2 / H3 | `foundation/hypothesis/` |
| Preregistration URL | https://osf.io/XXXXX | OSF |
| Preregistration Date | YYYY-MM-DD | OSF |
| Code Commit Hash | `git rev-parse HEAD` | Repository |
| Data DOI | 10.5281/zenodo.XXXXX | Zenodo |
| Compute Environment | GPU type, CUDA, PyTorch, Python versions | `reproduce.sh` |
| Total Seeds | N (≥5) | Protocol |
| Randomization Method | Seed permutation / Latin square | Protocol |
| Blinding | Analysis blinded to condition (Y/N) | Protocol |

### 1.2 Sample Size & Power
| Field | Value | Justification |
|-------|-------|---------------|
| Primary Endpoint | Held-out LL / ECE / Task Score / Transfer | Protocol |
| Minimum Detectable Effect | Cohen's d = X | Power analysis |
| Alpha | 0.01 (H*) / 0.05 (others) | Protocol |
| Power (1-β) | ≥0.80 | Power analysis |
| Required N per Condition | N | G*Power / simulation |
| Actual N per Condition | N | Experiment log |
| Attrition | N seeds failed / excluded | Experiment log |

---

## 2. E0: Emergence-vs-Injection Discrimination (H*)

### 2.1 Primary Analysis: Held-Out Predictive Log-Likelihood (DV-a)
**Design:** One-way ANOVA / Kruskal-Wallis (T, C1, C2) + planned contrasts

| Statistic | Template |
|-----------|----------|
| **Omnibus Test** | `F(df_between, df_within) = X.XX, p = X.XXX, η² = X.XX [95% CI: X.XX, X.XX]` or `H(df) = X.XX, p = X.XXX, ε² = X.XX` |
| **Planned Contrast T vs C1** | `t(df) = X.XX, p = X.XXX, d = X.XX [95% CI: X.XX, X.XX]` |
| **Planned Contrast T vs C2** | `t(df) = X.XX, p = X.XXX, d = X.XX [95% CI: X.XX, X.XX]` |
| **Multiple Comparison Correction** | Holm-Bonferroni: α_adj = 0.01/2 = 0.005 |
| **Bayesian t-test (T vs C1)** | `BF₁₀ = X.XX [X.XX, X.XX]` |
| **Bayesian t-test (T vs C2)** | `BF₁₀ = X.XX [X.XX, X.XX]` |

**Per-Seed Reporting (Table):**
| Seed | T (LL) | C1 (LL) | C2 (LL) | C3 (LL) |
|------|--------|---------|---------|---------|
| 1 | X.XX | X.XX | X.XX | X.XX |
| 2 | X.XX | X.XX | X.XX | X.XX |
| ... | ... | ... | ... | ... |
| Mean ± SD | X.XX ± X.XX | X.XX ± X.XX | X.XX ± X.XX | X.XX ± X.XX |

**Assumption Checks:**
- Normality (Shapiro-Wilk): W = X.XX, p = X.XXX per condition
- Homoscedasticity (Levene): F = X.XX, p = X.XXX
- Independence: Verified by seed separation

### 2.2 Primary Analysis: Emergence Statistic (DV-b)
**Design:** One-sample test against null (C3) + comparison T vs C1/C2

| Statistic | Template |
|-----------|----------|
| **M(θₖ) Definition** | `NMI(learned_partition, true_latent) - NMI(learned_partition, C3_shuffled)` |
| **Null Distribution** | Mean = X.XX, SD = X.XX (from C3, N seeds) |
| **T vs Null** | `t(df) = X.XX, p = X.XXX, d = X.XX [95% CI: X.XX, X.XX]` |
| **Pre-registered Margin** | Δ = X.XX (from preregistration) |
| **Margin Test** | `M(θₖ)_T - M(θₖ)_C3 > Δ` : PASS / FAIL |
| **T vs C1 on M(θₖ)** | `t(df) = X.XX, p = X.XXX, d = X.XX [95% CI: X.XX, X.XX]` |
| **T vs C2 on M(θₖ)** | `t(df) = X.XX, p = X.XXX, d = X.XX [95% CI: X.XX, X.XX]` |

**Kill Criterion Evaluation (H*):**
| Criterion | Threshold | Result | Pass/Fail |
|-----------|-----------|--------|-----------|
| T > C1 on DV-a | p < 0.01 | p = X.XXX | PASS/FAIL |
| T > C2 on DV-a | p < 0.01 | p = X.XXX | PASS/FAIL |
| DV-b > Margin | M(θₖ)_T - M(θₖ)_C3 > Δ | Δ_obs = X.XX | PASS/FAIL |
| **Overall H* Verdict** | All 3 PASS | | PASS/FAIL |

---

## 3. EXP-1: Calibration Curve (H1)

### 3.1 Primary Analysis: Expected Calibration Error (ECE)

| Statistic | Template |
|-----------|----------|
| **ECE Formula** | `ECE = Σᵢ |acc(Bᵢ) - conf(Bᵢ)| × |Bᵢ| / N` (10 bins) |
| **System ECE** | `ECE = X.XXX [95% CI: X.XXX, X.XXX]` (bootstrap, 10000 resamples) |
| **Constant Baseline ECE** | `ECE_const = X.XXX [95% CI: X.XXX, X.XXX]` |
| **Difference** | `ΔECE = X.XXX [95% CI: X.XXX, X.XXX], p = X.XXX` (paired bootstrap) |
| **Kill Criterion** | `ECE < 0.1 AND ΔECE < 0` (better than constant) | PASS/FAIL |

### 3.2 Reliability Diagram Data (Table)
| Bin | Confidence Range | Mean Confidence | Accuracy | Count | |acc - conf| |
|-----|------------------|-----------------|----------|-------|------------|
| 1 | [0.0, 0.1) | X.XX | X.XX | N | X.XX |
| 2 | [0.1, 0.2) | X.XX | X.XX | N | X.XX |
| ... | ... | ... | ... | ... | ... |
| 10 | [0.9, 1.0] | X.XX | X.XX | N | X.XX |

### 3.3 Tier-Level Calibration (CERTAIN/PROBABLE/DEBATED/UNKNOWN)
| Tier | N Queries | Empirical Accuracy | Claimed Confidence | |Acc - Conf| |
|------|-----------|-------------------|-------------------|------------|
| CERTAIN | N | X.XX | ≥0.95 | X.XX |
| PROBABLE | N | X.XX | [0.7, 0.95) | X.XX |
| DEBATED | N | X.XX | [0.3, 0.7) | X.XX |
| UNKNOWN | N | X.XX | <0.3 | X.XX |

---

## 4. EXP-2: Affective Bridge (H2)

### 4.1 Primary Analysis: Objective Task Score

**Design:** Paired or independent samples (per protocol)

| Statistic | Template |
|-----------|----------|
| **Design** | Paired (same tasks, framed vs unframed) / Independent |
| **Framed Mean ± SD** | X.XX ± X.XX (N tasks × N seeds) |
| **Unframed Mean ± SD** | X.XX ± X.XX (N tasks × N seeds) |
| **Test Statistic** | `t(df) = X.XX, p = X.XXX` / `W = X.XX, p = X.XXX` |
| **Effect Size** | `d = X.XX [95% CI: X.XX, X.XX]` / `r = X.XX |
| **Bayesian** | `BF₁₀ = X.XX [X.XX, X.XX]` |
| **Kill Criterion** | `p < 0.05 AND d > 0.2` | PASS/FAIL |

### 4.2 Per-Task Analysis (Table)
| Task ID | Domain | Framed Score | Unframed Score | Δ | p (paired) |
|---------|--------|--------------|----------------|---|------------|
| 1 | Debugging | X.XX | X.XX | X.XX | X.XXX |
| 2 | Planning | X.XX | X.XX | X.XX | X.XXX |
| ... | ... | ... | ... | ... | ... |

---

## 5. EXP-3: Minimal Predictive Organism (H3)

### 5.1 Primary Analysis: Transfer to Held-Out Prediction

| Statistic | Template |
|-----------|----------|
| **Transfer Metric** | Held-out LL on Task B after training on Task A |
| **Emergent Structure Mean ± SD** | X.XX ± X.XX (N seeds) |
| **Random Init Control Mean ± SD** | X.XX ± X.XX (N seeds) |
| **Test Statistic** | `t(df) = X.XX, p = X.XXX` |
| **Effect Size** | `d = X.XX [95% CI: X.XX, X.XX]` |
| **Kill Criterion** | `p < 0.05 AND d > 0.3` | PASS/FAIL |

---

## 6. Universal Reporting: Effect Size Interpretation

| | Cohen's d | Interpretation |
|---|-----------|----------------|
| Trivial | < 0.2 | Negligible |
| Small | 0.2–0.5 | Small but meaningful |
| Medium | 0.5–0.8 | Substantial |
| Large | > 0.8 | Very substantial |

---

## 7. Universal Reporting: Bayesian Interpretation

| BF₁₀ | Interpretation |
|------|----------------|
| < 1/10 | Strong evidence for H₀ |
| 1/10 – 1/3 | Moderate evidence for H₀ |
| 1/3 – 1 | Weak evidence for H₀ |
| 1 – 3 | Weak evidence for H₁ |
| 3 – 10 | Moderate evidence for H₁ |
| > 10 | Strong evidence for H₁ |

---

## 8. Supplementary Statistics (Appendix)

- [ ] Full ANOVA/Kruskal-Wallis tables
- [ ] All pairwise comparisons with correction
- [ ] Bootstrap CI distributions (histograms)
- [ ] Per-seed trajectories (learning curves)
- [ ] Assumption check plots (Q-Q, residuals vs fitted)
- [ ] Sensitivity analyses (outlier removal, alternative tests)
- [ ] Power analysis details (G*Power output or simulation code)

---

## 9. Reporting Checklist (Per Experiment)

| Item | E0 | EXP-1 | EXP-2 | EXP-3 |
|------|----|-------|-------|-------|
| Preregistration URL | [ ] | [ ] | [ ] | [ ] |
| Sample size justification | [ ] | [ ] | [ ] | [ ] |
| Omnibus test + effect size | [ ] | N/A | N/A | N/A |
| Planned contrasts + CI | [ ] | [ ] | [ ] | [ ] |
| Multiple comparison correction | [ ] | N/A | N/A | [ ] |
| Bayesian analysis | [ ] | [ ] | [ ] | [ ] |
| Assumption checks | [ ] | [ ] | [ ] | [ ] |
| Per-seed data table | [ ] | [ ] | [ ] | [ ] |
| Kill criterion evaluation | [ ] | [ ] | [ ] | [ ] |
| Negative results reported | [ ] | [ ] | [ ] | [ ] |

---

**Template Version:** 1.0
**Last Updated:** 2026-07-03
**Program D Constitution:** §2, §4 (falsifiability, kill criteria, burden of proof)