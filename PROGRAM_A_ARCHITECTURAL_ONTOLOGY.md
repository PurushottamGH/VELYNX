# PROGRAM A — ARCHITECTURAL ONTOLOGY

**Purpose:** the minimum typed foundation for ownership, authority, lifecycle,
and operation closure. This document does not redesign ES-1, PA-3, science,
register values, or implementation. **Status:** proposed; it creates no B2,
B3, G4, or implementation authorization.

## 1. Root cause

`PROGRAM_A_REGISTER_DERIVATION_ROOT_CAUSE_ANALYSIS.md` identifies the recurring
defect: semantic definitions were classified as deferred values. A required
semantic object could therefore be named by a register but owned by neither the
specification nor freeze layer. The missing foundation is a closed ontology that
makes type, origin, owner, lifecycle, and permitted operation total.

## 2. Architecture ontology

Let `K` be the finite union in Section 3. An architectural object is
`o = (id, class, origin, owner, lifecycle, payload, refs)`. It is well formed
iff `class ∈ K`, its origin/owner/lifecycle equal the assignments for that
class, every reference is allowed by Section 7, and its operation is typed by
Sections 4–6. Anything not well formed is not an architectural object and may
not be consumed, verified, governed, or implemented.

Layers are ordered `L0 Reference → L1 Semantic Specification → L2 Freeze → L3
Implementation → L4 Verification → L5 Governance`. References move only to an
object in the same or an earlier layer, except that L5 may attest an earlier
object's identity without altering it. The ontology declaration is itself a
root L1 `SemanticContract`, owned by Architect, with no semantic predecessor.

## 3. Object-class table

| Class | Meaning | Origin | Lifecycle |
|---|---|---|---|
| `ReferenceArtifact` | Typed locator/provenance pointer; no semantic authority. | L0 | registered → superseded/retired |
| `SemanticProposition` | Declared architectural/scientific assertion. | L1 | drafted → approved → frozen → superseded/retired |
| `SemanticPredicate` | Extensional criterion/relation: e.g. support, contradiction, independence, extraction. | L1 | drafted → approved → frozen → superseded/retired |
| `SemanticContract` | Interface, invariant, state table, boundary rule; the ontology is this subtype. | L1 | drafted → approved → frozen → superseded/retired |
| `SemanticTemplate` | Constrained semantic form, including answer form; not merely a code string. | L1 | drafted → approved → frozen → superseded/retired |
| `Parameter` | Concrete value instantiating an already-defined semantic object, never its definition. | L2 | proposed → approved → frozen → superseded/retired |
| `DerivationArtifact` | Reproducible derivation of a parameter, consequence, or identity. | L2 | recorded → verified → frozen/retired |
| `ImplementationArtifact` | Source, configuration, build, or executable realization of frozen inputs. | L3 | implemented → verified → released/retired |
| `EvidenceArtifact` | Immutable observation, snapshot, trace, fixture, or output; provenance, not authority. | L4 | captured → verified → retained/retired |
| `VerificationArtifact` | Test, audit, replay, proof obligation, or verdict over prior-layer objects. | L4 | planned → executed → recorded → superseded/retired |
| `GovernanceArtifact` | Decision, approval, freeze, status, or pin that records authority over a prior object. | L5 | proposed → recorded → effective → superseded/retired |

The classes are necessary and sufficient: semantic definitions must be distinct
from parameters; implementation, evidence, verification, and governance have
non-interchangeable authorities; and references must be typed so a locator
cannot impersonate authority.

## 4. Authority matrix

| Class | Owner | Creator | Approver | Consumers | Freeze point |
|---|---|---|---|---|---|
| Reference | Architect | Architect/designated curator | Architect | allowed layers | content-addressed registration |
| Semantic classes | Architect | Architect | ScientificAuditor if scientific/freeze-relevant; Reviewer if implementation-only | L2–L5 | approved revision; G4 where T1 scoped |
| Parameter | ScientificAuditor | ScientificAuditor | ScientificAuditor; ReleaseManager only records pin | L3–L5 | B2-authorized value and G4 pin |
| Derivation | ScientificAuditor | designated derivation author | ScientificAuditor | L2, L4, L5 | verified record |
| Implementation | Builder | Builder | Reviewer | L4–L5 | reviewed release revision |
| Evidence | capture-domain verifier | designated capture process | RepositoryVerifier or ScientificAuditor | L4–L5 | immutable capture identity |
| Verification | domain verifier | named verifier | named verifier for the result | L5 | recorded verdict identity |
| Governance | named governing role | that direct role | no proxy approval | L5 | direct approval or signed pin |

Ownership is singular. Approval authorizes a lifecycle transition but never
transfers ownership; a governance artifact records authority but cannot become
semantic authority.

## 5. Allowed operations

`Create(a,c,p)` exists only in `origin(c)` and only for `c`'s creator.
`Read(a,o)` exists only for an allowed consumer. `Transform(a,o,d)` exists only
for the creation authority, before freeze, and yields a same-class successor:
class, origin, and owner cannot change. A post-freeze change is `Create` of a
new revision, not mutation.

`Freeze(a,o)` exists only for an approved object at its stated freeze point and
produces an immutable identity. `Verify(v,o)` creates a verification artifact
but cannot modify `o`. `Reference(o,r)` exists only for Section 7 edges and
transfers no authority. `Implement(b,o)` creates an implementation artifact
only from frozen semantic/parameter inputs and only after its governance gate.

Thus L4/L5 creation of a semantic class, implementation from an untyped or
unfrozen object, and governance mutation of a semantic object are undefined
operations and architectural errors.

## 6. Type system

```
Class ::= Reference | Proposition | Predicate | Contract | Template | Parameter
        | Derivation | Implementation | Evidence | Verification | Governance
Create    : Actor × Class × Payload → Object[Class]       (origin class only)
Read      : Actor × Object[c] → Payload[c]
Transform : Actor × Object[c] × Delta[c] → Object[c]     (pre-freeze only)
Freeze    : Actor × Object[c] → FrozenObject[c]
Verify    : Verifier × FrozenObject[c] → VerificationArtifact
Reference : Object[c] × Object[d] → Ref[c,d]             (Section 7 only)
Implement : Builder × FrozenObject[Semantic|Parameter] → ImplementationArtifact
```

There is no coercion from reference, evidence, verification, governance, or
implementation to a semantic class. `Parameter[definition_id]` is inhabited
only when its L1 definition exists and is frozen. The historic form “a deferred
value supplies its own semantics” is therefore ill typed.

## 7. Interaction matrix

`R` means a typed reference is allowed; all omitted edges are forbidden.

| From \ To | Ref | Semantic | Parameter | Derivation | Implementation | Evidence | Verification | Governance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Reference | R | — | — | — | — | — | — | — |
| Semantic | R | R, acyclic | — | — | — | — | — | — |
| Parameter | R | R | R, acyclic | R | — | — | — | — |
| Derivation | R | R | R | R, acyclic | — | — | — | — |
| Implementation | R | R | R | R | R, acyclic | — | — | — |
| Evidence | R | — | — | — | R, identity only | R, acyclic | — | — |
| Verification | R | R | R | R | R | R | R, acyclic | — |
| Governance | R | R, identity only | R, identity only | R | R | R | R | R, acyclic |

AL-1 through AL-4 need no new substantive law. Their smallest completion is:
**every operand, authority, dependency, and output named by an AL law must be a
well-formed ontology object; an operation without a signature is forbidden.**
No AL-5 is necessary.

## 8. Formal closure proof

**Theorem.** Sections 2–7 close the named failure modes.

*Proof.* `K` is finite and `ArchitecturalObject` requires membership in `K`, so
an unclassified item cannot enter any architecture operation: no hidden object
class or semantic object. Sections 3–4 assign exactly one origin and owner per
class: no orphan or duplicate authority. Only L1 creates semantics: no
implementation-, verification-, or governance-created semantics. Section 7
types all references, admits only same-or-earlier-layer edges, and requires
acyclic same-class graphs: no upward dependency, circular authority, or hidden
selector. Parameters require a frozen definition identifier, so values cannot
silently supply undefined meanings. Frozen changes create new revisions, not
hidden transformations. Therefore the model is closed. ∎

## 9. Historical replay

| Failure | Result under this ontology |
|---|---|
| Register Finding 1 | Always-false support/empty extraction fail unless a L1 predicate defines their extension; a parameter cannot substitute. |
| Register Finding 2 | Scope, quantifier, normalization, granularity, span, and discourse are L1 predicate/template content, not hidden selector choices. |
| Root Cause Analysis | The formerly unowned semantic-definition layer has L1 origin and Architect owner. |
| Architecture Validation | Every boundary, invariant, and import rule is a `SemanticContract`, not informal authority. |
| Ownership Totality | The total `owner : K → Role` mapping rejects zero or multiple owners. |
| Orphan Semantic Authority | A semantic artifact without L1 origin, owner, and required approval is not well formed. |

## 10. Adversarial search

Attempt to introduce a `ConfidenceOverridePolicy` that changes a tier after
PA-3. It cannot be a parameter: no frozen definition licenses it; cannot be
implementation: implementation only realizes frozen inputs; cannot be evidence,
verification, governance, or reference: none has semantic creation authority.
As a new class it is absent from `K` and rejected. As a semantic contract it
must be created in L1, owned by Architect, approved/frozen through the existing
route, and must satisfy the existing tier-coupling contract. There is no hidden
insertion path.

## 11. Final verdict

**PASS WITH OBSERVATIONS.** This is a mathematically closed architecture-level
foundation: every architectural object has one type, origin, owner, lifecycle,
and permitted operation set. Observation: this proposed artifact does not
perform any existing sign-off, freeze, implementation, or gate action; their
current governance status is unchanged.
