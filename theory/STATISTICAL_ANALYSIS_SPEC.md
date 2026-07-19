# STATISTICAL ANALYSIS SPECIFICATION

**[FACT]** This document defines the exact statistical tests, decision rules, and evaluation procedures for Program D's kill criteria. 

## 1. General Rules
- **Significance Level:** $\alpha = 0.05$ unless otherwise specified (E0 demands $\alpha = 0.01$).
- **Multiple Comparisons:** Bonferroni correction must be applied when computing tests across multiple tiers or subsets.
- **Effect Size:** Cohen's $d$ must be reported alongside any t-test p-value.
- **Confidence Intervals:** 95% CIs via 10,000-iteration bootstrap for non-parametric metrics (like ECE).

## 2. EXP-0 Evaluation
- **Statistical Test:** McNemar's Test for paired nominal data.
- **Null Hypothesis Evaluation:** Compare `accuracy_exact` vs `accuracy_paraphrase`.
- **Kill Criterion Evaluation:** If paraphrase accuracy collapses to random chance baseline ($\approx 1/32$) and McNemar test shows significant difference ($p < 0.01$), the system FAILS the precondition.

## 3. EXP-1 Evaluation (H1)
- **Statistical Test:** Expected Calibration Error (ECE) computation. Chi-square test for independence.
- **Null Hypothesis Evaluation:** Chi-square test between `predicted_tier` categorical variable and `empirical_correctness` binary variable.
- **Kill Criterion Evaluation:** 
  1. If $ECE \geq 0.10$, FAIL.
  2. If Chi-square $p > 0.05$ (meaning correctness is statistically independent of predicted tier), FAIL.
- **Decision Rule:** PASS strictly if $ECE < 0.10$ AND Chi-square $p < 0.05$.

## 4. EXP-2 Evaluation (H2)
- **Statistical Test:** Independent samples t-test (if scores are continuous/normalized) or Mann-Whitney U test (if scores are ordinal/non-normal).
- **Null Hypothesis Evaluation:** $H_0: \mu_{framed} \leq \mu_{unframed}$.
- **Kill Criterion Evaluation:** If $p \geq 0.05$ (one-tailed) OR $\mu_{framed} \leq \mu_{unframed}$, FAIL.
- **Effect Size:** Compute Cohen's $d$. 

## 5. E0 Evaluation (H*)
- **Statistical Test:** Paired t-tests across $\geq 5$ seeds.
- **Null Hypothesis Evaluation:**
  - $H_{0a1}: LL_T \leq LL_{C1}$
  - $H_{0a2}: LL_T \leq LL_{C2}$
  - $H_{0b}: M_T \leq \epsilon$ (where $\epsilon$ is noise margin from C3).
- **Kill Criterion Evaluation:** 
  - If $p_{T>C1} \geq 0.01$ OR $p_{T>C2} \geq 0.01$ over 5 seeds, FAIL.
  - If $M_T$ is not statistically distinct from $M_{C3}$, FAIL.
- **Decision Rule:** Must pass ALL gates above across 2 honest attempts.

## 6. Power Analysis
- All tests must be adequately powered. 
- E0: 5 seeds are analytically derived as sufficient for deterministic algorithmic differences.
- EXP-1: $N \geq 200$ required for stable ECE bins.
- EXP-2: $N \geq 100$ tasks per condition required for 80% power assuming $d = 0.5$.
