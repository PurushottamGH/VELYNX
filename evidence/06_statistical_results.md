# Statistical Results — Sprint 1.1.1 Final Reconciliation

**[FACT]** E0 corrected production run (C2 data leakage fixed). Base seed 42, 5 seeds, 34.4s.

## Design

| Aspect | Specification |
|--------|--------------|
| Conditions | T (error-gated growth), C1 (fixed capacity), C2 (capacity-matched random growth), C3 (shuffled input) |
| Seeds | 5 (42–46) |
| DV-a | Held-out predictive log-likelihood (independent test sequence, not last 20% of training) |
| DV-b | M = NMI(learned, true) − NMI(learned, shuffled) |
| Correction | Holm-Bonferroni across T vs C1, T vs C2 (FWER = 0.01) |
| Kill criterion | T fails to beat BOTH C1 and C2 on DV-a at p < 0.01 across >= 5 seeds |

## Results

### DV-a: Held-out Predictive Log-Likelihood

| Seed | T | C1 | C2 | C3 |
|------|---|---|---|---|
| 42 | -0.9272 | -0.9272 | -0.9272 | -0.7619 |
| 43 | -0.6937 | -0.6937 | -0.6937 | -0.6914 |
| 44 | -0.7297 | -0.7297 | -0.7297 | -0.6957 |
| 45 | -0.6722 | -0.6722 | -0.6722 | -0.6697 |
| 46 | -0.7318 | -0.7318 | -0.7318 | -0.7373 |

**Key observation:** T == C1 == C2 for all seeds. All three conditions produced identical models (growth=0), so held-out LLs are identical.

| Comparison | Mean Δ | p-value | Significant (α=0.01, Holm-Bonf.) |
|------------|--------|---------|-----------------------------------|
| T vs C1 | 0.0 | NaN (zero variance) | No |
| T vs C2 | 0.0 | NaN (zero variance) | No |

**DV-a verdict: FAIL.** T did not beat BOTH C1 and C2 at corrected p < 0.01.

### DV-b: Emergence Statistic M

| Metric | Value |
|--------|-------|
| M statistic | 0.3013 |
| Margin (data-derived) | 0.0511 |
| Exceeds margin | Yes |

**DV-b verdict: PASS.** M exceeds data-derived margin.

## Growth Diagnostics

- **Total MDL checks:** 90 (across all seeds)
- **Growth events:** 0
- **Max margin (G − λ_model):** −21.95
- **Mean margin:** −26.25

Growth never fired. The MDL criterion consistently calculated G − λ_model ≪ 0 at every check point.

## C2 Fix Verification

- **C2 test_n:** 1999 (all seeds) — matches T's test_n of 1999
- **Held-out source:** Independent test sequence (not last 20% of training)
- **Verification status:** ✅ C2 now evaluates on the same held-out test sequence as T, C1, and C3

## Conclusion

**Verdict: FAIL (DV-a).** Treatment failed to beat BOTH controls on held-out predictive log-likelihood. This is a genuine negative result: the MDL trigger never fires on this environment class, so the treatment condition produces identical behavior to the fixed-capacity and decoupled controls. The C2 data leakage bug has been corrected, and the FAIL verdict is robust to the fix.
