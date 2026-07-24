# Repository Constitution: Project P1

This document defines the permanent repository organization, code layout rules, git workflows, and scientific preservation policies of Project P1. All developers and autonomous AI systems operating within this repository must adhere to this constitution.

---

## 1. Directory Purpose and Structure

The repository is organized into a clean, compartmentalized structure designed to support a scientific research program:

*   `framework/`
    *   **Purpose**: Single source of truth for reusable mathematical primitives and core scientific machinery.
    *   **Rules**: Contains the `core/` package and its subpackages (`predictors`, `emergence`, `mdl`, `measurement`, `controls`). All code must be stateless and modular, serializing state via explicit dicts.
*   `backend/`
    *   **Purpose**: The application and engineering layer.
    *   **Rules**: Contains replay engines, knowledge models, databases, persistence, and telemetry components. Research code must not depend on `backend/` packages directly, maintaining a strict scientific abstraction.
*   `frontend/`
    *   **Purpose**: The decoupled client web interface.
    *   **Rules**: A standalone React/Vite web application that communicates with the backend via APIs. Keeps frontend build configuration and node modules separated from the research framework.
*   `theory/`
    *   **Purpose**: Mathematical derivations, hypotheses registers, and scientific literature.
    *   **Rules**: Houses quantitative formulas, literature tracking, research decisions, and calibration preregistrations.
*   `experiments/`
    *   **Purpose**: Active and archived empirical validation runs.
    *   **Rules**: Contains experiment source code (e.g. `EXP0`, `EXP1`, `E0`), configuration specifications, benchmarks, and run scripts.
*   `evidence/`
    *   **Purpose**: Verification artifacts, ledgers, audit outputs, and trace logs.
    *   **Rules**: Holds proof files, compliance matrices, statistical analysis outputs, and run summaries. Large raw dumps must be git-ignored, with summaries committed alongside their hash provenance.
*   `audits/`
    *   **Purpose**: Code evaluations, dependency maps, and compliance checklists.
    *   **Rules**: Houses independent audits, code reviews, and tools targeting code quality or architectural checks.
*   `docs/`
    *   **Purpose**: Project documentation and sprint planning.
    *   **Rules**: Contains sprint retrospectives, guides, and migration documents.
*   `scripts/`
    *   **Purpose**: Reusable utility scripts.
    *   **Rules**: Scripts for installation check, graph generation, registry verification, and setup helpers.
*   `tests/`
    *   **Purpose**: Automated verification test suites.
    *   **Rules**: Subdivided into `unit/` and `integration/` tests. Keeps regression and validation gates (such as `validation/regression.py`) under centralized test management.
*   `configs/`
    *   **Purpose**: Shared runtime configurations.
    *   **Rules**: Stores configuration JSON/YAML templates used in experiments.
*   `data/`
    *   **Purpose**: Ground-truth datasets and static database templates.
*   `archive/`
    *   **Purpose**: Scientific vault for deprecated versions and inherited systems.
    *   **Rules**: Contains legacy code and snapshots from Programs A, B, and C to maintain historical reproducibility.
*   `worktrees/`
    *   **Purpose**: Git worktree workspace.
    *   **Rules**: Keeps concurrent workspace developments out of the main git directory path.
*   `p1/`
    *   **Purpose**: Bounded subtree for the P1 Research OS pilot — canonical Markdown records, methodology, specifications, tooling, templates, small reproducibility artifacts, disposable derived indexes, and transient transaction state.
    *   **Rules**: Governed by the approved P1 Research OS specification and Principal Investigator decisions, not by the VELYNX directory-placement rules in this section. P1 tooling must not depend on the VELYNX `backend/`, `frontend/`, runtime databases, remote APIs, or background services. P1 Research OS uses no database; the SQLite preservation rule in Section 5 applies only to VELYNX and legacy runtime components, not to `p1/`.

---

## 2. Naming Conventions

*   **Directories**: Lowercase with underscores (e.g. `framework/core`, `theory/preregistrations`).
*   **Python Files**: Lowercase with underscores (e.g. `cognitive_core.py`, `decision_policy.py`).
*   **Markdown Files**: Uppercase for main documents (e.g. `PROGRAM_D_CANONICAL.md`, `README.md`) and lowercase with underscores for support documents (e.g. `kill_criteria_validation.md`).
*   **Classes**: CamelCase (e.g. `DirichletMarkovPredictor`).
*   **Functions & Methods**: Lowercase with underscores (e.g. `should_grow`, `compute_nmi`).
*   **Constants**: Uppercase with underscores (e.g. `BITS_PER_PARAMETER`, `LAMBDA`, `MU`).

---

## 3. Code & Asset Placement Rules

*   **New Code**: Core mathematical changes go to `framework/core/`. Application features go to `backend/`. UI changes go to `frontend/`.
*   **New Experiments**: Must be placed in a subdirectory of `experiments/` (e.g., `experiments/EXP5/`) and preregistered in `theory/preregistrations/`.
*   **New Theory**: Hypotheses and mathematical specifications must be added to `theory/` or appended to `theory/HYPOTHESIS_REGISTER.md`.
*   **New Evidence**: Output results, metrics, and compliance logs must be placed in `evidence/`.

---

## 4. Root Directory Rules

*   The root directory must remain extremely clean.
*   Only the following files are permitted to reside directly in the root:
    *   `README.md`
    *   `REPOSITORY_CONSTITUTION.md`
    *   `RESEARCH_PROTOCOL.md`
    *   `pyproject.toml`
    *   `requirements.txt`
    *   `.gitignore`
    *   `.env.example`
*   No loose python scripts, markdown files, databases, or local run caches are allowed in the root.

---

## 5. Git Workflow & Archival Rules

*   **History Preservation**: All file moves and renames must be executed via `git mv` to preserve full revision history. Copy-and-delete operations are strictly forbidden.
*   **Secrets**: No credentials, private API keys, or cloud access files (e.g. `gcp-key.json.json`, `.env`) may be committed. They must be explicitly git-ignored.
*   **Archival Policy**: Legacy codebases (e.g., Programs A/B/C) and backup folders (e.g., `backend_backup_phase35`) must be moved inside `archive/` rather than deleted, to preserve historical reference and baseline regression capabilities.
*   **DB Preservation**: Local SQLite databases (`*.db`, `*.db-shm`, `*.db-wal`) must reside in the git-ignored `.velynx_data/` directory and are never committed to version control.

---

## 6. Forbidden Operations

*   **NO** raw secret keys or service accounts committed.
*   **NO** direct deletions of source code, experiments, or research documentation unless proven to be temporary/cache or duplicate empty folders.
*   **NO** modification of frozen scientific constants (such as `BITS_PER_PARAMETER = 1.0`) without explicit Scientific Auditor and Lead Architect approval.
