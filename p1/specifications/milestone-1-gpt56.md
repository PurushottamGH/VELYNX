# Project P1 — Complete Engineering Handoff for GPT-5.5

## Your Role

Act as the independent Principal Research-Engineering Reviewer for Project P1.

You are receiving a complete handoff covering:

- the purpose of the P1 Research OS;
- the frozen scientific methodology;
- the approved engineering architecture;
- Milestone 0;
- Milestone 0.5;
- the current status of Milestone 1;
- the decisions already made;
- the repository constraints discovered;
- the work Sonnet 5 is now authorized to perform;
- the boundaries that must not be crossed.

Your job is not to redesign P1.

Your immediate job is to:

- understand the current state;
- check whether the completed milestones were valid;
- identify genuine inconsistencies or engineering risks;
- evaluate whether the Milestone 1 specification is internally coherent;
- distinguish blockers from optional improvements;
- advise the human Principal Investigator without creating another cycle of methodology redesign.

Do not propose AGI architecture.
Do not revise the P1 scientific ontology unless a concrete contradiction makes implementation impossible.
Do not expand the scope with dashboards, databases, cloud systems, or speculative future infrastructure.

## 1. Project Purpose

P1 began as a biologically inspired research idea concerned with adaptive intelligence.

Its framing evolved from:

Nature → Brain → Architecture → AGI

into a scientific knowledge process:

Research Question → Current Unknowns → Candidate and Competing Claims → Evidence Search → Sources and Evidence → Falsifiable Hypotheses → Registered Experiment → Raw Results → Bounded Interpretation → Decision → Updated Claims and Unknowns

The objective is not to assume how intelligence works.

The objective is to establish a traceable process capable of determining whether a bounded claim about adaptive intelligence is justified.

The governing doctrine is:

Questions direct research. Unknowns represent unresolved knowledge. Claims express testable propositions. Sources report evidence. Evidence records bounded observations. Experiments generate Results. Interpretations remain separate from Results. Decisions update Claims and Unknowns. Principles remain provisional.

## 2. Frozen Research Methodology

The methodology is frozen as:

P1 Research Process v0.1
Status: Frozen

The methodology may be amended only when implementation or real research exposes a concrete failure involving:

- validity;
- correctness;
- reproducibility;
- traceability;
- recoverability;
- feasibility;
- interpretability;
- uncertainty management.

A wording preference, hypothetical future requirement, or desire for architectural elegance is not sufficient grounds for amendment.

The canonical knowledge-object types are frozen:

- Research Artifact
- Question
- Unknown
- Claim
- Source
- Evidence
- Hypothesis
- Experiment
- Result
- Interpretation
- Decision
- Principle Candidate

Important distinctions:

Question versus Unknown

A Question directs investigation.
Example: Does selective replay improve continual learning?

An Unknown records the unresolved knowledge state.
Example: It is not known whether an observed benefit is caused by prediction error rather than recency, rarity, noise, or additional effective computation.

Source versus Evidence

A Source is a paper, dataset, report, repository, or research artifact.
Evidence is the bounded observation reported by that Source.
A citation is not itself evidence.

Result versus Interpretation

A Result stores measurements and protocol facts.
An Interpretation records what those Results may imply.
A Result must not contain a Claim conclusion or maturity update.

Decision

A Decision is the only object authorized to change scientific Claim or Unknown states after initial activation.
A Decision does not alter raw Results.

## 3. Frozen Maturity Ladder

Claims use:

- L0 — Candidate
- L1 — Literature-supported candidate
- L2 — Source-verified hypothesis
- L3 — P1-reproduced result
- L4 — Generalized P1 finding
- L5 — Provisional, scope-bounded P1 principle

Rules:

- Claims begin at L0.
- Literature discovery alone cannot advance a Claim beyond L1.
- L2 requires direct source verification and review of credible counterevidence.
- L3 requires a valid, registered P1 experiment.
- L4 requires meaningful variation and replication.
- L5 remains reversible and requires strong convergent support.
- Maturity is never inferred automatically.
- Evidence count does not determine maturity.
- Model confidence does not determine maturity.
- One accepted Decision may advance a Claim by no more than one level.
- Multi-level upward jumps are prohibited.
- L4 and L5 are disabled during the pilot.
- Principle Candidate creation is prohibited during the pilot.

## 4. Research OS Architecture

The P1 Research OS uses:

- Markdown as canonical storage;
- YAML frontmatter as structured metadata;
- permanent IDs;
- explicit object relationships;
- Git for version history;
- local filesystem storage;
- Python;
- Pydantic;
- PyYAML;
- pytest.

The system does not use:

- SQL;
- SQLite;
- graph databases;
- vector databases;
- cloud services;
- web frameworks;
- remote APIs;
- background services;
- filesystem watchers;
- distributed systems.

The logical knowledge structure is graph-like, but no graph database is used.

Every relationship has one canonical stored owner.
Reverse navigation is derived.
Reciprocal fields are prohibited.

Example:

Relationship: Question ↔ Unknown
Canonical stored owner: Unknown
Canonical field: Unknown.question_ids
Derived reverse navigation: Question → Unknowns

The system must not store a duplicate reciprocal field on the Question.

## 5. Principal Investigator Decisions

The following PI decisions are authoritative.

**PI-001 — Canonical storage**
Markdown with YAML frontmatter is canonical.
Derived indexes are disposable and rebuildable.
P1 uses no database.
Database requirements elsewhere in the repository apply only to unrelated VELYNX or legacy runtime components.

**PI-002 — Relationship ownership**
Each relationship has one canonical stored owner.
Reverse navigation is derived.
Reciprocal relationship fields are prohibited.

**PI-003 — Decision transactions**
Accepting a Decision may update:

- the Decision;
- declared Claims;
- declared Unknowns.

This later operation must use a minimal transaction manifest:

- validate the complete proposed state;
- stage all replacement files;
- create a transaction manifest;
- replace canonical files in deterministic order;
- detect incomplete application;
- fail closed;
- require explicit human recovery;
- never alter a Result or Interpretation.

A general transaction framework is prohibited.

**PI-004 — Maturity transitions**
One accepted Decision may change a Claim by at most one maturity level.

Permitted examples:

- L0 → L1
- L1 → L2
- L2 → L3

Prohibited examples:

- L0 → L2
- L0 → L3
- L1 → L3

**PI-005 — Pilot maturity ceiling**
L4 and L5 are disabled during the pilot.
No Principle Candidate may be created during P1-KB-001.

**PI-006 — Experiment amendments**
An experiment amendment is a Research Artifact with:
artifact_kind: experiment_amendment

The registered base Experiment remains immutable.
Accepted amendments form one linear hash chain.

**PI-007 — Human identity**
Actor and reviewer handles match:
^[a-z][a-z0-9_-]{1,31}$

The initial Principal Investigator handle is:
pi

**PI-008 — Git**
Named human review on main is sufficient for the single-researcher pilot.

The CLI must never:

- commit;
- merge;
- tag;
- push;
- pull;
- rebase;
- rewrite Git history.

**PI-009 — Artifact retention**
Commit:

- canonical Markdown;
- registered protocol material;
- Decisions;
- Interpretations;
- small Results;
- configurations;
- small reproducibility artifacts;
- fixtures.

Large excluded artifacts require a manifest containing:

- path or locator;
- SHA-256;
- byte size;
- media type;
- availability;
- exclusion reason;
- generation or acquisition procedure;
- recovery procedure.

**PI-010 — Validation profiles**
Universal schema validity and pilot completion are separate.

Pilot object-count rules belong to a named validation profile such as:
pilot-kb-001

They are not permanent universal schema constraints.

**PI-011 — Source and Evidence lifecycle**
Draft Evidence may reference a draft or under-review Source.
Evidence can become accepted only when the Source satisfies the required verification conditions.

**PI-012 — Source locators**
Relationships among P1 objects use permanent IDs.

Evidence provenance may additionally contain:

- page numbers;
- sections;
- tables;
- figures;
- quotations;
- dataset records;
- repository paths;
- persistent identifiers.

These are source locators, not object relationships.

## 6. Approved Repository Layout

The bounded P1 subtree is:

```
p1/
├── records/
│   ├── research_artifacts/
│   ├── questions/
│   ├── unknowns/
│   ├── claims/
│   ├── sources/
│   ├── evidence/
│   ├── hypotheses/
│   ├── experiments/
│   ├── results/
│   ├── interpretations/
│   ├── decisions/
│   └── principle_candidates/
├── methodology/
├── specifications/
├── architecture_decisions/
├── artifacts/
├── templates/
├── tooling/
│   └── p1_os/
├── derived/
├── .transactions/
│   └── active/
└── audit/
    └── transaction_recoveries/
tests/
├── p1_os/
└── fixtures/
    └── p1_os/
```

Classification:

- p1/records/ — canonical scientific records
- p1/methodology/ — canonical P1 methodology
- p1/specifications/ — implementation specifications
- p1/architecture_decisions/ — engineering decisions
- p1/artifacts/ — small reproducibility artifacts and manifests
- p1/templates/ — tooling templates, not scientific records
- p1/tooling/p1_os/ — isolated Python implementation
- p1/derived/ — disposable generated indexes
- p1/.transactions/active/ — transient local transaction state
- p1/audit/transaction_recoveries/ — optional recovery audit records
- tests/p1_os/ — implementation tests
- tests/fixtures/p1_os/ — versioned fixtures

P1 tooling must not depend on:

- backend;
- frontend;
- infra;
- VELYNX runtime databases;
- VELYNX experiment runners;
- remote APIs;
- background services.

## 7. Milestone 0 — Repository Inspection

### Objective

Milestone 0 was a read-only repository inspection.

Sonnet 5 was required to:

- inspect the actual repository;
- identify policy conflicts;
- inspect dependencies;
- inspect Python and testing conventions;
- inspect .gitignore;
- verify Terra's repository findings;
- evaluate the proposed P1 layout;
- prepare the Milestone 1 file and test plan;
- modify nothing;
- install nothing;
- stop before implementation.

### Repository findings

Repository root: C:/Users/Purushottam/Documents/P1
Branch: main
HEAD: c7db7402834ad358a0fb0035919a4eb8ab7fa301
Commit message: refactor(repo): implement approved repository architecture restructure

The working tree was already dirty because of eight pre-existing untracked files under theory/.

Sonnet verified that these eight files existed before its inspection and remained unchanged afterwards.

No P1 Research OS directory or implementation previously existed.

No nested Git repositories or submodules existed, although three Git worktrees existed under P1.worktrees/.

The relevant governance files were:

- REPOSITORY_CONSTITUTION.md
- RESEARCH_PROTOCOL.md
- reproducibility.yaml

Dependency and packaging files included:

- pyproject.toml
- root requirements.txt
- backend/requirements.txt
- backend/requirements-dev.txt

### Important Milestone 0 findings

**No P1 subtree allocation**
REPOSITORY_CONSTITUTION.md assigned new work to existing VELYNX directories but did not allocate p1/.
This was considered a governance blocker before Milestone 1.

**Existing SQLite rule**
The repository constitution included SQLite preservation rules for VELYNX runtime components.
Because P1 uses no database, this was not a mechanical blocker, but clarification was desirable.

**Research Protocol naming confusion**
RESEARCH_PROTOCOL.md was titled for Project P1 but contained Program D/VELYNX-specific methods.
A scope statement was recommended.

**Root dependencies**
Root requirements.txt did not declare:

- Pydantic;
- PyYAML;
- pytest;
- Typer.

The packages were already installed in the local .venv, but the dependency declarations were absent.

**Package discovery**
The root setuptools discovery did not include p1_os.
This did not block schema tests because pytest could import from the repository root.
Package-discovery changes were therefore deferred.

**Genuine .gitignore collision**
An unanchored rule existed:
research_artifacts/

This silently ignored:
p1/records/research_artifacts/

This was a real blocker because canonical Research Artifact records could be created but remain untracked.

**Existing CLIs unsuitable**
Existing CLIs imported VELYNX backend, learning, memory, database, and runtime systems.
They were rejected as foundations for the P1 CLI.

### Milestone 0 outcome

Milestone 0 passed because Sonnet:

- inspected real repository files;
- cited actual repository constraints;
- independently verified Terra's claims;
- found an additional .gitignore problem;
- changed no files;
- installed nothing;
- did not begin implementation;
- stopped correctly.

## 8. Milestone 0.5 — Minimal Policy Patch

### Objective

Milestone 0.5 applied only the minimal repository-policy and dependency-declaration changes required before Milestone 1.
It did not implement Research OS software.

### Authorized files

Sonnet was allowed to create:

- p1/requirements.txt
- p1/requirements-dev.txt

Sonnet was allowed to modify:

- REPOSITORY_CONSTITUTION.md
- RESEARCH_PROTOCOL.md
- .gitignore

No other modifications were authorized.

### Dependency decisions

P1 dependencies were isolated from root VELYNX dependencies.

p1/requirements.txt was created with exactly:

```
pydantic==2.13.4
PyYAML==6.0.3
```

p1/requirements-dev.txt was created with exactly:

```
-r requirements.txt
pytest==9.0.3
```

Typer was deliberately deferred because Milestone 1 does not implement a CLI.

No package was installed.
Root and backend requirements remained unchanged.

### Constitution patch

REPOSITORY_CONSTITUTION.md was updated minimally to establish that:

- p1/ is the bounded P1 Research OS subtree;
- P1 is governed by the approved Research OS specification and PI decisions;
- VELYNX placement rules do not force P1 records into legacy directories;
- P1 tooling must not depend on backend, frontend, runtime databases, remote APIs, or background services;
- P1 uses no database;
- SQLite preservation rules apply to VELYNX/legacy components, not P1.

### Research Protocol patch

A scope line was added:

Scope: This protocol governs VELYNX Program D experiments. P1 Research OS records and P1-registered experiments are governed by the approved P1 Research OS specification and Principal Investigator decisions.

No other text was changed.

### .gitignore patch

The unanchored rule remained unchanged:
research_artifacts/

Narrow exceptions were added:

```
!/p1/records/research_artifacts/
!/p1/records/research_artifacts/**
```

Generated and transient P1 paths were ignored:

```
/p1/derived/
/p1/.transactions/active/
```

Sonnet verified that canonical paths were not ignored, including:

- p1/records/research_artifacts/P1-AR-001.md
- p1/records/questions/P1-Q001.md
- p1/records/claims/P1-C001.md
- p1/methodology/PI_DECISIONS.md
- p1/artifacts/example.json
- p1/templates/claim.md
- p1/tooling/p1_os/__init__.py
- tests/p1_os/test_identifiers.py
- tests/fixtures/p1_os/claims/valid.md

Sonnet verified that these paths were ignored as intended:

- p1/derived/index.yaml
- p1/.transactions/active/txn-001.yaml

No representative files were created during those checks.

### Milestone 0.5 outcome

Milestone 0.5 passed because:

- only five authorized files changed;
- no packages were installed;
- no unauthorized files changed;
- no implementation began;
- canonical P1 records became trackable;
- derived and transient state remained ignored;
- P1 dependencies were isolated;
- legacy VELYNX files remained untouched;
- no commit was made.

## 9. Current Repository State Before Milestone 1

Expected working-tree state:

**Pre-existing user work**
Eight untracked files under: theory/
These are unrelated and must remain untouched.

**Approved Milestone 0.5 changes**
Modified:

- .gitignore
- REPOSITORY_CONSTITUTION.md
- RESEARCH_PROTOCOL.md

Created:

- p1/requirements.txt
- p1/requirements-dev.txt

**No commit**
Neither Milestone 0 nor Milestone 0.5 was committed by the model.
The model is prohibited from committing.

## 10. Milestone 1 — Purpose

Milestone 1 is the first software implementation milestone.

Its purpose is to establish the canonical record foundation.
It is not the full Research OS.
It does not implement research workflows.

Milestone 1 implements:

- permanent-ID validation;
- actor-handle validation;
- object-type enums;
- object-specific status enums;
- Claim maturity enum;
- common canonical metadata;
- provenance entries;
- 12 strict Pydantic schemas;
- duplicate-safe YAML frontmatter loading;
- object-schema dispatch;
- exact Markdown-body preservation;
- deterministic metadata serialization;
- required-heading validation;
- path and filename validation;
- 12 canonical templates;
- fixtures;
- tests;
- import isolation.

Milestone 1 explicitly does not implement:

- CLI;
- ID allocation;
- ID retirement;
- repository scans;
- object creation commands;
- object links;
- relationship existence checks;
- derived reverse indexes;
- lifecycle transitions;
- maturity transitions;
- review commands;
- experiment registration;
- protocol hashing;
- amendment chains;
- Result recording workflow;
- Interpretation workflow;
- Decision application;
- transactions;
- transaction manifests;
- pilot validation profiles;
- Principle Candidate prohibition;
- scientific content;
- dashboards;
- databases;
- web services;
- Git automation.

## 11. Milestone 1 — Permanent IDs

Prefixes:

- Research Artifact: P1-AR
- Question: P1-Q
- Unknown: P1-U
- Claim: P1-C
- Source: P1-S
- Evidence: P1-V
- Hypothesis: P1-H
- Experiment: P1-E
- Result: P1-R
- Interpretation: P1-I
- Decision: P1-D
- Principle Candidate: P1-P

Format:
`<prefix><six-digit positive integer>`

Examples:

- P1-Q000001
- P1-C000001
- P1-AR000001

Rules:

- six digits exactly;
- 000000 is invalid;
- case-sensitive;
- prefix must match object type;
- no spaces;
- title-independent;
- validation only in Milestone 1;
- no allocation or reservation.

## 12. Milestone 1 — Actor Handles

Pattern: `^[a-z][a-z0-9_-]{1,31}$`

Valid examples:

- pi
- reviewer_1
- research-engineer
- sonnet5

Invalid examples:

- P1a
- user@example.com
- _reviewer
- two words
- more than 32 characters

## 13. Milestone 1 — Common Metadata

Every canonical object contains:

```yaml
id: P1-C000001
title: Example title
object_type: claim
status: draft
schema_version: "1.0"
created: "2026-07-23T12:00:00Z"
last_reviewed: null
created_by: pi
provenance: []
```

Rules:

- strict Pydantic v2 models;
- extra="forbid";
- no unknown metadata fields;
- title must be nonempty;
- schema version must equal "1.0";
- created datetime must be timezone-aware;
- last-reviewed datetime must be timezone-aware;
- last-reviewed must not precede creation;
- actor handle must be valid;
- provenance list is required but may be empty;
- no lifecycle transitions.

## 14. Milestone 1 — Provenance

Example:

```yaml
artifact_id: P1-AR000001
derived_from_ids:
  - P1-C000002
source_locator: "Page 12, section 3"
note: "Candidate claim extracted from a report."
```

At least one field must be present.
Unknown fields are prohibited.
Duplicate derived_from_ids are prohibited.
Existence and cycle checks are deferred.

## 15. Milestone 1 — Object Schemas

### Research Artifact

Additional fields:

```yaml
artifact_kind: deep_research_report
media_type: application/pdf
content_hash: null
external_locator: null
```

Required headings:

```
## Description
## Provenance
## Integrity
```

### Question

Additional fields:

```yaml
selected: false
scope: "Explicit scope"
```

Required headings:

```
## Research Question
## Rationale
## Scope
## Selection Criteria
```

### Unknown

Additional fields:

```yaml
question_ids:
  - P1-Q000001
priority: high
blocks: []
resolution_criteria:
  - "Resolution criterion"
```

Required headings:

```
## Unknown
## Why It Matters
## Current Evidence State
## Resolution Criteria
```

### Claim

Additional fields:

```yaml
question_ids:
  - P1-Q000001
unknown_ids:
  - P1-U000001
claim_role: candidate
maturity: L0
scope: "Explicit scope"
competes_with_claim_ids: []
```

Claim roles:

- candidate
- competing
- constraint
- scope_limit

Required headings:

```
## Claim
## Scope
## Current Justification
## Strongest Counterargument
## Reversal or Revision Conditions
```

### Source

Additional fields:

```yaml
source_type: primary_empirical
citation: "Full citation"
persistent_identifier: null
access_status: not_checked
accessed_at: null
```

Access states:

- not_checked
- abstract_only
- full_text_checked
- inaccessible

Required headings:

```
## Citation
## Relevance
## Directly Demonstrates
## Limitations
## Verification Notes
```

### Evidence

Additional fields:

```yaml
source_id: P1-S000001
claim_links:
  - claim_id: P1-C000001
    stance: supports
evidence_kind: reported_result
scope: "Exact evidence scope"
source_locator: "Results, table 1"
verification_status: pending
```

Stances:

- supports
- contradicts
- contextualizes
- null_evidence
- limits

Verification status:

- pending
- partially_verified
- verified
- unverifiable

Required headings:

```
## Evidence Statement
## Directly Establishes
## Does Not Establish
## Generalization Limits
## Verification
```

### Hypothesis

Additional fields:

```yaml
claim_ids:
  - P1-C000001
competing_hypothesis_ids: []
prediction: "Falsifiable prediction"
independent_variables:
  - "Independent variable"
dependent_variables:
  - "Dependent variable"
falsification_criteria:
  - "Observable criterion"
scope: "Explicit scope"
```

Required headings:

```
## Hypothesis
## Competing Explanations
## Predictions
## Falsification Criteria
## Scope
```

### Experiment

Additional fields:

```yaml
question_id: P1-Q000001
hypothesis_ids:
  - P1-H000001
competing_hypothesis_ids: []
competing_claim_ids: []
primary_metric: "Primary metric"
secondary_metrics: []
independent_variables:
  - "Independent variable"
dependent_variables:
  - "Dependent variable"
controls:
  - "Control"
baselines:
  - "Baseline"
resource_budgets:
  compute: "Defined budget"
randomization: "Defined procedure"
seed_policy: "Defined policy"
exclusions: []
failure_conditions:
  - "Failure condition"
invalidation_conditions:
  - "Invalidation condition"
analysis_plan: "Analysis plan"
prospective_update_rules:
  - rule_id: supports_primary
    outcome_class: supports_primary
    decision_required: true
    proposed_actions:
      - "Human review required"
```

Required headings:

```
## Research Question
## Hypotheses
## Variables
## Controls and Baselines
## Resource Budgets
## Randomization and Seeds
## Exclusions
## Failure and Invalidation Conditions
## Analysis Plan
## Prospective Decision Rules
```

Milestone 1 defines structure only.
It does not register or hash experiments.

### Result

Additional fields:

```yaml
experiment_id: P1-E000001
protocol_hash: "placeholder-valid-nonempty-string"
amendment_ids: []
started_at: "2026-07-23T12:00:00Z"
ended_at: "2026-07-23T13:00:00Z"
environment: {}
seeds: []
measurements: []
exclusions_applied: []
protocol_deviations: []
failure_facts: []
outcome_class: inconclusive
raw_artifact_ids: []
```

Outcome classes:

- supports_primary
- supports_competing
- inconclusive
- invalid

Required headings:

```
## Protocol Facts
## Raw Measurements
## Exclusions and Deviations
## Outcome Classification
```

Result records must not contain Claim conclusions.

### Interpretation

Additional fields:

```yaml
result_ids:
  - P1-R000001
hypothesis_ids:
  - P1-H000001
scope: "Bounded scope"
uncertainty: "Explicit uncertainty"
```

Required headings:

```
## Bounded Interpretation
## Alternative Explanations
## Prohibited Inference
## Uncertainty
```

### Decision

Additional fields:

```yaml
result_ids:
  - P1-R000001
interpretation_ids:
  - P1-I000001
claim_changes:
  - claim_id: P1-C000001
    prior_status: active
    proposed_status: accepted_for_use
    prior_maturity: L0
    proposed_maturity: L1
    update_rule_id: supports_primary
    rationale: "Bounded rationale"
unknown_changes:
  - unknown_id: P1-U000001
    prior_status: active
    proposed_status: closed
    rationale: "Bounded rationale"
accepted_conclusion: "Scope-bounded conclusion"
prohibited_conclusions:
  - "No broader conclusion"
scope: "Decision scope"
uncertainty: "Residual uncertainty"
reversal_conditions:
  - "Observable reversal condition"
reviewer_id: pi
decision_date: "2026-07-23"
counterevidence_review: null
```

Milestone 1 defines only the record schema.
It does not apply changes.

Required headings:

```
## Decision Rationale
## Evidence Considered
## Boundaries
## Reversal Conditions
```

### Principle Candidate

Additional fields:

```yaml
claim_ids:
  - P1-C000001
scope: "Explicitly bounded scope"
reversal_conditions:
  - "Observable reversal condition"
```

Required headings:

```
## Candidate Principle
## Supporting Claims
## Scope and Exclusions
## Reversal Conditions
```

No real Principle Candidate record may be created.

## 16. Milestone 1 — Frontmatter and Markdown

Canonical files begin with `---` at byte one.

Rules:

- UTF-8 only;
- no UTF-8 BOM;
- opening and closing delimiters contain only `---`;
- malformed YAML fails;
- empty YAML fails;
- non-mapping YAML fails;
- unterminated frontmatter fails;
- duplicate YAML keys fail at every nesting depth;
- unsafe tags fail;
- aliases and merge keys that obscure metadata fail;
- merge-conflict markers fail;
- no silent repair.

The parser returns a CanonicalDocument containing:

- validated Pydantic object;
- exact Markdown body;
- line-ending style;
- final-newline state;
- optional source path.

Line-ending rules:

- consistent LF accepted;
- consistent CRLF accepted;
- mixed line endings rejected;
- original line ending preserved in preservation mode;
- templates use LF.

Body preservation includes:

- blank lines;
- trailing spaces;
- indentation;
- Unicode;
- quotations;
- code fences;
- wrapping;
- final-newline state.

## 17. Milestone 1 — Serialization

Metadata serialization is deterministic.

Common fields appear first in this order:

```
id
title
object_type
status
schema_version
created
last_reviewed
created_by
provenance
```

Object-specific fields follow declaration order.

Rules:

- preserve list order;
- preserve mapping order;
- no alphabetical sorting;
- emit Unicode directly;
- emit no Python tags;
- empty list as [];
- empty mapping as {};
- null as null;
- Booleans as true and false;
- quote "1.0";
- quote dates and datetimes;
- use LF for new output;
- repeated serialization is byte-identical;
- do not mutate the source model;
- serializer returns text or bytes only;
- serializer does not write files.

## 18. Required Heading Validation

Maintain one authoritative heading registry.

Rules:

- exact second-level headings begin with `## `;
- trailing spaces/tabs may be removed for matching;
- leading indentation means the heading does not count;
- headings in fenced code blocks do not count;
- backtick and tilde fences are recognized;
- each required heading appears exactly once;
- order must match;
- additional headings are allowed;
- wrong heading level does not count;
- unterminated fences fail.

No external Markdown parser may be added.

## 19. Path Validation

Canonical locations:

```
p1/records/research_artifacts/
p1/records/questions/
p1/records/unknowns/
p1/records/claims/
p1/records/sources/
p1/records/evidence/
p1/records/hypotheses/
p1/records/experiments/
p1/records/results/
p1/records/interpretations/
p1/records/decisions/
p1/records/principle_candidates/
```

Filename: `<ID>.md`

Rules:

- directory matches object type;
- filename stem matches embedded ID;
- lowercase .md;
- no title slug;
- no nested directory;
- case-sensitive;
- validator takes an explicit root;
- no hard-coded Windows path;
- validator never moves or creates files.

## 20. Milestone 1 Source Layout

```
p1/tooling/p1_os/
├── __init__.py
├── identifiers.py
├── enums.py
├── metadata.py
├── frontmatter.py
├── paths.py
└── schemas/
    ├── __init__.py
    ├── common.py
    ├── research_artifacts.py
    ├── questions.py
    ├── unknowns.py
    ├── claims.py
    ├── sources.py
    ├── evidence.py
    ├── hypotheses.py
    ├── experiments.py
    ├── results.py
    ├── interpretations.py
    ├── decisions.py
    └── principle_candidates.py
```

Avoid duplicate definitions.

## 21. Templates

Create exactly 12 templates:

```
p1/templates/research_artifact.md
p1/templates/question.md
p1/templates/unknown.md
p1/templates/claim.md
p1/templates/source.md
p1/templates/evidence.md
p1/templates/hypothesis.md
p1/templates/experiment.md
p1/templates/result.md
p1/templates/interpretation.md
p1/templates/decision.md
p1/templates/principle_candidate.md
```

Every template:

- parses;
- validates;
- includes required headings;
- uses a valid placeholder ID;
- uses status: draft;
- uses schema_version: "1.0";
- uses created_by: pi;
- uses a timezone-aware creation datetime;
- contains placeholder content only;
- asserts no scientific truth;
- implies no verified evidence;
- uses LF;
- ends with exactly one LF;
- round-trips deterministically.

Templates are not canonical records.

## 22. Tests

Required test paths:

```
tests/p1_os/
tests/p1_os/schemas/
tests/fixtures/p1_os/
```

Tests must cover:

- IDs;
- actor handles;
- enums;
- common metadata;
- provenance;
- all 12 object schemas;
- missing required fields;
- invalid types;
- invalid enums;
- duplicate values;
- unknown fields;
- YAML delimiters;
- malformed YAML;
- duplicate YAML keys;
- unsafe tags;
- aliases and merge keys;
- LF and CRLF;
- mixed endings;
- UTF-8 BOM;
- Unicode;
- exact body preservation;
- deterministic serialization;
- required headings;
- code-fence handling;
- canonical paths;
- all 12 templates;
- module isolation.

Isolation tests must confirm P1 imports do not load:

- backend;
- frontend;
- infra;
- framework;
- research;
- sqlalchemy;
- redis;
- chromadb;
- fastapi;
- requests.

## 23. Milestone 1 Authorized Changes

Sonnet may create:

- p1/tooling/p1_os/
- p1/templates/
- tests/p1_os/
- tests/fixtures/p1_os/
- empty canonical directories under p1/records/

Sonnet must not modify:

- .gitignore;
- policy documents;
- requirements files;
- pyproject.toml;
- reproducibility.yaml;
- VELYNX source;
- experiment files;
- existing scientific records.

No packages may be installed.
No commit may be made.

## 24. Verification Commands

Use .venv Python.

Run:

```
.venv/Scripts/python.exe -m pytest tests/p1_os --collect-only -q
.venv/Scripts/python.exe -m pytest tests/p1_os -q
```

Also run:

- import-isolation verification;
- deterministic serialization twice;
- git status;
- Git diff inspection.

Do not run unrelated experiment suites.

## 25. Milestone 1 Acceptance Criteria

Milestone 1 passes only if:

- All 12 schemas exist.
- All ID prefixes validate.
- Prefix and object type agree.
- Actor handles validate.
- Unsupported schema versions fail.
- Unknown fields fail.
- Duplicate YAML keys fail.
- Malformed frontmatter fails.
- Unterminated frontmatter fails.
- Non-mapping frontmatter fails.
- Unsafe YAML tags fail.
- Markdown body remains exact.
- LF and CRLF are tested.
- Mixed line endings fail.
- Required headings work outside fences.
- Heading order and uniqueness validate.
- Paths and filenames validate.
- All templates parse and validate.
- Templates contain placeholders only.
- Imports remain isolated.
- All Milestone 1 tests pass.
- No later workflow is implemented.
- No package is installed.
- No unauthorized file is changed.
- The eight pre-existing theory files remain untouched.
- No commit occurs.

## 26. Current Milestone 1 Status

Milestone 1 has not begun.

Sonnet 5 correctly stopped because its earlier prompt was truncated after:
provenance: []

Sonnet explicitly refused to guess the missing schema, serialization, heading, template, and testing rules.
This was correct behavior.

A continuation specification was then prepared containing the complete remaining requirements.

The next action is:

Give Sonnet 5 the complete Milestone 1 continuation in the same conversation, allow it to implement Milestone 1, require all tests to pass, require a final Git diff review, prohibit commits, and stop before Milestone 2.

## 27. Review Requested from GPT-5.5

Review this handoff and answer:

- Were Milestone 0 and Milestone 0.5 executed correctly?
- Are any completed changes scientifically or technically unsafe?
- Is Milestone 1 properly bounded?
- Are any Milestone 1 schema rules internally contradictory?
- Are any requirements overengineered for the pilot?
- Are any critical validation rules missing?
- Does any schema logic accidentally implement deferred lifecycle behavior?
- Are the Source/Evidence and Result/Interpretation boundaries preserved?
- Is Markdown/YAML a reasonable canonical format for the pilot?
- Is the testing plan sufficient to begin implementation?
- Is Sonnet correct to proceed with Milestone 1 now?
- What exact issues, if any, must be corrected before implementation?

Classify every finding as:

- Blocking before Milestone 1
- Non-blocking improvement
- Already resolved
- Intentionally deferred
- No issue

Do not redesign the architecture.
Do not propose a database.
Do not add object types.
Do not select P1's scientific research question.
Do not expand the system beyond Milestone 1.

End with exactly one recommendation:

- Approve Milestone 1 as specified
- Approve Milestone 1 with listed minimal corrections
- Do not proceed until blocking issues are resolved.
