# Adopter Attestation — template

<!-- attestation-kind: adopter -->

- **Status:** Draft (template — not an attestation until completed and committed in the adoption revision)
- **Scope:** Initial adoption of `REPOSITORY_CONSTITUTION.md` v1.2.0 under §13 ¶3
- **Responsibility:** Record the adopter's attestation
- **Authority source:** §13 ¶3 bootstrap authority, which ends upon adoption
- **Version:** 0.1.0

> Fill every `[COMPLETE]`. A field left blank is a missing element, and §9 ¶3's fail-closed rule applies: the adoption is blocked, not qualified. §4 ¶4 forbids automation from supplying this attestation; it must be written and committed by the identified human named below.

---

## 1. Identity

| Field | Value |
|---|---|
| Adopter, identified human | `[COMPLETE]` full name |
| Contact | `[COMPLETE]` verifiable email or equivalent |
| Git identity used to commit | `[COMPLETE]` name and email as they appear in the commit |
| Role in this change | Author and adopter |

The Git identity must be resolvable to the named human. The repository's existing history uses `Purushottam <purushottam@local>`, a non-routable address; if that identity is used, state here how it maps to an identified person, since §2's "identified human" is not satisfied by a local-only handle.

## 2. Reviewed revision

| Field | Value |
|---|---|
| Revision attested | `[COMPLETE]` full commit SHA of the **reviewed pre-merge candidate revision** |
| Tree hash of that revision | `[COMPLETE]` `git rev-parse <SHA>^{tree}` |
| Constitution version | 1.2.0 |
| Registry state attested | `active_domain_standards: []`; `constitutional_steward: [COMPLETE]` |
| Time of attestation | `[COMPLETE]` timezone-qualified, precision stated (§2) |

This attestation names the candidate revision, not the accepted one. A commit cannot contain its own SHA, so an attestation committed *in* the adoption revision cannot identify it. The candidate revision carries the complete change except this attestation and the reviewer's; the branch is then squash-merged, so exactly one default-branch revision contains every element (§2). The accepted revision's identifier is recorded afterwards in the post-merge re-verification record. See the dossier §1.1.

## 3. Declarations

- [ ] I am an identified human, not an automated system (§4 ¶4).
- [ ] I am the author of this change and therefore **not** its Independent reviewer (§2, §12 ¶1).
- [ ] I adopt `REPOSITORY_CONSTITUTION.md` v1.2.0 under §13 ¶3.
- [ ] The same revision activates the Constitution, activates the Governance Registry, and assigns at least one constitutional steward (§13 ¶3).
- [ ] I understand that bootstrap authority ends upon adoption, and that later amendment requires a Registry-listed steward plus an Independent reviewer attestation (§13 ¶3–4).
- [ ] I have read the adoption conformance dossier and accept its unresolved-violations list as complete to my knowledge (§12 ¶1).
- [ ] No scientific record, Claim, or Result is created, relabelled, or reinterpreted by this change (§13 ¶4).

## 4. Steward assignment

| Field | Value |
|---|---|
| Constitutional steward assigned | `[COMPLETE]` identified human |
| Permitted transitions | amend, supersede, withdraw the Constitution; activate Domain standards (§13 ¶3) |
| Named successor | `[COMPLETE]` — recommended. With one steward, §4 ¶5 approval throughput is a single point of failure |
| Recorded in Registry at | `GOVERNANCE_REGISTRY.yaml` → `authority_assignments.constitutional_steward` |

## 5. Acknowledged limitations at adoption

State each explicitly; the dossier's §1 must match.

| # | Limitation |
|---|---|
| L-1 | `[COMPLETE]` credential exposure per `02_PREADOPTION_VERIFICATION.md` V-1: rotation status, and the unbounded disclosure window |
| L-2 | All pre-adoption execution is exploratory working output permanently; no pre-adoption output can become a confirmatory Result (§2, §5 ¶3, §13 ¶4) |
| L-3 | No Domain standard is Active at adoption, so no scientific transition is authorized until RS-1 activates (§4 ¶5) |
| L-4 | Registration ordering rests on author-controlled commit timestamps unless an external anchor is in use (§5 ¶3) |
| L-5 | `[COMPLETE]` any further limitation known to the adopter |

## 6. Conclusion

`[COMPLETE]` — "I adopt the Constitution at revision `<SHA>`, with the limitations listed in §5."

Signature or verifiable commit reference: `[COMPLETE]`

---

**What this attestation does not do.** It does not establish that any scientific claim is true (§4 ¶6, §3), does not authorize a scientific transition (§4 ¶5), and does not satisfy the Independent reviewer requirement (§12 ¶1: a self-review may find defects but MUST NOT be labelled independent).
