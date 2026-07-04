# Statistical Results — Sprint 1.2 20-Seed Extension

**[FACT]** E0 20-seed production run (C3 instrumentation complete). Base seed 42, 20 seeds (42–61), 640.5s.

## Design

| Aspect | Specification |
|--------|--------------|
| Conditions | T (error-gated growth), C1 (fixed capacity), C2 (capacity-matched random growth), C3 (shuffled input) |
| Seeds | 20 (42–61) |
| DV-a | Held-out predictive log-likelihood (independent test sequence, not last 20% of training) |
| DV-b | M = NMI(learned, true) − NMI(learned, shuffled) |
| Correction | Holm-Bonferroni across T vs C1, T vs C2 (FWER = 0.01) |
| Kill criterion | T fails to beat BOTH C1 and C2 on DV-a at p < 0.01 across >= 5 seeds |

## Results

### DV-a: Held-out Predictive Log-Likelihood

| Seed | T | C1 | C2 | C3 |
|------|---|---|---|---|
| 42 | −0.9272 | −0.9272 | −0.9272 | −0.7619 |
| 43 | −0.6937 | −0.6937 | −0.6937 | −0.6914 |
| 44 | −0.7297 | −0.7297 | −0.7297 | −0.6957 |
| 45 | −0.6722 | −0.6722 | −0.6722 | −0.6697 |
| 46 | −0.7318 | −0.7318 | −0.7318 | −0.7373 |
| 47 | −0.7501 | −0.7501 | −0.7501 | −0.7002 |
| 48 | −1.5810 | −1.5810 | −1.5810 | −1.2062 |
| 49 | −0.6891 | −0.6891 | −0.6891 | −0.7188 |
| 50 | −0.6478 | −0.6478 | −0.6478 | −0.6459 |
| 51 | −0.6615 | −0.6615 | −0.6615 | −0.6639 |
| 52 | −0.7584 | −0.7584 | −0.7584 | −0.8157 |
| 53 | −0.8040 | −0.8040 | −0.8040 | −0.7240 |
| 54 | −0.8307 | −0.8307 | −0.8307 | −0.7095 |
| 55 | −0.6977 | −0.6977 | −0.6977 | −0.7051 |
| 56 | −0.6935 | −0.6935 | −0.6935 | −0.6936 |
| 57 | −0.7495 | −0.7495 | −0.7495 | −0.7381 |
| 58 | −0.7081 | −0.7081 | −0.7081 | −0.7368 |
| 59 | −0.6439 | −0.6439 | −0.6439 | −0.6428 |
| 60 | −0.7075 | −0.7075 | −0.7075 | −0.6833 |
| 61 | −0.7075 | −0.7075 | −0.7075 | −0.7076 |

**Key observation:** T == C1 == C2 for ALL 20 seeds. All three conditions produced identical models (growth=0 across every seed), so held-out LLs are identical within each seed.

| Comparison | Mean Δ | p-value | Significant (α=0.01, Holm-Bonf.) |
|------------|--------|---------|-----------------------------------|
| T vs C1 | 0.0 | NaN (zero variance) | No |
| T vs C2 | 0.0 | NaN (zero variance) | No |

**DV-a verdict: UNTESTED (not FAIL).** T did not beat C1/C2 — but only because T == C1 == C2 identically: growth never fired, so the treatment and controls are the *same model*. The paired t-test collapses to NaN because every T−C1 and T−C2 difference is exactly 0.0. This is **not** an H\* result: growth could not fire because the MDL trigger is unit-incommensurate (per-symbol entropy delta vs. total-data-code penalty λ_model ≈ 22–28 bits; see F-A in `RESEARCH_DIRECTOR_DECISION.md`). The manipulation never activated, so **H\* is untested; attempts-toward-kill = 0.** (The raw δ=0.0 / p=NaN values above are what the run produced and are unchanged.)

### DV-b: Emergence Statistic M

| Metric | Value |
|--------|-------|
| M statistic | 0.2949 |
| Margin (data-derived) | 0.0440 |
| Exceeds margin | Yes |

**DV-b verdict: NO TRUSTWORTHY POSITIVE EMERGENCE.** M = 0.2949 exceeds the data-derived margin under the pre-registered C3 null and is stable across n (0.3013 at n=5 → 0.2949 at n=20) — but this "PASS" is a known artifact, not evidence of emergence (see below).

**⚠️ The C3-null PASS is a methodological artifact.** Per `M_STATISTIC_SPECIFICATION.md` (Sprint 1.3 companion), M was recomputed under a block-shuffled *self*-null (the predictor's own inferred sequence, block-shuffled at the median run length to preserve marginals and short-range statistics while destroying long-range temporal order). Under this stricter null, M = **−0.6055** (SE=0.0448, margin=0.0896) — the C3-null positive was inflated by shared marginal smoothing between T and C3 at K_learned=2. ARI tells the same story: 0.1376 under C3 null, −0.7967 under self-null. The negative self-null value is itself confounded by the K′=2 vs K=10 bottleneck and is **disconnected from H\***, since capacity never grew. See `evidence/12_m_recomputation.md` (incl. verified robustness to the 2-seed self-null gap). **Net: DV-b provides no trustworthy positive evidence; DV-a is untested (F-A). The n=20 result is "H\* untested," not a double-negative.**

## Growth Diagnostics

- **Total MDL checks:** 720 (360 from T, 360 from C3 — C3 now instrumented)
- **Growth events:** 0 across all 20 seeds
- **Max margin (G − λ_model):** −21.89
- **Mean margin:** −26.25

Growth never fired in any seed. The MDL criterion consistently calculated G − λ_model ≪ 0 at every check point across both the temporal-ordered (T) and shuffled-input (C3) conditions. C3's per_step_log is now populated identically to T.

## C2 Fix Verification

- **C2 test_n:** 1999 (all seeds) — matches T's test_n of 1999
- **Held-out source:** Independent test sequence (not last 20% of training)
- **Verification status:** ✅ C2 now evaluates on the same held-out test sequence as T, C1, and C3

## Comparison: n=5 vs n=20

| Metric | n=5 (Sprint 1.1.1) | n=20 (Sprint 1.2) | Delta |
|--------|---|---|---|
| DV-a status | Untested (F-A) | Untested (F-A) | Unchanged |
| DV-b (C3 null) | PASS (artifact) | PASS (artifact) | Unchanged |
| DV-b (self-null) | — | FAIL (M=−0.6055) | Stricter null |
| Overall verdict | H\* untested | H\* untested | Unchanged |
| Growth events | 0/5 | 0/20 | Unchanged |
| Mean G − λ_model | −26.25 | −26.25 | Stable |
| M statistic (C3) | 0.3013 | 0.2949 | −0.0064 drift |
| DV-b margin (C3) | 0.0511 | 0.0440 | Tighter (more seeds) |

**The characterization does not change at n=20.** The result is robust: growth never fires (F-A trigger-unit defect), T is identical to C1/C2, DV-a is untested, and DV-b shows no trustworthy positive emergence.

## Conclusion

**Verdict: H\* UNTESTED (growth-trigger unit defect, F-A; attempts-toward-kill = 0).** Across 20 independent seeds (42–61), the MDL-internal-growth trigger never fired once. Every MDL check — 360 in T, 360 in C3 — evaluated G − λ_model < 0, but this is a property of the trigger's units (a per-symbol entropy delta compared against a total-data-code penalty λ_model ≈ 22–28 bits), **not** evidence about error-gated growth. Treatment produces identical models to C1 (fixed capacity) and C2 (random growth) only because the manipulation never activated, so no H\* test was earned. The result is stable: the n=5 and n=20 characterizations are identical. At n=20, a true 15% growth-event rate can be ruled out at P(miss) = 0.039 < 0.10 (see power analysis). Sprint 1.3 must fix the trigger units before C2f can meaningfully test whether growth helps.
