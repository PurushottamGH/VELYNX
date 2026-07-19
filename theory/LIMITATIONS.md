# Limitations — Sprint 1 (n=20)

## ⚠️ CRITICAL LIMITATION: DV-a Is Untested, Not Failed (F-A — Trigger Unit Defect)

**The "0/720 growth events" result is an artifact of a unit-incommensurate MDL trigger (F-A), not a test of H\*.** The trigger compares a per-symbol conditional-entropy delta (`H_before − H_after ≈ 0.01 bits`) against a total-data-code-length penalty (`λ_model = k·b + n·log₂N ≈ 22–28 bits`). These are different quantities, so `G ≈ −22 to −28` at **every** one of the 720 checks — growth is precluded by construction, independent of the environment or the hypothesis. Consequences:

- **H\* is untested, not falsified.** "Growth never fired" is a property of the trigger's units, not evidence about error-gated growth. Sprint 1 must **not** be described as a "double-negative result."
- **Attempts-toward-kill = 0.** Because the treatment never activated (T = C1 = C2 identically), no honest attempt to falsify H\* was earned; this run does not count toward the kill criterion.
- **Prerequisite:** Sprint 1.3 must fix the trigger-unit mismatch (grow iff `N·ΔH > model-cost-of-one-state`) before C2f can meaningfully test whether growth helps.

---

## ⚠️ CRITICAL LIMITATION: C2 Control Was Not Independent

**C2 ("capacity-matched random growth") did not function as an independent random-growth control.** Its growth count was derived from Treatment's *observed* growth events (run.py:622,631), not drawn independently. Since Treatment had **zero** MDL-triggered growth events across all 20 seeds, C2's growth count was **structurally forced to zero** by construction. C2's zero-growth outcome was **structurally forced, not observed**. This means:
- C2 did not test whether random growth *would have* worked had growth occurred
- T = C2 identity reflects shared inactivity, not empirical equivalence under growth
- The question "would random growth have helped if growth occurred?" remains entirely untested
- This question is reserved for Sprint 1.3 (forced-growth sensitivity)

---

## ⚠️ CRITICAL LIMITATION: M-Statistic Dissociation from Generalization

**The emergence statistic M (DV-b) passed while held-out predictive likelihood (DV-a) failed.** M = 0.2949 (n=20) exceeds the data-derived margin 0.0440, but M measures NMI(learned, true) − NMI(learned, shuffled) — statistical structure recovery relative to a shuffled baseline. This does **not** imply task-relevant structure or better generalization. M and DV-a are dissociated on this task: positive emergence does not translate to improved held-out prediction. The theoretical link between M and the growth hypothesis is untested because growth never activated (0/720 checks).

---

## ⚠️ CRITICAL LIMITATION: M Fails Under Stricter Null (Recomputation with M_STATISTIC_SPECIFICATION.md)

**The M = 0.2949 PASS is sensitive to the choice of null reference.** Per the stricter methodology in `M_STATISTIC_SPECIFICATION.md` (Sprint 1.3 companion), the M statistic was recomputed against two alternative references:

1. **Hungarian-aligned NMI with the C3 (shuffled-input) null** (handles the K'≠K identifiability failure): mean M = **0.2949**, identical to the unaligned value because with K'=2 and K=10, alignment is a no-op. Margin still 0.0440. **PASS preserved.**

2. **Hungarian-aligned NMI with a block-shuffled *self*-null** (the predictor's own inferred sequence, block-shuffled at the median run length to preserve marginals and short-range statistics while destroying long-range temporal order): mean M = **−0.6055** (SE=0.0448, margin=0.0896). **FAIL by a wide margin (0.65 below the 0.044 threshold).**

3. **ARI with block-shuffled self-null**: mean = **−0.7967**. **FAIL.**

**Interpretation:** The predictor with K'=2 latent states produces a 2-state temporal sequence that is essentially a smoothed low-frequency version of the 10-state ground truth. The C3 null also produces a 2-state sequence, and crucially C3's two clusters are correlated with T's two clusters (both are picking up the same low-frequency structure of the marginal distribution). This inflates `NMI(learned, C3)` and inflates the legacy M. The block-shuffled self-null removes that shared low-frequency signal and asks: *does the predictor's specific temporal ordering match the true temporal ordering above what its own marginals would predict?* Answer: **no, it does not.** A 2-state model cannot distinguish 10 true states; any M>0 under the C3 null is partially attributable to shared marginal structure, not temporal learning.

**Consequence for DV-b verdict:** The DV-b verdict of PASS depends on the C3 null. Under the stricter self-null, DV-b **fails** by an even larger margin than DV-a's primary failure. The emergence claim ("the predictor recovered latent structure") is **not supported** under the more conservative null. This must be reported in any publication.

**Recomputation artifact:** `recompute_m_hungarian.py` (per-seed table and aggregate statistics) and `evidence/12_m_recomputation.md` (this analysis written up).

---

## Claims NOT Supported by Evidence

### 1. Treatment Outperforms Controls on Held-Out Prediction
**Cannot claim:** "Treatment outperforms Fixed Capacity (C1) or Random Growth (C2) on held-out predictive log-likelihood."
**Reason:** T = C1 = C2 identically on all 20 seeds (growth never fired — F-A trigger-unit defect). Paired t-test collapses (zero variance). No statistical evidence of superiority — and, because the manipulation never activated, no test of H\* was performed (DV-a is untested, not failed).

### 2. Growth Mechanism Is "Proven Useless" or "Impossible"
**Cannot claim:** "Growth cannot work" or "The growth mechanism is fundamentally flawed."
**Reason:** 0/20 observed growth events does not prove the mechanism cannot fire under any condition. The MDL threshold (λ_model) may be too conservative, the data may lack sufficient structure, or the growth budget may be too restrictive. The evidence shows growth did not fire *in this configuration on this task*.

### 3. True Growth Rate Is Zero
**Cannot claim:** "The true growth-event rate is 0%."
**Reason:** At n=20, a true 5% rate has P(miss) = 0.359; a true 10% rate has P(miss) = 0.122. Rates ≤10.9% remain compatible with 0/20 under P(miss) ≥ 0.10. The bound is ≈11%, not 0%.

### 4. Emergence (M) Implies Generalization Benefit
**Cannot claim:** "The positive emergence statistic M translates to better held-out prediction."
**Reason:** DV-a is untested (F-A: growth never fired) and DV-b's C3-null PASS is an artifact (self-null M=−0.6055). Even at face value, M measures structure recovery relative to a shuffle; it does not imply better generalization on this task.

### 5. C2 Control Is "Solved" or "Sufficient"
**Cannot claim:** "C2 is a sufficient control for all capacity confounds."
**Reason:** C2 matches capacity trajectory but uses random growth. T and C2 produce identical models here. C2 validates that capacity trajectory alone does not explain T (since both fail), but does not prove T's growth mechanism is correct—it simply did not activate.

### 6. Generalization Beyond This Task/Configuration
**Cannot claim:** "These results generalize to other tasks, architectures, or MDL configurations."
**Reason:** Single synthetic 10-latent-state task, single predictor class (Dirichlet–Markov, k=2), single MDL configuration (λ_model = k·b + n·log₂N with b=1.0; θ_model ≈ 21.9–28.4). Growth threshold may be miscalibrated for this setting.

### 7. n=20 Is "Sufficient" for All Inferences
**Cannot claim:** "20 seeds is enough to rule out meaningful growth rates."
**Reason:** At n=20, a true 10% growth rate remains plausible to miss (P=0.122 > 0.10). The pre-registered target for 10% detection was n≥22. n=20 tightens the bound to ~11% but does not meet the 10% target.

---

## Mandatory Limitations for Publication

1. **Single synthetic task, single predictor class (Dirichlet–Markov, k=2), single MDL configuration.** Results may not generalize.

2. **Growth mechanism never activated** (0/20 seeds). The treatment condition is functionally identical to fixed-capacity and random-growth controls. No evidence that the growth mechanism *can* work on this task.

3. **DV-a (primary outcome) is untested, not failed.** The growth trigger could not fire due to a unit-incommensurate MDL comparison (F-A); T = C1 = C2 identically. The primary hypothesis was never actually tested — this is distinct from a tested-and-failed result. Attempts-toward-kill = 0.

4. **DV-b (emergence) and DV-a dissociate.** Positive emergence (M > margin) does not translate to better generalization on this task.

5. **Power bound is ~11%, not 0%.** True growth rates ≤10.9% are not ruled out at the P(miss) < 0.10 threshold. The n=5 bound (~35%) is tightened but not eliminated.

6. **C2 control validates capacity matching but not growth mechanism.** T and C2 are empirically identical here; the growth mechanism's theoretical contribution is untested because it never fired.

7. **No hyperparameter sweep on MDL thresholds.** λ_model values (21.93–28.43) far exceed observed G (range ~−0.02 to +0.10). Threshold may be too conservative for this task.

8. **Single random seed for data order within each seed.** Each "seed" controls initialization and data order; no separate data-order randomization.

9. **Sprint 1 is a pilot/feasibility study.** n=20 was chosen for rapid iteration, not definitive power. The planned n=22 for 10% detection was not reached.

10. **No correction for multiple comparisons across Sprints.** Sprint 1 is the first in a sequence; later Sprints may require correction if treated as a family.

11. **M is null-reference-dependent.** The DV-b PASS (M=0.2949 > 0.044) holds under the C3-shuffled-input null but **fails** under the block-shuffled self-null prescribed in `M_STATISTIC_SPECIFICATION.md` (M=−0.6055, |M|≈14× the margin). The original M was partially driven by shared low-frequency marginal structure between T and C3, not by temporal learning. Publications must report M under both nulls; the stricter null is the more conservative evidence-relevant test.