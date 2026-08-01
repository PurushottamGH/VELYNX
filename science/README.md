# Project P1 Scientific Infrastructure

- **Framework version:** 1.0.0
- **Established:** 2026-07-28
- **Owner:** P1 Scientific Operating System (SOS), Chief Scientist
- **Engineering boundary:** Claude Opus owns implementation; this directory owns scientific state, method, and evidence decisions
- **Governance status:** Adopted as the P1 scientific operating baseline. These records do not override `REPOSITORY_CONSTITUTION.md`; formal normative activation remains subject to repository governance while that governance is in force.

## Purpose

This directory is the permanent scientific operating manual for P1. It makes the research state cumulative, falsifiable, and recoverable. It does not specify software architecture.

## Documents

| Document | Primary responsibility |
|---|---|
| `01_SCIENTIFIC_CONSTITUTION.md` | Durable truth-seeking principles and scope boundaries |
| `02_HYPOTHESIS_REGISTRY.md` | Hypothesis schema, lifecycle, versioning, confidence, dependencies |
| `03_EXPERIMENT_REGISTRY.md` | Permanent experiment traceability and phase-scaled requirements |
| `04_SCIENTIFIC_KNOWLEDGE_BASE.md` | Knowledge ontology: facts, evidence, hypotheses, theories, speculation, unknowns |
| `05_ASSUMPTION_AND_UNCERTAINTY_REGISTRIES.md` | Assumption validation/retirement and uncertainty prioritization |
| `06_THEORY_REGISTRY.md` | Theory formation, comparison, revision, and replacement |
| `07_SCIENTIFIC_DECISION_SYSTEM.md` | Accept, reject, revise, split, merge, archive, and supersede decisions |
| `08_SCIENTIFIC_DEBT_FRAMEWORK.md` | Unresolved scientific weakness, risk, priority, blockers, and evidence needed |
| `09_RESEARCH_ROADMAP_24_MONTHS.md` | Evidence-based scientific milestones for August 2026–July 2028 |
| `10_KNOWLEDGE_EVOLUTION_ENGINE.md` | Post-experiment update rules, conflict resolution, and evidence accumulation |
| `11_LIVING_SCIENTIFIC_MODEL.md` | Current best scientific understanding of P1 |
| `REGISTRY_TEMPLATES.yaml` | Canonical human-readable record templates and controlled vocabularies |

## Authority and non-duplication

Scientific records decide what is known, unknown, supported, rejected, or worth testing. They do not decide code structure, interfaces, deployment, staffing, schedules, or implementation technique.

This directory already contains engineering-owned Python infrastructure (`__init__.py`, `registries.py`, `mechanisms/`, and related runtime components). The M1 operating manual neither modifies nor governs how those components execute. Its Markdown/YAML records govern scientific meaning and evidence state only. Any future path separation is an engineering decision.

Engineering tests establish implementation conformance. They become scientific evidence only when an experiment explicitly uses the tested behavior as an observation relevant to a hypothesis.

## Progressive rigor

- **Discovery:** cheap discriminating tests; exploratory labels; enough provenance to learn.
- **Validation:** fit-for-claim controls, fair comparisons, replication, effect sizes, uncertainty, reproducibility.
- **Publication:** complete communication and preservation of already validated results.

Publication requirements never gate discovery. Exploratory observations never silently become validated evidence.

## Record rules

1. IDs are permanent and never reused.
2. Records are append-only after a decision-bearing state is reached. Correction occurs by linked supersession.
3. Negative and ambiguous results are retained.
4. Status changes require a Scientific Decision record.
5. Confidence never changes without an evidence-linked rationale.
6. Scope never widens silently.
7. Every completed experiment updates at least one hypothesis, assumption, uncertainty, theory, debt item, or roadmap decision.
8. The governing question is: **What is the smallest experiment that would most reduce uncertainty?**

## Legacy integration

Existing files such as `theory/HYPOTHESIS_REGISTER.md`, `experiment_registry.yaml`, `PROGRAM_D_RESEARCH_STATE_v0.1.md`, and `governance/activation/RS-1_RESEARCH_STANDARD.draft.md` are source material, not silently replaced evidence. Their live claims must be migrated record-by-record with provenance and epistemic status. Contradictions remain visible until resolved by a Scientific Decision.
