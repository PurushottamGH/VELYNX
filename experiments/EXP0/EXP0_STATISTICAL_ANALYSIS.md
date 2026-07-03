# EXP-0 — Statistical Analysis Plan

All numbers in this document except §1's power table and §4's clearly-labeled synthetic example are placeholders for a run that has not happened. Nothing here is an experimental result.

---

## 1. Why N=32 is adequately powered (no experiment run required to establish this)

EXP-0's population is fixed at 32 — every seeded concept in `backend/soul/concepts.json`, not a sample (`EXP0_PROTOCOL.md` §2, Finding F0). Because McNemar's exact test only concerns *discordant* pairs (items where the two conditions disagree), power depends on how many of the 32 pairs are expected to flip, not on 32 in the abstract. This is a property of the test itself and can be computed without running anything:

**Minimum discordant pairs needed for significance at N=32, assuming zero reversals (n10=0, i.e. no paraphrase ever detects a concept the original missed — the expected regime if the effect is a one-directional collapse):**

| Discordant pairs (n01) | Exact McNemar p |
|---|---|
| 6 | 0.03125 |
| 7 | 0.015625 |
| **8** | **0.007812** ← first p ≤ 0.01 |
| 9 | 0.003906 |
| 10 | 0.001953 |

**With reversal noise present** (n10 > 0, i.e. a few paraphrases unexpectedly detect a concept the original missed — plausible under Tier 1's embedding similarity, less plausible under Tier 2's exact matching):

| n01 | n10 | Discordant | Net drop (of 32) | p | Significant at α=0.01? |
|---|---|---|---|---|---|
| 8 | 0 | 8 | 0.25 | 0.00781 | Yes |
| 8 | 2 | 10 | 0.19 | 0.10938 | No |
| 16 | 4 | 20 | 0.38 | 0.01182 | No (just misses) |
| 20 | 5 | 25 | 0.47 | 0.00408 | Yes |

**Interpretation for the pre-registered success criterion (≥40-percentage-point drop, `EXP0_PREREGISTRATION.md`):** a 40-point drop on N=32 is ~13 net-collapsed pairs. Even with a substantial reversal rate (e.g. 4–5 reversals), reaching a *net* drop of that size requires roughly 17–20 pairs to flip in the collapse direction — comfortably above the ≈8-pair threshold where the test starts detecting *anything*. **The predicted effect (PI review: 100% → ≈4–40%) is large relative to what N=32 can detect; the design is not underpowered for the effect it is trying to find.** It is, correctly, much less powered to detect a *small* effect (e.g., a true 10-point drop) — which is appropriate, since a 10-point drop would not meet the pre-registered success criterion anyway and should not be over-interpreted as "collapse" if observed.

This table is exact combinatorics (`math.comb`), reproducible by anyone with a calculator; it required no call into `backend.*`.

---

## 2. McNemar's exact test — why this test, not a t-test or the repo's existing bootstrap-mean-difference test

`research/stats.py`'s `BootstrapMeanDifferenceTest` (used for the R1 ablation) compares two **independent** groups' continuous measurements. EXP-0's data is **paired** (same concept, two conditions) and **binary** (hit/miss) — using an independent-groups test here would throw away the pairing structure and treat 64 independent Bernoulli draws as if concept identity didn't matter, inflating the effective variance and understating the signal a within-subject design actually provides.

McNemar's test is the standard test for exactly this shape of data (paired binary outcomes, 2×2 contingency by condition). The **exact** (binomial) form, not the chi-square approximation, is used because expected discordant-pair counts at N=32 can be single digits, where the chi-square approximation is unreliable.

**Test statistic.** Given `n01` (original hit → paraphrase miss) and `n10` (original miss → paraphrase hit):

```
n = n01 + n10
p = 2 * sum_{i=0}^{min(n01,n10)} C(n, i) * 0.5^n     (capped at 1.0)
```

This is the two-sided exact binomial test of `H0: n01 and n10 are draws from Binomial(n, 0.5)` — i.e., under the null, a discordant pair is equally likely to go either direction. Implemented in `analysis.py:mcnemar_exact()`, using only `math.comb` (no `scipy` dependency, matching `research/stats.py`'s existing convention).

**Concordant pairs are uninformative and correctly excluded.** A concept detected under both conditions, or neither, contributes nothing to whether wording matters — only pairs where wording *changed the outcome* carry information about H₁.

---

## 3. Bootstrap CI and Holm-Bonferroni correction

**Paired bootstrap 95% CI** (`analysis.py:paired_bootstrap_ci`): resamples **item indices** (not the two conditions independently) with replacement, 10,000 times, recomputing `hit_rate(original) − hit_rate(paraphrase)` each time from the resampled set of pairs. Resampling indices (not the raw hit/miss values per group) is what preserves the pairing — this mirrors `research/stats.py`'s general bootstrap approach while being adapted for paired rather than independent-groups data. Reported alongside McNemar's p-value as an effect-size interval, since a p-value alone says nothing about magnitude.

**Holm-Bonferroni correction** (`analysis.py:holm_bonferroni`) is applied across exactly the **two pre-registered primary tests** (Tier 1, Tier 2) — not Tier 3, which is exploratory and reported uncorrected (`EXP0_PREREGISTRATION.md`, Statistical Tests). Step-down procedure: sort p-values ascending, compare the i-th smallest (0-indexed rank `i`) against `α / (m − i)` where `m` is the number of tests; the moment one comparison fails, every remaining (larger) p-value is treated as non-significant regardless of its own value against its own threshold. With `m=2`, this reduces to: smallest p compared against `α/2`, and (if that survives) the larger p compared against `α`.

---

## 4. Worked example — SYNTHETIC DATA, NOT A RESULT

To confirm the pipeline produces sensible numbers end-to-end, `analysis.py` was exercised with **fabricated** hit/miss vectors (`random.Random(42)`, no VELYNX code called):

```
30/32 original hits, 13/32 paraphrase hits (synthetic, not measured)
McNemar: n01=17, n10=0, p=0.0000153
Bootstrap 95% CI on (original - paraphrase) rate: [0.344, 0.688]
```

This is a self-test of `analysis.py`'s arithmetic (see `EXP0_IMPLEMENTATION_PLAN.md`), included here only to show the report format a real run will produce. **It must not be cited as evidence of anything about VELYNX.**

---

## 5. Threats to statistical validity

1. **Multiple comparisons beyond the two primary tests.** If Tier 3 (exploratory) or any per-`derivation`-stratum re-analysis (`EXP0_PREREGISTRATION.md`, Controls) is also tested for significance, those are additional comparisons not covered by the Holm correction in §3. Any such analysis must be reported as exploratory, not confirmatory, and is not used for the success/failure decision in `EXP0_PREREGISTRATION.md`.
2. **N is fixed at 32 by the concept population, not chosen for power.** This is a strength for eliminating concept-selection bias (§1) but means the design cannot be "topped up" with more concepts if a result lands in an ambiguous zone (e.g., a 12-point drop) — the Decision Matrix's "ambiguous" outcome (`EXP0_PREREGISTRATION.md`) exists specifically to handle this without post-hoc sample-size inflation, which would invalidate the pre-registration.
3. **The bootstrap seed (0) and trial-order seed (1, default) are fixed, not varied.** A single run is not a Monte-Carlo estimate of run-to-run variance in the *shuffling itself* — re-running `run_exp0.py` with a different `--seed` would change trial order (relevant under state contamination, `EXP0_PROTOCOL.md` §6) but should not change which items are concordant/discordant if the detectors are deterministic (Tier 2 always is; Tier 1/Tier 3 are deterministic only insofar as the embedding model and DB state are). Re-running at 2–3 seeds as a robustness check is a reasonable follow-up and is not required for the primary pre-registered decision.
