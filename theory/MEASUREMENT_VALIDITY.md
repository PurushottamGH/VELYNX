# Measurement Validity (Deliverable 4)

**Status:** Canonical experimental-instrument reference, version 1.0
**Date:** 2026-07-20
**Author role:** Principal Experimental Methodologist
**Input:** `METRIC_SPECIFICATION.md`, `PHENOMENON_REGISTRY.md`, `HYPOTHESIS_DISCRIMINATION_MATRIX.md`, `EXPERIMENT_ZERO_PREREGISTRATION.md`
**Epistemic status:** Construct-validity audit of every load-bearing metric. Registers no hypothesis.

---

## 0. Governing principle

**[FACT]** The brief's binding instruction: *"Avoid using task performance as a proxy for intelligence unless justified."* This document enforces it metric by metric. For each metric it states **what it measures, what it does NOT measure, its assumptions, confounds, failure modes, sensitivity, and limitations.** A metric is admitted into a kill criterion only if its "does NOT measure" column is explicitly reconciled with the claim it gates.

The single recurring validity move in this framework is **differencing against a null with known expectation**. Raw magnitudes (accuracy, log-likelihood, task score) are never construct-valid for "intelligence"; the *difference* between a treatment and a matched control with a computed null expectation is the only quantity permitted to carry evidential weight. Every metric below is therefore evaluated primarily as an *input to a difference*, not as a standalone number.

---

## M1 — Aliased-set loss gap `Δ` (PH-1 / EXP-Z0 primary)

- **What it measures:** The held-out NLL advantage of a memory-equipped system over the analytic memoryless ceiling, restricted to timesteps where current input is provably uninformative. It measures *use of a temporally-carried distinction*.
- **What it does NOT measure:** Intelligence, generality, or where memory is stored. It does not measure performance off the aliased set. It does not measure whether the carrier is internal vs external (`HYPOTHESIS_DISCRIMINATION_MATRIX.md` §4.2).
- **Assumptions:** (i) the environment's aliasing is genuine (marginals truly collide); (ii) the memoryless ceiling is correctly computed from the known generator; (iii) held-out evaluation is uncontaminated by the training stream.
- **Confounding factors:** leakage (bit survives in current input), spurious surface correlates, capacity difference between T and the ceiling model. All three are controlled in EXP-Z0 by N2, DV-3 localization, and capacity-matching respectively.
- **Failure modes:** if the generator leaks, `Δ>0` is an artifact; caught by the `C>0` (ablation) co-requirement, not by `Δ` alone. If the ceiling is miscomputed, `Δ` is biased; caught by the analytic/empirical ceiling-agreement check.
- **Sensitivity:** `Δ` scales with cue informativeness and inversely with sensor noise. At the frozen parameters (`k=8`, noise σ=0.05) a true carrier-using system produces `Δ` well above the 0.05-nat margin; near-margin `Δ` is treated as null.
- **Limitations:** valid only for the two-regime aliasing environment; a positive `Δ` on one aliasing structure does not transfer to another without re-running.

## M2 — Ablation collapse `C` (PH-1 leakage guard)

- **What it measures:** The loss increase when the historical carrier is destroyed but marginals preserved. It measures *dependence of the effect on the past*.
- **What it does NOT measure:** magnitude of competence; it is a *guard*, not a performance metric. `C` says nothing about how good T is, only that its advantage is history-dependent.
- **Assumptions:** the ablation permutation destroys the bit while preserving every marginal statistic (verified by a marginal-equality check).
- **Confounding factors:** an ablation that also perturbs marginals would inflate `C` spuriously; prevented by the marginal-equality precondition.
- **Failure modes:** `C ≈ 0` with `Δ > 0` is the *diagnostic* failure — it means the effect was leakage. This is a feature: the metric is designed to make leakage visible rather than silent.
- **Sensitivity:** high when the carrier is the sole disambiguator (by construction); would be low if multiple redundant carriers existed (excluded by single-cue design).
- **Limitations:** confirms history-dependence, not the *location* or *mechanism* of storage.

## M3 — Held-out predictive log-likelihood (PH-3, PH-5, E0 DV-a)

- **What it measures:** Average log-probability the model assigns to unseen observations; a proper scoring rule (`METRIC_SPECIFICATION.md` §4). It measures *calibrated predictive accuracy* of the density.
- **What it does NOT measure:** causal understanding, structure irreducibility (that is M5), or interactive competence (there is no action loop in a pure-prediction LL). High LL does not imply the model recovered the true generator — it can fit surface statistics.
- **Assumptions:** probabilities clipped to `ε=1e-12` and renormalized; held-out set drawn from the same distribution as training (stationarity); base-e nats used globally.
- **Confounding factors:** capacity (more parameters raise LL regardless of coupling — controlled by C1); overfitting (controlled by held-out split); environment easiness (F1 — a trivial environment saturates LL for all systems, erasing discrimination).
- **Failure modes:** comparing LL across different observation encodings is meaningless (units must match); un-clipped zero probabilities give `−∞`; non-stationary drift inflates or deflates LL for reasons unrelated to learning.
- **Sensitivity:** discriminative only when the environment is hard enough that controls do not saturate; EXP-Z0/E0 require a linear baseline to fail, guaranteeing headroom.
- **Limitations:** a *difference* in LL (T vs C1/C2) is construct-valid for "coupled retention helped"; the *absolute* LL is not construct-valid for anything about intelligence.

## M4 — Emergence statistic `M = NMI(learned,true) − NMI(learned,shuffled)` (PH-5, E0 DV-b)

- **What it measures:** How much more the learned partition aligns with the true latent than with a temporally-shuffled surrogate of identical marginals. Constructed so `E[M|H0]=0` (`METRIC_SPECIFICATION.md` §5). It measures *irreducibility of learned structure to injected marginal statistics*.
- **What it does NOT measure:** predictive usefulness (that is M3), causal structure, or "emergence" in any sense broader than this specific null-referenced subtraction (`THEORY_GAPS.md` §14). It is not a general emergence measure.
- **Assumptions:** the true latent sequence is available offline for scoring only; NMI is well-defined (non-degenerate partitions); the shuffle preserves marginals while destroying temporal structure.
- **Confounding factors:** researcher degrees of freedom in choosing the partition metric (the null-reference removes the *marginal-statistics* confound but not the *metric-choice* one); single-state degenerate partitions (handled as 0 NMI).
- **Failure modes:** if the "true latent" is itself investigator-defined at the wrong granularity, `M` scores alignment to an artifact; if the shuffle inadvertently preserves some temporal structure, the null expectation is not 0 (a validation precondition: verify `E[M|H0]=0` by feeding noise, `METRIC_SPECIFICATION.md` §5 validation).
- **Sensitivity:** `M` rises with the fraction of true-latent variance the partition captures; near-zero `M` correctly reports "no irreducible structure."
- **Limitations:** validates one confound (injected marginals) for one synthetic latent-recovery task. It does not generalize to a universal emergence claim; this is stated in `THEORY_GAPS.md` §14 and honored here.

## M5 — Expected Calibration Error (H1 / EXP-1)

- **What it measures:** Weighted gap between predicted confidence and empirical correctness across tiers (`METRIC_SPECIFICATION.md` §1). It measures *honesty of reported uncertainty*.
- **What it does NOT measure:** accuracy (a system can be perfectly calibrated and mostly wrong), retrieval quality, or intelligence. Low ECE with high error is possible and must be reported alongside accuracy.
- **Assumptions:** the tier→probability mapping is fixed before runs (equal-width midpoints); correctness is adjudicated in the *answer* label space, not the query-family or tier label space (`EXP1_PREREGISTRATION.md` §3 label-space guard).
- **Confounding factors:** bin-boundary hacking (controlled by locked equal-width bins); label-space substitution (the E0-style category error, explicitly guarded); empty bins masking miscalibration (must be reported, cannot establish a pass).
- **Failure modes:** adaptive/equal-frequency bins move thresholds after seeing outputs → invalid; scoring tiers against query types → measures the wrong construct; a one-tier system trivially achieves an ECE that says nothing (caught by the degenerate-tier kill).
- **Sensitivity:** sensitive to bin count and mapping; the framework fixes 4 bins = 4 tiers to keep a one-to-one measurement relation.
- **Limitations:** calibration is a *measurement property* supporting metacognitive control, explicitly **not** a principle of intelligence (`THEORY_NOTEBOOK_v3.md` §7.2).

## M6 — Objective task success score (H2 / EXP-2)

- **What it measures:** Binary/normalized task completion under a frozen grader (`METRIC_SPECIFICATION.md` §3). It measures *outcome on a specified third-party task set*.
- **What it does NOT measure:** intelligence, the mechanism of any framing effect, or transfer beyond the frozen set. This is the metric most at risk of the "task-performance-as-proxy" error, so it is admitted **only** as a *difference* (framed − unframed) on a **third-party** task set.
- **Assumptions:** tasks are isolated from the designer's authored concepts (circularity guard, `SCIENTIFIC_EXECUTION_SPEC.md` EXP-2); LLM temperature fixed to 0; grader is deterministic.
- **Confounding factors:** circularity (tasks implicitly matching the affect categories — the primary threat, guarded by third-party sourcing); prompt-length/format differences between conditions masquerading as framing effects.
- **Failure modes:** any dependence of the task set on the 32 authored concepts voids the experiment before results; schemas requiring per-task re-authoring prove injection, not a general effect (kill criterion).
- **Sensitivity:** sized for a moderate effect (`d=0.5`, 80% power, `N≥100`/condition).
- **Limitations:** even a positive result establishes one indexing mechanism on one task distribution, never a universal principle (`THEORY_NOTEBOOK_v3.md` §7.3).

## M7 — Concept detection accuracy (EXP-0 precondition)

- **What it measures:** Fraction of queries where the deployed legacy system detects the ground-truth concept (`METRIC_SPECIFICATION.md` §2). Used to *audit a prior claim*, not to support a hypothesis.
- **What it does NOT measure:** any P1 hypothesis; it is a precondition test that the legacy headline result collapses under paraphrase.
- **Assumptions:** strict state reset between trials (no Hebbian leakage); no keyword leakage into paraphrases.
- **Confounding factors:** keyword/stem collisions inflating paraphrase accuracy (failure conditions in EXP-0 spec).
- **Failure modes:** cross-trial memory leakage; paraphrases that retain the keyword.
- **Sensitivity:** 32 pairs suffice to detect a catastrophic collapse (~100%→~3%), not a subtle one.
- **Limitations:** informative only about the legacy system's fragility; carries no positive evidential weight for P1 claims.

---

## 8. Cross-metric validity rules (framework-wide)

1. **No raw magnitude gates a claim.** Every kill criterion is a *difference* T−control with a null of known expectation (M1 vs ceiling, M3 vs C1/C2, M4 vs shuffled, M5 vs constant-confidence, M6 vs unframed). This is the operational form of "no task performance as proxy."
2. **Label-space isolation.** A probability over label space X is never scored against observations from label space Y (the E0/EXP-1 category-error guard). Applies to M4 (learned vs true-latent granularity) and M5 (tier vs query-family) especially.
3. **Null-expectation verification precedes use.** Any null-referenced metric (M1 ceiling, M4) must first demonstrate `E[metric|H0]=0` by feeding random/structureless input, before it is trusted on real data.
4. **Resource co-reporting.** Every metric is reported with compute, memory, parameter count, and sample budget, so no effect is creditable to unmatched capacity (controls ALT-C globally).
5. **Behavior underdetermines mechanism.** No metric here identifies an internal mechanism; all mechanism language is confined to interventions (ablation in M1/M2), never inferred from a behavioral score alone.

## 9. Construct-validity summary table

| Metric | Intended construct | Construct-valid form | Would be INVALID as |
|---|---|---|---|
| M1 `Δ` | Use of temporal carrier | difference vs memoryless ceiling | absolute predictive skill |
| M2 `C` | History-dependence of effect | ablation difference | competence magnitude |
| M3 LL | Predictive accuracy | difference vs capacity/decoupled control | evidence of understanding |
| M4 `M` | Structure irreducibility | difference vs shuffled null | universal emergence |
| M5 ECE | Uncertainty honesty | vs constant-confidence, locked bins | accuracy or intelligence |
| M6 score | Task outcome | framed−unframed on third-party set | intelligence proxy |
| M7 acc | Legacy fragility audit | exact vs paraphrase | any P1 positive claim |

Every metric's construct-valid form is a **difference**, and every "INVALID as" column is the over-claim the framework's controls exist to prevent.
