# ASSUMPTION CLOSURE REPORT

**[FACT]** Every remaining assumption underlying Program D is identified, classified, and wired to a strict closure path. All unnecessary assumptions have been deleted.

---

## 1. Load-Bearing Assumptions

| ID | Assumption | Class | Closure Path |
| :--- | :--- | :--- | :--- |
| **I1** | Prediction error is a sufficient signal to drive representational structure. | Testable | Evaluated explicitly via E0 (Comparison of Error-Gated vs. Random Growth). |
| **I2** | "Emergent structure" is operationally distinguishable from injected/statistically-trivial structure. | Testable | Evaluated explicitly via the $M$ statistic in E0 (Null-referenced NMI). This is the keystone assumption. |
| **I3** | An environment exists that requires non-trivial structure yet is learnable in feasible compute. | Testable | Must be proven *offline* prior to E0 execution using a linear baseline to ensure non-linearity. |
| **I4** | Log-likelihood proper scoring loss ($-\log P_\theta$) is the optimal unique local strict scoring rule. | Proven | Mathematical derivation (Bernardo 1979); requires no experimental closure. |
| **I5** | The trigger for MDL-based growth ($\lambda_{model}$) strictly prevents runaway parameter explosion. | Proven / Derived | Wired to exact ledger arithmetic ($k \cdot b + n \cdot \log_2 N$). |

---

## 2. Experimental / Operational Assumptions

| Assumption | Class | Closure Path |
| :--- | :--- | :--- |
| Third-party objective tasks in EXP-2 do not implicitly require the exact affect categories authored by the designer. | Hidden / Circular | **Mitigated:** Mandatory use of strict external/third-party benchmarks (e.g., standard SWE-bench subsets) to break circularity. |
| ECE $< 0.10$ reflects genuine honest uncertainty rather than bin-boundary hacking. | Designer Injected | **Mitigated:** Bin boundaries must be evenly spaced and locked prior to EXP-1 execution. |
| Concept detection collapses when exact keywords are removed. | Testable | Evaluated directly via EXP-0 precondition test. |

---

## 3. Deleted / Falsified Assumptions (DO NOT IMPLEMENT)

* **[REJECTED]** "Linear combinations of independent heuristic pressures ($E = \lambda H + \mu S + \nu A$) create a valid thermodynamic free-energy equivalent." (Falsified by R1 ablation; mathematically unit-incommensurate).
* **[REJECTED]** "The 32 authored soul concepts represent universal cognitive primitives." (Untestable designer injection).
* **[REJECTED]** "A graph isomorphism metric accurately measures topological emergence for a probabilistic predictor." (Untestable/Circular).
