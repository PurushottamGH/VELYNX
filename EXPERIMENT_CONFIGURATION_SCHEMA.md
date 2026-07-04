# EXPERIMENT CONFIGURATION SCHEMA

**[FACT]** This document defines the exact schema required for each experiment. No hyperparameter tuning is permitted. Configs are frozen JSON/YAML files.

## Global Schema Rules
- `experiment_id`: String (EXP-0, EXP-1, EXP-2, E0).
- `random_seed`: Integer (Strictly controls the central PRNG).
- `execution_limits`: Defines compute boundaries.

## 1. EXP-0 Configuration Schema
```json
{
  "experiment_id": "EXP-0",
  "random_seed": 42,
  "dataset": {
    "name": "benchmark_paraphrase_v1",
    "path": "data/exp0_queries.json",
    "format": "json_pairs",
    "validation_rules": "must_contain_64_interleaved_queries"
  },
  "hyperparameters": {
    "wipe_state_between_trials": true,
    "hebbian_learning": false
  },
  "stopping_criteria": {
    "max_trials": 64
  },
  "logging": {
    "level": "INFO",
    "log_file": "artifacts/EXP-0/run.log"
  },
  "artifacts": {
    "output_dir": "artifacts/EXP-0",
    "metrics_file": "exp0_results.json"
  },
  "metrics": ["concept_detection_accuracy"],
  "outputs": ["binary_success_per_trial"]
}
```

## 2. EXP-1 Configuration Schema
```json
{
  "experiment_id": "EXP-1",
  "random_seed": 42,
  "dataset": {
    "name": "calibration_queries_v1",
    "path": "data/exp1_queries.json",
    "format": "json_records"
  },
  "hyperparameters": {
    "retrieval_backend": "program_a_core",
    "confidence_tiers": ["CERTAIN", "PROBABLE", "DEBATED", "UNKNOWN"],
    "control_backend": "bm25_random_tier"
  },
  "stopping_criteria": {
    "max_queries": 200
  },
  "logging": {
    "level": "INFO",
    "log_file": "artifacts/EXP-1/run.log"
  },
  "artifacts": {
    "output_dir": "artifacts/EXP-1",
    "metrics_file": "exp1_ece_metrics.csv"
  },
  "metrics": ["expected_calibration_error", "accuracy_per_tier"],
  "outputs": ["predicted_tier", "actual_correctness"]
}
```

## 3. EXP-2 Configuration Schema
```json
{
  "experiment_id": "EXP-2",
  "random_seed": 42,
  "dataset": {
    "name": "third_party_objective_tasks",
    "path": "data/exp2_tasks.json",
    "format": "json_records"
  },
  "hyperparameters": {
    "llm_temperature": 0.0,
    "conditions": ["affective_framed", "unframed_neutral"]
  },
  "stopping_criteria": {
    "max_tasks": 100
  },
  "logging": {
    "level": "INFO",
    "log_file": "artifacts/EXP-2/run.log"
  },
  "artifacts": {
    "output_dir": "artifacts/EXP-2",
    "metrics_file": "exp2_task_scores.csv"
  },
  "metrics": ["objective_task_success_rate"],
  "outputs": ["task_id", "condition", "score"],
  "validation_rules": {
    "no_soul_graph_dependency": true
  }
}
```

## 4. E0 Configuration Schema
```json
{
  "experiment_id": "E0",
  "random_seed": 42,
  "dataset": {
    "name": "synthetic_hmm_nonlinear",
    "generation_seed": 101,
    "num_latent_states": 10,
    "sequence_length": 50000
  },
  "hyperparameters": {
    "mdl_b_constant": 1.5,
    "mdl_n_multiplier": 1.0,
    "capacity_growth_operator": "enabled",
    "conditions": ["T", "C1", "C2", "C3"]
  },
  "stopping_criteria": {
    "max_steps": 50000
  },
  "logging": {
    "level": "DEBUG",
    "log_file": "artifacts/E0/run.log"
  },
  "artifacts": {
    "output_dir": "artifacts/E0",
    "metrics_file": "e0_metrics.csv"
  },
  "metrics": ["held_out_ll", "m_statistic"],
  "outputs": ["step_ll", "learned_partition"],
  "validation_rules": {
    "mdl_threshold_hardcoded": true,
    "no_seeded_concepts": true
  }
}
```
