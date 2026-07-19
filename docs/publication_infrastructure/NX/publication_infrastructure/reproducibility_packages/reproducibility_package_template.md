# Reproducibility Package Template — Program D

**Standard:** NeurIPS 2026 / ICML 2026 / ICLR 2027 Reproducibility
**Program:** D (E0, EXP-1, EXP-2, EXP-3)

---

## 1. Top-Level Structure

```
velynx_program_d_v{version}_reproducibility/
├── README.md                                      # Top-level reproduction guide
├── LICENSE                                        # Apache-2.0
├── CITATION.cff                                   # Citation metadata
├── requirements.txt                               # Pinned dependencies
├── pyproject.toml                                 # Modern Python packaging
├── Dockerfile                                     # Reproducible container
├── docker-compose.yml                             # Optional multi-service
├── .env.example                                   # Environment template
├── reproduce.sh                                   # One-command reproduction
├── verify_reproducibility.sh                      # Cross-check reproduction
├── foundation/                                    # 22 foundation files
├── core/                                          # Scientific primitives
├── experiments/                                   # Self-contained experiments
├── benchmarks/                                    # Evaluation harnesses
├── program_a/                                     # Program A (retrieval)
├── program_b/                                     # Program B (soul graph)
├── program_c/                                     # Program C (stack)
├── infra/                                         # Operations
├── tests/                                         # Unit + integration
├── artifacts/                                     # Generated outputs
├── results/                                       # Per-experiment results
│   ├── E0/
│   ├── EXP1/
│   ├── EXP2/
│   └── EXP3/
└── reports/                                       # Summary reports
    ├── summary_report.md
    ├── kill_criteria_report.md
    ├── novelty_report.md
    └── reproducibility_report.md
```

---

## 2. README.md Template

```markdown
# VELYNX Program D — Reproducibility Package

**Version:** 1.0.0
**Last Updated:** 2026-XX-XX
**Associated Paper:** [DOI]
**Pre-registrations:** https://osf.io/XXXXX

## What This Package Reproduces

This package reproduces the following results from Program D:

1. **E0** — Error-gated structure acquisition vs. fixed-capacity, error-decoupled, and shuffled-input controls (H*)
2. **EXP-1** — Calibration curve with ECE < 0.1 on ≥200 mixed queries (H1)
3. **EXP-2** — Affective framing effect on objective task performance (H2)
4. **EXP-3** — Transfer of emergent structure to held-out prediction task (H3)

## One-Command Reproduction

```bash
bash reproduce.sh
```

**Expected runtime:**
- E0: ~2 hours on RTX 3090 (5 seeds × 4 conditions)
- EXP-1: ~5 minutes on CPU
- EXP-2: ~10 minutes on CPU
- EXP-3: ~1 hour on RTX 3090 (5 seeds)
- **Total: ~3.5 hours**

## System Requirements

- **OS:** Linux (Ubuntu 20.04+), macOS 12+, Windows 10+ with WSL2
- **Python:** 3.10 or 3.11
- **GPU:** NVIDIA GPU with 8+ GB VRAM (RTX 3060 or better) for E0, EXP-3
- **CPU:** 8+ cores
- **RAM:** 16+ GB
- **Storage:** 20+ GB free

## Step-by-Step Reproduction

### Step 1: Install Dependencies
```bash
pip install -e .
# or
pip install -r requirements.txt
```

### Step 2: Verify Environment
```bash
python -c "import torch; print(torch.cuda.is_available())"
python -c "from core.predictors.dirichlet_markov import DirichletMarkovPredictor"
```

### Step 3: Run Experiments
```bash
# E0: Emergence-vs-injection discrimination
python experiments/E0/run.py --seeds 42 123 456 789 999
python experiments/E0/analysis.py

# EXP-1: Calibration
python experiments/EXP1/run.py --queries data/exp1_queries.json
python experiments/EXP1/analysis.py

# EXP-2: Affective indexing
python experiments/EXP2/run.py --tasks data/exp2_tasks.json --seeds 5
python experiments/EXP2/analysis.py

# EXP-3: Minimal predictive organism
python experiments/EXP3/run.py --seeds 42 123 456 789 999
python experiments/EXP3/analysis.py
```

### Step 4: Generate Reports
```bash
python -m foundation.kill_criteria.validate
python -m foundation.novelty.assess
python -m reproducibility.generate_report
```

### Step 5: Verify Reproduction
```bash
bash verify_reproducibility.sh
```

## Expected Outputs

After successful reproduction, the following should exist:

- `results/E0/figures/` — 4–6 figures
- `results/E0/tables/` — 2–4 tables
- `results/E0/stats/stats_E0.json` — All test statistics
- `results/E0/manifest.json` — Artifact manifest
- ... (similar for EXP1, EXP2, EXP3)
- `reports/summary_report.md` — Overall pass/fail
- `reports/kill_criteria_report.md` — Kill criteria evaluation
- `reports/reproducibility_report.md` — Reproduction verification

## What To Do If Reproduction Fails

1. Check `results/{experiment}/logs/` for error messages
2. Verify environment: `python -c "import torch; print(torch.__version__)"`
3. Check disk space: `df -h`
4. Check GPU: `nvidia-smi`
5. Re-run with `--verbose` flag
6. Report issue: [GitHub Issues URL]

## Citation

```bibtex
@article{velynx_program_d_2026,
  title={Program D: Error-Gated Structure Acquisition and the Null-Referenced Emergence Statistic},
  author={Author, Full Name},
  journal={[Journal Name]},
  year={2026},
  doi={10.XXXX/XXXXX}
}
```

## License

Apache-2.0
```

---

## 3. reproduce.sh Template

```bash
#!/usr/bin/env bash
# VELYNX Program D — One-command reproduction
# Last updated: 2026-XX-XX

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[REPRODUCE]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err() { echo -e "${RED}[ERROR]${NC} $*"; }

# Step 1: Environment verification
log "Step 1: Verifying environment..."
python --version || { err "Python 3.10+ required"; exit 1; }
python -c "import torch; print('PyTorch:', torch.__version__)" || { err "PyTorch not installed"; exit 1; }

# Step 2: Install dependencies
log "Step 2: Installing dependencies..."
pip install -e . --quiet

# Step 3: Verify imports
log "Step 3: Verifying core imports..."
python -c "from core.predictors.dirichlet_markov import DirichletMarkovPredictor" || { err "Core import failed"; exit 1; }
python -c "from core.emergence.emergence_statistic import EmergenceStatistic" || { err "Emergence import failed"; exit 1; }
python -c "from core.mdl.mdl_growth import MDLGrowth" || { err "MDL import failed"; exit 1; }

# Step 4: Run experiments
log "Step 4: Running E0 (Emergence-vs-injection)..."
python experiments/E0/run.py --seeds 42 123 456 789 999 --output-dir results/E0/
python experiments/E0/analysis.py --input-dir results/E0/ --output-dir results/E0/

log "Step 5: Running EXP-1 (Calibration)..."
python experiments/EXP1/run.py --queries data/exp1_queries.json --output-dir results/EXP1/
python experiments/EXP1/analysis.py --input-dir results/EXP1/ --output-dir results/EXP1/

log "Step 6: Running EXP-2 (Affective indexing)..."
python experiments/EXP2/run.py --tasks data/exp2_tasks.json --seeds 5 --output-dir results/EXP2/
python experiments/EXP2/analysis.py --input-dir results/EXP2/ --output-dir results/EXP2/

log "Step 7: Running EXP-3 (Emergent development)..."
python experiments/EXP3/run.py --seeds 42 123 456 789 999 --output-dir results/EXP3/
python experiments/EXP3/analysis.py --input-dir results/EXP3/ --output-dir results/EXP3/

# Step 5: Generate reports
log "Step 8: Generating reports..."
python -m foundation.kill_criteria.validate --output reports/kill_criteria_report.md
python -m foundation.novelty.assess --output reports/novelty_report.md
python -m reproducibility.generate_report --output reports/summary_report.md

# Step 6: Verify reproduction
log "Step 9: Verifying reproduction..."
bash verify_reproducibility.sh

log "Reproduction complete. See reports/ for summary."
```

---

## 4. verify_reproducibility.sh Template

```bash
#!/usr/bin/env bash
# Verify that reproduction matches paper claims

set -euo pipefail

PASS=0
FAIL=0

check() {
    local name=$1
    local condition=$2
    if [ "$condition" = "true" ]; then
        echo "PASS: $name"
        ((PASS++))
    else
        echo "FAIL: $name"
        ((FAIL++))
    fi
}

# E0 checks
if [ -f "results/E0/stats/stats_E0.json" ]; then
    T_VS_C1_P=$(jq -r '.contrasts.t_vs_c1.pvalue' results/E0/stats/stats_E0.json)
    T_VS_C2_P=$(jq -r '.contrasts.t_vs_c2.pvalue' results/E0/stats/stats_E0.json)
    
    check "E0: T > C1 on DV-a (p < 0.01)" \
        "$(python -c "print('true' if $T_VS_C1_P < 0.01 else 'false')")"
    check "E0: T > C2 on DV-a (p < 0.01)" \
        "$(python -c "print('true' if $T_VS_C2_P < 0.01 else 'false')")"
else
    echo "SKIP: E0 stats not found"
fi

# EXP-1 checks
if [ -f "results/EXP1/stats/stats_EXP1.json" ]; then
    ECE=$(jq -r '.ece' results/EXP1/stats/stats_EXP1.json)
    check "EXP-1: ECE < 0.1" \
        "$(python -c "print('true' if $ECE < 0.1 else 'false')")"
else
    echo "SKIP: EXP-1 stats not found"
fi

# EXP-2 checks
if [ -f "results/EXP2/stats/stats_EXP2.json" ]; then
    P=$(jq -r '.pvalue' results/EXP2/stats/stats_EXP2.json)
    D=$(jq -r '.effect_size.d' results/EXP2/stats/stats_EXP2.json)
    check "EXP-2: Significant improvement (p < 0.05)" \
        "$(python -c "print('true' if $P < 0.05 else 'false')")"
    check "EXP-2: Meaningful effect size (d > 0.2)" \
        "$(python -c "print('true' if $D > 0.2 else 'false')")"
else
    echo "SKIP: EXP-2 stats not found"
fi

# EXP-3 checks
if [ -f "results/EXP3/stats/stats_EXP3.json" ]; then
    P=$(jq -r '.pvalue' results/EXP3/stats/stats_EXP3.json)
    D=$(jq -r '.effect_size.d' results/EXP3/stats/stats_EXP3.json)
    check "EXP-3: Transfer > random init (p < 0.05)" \
        "$(python -c "print('true' if $P < 0.05 else 'false')")"
    check "EXP-3: Meaningful transfer (d > 0.3)" \
        "$(python -c "print('true' if $D > 0.3 else 'false')")"
else
    echo "SKIP: EXP-3 stats not found"
fi

echo ""
echo "Verification summary: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
    echo "ALL CHECKS PASSED"
    exit 0
else
    echo "SOME CHECKS FAILED — see above"
    exit 1
fi
```

---

## 5. requirements.txt Template

```
# Core scientific dependencies
numpy==1.24.3
scipy==1.11.1
pandas==2.0.3
scikit-learn==1.3.0
torch==2.0.1
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0

# Statistical analysis
statsmodels==0.14.0
pingouin==0.5.3
arviz==0.16.1

# Data handling
pyarrow==12.0.1
fastparquet==2023.4.0
h5py==3.9.0

# Configuration & validation
pydantic==2.0.3
hydra-core==1.3.2
omegaconf==2.3.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0
hypothesis==6.82.0

# Documentation
mkdocs==1.4.3
mkdocs-material==9.1.18

# Reproducibility
python-dotenv==1.0.0
```

---

## 6. Dockerfile Template

```dockerfile
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /velynx

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Install package
RUN pip install --no-cache-dir -e .

# Verify
RUN python -c "from core.predictors.dirichlet_markov import DirichletMarkovPredictor"

# Default command
CMD ["bash", "reproduce.sh"]
```

---

## 7. CITATION.cff Template

```yaml
cff-version: 1.2.0
message: "If you use this artifact, please cite the associated paper."
authors:
  - family-names: "Author"
    given-names: "Full Name"
    orcid: "https://orcid.org/XXXX-XXXX-XXXX-XXXX"
title: "Program D: Error-Gated Structure Acquisition — Reproducibility Package"
version: 1.0.0
date-released: 2026-XX-XX
license: Apache-2.0
doi: 10.5281/zenodo.XXXXX
repository-code: "https://github.com/velynx/program_d"
```

---

## 8. Reproducibility Report Template

```markdown
# Reproducibility Verification Report

**Experiment:** Program D
**Date:** 2026-XX-XX
**Hardware:** RTX 3090, 64GB RAM, Ubuntu 22.04
**Python:** 3.10.11
**PyTorch:** 2.0.1+cu118

## Reproduction Results

### E0
- Held-out LL (T): X.XX ± X.XX
- Held-out LL (C1): X.XX ± X.XX
- Held-out LL (C2): X.XX ± X.XX
- T vs C1: p = X.XXX, d = X.XX
- T vs C2: p = X.XXX, d = X.XX
- M(θₖ) margin: X.XX
- **Kill criteria: PASS / FAIL**

### EXP-1
- ECE: X.XXX
- ECE < 0.1: PASS/FAIL
- Tier calibration: [table]
- **Kill criteria: PASS / FAIL**

### EXP-2
- Framed: X.XX ± X.XX
- Unframed: X.XX ± X.XX
- p = X.XXX, d = X.XX
- **Kill criteria: PASS / FAIL**

### EXP-3
- Transfer (emergent): X.XX ± X.XX
- Transfer (random): X.XX ± X.XX
- p = X.XXX, d = X.XX
- **Kill criteria: PASS / FAIL**

## Numerical Tolerance

- Held-out LL: ±0.01 (acceptable)
- ECE: ±0.005 (acceptable)
- p-values: may vary with stochastic tests; BF₁₀ preferred
- Effect sizes: ±0.05 (acceptable)

## Environment Verification

- [ ] All seeds produce identical results when re-run
- [ ] CUDA deterministic mode enabled
- [ ] PYTHONHASHSEED set
- [ ] All dependencies at pinned versions
- [ ] GPU compute matches paper claims
- [ ] Runtime within 2x of paper claims

## Status

- [ ] All experiments reproduce within tolerance
- [ ] All kill criteria evaluated
- [ ] All expected outputs generated
- [ ] All figures/tables reproducible from data

**Overall:** REPRODUCED / FAILED
```

---

## 9. Common Reproduction Issues

| Issue | Solution |
|-------|----------|
| CUDA out of memory | Reduce batch size; use gradient accumulation |
| Different PyTorch version | Pin to exact version in requirements.txt |
| Non-deterministic results | Enable CUDA deterministic; set all seeds |
| Missing data | Check Zenodo DOI; re-download |
| Path errors | Use absolute paths in scripts; check `os.getcwd()` |
| Permission errors | `chmod +x reproduce.sh` |
| Port conflicts (if API) | Change port in `.env` |

---

**Template Version:** 1.0
**Last Updated:** 2026-07-03