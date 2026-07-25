# Normative Artifact Transition Record — template

- **Status:** Draft (template — not a transition record until completed and committed in the revision that performs the transition)
- **Scope:** One lifecycle transition of one Normative artifact: the Constitution's `Draft → Active` at change D, and RS-1's `Draft → Active` at change E
- **Responsibility:** Record the eight §9 ¶3 elements for one transition
- **Authority source:** None. This record *reports* a transition authorized elsewhere; it does not authorize one.
- **Version:** 0.1.0

> §9 ¶3: "A transition is valid only when a version-controlled transition record identifies the object, prior state, new state, criteria applied, evidence considered, authority, time, and rationale. **Missing information MUST cause the transition to fail closed.**"
>
> Every field below is one of those eight. A field left as `[COMPLETE]` is missing information, not a formality: the transition is blocked, not qualified. §4 ¶4 forbids an automated system from supplying the authority field.

---

## Why this record exists

§2 lists a transition record among the elements an Atomic change must contain, and §9 ¶3 is unqualified as to object type — it says "a transition", not "a transition of a subordinate object". The Constitution's own activation is a transition of a Normative artifact under the §9 ¶4 lifecycle, so it needs one.

§9 ¶1's carve-out is sometimes read as covering this. It does not: that clause exempts the Constitution, the Registry, and Domain standards from *needing an Active Domain standard to define their lifecycle*. It says nothing about the transition-record requirement, which is a separate rule in a separate paragraph. Without this record the adoption would be the one transition in the repository with no §9 ¶3 record — and the dossier row discharging §9 ¶3 as not applicable would be false.

---

## 1. Object (§9 ¶3)

| Field | Value |
|---|---|
| Transition id | `[COMPLETE]` — `T-0001` for the Constitution at D, `T-0002` for RS-1 at E |
| Object | `[COMPLETE]` full repository path of the Normative artifact |
| Object version | `[COMPLETE]` the version being transitioned |
| Object kind | Normative artifact (§2), using the §9 ¶4 lifecycle |

## 2. Prior state and new state (§9 ¶3)

| Field | Value |
|---|---|
| Prior state | `Draft` |
| New state | `Active` |
| Lifecycle | `Draft → Active → Superseded or Withdrawn` (§9 ¶4). Draft has no authority; Active is effective within its Scope |

## 3. Criteria applied (§9 ¶3)

State the clause that had to be satisfied, and how each was, one line per criterion.

**For the Constitution at D — §13 ¶3:**

| # | Criterion | Satisfied by |
|---|---|---|
| 1 | Attestations by two identified humans, an adopter and an Independent reviewer | `[COMPLETE]` both attestation paths |
| 2 | The same atomic change activates the Constitution | `[COMPLETE]` |
| 3 | The same atomic change creates or activates the Governance Registry | `[COMPLETE]` |
| 4 | The same atomic change assigns at least one constitutional steward | `[COMPLETE]` |
| 5 | No intervening default-branch revision lacks a required element (§2) | `[COMPLETE]` — squash merge; see the manifest's atomicity rule |

**For RS-1 at E — §4 ¶2:** the reviewed standard, its Registry entry, approval by a Registry-listed authority permitted to activate that jurisdiction, and an Independent reviewer attestation. Add the non-overlap determination against `active_domain_standards` as it stood immediately before activation.

## 4. Evidence considered (§9 ¶3)

| # | Evidence | Path or identifier |
|---|---|---|
| 1 | Conformance dossier | `[COMPLETE]` |
| 2 | Adopter attestation | `[COMPLETE]` |
| 3 | Independent reviewer attestation | `[COMPLETE]` |
| 4 | Recorded check run at the reviewed revision | `[COMPLETE]` |
| 5 | Unresolved violations disclosed at the time of transition | `[COMPLETE]` — list them; an omission is itself a nonconformance (§12 ¶1) |

Evidence is *considered*, not created, here. This record does not admit Evidence for a Claim (§6) and asserts nothing scientific (§3 ¶6).

## 5. Authority (§9 ¶3)

| Field | Value |
|---|---|
| Authority | `[COMPLETE]` |
| Basis | `[COMPLETE]` — at D: §13 ¶3 bootstrap authority of two identified humans, which **ends upon adoption**. At E: the constitutional steward listed in `GOVERNANCE_REGISTRY.yaml`, permitted for `activate_domain_standard` |
| Permitted for this transition | `[COMPLETE]` — cite the Registry entry. At D the Registry cannot pre-list the authority, because the assignment is made by this change; §13 ¶3 supplies it directly |

## 6. Time (§9 ¶3)

| Field | Value |
|---|---|
| Transition time | `[COMPLETE]` timezone-qualified, precision identified (§2) |
| Precision | `[COMPLETE]` — state it where it could affect the determination |

The transition becomes effective when the change is accepted into the default branch (§13 ¶4). This record is written before that acceptance and does not name the accepted revision: a commit cannot contain its own identifier. The accepted revision is recorded afterwards in the post-merge re-verification record.

## 7. Rationale (§9 ¶3)

`[COMPLETE]` — why this transition, now. It must not restate the criteria: rationale is the reason for acting, criteria are the conditions for being permitted to. A Decision "does not make its rationale true" (§2), and neither does this record.

---

## 8. What this record is not

- Not an approval. Approval is the authority's act, recorded in the attestation at D and in `D-0001` at E.
- Not an attestation. §13 ¶2 fixes attestation content separately, and the attestation is Repository evidence.
- Not a conformance claim. §12 ¶1 fixes that separately; it is the dossier.
- Not authority. It reports that a transition occurred and on what basis, so that a later reviewer need not reconstruct it.
