# Project P1 Repository Constitution

- **Status:** Draft; proposed for activation under Section 13
- **Scope:** All version-controlled research, governance, software, data descriptions, and documentation in Project P1
- **Responsibility:** Define repository-wide authority boundaries and epistemic invariants
- **Authority source:** Initial dual-human adoption or later amendment authority under Section 13
- **Authority jurisdiction:** Activation, amendment, supersession, or withdrawal of this Constitution
- **Version:** 1.2.0

## 1. Normative force

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative. A MUST or MUST NOT is satisfied only when repository evidence permits an independent reviewer to determine compliance. A SHOULD or SHOULD NOT may be departed from only when the affected record states the reason, risk, and scope of the departure. MAY indicates permission, not obligation, and does not imply that conduct not stated with MAY is prohibited unless another requirement prohibits it.

This Constitution is the highest repository governance standard. It governs process and authority; it does not establish scientific truth. A document, role, tool, test, model, or repository state MUST NOT override this Constitution by declaring itself canonical, absolute, frozen, or authoritative.

## 2. Operational definitions

For this Constitution:

- **Repository evidence** is version-controlled content or a content-addressed external artifact whose identity, provenance, and recovery procedure are version-controlled.
- **Scope** is the explicit population, environment, conditions, versions, and time interval to which a statement applies. Scope terms MUST be sufficiently identifiable for an Independent reviewer to determine whether a specified artifact, event, or observation is within them.
- **Question** is a recorded request for knowledge that directs investigation without asserting an answer. A Question is not necessarily an Unknown; a Question or uncertainty that is material to a Claim, Interpretation, Decision, Result validity, or governed transition MUST be recorded as an Unknown until resolved to the applicable standard.
- **Source** is an identified origin of an Observation, such as an instrument, dataset, publication, repository, or actor statement.
- **Observation** is a recorded measurement or Source statement before it is used to support or oppose a Claim.
- **Evidence** is an Observation admitted for a stated Claim under declared provenance, relevance, and validity conditions.
- **Claim** is a proposition that is assessable as supported, opposed, or unresolved within a stated Scope.
- **Operational** means specified in terms of observable inputs, procedures, measurements, decision rules, or reproducible transformations sufficient for an Independent reviewer to determine how the term is applied and what outcome would distinguish its asserted condition from alternatives.
- **Hypothesis** is a Claim paired with an operational test and a possible outcome that counts against it.
- **Working output** is mutable execution material that has not entered a scientific lifecycle and MUST NOT be cited as Evidence.
- **Result** is an immutable record of measurements and protocol facts created when working output enters the Result lifecycle.
- **Interpretation** is a scoped inference from identified Evidence or Results.
- **Decision** is a governance record authorizing declared transitions or actions. It references but does not contain Evidence or Interpretations, and it does not make its rationale true.
- **Principle** is a provisional, scope-bounded generalization accepted under a declared scientific standard.
- **Unknown** is a recorded question or uncertainty not resolved to the standard required for a Claim.
- **Scientific record** is a Question, Observation, Evidence record, Claim, Hypothesis, Result, Interpretation, Principle, or Unknown.
- **Normative artifact** is a document that imposes requirements on other artifacts or actions.
- **Domain standard** is a Normative artifact governing one declared scientific, governance, or engineering domain.
- **Registered protocol** is an immutable protocol whose registration transition occurred before its governed execution began.
- **Active** means, for a Normative artifact, accepted under its lifecycle and listed as Active in the Governance Registry; for any other governed object, entered into its Active state under the applicable Domain standard.
- **Atomic change** means one accepted default-branch repository revision that contains every required artifact, Registry entry, approval, attestation, and transition record, with no intervening default-branch revision in which any required element is absent.
- **Governance Registry** is `GOVERNANCE_REGISTRY.yaml`, whose sole responsibility is to identify active Normative artifacts, their non-overlapping jurisdictions, and authority assignments.
- **Implementation artifact** is code, configuration, schema, infrastructure, or documentation whose correctness is an engineering question.
- **Validation** is a comparison of an artifact or output with criteria declared before the comparison.
- **Authority** is permission to approve specified transitions within a stated jurisdiction. Authority is not Evidence and cannot determine truth.
- **Independent reviewer** is an identified human who is not an author of the reviewed change, did not produce the Evidence under review, and declares any material conflict of interest. A conflicted reviewer is not independent for that review.
- **Affected requirement** is a requirement whose subject, condition, output, evidence, or enforcement can change because of the reviewed change.
- **Valid Result** is a Result satisfying the validity criteria registered for its protocol; an **Invalid Result** fails at least one such criterion. Validity is independent of favorability.
- **Material** means capable, under the stated Scope and a documented reasonable assessment, of changing a scientific conclusion, validity determination, governance transition, externally observable software behavior, or an Independent reviewer’s assessment of conflict.
- **Material state** is any state capable of changing a scientific output, governance transition, or externally observable software behavior.
- **Falsifiable** means that, within its stated Scope, a Claim, Hypothesis, or Principle identifies at least one feasible Observation, test outcome, or Result that would count against it under its declared decision rule.
- **Recorded time** MUST use an unambiguous, timezone-qualified representation and identify its precision when that precision can affect the governed determination.
- **Negative Result** is a Valid Result that fails a success criterion, supports a null result, or counts against a Claim.
- **Confirmatory analysis** is an analysis represented as testing a Claim under the elements fixed by a Registered protocol before the access specified in Section 5. **Exploratory analysis** is any analysis not meeting that condition.
- **Reported as scientific success** means representing, in a version-controlled scientific record, Decision, Result, Interpretation, Claim, or conformance record, test success as support for a scientific conclusion.

Observation, Evidence, Interpretation, Decision, and Principle are distinct object kinds. A record MUST NOT use one kind as a substitute for another.

## 3. Separation of responsibilities

The following responsibilities MUST remain separate:

1. Scientific records describe questions, Unknowns, Claims, methods, Observations, Results, Interpretations, and Principles.
2. Governance records, including Decisions, define authority, required process, lifecycle, and acceptance.
3. Implementation artifacts realize behavior.
4. Validation artifacts assess declared criteria.
5. Audit records report observed conformance at a stated revision and time.

An artifact MUST have one primary responsibility. It MAY reference artifacts with other responsibilities but MUST NOT silently perform their transitions. In particular:

- implementation MUST NOT validate itself merely by executing successfully;
- validation MUST NOT alter the object it assesses;
- an audit MUST NOT create or amend the requirement it audits;
- a Result MUST NOT contain an Interpretation or Decision;
- an Interpretation MUST NOT alter a Result;
- a Decision MUST NOT alter an Observation or Result;
- governance approval MUST NOT be represented as scientific support;
- scientific support MUST NOT grant repository authority.

Passing software tests establishes only conformance to those tests. It MUST NOT be reported as scientific success unless a Registered protocol independently makes that test output relevant Evidence.

## 4. Authority and precedence

Every Normative artifact MUST state its status, Scope, responsibility, and authority source. Every authority source MUST identify its jurisdiction and permitted transitions. The Governance Registry MUST contain the same identity, status, Scope, responsibility, authority, and jurisdiction without contradiction. If any required field is absent or inconsistent, the artifact has no authority.

The Governance Registry MUST reject overlapping normative jurisdictions unless one entry explicitly delegates a non-conflicting refinement to the other. To activate a Domain standard, one atomic change MUST include the reviewed standard and its Registry entry, approval by a Registry-listed authority permitted to activate that jurisdiction, and an Independent reviewer attestation satisfying Section 13. If no such authority exists, activation fails closed. A standard MUST NOT authorize its own activation.

Authority is ordered as follows:

1. this Constitution;
2. an Active Domain standard;
3. an Active Registered protocol or Decision authorized by that standard;
4. implementation and explanatory documentation.

A lower level MUST NOT contradict or enlarge the jurisdiction of a higher level. A narrower artifact MAY refine a higher-level requirement only where the higher level explicitly delegates refinement. A delegation of refinement MUST identify the delegated subject, Scope, recipient artifact or role, permitted transitions, and limits. A refinement MUST NOT create authority over a transition, object type, or jurisdiction not expressly delegated. Conflicting requirements at the same level are both nonconforming until the authority for their common parent jurisdiction resolves the conflict; recency alone MUST NOT decide precedence.

Repository access controls authorize incorporation of changes into the default branch. They do not authorize a scientific transition. A scientific transition MUST be specified by an Active Domain standard and authorized by a Decision approved by the Registry-listed authority for that transition. Automated systems MAY propose, check, or apply an already-authorized transition; they MUST NOT supply human authority or independent review.

Historical, superseded, rejected, withdrawn, archived, generated, legacy, and Draft artifacts have no normative authority. Their content MUST remain distinguishable from Active requirements.

## 5. Scientific claims

Every Claim MUST state its Scope and at least one feasible Observation, test outcome, or Result that could count against it. This requirement does not by itself require a declared decision rule; a Claim is Falsifiable only when it also satisfies the decision-rule condition in Section 2.

Every Claim that is used to justify a scientific conclusion or action MUST state:

1. its operational terms;
2. its Scope;
3. the observations that could support it;
4. the observations that could count against it;
5. credible competing explanations, including a null where applicable;
6. the rule by which evidence changes its state;
7. its unresolved assumptions and limitations;
8. links to the Evidence, Interpretations, and Decisions on which its current state depends.

Before any author of, contributor to, or person communicating analysis-relevant information to a confirmatory analysis accesses an unblinded Observation or any data that reveals condition or outcome, a Registered protocol MUST fix the sampling frame, sample size or stopping rule, exclusions, assignment, controls, primary outcomes, analysis population, statistical or logical decision rule, multiplicity handling, model selection procedure, and randomness plan. Any element selected or changed after such access MUST be labeled exploratory and MUST NOT be represented as confirmatory Evidence for that execution.

Every Active Interpretation MUST record a null explanation and the strongest materially distinct alternative identified by a documented literature, model, or causal search. It MUST state an Observation or experiment capable of discriminating among them. If no materially distinct alternative is found, the search and its limits MUST be recorded as an Unknown; absence of an identified alternative MUST NOT support uniqueness.

A biological analogy, metaphor, mechanism name, model confidence, performance improvement, citation count, authority statement, or absence of an alternative MUST NOT by itself count as Evidence. A claim of mechanism or understanding requires an operational criterion that distinguishes it from prediction or performance alone.

Every Principle MUST remain falsifiable, reversible, and explicitly scoped. No scientific constant, threshold, model, ontology, hypothesis set, or conclusion is constitutional. Such objects MUST be governed by a revisable domain standard or registered protocol.

## 6. Evidence and provenance

Evidence MUST identify:

- the Claim for which it is relevant;
- the underlying Observation or Source;
- acquisition or generation method;
- responsible actor or process;
- time of acquisition or generation;
- code, configuration, data, environment, and randomness inputs material to reproduction;
- transformations from source to reported value;
- validity limitations and known missing information;
- an immutable identifier or digest when content may exist outside Git.

When an external artifact is identified by a digest, the applicable Domain standard or Registered protocol MUST specify a collision-resistant digest algorithm and version.

Evidence MUST NOT be promoted, demoted, or discarded because of agreement or disagreement with a preferred conclusion. Inclusion, exclusion, stopping, and transformation rules MUST be declared before confirmatory analysis. Post hoc changes MUST be preserved and labeled.

The applicable Domain standard or Registered protocol MUST define the authority, criteria, and recorded procedure for admitting, excluding, or revising Evidence for a Claim. An admission or exclusion record MUST state the relevant provenance, relevance, and validity conditions.

A citation identifies a Source; it is not Evidence until the relevant bounded observation and its provenance are recorded. Derived summaries MUST link to their inputs and method. If an input cannot be retained, its absence, reason, expected effect, and recovery status MUST be recorded as an Unknown or limitation.

## 7. Results, interpretations, and negative findings

A Result MUST be immutable from the transition that creates it from working output. Correction MUST occur through a new linked Result that identifies the error and superseded content; history MUST NOT be rewritten to conceal the prior Result. The linked correction MUST state whether and to what Scope the prior Result is invalid, corrected, or superseded for inference; later Evidence or Interpretation that relies on the prior Result MUST disclose that status.

An applicable Domain standard or Registered protocol MUST define when a governed execution is complete and the time and authority for recording its working output as a Result, Invalid Result, or preserved abandoned execution, with the disposition and rationale recorded.

Every Interpretation MUST identify its input Results or Evidence, Scope, assumptions, competing explanations, and uncertainty. It MUST distinguish description from inference and MUST NOT generalize beyond the narrowest material limitation of its inputs without additional justification.

Negative Results MUST be retained under the same provenance and retention rules as positive Results. A Valid Negative Result MUST NOT be deleted, hidden, relabeled as a failed run, or excluded from synthesis solely because it opposes a preferred Claim. An Invalid Result MAY be excluded from inference only by its Registered protocol's validity rule, with the Result and applied rationale preserved.

## 8. Unknowns and reversibility

Unknown is a permanent first-class object kind. Resolving one Unknown MAY change its state but MUST NOT remove the kind or erase its history. Material missing information, unresolved contradiction, untested assumption, failed replication, and unexplained anomaly MUST be represented as Unknowns rather than silently closed.

Every scientific state change MUST be reversible by a later authorized Decision. Reversal MUST preserve the previous state, rationale, supporting records, and transition history. Scientific records MUST NOT be physically deleted merely because they are rejected, superseded, inconvenient, or negative.

No status label may imply certainty beyond its operational definition. Labels such as proven, true, final, permanent, or certain MUST NOT be used for empirical Claims unless the applicable standard defines a bounded technical meaning that does not imply infallibility.

## 9. Lifecycles and transitions

Except for this Constitution and the Governance Registry, whose initial activation is governed by Section 13, and Domain standards, whose activation is governed by Section 4, every subordinate scientific or governance object type MUST have exactly one Active Domain standard within a given Scope defining:

- permitted states;
- the initial state;
- entry and exit criteria for each state;
- permitted transitions;
- the authority for each transition;
- required transition evidence;
- reversal and correction procedure;
- retention rules.

A Domain standard uses the Normative artifact lifecycle defined below. It MAY govern subordinate Registered protocols, Decisions, and scientific records; it MUST NOT require or authorize another Domain standard for its own object type.

A transition is valid only when a version-controlled transition record identifies the object, prior state, new state, criteria applied, evidence considered, authority, time, and rationale. Missing information MUST cause the transition to fail closed. Tools MUST NOT infer scientific maturity, acceptance, or rejection from evidence count, model confidence, test success, or elapsed time.

Normative artifacts use the minimum lifecycle **Draft → Active → Superseded or Withdrawn**. Draft has no authority. Active is effective within its Scope. Superseded identifies its replacement. Withdrawn states why no replacement applies. Prior versions MUST remain recoverable.

## 10. Software and material state

Software architecture and repository layout are not constitutional. They MUST be defined in versioned architecture records with explicit boundaries, dependencies, and rationale. A directory name MUST NOT be treated as proof of separation.

Every stateful component MUST declare ownership, representation, initialization, permitted transitions, persistence, reset, recovery, and concurrency behavior for its Material state. Material state MUST NOT depend on an undocumented global, cache, service, environment value, mutable default, clock, random source, or local file.

Every scientific execution MUST record or content-address all Material inputs and outputs. Randomized execution MUST record the generator, seed or equivalent state, and sampling procedure. Nondeterminism that cannot be controlled MUST be measured or declared as a limitation.

Implementation and validation MUST be independently changeable: changing implementation code MUST NOT silently change acceptance criteria, and changing criteria MUST occur in the responsible Normative artifact. Shared code MAY be used only when its use does not make the assessor depend on the behavior being assessed.

Generated, cached, secret, personal, and runtime-only material MUST be separated from canonical records and excluded from version control unless a domain standard explicitly requires a safe, reproducible fixture. Credentials and private keys MUST NOT be committed. Excluded material needed for reproduction MUST have a version-controlled manifest as required by Section 6.

## 11. Document responsibilities

Each maintained document MUST have exactly one primary responsibility. The following boundaries apply:

- this Constitution: repository-wide invariants and authority boundaries;
- domain scientific standard: one domain's method, object definitions, and scientific lifecycle;
- preregistration or protocol: one declared investigation or reusable procedure;
- Decision: authorization of one transition or one atomic set of explicitly coupled transitions;
- architecture Decision: one engineering trade-off and its consequences;
- implementation specification: required software behavior and interfaces;
- test specification: validation criteria and method;
- audit report: observations about conformance at one identified revision;
- Governance Registry: active Normative artifacts, jurisdictions, and authority assignments only;
- README or index: navigation and non-normative description.

A document combining responsibilities MUST be split or explicitly designate non-primary sections as informative. Informative text MUST NOT introduce requirements.

Terminology defined by an active higher-level artifact MUST be reused unchanged within its Scope. A domain-specific redefinition MUST use a different term or explicitly qualify the term and prove that no ambiguity results. Synonyms MUST NOT create distinct object types, and identical names MUST NOT conceal distinct types.

## 12. Conformance and enforcement

A change is constitutionally conforming only if an Independent reviewer can trace every Affected requirement expressed as MUST or MUST NOT to one of:

- an automated check and its output;
- a manual inspection procedure and version-controlled finding;
- a statement that the requirement is not applicable, with a testable reason.

A conformance claim MUST identify the repository revision, Scope, checks performed, results, reviewer, unresolved violations, and limitations. Tools and audits MUST report nonconformance; they MUST NOT redefine it away. An unavailable check MUST be reported as not verified, never as passed. A self-review MAY find defects but MUST NOT be labeled independent or satisfy an Independent reviewer requirement.

Nonconforming content MAY be retained for diagnosis or migration but MUST be labeled nonconforming and MUST NOT be used to authorize a dependent transition. Security containment MAY precede record creation when delay would materially increase harm; the action and rationale MUST be recorded immediately afterward and remains subject to review.

CI, tests, schemas, and linters SHOULD enforce every mechanically decidable requirement. Requirements not mechanically decidable MUST have a named manual review procedure. A check is evidence of conformance only for the criteria, revision, and Scope it actually assessed.

## 13. Amendments

Every part of this Constitution is revisable. An amendment MUST include:

1. a concrete failure, contradiction, or changed condition;
2. the affected clauses and artifacts;
3. considered alternatives, including no change;
4. consequences for falsifiability, reversibility, authority, and existing records;
5. a migration and rollback procedure;
6. evidence of conflict and terminology review;
7. an Independent reviewer attestation.

An Independent reviewer attestation MUST identify the reviewed revision, declare that the reviewer is not an author of the change, identify whether the reviewer produced reviewed Evidence, disclose conflicts, and state the review procedure and conclusion. It MUST also state the reviewer's relevant competence and identify the records, artifacts, or checks examined during the review. The attestation is Repository evidence.

Initial adoption requires attestations by two identified humans: an adopter and an Independent reviewer. The same atomic change MUST activate this Constitution, create or activate the Governance Registry, and assign at least one constitutional steward authorized to amend, supersede, or withdraw this Constitution and to activate Domain standards. This bootstrap authority ends upon adoption.

A later amendment requires approval by a Registry-listed constitutional steward, an Independent reviewer attestation, and one atomic change updating this document and its Registry entry. Adoption or amendment becomes Active only when that complete change is accepted into the default branch. Scientific preference, implementation convenience, current test failure, or desired conclusion is insufficient justification by itself.

Amendments MUST NOT retroactively alter the meaning or reported outcome of a prior scientific record. If a standard changes, affected records retain the standard version under which they were created and MAY be reassessed through a new Interpretation or Decision.

## 14. Adoption

Upon adoption, this Constitution supersedes the prior `REPOSITORY_CONSTITUTION.md`. Prior directory allowlists, naming rules, frozen scientific constants, personal approval requirements, and implementation-specific policies have no constitutional force unless re-established by an Active, scoped subordinate standard.

At adoption, every existing Normative artifact not activated in the Governance Registry becomes Legacy and has no normative authority. A Legacy artifact MUST satisfy Section 4 before later activation. Existing scientific records remain preserved; adoption changes their authority classification, not their recorded content.
