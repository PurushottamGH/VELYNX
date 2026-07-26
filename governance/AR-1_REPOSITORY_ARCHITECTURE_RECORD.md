# AR-1 — Repository Architecture Record

- **Status:** Current — descriptive Level-4 record (implementation and explanatory documentation). Deliberately **not** `Active`: §2 defines `Active` for a Normative artifact listed in the Governance Registry, or for a governed object entered into its Active state under a Domain standard. This record is neither, so applying that word to it would reuse constitutional terminology for a different type, which §11 ¶3 forbids. `Current` here means "the version that describes the repository at this revision"; it is superseded by the next accepted revision of this record, and prior versions remain recoverable in history
- **Scope:** Version-controlled directory layout and declared boundaries of Project P1, at the revision in which this record is accepted
- **Responsibility:** Define repository layout, boundaries, dependencies, and rationale, as required by `REPOSITORY_CONSTITUTION.md` §10 ¶1
- **Authority source:** None. This record imposes no requirement and authorizes no transition. It is not a Normative artifact under §2 and holds no Registry entry.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` §10 ¶1
- **Version:** 1.0.1

---

## 1. Why this record exists, and what it is not

§10 ¶1: "Software architecture and repository layout are not constitutional. They MUST be defined in versioned architecture records with explicit boundaries, dependencies, and rationale. A directory name MUST NOT be treated as proof of separation."

Three consequences shape this document:

1. **The MUST attaches to the record, not to a standard governing records.** One versioned record with three elements discharges §10 ¶1. No architecture Domain standard is required.
2. **This record is descriptive.** It reports the boundaries the repository *has*, not boundaries it *must* have. Descriptive text imposes no requirements, so this is Level-4 documentation and is revisable by ordinary engineering change without amendment or attestation.
3. **Names prove nothing.** Every boundary below states how it could be checked. Where no check exists, that is recorded as unverified rather than asserted.

If P1 later wants these boundaries *enforceable*, that is when an architecture standard becomes worth activating — the trigger is recorded in `governance/activation/01_STANDARD_CLASSIFICATION.md`.

---

## 2. Layout and declared boundaries

File counts are indicative, observed 2026-07-25.

| Directory | Declared responsibility | Declared dependencies | Boundary verifiable? |
|---|---|---|---|
| `framework/` (38) | Reusable mathematical primitives: predictors, emergence estimators, MDL, scoring, null controls | stdlib + numeric libraries only | yes — import scan for `backend`, `frontend`, `experiments` |
| `backend/` (987) | Application layer: replay engines, knowledge models, persistence, telemetry | may depend on `framework/` | yes — direction of dependency is checkable |
| `frontend/` (7,549) | Standalone React/Vite client | HTTP API only | yes — no Python imports cross this line |
| `theory/` (56) | Hypotheses, specifications, literature, foundations | documents only | partially — prose, not imports |
| `experiments/` (105) | Empirical runs: E0, EXP0, EXP1, configuration schemas | `framework/`, may read `backend/` | yes — import scan |
| `evidence/` (643) | Verification artifacts, ledgers, traces, certifications | consumes outputs; imports nothing | yes — no source files expected |
| `p1/` (64) | Record substrate: `records/`, `templates/`, `tooling/p1_os`, `methodology/`, `specifications/`, `architecture_decisions/` | `p1/tooling` depends on pydantic; nothing else depends on `p1/` | yes |
| `governance/` (20) | Governance design, activation plan, standards, attestations, decisions, conformance records | documents only | yes |
| `tests/` (182) | Automated verification suites | may import any implementation package | assessor/assessed overlap — see §4 |
| `scripts/` (43) | CLI wrappers, validators, generators | may import `framework/`, `backend/` | yes |
| `docs/` (52) | Documentation, sprints, migrations | none | yes |
| `archive/` (582) | Deprecated and inherited material, incl. `legacy_normative/` | nothing depends on it | yes — inbound import scan must be empty |
| `research/` (103), `benchmarks/` (16), `infra/` (18), `configs/` (4), `data/` (49), `artifacts/` (96), `audits/` (30), `reviews/` (4), `literature/` (0), `src/` (1) | Inherited or auxiliary; no declared boundary | undeclared | **no** — see §5 |

Excluded from version control per `.gitignore` and §10 ¶5: `.venv/`, `.venv314/`, `node_modules/`, `dist/`, `.velynx_data/`, `P1.worktrees/`, `*.db`, `artifacts/experiments/`, `artifacts/benchmarks/`, ChromaDB stores, and `gcp-key.json.json`. Editor, agent, and cache directories (`.kilo/`, `.opencode/`, `.hypothesis/`, `.pytest_cache/`, `__pycache__/`) are tooling state, not canonical records.

---

## 3. Dependency direction

Declared, acyclic:

```
frontend ──HTTP──▶ backend ──▶ framework
                                  ▲
experiments ──────────────────────┘
scripts ────────▶ backend, framework
tests ──────────▶ any implementation package
p1/tooling ─────▶ (pydantic only)
governance, docs, theory, evidence, archive ──▶ nothing
```

Rationale: `framework/` is the sink so that scientific machinery does not acquire application state, which is what makes §10 ¶2's Material-state discipline achievable at all. `frontend/` is separated to keep a Node toolchain out of the Python dependency graph.

---

## 4. Known boundary weaknesses

Recorded because §10 ¶1 says a directory name is not proof of separation, and an architecture record that only lists intentions is exactly the failure the clause names.

| # | Weakness | Clause pressure | Status |
|---|---|---|---|
| W-1 | `tests/` imports the code it assesses. §10 ¶4 permits shared code "only when its use does not make the assessor depend on the behavior being assessed" | §10 ¶4 | unverified; no check exists |
| W-2 | Acceptance criteria and implementation are not demonstrably independently changeable (§10 ¶4) | §10 ¶4 | unverified |
| W-3 | Ten directories have no declared responsibility or dependency (§2 row above) | §10 ¶1 | declared open; see §5 |
| W-4 | Material-state declarations do not exist for stateful components — persistence layers, caches, session state under `backend/` | §10 ¶2 | not started. Applicable from the first `backend/` change after adoption, not at adoption |
| W-5 | `backend/constitution/*.md` uses the word "constitution" for model-behaviour prompts | §11 ¶3 | naming collision; renaming is optional and cosmetic |
| W-6 | `data/`, `artifacts/`, and `evidence/` mix committed summaries with runtime output | §10 ¶5 | partially handled by `.gitignore`; not verified per-file |

W-4 is the largest deferred item and the reason `03_ADOPTION_CHANGE_MANIFEST.md` keeps software out of the adoption change: with no software change in that revision, §10 ¶2–4 discharge as not applicable with a testable reason.

---

## 5. Undeclared directories

`research/`, `benchmarks/`, `infra/`, `configs/`, `data/`, `artifacts/`, `audits/`, `reviews/`, `literature/`, `src/` are inherited. Rather than invent boundaries to make this record look complete, they are recorded as undeclared. §10 ¶1 requires layout to be defined in a record; a record stating "no boundary is declared for this directory, and nothing may be inferred from its name" satisfies that more honestly than a fabricated rule.

Consequence a reader should draw: no separation claim may be made about these directories on the basis of this record.

---

## 6. Revision

This record is Level-4 documentation. It is revised by ordinary engineering change with the version incremented and the rationale for the change recorded. It requires no steward approval, no attestation, and no Registry entry, because it creates no requirement (§4 ¶3, §10 ¶1).

This record carries no normative phrasing, and normative phrasing added to it would carry no authority: a Level-4 document imposing requirements contradicts §4 ¶3. Where a boundary needs to bind, the mechanism is an architecture Domain standard activated under §4 ¶2, not added obligations in this file.

Revision history: `1.0.1` restated this paragraph descriptively. The prior wording expressed it as a prohibition on the record itself, which introduced a requirement into informative text contrary to §11 ¶2 and asserted a requirement the record's own authority line disclaims. No boundary, dependency, weakness, or rationale in §§2–5 changed.
