# Domain Standard Interface — the extension point for future domains

- **Status:** Draft
- **Scope:** The constitutional interface that any future Domain standard must satisfy, and the framework by which new scientific, governance, or engineering domains enter P1
- **Responsibility:** Specify the form, not the method, of future domain standards
- **Authority source:** None. This record has no normative authority. On activation it would form part of DG-2.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. The design principle

The brief states it exactly: *"No scientific methodology should be hardcoded. Only constitutional interfaces."*

The Constitution already agrees. §5 ¶6: "No scientific constant, threshold, model, ontology, hypothesis set, or conclusion is constitutional. Such objects MUST be governed by a revisable domain standard or registered protocol." §10 ¶1 removes architecture from constitutional scope. §2 defines a Domain standard as governing "one declared scientific, governance, or engineering domain" — an open set.

So the interface must constrain **form** — declarations, jurisdiction shape, lifecycle completeness, terminology discipline, verification mapping — and must say nothing whatever about **method**. A domain standard for LLM evaluation and one for knowledge graphs must be equally accommodated, and the interface must not encode a preference for either. A useful test: if the interface could not accept a domain that the authors did not anticipate, it is a methodology in disguise.

This interface lives inside **DG-2** rather than as a separate Registry entry, because a framework imposing requirements on Domain standards owns the `domain_standard` object type, which is DG-2's jurisdiction. A separate entry would overlap and be rejected under §4 ¶2.

---

## 2. Required declarations

Every Domain standard MUST declare the following. Absence of any item means the artifact has no authority (§4 ¶1) — this is fail-closed, not a warning.

### 2.1 Identity block (§4 ¶1)

| Field | Requirement | Verified by |
|---|---|---|
| `id` | Unique, from O-1's identifier grammar, never reused | `DA-09` |
| `title` | Human-readable | — |
| `version` | Semantic, per DG-2's scheme | `DA-02` |
| `status` | One of Draft, Active, Superseded, Withdrawn (§9 ¶4) | `DA-02` |
| `scope` | §2-conforming: population, environment, conditions, versions, time interval, sufficiently identifiable for an Independent reviewer | `DA-02`, `MRP-14` |
| `responsibility` | Exactly one primary responsibility (§11 ¶1) | `MRP-14` |
| `authority_source` | The Registry entry and the authority permitted to activate this jurisdiction | `DA-03`, `DA-05` |
| `domain_class` | `scientific` \| `governance` \| `engineering` (§2) | `DA-02` |

The Registry MUST carry the same identity, status, Scope, responsibility, authority, and jurisdiction **without contradiction** (§4 ¶1), checked by `DA-03`.

### 2.2 Jurisdiction declaration (machine-readable)

This is the single most important element of the interface. §4 ¶2 requires the Registry to *reject overlapping normative jurisdictions*, which is undecidable against prose. Jurisdiction is therefore declared as tuples:

```yaml
jurisdiction:
  owned_object_types: [<o-1 type id>, ...]        # each type owned by exactly one standard (§9 ¶1)
  owned_transitions:                               # transition = (type, from_state, to_state)
    - {type: <id>, from: <state>, to: <state>}
  scope:
    population: <...>
    environment: <...>
    conditions: <...>
    versions: <...>
    time_interval: <...>
  referenced_types: [<id>, ...]                    # read-only; MUST NOT impose requirements on these
  not_owned: [<explicit disclaimers>]              # boundaries the standard renounces
```

`not_owned` is not decoration. Explicit renunciation is what makes an adjacent standard's ownership provable rather than merely assumed, and it is the field that catches the most jurisdiction drift over time.

### 2.3 Delegation declarations (§4 ¶4)

Every claimed refinement of a higher-level requirement MUST cite the delegating clause and restate the delegation's five elements:

```yaml
delegations_relied_upon:
  - delegating_clause: "REPOSITORY_CONSTITUTION.md §6 ¶4"
    delegated_subject: "authority, criteria, and recorded procedure for admitting Evidence"
    scope: <...>
    recipient: <this standard's id>
    permitted_transitions: [...]
    limits: <...>
```

A refinement with no citable delegation is void under §4 ¶4, and the check (`DA-63`) must fail the activation rather than warn. Note that three of the delegations this stack relies on are themselves under-specified — defect **DD-1** in `00_ECOSYSTEM_OVERVIEW.md` §8 — so a standard relying on §9 ¶4, §12 ¶4, or §10 ¶1 must say so and accept the recorded weakness.

### 2.4 Lifecycle definition (§9 ¶1, nine elements)

For each owned object type: permitted states; the initial state; entry and exit criteria per state; permitted transitions; the authority for each transition; required transition evidence; reversal and correction procedure; retention rules. Plus the §9 ¶3 requirement that a missing element causes the transition to fail closed.

A standard MUST NOT require or authorize another Domain standard for its own object type (§9 ¶2), and MUST NOT authorize its own activation (§4 ¶2).

### 2.5 Terminology declaration (§11 ¶3)

```yaml
terminology:
  reused_unchanged: [<constitutional and peer terms used as defined>]
  domain_specific: 
    - term: <new term>                # MUST be a different word, or an explicitly qualified form
      definition: <operational>
      disambiguation: <proof that no ambiguity results>
```

§11 ¶3 forbids redefining a higher-level term within its Scope, forbids synonyms creating distinct object types, and forbids identical names concealing distinct types. The `disambiguation` field is where the standard discharges that burden explicitly rather than by assertion.

### 2.6 Verification mapping (§12 ¶1, §12 ¶4)

Every MUST and MUST NOT in the standard MUST map to one of: a registered check id; a named manual review procedure `MRP-xx`; or a testable non-applicability statement.

```yaml
verification:
  - requirement_id: <clause id>
    mechanically_decidable: true|false
    check: <A-xx>            # if decidable
    manual_procedure: <MRP-xx>   # if not
```

This is the field that prevents a standard from being unenforceable by construction. `DA-39` fails any activation with an unmapped MUST. It also implies a practical obligation the Constitution does not currently support well: **requirements need addressable clause identifiers.** The v1.2.0 amendment record already flags this as finding F-19; without clause IDs, the mapping degrades to prose references that no check can follow.

### 2.7 Failure-mode declaration

Each standard declares its own anticipated failure modes with detection and mitigation. This is not a constitutional requirement; it is a design requirement of this interface, justified by §12's insistence that unverifiable requirements be named as such. A standard that cannot say how it fails cannot be reviewed for whether it fails safely.

### 2.8 Migration declaration (§13 ¶4)

How records created under prior versions are treated. §13 ¶4 is absolute: amendments MUST NOT retroactively alter the meaning or reported outcome of a prior scientific record; affected records retain the standard version under which they were created and MAY be reassessed only through a new Interpretation or Decision. Every standard therefore carries `standard_version` on its records and a migration clause stating the reassessment path.

---

## 3. Activation dossier

A new domain enters P1 through one Atomic change (§2, §4 ¶2) containing all of:

1. The reviewed standard, satisfying §2 of this document in full.
2. Its Registry entry with the machine-readable jurisdiction.
3. Its jurisdiction declaration in `registry/jurisdictions/`.
4. Approval by a Registry-listed authority **permitted to activate that jurisdiction** — not merely any authority (§4 ¶2).
5. An Independent reviewer attestation satisfying §13 ¶2 in full, including competence and records examined.
6. An overlap analysis against every Active standard, demonstrating disjointness or citing an explicit delegation of non-conflicting refinement (§4 ¶2).
7. An ontology impact statement: types added, types referenced, terminology introduced.
8. The verification mapping, with every check either already Active or included in the same change.
9. A migration statement for any existing records the standard will govern.

**Batch activation is permitted.** §4 ¶2 requires each activation to be atomic; it does not require each to be alone. Several standards may activate in one Atomic change provided every element above is present for each. This matters practically: the dependency graph makes six standards mutually near-simultaneous, and forcing six separate review cycles would consume the scarcest resource in the project — independent reviewer attention — for no constitutional gain. What batching MUST NOT do is let one attestation cover several standards; §13 requires per-artifact review, so a batch carries one attestation per standard.

**If no authority permitted to activate that jurisdiction exists, activation fails closed** (§4 ¶2). This is currently the state of every jurisdiction in P1.

---

## 4. Candidate future domains

These are illustrative, to demonstrate that the interface accommodates them without prejudging method. None is proposed for activation.

| Candidate domain | Class | Likely owned object types | Interface stress it creates |
|---|---|---|---|
| **Machine learning experimentation** | scientific | `training_run`, `checkpoint`, `dataset_version`, `ablation` | §10 ¶3 material-input recording at dataset scale; nondeterminism that "cannot be controlled MUST be measured or declared" (§10 ¶3) is genuinely hard on GPU |
| **LLM evaluation** | scientific | `eval_suite`, `rubric`, `judge_configuration`, `eval_run` | §3 ¶7's prohibition on reporting test success as scientific success; an LLM judge is a *model*, so §5 ¶7 bars its confidence from counting as Evidence by itself |
| **Benchmarking** | engineering | `benchmark_definition`, `benchmark_run`, `baseline` | Comparability across versions vs §7 ¶1 Result immutability; requires versioned benchmark definitions rather than mutable ones |
| **Simulation** | scientific | `simulation_model`, `parameterization`, `simulation_run` | Distinguishing simulation output from Observation (§2) — simulation output is a measurement *of a model*, not of the world, and conflating them is the domain's characteristic failure |
| **Knowledge graphs** | scientific | `graph_version`, `schema_mapping`, `assertion_set` | §11 ¶3 terminology collision with O-1: a KG "entity" is not a P1 governed object; requires explicit disambiguation |
| **Neurosymbolic systems** | scientific | `symbolic_component`, `neural_component`, `integration_contract` | §5 ¶7's mechanism criterion: an operational test distinguishing "reasoning" from performance is the domain's hardest obligation |
| **Reasoning systems** | scientific | `reasoning_trace`, `derivation`, `soundness_check` | Traces are working output until admitted; §2 forbids citing working output as Evidence |
| **Human subjects research** | scientific | `consent_record`, `participant_cohort` | §10 ¶5 personal material exclusion vs §6 provenance completeness — a genuine tension needing a domain-specific custody arrangement under DG-7 |

Two observations from this table. First, the recurring stress point is not governance mechanics but the **Observation/Evidence boundary** — every computational domain is tempted to treat its own output as an observation of the world. Second, several candidates would need to reference each other (LLM evaluation and benchmarking overlap heavily), which is exactly what the `not_owned` field and the Peer Reference Rule exist to discipline.

---

## 5. What the interface deliberately does not constrain

To make the "form, not method" boundary auditable, the exclusions are stated explicitly. A future Domain standard is free to choose, and the interface must never require:

- statistical framework (frequentist, Bayesian, likelihood, none);
- significance thresholds, effect-size conventions, or multiplicity corrections — §5 ¶3 requires that a protocol *fix* them, not which ones;
- sample size determination method;
- what counts as a strong alternative explanation in the domain;
- measurement instruments, metrics, or their validity criteria;
- replication requirements or their count;
- publication or dissemination practice;
- tooling, language, or file format.

Each of these is method. Encoding any of them here would make P1's constitution silently domain-specific, and would violate §5 ¶6 by fixing scientific choices above the level of a revisable standard. Where the project wants a house convention, it belongs in a domain standard that can be amended — not in the interface every future domain must satisfy.

---

## 6. Interface versioning and the compatibility problem

The interface is part of DG-2 and versions with it. The twenty-year concern is straightforward: an interface change invalidates the declarations of every Active standard simultaneously.

Rules:

1. **Additive changes** (a new optional declaration) are MINOR; existing standards remain conforming and adopt the field at their next revision.
2. **A new required declaration** is MAJOR and MUST be accompanied by a migration plan naming every Active standard and the change set that updates it. Under §2's atomicity rule, an interface version that makes existing standards nonconforming with no migration in the same change produces a revision in which Active standards lack required elements — and §4 ¶1 says such artifacts have no authority. The entire stack would silently lose authority at once. This is the single worst mechanical failure available in this design, and it is why interface MAJOR changes require a named migration plan rather than a generous grace period.
3. **Removing a requirement** is MINOR for conformance purposes but MAJOR for review, since prior attestations relied on it.
4. No interface change may retroactively alter the meaning or outcome of any scientific record (§13 ¶4).
