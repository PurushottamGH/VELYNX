# REPRODUCIBILITY_AUDIT

**Auditor:** Scientific Validation Lead, Program D
**Date:** 2026-07-04
**Scope:** Code-provenance, seed management, artifact immutability, data management, environment pinning, and end-to-end reproducibility
**Reference:** `PROGRAM_D_CANONICAL.md §7–9`; `DATA_MANAGEMENT_PLAN.md`; `REPRODUCIBILITY_CHECKLIST.md`

---

## Verdict: **WARNING**

Sprint 1 demonstrates **strong reproducibility discipline at the unit/component level**: deterministic seeds, separate env/agent seed registries, JSON-serializable results, artifact-immutable run directories, and verified seed-to-output determinism via `test_seeded_reproducibility`.

However, full **end-to-end reproducibility is untested**: no full-scale 5-seed E0 run has been executed, no EXP-0/1/2 artifacts exist, the `paraphrases.json` dataset is missing, and the Dockerized run environment and pinned-dependency bundle specified in the master roadmap M6 are not addressed in this sprint.

The unit-level reproducibility is genuine. The system-level reproducibility is unverified.

---

## 1. Code provenance and freezing

### 1.1 Frozen code for experiments
**Status: PARTIAL**

- **E0**: `experiments/E0/run.py` is a single entry point. No explicit code-freeze mechanism (e.g., `git tag` or commit hash check). The runner does not verify `git status` is clean before running.
- **EXP-0**: `experiments/EXP0/run_exp0.py:7-10` explicitly states: "Freezes nothing itself -- EXP0_RUNBOOK.md's step 1 (verify `git status` is clean, or record the diff) is the researcher's responsibility before invoking this script." This is a process control, not an automated check.
- **EXP-1, EXP-2**: Not implemented.

**Gap:** No automated commit-hash recording in the artifact manifest. The `manifest` dict in `run_exp0.py:249-256` records `seed`, `alpha_before_correction`, `tiers_run`, `run_dir`, and the dataset hashes, but not the code commit hash.

**Recommendation:** Add `git rev-parse HEAD` and `git status --porcelain` to every experiment's manifest.

### 1.2 Content-hash integrity checks
**Status: GOOD (for what exists)**

- **EXP-0 dataset**: `paraphrases.json` records `source_file_sha256` of `concepts.json`. The loader verifies the live hash matches. If they drift, `DatasetIntegrityError` is raised.
- **E0**: No content-hash check on the environment or predictor configuration. The `DEFAULT_CONFIG` is hardcoded.

---

## 2. Seed management

### 2.1 Central seed registry
**Status: GOOD**

`experiments/E0/run.py:88-116` implements `SeedRegistry`:
- `master_seed`: base seed for the run
- `env_seed = master_seed + 1000`: separate seed for environment generation
- `agent_seed(condition, seed_idx)`: derived from `master_seed + hash(f"agent::{condition}::{seed_idx}")`
- `analysis_seed()`: separate seed for analysis (currently unused)

**Test coverage:**
- `test_seed_registry_creation`: env_seed = master + 1000 ✓
- `test_agent_seeds_differ_from_env_seed` ✓
- `test_agent_seeds_differ_by_condition` ✓

**Strength:** The agent cannot predict the environment by sharing a PRNG.

**Weakness:** The `agent_seed` function uses Python's `hash()` which is **not stable across Python versions or processes** (hash randomization is enabled by default in Python 3.3+). This means agent seeds may differ across runs even with the same master_seed. This is a **reproducibility defect**.

**Recommendation:** Use `hashlib.sha256(f"agent::{condition}::{seed_idx}".encode()).hexdigest()` and take the first 8 bytes as an integer seed.

### 2.2 EXP-0 seed
**Status: GOOD**

`run_exp0.py:87-96` uses `random.Random(seed)` for trial-order shuffling. Deterministic given the seed.

### 2.3 EXP-0 leakage-check determinism
**Status: GOOD**

`leakage_check.py` is a pure function over the JSON file. Deterministic.

### 2.4 Predictor determinism
**Status: PARTIAL**

`DirichletMarkovPredictor` uses `np.random.RandomState(rng_seed)`. Deterministic given the seed. However, the `_infer_state` method uses the transition counts as centroids (a proxy) — this is deterministic but the inference quality is not well-calibrated to the observation space.

---

## 3. Artifact management

### 3.1 Artifact immutability
**Status: GOOD**

- **EXP-0**: `run_exp0.py:77-84` allocates a timestamped directory and refuses to overwrite. A crashed run writes `_FAILED.txt` to mark the directory as invalid.
- **E0**: `run.py:738-740` creates the output directory with `mkdir(parents=True, exist_ok=True)`. **Does not refuse to overwrite** — a re-run with the same `output_dir` will overwrite `aggregated_results.json`. This is a **defect** for artifact immutability.

**Recommendation:** Use a timestamp in the output directory name (as EXP-0 does) and refuse to overwrite.

### 3.2 Artifact contents
**Status: PARTIAL**

- **EXP-0**: Writes `exp0_manifest.json`, `exp0_raw_results.jsonl`, `exp0_summary.json`, `exp0_report.md`. Comprehensive.
- **E0**: Writes `config.json` and `aggregated_results.json`. Does **not** write per-seed CSVs, per-condition summaries, or a human-readable report. The `generate_e0_report` function exists in `analysis.py:301-339` but is **not called** by the runner.

**Gap:** The aggregated results are the only persistent artifact. Per-seed and per-condition details are nested inside the JSON but are not extracted into separate files.

**Recommendation:** Call `generate_e0_report` and write it to `e0_report.md` alongside the JSON.

### 3.3 JSON serializability
**Status: GOOD**

`test_results_json_serializable` passes. The `_json_serialize` helper in `run.py:763-773` handles numpy types and datetimes.

---

## 4. Data management

### 4.1 Dataset version control
**Status: PARTIAL**

- **EXP-0**: `paraphrases.json` includes a `source_file_sha256` of `concepts.json` and a `schema_version` (implied by the loader's version check). The dataset is versioned by content hash.
- **E0**: No dataset to version. The environment is generated from `SeedRegistry` each run.

### 4.2 State files
**Status: NOT AUDITED IN THIS SPRINT**

The `data/` directory contains `vector_backend.json`, `system_health.json`, `source_trust.json`, `soul_concepts.json`, `session.json`, `proposed_nodes.json`. The `concept_birth.db` SQLite file is also present. These are runtime state files, not experimental data, and are not in the scope of Sprint 1 (which is the `core/` + `experiments/E0/` path).

**Risk:** If any of these files are read by an experiment (none are, in the E0 path), reproducibility across machines would be at risk. The E0 experiment does not touch any of these files.

### 4.3 EXP-0 wipe mechanism
**Status: GOOD (in design, unverified in practice)**

`run_exp0.py:60-74` imports `scripts/wipe_db.py` and calls `run_wipe(dry=False, verbose=verbose, strict=True)`. This is the same wipe path used by `backend/tests/live_fire_harness.py`. The function is invoked before every Tier 1 and Tier 3 trial.

**Unverified:** EXP-0 has never been run, so the wipe mechanism is unverified in practice.

---

## 5. Environment pinning

### 5.1 Python version
**Status: IMPLICIT**

Tests run on Python 3.11.9 (per the pytest output). No `python_version` pin in any experiment config.

### 5.2 Dependency pinning
**Status: NOT AUDITED**

No `requirements.txt`, `pyproject.toml`, or `Pipfile` is present in the repository root that pins the scientific dependencies (`numpy`, `scipy`, `scikit-learn`, `nltk`). The `pyproject.toml` exists (pytest references it) but its contents are not audited here.

**Gap:** The reproducibility bundle specified in master roadmap M6 (Dockerized immutable run env, pinned deps) is not addressed in this sprint.

### 5.3 Random library versions
**Status: NOT PINNED**

- `numpy.random.RandomState` is used (not `numpy.random.Generator`). This is the legacy API but is stable.
- `scipy.stats.ttest_rel` is used. SciPy version is not pinned.
- `sklearn.metrics.normalized_mutual_info_score` is imported in `analysis.py:16` but is **not used** (the custom `compute_nmi` in `core/emergence/emergence_statistic.py` is used instead). Dead import.

---

## 6. End-to-end reproducibility

### 6.1 Seeded determinism (unit-level)
**Status: VERIFIED**

`test_seeded_reproducibility` in `tests/integration/test_e0_pipeline.py:259-273`:
```python
r1 = run_single_seed(42, 101, self.MINIMAL_CONFIG, str(tmpdir1))
r2 = run_single_seed(42, 101, self.MINIMAL_CONFIG, str(tmpdir2))
assert np.allclose(ll1, ll2)
```

This passes. Same seed → same log-likelihoods.

### 6.2 Full-scale reproducibility
**Status: UNVERIFIED**

No full-scale (10,000-step, 5-seed) E0 run has been executed. The 100 tests in Sprint 1 run at much smaller scale (100–500 steps, 1–3 seeds).

### 6.3 Cross-machine reproducibility
**Status: UNVERIFIED**

No test runs the experiment on a different machine or OS. The `np.random.RandomState` API is stable across platforms, but the `hash()` instability in `SeedRegistry.agent_seed` means agent seeds may differ across Python processes even with the same master_seed.

### 6.4 Cross-version reproducibility
**Status: UNVERIFIED**

No test pins the Python, NumPy, or SciPy version. A change in any of these could alter numerical results.

---

## 7. Documentation and provenance

### 7.1 Inline documentation
**Status: GOOD**

Every core module has a docstring citing the canon section it implements:
- `core/predictors/dirichlet_markov.py:13-14` cites canon §5.2
- `core/measurement/proper_scoring.py:85` cites canon §5.3
- `core/mdl/mdl_growth.py:13-14` cites canon §5.4
- `core/emergence/emergence_statistic.py` — no canon citation (should add §5.5)
- `experiments/E0/run.py:16-18` cites canon §7 (E0) and the execution spec
- `experiments/E0/decision.py:10-11` cites canon §6 (H* kill criteria)

### 7.2 Traceability matrix
**Status: NOT PRESENT**

The master roadmap M0 specifies a `TRACEABILITY_MATRIX.md` with zero unmapped rows. This file is not in the repository.

### 7.3 Implementation gaps document
**Status: NOT PRESENT**

The master roadmap M0 references `IMPLEMENTATION_GAPS.md`. This file is not in the repository.

---

## 8. Summary of reproducibility findings

| Area | Status | Evidence |
|---|---|---|
| Seed registry (env/agent separation) | PASS | `experiments/E0/run.py:88-116`; 3 tests |
| Seeded determinism (unit-level) | PASS | `test_seeded_reproducibility` |
| Artifact immutability (EXP-0) | PASS | `run_exp0.py:77-84` refuses overwrite |
| Artifact immutability (E0) | **FAIL** | `run.py:738-740` overwrites |
| JSON serializability | PASS | `test_results_json_serializable` |
| Content-hash integrity (EXP-0) | PASS | `dataset.py:50-60` |
| Commit-hash recording | **FAIL** | No `git rev-parse` in any manifest |
| `hash()` seed instability | **FAIL** | `run.py:107` uses Python `hash()` |
| Dependency pinning | **FAIL** | No `requirements.txt` or version pin |
| Full-scale reproducibility | UNVERIFIED | No 5-seed E0 run artifact |
| Cross-machine reproducibility | UNVERIFIED | No multi-machine test |
| Cross-version reproducibility | UNVERIFIED | No version pin |
| Traceability matrix | **FAIL** | Not in repository |
| Implementation gaps document | **FAIL** | Not in repository |
| `paraphrases.json` dataset | **FAIL** | Not in repository |
| E0 human-readable report | **FAIL** | `generate_e0_report` never called |

---

## 9. Recommendations

1. **Replace `hash()` with a stable hash** in `SeedRegistry.agent_seed` (e.g., `hashlib.sha256`).
2. **Add commit-hash recording** to every experiment manifest.
3. **Make E0 output directory timestamped** and refuse to overwrite.
4. **Call `generate_e0_report`** in the E0 runner to produce a human-readable `e0_report.md`.
5. **Commit `experiments/EXP0/paraphrases.json`** — the dataset is missing.
6. **Pin dependencies** in a `requirements.txt` or `pyproject.toml` with exact versions.
7. **Add a `TRACEABILITY_MATRIX.md`** mapping every hypothesis → experiment → metric → kill criterion.
8. **Run a full 5-seed E0 experiment** and commit the `aggregated_results.json` artifact.
9. **Remove the dead `sklearn` import** in `experiments/E0/analysis.py:16`.
10. **Add a cross-version reproducibility test** that runs the same seed under two different NumPy versions and asserts bit-identical output (or documents any acceptable tolerance).

---

**Reproducibility Audit Verdict: WARNING**

Unit-level reproducibility is strong. System-level reproducibility is unverified and has several latent defects (hash instability, missing commit-hash recording, missing dataset, missing full-scale run artifact). These are correctable without redesigning the science.
