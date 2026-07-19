# IMPLEMENTATION BLOCKERS

**[FACT]** The following scientific ambiguities and residual legacy code elements physically prevent the correct engineering implementation of Program D. These must be resolved by engineering before any experiment runs.

---

## 1. Missing Precondition Code (EXP-0)
* **Blocker:** `experiments/EXP-0/` is currently missing from the engineering repository manifest (`repository_v2.md`).
* **Resolution:** Engineers must implement the EXP-0 test harness.
* **Strict Constraint:** The harness must contain hardcoded logic to wipe the semantic graph and episodic memory state completely between every trial. Without this, Hebbian leakage will invalidate the test.

## 2. Unwired/Configurable MDL Threshold
* **Blocker:** Legacy documentation (`SPECIFICATION §2.4`) allows $\lambda$ to be treated as a configurable threshold.
* **Resolution:** The code must be rigidly wired to the exact mathematical ledger: $\lambda_{model} = k \cdot b + n \cdot \log_2 N$. Exposing this as a tunable float in a JSON config is a critical failure.

## 3. Circular Dependency in EXP-2
* **Blocker:** The migration plan (`repository_v2.md:152-158`) currently wires `program_b/soul_graph` and `concepts.json` as dependencies for EXP-2.
* **Resolution:** This is a fatal circularity violation. EXP-2 must be executed against an isolated, third-party task set entirely decoupled from the 32 seeded concepts.

## 4. Illegal Emergence Metric
* **Blocker:** The "graph isomorphism / topological alignment" metric is ill-defined for a probabilistic predictor and remains in legacy specifications.
* **Resolution:** Engineering must delete any graph-isomorphism code and implement the exact null-referenced NMI statistic: $M = \mathrm{NMI}(\text{learned}, \text{true}) - \mathrm{NMI}(\text{learned}, \text{shuffled})$.

## 5. Ambiguous Calibration Threshold Dead Zone
* **Blocker:** Legacy kill criteria specified an ECE $> 0.15$ for failure, but a pass required $< 0.10$, creating a dead zone.
* **Resolution:** The threshold is unified. Engineering must wire EXP-1 to report `PASS` strictly if $ECE < 0.10$, and `FAIL` otherwise. No other states exist.
