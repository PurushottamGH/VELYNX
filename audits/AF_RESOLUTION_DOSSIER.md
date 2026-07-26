# AF Resolution Dossier — engineering decision record for the disputed audit findings

- **Status:** Draft
- **Scope:** The five findings disputed across independent verification and adjudication — `AF-1`, `AF-2`, `AF-7`, `AF-8`, `AF-9` — plus the three defects found in adjudication and closed in the same sprint (`AF-23`, `AF-24`, `AF-25`) and the three hardening items closed with them (`AF-13`, `AF-15`, `AF-19`). Repository state: revision `234454c47bfb67bc28f3be12da633112ef443748` plus the final engineering sprint's changes
- **Responsibility:** Record, for each disputed finding, what was decided, on what evidence, and what remains a governance question rather than an engineering one
- **Authority source:** None. This is an engineering decision record. It authorizes no transition, closes no gate, creates no requirement, and confers no authority (§4 ¶4, §4 ¶7). Where it and an artifact disagree, the artifact governs and this record is stale
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft, not adopted, unchanged by this sprint)
- **Version:** 1.0.0

---

## 0. What this record is for, and what it deliberately is not

Four stages preceded it: a Constitutional Systems Audit (`AF-1`…`AF-22`), an implementation of `AF-1`…`AF-11`, an independent verification of that implementation, and an engineering adjudication of the verification. Two of those stages disagreed about several findings, and one finding's proposed remedy was not executable at all. Without a record, the next reviewer would have to reconstruct which position the repository actually adopted, and why — from artifacts that only show the outcome.

**It is not an audit.** §3 ¶5 reserves audit records to reporting observed conformance at a stated revision, and §3's separation rule forbids an audit from creating or amending the requirement it audits. This record reports engineering decisions about Draft instruments. It observes nothing about conformance and imposes nothing.

**It is not a conformance claim.** The §12 ¶1 traceability instrument is `governance/conformance/ADOPTION_CONFORMANCE_DOSSIER.md`, assembled from its template at `DOC-2`. Nothing here substitutes for it.

**It is not independent review.** It is written by the same party that performed the engineering. §12 ¶1: a self-review may find defects but MUST NOT be labelled independent. Every "verified" statement below names a command or an artifact so that an Independent reviewer can re-run it rather than take it on report.

### Authority order applied throughout

1. `REPOSITORY_CONSTITUTION.md` v1.2.0 — **not modified.** No amendment was made, proposed, or implied.
2. `GOVERNANCE_REGISTRY.yaml` — **not modified.** Still `status: Draft`, `constitutional_steward: []`, both attestations `null`.
3. The Constitutional Systems Audit — its findings are the subject; none was redefined away.
4. The repository — the artifacts, which govern over any narrative about them.
5. The engineering adjudication — persuasive, and departed from in one place, recorded in §3 below.

---

## 1. Summary of decisions

| Finding | Verification position | Adjudication | Engineering decision | Repository modified? |
|---|---|---|---|---|
| `AF-1` | partially resolved | Terra partly correct; no repository remedy exists | **Closed — no modification.** Constitutional ambiguity in an instrument this sprint may not amend; discharged by recorded, falsifiable interpretation 4.5, reserved to the Independent reviewer | no |
| `AF-2` | partially resolved | Terra correct, and understated | **Repaired.** `A-10` schema dispatch, emphasis-tolerant matcher, unticked-declaration detection, fixture tests | yes |
| `AF-7` | partially resolved | regress fix sound; grounding objection interpretive; verification apparatus contradicts the exemption | **Repaired, and the interpretive exposure removed rather than documented** — see `AF-8` | yes |
| `AF-8` | not resolved | Terra correct | **Repaired via Route A:** the Registry target grants all 21 transitions; no artifact narrowed | yes |
| `AF-9` | partially resolved | original defect resolved; residual belongs to `AF-7`/`AF-8` | **Closed by the `AF-8` repair**, which removes the residual at its source | yes, via `AF-8` |
| `AF-13`, `AF-15`, `AF-19` | out of the disputed set; recorded open | recommended closing with the sprint | **Closed.** Status word, measured recount, gate `G-9` hardening | yes |
| `AF-23`, `AF-24`, `AF-25` | `AF-23` raised in verification; `AF-24`, `AF-25` found in adjudication | engineering required | **Repaired.** Reversibility wording, `P-9` object-type dispatch, identifier re-keying | yes |

One decision departs from the adjudication's recommendation, and one finding is closed without any repository change. Both are argued below rather than asserted.

---

## 2. AF-1 — the §9 ¶1 "subordinate" discharge

**Original finding.** The dossier discharged §9 ¶1 by asserting that "no subordinate scientific or governance object type is in use". That is false at the D revision, which creates six governance objects of five kinds — two attestations, a conformance claim, an authority assignment, an architecture record, and a transition record — and `active_domain_standards: []` means no Active Domain standard owns any of them.

**Independent verification position.** §9 ¶1 does not define *subordinate*; the dossier supplies the meaning itself; under the required ambiguity rule the claim that these objects need no owning Active standard is not proven.

**Adjudication.** Terra's factual premises are correct — §2's definition list contains no entry for *subordinate*, and `ADOPTION_CONFORMANCE_DOSSIER.template.md` §4.5 supplies it. But the correction Terra demands ("constitutional text or an unambiguous governing basis") cannot be performed: constitutional text requires amending v1.2.0, which is authority level 1 and outside the audit's scope. A finding whose only remedy is barred by the controlling authority is not an implementation defect.

**Repository evidence.**

| Fact | Where |
|---|---|
| §9 ¶1's exception list and the word *subordinate* | `REPOSITORY_CONSTITUTION.md` §9 ¶1 |
| §2 contains no definition of *subordinate* | `REPOSITORY_CONSTITUTION.md` §2 — verified by reading the definition list end to end |
| §9 ¶2 uses the same word for the same class: "It MAY govern subordinate Registered protocols, Decisions, and scientific records" | `REPOSITORY_CONSTITUTION.md` §9 ¶2 |
| The interpretation, the five object kinds it covers, the rejected reading, and the falsification test | `ADOPTION_CONFORMANCE_DOSSIER.template.md` §4.5 |
| The reviewer's box for testing it | same file, §5: "I tested interpretation 4.5 and either accept it or have recorded my disagreement in §1's unresolved-violations field" |
| The fail-closed consequence if the reviewer rejects it | §4.5, *How to falsify it*: "adoption is impossible without a §13 amendment, and the correct action is to stop and say so (§12 ¶1)" |

**Engineering decision: closed, with no repository modification.**

Three reasons, in order of weight.

1. **The remedy is barred by the authority order.** The only correction that would satisfy the objection is constitutional text. Producing it means amending an authority-level-1 instrument — outside this sprint's scope, explicitly out of scope in the instruction, and not something an engineering sprint may do at all (§13 requires a Registry-listed steward, an Independent reviewer attestation, and an atomic change; none exists).
2. **§12 ¶1 provides the discharge route actually used.** It permits tracing an Affected MUST to "a manual inspection procedure and version-controlled finding". A recorded interpretation with a stated falsification test, a reviewer checkbox, and a fail-closed consequence is that route. The original defect — a false factual assertion — is gone; what remains is an interpretation that is *recorded and testable* rather than *proven*, which is the strongest available state.
3. **The alternative reading is self-defeating, and the repository says so.** Under it, adoption requires an Active standard owning `attestation`; activating any standard requires an Independent reviewer attestation (§4 ¶2); §13 ¶3 requires two attestations at adoption. The instrument becomes permanently unadoptable. That reductio is stated in §4.5, not hidden.

**Engineering action.** None. Verified unchanged: `REPOSITORY_CONSTITUTION.md` and `GOVERNANCE_REGISTRY.yaml` are byte-identical to their committed state at `234454c` (`git diff --name-only` lists neither).

**Residual governance question.** Does "subordinate" in §9 ¶1 reach constitutionally specified object types? This is reserved to the Independent reviewer and cannot be closed by engineering.

**Required future verification.** The reviewer must test interpretation 4.5 explicitly and record acceptance or disagreement. If they reject it, the correct outcome is a recorded finding and a **blocked adoption** — not a repository edit, and not a differently-worded discharge.

---

## 3. AF-2 — A-10 could not pass against the artifacts it must validate

**Original finding.** Five cited checks (`C-4`, `C-7`, `C-8`, `C-9`, `C-10`) had no implementation while being cited as evidence routes, which §12 ¶1 forbids. Two check namespaces were in use.

**First implementation.** One namespace `A-xx`; `C-xx` withdrawn; `A-10` built; the other four converted to manual procedures `P-A1`…`P-A4`.

**Independent verification position.** `check_attestations()` globs `governance/attestations/*.md` and applies all eight §13 ¶2 Independent-reviewer elements to every file, with no dispatch by document kind. The adopter template lacks reviewer-only content, so `A-10` cannot pass against the supplied templates.

**Adjudication.** Confirmed and understated: the reviewer template *also* failed, because its `- [ ] I am **not** an author` defeats the literal `not an author` matcher. So `A-10` failed against both templates and would fail even if the adopter document were correctly excluded.

**Repository evidence — reproduced before any change.** Importing the module and running its own matchers against both shipped templates:

```
ADOPTER  MISSING: ['non-authorship declaration', 'evidence production',
                   'conflict disclosure', 'review procedure',
                   'competence', 'records examined']
REVIEWER MISSING: ['non-authorship declaration']
```

Six of eight absent from the adopter document; one from the reviewer document. The consequence was concrete: `03_ADOPTION_CHANGE_MANIFEST.md` §6 states the expected post-merge result as "`A-10` attestation completeness | pass", and adds that any divergence other than `A-10` moving from not-verified to pass is itself a finding. That expectation was unreachable with the shipped matcher and the shipped templates. The adoption revision was engineered to fail its own gate on a wording artifact.

**Engineering decision: repair the check, not the templates.**

The templates are correct — §13 ¶2 fixes the reviewer attestation's content exactly, and the adopter is the *author* of the change, so requiring a non-authorship declaration of them is not a defect in the template but a category error in the check. §13 ¶3 requires an adopter attestation without enumerating its content the way ¶2 does for the reviewer, so the adopter element set is derived and is documented as a floor rather than a closed list.

**Engineering action.**

| Change | File |
|---|---|
| `ATTESTATION_ELEMENTS` split into `REVIEWER_ELEMENTS` (the eight §13 ¶2 clauses) and `ADOPTER_ELEMENTS` (attested revision, identified human, adoption declaration, authorship disclosure, steward assignment, acknowledged limitations, conclusion) | `scripts/governance/check_adoption.py` |
| Dispatch by **declared** document kind, via an `<!-- attestation-kind: … -->` marker, with the filename as fallback; a file matching neither reports `NOT_VERIFIED`, never PASS | same |
| Non-authorship matcher made emphasis-tolerant: `not[\W_]{0,6}an[\W_]{1,6}author` | same |
| Unticked declaration checkboxes reported as findings — an unticked box is not a declaration | same |
| Kind markers added | both attestation templates |
| Fixture tests: both completed templates PASS; each element's removal FAILs; raw templates FAIL on placeholders; empty directory and unclassifiable file both `NOT_VERIFIED`; emphasis variants of the non-authorship line all match | `tests/governance/test_check_adoption.py` |

**Verification.** `python -m pytest tests/governance/test_check_adoption.py -q` → **16 passed**. `A-10` remains `NOT_VERIFIED` at this revision, correctly: `governance/attestations/` does not exist, so the criterion is unassessed rather than passed (§12 ¶1). The repair is proven by fixture, not by the live run — which is the only honest way to prove a check that has no subject yet.

**Residual governance question.** None. Whether an attestation's declarations are *true*, and whether the named party is an identified human who is not an author, remains outside mechanical reach and is procedure `P-A1`. That limitation is stated in the check's own output.

**Required future verification.** At the candidate revision (`VER-1b`), confirm `A-10` reports PASS against the real attestations, and that it reports FAIL if any `[COMPLETE]` placeholder or unticked declaration survives.

---

## 4. AF-7, AF-8, AF-9 — one authority model, resolved once

The adjudication's most useful structural finding is that these three findings share a single root cause, and that treating them as three residual defects inflates the failure count. They are recorded together for that reason, with the decision stated once.

### 4.1 The state that was contradictory

| Artifact | Said |
|---|---|
| `RS-1_RESEARCH_STANDARD.draft.md` §11 | "The Registry lists an authority whose permitted transitions cover every transition in §1" — §1 contains 21 |
| `00_MINIMUM_ACTIVATION_PLAN.md` `E-13` | "Registry authority assignment covering every RS-1 transition" |
| `03_ADOPTION_CHANGE_MANIFEST.md` `CE-9` | "`permitted_transitions` extended to cover every RS-1 transition"; and "no Registry-listed authority is permitted for any of RS-1's 21 transitions" as the failure mode |
| `05_RELEASE_CANDIDATE_CHECKLIST.md` `RE-11` | "the `authority_assignments` extension so the steward is permitted every RS-1 transition" |
| `GOVERNANCE_REGISTRY.target.yaml` | granted 19, and stated that `{decision, none → proposed}` and `{decision, proposed → withdrawn}` "are absent by design, not by omission" |
| `RS-1` §7 authority row | named "any contributor" as the authority for those two transitions |

Four artifacts asserted 21; the target implemented 19; and `AF-8` was marked **done** on the strength of the assertion. The count was verified mechanically by joining `e_target.active_domain_standards[0].jurisdiction.owned_transitions` (21) against `e_target.authority_assignments.constitutional_steward[0].permitted_transitions` (19 mappings + 4 constitutional strings): exactly the two decision-lifecycle tuples the verification named were missing, and no grant existed for a tuple RS-1 does not own.

### 4.2 The two available routes

**Route A — Registry-complete.** Grant all 21. State in RS-1 that Registry listing records *permission*, not a required approval step, so no regress is reintroduced.

**Route B — exemption-complete.** Keep 19. Correct the four artifacts that assert 21.

The adjudication observed that Route B is smaller and preserves the `AF-7` reasoning, while Route A removes the interpretive exposure; that either is lawful; and that stating both is not.

### 4.3 Engineering decision: Route A

This departs from the adjudication's note that Route B is "smaller", and the reason is that Route B does not survive its own authority analysis.

1. **Route B leaves an authority assignment outside the Registry.** §2 states the Registry's "sole responsibility is to identify active Normative artifacts, their non-overlapping jurisdictions, and authority assignments". Under Route B, RS-1 §7 assigns authority for two transitions to "any contributor" — an authority source the Registry does not list. §4 ¶3 bars a lower level from enlarging the jurisdiction of a higher one, and §4 ¶1's last sentence is unambiguous: "If any required field is absent or inconsistent, the artifact has no authority."
2. **Route B reintroduces the regress in a second form.** If "any contributor" is not a valid authority source, then no `decision` can lawfully be created, and every transition of every type fails closed again — which is precisely the defect `AF-7` was raised to fix. Route B fixes the regress in the standard's text and leaves it in the authority graph.
3. **Route B repeats `AF-9`'s defect for the `decision` type.** `AF-9` was: RS-1 granted authority to "the executing actor" and "any contributor", enlarging what §4 ¶5 reserves. That was repaired for `observation`, `result`, and `unknown` — and left in place for `decision`. The independent verification saw this and filed it as an unresolved `AF-9`; the adjudication was right that it is not an `AF-9` residual, but wrong to treat it as harmless. Route A makes the authorship/authority separation uniform across all six owned types, which is the invariant `AF-9` established.
4. **Route A makes four existing claims true instead of narrowing them.** RS-1 §11, plan `E-13`, manifest `CE-9`, and checklist `RE-11` were all written to the 21-transition model and are correct as written under Route A. Route B would require editing five statements to say something weaker. When one artifact disagrees with four, the cheaper repair is not automatically the right one.

**The regress is still avoided, and this is the load-bearing distinction.** §2.2.1 now exempts the decision lifecycle from §2.2's requirement of a **prior approving decision** — not from §4 ¶1's requirement that the authority be Registry-listed and permitted. A `decision` transition is recorded *directly* by the permitted Registry-listed authority, with nothing in front of it. Nothing authorizes itself.

**Cost, stated plainly.** Every `decision` creation now requires the Registry-listed authority to record the transition, where Route B would have let any contributor do it. With one steward that is a real throughput constraint. It is not engineered away: RS-1 §2.2.1 and §6.3 record it, §6.2 requires it opened as an activation `unknown`, and reducing it needs either a second Registry-listed authority or a §4 ¶4 delegation — both Registry changes, and neither RS-1's to make (§4 ¶3). Authoring remains unrestricted throughout: any contributor MAY write a proposed `decision` at any time.

### 4.4 Engineering action

| Change | File |
|---|---|
| `{decision, none → proposed}` and `{decision, proposed → withdrawn}` added to the steward's `permitted_transitions`; the "absent by design" rationale replaced with the Route A rationale and the reason Route B was rejected | `GOVERNANCE_REGISTRY.target.yaml` |
| §2.2.1 restated: exemption is from the prior-decision requirement only; §4 ¶1 remains in force for all five `decision` transitions; authorship-is-not-authority applied uniformly; throughput consequence recorded | `RS-1` §2.2.1 |
| §7 authority row: "any contributor" removed as an authority; all five transitions attributed to the Registry-listed authority permitted for the tuple; authoring explicitly permitted to any contributor | `RS-1` §7 |
| §7.3 restated to say "no **prior** `decision` is required" rather than "no `decision` is required" | `RS-1` §7.3 |
| §11 item 7 recorded as **partial** — target complete, live Registry not — rather than ticked | `RS-1` §11 |
| `AF-7`, `AF-8`, `AF-9` rows rewritten with the reopen history and the Route A basis | `05_RELEASE_CANDIDATE_CHECKLIST.md` |

**Verification.** `tests/governance/test_registry_authority_coverage.py` — 7 tests, all passing:

- RS-1 §1 declares exactly 21 owned transitions;
- the target's jurisdiction block matches RS-1 §1 tuple-for-tuple;
- every owned transition has a Registry-granted authority (0 missing);
- no grant exceeds RS-1's jurisdiction (0 extra);
- the four constitutional transitions are still granted;
- the two specific `AF-8` tuples are granted;
- **no governance artifact still asserts the 19-grant model** — a text guard against a partial revert.

**Residual governance question.** Whether §4 ¶5's reservation reaches the decision lifecycle at all is an interpretive question that Route A makes moot for the Registry-grounding purpose: on either reading, the authority is Registry-listed and permitted. What remains open is the throughput consequence of a single steward, which is `AF-17`'s operational question for `HG-4` and the activation `unknown` under §6.2/§6.3.

**Required future verification.** At change E, confirm the live `GOVERNANCE_REGISTRY.yaml` carries all 21 tuples, not just the target; confirm procedure `P-9` is executed on the `decision` branch for at least one `decision` transition record; and confirm no `decision` records its proposer as its own approving authority.

---

## 5. AF-24 — the verification apparatus contradicted the exemption

Found in adjudication. Reported by neither the audit nor the first independent verification, and decidable without resolving any interpretive question.

**The defect.** RS-1 §7.2 and procedure `P-9` in §9.1 both instructed the reviewer to locate the approving `decision` "for each transition record", with no decision-lifecycle carve-out. `P-9` is the named manual procedure §12 ¶4 requires and the sole verification route for §2.2 in the §9 mapping table. Executed as written against a Decision-creation transition record, it finds no approving decision and fails the transition closed — defeating §2.2.1 at the point of verification rather than in its text.

This mattered independently of Route A: even a Registry-listed tuple has no approving decision for `P-9` to locate.

**Engineering action.** `P-9` now dispatches on object type. For a type other than `decision`: locate the approving `decision`, then resolve its approver against the Registry. For a `decision` transition: no prior approving `decision` exists and none is required (§2.2.1); confirm instead that the authority named in the transition record is Registry-listed and permitted for that exact tuple. Both branches fail closed on an unlisted authority, and the procedure requires the reviewer to record which branch was applied. New §7.2.1 states the two branches normatively; the §9 mapping gained rows for §2.2.1 and for §7.2/§7.2.1.

**Verification.** `tests/governance/test_rs1_mapping.py` asserts every RS-1 section carrying a MUST is cited in the §9 mapping, with four excluded sections each carrying a stated reason; that the mapping cites no section and no procedure that does not exist; and that every defined procedure is used. The mapping grew from 19 rows to 43, and the procedure set from 11 to 15. Measured at the pre-sprint revision: of 39 RS-1 sections carrying a MUST, **20 had no mapping row at all** — `§2.2.2`, `§2.3`, `§2.4`, `§2.6`, `§2.7`, `§3.1`, `§4.1`, `§4.2`, `§4.3`, `§5.3`, `§5.4`, `§6`, `§7`, `§7.2`, `§7.3`, `§8.3`, `§8.4`, `§10.1`, `§10.3`, `§10.4`. RS-1 §11's item "every MUST appears in the §9 mapping" would therefore have been false had it been ticked, and §11 now records its state with the test as evidence rather than as a checkbox. Procedures `P-12`…`P-15` were added to cover the gap: record-field completeness, tool-inferred state, over-claimed representations, and the lawfulness of an RS-1 amendment.

**Residual governance question.** None.

**Required future verification.** After `AUT-4` builds `A-11`…`A-15`, confirm the mapping test still passes and that no newly built check is cited without its status being accurate.

---

## 6. AF-23 — reversibility

**The defect, and the correction to how it was framed.** RS-1 §2.6 said "Every state change MUST be reversible", while §3 said "registration is **not reversible**". The independent verification called this an RS-1-versus-Constitution conflict; the adjudication corrected that: Constitution §8 ¶2 says "Every **scientific** state change", so RS-1 had over-broadened the clause it cited, and the conflict is RS-1 §2.6 against RS-1 §3.

**Engineering action.** §2.6 narrowed to §8 ¶2's own scope word, with a note that RS-1 does not extend it because a wider claim than the Constitution's would be a lower level enlarging a higher one (§4 ¶3). New §2.6.1 defines reversal: annulling the *effect* of a prior transition by a later authorized `decision` while retaining every record, never by edit or deletion — so "reversible" does not mean an immutable object's prior state can be re-entered. §3's row restated: registration is not **undone**, and its §8 ¶2 reversal route is supersession, which preserves the previous state, rationale, supporting records, and transition history. Mapping rows added for §2.6, §2.6.1 and §2.7.

This removes the contradiction without weakening §8 ¶2, because §8 ¶2 never reached beyond scientific state changes in the first place.

**Residual governance question.** Whether supersession satisfies §8 ¶2's "reversible by a later authorized Decision" for an object whose definition forbids re-entering its prior state. The repository now states its answer and its basis; a reviewer may disagree, in which case the affected row is §3's, not the Constitution's.

---

## 7. AF-25 — identifier namespaces

**The defect, measured.** `00_MINIMUM_ACTIVATION_PLAN.md` §7.3 stated: "One namespace. Checks are `A-xx`, and `A-xx` means exactly one thing." That sentence was false across fifteen identifiers, and four further prefixes carried two or three meanings:

| Token | Meanings in the repository |
|---|---|
| `A-01`…`A-15` | implemented checks · design-register checks · (unpadded `A-1`…`A-7`) proposed amendments |
| `G-1`…`G-12` | change-D preflight gates · governance-stack standards |
| `D-1`…`D-3` | change-D contents · design defects · amendment-record derived amendments |
| `X-1`…`X-7` | external blockers · extension points |
| `E-1`…`E-9` | plan engineering tasks · change-E contents |
| `F-1`…`F-5` | attestation finding rows · design redesign forces · amendment-record findings |

The `E-` collision is the sharpest, because both sides are live and both are cross-cited: plan `E-9` is "branch protection and commit signing"; manifest `E-9` is the `authority_assignments` extension whose omission activates a standard that authorizes nothing. §11 ¶3 forbids identical names concealing distinct types, and `AUT-4` was scheduled to build `A-11`…`A-15` into the very file whose design register had already spent those ids.

**Engineering action.** The Draft design register was re-keyed into a segregated namespace — `DA-xx` checks, `DG-x` stack standards, `DD-x` defects, `DX-x` extension points, `DF-x` redesign forces, and `DAM-8` for the one amendment the design set *proposes* rather than cites. Measured over the 13 files of `governance/design/**`, with the command below: live-shaped identifier tokens fell from **665** to **12**, and the 12 that remain are the disambiguation table in `design/README.md`, which must name the live ids in order to warn about them; design-namespace tokens now number **683**.

```
python -c "import pathlib,re,subprocess; D=pathlib.Path('governance/design'); NEW=re.compile(r'(?<![A-Za-z0-9])(DA|DG|DD|DX|DF|DAM)-\d{1,2}(?![0-9])'); OLD=re.compile(r'(?<![A-Za-z0-9])(A-\d\d|G-\d{1,2}|D-[123]|X-\d{1,2}|F-[1-5])(?![0-9])'); fs=[p for p in sorted(D.rglob('*')) if p.is_file() and p.suffix in ('.md','.yaml','.yml')]; new=sum(len(NEW.findall(p.read_text(encoding='utf-8'))) for p in fs); old=sum(len(OLD.findall(p.read_text(encoding='utf-8'))) for p in fs); head=sum(len(OLD.findall(subprocess.run(['git','show','HEAD:'+str(p).replace(chr(92),'/')],capture_output=True,text=True,encoding='utf-8').stdout)) for p in fs); print('files',len(fs),'| live-shaped at HEAD',head,'| live-shaped now',old,'| design-namespace now',new)"
```

The manifest's change contents were re-keyed `CD-1`…`CD-11` and `CE-1`…`CE-9`, **23** rewrites (11 + 12, from 0 of each at HEAD), with every cross-reference in the checklist and RS-1 updated. Plan §7.3's false sentence was replaced by a namespace register naming the owner artifact of every prefix. `governance/design/README.md` gained a disambiguation table.

**What was deliberately not renamed, and why.** Citations of another artifact's identifiers: the amendment record's `A-1`…`A-7`, `F-6`/`F-9`/`F-19`, and `L-4`. Renaming a citation breaks the reference, and re-keying an audit record's own identifiers after the fact would rewrite an audit at a stated revision (§3 ¶5). These are distinguished by zero-padding — a check is always `A-05`, an amendment always `A-5`, and an amendment is always cited with a form of the word "amend" — and the convention is stated in both namespace registers and enforced by two tests. `H-01`…`H-14` (design) versus `H-1`…`H-9` (plan) is the same case and is handled the same way.

One token in that set turned out **not** to be a citation. Six occurrences of "amendment `A-8`, the General Delegation Clause" pointed at nothing: `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md` defines `A-1`…`A-7` and stops. `A-8` was a proposal originating in the design set, wearing a citation's clothes — so it is design-owned, and it is re-keyed `DAM-8`. It is now enforced: a test parses the amendment record's own headings and fails on any unpadded `A-n` in the design set that the record does not define.

Archived content under `archive/` was not touched: it has no authority (§4 ¶7), and rewriting retained history to satisfy a naming convention would trade a legibility improvement for a retention violation.

**Verification.** `tests/governance/test_identifier_namespaces.py` — 11 tests, all passing: no design-space identifier appears in the live surface; no live identifier appears in the design set; the design set cites no amendment id the amendment record does not define; every unpadded `A-n` citation in the design set carries a disambiguating word; the `DX-` range is contiguous and nothing cites past its end; the manifest's rows are `CD-`/`CE-`; no document cites a manifest item by its old id; the implemented check set is exactly `A-01`…`A-10`; no withdrawn `C-xx` is cited as an evidence route; the plan's namespace register exists and records that its predecessor claim was false; the checklist carries `AF-25`.

**Residual governance question.** None. The padding-based distinction between check ids and amendment ids is a convention, not a mechanism, and is the one residual legibility hazard; it is disclosed rather than solved.

---

## 8. AF-13, AF-15, AF-19 — the hardening items

| Finding | Defect | Action | Evidence |
|---|---|---|---|
| `AF-13` | `AR-1` declared `Status: Active`, a term §2 defines for Registry-listed Normative artifacts and standard-governed objects; `AR-1` is deliberately neither, so §11 ¶3 was breached and `A-01` passed because it checks presence only | Status is now `Current — descriptive Level-4 record`, with the reason stated in the header | `governance/AR-1_REPOSITORY_ARCHITECTURE_RECORD.md`; `A-01` still PASS at `RUN_2026-07-25_C.md`; the dossier's §11 ¶3 row now names what to verify |
| `AF-15` | The dossier's "roughly 112 MUSTs and 44 MUST NOTs" overstated the MUST count — and that number is what justifies the not-applicable strategy to the reviewer | Recounted: **115** MUST-family occurrences, **44** `MUST NOT`, **71** bare `MUST`. The template carries the figures, the command that reproduces them, and the statement that these are occurrences rather than distinct requirements | `ADOPTION_CONFORMANCE_DOSSIER.template.md` §0 |
| `AF-19` | `G-9` was closable by an unsigned commit from a non-routable identity, while asserting "identified humans" | `G-9` now requires routable contacts **and** that the commits carrying the attestations are signed and verify; `SEC-3` and `HG-1` are prerequisites of `HG-5`/`HG-6`, because signing cannot be applied retroactively to a committed attestation | `03_ADOPTION_CHANGE_MANIFEST.md` §2; checklist `HG-5`, `HG-6` |

---

## 9. Verification summary for this sprint

| Instrument | Command | Result |
|---|---|---|
| Advisory constitutional checks | `python scripts/governance/check_adoption.py` | `PASS=5, FINDINGS=3, FAIL=1, NOT_VERIFIED=1`, exit 1. Blocking: `A-07` (FAIL, disclosed as `V-1`), `A-10` (NOT_VERIFIED, no subject yet). Verbatim in `governance/checks/RUN_2026-07-25_C.md` |
| Sprint guards | `python -m pytest tests/governance -q` | **39 passed** |
| p1_os suite | `python -m pytest tests/p1_os -q` | **382 passed** |
| Whole repository | `python -m pytest -q --continue-on-collection-errors` | **780 passed, 3 skipped, 15 collection errors** — all pre-existing, all under `tests/p1_os/`, reproduced with `--ignore=tests/governance`. Recorded as `AUT-5` |

**Nothing here is a conformance claim.** These are advisory checks and validation artifacts. `A-07` fails and will continue to fail after remediation; `A-10` is unassessed rather than passed; the whole-repository test run does not execute at all without a flag. All four facts are recorded rather than smoothed.

---

## 10. What this sprint did not do

Stated so that a reviewer does not have to infer it from absence.

- **No constitutional amendment.** `REPOSITORY_CONSTITUTION.md` is unmodified.
- **No Registry activation.** `GOVERNANCE_REGISTRY.yaml` is unmodified: `status: Draft`, `constitutional_steward: []`, both attestations `null`.
- **No attestation signed, no steward appointed, no adoption performed.** §4 ¶4 reserves these to identified humans.
- **No gate closed.** Two of ten remain closed, as before. `G-1` needs a person; `G-2` needs a provider action.
- **No readiness credit claimed for D or E.** Instrument repair is counted on its own axis, precisely so it cannot be mistaken for task execution.
- **`AF-12`, `AF-14`, `AF-16`…`AF-18`, `AF-20`…`AF-22`** remain out of scope by the audit's own recommendation. `AF-17` — two stewards rather than one plus an inert successor — is an operational decision for `HG-4` and is the only action available today that forecloses the single unrecoverable state the Constitution contains.
- **`AUT-5`** (whole-repository pytest collection) is disclosed and left open: repairing it means restructuring test packages this sprint does not otherwise touch, and no governance artifact cites `pytest` output as conformance evidence.

---

## 11. Standing residual risks

| # | Risk | Why engineering cannot close it |
|---|---|---|
| R-1 | Interpretation 4.5 may be rejected by the Independent reviewer | Constitutional interpretation of an instrument no engineering sprint may amend. Correct outcome is a recorded finding and blocked adoption (§12 ¶1) |
| R-2 | One steward means `decision` approval throughput is a single point of failure, and Route A raises the load | Requires a second Registry-listed authority or a §4 ¶4 delegation — Registry changes reserved to humans |
| R-3 | `A-07` will fail permanently | Presence of a secret in history is permanent; the conforming end state is a rotated key plus a disclosed violation |
| R-4 | Padding is the only thing separating check ids from amendment ids | A convention, not a mechanism. Disclosed in two namespace registers and enforced only for the ranges a test can see |
| R-5 | `A-11`…`A-15` are specified and unbuilt | `AUT-4`. Until built each is reported not verified and is cited as passed by nothing |
| R-6 | Four classes remain undetectable from inside the repository: backdated timestamps, pre-first-run history rewriting, forged records absent signing, and work performed and discarded outside version control | `SEC-3`/`SEC-4`/`SEC-5` narrow three; the fourth closes only by people, which is why §13 requires two |
| R-7 | This record, the checks, and the tests were produced by the same party that performed the engineering | §12 ¶1: a self-review may find defects but MUST NOT be labelled independent. Every claim above names a re-runnable command for that reason |

---

## 12. Independent audit of this sprint, and what it found

Before this record was finalised, an auditor that did not perform the engineering was asked to falsify eleven of its claims by reading the repository and running commands. It verified eight, partially falsified two, and found nine defects the sprint had not recorded. Recording that here, rather than only the corrected end state, is the point: the sprint's own first pass made the same class of error it was convened to fix.

| Claim tested | Result |
|---|---|
| Constitution and live Registry unmodified | verified — `git diff --stat` empty for both |
| Registry target grants all 21 tuples, no asymmetry either way | verified by an independent parse: 21 owned, 21 granted, 4 constitutional strings, empty difference in both directions |
| No artifact still asserts the 19-grant model | verified — `absent by design` survives only as quoted history in this record and as a negative assertion inside the test |
| `A-10` passes both completed templates and fails on each element's removal | verified independently: all 15 element patterns detected on removal (7 adopter + 8 reviewer) |
| Check-run summary and `A-05` figure | verified exactly |
| `RUN_2026-07-25_C.md` records that run accurately | **falsified** — see below |
| No identifier collision remains | **partially falsified** — see below |
| RS-1 §9 mapping and §9.1 procedure set are complete and gap-free | verified: `P-1`…`P-15`, no gaps, nothing cited-but-undefined, nothing defined-but-uncited |
| The dossier's numeric claims | five verified, one falsified, one unreproducible — corrected above |
| False completion claims | none found: three ticked boxes exist repository-wide and all three hold; every figure in the checklist reconciles |
| Whole-repository `pytest` aborts, pre-existing | verified — 15 errors persist with `--ignore=tests/governance` |

### What it falsified, and what was done

**The run record's self-reference disclosure was itself wrong.** `RUN_2026-07-25_C.md` reported a before/after pair of `669 → 670` matches. The true pre-record state is `668 in 103`, the file contributes **two** matches rather than one, and `669 in 104` is a state that never existed — the generator had counted an earlier draft of the same record. This is the `AF-3`/`AF-5` defect class reproduced inside the artifact written to prove the sprint's evidence reproduces, and two `done` rows cited it. It is now rewritten to state one measured figure, the exact decomposition, and the standing fact that **every** check-run record inflates `A-05`, because `governance/checks/` is inside the live surface and each record quotes `A-05`'s own limitation line.

**`A-8` was a dangling identifier**, so `AF-25` was not fully closed: six citations of "amendment `A-8`" resolved to nothing. Re-keyed `DAM-8` and now enforced by a test that parses the amendment record's own headings. **`DX-15`** was cited in `design/README.md` while only `DX-1`…`DX-14` exist — in the document written to fix identifier hygiene. Corrected, and the range is now asserted contiguous.

**The guard that would have caught `A-8` was dead code.** `DESIGN_ALLOWED_CITATIONS` was defined and never referenced, and the design-side pattern matched two-digit ids only, so no test constrained unpadded `A-n` at all. The suite passed while the boundary it documented was unenforced. Replaced by two tests that use it.

**Two stale counts.** `RUN_C` said 34 governance tests and 775 whole-repository; the suite had grown after the record was written. Both re-measured (39 and 780) and both records corrected. The lesson is mechanical: a record that quotes a count must be regenerated after the last change to what it counts, and this one was not.

**`SEC-2` had no task row** while the roll-up counted `SEC-1`…`SEC-5` as five and blocker `X-3` cited it — a pre-existing gap the sprint edited around without noticing. Row added.

**A throwaway analysis script was left at the repository root**, untracked and not ignored. Under `RE-9a` it would have ridden into the candidate revision whose contents `CD-1`…`CD-11` enumerate exactly, breaking the atomicity claim the manifest makes. Deleted.

**RS-1's namespace claim was stronger than the facts.** It said `A-xx` "denotes exactly one thing repository-wide". `A-11`…`A-15` do not appear in `check_adoption.py` at all, and `A-1`…`A-7` denote amendments. This record conceded that padding is a convention rather than a mechanism; RS-1 — the artifact that would become normative — did not. Reworded to match.

### What this says about the verdict

Nine defects in a sprint whose own report was about to claim internal consistency. Three rounds of external scrutiny have now each found defects in work already marked done: independent verification found two, adjudication found three, this audit found nine. The rate is falling in severity — this round produced no authority defect, no false ticked box, and no arithmetic error in the register — but it has not reached zero, and no self-assessment should be read as evidence that it has.
