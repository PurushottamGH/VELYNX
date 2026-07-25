# Legacy Disposition — discharging §4 ¶5 distinguishability at minimum cost

- **Status:** Draft
- **Scope:** Every version-controlled artifact that is not activated in the Governance Registry at adoption
- **Responsibility:** Specify how Legacy content is made distinguishable from Active requirements
- **Authority source:** None. This record describes engineering actions; it authorizes no transition.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. The obligation, and its actual size

§14: at adoption, every existing Normative artifact not activated in the Registry becomes Legacy and has no normative authority. That happens automatically and requires no work.

§4 ¶5 adds the part that does require work: Legacy content "MUST remain distinguishable from Active requirements."

Measured surface (see `02_PREADOPTION_VERIFICATION.md` §4): ~40 live-path artifacts assert authority or frozenness, out of 166 files matching the lexeme scan. Banner-editing all of them is days of work on artifacts that §14 has already neutralised, and it is not what §4 ¶5 asks for. §4 ¶5 asks that a reader be able to tell Active from not-Active.

**The load-bearing insight:** after adoption the Registry lists everything Active — and at adoption that list is *the Constitution and nothing else*. Distinguishability is therefore achievable by one clear statement plus a complete inventory, not by 40 edits. Banners are needed only where a reader would plausibly be misled before reaching either.

---

## 2. Three tiers

| Tier | Criterion | Action | Count |
|---|---|---|---|
| **T1** | Titled or self-described as constitutional, canonical, or absolute, in a live path — a reader could mistake it for the governing document | move + banner + index entry | 7 |
| **T2** | Imposes requirements in a live path but does not claim supremacy | index entry + one-line banner | ~33 |
| **T3** | Everything else: `archive/**`, agent configs, audits, evidence, generated output | index entry only, by directory rule | remainder |

### Tier 1 — move and banner

| Path | Destination |
|---|---|
| `theory/PROGRAM_D_CONSTITUTION.md` | `archive/legacy_normative/` |
| `PROGRAM_D_CANONICAL.md` | `archive/legacy_normative/` |
| `PROGRAM_D_MASTER_ROADMAP.md` | `archive/legacy_normative/` |
| `PROGRAM_D_RESEARCH_STATE_v0.1.md` | `archive/legacy_normative/` |
| `RESEARCH_PROTOCOL.md` | `archive/legacy_normative/` |
| `audits/CONSTITUTION_COMPLIANCE.md` | `archive/legacy_normative/` |
| `p1/specifications/milestone-1-gpt56.md` | **stays in place**, banner only |

The last is an exception on purpose: `p1/tooling/p1_os` imports its schema decisions, so moving it breaks working code for no compliance gain. A banner discharges §4 ¶5; §14 has already removed its authority.

Moving files is engineering, not a scientific transition: content is preserved in history (§8 ¶2), and no scientific record changes state. No Decision is required (dossier interpretation 4.4).

`README.md` cross-references to moved paths must be updated in the same change, or the index becomes the only navigation route.

### Tier 2 — banner only

Identified by the lexeme scan; the notable members are `theory/HYPOTHESIS_REGISTER.md`, `theory/PHENOMENON_REGISTRY.md`, `theory/SCIENTIFIC_EXECUTION_SPEC.md`, `theory/STATISTICAL_ANALYSIS_SPEC.md`, `theory/PROGRAM_D_SPECIFICATION.md`, the five files under `theory/preregistrations/`, `experiments/specs/EXP1_DATASET_SPEC.md`, `evidence/certifications/*`, `docs/EXECUTION_GUIDE.md`, `docs/EXECUTION_ORDER.md`, `docs/ARCHITECTURE_MAP.md`, `p1/methodology/STATUS_LIFECYCLE.md`, `p1/architecture_decisions/*`.

`theory/preregistrations/**` deserves separate mention. These are not Registered protocols under §2, because registration is a transition that never occurred and §13 ¶4 forbids retroactive relabelling. Their banner must say so explicitly, otherwise the most likely future error in this repository is treating one of them as satisfying §5 ¶3. `EXPERIMENT_ZERO_PREREGISTRATION.md` must be re-registered under RS-1 before its execution begins.

Two hypothesis registers exist (`theory/HYPOTHESIS_REGISTER.md` and the `theory/foundation/hypothesis/*` set). Under §4 ¶4 conflicting same-level requirements are both nonconforming; as Legacy, neither is a requirement, so the contradiction is defused rather than resolved. Do not attempt to reconcile them before adoption.

### Tier 3 — directory rule

One index entry per directory, stating the rule rather than enumerating files: `archive/**`, `docs/audits/**`, `evidence/**`, `artifacts/**`, `.agents/**`, `.opencode/**`, `.commandcode/**`, `audits/**`, `research/**`. Agent-configuration files matter here — several instruct models in reviewer-shaped roles, and §4 ¶4 bars automation from supplying independent review. The index should say so once, plainly.

---

## 3. Banner text

Verbatim, at the top of the file, before the title. Machine-detectable by exact first line.

```markdown
> **LEGACY — no normative authority.** This artifact is not activated in
> `GOVERNANCE_REGISTRY.yaml`. Under `REPOSITORY_CONSTITUTION.md` §14 it became
> Legacy at adoption, and under §4 ¶5 it has no normative authority. Any
> statement here that reads as a requirement, or that describes itself as
> canonical, absolute, frozen, or authoritative, has no force. Content is
> retained for history and diagnosis (§12 ¶2). Before any part of it is
> relied upon, it MUST satisfy §4 and be activated in the Registry.
```

Additional line for `theory/preregistrations/**`:

```markdown
> **Not a Registered protocol.** §2 defines a Registered protocol as one whose
> registration transition occurred before its governed execution began. That
> transition never occurred, and §13 ¶4 forbids supplying it retroactively.
> Executions described here are exploratory working output permanently.
```

---

## 4. `governance/LEGACY_INDEX.md` — required structure

Not a Normative artifact: it is an index under §11 ("navigation and non-normative description"), so it needs no Registry entry.

1. **Basis** — §14 and §4 ¶5 quoted, with the date and revision at which the classification was made.
2. **What is Active** — a pointer to the Registry, stating that at adoption the Active set is the Constitution and nothing else.
3. **Tier 1 table** — original path, new path, moving commit, one line on what it used to assert.
4. **Tier 2 table** — path and whether the banner is applied.
5. **Tier 3 rules** — directory-level statements, with the agent-configuration note.
6. **Completeness statement** — the method used to generate the inventory, its scope, and what it would miss. A Normative artifact that neither declares authority nor matches the lexeme list is the known false negative; say so rather than claiming completeness.
7. **Reactivation route** — §4 must be satisfied before any Legacy artifact carries force again.

---

## 5. Verification

| Question | Route |
|---|---|
| Does every Tier-1/Tier-2 file carry the banner? | automated: first-line match against the index |
| Is the index complete against the tree? | automated sweep for candidates + a recorded false-negative statement |
| Does any live-path artifact still read as Active? | manual, `P-L1`: read the first screen of each Tier-1 and Tier-2 file as a first-time reader; the finding is recorded |
| Do Registry and index disagree about what is Active? | automated: index's Active set must equal `active_domain_standards` plus the Constitution |

`P-L1` is the named manual procedure §12 ¶4 requires for the part that is not mechanically decidable — whether a document *reads* as authoritative. A lexeme scan cannot answer that, and it should not claim to.

---

## 6. What is deliberately not done

- **No deletion.** §8 ¶2 forbids deleting scientific records for being superseded or inconvenient, and §12 ¶2 permits retaining nonconforming content for diagnosis. Legacy is retained, labelled.
- **No rewriting of Legacy content to conform.** That converts a clean classification into an unbounded editing project, and edited Legacy text risks reading as Active again.
- **No resolution of contradictions between Legacy artifacts.** As Legacy, they impose nothing; there is no conflict to resolve. Reconciliation happens only if and when one is proposed for activation under §4.
