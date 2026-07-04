# Artifact Inventory — Sprint 1.1 Evidence Package

## Evidence Package Structure

```
evidence/
├── 01_manifest.json                  [✅] Git hash, dep versions, config
├── 02_git_diff_summary.md            [✅] All changes documented with line references
├── 03_ci_output.txt                  [✅] CI and production run logs
├── 04_test_output.txt                [✅] Full 101-test output (100 passed, 1 skipped)
├── 05_metrics.json                   [✅] Experiment metrics and verdicts
├── 06_statistical_results.md         [✅] Holm-Bonferroni, M threshold, results
├── 07_reproducibility.json           [✅] Dual-run verification, seed registry
├── 08_artifact_inventory.md          [✅] This file
├── 09_requirement_traceability.md    [✅] Maps F1, W1-W4, held-out, FWER, M → proof
├── 10_sprint_report.md               [✅] Full sprint report
└── experiment_logs/
    ├── run_20260704T125008Z_s42_n5/  [✅] First production run (verification)
    │   ├── config.json
    │   └── aggregated_results.json
    └── run_20260704T125108Z_s42_n5/  [✅] Second production run (reproducibility)
        ├── config.json
        └── aggregated_results.json
```

## Source Files Modified

| File | Change Type | Lines Changed |
|------|------------|---------------|
| `experiments/E0/run.py` | F1, W1, W2, W4, held-out | ~80 lines modified |
| `experiments/E0/analysis.py` | W4, held-out | ~20 lines modified |
| `experiments/E0/decision.py` | FWER, M threshold, held-out | ~70 lines added |
| `core/predictors/dirichlet_markov.py` | Bugfix | ~15 lines modified |
| `experiments/E0/dataset.py` | Expose attribute | 1 line added |

## Test Files (unchanged)

| File | Tests |
|------|-------|
| `tests/unit/test_e0_components.py` | 56 tests |
| `tests/integration/test_e0_pipeline.py` | 16 tests |
| `tests/unit/test_core_canonical.py` | 29 tests |

## Produced Artifacts

| Artifact | Path |
|----------|------|
| Production aggregated results | `evidence/experiment_logs/run_20260704T125108Z_s42_n5/aggregated_results.json` |
| Production config | `evidence/experiment_logs/run_20260704T125108Z_s42_n5/config.json` |
| Verification aggregated results | `evidence/experiment_logs/run_20260704T125008Z_s42_n5/aggregated_results.json` |
