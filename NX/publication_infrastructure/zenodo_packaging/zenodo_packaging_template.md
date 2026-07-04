# Zenodo Artifact Packaging Template — Program D

**Platform:** Zenodo (CERN)
**Standard:** Zenodo Best Practices for Research Artifacts
**Program:** D (E0, EXP-1, EXP-2, EXP-3)

---

## 1. Zenodo Deposit Strategy

### 1.1 One DOI Per Logical Unit

| DOI | Content | Size | Versioning |
|-----|---------|------|------------|
| `10.5281/zenodo.XXXXX` | Program D — Complete reproducibility package (all experiments) | ~500 MB | Per release |
| `10.5281/zenodo.XXXXX` | E0 — Synthetic data generators + raw results | ~50 MB | Per experiment run |
| `10.5281/zenodo.XXXXX` | EXP-1 — Query sets + calibration results | ~10 MB | Per experiment run |
| `10.5281/zenodo.XXXXX` | EXP-2 — Task suite + affective frame results | ~20 MB | Per experiment run |
| `10.5281/zenodo.XXXXX` | EXP-3 — Environment + transfer results | ~30 MB | Per experiment run |
| `10.5281/zenodo.XXXXX` | Foundation documents (hypotheses, math, novelty) | ~5 MB | Per release |
| `10.5281/zenodo.XXXXX` | Core primitives library | ~10 MB | Per release |

### 1.2 Versioning Strategy
- **Major versions** (v1.0, v2.0): New paper, new hypothesis
- **Minor versions** (v1.1, v1.2): New experiment, new baseline
- **Patches** (v1.0.1): Bug fixes, documentation updates

---

## 2. Zenodo Deposit Structure (Per Experiment)

### 2.1 E0 Deposit (`10.5281/zenodo.XXXXX`)
```
velynx_program_d_E0_v1.0.0.zip
├── README.md                              # E0-specific reproduction guide
├── LICENSE                                # Apache-2.0
├── preregistration.pdf                    # OSF preregistration PDF
├── protocol.pdf                           # Full protocol
├── analysis_plan.pdf                      # Statistical analysis plan
├── code/
│   ├── E0_run.py
│   ├── E0_analysis.py
│   ├── E0_detectors.py
│   ├── E0_dataset.py
│   └── E0_leakage_check.py
├── data/
│   ├── synthetic_stream_generator.py
│   ├── seeds.json                         # Pre-registered seeds
│   ├── paraphrases.json
│   └── raw/
│       ├── seed_42/
│       │   ├── T_results.json
│       │   ├── C1_results.json
│       │   ├── C2_results.json
│       │   └── C3_results.json
│       ├── seed_123/
│       └── ...
├── figures/
│   ├── fig1_design.pdf
│   ├── fig2_ll.pdf
│   ├── fig3_emergence.pdf
│   └── fig_data/
│       ├── fig1_data.csv
│       ├── fig2_data.csv
│       └── fig3_data.csv
├── tables/
│   ├── table1_main.tex
│   ├── table2_perseed.tex
│   ├── table3_assumptions.tex
│   └── table_data/
│       ├── table1_data.csv
│       ├── table2_data.csv
│       └── table3_data.csv
├── stats/
│   ├── stats_E0.json                      # All test statistics
│   ├── stats_E0.csv                       # Tabular
│   └── bayesian/
│       ├── BF10_T_vs_C1.csv
│       └── BF10_T_vs_C2.csv
├── kill_criteria/
│   ├── kill_criteria_E0.md
│   └── kill_criteria_validation_E0.md
├── logs/
│   ├── reproduce_E0.log
│   └── environment.txt                    # pip freeze, nvidia-smi
├── manifest.json                          # Artifact manifest
└── CITATION.cff                           # Citation metadata
```

### 2.2 EXP-1 Deposit
```
velynx_program_d_EXP1_v1.0.0.zip
├── README.md
├── LICENSE
├── preregistration.pdf
├── queries/
│   ├── queries_200.json
│   ├── queries_500.json
│   ├── ground_truth.json
│   └── tier_assignments.json
├── code/
│   ├── EXP1_run.py
│   ├── EXP1_analysis.py
│   └── ECE_calculator.py
├── results/
│   ├── per_query_results.csv
│   ├── reliability_diagram_data.csv
│   ├── tier_calibration_data.csv
│   └── ece_bootstrap_distribution.json
├── figures/
│   ├── reliability_diagram.pdf
│   └── tier_distribution.pdf
├── stats/
│   ├── stats_EXP1.json
│   └── bootstrap_CI.json
├── kill_criteria/
│   └── kill_criteria_validation_EXP1.md
├── logs/
├── manifest.json
└── CITATION.cff
```

### 2.3 EXP-2 Deposit
```
velynx_program_d_EXP2_v1.0.0.zip
├── README.md
├── LICENSE
├── preregistration.pdf
├── tasks/
│   ├── debugging_tasks.json
│   ├── planning_tasks.json
│   ├── reasoning_tasks.json
│   ├── objective_rubrics.json
│   └── affective_frames.json
├── code/
│   ├── EXP2_run.py
│   ├── EXP2_analysis.py
│   └── schema_retriever.py
├── results/
│   ├── per_task_results.csv
│   ├── per_seed_results.csv
│   └── schema_retrieval_log.json
├── figures/
├── stats/
├── kill_criteria/
├── logs/
├── manifest.json
└── CITATION.cff
```

### 2.4 EXP-3 Deposit
```
velynx_program_d_EXP3_v1.0.0.zip
├── README.md
├── LICENSE
├── preregistration.pdf
├── environments/
│   ├── task_A.py
│   ├── task_B.py
│   └── shared_latent.py
├── code/
│   ├── EXP3_run.py
│   ├── EXP3_analysis.py
│   └── minimal_organism.py
├── results/
│   ├── transfer_results.csv
│   ├── latent_visualizations/
│   └── learning_curves.json
├── figures/
├── stats/
├── kill_criteria/
├── logs/
├── manifest.json
└── CITATION.cff
```

---

## 3. Zenodo Metadata Template

### 3.1 Required Fields
| Field | Value |
|-------|-------|
| **Title** | "Program D — [Experiment Name] v[Version]" |
| **Authors** | [Name], [ORCID], [Affiliation] |
| **Description** | 1–3 sentence summary of contents and purpose |
| **Keywords** | error-gated structure acquisition, MDL, calibration, affective indexing, emergence |
| **License** | Apache-2.0 (code), CC-BY-4.0 (data/docs) |
| **Publication Date** | YYYY-MM-DD |
| **Resource Type** | Software / Dataset / Other |
| **Version** | X.Y.Z |

### 3.2 Description Template
```markdown
This deposit contains the complete reproducibility package for [Experiment Name] from Program D, a research program on error-gated structure acquisition and the null-referenced emergence statistic.

**Contents:**
- Source code (Apache-2.0)
- Synthetic data generators / query sets / task suites (CC-BY-4.0)
- Raw experimental results (per-seed JSON + CSV)
- Generated figures (PDF + data CSVs)
- Statistical outputs (JSON with CIs, effect sizes, Bayesian analyses)
- Kill criteria evaluation report
- Pre-registration (PDF)
- Reproduction logs and environment specification

**Reproduction:**
See `reproduce.sh` in the top-level directory. Expected runtime: X hours on RTX 3090.

**Associated Paper:**
[DOI of paper, if published]

**Pre-registration:**
https://osf.io/XXXXX

**Citation:**
See `CITATION.cff` or the paper for full citation.
```

---

## 4. manifest.json Template

```json
{
  "experiment": "E0",
  "version": "1.0.0",
  "date": "2026-XX-XX",
  "commit": "abc1234567890def",
  "title": "Error-Gated Structure Acquisition — E0 Results",
  "description": "Emergence-vs-injection discrimination on nonlinear-latent stream",
  "hypothesis": "H*",
  "preregistration": "https://osf.io/XXXXX",
  "preregistration_doi": "10.17605/OSF.IO/XXXXX",
  "paper_doi": "10.XXXX/XXXXX",
  "code_repository": "https://github.com/velynx/program_d",
  "code_commit": "abc1234567890def",
  "contents": {
    "code": ["E0_run.py", "E0_analysis.py", "E0_detectors.py", "E0_dataset.py"],
    "data": ["synthetic_streams/", "seeds.json", "paraphrases.json"],
    "results": ["raw/", "figures/", "tables/", "stats/"],
    "docs": ["README.md", "preregistration.pdf", "protocol.pdf", "analysis_plan.pdf"],
    "logs": ["reproduce_E0.log", "environment.txt"],
    "kill_criteria": ["kill_criteria_E0.md", "kill_criteria_validation_E0.md"]
  },
  "figures": [
    {
      "file": "figures/fig1_design.pdf",
      "data": "figures/fig_data/fig1_data.csv",
      "script": "code/E0_analysis.py"
    }
  ],
  "tables": [
    {
      "file": "tables/table1_main.tex",
      "data": "tables/table_data/table1_data.csv",
      "script": "code/E0_analysis.py"
    }
  ],
  "statistics": "stats/stats_E0.json",
  "seeds": [42, 123, 456, 789, 999],
  "compute": {
    "gpu": "NVIDIA RTX 3090",
    "vram_gb": 24,
    "cpu_cores": 8,
    "ram_gb": 64,
    "python": "3.10.11",
    "pytorch": "2.0.1+cu118",
    "runtime_hours_per_seed": 0.4
  },
  "results": {
    "primary_hypothesis": "H*",
    "kill_criteria_passed": true,
    "T_vs_C1_pvalue": 0.001,
    "T_vs_C1_effect_size_d": 1.23,
    "T_vs_C2_pvalue": 0.002,
    "T_vs_C2_effect_size_d": 1.15,
    "emergence_statistic_margin": 0.08,
    "verdict": "PASS"
  },
  "license": {
    "code": "Apache-2.0",
    "data": "CC-BY-4.0",
    "docs": "CC-BY-4.0"
  },
  "contact": {
    "name": "Author Name",
    "email": "author@institution.edu",
    "orcid": "XXXX-XXXX-XXXX-XXXX"
  }
}
```

---

## 5. environment.txt Template

```
# Generated by `pip freeze` and `nvidia-smi`
# Python: 3.10.11
# PyTorch: 2.0.1+cu118
# CUDA: 12.1
# GPU: NVIDIA RTX 3090

# Pip packages
numpy==1.24.3
scipy==1.11.1
pandas==2.0.3
scikit-learn==1.3.0
torch==2.0.1
torchvision==0.15.2
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0
statsmodels==0.14.0
pingouin==0.5.3
arviz==0.16.1
pyarrow==12.0.1
h5py==3.9.0
pydantic==2.0.3
hydra-core==1.3.2
pytest==7.4.0
pytest-cov==4.1.0
hypothesis==6.82.0
mkdocs==1.4.3
python-dotenv==1.0.0

# System packages
# Ubuntu 22.04 LTS
# Linux kernel 5.15.0
# GCC 11.3.0
# OpenSSL 3.0.2
```

---

## 6. Zenodo Upload Procedure

### 6.1 Steps
1. Create Zenodo account: https://zenodo.org/
2. Get API token: Settings → Applications → Personal access tokens
3. Use Zenodo REST API or web interface
4. Upload ZIP file
5. Fill metadata (title, authors, description, keywords, license)
6. Add related identifiers (paper DOI, GitHub repo, OSF preregistration)
7. Publish → get DOI
8. Add DOI to paper and GitHub

### 6.2 API Upload (Python)
```python
import requests

ZENODO_API = "https://zenodo.org/api"
TOKEN = "your_zenodo_token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Create deposit
response = requests.post(
    f"{ZENODO_API}/deposit/depositions",
    json={},
    headers=headers
)
deposition_id = response.json()["id"]

# Upload file
with open("velynx_program_d_E0_v1.0.0.zip", "rb") as f:
    response = requests.put(
        f"{ZENODO_API}/deposit/depositions/{deposition_id}/files",
        headers=headers,
        data=f
    )

# Add metadata
metadata = {
    "metadata": {
        "title": "Program D — E0 Results v1.0.0",
        "upload_type": "dataset",
        "publication_date": "2026-XX-XX",
        "description": "...",
        "creators": [{"name": "Author", "orcid": "XXXX-XXXX-XXXX-XXXX"}],
        "keywords": ["error-gated", "MDL", "calibration"],
        "license": "CC-BY-4.0",
        "related_identifiers": [
            {"identifier": "10.XXXX/XXXXX", "relation": "isSupplementTo"}
        ]
    }
}
requests.put(
    f"{ZENODO_API}/deposit/depositions/{deposition_id}",
    json=metadata,
    headers=headers
)

# Publish
requests.post(
    f"{ZENODO_API}/deposit/depositions/{deposition_id}/actions/publish",
    headers=headers
)
```

---

## 7. License Considerations

### 7.1 Recommended Licenses

| Content | License | Reason |
|---------|---------|--------|
| **Code** | Apache-2.0 | Permissive, patent grant, widely used in ML |
| **Data** | CC-BY-4.0 | Attribution, allows reuse |
| **Documentation** | CC-BY-4.0 | Attribution, allows reuse |
| **Figures** | CC-BY-4.0 | Attribution, allows reuse in derivative works |

### 7.2 License File Template
```
Apache License 2.0
Copyright 2026 [Author Name]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 8. Zenodo Best Practices

1. **Use versioned releases** — v1.0.0, v1.1.0, etc.
2. **Reserve DOI early** — Use "Reserve DOI" before publication
3. **Link to paper and code** — Use related_identifiers
4. **Include CITATION.cff** — Machine-readable citation
5. **Document compute environment** — environment.txt
6. **Include manifest** — JSON manifest of all contents
7. **Add reproduction log** — Output of `reproduce.sh`
8. **Tag with keywords** — For discoverability
9. **Add funding acknowledgment** — In description
10. **Update with errata** — New version for corrections

---

## 9. Common Zenodo Mistakes

1. **No DOI at submission** — Reserve DOI before submitting paper
2. **Missing metadata** — Title, authors, description required
3. **Wrong license** — Must be OSI-approved for code
4. **No CITATION.cff** — Required for proper citation
5. **Missing related identifiers** — Link to paper, GitHub, OSF
6. **Large files** — Zenodo limit 50 GB; split if needed
7. **No environment specification** — Can't reproduce without
8. **No manifest** — Hard to navigate contents
9. **Unversioned releases** — Hard to cite specific version
10. **No funding acknowledgment** — Required by many funders

---

**Template Version:** 1.0
**Last Updated:** 2026-07-03
**Aligned with:** Zenodo Best Practices, FAIR Data Principles, Program D Constitution §4 (reproducibility)