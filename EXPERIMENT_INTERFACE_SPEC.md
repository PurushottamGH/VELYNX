# EXPERIMENT INTERFACE SPECIFICATION

**[FACT]** This document defines the rigid boundary between science and engineering for Program D. No engineering implementation may violate these schemas.

---

## 1. Input Schemas

**Experiment Configuration (`experiment_config.json`)**
The configuration must strictly isolate scientific hyperparameters from system execution limits.
```json
{
  "experiment_id": "E0",
  "seed": 42,
  "scientific_parameters": {
    "mdl_b_constant": 1.5,
    "mdl_n_multiplier": 1.0,
    "capacity_growth_enabled": true
  },
  "execution_limits": {
    "max_compute_steps": 100000,
    "timeout_seconds": 3600
  }
}
```

**Task Inputs (EXP-2)**
```json
{
  "task_id": "task_001",
  "prompt_template": "You are experiencing {{affective_frame}}. Solve: {{task_body}}",
  "affective_frame": "shame -> debugging",
  "task_body": "def calculate_mean(arr): return sum(arr)/len(arr) + 1",
  "expected_output": "def calculate_mean(arr): return sum(arr)/len(arr)"
}
```

---

## 2. Output Schemas

**Metric Output (`metrics.jsonl`)**
Streamed incrementally to prevent data loss.
```json
{"step": 100, "timestamp": 1678886400, "metric": "log_likelihood", "value": -4.23}
{"step": 100, "timestamp": 1678886400, "metric": "mdl_trigger_delta", "value": 0.05}
```

**Aggregated Results (`results.json`)**
```json
{
  "experiment_id": "E0",
  "seed": 42,
  "summary_metrics": {
    "final_held_out_ll": -2.10,
    "nmi_learned_true": 0.85,
    "nmi_learned_shuffled": 0.02,
    "m_statistic": 0.83
  }
}
```

---

## 3. Metric & Artifact Formats

* **Metrics:** All continuous metrics must be logged as 64-bit floating point numbers. Discrete events (node synthesis) must be logged as integers with a corresponding timestamp and step index.
* **Artifacts:**
  * Tables: CSV format, headers matching the exact variable names defined in the execution spec.
  * Reports: Markdown (`.md`), tagged strictly with epistemological markers (`[FACT]`, `[HYPOTHESIS]`).
  * Graphs: Vector formats (SVG/PDF) exported directly from raw CSV data using reproducible matplotlib/seaborn scripts.

---

## 4. Logging Requirements

* **Provenance Tracking:** Every log line must be traceable to a specific git commit hash and configuration hash.
* **State Snapshots:** Model weights/state vectors must be serialized to disk prior to the initiation of any test evaluation.
* **Strict Isolation:** For EXP-0, the framework MUST log a boolean flag `graph_wiped: true` prior to every single trial evaluation.

---

## 5. Randomness Policy & Seed Handling

* **Central Registry:** A single, centralized pseudo-random number generator (PRNG) must be instantiated at the start of the execution thread.
* **Prohibited Calls:** No local `random.seed()` or `np.random.seed()` calls are permitted deep within the codebase.
* **Environment Generation:** The synthetic environment for E0 must be generated using an explicitly tracked and separate seed from the agent's internal PRNG.

---

## 6. Reproducibility Requirements

* **Code Freeze:** Engineers must halt all commits to the `core/` logic during the execution of any listed experiment.
* **No Tuning:** "Hyperparameter sweeps" to optimize metric outcomes are strictly prohibited. The formulas (such as the MDL threshold $\lambda$) are derivations, not tunable weights.
* **Containerization:** All evaluations must run inside an immutable Docker container locking all dependency versions (e.g., Python, NumPy, PyTorch).
