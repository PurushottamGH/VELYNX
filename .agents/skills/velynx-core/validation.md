# Validation

This document defines the scientific review workflow, the PASS/FAIL
rules, the experiment requirements, and the reproducibility requirements.
It is the closing reference for the skill; the subsystem documents feed
into it.

## 1. The binding handoff chain

Every change follows this chain. Stages are never skipped.

```
Architect -> Builder -> Reviewer -> ScientificAuditor -> ReleaseManager
```

- **Architect** - owns architecture, APIs, interfaces, module
  boundaries, dependency analysis. Never writes production code. Produces
  the design/contract that the Builder implements.
- **Builder** - owns implementation, tests, refactoring, bug fixes. Never
  changes scientific parameters. Implements to the Architect's contract.
- **Reviewer** - owns code review, determinism, maintainability,
  complexity, security, edge cases. Returns **PASS or FAIL only**.
- **ScientificAuditor** - owns preregistration, calibration, statistics,
  hypothesis validation, reproducibility, dimensional analysis. Returns
  **PASS or FAIL only**. Never writes production code.
- **ReleaseManager** - owns releases, manifests, changelogs, git tags,
  reproducibility reports. Never edits production code.

Supporting specialists, invoked off the main chain:

- **Debugger** - invoked on defect, nondeterminism, or reproducibility
  breaks. Performs root-cause analysis (telemetry, replay, SQLite
  debugging, profiling) and hands a **fix spec** back to the Builder. It
  never redesigns architecture.
- **ExperimentEngineer** - owns EXP-0, EXP-1, EXP-2, datasets, manifests,
  execution, reports. Runs experiments and hands **results** to the
  ScientificAuditor. Never changes hypotheses.
- **Documentation** - owns README, developer guides, architecture docs,
  API docs. Documentation updates ride alongside Builder changes and pass
  the Reviewer. Never changes scientific conclusions.

The VELYNX Director decomposes work, assigns tasks to these specialists,
and enforces the chain. The Director never writes production code and
never overrides a FAIL verdict.

## 2. PASS/FAIL rules

- **Nothing is released until Reviewer returns PASS**, ScientificAuditor
  returns PASS (where the scientific path is touched), and Documentation
  returns PASS.
- Reviewer and ScientificAuditor emit **PASS or FAIL only**. A FAIL
  carries the exact reasons; the work returns to the responsible agent
  with those reasons. The Director routes FAILs back - never overrides
  them.
- A change touches the **scientific path** if it modifies anything in
  `core/`, anything in `experiments/`, any preregistration or protected
  document, any frozen parameter or scientific constant, or any
  statistical test. Such a change requires ScientificAuditor PASS in
  addition to Reviewer PASS.
- A change that is purely application-layer (`backend/` product code
  with no scientific claim) requires Reviewer PASS and Documentation
  PASS; the ScientificAuditor is engaged only if a scientific claim is
  introduced or altered.
- The **RegressionGate** (`validation/regression.py`) is the CI
  enforcement point for the Freeze Rule: if any critical metric degrades
  beyond tolerance versus the baseline, `assert_no_regression` raises and
  blocks the change (see `testing.md`).

## 3. When each specialist is engaged (decision rules)

- Architecture changes -> **Architect**.
- Implementation, tests, refactoring, bug fixes -> **Builder**.
- Experiment execution, datasets, manifests, reports -> **ExperimentEngineer**.
- Defect, nondeterminism, reproducibility break -> **Debugger** (hands a
  fix spec to Builder).
- A scientific claim, preregistration, calibration, statistics,
  reproducibility, dimensional analysis -> **ScientificAuditor**.
- README, guides, architecture/API docs -> **Documentation**.
- Release, changelog, tag, reproducibility report -> **ReleaseManager**.

## 4. Experiment requirements

An experiment is not "code that runs"; it is a preregistered protocol.
Before any experiment may execute or ship a result, it must have:

1. **A preregistration document** stating the hypothesis, independent
   variables, dependent variables, null, kill criteria, and success
   criterion - written before implementation. Protected preregistrations
   are listed in `experiments.md` Section 7.
2. **A registry entry** in `experiment_registry.yaml` with name,
   hypothesis, status, location, description, and components.
3. **A frozen parameter block** in `parameter_registry.yaml` (value,
   location, role) and, where applicable, a `config.json` in the
   experiment directory.
4. **A leakage check** that runs before scoring and aborts on failure
   (see `experiments/E0/leakage_check.py`, `experiments/EXP0/leakage_check.py`).
5. **ScientificAuditor sign-off** on the protocol, the statistics, and
   the kill criteria before execution, and on the results before
   release.
6. **Reproducible execution** per Section 5.

Experiments whose status is `archived` (R1, R3F) or `[REJECTED]`
(EXP-3, EXP-4) must not be rebuilt or referenced as live experiments
(`experiment_registry.yaml`). New hypotheses are prohibited (canon
Section 1, rule 1) - only refinement, testing, or falsification of
inherited ones.

## 5. Reproducibility requirements

From `reproducibility.yaml`, every experiment must be reproducible from:

1. The source code at a pinned git commit.
2. The configuration files in `infra/config/` (e.g. `baseline.json`,
   `noisy.json`, `simple.json`).
3. The parameter registry (`parameter_registry.yaml`).
4. The dependency and environment specification (`requirements.txt`,
   Python >= 3.11).

Per-experiment reproducibility protocol:

1. `git checkout <experiment-commit>`.
2. `pip install -r requirements.txt`.
3. `cp infra/config/<experiment-config>.json infra/config/active.json`.
4. `python experiments/<EXPERIMENT>/run.py`.
5. `python experiments/<EXPERIMENT>/analysis.py`.

Hard requirements:

- **Seeds.** Every randomized path takes an explicit seed. Default
  benchmark seed is 42 (`BENCHMARK_SEED`). E0 uses `seed 42` and
  `env_seed 101`; EXP-0 uses shuffle seed 1 and a fixed bootstrap CI seed
  of 0. Canonical predictors use `numpy.random.RandomState`.
- **Determinism tests must pass.** Replay identity within `1e-10`
  (`test_replay_engine_vitals_r3c.py`) and read-only non-mutation
  (`research/tests/test_read_only_nonmutation.py`) are load-bearing
  (see `testing.md`, `replay.md`).
- **Regression gate.** `validation/regression.py` must report no
  critical regression versus baseline. `DEFAULT_TOLERANCE = 0.05`.
- **Test gate.** `pytest tests/ -m "not slow"` must be 100% green on the
  pinned commit. Run `python benchmark.py` for the benchmark check.
- **No committed databases.** `*.db`, `*.db-wal`, `*.db-shm` are
  git-ignored (see `sqlite.md`).
- **File moves use `git mv`** so `git log --follow` preserves history.

Known non-reproducibility factors (must be controlled, not ignored): LLM
API responses vary by model version and temperature (pin the model in
config); soul-graph Hebbian updates depend on query order (deterministic
in replay); web search results depend on external API availability (mock
for unit tests).

## 6. Protected documents and frozen constants

Never modify without explicit instruction, and never without
ScientificAuditor approval (see `experiments.md`, `coding.md`):

- `PROGRAM_D_CANONICAL.md`, `HYPOTHESIS_REGISTER.md`,
  `EXP1_PREREGISTRATION.md`, `experiments/EXP0/EXP0_PREREGISTRATION.md`,
  `F_A_TRIGGER_FIX_PREREGISTRATION.md`, `SPRINT_1.3_PREREGISTRATION.md`.
- Experiment thresholds (`ECE < 0.10`, McNemar `p <= 0.01`, hit-rate drop
  `>= 0.40`, E0 margin `0.05`).
- Calibration bins (4 equal-width bins) and tier mappings
  (UNKNOWN/DEBATED/PROBABLE/CERTAIN -> 0.125/0.375/0.625/0.875).
- Statistical tests (McNemar exact, Holm-Bonferroni, tier-independence
  test at `alpha 0.05`).
- Scientific constants (`BITS_PER_PARAMETER = 1.0`; the derived
  `lambda_model = k*b + n*log2(N)`; the F-A corrected marginal cost
  `b + log2(N)`).

## 7. Epistemic discipline

From PROGRAM_D_CANONICAL.md Section 0, every scientific claim is tagged:

- `[FACT]` - mechanically verified against code, empirical logs, or
  mathematical derivation. Provenance cited.
- `[HYPOTHESIS]` - falsifiable, with a pre-registered null and a wired
  kill criterion.
- `[SPECULATION]` - untested. **Prohibited in any load-bearing mechanism
  or execution path.** Test or delete.
- `[REJECTED]` - empirically falsified or superseded. Must not appear in
  any live mechanism.

Reviewers and the ScientificAuditor enforce these tags. A `[SPECULATION]`
claim cannot become load-bearing; a `[REJECTED]` mechanism cannot be
reintroduced (see `coding.md` Section 11 for the full rejected list).

## 8. Completion criteria

A change is complete when all of the following hold:

- The responsible specialist has returned PASS (or the work has been
  routed back on FAIL and re-done).
- `pytest tests/ -m "not slow"` is green on the pinned commit.
- The `RegressionGate` reports no critical regression.
- Where the scientific path was touched, the ScientificAuditor has
  returned PASS and no protected document or frozen constant was changed
  without approval.
- Documentation has returned PASS.
- The ReleaseManager has produced the manifest/reproducibility report
  for the release.

## 9. What is not present

- There is no automated CI configuration committed in the repo for the
  review workflow; `reproducibility.yaml` notes "GitHub Actions
  (configured separately)". The PASS/FAIL regime is enforced by the
  specialist agents and the RegressionGate, not by a hosted pipeline in
  this repository.
- There is no separate "approval" database; verdicts are returned by
  agents in their final message and recorded in the release
  manifest/reproducibility report by the ReleaseManager.
- The ScientificAuditor does not write production code and does not
  change hypotheses; it only audits.