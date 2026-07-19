# SPRINT 1 — Final Engineering Report

**[FACT]** Sprint 1 covers the E0 experiment implementation, canonical metric compliance, and blocker resolution for Program D.

---

## 1. Work Completed

### Blocker 1 — C2 Capacity-Matched
- **Status:** RESOLVED
- **Verification:** C2 receives exact growth event count from T via `run_single_seed` → `apply_growth_at_random_times`
- **Tests:** `TestC2CapacityMatched` (4 tests) — same count, same final capacity, random timing uncorrelated with error
- **Files:** `experiments/E0/run.py:342-415` — `apply_growth_at_random_times` with exact count

### Blocker 2 — Default Seeds >= 5
- **Status:** RESOLVED
- **Config:** `DEFAULT_CONFIG.num_seeds = 5` in `experiments/E0/run.py:78`
- **CLI:** `velynx_cli.py` now supports `e0` subcommand with `--num-seeds` (default 5)
- **Registry:** `experiment_registry.yaml` updated with `num_seeds: 5`
- **Parameter registry:** Updated with canonical E0 parameters
- **Multi-seed runner:** New `run_multi_seed()` function in `experiments/E0/run.py:371-452`
- **Tests:** `TestMultiSeedRunner` (5 tests) — verifies all seeds run, aggregated decision produced

### Blocker 3 — Latent-State Correctness
- **Status:** RESOLVED
- **Verification:** M statistic uses ONLY `true_latent_states` from `env.step()`, never predictor-derived states
- **Guards:** `analyze_conditions` raises `KeyError` if `true_latent_states` missing for T condition
- **Tests:** `TestLatentStateRegression` (5 tests) — separate lists, deterministic env, missing key raises, non-T conditions handled

### Blocker 4 — Growth Ordering
- **Status:** RESOLVED
- **Verification:** `predictor.grow()` called ONLY after `should_grow()` returns True (G > λ_model)
- **Hypothetical computation:** `_hypothetical_entropy_after_growth()` computes entropy WITHOUT modifying predictor state
- **Tests:** `TestGrowthOrderingRegression` (3 tests) — every growth event has positive gain, no growth when gain <= 0, hypothetical entropy preserves capacity

### Registry Cleanup
- `experiment_registry.yaml`: EXP3/EXP4 marked [REJECTED] status=archived; R1/R3F archived
- `parameter_registry.yaml`: Removed all [REJECTED] free_energy entries; replaced with canonical E0 parameters
- No banned symbols (`free_energy`, `graph_isomorphism`, `belief_model`) in `core/` or `experiments/E0/`

---

## 2. Files Modified

| File | Change |
|------|--------|
| `experiments/E0/run.py` | Added `run_multi_seed()`, updated `main()` with `num_seeds`, added `--num-seeds` CLI arg, imported `M_STATISTIC_MARGIN` |
| `velynx_cli.py` | Added `e0` subcommand with `--seed`, `--num-seeds`, `--config`, `--output-dir` |
| `experiment_registry.yaml` | Updated E0 with canonical components + `num_seeds: 5`; archived EXP3/EXP4 as [REJECTED]; archived R1/R3F |
| `parameter_registry.yaml` | Replaced legacy free_energy entries with canonical E0 parameter spec; added mdl.lambda_model derivation |
| `experiments/E0/config.json` | Already had `num_seeds: 5` (verified) |
| `tests/unit/test_e0_components.py` | Added `TestLatentStateRegression` (5 tests), `TestGrowthOrderingRegression` (3 tests), `TestMultiSeedRunner` (5 tests) |

---

## 3. Tests Added

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestLatentStateRegression` | 5 | Blocker 3: latent-state separation, deterministic env, KeyError guards |
| `TestGrowthOrderingRegression` | 3 | Blocker 4: every growth has gain>0, no speculative growth, hypothetical entropy preserves capacity |
| `TestMultiSeedRunner` | 5 | Blocker 2: multi-seed execution, aggregated decision, env seed independence, min seeds threshold |

---

## 4. Tests Passed

- **Unit tests (core):** 28/28 passed, 1 skipped (banned symbols — run manually)
- **Unit tests (E0):** 57/57 passed
- **Integration tests (E0):** 15/15 passed
- **Total:** 100/100 passed (1 skipped)

---

## 5. Remaining Blockers

**None.** All four Sprint 1 blockers are resolved.

---

## 6. Estimated Completion

Sprint 1 engineering: **COMPLETE**.

Waiting for:
- Gemini (Scientific Validation Lead) — scientific certification
- Claude Sonnet (Integration Lead) — integration sign-off

**Do not begin Sprint 2 until certification is received.**

---

## Appendix: Validation Summary

- All E0 condition runners verified (T, C1, C2, C3)
- C2 capacity-matched to T (same growth count, random timing)
- Default seeds = 5 (config, registry, CLI, decider)
- M statistic uses only environment true latent states
- Growth occurs only after G > λ_model (no speculative growth)
- No `free_energy` references in executable E0 code
- Canonical metrics only (log score, NMI-based M, derived λ_model)
- Deterministic execution verified (same seed → same results)
- All results JSON-serializable for reproducible artifacts
