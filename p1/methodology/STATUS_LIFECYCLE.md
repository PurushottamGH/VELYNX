# P1 Status Lifecycle — Representable States vs. Decision-Authorized Transitions

Scope: Milestone 1.1. This document is descriptive only. It records what
the Milestone 1 Pydantic schemas currently allow a record to *state*
(`status`, and for Claim also `maturity`), and separately what the frozen
P1 Research OS specification says is allowed to *change* that state and
under whose authority. No transition enforcement is implemented by this
document or by any code change in Milestone 1.1. Milestone 1's schemas
validate each record in isolation; they do not compare a proposed record
against a prior version, so any transition described below as
"Decision-authorized" is a methodology rule, not a runtime check.

## 1. Representable schema states (Milestone 1, as implemented)

Per object type, the `status` enum values a record's YAML frontmatter may
currently declare (`p1/tooling/p1_os/enums.py`):

| Object type         | `status` enum            | Values                                |
|----------------------|---------------------------|----------------------------------------|
| Research Artifact    | `ResearchArtifactStatus`  | `draft`                                |
| Question              | `QuestionStatus`          | `draft`                                |
| Unknown               | `UnknownStatus`           | `draft`, `active`, `closed`            |
| Claim                 | `ClaimStatus`             | `draft`, `active`, `accepted_for_use`  |
| Source                | `SourceStatus`            | `draft`                                |
| Evidence              | `EvidenceStatus`          | `draft`                                |
| Hypothesis            | `HypothesisStatus`        | `draft`                                |
| Experiment            | `ExperimentStatus`        | `draft`                                |
| Result                | `ResultStatus`            | `draft`                                |
| Interpretation        | `InterpretationStatus`    | `draft`                                |
| Decision              | `DecisionStatus`          | `draft`                                |
| Principle Candidate   | `PrincipleCandidateStatus`| `draft`                                |

Claim additionally carries a separate `maturity` field (`ClaimMaturity`):
`L0`, `L1`, `L2`, `L3`, `L4`, `L5` (L4/L5 disabled during the pilot per
PI-005; see specification section 3).

Only Unknown and Claim currently declare more than one representable
`status` value. `UnknownStatus.ACTIVE`/`.CLOSED` and
`ClaimStatus.ACTIVE`/`.ACCEPTED_FOR_USE` exist in the enum because they
appear in the worked `Decision.unknown_changes` / `Decision.claim_changes`
examples in specification section 15 — the schema must be able to
*represent* a Decision that proposes them, even though Milestone 1
performs no transition itself. All other object types expose exactly one
value (`draft`) at this milestone; the specification does not yet define
their subsequent states.

Every schema field above validates a single record snapshot independently
(`CanonicalRecordBase.model_validate`, `frontmatter.parse_document`).
Nothing in Milestone 1 or Milestone 1.1 reads a record's previous
on-disk state or compares it to a new one.

## 2. Decision-authorized transitions (specification, not code)

Per PI-003 ("Decision transactions") and section 2 of the Milestone 1
specification: "A Decision is the only object authorized to change
scientific Claim or Unknown states after initial activation. A Decision
does not alter raw Results."

- **Who may propose a transition:** only an accepted `Decision` record,
  via its `claim_changes` and `unknown_changes` fields (specification
  section 15). No other object type is authorized to change Claim or
  Unknown status/maturity.
- **What a Decision may change:** the Decision's own record, plus the
  declared Claims and Unknowns it names (PI-003). It must never alter a
  Result or an Interpretation.
- **Claim `status`:** a Decision's `claim_changes[].prior_status` /
  `.proposed_status` pair records the proposed transition
  (e.g. `draft` → `active` → `accepted_for_use`). Milestone 1 does not
  enumerate or restrict which `status` transitions are legal beyond both
  values being members of `ClaimStatus`.
- **Claim `maturity`:** governed by PI-004 — one accepted Decision may
  advance a Claim's maturity by at most one level (`L0`→`L1`, `L1`→`L2`,
  `L2`→`L3`, ...). Multi-level jumps (`L0`→`L2`, `L0`→`L3`, `L1`→`L3`,
  ...) are prohibited by methodology. L4/L5 are disabled during the pilot
  (PI-005).
- **Unknown `status`:** a Decision's `unknown_changes[].prior_status` /
  `.proposed_status` pair records the proposed transition
  (e.g. `active` → `closed`).
- **All other object types:** the specification defines no further
  states or transitions for Research Artifact, Question, Source,
  Evidence, Hypothesis, Experiment, Result, Interpretation, Decision, or
  Principle Candidate beyond their single `draft` value. Introducing
  additional states or transition rules for them is out of scope for
  Milestone 1.1 and is deferred to a future, explicitly authorized
  milestone.

## 3. What is explicitly not implemented

Per specification section 10 ("Milestone 1 explicitly does not
implement") and the Milestone 1.1 authorization, the following remain
unimplemented after this document and after Milestone 1.1:

- No code validates that a `status` or `maturity` value written to a
  record is a legal transition from that record's prior on-disk value.
- No code enforces the one-level-per-Decision maturity rule (PI-004).
- No code enforces that only a Decision may change Claim/Unknown state.
- No transaction manifest, staging, or fail-closed application exists
  (PI-003's transaction mechanics remain a future milestone).
- No pilot validation profile (PI-010) or Principle Candidate
  prohibition (PI-005) is enforced in code.

This document exists so the gap between "what the schema can represent"
and "what the methodology authorizes" is explicit and auditable, without
adding lifecycle enforcement code, which remains prohibited for
Milestone 1.1.
