# Scientific Stack — S-1 … S-10

- **Status:** Draft
- **Scope:** Design of the scientific Domain standards for Project P1
- **Responsibility:** Specify ontology, lifecycle, required fields, relationships, validation rules, failure cases, and migration rules for each proposed scientific Domain standard
- **Authority source:** None. This record has no normative authority and activates nothing.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 0. Common frame

Each standard below owns exactly one region of the scientific object graph, per the **Jurisdiction Rule**: *a transition belongs to the standard owning the object type whose state changes; a standard states input conditions on upstream types by reference and never imposes requirements on them.*

**Fields common to every scientific record** (owned by O-1, not restated by any S-*): `id`, `object_type`, `schema_version`, `status`, `scope`, `created` (§2 recorded time: timezone-qualified, precision identified), `created_by`, `provenance`, `last_reviewed`, `supersedes`, `superseded_by`, `standard_version` (the version of the owning standard under which the record was created — required by §13 ¶4, which preserves each record's originating standard version).

**Transitions.** Every transition produces a §9 ¶3 record with eight elements: object, prior state, new state, criteria applied, evidence considered, authority, time, rationale. Missing information causes the transition to fail closed. Every scientific transition additionally requires a Decision (DG-13) approved by the Registry-listed authority (§4 ¶5).

**Retention.** Scientific records are never physically deleted, including rejected, superseded, inconvenient, and negative ones (§8 ¶2). Every standard's retention rule is "permanent"; the only variable is state.

**A note on what these standards may not do.** §5, §6, §7, and §8 fix most of the substance directly. The S-* standards are largely *procedural*: they define states, criteria, authority, and record structure. Where a section below cites a constitutional clause, that clause is reserved and the standard restates it only as a pointer, never as a refinement (Peer Reference Rule).

---

## S-1 — Research Standard *(Investigation, Registered protocol)*

**Ontology.** Owns `investigation` (a bounded research effort with a question, scope, and lifecycle) and `registered_protocol` (an immutable protocol whose registration transition occurred before its governed execution began, §2). Also owns the `confirmatory` / `exploratory` designation of an analysis (§2, as amended by A-3).

*Naming note.* The brief calls this the Research Standard. Its jurisdiction is deliberately narrow: it does **not** govern research generally, because a standard owning "research" would overlap all nine peers and be rejected by §4 ¶2. It owns investigations and protocols.

**Lifecycle.**
- Investigation: `Proposed → Active → Suspended → Concluded / Abandoned`. Abandonment is recorded with disposition and rationale, never deleted (§7 ¶2).
- Registered protocol: `Draft → Registered → Executing → Closed`, plus `Amended` producing a **new** protocol linked to the prior one. **Registration is irreversible and immutable**; a protocol cannot be edited after registration, because §2 defines registration as preceding governed execution and §5 forbids post-access element changes from being represented as confirmatory.

**Required fields.**
*Registered protocol* — every §5 ¶3 element, fixed before any author, contributor, or person communicating analysis-relevant information accesses an unblinded Observation or any data revealing condition or outcome: sampling frame; sample size or stopping rule; exclusions; assignment; controls; primary outcomes; analysis population; statistical or logical decision rule; multiplicity handling; model selection procedure; randomness plan. Plus: registration timestamp with precision (§2); the validity criteria that determine Valid vs Invalid Result (§2, §7 ¶4); completion criteria and the authority for recording a Result (§7 ¶2, delegated); the digest algorithm reference (by reference to DG-7); the Claims or Hypotheses under test (by reference).
*Investigation* — question(s) by reference to S-2; scope; protocols by reference; Unknowns opened by reference.

**Relationships.** `investigation --contains--> registered_protocol` · `registered_protocol --tests--> hypothesis|claim` · `registered_protocol --governs--> result` · `registered_protocol --declares--> validity_criteria`.

**Validation rules.**
1. Registration timestamp strictly precedes the first execution artifact attributable to the protocol (`DA-20`).
2. All eleven §5 ¶3 elements present and non-empty; a placeholder is an absence and fails closed.
3. Any element changed after registration produces a new protocol and forces the `exploratory` label on the affected execution (`DA-21`).
4. Validity criteria are stated before execution and are independent of favourability (§2 *Valid Result*).
5. A protocol MUST NOT declare an exclusion rule that references outcome values.

**Failure cases.**
| Case | Constitutional breach | Detection |
|---|---|---|
| Protocol registered after data access | §5 ¶3; execution is exploratory, not confirmatory | `DA-20`, `DA-21` — but see limitation below |
| Registration timestamp forged or backdated | §5 ¶3 defeated entirely | **Not detectable from Git alone.** Requires an external timestamp anchor; recorded as risk R-08 and as an Unknown until mitigated |
| Protocol amended in place | §2 immutability of Registered protocol | `DA-14`-class immutability check on `protocols/registered/` |
| Stopping rule omitted or vague | Optional stopping; §5 ¶3 | `DA-21` plus manual `MRP-06` |
| "Frozen constants" declared outside a revisable standard | §5 ¶6 | `DA-07`; current nonconformance N-4 |

**Migration rules.** Protocols registered under standard version *n* retain version *n* semantics (§13 ¶4). A change to S-1 MUST NOT alter the confirmatory/exploratory status of any prior execution. Pre-adoption preregistrations in `theory/preregistrations/` are **Draft protocols**, not Registered protocols; executions against them are exploratory and may not be relabelled later (see `00_ECOSYSTEM_OVERVIEW.md` §7.5).

---

## S-2 — Question Standard

**Ontology.** Owns `question`: "a recorded request for knowledge that directs investigation without asserting an answer" (§2).

**Lifecycle.** `Draft → Open → Referred → Answered / Retired`. `Referred` records that the Question was referred to S-3 for Unknown creation; the Unknown itself is created by S-3 (Jurisdiction Rule).

**Required fields.** Question text; scope; why it matters; what an answer would look like; materiality assessment (whether the Question is material to a Claim, Interpretation, Decision, Result validity, or governed transition — §2); referral to Unknown (if material); investigation linkage.

**Relationships.** `question --refers_to--> unknown` · `question --motivates--> investigation` · `question --answered_by--> interpretation|result`.

**Validation rules.**
1. A Question MUST NOT assert an answer; declarative claim-shaped text fails review (`MRP-07`).
2. **If materiality is asserted, a referral to an Unknown MUST exist** — §2: "a Question or uncertainty that is material to a Claim, Interpretation, Decision, Result validity, or governed transition MUST be recorded as an Unknown until resolved" (`DA-54`).
3. `Answered` requires a linked Result or Interpretation; a Question is never answered by a Decision (§3 ¶6).

**Failure cases.** Question used as a disguised Claim (breaches §2's object-kind distinction) · material Question never escalated to an Unknown, the most common route by which uncertainty disappears from a research record · Question closed by governance fiat rather than evidence.

**Migration rules.** Existing gap records (`theory/THEORY_GAPS.md` G-items) are candidate Questions; each requires a materiality assessment on intake, and material ones require Unknowns before any dependent Claim may be stated.

---

## S-3 — Unknown Standard

**Ontology.** Owns `unknown`: "a recorded question or uncertainty not resolved to the standard required for a Claim" (§2). §8 ¶1: **"Unknown is a permanent first-class object kind."**

**Lifecycle.** `Open → Under investigation → Resolved → Reopened`. Resolution changes state only; it never removes the kind or erases history (§8 ¶1). Reopening is always permitted and requires no special authority beyond a Decision.

**Required fields.** Statement of what is not known; scope; why it is material; what would resolve it (the resolution criterion, stated operationally); consequences if unresolved; affected Claims, Interpretations, Decisions, and Results by reference; resolution record with evidence when resolved; reopening rationale when reopened.

**Relationships.** `unknown --limits--> claim|interpretation|principle` · `unknown --arises_from--> question|result|observation|audit_finding` · `unknown --resolved_by--> result|interpretation`.

**Validation rules.**
1. Material missing information, unresolved contradiction, untested assumption, failed replication, and unexplained anomaly MUST each be represented as an Unknown rather than silently closed (§8 ¶1) — five distinct intake triggers, each checkable at review (`MRP-08`).
2. An Unknown MUST NOT be deleted. Deletion detection is `DA-16`.
3. §5 ¶5: where no materially distinct alternative to an Interpretation is found, the search and its limits MUST be recorded as an Unknown. S-9 creates the referral; S-3 owns the object.
4. §6 ¶5: an unretainable input's absence, reason, expected effect, and recovery status MUST be recorded as an Unknown or limitation.
5. Resolution requires evidence meeting the criterion stated at open time — not a later, weaker criterion.

**Failure cases.**
| Case | Effect |
|---|---|
| Unknown quietly closed without meeting its criterion | Uncertainty vanishes from the record; downstream Claims overstate support. §8 ¶1 breach. |
| Resolution criterion rewritten at resolution time | Post hoc goalpost movement; equivalent to §5 ¶3's prohibited element change |
| Unknown never opened for a known limitation | The record looks cleaner than the science is — the failure §8 exists to prevent |
| Unknown deleted during a refactor | `DA-16` and `DA-15`; protected paths under DG-8 |

**Migration rules.** Unknowns carry their originating S-3 version. A future S-3 tightening the resolution criterion MUST NOT retroactively reopen resolved Unknowns (§13 ¶4); it MAY require reassessment through a new Interpretation or Decision.

---

## S-4 — Observation & Source Standard

**Ontology.** Owns `observation` ("a recorded measurement or Source statement **before** it is used to support or oppose a Claim", §2) and `source` ("an identified origin of an Observation, such as an instrument, dataset, publication, repository, or actor statement", §2).

**Lifecycle.** Observation: `Recorded → Verified → Quarantined → Superseded`. Append-only: a correction creates a new Observation linked to the prior one; the prior is never edited. Source: `Identified → Active → Deprecated`.

**Required fields.** *Observation* — measured or stated value; measurement procedure; instrument or method; Source by reference; acquisition time with precision; actor or process; environment and configuration; blinding status; known measurement limitations; raw-artifact custody reference (DG-7). *Source* — identity, type, version, access method, retrieval time, stability assessment.

**Relationships.** `observation --from--> source` · `observation --admitted_as--> evidence` *(edge created by S-5, not S-4)* · `observation --produced_under--> registered_protocol`.

**Validation rules.**
1. An Observation MUST NOT state the Claim it supports. Doing so collapses §2's Observation/Evidence distinction, which the Constitution's final paragraph of §2 expressly forbids.
2. Blinding status MUST be recorded, because §5 ¶3's pre-access condition is defined in terms of unblinded access.
3. A citation is a Source, not Evidence, until the bounded observation and its provenance are recorded (§6 ¶4).
4. Every Observation is either linked to a Registered protocol or explicitly labelled as arising outside one (and therefore exploratory).

**Failure cases.** Observation recorded with an interpretive gloss ("shows that X") — the most frequent object-kind violation in practice · Source cited without a bounded observation, so a citation count masquerades as support (§5 ¶7 explicitly forbids citation count as Evidence) · unblinding event unrecorded, silently converting a confirmatory analysis to exploratory without anyone noticing.

**Migration rules.** Pre-adoption measurements in `artifacts/`, `evidence/`, and `data/` are **working output** (§2) and MUST NOT be cited as Evidence. Promotion to Observation requires provenance reconstruction meeting §6; where provenance cannot be reconstructed, the material stays working output and the gap is recorded as an Unknown.

---

## S-5 — Evidence Standard

**Ontology.** Owns `evidence`: "an Observation admitted for a stated Claim under declared provenance, relevance, and validity conditions" (§2). Evidence is a *relation* between an Observation and a Claim, not a property of the Observation.

**Lifecycle.** `Proposed → Admitted → Excluded → Revised`. All states retained. Exclusion never deletes.

**Required fields (§6 ¶1, all nine mandatory).** The Claim for which it is relevant; the underlying Observation or Source; acquisition or generation method; responsible actor or process; time of acquisition or generation; code, configuration, data, environment, and randomness inputs material to reproduction; transformations from source to reported value; validity limitations and known missing information; an immutable identifier or digest when content may exist outside Git. Plus, from §6 ¶4: the admission or exclusion record stating the relevant provenance, relevance, and validity conditions, and the authority that admitted or excluded it.

**Relationships.** `evidence --admits--> observation` · `evidence --supports|opposes--> claim` · `evidence --derived_from--> evidence` (with method, §6 ¶4) · `evidence --custodied_by--> custody_manifest`.

**Validation rules.**
1. All nine §6 ¶1 items present (`DA-17`). Absence of any one is fatal, not advisory.
2. Evidence MUST NOT be promoted, demoted, or discarded because of agreement or disagreement with a preferred conclusion (§6 ¶3). Mechanically undecidable; mapped to manual procedure `MRP-09`, which compares admission/exclusion rates across supporting and opposing Evidence for the same Claim — a statistical tell, not a proof.
3. Inclusion, exclusion, stopping, and transformation rules MUST be declared before confirmatory analysis; post hoc changes MUST be preserved and labelled (§6 ¶3).
4. Derived summaries MUST link to inputs and method (§6 ¶4).
5. A biological analogy, metaphor, mechanism name, model confidence, performance improvement, citation count, authority statement, or absence of an alternative MUST NOT by itself count as Evidence (§5 ¶7) — a lexical screen (`DA-55`) plus `MRP-09`.
6. Digest algorithm resolves to a registered, non-deprecated algorithm in DG-7 (`DA-43`).

**Failure cases.**
| Case | Effect |
|---|---|
| Observation admitted as Evidence for a Claim it was not designed to address | Relevance condition unmet; inference silently broadened |
| Selective admission favouring a preferred Claim | §6 ¶3 breach; the single most damaging scientific failure the Constitution targets |
| Reproduction inputs omitted | Evidence unreproducible; §6 ¶1 item 6 breach; usually discovered only when replication is attempted |
| Model confidence cited as Evidence | §5 ¶7 breach; endemic in ML research records |

**Migration rules.** Evidence records carry the S-5 version under which they were admitted. Tightening admission criteria does not retroactively exclude prior Evidence; it triggers reassessment through a new Interpretation or Decision (§13 ¶4). Prior admissions remain visible with their originating criteria.

---

## S-6 — Claim Standard

**Ontology.** Owns `claim`: "a proposition that is assessable as supported, opposed, or unresolved within a stated Scope" (§2, as amended by A-6).

**Lifecycle.** `Draft → Active → Supported / Opposed / Unresolved → Retired`. State changes occur **only** by the Claim's own declared decision rule, executed through a Decision (DG-13). Tools MUST NOT infer state from evidence count, model confidence, test success, or elapsed time (§9 ¶3).

**Required fields.** §5 ¶1 requires of *every* Claim: its Scope, and at least one feasible Observation, test outcome, or Result that could count against it. §5 ¶2 requires of every Claim used to justify a scientific conclusion or action, all eight of: (1) operational terms; (2) Scope; (3) observations that could support it; (4) observations that could count against it; (5) credible competing explanations, including a null where applicable; (6) the rule by which evidence changes its state; (7) unresolved assumptions and limitations; (8) links to the Evidence, Interpretations, and Decisions on which its current state depends.

Note the two-tier structure precisely: every Claim needs a falsifier; only justifying Claims need all eight. And a Claim is **Falsifiable** in §2's sense only when it *also* has a declared decision rule (item 6) — §5 ¶1 says so explicitly. S-6 must not conflate "has a falsifier" with "is Falsifiable."

**Relationships.** `claim --supported_by|opposed_by--> evidence` · `claim --limited_by--> unknown` · `claim --paired_with--> hypothesis` (S-7 owns the pairing) · `claim --state_changed_by--> decision` · `claim --generalized_as--> principle` (S-10 owns).

**Validation rules.**
1. Falsifier present for every Claim (`DA-18`).
2. All eight §5 ¶2 fields present for any Claim referenced by an Interpretation, Decision, or Principle (`DA-56`).
3. Operational terms satisfy §2's *Operational* definition: observable inputs, procedures, measurements, decision rules, or reproducible transformations sufficient for an Independent reviewer to determine application and what outcome would distinguish the asserted condition from alternatives (`MRP-10`).
4. A mechanism or understanding claim requires an operational criterion distinguishing it from prediction or performance alone (§5 ¶7) (`MRP-10`).
5. Status labels MUST NOT imply certainty beyond operational definition; proven, true, final, permanent, certain are prohibited for empirical Claims unless the standard defines a bounded technical meaning that does not imply infallibility (§8 ¶3) (`DA-07`).
6. Decision-rule evaluation is recorded, with inputs, at each state change.

**Failure cases.** Unfalsifiable Claim admitted because its falsifier is stated but infeasible · decision rule written after the evidence arrives, converting confirmation into a formality · scope creep, where a Claim proven in one setting is cited generally · "supported" used as "true," which §8 ¶3 forbids.

**Migration rules.** A Claim retains the S-6 version under which its current state was set. A stricter S-6 does not silently demote existing Claims; it requires reassessment through a new Decision (§13 ¶4). Existing informal claims across `PROGRAM_D_*` and `theory/` are candidates requiring full §5 ¶2 reconstruction; those that cannot be reconstructed are retired, not grandfathered.

---

## S-7 — Hypothesis Standard

**Ontology.** Owns `hypothesis`: "a Claim paired with an operational test and a possible outcome that counts against it" (§2). A Hypothesis is therefore strictly more demanding than a Claim: it must carry a *test*, not merely a conceivable falsifier.

**Lifecycle.** `Proposed → Registered → Under test → Supported / Not supported / Indeterminate → Retired`. Registration must precede execution of the governing protocol (S-1), or the test is exploratory.

**Required fields.** The paired Claim by reference (never restated — Peer Reference Rule); the operational test; the outcome that counts against it; the discriminating prediction relative to named alternatives; the governing Registered protocol; prior state and the evidence that moved it.

**Relationships.** `hypothesis --pairs--> claim` · `hypothesis --tested_by--> registered_protocol` · `hypothesis --discriminates_from--> hypothesis|alternative` · `hypothesis --outcome_recorded_in--> result`.

**Validation rules.**
1. The paired Claim exists, is Active, and satisfies §5 ¶2 (`DA-57`).
2. The operational test is executable and its counting-against outcome is stated before execution.
3. **Mutual distinguishability**: where two Hypotheses predict identical observables under all registered protocols, they are not independently testable, and that must be recorded as an Unknown rather than presented as two supported hypotheses. This is not hypothetical — `theory/HYPOTHESIS_DISCRIMINATION_MATRIX.md` already records that T-01 and T-02 "are not mutually distinguishable." Under S-7 that finding would force an Unknown and block independent support claims for either (`MRP-11`).
4. No Hypothesis set is constitutional (§5 ¶6); the register is revisable and additions require no amendment.

**Failure cases.** Hypothesis registered without a discriminating prediction, so any outcome confirms it · post hoc hypothesis fitted to observed results and presented as confirmatory (§5 ¶3) · "Never invent new hypotheses" style freezes, which §5 ¶6 forbids as they make the hypothesis set effectively constitutional — the current `theory/HYPOTHESIS_REGISTER.md` posture.

**Migration rules.** Existing H\*, H1, H2 and the T-01/T-02 propositions are candidates. Each requires: a paired §5 ¶2 Claim, an operational test, a counting-against outcome, and a discrimination analysis. T-01/T-02 additionally require resolution of the recorded non-distinguishability before either may be tested as confirmatory.

---

## S-8 — Result Standard

**Ontology.** Owns `result` ("an immutable record of measurements and protocol facts created when working output enters the Result lifecycle", §2), `invalid_result` (fails at least one registered validity criterion), and `abandoned_execution` (preserved, per §7 ¶2).

**Lifecycle.** `Working output → Result | Invalid Result | Abandoned execution`, then `Corrected by` / `Superseded by`. **A Result is immutable from the transition that creates it** (§7 ¶1). There is no edit path — ever.

**Required fields.** Measurements; protocol facts; the governing Registered protocol by reference; execution environment; all Material inputs and outputs recorded or content-addressed (§10 ¶3); for randomized execution: generator, seed or equivalent state, and sampling procedure (§10 ¶3); uncontrollable nondeterminism measured or declared as a limitation (§10 ¶3); validity determination against the protocol's registered criteria, with the criteria cited; disposition and rationale (§7 ¶2); the completion determination and its authority (§7 ¶2).

**Relationships.** `result --produced_under--> registered_protocol` · `result --corrects--> result` · `result --interpreted_by--> interpretation` · `result --custodied_by--> custody_manifest`.

**Validation rules.**
1. Immutability: content digest of every Active Result matches its creating revision; no history rewrite touches `results/` (`DA-14`, `DA-45`).
2. Correction occurs only through a new linked Result identifying the error and superseded content; history MUST NOT be rewritten to conceal the prior Result (§7 ¶1) (`DA-58`).
3. The correction MUST state whether and to what Scope the prior Result is invalid, corrected, or superseded for inference; later Evidence or Interpretation relying on the prior Result MUST disclose that status (§7 ¶1) (`DA-59` — a propagation check across dependents).
4. **Negative Results are retained under identical provenance and retention rules** and MUST NOT be deleted, hidden, relabelled as a failed run, or excluded from synthesis solely because they oppose a preferred Claim (§7 ¶4) (`DA-60` compares Negative Result counts against execution counts per protocol; a large gap is a finding, not a proof).
5. An Invalid Result may be excluded from inference **only** by its Registered protocol's validity rule, with the Result and applied rationale preserved (§7 ¶4).
6. Validity is independent of favourability (§2) — a validity criterion may not reference whether the outcome was desired.
7. Passing software tests establishes only conformance to those tests and MUST NOT be reported as scientific success unless a Registered protocol independently makes that test output relevant Evidence (§3 ¶7) (`DA-61`).

**Failure cases.**
| Case | Effect |
|---|---|
| Result edited "to fix a typo" | §7 ¶1 breach; immutability is absolute and admits no benign exception |
| Failed run discarded as "not a real run" | §7 ¶4 breach; the file-drawer mechanism the clause exists to close |
| Validity criterion applied that was not registered before execution | Post hoc invalidation of inconvenient Results |
| Test suite success reported as scientific success | §3 ¶7 breach; the specific failure mode a software-heavy research project is most prone to |
| Seed unrecorded | Irreproducible; §10 ¶3 breach |

**Migration rules.** Existing `artifacts/exp_001…exp_019` outputs are working output. Promotion to Result requires a governing Registered protocol that existed before the execution — which, for all pre-adoption runs, it did not. Therefore **no existing artifact can become a confirmatory Result.** They may be preserved as exploratory working output and cited as such. This is a hard consequence of §2 and §5 and should be understood before adoption, not after.

---

## S-9 — Interpretation Standard

**Ontology.** Owns `interpretation`: "a scoped inference from identified Evidence or Results" (§2).

**Lifecycle.** `Draft → Active → Superseded → Withdrawn`. An Interpretation MUST NOT alter a Result (§3 ¶6).

**Required fields.** Input Results or Evidence by reference; Scope; assumptions; competing explanations; uncertainty (§7 ¶3). Plus, for every **Active** Interpretation (§5 ¶5): a null explanation; the strongest materially distinct alternative identified by a documented literature, model, or causal search; and an Observation or experiment capable of discriminating among them. Where no materially distinct alternative is found, the search and its limits MUST be recorded as an Unknown — and **absence of an identified alternative MUST NOT support uniqueness** (§5 ¶5).

**Relationships.** `interpretation --infers_from--> result|evidence` · `interpretation --considers--> alternative_explanation` · `interpretation --discriminated_by--> proposed_observation` · `interpretation --qualified_by--> unknown`.

**Validation rules.**
1. Null explanation present and non-trivial (`DA-19`).
2. Strongest materially distinct alternative present, with the search documented — method, sources, date, limits (`DA-19`, `MRP-12`).
3. Discriminating Observation or experiment stated (`DA-19`).
4. Where no alternative was found, an Unknown exists recording the search and its limits (`DA-54`).
5. Description is distinguished from inference (§7 ¶3) (`MRP-12`).
6. **MUST NOT generalize beyond the narrowest material limitation of its inputs** without additional justification (§7 ¶3) — scope is computed from inputs and compared to the stated scope (`DA-62` for the mechanical part; `MRP-12` for the rest).
7. Reliance on a corrected or superseded Result requires disclosure of that status (§7 ¶1) (`DA-59`).

**Failure cases.** Interpretation stated over a scope wider than any input supports — the most common overclaiming route · the null omitted or written as a strawman · "no alternative explanation exists" used as positive support, which §5 ¶5 explicitly forbids · an Interpretation quietly amending a Result's meaning without a correcting Result.

**Migration rules.** Interpretations retain their S-9 version. Existing synthesis documents (`theory/THEORY_LANDSCAPE.md`, `theory/EXPERIMENTAL_FRAMEWORK.md`) are candidate Interpretations; each needs null, alternative, discriminator, and scope-computation before activation.

---

## S-10 — Principle Standard

**Ontology.** Owns `principle`: "a provisional, scope-bounded generalization accepted under a declared scientific standard" (§2). Every word of that definition is load-bearing: provisional, scope-bounded, and accepted under a *declared standard*.

**Lifecycle.** `Candidate → Accepted → Under challenge → Falsified / Retired / Superseded`. §5 ¶6: every Principle MUST remain falsifiable, reversible, and explicitly scoped. There is no terminal "established" state, and S-10 MUST NOT create one.

**Required fields.** The generalization; explicit scope boundaries; the falsification condition; supporting Claims, Interpretations, and Results by reference; the declared scientific standard under which it was accepted, with version; known counter-evidence and limitations; the reversal path.

**Relationships.** `principle --generalizes--> claim|interpretation` · `principle --falsified_by--> result` · `principle --bounded_by--> scope` · `principle --challenged_by--> unknown`.

**Validation rules.**
1. Falsifiable per §2: within its stated Scope it identifies at least one feasible Observation, test outcome, or Result that would count against it under its declared decision rule (`DA-18`).
2. Scope stated as §2 requires — population, environment, conditions, versions, and time interval, sufficiently identifiable for an Independent reviewer to determine membership (`MRP-13`).
3. **No Principle is constitutional** (§5 ¶6). A Principle MUST NOT be cited to justify a governance transition, and no scientific constant, threshold, model, ontology, or hypothesis set may be elevated beyond a revisable standard.
4. Prohibited certainty labels (§8 ¶3) (`DA-07`).
5. Acceptance requires a Decision (DG-13); accumulated support alone never promotes a Principle (§9 ¶3).

**Failure cases.** A Principle hardening into an unquestionable assumption — the failure §5 ¶6 exists to prevent, and the reason "provisional" appears in the definition · Principle cited as governance authority, conflating scientific support with repository authority (§3 ¶6) · scope quietly widened after acceptance, without a new Decision.

**Migration rules.** No existing artifact qualifies as a Principle. The repository currently contains frozen constants and "canonical" specifications that behave like Principles without satisfying §5 ¶6; at adoption these become Legacy (§14) and require full reconstruction to be re-established.

---

## 1. Cross-cutting: the confirmatory chain

The stack's scientific integrity reduces to one ordering that must hold in real time, not merely on paper:

```
S-1 protocol registered   (all §5 ¶3 elements fixed)
        ↓  strictly before
S-4 unblinded observation access
        ↓
S-8 result recorded       (validity judged by pre-registered criteria only)
        ↓
S-5 evidence admitted     (nine §6 ¶1 items; admission rule declared pre-analysis)
        ↓
S-6 claim state changed   (by its own pre-declared decision rule, via a DG-13 Decision)
        ↓
S-9 interpretation        (null + strongest alternative + discriminator)
        ↓
S-10 principle            (provisional, scoped, falsifiable, reversible)
```

Every arrow is a transition owned by exactly one standard, authorized by exactly one Decision, and recorded with §9's eight elements. Break any arrow's ordering and the execution is exploratory — permanently, since §13 ¶4 forbids amendments that retroactively alter a prior record's meaning.

The weakest link is the first arrow, and it is weak for a reason worth stating plainly: **Git timestamps are not trustworthy evidence of registration order.** A committer can backdate. Every other guarantee in this stack is enforceable within the repository; this one is not. Mitigation requires an external anchor — a public timestamping service, a signed third-party receipt, or registration with an external registry — and until one exists, the pre-registration guarantee rests on the honesty of a single actor. That is recorded as risk R-08 and as an open item for human decision (H-14).
