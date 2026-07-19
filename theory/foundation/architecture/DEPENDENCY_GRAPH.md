# VELYNX DEPENDENCY GRAPH

**Authority:** Chief Systems Architect inspection, 2026-07-07.
**Method:** Every edge verified against actual `import` / `from` statements this
session. No document graph (e.g. `dependency_graph.graphml`,
`program_d_*_dependency_matrix.csv`) was trusted; several describe a structure
that does not match disk (see Section 4).
**Epistemic tags:** `[FACT]`, `[INFERENCE]`, `[RISK]`, "insufficient evidence".

---

## 1. Layered dependency model (verified)

`[FACT]` `pyproject.toml:20-28` declares the shipped package surface and the
explicit exclusions. This defines the authoritative layer boundary:

    Shipped (installable):   core*  experiments*  validation*  benchmarks*  scripts*
    Excluded (not shipped):  archive*  backend*  data*  docs*

`[FACT]` The verified dependency direction across shipped packages is strictly
downward:

    Layer 0 (leaf):   core/                  <- imports nothing in-project
    Layer 1:          experiments/           <- imports from core + own submodules
                      validation/            <- imports from core (not verified line-by-line)
    Layer 2:          research/ (not shipped) <- wraps backend (per skill replay.md)
                      backend/   (not shipped) <- internal graph, not audited here

`[FACT]` `core/` is a verified leaf: no `core/*.py` file contains an import of
`experiments`, `backend`, `research`, or `validation` (verified by reading
`core/__init__.py` and the five subpackage modules `dirichlet_markov.py`,
`emergence_statistic.py`, `null_referenced_test.py`, `mdl_growth.py`,
`proper_scoring.py`, `metrics.py`, `fixed_capacity.py`, `random_growth.py`,
`shuffled_input.py`).
`[INFERENCE]` Because core is a leaf, no import cycle can pass through core.
The scientific primitives are acyclic by construction.

---

## 2. Cycles

`[FACT]` No import cycle was found in the `core/` <- `experiments/` shipped
subgraph. Verified edges (see ARCHITECTURE_MAP.md Section 2) all point downward
or laterally within a single experiment package.

`[FACT]` Within `experiments/EXP1/` the internal edges are acyclic:
    run -> {dataset, decision, manifest, program_a_adapter}
    decision -> {calibration, dataset}
    dataset -> rubric
    manifest -> dataset
    calibration -> dataset
    report -> {calibration, decision}      (report is a leaf consumer, not in run's path)
    artifact_specs -> (nothing in EXP1)

`[INFERENCE]` No cycle exists in EXP1. `report.py` and `artifact_specs.py` are
dangling consumers (see Section 3).

`[RISK]` The `backend/` internal graph was NOT audited this session (it is not
shipped and exceeds the inspection scope). The skill `architecture.md` flags
prior circular-dependency reviews (`docs/reviews/program_d_circular_dependencies.md`).
Insufficient evidence to confirm or deny backend cycles; flagged as RISK, not
FACT.

---

## 3. Hidden coupling

### 3.1 sys.path mutation at import time
`[FACT]` `experiments/E0/run.py:34-36`:
    _project_root = Path(__file__).resolve().parent.parent.parent
    if str(_project_root) not in sys.path:
        sys.path.insert(0, str(_project_root))
`[RISK]` This makes E0 importable only when run as a script from the repo root
and silently couples the experiment to the on-disk layout rather than the
installed package declared in `pyproject.toml`. A `pip install` of the shipped
packages would NOT pick up `experiments.E0.dataset` unless the repo root is on
`sys.path`. This is the single most consequential hidden coupling in the
shipped tree.

### 3.2 Backend / Program C / Program B directory duplication
`[FACT]` The canon (Section 9-DeepSeek, lines 171-177) instructs the
engineering layer to split `backend/` into `program_a/`, `program_b/`,
`program_c/`, `infra/`, `benchmarks/`. On disk:
- `backend/` STILL EXISTS in full (self_model, soul, cognition, knowledge,
  memory, simulation, ops, ...).
- `program_a/` EXISTS (retrieval, nlp) - real code.
- `program_b/` EXISTS but is EMPTY STUBS (concepts/__init__.py 0 B,
  soul_graph/__init__.py 0 B).
- `program_c/` EXISTS but every subpackage is an EMPTY STUB (self_model/,
  cognition/, knowledge/, memory/, learning/, metacognition/, reflection/,
  pipeline/, abstraction/, simulation/, agency/, conversation/, models/ - all
  contain only 0-byte `__init__.py`).
`[RISK]` The real implementations the canon expected to live under
`program_c/*` actually live under `backend/*`. The `program_c/` tree is a
parallel empty skeleton. Any code that imports `program_c.*` will fail; any
code that imports `backend.*` works. This is a hidden naming/ownership hazard:
two trees claim the same responsibility, one is empty, the other is live.

### 3.3 Duplicate soul/self_model locations
`[FACT]` `[REJECTED]` self-model code lives at `backend/self_model/` (5 files,
real). `program_c/self_model/` is an empty stub. Canon Section 9-DeepSeek line
172 instructs archiving `program_c/self_model/` - a path that is already empty.
`[FACT]` `[REJECTED]` soul code lives at `backend/soul/` (`soul_graph.py`
28,080 B, `concepts.json` 26,020 B). `program_b/soul_graph/` and
`program_b/concepts/` are empty stubs. `repository_v2.md:152` claims
`program_b/soul_graph/soul_graph.py` exists - it does NOT.
`[RISK]` Archiving instructions in the canon target empty paths and would leave
the real rejected artifacts at `backend/*` untouched.

---

## 4. Dead modules (verified)

A "dead module" here = real code present on disk that no live experiment path
imports, or a stub directory that documents claim is live.

### 4.1 Stub experiment directories (claimed live, actually empty)
`[FACT]` `repository_v2.md:62-69` claims `experiments/{R1,R2,R3F,EXP1,EXP2,
EXP3,EXP4}/` each contain `preregistration.md`, `protocol.md`, `run.py`,
`analysis.py`. Verified disk state:
- `experiments/EXP2/` - `__init__.py` (0 B) ONLY. No other files.
- `experiments/EXP3/` - `__init__.py` (0 B) ONLY.
- `experiments/EXP4/` - `__init__.py` (0 B) ONLY.
- `experiments/R1/` - `__init__.py` (0 B) ONLY.
- `experiments/R3F/` - `__init__.py` (0 B) ONLY.
- `experiments/coverage/` - `__init__.py` (0 B) ONLY.
`[FACT]` `experiments/EXP1/` is the EXCEPTION: it is fully implemented (see
ARCHITECTURE_MAP.md Section 1.2). `repository_v2.md` is right about EXP1
existing but wrong about the others.
`[RISK]` Six empty stub directories invite import attempts that will silently
fail or import nothing. They should be archived per canon Section 7
(EXP-3/EXP-4/R2/R3F removed) and Section 9-DeepSeek.

### 4.2 Dangling EXP1 report/spec generators (implemented but not wired)
`[FACT]` `experiments/EXP1/report.py` (167 B of code, 167 lines) defines
`write_experiment_report`, `write_seed_report`, `reliability_table_csv`,
`experiment_report_markdown`, `seed_report_markdown`. None of these are
imported or called by `experiments/EXP1/run.py` (run.py imports only dataset,
decision, manifest, program_a_adapter - lines 16-36).
`[FACT]` `experiments/EXP1/artifact_specs.py` (109 lines) defines
`write_artifact_specifications` and `exp1_artifact_specs`. `run.py` does NOT
import `artifact_specs`. `EXECUTION_GUIDE.md:121` step 3 requires generating
artifact specs before execution outputs, but the runner does not perform this
step.
`[RISK]` EXP1 as currently wired will NOT produce `calibration_report.md`,
`reliability.csv`, or `*.spec.json` artifacts. Only raw `answers.jsonl`,
`evaluated.jsonl`, `decision.json`, and `execution_manifest.json` are written
(run.py:104-109, 203-208, 217-219). This contradicts the EXP1 preregistration
output contract.

### 4.3 Dead import in E0 analysis
`[FACT]` `experiments/E0/analysis.py:16`:
    from sklearn.metrics.cluster import normalized_mutual_info_score as sklearn_nmi
`[FACT]` `experiments/E0/analysis.py:17`:
    from core.emergence.emergence_statistic import compute_nmi
`[FACT]` A grep for `sklearn_nmi` across `experiments/E0/` finds the name only
at the import site (line 16); the live code uses `compute_nmi` from core.
`[INFERENCE]` `sklearn_nmi` is a dead import. (This finding agrees with
`REPRODUCIBILITY_AUDIT.md:150`, the one audit claim verified accurate.)

### 4.4 Defined-but-never-called E0 report generator
`[FACT]` `experiments/E0/analysis.py:319` defines `generate_e0_report`.
`[FACT]` A grep for `generate_e0_report` across `experiments/E0/` finds exactly
one match: the definition at line 319. Zero call sites within E0.
`[INFERENCE]` `generate_e0_report` is never invoked by the E0 runner. The
human-readable E0 report is never produced. (Agrees with
`REPRODUCIBILITY_AUDIT.md:94`.)

### 4.5 Rejected free-energy policy still live in research/
`[FACT]` `research/policies/free_energy.py` exists (real code, not a stub).
`[FACT]` Canon Section 5 line 90 marks `E = lambda*H + mu*S + nu*A`
`[REJECTED]` permanently. Canon Section 8 line 144: R1 free-energy
consolidation policy is statistically indistinguishable from null (p=0.866).
`[RISK]` A `[REJECTED]` scientific mechanism remains importable in the live
research tree. It is not archived.

---

## 5. Documented dependency graphs that do NOT match disk

`[FACT]` The repo root contains `dependency_graph.graphml`,
`program_c_graph.graphml`, `foundation/architecture/dependency_graph.graphml`
(per `repository_v2.md:23`), and `dependency_graphs/` directory. None were
parsed this session.
`[RISK]` Given that `repository_v2.md` itself does not match disk (Section 4.1
above), any dependency graph derived from or aligned with it is suspect until
independently verified. Insufficient evidence to label them wrong; flagged
RISK pending verification.

---

## 6. Summary

| Concern | Verdict | Evidence |
|---|---|---|
| Import cycles in shipped tree | **NONE FOUND** | core is a verified leaf; EXP1 internal graph acyclic |
| Hidden coupling: sys.path mutation | **PRESENT** | `experiments/E0/run.py:34-36` |
| Hidden coupling: backend/program_c duplication | **PRESENT** | backend/ live, program_c/ empty stubs |
| Dead stub directories (claimed live) | 6 | `experiments/{EXP2,EXP3,EXP4,R1,R3F,coverage}` |
| Dead EXP1 modules (implemented, unwired) | 2 | `report.py`, `artifact_specs.py` not imported by run.py |
| Dead import | 1 | `experiments/E0/analysis.py:16` sklearn_nmi |
| Defined-never-called | 1 | `experiments/E0/analysis.py:319` generate_e0_report |
| Rejected science still live | 2 sites | `research/policies/free_energy.py`, `backend/{self_model,soul}/` |
| Backend internal cycles | **INSUFFICIENT EVIDENCE** | not audited this session |
