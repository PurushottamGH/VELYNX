# Abstract Language — Sprint 1 Result (Revised)

## Exact Wording (revised — corrected for F-A / H\*-untested and F-B)

We evaluated whether an MDL-internal growth mechanism improves held-out predictive performance on a synthetic 10-latent-state sequence task, using a Dirichlet–Markov conjugate predictor (initial capacity k=2). Across 20 independent seeds, Treatment (error-gated growth) produced identical models to Fixed Capacity (C1) and Random Growth (C2) controls: the growth trigger never fired (0/720 MDL checks). This is a trigger-unit defect (F-A), not a property of the task — the MDL trigger compares a per-symbol conditional-entropy delta (~0.01 bits) against a total-data-code-length penalty (λ_model ≈ 22–28 bits), so the growth criterion G is negative by construction at every step. The primary hypothesis (H\*) is therefore **untested, not falsified** (attempts-toward-kill = 0); held-out log-likelihood was identical across T, C1, and C2 (paired t-test: zero variance, p = NaN) only because the manipulation never activated. The secondary emergence statistic M showed no trustworthy positive signal: an earlier positive M = 0.295 under the C3-shuffle null was found to be a methodological artifact of shared marginal smoothing at K_learned = 2, and under the preregistered self-null M = -0.606 (margin 0.090), a value itself confounded by the k=2 bottleneck. With 0 growth events in 20 seeds, a true growth-event rate above ~10.9% is surprising to miss (P < 0.10); a 15% rate is ruled out at P = 0.039. Sprint 1 is a feasibility pilot whose value is surfacing this load-bearing trigger defect before publication.

---

## Ultra-Short Version (revised)

Across 20 seeds, MDL-internal growth never activated (0/720 checks) — a unit-incommensurate trigger defect (F-A), not a tested-and-failed result: H\* is untested (attempts-toward-kill = 0). Treatment matched Fixed Capacity and Random Growth identically because the manipulation never fired. Emergence M = -0.606 under self-null shows no trustworthy positive signal; the original M = 0.295 was a C3-shuffle artifact. True growth rate >10.9% ruled out (P < 0.10).

---

## Key Phrases for Reuse

- "The growth trigger never fired (0/720 MDL checks across 20 seeds) — a unit-incommensurate MDL trigger defect (F-A), not a test of H\*"
- "H\* is untested, not falsified; attempts-toward-kill = 0 (the treatment never activated: T = C1 = C2)"
- "Secondary emergence M shows no trustworthy positive signal: M = -0.606 under the preregistered self-null; the original M = 0.295 (C3-shuffle) was a methodological artifact of shared marginal smoothing at K_learned = 2"
- "Under the self-null, |M| = 0.606 is ~6.8× the 0.090 margin (the earlier '~14×' compared against the wrong 0.044 threshold)"
- "The review process catching its own false positive strengthens the paper's credibility"
- "True growth-event rate above ~10.9% surprising to miss (P < 0.10); 15% ruled out at P = 0.039"
- "The n=5 sensitivity bound of ~35% tightens to ~11% at n=20"
- "Sprint 1 is a feasibility pilot; its value is surfacing the F-A trigger defect before publication; H\*'s theoretical contribution remains untested"