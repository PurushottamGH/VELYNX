# Power Analysis - Binomial Sensitivity for Growth Events

## Purpose

This note quantifies how much can be inferred from observing 0 growth events across 20 seeds. It treats each seed as a Bernoulli trial with an assumed true growth-event rate `p` and reports the probability of observing zero growth events:

`P(0 observed in n seeds) = (1 - p)^n`

The current result is `0/20` growth events (extended from `0/5` in Sprint 1.1.1). This table is a sensitivity analysis, not evidence that the true rate is exactly zero. Both the old 5-seed and new 20-seed tables are retained for comparison.

## Current 5-Seed Sensitivity Table

| Assumed true growth rate | P(observe 0/5) | Interpretation |
|--------------------------|----------------|----------------|
| 5% | 0.7738 | Very easy to miss |
| 10% | 0.5905 | Very easy to miss |
| 15% | 0.4437 | Easy to miss |
| 20% | 0.3277 | Plausible to miss |
| 25% | 0.2373 | Plausible to miss |
| 30% | 0.1681 | Plausible to miss |
| 35% | 0.1160 | Still not very surprising to miss |
| 40% | 0.0778 | Somewhat surprising to miss |
| 45% | 0.0503 | Surprising to miss |
| 50% | 0.0313 | Very surprising to miss |

## Plain-Language Interpretation

With only 5 seeds, observing 0 growth events does not sharply distinguish true zero growth from a low or moderate true growth rate.

Under a practical `P(0 observed) < 0.10` threshold for calling a miss "surprising," the current `0/5` result is still compatible with true growth rates up to roughly 35%. For example, if the true growth rate were 10%, there would still be a 59.05% chance of seeing no growth events in 5 seeds. If the true rate were 15%, there would still be a 44.37% chance of seeing no growth events.

Therefore, the current 5-seed run supports the statement that growth was not observed in this sample, but it does not by itself rule out true growth rates in the 5% to 35% range. Rates around 40% or higher begin to look inconsistent with `0/5` under the 10% surprise threshold.

## Recommended Target n

The target is to make even a 10% to 15% true growth rate surprising to miss:

`(1 - p)^n < 0.10`

| Target true rate to detect-by-missing | Minimum n for P(0 observed) < 0.10 | P(0 observed) at minimum n |
|---------------------------------------|------------------------------------|-----------------------------|
| 10% | 22 | 0.0985 |
| 15% | 15 | 0.0874 |

Recommendation: use at least `n=22` total seeds if the goal is to make a true 10% growth rate surprising to miss. If the practical target is only to make a true 15% rate surprising to miss, `n=15` is sufficient.

The planned 20-seed extension is still useful: at `n=20`, a true 15% rate has only `P(0 observed) = 0.0388`, so missing all events would be surprising. However, at a true 10% rate, `P(0 observed) = 0.1216`, which remains just above the 0.10 threshold. Thus, `n=20` is close but not sufficient for the stricter 10% target.

## 20-Seed Extension Result

Observed: 0 growth events in 20 seeds (42–61). This replaces the `0/5` result from Sprint 1.1.1.

| Field | Value |
|-------|-------|
| Total seeds | 20 |
| Growth-event seeds | 0 |
| Observed growth rate | 0% |
| Base seed / seed range | 42 / 42–61 |
| Artifact path | `evidence/experiment_logs/run_20260704_n20/aggregated_results.json` |

### 20-Seed Sensitivity Table

`P(0 observed in 20 seeds) = (1 − p)^20`

| Assumed true growth rate | P(observe 0/20) | Interpretation |
|--------------------------|-----------------|----------------|
| 5% | 0.3585 | Easy to miss |
| 10% | 0.1216 | Plausible to miss |
| 15% | 0.0388 | Surprising to miss |
| 20% | 0.0115 | Very surprising to miss |
| 25% | 0.0032 | Extremely surprising to miss |
| 30% | 0.0008 | Nearly impossible to miss |
| 35% | 0.0002 | Virtually impossible to miss |
| 40% | <0.0001 | Effectively ruled out |
| 45% | <0.0001 | Effectively ruled out |
| 50% | <0.0001 | Effectively ruled out |

## Plain-Language Interpretation (n=20)

At 20 seeds with 0 observed growth events, the inference is substantially sharper than at n=5:

- A true 15% growth-event rate is now **surprising to miss** (P = 0.039 < 0.10).
- A true 10% rate remains **plausible** (P = 0.122 > 0.10) — still not ruled out.
- A true 5% rate is **easy to miss** (P = 0.359).

The threshold question: **what true growth rate becomes "surprising" to miss (P < 0.10)?** At n=20:

`(1 − p)^20 < 0.10 ⇒ p > 1 − 0.10^(1/20) ≈ 0.1089`

So any true growth rate above **≈10.9%** would be surprising to miss at n=20. Conversely, rates at or below ≈10.9% remain compatible with the observed `0/20` under the 10% surprise threshold.

This means the 20-seed run can state: **the true growth-event rate is unlikely to exceed ≈11%** (with 90% confidence in the sense of P(miss) < 0.10). This is a meaningful improvement over the n=5 bound of ≈35%.

The recommended target of n=22 (from the 5-seed analysis) was nearly correct — at n=22, the 10% threshold becomes detectable-by-miss with P = 0.0985. The n=20 result misses that target by a narrow margin (P = 0.122 for 10%), but decisively rules out any rate above ≈10.9%.

## Reporting Guidance (n=20)

For the current `0/20` result, the inference is sharper. Prefer:

"Growth was observed in 0/20 independent seeds. At n=20, a true growth-event rate above approximately 10.9% would be surprising to miss (P < 0.10). A true 15% rate is ruled out at P = 0.039. A true 10% rate remains plausible (P = 0.122), and a true 5% rate is still easy to miss (P = 0.359). The 5-seed bound of ≈35% has been tightened to ≈11%."

The n=5 table is retained for historical reference. The n=20 table is the definitive sensitivity for Sprint 1.2.
