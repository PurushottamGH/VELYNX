# Repository Architecture Record (Proposed)

- **Status:** Draft
- **Scope:** Directory structure, boundary declarations, and dependency rules for the Project P1 repository
- **Responsibility:** Define the repository layout, its boundaries, dependencies, and rationale, as the architecture record contemplated by Constitution §10
- **Authority source:** None. This record has no normative authority. It is the *design* of an architecture record; it becomes one only on activation under DG-12 per Constitution §4.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 §10 (Draft, not adopted)
- **Version:** 0.1.0

---

## 1. Constitutional basis and its consequences

Constitution §10 ¶1:

> "Software architecture and repository layout are not constitutional. They MUST be defined in versioned architecture records with explicit boundaries, dependencies, and rationale. **A directory name MUST NOT be treated as proof of separation.**"

Three consequences drive this design.

**1.1 Layout is Level-4 material, and is revisable without amendment.** Nothing here binds the Constitution, and the Constitution imposes nothing here beyond §10's form requirements and §2's pin on the Registry path. Reorganisation is an engineering decision under DG-12, not a constitutional event. This is deliberate: over a twenty-year horizon, layout will change many times and the Constitution should survive all of them untouched.

**1.2 A directory is not a boundary.** Because §10 explicitly refuses to let a directory name prove separation, this design pairs every directory with a machine-readable **boundary declaration** (`_BOUNDARY.yaml`) stating its owning standard, the object types it may contain, and the directories it may depend on. The declaration — not the name — is the boundary, and check `DA-34` enforces it. A repository whose separation exists only in folder names satisfies §10 in appearance and fails it in substance.

**1.3 Two paths are constitutionally pinned.** `GOVERNANCE_REGISTRY.yaml` is pinned by §2 ("the Governance Registry is `GOVERNANCE_REGISTRY.yaml`"). `REPOSITORY_CONSTITUTION.md` is pinned by §14 and by its own Registry entry. Neither may be moved by this record; moving either requires a §13 amendment. This is defect DD-3 in `00_ECOSYSTEM_OVERVIEW.md` §8 — a constitutional clause fixing layout inside a Constitution that declares layout non-constitutional. The design accepts the pin and documents the exception rather than proposing an amendment for cosmetic gain.

---

## 2. Proposed tree

```
P1/
├── REPOSITORY_CONSTITUTION.md      [PINNED §14]  Level-1 authority
├── GOVERNANCE_REGISTRY.yaml        [PINNED §2 ]  identity · jurisdiction · authority
├── README.md                                     non-normative navigation only
│
├── constitution/                   Tier-0 supporting record store
│   ├── amendments/                 amendment dossiers (§13 seven-element form)
│   ├── attestations/               Independent reviewer attestations; adopter attestations
│   ├── adoption/                   adoption dossier and its evidence
│   └── superseded/                 prior constitution versions, recoverable per §9
│
├── registry/                       the Registry's machinery, NOT the Registry itself
│   ├── schema/                     JSON Schema for GOVERNANCE_REGISTRY.yaml
│   ├── jurisdictions/              machine-readable jurisdiction tuples, one per standard
│   └── transitions/                Registry transition records (§9 eight-element form)
│
├── domain_standards/               ALL Level-2 Domain standards
│   ├── ontology/                   O-1
│   ├── governance/                 DG-1 … DG-13
│   ├── scientific/                 S-1 … S-10
│   └── engineering/                (empty; reserved for future engineering domains)
│
├── governance/                     governance RECORDS (not standards)
│   ├── design/                     this design set — Draft, no authority
│   ├── authority/                  authority assignment records; steward roster
│   ├── delegations/                delegation records (§4 five-element form)
│   ├── conflicts/                  conflict records under DG-10
│   ├── containment/                emergency containment action records under DG-9
│   └── reviews/                    review records under DG-4
│
├── ontology/                       the ontology CONTENT owned by O-1
│   ├── TYPE_REGISTER.yaml          the governed object types
│   ├── RELATIONSHIPS.yaml          permitted edges between types
│   ├── IDENTIFIERS.yaml            identifier grammar and allocation
│   └── schemas/                    per-type JSON Schema / Pydantic contracts
│
├── research/                       Investigation records (S-1); programme material
│   ├── investigations/
│   └── literature/                 Source surveys feeding S-4
│
├── protocols/                      Registered protocols and preregistrations (S-1, Level 3)
│   ├── registered/                 immutable once registered
│   └── draft/                      not yet registered; execution against these is exploratory
│
├── questions/                      S-2 record store
├── unknowns/                       S-3 record store
├── observations/                   S-4 record store
│   └── sources/                    Source records (S-4)
├── evidence/                       S-5 record store
├── claims/                         S-6 record store
├── hypotheses/                     S-7 record store
├── results/                        S-8 record store  — immutable from creation (§7)
├── interpretations/                S-9 record store
├── principles/                     S-10 record store
├── decisions/                      DG-13 record store
│
├── software/                       Level-4 implementation
│   ├── p1_os/                      record tooling (schemas, frontmatter, identifiers)
│   ├── cli/
│   └── lib/
│
├── validation/                     Level-4 validation, independently changeable from software (§10 ¶4)
│   ├── specifications/             test specifications = criteria
│   └── suites/                     executable validation
│
├── automation/                     the checks themselves, owned by DG-11
│   ├── checks/                     one module per registered check A-xx
│   ├── CHECK_REGISTER.yaml         scope, limitations, FP/FN disclosure per check
│   └── ci/                         workflow definitions
│
├── audit/                          audit reports under DG-6 (§3 ¶5: observation only)
│
├── custody/                        DG-7: external artifact manifests, digests, retention schedules
│
└── archive/                        Legacy material (§14). No authority. Read-only.
    ├── legacy_normative/           artifacts that asserted authority pre-adoption
    └── programs/                   Program A/B/C/D historical corpus
```

**Boundary declarations.** Every directory above carries `_BOUNDARY.yaml`:

```yaml
directory: results/
owning_standard: S-8
permitted_object_types: [result, invalid_result, abandoned_execution]
permitted_dependencies: [protocols/registered/, custody/, ontology/]
forbidden_content: [interpretation, decision]     # Constitution §3
mutability: append_only                            # Constitution §7
retention: permanent                               # Constitution §7, §8
```

---

## 3. Per-directory specification

Columns: **Why it exists** · **Constitutional authority** · **Ownership** · **Dependencies** · **Lifecycle**.

### 3.1 Tier 0 — constitutional

| Directory | Why it exists | Constitutional authority | Ownership | Dependencies | Lifecycle |
|---|---|---|---|---|---|
| `constitution/amendments/` | §13 requires a seven-element dossier per amendment; dossiers are Repository evidence and must be retained | §13 | Constitutional steward | none | Append-only. A dossier is Draft → Submitted → Ratified or Rejected; all outcomes retained (§8). |
| `constitution/attestations/` | §13 makes attestations Repository evidence; they must be independently locatable and auditable | §13 ¶2 | Independent reviewer (author); steward (custody) | `governance/authority/` for identity | Append-only, immutable once signed. Never edited; a defective attestation is superseded by a new one. |
| `constitution/adoption/` | The §13 initial-adoption event needs one atomic, inspectable dossier | §13 ¶3 | Adopter | attestations, registry | Written once. Retained permanently even if adoption fails. |
| `constitution/superseded/` | §9 ¶5 "Prior versions MUST remain recoverable" | §9, §13 ¶4 | Steward | none | Write-once, read-only. |
| `registry/schema/` | §4 makes the Registry determinative of authority; an unvalidated Registry is an unverified authority source | §4, §12 ¶3 | DG-1 | ontology | Versioned with DG-1. Breaking schema change requires DG-1 amendment. |
| `registry/jurisdictions/` | §4 requires rejection of overlapping jurisdictions — undecidable against prose, decidable against tuples | §4 ¶2 | DG-1 | ontology | One file per standard, created in the standard's activation atomic change. |
| `registry/transitions/` | §9 ¶3 requires a version-controlled eight-element transition record for every valid transition | §9 ¶3 | DG-1 | authority records | Append-only, immutable. |

**Note on `registry/` vs `GOVERNANCE_REGISTRY.yaml`.** §2 confines the Registry's responsibility to identifying artifacts, jurisdictions, and authority. Its schema, its validators, and its transition history therefore **cannot** live inside it without violating §2's sole-responsibility limit and §11's one-primary-responsibility rule. They live here.

### 3.2 Standards

| Directory | Why it exists | Constitutional authority | Ownership | Dependencies | Lifecycle |
|---|---|---|---|---|---|
| `domain_standards/ontology/` | O-1 must be locatable and activatable before any type-owning standard | §9 ¶1 | O-1 authority per Registry | none | Draft → Active → Superseded/Withdrawn (§9 ¶4). |
| `domain_standards/governance/` | DG-1…DG-13; §2 permits Domain standards over a "governance … domain" | §2, §4, §9 | per-standard Registry authority | ontology | as above |
| `domain_standards/scientific/` | S-1…S-10; one owner per scientific object type, per §9 | §2, §9 | per-standard Registry authority | ontology, peers by reference | as above |
| `domain_standards/engineering/` | §2 permits engineering domains; kept empty so the extension point is visible rather than invented later | §2 | unassigned | ontology | Created on first engineering domain activation. |

Co-locating all Level-2 standards in one subtree is deliberate: it makes the §9 "exactly one standard per object type" invariant checkable by enumerating one directory, and it prevents standards from accruing implied authority by proximity to the records they govern.

### 3.3 Governance records

| Directory | Why it exists | Constitutional authority | Ownership | Dependencies | Lifecycle |
|---|---|---|---|---|---|
| `governance/design/` | Design work must exist somewhere that cannot be mistaken for a standard | §4 ¶1 (no fields ⇒ no authority) | authors | none | Draft indefinitely. Superseded by activated standards; retained. |
| `governance/authority/` | §4 requires every authority source to identify jurisdiction and permitted transitions; that must be a record, not folklore | §4 ¶1-2, §13 ¶3 | DG-3 | registry | Assign → Active → Revoked/Expired/Succeeded. Never deleted. |
| `governance/delegations/` | §4 requires delegations to state five elements; unrecorded delegation is void | §4 ¶4 | DG-3 | authority | Same as authority records. |
| `governance/conflicts/` | §4 ¶4 leaves conflicting same-level requirements "both nonconforming" until resolved — that interval needs a tracked object | §4 ¶4 | DG-10 | authority | Open → Resolved/Escalated. Retained. |
| `governance/containment/` | §12 ¶2 permits containment before record creation, requiring the record "immediately afterward" | §12 ¶2 | DG-9 | none | Append-only. Each entry is subject to subsequent review by construction. |
| `governance/reviews/` | §12 ¶1 requires traceable manual inspection procedures and findings | §12 ¶1, §12 ¶4 | DG-4 | authority | Requested → Conducted → Attested/Rejected. Retained. |

### 3.4 Ontology

| Directory | Why it exists | Constitutional authority | Ownership | Dependencies | Lifecycle |
|---|---|---|---|---|---|
| `ontology/` | §11 ¶3 requires terminology reuse and forbids synonyms creating distinct types or identical names concealing distinct types. Enforcing that needs one register. | §5 ¶6 (ontologies must be governed by a revisable domain standard), §11 ¶3 | O-1 | none | Versioned with O-1. Type addition = O-1 amendment. Type removal requires a migration record. |

§5 ¶6 is explicit that no ontology is constitutional. Placing the type register under a revisable Level-2 standard is therefore not a convenience but a requirement.

### 3.5 Scientific record stores

All ten stores share a common specification:

- **Why they exist:** §3 ¶1 separates scientific records from governance, implementation, validation, and audit. §9 requires per-type lifecycles. One store per type makes the owner unambiguous and makes "exactly one standard per type" visible on disk.
- **Constitutional authority:** §2 (kind definitions), §3 (separation), §9 (lifecycles).
- **Ownership:** the type's Level-2 standard, per the table below.
- **Dependencies:** `ontology/` for schema; `protocols/registered/` where a protocol governs the transition; `custody/` for external artifacts; upstream record stores by reference only.
- **Lifecycle:** defined by the owning standard; every transition produces a §9 eight-element record.

| Store | Owner | Mutability | Retention | Constitutional constraint of note |
|---|---|---|---|---|
| `questions/` | S-2 | mutable while Draft | permanent | §2: a Question is not automatically an Unknown |
| `unknowns/` | S-3 | state-mutable | permanent, kind never removed | §8 ¶1: "Unknown is a permanent first-class object kind" |
| `observations/` | S-4 | append-only | permanent | §2: an Observation precedes admission; it is not Evidence |
| `evidence/` | S-5 | append-only; admission/exclusion recorded | permanent | §6 ¶3: may not be promoted or discarded for agreement with a preferred conclusion |
| `claims/` | S-6 | state-mutable | permanent | §5 ¶1: every Claim states a falsifying observation |
| `hypotheses/` | S-7 | state-mutable | permanent | §2: Claim + operational test + counting-against outcome |
| `results/` | S-8 | **immutable from creation** | permanent | §7 ¶1: correction only via a new linked Result; history never rewritten |
| `interpretations/` | S-9 | state-mutable | permanent | §3: must not alter a Result; §5 ¶5 requires null + strongest alternative |
| `principles/` | S-10 | state-mutable | permanent | §5 ¶6: falsifiable, reversible, explicitly scoped |
| `decisions/` | DG-13 | append-only | permanent | §2: references but does not contain Evidence; §3: must not alter an Observation or Result |

`results/` deserves emphasis. §7 makes Results immutable from the creating transition and forbids history rewriting. That is a *filesystem and version-control* requirement, not merely a policy: it implies branch protection, a prohibition on force-push affecting this subtree, and check `DA-14` comparing content digests of Active Results against history.

### 3.6 Realization and assurance

| Directory | Why it exists | Constitutional authority | Ownership | Dependencies | Lifecycle |
|---|---|---|---|---|---|
| `software/` | §3 ¶3 makes implementation a distinct responsibility; §10 requires declared Material state | §3, §10 | DG-12 | ontology, custody | Ordinary engineering lifecycle under DG-8. |
| `validation/` | §10 ¶4: "Implementation and validation MUST be independently changeable" — a shared directory makes that structurally impossible | §3 ¶4, §10 ¶4 | DG-12 + DG-5 | software (by interface only) | Criteria change only in the responsible Normative artifact (§10 ¶4). |
| `automation/` | §12 ¶3: CI/tests/schemas SHOULD enforce every mechanically decidable requirement; §12 ¶4 limits a check's evidentiary reach to what it assessed | §12 | DG-11 | ontology, registry | Check: Proposed → Active → Advisory → Retired. A broken check is Advisory, never silently absent. |
| `audit/` | §3 ¶5 and §11: audit reports observe conformance at one revision and may not create the requirements they audit | §3 ¶5, §11 | DG-6 | everything, read-only | Append-only, immutable, revision-stamped. |
| `custody/` | §6 ¶2 and §10 ¶5: material excluded from version control still needs a version-controlled manifest | §6, §10 ¶5 | DG-7 | none | Append-only manifests; retention schedule per artifact class. |
| `archive/` | §14: artifacts not activated at adoption become Legacy; §4 ¶5 requires Legacy content to stay distinguishable from Active requirements | §4 ¶5, §14 | DG-2 | none | Write-once. Content never edited; re-activation requires satisfying §4 afresh. |

The separation of `software/` from `validation/` is the structural expression of §10 ¶4 and of §3's rule that "implementation MUST NOT validate itself merely by executing successfully." Note also §10 ¶4's final sentence: shared code between the two is permitted **only** where it does not make the assessor depend on the behaviour being assessed — a rule that a directory split alone does not enforce, and which therefore also appears as check `DA-35`.

---

## 4. Dependency rules

Directory dependencies form a DAG. The permitted edges, in one statement:

1. Any directory MAY depend on `ontology/`.
2. Record stores MAY depend on upstream record stores **by identifier reference only** — never by importing or restating their content.
3. Record stores MUST NOT depend on `software/`, `validation/`, `automation/`, or `audit/`. Records are data; tooling reads them, not the reverse.
4. `validation/` MAY depend on `software/` interfaces; `software/` MUST NOT depend on `validation/` (§10 ¶4).
5. `audit/` MAY read everything and MUST write only within `audit/` (§3 ¶5).
6. `automation/` MAY read everything and MUST write only findings (§4 ¶4: automation may propose or check, never authorize).
7. `archive/` is a sink: nothing may depend on it. A dependency on archived material is a nonconformance, since Legacy artifacts have no authority (§4 ¶5).
8. `domain_standards/` MUST NOT depend on any record store. A standard that depends on the records it governs is circular and unfalsifiable.

Rules 3, 7, and 8 are the load-bearing ones and are enforced by check `DA-34`.

---

## 5. Rationale and rejected alternatives

§10 requires rationale. The three consequential choices:

**5.1 Flat per-type record stores rather than a single `records/` root.**
*Chosen:* ten top-level stores. *Rejected:* `records/{type}/`.
Rationale: §9's "exactly one Active Domain standard per object type" is the invariant most likely to erode over twenty years. Top-level stores make each type's owner visible without opening a file, keep boundary declarations at depth 1, and make ownership violations obvious in a diff. The cost is a wide repository root. A nested `records/` root is tidier but hides the ownership map one level down and invites a single `records/` boundary declaration to stand in for ten distinct ones — precisely the "directory name as proof of separation" failure §10 warns against.
*Reversal cost:* low. This is a Level-4 decision; a future DG-12 revision may nest the stores provided the boundary declarations move with them.

**5.2 All Level-2 standards co-located, separated from the records they govern.**
*Chosen:* `domain_standards/{ontology,governance,scientific,engineering}/`. *Rejected:* placing each standard beside its store (e.g. `results/STANDARD.md`).
Rationale: co-location by governed subject would let a standard inherit apparent authority from the records around it, and would make the "one owner per type" audit require walking the whole tree. Separation also matches §3's insistence that governance and scientific records are distinct responsibilities.

**5.3 Existing `p1/` Research OS is migrated, not replaced.**
The repository already contains a working record substrate: twelve strict Pydantic v2 schemas, governed frontmatter templates, an identifier grammar, and 382 passing tests, with `p1/records/` present but empty. Rebuilding it would discard verified engineering for no constitutional gain.
*Proposed migration:* `p1/tooling/p1_os/` → `software/p1_os/`; `p1/templates/` → `ontology/schemas/` templates; `p1/records/{type}/` → the corresponding top-level store; `p1/methodology/STATUS_LIFECYCLE.md` → input to the relevant S-* standard, not a standard itself (it self-describes as "descriptive only… No transition enforcement is implemented").
*Blocking reconciliation:* the Research OS defines twelve `ObjectType` values; Constitution §2 defines eleven scientific kinds plus Decision. The Research OS adds `research_artifact` and `principle_candidate` and omits `Observation` and `Principle`. Under §11 ¶3, that mismatch must be resolved **before** O-1 activates — synonyms must not create distinct types, and identical names must not conceal distinct ones. Recorded as roadmap item M-3 and risk R-06.

---

## 6. Known nonconformances in the current tree

Recorded as observations, not repaired here; repair requires authority that does not yet exist.

| # | Observation | Clause |
|---|---|---|
| N-1 | No architecture record exists; layout is carried de facto by `README.md`, which correctly disclaims authority | §10 ¶1 |
| N-2 | `theory/PROGRAM_D_CONSTITUTION.md` asserts absolute authority over a program | §1 ¶2, §14 |
| N-3 | ~13 artifacts self-declare canonical / frozen / definitive / supreme | §1 ¶2 |
| N-4 | `RESEARCH_PROTOCOL.md` and `parameter_registry.yaml` freeze scientific constants outside any revisable standard | §5 ¶6 |
| N-5 | `audits/CONSTITUTION_COMPLIANCE.md` audits an "implicit" constitution it derived, and creates the gate rule it enforces | §3 ¶6, §12 ¶3 |
| N-6 | `.github/workflows/ci.yml` uses PowerShell `Test-Path` on `ubuntu-latest` and terminates checks with `\|\| true`; several jobs cannot fail | §12 ¶3 (an unavailable check must be reported as not verified, never as passed) |
| N-7 | `reproducibility.yaml` freezes coefficients that `PROGRAM_D_CANONICAL.md` marks `[REJECTED]`, and cites a HEAD that no longer exists | §4 ¶4 (same-level conflict) |
| N-8 | A credential-shaped file `gcp-key.json.json` and a populated `.env` are present in the working tree | §10 ¶5 |
| N-9 | Two hypothesis registers and two experiment-registration paths coexist | §9 ¶1 |
| N-10 | `p1/records/` is empty: zero canonical records exist, so no record-layer requirement has ever been exercised | — (readiness, not conformance) |

N-8 warrants immediate attention independent of governance: verify both files are ignored, confirm they were never committed in any historical revision, and rotate the credentials if there is any doubt. That is an operational security matter, and §12 ¶2 explicitly permits containment to precede record creation.
