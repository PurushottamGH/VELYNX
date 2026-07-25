# Activation — index and current state

- **Status:** Draft
- **Scope:** The activation work set: what exists, what each document answers, and what still blocks adoption
- **Responsibility:** Navigation and current status. Non-normative
- **Authority source:** None
- **Version:** 0.2.0 (2026-07-25)

---

## 1. Documents

| File | Answers |
|---|---|
| `00_MINIMUM_ACTIVATION_PLAN.md` | Objectives 1, 2, 4, 5, 6, 7: the minimum plan, why one standard suffices, dependency graph, roadmap, task classification |
| `01_STANDARD_CLASSIFICATION.md` | Objective 3: every proposed standard classified, each Optional/Future entry with a named trigger |
| `02_PREADOPTION_VERIFICATION.md` | Observed repository state; four premises of the plan corrected |
| `03_ADOPTION_CHANGE_MANIFEST.md` | The atomic change as a runbook: preflight gates, contents of D and E, ordering, verification, reversal |
| `04_LEGACY_DISPOSITION.md` | How §4 ¶5 distinguishability is discharged in three tiers instead of 40 edits |
| `05_RELEASE_CANDIDATE_CHECKLIST.md` | The activation register: dependency waves, seven categories including instrument correction, one critical path, external blockers, measured readiness |
| `RS-1_RESEARCH_STANDARD.draft.md` | The one Domain standard required for lawful research operation |
| `ADOPTION_CONFORMANCE_DOSSIER.template.md` | The §12 ¶1 traceability instrument the reviewer needs |
| `GOVERNANCE_REGISTRY.target.yaml` | Target Registry state after D, and after E |
| `templates/ADOPTER_ATTESTATION.template.md` | §13 ¶2 adopter attestation |
| `templates/INDEPENDENT_REVIEWER_ATTESTATION.template.md` | §13 ¶2 independent reviewer attestation |
| `templates/NORMATIVE_TRANSITION_RECORD.template.md` | §9 ¶3 eight-element transition record for `T-0001` (D) and `T-0002` (E) |

Outside this folder, produced for the adoption change:

| File | Purpose |
|---|---|
| `governance/AR-1_REPOSITORY_ARCHITECTURE_RECORD.md` | Descriptive §10 ¶1 record, Level 4, no Registry entry |
| `governance/LEGACY_INDEX.md` | Generated inventory: 7 Tier-1, 34 Tier-2, 11 Tier-3 directory rules |
| `governance/checks/RUN_2026-07-25.md` | Recorded check output, nine-check set, superseded for currency |
| `governance/checks/RUN_2026-07-25_B.md` | Recorded check output at the current ten-check set |
| `scripts/governance/check_adoption.py` | Ten advisory checks, honest about limits |
| `scripts/governance/generate_legacy_index.py` | Regenerates the index |

## 2. Shape of the answer

Zero Domain standards required before adoption; one (RS-1) for lawful research operation; everything else activates on a named trigger. Adoption needs the Constitution, the Registry, one steward, and two attestations — plus three non-standard artifacts whose MUSTs bind the moment the Constitution goes Active: an architecture record (§10 ¶1), a Legacy index (§4 ¶5), and a conformance dossier (§12 ¶1). The dossier does most of the work by discharging §5–§7 as not applicable with a testable reason, verified by `p1/records/` being empty.

## 3. Current state — one blocker inside the repository, one outside

Latest run: `PASS=5, FINDINGS=3, FAIL=1, NOT_VERIFIED=1`; blocking `A-07`, `A-10`.

| Item | State | Owner |
|---|---|---|
| A-07 credential in history | **FAIL** — `gcp-key.json.json` added in 9 commits | operator: rotate at the provider. Deletion does not remediate |
| A-10 attestation completeness | **NOT_VERIFIED** — no attestation exists yet, so the criterion is unassessed, not passed (§12 ¶1) | resolves at change D; blocked behind the second human |
| Second identified human | **absent** — every commit by one identity | human. Blocks D and E entirely |
| A-06 banners | 42 files listed, 0 applied; 0 unresolvable entries | engineering, applied in revision D so the banner text is true when committed |
| A-05 lexeme findings | 665 matches in 102 live files, after `authoritative` and bare `absolute` were added to the pattern | disposition by Tier assignment plus manual `P-L1` (`VER-4`) |
| A-09 identity quality | git identity is `purushottam@local`, non-routable | human: §2's "identified human" needs more than a local handle |

Everything else on the engineering path is done or specified. The remaining engineering work is: apply banners and Tier-1 moves in D, complete the dossier, reconcile `p1_os` to RS-1's six owned types, and finish RS-1's §11 checklist.

## 4. Two things not to do

**Do not commit an Active status without both attestations in the same revision.** Draft costs nothing (§4 ¶5, §9 ¶4); a partial adoption is a nonconformance that §13 ¶4 makes awkward to unwind. Commit freely with `status: Draft`, `constitutional_steward: []`, attestations `null`.

**Do not activate a standard because it is written.** §12 ¶1 makes an unverifiable requirement a nonconformance, so activating beyond review capacity manufactures nonconformance. One Active standard, fully verified, is a stronger position than twenty-four partly verified.
