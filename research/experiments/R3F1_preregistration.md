# R3F.1 — Serialization Recovery & Predictive Validity

## Experiment ID

**R3F.1**

---

## Research Question

Does Replay ΔS predict held-out counterfactual rank better than Replay ΔE?

---

## Hypothesis

**H₁**: The per-proposal signed improvement in Markov prediction error (ΔS = S_before − S_after) correlates more strongly with the held-out counterfactual ranking than the per-proposal signed improvement in cognitive free energy (ΔE = E_before − E_after).

**Rationale**: ΔS measures the merge's effect on spatial surprise — the primary vital the brain uses to detect novel structure. If the objective function (ΔE) dilutes this signal by mixing S with H (entropy) and A (active load), the raw ΔS may retain more predictive information.

---

## Null Hypothesis

**H₀**: ρ(ΔS, counterfactual_rank) ≤ ρ(ΔE, counterfactual_rank).

ΔS does not outperform ΔE. Any observed advantage is attributable to sampling noise.

---

## Independent Variables

| Variable | Levels | Description |
|----------|--------|-------------|
| Objective function | ΔS, ΔE, AlwaysMerge, NeverMerge, RandomMerge | The scoring rule used to rank proposals within each window. ΔS and ΔE are the treatment comparisons; the three controls bound the performance range. |

---

## Dependent Variables

| Variable | Description | Range |
|----------|-------------|-------|
| Pearson r | Linear correlation between objective score and negated counterfactual rank | [−1, 1] |
| Spearman ρ | Monotonic rank correlation | [−1, 1] |
| ROC AUC | Ability to discriminate counterfactual-best from non-best | [0, 1] |
| Sign Agreement | Fraction of pairwise comparisons where sign(score_i − score_j) matches sign(rank_i − rank_j) | [0, 1] |
| MAE | Mean absolute error between score and rank | [0, ∞) |
| RMSE | Root mean squared error | [0, ∞) |
| Cohen's d | Effect size of ΔS scores vs ΔE scores | ℝ |

---

## Controls

| Control | Purpose |
|---------|---------|
| AlwaysMerge (score = 1.0) | Upper-bound ceiling — every proposal is equally "best" |
| NeverMerge (score = 0.0) | Lower-bound floor — every proposal is equally "worst" |
| RandomMerge (p = 0.5) | Null-model reference — no signal, only noise |
| Identical dataset | `environment`, seed=1 |
| Identical replay horizon | 200 ticks |
| Identical seeds | Proposal generation, held-out window (999999), bootstrap (0) |
| Identical proposal generation | 4 sources × top-k=2 = 8 proposals/window |
| Identical evaluation pipeline | Counterfactual ranking by actual_energy_held_out |

---

## Dataset

- **Name**: `environment`
- **Master seed**: 1
- **Held-out seed**: 999999
- **Noise sigma**: 0.15
- **Ticks**: 5000
- **Held-out window**: 200 ticks
- **Replay horizon**: 200
- **Proximity threshold**: 0.28
- **Max clusters**: 50

---

## Random Seed

- Attribution runner seed: **1**
- Bootstrap seed: **0**
- RandomMerge seed: **42**

---

## Success Criterion

ΔS yields a statistically significant improvement over ΔE in Pearson r, with:
- ΔS Pearson r > 0.30 (Case A threshold)
- ΔS Pearson r > ΔE Pearson r
- Non-overlapping 95% bootstrap confidence intervals for ρ, OR Cohen's d 95% CI excludes zero

---

## Failure Criterion

- ΔS Pearson r ≤ ΔE Pearson r (Case B or C)
- Bootstrap confidence intervals overlap substantially
- Effect size d < 0.2 (negligible)

---

## Statistical Tests

| Test | Purpose |
|------|---------|
| Pearson r | Linear association between predicted score and ground-truth rank |
| Spearman ρ | Monotonic association (robust to outliers) |
| ROC AUC | Binary discrimination (is_cf_best) |
| Sign Agreement | Pairwise preference alignment |
| Bootstrap 95% CI (10,000 iterations) | Uncertainty quantification for r, ρ, AUC |
| Cohen's d (vs ΔE) | Standardised effect size of ΔS vs ΔE |

---

## Decision Matrix

| Outcome | Pearson r(ΔS) | Interpretation | Next Sprint |
|---------|---------------|----------------|-------------|
| Case A | > 0.30 AND > r(ΔE) | Replay objective is the bottleneck | Objective Reformulation |
| Case B | ≈ r(ΔE) | Replay representation or horizon is limiting | Replay Information Content Audit |
| Case C | < 0 | Evaluation pipeline is suspect | Benchmark Correctness Audit |

---

## Threats to Validity

1. **Serialization is the only change** — If regeneration produces different logs despite identical seeds, the system is not reproducible and any conclusion is invalid.
2. **Counterfactual ground truth is noisy** — The held-out window (200 ticks) may be too short to reliably estimate post-merge energy; replay_error inflates label noise.
3. **ΔS and ΔE are correlated** — ΔE is a linear combination of ΔS, ΔH, and ΔA. If ΔH and ΔA contain no signal, ΔE and ΔS will track each other closely and power is limited.
4. **Single dataset** — Results may not generalise beyond `environment`.

---

## Freeze Date

This document is frozen before any code modification.

All subsequent changes are tracked by Git and referenced to this experiment ID.
