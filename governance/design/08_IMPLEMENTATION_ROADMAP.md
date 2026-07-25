# Implementation Roadmap

- **Status:** Draft
- **Scope:** Sequenced activation of the P1 constitutional ecosystem from the current state
- **Responsibility:** Define phases, gates, dependencies, and deliverables for activation
- **Authority source:** None. This record has no normative authority and authorizes no transition.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. Ordering logic

Three constraints fix the order, and no sequencing cleverness escapes them.

1. **Nothing activates before adoption.** §13 requires the adoption Atomic change to activate the Constitution, create or activate the Registry, and assign at least one constitutional steward. Until then no authority exists to activate anything, and §4 ¶2 says activation "fails closed."
2. **Adoption requires two identified humans.** §13 ¶3. One exists. This is not a task that can be worked around; it is a precondition.
3. **The dependency graph is the activation order.** O-1 gates every type-owning standard; G-3 gates every authorized transition; G-4 gates every attestation and therefore every activation; G-13 gates every scientific state change.

The roadmap is therefore short at the front and long in the middle, with a single hard blocker at the very start. Phases M-1 and M-2 can proceed *now*, because drafting and building checks claims no authority.

---

## 2. Phases

### M-0 · Adoption *(BLOCKED — H-01)*

**Gate:** two identified humans exist, one of whom is not an author of the adoption change.

**Deliverables, in one Atomic change (§2, §13 ¶3):**
- `REPOSITORY_CONSTITUTION.md` status Draft → Active.
- `GOVERNANCE_REGISTRY.yaml` created or activated, with the Constitution's entry consistent per §4 ¶1.
- At least one constitutional steward assigned, authorized to amend, supersede, or withdraw the Constitution and to activate Domain standards.
- Adopter attestation and Independent reviewer attestation, each satisfying §13 ¶2 in full (reviewed revision, non-authorship, Evidence production, conflicts, procedure, conclusion, competence, records examined).
- Adoption dossier in `constitution/adoption/`.

**Prior decisions required (all human):**
- H-01 — who the second human is.
- H-02 — ratify v1.2.0 via **initial adoption**, not amendment. Finding F-9 in `audits/CONSTITUTION_v1.2.0_AMENDMENT_RECORD.md` establishes that the Constitution is silent on whether §13's amendment rules govern revision of a *Draft* constitution; initial adoption is the defensible path since the prior version was never Active.
- H-03 — whether to include amendment **A-8** (General Delegation Clause, defect D-1) in the adoption change. Doing it at adoption is far cheaper than amending an Active Constitution later, and G-2, G-4, G-5, and G-12 all depend on it.
- H-04 — whether to include the Registry precedence clause (defect D-2, finding F-6).
- H-12 — whether to add clause identifiers (finding F-19), on which `A-39` coverage depends.

**Consequence of §14 at this moment:** every Normative artifact not activated in the same change becomes **Legacy** with no authority. That is roughly thirteen self-declared canonical artifacts, `theory/PROGRAM_D_CONSTITUTION.md`, `RESEARCH_PROTOCOL.md`, both parameter registries, and the whole Program D specification chain. Existing scientific records are preserved; only their authority classification changes. **This must be understood and accepted before adoption, not discovered after** — see M-6 and risk R-02.

---

### M-1 · Pre-adoption preparation *(can start immediately; claims no authority)*

Nothing here requires authority, because nothing here activates.

| # | Deliverable | Why now |
|---|---|---|
| M-1.1 | Draft O-1, G-1, G-2, G-3, G-4, G-13 to the Domain Standard Interface | These six gate everything; drafting is the long-lead item |
| M-1.2 | Machine-readable jurisdiction declarations for all 24 standards | Makes `A-04` possible; forces the disjointness discipline early, when it is cheap to fix |
| M-1.3 | Registry JSON Schema | `A-01`, `A-03` |
| M-1.4 | Build checks A-01…A-09, A-22, A-29, A-36, A-38, A-39, A-50, A-51 as **Advisory** | Governance-header and Registry checks are the cheapest high-value automation and need no authority to run |
| M-1.5 | Repair `.github/workflows/ci.yml` | Wrong-OS shell syntax and `|| true` mean several jobs cannot fail; under §12 ¶1 their green status means "not verified," not "passed" (N-6) |
| M-1.6 | Credential remediation | Verify `gcp-key.json.json` and `.env` are ignored, confirm they never entered history, rotate if uncertain (N-8). Operational security, independent of governance |
| M-1.7 | External anchors: commit signing, branch protection on record paths, third-party timestamping | Closes the four structurally-undetectable classes in `05_AUTOMATION_ARCHITECTURE.md` §5. **Timestamping must precede any confirmatory work**, or `A-20` remains Advisory forever |
| M-1.8 | Legacy inventory | Enumerate every artifact that will become Legacy at adoption, with its dependents. Input to M-6 and to the H-06 decision |

**M-1.7 deserves emphasis.** External timestamping is cheap, additive, requires no governance change, and is the *only* mechanism that makes the preregistration guarantee real. Every day of confirmatory work performed without it is work whose registration ordering rests on a single actor's honesty (risk R-08). It should be done before M-2, not after.

---

### M-2 · Ontology reconciliation *(can start immediately; gates M-3)*

**Gate:** the Constitution's object kinds and the existing P1 Research OS type set agree, or their differences are explicitly reconciled.

| Constitution §2 kinds | P1 Research OS `ObjectType` | Action |
|---|---|---|
| Question, Evidence, Claim, Hypothesis, Result, Interpretation, Unknown, Decision, Source | present | align field-by-field |
| **Observation** | **absent** | must be added — §2 makes it a distinct kind and forbids substitution |
| **Principle** | present as `principle_candidate` | §11 ¶3: either use the constitutional term or prove no ambiguity from the variant |
| — | `research_artifact` | subordinate type; needs an owning standard or removal (§9 ¶1) |
| — | `experiment` | maps to S-1 `investigation` / `registered_protocol`; resolve the synonym |

Also reconcile: `p1/methodology/STATUS_LIFECYCLE.md` states only Unknown and Claim have more than one representable state and that PI-003/004/005 are unenforced — those become S-3 and S-6 lifecycle inputs, not standards. And the maturity ladder L0–L5 has no constitutional counterpart; it must be either an S-6 state model or dropped, not both.

**Deliverable:** a reconciliation record naming every type, its constitutional counterpart, its owning standard, and its identifier namespace.

---

### M-3 · Foundation activation *(gate: M-0, M-2)*

Activate, as one Atomic change with six attestations (batching permitted by §4 ¶2; attestations are per-standard):

**O-1, G-1, G-2, G-3, G-4, G-13.**

**Exit criteria:** `A-04` reports no overlap; every registered type has exactly one owner; every declared transition resolves to a living authority (`A-05`); every MUST in the six standards maps to a check or an `MRP-xx` (`A-39`).

After M-3 the system can authorize transitions. Before M-3 it cannot, no matter what any document says.

---

### M-4 · Execution capability *(gate: M-3)*

Activate **S-1, S-3, S-4, S-8, G-7, G-12.**

This is the minimum set that permits a scientific execution to produce a Result: a Registered protocol (S-1), Observations (S-4), Results (S-8), Unknowns (S-3), custody (G-7), and an Active architecture record (G-12, discharging the §10 nonconformance N-1).

Promote checks A-12…A-17, A-20, A-21, A-31…A-34, A-43…A-45, A-58…A-60 from Advisory to Active as their requirements come under Active standards.

**Milestone:** the first genuinely Registered protocol can be registered, and the first constitutionally valid Result recorded. Note what this implies: **no work executed before this point can become a confirmatory Result** (§2, §5 ¶3, §13 ¶4). The nineteen existing `artifacts/exp_*` directories remain exploratory working output permanently.

---

### M-5 · Inference capability *(gate: M-4)*

Activate **S-2, S-5, S-6, S-9.** Claims, Evidence admission, Interpretations, Questions. Promote A-17…A-19, A-54…A-56, A-62.

**Milestone:** the confirmatory chain in `03_SCIENTIFIC_STACK.md` §1 is complete end to end, and a Claim's state can change on admitted Evidence through an authorized Decision.

---

### M-6 · Legacy disposition *(gate: M-3; should not lag M-4)*

Every artifact made Legacy at adoption gets an explicit disposition under G-2. Three outcomes only:

- **Re-activate** — satisfy §4 afresh: rewrite to the Domain Standard Interface, register, review, attest.
- **Archive** — move to `archive/legacy_normative/`, retain, mark clearly, remove all authority claims from live paths.
- **Supersede** — replaced by an Active standard that states the supersession.

Priority order, worst first:
1. `theory/PROGRAM_D_CONSTITUTION.md` — a competing constitution asserting absolute authority (§1 ¶2).
2. `PROGRAM_D_CANONICAL.md` — "every other document must derive from this one"; claims to supersede `audits/CONSTITUTION_COMPLIANCE.md`.
3. `RESEARCH_PROTOCOL.md` and `parameter_registry.yaml` — frozen scientific constants outside any revisable standard (§5 ¶6).
4. `audits/CONSTITUTION_COMPLIANCE.md` — audits an "implicit" constitution and creates the rule it enforces (§3 ¶6).
5. `PROGRAM_D_RESEARCH_STATE_v0.1.md`, `PROGRAM_D_MASTER_ROADMAP.md`, `docs/repository_v2.md`, `theory/*` instrument files with "Canonical" status lines.
6. `reproducibility.yaml` — freezes coefficients marked `[REJECTED]` elsewhere; cites a nonexistent HEAD (N-7).

**Do not defer this.** While Legacy artifacts sit in live paths asserting authority, `A-07` and `A-30` produce standing findings, and — more importantly — contributors will continue to follow them. The gap between "has no authority" and "is not being followed" is where governance systems actually fail.

Also resolve here: two hypothesis registers and two experiment-registration paths (N-9), and the T-01/T-02 non-distinguishability that `theory/HYPOTHESIS_DISCRIMINATION_MATRIX.md` already records — under S-7 that finding forces an Unknown and blocks independent support for either.

---

### M-7 · Assurance *(gate: M-5)*

Activate **G-5, G-6, G-8, G-11.** Conformance claims, audit, change and release, the check register itself. Promote the remaining checks; register every `MRP-xx`.

**Exit:** `A-39` reports full requirement coverage across all Active standards; the first conformance claim and first constitutionally valid audit are published.

---

### M-8 · Maturity *(gate: M-7)*

Activate **S-7, S-10, G-9, G-10.** Hypotheses, Principles, containment, conflict records. These are last because Hypotheses and Principles depend on the full inference chain, and containment and conflict machinery is only meaningful once there is something to contain or conflict.

---

### M-9 · Federation *(optional; gate: M-7)*

Per `07_EXTENSION_ARCHITECTURE.md` §2.6. Note the appealing property: federation is the natural solution to H-01, since an external partner supplies exactly the Independent reviewer the project lacks. Two open constraints: partners must accept §6 ¶1 provenance obligations, and multi-repository precedence remains a constitutional gap (F-1).

---

## 3. Critical path

```
H-01 (second human)
   ↓
M-0 adoption ──────────────────────────► [everything]
   ↓
M-2 ontology reconciliation
   ↓
M-3 foundation      O-1 G-1 G-2 G-3 G-4 G-13
   ↓
M-4 execution       S-1 S-3 S-4 S-8 G-7 G-12   ──► first valid Result
   ↓
M-5 inference       S-2 S-5 S-6 S-9            ──► first valid Claim state change
   ↓
M-7 assurance       G-5 G-6 G-8 G-11
   ↓
M-8 maturity        S-7 S-10 G-9 G-10

parallel, unblocked now:   M-1 (drafting, checks, CI repair, credentials, external anchors)
parallel, after M-3:       M-6 (legacy disposition)
```

**The single critical-path item is H-01.** Everything else is either parallelizable or downstream of it. It is worth stating baldly: a project with one human can build this entire system and activate none of it.

---

## 4. Sequencing guidance

**Do first, regardless of adoption timing:** M-1.6 credentials, M-1.5 CI repair, M-1.7 external anchors. All three are cheap, none needs authority, and M-1.7 gets more valuable the earlier it lands because it cannot retroactively secure past commits.

**Do not do:** activate a standard whose owned types O-1 has not registered; activate G-2 while D-1 is unresolved (H-03); begin confirmatory work before M-4; treat any current `artifacts/exp_*` output as Evidence.

**Resist:** activating standards faster than review capacity supports. Twenty-four Active standards with unmapped requirements and stale checks is worse than six Active standards fully verified — §12 ¶1 makes an unverifiable requirement a nonconformance, so over-activation manufactures nonconformance. If capacity is limited, govern less and govern it properly (H-11).

**Effort shape rather than dates.** Deliberately no calendar estimates: the binding resource is independent human review, whose availability is unknown until H-01 resolves. Relative sizes: M-1 large but parallelizable; M-2 moderate and well-defined; M-3 large (six standards, six attestations); M-4 moderate; M-5 moderate; M-6 large and unpleasant; M-7 moderate; M-8 small.
