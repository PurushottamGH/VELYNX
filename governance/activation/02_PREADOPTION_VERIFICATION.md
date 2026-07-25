# Pre-Adoption Verification — observed repository state

- **Status:** Draft
- **Scope:** Repository state at revision `66e3e2a` plus uncommitted working-tree changes, observed 2026-07-25 (+05:30, minute precision)
- **Responsibility:** Report observed facts the activation plan depends on, and correct the plan's wrong premises
- **Authority source:** None. This record reports observations; it authorizes nothing and creates no requirement.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

An observation record under §3 ¶5 and §11 — conformance observations at one identified revision. It does not amend `00_MINIMUM_ACTIVATION_PLAN.md`; it corrects four of its factual premises.

---

## 1. Findings that change the plan

| # | Finding | Status | Effect |
|---|---|---|---|
| V-1 | A private key file was committed and remains reachable in history | **realized violation** | §10 ¶5 breach that deletion does not cure; rotation required now |
| V-2 | A record-management substrate already exists in `p1/` | plan was unaware | lowers engineering cost; creates a lifecycle/terminology collision with RS-1 |
| V-3 | Legacy surface is ~40 live-path artifacts, not 6 | plan understated | forces the tiered disposition in `04_LEGACY_DISPOSITION.md` |
| V-4 | Constitution v1.2.0 text is uncommitted | plan was unaware | changes what the adoption atomic change must contain |

Confirmed unchanged: exactly one identified human in history — 23 of 23 commits authored by `Purushottam <purushottam@local>` — and CI contains suppressed failures.

---

## 2. V-1 — private key in history *(most urgent item in the repository)*

`gcp-key.json.json` is absent from the working tree and listed in `.gitignore`, which reads as remediated. It is not. Observed via `git log --all --diff-filter=A --name-only -- "*gcp-key*"`:

```
c7db740  refactor(repo): implement approved repository architecture restructure
77584cc  Agent host session 49e6e5e3… — baseline checkpoint
4379339  Agent host session 2783b344… — baseline checkpoint
ec8b116  Agent host session 60519a91… — turn 1
c122129  restructure: move legacy codebase to legacy/   (legacy/gcp-key.json.json)
e350820  Agent host session 17a421ca… — baseline checkpoint
64edcc7  Agent host session 60519a91… — baseline checkpoint
b637623  Agent host session 83bd7d2f… — baseline checkpoint
fd7aabf  Sprint 1.1 + 1.1.1: F1 fix, C2 held-out fix, growth diagnostics
```

Two distinct paths were added, so the content is reachable from multiple commits. §10 ¶5: "Credentials and private keys MUST NOT be committed." This is a realized nonconformance from `fd7aabf` forward, and `.gitignore` does not cure it.

**Actions, in order:**

1. **Rotate the credential at the provider.** The only step that reduces exposure. Deletion or history rewriting does not — assume the key is disclosed. Operator action; no repository authority required.
2. Open a standing `unknown` at RS-1 activation (§6 ¶5: absence, reason, expected effect, recovery status), stating the disclosure window cannot be bounded from inside the repository.
3. List the residual state in the dossier's unresolved-violations field. §12 ¶1 forbids omitting known violations, so `A-07` MUST NOT be reported as passing.
4. Treat history rewriting as a separate decision. Recommendation: **do not** rewrite as part of adoption. It is destructive, invalidates every recorded commit reference and digest, and §7 ¶1 and §8 ¶2 both lean against it. Rotation plus disclosure is the conforming path; rewriting afterwards is a cleanliness choice requiring explicit approval.

The check must stay honest about its limits: a scan proves presence, never absence, since a secret may have been committed under an unrecognized name.

---

## 3. V-2 — the `p1/` substrate already exists

| Path | Contents |
|---|---|
| `p1/records/` | 12 type directories — **0 files** |
| `p1/templates/` | 11 templates: claim, decision, evidence, experiment, hypothesis, interpretation, principle_candidate, question, research_artifact, result, source, unknown |
| `p1/tooling/p1_os/` | frontmatter parser, identifier allocator, path resolver, enums, 12 Pydantic schemas |
| `p1/methodology/STATUS_LIFECYCLE.md` | descriptive; states plainly that no transition enforcement exists |
| `p1/specifications/milestone-1-gpt56.md` | 34 KB specification asserting PI-003/PI-004/PI-005 — a Normative artifact |
| `p1/architecture_decisions/` | two records, incl. `v0.1.0-release-gate.md` |

**Two consequences, opposite in sign.**

*Favourable:* `p1/records/` holding zero files is the one-command verification of the dossier's largest burden reducer. The §5/§6/§7 "no record of this kind exists" discharge is not an argument, it is an empty directory. Engineering task E-6 is also largely pre-built.

*Unfavourable:* the substrate does not match RS-1, structurally.

| Divergence | Detail | Consequence |
|---|---|---|
| Type set | `p1_os` defines 12 types including `claim`, `evidence`, `hypothesis`, `principle_candidate`, `source`, `question` | RS-1 owns 6 and lists 6 of these as `not_owned`. Tooling that validates a `claim` while no Active standard owns `claim` invites records that fail closed under §9 ¶1 |
| State names | enums use `draft`/`active`/`closed`; RS-1 uses `registered`/`executing`/`closed`, `recorded`, `open`/`resolved`, `proposed`/`approved`/`executed`/`reversed` | §11 ¶3: identical names MUST NOT conceal distinct types |
| Claim maturity | `ClaimMaturity` L0–L5, described as frozen | §5 ¶6: no ontology or threshold is constitutional; and no Active standard owns it |
| `experiment` vs `registered_protocol` | both names present for the same role | §11 ¶3: synonyms MUST NOT create distinct object types. One name must win |

**Cheapest disposition — three engineering decisions, no authority:**

1. RS-1 §1 adopts `p1/records/<type>/` and the `p1_os` frontmatter shape as its record format, reusing the tooling rather than rebuilding it.
2. Resolve the `experiment` / `registered_protocol` naming to one term, in both RS-1 and `enums.py`.
3. Add a `p1_os` validation profile restricted to RS-1's six types. The other six schemas stay in the tree as Legacy tooling and MUST NOT be used to create records. A config change, not a rewrite.

`p1/specifications/milestone-1-gpt56.md` becomes Legacy under §14 and needs Tier-1 treatment: it currently imposes requirements (PI-003 authorizing Decisions to change Claim state) that no Active standard would carry.

---

## 4. V-3 — Legacy surface is larger than stated

A lexeme scan for authority and certainty assertions (`canonical`, `frozen`, `is absolute`, `final authority`, `supersedes all`, `single source of truth`, `non-negotiable`, `must not be violated`) matched **1,585 occurrences in 166 files**. Excluding `archive/`, agent-configuration directories, and generated evidence, roughly **40 live-path artifacts** assert authority or frozenness, including:

`theory/PROGRAM_D_CONSTITUTION.md`, `PROGRAM_D_CANONICAL.md`, `PROGRAM_D_MASTER_ROADMAP.md` (31 matches), `PROGRAM_D_RESEARCH_STATE_v0.1.md`, `RESEARCH_PROTOCOL.md`, `audits/CONSTITUTION_COMPLIANCE.md`, `p1/specifications/milestone-1-gpt56.md` (30), five files under `theory/preregistrations/` (one with 72), `experiments/specs/EXP1_DATASET_SPEC.md` (38), `theory/HYPOTHESIS_REGISTER.md`, `theory/PHENOMENON_REGISTRY.md`, `evidence/certifications/*`, `docs/EXECUTION_GUIDE.md`, `docs/ARCHITECTURE_MAP.md`.

The plan's six-file move list is necessary but not sufficient. Banner-editing 40+ files before adoption is also the wrong trade — low-value work on artifacts §14 has already stripped. `04_LEGACY_DISPOSITION.md` resolves this with one index, banners only where a first-time reader would plausibly be misled, and a generated inventory for the rest.

Note `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md`: its title asserts an amendment, but no Constitution has ever been Active, so none occurred. Its header correctly declares no authority; the dossier's recorded interpretation 4.1 (adoption, not amendment) carries the point. Renaming is optional.

---

## 5. V-4 — the Constitution text is uncommitted

Working tree: `REPOSITORY_CONSTITUTION.md` modified (v1.1.0 → v1.2.0, full rewrite), `GOVERNANCE_REGISTRY.yaml` untracked, `README.md` modified, all of `governance/` untracked. `git log -1` is `66e3e2a Release candidate: Project P1 v0.1.0`.

**This is convenient, not a problem.** With nothing committed, §2 atomicity is easy: there is no partially-adopted state on the default branch to unwind.

**Committing the Draft text now is safe and advisable.** Draft has no authority (§4 ¶5, §9 ¶4), so committing the v1.2.0 text with `Status: Draft`, the Draft Registry, and `governance/**` protects the work without triggering anything. What MUST NOT happen is a commit that sets `Status: Active`, or populates `constitutional_steward`, without both attestations in the same revision — that is a nonconforming adoption, and §13 ¶4 makes it awkward to unwind.

Rule for intermediate commits: `status: Draft` everywhere, `constitutional_steward: []`, both attestation fields `null`.

---

## 6. Standing Unknowns to open at RS-1 activation

Extends RS-1 §6.2. Each is material and unresolved, so each is an `unknown`, not a footnote (§8 ¶1).

| Id | Statement | Resolution criterion |
|---|---|---|
| U-a | `gcp-key.json.json` was committed; the disclosure window and any use of the key cannot be bounded from inside the repository | Provider-side rotation confirmed and provider audit logs reviewed for the window |
| U-b | Registration-ordering evidence rests on author-controlled commit timestamps; §5 ¶3's trigger is unblinded access, which may leave no trace | An external timestamp anchor is in use for every protocol supporting a confirmatory analysis |
| U-c | No Active standard owns `claim` or `evidence`, so no Interpretation may assert Claim support | RS-1 MINOR amendment owning both types, activated |
| U-d | Nineteen `artifacts/exp_*` outputs and all pre-adoption execution are permanently exploratory working output | Not resolvable. Closes only by superseding execution under a Registered protocol |
| U-e | `p1_os` validates six record types no Active standard owns; records created through it would fail closed | Validation profile restricted to RS-1's owned types |
| U-f | CI reports success for checks that did not run (§12 ¶1) | `\|\| true` removed and shell corrected, so a green run means the checks executed |

---

## 7. CI honesty — confirmed by reading `.github/workflows/ci.yml`

- Five jobs install dependencies with PowerShell syntax — `if (Test-Path requirements.txt) { pip install -r requirements.txt }` — on `runs-on: ubuntu-latest`. Under `bash` this is not the intended conditional, so dependency installation does not behave as written.
- Three steps end in `|| true`: `mypy …`, the unit-test chain, and `Run research tests`. Those steps cannot fail.

Under §12 ¶1 a green run is therefore not evidence that those criteria were assessed. **Adoption does not require fixing this — it requires not citing it.** The remedy is cheap and is applied in this change set. If CI turns red afterwards, that is the correct signal, not a regression.
