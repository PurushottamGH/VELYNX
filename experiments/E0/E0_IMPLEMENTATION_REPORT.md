# E0 Implementation Report — Sprint 1.1 Remediation

**Date:** 2026-07-04
**Status:** Integration Review #001 remediated — awaiting Review #002
**Tests:** 100 passed, 1 skipped, 0 failures

---

## Objective Summary

The canonical E0 experiment (H* decider) is implemented and scientifically valid. The experiment discriminates between genuine emergent structure and designer-injected statistics on a nonlinear latent stream. All deferred issues from the initial Sprint 1 delivery are resolved.

| Objective | Status | Evidence |
|-----------|--------|----------|
| F1: DV-a category error | ✅ | `predictor.log_predictive_probability(obs_list, context)` at all 4 sites |
| W1: Deterministic seeding | ✅ | `hashlib.sha256` in SeedRegistry |
| W2: No private attribute access | ✅ | `predictor.hypothetical_entropy_after_growth()` used |
| W4: Dead code removed | ✅ | Imports cleaned from run.py and analysis.py |
| Independent held-out | ✅ | Fresh environment (seed +9999), no predictor update |
| Holm-Bonferroni FWER | ✅ | α=0.01, step-down across T vs C1, T vs C2 |
| M threshold derived | ✅ | `2 * std(M) / sqrt(n)` from per-seed null distribution |
| Production 5-seed run | ✅ | 27.5s, FAIL (DV-a), artifacts archived |

## Test Results (from `pytest -v`)

```
100 passed, 1 skipped, 3 warnings in 13.88s
```

- `tests/unit/test_core_canonical.py`: 28 passed — lambda model, log score, NMI, predictor, MDL gain
- `tests/unit/test_e0_components.py`: 56 passed — environment, leakage, seeds, analysis, decision, condition runners, C2 matching, growth ordering, latent states
- `tests/integration/test_e0_pipeline.py`: 16 passed — end-to-end pipeline, analysis, decision, artifacts, seeded reproducibility

## Production Run Output

```
python -m experiments.E0.run --seed 42 --num-seeds 5
[E0] Multi-seed run: 5 seeds starting at base_seed=42
[E0]   seed 42: FAIL (DV-a: T did not beat both controls) (5.5s)
[E0]   seed 43: FAIL (DV-a: T did not beat both controls) (5.6s)
[E0]   seed 44: FAIL (DV-a: T did not beat both controls) (6.3s)
[E0]   seed 45: FAIL (DV-a: T did not beat both controls) (5.1s)
[E0]   seed 46: FAIL (DV-a: T did not beat both controls) (5.1s)
[E0] Multi-seed run completed in 27.5s
[E0] Aggregated decision: FAIL (DV-a)
[E0] Seeds: 5 / 5 required
```

## Evidence Package

Complete evidence package available at `evidence/`:

```
evidence/
├── 01_manifest.json                  — Git hash, dep versions, config
├── 02_git_diff_summary.md            — All changes documented
├── 03_ci_output.txt                  — CI and production run logs
├── 04_test_output.txt                — Full 101-test output
├── 05_metrics.json                   — Experiment metrics and verdicts
├── 06_statistical_results.md         — Holm-Bonferroni, M threshold
├── 07_reproducibility.json           — Dual-run verification
├── 08_artifact_inventory.md          — File inventory
├── 09_requirement_traceability.md    — F1, W1-W4, held-out, FWER, M → proof
├── 10_sprint_report.md               — Full sprint report
└── experiment_logs/                  — Production run artifacts
    ├── run_20260704T125008Z_s42_n5/  (verification run)
    └── run_20260704T125108Z_s42_n5/  (production run)
```

## Files Changed

| File | Change |
|------|--------|
| `experiments/E0/run.py` | F1 scoring fix, W1 hashlib, W2 public entropy, W4 dead imports, held-out env |
| `experiments/E0/analysis.py` | W4 dead imports, held-out analysis integration |
| `experiments/E0/decision.py` | Holm-Bonferroni, M threshold derivation, held-out LL extraction |
| `core/predictors/dirichlet_markov.py` | `_compute_stationary` fallback fix (IndexError on hypothetical growth) |
| `experiments/E0/dataset.py` | Exposed `_transition_alpha` for test env creation |
| `experiments/E0/E0_IMPLEMENTATION_REPORT.md` | Regenerated from actual output |

## How to Run

```bash
# Tests
python -m pytest tests/unit/test_e0_components.py tests/integration/test_e0_pipeline.py tests/unit/test_core_canonical.py -v

# Production 5-seed run
python -m experiments.E0.run --seed 42 --num-seeds 5

# Custom config
python -m experiments.E0.run --seed 42 --num-seeds 5 --config experiments/E0/config.json
```
