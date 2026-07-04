# INTEGRATION LEDGER

**Role:** Integration Lead — continuous integration review of Sprint 1 engineering against `PROGRAM_D_CANONICAL.md` (immutable).
**Rules:** Never rewrite code. Never redesign. Review only. Verdicts: **PASS / WARNING / FAIL** with exact evidence. On FAIL, minimum corrections only.

Reference authority (most-authoritative-first): `PROGRAM_D_CANONICAL.md` → `foundation/program_d_scientific_foundation_v0.1.md` → experiment specs → repository architecture.

---

## Review #001 — 2026-07-04 — E0 core primitives + experiment runner (uncommitted Sprint-1 delivery)

**Scope reviewed** (working-tree changes, not yet committed): `core/mdl/mdl_growth.py`, `core/measurement/proper_scoring.py`, `core/emergence/emergence_statistic.py`, `experiments/E0/__init__.py`, `experiments/E0/run.py` (modified) + new files `core/predictors/dirichlet_markov.py`, `experiments/E0/{dataset,leakage_check,analysis,decision,config.json,E0_IMPLEMENTATION_REPORT.md}`, tests `tests/unit/test_e0_components.py`, `tests/unit/test_core_canonical.py`, `tests/integration/test_e0_pipeline.py`.

### VERDICT: **FAIL**

Single blocking defect (F1). Test suite is green (100 passed, 1 skipped, verified) — the failure is a **scientific-correctness** defect that passing tests do not catch, in the one measurement that decides H\*.

---

### Canonical-consistency checks that PASS (evidence)

| Canon | Requirement | Status | Evidence |
|---|---|---|---|
| §5.3 | Log score `L=−log P_θ` replaces `E=λH+μS+νA` | ✅ | `proper_scoring.py:75` `predictive_log_likelihood`; old `run.py` `compute_free_energy` loop **removed** in diff. |
| §5.4 | MDL trigger `G=H_b−H_a−λ_model`, `λ_model=k·b+n·log₂N`, **not hand-set** | ✅ | `mdl_growth.py:compute_lambda_model` hardcoded; `should_grow` removes `birth_threshold`. |
| §5.5 | `M=NMI(learned,true)−NMI(learned,shuffled)`, `E[M|H₀]=0` | ✅ | `analysis.py:87 compute_emergence_statistic`; NMI is permutation-invariant (correct label-agnostic comparison). |
| §7-E0 | Conditions T/C1/C2/C3; C2 capacity-matched to T; C3 marginals-preserved | ✅ | `run.py` `run_treatment/run_fixed_capacity/apply_growth_at_random_times/run_shuffled_input`; C2 uses `t_growth_count`. |
| §7-E0 | Nonlinear latent stream, verified a linear predictor can't recover it (I3) | ✅ | `dataset.py` nonlinear obs; `leakage_check.py` linear-probe test present. |
| §6-H\* | Kill wired: T>C1 **and** T>C2 at p<0.01, ≥5 seeds, 2-attempt protocol | ✅ (logic) | `decision.py:E0Decider`, `should_falsify` (2 attempts), `evaluate_multi_seed` (min_seeds gate). |
| §1 rule 5 | No anthropomorphism in live names | ✅ | Only hit: `dirichlet_markov.py:10` docstring naming "belief model" **to reject it** ("deliberately absent"). No live symbol. |
| §6 | H3 rejected / absent | ✅ | Zero `H3` refs in `core/` or `experiments/E0/`. |
| §8 | No `free_energy` in E0 path | ✅ | Zero refs in `core/` primitives + `experiments/E0/`. |

---

### F1 — FAIL — DV-a does not measure held-out predictive log-likelihood (category error + 79.5% floored)

- **Canon violated:** §6-H\* DV-a ("held-out predictive log-likelihood"), §7-E0 DV-a pass gate, §5.3 log score on the observation `x_{t+1}`. This is the **primary** variable that decides H\* (kill criterion is stated on DV-a). Priority order §1.4: scientific correctness is the top constraint.
- **Evidence (code):** `experiments/E0/run.py:219-220` (and identically `319-320`, `388-389`, `465-466`):
  ```python
  probs = predictor.predict(context)              # distribution over predictor's k INTERNAL states (len == k)
  ll = predictive_log_likelihood(probs, latent)   # indexed by ENV true latent id in [0, K_env)
  ```
  `predict()` returns a length-`k` vector (`dirichlet_markov.py:73`, `_predictive_distribution`). `latent` is `env.step()[0] = rng.choice(K_env)` in `[0,10)` (`dataset.py:109`, `config.json` `num_latent_states=10`, `initial_capacity=2`). Two different label spaces; the predictor is never told the true latent, so its internal state ids have no identity map to env latent ids **even after growth to k=K**. `proper_scoring.py:104-105` silently floors any out-of-range index to `log(1e-15) = −34.54`.
- **Evidence (runtime, my probe, 1 500 steps seed 42):**
  ```
  scored steps          = 1499
  floored to log(1e-15) = 1192  (79.5%)
  mean DV-a LL          = -27.61   (floor const = -34.54)
  ```
  → DV-a is dominated by the frequency of out-of-range index collisions, not by prediction quality. The number fed to the paired t-test in `decision.py` is an artifact.
- **Why tests miss it:** unit tests exercise `predictive_log_likelihood` on aligned toy vectors and `should_grow` in isolation; no test asserts DV-a scores the *observation* in the predictor's own label space.
- **Minimum correction (only this; no redesign):** at the four sites, route scoring through the predictor's already-implemented canonical log score on the observation (in-range by construction via `_infer_state`, `dirichlet_markov.py:220`):
  ```python
  ll = predictor.log_predictive_probability(obs_list, context)
  ```
  Delete the paired `probs = predictor.predict(context)` line at each site. (Leave `proper_scoring.predictive_log_likelihood` as a primitive — the defect is the caller pairing incompatible operands, not the function.)

---

### WARNINGS (logged; do not block independently, fix alongside F1)

**W1 — Non-reproducible seeding inside the component built to guarantee reproducibility.** `run.py:107` `self.master_seed + hash(f"agent::{condition}::{seed_idx}")` and `run.py:565` `hash(condition)` use builtin `hash()` on `str`, which Python salts per-process (`PYTHONHASHSEED`). Agent seeds and C2's growth-position RNG therefore differ run-to-run — violating §1.4 (experiment reproducibility) and the intent of `reproducibility.yaml`. Ironic locus: `SeedRegistry` is documented "central PRNG registry … ensures the agent cannot predict the environment." *Min fix:* replace `hash(...)` with a deterministic hash (e.g. `zlib.crc32(s.encode())` / `hashlib`) or integer arithmetic on `seed_idx`.

**W2 — Duplicated measurement logic + private coupling.** `run.py:122 _hypothetical_entropy_after_growth()` re-implements `DirichletMarkovPredictor.hypothetical_entropy_after_growth()` (`dirichlet_markov.py:263`) verbatim and reaches into predictor privates `predictor._alpha`, `predictor._counts` (`run.py:135-136`). The public method has **zero** production callers (only `test_e0_components.py:954`). Hidden coupling + dead public API; MDL-entropy logic belongs in the primitive, not the runner. *Min fix:* call `predictor.hypothetical_entropy_after_growth()` at `run.py:247,481`; delete the private duplicate.

**W3 — Living document contradicts shipped code (repository drift).** `experiments/E0/E0_IMPLEMENTATION_REPORT.md:38-45` describes the Issue-A fix as "save `state_dict()` → `grow()` → evaluate → `load_state_dict()` revert on negative gain." Shipped code does **not** do this — it uses the (better, non-mutating) hypothetical-entropy path; `run.py` never calls `load_state_dict`/revert. The report also claims test `test_should_grow_wires_lambda_correctly` "asserts `load_state_dict` restores capacity" — that test (`test_core_canonical.py:76`) does no such thing. Header says "77 passed, 1 skipped"; actual is **100 passed, 1 skipped**. *Min fix:* rewrite the Issue-A section to describe the hypothetical-entropy mechanism; correct the test count and the test-name claim.

**W4 — Dead imports in `run.py`.** `ArtifactStore` (`run.py:51`) imported, never instantiated (0 `store.` uses). `compute_held_out_log_likelihood` (`run.py:46`) imported, never called in `run.py`. `SeedRegistry.analysis_seed()/to_dict()` unused. *Min fix:* remove unused imports/members.

**W5 — Dead subsystems in the canonical `core/` tree (pre-existing, committed `a41b5c4`; not introduced by this delivery, but the new work routed around them).** `core/emergence/null_referenced_test.py` and `core/controls/{fixed_capacity,random_growth,shuffled_input}.py` (`FixedCapacityControl`/`RandomGrowthControl`/`ShuffledInputControl`) have **zero** importers — E0 implements C1/C2/C3 inline in `run.py`. Per §1 rule 2 ("no subsystem without a pre-registered experiment that requires it") these are archive/delete candidates. **Not charged to this delivery.**

**W6 — [REJECTED] constructs sitting in the canonical tree (pre-existing, committed `a41b5c4`).** `core/measurement/metrics.py:73 cognitive_energy` computes `E=λH+μS+νA` with `ENERGY_EXHAUSTION=18.0`; `experiments/metrics.py:21-32` carries `LAMBDA/MU/NU`, `ENERGY_EXHAUSTION=18.0`. These are §5-[REJECTED]. The E0 path does **not** import them (contained), so this is repository drift, not a live-path violation. Owner action per §9-DeepSeek: move to `archive/`. **Not charged to this delivery.**

---

### Required to clear Review #001
Fix **F1** (blocking). W1–W4 to be resolved in the same delivery. W5–W6 tracked as pre-existing drift for the §9-DeepSeek archive pass. Re-submit for Review #002.

---

*Awaiting next engineering delivery.*
