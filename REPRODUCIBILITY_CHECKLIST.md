# VELYNX Reproducibility Checklist

**Target**: ML Reproducibility Checklist (NeurIPS/ICML/ICLR) + ACM Artifact Evaluation  
**Standard**: "Results can be independently reproduced by a third party using the provided artifacts"  
**Status**: Pre-submission audit — all items must be ✅ before submission

---

## 1. Code Availability

| Item | Status | Evidence / Action Required |
|------|--------|----------------------------|
| Public repository | ✅ | GitHub (to be created) |
| License (MIT/BSD/Apache-2.0) | ✅ | MIT — add LICENSE file |
| DOI for release (Zenodo) | 🔴 | Create on first release |
| Code completeness | 🟡 | Core exists; need `requirements.txt`, `setup.py`, CLI entry points |
| No proprietary dependencies | ✅ | Pure Python stdlib only (verified) |
| Hardware requirements documented | ✅ | CPU only; no GPU; <4 GB RAM |

---

## 2. Compute Environment

| Item | Status | Evidence / Action Required |
|------|--------|----------------------------|
| Python version pinned | 🔴 | Add `python_requires=">=3.11"` in `pyproject.toml` |
| Dependency lock file | 🔴 | Create `requirements.txt` (stdlib only — document this) |
| Conda environment file | 🟡 | Create `environment.yml` for convenience |
| Dockerfile | 🔴 | Create `Dockerfile` (python:3.11-slim) |
| Container image on registry | 🔴 | Push to GHCR/Docker Hub on release |
| Random seeds controlled | ✅ | All stochastic components accept `seed` param (`random.Random(seed)`) |
| CUDA/GPU not required | ✅ | Verified — no torch/tensorflow/jax imports |

---

## 3. Data & Artifacts

| Item | Status | Evidence / Action Required |
|------|--------|----------------------------|
| Synthetic data generation scripts | ✅ | `environment.py`, `cognitive_core.py` demos |
| Pre-generated datasets (Zenodo) | 🔴 | Deposit before submission |
| Dataset DOIs | 🔴 | Mint via Zenodo |
| Data licenses (CC-BY-4.0) | 🔴 | Add to dataset metadata |
| Checksums (SHA-256) | 🔴 | Generate at deposit |
| Data format documentation | 🟡 | Add `validation/schemas/` with JSON schemas |

---

## 4. Experimental Pipeline

| Item | Status | Evidence / Action Required |
|------|--------|----------------------------|
| Single-command reproduction | 🟡 | `make eval` or `python -m validation.runner` — needs CLI wrapper |
| All hyperparameters configurable | 🟡 | `validation/runner.py` accepts config dict; need CLI args |
| Experiment tracking (logs) | ✅ | `BenchmarkRunner.output_log` captures all ticks |
| Reproducible random seeds | ✅ | `dataset.reset()`, `monitor` seed, `runner` config |
| Pre-computed results provided | 🔴 | Deposit ablation study outputs to Zenodo |
| Figure generation scripts | 🔴 | Create `scripts/figures/*.py` using saved logs |
| Table generation scripts | 🔴 | Create `scripts/tables/*.py` |

---

## 5. Compute Requirements

| Experiment | Est. Time (CPU) | Est. Memory | Parallelizable |
|------------|-----------------|-------------|----------------|
| C1–C6 symbolic demo | <1 min | <100 MB | Yes (per seed) |
| C7 sensorium 5K ticks | ~2 min | <200 MB | Yes (per seed) |
| Ablation: Continual (Split MNIST) | ~30 min × 10 seeds | <1 GB | Yes (per seed) |
| Ablation: Concept birth | ~5 min × 10 seeds | <200 MB | Yes (per seed) |
| Ablation: Sensorium regime recovery | ~10 min × 10 seeds | <500 MB | Yes (per seed) |
| **Full suite (all ablations, 10 seeds)** | **~6 hours** | **<4 GB** | **Embarrassingly parallel** |

**Hardware**: Any modern laptop (4+ cores, 8+ GB RAM). No cluster needed.

---

## 6. Automation & CI

| Item | Status | Action Required |
|------|--------|-----------------|
| GitHub Actions CI | 🔴 | Create `.github/workflows/ci.yml` |
| `make test` passes | 🟡 | Add pytest config; wire up existing test stubs |
| `make eval` runs full suite | 🔴 | Create Makefile with `eval` target |
| `make figures` regenerates all figures | 🔴 | Create figure scripts |
| `make tables` regenerates all tables | 🔴 | Create table scripts |
| Pre-commit hooks | 🔴 | Add black, ruff, mypy |
| Dependency check | 🟡 | Add `pip check` to CI |

---

## 7. Documentation

| Item | Status | Action Required |
|------|--------|-----------------|
| README with quickstart | 🔴 | Create `README.md` |
| Installation instructions | 🟡 | `pip install -e .` after `pyproject.toml` |
| Usage examples | 🟡 | `python -m cognitive_core`, `python -m validation.runner` |
| API documentation | 🔴 | Add docstrings; consider Sphinx |
| Architecture diagram | 🔴 | Create `docs/architecture.png` |
| Reproducibility statement | 🔴 | Add to paper + README |

---

## 8. Artifact Evaluation Package (ACM)

| Component | Status | Notes |
|-----------|--------|-------|
| Artifact appendix | 🔴 | 2-page PDF describing artifact |
| Kick-the-tires (30 min) | 🟡 | `python -m cognitive_core` REPL works |
| Functional test (2 hr) | 🟡 | `make eval` — need to implement |
| Full reproduction (24 hr) | 🟡 | All ablations — need to implement |
| Badge application | 🔴 | Submit after acceptance |

---

## 9. Specific VELYNX Reproducibility Gaps

### Critical (Must Fix Before Submission)

1. **No `pyproject.toml` / `requirements.txt`** — reviewers cannot install
2. **No Dockerfile** — environment not containerized
3. **No ablation study scripts** — core claims (C6, C4, C7) unverified
4. **No figure/table generation scripts** — results not reproducible from logs
5. **No CI** — no evidence code runs on clean environment
6. **No pre-computed results on Zenodo** — reviewers cannot verify without running

### High Priority

7. **CLI entry points** — `velynx-core`, `velynx-eval`, `velynx-sensorium`
8. **JSON schemas for logs** — `validation/schemas/log_entry.json`
9. **Statistical testing utilities** — bootstrap CI, permutation tests
10. **Multi-seed runner** — `python -m validation.runner --seeds 10 --parallel`

### Medium Priority

11. **Sphinx docs** — `docs/` with autodoc
12. **Architecture diagram** — Mermaid or GraphViz
13. **Pre-commit config** — `.pre-commit-config.yaml`

---

## 10. Sign-Off Checklist (Pre-Submission)

- [ ] `pyproject.toml` with dependencies (stdlib), entry points, metadata
- [ ] `Dockerfile` builds and runs `make eval` successfully
- [ ] `make test` passes on clean container (GitHub Actions green)
- [ ] `make eval` completes full ablation suite in <6 hours
- [ ] `make figures` regenerates all paper figures from Zenodo logs
- [ ] `make tables` regenerates all paper tables from Zenodo logs
- [ ] All ablation logs deposited on Zenodo with DOIs
- [ ] All datasets deposited on Zenodo with DOIs
- [ ] README has "Reproduce Paper Results" section with exact commands
- [ ] Artifact appendix PDF ready
- [ ] ACM badge application submitted (if accepted)

---

**Reviewer Simulation**: "I cloned the repo, ran `docker build -t velynx . && docker run velynx make eval`, and got all tables/figures matching the paper within error bars." → **This must work.**

---

**Next Action**: Implement `pyproject.toml`, `Dockerfile`, `Makefile`, and `validation/ablation_*.py` scripts. Target: 2 weeks before submission deadline.