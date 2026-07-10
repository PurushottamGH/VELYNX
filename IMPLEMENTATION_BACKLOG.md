# PROGRAM D — IMPLEMENTATION BACKLOG

**Authority:** Derives from `PROGRAM_D_CANONICAL.md` via `PROGRAM_D_MASTER_ROADMAP.md`. Every task maps to a canonical hypothesis/experiment; a task with no such mapping is out of scope (canonical §1 rule 2).
**Format:** GitHub-Projects-ready. Columns: **ID · Description · Maps-to · Deps · Difficulty · Est(h) · Files · Acceptance test · Definition of Done**.
**Difficulty scale:** Trivial / Easy / Medium / Hard / Very-Hard. **Est** in hours, single engineer.
**Global DoD (applies to every task):** change is committed on a green `pytest -m "not slow"`; no live reference to a [REJECTED] object is introduced; provenance (commit+config hash) preserved where the task touches an experiment path.

---

## Milestone M0 — Canonical Reconciliation (docs/registries only; no science)

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| **[DONE]** RC-01 | Strike H3 as a live hypothesis; mark `[REJECTED]/subsumed by H*`; ensure H* present | H\* | — | Easy | 1 | `HYPOTHESIS_REGISTER.md` | `grep -n "H3" HYPOTHESIS_REGISTER.md` shows only `[REJECTED]` cross-refs; H* block present | Register lists H\*,H1,H2 live; H3 archival only |
| **[DONE]** RC-02 | Remove EXP-3 protocol; note "subsumed by E0" | H\* | RC-01 | Easy | 0.5 | `EXPERIMENT_PROTOCOLS.md` | no live EXP-3 section; E0 present | Protocols list EXP-0/1/2/E0 only |
| **[DONE]** RC-03 | Rewrite SPEC §3-H2 to task-score/unframed form; retire 0.15 ECE dead-zone (single gate <0.10) | H2, H1 | — | Medium | 2 | `PROGRAM_D_SPECIFICATION.md` | `grep -niE "dimensionality reduction|search steps|dense.embedding|0\.15"` → 0 live hits | SPEC H2 = affective→task-score, unframed control; H1 gate single `<0.10` |
| **[DONE]** RC-04 | `repository_v2.md`: delete EXP3/EXP4 rows; `self_model`→archive; drop soul_graph+concepts.json from EXP-2 deps | H2, H\* | — | Medium | 2 | `repository_v2.md` | no EXP3/EXP4 experiment rows; EXP-2 dependents exclude program_b | Engineering doc has no rejected experiments/deps |
| **[DONE]** RC-05 | `migration_plan.md`+`implementation_checklist_v1.md`: drop EXP3/EXP4, self_model, infra/app/soul from skeleton; add anthropomorphic-rename step; de-dup to one skeleton/remap/archive list | H\*, H2 | RC-04 | Medium | 3 | `migration_plan.md`, `implementation_checklist_v1.md` | Phase-0 skeleton has no `EXP3/EXP4/self_model/soul`; one remap table only | Three engineering docs agree on one skeleton |
| **[DONE]** RC-06 | `experiment_registry.yaml`: delete EXP3/EXP4; set R2/R3F=archived (not live) | H\* | RC-04 | Easy | 1 | `experiment_registry.yaml` | YAML has E0/EXP1/EXP2 live + EXP-0; no EXP3/EXP4 live | Registry = live set only |
| **[DONE]** RC-07 | `parameter_registry.yaml`: mark free-energy λ/μ/ν, ENERGY_EXHAUSTION, STRATEGY_FREE_ENERGY `[REJECTED] archive-only`; pin `mdl.lambda_model=k·b+n·log₂N` (remove "configurable") | H\* | — | Easy | 1 | `parameter_registry.yaml` | `grep -n "configurable" parameter_registry.yaml` → 0 for lambda_model; free_energy block tagged REJECTED | Registry carries no live rejected params; λ pinned |
| **[DONE]** RC-08 | Author Program-D coverage matrix over EXP-0/1/2/E0 (replace legacy E1–E13) | all exp | RC-06 | Medium | 2 | `experiments/coverage/experiment_coverage_matrix.csv` | every row ∈ {EXP-0,EXP-1,EXP-2,E0}; no `E1..E13`/`self_coder`/`free_energy_vs_pareto` rows | Matrix maps live experiments→component→hypothesis→metric→kill |

---

## Milestone M1 — Compliant 5-Primitive Core + Skeleton

### Epic M1-E1 — Canon-exact core

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| CORE-01 | Growable Dirichlet–Markov predictor `{P_θ:θ∈Θ_k}` indexed by capacity k; drop "belief model" label | H\* | RC-05 | Hard | 6 | `core/predictors/dirichlet_markov.py`, `core/predictors/base.py` | `predict/update/entropy/grow` unit tests pass; capacity k increments; no symbol `belief` | Predictor conforms to §5.2; imported by E0 |
| CORE-02 | Log score `L=−log P_θ` as sole loss; delete any `E=λH+μS+νA` path | H\*, H1 | — | Medium | 3 | `core/measurement/proper_scoring.py` | log-loss matches reference to 1e-9; `grep -RniE "free_energy|λH|E *= *λ"` in core → 0 | Only proper scoring rule present (§5.3) |
| CORE-03 | MDL trigger `G=H_before−H_after−λ_model`, **λ_model=k·b+n·log₂N**, ledger-wired not hand-set | H\* | CORE-01 | Hard | 5 | `core/mdl/mdl_growth.py`, `core/mdl/concept_birth_ledger.py` | test: for sampled (k,b,n,N), `λ_model==k*b+n*log2(N)`; assert not read from any JSON/config | Growth trigger is a derivation (§5.4); F2 avoided |
| CORE-04 | Null-referenced `M=NMI(learned,true)−NMI(learned,shuffled)`, `E[M|H₀]=0`; delete graph-isomorphism form | H\* | — | Hard | 5 | `core/emergence/emergence_statistic.py`, `core/emergence/null_referenced_test.py` | test: `E[M|H₀]≈0` (±tol) on shuffled input; no graph-isomorphism symbol | `M` per §5.5; F3 avoided |
| CORE-05 | Controls C1 fixed-capacity, C2 random-growth, C3 shuffled-input as importable classes | H\* | CORE-01 | Medium | 3 | `core/controls/{fixed_capacity,random_growth,shuffled_input}.py` | each control instantiable + reproducible under seed | C1/C2/C3 ready for E0 (§7) |
| CORE-TEST | Core canon-exactness test suite (λ, M, log-loss, no-rejected-symbol) | H\* | CORE-01..05 | Medium | 3 | `tests/unit/test_core_canonical.py` | suite asserts all four canon properties; CI grep-gate for banned symbols | Green suite gates M1 |

### Epic M1-E2 — Archive rejected & anthropomorphic

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| CORE-06 | Archive `self_model/`, `reasoning_engine` type-lifting, `ontology_loader`, free-energy/R1 (closed evidence) with zero live imports | §1 r5 | CORE-TEST | Medium | 4 | `program_c/self_model/*`, `program_c/knowledge/ontology_loader.py`, `program_c/cognition/reasoning_engine.py` → `archive/` | `grep -RIl "self_model\|ontology_loader" --include=*.py` under live tree → 0 (shims excepted) | Rejected mechanisms out of live tree |
| CORE-07 | Anthropomorphic-name rename/retire: `soul,belief,curiosity,dream_state,monologue` | §1 r5 | CORE-06 | Medium | 4 | rename map across `program_c/*`, `program_b/*` | `grep -RniE "\b(soul|belief|curiosity|dream_state|monologue)\b" --include=*.py` under live → 0 | No anthropomorphic live names |

### Epic M1-E3 — Repo v2 skeleton (dual-import shim)

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| INFRA-01 | Create v2 directory skeleton + `__init__.py` (no EXP3/EXP4/self_model/soul) | infra | RC-05 | Trivial | 0.5 | dir tree per `repository_v2.md` | `git status` shows only new empty dirs; suite unchanged | Skeleton exists |
| INFRA-02 | Move `infra/{config,constitution,ops,runtime,database,app}` with shims | infra | INFRA-01 | Medium | 6 | `backend/{ops,runtime,database,app,constitution}/*`→`infra/*` | `pytest -m "not slow"` green; `from backend.*` resolves via shim | Infra relocated, backward-compatible |
| INFRA-03 | Move Program A (retrieval + nlp) with shims | H1 | INFRA-02 | Medium | 3 | `backend/{retrieval,nlp}/*`→`program_a/*` | suite green; `from infra.app.main import app` works | Program A relocated |
| INFRA-04 | Move Program B soul_graph + concepts with shims (retained, not an EXP-2 dep) | H2 | INFRA-02 | Easy | 1 | `backend/soul/*`→`program_b/*` | suite green | Program B relocated; flagged non-EXP-2-dependency |
| INFRA-05 | Move Program C subpackages (cognition/memory/learning/knowledge/pipeline/…) with shims | H\* infra | INFRA-02 | Hard | 12 | `backend/*`→`program_c/*` | suite green after each subpackage commit | Program C relocated |
| INFRA-06 | Consolidate benchmarks (backend/evaluation, validation, research/evaluation) | infra | INFRA-05 | Medium | 3 | `→benchmarks/*` | `pytest research/tests -m "not slow"` green | One benchmark tree |
| INFRA-07 | Refactor legacy predictor/MDL/metric sites to import from `core/` (thin wrappers) | H\* | CORE-TEST, INFRA-05 | Hard | 6 | `program_c/cognition/*`, `benchmarks/evaluation/metrics.py` | duplicated predictor/NMI logic removed; imports resolve to `core/` | Single source of truth = `core/` |
| INFRA-08 | Bulk import-rewrite codemod + delete all shims | infra | INFRA-03..07 | Very-Hard | 8 | `scripts/_fix_imports_v2.py`, ~250 files | pre/post gate: `from backend.` count → 0; full `pytest` green | v2 imports everywhere; shims gone |

---

## Milestone M2 — EXP-0 Paraphrase Precondition

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| EXP0-01 | Freeze code; config+commit hashing for the run | EXP-0 | RC-08 | Easy | 2 | `experiments/EXP-0/run_exp0.py`, `.../config.json` | run records git+config hash; refuses to run on dirty tree | Frozen, provenance-stamped harness |
| EXP0-02 | 64 interleaved trials: 32 original "What is X?" + 32 keyword-free paraphrases | EXP-0 | EXP0-01 | Medium | 3 | `experiments/EXP-0/paraphrases.json`, `.../dataset.py` | 64 trials load; 32/32 split; interleaved order asserted | Trial set built |
| EXP0-03 | Wipe semantic graph + episodic memory before every trial; log `graph_wiped:true` | EXP-0 | EXP0-02 | Hard | 4 | `experiments/EXP-0/run_exp0.py` | every trial logs `graph_wiped:true` before eval; state hash resets between trials | No Hebbian leakage across trials |
| EXP0-04 | Leakage checks: no keyword, no Porter-stem collision | EXP-0 | EXP0-02 | Medium | 2 | `experiments/EXP-0/leakage_check.py` | check fails build if any paraphrase shares stem/keyword with target | Leakage-free paraphrases certified |
| EXP0-05 | Score detection across Tier-1 embedding + Tier-2 lexical | EXP-0 | EXP0-03 | Medium | 3 | `experiments/EXP-0/detectors.py` | per-trial detection score emitted for both tiers | Detection measured original vs paraphrase |
| EXP0-06 | Analysis + `[FACT]`-tagged report (original vs paraphrase delta + CI) | EXP-0 | EXP0-05 | Easy | 2 | `experiments/EXP-0/analysis.py`, `.../EXP0_REPORT.md` | report shows collapse magnitude + CI; decision recorded | Headline retired or confirmed per §7 |

---

## Milestone M3 — EXP-1 Calibration Gate (Deliverable #1)

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| EXP1-01 | Build ≥200 mixed query set (facts, ambiguous, hallucinations) with ground truth | H1 | RC-03 | Medium | 4 | `experiments/EXP-1/dataset.py`, `.../queries.jsonl` | ≥200 queries; label distribution documented | Query set frozen |
| EXP1-02 | Log predicted tier (CERTAIN/PROBABLE/DEBATED/UNKNOWN) vs empirical correctness | H1 | EXP1-01 | Medium | 3 | `experiments/EXP-1/run.py` | per-query (tier, correct?) rows emitted | Tier↔correctness captured |
| EXP1-03 | ECE + reliability diagram from `core/measurement` | H1 | EXP1-02, CORE-02 | Medium | 3 | `core/measurement/metrics.py`, `experiments/EXP-1/analysis.py` | ECE computed on fixed bins; SVG reliability diagram from raw CSV | ECE artifact produced |
| EXP1-04 | Control: BM25/TF-IDF retrieval with randomly assigned confidence | H1 | EXP1-01 | Medium | 3 | `experiments/EXP-1/control_bm25.py` | control ECE computed on same query set | Baseline present for comparison |
| EXP1-05 | Goodhart guard: flag bin-boundary hacking (lower ECE w/o retrieval-signal gain) | H1 | EXP1-03 | Medium | 2 | `experiments/EXP-1/goodhart_guard.py` | guard detects bin re-drawing that lowers ECE without accuracy change | Threshold-hacking blocked |
| EXP1-06 | PASS/FAIL decision: PASS iff ECE<0.10 else FAIL (single gate) | H1 | EXP1-03..05 | Easy | 1 | `experiments/EXP-1/decision.py` | decision emitted from artifact; no 0.10–0.15 dead zone | Product-honesty verdict wired (§6-H1) |

---

## Milestone M4 — E0 H\* Decider (Deliverable #3)

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| E0-01 | Synthetic generator: K latent states + nonlinear observation mixing | H\*/I3 | CORE-01 | Hard | 5 | `experiments/E0/dataset.py` | generator emits (obs, true_latent) pairs; K configurable via scientific-params | Environment exists |
| E0-02 | Offline verification a linear/fixed-capacity predictor cannot recover latent | H\*/I3 | E0-01 | Hard | 4 | `experiments/E0/leakage_check.py` | linear-probe recovery ≈ chance; nonlinearity certificate stored | F1/I3 addressed offline |
| E0-03 | Condition T: error-gated growth ON (CORE-03 trigger; no seeded concepts/ontology/self-model) | H\* | CORE-03, E0-01 | Hard | 5 | `experiments/E0/run.py` | T runs; growth events logged as integers+step; no seed concepts loaded | Treatment wired |
| E0-04 | Condition C1: fixed capacity | H\* | CORE-05, E0-03 | Easy | 1 | `experiments/E0/run.py` | C1 runs, no growth | C1 wired |
| E0-05 | Condition C2: capacity-matched growth at random times (decoupled from error) | H\* | CORE-05, E0-03 | Medium | 2 | `experiments/E0/run.py` | C2 growth count matches T but timing random | C2 wired |
| E0-06 | Condition C3: shuffled input | H\* | CORE-05, E0-03 | Easy | 1 | `experiments/E0/run.py` | C3 preserves marginals, destroys temporal order | C3 wired |
| E0-07 | DV-a: held-out predictive log-likelihood via proper held-out split | H\* | E0-03, CORE-02 | Medium | 3 | `experiments/E0/analysis.py` | held-out LL emitted per condition per seed | DV-a measured |
| E0-08 | DV-b: `M=NMI(learned,true)−NMI(learned,shuffled)` via CORE-04 | H\* | E0-03, CORE-04 | Medium | 3 | `experiments/E0/analysis.py` | `M` emitted with null reference | DV-b measured |
| E0-09 | **Purge [REJECTED] free-energy** in `experiments/E0/run.py`; replace with log score + MDL trigger | H\* | CORE-02, CORE-03 | Medium | 2 | `experiments/E0/run.py` | `grep -n "free_energy\|compute_free_energy" experiments/E0/run.py` → 0 | E0 path free of rejected math |
| E0-10 | Instrument ≥1 of 5 unmeasurable primary metrics (HeldOutPredictiveLogLikelihood) | H\*/R-2 | E0-07 | Medium | 3 | `core/measurement/observability.py` | HeldOut LL measured end-to-end and logged | Observability gap reduced |
| E0-11 | Central PRNG registry; env seed separate from agent seed | H\* | E0-03 | Medium | 2 | `experiments/E0/run.py` | no deep `np.random.seed()`; two tracked seeds logged | Reproducible randomness |
| E0-12 | Pre-evaluation state snapshots; provenance = commit+config hash | H\* | E0-03 | Easy | 2 | `experiments/E0/run.py` | state serialized before eval; hashes in results.json | Reproducible state |
| E0-13 | Decision: T>C1 AND T>C2 on DV-a at p<0.01 over ≥5 seeds; DV-b > margin | H\* | E0-07, E0-08 | Medium | 3 | `experiments/E0/decision.py` | decision computed from CSVs (paired t-test); ≥5 seeds required | Pass/kill machine-checked |
| E0-14 | Two-honest-attempts protocol; on fail emit "H\* falsified for this environment class" | H\* | E0-13 | Easy | 1 | `experiments/E0/decision.py` | after 2 attempts, verdict string emitted per §6-H\* | Kill criterion wired |

---

## Milestone M5 — EXP-2 Affective Indexing (Deliverable #2)

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| EXP2-01 | Assemble isolated third-party task battery (debugging, planning) not authored against affect categories | H2 | RC-03 | Medium | 4 | `experiments/EXP-2/tasks.jsonl` | task provenance shows zero overlap with 32 affect categories | Circularity-safe task set |
| EXP2-02 | Enforce zero dependency on soul concepts/`concepts.json` | H2 | EXP2-01 | Easy | 1 | `experiments/EXP-2/` | `grep -RniE "soul|concepts.json|program_b" experiments/EXP-2` → 0 | Designer-injection confound removed |
| EXP2-03 | Treatment (affective-frame prompt) vs control (neutral prompt) | H2 | EXP2-01 | Medium | 3 | `experiments/EXP-2/run.py` | both arms run on identical tasks; only prompt differs | Framed/unframed arms wired |
| EXP2-04 | Objective task-success scoring (not search-steps/compression) | H2 | EXP2-03 | Medium | 3 | `experiments/EXP-2/analysis.py` | success rate computed from objective checks (tests pass / plan valid) | Correct observable measured (§10 Issue-5) |
| EXP2-05 | Significance test at pre-registered level; guard against per-task schema re-authoring | H2 | EXP2-04 | Medium | 2 | `experiments/EXP-2/decision.py` | test emitted; schemas fixed across tasks (hash-checked) | Kill criterion wired (§6-H2) |

---

## Milestone M6 — Publication & Reproducibility

| ID | Description | Maps-to | Deps | Diff | Est | Files | Acceptance test | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| PUB-01 | Delete "Novel/First" tags on `E`, Inertia Law, three-pressure scoring, "forgetting cure" | §8 | M2..M5 | Easy | 2 | `RELATED_WORK.md`, `GRANT_PACKAGE.md`, `PUBLICATION_CHECKLIST.md` | `grep -niE "novel|first" ` → no hits on rejected constructs | No novelty overclaim |
| PUB-02 | Cite owning prior art: Oudeyer&Kaplan 2007, Weng 2001, Pathak 2017, Burda 2018; upgrade Rao–Ballard 1999 | §8 | PUB-01 | Medium | 3 | `RELATED_WORK.md` | four anchors + Rao–Ballard present with citations | Prior art closed |
| PUB-03 | Concede novelty objection; keep stats/baseline objections | §8 | PUB-01 | Easy | 2 | `REVIEWER_OBJECTIONS.md` | novelty objection conceded; R1 null (p=0.866) reported as finding | Honest posture |
| PUB-04 | Dockerized immutable run env; pinned deps; code-freeze policy | repro | M1 | Medium | 4 | `Dockerfile`, `pyproject.toml`, `reproducibility.yaml` | clean container reproduces an experiment artifact | Repro env builds |
| PUB-05 | Each experiment ships prereg+protocol+run+analysis+artifact; figures from raw CSV | repro | M2..M5 | Medium | 4 | `experiments/*/` | every live experiment dir complete; SVG regenerated from CSV | Reproducible experiment bundles |

---

## Backlog summary

| Milestone | Tasks | Est (h) | Critical-path risk |
|---|---|---|---|
| M0 Reconciliation | 8 | **0 (DONE)** | None (Completed) |
| M1 Core + Skeleton | 16 | ~92 | Very-High (INFRA-08 codemod, CORE extraction) |
| M2 EXP-0 | 6 | ~16 | Medium (state reset) |
| M3 EXP-1 | 6 | ~16 | Medium |
| M4 E0 | 14 | ~40 | High (keystone I2) |
| M5 EXP-2 | 5 | ~13 | Medium (circularity) |
| M6 Publication | 5 | ~15 | Low–Medium |
| **Total** | **60** | **~192.5 h (~24 ed)** | — |

*Note:* the ~24 engineer-day floor here counts only atomic coding tasks; the roadmap's ~55 ed adds review, preregistration authoring, seeded reruns, and analysis iteration (canonical priority: reproducibility > speed).

**Ready-to-start now (no open deps):** CORE-02, CORE-04. See `EXECUTION_ORDER.md` for the full unblock sequence.
