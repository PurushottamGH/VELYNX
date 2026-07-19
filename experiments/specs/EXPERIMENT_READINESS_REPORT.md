# EXPERIMENT READINESS REPORT

This report evaluates the scientific readiness of the required experiments: EXP0, EXP1, EXP2, and E0.

## 1. EXP0 (Benchmark Paraphrase / Precondition)
**Status: READY**
- **Implementation Status:** The run script `experiments/EXP0/run_exp0.py` fully implements the pre-registered protocol.
- **Scientific Validation:** It properly interleaves trials to prevent Hebbian accumulation confounds, relies on a pre-validated leakage checker, uses exact randomized seeds, and resets the cognitive database before each relevant trial.
- **Action Required:** Execute to formally test the collapse to noise.

## 2. EXP1 (Calibration Curve / Program A Gate)
**Status: NOT READY (Unimplemented)**
- **Implementation Status:** `experiments/EXP1/` is effectively empty (only `__init__.py`).
- **Scientific Validation:** Code does not exist to measure Expected Calibration Error (ECE) or to map the symbolic confidence tiers to the empirical accuracies on a mixed query set.
- **Action Required:** Implement the evaluation runner per `SCIENTIFIC_EXECUTION_SPEC.md` against a fixed query dataset of $\geq 200$ items.

## 3. EXP2 (Affective Bridge / Program B Audit)
**Status: NOT READY (Unimplemented)**
- **Implementation Status:** `experiments/EXP2/` is effectively empty.
- **Scientific Validation:** There is no implementation to test objective task scores under affective-framed vs. neutral prompts.
- **Action Required:** Procure an isolated third-party task set (zero overlap with authored concepts) and implement the evaluation logic utilizing the unframed baseline control.

## 4. E0 (Emergence-vs-Injection / Program C Central Test)
**Status: FATALLY FLAWED (Requires Total Rewrite)**
- **Implementation Status:** `experiments/E0/run.py` exists but is a mock stub rather than a rigorous test.
- **Scientific Validation:** It uses dummy data generation loops instead of the required synthetic nonlinear HMM sequences. It fails to implement the required control conditions (C1, C2, C3). Worst of all, it implements and computes the **[REJECTED]** `free_energy` metric instead of the proper scoring loss ($L$) and the required null-referenced emergence statistic ($M$).
- **Action Required:** Rewrite `E0/run.py` to strictly adhere to `SCIENTIFIC_EXECUTION_SPEC.md`. Remove `free_energy` computations completely. Implement actual predictive tracking and the NMI-based $M$ calculation.
