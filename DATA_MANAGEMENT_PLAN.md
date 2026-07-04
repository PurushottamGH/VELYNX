# VELYNX Data Management Plan

**Compliance**: NSF 22-1, NIH GEN-03, FAIR Principles, GDPR (no personal data)  
**Project**: VELYNX Cognitive Architecture  
**PI**: [Name]  
**Institution**: [Institution]  
**Version**: 1.0  
**Date**: 2026-07-03

---

## 1. Data Types & Sources

| Data Type | Format | Volume (est.) | Source | Sensitivity |
|-----------|--------|---------------|--------|-------------|
| Synthetic sensor streams | JSON/CSV/NumPy | <1 GB/year | `environment.py` (procedural) | Public |
| Symbolic sequences (C1–C6) | JSON/CSV | <100 MB/year | `cognitive_core.py` demos | Public |
| Benchmark results | JSON/CSV | <50 MB/year | `validation/runner.py` output | Public |
| Model checkpoints | JSON | <10 MB/year | `StableBeliefModel`, `DirichletMarkovModel` serialization | Public |
| Experimental logs | JSONL | <500 MB/year | `BenchmarkRunner.output_log` | Public |
| Ablation study outputs | JSON/CSV | <200 MB/year | `validation/ablation_*.py` | Public |
| Figures (publication) | PNG/PDF/SVG | <100 MB | Matplotlib/Seaborn generated | Public |
| Source code | Python (.py) | ~30 MB | Repository | Public (MIT) |

**Total Annual Volume**: <2 GB (well within institutional storage limits)

**No Human Subjects Data**: All data is synthetically generated. No PII, PHI, or sensitive information.

---

## 2. Metadata Standards

| Standard | Application |
|----------|-------------|
| **DataCite** | Dataset DOIs via Zenodo |
| **JSON Schema** | All JSON/JSONL outputs validated against schemas in `validation/schemas/` |
| **CSV Headers** | Self-describing: `tick,vector,prediction,surprise,regime` |
| **README per dataset** | Human-readable description, generation script, version |
| **Code-as-Metadata** | Generation scripts (`environment.py`, `cognitive_core.py`) serve as executable documentation |

**Example Metadata Record** (for benchmark result):
```json
{
  "title": "VELYNX C6 Catastrophic Forgetting Ablation — Split MNIST",
  "creators": [{"name": "PI", "affiliation": "Institution"}],
  "description": "Comparison of DirichletMarkov vs StableBeliefModel vs EWC/SI/GEM/ER on Split MNIST, 10 seeds",
  "keywords": ["continual learning", "catastrophic forgetting", "predictive processing"],
  "license": "CC-BY-4.0",
  "funding": ["NSF IIS-XXXXXXX"],
  "version": "1.0",
  "generated_by": "validation/ablation_continual.py",
  "seed_range": [0, 9],
  "date_created": "2026-07-15"
}
```

---

## 3. Access & Sharing Policies

| Artifact | License | Repository | DOI | Embargo |
|----------|---------|------------|-----|---------|
| Source code | MIT | GitHub (public) | Zenodo (per release) | None |
| Synthetic datasets | CC-BY-4.0 | Zenodo | Yes | None |
| Benchmark results | CC-BY-4.0 | Zenodo | Yes | None |
| Experimental logs | CC-BY-4.0 | Zenodo | Yes | None |
| Preprints | CC-BY-4.0 | arXiv | Yes | None |
| Peer-reviewed papers | Publisher policy | Institutional repo | Crossref | Per publisher |

**Access Statement**: "All data and code supporting the findings of this work are openly available at [Zenodo DOI] and [GitHub URL] under MIT/CC-BY-4.0 licenses."

---

## 4. Reuse & Redistribution

- **Permitted**: Commercial/non-commercial reuse, modification, redistribution with attribution
- **Citation Requirement**: Cite the VELYNX paper + dataset DOI
- **Derivative Works**: Encouraged; submit PR to upstream or fork
- **No Restriction**: No patents, no proprietary formats, no encryption

---

## 5. Preservation & Archival

| Repository | Retention | Backup |
|------------|-----------|--------|
| **Zenodo** (primary) | 10+ years (institutional guarantee) | CERN replication |
| **GitHub** (code) | Indefinite | GitHub Archive Program (Arctic Code Vault) |
| **Institutional Repository** | Permanent | LOCKSS / CLOCKSS |
| **arXiv** (preprints) | Permanent | Cornell University Library |

**Fixity**: SHA-256 checksums recorded at deposit. Annual verification.

---

## 6. Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| **PI** | Overall DMP compliance; annual review; deposit approval |
| **PhD Student** | Day-to-day data generation; metadata creation; checksum verification |
| **Postdoc** | Ablation study data curation; schema validation |
| **Institutional Librarian** | DOI minting; long-term preservation monitoring |
| **IT / Research Computing** | Storage allocation; backup verification |

---

## 7. Budget for Data Management

| Item | Annual Cost | Notes |
|------|-------------|-------|
| Zenodo storage | $0 | Free for open data |
| GitHub (private during review) | $0 | Free for academic |
| Institutional repository | $0 | Included in overhead |
| Personnel time (curation) | ~$5,000 | 0.1 FTE PhD student |
| **Total** | **~$5,000/year** | Covered by grant direct costs |

---

## 8. Timeline

| Milestone | Target Date |
|-----------|-------------|
| DMP v1.0 finalized | 2026-07-15 |
| First dataset deposit (synthetic env) | 2026-08-01 |
| Code release v1.0 (MIT) | 2026-09-01 |
| Ablation study data deposits | 2026-12-01 (Aim 1), 2027-03-01 (Aim 2), 2027-06-01 (Aim 3) |
| Annual DMP review | Each grant anniversary |
| Final archive deposit | Project end + 30 days |

---

## 9. Ethical & Legal Compliance

- **Human Subjects**: N/A (no human data)
- **Animal Subjects**: N/A
- **Dual Use**: Cognitive architecture for scientific discovery; no weapons applications. See Broader Impacts.
- **Export Control**: EAR99 (open source, fundamental research)
- **GDPR**: No personal data processed
- **Indigenous Data Sovereignty**: N/A

---

## 10. Monitoring & Reporting

- **Quarterly**: PhD student verifies new data deposits have metadata + checksums
- **Annually**: PI reviews DMP compliance; updates for new data types
- **Final Report**: Data availability statement in all publications; final archive manifest

---

**Approval**: _________________________ (PI)  Date: ___________

**Institutional Sign-off**: _________________________ (Research Admin)  Date: ___________