# H1: Calibration Hypothesis

**A live-truth retrieval engine can maintain calibrated uncertainty (ECE < 0.1) when evaluated against ground-truth corpora under distribution shift.**

## Key Predictions

1. Expected Calibration Error (ECE) remains below 0.1 across held-out domains.
2. Confidence scores correlate monotonically with accuracy (AUC-ROC > 0.9).
3. Under distribution shift, recalibration requires fewer than 10 exemplars.

## Experimental Test (EXP1)

- **Measurement:** ECE, AUC-ROC, recalibration sample efficiency.
- **Success criterion:** ECE < 0.1 on held-out domain after ≤10 recalibration examples.
- **Location:** `experiments/EXP1/`

Derived from: VELYNX_v2_PI_Review.md Phase 5 H1
