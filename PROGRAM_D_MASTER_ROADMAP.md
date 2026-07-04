# PROGRAM D — MASTER ROADMAP

**Status:** Official engineering execution plan for Program D.
**Supreme authority:** `PROGRAM_D_CANONICAL.md`. Every milestone, epic, feature, and task below derives from it and cites the governing section. Where this roadmap and any other document disagree, the canon wins and the other document is a defect (see `IMPLEMENTATION_GAPS.md`).
**Derivation rule (canonical §9):** every downstream document — including this one — is a *proposal* until it derives from canonical §1–§8. This roadmap is written to derive from those sections and to *force* the still-unreconciled documents into compliance (Milestone M0).
**Generated:** 2026-07-03. **Integrator:** Program Director / Canonical Integrator.

---

## 0. How to read this roadmap

- **Prime directive (canonical §1):** Program D is an *audit-and-falsification protocol*, not a generator of new science. No task below invents a hypothesis, mechanism, or metric. Every task exists because a pre-registered experiment in `{EXP-0, EXP-1, EXP-2, E0}` requires it (canonical §1 rule 2).
- **Priority order under trade-off (canonical §1 rule 4):** scientific correctness > experiment reproducibility > code simplicity > performance > features. All effort estimates and sequencing obey this.
- **Every task maps to a hypothesis or experiment.** The mapping column is mandatory. A task with no hypothesis/experiment owner is out of scope by construction and does not appear here.
- **Owners.** *Scientific owner* = accountable for the claim being tested (PI / Lead Research Director). *Engineering owner* = accountable for the build (role names from `repository_v2.md`: Research Engineering Lead, Product Engineering Lead, Engineering Lead).
- **Effort** is in engineer-days (ed), single engineer, and is an estimate for planning only — never a reason to cut scientific correctness.

### Canonical objects this roadmap builds toward

| Object | Canonical source | Frozen definition |
|---|---|---|
| Hypotheses | §6 | **H\*** (error-gated structure acquisition, central), **H1** (calibration), **H2** (affective indexing). **H3 is [REJECTED]/subsumed by H\***. |
| Experiments | §7 | **EXP-0** (paraphrase precondition), **EXP-1** (H1, ECE<0.10), **EXP-2** (H2, framed vs unframed), **E0** (H\*, T/C1/C2/C3). No EXP-3/EXP-4/R2/R3F in the live program. |
| Primitives | §5 | `{ x_t, P_θ over Θ_k, L=−log P_θ, G with λ_model=k·b+n·log₂N, M=NMI(learned,true)−NMI(learned,shuffled) }`. |
| Keystone | §4 | **I2** — "emergent structure operationally distinguishable from injected." Program D's entire viability reduces to making I2 true. E0 is the first test wired to it. |

---

## 1. Milestone map (scientifically ordered)

| # | Milestone | Canonical driver | Exit gate | Effort |
|---|---|---|---|---|
| **M0** | Canonical Reconciliation & Defect Closure | §9 (all docs are proposals until reconciled), §10 | All eight downstream docs + 2 registries derive from canon; zero live references to H3/EXP-3/EXP-4/free-energy `E`/anthropomorphic names | 4 ed |
| **M1** | Repository v2 Skeleton & Compliant 5-Primitive Core | §5, §9-DeepSeek | `core/` implements exactly the 5 primitives with `λ_model=k·b+n·log₂N` and null-referenced `M`; rejected/anthropomorphic modules archived; suite green | 10 ed |
| **M2** | EXP-0 — Paraphrase Precondition | §7 EXP-0, §11 (immediate next action) | Frozen-code paraphrase run complete; headline claim retired or confirmed | 5 ed |
| **M3** | EXP-1 — Program A Calibration Gate (Deliverable #1) | §3 deliverable 1, §6-H1, §7 EXP-1 | ECE reported on ≥200 queries; PASS iff ECE<0.10 | 7 ed |
| **M4** | E0 — H\* Decider & Observability (Deliverable #3) | §3 deliverable 3, §6-H\*, §7 E0, §4-I2 | E0 runs T/C1/C2/C3 on nonlinear-latent stream; DV-a LL + DV-b `M`; ≥1 of 5 unmeasurable metrics instrumented; kill wired | 15 ed |
| **M5** | EXP-2 — Affective Indexing (Deliverable #2, the possibly-novel question) | §3 deliverable 2, §6-H2, §7 EXP-2 | Framed vs unframed on third-party task set with zero soul-concept dependency | 8 ed |
| **M6** | Publication Reconciliation & Reproducibility | §8, §9-Nemotron | Novelty verdict enforced; prior art cited; negative-result/methodology path packaged; repro bundle builds | 6 ed |

**Total planning effort:** ~55 engineer-days (~11 engineer-weeks). Scientific-correctness gates (M0, M1) are non-negotiable predecessors; they are not "overhead," they are the thing that makes the rest science (canonical §4: "making I2 true before the word 'emergence' is used again").

**Deliverable priority (canonical §3) vs. build order:** the *scientific* priority is EXP-1 (1) > EXP-2 (2) > E0 (3). The *build* order differs because EXP-0 is the cheap precondition that must run first (§11) and M0/M1 gate everything. Reconciled sequence is in `EXECUTION_ORDER.md`.

---

## 2. Milestone M0 — Canonical Reconciliation & Defect Closure

**Why (canonical §9, §10):** Eight downstream documents and two registries still assert the pre-redesign program (H3 live, EXP-3/EXP-4 built, free-energy `E` in the E0 path, `soul_graph` as an EXP-2 dependency, anthropomorphic module names). Canonical §9 declares each a *proposal* until reconciled; §1 rule 2 forbids building any subsystem no live experiment needs. Until M0 closes, every engineering task risks implementing a [REJECTED] claim. This milestone contains **no science** — it only forces existing docs to match the canon.

**Scientific owner:** Lead Research Director. **Engineering owner:** Research Engineering Lead.

### Epic M0-E1 — Hypothesis & protocol layer reconciliation
- **Feature:** Purge H3 as a live hypothesis; make H\*/H1/H2 the sole set (canonical §6, §10 Issue-1).
- **Tasks:** RC-01 (strike H3/EXP-3 from `HYPOTHESIS_REGISTER.md`), RC-02 (strike EXP-3 from `EXPERIMENT_PROTOCOLS.md`), RC-03 (rewrite `PROGRAM_D_SPECIFICATION.md` §3-H2 from "dimensionality reduction/search-steps/dense-embedding" to the §6-H2 task-score/unframed-prompt form; retire the 0.15 ECE dead-zone per §10 Issue-4).
- **Deliverable:** Hypothesis/protocol docs contain H\*, H1, H2 and experiments EXP-0/EXP-1/EXP-2/E0 only.
- **Acceptance:** `grep -RniE "H3|EXP-?3|EXP-?4|dimensionality reduction|search steps|dense.embedding|0\.15"` over the four science docs returns only `[REJECTED]`/archival cross-references.
- **Maps to:** H\*, H1, H2 (all). **Risk:** low. **Rollback:** `git revert` (docs only).

### Epic M0-E2 — Engineering & registry layer reconciliation
- **Feature:** Remove EXP-3/EXP-4, `self_model`, and `soul_graph`-as-EXP-2-dependency from the engineering plan and registries (canonical §9-DeepSeek, §10 Issue-6).
- **Tasks:** RC-04 (`repository_v2.md`: delete EXP3/EXP4 rows, mark `self_model`→archive, remove `soul_graph`+`concepts.json` from EXP-2 dependents), RC-05 (`migration_plan.md` + `implementation_checklist_v1.md`: drop `experiments/EXP3|EXP4`, `program_c/self_model`, `infra/app/soul` from Phase-0 skeleton; add the anthropomorphic-rename step), RC-06 (`experiment_registry.yaml`: delete EXP3/EXP4 entries, set R2/R3F to archived — not live), RC-07 (`parameter_registry.yaml`: relabel `free_energy` λ/μ/ν, `ENERGY_EXHAUSTION`, `STRATEGY_FREE_ENERGY` as `[REJECTED] archive-only`; pin `mdl.lambda_model` to `k·b+n·log₂N` — remove "configurable").
- **Deliverable:** One import-remap table, one directory skeleton, one archive-target list (de-duplicated per §9-DeepSeek), free of rejected constructs.
- **Acceptance:** the three engineering docs agree on a single skeleton with no EXP-3/EXP-4/self_model; registries carry no live free-energy parameter.
- **Maps to:** H2 (circularity guard), H\* (MDL derivation). **Risk:** low. **Rollback:** `git revert`.

### Epic M0-E3 — Coverage-matrix replacement
- **Feature:** Replace the legacy Program-C coverage matrix (E1–E13, `self_coder`, `inertia_law`, `free_energy_vs_pareto`) with a Program-D matrix over EXP-0/EXP-1/EXP-2/E0 (canonical §7).
- **Tasks:** RC-08 (author `experiments/coverage/experiment_coverage_matrix.csv` mapping each live experiment → component → hypothesis → metric → kill criterion).
- **Acceptance:** every row maps to a `{EXP-0,EXP-1,EXP-2,E0}` experiment; no legacy `E*` rows remain.
- **Maps to:** all four experiments. **Risk:** low.

**M0 acceptance criteria (gate):** `TRACEABILITY_MATRIX.md` has zero unmapped rows; no live document references a [REJECTED] object; `IMPLEMENTATION_GAPS.md` shows all "contradiction" gaps closed.

---

## 3. Milestone M1 — Repository v2 Skeleton & Compliant 5-Primitive Core

**Why (canonical §5, §9-DeepSeek):** The five primitives are the only mathematical substrate permitted. The current `core/` partially exists but (a) `core/mdl/mdl_growth.py` implements a BIC-style `params·log(n)/2` cost with a `lambda_model=1.0` default rather than the derived ledger `λ_model=k·b+n·log₂N`, and (b) anthropomorphic/rejected modules (`self_model`, `dream_state`, `monologue`, `curiosity`, `belief*`, free-energy `E`) still sit in the live tree. This milestone makes `core/` canon-exact and archives everything no live experiment needs.

**Scientific owner:** Lead Research Director. **Engineering owner:** Research Engineering Lead.

### Epic M1-E1 — Canon-exact 5-primitive core
- **Features & tasks:**
  - CORE-01 — `core/predictors/dirichlet_markov.py`: growable Dirichlet–Markov conjugate predictor `{P_θ(x_{t+1}|x_≤t):θ∈Θ_k}` indexed by capacity `k`; drop the label "belief model" (§5.2).
  - CORE-02 — `core/measurement/proper_scoring.py`: log score `L=−log P_θ` as the sole loss; delete any `E=λH+μS+νA` path (§5.3, Bernardo-1979 uniqueness).
  - CORE-03 — `core/mdl/mdl_growth.py` + `concept_birth_ledger.py`: implement `G=H_before−H_after−λ_model` with **`λ_model=k·b+n·log₂N`** wired from the concept-birth ledger, **not hand-set** (§5.4, §10 Issue-3; hand-set = failure-mode F2, violates I2).
  - CORE-04 — `core/emergence/emergence_statistic.py` + `null_referenced_test.py`: `M=NMI(learned,true)−NMI(learned,shuffled)` with `E[M|H₀]=0`; delete the graph-isomorphism form (§5.5, §10 Issue-2).
  - CORE-05 — `core/controls/{fixed_capacity,random_growth,shuffled_input}.py`: C1/C2/C3 as importable controls (§7 E0).
- **Deliverable:** `core/` = exactly `{predictors, measurement, mdl, emergence, controls}` implementing the 5 primitives, single source of truth for all experiments.
- **Acceptance:** unit tests prove (i) `λ_model` equals `k·b+n·log₂N` for sampled `(k,n,N)` and is not readable from any JSON config; (ii) `E[M|H₀]≈0` on shuffled input within tolerance; (iii) log score matches a reference implementation; (iv) no symbol named `free_energy`/`E`/`belief` in `core/`.
- **Maps to:** H\* (CORE-01..05), H1 (CORE-02 scoring reused), H2 (none). **Risk:** High (scientific-semantics extraction). **Rollback:** revert; re-extract against reference.

### Epic M1-E2 — Archive rejected & anthropomorphic mechanisms
- **Feature:** Move to `archive/` (never live): `program_c/self_model/`, `reasoning_engine` type-lifting, `ontology_loader`, free-energy/R1 (as closed evidence), and rename/retire live names `soul`, `belief`, `curiosity`, `dream_state`, `monologue` (§5 rejected list, §9-DeepSeek).
- **Tasks:** CORE-06 (grep-verified archival with zero live imports), CORE-07 (anthropomorphic-name rename map).
- **Acceptance:** `grep -RniE "\b(soul|belief|curiosity|dream_state|monologue|self_model)\b"` returns matches only under `archive/`. Suite green via shims until Phase-9 rewrite.
- **Maps to:** constitutional §1 rule 5 (anti-anthropomorphism), enables clean E0/EXP-2. **Risk:** Medium.

### Epic M1-E3 — Repo migration skeleton (v2)
- **Feature:** Execute the de-duplicated `repository_v2.md` skeleton (post-M0), dual-import shim strategy, per `implementation_checklist_v1.md` Phases 0/3/4/5.
- **Tasks:** INFRA-01..08 (directory skeleton; infra/programA/programB/programC moves; benchmark consolidation; shim removal codemod).
- **Acceptance:** `pytest -m "not slow"` green at every commit; post-codemod `from backend.*` resolves to zero.
- **Maps to:** infrastructure for all experiments. **Risk:** Very High at codemod (INFRA-08). **Rollback:** revert per commit; shims restore old paths.

**M1 acceptance criteria (gate):** `python -c "import core"` exposes the 5 primitives; `λ_model` and `M` are canon-exact; no rejected/anthropomorphic symbol in the live tree; test suite green.

---

## 4. Milestone M2 — EXP-0 Paraphrase Precondition

**Why (canonical §7 EXP-0, §11):** The immediate next action. It tests the *old deployed system*, not H\*: does concept detection collapse when the 32 seeded concepts are queried via keyword-free paraphrases? Predicted collapse ~100/100 → ~4.0/10. Its purpose is to **stop the deployed system claiming its headline** before any H\* work.

**Scientific owner:** Lead Research Director. **Engineering owner:** Engineering Lead.

### Epic M2-E1 — Frozen paraphrase harness
- **Features & tasks:** EXP0-01 (freeze code + config/commit hashing), EXP0-02 (64 interleaved trials: 32 original "What is X?" vs 32 keyword-free paraphrases from `paraphrases.json`), EXP0-03 (**wipe semantic graph + episodic memory before every trial**; log `graph_wiped:true` per trial — no Hebbian leakage), EXP0-04 (leakage checks: no keyword, no Porter-stem collision), EXP0-05 (reliability scoring across Tier-1 embedding + Tier-2 lexical), EXP0-06 (analysis + report).
- **Deliverable:** `experiments/EXP-0/` complete harness + result artifact + finding memo.
- **Acceptance:** run produces per-trial `graph_wiped` flags, leakage-check pass, and an original-vs-paraphrase detection delta with CI; report tagged `[FACT]`.
- **Kill/decision (§7):** if detection collapses to noise on paraphrases → the "semantic understanding over a lookup table" claim is **falsified**; the headline is retired.
- **Maps to:** EXP-0 (precondition; not a hypothesis test). **Risk:** Medium (state-reset correctness is the whole validity). **Rollback:** revert; artifacts archived pre-migration.

---

## 5. Milestone M3 — EXP-1 Program A Calibration Gate  *(Deliverable #1)*

**Why (canonical §3 deliverable 1, §6-H1, §7 EXP-1):** Program A as an honest product, gated strictly on calibration. Current status is **[REJECTED]** — it emits `CERTAIN` on hallucinated content (Q6). This is engineering, not the research center, but it is priority-1 among the three surviving deliverables.

**Scientific owner:** Lead Research Director. **Engineering owner:** Product Engineering Lead.

### Epic M3-E1 — Calibration measurement harness
- **Features & tasks:** EXP1-01 (query set ≥200: facts, ambiguous, hallucinations), EXP1-02 (tier→correctness logging for CERTAIN/PROBABLE/DEBATED/UNKNOWN), EXP1-03 (ECE + reliability diagram in `core/measurement`), EXP1-04 (control: BM25/TF-IDF retrieval with randomly assigned confidence), EXP1-05 (Goodhart guard: detect bin-boundary hacking that lowers ECE without improving the retrieval signal).
- **Deliverable:** `experiments/EXP-1/` harness + reliability diagram + ECE artifact.
- **Acceptance:** ECE computed on ≥200 queries with the fixed binning; control run present; PASS iff **ECE<0.10**, else FAIL (single gate, §10 Issue-4).
- **Kill (§6-H1):** ECE≥0.10 or tier-independence over the query set → "honest uncertainty" rejected.
- **Maps to:** H1 / EXP-1. **Risk:** Medium. **Rollback:** revert.

---

## 6. Milestone M4 — E0 H\* Decider & Observability  *(Deliverable #3)*

**Why (canonical §3 deliverable 3, §6-H\*, §7 E0, §4-I2):** E0 is the first-ever test wired to the keystone gate I2. H\* is **definitely not novel** (§8: Oudeyer, Weng, predictive coding, MDL) and its most probable publishable output is a **rigorous negative result + the discrimination methodology**. It is retained only because it is now cheap and wired to a real kill decision. E0 also attacks risk R-2 by instrumenting ≥1 of the 5 currently-unmeasurable primary metrics.

**Scientific owner:** Lead Research Director. **Engineering owner:** Research Engineering Lead.

### Epic M4-E1 — Nonlinear-latent environment
- **Tasks:** E0-01 (synthetic generator: K latent states, nonlinear observation mixing), E0-02 (**offline verification** that a linear/fixed-capacity predictor cannot recover the latent — addresses failure-mode F1 and assumption I3).
- **Acceptance:** offline check shows linear predictor recovery ≈ chance; nonlinearity certificate stored with the dataset.
- **Maps to:** H\* / E0, assumption I3.

### Epic M4-E2 — Conditions & DV instrumentation
- **Tasks:** E0-03 (**T**: error-gated growth ON — uses CORE-03 trigger, **no seeded concepts/ontology/self-model**), E0-04 (**C1** fixed capacity), E0-05 (**C2** capacity-matched growth at random times), E0-06 (**C3** shuffled input), E0-07 (**DV-a**: held-out predictive log-likelihood via a proper held-out split), E0-08 (**DV-b**: `M=NMI(learned,true)−NMI(learned,shuffled)` via CORE-04), E0-09 (**purge the [REJECTED] free-energy** compute currently in `experiments/E0/run.py` — replace with log score + MDL trigger).
- **Acceptance:** all four conditions run from one frozen build across **≥5 seeds**; DV-a and DV-b emitted per seed; `run.py` contains no `free_energy`/`E` symbol.
- **Maps to:** H\* / E0 (crux clause iii = I2).

### Epic M4-E3 — Observability instrumentation (attacks R-2)
- **Tasks:** E0-10 (instrument ≥1 of the 5 unmeasurable primary metrics — HeldOutPredictiveLogLikelihood is the natural first, since DV-a already requires it), E0-11 (central PRNG registry; separate env seed from agent seed per `EXPERIMENT_INTERFACE_SPEC.md`), E0-12 (state snapshots pre-evaluation; provenance = commit+config hash).
- **Acceptance:** at least HeldOutPredictiveLogLikelihood is measured end-to-end; seeds and snapshots logged.
- **Maps to:** H\* / E0, risk R-2 (observability gap).

### Epic M4-E4 — Wired kill decision
- **Tasks:** E0-13 (decision module: T>C1 **and** T>C2 on DV-a at **p<0.01** across ≥5 seeds; DV-b exceeds pre-registered margin), E0-14 (two-honest-attempts protocol; on failure emit **"H\* falsified for this environment class"**).
- **Acceptance:** decision is computed automatically from artifacts, not by hand; kill/pass is reproducible from the CSVs.
- **Kill (§6-H\*):** T fails to beat both C1 and C2 on DV-a at p<0.01 across ≥5 seeds, **OR** DV-b within noise of shuffled control — after two honest attempts → H\* falsified.
- **Maps to:** H\* / E0. **Risk:** High (this is the keystone; prior on H₀ is high per R1 null). **Rollback:** revert; artifacts immutable.

**M4 acceptance criteria (gate):** E0 produces a machine-checked pass/kill on H\* from frozen code, with DV-a and null-referenced DV-b, ≥5 seeds, ≥1 unmeasurable metric now measured, and zero rejected math in the path.

---

## 7. Milestone M5 — EXP-2 Affective Indexing  *(Deliverable #2 — the one possibly-novel question)*

**Why (canonical §3 deliverable 2, §6-H2, §7 EXP-2, §8):** H2 is the **only possibly-novel [PN] element** in the entire corpus and is untested. It asks whether a learned affective-framing→problem-solving-schema mapping improves **objective task outcomes** over an unframed baseline.

**Scientific owner:** Lead Research Director. **Engineering owner:** Engineering Lead.

### Epic M5-E1 — Third-party task battery (circularity guard)
- **Tasks:** EXP2-01 (assemble isolated third-party tasks — debugging fixes, planning — the affect categories were **not** authored against), EXP2-02 (**forbid any dependency on the 32 soul concepts / `concepts.json`** — canonical §10 Issue-6; the control is the *unframed prompt*, not dense-embedding cosine search).
- **Acceptance:** task set provenance shows zero overlap with the authored affect categories; no import of `program_b`/`soul_graph`/`concepts.json` in the EXP-2 path.
- **Maps to:** H2 / EXP-2 circularity guard.

### Epic M5-E2 — Framed-vs-unframed measurement
- **Tasks:** EXP2-03 (treatment: affective-frame prompt e.g. shame→debugging; control: neutral prompt), EXP2-04 (objective task-success scoring — **not** search-steps or compression ratio, §10 Issue-5), EXP2-05 (significance test at pre-registered level; guard against per-task schema re-authoring = circularity).
- **Acceptance:** framed vs unframed success rates with a pre-registered test; schemas fixed across tasks.
- **Kill (§6-H2):** no significant task-outcome difference, **or** schemas must be re-authored per task.
- **Maps to:** H2 / EXP-2. **Risk:** Medium.

---

## 8. Milestone M6 — Publication Reconciliation & Reproducibility

**Why (canonical §8, §9-Nemotron):** The publication cluster overclaims novelty and omits owning prior art. The honest path is a **negative-result + methodology** paper (designer-injection confound, paraphrase-collapse, the I2 null-referenced emergence-discrimination protocol), plus a focused H2 paper *if* EXP-2 finds signal.

**Scientific owner:** Lead Research Director. **Engineering owner:** Research Engineering Lead.

### Epic M6-E1 — Novelty verdict enforcement
- **Tasks:** PUB-01 (delete every "Novel/First" tag on `E`, Inertia Law, three-pressure scoring, "catastrophic-forgetting cure" — contradicted by R1 null p=0.866), PUB-02 (add owning prior art to `RELATED_WORK.md`: **Oudeyer & Kaplan 2007, Weng 2001, Pathak 2017 ICM, Burda 2018 RND**; upgrade Rao–Ballard 1999 to prior art of the core loop), PUB-03 (concede the novelty objection in `REVIEWER_OBJECTIONS.md`; keep the sound stats/baseline objections).
- **Acceptance:** no novelty tag survives on a rejected construct; the four prior-art anchors are cited.
- **Maps to:** §8 novelty verdict (governs H\*), publication of all experiments.

### Epic M6-E2 — Reproducibility bundle
- **Tasks:** PUB-04 (Dockerized immutable run env; pinned deps; code-freeze policy during any experiment), PUB-05 (each experiment ships preregistration + protocol + run + analysis + result artifact; SVG/PDF figures regenerated from raw CSV).
- **Acceptance:** `DATA_MANAGEMENT_PLAN.md` / `REPRODUCIBILITY_CHECKLIST.md` satisfied; a clean checkout reproduces each experiment's artifact.
- **Maps to:** reproducibility of EXP-0/EXP-1/EXP-2/E0. **Risk:** Low–Medium.

---

## 9. Dependencies (milestone-level)

```
M0 (reconcile) ─┬─▶ M1 (core) ─┬─▶ M4 (E0)      ┐
                │              └─▶ M2 (EXP-0)*   │
                ├─────────────────▶ M3 (EXP-1)   ├─▶ M6 (publication)
                └─────────────────▶ M5 (EXP-2)   ┘
```
- **M0 blocks everything** (canon compliance precondition).
- **M2 (EXP-0)** depends only on M0 + a frozen build of the *existing* system — not on the new `core/`; it can start as soon as M0 lands (this is why §11 calls it the immediate next action).
- **M3 (EXP-1)** depends on M0 + `core/measurement` (ECE) from M1-E1 (CORE-02/03 not required; only scoring/metrics).
- **M4 (E0)** depends on the full compliant `core/` (M1-E1 CORE-01..05).
- **M5 (EXP-2)** depends on M0 + M1-E2 (soul-concept decoupling) only.
- **M6** depends on results from M2–M5.

Full task-level DAG is in `EXECUTION_ORDER.md`.

---

## 10. Risk register (program-level)

| ID | Risk | Canonical link | Likelihood | Impact | Mitigation | Rollback |
|---|---|---|---|---|---|---|
| R-KEYSTONE | I2 remains un-operationalized; "emergence" used without a null reference | §4, §5.5 | Med | Fatal (not science) | E0 DV-b is null-referenced by construction; block the word "emergence" in outputs until `M` ships | N/A — gate, cannot ship without it |
| R-REJECTED-MATH | Free-energy `E` re-enters a live path (already present in `E0/run.py`) | §5 rejected list, §8 | High (observed) | High | CORE-02 deletes `E`; CI grep-gate bans `free_energy`/`E=λH` symbols in `core/`+`experiments/` | revert to pre-M1 |
| R-CIRCULARITY | EXP-2 tied to the 32 authored concepts | §10 Issue-6 | Med | High (kills the only novel result) | M5-E1 forbids soul-concept imports; third-party task provenance check | revert task set |
| R-2 OBSERVABILITY | 5 of 6 primary metrics unmeasurable → hypotheses untestable | §7 E0, RESEARCH_STATE R-2 | High | High | E0-10 instruments ≥1 (HeldOut LL); roadmap does not claim the other 4 until measured | scope-limit claims |
| R-HANDSET-λ | `λ_model` exposed as a tunable config (present in registry + interface spec) | §5.4, §10 Issue-3 | High (observed) | High | CORE-03 wires `k·b+n·log₂N`; test asserts non-configurability | revert |
| R-NOVELTY | Publication asserts novelty in uncited Oudeyer/Weng space | §8 | High | High (desk-reject) | M6-E1 cites owning prior art; concede objection | doc revert |
| R-CODEMOD | Bulk import rewrite breaks the suite | checklist 9.1 | Med | High | pre/post grep-count gate; split by module; clean-tree checkpoint | revert commit |

---

## 11. Program-level acceptance criteria (definition of done for Program D execution)

1. **Canon compliance:** every live document and registry derives from `PROGRAM_D_CANONICAL.md`; `TRACEABILITY_MATRIX.md` has zero unmapped rows; no live reference to any [REJECTED] object (H3, EXP-3/4, `E`, graph-isomorphism `M`, hand-set `λ`, soul-concept EXP-2 dependency, anthropomorphic live names).
2. **Core correctness:** `core/` implements exactly the 5 primitives with `λ_model=k·b+n·log₂N` and null-referenced `M`; unit tests prove canon-exactness.
3. **Four experiments runnable from frozen code:** EXP-0, EXP-1, EXP-2, E0 each produce a pre-registered, provenance-stamped artifact and a machine-checked pass/kill.
4. **Keystone attacked:** E0 emits a null-referenced `M` and instruments ≥1 previously-unmeasurable primary metric.
5. **Honest publication posture:** novelty verdict enforced; owning prior art cited; negative-result/methodology path packaged; reproducibility bundle builds.

**Single next action (canonical §11):** land **M0** (reconciliation), then start **M2 (EXP-0)** in parallel with **M1 (core)**. See `EXECUTION_ORDER.md`.
