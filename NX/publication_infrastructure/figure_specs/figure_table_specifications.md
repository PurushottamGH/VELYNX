# Figure & Table Specifications — Program D Papers

**Standard:** NeurIPS / ICML / ICLR / Nature MI / Science Robotics
**Program:** D (E0, EXP-1, EXP-2, EXP-3)

---

## 1. Figure Specifications

### 1.1 Universal Requirements
| Requirement | Specification |
|-------------|---------------|
| **Format** | Vector (PDF/SVG) preferred; PNG ≥300 DPI if raster |
| **Color space** | CMYK for print; sRGB for screen |
| **Font** | Helvetica/Arial (sans-serif); 8–10 pt axis labels; 7–9 pt tick labels |
| **Line width** | 1.5–2 pt for primary; 1 pt for secondary |
| **Color palette** | Colorblind-safe (viridis, cividis, Okabe-Ito); no red-green |
| **Width** | Single column: 85 mm (3.35 in); Double column: 178 mm (7 in) |
| **Height** | ≤ single column width (aspect ratio ~1:1 to 1:1.6) |
| **File naming** | `fig{N}_{description}.{pdf|svg|png}` |

### 1.2 E0 Figures (H*: Error-Gated Structure Acquisition)

#### Figure 1: Experimental Design Schematic
| Panel | Content | Type | Width |
|-------|---------|------|-------|
| A | Environment: Nonlinear latent generator → observation mixing | Diagram | Single |
| B | Treatment (T): Error-gated growth ON | Diagram | Single |
| C | Control 1 (C1): Fixed capacity | Diagram | Single |
| D | Control 2 (C2): Random growth timing | Diagram | Single |
| E | Control 3 (C3): Shuffled input | Diagram | Single |
| F | Measurements: DV-a (held-out LL), DV-b (M(θₖ)) | Diagram | Single |
**Composite:** 2×3 grid, double-column width
**Caption:** "E0 experimental design. (A) Synthetic environment with K latent states and nonlinear observation mixing. (B–E) Four conditions: Treatment (error-gated growth), Control 1 (fixed capacity), Control 2 (capacity-matched random growth), Control 3 (shuffled input). (F) Primary dependent variables: DV-a = held-out predictive log-likelihood; DV-b = emergence statistic M(θₖ) = NMI(learned, true) - NMI(learned, C3)."

#### Figure 2: Primary Results — Held-Out Log-Likelihood (DV-a)
| Panel | Content | Type | Width |
|-------|---------|------|-------|
| A | Box/violin plot: T, C1, C2, C3 held-out LL (N seeds) | Plot | Single |
| B | Learning curves: Mean ± 95% CI per condition across training | Plot | Single |
| C | Contrast estimates: T-C1, T-C2 with 95% CI | Forest plot | Single |
**Composite:** 1×3 or 2×2, double-column
**Statistics on figure:** Omnibus p, contrast p-values, effect sizes (d with CI)

#### Figure 3: Primary Results — Emergence Statistic (DV-b)
| Panel | Content | Type | Width |
|-------|---------|------|-------|
| A | M(θₖ) distribution: T, C1, C2, C3 (violin + points) | Plot | Single |
| B | Null-referenced: M(θₖ)_T - M(θₖ)_C3 with pre-registered margin | Plot | Single |
| C | NMI heatmap: Learned partition vs true latent (T vs C3) | Heatmap | Single |
**Composite:** 1×3, double-column

#### Figure 4: Ablation / Sensitivity (Supplementary)
| Panel | Content |
|-------|---------|
| S1 | λ_model sensitivity (MDL threshold) |
| S2 | K (latent states) sensitivity |
| S3 | Observation mixing nonlinearity sensitivity |
| S4 | Seed-wise trajectories (all seeds, all conditions) |

---

### 1.3 EXP-1 Figures (H1: Calibration)

#### Figure 1: Reliability Diagram
| Panel | Content | Type |
|-------|---------|------|
| A | Reliability diagram: 10 bins, identity line, system curve | Plot |
| B | Histogram of confidences per tier (CERTAIN/PROBABLE/DEBATED/UNKNOWN) | Stacked bar |
| C | ECE comparison: System vs Constant baseline (bootstrap CI) | Bar + error bars |
**Width:** Single column

#### Figure 2: Tier-Level Calibration (Supplementary)
| Panel | Content |
|-------|---------|
| S1 | Per-tier accuracy vs confidence with binomial CI |
| S2 | Calibration curves per query type (fact/ambiguous/hallucination) |
| S3 | ECE vs number of queries (convergence) |

---

### 1.4 EXP-2 Figures (H2: Affective Indexing)

#### Figure 1: Task Performance
| Panel | Content | Type |
|-------|---------|------|
| A | Framed vs Unframed: Paired dot plot / violin + lines | Plot |
| B | Effect size per task domain (debugging, planning, etc.) | Forest plot |
| C | Raw scores heatmap: Tasks × Seeds × Condition | Heatmap |
**Width:** Double column

---

### 1.5 EXP-3 Figures (H3: Emergent Development)

#### Figure 1: Transfer Learning
| Panel | Content | Type |
|-------|---------|------|
| A | Held-out LL on Task B: Emergent vs Random init | Plot |
| B | Emergent structure visualization (latent space) | Scatter/TSNE |
| C | Learning curves: Task A → Task B transfer | Plot |
**Width:** Double column

---

## 2. Table Specifications

### 2.1 Universal Table Style
| Requirement | Specification |
|-------------|---------------|
| **Format** | LaTeX `booktabs` (no vertical lines) |
| **Font** | 8–9 pt |
| **Alignment** | Numbers: decimal-aligned (`siunitx` S column); Text: left |
| **Significance** | † p<0.1, * p<0.05, ** p<0.01, *** p<0.001 |
| **CI format** | `X.XX [X.XX, X.XX]` |
| **Effect size** | Report with CI: `d = 0.52 [0.12, 0.91]` |

### 2.2 E0 Tables

#### Table 1: E0 Primary Results (Main Paper)
| Condition | Held-Out LL (DV-a) | M(θₖ) (DV-b) |
|-----------|-------------------|--------------|
| T (Error-gated) | X.XX ± X.XX | X.XX ± X.XX |
| C1 (Fixed) | X.XX ± X.XX | X.XX ± X.XX |
| C2 (Random growth) | X.XX ± X.XX | X.XX ± X.XX |
| C3 (Shuffled) | X.XX ± X.XX | X.XX ± X.XX |
| **Omnibus p** | **p = X.XXX** | **p = X.XXX** |
| **T vs C1** | **p = X.XXX, d = X.XX** | **p = X.XXX, d = X.XX** |
| **T vs C2** | **p = X.XXX, d = X.XX** | **p = X.XXX, d = X.XX** |
| **Kill: T>C1 @ p<0.01** | **PASS/FAIL** | — |
| **Kill: T>C2 @ p<0.01** | **PASS/FAIL** | — |
| **Kill: DV-b > Margin** | — | **PASS/FAIL** |

#### Table 2: E0 Per-Seed Data (Supplementary)
| Seed | T_LL | C1_LL | C2_LL | C3_LL | T_M | C1_M | C2_M | C3_M |
|------|------|-------|-------|-------|-----|------|------|------|
| 1 | X.XX | X.XX | X.XX | X.XX | X.XX | X.XX | X.XX | X.XX |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

#### Table 3: E0 Assumption Checks (Supplementary)
| Check | Statistic | p-value | Pass/Fail |
|-------|-----------|---------|-----------|
| Normality (T) | W = X.XX | X.XXX | PASS/FAIL |
| Normality (C1) | W = X.XX | X.XXX | PASS/FAIL |
| Normality (C2) | W = X.XX | X.XXX | PASS/FAIL |
| Normality (C3) | W = X.XX | X.XXX | PASS/FAIL |
| Homoscedasticity | F = X.XX | X.XXX | PASS/FAIL |

#### Table 4: E0 Sensitivity Analysis (Supplementary)
| Parameter | Values Tested | T vs C1 (p, d) | T vs C2 (p, d) | DV-b Margin |
|-----------|---------------|----------------|----------------|-------------|
| λ_model | [0.1, 0.5, 1.0, 2.0] | ... | ... | ... |
| K (latent states) | [3, 5, 7, 10] | ... | ... | ... |
| Mixing nonlinearity | [tanh, ReLU, MLP] | ... | ... | ... |

---

### 2.3 EXP-1 Tables (H1: Calibration)

#### Table 1: ECE Results (Main Paper)
| Metric | System | Constant Baseline | Δ | p (bootstrap) |
|--------|--------|-------------------|---|---------------|
| ECE (10-bin) | X.XXX [CI] | X.XXX [CI] | X.XXX [CI] | X.XXX |
| ECE (15-bin) | X.XXX [CI] | X.XXX [CI] | X.XXX [CI] | X.XXX |
| **Kill: ECE < 0.1** | **PASS/FAIL** | — | — | — |
| **Kill: Better than constant** | **PASS/FAIL** | — | — | — |

#### Table 2: Tier-Level Calibration (Main Paper)
| Tier | N | Empirical Accuracy | Claimed Range | |Acc - Conf| |
|------|---|-------------------|---------------|------------|
| CERTAIN | N | X.XX [CI] | ≥0.95 | X.XX |
| PROBABLE | N | X.XX [CI] | [0.7, 0.95) | X.XX |
| DEBATED | N | X.XX [CI] | [0.3, 0.7) | X.XX |
| UNKNOWN | N | X.XX [CI] | <0.3 | X.XX |

#### Table 3: Per-Query-Type Calibration (Supplementary)
| Query Type | N | ECE | Accuracy |
|------------|---|-----|----------|
| Known facts | N | X.XXX | X.XX |
| Ambiguous | N | X.XXX | X.XX |
| Hallucination traps | N | X.XXX | X.XX |

---

### 2.4 EXP-2 Tables (H2: Affective Indexing)

#### Table 1: Primary Task Results (Main Paper)
| Condition | Mean Score ± SD | N (tasks × seeds) |
|-----------|-----------------|-------------------|
| Framed | X.XX ± X.XX | N |
| Unframed | X.XX ± X.XX | N |
| **Difference** | **X.XX [CI]** | — |
| **Test** | **t = X.XX, p = X.XXX** | — |
| **Effect size** | **d = X.XX [CI]** | — |
| **BF₁₀** | **X.XX** | — |
| **Kill criterion** | **PASS/FAIL** | — |

#### Table 2: Per-Task Breakdown (Supplementary)
| Task ID | Domain | Framed | Unframed | Δ | p (paired) |
|---------|--------|--------|----------|---|------------|
| 1 | Debugging | X.XX | X.XX | X.XX | X.XXX |
| 2 | Planning | X.XX | X.XX | X.XX | X.XXX |
| ... | ... | ... | ... | ... | ... |

---

### 2.5 EXP-3 Tables (H3: Emergent Development)

#### Table 1: Transfer Results (Main Paper)
| Condition | Held-Out LL (Task B) | N seeds |
|-----------|---------------------|---------|
| Emergent structure | X.XX ± X.XX | N |
| Random init | X.XX ± X.XX | N |
| **Difference** | **X.XX [CI]** | — |
| **Test** | **t = X.XX, p = X.XXX** | — |
| **Effect size** | **d = X.XX [CI]** | — |
| **Kill criterion** | **PASS/FAIL** | — |

---

## 3. Supplementary Material Figure/Table Numbering

| Experiment | Main Figures | Main Tables | Supplementary Figures | Supplementary Tables |
|------------|--------------|-------------|----------------------|---------------------|
| E0 | 3–4 | 1–2 | S1–S6 | S1–S4 |
| EXP-1 | 1–2 | 1–2 | S1–S3 | S1–S2 |
| EXP-2 | 1 | 1 | S1 | S1 |
| EXP-3 | 1 | 1 | S1–S2 | S1 |

**Naming convention:** `Figureing convention:** `Figure S1`, `Table S1` (not `Figure 1S`)

---

## 4. Data Availability Statements (Per Figure/Table)

Each figure/table must have a corresponding data file:
- `fig1_data.csv` — raw data for Figure 1
- `table1_data.csv` — raw data for Table 1
- Deposited on Zenodo with DOI
- Referenced in caption: "Data available at DOI: 10.5281/zenodo.XXXXX"

---

## 5. Generation Pipeline (Reproducibility)

All figures/tables generated by analysis scripts:
```
experiments/E0/analysis.py --output-dir artifacts/experiments/E0/figures/
experiments/EXP1/analysis.py --output-dir artifacts/experiments/EXP1/figures/
experiments/EXP2/analysis.py --output-dir artifacts/experiments/EXP2/figures/
experiments/EXP3/analysis.py --output-dir artifacts/experiments/EXP3/figures/
```

**Required outputs per experiment:**
- `figures/` — All PDF/SVG figures
- `tables/` — All LaTeX tables (.tex) + CSV data
- `stats/` — JSON with all test statistics, CIs, effect sizes
- `manifest.json` — Maps each figure/table to generating script + data file

---

**Template Version:** 1.0
**Last Updated:** 2026-07-03