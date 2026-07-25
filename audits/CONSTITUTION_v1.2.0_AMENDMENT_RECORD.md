# Repository Constitution v1.2.0 — Amendment Record

- **Status:** Draft; supporting record for the proposed v1.2.0 revision
- **Scope:** `REPOSITORY_CONSTITUTION.md` v1.1.0 → v1.2.0, and the `GOVERNANCE_REGISTRY.yaml` consistency repair in the same change
- **Responsibility:** Record the amendment rationale, audit findings, impact, and limitations for the revision. Informative except where it quotes constitutional text.
- **Authority source:** None. This record has no normative authority and does not authorize any transition.
- **Verification basis:** Terra Verification Report (authoritative), verified against `REPOSITORY_CONSTITUTION.md` v1.1.0

Informative note: this document reports and recommends. It does not impose requirements. Where it states that something "MUST" occur, it is quoting or paraphrasing the Constitution, not creating an obligation.

---

## 1. Disposition of Terra findings

Terra assessed 28 findings (ADV-001 … ADV-028). Terra determined 21 already resolved by v1.1.0 text and 7 unresolved. Per instruction, resolved findings were **not re-opened** and are recorded here only for traceability.

| Finding | Terra disposition | Action in v1.2.0 |
|---|---|---|
| ADV-001 Bootstrap paradox | Resolved | None |
| ADV-002 Reviewer regress | Resolved | None |
| ADV-003 "Material" undefined | Resolved | None |
| ADV-004 "Operational" undefined | Resolved | None |
| ADV-005 Evidence-admission criteria | Resolved | None |
| ADV-006 Immutable Results | Resolved | None |
| ADV-007 Domain-standard deadlock | Resolved | None |
| ADV-008 Active circularity | Resolved | None |
| ADV-009 "Atomic change" undefined | Resolved | None |
| ADV-010 Authority escalation | Resolved | None |
| ADV-011 Scope unbounded | Resolved | None |
| ADV-012 Validation separation | Resolved | None |
| **ADV-013 Attestation depth** | **Unresolved** | **A-1 (§13)** |
| ADV-014 "Falsifiable" undefined | Resolved | None |
| ADV-015 Negative-result retention | Resolved | None |
| ADV-016 Question vs Unknown | Resolved | None |
| ADV-017 Working-output lifecycle | Resolved | None |
| **ADV-018 Digest algorithm** | **Unresolved** | **A-2 (§6)** |
| ADV-019 Time representation | Resolved | None |
| ADV-020 Exactly-one Domain standard | Resolved | None |
| ADV-021 Legacy limbo | Resolved | None |
| ADV-022 "Primarily" loophole | Resolved | None |
| **ADV-023 Confirmatory vs exploratory** | **Unresolved** | **A-3 (§2)** |
| **ADV-024 "Scientific success"** | **Unresolved** | **A-4 (§2)** |
| **ADV-025 MAY has no force** | **Unresolved** | **A-5 (§1)** |
| ADV-026 Self-referential force | Resolved | None |
| **ADV-027 Claim "can be assessed"** | **Unresolved** | **A-6 (§2)** |
| **ADV-028 Unfalsifiable Claims** | **Unresolved** | **A-7 (§5)** |

**Coverage: 7 of 7 unresolved findings implemented.**

---

## 2. Amendment log

Amendments A-1 … A-7 implement Terra's stated minimum wording. Amendments D-1 and D-2 are **derived**: they are not mandated by Terra and were added only to remove ambiguity created by, or directly obstructing, the mandated text. Derived amendments are separable — striking them leaves A-1…A-7 intact and conforming.

### A-1 — Independent reviewer attestation depth (ADV-013)

- **Section:** 13, paragraph 2
- **Class:** Governance
- **Change:** Appended — "It MUST also state the reviewer's relevant competence and identify the records, artifacts, or checks examined during the review."
- **Why it improves the Constitution:** v1.1.0 required a review *procedure and conclusion* but nothing establishing that the procedure was performed or that the reviewer could perform it. The attestation was satisfiable by an unqualified party asserting a conclusion. Because §4 makes attestation a precondition for Domain-standard activation and §13 for amendment, this was the single load-bearing control with the weakest evidentiary floor. The amendment converts the attestation from an assertion into a checkable record.
- **Trade-offs:** Raises the cost of every activation and amendment. "Relevant competence" is judgement-laden and not mechanically decidable, so under §12 it requires a named manual review procedure that no Active Domain standard currently supplies.
- **New risks:** Competence claims are self-asserted and unverified by the Constitution; a reviewer may overstate competence. The amendment makes overstatement *recorded and falsifiable* rather than preventing it. In a two-person project, a strict competence reading could make some reviews unsatisfiable, incentivising boilerplate.
- **Backward compatibility:** Breaking for future attestations only. Attestations created under v1.1.0 remain valid under §13's non-retroactivity rule.

### A-2 — Digest algorithm specification (ADV-018)

- **Section:** 6, after the Evidence bullet list
- **Class:** Scientific
- **Change:** Added — "When an external artifact is identified by a digest, the applicable Domain standard or Registered protocol MUST specify a collision-resistant digest algorithm and version."
- **Why it improves the Constitution:** §2 defines Repository evidence to include content-addressed external artifacts, and §6 requires a digest, but neither constrained the digest's security properties. A digest under a broken algorithm satisfies the letter of §6 while failing its purpose — the artifact is no longer uniquely identified, so provenance claims silently become unsound. This closes the gap without naming an algorithm, which would violate §5's prohibition on constitutional constants.
- **Trade-offs:** Delegation means the Constitution cannot itself be checked for digest adequacy; conformance depends on a Domain standard that does not yet exist. Until one is activated, external-artifact Evidence cannot fully conform.
- **New risks:** "Collision-resistant" is time-dependent — an algorithm adequate today may not be later. Terra identified *algorithm transition procedure* as part of the defect, but its minimum amendment does not require one. See Limitation L-2.
- **Backward compatibility:** Non-breaking. Existing digests remain valid; the requirement binds the governing standard, not historical records.

### A-3 — Confirmatory and exploratory analysis (ADV-023)

- **Section:** 2, definitions
- **Class:** Scientific
- **Change:** Added — "**Confirmatory analysis** is an analysis represented as testing a Claim under the elements fixed by a Registered protocol before the access specified in Section 5. **Exploratory analysis** is any analysis not meeting that condition."
- **Why it improves the Constitution:** §5's preregistration rule is the strongest anti-HARKing control in the document, and it turned on two undefined terms. Undefined, an author could label a post-hoc analysis "confirmatory" without contradicting any text. The definition is *complementary and exhaustive* — every analysis is one or the other — so there is no unclassified residue, and the burden falls on the party claiming confirmatory status.
- **Trade-offs:** Anchoring on "represented as" makes classification depend on how the analysis is presented rather than on its intrinsic properties. This is deliberate: it is checkable from repository evidence, whereas intent is not. A consequence is that an analysis can be re-classified by changing how it is represented — but §5 already forbids representing post-access selections as confirmatory.
- **New risks:** Introduces a forward cross-reference from §2 to §5, adding a maintenance dependency (see F-6).
- **Backward compatibility:** Non-breaking. Formalises the existing §5 distinction rather than altering it.

### A-4 — "Reported as scientific success" (ADV-024)

- **Section:** 2, definitions
- **Class:** Scientific
- **Change:** Added — "**Reported as scientific success** means representing, in a version-controlled scientific record, Decision, Result, Interpretation, Claim, or conformance record, test success as support for a scientific conclusion."
- **Why it improves the Constitution:** §3's prohibition ("Passing software tests … MUST NOT be reported as scientific success") was unenforceable because the prohibited act was undefined. The definition bounds it to representations *in version-controlled records*, which makes it decidable from repository evidence as §1 requires, and deliberately excludes informal speech, which the repository cannot govern.
- **Trade-offs:** The bound to version-controlled records means the same conflation in a paper, slide, or message is out of constitutional scope. This is a correct scoping choice — §2 limits Repository evidence to version-controlled content — but it does leave the highest-visibility venue ungoverned.
- **New risks:** The enumeration ("scientific record, Decision, Result, Interpretation, Claim, or conformance record") is closed. A record type outside the list could carry the conflation. Note that "scientific record" is itself defined in §2 as a nine-member union, so coverage is broad.
- **Backward compatibility:** Non-breaking. Narrows an existing prohibition to a decidable form.

### A-5 — Permissive force of MAY (ADV-025)

- **Section:** 1
- **Class:** Clarification
- **Change:** Appended — "MAY indicates permission, not obligation, and does not imply that conduct not stated with MAY is prohibited unless another requirement prohibits it."
- **Why it improves the Constitution:** §1 declared MAY normative without stating its effect. MAY appears 12 times in the document, several in load-bearing positions (§4 automated systems, §7 exclusion of Invalid Results, §12 retention of nonconforming content). Without a stated effect, a strict reviewer could read the Constitution as default-deny — that everything not expressly permitted is forbidden — which would make ordinary work nonconforming. The amendment fixes the default as permissive-unless-prohibited.
- **Trade-offs:** Confirms an open-world reading, so the Constitution constrains only what it names. Given §5's rule that no ontology or conclusion is constitutional, this is the intended posture, but it means gaps are permissive by default rather than fail-closed.
- **New risks:** Mild tension with the fail-closed provisions in §4 and §9. Those are explicit MUST-level rules for specific transitions, so they override the general default; the tension is one of tone, not of logic.
- **Backward compatibility:** Non-breaking and clarifying only.

### A-6 — Claim assessability (ADV-027)

- **Section:** 2, Claim definition
- **Class:** Editorial
- **Change:** "a proposition that **can be assessed** as supported, opposed, or unresolved" → "a proposition that **is assessable** as supported, opposed, or unresolved".
- **Why it improves the Constitution:** Terra's objection is that "can be assessed" reads as bare logical possibility. "Is assessable" states a present property of the proposition rather than a hypothetical capacity.
- **Trade-offs:** **This amendment is weaker than the defect Terra described.** Terra's stated defect was that the definition "does not require a Claim itself to identify an actual assessment method or assessment state"; the mandated minimum wording does not add either requirement. The two phrasings are near-synonymous in ordinary English, so the residual gap is largely untouched by this change alone. It was implemented as specified because Terra's report is authoritative and the instruction was to implement the minimum amendment, not to redesign it. The residual is materially mitigated by A-7, which requires every Claim to state a falsifying observation. See Limitation L-1.
- **New risks:** None identified.
- **Backward compatibility:** Non-breaking.

### A-7 — Universal Claim falsifiability (ADV-028)

- **Section:** 5, new opening paragraph
- **Class:** Scientific
- **Change:** Added — "Every Claim MUST state its Scope and at least one feasible Observation, test outcome, or Result that could count against it."
- **Why it improves the Constitution:** This is the most substantive amendment in v1.2.0. v1.1.0 required adverse observations only for Claims "used to justify a scientific conclusion or action", and required falsifiability of Principles. Unfalsifiable Claims could therefore accumulate in the record so long as nothing formally relied on them — and could later be promoted to justificatory use, or cited informally, without ever having been falsifiable. Given that Project P1's stated purpose is falsification, a falsifiability floor that applied only on use was the largest scientific gap in the document. The amendment makes falsifiability an *entry* condition rather than a *use* condition.
- **Trade-offs:** Materially raises the cost of recording a Claim, and may push authors to record propositions as Questions or Unknowns instead — which is acceptable, since §2 and §8 give both first-class status and §8 forbids silently closing them. Some legitimately useful propositions (existence statements, scoping assertions) are awkward to falsify and may be misclassified to avoid the burden.
- **New risks:**
  - **Ontology compression.** §2 defines Hypothesis as "a Claim paired with an operational test and a possible outcome that counts against it". Now that every Claim requires a possible adverse outcome, the *sole* remaining distinction between Claim and Hypothesis is the operational test. The boundary survives but is narrower, and is a predictable source of reviewer disagreement. See F-2.
  - **Retroactive nonconformance.** Existing Claims lacking adverse observations become nonconforming on adoption. §13's non-retroactivity rule and §12's provision for labelled nonconforming content together handle this without new text, but a migration pass is required. See the impact assessment.
- **Backward compatibility:** **Breaking for existing Claim records.** Mitigated, not eliminated, by §13 paragraph 5.

### D-1 — Falsifiable disambiguation (derived, from A-7)

- **Section:** 5, second sentence of the new paragraph
- **Class:** Clarification
- **Change:** Added — "This requirement does not by itself require a declared decision rule; a Claim is Falsifiable only when it also satisfies the decision-rule condition in Section 2."
- **Why it was added:** A-7's mandated wording deliberately mirrors §2's definition of **Falsifiable** but omits its final clause, "under its declared decision rule". Without D-1, a reviewer faces an unresolvable question: does A-7 require every Claim to be Falsifiable as defined, thereby importing the decision-rule requirement, or not? Both readings are textually available and they impose materially different burdens. D-1 fixes the narrower reading, preserving Terra's stated minimum. Objectives 3 and 4 — remove ambiguity, reduce reviewer disagreement — are not achievable here without it.
- **Trade-offs:** Adds text not mandated by Terra. It resolves the ambiguity in the *permissive* direction; the ratifying humans may prefer the stricter reading, in which case D-1 should be replaced by "Every Claim MUST state its Scope and MUST be Falsifiable within that Scope," and A-7's first sentence struck.
- **New risks:** None identified. Introduces no new concept; disambiguates two existing ones.
- **Separability:** Strike D-1 and A-7 still conforms to Terra's minimum, at the cost of the ambiguity returning.

### D-2 — Attestation cross-reference (derived, from A-1)

- **Section:** 4, paragraph 2
- **Class:** Editorial
- **Change:** "and an Independent reviewer attestation" → "and an Independent reviewer attestation satisfying Section 13".
- **Why it was added:** The content requirements for an attestation live in §13 (Amendments), but §4 (Domain-standard activation) also depends on them and previously pointed nowhere. A-1 increases what an attestation must contain, which widens the consequence of missing the link. Zero semantic change — §13's definition was already general — but it removes a reviewer's need to infer the connection.
- **Trade-offs:** None material.
- **New risks:** Adds a cross-reference that must be maintained if §13 is renumbered. See F-6.
- **Separability:** Fully separable.

### R-1 — Governance Registry consistency repair (not a constitutional amendment)

- **File:** `GOVERNANCE_REGISTRY.yaml`
- **Class:** Governance
- **Change:** `version` `"1.0.0"` → `"1.2.0"`; `scope` and `authority_source` aligned to the Constitution's exact wording.
- **Why:** §4 requires the Registry to carry the same identity, status, Scope, responsibility, authority, and jurisdiction as the artifact "without contradiction", and states that "**If any required field is absent or inconsistent, the artifact has no authority.**" The Registry recorded the Constitution at v1.0.0 while the document declared v1.1.0, and gave divergent Scope and authority-source text. On a literal reading the Constitution had no authority in the pre-existing working tree. This repair is a precondition for ratification, not a discretionary improvement.
- **Not repaired (requires humans):** `authority_assignments.constitutional_steward` remains `[]`; `adopter_attestation` and `independent_reviewer_attestation` remain `null`. These are the §13 bootstrap elements and cannot be supplied by an automated agent — §4 is explicit that automated systems "MUST NOT supply human authority or independent review."

---

## 3. Audit report

Nine audits were performed against v1.1.0. Findings marked **[Applied]** are addressed in v1.2.0. Findings marked **[Reported]** are outside Terra's unresolved set and outside the mandate to avoid speculative change; they are recorded for the ratifying humans and recommended for a future revision.

### 3.1 Consistency audit

- **F-1 [Reported] — Lowercase "independent reviewer" in §1.** §1 reads "permits an independent reviewer to determine compliance", using lowercase where §2 defines the capitalised term **Independent reviewer**. §2's own Scope and Operational definitions capitalise it. §1 is the outlier. A reader could argue §1 invokes a weaker, undefined notion. Terra cited this exact sentence as resolving ADV-002, which makes its precision load-bearing. Recommended fix: capitalise. Not applied — Terra deemed the sentence sufficient, and altering cited resolving text would exceed the mandate.
- **F-2 [Reported, consequence of A-7] — Claim/Hypothesis boundary compression.** See A-7 risks. Recommended for the next revision: state explicitly in §2 that a Hypothesis is a Claim that additionally identifies an operational test.
- **F-3 [Reported] — "legacy" vs "Legacy".** §4 lists "legacy" lowercase among classes without authority; §14 defines **Legacy** capitalised as an adoption-time classification. §11 forbids synonyms creating distinct object types. Low severity; recommended alignment.

### 3.2 Ontology audit

- **F-4 [Reported] — "Evidence record" is undefined.** §2 defines **Scientific record** as "a Question, Observation, **Evidence record**, Claim, Hypothesis, Result, Interpretation, Principle, or Unknown", but §2 defines **Evidence**, not "Evidence record", and §2's closing sentence enumerates the distinct object kinds as "Observation, **Evidence**, Interpretation, Decision, and Principle". Either "Evidence record" is a synonym for Evidence — which §11 forbids, since synonyms "MUST NOT create distinct object types" — or it is a distinct undefined kind. Not applied: the correction is one word, but choosing between the two readings is an ontology decision reserved to the ratifying humans, not an editorial one.
- **F-5 [Reported] — Lifecycle states not in the ontology.** §4 refers to "Historical, superseded, rejected, withdrawn, archived, generated, legacy, and Draft" artifacts; §9's minimum lifecycle defines only Draft, Active, Superseded, Withdrawn. §9 says "minimum", so additional states are permitted, but *rejected*, *archived*, and *historical* are used without definition or entry criteria. Low severity.

### 3.3 Authority audit

- **F-6 [Reported] — The Governance Registry has no position in the precedence order.** §4 orders authority as (1) Constitution, (2) Active Domain standard, (3) Active Registered protocol or Decision, (4) implementation and documentation. The Registry is a Normative artifact — §11 assigns it a distinct primary responsibility — but it appears at no level. If the Registry and a Domain standard conflict, no ordering rule resolves it. In practice §4's "if any required field is … inconsistent, the artifact has no authority" fails the situation closed, so the gap is mitigated rather than open. Recommended: place the Registry explicitly at level 1 alongside the Constitution, or state that it is constitutive rather than ordered.
- **F-7 [Verified sound] — No self-activation path.** §4 "A standard MUST NOT authorize its own activation", §13 "This bootstrap authority ends upon adoption", and §4's automated-systems prohibition together close the obvious escalation routes. Consistent with Terra's resolution of ADV-001, ADV-007, ADV-010.
- **F-8 [Applied via D-2]** — §4's attestation requirement previously had no pointer to its content specification.

### 3.4 Lifecycle audit

- **F-9 [Reported, material to this revision] — The Constitution does not state whether §13's amendment requirements govern revision of a *Draft* Constitution.** §9 and §4 both state that Draft artifacts have no authority. v1.1.0 was never adopted: the Registry records `status: Draft`, no steward, and null attestations. Strictly, v1.2.0 is therefore **not** an amendment under §13 paragraph 4 — which requires "approval by a Registry-listed constitutional steward", of whom none exists — but a revision of an unadopted Draft, to be ratified through §13 paragraph 3 (initial adoption). The Constitution is silent on this case.
  - **Operative assumption for this record:** v1.2.0 is a Draft revision. §13's amendment requirements have been satisfied *voluntarily* as best practice and become binding only after adoption.
  - This finding does not block ratification, but it determines *which* §13 path the ratifying humans must use. Getting it wrong would produce an adoption record that cites an authority that does not exist.
  - Recommended wording for a future revision: "Revision of this Constitution before its initial adoption is governed by the adoption requirements of this Section, not by its amendment requirements."
- **F-10 [Reported] — Registry self-listing.** §2 defines **Active**, for a Normative artifact, as "listed as Active in the Governance Registry". The Registry is itself a Normative artifact, so its own Active status depends on listing itself. §9 exempts its *initial activation* to §13, and Terra resolved ADV-008, but the ongoing case is unaddressed. Very low severity.

### 3.5 Scientific-method audit

- **F-11 [Applied — A-7]** Falsifiability floor raised from use-conditional to universal.
- **F-12 [Applied — A-3]** The preregistration boundary now rests on defined terms.
- **F-13 [Applied — A-2]** Digest integrity now has a required security property.
- **F-14 [Verified sound]** The anti-motivated-reasoning stack is coherent: §5 preregistration and mandatory alternatives; §6 prohibition on promoting or discarding Evidence by agreement with a preferred conclusion; §7 negative-result retention; §8 permanent Unknowns; §3 separation of governance approval from scientific support. A-4 closes the remaining reporting loophole in §3.
- **F-15 [Reported] — No requirement to quantify uncertainty in a Result.** §7 requires an Interpretation to state uncertainty, but a Result need only be "an immutable record of measurements and protocol facts". A Result may therefore carry a point estimate with no error term, and the uncertainty obligation attaches only downstream. Arguably correct — uncertainty quantification is a domain-standard concern under §5's prohibition on constitutional constants — but worth an explicit decision.

### 3.6 Cross-reference audit

All cross-references verified against the v1.2.0 text:

| Location | Target | Status |
|---|---|---|
| §2 Confirmatory analysis → Section 5 | §5 ¶3 unblinded-access rule | **Valid** (new, A-3) |
| §5 ¶1 → Section 2 decision-rule condition | §2 **Falsifiable** | **Valid** (new, D-1) |
| §4 ¶2 → Section 13 | §13 ¶2 attestation content | **Valid** (new, D-2) |
| §9 ¶1 → Section 13, Section 4 | Activation provisions | Valid |
| §10 ¶5 → Section 6 | Manifest requirement | Valid |
| §14 ¶2 → Section 4 | Legacy activation | Valid |

- **F-16 [Reported] — Section-number coupling.** All six cross-references use section *numbers*. Any future renumbering silently breaks them, and nothing in the document requires a renumbering check. v1.2.0 adds three such references, increasing exposure. Recommended: add cross-reference integrity to the §12 mechanical-check set.

### 3.7 RFC-2119 audit

- **Verified:** the document uses exactly the five terms §1 declares — MUST (112), MUST NOT (44), SHOULD (5), SHOULD NOT (2), MAY (12, now 13). Zero occurrences of SHALL, REQUIRED, RECOMMENDED, or OPTIONAL. The keyword set is closed and self-consistent; no undeclared normative term is in use.
- **F-17 [Applied — A-5]** MAY's effect is now stated.
- **F-18 [Reported] — SHOULD departures are not centrally traceable.** §1 permits departure from a SHOULD when "the affected record states the reason, risk, and scope". With only 7 SHOULD/SHOULD NOT occurrences this is manageable, but there is no register of departures, so a reviewer cannot enumerate them. Low severity at current scale.

### 3.8 Long-term maintainability audit

- **F-19 [Reported] — Requirements are not individually addressable.** Sections are numbered; paragraphs, sentences, and list items are not. §5 alone carries eight enumerated obligations plus five unnumbered paragraphs. Amendments, audits, and conformance claims must therefore cite requirements by quotation. This is the single largest structural obstacle to objective 4 (reduce reviewer disagreement) and objective 6 (maintainability) — Terra's own report had to quote text rather than cite clause identifiers. **Recommended for v1.3.0:** stable clause identifiers (e.g. §5.3, §5.3.a) assigned once and never reused. Not applied: this is an architectural change touching every section, would produce a diff in which the substantive amendments could not be reviewed, and was not identified by Terra.
- **F-20 [Reported] — Attestation content is specified inside §13.** §13 is titled Amendments, but its attestation definition is general and §4 depends on it. A reader looking for attestation requirements has no reason to look under Amendments. D-2 mitigates by pointing there explicitly. Recommended for a future revision: relocate to §2 as a definition. Not applied — relocation is architectural.
- **F-21 [Applied — R-1] — Dual-maintenance of version metadata.** The Constitution's version exists in both the document header and the Registry, with no mechanical check binding them. They had already diverged. Repaired; recommended for the §12 mechanical-check set.

### 3.9 Future extensibility audit

- **F-22 [Verified sound] — Delegation pattern is consistent.** §5's "No scientific constant, threshold, model, ontology, hypothesis set, or conclusion is constitutional" is honoured by every amendment in v1.2.0. A-2 in particular delegates algorithm choice to a Domain standard rather than naming SHA-256, which keeps the Constitution stable across cryptographic transitions. This is the correct extensibility posture and was preserved deliberately.
- **F-23 [Reported] — No procedure for migrating historical digests.** Consequence of A-2; see Limitation L-2.
- **F-24 [Verified sound] — Amendment path is complete.** §13's seven required elements cover failure, alternatives, consequences, migration, rollback, terminology review, and attestation. No extensibility blocker identified.

---

## 4. Architectural impact assessment

**Architecture preserved.** v1.2.0 introduces no new section, no new object kind, and no new authority level. Every change lands inside an existing structure: definitions in §2, normative force in §1, claims in §5, provenance in §6, amendments in §13. The four-level authority ordering, the Draft → Active → Superseded/Withdrawn lifecycle, the separation-of-responsibilities model, and the delegation-to-domain-standards pattern are all unchanged.

**Net text change:** +6 sentences, +2 definitions, 2 word-level substitutions, 1 cross-reference. No deletions.

### Impact by object class

| Class | Impact | Required action |
|---|---|---|
| Existing Claims | **Breaking (A-7)** | Migration pass: every recorded Claim needs a stated Scope and a falsifying observation, or reclassification to Question or Unknown, or a §12 nonconformance label |
| Existing Hypotheses (H\*, H1, H2) | Low | Already carry operational tests and adverse outcomes; expected to satisfy A-7 as written. Requires confirmation, not rework |
| Existing Results, Evidence, Interpretations | None | No amendment touches them |
| Preregistrations | Low | `theory/preregistrations/` gains defined confirmatory/exploratory terms (A-3); existing content unaffected |
| External-artifact Evidence | Deferred | A-2 binds the governing Domain standard; no such standard is Active, so this cannot be satisfied yet |
| Attestations | **Breaking forward (A-1)** | Future attestations need competence and examined-records statements. None exist yet, so there is nothing to migrate |
| Domain standards | Deferred | None Active. A-2 and A-1 both create obligations that the first Domain standard must discharge |
| Governance Registry | **Repaired (R-1)** | Steward assignment and two attestations still required |

### Migration path for A-7

§13 paragraph 5 already supplies the mechanism — "affected records retain the standard version under which they were created and MAY be reassessed through a new Interpretation or Decision" — so **no new constitutional text is needed** and no record is retroactively invalidated. Operationally: at adoption, enumerate existing Claims; for each, either add the missing Scope and falsifying observation, reclassify under §2, or label nonconforming under §12. §12 explicitly permits retaining nonconforming content for migration provided it is labelled and not used to authorize a dependent transition.

Given this repository's stated purpose — reducing inherited Programs A/B/C material into falsifiable hypotheses — this migration is substantially the work the project already intends to do. A-7 makes it a precondition rather than an aspiration. That is the intended effect, and it is the main reason A-7 is the highest-value amendment in this revision.

### Rollback

Every amendment is a localised insertion or a two-word substitution. Rollback to v1.1.0 is: revert the eight edits and restore the Registry `version` to `"1.0.0"`. No dependent artifact would need to change, because no Domain standard is Active and no attestation has been issued under v1.2.0.

---

## 5. Remaining known limitations

**L-1 — ADV-027's residual gap is not closed.** Terra's stated defect was that the Claim definition "does not require a Claim itself to identify an actual assessment method or assessment state"; its minimum amendment changes only the modality. A-7 supplies the falsifying-observation half but no amendment requires a Claim to record its *current assessment state* (supported / opposed / unresolved). §5 item 8 requires a justificatory Claim to link the records "on which its current state depends", implying a state exists, but nothing requires it to be recorded. **Recommended for v1.3.0.**

**L-2 — No digest-algorithm transition procedure.** Terra listed "algorithm transition procedure" among ADV-018's gaps; its minimum amendment requires only algorithm and version. When an algorithm is deprecated, the Constitution does not say what happens to Evidence already identified under it, who decides, or whether re-digesting breaks the immutability guarantee in §7. **Recommended for the first Domain standard governing Evidence.**

**L-3 — Informal-venue conflation remains ungoverned.** A-4 binds only version-controlled records. Presenting test success as scientific success in a paper or talk is outside constitutional scope. This is a deliberate and correct scoping limit, not a defect, but it should be understood.

**L-4 — Competence is self-asserted.** A-1 requires a competence statement; nothing verifies it. In a two-person project the pool of Independent reviewers is structurally small, and §12's prohibition on self-review labelled as independent may make some reviews unsatisfiable in practice. The Constitution correctly fails closed here, but the project should expect to source external reviewers.

**L-5 — No Active Domain standard exists.** A-2 (digest algorithm), §9 (every subordinate object type needs exactly one Active Domain standard), and §5 (Evidence-admission criteria) all delegate to Domain standards, of which zero are Active. Until at least one is activated, large parts of the Constitution are structurally unsatisfiable. This is expected at bootstrap and is not a defect in v1.2.0, but it means **constitutional conformance cannot be fully claimed at ratification.**

**L-6 — Requirements are not individually addressable.** See F-19. Affects every future amendment, audit, and conformance claim.

**L-7 — Findings F-1, F-3, F-4, F-5, F-6, F-9, F-10, F-15, F-16, F-18, F-20 are reported but unimplemented.** They fall outside Terra's unresolved set. F-9 is the most consequential: it determines which §13 path ratification must use. F-4 is an ontology inconsistency that a careful reviewer will likely raise.

**L-8 — Derived amendments D-1 and D-2 exceed Terra's literal mandate.** Both are justified by identified defects rather than preference, both are separable, and both are flagged here so the ratifying humans can strike them. D-1 in particular makes a *substantive* choice — the permissive reading of A-7 — that the ratifiers may wish to reverse.

---

## 6. Ratification readiness assessment

### Confidence that v1.2.0 correctly implements Terra: **High**

All 7 unresolved findings are implemented using Terra's stated minimum wording, verified line by line against the amended file. No resolved finding was re-opened. No Terra-mandated text was paraphrased except A-1's leading connective ("It MUST also…"), which preserves meaning. Two derived amendments are disclosed and separable.

### Confidence that v1.2.0 is internally consistent: **Moderate-to-high**

All cross-references verified. The RFC-2119 keyword set is closed. No contradiction was introduced. Confidence is held below high by two known residues: the Claim/Hypothesis boundary compression from A-7 (F-2) and the pre-existing "Evidence record" ontology inconsistency (F-4), neither of which v1.2.0 resolves.

### Confidence that the repository is **ready to ratify: Low — blocked**

Three blockers, none of which an automated agent can clear:

1. **No constitutional steward.** `authority_assignments.constitutional_steward` is `[]`. §13 requires the activating change to assign at least one steward. Without this, no §13 path can complete.
2. **No attestations.** Both `adopter_attestation` and `independent_reviewer_attestation` are `null`. §13 requires two identified humans, and §4 forbids automated systems from supplying human authority or independent review. The Independent reviewer attestation must now also satisfy A-1 (competence and examined records).
3. **§13 path undetermined (F-9).** The ratifiers must decide whether v1.2.0 is adopted as an initial adoption of a Draft or as an amendment. On the evidence — Registry `status: Draft`, no steward, null attestations — **initial adoption is the correct path**, and the amendment path is unavailable because it requires a Registry-listed steward who does not exist. This should be recorded explicitly in the adoption record.

Additionally, **§12 conformance cannot be fully claimed at ratification** because zero Domain standards are Active (L-5). This does not block adoption of the Constitution itself; §4 and §9 both anticipate a state in which no Domain standard exists and fail closed rather than open. It does mean the adoption record should state which requirements are not yet verifiable rather than reporting them as satisfied — §12 is explicit that "An unavailable check MUST be reported as not verified, never as passed."

### Recommended ratification sequence

One atomic change under §13 containing: `REPOSITORY_CONSTITUTION.md` v1.2.0; `GOVERNANCE_REGISTRY.yaml` with steward assigned and both attestations populated; this record or an equivalent; and a conformance statement identifying the revision, the checks performed, and the requirements reported as not verified. §2's definition of Atomic change requires no intervening default-branch revision in which any required element is absent — so these cannot be committed separately.
