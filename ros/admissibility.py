"""P1 Research Operating System — the admissibility kernel (invariant K2).

No human decides whether a result may bear a scientific claim. This module
computes it, from the run manifest and the repository's registration state, and
the answer is attached to the record.

Every rule here is traceable to a frozen artifact. Nothing is invented:

* **Article L-11** — implementation against an unregistered lock produces *no
  admissible evidence*. This is the dominant rule: with
  ``GOVERNANCE_REGISTRY.yaml`` carrying ``active_domain_standards: []`` and null
  attestations, every run in the repository today is ``ENGINEERING_ONLY``.
* **Lock R1 acceptance** — "a D2 run is mechanically refused by the confirmatory
  decision path; incomplete runs cannot reach confirmatory-admissible".
* **Lock E1 acceptance** — "no result advances past exploratory-admissible
  without a hash-matched protocol frozen before the first run".
* **Constraint C-a** — unit- and edge-level claims require D0/D1 runs with the
  relevant stream complete; population claims require coverage disclosure.
* **Constraint C-b** — the collection non-interference test is defined for D0
  only; D1 asserts it within a fixed layout; D2 may never be offered as
  confirmatory evidence.

The kernel is a pure function of its inputs. It has no I/O, no clock, and no
configuration, so its verdict is reproducible and reviewable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Tier(str, Enum):
    """Admissibility tiers, ordered from least to most admissible."""

    INADMISSIBLE = "inadmissible"
    ENGINEERING_ONLY = "engineering-only"
    EXPLORATORY = "exploratory-admissible"
    CONFIRMATORY = "confirmatory-admissible"

    @property
    def rank(self) -> int:
        return _TIER_ORDER.index(self)

    # All four comparisons are defined explicitly. `Tier` subclasses `str`, so
    # any operator left undefined here silently falls through to *alphabetical*
    # string comparison — under which "confirmatory-admissible" sorts below
    # "exploratory-admissible" and the strongest tier reads as the weakest.
    # `functools.total_ordering` cannot help: it only fills in operators the
    # class does not already inherit, and `str` supplies all of them.
    def __lt__(self, other: object) -> bool:  # type: ignore[override]
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank < other.rank

    def __le__(self, other: object) -> bool:  # type: ignore[override]
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank <= other.rank

    def __gt__(self, other: object) -> bool:  # type: ignore[override]
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank > other.rank

    def __ge__(self, other: object) -> bool:  # type: ignore[override]
        if not isinstance(other, Tier):
            return NotImplemented
        return self.rank >= other.rank


_TIER_ORDER = (
    Tier.INADMISSIBLE,
    Tier.ENGINEERING_ONLY,
    Tier.EXPLORATORY,
    Tier.CONFIRMATORY,
)


class Determinism(str, Enum):
    """Determinism tiers from the Lock R1 manifest."""

    D0 = "D0"  # bit-exact
    D1 = "D1"  # exact within a fixed layout
    D2 = "D2"  # neither


class ClaimScope(str, Enum):
    """The scope at which a claim is asserted, per Constraint C-a."""

    OBJECT = "object"  # unit- or edge-level
    POPULATION = "population"
    RUN = "run"  # apparatus / methodological claims


@dataclass(frozen=True)
class Manifest:
    """The decision-relevant subset of a Lock R1 run manifest.

    Only fields the kernel reads are modelled. A real manifest carries more; the
    kernel deliberately depends on as little as possible so that a manifest
    schema change does not silently change an admissibility verdict.
    """

    run_id: str
    determinism: Determinism
    #: Was the working tree clean and the commit tracked at allocation time?
    clean_checkout: bool
    #: Did the run reach its declared end without truncation?
    complete: bool
    #: A protocol record was frozen and hashed *before* tick 0 of the first run.
    protocol_frozen_before_first_run: bool
    #: The frozen protocol hash still matches the protocol on disk.
    protocol_hash_matched: bool
    #: `stream_meta` discloses drop ledger, sampling rule and omitted mass.
    coverage_disclosed: bool
    #: The streams the intended claim reads are complete for this run.
    stream_complete_for_scope: bool
    #: Faults were emitted rather than suppressed (Article L-3).
    faults_intact: bool = True


@dataclass(frozen=True)
class Registration:
    """Repository registration state, read from ``GOVERNANCE_REGISTRY.yaml``.

    Article L-11 makes this a precondition of *all* admissibility, which is why
    it is a separate input rather than a manifest field: it is a property of the
    repository at the time of the run, not of the run.
    """

    #: The governing lock/constitution is entered in the registry with a status,
    #: jurisdiction and authority assignment.
    lock_registered: bool
    #: A constitutional steward is assigned.
    steward_assigned: bool
    #: Adopter attestation present.
    adopter_attested: bool
    #: *Independent* reviewer attestation present — a different person.
    independent_reviewer_attested: bool

    @property
    def active(self) -> bool:
        return (
            self.lock_registered
            and self.steward_assigned
            and self.adopter_attested
            and self.independent_reviewer_attested
        )

    def missing(self) -> list[str]:
        gaps = []
        if not self.lock_registered:
            gaps.append("lock not entered in GOVERNANCE_REGISTRY.yaml")
        if not self.steward_assigned:
            gaps.append("no constitutional steward assigned")
        if not self.adopter_attested:
            gaps.append("adopter attestation is null")
        if not self.independent_reviewer_attested:
            gaps.append("independent reviewer attestation is null")
        return gaps


@dataclass(frozen=True)
class Verdict:
    """The computed admissibility of a run for an intended claim scope."""

    tier: Tier
    reasons: tuple[str, ...] = field(default=())
    #: Rules that would have to change for the tier to rise, most binding first.
    ceilings: tuple[str, ...] = field(default=())

    @property
    def admissible(self) -> bool:
        """True when the run may bear a scientific claim at any tier."""
        return self.tier >= Tier.EXPLORATORY

    def permits(self, required: Tier) -> bool:
        return self.tier >= required

    def explain(self) -> str:
        lines = [f"tier: {self.tier.value}"]
        for reason in self.reasons:
            lines.append(f"  - {reason}")
        return "\n".join(lines)


def assess(
    manifest: Manifest,
    registration: Registration,
    scope: ClaimScope = ClaimScope.POPULATION,
) -> Verdict:
    """Compute the admissibility tier of a run for an intended claim scope.

    Pure. The verdict is the *minimum* permitted by every applicable rule, and
    every rule that bound the result is reported, not only the first.
    """
    reasons: list[str] = []
    ceilings: list[str] = []

    # ---- Article L-11. Registration gates everything. -------------------
    if not registration.active:
        gaps = "; ".join(registration.missing())
        return Verdict(
            tier=Tier.ENGINEERING_ONLY,
            reasons=(
                f"Article L-11: governing lock is not registered ({gaps}). "
                "Implementation may proceed as engineering-only work producing no "
                "admissible evidence.",
            ),
            ceilings=("Article L-11 registration",),
        )

    # ---- Faults and provenance are preconditions of any tier. -----------
    if not manifest.faults_intact:
        return Verdict(
            tier=Tier.INADMISSIBLE,
            reasons=(
                "Article L-3: FAULT tier is undroppable; a suppressed fault is a "
                "fabricated healthy run.",
            ),
            ceilings=("Article L-3 fault integrity",),
        )
    tier = Tier.CONFIRMATORY

    def cap(limit: Tier, reason: str, ceiling: str) -> None:
        nonlocal tier
        reasons.append(reason)
        ceilings.append(ceiling)
        if limit < tier:
            tier = limit

    if not manifest.clean_checkout:
        cap(
            Tier.EXPLORATORY,
            "Lock R1 failure mode: dirty or untracked code at allocation. "
            "Provenance cannot be established.",
            "clean checkout",
        )

    # ---- Lock E1. Preregistration gates the exploratory ceiling. --------
    if not manifest.protocol_frozen_before_first_run:
        cap(
            Tier.EXPLORATORY,
            "Lock E1: no result advances past exploratory-admissible without a "
            "protocol frozen before the first run.",
            "protocol frozen before first run",
        )
    elif not manifest.protocol_hash_matched:
        cap(
            Tier.EXPLORATORY,
            "Lock E1: the frozen protocol hash does not match the protocol on "
            "disk; post hoc choices cannot appear preregistered.",
            "protocol hash match",
        )

    # ---- Lock R1. Determinism and completeness gate confirmatory. -------
    if manifest.determinism is Determinism.D2:
        cap(
            Tier.EXPLORATORY,
            "Lock R1 / Constraint C-b: a D2 run is mechanically refused by the "
            "confirmatory decision path.",
            "determinism tier D2",
        )
    if not manifest.complete:
        cap(
            Tier.EXPLORATORY,
            "Lock R1: incomplete or truncated runs cannot reach " "confirmatory-admissible.",
            "run completeness",
        )

    # ---- Constraint C-a. Scope-conditional stream requirements. ---------
    if scope is ClaimScope.OBJECT:
        if manifest.determinism is Determinism.D2:
            cap(
                Tier.INADMISSIBLE,
                "Constraint C-a: unit- and edge-level claims require a D0 or D1 "
                "run; the dynamic stream is admittedly lossy and a D2 run cannot "
                "support an object-level claim.",
                "C-a object-level determinism",
            )
        if not manifest.stream_complete_for_scope:
            cap(
                Tier.INADMISSIBLE,
                "Constraint C-a: unit- and edge-level claims require the relevant "
                "stream to be complete for this run.",
                "C-a stream completeness",
            )
    elif scope is ClaimScope.POPULATION and not manifest.coverage_disclosed:
        cap(
            Tier.EXPLORATORY,
            "Constraint C-a / Constitution section 70: population claims require "
            "stream_meta coverage disclosure of omitted mass.",
            "C-a coverage disclosure",
        )

    if not reasons:
        reasons.append(
            "All applicable rules satisfied: registered lock, clean checkout, "
            "hash-matched protocol frozen before first run, complete run, "
            f"determinism {manifest.determinism.value}, coverage disclosed."
        )

    return Verdict(tier=tier, reasons=tuple(reasons), ceilings=tuple(dict.fromkeys(ceilings)))


def required_tier_for(intent: str) -> Tier:
    """The admissibility tier an intended use requires.

    ``intent`` names what the result is about to be used for. Advancing a claim
    to Validated, or accepting one within scope, is confirmatory work; redirecting
    engineering or nominating a hypothesis is exploratory (SOS section 3.1).
    """
    confirmatory = {
        "accept_within_scope",
        "reject",
        "validate",
        "advance_claim_level",
        "causal_interpretation",
        "generalize",
    }
    exploratory = {
        "nominate_hypothesis",
        "redirect_engineering",
        "explore",
        "screen",
    }
    key = intent.strip().lower()
    if key in confirmatory:
        return Tier.CONFIRMATORY
    if key in exploratory:
        return Tier.EXPLORATORY
    return Tier.CONFIRMATORY  # unknown intent is treated as the strictest


__all__ = [
    "ClaimScope",
    "Determinism",
    "Manifest",
    "Registration",
    "Tier",
    "Verdict",
    "assess",
    "required_tier_for",
]
