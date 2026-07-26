# Risk Assessment

- **Status:** Draft
- **Scope:** Risks to the operation and durability of the P1 constitutional ecosystem
- **Responsibility:** Identify risks, their mechanism, severity, detection, and mitigation
- **Authority source:** None. This record has no normative authority.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. Framing

Severity is judged by *consequence if realized*, not by probability alone:

- **Critical** — the governance system cannot function, or its central guarantee is void.
- **High** — a constitutional guarantee is defeated in a specific area.
- **Medium** — degraded assurance or significant cost.
- **Low** — friction or localized defect.

Several risks are **already realized** in the current repository. Those are marked accordingly; they are not forecasts.

---

## 2. Structural risks

### R-01 · No second identified human — Critical — **realized**
**Mechanism.** §13 ¶3 requires two identified humans for initial adoption. §2 defines an Independent reviewer as an identified human who is not an author. §4 ¶4 forbids automated systems from supplying independent review. Exactly one human appears in the entire repository history.
**Consequence.** Adoption cannot occur; no Domain standard can activate; every activation path fails closed under §4 ¶2. The entire ecosystem is inert. This is not a delay — it is a precondition failure.
**Detection.** `DA-23`, `DA-38`, and direct inspection of `GOVERNANCE_REGISTRY.yaml` (`constitutional_steward: []`, both attestations `null`).
**Mitigation.** Recruit an external reviewer, or federate (M-9). **No engineering mitigation exists**, and none should be invented: weakening §2 or §13 to accommodate one person would dissolve the guarantee those clauses exist to provide while retaining its appearance. Escalated as H-01.
**Residual.** Total until resolved.

### R-02 · Legacy shock at adoption — Critical — realized on adoption
**Mechanism.** §14: every Normative artifact not activated in the adoption change becomes Legacy with no authority. Approximately thirteen artifacts currently assert canonical, absolute, frozen, or supreme status, including a competing `theory/PROGRAM_D_CONSTITUTION.md`, `PROGRAM_D_CANONICAL.md` ("every other document must derive from this one"), `RESEARCH_PROTOCOL.md`'s frozen constants, and the Program D specification chain that active work depends on.
**Consequence.** At the instant of adoption, the documents governing current research lose authority while remaining in live paths and continuing to be followed. Either work stalls awaiting re-activation, or it proceeds against artifacts §4 ¶5 says have no authority — producing nonconformance that §12 ¶2 forbids from authorizing dependent transitions.
**Detection.** `DA-07`, `DA-30`; the M-1.8 legacy inventory.
**Mitigation.** Complete the M-1.8 inventory *before* adoption so the scope is known; execute M-6 disposition promptly after M-3; accept that some Program D material will need full reconstruction rather than grandfathering. Decide H-06 explicitly.
**Residual.** High until M-6 completes. This is the risk most likely to be underestimated, because the failure is social — people follow documents that have lost authority — and no check detects being followed.

### R-03 · Governance overhead exceeds research throughput — High
**Mechanism.** Twenty-four standards, each with lifecycle definitions, verification mappings, and per-transition Decisions; a nine-stage pipeline; per-transition eight-element records. The binding resource is independent human review.
**Consequence.** Either research slows to governance speed, or governance is bypassed and becomes theatre — the more common outcome, and the worse one, because the records then misrepresent the process.
**Detection.** Transition latency; the ratio of recorded transitions to actual work; conformance claims whose coverage is thin.
**Mitigation.** Proportionality is built in: §12 ¶1 scopes conformance to *Affected requirements*, so a small change carries small obligations. Batch activation (§4 ¶2) reduces coordination cost without reducing review. Most importantly: **activate fewer standards.** Six Active standards fully verified beats twenty-four partly verified, because §12 ¶1 makes an unverifiable requirement a nonconformance. Escalated as H-11.
**Residual.** Medium with discipline; High without.

### R-04 · Activation deadlock — Medium
**Mechanism.** Each activation needs a steward approval plus an independent attestation; the dependency graph makes six standards near-simultaneous.
**Consequence.** Serialized review cycles consume the scarcest resource for no constitutional gain.
**Mitigation.** §4 ¶2 requires activations to be atomic, not solitary — several standards may activate in one Atomic change, with one attestation each. §13 permits no batching of attestations.
**Residual.** Low once understood; the deadlock is largely an artifact of misreading §4 ¶2 as one-standard-per-change.

### R-17 · Steward single point of failure — High
**Mechanism.** §13 requires "at least one" steward. One steward with no successor holds the sole authority to amend the Constitution, activate standards, and authorize reversals.
**Consequence.** On that person's unavailability, the repository freezes permanently: no activation, no amendment, no reversal, and no mechanism to appoint a successor — because appointing one requires the authority that is unavailable. Over twenty years this is not a tail risk.
**Detection.** Inspection of `governance/authority/`.
**Mitigation.** DG-3 MUST require a named successor for every authority assignment, and the adoption change SHOULD assign more than one steward with disjoint or clearly-quorumed jurisdictions (see `07_EXTENSION_ARCHITECTURE.md` §2.4 — prefer disjoint jurisdictions over inventing a voting rule the Constitution never contemplated). Escalated as H-08.
**Residual.** Medium with succession; Critical without.

---

## 3. Epistemic-integrity risks

### R-08 · Preregistration order is not verifiable — High — realized
**Mechanism.** §2 defines a Registered protocol by registration *preceding* execution, and §5 ¶3 fixes eleven elements before unblinded access. The only evidence available inside the repository is Git commit metadata, which is author-controlled and trivially backdated. §5 ¶3's actual trigger is *access*, which leaves no trace at all.
**Consequence.** The confirmatory/exploratory distinction — the load-bearing guarantee of the entire scientific stack — rests on a single actor's honesty. `DA-20` verifies only that no *recorded* execution precedes registration.
**Detection.** `DA-20`, registered **Advisory** by construction. Reporting it Active would misrepresent a heuristic as a proof.
**Mitigation.** External timestamping (public timestamp service, signed third-party receipt, or an external registry) plus commit signing. Cheap, additive, no governance change required — M-1.7. Until then, record the exposure as an Unknown rather than treating the guarantee as held.
**Residual.** High until an external anchor exists; Low after.

### R-05 · Green CI read as conformance — High — realized
**Mechanism.** §3 ¶7 forbids reporting test success as scientific success. §12 ¶1 requires an unavailable check to be reported as not verified, never passed. `.github/workflows/ci.yml` terminates lint and test steps with `|| true` and targets `core/` and `validation/`, which no longer exist; those jobs cannot fail. `RESEARCH_PROTOCOL.md` additionally imposes a "100% pass rate" gate — exactly the construct §3 ¶7 targets.
**Consequence.** A green pipeline that verifies nothing is cited as evidence of conformance and, worse, of scientific validity.
**Detection.** `DA-29`, `DA-51`, `DA-61`; every check asserting a non-empty target set.
**Mitigation.** M-1.5 CI repair; prohibit exit-code suppression in any conformance-relevant check; make Advisory a registration status rather than a runtime trick; DG-5 claims enumerate criteria actually assessed.
**Residual.** Low after M-1.5.

### R-06 · Ontology divergence — High
**Mechanism.** The Constitution defines eleven scientific kinds plus Decision; the P1 Research OS defines twelve `ObjectType` values, adding `research_artifact` and `principle_candidate` and omitting `Observation` and `Principle`. §11 ¶3 forbids synonyms creating distinct types and identical names concealing distinct ones. §2 forbids using one kind as a substitute for another.
**Consequence.** Two type systems drift; records validate against a schema that disagrees with the governing standard; the Observation/Evidence boundary — the boundary every computational domain is tempted to blur — is absent from the code entirely.
**Detection.** `DA-10`, `DA-27`; the M-2 reconciliation.
**Mitigation.** Gate O-1 activation on M-2 completion. Add `observation`. Resolve `principle_candidate` versus Principle explicitly. Assign or remove `research_artifact`. Map `experiment` onto S-1's types.
**Residual.** Low after M-2; High if O-1 activates before it.

### R-18 · File-drawer effects survive the mechanism — Medium
**Mechanism.** §7 ¶4 forbids deleting, hiding, or relabelling Negative Results. But a Result never recorded is undetectable: `DA-60` can only compare records that exist.
**Consequence.** Selective recording produces a literature-shaped bias inside a repository designed to prevent it.
**Detection.** `DA-60` (Advisory, statistical); `MRP-17` reconciles execution evidence against recorded Results.
**Mitigation.** Custody manifests registered at execution start rather than at Result creation, so an execution is on record before its outcome is known. This is the single most effective structural fix available and costs little.
**Residual.** Medium — irreducible without external execution logging.

### R-19 · Non-distinguishable hypotheses treated as independently supported — Medium — realized
**Mechanism.** `theory/HYPOTHESIS_DISCRIMINATION_MATRIX.md` already records that propositions T-01 and T-02 "are not mutually distinguishable." §2 requires a Hypothesis to pair a Claim with an operational test and a counting-against outcome; two hypotheses predicting identical observables under all registered protocols cannot both be independently tested.
**Consequence.** Evidence claimed for one is evidence for both; support is double-counted.
**Detection.** `MRP-11`.
**Mitigation.** Under S-7 the recorded non-distinguishability forces an Unknown and blocks independent support claims until a discriminating protocol exists. Resolve in M-6. Escalated as H-06.
**Residual.** Low once S-7 is Active.

---

## 4. Mechanical risks

### R-10 · Registry as unranked single point of authority — High
**Mechanism.** §2 makes the Registry determinative of what is Active; §4's precedence order omits it (defect DD-2, finding F-6). A Registry/standard conflict is formally unresolvable: the standard's authority depends on the entry, and the entry's correctness depends on the standard.
**Consequence.** An unresolvable conflict in the one artifact every other artifact's authority depends on. Registry corruption or loss makes every Active artifact's authority simultaneously unverifiable.
**Mitigation.** Amend §4 to state that the Registry determines *whether* an artifact has authority, never *what* it requires (H-04); include this in the adoption change while amendment is cheap. Append-only `registry/transitions/` permits reconstruction. `DA-01`/`DA-03` detect drift.
**Residual.** Medium with the amendment; High without.

### R-20 · Interface MAJOR change de-authorizes the whole stack — High
**Mechanism.** §4 ¶1: an artifact missing a required field has no authority. If the Domain Standard Interface adds a required declaration without migrating every Active standard in the same Atomic change, a revision exists in which all Active standards lack a required element.
**Consequence.** Every Active standard loses authority simultaneously, and every transition authorized in that window is void.
**Mitigation.** `04_DOMAIN_STANDARD_INTERFACE.md` §6: interface MAJOR changes require a named migration plan covering every Active standard in the same change. `DA-02`/`DA-03` detect the state, but detection after the fact does not undo the void transitions.
**Residual.** Low with the rule enforced; the worst available mechanical failure without it.

### R-21 · Check rot — High
**Mechanism.** Paths are renamed; a check silently matches zero files and reports success. Already realized: `ci.yml` lints directories that no longer exist.
**Consequence.** Zero findings misread as conformance — the most insidious automation failure, because it looks exactly like success.
**Mitigation.** Every check asserts a non-empty target set and reports `NOT_VERIFIED` otherwise; self-test fixtures with known-violating inputs, so a check that passes its own negative fixtures is Broken by definition; `DA-50` register completeness.
**Residual.** Low with both mechanisms.

### R-09 · Digest algorithm obsolescence — Medium
**Mechanism.** §6 ¶2 requires a collision-resistant digest algorithm and version. Over twenty years at least one registered algorithm will be considered broken.
**Consequence.** Historical identity claims weaken; §6 ¶2 is no longer satisfied for old manifests.
**Mitigation.** DG-7's versioned algorithm register; deprecation without invalidating history; re-digesting recorded as a new linked manifest, never an edit; `DA-43`, `DA-44`.
**Residual.** Low.

### R-22 · Forged records in a single-writer repository — High
**Mechanism.** Authority assignments, attestations, and transition records are plain files. Absent cryptographic signing, anyone with write access can create a record purporting to be another party's approval, and `DA-05`/`DA-38`/`DA-53` verify only internal consistency.
**Consequence.** Every authority guarantee reduces to trust in whoever holds write access.
**Mitigation.** Commit signing; platform branch protection with immutable audit logs; attestations authored by their own signer. M-1.7.
**Residual.** Medium — this is the mechanical restatement of why §13 requires two humans.

### R-13 · History rewriting on protected paths — Medium
**Mechanism.** §7 ¶1 forbids rewriting history to conceal a prior Result; §8 ¶2 forbids deletion. Force-push can do both, and a rewrite that also rewrites stored digests is invisible from inside the repository.
**Mitigation.** Platform-level branch protection on `results/`, `evidence/`, `observations/`, `decisions/`, `unknowns/`, `constitution/attestations/`, `registry/transitions/`; an off-repository mirror; `DA-14`, `DA-15`, `DA-45`.
**Residual.** Low with protection and a mirror; otherwise undetectable.

### R-23 · Requirement coverage decay — Medium
**Mechanism.** `DA-39` maps every MUST to a check, an `MRP`, or a testable non-applicability statement. The Constitution has no clause identifiers (finding F-19), so coverage against it must be hand-curated.
**Consequence.** New requirements land unmapped; coverage silently decays; §12 ¶1 traceability becomes a claim rather than a fact.
**Mitigation.** Add clause identifiers at adoption, when it is a cheap textual change (H-12); fail any change that adds a MUST without adding coverage.
**Residual.** Medium without clause IDs; Low with them.

### R-14 · Reviewer capture in a small pool — High
**Mechanism.** §2's independence test is per-review. In a two- or three-person project, the same person reviews nearly everything and independence becomes formal rather than real. The v1.2.0 amendment record already concedes this as limitation L-4.
**Consequence.** Attestations satisfy §13's form while providing little of its substance.
**Mitigation.** External reviewers; rotation; mandatory conflict declarations; `MRP` procedures that require the reviewer to *do* something checkable (re-execute, re-derive, construct a counter-case) rather than merely opine.
**Residual.** Medium — reducible by federation (M-9), not eliminable.

### R-16 · Permanent retention cost — Medium
**Mechanism.** §7 ¶4 and §8 ¶1 make retention of Results, Negative Results, and Unknowns permanent with no expiry mechanism; §6 ¶5 provides only for *recording* loss, not authorizing it.
**Consequence.** With large artifacts over twenty years, an open-ended financial commitment. Cost pressure creates institutional temptation toward exactly the deletion §7 ¶4 forbids.
**Mitigation.** Custody tiering under DG-7 (retain digests and manifests permanently; migrate bulk artifacts to cheaper storage with recorded recovery procedures); record any loss as an Unknown. If retention becomes genuinely infeasible, the correct path is a constitutional amendment defining bounded, recorded, reviewed disposal — not quiet deletion. Escalated as H-09.
**Residual.** Medium.

### R-24 · Same-level conflict proliferation — Medium
**Mechanism.** §4 ¶4 makes conflicting same-level requirements *both* nonconforming until resolved, and forbids recency from deciding. Twenty-four peer standards create a large conflict surface; drift is normal.
**Consequence.** Conflicts block dependent transitions (§12 ¶2), and semantic conflict detection is undecidable, so conflicts persist unnoticed — the current state, with two hypothesis registers, two experiment paths, and contradictory frozen constants (N-7, N-9).
**Mitigation.** The **Peer Reference Rule** — never restate a peer's requirement — is the primary structural defence, because most same-level conflicts arise from duplicated text drifting apart. Plus `DA-28` (Advisory), `MRP-04`, DG-10 conflict records.
**Residual.** Medium.

---

## 5. Human and institutional risks

### R-25 · Consolidation by a well-meaning successor — High
**Mechanism.** The separation rules (§3, §11 ¶1) look like bureaucracy to someone who does not know why they exist. A future maintainer merges the Result and Interpretation stores "for convenience," or lets an audit fix the requirement it audits.
**Consequence.** The guarantees dissolve while the folder structure survives — precisely what §10 ¶1 warns about when it says a directory name is not proof of separation.
**Mitigation.** Every standard cites its constitutional clause and states its failure modes; every architecture decision records rationale and rejected alternatives; `DA-34` boundary declarations are executable, not prose. A successor should be able to reconstruct *why*, not only *what*.
**Residual.** Medium — irreducible; this is why documentation of rationale is a durability mechanism, not decoration.

### R-26 · Emergency scope creep — High
**Mechanism.** §12 ¶2 authorizes exactly one thing: deferring a containment record. "Emergency policy" is the classic vector by which governance acquires an unbounded override.
**Consequence.** A general bypass of §13 and §4 under cover of urgency.
**Mitigation.** DG-9's jurisdiction owns exactly one object type; `DA-48` verifies no containment record authorizes a non-containment transition; every containment action remains subject to review by §12 ¶2's own terms.
**Residual.** Low with the narrow jurisdiction; High if DG-9 is drafted expansively.

### R-27 · AI review over-credited — High
**Mechanism.** §4 ¶4 forbids automation supplying human authority or independent review; §2 requires an identified human. The repository's review history is already populated with model names in reviewer-shaped roles.
**Consequence.** Attestations backed by model output are void, and every downstream activation with them is void. The failure is silent, because the records look complete.
**Mitigation.** `DA-38` requires an identified human and a competence statement; V4 records AI output as findings; V6 attestations state which findings the human examined. Escalated as H-07 so the boundary is affirmed deliberately rather than assumed.
**Residual.** Low with the checks; High without, because the temptation scales with model capability.

### R-28 · Credential exposure — High — realized (working tree)
**Mechanism.** §10 ¶5 forbids committing credentials and private keys. `gcp-key.json.json` and a populated `.env` are present in the working tree.
**Consequence.** If either ever entered history, the credentials are compromised regardless of later deletion.
**Detection.** `DA-25` scanning full history, not only HEAD.
**Mitigation.** M-1.6: verify both are ignored, verify no historical revision contains them, rotate if there is any doubt. §12 ¶2 explicitly permits containment to precede record creation. **Do this independently of the governance roadmap.**
**Residual.** Unknown until history is checked — which is itself the reason to check now.

---

## 6. Summary

| Id | Risk | Severity | Status |
|---|---|---|---|
| R-01 | No second identified human | Critical | realized |
| R-02 | Legacy shock at adoption | Critical | realized on adoption |
| R-03 | Governance overhead vs throughput | High | forecast |
| R-05 | Green CI read as conformance | High | realized |
| R-06 | Ontology divergence | High | forecast |
| R-08 | Preregistration order unverifiable | High | realized |
| R-10 | Registry unranked / single point | High | realized (DD-2) |
| R-14 | Reviewer capture in a small pool | High | realized |
| R-17 | Steward single point of failure | High | forecast |
| R-20 | Interface MAJOR de-authorizes stack | High | forecast |
| R-21 | Check rot | High | realized |
| R-22 | Forged records, single writer | High | realized |
| R-25 | Consolidation by a successor | High | forecast |
| R-26 | Emergency scope creep | High | forecast |
| R-27 | AI review over-credited | High | realized |
| R-28 | Credential exposure | High | realized |
| R-04 | Activation deadlock | Medium | forecast |
| R-09 | Digest obsolescence | Medium | forecast |
| R-13 | History rewriting | Medium | forecast |
| R-16 | Permanent retention cost | Medium | forecast |
| R-18 | File-drawer effects | Medium | forecast |
| R-19 | Non-distinguishable hypotheses | Medium | realized |
| R-23 | Coverage decay | Medium | forecast |
| R-24 | Same-level conflict proliferation | Medium | realized |

**Nine of the twenty-four are already realized.** The design's first job is therefore not to prevent future problems but to make present ones visible and dispositioned. Of the realized set, three are cheap to fix now and get more expensive later: R-28 (credentials), R-05 (CI), R-08 (external timestamping). None requires adoption, authority, or a single line of governance prose.
