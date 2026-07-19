"""FROZEN ES-1 constants -- the single home of every ES-1 free constant.

These constants ARE the mechanism (CR-6/CR-11/CR-12). A change here is a
mechanism change: it requires a T1 revision + re-freeze + a new
``SPEC_VERSION`` + a new ``mechanism_id()`` before any frozen-row output is
observed, and is prohibited after (prereg Section 4 #5; CR-6).

G4-FREEZE PREPARATION STATE (2026-07-09)
---------------------------------------
The concrete frozen values transcribed verbatim from the T1 free-constant
register (``PROGRAM_A_T1_MECHANISM_PREREGISTRATION.md`` Section 5) are in place
for:

  * ``SPEC_VERSION``                    -- Section 5.8
  * ``MIN_INDEPENDENT_ORIGINS_FOR_S3``   -- Section 5.1
  * ``INDEPENDENCE_RELATION``            -- Section 5.2
  * ``EVIDENCE_ORDERING_KEY``            -- Section 5.5
  * ``PA3_RULESET_VERSION``              -- addendum Section A6-DIGEST
  * ``STATE_TIER_MAP``, ``CONFIDENCE_TIERS`` -- Section 3.2 (structural)

The following four register entries are NOT YET transcribed -- their concrete
values are "fixed at G4 from this register" (T1 Section 5.3/5.4/5.6/5.7) and
addendum Section C condition 4 names this as "the pre-existing T1
transcription duty". They are owed at the G4 freeze step (owned by the
ReleaseManager + ScientificAuditor) and are held here as the empty-dict
placeholder ``{}`` (listed in ``_FREEZE_PENDING_ENTRIES``). NO default or
inferred value is fabricated:

  * ``SUPPORT_TEST_PARAMS``              -- Section 5.3
  * ``CONTRADICTION_MATERIALITY_PARAMS`` -- Section 5.4
  * ``EXTRACTION_PARAMS``                -- Section 5.6
  * ``ANSWER_TEMPLATES``                 -- Section 5.7

Consequently ``frozen_constants_digest()`` is implemented per Section 6.1
(SHA-256 over the ordered serialization of all eleven inputs) but REFUSES to
emit a final digest while any pending entry remains the placeholder, and
``CONSTANTS_HASH`` is ``None`` (not pinned). The digest + hash are finalized at
the G4 freeze step once the four entries above are transcribed.

No tier->probability values or bin boundaries appear here at all (CR-8/L8
compliance by construction).

Reference: PROGRAM_A_CONFIDENCE_MECHANISM.md Section 7.4 (register);
PROGRAM_A_MODULE_SPEC.md Section 2;
PROGRAM_A_FINAL_ARCHITECTURE.md Section 4 PA-3;
PROGRAM_A_T1_PA3_FREEZE_ADDENDUM.md Section A6-DIGEST.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


class FrozenConstantsIncomplete(RuntimeError):
    """Raised by ``frozen_constants_digest()`` while register entries are pending.

    The T1 free-constant register leaves four entries' concrete values to be
    "fixed at G4 from this register" (addendum Section C condition 4). Until
    those are transcribed, no final digest may be emitted and ``CONSTANTS_HASH``
    stays ``None``. The exception message names the owed entries so the freeze
    step has an unambiguous checklist.
    """


# --- T1 spec identity (Section 5.8) -----------------------------------------
# Transcribed verbatim from the T1 register; ratified to its final frozen value
# at the G4 freeze commit.
SPEC_VERSION: str = "es1-t1-2026-07-09"

# --- PA-3 corroboration threshold (Section 5.1) ------------------------------
# The >=2-independent-origins threshold for S3; a-priori justified per the T1
# free-constant register (2 is the smallest count that is corroboration at all).
MIN_INDEPENDENT_ORIGINS_FOR_S3: int = 2

# --- PA-3 source-independence relation (Section 5.2) -------------------------
# Frozen structural definition: two evidence items are independent iff they
# have distinct origin_domain provenance, with mirror/syndication domains
# counted once (exact relation text fixed at G4 from the T1 register).
INDEPENDENCE_RELATION: str = (
    "two evidence items are independent iff they have distinct origin_domain "
    "provenance, with mirror/syndication domains counted once"
)

# --- PA-3 claim-support test parameters (Section 5.3) -- PENDING -------------
# TODO(T1/G4-freeze): the frozen deterministic claim-support test parameters
# (entity-level matching; no probability numbers). Exact parameters fixed at G4
# from the T1 register (addendum Section C condition 4). Held as {} until then;
# no default is fabricated.
SUPPORT_TEST_PARAMS: dict[str, Any] = {}

# --- PA-3 contradiction / materiality rule parameters (Section 5.4) - PENDING -
# TODO(T1/G4-freeze): the frozen materiality-rule parameters (no probability
# numbers). Exact parameters fixed at G4 from the T1 register (addendum Section
# C condition 4). Held as {} until then; no default is fabricated.
CONTRADICTION_MATERIALITY_PARAMS: dict[str, Any] = {}

# --- PA-1 frozen evidence ordering key (Section 5.5) ------------------------
# The frozen total-order key over the evidence set.
EVIDENCE_ORDERING_KEY: str = "lexicographic on (origin_domain, doc_id)"

# --- PA-2 extraction parameters (Section 5.6) -- PENDING ---------------------
# TODO(T1/G4-freeze): PA-2 deterministic extraction parameters (no probability
# numbers, no model calls). Exact parameters fixed at G4 from the T1 register
# (addendum Section C condition 4). Held as {} until then; no default is
# fabricated; claim_extraction.py governs via its structural defaults meanwhile.
EXTRACTION_PARAMS: dict[str, Any] = {}

# --- PA-4 frozen answer templates per state (Section 5.7) -- PENDING --------
# TODO(T1/G4-freeze): a frozen template string per state {S0, S1, S2, S3}; the
# UNKNOWN/DEBATED forms assert no fact; the PROBABLE/CERTAIN forms are
# source-attributed. Exact template text fixed at G4 from the T1 register
# (addendum Section C condition 4). Held as {} until then; no default is
# fabricated.
ANSWER_TEMPLATES: dict[str, Any] = {}

# --- PA-3 ruleset structural identity tag (addendum Section A6-DIGEST) ------
# Pure identity string (no probability, no numeric evaluation constant), in the
# same class as SPEC_VERSION. Folding it into the digest closes the coverage
# gap so a silent edit to the PA-3 rule text (addendum A1-A7) trips the runtime
# tripwire. Transcribed from the frozen addendum.
PA3_RULESET_VERSION: str = "pa3-ruleset-2026-07-09"

# --- Frozen ES-1 state -> tier map (Section 3.2; verbatim, not tunable) -----
STATE_TIER_MAP: dict[str, str] = {
    "S0": "UNKNOWN",
    "S1": "DEBATED",
    "S2": "PROBABLE",
    "S3": "CERTAIN",
}

# --- Confidence tier label set (mirrors experiments.EXP1.dataset.CONFIDENCE_TIERS)
# Frozen structural label set; equality with the EXP-1 constant is asserted by
# the structural/conformance tests.
CONFIDENCE_TIERS: tuple[str, ...] = ("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")

# --- Register entries whose concrete values are still owed at the G4 freeze --
# (addendum Section C condition 4). ``{}`` denotes "pending transcription"; the
# frozen values will be non-empty dicts. Do NOT pin CONSTANTS_HASH while any
# member is still the placeholder.
_FREEZE_PENDING_ENTRIES: tuple[str, ...] = (
    "SUPPORT_TEST_PARAMS",
    "CONTRADICTION_MATERIALITY_PARAMS",
    "EXTRACTION_PARAMS",
    "ANSWER_TEMPLATES",
)

# --- Pinned digest (Section 6.1) -- PENDING ---------------------------------
# None until the four entries in _FREEZE_PENDING_ENTRIES are transcribed at the
# G4 freeze step and frozen_constants_digest() is run to produce the pinned
# value. Not fabricated.
CONSTANTS_HASH: str | None = None


def _frozen_constants_items() -> tuple[tuple[str, object], ...]:
    """The ordered (name, value) pairs of every digest input.

    Canonical order per T1 Section 6.1 (the eight Section-5 register entries,
    then the structural STATE_TIER_MAP and CONFIDENCE_TIERS) with
    PA3_RULESET_VERSION folded in per addendum Section A6-DIGEST. The order is
    itself part of the frozen serialization; the Release Manager ratifies it at
    the G4 freeze.
    """
    return (
        ("MIN_INDEPENDENT_ORIGINS_FOR_S3", MIN_INDEPENDENT_ORIGINS_FOR_S3),
        ("INDEPENDENCE_RELATION", INDEPENDENCE_RELATION),
        ("SUPPORT_TEST_PARAMS", SUPPORT_TEST_PARAMS),
        ("CONTRADICTION_MATERIALITY_PARAMS", CONTRADICTION_MATERIALITY_PARAMS),
        ("EVIDENCE_ORDERING_KEY", EVIDENCE_ORDERING_KEY),
        ("EXTRACTION_PARAMS", EXTRACTION_PARAMS),
        ("ANSWER_TEMPLATES", ANSWER_TEMPLATES),
        ("SPEC_VERSION", SPEC_VERSION),
        ("PA3_RULESET_VERSION", PA3_RULESET_VERSION),
        ("STATE_TIER_MAP", STATE_TIER_MAP),
        ("CONFIDENCE_TIERS", CONFIDENCE_TIERS),
    )


def _serialize_frozen_constants() -> bytes:
    """Canonical ordered UTF-8 serialization of the frozen-constant set.

    Each entry is ``name:`` + a canonical JSON encoding (sorted keys, no
    insignificant whitespace, ensure_ascii=False) joined by ``\\n`` with a
    trailing newline. Deterministic across Python versions and runs.
    """
    parts: list[str] = []
    for name, value in _frozen_constants_items():
        parts.append(
            name
            + ":"
            + json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        )
    return ("\n".join(parts) + "\n").encode("utf-8")


def frozen_constants_digest() -> str:
    """Return the SHA-256 digest over the frozen constant set (T1 Section 6.1).

    PENDING: four register entries (``SUPPORT_TEST_PARAMS``,
    ``CONTRADICTION_MATERIALITY_PARAMS``, ``EXTRACTION_PARAMS``,
    ``ANSWER_TEMPLATES``) are not yet transcribed -- their concrete values are
    "fixed at G4 from this register" (addendum Section C condition 4). Until
    they are supplied at the G4 freeze step, this function REFUSES to emit a
    digest (no fabricated hash over placeholders) and raises
    :class:`FrozenConstantsIncomplete` naming the owed entries;
    ``CONSTANTS_HASH`` remains ``None``.

    Once all entries are transcribed, returns
    ``hashlib.sha256(_serialize_frozen_constants()).hexdigest()``.
    """
    pending = [name for name in _FREEZE_PENDING_ENTRIES if globals()[name] == {}]
    if pending:
        raise FrozenConstantsIncomplete(
            "frozen_constants_digest() is not final: the following register "
            "entries are still pending transcription (addendum Section C "
            "condition 4, the pre-existing T1 transcription duty) and must be "
            "supplied at the G4 freeze step before a digest may be pinned: "
            + ", ".join(pending)
            + ". No default or inferred value is fabricated; CONSTANTS_HASH is "
            "None."
        )
    return hashlib.sha256(_serialize_frozen_constants()).hexdigest()


__all__ = [
    "SPEC_VERSION",
    "MIN_INDEPENDENT_ORIGINS_FOR_S3",
    "INDEPENDENCE_RELATION",
    "SUPPORT_TEST_PARAMS",
    "CONTRADICTION_MATERIALITY_PARAMS",
    "EVIDENCE_ORDERING_KEY",
    "EXTRACTION_PARAMS",
    "ANSWER_TEMPLATES",
    "PA3_RULESET_VERSION",
    "STATE_TIER_MAP",
    "CONFIDENCE_TIERS",
    "CONSTANTS_HASH",
    "FrozenConstantsIncomplete",
    "frozen_constants_digest",
]