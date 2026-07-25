# RS-1 — P1 Research Standard

- **Status:** Draft
- **Scope:** All governed scientific execution and inference in Project P1: registered protocols, observations, results, unknowns, decisions, and interpretations, in the repository environment, from activation until superseded
- **Responsibility:** Define this domain's object definitions and scientific lifecycles
- **Authority source:** None while Draft. On activation: the constitutional steward listed in `GOVERNANCE_REGISTRY.yaml`, per `REPOSITORY_CONSTITUTION.md` §4 ¶2
- **Version:** 0.1.0 (draft skeleton)
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0

> **Draft notice.** Under Constitution §4 ¶5 and §9 ¶4, Draft has no authority. The MUST and MUST NOT statements below are the requirements this standard *would* impose once Active; they impose nothing now. This document does not authorize its own activation (§4 ¶2).
>
> **Completion status.** This is a skeleton: every §9 ¶1 element is present in structure, and sections marked **`[COMPLETE BEFORE ACTIVATION]`** need project-specific values. Engineering task E-1 in `00_MINIMUM_ACTIVATION_PLAN.md`.

---

## 1. Jurisdiction

Declared as tuples so §4 ¶2's overlap test is mechanically decidable.

```yaml
owned_object_types:
  [registered_protocol, observation, result, unknown, decision, interpretation]

owned_transitions:
  - {type: registered_protocol, from: draft,      to: registered}
  - {type: registered_protocol, from: draft,      to: withdrawn}     # abandoned before registration
  - {type: registered_protocol, from: registered, to: executing}
  - {type: registered_protocol, from: executing,  to: closed}
  - {type: observation,         from: none,       to: recorded}
  - {type: observation,         from: recorded,   to: superseded}
  - {type: result,              from: none,       to: recorded}
  - {type: result,              from: recorded,   to: superseded}
  - {type: unknown,             from: none,       to: open}
  - {type: unknown,             from: open,       to: resolved}
  - {type: unknown,             from: resolved,   to: open}          # reopening
  - {type: decision,            from: none,       to: proposed}
  - {type: decision,            from: proposed,   to: approved}
  - {type: decision,            from: proposed,   to: withdrawn}     # retracted before approval
  - {type: decision,            from: approved,   to: executed}
  - {type: decision,            from: executed,   to: reversed}
  - {type: interpretation,      from: none,       to: draft}
  - {type: interpretation,      from: draft,      to: active}
  - {type: interpretation,      from: draft,      to: withdrawn}     # abandoned before activation
  - {type: interpretation,      from: active,     to: superseded}
  - {type: interpretation,      from: active,     to: withdrawn}

scope:
  population:    governed scientific execution and inference in Project P1
  environment:   this repository
  conditions:    all
  versions:      RS-1 >= 1.0.0
  time_interval: from activation until superseded or withdrawn

not_owned:
  - "claim, evidence, source, question, hypothesis, principle — no Active standard owns
     these; no record of these kinds may be created until RS-1 is amended to own one
     (§9 ¶1: transitions without a defining standard fail closed under §9 ¶3)."
  - "Normative artifacts and Domain standards — excepted from §9 ¶1; governed by §4 and §9 ¶4."
  - "Repository layout — not constitutional (§10 ¶1); see the architecture record."
```

**Terminology.** Every term used here is reused unchanged from Constitution §2 (§11 ¶3). RS-1 defines no new term and no synonym for a constitutional kind.

**Exit completeness.** §9 ¶3 fails an unlisted transition closed, so any state with no listed exit is a permanent trap: the record can be created and then never disposed of. The three `→ withdrawn` tuples are the abandonment paths for objects that never reach their active state — a `draft` protocol that is never registered, a `proposed` decision that is retracted, a `draft` interpretation that is abandoned. Withdrawal retains the record (§2.5); it is not deletion.

---

## 2. Requirements common to all owned types

**2.1 Transition records.** A transition is valid only when a version-controlled transition record identifies the object, prior state, new state, criteria applied, evidence considered, authority, time, and rationale. Missing information MUST cause the transition to fail closed (§9 ¶3).

**2.2 Authorization.** Every transition in §1 of an owned type **other than `decision`** MUST be authorized by a `decision` approved by the Registry-listed authority permitted for that transition (§4 ¶5). Authoring a record is not authorizing its transition: the actor who writes an Observation or opens an Unknown supplies content, and the Registry-listed authority supplies the authorization. A tool MAY apply an already-authorized transition; it MUST NOT supply the authority (§4 ¶4).

**2.2.1 The `decision` lifecycle is exempt from §2.2, and must be.** §1 owns `{decision, none → proposed}`. Requiring a prior `decision` to authorize it does not terminate, so under an unexempted §2.2 no first `decision` is creatable and therefore no transition of any type is ever authorizable.

The exemption is available without amendment because a `decision` is a **governance** record under §2 and §3 ¶2, not a scientific record. §4 ¶5 governs *scientific* transitions; the transitions of the decision lifecycle itself are governance transitions and fall outside it. Each is instead authorized directly by the authority named in §7, which is Registry-listed for that transition. Every transition RS-1 owns therefore has a named authority, as §9 ¶1 requires, and none depends on itself.

**2.2.2 Coupled transitions.** A single `decision` MAY authorize one transition or one atomic set of explicitly coupled transitions (§11). This is how a governed execution is authorized without one approval per measurement; the coupled set MUST be enumerated in the `decision`, because §11 permits coupling only where it is explicit.

**2.3 No inference of state.** Tools MUST NOT infer maturity, acceptance, or rejection from evidence count, model confidence, test success, or elapsed time (§9 ¶3).

**2.4 Recorded time.** Every time MUST be timezone-qualified and MUST identify its precision where precision can affect the determination (§2).

**2.5 Retention.** Every record of every owned type MUST be retained permanently. A record MUST NOT be physically deleted because it is rejected, superseded, inconvenient, or negative (§8 ¶2).

**2.6 Reversal.** Every state change MUST be reversible by a later authorized `decision`, and reversal MUST preserve the previous state, rationale, supporting records, and transition history (§8 ¶2).

**2.7 Digest algorithm.** Where an artifact is identified by digest, the algorithm is **SHA-256**, algorithm register version **1**, discharging §6 ¶2. A protocol MAY register a stronger algorithm for its own execution; deprecating an algorithm MUST NOT invalidate existing records, and re-digesting MUST create a new linked record rather than editing the prior one.

**2.8 Prohibited labels.** A record MUST NOT use proven, true, final, permanent, or certain of an empirical matter (§8 ¶3). A record MUST NOT declare itself canonical, absolute, frozen, or authoritative (§1 ¶2).

**2.9 Test output.** Passing software tests establishes only conformance to those tests and MUST NOT be reported as scientific success unless a `registered_protocol` independently makes that test output relevant Evidence (§3 ¶7).

**2.10 Common fields.** Every record carries: `id`, `object_type`, `schema_version`, `status`, `scope`, `created`, `created_by`, `provenance`, `rs1_version` (the RS-1 version under which it was created, required by §13 ¶4), `supersedes`, `superseded_by`.

---

## 3. `registered_protocol`

**Definition.** Reused unchanged from §2: an immutable protocol whose registration transition occurred before its governed execution began.

| §9 ¶1 element | Specification |
|---|---|
| Permitted states | `draft`, `registered`, `executing`, `closed`, `withdrawn` |
| Initial state | `draft` |
| Entry criteria — `registered` | All eleven §5 ¶3 elements present and non-empty: sampling frame; sample size or stopping rule; exclusions; assignment; controls; primary outcomes; analysis population; statistical or logical decision rule; multiplicity handling; model selection procedure; randomness plan. Plus: validity criteria determining Valid vs Invalid Result (§2, §7 ¶4); completion criteria (§7 ¶2); the recording authority for Results (§7 ¶2); digest algorithm reference (§2.7). A placeholder value is an absence and fails closed. |
| Entry criteria — `executing` | State is `registered`; registration time strictly precedes the earliest execution evidence |
| Entry criteria — `closed` | The protocol's own completion criteria are met, or the execution is abandoned with disposition and rationale recorded (§7 ¶2) |
| Entry criteria — `withdrawn` | State is `draft`, no governed execution has begun under it, and a statement of why no registration will occur is recorded (§9 ¶4). A `registered` protocol MUST NOT be withdrawn: registration is not reversible, and correction occurs by superseding registration instead |
| Exit criteria | `draft` exits to `registered` or `withdrawn`. **`registered` is terminal for content:** the protocol MUST NOT be edited after registration. A change produces a **new** protocol linked to the prior one, and the affected execution MUST be labelled exploratory (§5 ¶3). `withdrawn` and `closed` are terminal. |
| Permitted transitions | `draft → registered`, `draft → withdrawn`, `registered → executing`, `executing → closed` |
| Authority | The Registry-listed authority permitted for that transition, via an approved `decision` (§4 ¶5, §2.2) |
| Required transition evidence | §2.1 record, plus: for `→ registered`, the completeness attestation of the eleven elements and the registration timestamp with precision; for `→ executing`, the identity of the execution; for `→ closed`, the completion or abandonment determination and its rationale |
| Reversal and correction | Registration is **not reversible**: §2 defines a Registered protocol by registration preceding execution, and reversal would falsify that. Correction occurs only by registering a superseding protocol that identifies the defect. The superseded protocol is retained. |
| Retention | Permanent |

**3.1 Pre-access requirement.** Before any author of, contributor to, or person communicating analysis-relevant information to a confirmatory analysis accesses an unblinded Observation or any data revealing condition or outcome, the protocol MUST be `registered` (§5 ¶3). Any element selected or changed after such access MUST be labelled exploratory and MUST NOT be represented as confirmatory Evidence for that execution.

**3.2 Known limitation, recorded as an Unknown at activation.** Registration ordering is verifiable from within the repository only to the extent commit metadata is trustworthy, and commit timestamps are author-controlled. §5 ¶3's actual trigger is unblinded *access*, which may leave no trace. RS-1 therefore requires an external timestamp anchor for any protocol supporting a confirmatory analysis. **`[COMPLETE BEFORE ACTIVATION]`** — name the anchor mechanism, or record the residual exposure as a standing `unknown` and label all analyses exploratory until one exists.

---

## 4. `observation`

**Definition.** Reused unchanged from §2: a recorded measurement or Source statement before it is used to support or oppose a Claim.

| §9 ¶1 element | Specification |
|---|---|
| Permitted states | `recorded`, `superseded` |
| Initial state | `recorded` |
| Entry criteria — `recorded` | Measured value or Source statement; measurement procedure; instrument or method; origin identification; acquisition time with precision; actor or process; environment and configuration; blinding status; known measurement limitations; digest of any external raw artifact |
| Entry criteria — `superseded` | A new Observation exists identifying the defect in the prior one |
| Exit criteria | `recorded` exits only to `superseded`. Content is append-only: an Observation MUST NOT be edited after recording. |
| Permitted transitions | `none → recorded`, `recorded → superseded` |
| Authority | Recording and superseding: the Registry-listed authority permitted for that transition, via an approved `decision` (§4 ¶5, §2.2). The executing actor under a `registered_protocol` **authors** the record; authorship is not authority (§4 ¶4), and RS-1 cannot enlarge who may authorize (§4 ¶3) |
| Required transition evidence | §2.1 record, plus the measurement provenance above |
| Reversal and correction | By a new linked Observation only; the prior Observation is retained with its status |
| Retention | Permanent |

**4.1 Object-kind boundary.** An Observation MUST NOT state the Claim it supports, and MUST NOT contain an inference. §2's final paragraph forbids using one object kind as a substitute for another. An Observation records what was measured; an `interpretation` records what it means.

**4.2 Blinding.** Blinding status MUST be recorded, because §5 ¶3's pre-access condition is defined in terms of unblinded access. An unblinding event MUST be recorded as it occurs.

**4.3 Source identification.** Where the Observation derives from a Source, the Source MUST be identified within the Observation record. RS-1 does not own `source` as a separate type; a citation alone is not Evidence and, absent an Active Evidence standard, MUST NOT be represented as one (§6 ¶4).

---

## 5. `result`

**Definition.** Reused unchanged from §2: an immutable record of measurements and protocol facts created when working output enters the Result lifecycle.

| §9 ¶1 element | Specification |
|---|---|
| Permitted states | `recorded`, `superseded` |
| Initial state | `recorded` |
| Entry criteria — `recorded` | The governing protocol's completion criteria are met (§7 ¶2); measurements and protocol facts; all Material inputs and outputs recorded or content-addressed (§10 ¶3); for randomized execution, the generator, seed or equivalent state, and sampling procedure (§10 ¶3); uncontrollable nondeterminism measured or declared as a limitation (§10 ¶3); a validity determination against the protocol's registered criteria, citing those criteria; disposition and rationale (§7 ¶2) |
| Entry criteria — `superseded` | A new Result exists identifying the error and the superseded content, and stating whether and to what Scope the prior Result is invalid, corrected, or superseded for inference (§7 ¶1) |
| Exit criteria | **A Result is immutable from the transition that creates it** (§7 ¶1). There is no edit path. `recorded` exits only to `superseded`. |
| Permitted transitions | `none → recorded`, `recorded → superseded` |
| Authority | The Registry-listed authority permitted for that transition, via an approved `decision` (§4 ¶5, §2.2). The protocol's named recording authority (§7 ¶2) identifies who **authors** the Result; authorship is not authority (§4 ¶4) |
| Required transition evidence | §2.1 record, plus the validity determination with criteria cited, and the content digest of the Result at creation |
| Reversal and correction | Correction MUST occur through a new linked Result. History MUST NOT be rewritten to conceal a prior Result (§7 ¶1). Later Evidence or Interpretation relying on a superseded Result MUST disclose that status. |
| Retention | Permanent |

**5.1 Validity.** A `result` records a validity determination of `valid` or `invalid` against the criteria registered *before* execution. Validity is independent of favourability (§2). A validity criterion MUST NOT reference whether the outcome was desired. An Invalid Result MAY be excluded from inference only by its protocol's registered validity rule, with the Result and the applied rationale preserved (§7 ¶4).

**5.2 Negative Results.** A Valid Result that fails a success criterion, supports a null, or counts against a proposition is a Negative Result and MUST be retained under identical provenance and retention rules. It MUST NOT be deleted, hidden, relabelled as a failed run, or excluded from synthesis solely because it opposes a preferred conclusion (§7 ¶4).

**5.3 Abandoned execution.** An execution that does not reach completion MUST be recorded as a `result` with disposition `abandoned`, retaining its rationale (§7 ¶2). Abandonment is not deletion.

**5.4 Working output.** Material that has not entered this lifecycle is working output and MUST NOT be cited as Evidence (§2). All pre-activation execution artifacts are working output and cannot become confirmatory Results, because no Registered protocol preceded them.

---

## 6. `unknown`

**Definition.** Reused unchanged from §2: a recorded question or uncertainty not resolved to the standard required for a Claim. §8 ¶1: Unknown is a permanent first-class object kind.

| §9 ¶1 element | Specification |
|---|---|
| Permitted states | `open`, `resolved` |
| Initial state | `open` |
| Entry criteria — `open` | Statement of what is not known; scope; why it is material; the resolution criterion, stated operationally; consequences if unresolved; affected records by reference |
| Entry criteria — `resolved` | Evidence meeting **the resolution criterion recorded at open time**. A criterion rewritten at resolution time does not satisfy this. |
| Exit criteria | `resolved` may return to `open` at any time (reopening), with rationale. Resolution changes state only; it MUST NOT remove the record, the kind, or its history (§8 ¶1). |
| Permitted transitions | `none → open`, `open → resolved`, `resolved → open` |
| Authority | Opening, resolving, and reopening: the Registry-listed authority permitted for that transition, via an approved `decision` (§4 ¶5, §2.2). Any contributor MAY **author** a proposed `unknown`; see §6.3 |
| Required transition evidence | §2.1 record, plus the resolution evidence assessed against the original criterion |
| Reversal and correction | Reopening is always permitted and requires no special authority beyond a `decision` |
| Retention | Permanent. Deletion is prohibited absolutely. |

**6.1 Mandatory intake triggers.** Each of the following MUST be recorded as an `unknown` rather than silently closed (§8 ¶1): material missing information; unresolved contradiction; untested assumption; failed replication; unexplained anomaly. Additionally: a Question or uncertainty material to an Interpretation, Decision, or Result validity (§2); an input that cannot be retained, with its absence, reason, expected effect, and recovery status (§6 ¶5); and an Interpretation for which no materially distinct alternative was found, recording the search and its limits (§5 ¶5).

**6.2 Unknowns required at activation.** **`[COMPLETE BEFORE ACTIVATION]`** — open, at minimum: the registration-ordering exposure (§3.2); the absence of an Active standard owning `claim` and `evidence`, which limits what any Interpretation may assert; the disposition status of Legacy scientific content; and the approval-throughput exposure in §6.3.

**6.3 Intake is not gated by authority.** §8 ¶1 makes recording a material uncertainty obligatory, while §2.2 puts the `open` transition behind an approved `decision`. Those two pull in opposite directions, and the resolution is that **authoring is unrestricted**: any contributor MAY write an `unknown` in the `proposed` form at any time, without approval and without delay. The authority approves the transition to `open`; it does not decide whether the uncertainty exists. An authority that declines to open a material uncertainty does not thereby discharge §8 ¶1, and the unresolved proposal MUST itself be retained (§2.5).

This is the point where RS-1's approval load is highest and most likely to bind in practice. The exposure is recorded as an activation Unknown under §6.2 rather than engineered away, because reducing it requires either a second Registry-listed authority or a §4 ¶4 delegation — both of which are Registry changes under §4, not RS-1's to make (§4 ¶3).

---

## 7. `decision`

**Definition.** Reused unchanged from §2: a governance record authorizing declared transitions or actions. It references but does not contain Evidence or Interpretations, and it does not make its rationale true.

Owned by RS-1 under the explicit permission of §9 ¶2 ("MAY govern subordinate Registered protocols, **Decisions**, and scientific records").

| §9 ¶1 element | Specification |
|---|---|
| Permitted states | `proposed`, `approved`, `executed`, `reversed`, `withdrawn` |
| Initial state | `proposed` |
| Entry criteria — `proposed` | Identifies exactly one transition, or one atomic set of explicitly coupled transitions enumerated in full (§11, §2.2.2); the specifying standard clause; the records relied upon, by reference only; the rationale; the named reversal path |
| Entry criteria — `approved` | Approved by the Registry-listed authority permitted for that specific transition (§4 ¶5) |
| Entry criteria — `executed` | The authorized transition has occurred and its §2.1 transition record exists |
| Entry criteria — `reversed` | A later `decision` reverses it, preserving the previous state, rationale, supporting records, and transition history (§8 ¶2) |
| Entry criteria — `withdrawn` | State is `proposed`, the proposal is retracted before approval, and the rationale for retraction is recorded. The record is retained (§2.5); withdrawal is not deletion |
| Exit criteria | `proposed` exits to `approved` or `withdrawn`; `approved` exits to `executed`; `executed` exits to `reversed`. `reversed` and `withdrawn` are terminal |
| Permitted transitions | `none → proposed`, `proposed → approved`, `proposed → withdrawn`, `approved → executed`, `executed → reversed` |
| Authority | Authoring (`none → proposed`) and retraction (`proposed → withdrawn`): any contributor, recorded without a prior `decision` per §2.2.1. Approval, execution, and reversal: the Registry-listed authority permitted for that transition. Automation MAY apply an approved decision; it MUST NOT approve one (§4 ¶4). |
| Required transition evidence | §2.1 record, plus the approving authority's Registry-listed identity and the transition tuple approved |
| Reversal and correction | By a later `decision`; never by edit or deletion |
| Retention | Permanent, append-only |

**7.1 Separation.** A `decision` MUST NOT alter an Observation or Result (§3 ¶6). Governance approval MUST NOT be represented as scientific support (§3 ¶6). A `decision` MUST NOT embed the content of records it cites; it references them (§2).

**7.2 Fail closed.** A `decision` whose approving authority is not Registry-listed and permitted for that transition does not authorize it, and the dependent transition fails closed (§4 ¶2, §9 ¶3). This is checked against `GOVERNANCE_REGISTRY.yaml` → `authority_assignments`, which MUST list the transition tuple among that authority's permitted transitions; §4 ¶1 voids an authority whose permitted transitions are absent or inconsistent.

**7.3 Self-authorization is barred, self-reference is not.** A `decision` MUST NOT authorize its own approval, and no `decision` is required to author another (§2.2.1). The distinction matters: exempting the decision lifecycle removes an infinite regress, it does not create a route by which an actor approves their own authorization. Approval remains with the Registry-listed authority in every case, and §4 ¶4 bars automation from supplying it.

---

## 8. `interpretation`

**Definition.** Reused unchanged from §2: a scoped inference from identified Evidence or Results. Because no Active standard owns `evidence`, every Interpretation under RS-1 v0.1 infers from **Results** only.

| §9 ¶1 element | Specification |
|---|---|
| Permitted states | `draft`, `active`, `superseded`, `withdrawn` |
| Initial state | `draft` |
| Entry criteria — `active` | Input Results by reference; Scope; assumptions; competing explanations; uncertainty (§7 ¶3). Plus, per §5 ¶5: a null explanation; the strongest materially distinct alternative identified by a documented literature, model, or causal search, with method, sources, date, and limits; and an Observation or experiment capable of discriminating among them. Where no materially distinct alternative is found, a linked `unknown` records the search and its limits, and the Interpretation MUST NOT assert uniqueness. |
| Entry criteria — `superseded` | A replacement Interpretation exists and is identified |
| Entry criteria — `withdrawn` | A statement of why no replacement applies (§9 ¶4). From `draft`, this is abandonment before activation; from `active`, retraction of an activated inference. Either way the record is retained (§2.5) |
| Exit criteria | `draft` exits to `active` or `withdrawn`; `active` exits to `superseded` or `withdrawn`. `superseded` and `withdrawn` are terminal |
| Permitted transitions | `none → draft`, `draft → active`, `draft → withdrawn`, `active → superseded`, `active → withdrawn` |
| Authority | The Registry-listed authority permitted for that transition, via an approved `decision` (§4 ¶5, §2.2) |
| Required transition evidence | §2.1 record, plus the §5 ¶5 triple (null, strongest alternative with search, discriminator) |
| Reversal and correction | By supersession or withdrawal; the prior Interpretation is retained |
| Retention | Permanent |

**8.1 Scope discipline.** An Interpretation MUST distinguish description from inference and MUST NOT generalize beyond the narrowest material limitation of its inputs without additional justification (§7 ¶3).

**8.2 What may not count as support.** A biological analogy, metaphor, mechanism name, model confidence, performance improvement, citation count, authority statement, or the absence of an identified alternative MUST NOT by itself support an Interpretation (§5 ¶7). A claim of mechanism or understanding requires an operational criterion distinguishing it from prediction or performance alone (§5 ¶7).

**8.3 Superseded inputs.** An Interpretation relying on a Result later corrected or superseded MUST disclose that status (§7 ¶1).

**8.4 Limit of RS-1 v0.1.** An Interpretation MUST NOT assert that a proposition is supported or opposed as a Claim, because no Active standard owns `claim` and §5 ¶2's eight requirements cannot be discharged. Findings are expressed as scoped inferences over identified Results. Amending RS-1 to own `claim` and `evidence` is the expected first extension.

---

## 9. Verification mapping

§12 ¶1 requires every Affected MUST to trace to a check, a named manual procedure, or a testable non-applicability statement.

**Namespace.** Automated checks are `A-xx`, implemented in `scripts/governance/check_adoption.py`. That is the only check namespace in this repository; no `C-xx` identifier is in use. A check marked **[NOT IMPLEMENTED]** does not exist: under §12 ¶1 it MUST be reported as not verified and MUST NOT be cited as passed, and no requirement below rests on it alone. Manual procedures are `P-xx`, defined in §9.1 within this document so that RS-1 does not depend on a Draft Level-4 record for its own verification (§4 ¶3).

| Requirement | Mechanically decidable | Verified by |
|---|---|---|
| §2.1 eight-element transition record | yes | `P-8` — decidable, but no implemented check assesses it |
| §2.2 authorization by a permitted Registry-listed authority | yes | `P-9` — resolves the approving authority and the transition tuple against the Registry |
| §2.5 retention / no deletion | yes | `P-10` |
| §2.8 prohibited labels | yes | `A-05` |
| §3 eleven §5 ¶3 elements present, no placeholders | yes | `A-11` **[NOT IMPLEMENTED]** |
| §3 registration precedes execution | partially | `P-11`, advisory without an external anchor (§3.2) |
| §3 protocol immutable after registration | yes | `P-10`, applied to registered protocols |
| §4 Observation contains no inference | no | `P-1` |
| §5 Result immutability and digest match | yes | `P-10` |
| §5.1 validity criteria registered before execution | yes | `A-12` **[NOT IMPLEMENTED]** — compares cited criteria against the protocol at registration |
| §5.2 Negative Results retained | partially | `A-13` **[NOT IMPLEMENTED]**, advisory: compares execution evidence to recorded Results; `P-2` |
| §2.9 test success not reported as scientific success | no | `P-3` |
| §6.1 mandatory Unknown intake triggers | no | `P-4` |
| §6.3 authoring an Unknown is not gated by authority | no | `P-4` |
| §7.1 Decision embeds no cited content | partially | `A-14` **[NOT IMPLEMENTED]**; `P-5` |
| §8 Interpretation null + alternative + discriminator present | yes | `A-15` **[NOT IMPLEMENTED]** |
| §8 alternative is genuinely the strongest; scope is honest | no | `P-6` |
| §8.1 no generalization beyond narrowest input limitation | no | `P-6` |
| §8.2 prohibited support forms | partially | `A-05` lexical; `P-7` |

Five checks — `A-11` … `A-15` — are specified and unbuilt. Building them is RS-1's §11 pre-activation item; until then each of their rows rests on the paired manual procedure or is reported not verified. No row cites a check that does not exist without saying so.

### 9.1 Named manual review procedures (§12 ¶4)

Each states its question and its method; a finding is recorded per review. `P-8` … `P-11` cover the requirements that are mechanically decidable but have no implemented check.

| Id | Question | Method |
|---|---|---|
| `P-1` | Does this Observation contain an inference? | Read for interpretive verbs; test whether the text asserts what the measurement means rather than what it was |
| `P-2` | Were any Results not recorded? | Reconcile execution evidence — logs, digests, compute records — against recorded Results; question the executor about gaps |
| `P-3` | Is test success being reported as scientific success by paraphrase? | Read every record citing pass rates, coverage, or suite outcomes; confirm a protocol makes that output relevant Evidence |
| `P-4` | Has each of the mandatory Unknown triggers been checked, and was any proposed `unknown` left unopened? | Walk the change for the §6.1 triggers; confirm each is absent or recorded as an `unknown`; list every proposed-but-unopened `unknown` and the authority's stated reason (§6.3) |
| `P-5` | Does this Decision make its own rationale true? | Confirm it authorizes only, references rather than embeds, and claims no scientific support |
| `P-6` | Is the alternative genuinely strongest, and the scope honest? | Independently search for a stronger alternative; test the null's non-triviality; recompute the narrowest material limitation of the inputs and compare to the declared scope |
| `P-7` | Does support rest on analogy, confidence, performance, or citation alone? | Trace each supporting element to a Result; reject those resting only on §5 ¶7's prohibited forms |
| `P-8` | Does each transition record carry all eight §9 ¶3 elements? | For every transition record in the change, confirm object, prior state, new state, criteria applied, evidence considered, authority, time, and rationale are each present and non-empty. A placeholder is an absence and fails the transition closed |
| `P-9` | Was each transition authorized by an authority permitted for it? | For each transition record, locate the approving `decision`; confirm the approver appears in `GOVERNANCE_REGISTRY.yaml` → `authority_assignments` and that the exact transition tuple appears among that authority's permitted transitions (§4 ¶1, §7.2) |
| `P-10` | Was any governed record deleted, edited, or replaced in place? | Diff the change against the prior revision over the record paths; confirm no record file is deleted, and that no `result`, `observation`, or registered protocol is modified rather than superseded by a new linked record (§2.5, §5, §7 ¶1) |
| `P-11` | Did registration precede execution? | Compare the registration transition record's time against the earliest execution evidence. Advisory only: commit timestamps are author-controlled and §5 ¶3's trigger is unblinded access, which may leave no trace (§3.2). Without an external anchor, record the residual exposure rather than reporting the ordering as verified |

---

## 10. Amendment and migration

**10.1 Lifecycle.** RS-1 uses the §9 ¶4 minimum lifecycle: `Draft → Active → Superseded or Withdrawn`. Prior versions remain recoverable. RS-1 MUST NOT authorize its own activation (§4 ¶2), and MUST NOT require another Domain standard for any object type it owns (§9 ¶2).

**10.2 Versioning.** MAJOR: a changed or removed requirement, or a jurisdiction change. MINOR: an added requirement or a newly owned object type that no existing record violates — the expected path for adding `claim` and `evidence`. PATCH: non-normative clarification only.

**10.3 Migration.** Every record carries `rs1_version` (§2.10). An amendment MUST NOT retroactively alter the meaning or reported outcome of any prior record (§13 ¶4). Records retain the version under which they were created and MAY be reassessed only through a new Interpretation or Decision.

**10.4 Adding an object type.** A MINOR amendment adding a type requires: the type's nine §9 ¶1 elements; confirmation that no other Active standard owns it (§9 ¶1); a verification mapping for each new MUST; and removal of the type from §1's `not_owned` list. One steward approval and one Independent reviewer attestation, in one atomic change (§4 ¶2).

---

## 11. Pre-activation checklist

- [ ] §3.2 external timestamp anchor named, or the exposure recorded as a standing `unknown`
- [ ] §6.2 activation Unknowns opened, including the §6.3 throughput exposure
- [ ] Checks `A-11` … `A-15` built
- [ ] Procedures `P-1` … `P-11` written to be executable by a reviewer who did not author the change
- [ ] Record templates for six types, including the §2.1 transition record
- [ ] Registry entry drafted with the §1 jurisdiction tuples — all **21**, including the three `→ withdrawn` exits
- [ ] The Registry lists an authority whose permitted transitions cover every transition in §1; §4 ¶1 voids an authority whose permitted transitions are absent or inconsistent
- [ ] Every MUST in this document appears in the §9 mapping
- [ ] Constitution is Active and a steward is assigned — RS-1 cannot activate before adoption
