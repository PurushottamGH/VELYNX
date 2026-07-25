# Human Constitutional Judgment Register

- **Status:** Draft
- **Scope:** Matters that require human constitutional judgment rather than engineering, in the design and activation of the P1 ecosystem
- **Responsibility:** Identify each open question, why engineering cannot settle it, the options, and what each option costs
- **Authority source:** None. This record has no normative authority and settles nothing.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 0. Why these are not engineering problems

Each item below has the same shape: the Constitution is either silent, or it is clear but the project cannot satisfy it, or satisfying it requires trading one guarantee against another. In every case a technically defensible answer exists on more than one side, and choosing among them is an exercise of authority — which §4 reserves to identified humans and §13 reserves to constitutional stewards.

An automated system may propose, check, or apply an already-authorized transition (§4 ¶4). It may not decide any of these.

Items are ordered by blocking effect, not by difficulty.

---

## H-01 · Who is the second identified human? — **BLOCKING EVERYTHING**

**The situation.** §13 ¶3 requires initial adoption to carry attestations by two identified humans, an adopter and an Independent reviewer. §2 defines an Independent reviewer as an identified human who is not an author of the reviewed change, did not produce the Evidence under review, and declares material conflicts. §4 ¶4 forbids automated systems from supplying independent review. The repository's entire history contains one human.

**Why engineering cannot settle it.** There is no technical construction that produces a second person. Every alternative — an AI reviewer, a second Git identity, a deferred attestation, a self-review labelled independent — defeats the clause it purports to satisfy.

**Options.**

| Option | Cost | Assessment |
|---|---|---|
| **A. Recruit an external independent reviewer** | Requires finding someone competent and willing; introduces a dependency on an outside party's availability | **Recommended.** Preserves every guarantee. The competence requirement (§13 ¶2, as amended by A-1) means the reviewer must actually understand the material, which narrows the field but is the point. |
| **B. Federate with a partner institution** | Slowest; requires the partner to accept §6 ¶1 provenance obligations | Best long-term answer; also resolves R-14 reviewer capture. See `07_EXTENSION_ARCHITECTURE.md` §2.6 |
| **C. Amend §13 to permit single-human adoption with deferred review** | Dissolves the Independent reviewer guarantee that §2, §12, and §13 jointly depend on | **Not recommended.** It preserves the appearance of review while removing its substance — the worst of the available outcomes, because the records would then misrepresent the process. |
| **D. Remain in Pre-Adoption Operating Mode indefinitely** | No governance takes effect; scientific work stays exploratory permanently (§2, §5 ¶3) | Honest, and safe, but forecloses confirmatory research. Viable as a holding position, not as a destination. |

**Consequence of delay.** Work executed before S-1 activates cannot later be relabelled confirmatory — §5 ¶3 fixes the pre-access condition and §13 ¶4 forbids amendments that retroactively alter a prior record's meaning. Every week of unadopted operation is a week of permanently exploratory work.

---

## H-02 · Ratify v1.2.0 as initial adoption, or as an amendment?

**The situation.** The Constitution is Draft and has never been Active. §13 ¶3 governs initial adoption; §13 ¶4 governs later amendment. The Constitution is silent on which applies to revising a Draft constitution — finding F-9 in `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md`.

**Why engineering cannot settle it.** It is a question of interpretation with consequences for what evidence the adoption change must carry.

**Assessment.** Initial adoption is the defensible reading: §13 ¶4's amendment path presupposes a Registry-listed constitutional steward, and none exists. §14's language ("Upon adoption, this Constitution supersedes the prior `REPOSITORY_CONSTITUTION.md`") also fits an adoption event rather than an amendment. Choosing amendment would require an authority that the amendment itself would create — circular.

**Recommended:** treat it as initial adoption under §13 ¶3, and record the interpretation in the adoption dossier so a future reviewer can see the reasoning rather than infer it.

---

## H-03 · Adopt amendment A-8, the General Delegation Clause? (defect D-1)

**The situation.** §4 ¶4 requires every delegation of refinement to identify five elements: subject, Scope, recipient, permitted transitions, limits. Three delegations this ecosystem depends on identify at most two:
- §9 ¶4 "Normative artifacts use the **minimum** lifecycle…" — G-2 depends on it;
- §12 ¶4 "Requirements not mechanically decidable MUST have a named manual review procedure" — G-4 and G-5 depend on it;
- §10 ¶1 "MUST be defined in versioned architecture records" — G-12 depends on it.

A strict reader concludes these standards cannot legitimately refine anything — while §10 simultaneously *requires* architecture records to exist. That is a contradiction that prevents implementation.

**Why engineering cannot settle it.** Whether the Constitution's own delegation-specification requirement applies to its own delegation clauses is a constitutional reading, not a defect to be patched by a tool.

**Options.**
- **A. Include A-8 in the adoption change** — one additive §4 paragraph enumerating the existing delegations in five-element form. Changes no existing requirement. Cheapest now, while the Constitution is Draft and no records depend on the prior text.
- **B. Adopt without A-8, activate G-2/G-4/G-5/G-12 anyway** — leaves every activation open to a well-founded challenge. An adversarial reviewer could void the lifecycle machinery of the entire stack.
- **C. Adopt without A-8 and do not activate the four affected standards** — constitutionally clean, but §10 ¶1's requirement for architecture records becomes unsatisfiable, and N-1 becomes a permanent nonconformance.

**Recommended:** A. Amending a Draft constitution costs almost nothing; amending an Active one costs a full §13 cycle including an independent attestation — the scarcest resource in the project.

---

## H-04 · Give the Governance Registry a rank in the precedence order? (defect D-2)

**The situation.** §4 orders four authority levels and omits the Registry. §2 makes the Registry the sole determinant of what is Active. So a Registry/standard conflict is formally unresolvable: the standard's authority depends on the entry, and the entry's correctness depends on the standard. Finding F-6.

**Why engineering cannot settle it.** A subordinate standard resolving its own precedence would enlarge jurisdiction, which §4 ¶4 forbids. Only §13 can fix it.

**Recommended:** include in the adoption change a clause stating that the Registry is determinative of identity, status, jurisdiction, and authority assignment, and that on conflict the artifact is nonconforming until reconciled. In one sentence: the Registry decides *whether* an artifact has authority, never *what* it requires. This keeps §2's sole-responsibility limit intact while closing the gap.

---

## H-05 · Accept §2's hard-coded Registry path, or generalize it? (defect D-3)

**The situation.** §2 pins the Registry to `GOVERNANCE_REGISTRY.yaml`. §10 ¶1 declares repository layout non-constitutional and requires it to live in architecture records. The Registry's location is therefore simultaneously constitutional and prohibited from being constitutional.

**Assessment.** Low severity. Two readings are available: (a) accept the pin as a deliberate exception and document it in §10, or (b) identify the Registry by role in §2 and require the architecture record to bind exactly one path to that role.

**Recommended:** (a) — accept and document. Option (b) is tidier but introduces an indirection in the one artifact whose location should be unambiguous to anyone opening the repository for the first time. Note also that this pin becomes materially limiting only if P1 ever needs multi-repository governance (F-1), at which point it should be revisited alongside that larger question rather than pre-emptively.

---

## H-06 · Disposition of the Program D corpus

**The situation.** §14 makes every non-activated Normative artifact Legacy at adoption. That includes `theory/PROGRAM_D_CONSTITUTION.md` ("Its authority is absolute"), `PROGRAM_D_CANONICAL.md` ("every other document must derive from this one"), `PROGRAM_D_MASTER_ROADMAP.md`, `PROGRAM_D_RESEARCH_STATE_v0.1.md`, `RESEARCH_PROTOCOL.md`, `parameter_registry.yaml`, `reproducibility.yaml`, the `theory/` specification chain, and `audits/CONSTITUTION_COMPLIANCE.md`.

**Why engineering cannot settle it.** Deciding which of these to reconstruct, archive, or abandon is a judgement about what the research programme actually is. It requires knowing which findings the project still stands behind.

**Sub-decisions:**
1. Which artifacts are worth reconstructing to the Domain Standard Interface, and which are archived?
2. Do the frozen constants in `RESEARCH_PROTOCOL.md` and `parameter_registry.yaml` survive as a revisable domain standard, or are they retired? §5 ¶6 forbids them being constitutional; it does not forbid them existing under a standard. (See H-10.)
3. Hypotheses H\*, H1, H2 — reconstruct with paired §5 ¶2 Claims, operational tests, and counting-against outcomes, or retire?
4. **T-01 and T-02:** `theory/HYPOTHESIS_DISCRIMINATION_MATRIX.md` already records that they are not mutually distinguishable. Retire one, find a discriminating protocol, or record an Unknown and block independent support for both? Under S-7 the third is automatic; the first two are choices.
5. Which of the nineteen `artifacts/exp_*` outputs are worth preserving as exploratory working output, given that none can become a confirmatory Result?

**Note.** Item 5 has a hard constitutional consequence worth stating once more: no pre-adoption execution can become confirmatory, because no Registered protocol preceded it. That is not a technicality to be worked around; it is the mechanism by which §5 ¶3 has any force at all.

---

## H-07 · Affirm the boundary on AI participation

**The situation.** §4 ¶4: automated systems "MAY propose, check, or apply an already-authorized transition; they MUST NOT supply human authority or independent review." §2 requires an Independent reviewer to be an identified human. The repository's review history is already populated with model names — Terra, GPT-5.5, Sonnet 5, DeepSeek, Nemotron, Gemini — in reviewer-shaped roles.

**Why this needs an explicit human decision rather than silent compliance.** The boundary will be under continuous pressure as models improve, and the pressure will be strongest exactly when the project is short of human reviewers — which is now. A boundary that was never explicitly affirmed erodes without anyone deciding to erode it.

**What the Constitution permits.** AI systems may draft standards, implement and run every check, attempt refutation at stage V4, produce finding sets, propose transitions, and apply transitions a human has authorized. Their findings are recorded, and the human attestation states which were examined (§13 ¶2 as amended by A-1). This is substantial.

**What it forbids, at any capability level.** Counting AI output as an attestation, as independent review, or as human authority. Relaxing this requires amending §2, §4, and §13 together, which would dissolve the guarantee those clauses jointly provide.

**Recommended:** affirm the boundary explicitly in the adoption dossier, and record the historical model-review material as adversarial input rather than review — so the record does not imply a review that did not occur.

---

## H-08 · Steward count and succession

**The situation.** §13 ¶3 requires "at least one" constitutional steward. One steward with no successor is an unrecoverable single point of failure: on their unavailability, no activation, amendment, or reversal is possible, and appointing a successor requires the authority that is unavailable (R-17).

**Sub-decisions:** how many stewards; whether their jurisdictions are disjoint or shared; if shared, the quorum rule; the succession trigger and mechanism; whether stewardship is time-bounded and renewable.

**Assessment.** §4's conflict rule (§4 ¶4) addresses conflicting *requirements*, not conflicting *stewards*. Two stewards holding the same jurisdiction who disagree produce a deadlock the Constitution does not resolve. Disjoint jurisdictions per steward use the same disjointness discipline as the rest of the stack and avoid inventing a voting mechanism the Constitution never contemplated.

**Recommended:** more than one steward, with disjoint jurisdictions and a named successor for each; time-bounded assignments with renewal as a reviewed transition.

---

## H-09 · Retention horizon and custody funding

**The situation.** §7 ¶4 and §8 ¶1 make retention of Results, Negative Results, and Unknowns permanent. §6 ¶5 provides for *recording* loss, not authorizing it. There is no expiry mechanism anywhere in the Constitution.

**Why engineering cannot settle it.** It is a commitment of resources over decades, and the honest question is whether the project can actually keep the promise it is making.

**Options.** Fund permanent retention with tiering under G-7 (digests and manifests permanent, bulk artifacts migrated to cheaper storage with recorded recovery procedures) · constrain what is retained by constraining what is executed · amend the Constitution to permit bounded, recorded, reviewed disposal.

**Assessment.** The failure mode to avoid is cost pressure producing quiet deletion — exactly what §7 ¶4 exists to prevent. If the promise cannot be kept, amending openly is far better than breaking it silently. Recommended: tiering first; revisit if infeasible.

---

## H-10 · Do the frozen constants survive?

**The situation.** `RESEARCH_PROTOCOL.md` declares constants "locked and cannot be adjusted without explicit auditor approval": b=1.0, a λ_model formula, ECE<0.10, an M margin of 0.05. `parameter_registry.yaml` marks parameters "NOT configurable" and "scientific constant, not tunable." `reproducibility.yaml` freezes free-energy coefficients that `PROGRAM_D_CANONICAL.md` marks `[REJECTED]` (N-7).

**The constitutional position.** §5 ¶6: "No scientific constant, threshold, model, ontology, hypothesis set, or conclusion is constitutional. Such objects MUST be governed by a revisable domain standard or registered protocol." So these constants may exist — but only inside something amendable, with a stated basis and a revision path.

**Why engineering cannot settle it.** Whether each constant is still believed, and on what evidence, is a scientific judgement.

**Sub-decisions:** for each constant — is it a *pre-registered decision threshold* (belongs in a Registered protocol under S-1), a *measurement convention* (belongs in a domain standard), or a *claim about the world* (belongs in a Claim under S-6 with a falsifier)? The three have different homes and different revision paths, and conflating them is how a threshold becomes an unquestioned assumption.

Also resolve the direct contradiction in N-7 — two artifacts freezing incompatible values is a §4 ¶4 same-level conflict, and both are nonconforming until an authority resolves it.

---

## H-11 · How much governance can the project actually sustain?

**The situation.** Twenty-four standards, a nine-stage pipeline, per-transition Decisions, and per-activation attestations. The binding resource is independent human review.

**Why engineering cannot settle it.** It is a capacity judgement about people.

**The trade-off, stated plainly.** §12 ¶1 makes an unverifiable requirement a nonconformance. So activating more standards than can be verified *manufactures* nonconformance. Six Active standards fully verified is a better constitutional position than twenty-four partly verified — and a much better one than twenty-four whose verification is nominal.

**Options.** Activate the full stack over time as capacity allows (M-3 → M-8) · activate only the foundation and execution tiers and defer the rest indefinitely · reduce the standard count by merging jurisdictions further, accepting coarser separation.

**Recommended:** the roadmap's phased order, with an explicit decision point after M-4: if review capacity has not grown, stop there rather than proceeding to M-5. Governing less, properly, is the constitutionally sound choice — not a compromise.

---

## H-12 · Add clause identifiers to the Constitution?

**The situation.** The Constitution has no addressable clause identifiers (finding F-19). `A-39` requirement coverage — the check that guarantees §12 ¶1 traceability — must therefore be maintained as a hand-curated map, which decays silently as the corpus grows (R-23).

**Why this is borderline-engineering but ultimately constitutional.** Adding identifiers is a textual change to the Constitution, which §13 governs regardless of how mechanical it looks. It also changes how every existing citation should be written.

**Assessment.** Cheap now while the Constitution is Draft; a full §13 amendment cycle later. The mechanical benefit is large and compounds: every check, every conformance claim, and every attestation becomes precisely anchored instead of approximately.

**Recommended:** include at adoption.

---

## H-13 · Does `theory/PROGRAM_D_CONSTITUTION.md` get withdrawn explicitly?

**The situation.** A second document claiming "Its authority is absolute" over Program D. §1 ¶2 forbids any artifact from overriding the Repository Constitution by declaring itself absolute; §14 makes it Legacy at adoption.

**Why a decision is needed.** §14 strips its authority automatically, but the document remains in a live path asserting absolute authority. §4 ¶5 requires Legacy content to remain *distinguishable* from Active requirements — and a file titled "Constitution" asserting absoluteness is not distinguishable to a reader who has not read §14.

**Options.** Withdraw explicitly with a stated reason and archive it · re-scope its content into a properly registered Program D domain standard · leave it and rely on §14.

**Recommended:** explicit withdrawal plus archival. Relying on §14 alone is exactly the gap between "has no authority" and "is not being followed" that R-02 describes.

---

## H-14 · Accept an external timestamping dependency?

**The situation.** The preregistration guarantee — §2's Registered protocol and §5 ¶3's pre-access fixing — cannot be verified from inside the repository. Git timestamps are author-controlled; §5 ¶3's actual trigger is unblinded *access*, which leaves no trace at all (R-08).

**Why this needs a human decision.** It introduces a dependency on a third party, and it makes a currently-implicit weakness explicit and dated.

**Options.** A public timestamping service (RFC 3161 or a transparency log) · registration with an external study registry · a signed receipt from the independent reviewer at registration time · accept the exposure and record it as a permanent Unknown.

**Assessment.** The fourth option is honest but leaves the scientific stack's foundational guarantee resting on one actor's honesty. The third is the cheapest that actually works and composes naturally with H-01: the same external human who supplies independent review can countersign registrations.

**Recommended:** implement before any confirmatory work begins (M-1.7). It cannot retroactively secure past registrations, so its value strictly decreases with delay.

---

## Summary

| Id | Judgment required | Blocks | Recommendation |
|---|---|---|---|
| H-01 | Second identified human | **everything** | Recruit external reviewer or federate |
| H-02 | Adoption vs amendment path | M-0 | Initial adoption under §13 ¶3 |
| H-03 | Amendment A-8, general delegation (D-1) | G-2, G-4, G-5, G-12 | Include at adoption |
| H-04 | Registry precedence rank (D-2) | R-10 mitigation | Include at adoption |
| H-05 | §2 path pin vs §10 (D-3) | nothing | Accept and document |
| H-06 | Program D corpus disposition | M-6 | Decide before adoption; inventory first |
| H-07 | AI participation boundary | credibility of all review | Affirm explicitly |
| H-08 | Steward count and succession | R-17 mitigation | >1 steward, disjoint jurisdictions, named successors |
| H-09 | Retention horizon and funding | G-7 design | Tiered custody; amend openly if infeasible |
| H-10 | Fate of frozen constants | M-6 | Classify each; resolve the N-7 contradiction |
| H-11 | Sustainable governance scope | M-5 onward | Phase, with a decision point after M-4 |
| H-12 | Clause identifiers (F-19) | A-39 durability | Include at adoption |
| H-13 | Withdraw the second constitution | R-02 mitigation | Explicit withdrawal + archive |
| H-14 | External timestamping | confirmatory research | Implement before M-4 |

**Five of these are cheapest at adoption** — H-02, H-03, H-04, H-12, and the framing of H-07 — because amending a Draft constitution costs a paragraph while amending an Active one costs a full §13 cycle including an independent attestation, which is precisely the resource the project has least of.

**One blocks everything.** No further design work changes that.
