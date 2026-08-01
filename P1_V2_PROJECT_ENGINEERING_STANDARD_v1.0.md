# Project P1-v2 — Project Engineering Standard (PES) v1.0

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**

- **Artifact:** `P1_V2_PROJECT_ENGINEERING_STANDARD_v1.0.md`
- **Version:** 1.0.0
- **Kind:** Engineering process standard. **Non-normative with respect to every frozen specification.**
- **Scope:** How software engineering proceeds in Project P1-v2 **after** specification freeze.
- **Out of scope:** Specification content, architecture, scientific claims, admissibility, registration.
- **Status:** Proposed / Unregistered. **Authority source: none until registered.**
- **Date:** 2026-07-31
- **Operation:** PROJECT ENGINEERING STANDARD (PES) v1.0

---

## 0. Standing, jurisdiction, and precedence

### 0.1 What this document is

This document defines the **engineering process**. It answers *how work is done, reviewed, merged,
versioned, released and maintained*. It does not answer *what the software must do* — that question is
closed by the frozen artifacts below and is not reopened here.

This standard **adds no rule, field, default, API, invariant, acceptance criterion, observable, or
architecture** to any specification. Every process rule below is either (a) a procedure with no
specification content, or (b) a restatement of a frozen sentence with a citation.

### 0.2 Frozen and authoritative inputs — not modified by this document

| # | Artifact | Path | Version | Role in this standard |
|---|---|---|---|---|
| 1 | P1 Constitution (repository) | `REPOSITORY_CONSTITUTION.md` + `GOVERNANCE_REGISTRY.yaml` | 1.2.0 / schema 1.0 | Registration, authority boundaries, epistemic invariants |
| 2 | P1-v2 Constitution Lock | `P1_V2_CONSTITUTION_LOCK_v1.0.md` | 1.0.0 | Primitive ontology, lifecycle/event vocabulary, evidence boundary, generation gates |
| 3 | LSKE Specification | `P1_V2_LSKE_SPECIFICATION_v1.1.2.md` | 1.1.2 (frozen under R9-19) | The single normative source for LSKE behaviour |
| 4 | Phase 1 Implementation Authority Package | `outputs/P1_V2_PHASE1_IMPLEMENTATION_AUTHORITY_PACKAGE_v1.0.md` (+ Documents 1–6) | 1.0 | Conformance guide, checklist, traceability, latitude register, playbook, code review standard |
| 5 | Reference Implementation Design | `outputs/P1_V2_PHASE1_REFERENCE_IMPLEMENTATION_DESIGN_v1.0.md` | 1.0 | Reference construction of the frozen design |
| 6 | Production Implementation Roadmap | `outputs/P1_V2_PHASE1_PRODUCTION_IMPLEMENTATION_ROADMAP_v1.0.md` | 1.0 | Task register `T-01`…`T-33`, phase order, verification and exit conditions |

Items 1–6 are **read-only inputs**. No rule in this standard edits, weakens, reinterprets, or extends
them.

### 0.3 Precedence order (PES-0.1)

When two documents appear to disagree, the higher row governs and the lower row is **defective**:

1. `REPOSITORY_CONSTITUTION.md` and `GOVERNANCE_REGISTRY.yaml`
2. `P1_V2_CONSTITUTION_LOCK_v1.0.md`
3. `P1_V2_LSKE_SPECIFICATION_v1.1.2.md`
4. Phase 1 Implementation Authority Package, Documents 1–6
5. Reference Implementation Design; Production Implementation Roadmap
6. **This standard (PES v1.0)**
7. All other engineering documentation, playbooks, dashboards, and reports

An engineer who finds this standard in conflict with rows 1–5 **follows rows 1–5 and files a PES defect**
(§9.5). Resolving such a conflict by choosing is forbidden.

### 0.4 Standing condition (PES-0.2)

The LSKE specification remains **Proposed / Unregistered**; `GOVERNANCE_REGISTRY.yaml` records
`status: Draft` and `active_domain_standards: []`. Therefore:

- All P1-v2 engineering work is **engineering-only** and produces **no admissible scientific evidence**
  (R0-3, §9.12, Article L-11, Appendix J cl. 3).
- Every artifact produced under this standard **SHALL** carry the banner
  `GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE`.
- Building, testing, releasing, or benchmarking the LSKE **does not** raise Scientific Readiness and
  **may not be reported as** doing so.
- **This standard itself** acquires normative force only by registration in `GOVERNANCE_REGISTRY.yaml`
  under Section 13 of the Repository Constitution, or by explicit adoption by the Human release
  authority (§10). Its root-directory location grants it nothing.

### 0.5 Reading rules

`SHALL` / `SHALL NOT` = mandatory process obligation. `MAY` = released latitude. Every rule carries an
ID `PES-<part>.<n>`. A rule without a decidable check is not a rule; each rule below states either its
check or its enforcement point.

---

## PART 1 — Engineering Principles

Ten principles. They are **immutable**: they may be superseded only by a new PES major version adopted by
the Human release authority, never by a branch, a review, an urgency, or a convenience.

### P-01 Specification-first engineering

**Statement.** Code follows a frozen sentence. No implementation work begins on a behaviour that no
normative sentence requires.
**Consequence.** Every task traces to a rule (Document 3 reverse trace, `T-01`…`T-33`). A task with no
rule is not a task; it is a proposed amendment (§9).
**Check.** Every merged change cites at least one specification sentence or one latitude entry
`L-01`…`L-21`.

### P-02 Deterministic implementation

**Statement.** Identical inputs produce identical observable outputs and identical bytes.
**Consequence.** No clock, randomness, environment lookup, network access, dictionary-iteration
dependence, address-dependent ordering, or locale dependence on any path that produces an observable
(`RF-0.2`, §9.13.0).
**Check.** Two runs of the same test command on a clean checkout produce byte-identical generated schema
files, digests, and event log lines.

### P-03 Single source of truth

**Statement.** Every value, name, literal, and contract has exactly one definition site.
**Consequence.** `ONTOLOGY_VERSION` at one site (§9.13.2, `RF-04`); one owner per component (§9.13.1's
twelve-row ownership map); one definition per public callable (Appendix G.1).
**Check.** A grep for any governed literal returns exactly one defining occurrence.

### P-04 Observable behaviour over internal implementation

**Statement.** Conformance is judged on externally observable behaviour (`O-01`…`O-15`), never on interior
construction.
**Consequence.** Helpers, private algorithms, data structures, optimisation strategy, dependency
selection, and private module organisation are latitude (R9-19 cl. 3).
**Check.** Every review finding names an observable or cites a normative sentence directly (§5).

### P-05 Reproducibility

**Statement.** Any result an engineer reports SHALL be re-derivable by another engineer from a clean
checkout with a recorded command.
**Consequence.** Evidence is a command plus its output, not a claim. Determinism tiers `D0/D1/D2` are
recorded, never assumed (Constitution Lock R1).
**Check.** Every evidence artifact names the command that produced it.

### P-06 Minimal public surface

**Statement.** The public surface is exactly what the specification names — no more, and no less.
**Consequence.** Required **absences** are as binding as required presences (e.g. no `ONTOLOGY_VERSION`
export from `v2.lske`, `RF-04` cl. 2). Adding a convenience export is a defect, not a courtesy.
**Check.** Two-way set diff of the enumerated public surface against §9.13 is empty in both directions
(Document 6 §2.3).

### P-07 Fail-closed design

**Statement.** On any condition the specification does not admit, the code refuses rather than proceeds.
**Consequence.** No silent coercion, no default substitution for an invalid input, no partial write, no
swallowed exception, no "best effort" path. Refusal is by the §9.5 taxonomy only.
**Check.** No `except` clause discards an exception without re-raising a taxonomy class; no code path
returns a degraded value where a raise is specified.

### P-08 Explicit ownership

**Statement.** Every file, module, component, version number, and gate has exactly one named owner.
**Consequence.** Ownership tables in Part 2 and Part 8 are authoritative for process. Unowned artifacts
are deleted or assigned; they are not tolerated.
**Check.** Every path in the P1-v2 tree matches exactly one row of the Part 2 ownership table.

### P-09 Backward compatibility policy

**Statement.** Within a frozen specification version, the public surface is **append-only under
specification authority and immutable under engineering authority**.
**Consequence.** Engineering may never rename, remove, re-sign, or re-type a public surface element.
Public surface change is a specification act (§9). Private surface carries **no** compatibility promise
and may change freely in any commit.
**Check.** A public-surface diff on any engineering branch is empty unless the branch implements a named
specification amendment.

### P-10 Engineering discipline

**Statement.** The process is followed when it is inconvenient. Schedule pressure is not a defence, an
exception, or a finding class.
**Consequence.** No merge without evidence; no green-by-suppression; no disabled test; no unpinned
dependency; no undocumented deviation; no self-approval.
**Check.** Merge blockers (§3.5) are never waived silently; a waiver requires a Human decision recorded
in the merge record.

**PES-1.1** — Principles P-01…P-10 SHALL be cited by ID when a review, a debt entry, or a revert invokes
them. An appeal to an unnamed principle is not admissible.

---

## PART 2 — Repository Governance

### 2.1 Directory ownership (PES-2.1)

| Path | Owner role | Write authority | Constraint |
|---|---|---|---|
| `v2/`, `v2/lske/` | Implementation engineer | GPT role, human-approved merge | Layout closed by §9.1; no file outside the closed layout |
| `schemas/lske/` | Generated artifact | Test 1 regeneration only | 23 files; bytes are an observable; hand-editing is a defect |
| `tests/lske/` | Implementation engineer | GPT role | Rows 1–3 in Phase 1; row set is 23 and is not renamed or extended |
| `outputs/` | Governance/authority packages | Specification authority | Non-normative deliverables; DRAFT banner mandatory |
| Root `P1_V2_*.md` | Specification authority | Human adoption | Frozen artifacts are read-only |
| `GOVERNANCE_REGISTRY.yaml`, `REPOSITORY_CONSTITUTION.md` | Constitutional steward | Human only | Registration acts only |
| `ros/`, `core/`, `framework/`, `science/`, `experiments/`, `p1/tooling/` | Inherited M1/ROS platform | Existing platform owners | **Out of scope for Phase 1**; any change in a Phase 1 branch is a blocking defect (§9.8 stage 1) |
| `evidence/`, `audits/` | Evidence recorder | Append-only in practice | Records, never re-written to match a later belief |
| `archive/` | Frozen vault | No writes | Historical material; never a citation source for current behaviour |

**PES-2.2** — A path not covered by a row above SHALL NOT receive P1-v2 implementation code. If P1-v2 code
appears to require a new location, that is a specification question (§9), not an engineering choice.

### 2.2 Module ownership (PES-2.3)

- The specification's §9.13.1 ownership map (twelve rows) is the authority for **component → owning
  module**. This standard adds no row and moves no component.
- Modules are addressed in engineering by their Document 2 identifiers `MOD-01`…`MOD-09` and the
  `schema.py` components `C-01`…`C-06`.
- **PES-2.4** — No component appears in two modules. A helper needed by two modules is either duplicated
  privately or lives in the module that owns the contract — never in a new shared module invented by an
  engineer.

### 2.3 Package boundaries (PES-2.5)

| Boundary | Rule | Citation |
|---|---|---|
| Purity | `v2.lske.schema` performs no I/O, no clock read, no environment read, no randomness, no network | §9.13.0 |
| Dependency direction | No `v2.lske.*` module imports from the runtime tree (`ros/*`, `core/*`, …) | §9.13.0, §9.13.7 |
| Position | `v2.lske` sits at the bottom of the LSKE dependency order | §9.13.7 |
| Stage boundary | Phase 1 touches stage-1 files only; no reader in `events.py`, no `ros.model` alignment, no transaction phase | §9.8 stage 1, §9.13.8 cl. 1 |
| Observatory boundary | `obs2` node/edge/overlay interiors are Observatory-owned; the LSKE does not type them | §9.2.4 note 3, R7-2 |

### 2.4 Import rules (PES-2.6)

1. Import graph within `v2/` SHALL be acyclic. A cycle is a blocking defect.
2. `errors.py` imports nothing from `v2.lske`. `schema.py` may import `errors`. `events.py` may import
   `errors` and `schema`. No reverse edge exists.
3. Third-party imports are permitted only where a latitude entry admits them (`L-01`-class: the Draft
   2020-12 validator, §0Y.2 / `IMP-BLK-01`).
4. `import *` is forbidden anywhere in `v2/`.
5. Conditional, deferred, or in-function imports are forbidden in `v2/lske/` except where required to
   break a *documented* third-party import cost; the reason SHALL be a comment citing this rule.
6. Test modules may import only the public surface plus `pytest`; a test that imports a private helper to
   assert on it is a **test defect** (§5).

### 2.5 Public vs private APIs (PES-2.7)

- **Public** = named in §9.13 (and the §9.5 taxonomy) **and** exported by `__all__`. Nothing else is
  public, regardless of name.
- **Private** = a leading underscore. Private names carry no stability promise, appear in no `__all__`,
  are asserted on by no test, and are freely renamed (R9-19 cl. 3, §9.9 item 1).
- **PES-2.8** — Making a private name public is a specification act. Making a public name private is a
  defect. Re-exporting a private name through a public module is a defect.
- **PES-2.9** — A public callable SHALL NOT return an object whose type is private. Observable types are
  part of the surface.

### 2.6 Naming conventions (PES-2.10)

| Element | Convention | Authority |
|---|---|---|
| Public callables, parameters, return annotations | **Exactly** as §9.13 writes them, character for character | Specification |
| Public classes | Exactly as §9.13 / §9.5 write them | Specification |
| Private functions/variables | `_lower_snake_case` | Latitude — style only |
| Modules | `lower_snake_case`, and only the filenames §9.1 lists | Specification |
| Test functions | `test_<criterion-or-clause>` with the `AC-P1-nn` or row/clause id in the name or docstring | This standard |
| Branches | `<class>/<id>-<slug>` (§3.1) | This standard |
| Debt entries | `TD-nn` (§7.1) | This standard |
| Findings | `F-nn` (§5.4) | Document 6 §4.3 |

A review comment about **private** naming style is out of order (Document 6 §3 item 4).

### 2.7 File creation policy (PES-2.11)

A new file may be created only if one of the following holds, and the merge record states which:

1. §9.1 lists it and it does not yet exist.
2. It is a test file the §9.6 matrix names.
3. It is a generated schema file produced by test 1's regeneration path.
4. It is an evidence, review-record, or debt artifact required by this standard.

**PES-2.12** — Creating any other file inside `v2/`, `schemas/lske/`, or `tests/lske/` is a **blocking
defect**: the layout is closed. "Helper module", "utils", "constants", "types", and "compat" files are
forbidden by construction.

### 2.8 File deletion policy (PES-2.13)

1. No frozen artifact (row 1–6 of §0.2) is ever deleted, renamed, or edited.
2. No file §9.1 lists is ever deleted.
3. Deleting a test, an assertion, or a clause is forbidden. Where a clause belongs to a later stage, it is
   **skipped by an explicit stage marker**, never removed (Document 6 §5 item 10).
4. Superseded material is **archived**, not deleted, and the archive record names what superseded it.
5. Any deletion outside cases 3–4 requires Human approval recorded in the merge record.
6. History rewriting (`push --force`, `reset --hard` on a shared branch, `filter-branch`) is forbidden
   (§3.6).

---

## PART 3 — Branching & Merge Policy

### 3.1 Feature branch rules (PES-3.1)

| Class | Prefix | Contents |
|---|---|---|
| Specification-derived task | `task/T-nn-<slug>` | Exactly one roadmap task `T-01`…`T-33` |
| Playbook step | `step/S-nn-<slug>` | Exactly one playbook step `S-01`…`S-18` |
| Defect fix | `fix/F-nn-<slug>` | Exactly one accepted finding |
| Behaviour-preserving refactor | `refactor/<slug>` | No public-surface change, no observable change |
| Test-only work | `test/<slug>` | No production file changed |
| Documentation | `docs/<slug>` | No code file changed |
| Change request | `cr/<id>-<slug>` | A specification amendment proposal; **no implementation** |

Rules:

1. `main` is protected. No direct push. Every change arrives by pull request.
2. One branch = one task, step, or finding. Mixed-purpose branches are rejected without review.
3. A branch SHALL NOT change files outside the scope its class permits.
4. A branch SHALL NOT bump any version number unless it is a version branch (§8.6).
5. A branch that discovers a second problem files it; it does not fix it in place.
6. Branches are rebased or merged forward from `main`; `main` is never rewritten to suit a branch.

### 3.2 Merge requirements (PES-3.2)

All of the following, with no exceptions and no partial credit:

| # | Requirement | Verification |
|---|---|---|
| 1 | Scope check passes | Changed files ⊆ the branch class's permitted set (Document 6 §4.2 step 1) |
| 2 | Public surface diff empty in both directions | Programmatic enumeration vs §9.13 (Document 6 §2.3) |
| 3 | Signature diff empty | Parameter names, order, and return annotations vs §9.13 |
| 4 | All in-scope acceptance criteria evidenced | Document 3 rows; stage 1 requires all **27** |
| 5 | §9.6 clause coverage complete for in-scope rows | Clause-by-clause checklist |
| 6 | Determinism check passes | Repeated run produces byte-identical generated artifacts |
| 7 | CI green with no suppressed exit code | `lint`, `test`, `reproducibility`, `experiment-validation`, `benchmark`, `kill-criteria`, `research-os`, `artifact-integrity` (`.github/workflows/ci.yml`) |
| 8 | Release-gate job green where the branch touches released surface | `P1 Release Gate` (`.github/workflows/p1-release.yml`) |
| 9 | Review record complete and attached | Document 6 §6 template |
| 10 | Governance posture check passes | DRAFT banner present; no admissibility claim (Document 6 §2.6) |
| 11 | No open finding of a blocking category | §5.3 |
| 12 | Human approval where §10 requires it | Named approver in the merge record |

**PES-3.3** — A merge that satisfies 1–12 SHALL be merged. Approval may not be withheld for a latitude
item, a style preference, a dependency choice, an optimisation, or an absent feature the specification
does not require (Document 6 §4.4). Withholding on those grounds is itself a process defect.

### 3.3 Code review requirements (PES-3.4)

1. Every pull request receives **at least one conformance review** by the reviewer role (§10), and the
   reviewer is never the author.
2. The review follows Document 6 §4.2's ten-step sequence in order.
3. Every finding is classified under §5's six categories and carries the §5.4 fields.
4. A finding claiming a specification gap without the R9-19 cl. 2 two-implementation demonstration is
   **out of order** and is closed as such; closing it is the rule being applied, not a concession.
5. Reviews of architecture, of a version bump, or of a release require **Human** approval in addition.
6. Self-merge is forbidden, including for documentation branches.

### 3.4 Required evidence (PES-3.5)

Attached to the merge record, each item naming the command that produced it:

| Evidence | Form |
|---|---|
| Test transcript | Full `pytest` output for the in-scope rows, exit code visible |
| Criterion table | One row per in-scope `AC-P1-nn`: criterion, test, result, artifact |
| Observable ledger | One line per in-scope `O-nn`: confirmed / defect / not exercised |
| Surface diff | Both set differences, both empty |
| Determinism transcript | Two runs, byte comparison or digest equality |
| Generated-artifact digests | Digest per generated schema file |
| Review record | Document 6 §6 template, fully filled |
| Debt entries opened/closed | `TD-nn` ids |

**PES-3.6** — Evidence is the output of a command, not a summary of it. A claim without a transcript is
not evidence and does not satisfy a gate.

### 3.5 Merge blockers (PES-3.7)

Any one of these blocks the merge:

1. A file changed outside the branch class's permitted scope; in particular, any `ros/*` change in a
   Phase 1 branch.
2. A public surface difference in either direction, including a missing required absence.
3. A signature, parameter name, parameter order, or return annotation difference.
4. A file created inside a closed layout, or a listed file missing.
5. An unmet in-scope acceptance criterion, or one asserted without an artifact.
6. A §9.6 clause absent, weakened, reworded, deleted, or satisfied by a mock.
7. A test skipped without an explicit stage marker, or an `xfail` added to pass a gate.
8. A raise site escaping the §9.5 taxonomy; an exception message carrying a measured value (R9-9); an
   `args` length other than one (§9.5.1 cl. 1).
9. Non-determinism on an observable path: clock, randomness, environment, network, iteration-order
   dependence, or caching where `RF-03` cl. 6 forbids it.
10. A new dependency without a §4.3 record and an exact pin.
11. A hand-edited generated schema file.
12. A version number changed outside a version branch, or `ONTOLOGY_VERSION` changed by engineering.
13. Any suppressed failure: `|| true`, `continue-on-error` added to a mandatory job, a broadened
    `filterwarnings`, a lowered assertion, or a deleted check.
14. A missing DRAFT banner, or any claim of admissibility, registration, or raised Scientific Readiness.
15. An open finding of category **Specification violation**, **Implementation bug**, or **Test defect**.
16. A missing review record, or a review record whose author and reviewer are the same person or role.

**PES-3.8** — Blockers 1–16 are not waivable by an engineer or a reviewer. Only the Human release
authority may record a waiver, and only with a named expiry and a `TD-nn` entry.

### 3.6 Revert policy (PES-3.9)

1. **Revert first, diagnose second.** If `main` fails a mandatory gate, the offending merge is reverted
   before any forward fix is attempted.
2. Reverts are performed with a new commit (`git revert`). History is never rewritten. `push --force` to
   `main`, `reset --hard` on a shared branch, and `git clean -f` on a shared checkout are forbidden.
3. A revert requires no review beyond the gate transcript that justifies it; **restoring** the reverted
   change does require a full review.
4. Every revert opens a finding (§5) recording the category, the missed gate, and the gate hardening that
   would have caught it earlier.
5. A revert of a version bump or a release requires Human authority (§10).
6. A change reverted twice for the same root cause SHALL NOT be re-attempted incrementally; it returns to
   the roadmap as a re-planned task.

---

## PART 4 — Implementation Rules

### 4.1 Public API additions (PES-4.1)

1. Engineering **SHALL NOT** add, remove, rename, re-sign, re-type, or re-export a public API element.
2. A public element exists only where §9.13 or §9.5 names it; its definition site is unique (Appendix
   G.1); it appears in exactly one `__all__`.
3. A perceived need for a new public element is a **specification amendment request** (§9) and requires
   the R9-19 cl. 2 demonstration.
4. Required absences are implemented as absences and asserted as absences.
5. Convenience aliases, deprecation shims, `__getattr__` fallbacks, and dynamic surface construction are
   forbidden in `v2/lske/`.

### 4.2 Internal helpers (PES-4.2)

1. Helpers are latitude: their existence, count, names, signatures, and algorithms are the implementer's
   choice (R9-19 cl. 3, §9.9 item 1).
2. A helper SHALL NOT hold module-level mutable state, memoise a value the specification requires to be
   freshly constructed (`RF-03` cl. 6), or perform I/O inside a pure module.
3. A helper SHALL NOT be the sole carrier of an observable: every observable is reachable and asserted
   through the public surface.
4. Helpers are not tested directly; they are exercised through public behaviour.
5. A helper's complexity is not a review subject unless it produces a wrong observable.

### 4.3 Dependency introduction (PES-4.3)

A new third-party dependency requires **all** of:

| # | Condition |
|---|---|
| 1 | A latitude entry or normative sentence admits a dependency for that purpose |
| 2 | An **exact pin** (`==`) in the manifest; ranges, `>=`, and unpinned extras are forbidden |
| 3 | A recorded license compatible with the project license (MIT) |
| 4 | Evidence of active maintenance and a name check against typosquatting variants |
| 5 | A statement that it introduces no non-determinism, no network access at import, and no clock/locale dependence on an observable path |
| 6 | Human approval, because a dependency is a supply-chain decision |

Rules: no dependency is added to satisfy a style preference; **dependency selection is latitude, so a
review may not request a different library** (Document 6 §3 item 6) — but it may report a wrong observable
the library causes. Test-only dependencies follow the same six conditions.

### 4.4 Schema evolution (PES-4.4)

1. The 23 `schemas/lske/*.json` files are **generated**. Their bytes are an observable. Hand-editing is a
   blocking defect.
2. Test 1 writes the expected file and fails in the same run on divergence or absence; that property is
   never weakened.
3. `ONTOLOGY_VERSION` has one literal at one site and its value is owned by the specification (`RF-04`
   cl. 1–2). Engineering never changes it.
4. Any change to a schema's content is a **specification act**. The engineering-visible consequence is
   regeneration and a byte-diff record, never an edit.
5. Adding a collection, relation type, dimension, dimension state, lifecycle state, event kind, or schema
   file is forbidden to engineering (Appendix H cl. 1).
6. No migration mechanism exists in Phase 1 and none may be invented (§9.8 stage 1). Migration is
   introduced by the specification at the stage that requires it (§8.5).

### 4.5 Error handling (PES-4.5)

1. Every raise site uses the §9.5 seven-class taxonomy. A raise escaping the taxonomy is a blocking
   defect.
2. `exc.args` has length exactly one (§9.5.1 cl. 1).
3. Exception messages carry no measured value (R9-9). Message prose is style and is not a review subject.
4. `SchemaViolation.failures` content and order follow §9.13.3 and `RF-01`/`RF-02`: no applicator
   keywords; `derived` true only under the stated predicate; failures ordered with the specified tie-break;
   derived findings last.
5. Fail-closed: no bare `except`, no `except Exception: pass`, no coercion of an invalid input to a valid
   one, no partial write, no degraded return where a raise is specified.
6. Validation reports **all** failures where the specification requires it; short-circuiting a required
   report is a defect.

### 4.6 Logging (PES-4.6)

1. The only durable write path in Phase 1 is `append_event` (§9.13.8). Nothing else writes.
2. `append_event` appends exactly one line and leaves previously written bytes untouched (§9.13.8
   cl. 5–6).
3. `print` is forbidden in `v2/lske/`. Diagnostic logging is forbidden in the pure module.
4. No log line contains a secret, a credential, a token, an absolute developer path, a hostname, or a
   wall-clock value that is not specified.
5. Log bytes and line counts are observables; a log format change is a specification act.
6. Test output is not a log; a test SHALL NOT write into a real store or a repository-tracked path.

### 4.7 Serialization (PES-4.7)

1. Canonical serialisation is `canonical_json`; hashing is `content_hash`; sealing is `seal`
   (§9.13.5–§9.13.6). No alternative serialiser or hash is introduced (Document 6 §3 item 3).
2. Bytes are UTF-8; newlines are LF; key order is the specified order, never insertion order or a
   locale-dependent sort.
3. `pickle`, `marshal`, `eval`, and Python-repr round-trips are forbidden for any persisted or hashed
   value.
4. Float formatting, integer widths, and `None` encoding follow the specification exactly; no
   platform-dependent formatting reaches a digest.
5. Pre-seal and post-seal records compare unequal while sharing one `content_hash` (§9.13.4 cl. 4–5);
   this pair of properties is asserted, not assumed.

### 4.8 Determinism (PES-4.8)

1. No clock, random source, network call, environment lookup, process id, memory address, or thread
   scheduling result influences an observable (`RF-0.2`, §9.13.0).
2. Every iteration over a mapping or set that reaches an observable is explicitly ordered.
3. Where the specification states case order, the case order is part of the rule and is implemented in
   that order.
4. Concurrency is not introduced in Phase 1. Parallelism that could reorder an observable is forbidden.
5. Determinism tier claims (`D0`/`D1`/`D2`) are recorded from evidence, never asserted; a `D2` result is
   never presented as decision-relevant (Constitution Lock R1).
6. A determinism failure is a **blocking** defect regardless of how rarely it reproduces.

### 4.9 Performance changes (PES-4.9)

1. A performance change SHALL NOT change any observable. If it does, it is a behaviour change and needs a
   specification basis.
2. No Phase 1 acceptance criterion asserts a performance bound; therefore performance is **not** a merge
   gate and an optimisation request is out of order as a blocker (Document 6 §3 item 7).
3. Caching, laziness, and copy elimination are forbidden where the specification requires fresh objects
   or distinct identity (`RF-03` cl. 6).
4. A performance change merges only with a before/after measurement produced by a recorded command on the
   same machine, plus a full green gate set.
5. Performance work is a separate branch class (`refactor/`) and is never bundled with a behaviour task.
6. A performance problem that cannot be fixed within latitude is recorded as debt (`TD-nn`), never as a
   specification gap.

---

## PART 5 — Review Standards

### 5.1 The six categories — and no others (PES-5.1)

Every review finding SHALL be classified as **exactly one** of the following six. **No other category is
permitted**, and an unclassifiable comment is not a finding.

| Category | Definition | Admissibility condition | Blocking |
|---|---|---|---|
| **C1 Specification violation** | The implementation contradicts a normative sentence, or fails an acceptance criterion | Cites the sentence by section/clause **and** file:line | **Yes** |
| **C2 Implementation bug** | The code is wrong on its own terms — crash, wrong result, unreachable path, resource leak — while a normative sentence or observable is at stake | Cites the failing input, the actual result, and the expected observable | **Yes** |
| **C3 Test defect** | A test is missing a §9.6 clause, asserts the wrong subject, is satisfied by a mock, is skipped without a stage marker, asserts on a private name, or passes for the wrong reason | Names the row and clause, or the criterion `AC-P1-nn` | **Yes** |
| **C4 Documentation defect** | A docstring, comment, README line, or record misstates observable behaviour, a citation, a version, or the governance posture | Names the false statement and the true one, with citation | **No**, unless it misstates governance posture or a public contract |
| **C5 Performance issue** | A measured cost that either violates a normative bound or produces a wrong observable | Requires a measurement **and** a normative bound or a named wrong observable | **No** in Phase 1 (no bound exists), unless it is really C1/C2 |
| **C6 Implementation latitude** | The subject is released to the implementer: private helpers, naming style, internal structures, dependency selection, optimisation strategy, private module organisation | Cite the releasing rule (§9.9, `L-01`…`L-21`, R9-19 cl. 3) | **No** — recorded and closed |

### 5.2 Reconciliation with the frozen review rules (PES-5.2)

The Phase 1 Code Review Standard (Document 6 §4.3) names the classes *Specification non-conformance*,
*Implementation defect*, *Implementation bug*, *Out-of-order (closed)*, and R9-19 cl. 1 limits reviews to
implementation defects, specification non-conformance, and implementation bugs. The six categories are a
**partition of those classes, not an extension of them**:

| PES category | Maps to | Basis |
|---|---|---|
| C1 Specification violation | Specification non-conformance | R9-19 cl. 1 |
| C2 Implementation bug | Implementation bug | R9-19 cl. 1 |
| C3 Test defect | Implementation defect, confined to test code | R9-19 cl. 1; §9.6 |
| C4 Documentation defect | Implementation defect, confined to prose | R9-19 cl. 1; never a specification request (cl. 2) |
| C5 Performance issue | Implementation defect **only** when it carries a wrong observable; otherwise latitude | R9-19 cl. 3 |
| C6 Implementation latitude | Out-of-order (closed) | R9-19 cl. 2–3 |

**No category creates a new requirement.** C4 may never request specification detail. C5 may never
request an optimisation. C6 is a disposition, not a demand. If this mapping ever appears to widen R9-19,
R9-19 governs and this section is defective (§0.3).

### 5.3 Blocking rule (PES-5.3)

- Open **C1**, **C2**, or **C3** ⇒ **Request changes**; the merge is blocked (§3.5 item 15).
- **C4** blocks only where it misstates governance posture or a public contract; otherwise it is fixed in
  the same or a following `docs/` branch.
- **C5** and **C6** never block. They are recorded, dispositioned, and closed.
- A finding showing that two normative sentences contradict, or that no implementation can satisfy a
  sentence, is **Blocked — escalate under R9-0**. The reviewer does **not** choose; a Constitutional
  Change Request is raised (Document 6 §4.4).

### 5.4 Finding format (PES-5.4)

```
ID:            F-nn
Category:      C1 Specification violation | C2 Implementation bug | C3 Test defect
               | C4 Documentation defect | C5 Performance issue | C6 Implementation latitude
Class (Doc 6): Specification non-conformance | Implementation defect | Implementation bug
               | Out-of-order (closed)
Observable:    O-nn, or "none — non-observable" (which makes the finding out of order unless it
               cites a normative sentence directly)
Citation:      the normative sentence, by section and clause; or the releasing latitude entry
Evidence:      file:line plus the failing assertion, command output, or byte comparison
Disposition:   Fix required | Fixed | Closed as latitude | Escalated under R9-0
```

For any finding that claims a specification gap, the sixth field is **mandatory** (R9-19 cl. 2):

```
Demonstration: implementation A and implementation B, each satisfying every normative sentence,
               differing in observable O-nn — stated concretely, not asserted
```

A finding missing a required field is **malformed** and is returned, not debated.

### 5.5 Reviewer conduct (PES-5.5)

1. The reviewer's authority is the specification's authority and no more.
2. A review states findings; it does not choose between admissible implementations.
3. Counting findings is not a quality measure; an out-of-order finding is a **process defect against the
   reviewer**, and its rate is a KPI (§12 `K-09`).
4. Every review ends with exactly one verdict: **Approve**, **Request changes**, or **Blocked — escalate
   under R9-0**.

---

## PART 6 — Regression Policy

### 6.1 Regression, defined (PES-6.1)

A **regression** is any of the following occurring without a specification amendment that requires it:

1. A previously passing test fails, is weakened, is deleted, is skipped, or is marked `xfail`.
2. An observable `O-01`…`O-15` changes value, type, identity relation, order, or mutability.
3. A previously satisfied acceptance criterion `AC-P1-nn` ceases to be satisfied or loses its artifact.
4. A generated artifact's bytes or digest change.
5. The public surface diff becomes non-empty in either direction.
6. A mandatory CI job that was green becomes red, flaky, or suppressed.
7. A determinism property that held stops holding, including intermittently.
8. Governance posture degrades: a banner disappears, or a claim overstates admissibility.

**PES-6.2** — Flakiness is a regression. An intermittent failure is treated as a failure, never retried
into green.

### 6.2 Required tests (PES-6.3)

| Change type | Minimum required tests |
|---|---|
| New stage-1 module or component | The §9.6 rows covering it, all clauses, plus every `AC-P1-nn` mapped to it in Document 3 |
| Defect fix (C1/C2) | A test that fails before the fix and passes after, asserting the **observable**, not the internals |
| Test defect fix (C3) | The corrected clause, plus proof the test now fails against the pre-fix code |
| Refactor | No new test; the full in-scope suite plus an empty surface diff and byte-identical artifacts |
| Dependency change | Full in-scope suite plus the determinism transcript |
| Schema regeneration | Test 1, including its write-and-fail-in-the-same-run behaviour |
| Documentation | No code test; citation check |

**PES-6.4** — A fix without a test that reproduces the defect is not a fix. **PES-6.5** — No required test
is satisfiable by a mock (§9.6: each row requires a constructed store).

### 6.3 Acceptance gates (PES-6.6)

| Gate | Condition | Owner |
|---|---|---|
| **G-task** | The task's `AC-P1-nn` rows evidenced; scope, surface, and signature diffs clean | Reviewer |
| **G-step** | The playbook step's exit conditions met (`S-01`…`S-18`) | Reviewer |
| **G-stage** | **All 27** acceptance criteria hold, with artifacts; the ten-gate stage-1 exit satisfied; test rows 1–3 clause-complete; stage-2 clause skipped by marker | Reviewer + Human |
| **G-boundary** | No file outside the stage boundary changed across the whole stage | Reviewer |

A stage is complete **when and only when** every criterion holds (Appendix D.1). Partial stage completion
is not a state and is never reported as one.

### 6.4 Release gates (PES-6.7)

| # | Gate |
|---|---|
| 1 | `G-stage` satisfied for every stage in the release |
| 2 | Every mandatory CI job green on the release commit, no suppression |
| 3 | `P1 Release Gate` workflow green, with pip-freeze, test transcript, and build output recorded |
| 4 | Build reproducible: two builds from the clean release commit produce identical declared artifacts |
| 5 | Version numbers consistent across all owning sites (§8) |
| 6 | Zero open C1, C2, or C3 findings |
| 7 | Debt register reviewed; no forbidden debt present; every open `TD-nn` has an owner and exit condition |
| 8 | Governance posture verified: DRAFT banner on every artifact; no admissibility, registration, or Scientific Readiness claim |
| 9 | Human release authority approval recorded |

### 6.5 Evidence requirements (PES-6.8)

1. Evidence is a **command plus its output**, stored under `evidence/`, naming the commit and the
   environment.
2. Evidence is append-only. A superseded record is annotated, never overwritten.
3. Absence of evidence is reported as absence — never as a pass (an unassessed criterion is not a
   satisfied criterion).
4. Every release carries a complete evidence bundle: transcripts, criterion tables, digests, surface
   diffs, review records, debt register snapshot.
5. No evidence produced under the standing condition (§0.4) is scientific evidence, and no bundle may
   imply otherwise.

---

## PART 7 — Technical Debt Policy

### 7.1 Acceptable debt (PES-7.1)

Debt is acceptable only when **all** hold, and it is recorded as `TD-nn` with owner, opened date, exit
condition, and expiry:

1. It is invisible from the public surface and changes no observable.
2. It violates no normative sentence.
3. It is bounded: a named file set, a named cost, a named consequence.
4. It has a written exit condition that a later engineer can execute without new decisions.
5. It has an owner and a review date.

Typical acceptable debt: an inelegant private helper, a slow but correct path with no bound to violate, a
duplicated private constant, an incomplete internal docstring, a manual verification step awaiting
automation.

### 7.2 Forbidden debt (PES-7.2)

Never acceptable, at any deadline, in any branch:

1. A known specification non-conformance left in `main`.
2. A disabled, deleted, weakened, or unmarked-skipped test.
3. A suppressed failure: `|| true`, `continue-on-error` on a mandatory job, a swallowed exception, a
   broadened warning filter.
4. Non-determinism on an observable path.
5. An undeclared or unpinned dependency.
6. A hand-edited generated artifact.
7. A public surface deviation, including an extra export.
8. A `TODO`/`FIXME`/`HACK` without a `TD-nn` id and an owner.
9. Dead code reachable from the public surface.
10. An artifact missing the governance banner, or a claim that overstates admissibility.
11. A mock standing in for a construction the specification requires.
12. A private-surface secret: a hardcoded credential, token, or absolute developer path.

**PES-7.3** — Forbidden debt is not negotiated down to acceptable debt. It is fixed or reverted.

### 7.3 Refactoring rules (PES-7.4)

1. A refactor changes no observable and no public surface. It proves this with an empty two-way surface
   diff and byte-identical generated artifacts.
2. A refactor adds no test and deletes no test. Any test change makes it not a refactor.
3. Refactor and behaviour change are never in the same branch or commit.
4. A refactor requires the full in-scope gate set; "it's only internal" is not a gate exemption.
5. A refactor may not be requested by a review as a condition of approval (Document 6 §3 items 4–5).
6. A refactor that turns out to change an observable is reverted, then re-planned as a specification
   question.

### 7.4 Cleanup policy (PES-7.5)

1. Cleanup is scheduled work with its own branch class, not opportunistic edits inside a task branch.
2. Every stage exit includes a cleanup pass: dead private code removed, `TD-nn` register reconciled,
   temporary verification files deleted, stale comments corrected.
3. Temporary files created during verification are removed before merge; the repository is left clean.
4. Cleanup never deletes a test, an assertion, a record, or a frozen artifact (§2.8).
5. Debt past its expiry is escalated to the Human authority, which either schedules it or re-approves it
   with a new expiry — silence is not a renewal.

### 7.5 Deprecation policy (PES-7.6)

1. **Public surface deprecation is a specification act.** Engineering may not deprecate, shim, alias, or
   soft-remove a public element (§9).
2. Private elements are removed outright when unused; no deprecation period, no shim, no
   `DeprecationWarning`.
3. No compatibility layer is introduced in `v2/lske/`; the specification's surface is the only surface.
4. A deprecation, once specified, is implemented exactly as specified — the implementation invents no
   grace period.
5. Superseded engineering documents are marked superseded, dated, and pointed at their replacement; they
   are archived, never deleted.

---

## PART 8 — Versioning Policy

### 8.1 The five version kinds and their owners (PES-8.1)

| Kind | Single site | Current | Owner (may change it) | Bump rule |
|---|---|---|---|---|
| **Specification version** | Artifact filename + document header (`P1_V2_LSKE_SPECIFICATION_v1.1.2.md`) | 1.1.2 | Specification authority proposes; **Human** adopts | Only by an amendment under R9-0/R9-12 with the R9-19 cl. 2 basis. A new version is a new file; frozen files are never edited |
| **Implementation version** | `v2.lske.__version__` | Latitude value (`L-20`) | Implementation engineer | Engineering-owned. **It never implies conformance** and is never read as a specification version |
| **Package version** | `pyproject.toml` `project.version`; `p1/tooling` distribution | `velynx` 0.1.0; `p1_os` 0.1.0 | **Human** release authority | Bumped only in a release branch, in its own commit, with the release-gate transcript |
| **Schema / ontology version** | `ONTOLOGY_VERSION`, one literal site in `v2/lske/schema.py` | `"1.1.2"` | **Specification** (`RF-04` cl. 1–2) | Mirrors the specification version; engineering **never** edits it; `v2.lske` exports it not at all |
| **Migration version** | Does not exist in Phase 1 | — | Specification, at the stage that introduces store migration | May not be invented by engineering (§9.8 stage 1) |

### 8.2 Specification versions (PES-8.2)

1. A frozen specification version is immutable. Corrections produce a **new version file**.
2. The specification version is the only version that expresses what the software must do.
3. No engineering artifact may claim conformance to a version that does not exist on disk.

### 8.3 Implementation versions (PES-8.3)

1. `__version__` identifies the build, not the contract.
2. It is bumped in its own commit, never as a side effect of a task branch (§3.1 rule 4).
3. No code branches on `__version__`. Behaviour is never version-conditional.

### 8.4 Package versions (PES-8.4)

1. Package version changes are release acts, owned by the Human authority.
2. The release-gate workflow asserts the expected artifact names and versions; a mismatch blocks the
   release.
3. Package version and specification version are independent and are never presented as equivalent.

### 8.5 Schema and migration versions (PES-8.5)

1. `ONTOLOGY_VERSION` has exactly one literal site and one owner; a second occurrence is a P-03 violation
   and a blocking defect.
2. A schema content change requires a specification amendment first, regeneration second, byte-diff
   evidence third.
3. Migration versioning enters the project only when a specification stage defines a store migration.
   Until then, no migration file, table, or field exists, and none may be added in anticipation.

### 8.6 Version branch rule (PES-8.6)

Version bumps occur only on a branch of class `release/<version>` or `chore/version-<kind>`, contain
**only** the version change and its changelog line, and carry the owning authority's approval from the
table in §8.1.

---

## PART 9 — Future Specifications

### 9.1 The only admissible triggers (PES-9.1)

A new specification, or an amendment to a frozen one, may be written **only** when at least one of these
is demonstrated:

| # | Trigger | Required demonstration |
|---|---|---|
| **T-A** | **Observable underdetermination** | Two implementations, each satisfying every normative sentence, differ in an externally observable behaviour — stated concretely (R9-19 cl. 2) |
| **T-B** | **Internal contradiction** | Two normative sentences cannot both be satisfied (R9-0 escalation) |
| **T-C** | **Unsatisfiable sentence** | No implementation can satisfy a stated sentence; the impossibility is shown, not asserted |
| **T-D** | **New externally observable requirement** | A stakeholder-level requirement for behaviour observable from outside the system, approved by the Human authority as in scope |
| **T-E** | **New stage or scope entry** | A specification stage that the frozen build order already contemplates is opened, within the Constitution Lock's gates |

### 9.2 Absolute prohibitions (PES-9.2)

1. **Engineering problems never create specifications.** Difficulty, awkwardness, verbosity, slowness,
   duplication, tooling friction, deadline pressure, and reviewer preference are **not** triggers. Their
   correct outputs are: a latitude decision, a debt entry, or a fix.
2. **Internal implementation choices never become normative.** No helper, private algorithm, data
   structure, dependency, file split, optimisation, or private naming pattern may be written into a
   specification — including retroactively, and including "as implemented" clauses. Codifying the
   existing implementation because it exists is forbidden.
3. **Only externally observable behaviour can justify an amendment.** A finding whose subject is not
   observable, and which cites no normative sentence directly, is out of order (R9-19 cl. 2–3).
4. A closed matter is not reopened as a gap (`IMP-BLK-01`, `IMP-BLK-02`, `IMP-BLK-07A`; §0Y.2, `RF-0.3`).
5. A jurisdictional boundary that names its owner is a decision, not an ambiguity, and is not
   specified away (Appendix J; `obs2` interiors → Observatory, R7-2).
6. A specification may not be written to make a failing implementation conform.

### 9.3 Change Request procedure (PES-9.3)

A Change Request (`cr/<id>-<slug>` branch, **no implementation code**) SHALL carry:

```
CR ID:            CR-nn
Trigger:          T-A | T-B | T-C | T-D | T-E
Demonstration:    the concrete two-implementation divergence, contradiction, or impossibility
Observable:       the externally observable behaviour at stake
Affected sentences: sections and clauses
Non-goals:        the internal choices this CR does NOT make normative
Requested authority: Specification authority action sought
Impact:           observables, acceptance criteria, test rows, schemas, versions
Governance:       registration/posture consequences, if any
```

Flow: engineer or reviewer files the CR → Specification authority rules or drafts → **Human** approves the
amendment → a **new** specification version file is issued → the roadmap and traceability are extended →
implementation begins. **No implementation of an unapproved CR exists on any branch.**

### 9.4 What a CR may not contain (PES-9.4)

A proposed API shape copied from working code; a request for "more detail" without T-A; a performance
target with no observable basis; a style rule; a dependency mandate; a private-structure requirement; a
claim of admissibility.

### 9.5 PES defects (PES-9.5)

A defect **in this standard** — an internal contradiction, a conflict with rows 1–5 of §0.3, an
unenforceable rule, or an ambiguity — is filed as a PES defect, not resolved by local interpretation. PES
defects are corrected in a new PES version adopted by the Human authority. Rows 1–5 govern in the interim.

---

## PART 10 — AI Collaboration Standard

### 10.1 Roles and authority (PES-10.1)

| Role | Authority | Deliverables | SHALL NOT |
|---|---|---|---|
| **Opus** — Specification authority, Conformance reviewer, Governance owner | Interpret frozen sentences; rule on conformance; classify findings; own the governance posture; draft amendments when a §9.1 trigger is demonstrated | Rulings, conformance reviews, review records, CR drafts, governance checks | Write production implementation code; approve its own ruling as a release; adopt an amendment; register an artifact; claim admissibility; raise a finding without citation or, for a gap, without the R9-19 cl. 2 demonstration |
| **GPT** — Implementation engineer, Refactoring, Testing, Bug fixing | Choose within latitude; write and refactor implementation and test code; fix defects; produce evidence | Code, tests, evidence bundles, debt entries, findings against the specification (properly formed) | Add/rename/remove a public element; edit a frozen artifact; change `ONTOLOGY_VERSION` or a package version; add a dependency without §4.3 approval; weaken a test; interpret a contradictory sentence by choosing; self-approve a merge |
| **Human** — Final approval, Architectural changes, Release authority | Adopt amendments and this standard; approve architecture, dependencies, deletions, waivers, version bumps, releases; assign the constitutional steward; act in the Governance Registry | Approvals, adoptions, registrations, release decisions, waivers with expiry | Delegate release authority or amendment adoption to an AI role |

### 10.2 Separation of duties (PES-10.2)

1. The role that writes a change never reviews it. The role that reviews never silently rewrites it.
2. No AI role approves a merge that requires Human authority (§3.2 item 12).
3. No AI role asserts registration, admissibility, or raised Scientific Readiness — those are Human acts
   under the Repository Constitution.
4. Every review record and merge record names the acting role and the model identity, so authority is
   auditable after the fact.

### 10.3 Handoff protocol (PES-10.3)

| Handoff | Required payload |
|---|---|
| Specification authority → engineer | The governing sentences, the task id, the acceptance criteria, the released latitude entries, the stage boundary |
| Engineer → reviewer | Branch, scope statement, evidence bundle, surface diff, self-check against §3.2 |
| Reviewer → engineer | Findings with §5.4 fields and dispositions; nothing else |
| Reviewer/engineer → Human | Verdict, evidence bundle, the exact decision sought, the risk if declined |
| Anyone → Specification authority | A CR per §9.3, with its demonstration |

### 10.4 Conflict resolution (PES-10.4)

Engineer and reviewer disagree on conformance → the reviewer's citation decides; absent a citation, the
finding is out of order. Two normative sentences conflict → nobody chooses; escalate under R9-0. A process
question this standard does not answer → the Human authority decides and the answer is recorded for the
next PES version.

---

## PART 11 — Release Process

### 11.1 Lifecycle (PES-11.1)

```
Idea → Specification → Freeze → Implementation → Testing → Conformance Review
     → Release → Maintenance → Future Specification (if required) → …
```

| # | Phase | Owner | Entry condition | Exit condition (gate) |
|---|---|---|---|---|
| 1 | **Idea** | Human | An externally observable need, or a §9.1 trigger | Human accepts it as in scope; a CR id exists |
| 2 | **Specification** | Specification authority (Opus) | Accepted idea with its demonstration | A specification version whose every contract is single-valued and testable, with acceptance criteria and traceability |
| 3 | **Freeze** | Human adopts | Specification complete; readiness assessment `COMPLETE` | The version file is immutable; implementation is authorized; latitude is released |
| 4 | **Implementation** | Engineer (GPT) | Frozen specification, task register, playbook | Every task's exit conditions met; scope, surface, and signature diffs clean |
| 5 | **Testing** | Engineer (GPT) | Implementation complete for the stage | All in-scope criteria evidenced; §9.6 clauses complete; determinism transcript recorded; no mock substitution |
| 6 | **Conformance Review** | Reviewer (Opus) | Evidence bundle complete | Verdict **Approve**: zero open C1/C2/C3; all criteria evidenced; surface diff empty both ways |
| 7 | **Release** | Human | `G-stage` satisfied; §6.4's nine release gates green | Version bumped at its owning site; artifacts built and verified; evidence bundle archived; release record signed |
| 8 | **Maintenance** | Engineer + Reviewer | A released version exists | Defects fixed with reproducing tests; regressions reverted first; debt register current; no scope creep |
| 9 | **Future Specification** | Specification authority + Human | A §9.1 trigger demonstrated in maintenance | A CR enters phase 1; the cycle repeats. **No implementation precedes it** |

### 11.2 Phase discipline (PES-11.2)

1. Phases are not skipped and not overlapped. Implementation before freeze, or release before review, is
   a process defect.
2. A phase's exit gate is evidenced, not asserted.
3. Rollback is defined at every phase: revert the merge (phase 4–6), revert the release and re-issue
   (phase 7), revert and re-plan (phase 8).
4. Under the standing condition (§0.4), a release is an **engineering** release only. It carries no
   scientific claim, and its record says so.

---

## PART 12 — Success Metrics

Each KPI is measurable by a named method. A KPI with no method is deleted, not estimated.

| ID | KPI | Definition | Target | Method | Cadence | Owner |
|---|---|---|---|---|---|---|
| **K-01** | Specification conformance | In-scope acceptance criteria satisfied with artifacts / in-scope criteria | **100 %** (27/27 at stage 1) | Criterion table from the test transcript | Per merge, per stage | Reviewer |
| **K-02** | Public surface fidelity | Size of the two-way surface diff vs §9.13 | **0** in both directions | Programmatic enumeration (Document 6 §2.3) | Per merge | Reviewer |
| **K-03** | Test clause coverage | §9.6 clauses located and executing / clauses in in-scope rows | **100 %** | Clause-by-clause checklist | Per merge | Engineer |
| **K-04** | Deterministic build | Repeated builds/runs from a clean checkout producing identical declared artifacts and digests | **100 %** | Two-run byte/digest comparison; `P1 Release Gate` build output | Per merge, per release | Engineer |
| **K-05** | Regression rate | Regressions (§6.1) reaching `main` per 10 merges | **0**; any occurrence is reviewed | Merge and revert log | Monthly | Reviewer |
| **K-06** | API stability | Public surface changes not backed by a specification amendment | **0** | Surface diff history across releases | Per release | Reviewer |
| **K-07** | Review turnaround | Median time from evidence-complete to verdict | ≤ 1 working day; ≤ 2 for a stage gate | Review record timestamps | Monthly | Reviewer |
| **K-08** | Release quality | Releases requiring a revert or a hotfix within one maintenance cycle | **0** | Release and revert records | Per release | Human |
| **K-09** | Review order discipline | Findings closed as out-of-order (C6 or R9-19 cl. 2/3) / total findings | Trend to **0**; any rise triggers a reviewer-conduct review | Finding register by category | Monthly | Reviewer |
| **K-10** | Debt health | Open `TD-nn` past expiry; forbidden-debt instances | **0** past expiry; **0** forbidden | Debt register reconciliation | Per stage, per release | Engineer + Human |
| **K-11** | Evidence completeness | Merges whose evidence bundle satisfies §3.4 in full | **100 %** | Merge record audit | Per merge | Reviewer |
| **K-12** | Governance posture integrity | Artifacts missing the DRAFT banner, or making an admissibility/registration/Readiness claim | **0** | Header and claim check (Document 6 §2.6) | Per merge, per release | Reviewer |
| **K-13** | Gate integrity | Mandatory CI jobs suppressed, made advisory, or bypassed | **0** | Workflow diff review on every merge touching CI | Per merge | Human |
| **K-14** | Specification churn from engineering | Amendments whose trigger was not `T-A`…`T-E` | **0** | CR register audit | Per release | Specification authority |

**PES-12.1** — A KPI is never improved by weakening its method. Changing a KPI definition or target
requires Human approval and a note in the metric's history.

---

## SELF AUDIT

| # | Check | Method | Result |
|---|---|---|---|
| 1 | **No specification changes** | Scan every rule for a new field, default, API, invariant, acceptance criterion, observable, or value. Confirm each normative-sounding statement is a citation of §9.x / `RF-nn` / `R9-nn` / a Constitution Lock clause, or a pure procedure | **PASS.** Parts 1–12 introduce no specification content. All behavioural statements are restatements with citations (e.g. §9.5.1 cl. 1, `RF-03` cl. 6, §9.13.8 cl. 5–6, R9-19 cl. 1–4). The 27 criteria, 15 observables, 23 test rows, 23 schema files, 9 build stages, 12 ownership rows, and the `ONTOLOGY_VERSION` value are cited, never redefined |
| 2 | **No architecture changes** | Scan for any added/removed/moved module, package, file, layer, boundary, or dependency edge | **PASS.** §9.1's closed layout, §9.13.1's ownership map, and §9.13.7's dependency order are cited and enforced. §2.7/§2.12 forbid new files inside the closed layout, including "utils"-class helper modules. No new module, file, or shared component is created by this standard |
| 3 | **No governance conflicts** | Compare against `REPOSITORY_CONSTITUTION.md` v1.2.0 + `GOVERNANCE_REGISTRY.yaml` (`status: Draft`, `active_domain_standards: []`), R0-3, §9.12, Article L-11, Appendix J, R9-0/R9-12, R9-19 | **PASS with one reconciliation, recorded in §5.2.** This standard declares itself Proposed / Unregistered with no authority until registered (§0.4), asserts a precedence order that subordinates itself to all frozen artifacts (§0.3), carries the DRAFT banner, reserves registration and adoption to the Human role (§10.1), and forbids any admissibility claim. The six review categories are a **partition** of Document 6 §4.3's classes under R9-19 cl. 1, not an extension; §5.2 states the mapping and the override rule if it ever appears to widen R9-19 |
| 4 | **No ambiguity** | For each rule, ask: does it name a check, an enforcement point, or an owner? Is any subject left to an unowned choice? | **PASS.** Every rule carries an ID and either a decidable check or an owner. Every latitude subject names its releasing rule (§9.9, `L-01`…`L-21`, R9-19 cl. 3) rather than being left open. Two bounded matters remain **owned elsewhere and are declared as such**: `obs2` interiors (Observatory, R7-2) and stage-2/stage-7 observations (their stages). Per Appendix J, a boundary naming its owner is a decision, not an ambiguity |
| 5 | **Complete engineering lifecycle coverage** | Walk Idea → Specification → Freeze → Implementation → Testing → Conformance Review → Release → Maintenance → Future Specification; confirm each phase has an owner, an entry condition, an exit gate, a rollback, and an evidence requirement | **PASS.** Part 11's nine phases each carry owner, entry, exit gate, and rollback; Parts 3 and 6 supply the gates and evidence; Part 7 covers maintenance-time debt and cleanup; Part 9 closes the loop back to specification with admissible triggers only; Part 8 assigns every version kind an owner; Part 12 measures the whole cycle |
| 6 | **Self-consistency of this standard** | Cross-check rule references and category names across parts | **PASS.** The six categories of Part 5 are used identically in §3.5 item 15, §6.2, §7.2, and `K-09`. Branch classes of §3.1 are the same set referenced in §7.3 and §8.6. Version kinds of §8.1 are the same five referenced in §3.5 item 12 and §4.4 |

**Recorded reconciliation.** One: the Part 5 category set required by this operation is broader in wording
than Document 6 §4.3's class list. §5.2 resolves it by mapping, subordinates it to R9-19, and states that
R9-19 governs any residual tension. No other reconciliation was required, and no frozen sentence was
reinterpreted.

---

## FINAL CERTIFICATION

**Project Engineering Standard v1.0 Complete.**

This document is the permanent engineering governance standard for Project P1-v2. All future
implementation shall follow this standard. Future specifications are governed by this document and the
Constitution: they may be written only on a demonstrated trigger `T-A`…`T-E` (§9.1), never from an
engineering problem, never from an internal implementation choice, and only on externally observable
grounds.

**Standing:** Proposed / Unregistered. **Authority source: none until registered.** This standard binds
engineering practice upon adoption by the Human release authority and acquires normative standing only on
registration in `GOVERNANCE_REGISTRY.yaml` under Section 13 of `REPOSITORY_CONSTITUTION.md`. Its
root-directory location grants it no authority.

**Frozen artifacts unchanged:** `REPOSITORY_CONSTITUTION.md`, `P1_V2_CONSTITUTION_LOCK_v1.0.md`,
`P1_V2_LSKE_SPECIFICATION_v1.1.2.md`, the Phase 1 Implementation Authority Package (Documents 1–6), the
Reference Implementation Design, and the Production Implementation Roadmap are unmodified by this
document.

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**
