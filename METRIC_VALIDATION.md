# METRIC VALIDATION

This document verifies the metrics, statistics, and kill criteria for each experiment.

## 1. EXP-0
- **Metrics**: Concept detection accuracy (%). Compliant.
- **Statistics**: Uses McNemar's exact test and bootstrap CI for paired nominal data. Compliant.
- **Kill Criteria**: Detects if accuracy collapses to noise on paraphrases.
- **Status**: Ready.

## 2. EXP-1
- **Metrics**: Expected Calibration Error (ECE), Accuracy per tier. (Unimplemented).
- **Statistics**: Chi-square test for independence. (Unimplemented).
- **Kill Criteria**: $ECE \geq 0.10$ or accuracy is statistically independent of tier. (Unimplemented).
- **Status**: Blocked.

## 3. EXP-2
- **Metrics**: Objective task success rate. (Unimplemented).
- **Statistics**: Independent samples t-test / Mann-Whitney U test. (Unimplemented).
- **Kill Criteria**: No statistically significant task-outcome difference. (Unimplemented).
- **Status**: Blocked.

## 4. E0
- **Metrics**: Held-out predictive log-likelihood (DV-a) and Emergence statistic $M$ (DV-b). The current script incorrectly uses `free_energy`.
- **Statistics**: Paired t-tests ($p < 0.01$). Currently missing.
- **Kill Criteria**: Treatment fails to beat both C1 and C2 on DV-a, or DV-b within noise of C3. Currently missing.
- **Status**: Scientifically invalid.
