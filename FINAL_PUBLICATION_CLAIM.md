# Final Publication Claim — Sprint 1 (Revised)

## What CAN Be Claimed

**Sprint 1 did not test H\*. The result is "H\* untested," not a hypothesis that was tested and failed.** Corrected three-point summary:

1. **H\* remains untested — growth-trigger unit defect (F-A) precluded firing; attempts-toward-kill = 0.** The growth trigger never fired (0/720 MDL checks across 20 seeds), but this is a *unit-incommensurate MDL trigger defect (F-A)*, not a property of the environment or the hypothesis. The trigger compares a per-symbol conditional-entropy delta (~0.01 bits) against a total-data-code-length penalty `λ_model ≈ 22–28 bits`, so `G ≈ −22 to −28` at **every** one of the 720 checks — growth is precluded by construction. Because the treatment never activated (T = C1 = C2 identically), no attempt to falsify H\* was earned: attempts-toward-kill = 0. This is distinct from a tested-and-failed hypothesis.

2. **DV-b shows no trustworthy positive emergence.** The original DV-b PASS (M = 0.2949 under the C3-shuffle null) was investigated and found to be a methodological artifact of shared marginal smoothing at K_learned = 2 — not a real signal. Under the preregistered block-shuffled self-null, M = −0.6055 (self-null margin 0.0896; |M| ≈ 6.8× the margin). But this negative value is itself confounded by the K′=2 vs K=10 bottleneck and is disconnected from H\*, since capacity never grew. Honest reading: **no trustworthy positive evidence for DV-b as a test of error-gated growth.**

3. **Self-null implementation gap is bounded and does not change direction.** For 2 of 20 seeds (42, 58) the block-shuffled null was identical to the learned sequence. Dropping both moves the aggregate from −0.6055 to −0.5797 — still a wide FAIL (~6.5×) against the 0.0896 margin. See `evidence/12_m_recomputation.md`. The fix is queued as a Sprint 1.3 prerequisite.

The value of Sprint 1 is a **feasibility pilot that surfaced a load-bearing engineering defect (F-A) before it reached publication.** The review process catching its own false positive (the DV-b artifact) strengthens rather than weakens credibility. With 0 growth events in 20 seeds, true growth-event rates above ~11% are surprising to miss (P < 0.10); rates ≤11% remain compatible with the data. The growth mechanism's theoretical contribution remains untested.

---

## What CANNOT Be Claimed

1. **"Growth mechanism fails" or "MDL growth doesn't work."** Growth never activated; the mechanism is untested, not falsified.

2. **"True growth rate is zero."** Only that rates >~11% are surprising to miss. Rates ≤11% remain compatible with the data.

3. **"Emergence is real/meaningful."** M is negative under the self-null (M = -0.6055 vs. margin = 0.0896). The original positive M was an artifact of the C3-shuffle null (shared marginal smoothing at K_learned = 2). M does not predict generalization.

4. **"Fixed capacity is sufficient / growth is unnecessary."** T = C1 here because growth never fired. C1's sufficiency is only observed when growth is inactive.

5. **"Random growth is equivalent to error-gated growth."** T = C2 here because both have zero growth events. Equivalence holds only under inactivity.

6. **"n=20 is adequately powered."** Planned n=22 for 10% detection at P(miss) < 0.10 was not reached. Current bound is ~11%, not 10%.

7. **"Results generalize beyond this task / predictor / MDL configuration."** Single synthetic 10-latent-state task, single predictor class (Dirichlet–Markov, k=2), single MDL threshold schedule (θ_model ≈ 21.9–28.4).

8. **"DV-b (M) validates the growth hypothesis."** M fails under the self-null (M = -0.6055). The original PASS was a methodological artifact.

9. **"No multiple-comparison burden."** Sprint 1 is first in a sequence; later Sprints may require family-wise correction.

10. **"The experiment is complete."** Sprint 1 is a feasibility/pilot study. The protocol continues to Sprint 2+ with architectural/MDL modifications.

---

## Precise Numerical Claims

| Claim | Value | Basis |
|-------|-------|-------|
| Growth events observed | 0 / 720 | growth_diagnostics.md |
| Max G − θ_model | −21.89 | growth_diagnostics.md |
| Mean G − θ_model | −26.25 | growth_diagnostics.md |
| Held-out LL (T vs C1) | δ = 0.0, p = NaN | 06_statistical_results.md |
| Held-out LL (T vs C2) | δ = 0.0, p = NaN | 06_statistical_results.md |
| DV-b M statistic (self-null, n=20) | -0.6055 | M_STATISTIC_SPECIFICATION.md |
| DV-b margin (self-null, n=20) | 0.0896 | M_STATISTIC_SPECIFICATION.md |
| DV-b M (C3-shuffle, n=20) | 0.2949 | 06_statistical_results.md (artifact) |
| DV-b margin (C3-shuffle, n=20) | 0.0440 | 06_statistical_results.md (artifact) |
| M drift (n=5 → n=20) | −0.0064 | 06_statistical_results.md |
| Sensitivity bound (P<0.10) | p > 0.109 | 11_power_analysis.md |
| P(0 | p=0.15, n=20) | 0.039 | 11_power_analysis.md |
| C2 test_n | 1999 | 06_statistical_results.md |

---

## Required Caveat Language (Must Appear in Publication)

> "The growth mechanism did not activate in any of 20 seeds (0/720 MDL checks) because the MDL growth trigger, as implemented, compares a per-symbol entropy delta against a total-data-code-length penalty (λ_model ≈ 22–28 bits) — a unit-incommensurate comparison (F-A) that precludes growth by construction. The observation is therefore a property of the trigger's units, not evidence about error-gated growth: H* is untested, not falsified (attempts-toward-kill = 0). Because Treatment, Fixed Capacity, and Random Growth were identical (T = C1 = C2), no paired difference could be tested. The secondary emergence metric M shows no trustworthy positive signal: the original PASS (M = 0.2949 under the C3-shuffle null) was a methodological artifact of shared marginal smoothing at K_learned = 2, and under the preregistered self-null M = -0.6055 (margin 0.0896), a value itself confounded by the K'=2 bottleneck and disconnected from H* since capacity never grew. With 0 growth events in 20 seeds, true growth-event rates above ~11% are surprising to miss (P < 0.10); rates ≤11% remain compatible with the data. The growth mechanism's theoretical contribution remains untested."