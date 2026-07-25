# Standard Classification

- **Status:** Draft
- **Scope:** Classification of every proposed Domain standard against the minimum activation plan
- **Responsibility:** Assign each proposed standard to a class with its activation trigger
- **Authority source:** None. This record has no normative authority and activates nothing.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. Classes

| Class | Meaning |
|---|---|
| **Required before adoption** | Must be Active in or before the §13 ¶3 adoption atomic change |
| **Required after adoption** | Must be Active before the first governed scientific transition |
| **Optional** | Activate only when a named trigger occurs; the Constitution is satisfied without it |
| **Future extension** | No foreseeable trigger in current P1 scope |

Every standard classified Optional or Future has a **trigger** — the specific condition that converts it to Required. Absent the trigger, activating it adds a steward approval and an independent attestation for no constitutional gain.

---

## 2. Required before adoption

**None.**

§13 ¶3's adoption list is Constitution, Registry, steward, and two attestations. No Domain standard appears, and `active_domain_standards: []` is a valid Active state.

Two **non-standard** artifacts are nonetheless required in the adoption change, because their MUSTs bind the instant the Constitution becomes Active:

| Artifact | Clause | Why it is not a standard |
|---|---|---|
| Architecture record (descriptive, versioned) | §10 ¶1 | The MUST attaches to the record, not to a standard governing records. Kept descriptive, it is Level-4 documentation, not a Normative artifact under §2. |
| Legacy index + moves + banners | §4 ¶5, §14 | §14 strips authority automatically; §4 ¶5's distinguishability duty is discharged by file placement and labelling — engineering, not authority. |

Plus the adoption conformance dossier (§12 ¶1), which is the reviewer's instrument rather than a governed artifact.

---

## 3. Required after adoption

### RS-1 — P1 Research Standard

The only standard required for lawful research operation. Owns six object types under the explicit permission of §9 ¶2 ("MAY govern subordinate Registered protocols, Decisions, and scientific records").

| Owned type | Clause forcing inclusion |
|---|---|
| `registered_protocol` | §2, §5 ¶3 — omission is **permanently** costly: without pre-registration every execution is exploratory, and §13 ¶4 forbids relabelling later |
| `observation` | §2 — distinct kind; substitution prohibited |
| `result` | §7 ¶2 — completion criteria and recording authority are delegated to a Domain standard or protocol |
| `unknown` | §8 ¶1 — permanent first-class kind; material uncertainty MUST be recorded as one, immediately |
| `decision` | §4 ¶5 — no scientific transition is lawful without one |
| `interpretation` | §2 — inference from "Evidence **or Results**"; Results suffice, so this closes the loop without Claim or Evidence |

**Trigger already met.** Any scientific transition requires it.

---

## 4. Optional

Ordered by how likely the trigger is to fire in P1's current programme.

| Standard | Owned types | Trigger that makes it Required | Clause | Likelihood |
|---|---|---|---|---|
| **RS-1 extension: Claim + Evidence** *(MINOR amendment, not a new standard)* | `claim`, `evidence`, `source` | First assertion of the form "Evidence E supports Claim C," or any need to admit Observations for a Claim | §5 ¶2, §6 ¶4 | **High** — likely the first amendment |
| **RS-1 extension: Question** | `question` | First need to record a research question as a governed object rather than prose | §2 | Medium — note §2 already forces *material* questions into Unknowns, which RS-1 owns, so this is often unnecessary |
| **RS-1 extension: Hypothesis** | `hypothesis` | First registration of a Claim paired with an operational test | §2 | Medium — requires Claim first |
| **Custody & Retention** | `custody_manifest`, `digest_algorithm_registration`, `retention_schedule` | External artifacts too large or numerous for the protocol to enumerate; or a second digest algorithm; or a retention schedule spanning protocols | §6 ¶2, §10 ¶5 | Medium — §6 ¶2 permits the *protocol* to specify the digest, which defers this |
| **Automation & Tooling** | `check_registration`, `check_run_record` | First time check output is cited as conformance evidence in a formal claim, requiring declared scope and false-negative disclosure | §12 ¶3-4 | Medium |
| **Authority & Delegation** | `authority_assignment`, `delegation_record`, `role_definition`, `conflict_of_interest_declaration` | Second steward; any delegation; any role-based approval; formal succession beyond a named successor in the Registry | §4 ¶1, §4 ¶4 | Medium — rises sharply the moment throughput of H-7 becomes a bottleneck |
| **Architecture** | `architecture_record`, `boundary_declaration`, `material_state_declaration` | Boundaries must become **enforceable** rather than described; or Material state declarations are needed for reproducibility (§10 ¶2) | §10 | Medium — a descriptive record satisfies §10 ¶1 indefinitely |
| **Ontology** | `object_type_registration`, `identifier_allocation`, `relationship_kind` | A **second** standard owns object types, creating cross-standard drift risk under §11 ¶3 | §5 ¶6, §11 ¶3 | Low while RS-1 is the only standard |
| **Review & Attestation** | `review_request`, `review_record`, `attestation`, `manual_review_procedure` | More than two reviewers; or manual procedures numerous enough to need their own lifecycle | §12 ¶4, §13 ¶2 | Low — §13 ¶2 fully specifies attestation content |
| **Conformance** | `conformance_claim`, `nonconformance_record`, `non_applicability_statement` | Conformance claims must be tracked as governed objects with their own lifecycle, e.g. for external reporting | §12 ¶1 | Low |
| **Change & Release** | `change_set`, `release`, `rollback_record` | P1 releases software as a governed artifact to external users | §2, §4 ¶5 | Low — `p1-os` packaging exists but is not externally consumed |
| **Audit** | `audit_report`, `audit_finding`, `audit_response` | Recurring formal audits, or an external party audits P1 | §3 ¶5 | Low |
| **Registry Specification** | `registry_schema`, `jurisdiction_declaration`, `registry_transition_record` | Roughly three or more Active standards, where §4 ¶2 overlap rejection stops being trivially verifiable by reading | §4 ¶1-2 | Low at one standard |
| **Conflict Resolution** | `conflict_record` | A same-level conflict actually arises between two Active standards — impossible with one | §4 ¶4 | Low |
| **Emergency & Containment** | `containment_action_record` | First security containment action under §12 ¶2 | §12 ¶2 | Low — §12 ¶2 is self-executing; the record can be written without a standard |

**Never required:** the **Normative Artifact Standard** (proposed as G-2). §9 ¶1 explicitly excepts Domain standards from the per-type ownership rule, and §9 ¶4, §4 ¶1, and §4 ¶2 supply the lifecycle, fields, and activation procedure directly. Activating it would add burden and would require relying on §9 ¶4's "minimum lifecycle" phrase as a delegation — a dependency worth not creating. It is reclassified from Optional to **unnecessary**.

---

## 5. Future extension

No foreseeable trigger in current scope. Listed so the extension point is visible rather than invented later.

| Candidate | Would own | Precondition |
|---|---|---|
| **RS-1 extension: Principle** | `principle` | A generalization survives enough discriminating tests to be worth accepting under §5 ¶6 as provisional, scoped, falsifiable, reversible. Nothing in P1 is close. |
| **Splitting RS-1 into per-type standards** | the ten-standard scientific stack | RS-1 grows past what one document can carry with a single §11 ¶1 responsibility. A refactoring target, never a requirement. §9 ¶1 needs one owner per type, not one type per owner. |
| **Machine learning experimentation** | `training_run`, `checkpoint`, `dataset_version`, `ablation` | ML experiments become governed scientific executions rather than tooling |
| **LLM evaluation** | `eval_suite`, `rubric`, `judge_configuration` | Evaluation output is cited as Evidence. Note §5 ¶7 bars model confidence from counting as Evidence by itself, and §3 ¶7 bars test success from being reported as scientific success |
| **Benchmarking** | `benchmark_definition`, `benchmark_run`, `baseline` | Benchmarks become comparative scientific instruments |
| **Simulation** | `simulation_model`, `parameterization`, `simulation_run` | Simulation output is used inferentially — requires care, since it measures a model, not the world (§2) |
| **Knowledge graphs / neurosymbolic / reasoning systems** | domain-specific | The programme reaches them; each needs §11 ¶3 disambiguation against RS-1's terms |
| **Federation** | `external_partner`, `shared_protocol`, `external_attestation` | Multi-institution work. Attractive because an external partner supplies the Independent reviewer P1 lacks. Multi-repository precedence remains a constitutional gap. |

---

## 6. Summary

| Class | Count | Contents |
|---|---|---|
| Required before adoption | **0** | — |
| Required after adoption | **1** | RS-1 (six object types) |
| Optional | **15** | 3 RS-1 extensions + 12 standalone standards, each with a named trigger |
| Unnecessary | **1** | Normative Artifact Standard (§9 ¶1 carve-out) |
| Future extension | **8** | 1 RS-1 extension + 7 domains |

**The operating rule:** activate on trigger, never on anticipation. Each activation costs one steward approval and one Independent reviewer attestation, and independent review is the project's scarcest resource. §12 ¶1 also makes an unverifiable requirement a nonconformance, so activating a standard the project cannot verify manufactures nonconformance rather than reducing it.

**The one exception to activating late** is `registered_protocol`, which is in the minimum set precisely because its omission cannot be repaired: §5 ¶3 fixes the pre-access condition and §13 ¶4 forbids retroactively altering a prior record's meaning. Everything else can wait until it is actually needed.
