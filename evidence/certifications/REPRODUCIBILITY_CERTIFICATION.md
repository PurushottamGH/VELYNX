# REPRODUCIBILITY CERTIFICATION

This document verifies the reproducibility guarantees of Program D experiments.

## 1. EXP-0
- **Reproducibility Verification**: Explicit seed (`DEFAULT_SEED=1`), dataset loads exact 64 query text corpus, fixed leakage check.
- **Verdict**: Fully reproducible.
- **Status**: Ready.

## 2. EXP-1
- **Reproducibility Verification**: No fixed evaluation query set or ground-truth labels found.
- **Verdict**: Not reproducible.
- **Status**: Blocked.

## 3. EXP-2
- **Reproducibility Verification**: No frozen third-party task set or fixed prompt templates found.
- **Verdict**: Not reproducible.
- **Status**: Blocked.

## 4. E0
- **Reproducibility Verification**: The current script does not use a real synthetic environment generator parameters, nor the hardcoded MDL ledger formula $\lambda_{model} = k \cdot b + n \cdot \log_2 N$.
- **Verdict**: Irreproducible and invalid.
- **Status**: Scientifically invalid.
