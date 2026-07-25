# Independent Reviewer Attestation — template

- **Status:** Draft (template — not an attestation until completed and committed in the reviewed revision)
- **Scope:** Independent review of one reviewed revision: the §13 ¶3 adoption change, or a §4 ¶2 Domain standard activation
- **Responsibility:** Record the Independent reviewer attestation required by §13 ¶2
- **Authority source:** §13 ¶2. The attestation is Repository evidence; it is not authority and does not approve anything
- **Version:** 0.1.0

> §13 ¶2 fixes the required content exactly. Each numbered section below is one of its elements; omitting any leaves the attestation incomplete and the transition blocked (§9 ¶3). §4 ¶4: an automated system MUST NOT supply this. §12 ¶1: a self-review MUST NOT be labelled independent.

---

## 1. Reviewed revision (§13 ¶2)

| Field | Value |
|---|---|
| Revision reviewed | `[COMPLETE]` full commit SHA of the **pre-merge candidate revision** |
| Tree hash of that revision | `[COMPLETE]` `git rev-parse <SHA>^{tree}` |
| What is being activated | `[COMPLETE]` Constitution v1.2.0 adoption / RS-1 activation |
| Review period | `[COMPLETE]` start and end, timezone-qualified |

The revision reviewed is the candidate branch commit, which exists and can be read at review time. It is deliberately not the accepted default-branch revision: a commit cannot contain its own SHA, and this attestation is committed inside the change it attests to. Before signing, confirm that the accepted revision differs from the reviewed one **only** by the attestation files — `git diff <candidate> <merge>` — and that the merge is a squash, since a `--no-ff` merge would leave the candidate reachable from the default branch and it sets `Status: Active` (gate `G-3`, `VER-6`).

## 2. Non-authorship declaration (§13 ¶2, §2)

- [ ] I am an identified human. Name: `[COMPLETE]`. Contact: `[COMPLETE]`.
- [ ] I am **not** an author of the reviewed change. Specifically, I authored none of: `[COMPLETE]` list the reviewed artifacts.
- [ ] I did not produce any Evidence under review. If I did, identify it: `[COMPLETE]` / none.
- [ ] I am not an automated system, and no model output is being presented as my review (§4 ¶4).

The last box matters in this repository specifically: prior review-shaped records here are populated by model names, and agent configuration files define reviewer roles. Neither can satisfy §13 ¶2.

## 3. Conflict of interest (§2, §13 ¶2)

| Field | Value |
|---|---|
| Material conflicts | `[COMPLETE]` or "none identified" |
| Relationship to the adopter | `[COMPLETE]` |
| Interest in the outcome | `[COMPLETE]` |

§2: "A conflicted reviewer is not independent for that review." Disclosure does not cure a conflict that defeats independence — it lets the record show whether one exists.

## 4. Competence (§13 ¶2)

`[COMPLETE]` — relevant competence for this review: governance and normative-document review, and enough familiarity with the subject matter to judge whether the §12 ¶1 traceability is genuine rather than formal. State it concretely; "generally competent" is not a statement of competence.

## 5. Records, artifacts, and checks examined (§13 ¶2)

Enumerate. A reviewer who examined fewer artifacts than the change contains should say so here rather than leave it implicit.

| # | Artifact or check | Examined | Finding |
|---|---|---|---|
| 1 | `REPOSITORY_CONSTITUTION.md` v1.2.0 | `[ ]` | `[COMPLETE]` |
| 2 | `GOVERNANCE_REGISTRY.yaml` | `[ ]` | `[COMPLETE]` |
| 3 | `governance/conformance/ADOPTION_CONFORMANCE_DOSSIER.md` | `[ ]` | `[COMPLETE]` |
| 4 | `governance/AR-1_REPOSITORY_ARCHITECTURE_RECORD.md` | `[ ]` | `[COMPLETE]` |
| 5 | `governance/LEGACY_INDEX.md` | `[ ]` | `[COMPLETE]` |
| 6 | Adopter attestation | `[ ]` | `[COMPLETE]` |
| 7 | Check run output at the reviewed revision, with the `A-xx` ids named | `[ ]` | `[COMPLETE]` |
| 8 | Transition record `T-0001` — all eight §9 ¶3 elements (`P-A2`) | `[ ]` | `[COMPLETE]` |
| 9 | Dossier interpretation 4.5, and whether "subordinate" in §9 ¶1 reaches the objects this change creates | `[ ]` | `[COMPLETE]` |
| 10 | `[COMPLETE]` further artifacts | `[ ]` | `[COMPLETE]` |

## 6. Review procedure (§13 ¶2)

State the method actually used, not an idealised one:

1. `[COMPLETE]` how Affected requirements were enumerated (§2: a requirement whose subject, condition, output, evidence, or enforcement can change).
2. `[COMPLETE]` how each was traced to a check output, a manual finding, or a testable non-applicability statement (§12 ¶1).
3. `[COMPLETE]` how each non-applicability reason was independently verified — for the adoption change, by confirming the absence of records of the named kind.
4. `[COMPLETE]` which checks were re-run rather than taken on report.
5. `[COMPLETE]` what was **not** examined, and why.

## 7. Findings

| # | Finding | Clause | Severity | Disposition |
|---|---|---|---|---|
| F-1 | `[COMPLETE]` | | | |

Unresolved violations must appear here and in the dossier. §12 ¶1: an unavailable check is reported as **not verified**, never as passed; §12 ¶2: nonconformance is reported, not redefined away.

## 8. Conclusion (§13 ¶2)

`[COMPLETE]` — one of:

- **Conforming.** Every Affected MUST and MUST NOT traces to a check output, a manual finding, or a verified testable N/A.
- **Conforming with listed violations.** As above, with §7's unresolved items disclosed and none of them authorizing a dependent transition (§12 ¶2).
- **Nonconforming.** The change is blocked.

Signature or verifiable commit reference: `[COMPLETE]`

---

**Limits of this attestation.** It states what this reviewer examined at one revision (§12 ¶3: a check is evidence only for the criteria, revision, and scope it actually assessed). Four things are not verifiable from inside the repository and are outside any attestation's reach: backdated commit timestamps, history rewritten before the first recorded check run, forged records absent commit signing, and work performed and discarded outside version control. A reviewer should say so rather than let the attestation imply otherwise.
