"""
VELYNX Cognitive Milestone C4 — Concept Birth via Predictive Entropy Reduction
==============================================================================

A concept is not born to *save memory*. It is born because grouping a swarm of
isolated, unexplained exceptions behind a single latent pointer **measurably
reduces the uncertainty of the system's next-step prediction**. Understanding is
compression of the *future*, not of the *archive*.

This module is the formal arbiter of that decision. Given a single
:class:`cognitive_core.InternalModelView` — the localized world model for one
context, carrying a dominant ``Rule`` plus a quarantine of ``Exceptions`` — it:

1. **Hypothesises** a :class:`LatentConcept` that swallows every quarantined
   exception into one abstraction (one new symbol in the predictor's codebook).
2. **Measures the predictive Shannon entropy** of the system *without* the
   concept (``H_before``: the top-level predictor juggling each isolated
   exception as its own competing outcome) and *with* it (``H_after``: the
   predictor sees only ``{Rule, Concept}`` plus the amortised cost of declaring
   the abstraction).
3. **Computes the compression gain** ``G = H_before - H_after`` in bits and, if
   ``G`` clears the birth threshold (default 0.5 bits), raises a
   ``[!] CONCEPT BIRTH`` alert stating exactly how many bits of future
   uncertainty the abstraction mathematically eliminated.

The mathematics (all in bits; ``log`` is ``log2``)
--------------------------------------------------
Let a context have accumulated ``T`` events: ``R`` confirmations of the rule and
exception counts ``{e_1 ... e_N}`` with ``E = Σ e_i``. The predictor's
distribution over "what follows", *before* any abstraction, enumerates the rule
and **every exception separately**::

    D_before = { rule: R/T,  e_1: e_1/T,  ... ,  e_N: e_N/T }
    H_before = - Σ p · log p           (over all N+1 outcomes)

Birthing the concept collapses the ``N`` exceptions behind one pointer ``C``. The
top-level predictor now contends with only two structured outcomes::

    D_coarse = { rule: R/T,  C: E/T }
    H_coarse = - (R/T)·log(R/T) - (E/T)·log(E/T)

By the **grouping (chain) rule of Shannon entropy**::

    H_before = H_coarse + (E/T) · H_within
    H_within = - Σ (e_i/E) · log(e_i/E)        (entropy *inside* the concept)

so the uncertainty lifted clean off the top-level predictor is *exactly*::

    G_raw = H_before - H_coarse = (E/T) · H_within        (always ≥ 0)

This is the heart of the principle: ``G_raw`` scales with both the **mass** the
exceptions command (``E/T``) and their **multiplicity / spread** (``H_within``).
A lone anomaly has ``H_within = 0`` → ``G_raw = 0`` → no concept is born for a
single surprise, exactly as a disciplined mind should behave.

Abstractions are not free. Declaring a new concept symbol costs bits (its
codebook entry / definition), amortised over the ``T`` events it must explain::

    λ_model = concept_definition_bits / T
    H_after = H_coarse + λ_model
    G       = H_before - H_after = (E/T)·H_within - λ_model

A concept is born iff ``G > threshold`` (default 0.5 bits). This is a
Minimum-Description-Length verdict cast entirely in the currency of *predictive*
entropy: the concept must earn its existence by shrinking tomorrow's surprise by
more than it costs to name it.

Strictly Python standard library. No numpy, no scipy, no I/O, no network.
Runnable directly::

    python concept_birth.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

# --- Canonical InternalModelView -------------------------------------------
# Prefer the real structure from the cognitive core; fall back to a minimal,
# structurally-compatible stand-in so this module is genuinely standalone and
# can be imported / executed in isolation.
try:  # pragma: no cover - exercised by environment, not by tests
    from cognitive_core import InternalModelView  # type: ignore
except Exception:  # noqa: BLE001 - any import failure → use the local shim

    @dataclass(frozen=True)
    class InternalModelView:  # type: ignore[no-redef]
        """Minimal structural stand-in for :class:`cognitive_core.InternalModelView`.

        Only the fields C4 actually reads are modelled. The real class carries
        considerably more (rationale, stability tiers, fracture ratio, ...); the
        compression-gain mathematics depends solely on the rule mass, the
        exception frequencies, and the raw event tallies.
        """

        context: Tuple[str, ...]
        rule_consequent: Optional[str]
        rule_confidence: float
        rule_support: float
        exceptions: Tuple[Tuple[str, float], ...]
        stability: float = 0.0
        support_count: int = 0
        contradiction_count: int = 0


__all__ = [
    "DEFAULT_BIRTH_THRESHOLD_BITS",
    "LatentConcept",
    "ConceptBirthDecision",
    "hypothesize_concept",
    "evaluate_concept_birth",
    "announce",
]

# ---------------------------------------------------------------------------
# Tunable constants
# ---------------------------------------------------------------------------

#: Minimum compression gain (bits) before an abstraction is judged worth its
#: keep. Configurable per call. 0.5 bits ≈ "halving one outcome's uncertainty".
DEFAULT_BIRTH_THRESHOLD_BITS: float = 0.5

#: Fallback event horizon used to amortise the concept's definition cost when
#: the view exposes no raw event tallies (``support_count + contradiction_count
#: == 0``). Keeps ``λ_model`` finite and the verdict conservative.
DEFAULT_AMORTIZATION_HORIZON: float = 16.0

_LOG2 = math.log(2.0)


def _log2(x: float) -> float:
    """``log2`` with the information-theoretic convention ``0·log 0 = 0``."""
    return math.log(x) / _LOG2 if x > 0.0 else 0.0


def _entropy_bits(probabilities: Sequence[float]) -> float:
    """Shannon entropy ``-Σ p·log2 p`` in bits over a probability vector.

    Zero-mass outcomes contribute nothing (the ``0·log 0 = 0`` convention). The
    caller is responsible for passing a coherent (≈normalised) vector; tiny
    floating-point drift is tolerated and does not corrupt the result.
    """
    return -sum(p * _log2(p) for p in probabilities if p > 0.0)


# ---------------------------------------------------------------------------
# The hypothesis — a concept that swallows the quarantined exceptions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LatentConcept:
    """A hypothetical abstraction grouping a context's exceptions into one pointer.

    This is a *proposal*, not yet a committed belief. It records the exact
    probabilistic footprint the concept would occupy in the predictor so the
    entropy arithmetic is fully auditable.
    """

    #: Provisional label, e.g. ``"concept<Day>#3"``. Pre-linguistic: a handle,
    #: not a meaning. A human (or a later milestone) may rename it.
    label: str
    #: Context whose world-model spawned this hypothesis.
    context: Tuple[str, ...]
    #: The exception symbols the concept would absorb.
    member_symbols: Tuple[str, ...]
    #: Total predictive probability mass the concept would command, ``E/T`` —
    #: i.e. how often the system actually lands in the exception regime.
    concept_mass: float
    #: Within-concept conditional distribution ``q_i = e_i / E`` over members,
    #: in the same order as :attr:`member_symbols`.
    member_distribution: Tuple[float, ...]
    #: Residual entropy *inside* the concept, ``H_within`` (bits). This is the
    #: uncertainty re-homed into the concept's private sub-model; it is exactly
    #: what gets subtracted from the top-level predictor when the concept fires.
    internal_entropy_bits: float

    @property
    def size(self) -> int:
        """Number of distinct exception symbols the concept would absorb."""
        return len(self.member_symbols)

    def describe(self) -> str:
        members = ", ".join(self.member_symbols) if self.member_symbols else "(none)"
        return (
            f"{self.label} := {{{members}}} "
            f"[mass {self.concept_mass:.3f}, internal H {self.internal_entropy_bits:.3f} bits]"
        )


# ---------------------------------------------------------------------------
# The verdict
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConceptBirthDecision:
    """The full, auditable record of a concept-birth evaluation.

    Every term of ``G = H_before - H_after`` is retained so the alert can show
    precisely where the eliminated bits came from and what the abstraction cost.
    """

    context: Tuple[str, ...]
    concept: Optional[LatentConcept]
    #: Predictive entropy juggling each isolated exception (bits).
    h_before: float
    #: Predictive entropy with exceptions collapsed behind the pointer (bits).
    h_after: float
    #: The coarse two-outcome entropy ``{rule, concept}`` before model cost.
    h_coarse: float
    #: Amortised description cost of declaring the concept (bits), ``λ_model``.
    model_cost_bits: float
    #: Compression gain ``G = H_before - H_after`` (bits).
    gain_bits: float
    #: Threshold ``G`` had to clear.
    threshold_bits: float
    #: Whether the concept was born.
    born: bool
    #: Human-readable reason when no concept is born.
    reason: str = ""

    @property
    def bits_eliminated(self) -> float:
        """Bits of predictive uncertainty removed from the top-level predictor.

        Positive ⇒ understanding; clamped at 0 for reporting clarity.
        """
        return max(0.0, self.gain_bits)

    def report(self) -> str:
        """Render the decision as a multi-line, human-auditable block."""
        ctx = " ".join(self.context) if self.context else "(empty)"
        lines = [
            f"context [{ctx}]",
            f"  H_before (isolated exceptions) : {self.h_before:.4f} bits",
            f"  H_after  (rule + concept)      : {self.h_after:.4f} bits",
            f"     |- coarse {{rule, concept}}  : {self.h_coarse:.4f} bits",
            f"     `- concept definition cost  : {self.model_cost_bits:.4f} bits",
            f"  G = H_before - H_after         : {self.gain_bits:+.4f} bits",
            f"  threshold                      : {self.threshold_bits:.4f} bits",
        ]
        if self.born and self.concept is not None:
            lines.append(f"  VERDICT: BORN → {self.concept.describe()}")
        else:
            lines.append(f"  VERDICT: withheld ({self.reason})")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core machinery
# ---------------------------------------------------------------------------


def _exception_mass(view: "InternalModelView") -> float:
    """Total predictive mass commanded by the exceptions, ``E/T``.

    ``InternalModelView.exceptions`` already stores each exception's *frequency*
    as a fraction of total events (both substrates in ``cognitive_core`` define
    it this way), so the masses sum directly to ``E/T`` and need no further
    normalisation. Clamped to ``[0, 1]`` against floating-point drift.
    """
    total = sum(max(0.0, freq) for _, freq in view.exceptions)
    return min(1.0, total)


def _observation_horizon(view: "InternalModelView") -> float:
    """Event count ``T`` used to amortise the concept's definition cost.

    Prefers the raw episodic tallies on the view; falls back to a fixed horizon
    when the substrate did not populate them (keeps ``λ_model`` finite).
    """
    tally = float(getattr(view, "support_count", 0)) + float(
        getattr(view, "contradiction_count", 0)
    )
    return tally if tally > 0.0 else DEFAULT_AMORTIZATION_HORIZON


def hypothesize_concept(
    view: "InternalModelView", label: Optional[str] = None
) -> Optional[LatentConcept]:
    """Propose a :class:`LatentConcept` grouping every exception in ``view``.

    Returns ``None`` when there is nothing to abstract (no exceptions): you
    cannot compress an empty quarantine. The hypothesis captures the concept's
    predictive footprint — its total mass ``E/T`` and the within-concept
    conditional distribution ``q_i = e_i / E`` — from which the residual entropy
    ``H_within`` is computed.
    """
    exceptions = [(sym, max(0.0, freq)) for sym, freq in view.exceptions if freq > 0.0]
    if not exceptions:
        return None

    concept_mass = sum(freq for _, freq in exceptions)
    if concept_mass <= 0.0:
        return None

    members = tuple(sym for sym, _ in exceptions)
    within = tuple(freq / concept_mass for _, freq in exceptions)
    internal_entropy = _entropy_bits(within)

    if label is None:
        anchor = view.rule_consequent if view.rule_consequent else "?"
        label = f"concept<{anchor}>#{len(members)}"

    return LatentConcept(
        label=label,
        context=tuple(view.context),
        member_symbols=members,
        concept_mass=min(1.0, concept_mass),
        member_distribution=within,
        internal_entropy_bits=internal_entropy,
    )


def evaluate_concept_birth(
    view: "InternalModelView",
    threshold_bits: float = DEFAULT_BIRTH_THRESHOLD_BITS,
    concept_definition_bits: Optional[float] = None,
    label: Optional[str] = None,
) -> ConceptBirthDecision:
    """Decide whether a latent concept should be born for ``view``.

    The full predictive-entropy ledger::

        H_before = H({rule} ∪ {each isolated exception})
        H_coarse = H({rule, concept})
        H_after  = H_coarse + λ_model
        G        = H_before - H_after = (E/T)·H_within - λ_model

    Parameters
    ----------
    view:
        The localized world model (rule + quarantined exceptions) to assess.
    threshold_bits:
        Minimum gain ``G`` (bits) required to birth the concept.
    concept_definition_bits:
        One-time cost of declaring the concept symbol, amortised over the
        context's event horizon ``T``. Defaults to ``log2(N + 1)`` — the bits to
        name one new symbol given the ``N`` exception types it subsumes.
    label:
        Optional override for the hypothesised concept's label.

    Returns
    -------
    ConceptBirthDecision
        A fully populated, auditable verdict (born or withheld).
    """
    context = tuple(view.context)
    concept = hypothesize_concept(view, label=label)

    # Probabilistic footprint. Exception frequencies are fractions of T; the
    # residual mass (rule + any reserved novelty) is the rule outcome.
    exc_freqs = [max(0.0, freq) for _, freq in view.exceptions if freq > 0.0]
    concept_mass = min(1.0, sum(exc_freqs))
    rule_mass = max(0.0, 1.0 - concept_mass)

    # H_before — the predictor enumerates the rule and EVERY exception.
    h_before = _entropy_bits([rule_mass, *exc_freqs])
    # H_coarse — the predictor sees only {rule, concept}.
    h_coarse = _entropy_bits([rule_mass, concept_mass])

    # Amortised cost of declaring the abstraction (MDL honesty term).
    n_members = len(exc_freqs)
    if concept_definition_bits is None:
        concept_definition_bits = _log2(float(n_members) + 1.0)
    horizon = _observation_horizon(view)
    model_cost = concept_definition_bits / horizon if horizon > 0.0 else 0.0

    h_after = h_coarse + model_cost
    gain = h_before - h_after

    # Reasons a birth is withheld, in order of specificity.
    if concept is None or n_members == 0:
        reason = "no exceptions to abstract"
    elif n_members == 1:
        reason = "single exception carries no within-concept entropy (H_within = 0)"
    elif gain <= threshold_bits:
        reason = f"gain {gain:.3f} <= threshold {threshold_bits:.3f} bits"
    else:
        reason = ""

    born = bool(concept is not None and n_members >= 2 and gain > threshold_bits)

    return ConceptBirthDecision(
        context=context,
        concept=concept,
        h_before=h_before,
        h_after=h_after,
        h_coarse=h_coarse,
        model_cost_bits=model_cost,
        gain_bits=gain,
        threshold_bits=threshold_bits,
        born=born,
        reason=reason,
    )


def announce(decision: ConceptBirthDecision, *, verbose: bool = True) -> Optional[str]:
    """Emit the ``[!] CONCEPT BIRTH`` alert for a positive decision.

    Prints (and returns) the alert when a concept was born; returns ``None``
    otherwise. The alert states exactly how many bits of predictive uncertainty
    the abstraction eliminated — the empirical signature of *understanding*.
    """
    if not decision.born or decision.concept is None:
        if verbose:
            print(decision.report())
        return None

    concept = decision.concept
    ctx = " ".join(decision.context) if decision.context else "(empty)"
    banner = (
        f"[!] CONCEPT BIRTH  —  {concept.label}\n"
        f"    context        : [{ctx}]\n"
        f"    absorbs        : {{{', '.join(concept.member_symbols)}}}\n"
        f"    H_before       : {decision.h_before:.4f} bits  (juggling {concept.size} isolated exceptions)\n"
        f"    H_after        : {decision.h_after:.4f} bits  (rule + single concept pointer)\n"
        f"    bits eliminated: {decision.bits_eliminated:.4f} bits  "
        f"(gain {decision.gain_bits:+.4f} > threshold {decision.threshold_bits:.2f})\n"
        f"    => understanding reduced future uncertainty by "
        f"{decision.bits_eliminated:.4f} bits."
    )
    if verbose:
        print(banner)
    return banner


# ---------------------------------------------------------------------------
# Demonstration — proving the math discriminates understanding from noise
# ---------------------------------------------------------------------------


def _demo_view(
    context: Tuple[str, ...],
    rule: str,
    rule_count: int,
    exceptions: Sequence[Tuple[str, int]],
) -> "InternalModelView":
    """Build an :class:`InternalModelView` from raw integer event counts.

    Mirrors how ``cognitive_core`` substrates populate the view: each
    exception's stored frequency is ``count / T`` with ``T`` the total events.
    """
    total = float(rule_count + sum(c for _, c in exceptions))
    exc_tuple = tuple((sym, c / total) for sym, c in exceptions)
    return InternalModelView(
        context=context,
        rule_consequent=rule,
        rule_confidence=rule_count / total,
        rule_support=float(rule_count),
        exceptions=exc_tuple,
        stability=0.0,
        support_count=rule_count,
        contradiction_count=sum(c for _, c in exceptions),
    )


def _run_demo() -> None:
    print("=" * 74)
    print("VELYNX C4 — Concept Birth by Predictive Entropy Reduction")
    print("=" * 74)

    scenarios = [
        (
            "A — diffuse anomaly swarm (strong abstraction expected)",
            _demo_view(
                context=("Sky",),
                rule="Clear",
                rule_count=20,
                exceptions=[
                    ("Drizzle", 6),
                    ("Storm", 5),
                    ("Hail", 4),
                    ("Fog", 4),
                    ("Snow", 3),
                ],
            ),
        ),
        (
            "B — lone anomaly (no within-concept entropy -> refuse)",
            _demo_view(
                context=("Day",),
                rule="Night",
                rule_count=30,
                exceptions=[("Eclipse", 4)],
            ),
        ),
        (
            "C — tiny, rare exceptions (gain below threshold -> refuse)",
            _demo_view(
                context=("Coin",),
                rule="Heads",
                rule_count=200,
                exceptions=[("EdgeLand", 1), ("Vanished", 1)],
            ),
        ),
    ]

    for title, view in scenarios:
        print("\n" + "-" * 74)
        print(title)
        print("-" * 74)
        decision = evaluate_concept_birth(view)
        announce(decision)

    print("\n" + "=" * 74)
    print(
        "Note: the gain (E/T)·H_within rewards exceptions that are both\n"
        "FREQUENT (command real predictive mass) and DIVERSE (spread across\n"
        "many forms). One anomaly, or a vanishingly rare one, is correctly\n"
        "judged unworthy of its own abstraction."
    )
    print("=" * 74)


if __name__ == "__main__":
    _run_demo()
