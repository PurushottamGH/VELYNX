# Extension Architecture — twenty-year growth without redesign

- **Status:** Draft
- **Scope:** The extension points by which P1 accommodates new domains, artifacts, repositories, stewards, reviewers, and federation without architectural redesign
- **Responsibility:** Identify each anticipated growth axis, the mechanism that absorbs it, and the conditions that would nonetheless force redesign
- **Authority source:** None. This record has no normative authority.
- **Governing artifact:** `REPOSITORY_CONSTITUTION.md` v1.2.0 (Draft)
- **Version:** 0.1.0

---

## 1. What "without redesign" means

A design claim about twenty years is worthless unless it is falsifiable. So the claim here is specific:

> **Extension claim.** Each growth axis in §2 can be absorbed by (a) adding a Registry entry, (b) adding a Domain standard satisfying the existing interface, (c) adding a check, or (d) adding an authority assignment — without amending the Constitution, without changing the Domain Standard Interface, and without altering any existing standard's jurisdiction.

Section 4 states the conditions that would **falsify** this claim. A design that cannot say what would break it is not an architecture; it is an aspiration.

---

## 2. Growth axes

### 2.1 New scientific domains
**Mechanism:** a new Domain standard under `domain_standards/scientific/`, satisfying `04_DOMAIN_STANDARD_INTERFACE.md`, activated per §4 ¶2.
**Why no redesign:** §2 defines a Domain standard as governing "one declared scientific, governance, or engineering domain" — an open set. §5 ¶6 forbids any methodology from being constitutional. The interface constrains form only.
**Constraint:** the new domain must own object types that no Active standard owns (§9 ¶1), or refine an existing type only under an explicit delegation recorded in the Registry (§4 ¶2). In practice this means new domains usually add *new* types rather than reinterpreting existing ones — e.g. an ML domain owns `training_run`, not a private variant of `result`.
**Cost:** one activation dossier, one attestation, an ontology impact statement.

### 2.2 New governance artifacts
**Mechanism:** a new governance Domain standard, or a version bump to an existing one.
**Why no redesign:** the jurisdiction partition is a partition of *transitions over object types*, not a fixed list of policies. A genuinely new governance concern introduces a new object type and takes a new region of the partition.
**Constraint:** if a proposed artifact owns no new object type, it is a refinement of an existing standard and belongs inside it (§4 ¶2, §11 ¶1). This test is what keeps the governance stack from accreting overlapping policies — the failure visible in the current repository's three competing constitutions.

### 2.3 New repositories
**Mechanism:** each repository carries its own Constitution instance and Registry, or a shared Constitution is referenced with a repository-scoped Registry.
**Why no redesign:** §2's Scope definition includes "population, environment, conditions, versions, and time interval," so a Registry entry can be scoped to a repository. Cross-repository references use G-7 custody manifests, which already handle content-addressed external artifacts.
**Real limitation:** §2 pins the Registry to `GOVERNANCE_REGISTRY.yaml`, a *repository-relative* path. Two repositories therefore have two Registries with no defined relationship, and §4's precedence order says nothing about cross-repository conflict. Multi-repository governance is **not** a solved extension; it is a known gap requiring either a federation standard (§2.6) or a constitutional amendment. Stated plainly rather than papered over.

### 2.4 Multiple stewards
**Mechanism:** `authority_assignments.constitutional_steward` is already a list in `GOVERNANCE_REGISTRY.yaml`. Multiple stewards are added as authority assignments under G-3.
**Why no redesign:** §13 requires "at least one constitutional steward," not exactly one.
**Design obligation:** G-3 must define quorum and disagreement handling for co-stewards. §4 ¶4's conflict rule addresses conflicting *requirements*, not conflicting *stewards* — two stewards holding the same jurisdiction who disagree produce a deadlock the Constitution does not resolve. G-3 must therefore either (a) assign non-overlapping jurisdictions per steward, or (b) define a quorum rule. Option (a) is preferable: it uses the same disjointness discipline as the rest of the stack, and avoids inventing a voting mechanism the Constitution never contemplated.
**Succession is mandatory, not optional.** A single steward with no successor is an unrecoverable single point of failure over twenty years (risk R-17).

### 2.5 Distributed governance
**Mechanism:** delegation chains under G-3, each recording subject, Scope, recipient, permitted transitions, and limits (§4 ¶4), with sub-delegation containment enforced by `A-37`.
**Why no redesign:** §4 already models authority as a tree rooted at the constitutional steward. Distribution is depth in that tree.
**Constraint:** delegation can never enlarge (§4 ¶4). Distributed governance in P1 means distributed *exercise* of authority, never distributed *sources* of it. A working group can be delegated activation authority for one scientific domain; it cannot acquire authority to amend the Constitution.

### 2.6 Federated research
**Mechanism:** a Federation Domain standard owning `external_partner`, `shared_protocol`, and `external_attestation`, plus G-7 custody arrangements for artifacts held by partners.
**Why partially unsolved:** three constitutional requirements bind hard here.
- §2's Independent reviewer must be "an identified human" — workable across institutions, and in fact federation is the most natural solution to P1's current single-human problem.
- §6 ¶1 requires reproduction-material identification for Evidence; a partner unwilling or unable to share code, configuration, data, environment, and randomness inputs cannot supply admissible Evidence. Federation therefore constrains partner selection, not merely paperwork.
- §7 ¶1's Result immutability and §8 ¶2's retention must hold for partner-held Results, which requires either mirroring or a custody arrangement with recovery procedures the partner will actually honour.
**Assessment:** federation is an extension the architecture *supports* but does not yet *specify*. It needs one new standard and no constitutional change — provided partners accept §6's provenance obligations.

### 2.7 AI reviewers
**Mechanism:** AI review is a first-class **input** at stage V4 (adversarial review) and may implement any check in G-11's register.
**Hard ceiling:** §4 ¶4 — "Automated systems MAY propose, check, or apply an already-authorized transition; they MUST NOT supply human authority or independent review." §2 defines an Independent reviewer as "an identified human." §13 requires two identified humans for adoption.
**What this permits, concretely:** AI systems may draft standards, run every check, attempt refutation, produce finding sets, propose transitions, and apply transitions a human has already authorized. Their findings are recorded and the human attestation states which were examined (§13 ¶2 as amended by A-1).
**What it forbids:** counting AI output as an attestation, as independent review, or as human authority — in any quantity, at any capability level. This is a *structural* limit, not a capability judgement, and increasing model capability does not relax it. Changing it requires amending §2, §4, and §13 together, and would dissolve the guarantee those clauses jointly provide. Recorded as H-07.
**Note on this project specifically:** the repository's review history is populated by model names — Terra, GPT-5.5, Sonnet 5, DeepSeek, Nemotron, Gemini — appearing in reviewer-shaped roles. Under §4 ¶4 none of that constitutes review. The design accommodates their continued use as adversarial input while being explicit that it does not substitute for V6.

### 2.8 Human reviewers
**Mechanism:** authority assignments and conflict-of-interest declarations under G-3; attestations under G-4.
**Scaling property:** review capacity is the pipeline's binding constraint (`06_VERIFICATION_ARCHITECTURE.md` §6). Adding reviewers is the highest-leverage change available to the project — higher than any automation.
**Constraint:** §2's independence test is per-review, not per-person. A reviewer independent for one change may be conflicted for the next. G-4 must therefore record independence *per attestation*, which it does.

### 2.9 Automated verification growth
**Mechanism:** new checks registered in `automation/CHECK_REGISTER.yaml` with mandatory FP/FN disclosure.
**Why no redesign:** §12 ¶3's "SHOULD enforce every mechanically decidable requirement" is open-ended and additive. New checks strengthen V1 without touching any standard.
**Constraint:** a new check may *not* silently expand its evidentiary reach; §12 ¶4 confines it to the criteria, revision, and Scope it actually assessed.
**Growth expectation:** the four structurally-undetectable classes in `05_AUTOMATION_ARCHITECTURE.md` §5 — backdating, pre-baseline history rewriting, forged records, off-repository work — are addressable only by external anchors (signing, mirrors, third-party timestamping, platform audit logs). Adding those is the highest-value automation work available, and none of it requires a governance change.

### 2.10 Future constitutional amendments
**Mechanism:** §13's seven-element dossier, steward approval, Independent reviewer attestation, one Atomic change.
**Why the architecture survives amendment:** every standard records the `standard_version` under which each record was created, and §13 ¶4 forbids retroactive alteration of prior scientific records' meaning or outcome. So amendment changes future behaviour, not history.
**Amendment-fragile surfaces** — the places where a Constitution change propagates widely, and which therefore deserve extra care:
| Surface | Why fragile |
|---|---|
| §2 object kinds | Adding or removing a kind forces an O-1 change and possibly a new standard to own it (§9 ¶1) |
| §4 authority order | Would invalidate the peer-level assumption on which all 24 standards rest |
| §9 lifecycle elements | Adding a tenth element makes every Active standard's lifecycle definition incomplete simultaneously |
| §12 ¶1 traceability | Changing the three permitted trace targets invalidates every conformance claim |
| §13 ¶2 attestation content | Invalidates prospective attestation templates; prior attestations retain their version |
Each is manageable, but each requires a migration plan naming every affected artifact **in the same Atomic change** — exactly as `04_DOMAIN_STANDARD_INTERFACE.md` §6 requires for interface changes, and for the same reason: otherwise a revision exists in which Active artifacts lack required elements, and §4 ¶1 strips their authority all at once.

---

## 3. Extension points, enumerated

The concrete places designed to be extended, so that extension does not require inventing a mechanism:

| # | Extension point | Location | Extends by |
|---|---|---|---|
| X-1 | Object type register | `ontology/TYPE_REGISTER.yaml` | adding a type + naming its owning standard |
| X-2 | Relationship kinds | `ontology/RELATIONSHIPS.yaml` | adding an edge kind with endpoint type constraints |
| X-3 | Identifier namespaces | `ontology/IDENTIFIERS.yaml` | allocating a namespace; never reusing a retired id |
| X-4 | Domain standards | `domain_standards/{class}/` | one activation dossier per standard |
| X-5 | Domain classes | `domain_standards/` subdirectories | adding a class directory; `engineering/` already reserved and empty |
| X-6 | Check register | `automation/CHECK_REGISTER.yaml` | adding a check with FP/FN disclosure |
| X-7 | Manual procedures | the `MRP-xx` register | adding a procedure; required whenever a new non-decidable MUST appears |
| X-8 | Authority assignments | `governance/authority/` | assignment + succession |
| X-9 | Delegations | `governance/delegations/` | five-element record, contained in its parent |
| X-10 | Digest algorithms | G-7's algorithm register | registering a new algorithm; deprecating an old one without invalidating history |
| X-11 | Custody backends | `custody/` manifests | new backend with identity, provenance, recovery procedure |
| X-12 | Record stores | repository root | new top-level store + `_BOUNDARY.yaml` + owning standard |
| X-13 | Scope dimensions | jurisdiction declarations | adding a controlled dimension to sharpen `A-04` |
| X-14 | External anchors | G-11 + G-7 | signing, timestamping, mirroring — additive, no governance change |

Fourteen extension points, none requiring a constitutional amendment, and none requiring an existing standard to change jurisdiction.

---

## 4. What would force redesign

The falsification conditions for the extension claim. If any of these occurs, the architecture — not merely a standard — must be reconsidered.

**F-1 — Multi-repository governance becomes a primary requirement.** §2's repository-relative Registry pin and §4's silence on cross-repository precedence mean two Registries have no defined relationship. Federation via custody manifests handles *artifacts*; it does not handle *conflicting Active requirements across repositories*. This is the most likely redesign trigger, and it is a constitutional gap, not an architectural one.

**F-2 — Two standards must genuinely co-own an object type.** §9 ¶1's "exactly one" is the load-bearing assumption behind the whole partition. If a real case arises where two standards must jointly govern one type in one scope — plausible for a type spanning a scientific and an engineering concern — the partition model breaks and §9 requires amendment.

**F-3 — Real-time or high-frequency scientific transitions.** The pipeline assumes human review per governed transition. A domain producing thousands of transitions per day (continuous evaluation, online learning, automated experimentation) cannot route each through V6. §4 ¶4 forbids automation supplying the human authority, so the resolution must be to redefine the *granularity* of a governed transition — batching many executions under one authorized transition — which is a change to what "transition" means and touches §9.

**F-4 — Independent review becomes structurally unavailable.** If the project cannot sustain two humans, the choice is between a permanently dormant governance system and amending §2/§13 to weaken independence. Both are bad; the second is worse, because it retains the appearance of the guarantee. Currently active as H-01.

**F-5 — The Constitution's own requirements become individually unaddressable at scale.** `A-39` coverage depends on clause identifiers the Constitution does not have (finding F-19). At the present size a hand-curated map works. At three times the size it will not, and coverage will silently decay. Adding clause IDs is a cheap amendment now and an expensive migration later.

**F-6 — Retention cost exceeds the project's means.** §7 ¶4 and §8 ¶1 make retention of Results, Negative Results, and Unknowns permanent, with no expiry mechanism. Over twenty years, with large artifacts, this is a real financial commitment. §6 ¶5 provides only for *recording* loss, not for authorizing it. If retention becomes infeasible, the correct path is a constitutional amendment defining bounded, recorded, reviewed disposal — not quiet deletion.

---

## 5. Twenty-year durability notes

Practical matters that determine whether this survives, listed because they are the things that actually kill long-lived systems.

**Formats.** Markdown and YAML are plain text, diffable, and readable without tooling. That is the right choice for a twenty-year horizon and should not be traded for a database. The *tooling* (Pydantic v2, JSON Schema draft version, Python version) will churn; records must remain readable when it does. Therefore: schemas validate records, but no record may be *unreadable* without its validator.

**Identifiers.** Never reused, never renumbered, never repurposed. An identifier scheme that survives is one where a citation written in year one still resolves in year twenty. Retired ids stay retired (X-3).

**Digests.** At least one registered algorithm will be considered broken within twenty years. G-7's versioned algorithm register and linked re-digest procedure handle this without invalidating history — provided re-digesting is recorded as a new manifest linked to the prior one, never as an edit.

**Institutional memory.** The most probable failure is not mechanical but human: a successor who does not understand why the separation rules exist and consolidates them for convenience. The mitigation is that every standard states its constitutional citation and its failure modes, and every design decision here states its rationale and rejected alternatives. A future maintainer should be able to reconstruct *why*, not merely *what*.

**The dormancy property.** The system is designed to be correct while inert. If P1 pauses for three years and resumes, nothing has silently expired into a false Active state: Draft artifacts remain Draft, unavailable checks report `NOT_VERIFIED`, and no transition occurred without a record. That property is worth more than any efficiency this design gives up to obtain it.
