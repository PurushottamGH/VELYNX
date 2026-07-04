# Changelog — Program D Sprint 1

All notable changes for Sprint 1 engineering closure.

---

## [2026-07-04] Sprint 1 Final

### Added
- **Multi-seed experiment runner** (`experiments/E0/run.py:run_multi_seed`): Runs N seeds, aggregates results, produces pass/kill decision via `E0Decider.evaluate_multi_seed()`. Default: 5 seeds per canonical requirement.
- **CLI E0 subcommand** (`velynx_cli.py`): `python velynx_cli.py e0 --num-seeds 5` to run E0 from command line.
- **Regression tests** (`tests/unit/test_e0_components.py`):
  - `TestLatentStateRegression` (5 tests): Verifies M statistic uses ONLY environment `true_latent_states`, never predictor-derived states.
  - `TestGrowthOrderingRegression` (3 tests): Verifies `predictor.grow()` called only after G > λ_model; no speculative growth.
  - `TestMultiSeedRunner` (5 tests): Verifies multi-seed execution, aggregated decision, env seed independence, min seeds threshold.

### Changed
- **`experiments/E0/run.py`**: `main()` now accepts `num_seeds` parameter; CLI supports `--num-seeds`.
- **`velynx_cli.py`**: Added `e0` subcommand with full argument support.
- **`experiment_registry.yaml`**: E0 entry updated with canonical components and `num_seeds: 5`. EXP3/EXP4 marked `[REJECTED]` status=archived. R1/R3F archived.
- **`parameter_registry.yaml`**: Replaced all `[REJECTED]` free_energy entries with canonical E0 parameter specification. Added MDL `lambda_model` derivation formula.

### Fixed
- **Blocker 1 (C2 capacity-matched)**: Verified correct. C2 receives exact growth count from T via `run_single_seed` → `apply_growth_at_random_times`.
- **Blocker 2 (default seeds >= 5)**: Verified across config, registry, manifests, CLI, decider.
- **Blocker 3 (latent-state correctness)**: Verified. `analyze_conditions` raises `KeyError` if `true_latent_states` missing for T condition.
- **Blocker 4 (growth ordering)**: Verified. `predictor.grow()` called only after `should_grow()` returns True.

### Removed
- `[REJECTED]` free_energy entries from `parameter_registry.yaml` (archived as comments).
- EXP3/EXP4 as live experiments in registry (marked `[REJECTED]` archived).

### Compliance
- Zero `free_energy` references in executable E0 code.
- Zero `graph_isomorphism` references in executable E0 code.
- Zero `belief_model` references in executable E0 code.
- Canonical metrics only: log score L = -log P_θ, null-referenced M = NMI(true) - NMI(shuffled), derived λ_model = k·b + n·log₂N.
- Deterministic execution verified (same seed → same results).
- All results JSON-serializable for reproducible artifacts.
