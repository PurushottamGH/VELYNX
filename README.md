# VELYNX — Repository Index & Map

This repository houses the **VELYNX** cognitive architecture. It is organized as a research-first repository with clear separation between mathematical core, engineering application, experiments, and scientific evidence.

---

## 1. Directory Structure

The repository is organized according to the [Repository Constitution](file:///C:/Users/Purushottam/Documents/P1/REPOSITORY_CONSTITUTION.md), which governs repository-wide authority boundaries and epistemic invariants. Directory purposes below are descriptive; enforceable domain boundaries belong in active scoped standards registered in `GOVERNANCE_REGISTRY.yaml`.

*   [framework/](file:///C:/Users/Purushottam/Documents/P1/framework/)
    *   **Purpose**: Single source of truth for reusable mathematical primitives and core scientific machinery.
    *   **Contents**: Stateless predictors, emergence estimators, MDL calculations, proper scoring metrics, and null controls under [framework/core/](file:///C:/Users/Purushottam/Documents/P1/framework/core/).
*   [backend/](file:///C:/Users/Purushottam/Documents/P1/backend/)
    *   **Purpose**: The application and engineering layer.
    *   **Contents**: Replay engines, knowledge models, database persistence, and telemetry components.
*   [frontend/](file:///C:/Users/Purushottam/Documents/P1/frontend/)
    *   **Purpose**: Standalone client web interface (React/Vite app).
*   [theory/](file:///C:/Users/Purushottam/Documents/P1/theory/)
    *   **Purpose**: Hypotheses register, mathematical specifications, literature, and foundations.
    *   **Contents**: [SCIENTIFIC_EXECUTION_SPEC.md](file:///C:/Users/Purushottam/Documents/P1/theory/SCIENTIFIC_EXECUTION_SPEC.md), [STATISTICAL_ANALYSIS_SPEC.md](file:///C:/Users/Purushottam/Documents/P1/theory/STATISTICAL_ANALYSIS_SPEC.md), hypotheses registers, and assumption ledgers.
*   [experiments/](file:///C:/Users/Purushottam/Documents/P1/experiments/)
    *   **Purpose**: Active empirical validation runs.
    *   **Contents**: [experiments/E0/](file:///C:/Users/Purushottam/Documents/P1/experiments/E0/) (central H\* test), [experiments/EXP0/](file:///C:/Users/Purushottam/Documents/P1/experiments/EXP0/) (precondition), [experiments/EXP1/](file:///C:/Users/Purushottam/Documents/P1/experiments/EXP1/) (calibration gate), and experiment configuration schemas under [experiments/specs/](file:///C:/Users/Purushottam/Documents/P1/experiments/specs/).
*   [evidence/](file:///C:/Users/Purushottam/Documents/P1/evidence/)
    *   **Purpose**: Verification artifacts, audit ledgers, compliance matrices, and trace logs.
    *   **Contents**: [evidence/certifications/](file:///C:/Users/Purushottam/Documents/P1/evidence/certifications/) (scientific, metric, and reproducibility certifications) and [evidence/reports/](file:///C:/Users/Purushottam/Documents/P1/evidence/reports/) (implementation audits and dataset reconciliations).
*   [tests/](file:///C:/Users/Purushottam/Documents/P1/tests/)
    *   **Purpose**: Automated verification test suites.
    *   **Contents**: Centralized [tests/unit/](file:///C:/Users/Purushottam/Documents/P1/tests/unit/), [tests/integration/](file:///C:/Users/Purushottam/Documents/P1/tests/integration/), and regression tests.
*   [docs/](file:///C:/Users/Purushottam/Documents/P1/docs/)
    *   **Purpose**: Project documentation, sprint planning, and migration roadmaps.
    *   **Contents**: Sprint reports, execution order guides, and historical reduction plans under [docs/plans/](file:///C:/Users/Purushottam/Documents/P1/docs/plans/).
*   [scripts/](file:///C:/Users/Purushottam/Documents/P1/scripts/)
    *   **Purpose**: Reusable utility scripts.
    *   **Contents**: CLI execution wrappers, graph generators, and build validation tools.
*   [archive/](file:///C:/Users/Purushottam/Documents/P1/archive/)
    *   **Purpose**: Scientific vault for deprecated versions and inherited systems (Programs A/B/C code and legacy docs).

---

## 2. Root Governance and Metadata

The root contains repository-wide governance, indexes, registries, and cross-tool configuration. This section is descriptive, not a constitutional allowlist. In particular:

*   [README.md](file:///C:/Users/Purushottam/Documents/P1/README.md) — Repository map.
*   [REPOSITORY_CONSTITUTION.md](file:///C:/Users/Purushottam/Documents/P1/REPOSITORY_CONSTITUTION.md) — Repository-wide authority boundaries and epistemic invariants.
*   `GOVERNANCE_REGISTRY.yaml` — Status, jurisdiction, and authority registry for active normative artifacts.
*   [RESEARCH_PROTOCOL.md](file:///C:/Users/Purushottam/Documents/P1/RESEARCH_PROTOCOL.md) and `PROGRAM_D_*.md` — Program D domain material subject to constitutional registration and scope.
*   `experiment_registry.yaml`, `parameter_registry.yaml`, and `reproducibility.yaml` — Scientific registries and reproducibility metadata.
*   `pyproject.toml`, `requirements.txt`, `package.json`, `tsconfig.json`, lockfiles, and container files — Build and tool configuration.
*   [.gitignore](file:///C:/Users/Purushottam/Documents/P1/.gitignore) and [.env.example](file:///C:/Users/Purushottam/Documents/P1/.env.example) — Version-control exclusions and a non-secret environment template.

A root location does not grant an artifact authority. Normative authority exists only as specified by the Constitution and Governance Registry.
