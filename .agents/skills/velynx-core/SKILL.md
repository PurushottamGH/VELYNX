---
name: velynx-core
description: VELYNX repository guide. Use when touching the VELYNX deterministic neurosymbolic cognitive architecture - the core scientific primitives (core/), the backend application layer, experiments (EXP0/EXP1/E0), replay engine, ontology, identity, telemetry, SQLite persistence, validation, or scientific review. Covers module boundaries, frozen parameters, and protected documents. Use ONLY for VELYNX work; not for unrelated Python or TypeScript projects.
---

# VELYNX Core

This skill orients an agent inside the VELYNX repository. It is a navigation
layer, not a substitute for reading the code. Every statement below is
derived from the repository; where a subsystem named by the project does not
exist as live code, that is stated explicitly rather than fabricated.

## Project overview

VELYNX is a deterministic neurosymbolic cognitive architecture organized as
**Program D** - an audit-and-falsification protocol over inherited Programs
A/B/C. It optimizes for truth, not elegance. The binding priority order under
trade-off is (PROGRAM_D_CANONICAL.md Section 1):

    scientific correctness > experiment reproducibility > code simplicity > performance > features

The repository enforces three constitutional rules that shape every
engineering decision:

1. No new hypotheses. Only refine, test, or falsify inherited ones.
2. No subsystem without a pre-registered experiment that requires it. If
   nothing in {EXP-0, EXP-1, EXP-2, E0} needs it, it is not built - it is
   archived.
3. If a mechanism cannot be operationally distinguished from a null/random
   baseline, it is a delete candidate, not a feature.

Prohibited in any live name or claim: anthropomorphism (mind/soul/belief/
understanding/curiosity), designer-injection sold as emergence, novelty
inflation of MDL/ECE/SSL, and unit-incommensurate mathematics.

## When to use this skill

Use this skill for ANY task that touches the VELYNX repository, including:

- Reading or modifying code under `core/`, `experiments/`, `validation/`,
  `research/`, or `backend/`.
- Running or reasoning about experiments EXP0, EXP1, E0, and the
  archived/rejected EXP2-EXP4, R1, R3F.
- Touching the Replay Engine, Predictive Processing, Ontology, Identity,
  Telemetry, or SQLite subsystems.
- Scientific review, reproducibility, or release work.
- Questions about frozen parameters, protected documents, or architectural
  boundaries.

Do NOT use this skill for unrelated Python or TypeScript projects. It
documents VELYNX only.

## Repository overview

VELYNX has a **dual-core** structure (see `repository_v2.md` and
`reduction/program_d_migration_plan.md`). The build (`pyproject.toml`) ships
only the scientific packages: `core*`, `experiments*`, `validation*`,
`benchmarks*`, `scripts*`. The `backend/` application layer is excluded from
the distribution.

| Path          | Role                                                                 | Status                                           |
|---------------|----------------------------------------------------------------------|--------------------------------------------------|
| `core/`       | Canonical scientific primitives (single source of truth)             | Active research core                             |
| `experiments/`| Experiment framework (EXP0, EXP1, E0 + stubs)                        | Active                                           |
| `validation/` | Validation framework, regression gate                                | Active                                           |
| `research/`   | Side-effect-free harness wrapping the backend ReplayEngine           | Active (study layer)                             |
| `backend/`    | Application/product layer: replay, ontology, identity, telemetry, DB | Engineering, "not the research center" (canon 2) |
| `tests/`      | unit / integration / EXP1 / fixtures                                 | Active                                           |
| `velynx_core/`| Legacy package                                                        | Empty (migrated to `core/`)                      |
| `src/`        | TypeScript entry (`index.ts` only)                                   | Minimal                                          |
| `configs/`, `infra/` | Runtime configuration, reproducibility config                | Active                                           |

`core/` is documented in its `__init__.py` as the "Single source of truth for
all reusable scientific machinery" with five subpackages: `predictors`,
`emergence`, `mdl`, `measurement`, `controls`. These implement the five
canonical mathematical primitives of PROGRAM_D_CANONICAL.md Section 5:
`x_t`, `P_theta`, `L`, `G`, `M`.

## Subsystem index

Each subsystem has a dedicated companion document in this folder. Read the
relevant one before editing.

| Subsystem               | Lives in                                  | Document          |
|-------------------------|-------------------------------------------|-------------------|
| Architecture & boundaries | whole repo                              | `architecture.md` |
| Coding conventions       | whole repo                              | `coding.md`       |
| Predictive processing    | `core/predictors`, `core/measurement`, `core/mdl` | `prediction.md` |
| Replay engine            | `backend/cognition/replay_engine.py` + `research/` | `replay.md`    |
| Ontology                 | `backend/knowledge/`                     | `ontology.md`     |
| Identity                 | `backend/self_model/`                     | `identity.md`     |
| Telemetry                | `backend/simulation/`, `backend/memory/`, `backend/ops/` | `telemetry.md` |
| SQLite persistence       | `backend/memory/_sqlite.py`              | `sqlite.md`       |
| Experiments              | `experiments/`                            | `experiments.md`  |
| Testing                  | `tests/`, `validation/`, `research/tests/` | `testing.md`     |
| Scientific validation    | review workflow + reproducibility         | `validation.md`   |

**Important duality.** The Replay Engine, Ontology, Identity, Telemetry, and
SQLite subsystems all live in `backend/`, the application layer. The canon
(PROGRAM_D_CANONICAL.md Section 5) marks several of these `[REJECTED]` as
load-bearing *science* (the self-model, the hand-authored ontology, the soul
concepts). They remain present as *engineering* for the Program A product.
Each companion document states this status explicitly. The canonical
science lives in `core/` and contains none of them.

## Workflow

Every change follows the binding handoff chain (see `validation.md` for the
full PASS/FAIL rules):

    Architect -> Builder -> Reviewer -> ScientificAuditor -> ReleaseManager

- The Debugger is invoked on defect, nondeterminism, or reproducibility
  breaks, and hands a fix spec back to Builder.
- The ExperimentEngineer runs experiments and hands results to the
  ScientificAuditor.
- Documentation updates ride alongside Builder changes and pass Reviewer.
- Nothing is released until Reviewer returns PASS, ScientificAuditor returns
  PASS (where the scientific path is touched), and Documentation returns PASS.
- When a specialist returns FAIL, the work returns to the responsible agent
  with the exact reasons. Directors never override a FAIL verdict.

## Protected documents and frozen constants

Never modify without explicit instruction, and never without Scientific
Auditor approval:

- `PROGRAM_D_CANONICAL.md` - the single source of truth.
- `EXP1_PREREGISTRATION.md` - the H1 calibration gate.
- `HYPOTHESIS_REGISTER.md` - H*, H1, H2 (and H3, rejected).
- `experiments/EXP0/EXP0_PREREGISTRATION.md`
- `F_A_TRIGGER_FIX_PREREGISTRATION.md`
- `SPRINT_1.3_PREREGISTRATION.md`

Frozen, non-tunable scientific constants (see `experiments.md` and
`parameter_registry.yaml`):

- `BITS_PER_PARAMETER b = 1.0` - a scientific constant, not a hyperparameter.
- `lambda_model = k*b + n*log2(N)` - derived, not configurable.
- ECE pass gate `< 0.10` (EXP-1); four locked tiers
  UNKNOWN/DEBATED/PROBABLE/CERTAIN -> 0.125/0.375/0.625/0.875.
- E0 margin for the emergence statistic `M`: `0.05` above the shuffled null.

Never change experiment thresholds, calibration bins, tier mappings,
statistical tests, or scientific constants without Scientific Auditor
approval.

## Document index

1. `architecture.md` - repository layout, module ownership, dependency
   boundaries, extension points.
2. `coding.md` - naming, typing, error handling, logging, testing
   expectations, refactoring rules, forbidden modifications.
3. `prediction.md` - the canonical predictive-processing primitives
   (`P_theta`, proper scoring `L`, MDL growth `G`).
4. `replay.md` - the backend ReplayEngine and the `research/` study harness.
5. `ontology.md` - the backend world-model ontology and its canonical status.
6. `identity.md` - the backend self-model/identity store and its persistence.
7. `telemetry.md` - non-blocking telemetry invariant across subsystems.
8. `sqlite.md` - the shared SQLite connection helper, PRAGMAs, DB inventory.
9. `experiments.md` - EXP0/EXP1/EXP2/E0, preregistrations, frozen parameters.
10. `testing.md` - pytest layout, markers, determinism and regression tests.
11. `validation.md` - the scientific review workflow and reproducibility rules.

## References (canonical, in the repository root)

- `PROGRAM_D_CANONICAL.md` - single source of truth.
- `EXP1_PREREGISTRATION.md`, `HYPOTHESIS_REGISTER.md` - preregistrations.
- `experiment_registry.yaml`, `parameter_registry.yaml`, `reproducibility.yaml`
- `pyproject.toml`, `requirements.txt` - build and dependency surface.
- `repository_v2.md`, `reduction/program_d_migration_plan.md` - the dual-core
  migration record.