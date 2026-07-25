# Adoption Change Manifest — the §13 ¶3 atomic change, as an executable runbook

- **Status:** Draft
- **Scope:** The single default-branch revision that activates `REPOSITORY_CONSTITUTION.md` v1.2.0, and the separate revision that activates RS-1
- **Responsibility:** Specify exactly what the adoption revision contains, in what order it is assembled, what gates it, and how it is reversed
- **Authority source:** None. This record describes a procedure; it authorizes no transition and confers no authority.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. What "atomic" requires

§2: an Atomic change is "one accepted default-branch repository revision that contains every required artifact, Registry entry, approval, attestation, and transition record, with no intervening default-branch revision in which any required element is absent."

Operationally: **one accepted default-branch revision, produced by a squash merge.**

`--no-ff` is not an equivalent alternative, and an earlier draft of this manifest was wrong to offer it. A `--no-ff` merge leaves every branch commit reachable from the default branch. The candidate commit sets `Status: Active` and populates the steward, so under `--no-ff` an earlier default-branch revision would carry adoption elements without the attestations — which is what gate `G-3` forbids and what `VER-6` tests for. **Squash merge is mandatory.**

The assembly is two steps, because the attestations cannot name the revision that contains them (see §5 and the dossier §1.1):

1. a **candidate** branch commit carrying every element in §3 except the attestations;
2. the attestations, written against that candidate, then squash-merged with it into one revision.

Only step 2's output reaches the default branch, so no intervening default-branch revision lacks a required element.

Two changes, in sequence, per `00_MINIMUM_ACTIVATION_PLAN.md` §5: **D** (adoption) then **E** (RS-1 activation). Bootstrap authority ends upon adoption (§13 ¶3), so a steward assigned *within* D approving a standard *within* D is contestable; separating them removes the ambiguity at a cost of one merge and no extra attestations.

---

## 2. Preflight gates — every one must be closed before D is merged

Fail-closed: an unknown answer is a blocked gate, never a note.

| Gate | Condition | Who closes it |
|---|---|---|
| G-1 | A second identified human exists, is not an author of D, and has declared conflicts (§2, §13 ¶3) | human |
| G-2 | The credential in V-1 is rotated at the provider | operator |
| G-3 | `status: Draft` → `Active` appears **only** in the accepted D revision; no earlier **default-branch** revision sets it | engineering |
| G-4 | Architecture record exists with boundaries, dependencies, rationale (§10 ¶1) | engineering |
| G-5 | Legacy index exists and is complete against a repository sweep (§4 ¶5, §14) | engineering |
| G-6 | Dossier complete: every Affected MUST traced to check, procedure, or testable N/A (§12 ¶1) | engineering, then reviewer |
| G-7 | `p1/records/**` contains zero record files, verified, so the dossier's N/A discharges hold | automated |
| G-8 | Known violations are listed in the dossier, not omitted — including V-1 (§12 ¶1) | engineering |
| G-9 | Both attestations name identified humans, and no tool output substitutes for either (§4 ¶4, §13 ¶2) | reviewer |
| G-10 | `T-0001` exists and carries all eight §9 ¶3 elements, none left as a placeholder (`P-A2`) | engineering, then reviewer |

G-3's wording is precise on purpose. The candidate revision *does* set `Active`, and that is not a breach: it is a branch commit, never a default-branch revision. The gate is about what the default branch ever contained, which is why the merge must be a squash (§1) and why `VER-6` audits it afterwards.

G-1 is the only gate that cannot be closed by work inside this repository. Everything else can be finished before it, and should be.

---

## 3. Change D — contents of the single adoption revision

| # | Path | Action | Clause |
|---|---|---|---|
| D-1 | `REPOSITORY_CONSTITUTION.md` | `Status:` → `Active; adopted under Section 13` | §13 ¶3 |
| D-2 | `GOVERNANCE_REGISTRY.yaml` | `status: Active`; `constitution.status: Active`; `constitutional_steward: [<name>]`; both attestation fields populated with paths; `active_domain_standards: []` | §13 ¶3, §4 ¶1 |
| D-3 | `governance/attestations/ADOPTER_ATTESTATION.md` | new, signed content | §13 ¶2 |
| D-4 | `governance/attestations/INDEPENDENT_REVIEWER_ATTESTATION.md` | new, signed content | §13 ¶2 |
| D-5 | `governance/AR-1_REPOSITORY_ARCHITECTURE_RECORD.md` | new, descriptive, Level 4 | §10 ¶1 |
| D-6 | `governance/LEGACY_INDEX.md` | new; complete inventory with §14 basis | §4 ¶5, §14 |
| D-7 | `governance/conformance/ADOPTION_CONFORMANCE_DOSSIER.md` | new, completed from the template | §12 ¶1 |
| D-8 | Tier-1 Legacy banners | edits per `04_LEGACY_DISPOSITION.md` | §4 ¶5 |
| D-9 | `governance/checks/` + the run recorded at the **candidate** revision | new; advisory checks and their recorded output | §12 ¶3 (SHOULD) |
| D-10 | `governance/design/**`, `governance/activation/**` | committed as Draft, non-normative | §4 ¶5 |
| D-11 | `governance/transitions/T-0001-constitution-draft-to-active.md` | new; the eight §9 ¶3 elements for the Constitution's `Draft → Active` | §2, §9 ¶3 |

`active_domain_standards: []` is deliberate and conforming: §13 ¶3's list is Constitution, Registry, steward, two attestations, and §9 ¶1 excepts Domain standards from per-type ownership.

**Not in D:** RS-1, any Registry entry for RS-1, any scientific record, any change under `framework/`, `backend/`, or `frontend/`. Keeping software out of D is what lets §10 ¶2–4 discharge as N/A.

---

## 4. Change E — RS-1 activation

| # | Path | Action | Clause |
|---|---|---|---|
| E-1 | `governance/standards/RS-1_RESEARCH_STANDARD.md` | Draft → `Active`, promoted from the activation folder, `Version: 1.0.0` | §9 ¶4 |
| E-2 | `GOVERNANCE_REGISTRY.yaml` | RS-1 entry with identity, status, scope, responsibility, authority, jurisdiction tuples | §4 ¶1–2 |
| E-3 | `governance/decisions/D-0001-activate-rs1.md` | steward approval of the activation transition | §4 ¶2 |
| E-4 | `governance/attestations/RS-1_INDEPENDENT_REVIEWER_ATTESTATION.md` | new | §4 ¶2 |
| E-5 | `p1/records/unknowns/*` | standing Unknowns U-a … U-f from `02_PREADOPTION_VERIFICATION.md` §6 | §8 ¶1 |
| E-6 | `p1/tooling/p1_os` validation profile | restricted to RS-1's six owned types | §9 ¶1 |
| E-7 | `governance/conformance/RS-1_CONFORMANCE_RECORD.md` | §12 ¶1 traceability for RS-1's MUSTs | §12 ¶1 |
| E-8 | `governance/transitions/T-0002-rs1-draft-to-active.md` | new; the eight §9 ¶3 elements for RS-1's `Draft → Active` | §2, §9 ¶3, RS-1 §2.1 |
| E-9 | `GOVERNANCE_REGISTRY.yaml` → `authority_assignments` | steward's `permitted_transitions` extended to cover every RS-1 transition | §4 ¶1, §4 ¶5 |

RS-1's pre-activation checklist (its §11) gates E. The overlap test in §4 ¶2 is trivially satisfied: RS-1's jurisdiction is compared against an empty `active_domain_standards`.

`E-8` and `E-3` are different objects and both are required. `D-0001` is the steward's *approval* of the transition; `T-0002` is the record *that the transition occurred*, with its eight §9 ¶3 elements. RS-1 §2.1 requires the record in addition to the authorizing decision.

`E-9` is easy to miss and fatal to omit. Without it the Registry lists a steward permitted only for the four constitutional transitions, so after E no Registry-listed authority is permitted for any of RS-1's 21 transitions: §4 ¶5 has no authority to name, §4 ¶1 voids an authority whose permitted transitions are inconsistent, and every research transition fails closed under §9 ¶3. E would activate a standard that authorizes nothing. Target state is in `GOVERNANCE_REGISTRY.target.yaml`, block E.

---

## 5. Assembly order

```
now, no authority needed
  1. commit current Draft state (Constitution v1.2.0 Draft, Draft Registry, governance/**)
  2. rotate credential                                   → closes G-2
  3. write AR-1 architecture record                       → G-4
  4. legacy index + Tier-1 banners                        → G-5
  5. build + run checks, record output                    → G-7, and inputs to G-6
  6. complete the dossier, listing V-1 as unresolved      → G-6, G-8
  7. draft T-0001 transition record                       → part of G-6
  8. reconcile p1_os profile and RS-1 naming (V-2)        → prerequisite for E
  9. finish RS-1: its §11 checklist                       → prerequisite for E

blocked on a second human
 10. commit the CANDIDATE revision: every D element except
     the two attestations. Note its SHA and tree hash
 11. reviewer reviews the candidate, runs the checks at it,
     records that run as the dossier's cited evidence     → G-1
 12. both attestations written against the candidate SHA   → G-9
 13. squash-merge candidate + attestations as ONE revision → D accepted
 14. re-run checks at the accepted revision, recorded as a
     SEPARATE re-verification record                      → VER-5
 15. assemble and squash-merge E the same way             → E accepted
```

Steps 1–9 are engineering and are the whole of the work that can proceed today. Steps 10–15 are the whole of the work that cannot.

**Why steps 10–14 are ordered this way.** Naming "the adoption revision" in the dossier, the attestations, and the Registry created a cycle: the dossier cited a check run that could only exist after the merge, the merge could only happen once the dossier was in the revision, and each SHA field demanded the identifier of the commit containing it. Reviewing a candidate revision and treating the post-merge run as a separate record breaks the cycle without weakening anything — the reviewer still reads the exact content that is accepted, and the accepted revision is still verified, just in a record that is allowed to come afterwards.

The alternative — merge, then add a fix-up commit filling in the SHAs — is what §2 exists to prevent. It produces a default-branch revision in which required elements are absent or unfilled, which is a nonconforming partial adoption.

---

## 6. Re-verification of D, after merge

Run the checks at the accepted revision and record the output as a **separate re-verification record** — `governance/checks/RUN_<date>_POST_D.md`.

This is deliberately *not* the dossier's cited evidence, and an earlier draft of this manifest was wrong to say it was. The dossier is committed inside the revision it assesses, so it cannot cite a run performed after that revision exists; requiring it to do so was what forced the cycle `DOC-2 → RE-9 → RE-10 → VER-5 → DOC-2`. The dossier cites the run at the reviewed candidate revision (§5 step 11). This record confirms that the accepted revision behaves as the reviewed one did, and it modifies nothing.

Expected results at the accepted revision:

| Check | Expected |
|---|---|
| `A-01` header completeness | pass |
| `A-02` Registry ↔ Constitution consistency | pass |
| `A-03` adoption element completeness | pass — including a transition record present |
| `A-04` no scientific records exist | pass |
| `A-05` authority-lexeme scan | **findings expected**, dispositioned by `VER-4` |
| `A-06` Legacy index and banner coverage | pass — and **zero unresolvable entries**, which is what proves the Tier-1 moves did not silently drop out of verification |
| `A-07` credentials in history | **FAIL, disclosed** — V-1 is a known unresolved violation |
| `A-08` check honesty | pass |
| `A-09` identified humans | findings — never returns pass |
| `A-10` attestation completeness | pass — this is its first revision with a non-empty target set |

A dossier claiming all checks pass would itself be a nonconformance. The correct output is "conforming with listed violations," with V-1 listed.

If this record diverges from the run at the candidate revision in any way other than `A-10` moving from not-verified to pass, the divergence is a finding: it means the merge changed something the reviewer did not review.

---

## 7. Reversal

Before merge: abandon the branch. Nothing happened; Draft has no authority.

After merge: adoption cannot be un-adopted by deletion. §13 gives one route — a §13 ¶4 amendment by a Registry-listed steward with an Independent reviewer attestation, superseding or withdrawing the Constitution, with the prior version recoverable (§9 ¶4). §8 ¶2 requires the previous state and rationale to be preserved. Practically: reversal costs the same as adoption plus a migration record, which is the argument for closing every gate before merging rather than adopting and repairing.

---

## 8. What this manifest does not do

It does not authorize the merge. §4 ¶2 and §13 ¶3 place that with identified humans, and no document, script, or check output can supply it (§4 ¶4). The manifest's only claim is that when those humans act, nothing else will be missing.
