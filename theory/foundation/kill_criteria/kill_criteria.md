# Program D Kill Criteria

These are the automated gates that determine whether an experiment should be
terminated early (critical) or flagged for review (warning).

## Critical Criteria (Auto-Terminate)

| ID | Criterion | Threshold | Trigger |
|----|-----------|-----------|---------|
| KC-01 | Energy Exhaustion | Free energy > 18.0 | System has fragmented beyond recovery |
| KC-02 | Entropy Collapse | Entropy > 2.0 bits | Predictive uncertainty has collapsed |
| KC-03 | Entropy Collapse (Low) | Entropy < 0.01 bits | System is pathologically certain |
| KC-04 | Divergence | Free energy is NaN or Inf | Numerical instability |

## Warning Criteria (Flag for Review)

| ID | Criterion | Threshold | Trigger |
|----|-----------|-----------|---------|
| KC-05 | Surprise Overload | Surprise > 0.5 | Prediction errors persistently high |
| KC-06 | Structural Overload | Structural load > 2.0 | Too many active clusters/structures |
| KC-07 | Free Energy Plateau | No decrease over 100 ticks | System not learning |

## Implementation

- **Validation:** `scripts/check_kill_criteria.py` runs in CI.
- **Runtime:** `experiments/metrics.py` `MetricsCollector.check_kill_criteria()`.
- **Reporting:** Triggers are logged in `MetricsRecord.kill_criteria_triggered`.
