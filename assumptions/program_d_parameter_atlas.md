# Program D — Parameter Atlas

## Purpose
Catalog all tunable parameters across the system, their default values, locations, and constraints.

---

## 1. COGNITIVE ENGINE PARAMETERS

### 1.1 Free-Energy Coefficients
| Parameter | Default | Location | Description | Constraint |
|-----------|---------|----------|-------------|------------|
| LAMBDA | 1.0 | `validation/metrics.py:29`, `decision_policy.py:79` | Weight on Entropy (H) | [0, ∞) |
| MU | 2.0 | `validation/metrics.py:30`, `decision_policy.py:80` | Weight on Prediction Error (S) | [0, ∞) |
| NU | 0.5 | `validation/metrics.py:31`, `decision_policy.py:81` | Weight on Active Load (A) | [0, ∞) |
| tolerance | 0.0 | `decision_policy.py:186` | Slack on free-energy rule | [0, ∞) |

### 1.2 Thermodynamic State
| Parameter | Default | Location | Description | Constraint |
|-----------|---------|----------|-------------|------------|
| thermodynamic_state | 0.5 | `reasoning_engine.py:306` | System energy (cold→hot) | [0, 1] |
| conf_threshold | 0.55→0.10 | `reasoning_engine.py:792-793` | Confidence floor (cold→hot derived) | [0.05, 0.55] |
| max_depth | 2→6 | `reasoning_engine.py:796` | Max path length (cold→hot) | [2, 6] |
| resolution_margin | 0.25→0.02 | `reasoning_engine.py:798-799` | Contradiction win margin | [0.02, 0.25] |
| max_paths_per_pair | 1→3 | `reasoning_engine.py:801` | Max reasoning paths per concept pair | [1, 3] |

### 1.3 Cognitive Metrics Thresholds
| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| ENTROPY_HIGH | 2.0 | `validation/metrics.py:35` | High entropy threshold (bits) |
| SURPRISE_HIGH | 0.50 | `validation/metrics.py:36` | High surprise threshold |
| SURPRISE_MILD | 0.20 | `validation/metrics.py:37` | Mild surprise threshold |
| PRESSURE_HIGH | 1.00 | `validation/metrics.py:38` | High anomaly pressure |
| PRESSURE_MILD | 0.25 | `validation/metrics.py:39` | Mild anomaly pressure |
| ENERGY_EXHAUSTION | 18.0 | `validation/metrics.py:40` | Exhaustion energy threshold |

## 2. LEARNER PARAMETERS

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| batch_size | 5 | `velynx_core/learner.py:276` | Items learned per batch |
| sleep_between_items | 1.5s | `velynx_core/learner.py:277` | Pause between fetches |
| max_retries | 3 | `velynx_core/learner.py:278` | Max retries per topic |
| min_confidence_threshold | 0.35 | `velynx_core/brain.py:140` | Minimum concept confidence |
| DEFAULT_LEARNING_RATE | 0.1 | `predictive_core.py:25` | Predictive core learning rate |
| DEFAULT_BASELINE_RATE | 0.05 | `predictive_core.py:26` | Baseline update rate |

## 3. SELF-CODER PARAMETERS

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| cycle_interval_seconds | 3600 | `velynx_core/self_coder.py:343` | Self-improvement cycle interval |
| timeout | 30s | `velynx_core/self_coder.py:232` | Sandbox execution timeout |
| memory_limit_mb | 512 | `velynx_core/self_coder.py:233` | Sandbox memory limit |
| BUILD_CHAIN_TIMEOUT_S | 10.0 | `reasoning_engine.py:292` | Reasoning timeout |
| QUALITY_THRESHOLD | 0.70 | `backend/brain.py:48` | KG answer quality gate |
| MAX_RETRY | 2 | `backend/brain.py:49` | Brain retry limit |

## 4. PREDICTIVE CORE

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| decay | 0.001 | `predictive_core.py:60` | Rule decay rate |
| rule_confidence (CERTAIN) | 0.9 | `predictive_core.py:434` | Confidence for CERTAIN edges |
| rule_confidence (PROBABLE) | 0.7 | `predictive_core.py:434` | Confidence for PROBABLE edges |

## 5. CONCEPT BIRTH (MDL)

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| threshold_bits | 0.5 | `concept_birth.py:240` | MDL gain threshold for concept birth |
| min_exception_mass | 0.15 | `concept_birth.py:240` | Minimum exception mass for consideration |
| max_model_bits_per_symbol | 4.0 | `concept_birth.py` | Max bits per symbol for model cost |

## 6. BENCHMARK/EXPERIMENT

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| DEFAULT_TOLERANCE | 0.05 | `regression.py` | Regression gate tolerance (5%) |
| _DEFAULT_MAX_LOG_SIZE | 50000 | `runner.py` | Max experiment log entries |
| _LOG_TRIM_TARGET | 40000 | `runner.py` | Trim target for logs |
| _MAX_MERGES_PER_CYCLE | 3 | `runner.py` | Max C8 merges per cycle |
| _RECENT_VECTORS_MAXLEN | 200 | `runner.py` | Short-term memory buffer |

## Dependencies
- `DEFAULT_LAMBDA/MU/NU` are duplicated in `decision_policy.py` and `validation/metrics.py` — must be kept in sync
- `thermodynamic_state` flows through `reasoning_engine.py` → all downstream thresholds

## Experiments Affected
- All benchmark experiments depend on free-energy coefficients
- Predictive core experiments depend on `DEFAULT_LEARNING_RATE`, `DEFAULT_BASELINE_RATE`
- C8 experiments depend on `_MAX_MERGES_PER_CYCLE`, `_RECENT_VECTORS_MAXLEN`

## Removal Risk
- N/A — this is a catalog, not a removal recommendation

## Regression Tests
- None needed for catalog

## Confidence
- 0.95 for confirmed parameter defaults
- 0.80 for derived parameters (e.g., thermodynamic state → thresholds)
