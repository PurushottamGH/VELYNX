# VELYNX — Repository Index & Map

This repository houses the **VELYNX** cognitive architecture. It is organized as a research-first repository with clear separation between mathematical core, engineering application, experiments, and scientific evidence.

---

## 1. Directory Structure

The repository is organized according to the [Repository Constitution](file:///C:/Users/Purushottam/Documents/P1/REPOSITORY_CONSTITUTION.md):

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

## 2. Root Files

To keep the root clean, only essential project governance and metadata files are permitted:
*   [README.md](file:///C:/Users/Purushottam/Documents/P1/README.md) — This directory map.
*   [REPOSITORY_CONSTITUTION.md](file:///C:/Users/Purushottam/Documents/P1/REPOSITORY_CONSTITUTION.md) — Operational guidelines and design policies.
*   [RESEARCH_PROTOCOL.md](file:///C:/Users/Purushottam/Documents/P1/RESEARCH_PROTOCOL.md) — Peer review and reproducibility workflows.
*   [pyproject.toml](file:///C:/Users/Purushottam/Documents/P1/pyproject.toml) — Package configuration, dependencies, and pytest options.
*   [requirements.txt](file:///C:/Users/Purushottam/Documents/P1/requirements.txt) — Python dependencies list.
*   [.gitignore](file:///C:/Users/Purushottam/Documents/P1/.gitignore) — Version control exclusion patterns.
*   [.env.example](file:///C:/Users/Purushottam/Documents/P1/.env.example) — Configuration template for environment variables.
*   [docker-compose.yml](file:///C:/Users/Purushottam/Documents/P1/docker-compose.yml) — Container setup.
*   [package.json](file:///C:/Users/Purushottam/Documents/P1/package.json) — Frontend package settings.
*   [tsconfig.json](file:///C:/Users/Purushottam/Documents/P1/tsconfig.json) — TypeScript config.
*   [skills-lock.json](file:///C:/Users/Purushottam/Documents/P1/skills-lock.json) — Agent skill registry configuration.
