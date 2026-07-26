# Automation Architecture — the check register

- **Status:** Draft
- **Scope:** Design of every mechanically decidable check derivable from `REPOSITORY_CONSTITUTION.md` v1.2.0 and the proposed standard stack
- **Responsibility:** Specify inputs, outputs, algorithm, limitations, false positives, and false negatives for each proposed check
- **Authority source:** None. This record has no normative authority. On activation the register would be owned by DG-11.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. Constitutional position of automation

Four clauses bound everything here, and they cut in different directions.

**§12 ¶3 — obligation.** "CI, tests, schemas, and linters SHOULD enforce every mechanically decidable requirement. Requirements not mechanically decidable MUST have a named manual review procedure." So the register should be *maximal*: every decidable MUST gets a check.

**§4 ¶4 — limit.** "Automated systems MAY propose, check, or apply an already-authorized transition; they MUST NOT supply human authority or independent review." So a check emits **findings**, never approvals. A green pipeline is not a conformance claim, an attestation, or an authorization. DG-5 conformance claims *cite* check outputs; they are not produced by them.

**§12 ¶4 — scope limit.** "A check is evidence of conformance only for the criteria, revision, and Scope it actually assessed." So every check declares its scope, and its output is only admissible within it.

**§12 ¶1 — honesty requirement.** "An unavailable check MUST be reported as not verified, never as passed." This single sentence prohibits the repository's current dominant pattern. `.github/workflows/ci.yml` terminates lint and test steps with `|| true` and targets directories (`core/`, `validation/`) that no longer exist; those jobs cannot fail and their green status is not evidence of anything. Under §12 ¶1 that is not a minor defect — it is a check reporting "passed" when it means "not verified."

Two engineering consequences follow directly:

1. **Every check asserts its own target set is non-empty.** A check that silently matches zero files reports `NOT_VERIFIED`, not `PASS`. This is the most valuable single line of defence in the whole register, because path drift is the normal way checks die.
2. **`|| true`, `continue-on-error`, and equivalent suppression are prohibited** in any check whose output may be cited for conformance. A check may be registered as *Advisory* — but that status is declared in the register and surfaces in output, not achieved by swallowing an exit code.

---

## 2. Check status model (owned by DG-11)

```
Proposed → Active → Advisory → Broken → Retired
```

- **Active** — output is admissible as conformance evidence within its declared scope.
- **Advisory** — runs and reports; output is *not* admissible. Used for heuristics with high false-positive rates.
- **Broken** — the check cannot execute or its target set is empty. Reports `NOT_VERIFIED` loudly; MUST NOT be silently skipped.
- **Retired** — superseded; retained with its history.

Every check declares, at registration: `id`, `requirement_ids` (the clauses it assesses), `scope`, `inputs`, `outputs`, `algorithm`, `limitations`, `known_false_positives`, `known_false_negatives`, `status`, `owner`. Registration without the FP/FN disclosure is rejected — an undisclosed false-negative rate is how a check register becomes a false assurance.

Checks are themselves validated: each ships fixtures containing known-violating and known-conforming inputs, and a check that passes its own negative fixtures is Broken by definition.

---

## 3. Detailed specifications — the twelve consequential checks

### DA-04 · Jurisdiction disjointness and single ownership
**Requirement:** §4 ¶2 (Registry MUST reject overlapping jurisdictions), §9 ¶1 (exactly one Active Domain standard per object type per Scope).
**Inputs:** `GOVERNANCE_REGISTRY.yaml`; every `registry/jurisdictions/*.yaml`; `ontology/TYPE_REGISTER.yaml`.
**Outputs:** Findings listing colliding pairs with the specific colliding element; `PASS` / `FAIL` / `NOT_VERIFIED`.
**Algorithm:** Build the set of `(object_type)` owners; fail on any type with ≠ 1 Active owner. Build the set of `(type, from_state, to_state)` transitions; fail on any tuple owned by more than one standard. For scope overlap, compare declared scope dimensions pairwise; where two standards own the same type under scopes whose declared populations, environments, conditions, versions, and time intervals intersect, fail unless one Registry entry contains an explicit delegation of non-conflicting refinement to the other (§4 ¶2). Verify each standard's `not_owned` disclaimers do not intersect its own `owned_object_types`.
**Limitations:** Scope intersection is decidable only to the precision of the declared scope dimensions. Free-text scope values reduce this to string comparison, which is why §2's identifiability requirement matters mechanically and not only rhetorically.
**False positives:** Two standards legitimately governing the same type in genuinely disjoint scopes that happen to share vocabulary (e.g. "production" meaning different environments). Mitigation: scope values drawn from controlled enumerations where possible.
**False negatives:** Semantic overlap between differently-named object types — e.g. one standard owning `evaluation_run` and another owning `benchmark_run` for the same real activity. No structural check can catch this; it is `MRP-15`'s job.

### DA-05 · Authority exists and permits the declared transition
**Requirement:** §4 ¶1-2 (every authority source identifies jurisdiction and permitted transitions; activation fails closed if no permitted authority exists), §4 ¶5.
**Inputs:** Registry authority assignments; `governance/authority/*`; `governance/delegations/*`; the transition record or activation dossier under assessment.
**Outputs:** `PASS` / `FAIL(no_authority | authority_not_permitted | authority_expired)`.
**Algorithm:** Resolve the claimed approver to an Active authority assignment; verify the assignment's `permitted_transitions` contains the transition tuple; walk the delegation chain to the constitutional steward, verifying at each hop that the child's transitions and scope are contained in the parent's; verify no hop is expired, revoked, or held by a non-human (§4 ¶4).
**Limitations:** Verifies the *record*, not that the human actually approved. Signature or platform-attested identity strengthens this; without it, the check confirms only internal consistency.
**False positives:** An authority whose assignment is Active but whose Registry entry is mid-migration; appears unpermitted during the window. Mitigation: §2 atomicity eliminates the window.
**False negatives:** A forged authority record committed by someone with write access. Undetectable without signing. This is the check most improved by commit signing and branch protection, and it is the reason a single-actor repository cannot self-verify authority.

### DA-20 · Registration precedes execution
**Requirement:** §2 (*Registered protocol* = registration transition occurred **before** governed execution began), §5 ¶3 (elements fixed before unblinded access).
**Inputs:** `protocols/registered/*` with registration transition records; execution artifacts and their commit metadata; custody manifests; where available, external timestamp receipts.
**Outputs:** `PASS` / `FAIL(execution_precedes_registration)` / `NOT_VERIFIED(no_external_anchor)`.
**Algorithm:** For each protocol, take the registration transition's recorded time and its commit; for each execution artifact attributable to that protocol, take the earliest evidence of execution (commit time, artifact internal timestamp, custody manifest registration); fail if any execution evidence precedes registration. Where an external timestamp anchor exists, verify the registration commit against it.
**Limitations:** **This is the weakest check in the register, and its weakness is structural.** Git commit timestamps are author-controlled and trivially backdated; commit order can be rewritten before push. Absent an external anchor, the check verifies only that no *recorded* execution precedes registration — a property the same actor controls.
**False positives:** Legitimate re-execution of a protocol after amendment, where artifacts from the prior protocol version are attributed to the new one. Mitigation: attribution by protocol version, not protocol id.
**False negatives:** Backdated registration; execution performed outside the repository and imported later; unblinded access that produced no artifact at all — §5 ¶3's trigger is *access*, and access leaves no trace. Because the false-negative surface is this large, `DA-20` SHOULD be registered as **Advisory** until an external anchor exists, and the residual exposure recorded as an Unknown. Reporting it as Active would overstate the guarantee.

### DA-14 / DA-45 · Result immutability and protected-path history integrity
**Requirement:** §7 ¶1 (Results immutable from creation; history MUST NOT be rewritten to conceal a prior Result), §8 ¶2.
**Inputs:** `results/**`; full git history for protected paths; prior check-run records holding known digests.
**Outputs:** Findings identifying modified or vanished Results; `PASS` / `FAIL`.
**Algorithm (DA-14):** For each Result, compute a canonical content digest; compare against the digest recorded in its creating transition record; fail on mismatch. **(DA-45):** For every protected path (`results/`, `evidence/`, `observations/`, `decisions/`, `unknowns/`, `constitution/attestations/`, `registry/transitions/`), verify that the commit introducing each file is still reachable from the default branch and that no reachable commit modifies or deletes a previously-recorded file; compare the current commit graph against the graph recorded at the last run.
**Limitations:** A history rewrite that also rewrites the check's own stored digests is invisible from inside the repository. Detecting it requires state outside the repository — a mirror, a signed tag registry, or a CI provider's immutable log.
**False positives:** Line-ending or encoding normalization changing digests without changing content. Mitigation: canonicalize before digesting, and record the canonicalization version.
**False negatives:** Force-push before the first run; content changed in the same commit that created it; a Result never committed at all.

### DA-22 · Atomic change completeness
**Requirement:** §2 (*Atomic change* — every required artifact, Registry entry, approval, attestation, and transition record present in one accepted revision, with no intervening revision missing any element), §4 ¶2.
**Inputs:** The proposed merge commit's full tree and diff; the activation or transition type being claimed; the Domain Standard Interface requirements.
**Outputs:** `PASS` / `FAIL(missing: [...])` naming each absent element.
**Algorithm:** Classify the change (standard activation, amendment, scientific transition, release). Look up the required element set for that class. Verify every element is present **in the resulting tree**, and — critically — that the change is a single revision on the default branch rather than a sequence in which an intermediate revision lacks an element. For a squash or merge, verify the resulting default-branch revision is complete.
**Limitations:** Classification depends on the change declaring its own type. A misdeclared change is checked against the wrong element set.
**False positives:** Large refactors touching governance paths incidentally and being classified as activations.
**False negatives:** A change that declares itself as an ordinary edit while performing an activation. Mitigation: `DA-03` independently detects a status change to `Active` without an activation dossier, so the two checks cover each other.

### DA-39 · Requirement coverage
**Requirement:** §12 ¶1 (every Affected MUST/MUST NOT traces to a check, a manual procedure, or a testable non-applicability statement), §12 ¶4.
**Inputs:** Every Active normative artifact; `automation/CHECK_REGISTER.yaml`; the `MRP-xx` register; non-applicability statements.
**Outputs:** Per-requirement coverage table; `FAIL` listing unmapped requirements.
**Algorithm:** Extract every RFC-2119 MUST/MUST NOT sentence from Active artifacts, keyed by clause id. Join against the union of check `requirement_ids`, MRP coverage, and non-applicability statements. Fail on any unmapped requirement. Additionally fail any change that *adds* a MUST without adding coverage in the same change.
**Limitations:** **Requires addressable clause identifiers.** The Constitution currently has none (finding F-19 in the v1.2.0 amendment record), so coverage against the Constitution itself must be maintained as a hand-curated map — which is exactly the kind of artifact that silently rots. Adding clause IDs is the highest-leverage mechanical improvement available to the Constitution.
**False positives:** A sentence containing "must" inside a quotation or an example.
**False negatives:** A requirement expressed without RFC-2119 keywords ("is required to", "shall", "it is necessary that"). Mitigation: a lexical screen for requirement-shaped prose lacking keywords, registered separately as Advisory.

### DA-07 · Prohibited self-authority and certainty lexemes
**Requirement:** §1 ¶2 (no artifact may override the Constitution by declaring itself canonical, absolute, frozen, or authoritative), §8 ¶3 (proven, true, final, permanent, certain prohibited for empirical Claims absent a bounded technical definition), §5 ¶6.
**Inputs:** All version-controlled text outside `archive/`.
**Outputs:** Findings with file, line, matched lexeme, and clause.
**Algorithm:** Match a lexeme list — canonical, absolute, frozen, authoritative, definitive, supreme, immutable-by-declaration, single source of truth, proven, final, permanent, certain — in artifact headers, status fields, and normative sentences. Exempt: quotations of the Constitution; `archive/` content; occurrences where an Active standard defines a bounded technical meaning and the occurrence cites that definition.
**Limitations:** Purely lexical. Cannot detect an artifact that *behaves* as canonical without saying so.
**False positives:** Legitimate technical uses — "immutable" describing a Result correctly per §7, "frozen" describing a dependency lockfile, "canonical" describing a canonicalization algorithm. Requires an allowlist with per-occurrence justification, which is real ongoing cost.
**False negatives:** Paraphrase ("this document takes precedence over all others"). Mitigation: `MRP-16` reviews precedence-shaped prose.
**Note:** Running this check today produces roughly 13 findings across `PROGRAM_D_CANONICAL.md`, `theory/PROGRAM_D_CONSTITUTION.md`, `RESEARCH_PROTOCOL.md`, and four `theory/` instrument files. That is the expected pre-adoption state, not a bug in the check.

### DA-17 · Evidence provenance completeness
**Requirement:** §6 ¶1 (nine mandatory identification items).
**Inputs:** `evidence/**`; O-1 schema; custody manifests.
**Outputs:** Per-record findings naming each missing item.
**Algorithm:** Schema-validate each Evidence record for all nine items; verify each is non-empty and not a placeholder (`TBD`, `N/A`, `unknown`, empty list) — an absence stated as a value is still an absence; verify the digest field resolves to a registered non-deprecated algorithm (`DA-43`); verify reproduction inputs (code, config, data, environment, randomness) each resolve to a retrievable identifier.
**Limitations:** Presence is decidable; *sufficiency for reproduction* is not. A record can list an environment and still be irreproducible.
**False positives:** Legitimately inapplicable items — e.g. randomness inputs for a deterministic transformation. Requires an explicit, testable non-applicability statement per §12 ¶1, not silence.
**False negatives:** Plausible but wrong provenance; a digest of the wrong artifact. Only replication detects this, which is why `DA-17` is a floor and not a guarantee.

### DA-60 · Negative Result retention
**Requirement:** §7 ¶4 (Negative Results retained under identical rules; MUST NOT be deleted, hidden, relabelled as a failed run, or excluded from synthesis solely because they oppose a preferred Claim).
**Inputs:** `results/**`; execution records; protocol registrations; custody manifests.
**Outputs:** Advisory findings: per-protocol execution count vs recorded Result count vs Negative Result count.
**Algorithm:** For each Registered protocol, count executions evidenced by any source (custody manifests, run logs, artifact directories) and compare to recorded Results. Flag gaps. Compare the ratio of Negative to Positive Results against the protocol's declared power or expected null rate where stated. Flag Results labelled "failed run" whose validity determination shows they satisfied all registered validity criteria — the specific relabelling §7 ¶4 prohibits.
**Limitations:** Statistical and circumstantial. A gap is a *question*, not a violation; executions can legitimately be abandoned (§7 ¶2 provides for it, with disposition recorded).
**False positives:** Genuinely abandoned executions with recorded disposition; exploratory runs never intended to produce Results.
**False negatives:** A Negative Result never recorded anywhere, in a workflow where execution leaves no independent trace. This check can only compare records that exist; the file-drawer problem is fundamentally not mechanically closable, which is why §7 ¶4 is a MUST addressed to people and `MRP-17` exists.
**Status:** Advisory by construction. Reporting it as Active would misrepresent a heuristic as a proof.

### DA-61 · Test success not reported as scientific success
**Requirement:** §3 ¶7 ("Passing software tests establishes only conformance to those tests. It MUST NOT be reported as scientific success unless a Registered protocol independently makes that test output relevant Evidence"), §2 (*Reported as scientific success*).
**Inputs:** Scientific records, Decisions, Results, Interpretations, Claims, conformance records; test outputs; protocol registrations.
**Outputs:** Findings where a test result is cited in a scientific record without a protocol making it relevant Evidence.
**Algorithm:** Identify references to test suites, CI runs, pass rates, or coverage inside scientific records. For each, verify a Registered protocol declares that test output as relevant Evidence for the cited Claim. Fail otherwise.
**Limitations:** Requires recognising test-derived assertions, which are often paraphrased ("all validation passed", "100% pass rate").
**False positives:** A record legitimately describing engineering status in an informative section.
**False negatives:** Paraphrased test results with no lexical marker. Mitigation: `MRP-18`.
**Note:** `RESEARCH_PROTOCOL.md`'s "must return a 100% pass rate" gate is precisely the construct §3 ¶7 targets; under this check it would be a standing finding until a protocol makes those tests relevant Evidence for a stated Claim.

### DA-19 · Interpretation alternatives completeness
**Requirement:** §5 ¶5 (Active Interpretation records a null explanation, the strongest materially distinct alternative from a documented search, and a discriminating Observation or experiment; absence of an alternative MUST NOT support uniqueness).
**Inputs:** `interpretations/**`; linked Unknowns.
**Outputs:** Per-record findings.
**Algorithm:** For each Active Interpretation, verify presence and non-triviality of: null explanation; at least one materially distinct alternative with a documented search (method, sources, date, limits); a stated discriminating Observation or experiment. Where alternatives are empty, verify a linked Unknown records the search and its limits, and verify the Interpretation does **not** assert uniqueness.
**Limitations:** "Strongest" and "materially distinct" are judgements. The check verifies structure; `MRP-12` verifies substance.
**False positives:** A genuinely exhausted alternative space with a properly recorded Unknown, flagged as incomplete.
**False negatives:** A strawman alternative satisfying the field while defeating the clause's purpose — the characteristic failure of this requirement.

### DA-34 · Boundary and dependency conformance
**Requirement:** §10 ¶1 ("A directory name MUST NOT be treated as proof of separation"), §3, §10 ¶4.
**Inputs:** Every `_BOUNDARY.yaml`; the file tree; import and reference graphs across `software/`, `validation/`, `automation/`, and the record stores.
**Outputs:** Findings per violated edge or misplaced object.
**Algorithm:** Verify every directory has a boundary declaration. Verify each file's `object_type` is permitted in its directory. Verify every cross-directory dependency (import, path reference, record reference) is in the source directory's `permitted_dependencies`. Enforce the eight dependency rules of the architecture record — in particular: record stores MUST NOT depend on `software/`, `validation/`, `automation/`, or `audit/`; nothing may depend on `archive/`; `domain_standards/` MUST NOT depend on any record store; `software/` MUST NOT depend on `validation/`.
**Limitations:** Static reference detection misses dynamic imports, string-constructed paths, and out-of-band coupling (a shared database, an environment variable).
**False positives:** Documentation referencing an archived artifact for historical context. Requires an explicit citation form distinguishable from a dependency.
**False negatives:** Runtime coupling; conceptual coupling with no textual reference. Mitigation: `MRP-19` architecture review, plus `DA-32` on Material state.

---

## 4. Complete register

Status legend: **A** Active-eligible · **Adv** Advisory by construction · **P** Partial (mechanical part only; paired with an MRP).

| Id | Requirement | Inputs | Outputs | Algorithm (summary) | Limitations | False positives | False negatives | St |
|---|---|---|---|---|---|---|---|---|
| DA-01 | §4 ¶1, §12 | `GOVERNANCE_REGISTRY.yaml`, schema | pass/fail + errors | JSON Schema validation; required-field presence; enum conformance | Schema correctness is assumed | Schema lagging a legitimate new field | Semantically wrong but well-formed values | A |
| DA-02 | §4 ¶1 | all normative artifacts | per-artifact findings | Parse header; require status, scope, responsibility, authority_source, version; reject placeholders | Header parsing is format-dependent | Non-normative docs misclassified as normative | Requirement-bearing doc not recognised as normative | A |
| DA-03 | §4 ¶1 | Registry + artifact headers | mismatch list | Field-by-field comparison of identity, status, scope, responsibility, authority, jurisdiction | Text normalization needed | Formatting-only differences | Both sides wrong identically | A |
| DA-04 | §4 ¶2, §9 ¶1 | Registry, jurisdictions, types | collision list | See §3 | Scope precision | Shared vocabulary, disjoint reality | Semantically overlapping type names | A |
| DA-05 | §4 ¶1-2, §4 ¶5 | authority + delegation records | pass/fail | See §3 | Records only, not real approval | Mid-migration entries | Forged records without signing | A |
| DA-06 | §1, §4 ¶5, §11 ¶2 | Draft/Legacy/informative text | findings | Detect RFC-2119 caps in non-Active or informative sections | Section boundary detection | Quotations of Active requirements | Lowercase requirement prose | A |
| DA-07 | §1 ¶2, §8 ¶3, §5 ¶6 | all text outside `archive/` | findings | See §3 | Lexical only | Legitimate technical usage | Paraphrased precedence claims | A |
| DA-08 | §6 ¶4, §11 | all records and artifacts | broken-reference list | Resolve every internal link, path, and record id; fail on unresolvable | Cannot judge whether the target is the *intended* one | Intentional references to planned artifacts | Reference resolving to a wrong object of the right shape | A |
| DA-09 | O-1, §11 ¶3 | all records | duplicate/invalid ids | Grammar match; global uniqueness; retired-id reuse detection | — | — | Ids valid but semantically misassigned | A |
| DA-10 | §9, O-1 | record frontmatter | schema errors | Validate each record against its registered type schema; `extra=forbid` | Schema must track O-1 | Legitimate new field before schema update | Correct shape, wrong type declared | A |
| DA-11 | O-1 relationships | all records | invalid-edge list | Verify each relationship is a registered kind and endpoints are of permitted types and exist | — | — | Valid edge, wrong semantics | A |
| DA-12 | §9 ¶3 | transition records | missing-element list | Require all eight elements; fail closed on any absence | Presence, not correctness | Placeholder rationale accepted as present | Fabricated but complete records | A |
| DA-13 | §9 ¶1 | transition records + lifecycle defs | illegal-transition list | Build the state machine from the owning standard; verify every prior→new pair is permitted and the authority matches that transition | Requires machine-readable lifecycles | Lifecycle mid-amendment | Transition recorded as a legal one it wasn't | A |
| DA-14 | §7 ¶1 | `results/**`, transition digests | modified-Result list | See §3 | Needs external anchor | Encoding normalization | Rewritten digests | A |
| DA-15 | §8 ¶2 | git history, record stores | deletion list | Detect any deletion or rename-out of a scientific record path across history | Renames vs deletions | Legitimate migration with recorded mapping | Pre-first-run deletions | A |
| DA-16 | §8 ¶1 | `unknowns/**`, history | findings | Verify no Unknown is deleted; verify resolution did not remove the record or its history | — | — | Unknown never created | A |
| DA-17 | §6 ¶1 | `evidence/**` | missing-item list | See §3 | Sufficiency undecidable | Legitimate non-applicability | Wrong-but-present provenance | A |
| DA-18 | §5 ¶1, §2 *Falsifiable* | `claims/**`, `principles/**` | findings | Require ≥1 falsifying observation field; separately require a decision rule before labelling Falsifiable | Feasibility not assessable | — | Stated-but-infeasible falsifier | P |
| DA-19 | §5 ¶5 | `interpretations/**` | findings | See §3 | Judgement-bound | Exhausted space properly recorded | Strawman alternative | P |
| DA-20 | §2, §5 ¶3 | protocols, executions | ordering violations | See §3 | Timestamps forgeable | Re-execution attribution | Backdating; access without artifact | Adv |
| DA-21 | §2 *Confirmatory*, §5 ¶3 | protocols, analyses, Results | mislabel list | Verify any analysis whose fixed elements changed after registration is labelled exploratory; verify confirmatory analyses cite a protocol registered before access | Depends on element-change detection | Cosmetic protocol edits | Undisclosed element change | P |
| DA-22 | §2, §4 ¶2 | merge tree + diff | missing-element list | See §3 | Self-declared change class | Incidental governance-path edits | Misdeclared change class | A |
| DA-23 | §2, §13 ¶2 | attestations, git authorship | findings | Compare attesting identity against every author of the reviewed change; fail on identity | Identity aliasing | Shared account for distinct humans | Same human under two identities | A |
| DA-24 | §12 ¶1 | reviews, authorship | findings | Detect a review whose reviewer authored the reviewed content; verify it is not labelled independent | Aliasing | — | Undisclosed alias | A |
| DA-25 | §10 ¶5 | tree + full history | secret findings | Entropy and pattern scanning for credentials, keys, tokens; scan history, not only HEAD | Novel secret formats | Test fixtures resembling keys | Encoded or split secrets | A |
| DA-26 | §10 ¶5 | tree, ignore rules | findings | Detect generated, cached, runtime, or personal material under version control absent an explicit fixture requirement | Classification heuristics | Legitimate declared fixtures | Generated files indistinguishable from authored | A |
| DA-27 | §11 ¶3 | all artifacts vs §2 and O-1 | drift findings | Detect redefinition of a constitutional or peer-owned term; detect synonyms mapped to distinct types and identical names on distinct types | Semantic | Domain terms properly qualified | Silent semantic drift with unchanged wording | P |
| DA-28 | §4 ¶4 | all Active artifacts | conflict candidates | Detect same-subject requirements with opposing modality (MUST vs MUST NOT); detect jurisdictional conflicts from `DA-04`; detect numeric threshold disagreement on the same named quantity | Semantic contradiction is undecidable | Complementary requirements read as opposing | Contradictions expressed in different vocabulary | Adv |
| DA-29 | §12 ¶1 | check run records | findings | Verify every registered check reported a definite verdict; any absent, errored, skipped, or empty-target check reports `NOT_VERIFIED`; fail if any output claims pass without execution | — | — | Check reporting a hardcoded pass | A |
| DA-30 | §4 ¶5, §14 | Draft/Legacy/Superseded/Withdrawn artifacts | findings | Detect authority assertions, RFC-2119 requirements, or Registry references in non-Active artifacts | Section classification | Historical quotation | Implicit authority by convention | A |
| DA-31 | §2, §6 ¶2, §10 ¶5 | records referencing external artifacts | findings | Verify every external reference has a custody manifest with identity, provenance, and recovery procedure | — | — | Manifest present but stale | A |
| DA-32 | §10 ¶2 | `software/**` | findings | Detect stateful components lacking a Material state declaration; detect state depending on undocumented global, cache, service, env value, mutable default, clock, or random source | Static analysis limits | Immutable module constants flagged | State hidden behind indirection | P |
| DA-33 | design invariant | jurisdiction + dependency declarations | cycle list | Topological sort of the standard dependency graph; fail on any cycle | Declared edges only | — | Undeclared dependency | A |
| DA-34 | §10 ¶1, §3 | boundary declarations, reference graph | violations | See §3 | Static only | Historical citations | Runtime coupling | A |
| DA-35 | §10 ¶4 | `software/`, `validation/` | findings | Detect code shared between an assessor and the behaviour assessed; flag where validation imports the implementation under test rather than its interface | Interface vs implementation distinction | Shared pure utilities | Indirect sharing via a third module | P |
| DA-36 | §4 ¶4 | `governance/delegations/**` | findings | Require all five elements; reject any delegation missing one as void, not defective | — | — | Five elements present but vacuous | A |
| DA-37 | §4 ¶4 | delegation chains | containment violations | Verify each child delegation's transitions and scope are subsets of its parent's, transitively to the steward | Scope subset needs structured scopes | Free-text scope comparison failures | Semantic scope expansion | A |
| DA-38 | §13 ¶2 | attestations | missing-field list | Require reviewed revision, non-authorship declaration, Evidence-production declaration, conflict disclosure, procedure, conclusion, competence, records examined; require an identified human | — | Sparse but valid competence statements | Complete but untruthful attestation | A |
| DA-39 | §12 ¶1, §12 ¶4 | Active artifacts, check + MRP registers | coverage table | See §3 | Needs clause ids | "must" in examples | Non-RFC-2119 requirement prose | A |
| DA-40 | §12 ¶1 | non-applicability statements | findings | Verify each states a *testable* reason and names the condition under which it would become applicable | Testability is judgement-bound | Terse but valid reasons | Plausible untestable reasons | P |
| DA-41 | §3 ¶6, §12 ¶1 | `audit/**` | findings | Verify the audit's requirement basis resolves to an Active registered artifact and version; fail on implicit or derived bases | — | — | Correct citation, misapplied | A |
| DA-42 | §3 ¶6 | `audit/**` | findings | Detect requirement-creating sentences in audit reports | Lexical | Quoted requirements | Requirements implied by recommendation | P |
| DA-43 | §6 ¶2 | records with digests | findings | Verify the algorithm is registered in DG-7, non-deprecated, and versioned | — | — | Registered algorithm later broken | A |
| DA-44 | §2, §6 | custody manifests, external stores | degraded list | Scheduled re-computation of digests for retained artifacts; mark mismatches Degraded | Requires store access; cost scales with corpus | Transient access failures reported as degradation | Silent substitution with a matching digest (infeasible if collision-resistant) | A |
| DA-45 | §7 ¶1, §8 ¶2 | git history, protected paths | findings | See §3 | Needs external anchor | Legitimate migrations | Pre-baseline rewrites | A |
| DA-46 | §6 ¶1, §12 | release artifacts | findings | Verify every release artifact has a recorded digest and the digest matches; verify the release records its source revision | — | — | Correct digest of a wrong build | A |
| DA-47 | §12 ¶2 | containment records | findings | Verify a record exists within the declared window after each containment action | Depends on the action being reported at all | Clock skew at window boundary | Unreported containment | A |
| DA-48 | §12 ¶2 | containment records | findings | Verify no containment record authorizes a transition other than deferral of its own recording | — | — | Authorization implied rather than stated | A |
| DA-49 | §4 ¶4, §12 ¶2 | conflict records, transitions | blocking findings | Verify no transition depends on a requirement with an open conflict record | Dependency detection | Over-broad blocking | Conflict not recorded | A |
| DA-50 | §12 ¶3-4 | `CHECK_REGISTER.yaml` | findings | Verify every registered check declares all eleven registration fields including FP/FN; verify every check file is registered and vice versa | — | — | Disclosures present but understated | A |
| DA-51 | §4 ¶4 | check implementations and outputs | findings | Detect any check emitting approval, authorization, attestation, or acceptance language | Lexical | "approved" in quoted data | Approval implied by exit code semantics elsewhere | A |
| DA-52 | §2, §3 ¶6 | `decisions/**` | findings | Detect embedded Evidence or Interpretation content in a Decision rather than references | Distinguishing quotation from embedding | Brief context quotations | Paraphrased embedding | P |
| DA-53 | §4 ¶5 | Decisions, authority records | findings | Verify the approver is Registry-listed and permitted for that specific transition | Same limits as DA-05 | — | Forged approval | A |
| DA-54 | §2, §5 ¶5, §6 ¶5 | Questions, Interpretations, Evidence | findings | Verify each material Question has an Unknown referral; each alternative-free Interpretation has a search Unknown; each unretainable input has an Unknown or limitation | Materiality is declared, not derived | Over-escalation | Materiality understated | P |
| DA-55 | §5 ¶7 | `evidence/**`, `claims/**` | findings | Detect analogy, metaphor, mechanism name, model confidence, performance improvement, citation count, authority statement, or absence-of-alternative used as the sole support | Lexical | Legitimate discussion of an analogy | Sole support expressed indirectly | Adv |
| DA-56 | §5 ¶2 | `claims/**` referenced by inference | missing-field list | Require all eight fields for any Claim cited by an Interpretation, Decision, or Principle | Presence only | — | Fields present but vacuous | A |
| DA-57 | §2, §5 ¶2 | `hypotheses/**` | findings | Verify the paired Claim exists, is Active, and satisfies §5 ¶2; verify test and counting-against outcome present | — | — | Test present but non-discriminating | P |
| DA-58 | §7 ¶1 | `results/**` | findings | Verify each correction is a new linked Result identifying the error and superseded content; reject in-place correction | — | — | Correction recorded but content unchanged | A |
| DA-59 | §7 ¶1 | Results, Evidence, Interpretations | propagation findings | For each corrected or superseded Result, verify every dependent record discloses that status | Dependency graph completeness | — | Dependency via untracked reference | A |
| DA-60 | §7 ¶4 | Results, executions | advisory findings | See §3 | Statistical | Recorded abandonments | Never-recorded Negative Results | Adv |
| DA-61 | §3 ¶7, §2 | scientific records, test outputs | findings | See §3 | Recognition of test-derived assertions | Informative engineering status | Paraphrase | P |
| DA-62 | §7 ¶3 | Interpretations, inputs | findings | Compute the narrowest material limitation across inputs; compare to the Interpretation's declared scope; flag widening without stated justification | Requires structured scopes | Justified generalization flagged | Scope widened in prose only | P |
| DA-63 | §4 ¶4 | standards' delegation declarations | findings | Verify each claimed refinement cites a delegating clause and restates all five elements; flag reliance on the three under-specified delegations (DD-1) | — | — | Citation valid, refinement exceeds it | A |

---

## 5. What automation cannot do

Stated explicitly, because a check register invites the belief that it is sufficient.

**Not mechanically decidable, by nature:**
- whether Evidence was admitted or excluded because of its agreement with a preferred conclusion (§6 ¶3);
- whether an alternative explanation is genuinely the strongest materially distinct one (§5 ¶5);
- whether operational terms are sufficient for an Independent reviewer (§2, §5 ¶2);
- whether a mechanism claim is distinguishable from prediction (§5 ¶7);
- whether a Result was quietly not recorded;
- whether a reviewer's independence declaration is truthful;
- whether a scope is honestly drawn;
- whether two differently-named object types describe the same thing.

Every item above maps to a named manual review procedure in `06_VERIFICATION_ARCHITECTURE.md`, per §12 ¶4.

**Structurally undetectable from inside the repository:**
- backdated timestamps (`DA-20`);
- history rewriting prior to the first check run (`DA-14`, `DA-45`);
- forged authority or attestation records absent cryptographic signing (`DA-05`, `DA-38`);
- work performed and discarded outside version control (`DA-60`).

These four require *external* anchors: commit signing, platform branch protection with audit logs, an off-repository mirror, and third-party timestamping. Without them, a determined single actor can satisfy every check while violating the Constitution — which is the mechanical restatement of why §13 requires two humans, and why no amount of automation substitutes for that requirement.
