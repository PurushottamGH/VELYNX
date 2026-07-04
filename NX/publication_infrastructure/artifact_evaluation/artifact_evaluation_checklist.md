# Artifact Evaluation Checklist — Program D

**Standard:** NeurIPS / ICML Artifact Evaluation (AE)
**Program:** D (E0, EXP-1, EXP-2, EXP-3)

---

## 1. Artifact Badges (NeurIPS / ICML)

Target badges for Program D:
- [ ] **Artifacts Available** — Code + data publicly accessible
- [ ] **Artifacts Functional** — Code runs and produces stated results
- [ ] **Results Reproduced** — Independent reproduction of main results

---

## 2. Required Artifacts Per Experiment

### 2.1 Code Artifacts
| Artifact | Location | Purpose | Required |
|----------|----------|---------|----------|
| Experiment code | `experiments/{ID}/run.py` | Execute experiment | Yes |
| Analysis code | `experiments/{ID}/analysis.py` | Generate figures/tables | Yes |
| Detection code | `experiments/{ID}/detectors.py` | Implement emergence statistic, ECE, etc. | Yes |
| Dataset code | `experiments/{ID}/dataset.py` | Generate/synthetic data | Yes |
| Leakage check | `experiments/{ID}/leakage_check.py` | Verify no data leakage | Yes |
| Paraphrases | `experiments/{ID}/paraphrases.json` | For EXP-0 | Yes |
| Core primitives | `core/` | Predictor, MDL, emergence, controls | Yes |
| Benchmarks | `benchmarks/` | Shared evaluation harness | Yes |
| Infrastructure | `infra/` | Operational code | Optional (not load-bearing for science) |

### 2.2 Data Artifacts
| Artifact | Format | Purpose | Required |
|----------|--------|---------|----------|
| Synthetic data generators | Python code | Regenerate synthetic streams | Yes |
| Query sets | JSON/CSV | EXP-1 queries with ground truth | Yes |
| Task suite | JSON | EXP-2 tasks with scoring rubrics | Yes |
| Pre-registration | OSF export | H*, H1, H2, H3 preregistrations | Yes |
| Raw results | CSV/Parquet | Per-seed metrics | Yes |
| Figure data | CSV | Data behind each figure | Yes |
| Table data | CSV | Data behind each table | Yes |
| Pre-trained weights | PyTorch/HF | If any model weights produced | If applicable |

### 2.3 Documentation Artifacts
| Artifact | Location | Purpose | Required |
|----------|----------|---------|----------|
| Protocol | `experiments/{ID}/protocol.md` | Full experimental procedure | Yes |
| Preregistration | `experiments/{ID}/preregistration.md` | Pre-registered plan | Yes |
| README | `experiments/{ID}/README.md` | How to run | Yes |
| Foundation docs | `foundation/` | Hypotheses, assumptions, kill criteria, math, novelty | Yes |
| Architecture | `foundation/architecture/architecture.md` | System structure | Yes |
| Variable provenance | `foundation/mathematics/variable_provenance.md` | Variable definitions | Yes |
| Kill criteria report | `foundation/kill_criteria/kill_criteria_validation_report.md` | Per-experiment pass/fail | Yes |

### 2.4 Containerization
| Artifact | File | Purpose | Required |
|----------|------|---------|----------|
| Dockerfile | `Dockerfile` (or `infra/Dockerfile`) | Reproducible environment | Yes |
| docker-compose | `docker-compose.yml` | Multi-service orchestration | If multi-service |
| requirements.txt | `requirements.txt` | Pinned dependencies | Yes |
| pyproject.toml | `pyproject.toml` | Modern packaging | Yes |
| environment.yml | `environment.yml` | Conda env (if used) | If conda |
| .env.example | `.env.example` | Environment variables | Yes |

---

## 3. Artifact Submission Package Structure

```
velynx_program_d_artifact_v{version}/
├── README.md                                    # Top-level instructions
├── LICENSE                                       # MIT/Apache-2.0/BSD
├── CITATION.cff                                  # How to cite
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── .env.example
├── reproduce.sh                                  # One-command reproduction
├── reproduce_all.sh                              # All experiments
├── foundation/                                   # All foundation docs (22 files)
│   ├── hypothesis/
│   │   ├── central_hypothesis.md
│   │   ├── H1_calibration.md
│   │   ├── H2_affective_indexing.md
│   │   └── H3_emergent_development.md
│   ├── assumptions/
│   │   ├── assumption_ledger.md
│   │   ├── assumption_coverage_matrix.csv
│   │   └── parameter_atlas.md
│   ├── kill_criteria/
│   │   ├── kill_criteria.md
│   │   └── kill_criteria_validation_report.md
│   ├── mathematics/
│   │   ├── mathematical_foundation.md
│   │   ├── variable_provenance.md
│   │   ├── variable_dependency_graph.graphml
│   │   └── variable_dependency_matrix.csv
│   ├── architecture/
│   │   ├── architecture.md
│   │   ├── dependency_graph.graphml
│   │   ├── dependency_matrix.csv
│   │   └── layer_diagram.mmd
│   └── novelty/
│       ├── novelty_analysis.md
│       └── publication_test.md
├── core/                                         # Reusable primitives
│   ├── predictors/
│   │   ├── base.py
│   │   └── dirichlet_markov.py
│   ├── emergence/
│   │   ├── emergence_statistic.py
│   │   └── null_referenced_test.py
│   ├── mdl/
│   │   ├── mdl_growth.py
│   │   └── concept_birth_ledger.py
│   ├── measurement/
│   │   ├── proper_scoring.py
│   │   ├── metrics.py
│   │   └── observability.py
│   └── controls/
│       ├── fixed_capacity.py
│       ├── random_growth.py
│       └── shuffled_input.py
├── experiments/                                  # Self-contained
│   ├── E0/
│   │   ├── preregistration.md
│   │   ├── protocol.md
│   │   ├── run.py
│   │   ├── analysis.py
│   │   ├── detectors.py
│   │   ├── dataset.py
│   │   ├── leakage_check.py
│   │   ├── paraphrases.json (EXP-0 only)
│   │   └── results/                             # Generated outputs
│   │       ├── figures/
│   │       ├── tables/
│   │       ├── stats/
│   │       └── manifest.json
│   ├── EXP1/
│   ├── EXP2/
│   ├── EXP3/
│   └── coverage/
│       └── experiment_coverage_matrix.csv
├── benchmarks/                                   # Evaluation harnesses
├── program_a/                                    # Retrieval (for H1)
├── program_b/                                    # Soul graph (for H2)
├── program_c/                                    # Engineering stack
├── infra/                                        # Operations
├── tests/                                        # Unit + integration
├── docs/                                         # Additional documentation
└── artifacts/                                    # Generated outputs
    ├── experiments/
    └── benchmarks/
```

---

## 4. Reproduction Verification

### 4.1 One-Command Reproduction
```bash
# From artifact root:
bash reproduce.sh
```

**Expected behavior:**
1. Verify Python version (3.10+)
2. Install dependencies (`pip install -e .`)
3. Verify GPU availability (if applicable)
4. Run E0: 5 seeds × 4 conditions = 20 runs
5. Run EXP-1: 200+ queries, ECE calculation
6. Run EXP-2: N tasks × 5 seeds, paired comparison
7. Run EXP-3: 5 seeds, transfer evaluation
8. Generate all figures/tables
9. Run kill criteria evaluation
10. Print summary report with pass/fail

**Expected output:**
- `artifacts/experiments/*/figures/` — All figures
- `artifacts/experiments/*/tables/` — All tables
- `artifacts/experiments/*/stats/` — All statistics
- `artifacts/experiments/*/manifest.json` — Artifact manifest
- `artifacts/summary_report.md` — Pass/fail summary

### 4.2 Determinism Verification
```bash
# Same seed should produce identical results:
python experiments/E0/run.py --seed 42
python experiments/E0/run.py --seed 42
# diff: should be empty
```

### 4.3 Statistical Reproduction
- ECE should match within ±0.005 (binning variability)
- Held-out LL should match within ±0.01
- p-values may vary slightly with stochastic tests; report BF₁₀ for robustness

---

## 5. Artifact Evaluation Test Cases (NeurIPS AE Style)

### 5.1 Test 1: Fresh Install
- [ ] Clean environment (no cached packages)
- [ ] `bash reproduce.sh` succeeds without errors
- [ ] All expected output files present
- [ ] Summary report shows expected pass/fail

### 5.2 Test 2: Different Hardware
- [ ] Reproduce on different GPU (if applicable)
- [ ] Reproduce on CPU-only
- [ ] Numerical results within tolerance

### 5.3 Test 3: Partial Reproduction
- [ ] Run only E0 (`bash reproduce_e0.sh`)
- [ ] Run only EXP-1 (`bash reproduce_exp1.sh`)
- [ ] Each produces its expected outputs

### 5.4 Test 4: Documentation Completeness
- [ ] All foundation documents present (22 files)
- [ ] All experiment protocols/preregistrations present
- [ ] All code has docstrings
- [ ] README explains how to navigate

### 5.5 Test 5: Kill Criteria Evaluation
- [ ] `python -m foundation.kill_criteria.validate` runs
- [ ] Reports pass/fail for each criterion
- [ ] Generates `kill_criteria_validation_report.md`

---

## 6. License & Citation

### 6.1 Recommended License
- **Code:** Apache-2.0 (permissive, patent grant)
- **Data:** CC-BY-4.0 (attribution)
- **Docs:** CC-BY-4.0

### 6.2 CITATION.cff
```yaml
cff-version: 1.2.0
message: "If you use this artifact, please cite the associated paper and the artifact itself."
authors:
  - family-names: "Author"
    given-names: "Full Name"
    orcid: "https://orcid.org/XXXX-XXXX-XXXX-XXXX"
title: "Program D: Error-Gated Structure Acquisition — Artifact"
version: 1.0.0
date-released: 2026-XX-XX
license: Apache-2.0
doi: 10.5281/zenodo.XXXXX
```

---

## 7. Submission Checklist (Per Experiment)

| Item | E0 | EXP-1 | EXP-2 | EXP-3 |
|------|----|-------|-------|-------|
| Code runs end-to-end | [ ] | [ ] | [ ] | [ ] |
| Preregistration on OSF | [ ] | [ ] | [ ] | [ ] |
| Preregistration matches protocol | [ ] | [ ] | [ ] | [ ] |
| Preregistration matches results | [ ] | [ ] | [ ] | [ ] |
| Seeds fixed and documented | [ ] | [ ] | [ ] | [ ] |
| Compute requirements documented | [ ] | [ ] | [ ] | [ ] |
| Figures reproducible from data | [ ] | [ ] | [ ] | [ ] |
| Tables reproducible from data | [ ] | [ ] | [ ] | [ ] |
| Kill criteria evaluated | [ ] | [ ] | [ ] | [ ] |
| Negative results reported | [ ] | [ ] | [ ] | [ ] |
| License included | [ ] | [ ] | [ ] | [ ] |
| CITATION.cff included | [ ] | [ ] | [ ] | [ ] |
| DOI assigned (Zenodo) | [ ] | [ ] | [ ] | [ ] |

---

## 8. Common Rejection Reasons (Artifact AE)

1. **No pre-registration** — Hypothesis and analysis plan must be pre-registered
2. **Code doesn't run** — Even one error = "Artifacts Available" but not "Functional"
3. **Results not reproducible** — Numerical results differ from paper
4. **Missing data** — Can't verify queries, tasks, or synthetic generators
5. **Missing compute specs** — Reviewer can't estimate resources
6. **Missing kill criteria evaluation** — Program D specific; Constitution §4
7. **Designer injection detected** — Seeded concepts in E0 = automatic fail
8. **Anthropomorphic language in code/docs** — Constitution §2.4
9. **License not open** — Must be OSI-approved permissive
10. **No DOI** — Must have Zenodo DOI for citation

---

**Template Version:** 1.0
**Last Updated:** 2026-07-03
**Program D Constitution:** §2, §4, §6 (vigilance, burden of proof, terminology)