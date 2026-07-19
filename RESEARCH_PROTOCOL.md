# Research Protocol: Project P1

This protocol defines the scientific method, hypothesis registration, experimental calibration gates, and replication protocols for Project P1 (Program D).

---

## 1. Scientific Method & Hypotheses

Project P1 is governed by the principles of Program D—an audit-and-falsification protocol over inherited Programs A/B/C. 

### Core Scientific Guidelines
1.  **Hypothesis Constraint**: No new hypotheses may be introduced without pre-registration. New mechanisms must only refine, test, or falsify inherited hypotheses ($H^*, H_1, H_2$).
2.  **Null Hypothesis Testing**: Any new mechanism or primitive must be operationally distinguished from a null/random baseline (e.g. `shuffled_input` or random walk controls). If it cannot be distinguished, it is a delete candidate.
3.  **No Anthropomorphism**: Live code, variables, and documentation must not contain anthropomorphic terms (e.g., mind, soul, belief, understanding, curiosity).

---

## 2. Experimental Execution

### Pre-Registration
Every experiment (such as `EXP0`, `EXP1`, `E0`) must have a corresponding pre-registration document in `theory/preregistrations/` defining:
*   The hypothesis under test.
*   The calibration metrics (e.g., Expected Calibration Error - ECE).
*   The success thresholds.
*   The dataset and seed specifications.

### Execution Steps
1.  **Environment Sync**: Install dependencies from `requirements.txt`.
2.  **Configuration**: Use the configuration files located in `configs/` (e.g., `baseline.json`, `noisy.json`).
3.  **Run Command**: Execute the experiment entry point (e.g. `python experiments/E0/run.py`).
4.  **Analysis**: Execute the analysis script to extract metrics and output them to `evidence/`.

---

## 3. Replication & Regression Gates

*   **100% Pass Rate**: The test suite (`pytest tests/`) must return a 100% pass rate.
*   **Regression Gate**: Any code modifications must pass through `tests/validation/regression.py` to ensure no regression in historical model performance or metric extraction.
*   **Frozen Constants**: The following parameters are locked and cannot be adjusted without explicit auditor approval:
    *   $\text{Bits per parameter } b = 1.0$
    *   $\text{Model cost formulation } \lambda_{\text{model}} = k \cdot b + n \cdot \log_2(N)$
    *   $\text{ECE threshold } < 0.10$
    *   $\text{Emergence margin } M = 0.05$ above shuffled null.
