# VELYNX TECHNICAL DEBT

**Authority:** Chief Systems Architect inspection, 2026-07-07.
**Method:** Every item verified against the actual file on disk this session.
File:line citations point to evidence observed directly. No item is taken from
a prior audit document without independent re-verification; where a prior audit
was consulted, its accuracy is separately assessed (see TD-09, TD-10).
**Epistemic tags:** `[FACT]`, `[INFERENCE]`, `[RISK]`.
**Severity:** CRITICAL (canonical/science violation) > HIGH (blocks an
experiment or breaks a contract) > MEDIUM (drift, dead code, maintainability) >
LOW (cosmetic, documentation proliferation).

---

## CRITICAL

### TD-01 ? H3 listed as a LIVE hypothesis with an expected positive result
- **Evidence:** `HYPOTHESIS_REGISTER.md:73-89` lists "H3 (Emergent Development)"
  as a normal hypothesis with
  "Expected positive result: Significant transfer of learned structure to a
  held-out prediction task." (line 88). No `[REJECTED]` marker appears anywhere
  in the file.
- **Canonical conflict:** `PROGRAM_D_CANONICAL.md:123-124` (Section 6):
  "H3 - [REJECTED] (subsumed) ... It must not be re-listed as a live surviving
  hypothesis." `PROGRAM_D_CANONICAL.md:193` (Section 10 Issue-1):
  "H3 [REJECTED]/subsumed by H*. Canonical hypotheses are H*, H1, H2.
  Experiments EXP-3/EXP-4 removed."
- **Status:** `HYPOTHESIS_REGISTER.md` is in the canon's supersede list
  (`PROGRAM_D_CANONICAL.md:13`). It is a proposal until reconciled; it has not
  been reconciled.
- **Impact:** A rejected hypothesis is presented as live with an expected
  positive result. Direct canonical defect.
- **Tag:** `[FACT]`

### TD-02 ? EXPERIMENT_INTERFACE_SPEC exposes MDL constants as configurable
- **Evidence:** `EXPERIMENT_INTERFACE_SPEC.md:14-19`:
  ```
  "scientific_parameters": {
    "mdl_b_constant": 1.5,
    "mdl_n_multiplier": 1.0,
    "capacity_growth_enabled": true
  }
  ```
- **Canonical conflict:** `PROGRAM_D_CANONICAL.md:83` (Section 5.4):
  "lambda_model = k*b + n*log2(N) ... The trigger must not be hand-set - a
  hand-set threshold violates I2 by construction (failure mode F2). This is the
  one load-bearing derivation."
  `PROGRAM_D_CANONICAL.md:205-207` (Section 10 Issue-3): pin
  `lambda_model = k*b + n*log2(N)`; "A bare/hand-set lambda is exactly failure
  mode F2."
- **Counter-evidence (code is CORRECT):** `core/mdl/mdl_growth.py:28`
  `BITS_PER_PARAMETER = 1.0` (scientific constant). `:85` `compute_lambda_model`
  returns `k * b + n * math.log2(N)` (derived). `parameter_registry.yaml:55-62`
  marks `mdl.lambda_model` "NOT configurable" and `b` "scientific constant, not
  tunable".
- **Status:** The interface spec is the SOLE stale artifact on this point.
  The value `1.5` for `mdl_b_constant` is also wrong (must be `1.0`). The spec
  also exposes `mdl_n_multiplier` as a tunable, which the canon forbids.
- **Impact:** Any reader/implementer following the interface spec would
  reintroduce failure mode F2 and violate keystone I2. The spec contradicts
  both the canon and the actual code.
- **Tag:** `[FACT]`

### TD-03 ? repository_v2.md describes a structure that does not exist
- **Evidence:**
  - `repository_v2.md:62-69` claims `experiments/{R1,R2,R3F,EXP1,EXP2,EXP3,
    EXP4}/` each contain `preregistration.md`, `protocol.md`, `run.py`,
    `analysis.py`. Verified: `experiments/{EXP2,EXP3,EXP4,R1,R3F,coverage}/`
    each contain ONLY a 0-byte `__init__.py`. No other files.
  - `repository_v2.md:152` claims `program_b/soul_graph/soul_graph.py` and
    `soul_store.py` exist. Verified: `program_b/soul_graph/` contains only a
    0-byte `__init__.py`.
  - `repository_v2.md:178` claims `program_c/self_model/` contains
    `self_model.py`, `identity_store.py`, `health_monitor.py`,
    `baseline_tracker.py`, `self_audit.py`. Verified:
    `program_c/self_model/` contains only a 0-byte `__init__.py`. The real
    files live in `backend/self_model/`.
  - `repository_v2.md:170-182` lists 13 `program_c/` subpackages each with many
    named `.py` files. Verified: EVERY `program_c/*` subpackage contains only a
    0-byte `__init__.py`.
- **Canonical conflict:** `PROGRAM_D_CANONICAL.md:130` (Section 7):
  "EXP-3, EXP-4, R2, R3F are not part of the redesigned program; R1 is closed
  evidence, not a live experiment." `repository_v2.md` lists them as live.
- **Impact:** The canonical engineering-layer roadmap document is fiction for
  ~80% of the paths it names. Any plan, import, or reference derived from it is
  built on non-existent files.
- **Tag:** `[FACT]`

### TD-04 ? REPRODUCIBILITY_AUDIT.md makes false existence claims
- **Evidence (false claims verified against disk):**
  - `REPRODUCIBILITY_AUDIT.md:201` "TRACEABILITY_MATRIX.md ... This file is not
    in the repository." -> FALSE. `TRACEABILITY_MATRIX.md` exists, 12,294 bytes,
    real content.
  - `REPRODUCIBILITY_AUDIT.md:205` "IMPLEMENTATION_GAPS.md ... This file is not
    in the repository." -> FALSE. `IMPLEMENTATION_GAPS.md` exists, 16,226
    bytes, real content.
  - `REPRODUCIBILITY_AUDIT.md:228` "paraphrases.json dataset ... Not in
    repository" -> FALSE. `experiments/EXP0/paraphrases.json` exists, 18,803
    bytes.
  - `REPRODUCIBILITY_AUDIT.md:27` "EXP-1, EXP-2: Not implemented." -> FALSE for
    EXP-1. `experiments/EXP1/` has a full implementation: `run.py` (10,962 B),
    `decision.py` (10,794 B), `dataset.py` (14,813 B), `calibration.py`,
    `rubric.py`, `report.py`, `manifest.py`, `artifact_specs.py`,
    `program_a_adapter.py`, `config.json`.
- **Additional stale claim:** `REPRODUCIBILITY_AUDIT.md:59,221` asserts
  `run.py:107` uses Python `hash()`. Verified FALSE:
  `experiments/E0/run.py:107` is `digest = hashlib.sha256(seed_bytes).hexdigest()`
  followed by `return self.master_seed + int(digest[:8], 16) % (2**31)`. The
  recommended fix was already applied; the audit is stale.
- **Impact:** The audit document is unreliable as a reference. Its
  recommendations (Section 9) are a mix of already-applied, already-existed, and
  possibly-still-valid items that cannot be distinguished without re-verification.
- **Tag:** `[FACT]`

---

## HIGH

### TD-05 ? EXP1 runner does not produce its preregistered report artifacts
- **Evidence:** `experiments/EXP1/run.py:16-36` imports only `dataset`,
  `decision`, `manifest`, `program_a_adapter`. It does NOT import `report.py`
  or `artifact_specs.py`. The runner writes only `answers.jsonl`,
  `evaluated.jsonl`, `decision.json`, `execution_manifest.json`
  (`run.py:104-109`, `203-208`, `217-219`).
- **Contract conflict:** `EXECUTION_GUIDE.md:64-76` specifies generated outputs
  `reliability.csv`, `calibration_report.md`, `experiment_summary.json` and
  their `.spec.json` schemas. `EXECUTION_GUIDE.md:121` step 3 requires
  generating artifact specs "before execution outputs are written."
- **Implementation that exists but is unwired:**
  - `experiments/EXP1/report.py:114-138` defines `write_seed_report` and
    `write_experiment_report` (never called by run.py).
  - `experiments/EXP1/artifact_specs.py:96-109` defines
    `write_artifact_specifications` (never called by run.py).
- **Impact:** A complete EXP1 run as currently wired will NOT emit the
  preregistered human-readable report, reliability CSV, or experiment summary.
  This breaks the `EXP1_PREREGISTRATION.md` output contract.
- **Tag:** `[FACT]`

### TD-06 ? EXP1 trace has three missing concrete links
- **Evidence:**
  - Missing frozen dataset: `experiments/EXP1/config.json:11` points to
    `data/exp1_queries.json`. `Test-Path data/exp1_queries.json` -> False.
    `EXECUTION_GUIDE.md:128` confirms: "The actual frozen dataset file
    data/exp1_queries.json is not present in this workspace."
  - Missing concrete Program A adapter: `experiments/EXP1/program_a_adapter.py`
    defines only the `ProgramAAdapter` Protocol (line 18) and a generic
    `CallableProgramAAdapter` wrapper (line 30). No module wires the actual
    `program_a/retrieval/` system to EXP1. `run.py:54,118` requires the caller
    to inject `answer_fn` or `adapter`.
  - Missing concrete adjudicator: `run.py:40,63-64,128-129` requires an
    `adjudicator_fn` to be injected. No module in the repo implements rubric-based
    answer correctness scoring. `EXECUTION_GUIDE.md:130` confirms: "A
    frozen-rubric adjudicator is not wired to the EXP-1 runner."
- **Impact:** EXP1 cannot execute end-to-end as-is. The orchestration, ECE
  math, decision rules, and manifest are complete; the three injected
  dependencies are absent.
- **Tag:** `[FACT]` (dataset, adapter, adjudicator absence);
  `[INFERENCE]` (EXP1 cannot execute end-to-end)

### TD-07 ? E0 mutates sys.path at import time
- **Evidence:** `experiments/E0/run.py:34-36`:
  ```
  _project_root = Path(__file__).resolve().parent.parent.parent
  if str(_project_root) not in sys.path:
      sys.path.insert(0, str(_project_root))
  ```
- **Impact:** E0 is importable only when run as a script from the repo root.
  A `pip install` of the shipped packages (per `pyproject.toml:20-28`) would
  not satisfy `from experiments.E0.dataset import ...` without the repo root on
  `sys.path`. Hidden coupling to filesystem layout; packaging smell.
- **Tag:** `[FACT]`

### TD-08 ? Rejected science persists as live engineering code
- **Evidence:**
  - `backend/self_model/` contains `self_model.py`, `identity_store.py`,
    `health_monitor.py`, `baseline_tracker.py`, `self_audit.py` (real code).
    Canon `PROGRAM_D_CANONICAL.md:90` (Section 5) [REJECTED] list includes
    "the self-model."
  - `backend/soul/soul_graph.py` (28,080 B) and `backend/soul/concepts.json`
    (26,020 B) (real code). Canon `PROGRAM_D_CANONICAL.md:90` [REJECTED] list
    includes "the 32 soul concepts", "the hand-authored ontology."
  - `research/policies/free_energy.py` (real code). Canon
    `PROGRAM_D_CANONICAL.md:90` [REJECTED] list includes
    `E = lambda*H + mu*S + nu*A`. Canon `PROGRAM_D_CANONICAL.md:144` (Section
    8): R1 free-energy statistically indistinguishable from null (p=0.866).
- **Canon nuance:** Canon Section 2 line 42 permits rejected science to remain
  as engineering for the Program A product. The skill `velynx-core` records this
  duality explicitly. So the presence is not automatically a violation.
- **Risk:** The rejected mechanisms remain importable and could be silently
  pulled into a live experiment path. No CI guard was verified that prevents
  `experiments/` or `core/` from importing `backend.self_model`,
  `backend.soul`, or `research.policies.free_energy`.
- **Tag:** `[FACT]` (presence), `[RISK]` (no verified guard)

---

## MEDIUM

### TD-09 ? IMPLEMENTATION_GAPS.md contains two stale BLOCKER entries
- **Note:** `IMPLEMENTATION_GAPS.md` itself was falsely claimed absent by
  `REPRODUCIBILITY_AUDIT.md:205` (see TD-04). It exists and is largely
  accurate, but two of its Tier-0 BLOCKERS are stale:
- **G-01 stale:** `IMPLEMENTATION_GAPS.md:11-16` (G-01) claims
  `experiments/E0/run.py:39,46,53` calls
  `collector.compute_free_energy(entropy=..., surprise=..., structural_load=...)`.
  Verified: a grep for `free_energy|compute_free_energy` across
  `experiments/E0/` returns NO files found. Line 39 is
  `from core.mdl.mdl_growth import should_grow`. The free-energy code has been
  purged from E0. G-01 is RESOLVED, not a current blocker.
- **G-02 stale:** `IMPLEMENTATION_GAPS.md:18-23` (G-02) claims
  `core/mdl/mdl_growth.py` uses `model_cost = model_params*log(n)/2` (BIC) and
  `mdl_gain(..., lambda_model=1.0)` (hand-set default), and
  `parameter_registry.yaml` lists `mdl.lambda_model: configurable`. Verified:
  `core/mdl/mdl_growth.py:85` implements `k*b + n*log2(N)` (canonical);
  `parameter_registry.yaml:55-62` marks lambda_model "NOT configurable".
  G-02 is RESOLVED.
- **Impact:** IMPLEMENTATION_GAPS.md overstates the current blocker count.
  Its remaining entries (G-03 EXP-0 path, G-04 state-reset, G-05 H3/EXP-3/4
  liveness) were not all re-verified this session but G-05 aligns with TD-01.
- **Tag:** `[FACT]`

### TD-10 ? EXECUTION_GUIDE_AUDIT.md cites stale blocker state
- **Evidence:** `EXECUTION_GUIDE_AUDIT.md:24-30` (item 6) treats
  `EXECUTION_GUIDE.md:128-131` blockers as accurate. `EXECUTION_GUIDE.md:129`
  says "Program A answer adapter is not wired to the EXP-1 runner." Verified:
  the adapter CONTRACT exists (`experiments/EXP1/program_a_adapter.py`, 76
  lines, with `ProgramAAdapter` Protocol + `CallableProgramAAdapter`). The
  runner imports and uses it (`run.py:32-36,66-70,130-134`). What is MISSING is
  a CONCRETE adapter instance wiring `program_a/retrieval/` (see TD-06).
  `EXECUTION_GUIDE.md:130` says "A frozen-rubric adjudicator is not wired."
  Verified TRUE: `rubric.py` validates rubrics but does not adjudicate answers
  (it explicitly states at `rubric.py:3-4` "It does not adjudicate answers and
  does not infer correctness"). No adjudicator module exists.
- **Impact:** The audit's framing ("adapter not wired") is imprecise: the
  adapter framework IS wired; only the concrete Program A binding is missing.
- **Tag:** `[FACT]`

### TD-11 ? TRACEABILITY_MATRIX.md references non-existent EXP1 modules
- **Evidence:** `TRACEABILITY_MATRIX.md:33` listed the EXP1 implementation as
  `experiments/EXP-1/{dataset,run,analysis,control_bm25,goodhart_guard,decision}.py`
  and the ECE primitive as `core/measurement/metrics.py`. Verified 2026-07-07
  against actual `experiments/EXP1/` contents. Decomposed into four distinct
  categories (not a single item):
  1. `analysis.py` -- **STALE-REF**: functionality lives in `calibration.py`
     (ECE) + `decision.py` (kill criteria) + `report.py` (rendering).
  2. `control_bm25.py` -- **DEFERRED-BACKLOG**: EXP1-04 BM25/TF-IDF control
     (`PROGRAM_D_MASTER_ROADMAP.md:132`, `IMPLEMENTATION_BACKLOG.md:80`); not
     preregistered in `EXP1_PREREGISTRATION.md` Section 4. Tracked in
     `IMPLEMENTATION_GAPS.md:126`.
  3. `goodhart_guard.py` -- **DEFERRED-BACKLOG + RECORDED DISSENT**: EXP1-05
     active detector. Canonical guard (`PROGRAM_D_CANONICAL.md:110`)
     implemented passively (locked equal-width bins, `calibration.py:20`) +
     `protocol_violation` kill flag (`decision.py:210`);
     `EXP1_PREREGISTRATION.md:74,166` certifies this as the guard.
     `STATISTICAL_AUDIT.md:188` dissents (active detector required, "not
     implemented"). Unresolved.
  4. `core/measurement/metrics.py` (ECE) -- **STALE-REF**: canonical ECE
     primitive is `core/measurement/proper_scoring.py:42`
     (`expected_calibration_error`); EXP-1 wrapper is
     `experiments/EXP1/calibration.py:102`.
- **Impact:** Matrix cell corrected at source (TRACEABILITY_MATRIX.md:33).
  EXP1_TRACE.md verdict supplemented with items ML-12..ML-15 + Goodhart-guard
  qualification (see `EXP1_TRACE.md` Verdict). The `goodhart_guard.py`
  categorization is PROVISIONAL pending ScientificAuditor ratification.
- **Cross-ref:** `EXP1_TRACE.md` Verdict (items 5-7, ML-12..ML-15).
- **Tag:** `[FACT]` (items 1, 4); `[FACT]` + recorded dissent (item 3); roadmap (item 2).

### TD-12 ? Dead import and defined-never-called in E0
- **Evidence:**
  - `experiments/E0/analysis.py:16` imports
    `from sklearn.metrics.cluster import normalized_mutual_info_score as sklearn_nmi`.
    Grep finds `sklearn_nmi` only at the import site; live code uses
    `compute_nmi` from `core.emergence.emergence_statistic` (line 17). Dead import.
  - `experiments/E0/analysis.py:319` defines `generate_e0_report`. Grep finds
    zero call sites in `experiments/E0/`. The human-readable E0 report is never
    produced.
- **Tag:** `[FACT]`

### TD-13 ? program_c/ parallel empty skeleton
- **Evidence:** `program_c/` has 13 subpackages (cognition, knowledge, memory,
  learning, metacognition, reflection, pipeline, abstraction, self_model,
  simulation, agency, conversation, models). Every one contains only a 0-byte
  `__init__.py`. The real implementations live in `backend/`.
- **Risk:** Two trees claim the same responsibility; imports targeting
  `program_c.*` will fail silently. Canon Section 9-DeepSeek disposition
  instructions reference `program_c/self_model/` (an empty path) and miss
  `backend/self_model/` (the real code).
- **Tag:** `[FACT]`

---

## LOW

### TD-14 ? Duplicate configuration directories
- **Evidence:** `configs/` and `infra/config/` both exist.
  `repository_v2.md:279` acknowledges the intended consolidation
  ("configs/ -> infra/config/") but both are still present.
- **Tag:** `[FACT]`

### TD-15 ? SQLite database files at repo root
- **Evidence:** `velynx_identity.db`, `velynx_state.db`, `concept_birth.db`
  plus `-shm`/`-wal` sidecars exist at repo root.
- **Risk:** Accidental commit of binary DB state.
  `.gitignore` handling not verified this session.
- **Tag:** `[FACT]` (presence), `[RISK]` (commit hazard)

### TD-16 ? Root documentation proliferation
- **Evidence:** 188 entries at repo root including ~70 standalone `.md`
  documents and ~20 standalone `test_*.py` / `*_benchmark*.py` scripts outside
  the `tests/` and `benchmarks/` packages.
- **Risk:** Discovery cost; unclear authority among overlapping docs (e.g.
  `PROGRAM_D_SPECIFICATION.md`, `PROGRAM_D_CANONICAL.md`,
  `PROGRAM_D_CONSTITUTION.md`, `PROGRAM_D_MASTER_ROADMAP.md`,
  `SCIENTIFIC_EXECUTION_SPEC.md`, `EXPERIMENT_PROTOCOLS.md`,
  `EXPERIMENT_CONFIGURATION_SCHEMA.md`, `EXPERIMENT_INTERFACE_SPEC.md`).
  Canon `PROGRAM_D_CANONICAL.md:13` declares most of these superseded
  proposals, but they remain in the live tree.
- **Tag:** `[FACT]`

---

## Summary table

| ID | Severity | One-line | Primary citation |
|---|---|---|---|
| TD-01 | CRITICAL | H3 still live with expected positive result | HYPOTHESIS_REGISTER.md:73-89 |
| TD-02 | CRITICAL | MDL constants exposed as configurable; value wrong | EXPERIMENT_INTERFACE_SPEC.md:14-19 |
| TD-03 | CRITICAL | repository_v2.md describes non-existent files/dirs | repository_v2.md:62-69,152,170-182 |
| TD-04 | CRITICAL | REPRODUCIBILITY_AUDIT.md false existence claims | REPRODUCIBILITY_AUDIT.md:201,205,228,27,59 |
| TD-05 | HIGH | EXP1 runner omits report/artifact-spec generation | experiments/EXP1/run.py:16-36 |
| TD-06 | HIGH | EXP1 missing dataset, concrete adapter, adjudicator | EXECUTION_GUIDE.md:128-130 |
| TD-07 | HIGH | E0 mutates sys.path at import time | experiments/E0/run.py:34-36 |
| TD-08 | HIGH | Rejected science persists as live code (no guard) | backend/self_model/, backend/soul/, research/policies/free_energy.py |
| TD-09 | MEDIUM | IMPLEMENTATION_GAPS.md G-01/G-02 stale (already fixed) | IMPLEMENTATION_GAPS.md:11-23 |
| TD-10 | MEDIUM | EXECUTION_GUIDE_AUDIT.md imprecise about adapter wiring | EXECUTION_GUIDE_AUDIT.md:24-30 |
| TD-11 | MEDIUM | TRACEABILITY_MATRIX.md:33 stale-refs decomposed (analysis.py STALE-REF; control_bm25.py DEFERRED; goodhart_guard.py DEFERRED+DISSENT; metrics.py->proper_scoring.py STALE-REF) | TRACEABILITY_MATRIX.md:33; EXP1_TRACE.md ML-12..15 |
| TD-12 | MEDIUM | E0 dead import + defined-never-called report | experiments/E0/analysis.py:16,319 |
| TD-13 | MEDIUM | program_c/ parallel empty skeleton | program_c/* (all 0-byte __init__.py) |
| TD-14 | LOW | Duplicate config dirs | configs/, infra/config/ |
| TD-15 | LOW | SQLite DB files at repo root | velynx_*.db at root |
| TD-16 | LOW | Root documentation proliferation | ~70 .md files at root |
