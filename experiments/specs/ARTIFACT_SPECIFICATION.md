# ARTIFACT SPECIFICATION

**[FACT]** Reproducibility demands precise and structured outputs. This document specifies the required file layouts, schemas, and naming conventions for all outputs.

## Directory Layout
Every experiment execution must produce a timestamped run directory.
```
artifacts/
├── <EXPERIMENT_ID>_<TIMESTAMP>_<GIT_HASH>/
│   ├── manifest.json
│   ├── run.log
│   ├── config_used.json
│   ├── raw_outputs/
│   │   └── predictions.jsonl
│   ├── metrics/
│   │   ├── summary.json
│   │   └── timeseries.csv
│   ├── plots/
│   │   └── <metric>_plot.svg
│   └── checkpoints/
│       └── model_state_<step>.pt
```

## Generated Files & Naming Conventions
- **Manifest:** `manifest.json` - Describes environment, system specs, commit hash.
- **Log Files:** `run.log` - Standard output/error with timestamps and log levels.
- **Config:** `config_used.json` - The exact configuration schema run.
- **Reports:** `<EXPERIMENT_ID>_report.md` - Final tagged report.

## CSV Schemas

### `exp1_ece_metrics.csv`
| query_id | predicted_tier | empirical_correctness | is_control |
|----------|----------------|-----------------------|------------|
| string   | string         | int (0/1)             | boolean    |

### `exp2_task_scores.csv`
| task_id | condition | score | execution_time_ms |
|---------|-----------|-------|-------------------|
| string  | string    | float | float             |

### `e0_loglikelihoods.csv`
| seed | step | condition | log_likelihood |
|------|------|-----------|----------------|
| int  | int  | string    | float          |

### `e0_m_statistic_results.csv`
| seed | condition | nmi_true | nmi_shuffled | m_statistic |
|------|-----------|----------|--------------|-------------|
| int  | string    | float    | float        | float       |

## JSON Schemas
### `manifest.json`
```json
{
  "experiment_id": "E0",
  "timestamp": "2026-07-03T12:00:00Z",
  "git_hash": "a1b2c3d4",
  "python_version": "3.11.0",
  "random_seed": 42
}
```

## Plot Specifications
- **Format:** SVG for vectors, PNG for raster fallback.
- **Styling:** Matplotlib/Seaborn, dark/light agnostic.
- **Axis labels:** Mandatory units.
- **Titles:** Must include Experiment ID and N-value.
- **Legends:** Explicit naming of all series (e.g., T vs C1 vs C2 vs C3).

## Model Checkpoints
- **Format:** Binary `.pt` or `.safetensors`.
- **Contents:** Must only contain the mathematical primitive arrays (transition matrices, capacities, Dirichlet counts). NO anthropomorphic naming (e.g., no `soul_weights`).
