# Requirement Traceability — Sprint 1.1.1 Final Reconciliation

## Priority Mappings

| Priority | Requirement | Proof Artifact | Status |
|----------|-------------|----------------|--------|
| P0 | Artifact provenance — answer commit hash, timing, and pre-existing vs new changes | `01_manifest.json` (commit `57516757`); `02_git_diff_summary.md` (delineation of F1); `git show HEAD:experiments/E0/run.py` (committed stub); `git diff HEAD -- experiments/E0/run.py` (working tree delta) | ✅ Answered |
| P1 | Fix C2 data leakage — C2 must evaluate on held-out test sequence, not last 20% of training | `experiments/E0/run.py` line 618 (test_steps passed to apply_growth_at_random_times); line 359 (test_steps passed in run_fixed_capacity fallback); `05_metrics.json` (C2 test_n=1999 per seed); `06_statistical_results.md` (verification section) | ✅ Fixed |
| P2 | Growth diagnostics — full table of every MDL check across all 5 seeds | `growth_diagnostics.md` (90 rows covering all seeds); `05_metrics.json` (growth_diagnostics section); `06_statistical_results.md` (growth diagnostics summary) | ✅ Generated |
| P3 | Re-run corrected 5-seed production experiment | `artifacts/experiments/E0/run_20260704T131335Z_s42_n5/aggregated_results.json` (full results); `05_metrics.json` (per-seed metrics); `06_statistical_results.md` (narrative) | ✅ Completed |
| P4 | Power analysis (conditional on results) | `06_statistical_results.md` (power analysis section); `05_metrics.json` (growth_diagnostics.diagnosis: "Growth never fired — effect size exactly zero") | ✅ Completed |

## Evidence File Inventory

| File | Path | Description |
|------|------|-------------|
| Manifest | `evidence/01_manifest.json` | Artifact provenance, remediation inventory, result summary |
| Git diff summary | `evidence/02_git_diff_summary.md` | Sprint 1.1 code changes (includes F1, W1, W4, held-out, FWER) |
| Test output | `evidence/04_test_output.txt` | Test results from Sprint 1.1 (100 passed, 1 skipped) |
| Metrics JSON | `evidence/05_metrics.json` | Structured per-seed metrics from corrected 5-seed run |
| Statistical results | `evidence/06_statistical_results.md` | Narrative with DV-a, DV-b, growth diagnostics, C2 fix verification |
| Traceability | `evidence/09_requirement_traceability.md` | This file — mapping priorities to artifacts |
| Sprint report | `evidence/10_sprint_report.md` | Sprint 1.1.1 reconciliation report |
| Growth diagnostics | `artifacts/experiments/E0/run_20260704T131335Z_s42_n5/growth_diagnostics.md` | Full 90-row MDL check table across all seeds |
| Aggregated results | `artifacts/experiments/E0/run_20260704T131335Z_s42_n5/aggregated_results.json` | Full experiment output (5 seeds) |
| Run config | `artifacts/experiments/E0/run_20260704T131335Z_s42_n5/config.json` | Experiment configuration |
| C2 fix code | `experiments/E0/run.py` (lines 359, 618) | Source code changes for C2 data leakage fix |

## Code Changes

| File | Change | Lines |
|------|--------|-------|
| `experiments/E0/run.py` | C2 fix: pass test_steps to apply_growth_at_random_times in run_single_seed | ~618 |
| `experiments/E0/run.py` | C2 fix: pass test_steps in run_fixed_capacity fallback when growth_count <= 0 | ~359 |
| `experiments/E0/growth_diagnostics.py` | **New file**: growth diagnostics extraction and formatting script | Full file |

## Verification Status

| Check | Result | Evidence |
|-------|--------|----------|
| C2 test_n matches T | ✅ Pass | `05_metrics.json` per_seed: all C2 test_n=1999, matching T |
| C2 evaluated on independent held-out | ✅ Pass | C2 test_log_likelihoods populated with 1999 entries per seed |
| Growth diagnostics covers all 90 MDL checks | ✅ Pass | `growth_diagnostics.md` with 90 rows across 5 seeds |
| Growth events = 0 | ✅ Confirmed | 0 growth events across all seeds and conditions |
| DV-a still FAIL after fix | ✅ Confirmed | Paired t-test: zero variance, NaN p-values |
| DV-b PASS | ✅ Confirmed | M=0.301 > margin=0.051 |
| Effect size | Exactly zero | T==C1==C2 produce identical models (0 growth), so δ = 0 |
