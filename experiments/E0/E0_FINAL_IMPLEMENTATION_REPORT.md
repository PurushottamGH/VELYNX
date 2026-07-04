# E0 — Final Implementation Report

**[FACT]** E0 is the central H* experiment: emergence-vs-injection discrimination on a nonlinear-latent stream. This report documents the final engineering state.

---

## 1. Experiment Design

### Conditions
| ID | Name | Description |
|----|------|-------------|
| **T** | Treatment | Error-gated growth ON (MDL trigger: G > λ_model) |
| **C1** | Fixed-capacity | No growth, predictor capacity fixed at init |
| **C2** | Capacity-matched | Same growth count as T, at random times (error-decoupled) |
| **C3** | Shuffled-input | Temporal order destroyed, marginals preserved |

### Dependent Variables
- **DV-a:** Held-out predictive log-likelihood (proper scoring rule L = -log P_θ)
- **DV-b:** Emergence statistic M = NMI(learned, true) - NMI(learned, shuffled)

### Kill Criteria (PROGRAM_D_CANONICAL.md §6)
- T fails to beat BOTH C1 and C2 on DV-a at p < 0.01 across ≥ 5 seeds
- OR DV-b within noise of shuffled control (M ≤ 0.05 margin)
- After two honest attempts → H* falsified for this environment class

---

## 2. Core Components

| Component | File | Description |
|-----------|------|-------------|
| Environment | `experiments/E0/dataset.py` | Nonlinear latent Markov chain with 3rd-order polynomial + sinusoidal observation mixing |
| Predictor | `core/predictors/dirichlet_markov.py` | Growable conjugate Dirichlet-Markov predictor |
| MDL Trigger | `core/mdl/mdl_growth.py` | λ_model = k·b + n·log₂N (derived, non-configurable) |
| Analysis | `experiments/E0/analysis.py` | DV-a computation (held-out LL), DV-b computation (M statistic) |
| Decision | `experiments/E0/decision.py` | Paired t-test, bootstrap, two-attempt falsification protocol |
| Runner | `experiments/E0/run.py` | Condition runners, single-seed runner, multi-seed runner |
| Leakage check | `experiments/E0/leakage_check.py` | Offline nonlinearity verification |

---

## 3. Blocker Resolution

### Blocker 1 — C2 Capacity-Matched ✅
C2 in `apply_growth_at_random_times()` receives exact growth count from T. Growth positions are uniformly random, independent of prediction error. Verified by `TestC2CapacityMatched`.

### Blocker 2 — Default Seeds >= 5 ✅
- `DEFAULT_CONFIG.num_seeds = 5`
- `E0Decider.min_seeds = 5`  
- `experiment_registry.yaml` — `num_seeds: 5`
- `velynx_cli.py` — `e0 --num-seeds 5`
- `run_multi_seed()` — iterates over N seeds, produces aggregated pass/kill decision

### Blocker 3 — Latent-State Correctness ✅
- `true_latent_states` captured from `env.step()` in every condition runner
- `latent_states` captured from `predictor.current_state` — separate variable
- `analyze_conditions()` raises `KeyError` if T has no `true_latent_states`
- Verified by `TestLatentStateRegression`

### Blocker 4 — Growth Ordering ✅
- `_hypothetical_entropy_after_growth()` computes entropy without calling `grow()`
- `predictor.grow()` called only after `should_grow()` returns True
- Per-step log records gain; every growth event has gain > 0
- Verified by `TestGrowthOrderingRegression`

---

## 4. Canonical Compliance

| Requirement | Status | Evidence |
|-------------|--------|----------|
| λ_model = k·b + n·log₂N | ✅ | `core/mdl/mdl_growth.py:35` — derived, non-configurable |
| M = NMI(true) - NMI(shuffled) | ✅ | `experiments/E0/analysis.py:87` — null-referenced |
| Log score L = -log P_θ | ✅ | `core/measurement/proper_scoring.py:75` — unique proper scoring rule |
| No free_energy in E0 code | ✅ | Grep: zero matches in `experiments/E0/` and `core/` |
| No graph_isomorphism | ✅ | Grep: zero matches in `experiments/E0/` and `core/` |
| No belief_model | ✅ | Grep: zero matches in `experiments/E0/` and `core/` |
| Deterministic execution | ✅ | Same seed → identical results (tested) |
| Reproducible artifacts | ✅ | All results JSON-serializable |

---

## 5. Test Summary

| Suite | Tests | Pass | Fail | Skip |
|-------|-------|------|------|------|
| `test_core_canonical.py` | 29 | 28 | 0 | 1 |
| `test_e0_components.py` | 57 | 57 | 0 | 0 |
| `test_e0_pipeline.py` | 15 | 15 | 0 | 0 |
| **Total** | **101** | **100** | **0** | **1** |

---

## 6. Usage

```bash
# Run E0 with default 5 seeds
python -m experiments.E0.run

# Run E0 with 10 seeds
python -m experiments.E0.run --num-seeds 10

# Run via CLI
python velynx_cli.py e0 --num-seeds 5

# Run with custom config
python velynx_cli.py e0 --config experiments/E0/config.json --num-seeds 5
```

---

## 7. Status

**E0 engineering implementation: COMPLETE.**

Waiting for:
- Gemini scientific certification
- Claude Sonnet integration sign-off
