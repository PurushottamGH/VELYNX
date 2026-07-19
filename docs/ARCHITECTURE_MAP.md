# VELYNX ARCHITECTURE MAP

**Authority:** Chief Systems Architect inspection, 2026-07-07.
**Method:** Every claim verified against the actual file on disk this session. No
prior documentation was trusted. The two sibling audit documents
(`EXECUTION_GUIDE_AUDIT.md`, `REPRODUCIBILITY_AUDIT.md`) were found to make
multiple false existence claims and are NOT used as sources here.
**Epistemic tags:** `[FACT]` = verified against code/file this session.
`[INFERENCE]` = derived from verified facts but not directly observed.
`[RISK]` = a hazard inferred from the evidence. "Insufficient evidence" is used
where a claim could not be verified; we never guess.
**Canonical authority:** `PROGRAM_D_CANONICAL.md` is the single source of truth
(canon lines 3-4). Where any document conflicts with it, the canon wins and the
document is a defect.

---

## 0. Canonical program taxonomy (verified)

`[FACT]` `PROGRAM_D_CANONICAL.md` Section 2 (lines 42-45) defines exactly four
programs:

| Program | Canonical status | Evidence |
|---|---|---|
| **Program A** | Live-truth retrieval engine. Scientific claim: honest uncertainty (calibration). Engineering product, NOT the research center. | canon Section 2 line 42 |
| **Program B** | Authored affective concept graph ("Soul Graph"). Only surviving science: the affective-indexing kernel (H2). The 32 authored concepts + edge labels are `[REJECTED]` designer artifacts. | canon Section 2 line 43 |
| **Program C** | Symbolic cognitive stack (~24-30k LOC). Reduced to a single testable claim: error-gated structure acquisition (H*). Everything else is scaffolding. | canon Section 2 line 44, Section 5 |
| **Program D** | This audit/falsification protocol over A/B/C. | canon Section 2 line 45 |

`[FACT]` Canon Section 3 (lines 49-57) records the PI verdict as REDESIGN: the
old thesis ("raise a developing symbolic mind") is retired. Three surviving
deliverables, in priority order: (1) Program A as honest product (gated on
EXP-1, currently `[REJECTED]`-state), (2) H2 affective indexing (the only
possibly-novel question), (3) H* demoted to one cheap experiment E0.

`[FACT]` Canon Section 7 (line 130): the experiment set is exactly four frozen
experiments: EXP-0, EXP-1, EXP-2, E0. EXP-3, EXP-4, R2, R3F are NOT part of the
redesigned program; R1 is closed evidence (Section 8), not a live experiment.

---

## 1. Subsystem inventory (verified against disk)

Each row below was verified by listing the actual directory contents this
session. "Status" reflects what the code IS, not what any document CLAIMS.

| # | Subsystem | Path on disk | Purpose | Status | Shipped? |
|---|---|---|---|---|---|
| 1 | Core scientific primitives | `core/` | Single source of truth for the 5 canonical math primitives (x_t, P_theta, L, G, M) | **LIVE** | Yes (`pyproject.toml:22`) |
| 2 | Experiments framework | `experiments/` | EXP0, E0, EXP1 + stubs | **PARTIAL** | Yes (`pyproject.toml:23`) |
| 3 | Validation framework | `validation/` | Regression gate, artifact validation, shared metrics | **LIVE** | Yes (`pyproject.toml:24`) |
| 4 | Research/study harness | `research/` | Side-effect-free harness; attribution, evaluation, policies, proposals | **LIVE** | No (not in packages.find) |
| 5 | Backend application layer | `backend/` | Replay, ontology, identity, telemetry, DB, soul, self_model | **LIVE (engineering)** | No (`pyproject.toml:28` excludes backend) |
| 6 | Program A retrieval | `program_a/` | Unified retriever (Arxiv, Brave, DuckDuckGo, etc.), NLP | **STUB / UNDER IMPLEMENTATION** | No (not in packages.find) |
| 7 | Program B soul graph | `program_b/` | claimed: authored affective concept graph | **STUB** (only empty `__init__.py`) | No |
| 8 | Program C cognitive stack | `program_c/` | claimed: symbolic cognitive stack, 13 subpackages | **STUB** (all subdirs: 0-byte `__init__.py` only) | No |
| 9 | Benchmarks | `benchmarks/` | Evaluation harnesses | **UNKNOWN** (not inspected this session) | Yes (`pyproject.toml:25`) |
| 10 | Tests | `tests/` | Unit/integration/EXP1/fixtures | **LIVE** | n/a |

### 1.1 Core subpackages (`core/`) - `[FACT]` verified

`[FACT]` `core/__init__.py` (9 lines) declares core the "Single source of truth
for all reusable scientific machinery" with five subpackages. All five exist
with non-trivial implementation:

| Subpackage | Files (verified sizes) | Canonical primitive | Canon ref |
|---|---|---|---|
| `core/predictors/` | `base.py` (1,156 B), `dirichlet_markov.py` (15,440 B) | `P_theta` (growable predictor class) | Section 5.2 |
| `core/emergence/` | `emergence_statistic.py` (1,941 B), `null_referenced_test.py` (2,843 B) | `M` (emergence statistic, null-referenced NMI) | Section 5.5 |
| `core/mdl/` | `mdl_growth.py` (8,828 B) | `G` (MDL growth operator) | Section 5.4 |
| `core/measurement/` | `metrics.py` (3,247 B), `proper_scoring.py` (3,962 B) | `L` (proper scoring / log-loss) | Section 5.3 |
| `core/controls/` | `fixed_capacity.py`, `random_growth.py`, `shuffled_input.py` | C1/C2/C3 controls for E0 | Section 7 E0 |

`[FACT]` `core/mdl/mdl_growth.py:28` defines `BITS_PER_PARAMETER = 1.0` as a
scientific constant. Line 85 implements `compute_lambda_model` returning
`k * b + n * math.log2(N)` (the canonical Section 5.4 derivation). Line 131
implements the F-A corrected marginal cost `b + log2(N)`. Lines 218-219
`should_grow` uses the derived (non-tunable) threshold.
**The code is canonical-compliant.**

`[FACT]` `parameter_registry.yaml:55-62` records `mdl.lambda_model` with
formula `"lambda_model = k * b + n * log2(N)"` and role
`"Derived MDL complexity penalty. NOT configurable (PROGRAM_D_CANONICAL.md Section 5.4)"`.
`b` is marked "scientific constant, not tunable". Lines 76-79 explicitly
comment out the rejected configurable thresholds.
**The registry is canonical-compliant.**

### 1.2 Experiments (`experiments/`) - `[FACT]` verified

| Dir | Contents (verified) | Status |
|---|---|---|
| `experiments/E0/` | `run.py` (27,526 B), `decision.py` (19,337 B), `analysis.py` (12,493 B), `dataset.py`, `growth_diagnostics.py`, `leakage_check.py`, `config.json` | **LIVE** - central H* experiment |
| `experiments/EXP0/` | `run_exp0.py` (12,569 B), `paraphrases.json` (18,803 B), `dataset.py`, `detectors.py`, `analysis.py`, `leakage_check.py`, + 6 docs | **LIVE** - precondition experiment |
| `experiments/EXP1/` | `run.py` (10,962 B), `decision.py` (10,794 B), `dataset.py` (14,813 B), `calibration.py`, `rubric.py`, `report.py`, `manifest.py`, `artifact_specs.py`, `program_a_adapter.py`, `config.json` | **LIVE** - H1 calibration gate, fully implemented |
| `experiments/EXP2/` | `__init__.py` (0 B) only | **STUB** |
| `experiments/EXP3/` | `__init__.py` (0 B) only | **STUB / REJECTED** (canon Section 6 H3 rejected, Section 7 EXP-3 removed) |
| `experiments/EXP4/` | `__init__.py` (0 B) only | **STUB / REJECTED** (canon Section 7 EXP-4 removed) |
| `experiments/R1/` | `__init__.py` (0 B) only | **STUB** (canon Section 7: R1 is closed evidence, not live) |
| `experiments/R3F/` | `__init__.py` (0 B) only | **STUB / REJECTED** (canon Section 7 R3F not part of redesigned program) |
| `experiments/coverage/` | `__init__.py` (0 B) only | **STUB** |

`[FACT]` `repository_v2.md:62-69` CLAIMS these stub dirs contain
`preregistration.md`, `protocol.md`, `run.py`, `analysis.py`. This is FALSE for
every stub directory. The document describes a structure that does not exist.

### 1.3 Backend (`backend/`) - `[FACT]` verified

`[FACT]` `backend/` is NOT shipped (`pyproject.toml:28` excludes `backend*`).
Canon Section 2 line 42 marks it "engineering, not the research center".
However it contains substantial live code including subsystems the canon marks
`[REJECTED]` as science:

| Backend dir | Verified contents | Canonical science status |
|---|---|---|
| `backend/self_model/` | `self_model.py`, `identity_store.py`, `health_monitor.py`, `baseline_tracker.py`, `self_audit.py` | `[REJECTED]` as science (canon Section 5 line 90: "the self-model") |
| `backend/soul/` | `soul_graph.py` (28,080 B), `concepts.json` (26,020 B) | `[REJECTED]` as science (canon Section 5 line 90: "the 32 soul concepts", "the hand-authored ontology") |
| `backend/cognition/`, `backend/knowledge/`, `backend/memory/`, `backend/simulation/`, `backend/ops/` | present (not fully inspected) | Engineering scaffolding |

`[FACT]` `repository_v2.md:178` CLAIMS `program_c/self_model/` contains
`self_model.py`, `identity_store.py`, etc. This is FALSE.
`program_c/self_model/` contains only a 0-byte `__init__.py`. The real code
lives in `backend/self_model/`.
`[RISK]` The canonical disposition instructions (Section 9-DeepSeek line 172:
"Move to archive: program_c/self_model/") target a path that is already empty;
the actual rejected code at `backend/self_model/` is not addressed by that
instruction.

### 1.4 Research (`research/`) - `[FACT]` verified

`[FACT]` `research/` contains live code: `attribution/`, `evaluation/`,
`policies/` (including `free_energy.py`), `proposals/`, `tests/`, plus
`runner.py`, `stats.py`, `metrics.py`, `r3e_benchmark.py`.
`[FACT]` `research/policies/free_energy.py` implements the `E = lambda*H +
mu*S + nu*A` formula that canon Section 5 line 90 marks `[REJECTED]` and canon
Section 8 line 144 reports as statistically indistinguishable from null
(R1 p=0.866).
`[RISK]` This rejected policy remains live in the research tree; it is not
archived.

---

## 2. Real import graph (core dependency direction)

`[FACT]` The canonical dependency direction is one-way: experiments and
validation import FROM core; core imports from nothing in the project.

Verified import edges (source file -> imported module):

    experiments/E0/run.py
      +-> core.predictors.dirichlet_markov.DirichletMarkovPredictor   (run.py:38)
      +-> core.mdl.mdl_growth.should_grow                              (run.py:39)
      \-> experiments.E0.dataset.NonlinearLatentEnvironment            (run.py:40)

    experiments/EXP1/run.py
      +-> experiments.EXP1.dataset  (run.py:16-24)
      +-> experiments.EXP1.decision (run.py:25)
      +-> experiments.EXP1.manifest (run.py:26-31)
      \-> experiments.EXP1.program_a_adapter (run.py:32-36)

    experiments/EXP1/decision.py
      +-> experiments.EXP1.calibration (decision.py:8)
      \-> experiments.EXP1.dataset     (decision.py:9-14)

    experiments/EXP1/dataset.py
      \-> experiments.EXP1.rubric (dataset.py:14)

    experiments/EXP1/manifest.py
      \-> experiments.EXP1.dataset (manifest.py:12)

    experiments/EXP1/report.py        <-- NOT imported by run.py
      +-> experiments.EXP1.calibration (report.py:8)
      \-> experiments.EXP1.decision    (report.py:9)

    experiments/EXP1/artifact_specs.py <-- NOT imported by run.py (imports nothing from EXP1)

`[FACT]` `core/` has zero imports from `experiments/`, `backend/`, `research/`,
or `validation/` (verified by reading core modules). The core is a true leaf -
no upward coupling.
`[INFERENCE]` No import cycles exist in the `core/` <- `experiments/` path.

`[FACT]` `experiments/E0/run.py:34-36` mutates `sys.path` at import time
(`sys.path.insert(0, str(_project_root))`). This is a hidden coupling to the
filesystem layout and a packaging smell; it bypasses the installed package
boundary declared in `pyproject.toml`.

---

## 3. Cross-cutting concerns

### 3.1 Persistence
`[FACT]` SQLite databases exist at repo root: `velynx_identity.db`,
`velynx_state.db`, `concept_birth.db`, plus `-shm`/`-wal` sidecars.
`[RISK]` Multiple `.db` files at repo root risk accidental commit; `.gitignore`
handling not verified this session.

### 3.2 Configuration
`[FACT]` `experiments/E0/config.json` (458 B), `experiments/EXP1/config.json`
(2,333 B) are frozen experiment configs. `parameter_registry.yaml` (79 lines)
records every scientific parameter with location and role.
`[FACT]` `configs/` and `infra/config/` both exist (see `repository_v2.md`
removal notes line 279); duplication not resolved.

---

## 4. Status legend

- **LIVE** - real, non-trivial implementation present and used.
- **PARTIAL** - some components live, some stub/missing.
- **STUB** - directory exists but contains only empty `__init__.py`; no implementation.
- **REJECTED** - canon marks this `[REJECTED]`; must not appear in live science (may persist as engineering).
- **ARCHIVED** - moved to `archive/` (canon Section 9).
- **UNKNOWN** - not inspected this session; insufficient evidence.
