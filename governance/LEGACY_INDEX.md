# Legacy Index

- **Status:** Draft (generated). Becomes the adoption-revision index when committed in change D.
- **Scope:** Every version-controlled artifact not activated in `GOVERNANCE_REGISTRY.yaml`
- **Responsibility:** Navigation. Identify Legacy artifacts and the basis of their classification
- **Authority source:** None. An index under section 11; it imposes no requirement and strips no authority.
- **Generated:** 2026-07-25T21:37+05:30 at revision `66e3e2aa1f5ac3df4d822c8c8f484269766beb47`
- **Generator:** `scripts/governance/generate_legacy_index.py`

## 1. Basis

Section 14: "At adoption, every existing Normative artifact not activated in the Governance Registry becomes Legacy and has no normative authority. A Legacy artifact MUST satisfy Section 4 before later activation."

Section 4 paragraph 5: Legacy content "MUST remain distinguishable from Active requirements."

Classification follows automatically from the Registry. This index records it so a reader need not derive it, and marks where a banner is required because the artifact would otherwise read as Active.

## 2. What is Active

`GOVERNANCE_REGISTRY.yaml` is the only answer. At adoption the Active set is **`REPOSITORY_CONSTITUTION.md` and nothing else** (`active_domain_standards: []`). Everything listed below, and everything not listed, is Legacy or non-normative.

## 3. Tier 1 — moved and bannered

`Current path` is where the banner is verified. Until change D moves the file it is the original path; afterwards it is the destination. The check resolves the current path first, then the original, and reports an entry that resolves to neither as **not verified** rather than skipping it — otherwise the moves would silently remove the Tier-1 files from banner verification.

The moving commit is deliberately not recorded here. It is the revision that contains this index, so naming it inside the index would be self-referential; `git log --follow <current path>` recovers it after the fact.

| Original path | Current path | Disposition | What it used to assert |
|---|---|---|---|
| `theory/PROGRAM_D_CONSTITUTION.md` | `archive/legacy_normative/PROGRAM_D_CONSTITUTION.md` | archive/legacy_normative/ | titled as a constitution; asserted program-wide authority |
| `PROGRAM_D_CANONICAL.md` | `archive/legacy_normative/PROGRAM_D_CANONICAL.md` | archive/legacy_normative/ | asserted canonical status for Program D content |
| `PROGRAM_D_MASTER_ROADMAP.md` | `archive/legacy_normative/PROGRAM_D_MASTER_ROADMAP.md` | archive/legacy_normative/ | asserted frozen scope and sequencing |
| `PROGRAM_D_RESEARCH_STATE_v0.1.md` | `archive/legacy_normative/PROGRAM_D_RESEARCH_STATE_v0.1.md` | archive/legacy_normative/ | asserted current research state as settled |
| `RESEARCH_PROTOCOL.md` | `archive/legacy_normative/RESEARCH_PROTOCOL.md` | archive/legacy_normative/ | read as the governing research procedure |
| `audits/CONSTITUTION_COMPLIANCE.md` | `archive/legacy_normative/CONSTITUTION_COMPLIANCE.md` | archive/legacy_normative/ | asserted compliance against a superseded constitution |
| `p1/specifications/milestone-1-gpt56.md` | `p1/specifications/milestone-1-gpt56.md` | (stays in place) | imposes PI-003/PI-004/PI-005; imported by p1/tooling, so moving it breaks working code for no compliance gain |

<!-- TIER1_BEGIN -->
- `theory/PROGRAM_D_CONSTITUTION.md` -> `archive/legacy_normative/PROGRAM_D_CONSTITUTION.md`
- `PROGRAM_D_CANONICAL.md` -> `archive/legacy_normative/PROGRAM_D_CANONICAL.md`
- `PROGRAM_D_MASTER_ROADMAP.md` -> `archive/legacy_normative/PROGRAM_D_MASTER_ROADMAP.md`
- `PROGRAM_D_RESEARCH_STATE_v0.1.md` -> `archive/legacy_normative/PROGRAM_D_RESEARCH_STATE_v0.1.md`
- `RESEARCH_PROTOCOL.md` -> `archive/legacy_normative/RESEARCH_PROTOCOL.md`
- `audits/CONSTITUTION_COMPLIANCE.md` -> `archive/legacy_normative/CONSTITUTION_COMPLIANCE.md`
- `p1/specifications/milestone-1-gpt56.md` -> `p1/specifications/milestone-1-gpt56.md`
<!-- TIER1_END -->

## 4. Tier 2 — banner required, in place

35 artifacts in `theory/`, `experiments/`, and `p1/` that either assert authority or frozenness, or impose requirements with a normative modal (MUST, SHALL, REQUIRED, SHOULD) — that is, artifacts a reader could take as Active. Descriptive prose in the same directories falls to the Tier-3 rule and needs no banner. The count column is lexeme matches; it indicates how strongly the text reads as Active and is not a severity score.

<!-- BANNER_REQUIRED_BEGIN -->
- `theory/preregistrations/PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md` (84)
- `experiments/specs/EXP1_DATASET_SPEC.md` (41)
- `theory/preregistrations/EXP1_PREREGISTRATION.md` (23)
- `p1/architecture_decisions/v0.1.0-release-gate.md` (17)
- `theory/governance/RESEARCH_DIRECTOR_DECISION.md` (12)
- `theory/preregistrations/PROGRAM_A_SEM_S0_PREREGISTRATION.md` (10)
- `theory/PROGRAM_D_SPECIFICATION.md` (8)
- `theory/MEASUREMENT_VALIDITY.md` (6)
- `theory/foundation/program_d_scientific_foundation_v0.1.md` (6)
- `experiments/EXP0/EXP0_PROTOCOL.md` (5)
- `theory/PHENOMENON_REGISTRY.md` (5)
- `theory/governance/PA2_ACCEPTANCE_DECISION.md` (5)
- `p1/architecture_decisions/milestone-1.1-acceptance-review.md` (4)
- `experiments/EXP0/EXP0_IMPLEMENTATION_PLAN.md` (3)
- `theory/EXPERIMENTAL_FRAMEWORK.md` (3)
- `experiments/EXP0/EXP0_DIRECTORY_STRUCTURE.md` (2)
- `experiments/EXP0/EXP0_PREREGISTRATION.md` (2)
- `experiments/EXP0/EXP0_RUNBOOK.md` (2)
- `theory/HYPOTHESIS_DISCRIMINATION_MATRIX.md` (2)
- `theory/SCIENTIFIC_EXECUTION_SPEC.md` (2)
- `theory/THEORY_NOTEBOOK_v3.md` (2)
- `theory/parameter_atlas.md` (2)
- `theory/preregistrations/EXPERIMENT_ZERO_PREREGISTRATION.md` (2)
- `experiments/E0/E0_FINAL_IMPLEMENTATION_REPORT.md` (1)
- `experiments/E0/E0_IMPLEMENTATION_REPORT.md` (1)
- `experiments/specs/EXPERIMENT_CONFIGURATION_SCHEMA.md` (1)
- `experiments/specs/EXPERIMENT_PROTOCOLS.md` (1)
- `experiments/specs/REFERENCE_DATA_SPEC.md` (1)
- `p1/methodology/STATUS_LIFECYCLE.md` (1)
- `theory/THEORY_LANDSCAPE.md` (1)
- `theory/foundation/architecture/DEPENDENCY_GRAPH.md` (1)
- `theory/preregistrations/F_A_TRIGGER_FIX_PREREGISTRATION.md` (1)
- `theory/preregistrations/SPRINT_1.3_PREREGISTRATION.md` (1)
- `experiments/specs/EXPERIMENT_INTERFACE_SPEC.md` (0)
- `theory/VELYNX_Metacognitive_Loop.md` (0)
<!-- BANNER_REQUIRED_END -->

### 4.1 Preregistration-shaped artifacts

These require the second banner paragraph in `governance/activation/04_LEGACY_DISPOSITION.md` section 3. None is a Registered protocol: section 2 requires the registration transition to have occurred before governed execution began, and section 13 paragraph 4 forbids supplying it retroactively.

- `theory/preregistrations/PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`
- `theory/preregistrations/EXP1_PREREGISTRATION.md`
- `theory/preregistrations/PROGRAM_A_SEM_S0_PREREGISTRATION.md`
- `experiments/EXP0/EXP0_PREREGISTRATION.md`
- `theory/preregistrations/EXPERIMENT_ZERO_PREREGISTRATION.md`
- `theory/preregistrations/F_A_TRIGGER_FIX_PREREGISTRATION.md`
- `theory/preregistrations/SPRINT_1.3_PREREGISTRATION.md`

## 5. Tier 3 — directory rules

| Prefix | Statement |
|---|---|
| `archive/` | Inherited Programs A/B/C material and legacy documents. Retained for history; nothing depends on it. |
| `docs/` | Documentation, sprint planning, migrations, and model-authored audits. Descriptive; imposes nothing. |
| `audits/` | Audit and checklist reports. Under section 3 paragraph 5 an audit reports observations and MUST NOT create the requirement it audits. |
| `evidence/` | Verification artifacts, certifications, traces, ledgers. Certification language here confers no authority. |
| `artifacts/` | Nineteen exp_* execution outputs. Permanently exploratory working output: no Registered protocol preceded them (sections 2, 5 paragraph 3, 13 paragraph 4). |
| `research/` | Inherited research scaffolding and preregistration-shaped documents. Not Registered protocols. |
| `reviews/` | Review-shaped records. Section 4 paragraph 4 bars automation from supplying independent review; these do not satisfy section 13 paragraph 2. |
| `.agents/` | Agent and skill configuration. Several define reviewer or auditor roles for models; none can supply human authority or independent review (section 4 paragraph 4). |
| `.opencode/` | Agent configuration, as above. |
| `.commandcode/` | Agent configuration, as above. |
| `backend/constitution/` | Model-behaviour prompt files. The directory name collides with the Constitution and carries no governance meaning (section 11 paragraph 3). |

## 6. Completeness

**Method.** Tier 1 is a hand-curated list of artifacts that describe themselves as constitutional or canonical in a live path. Tier 2 is every `.md` file under `theory/`, `experiments/`, and `p1/`, ranked by lexeme matches. Tier 3 is stated by directory rather than enumerated.

**Scope.** Version-controlled Markdown only, at the revision above.

**Known false negative.** A Normative artifact that imposes requirements without declaring authority and without matching the lexeme list is not detected — for example a YAML registry, a JSON schema, or a plainly-worded specification. `experiment_registry.yaml`, `parameter_registry.yaml`, and `reproducibility.yaml` are in that category and are Legacy on the same section 14 basis even though the scan does not surface them. This index therefore does not claim completeness, and a conformance claim citing it MUST carry that limitation (section 12 paragraph 3).

**Not mechanically decidable.** Whether a document *reads* as authoritative is manual procedure `P-L1` in `04_LEGACY_DISPOSITION.md` section 5. A lexeme count does not answer it.

## 7. Reactivation

A Legacy artifact carries force again only by satisfying section 4: complete status/scope/responsibility/authority fields, a non-overlapping Registry jurisdiction, approval by a Registry-listed authority permitted for that jurisdiction, and an Independent reviewer attestation under section 13 — in one atomic change. Nothing here is activated by being read, cited, or relied upon.
