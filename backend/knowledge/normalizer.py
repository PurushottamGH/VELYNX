"""
VELYNX Phase 54 — Semantic Normalizer
=====================================

The active knowledge graph stores facts as ``(subject, relation, object)``
triples keyed by surface strings. Without normalization, "Bangalore" and
"Bengaluru" are two unrelated nodes, so a fact taught under one name is
invisible to a query phrased with the other. The same fragmentation happens
for relation verbs ("created by" vs. "authored by") and common entity
aliases ("creator" vs. "author").

:class:`ConceptNormalizer` collapses known synonyms onto a single *canonical*
surface form. It is applied on **both** sides of the graph:

* **Write path** (:mod:`backend.knowledge.consolidator`): subject, relation and
  object are normalized before ``add_concept`` / ``add_relationship`` so every
  synonym is stored under one canonical node.
* **Read path** (:mod:`backend.pipeline.reasoning_wiring`): query concepts are
  normalized before they hit the graph / vector DB, so a query phrased with any
  synonym lands on the same canonical node the fact was written to.

Design notes
------------
* **Local + deterministic.** No network, no model load — a plain in-memory
  alias dictionary. Lookup is O(1) and side-effect free, safe to call on every
  token of every query.
* **Case-insensitive matching, clean canonical output.** Matching always folds
  case (so "BANGALORE", "Bangalore" and "bangalore" all resolve). For matched
  aliases the canonical value from the table is returned verbatim. For
  unmatched tokens the input is returned lowercased + whitespace-collapsed by
  default, which is the format the graph and ``get_related`` already use
  (seed concepts are lowercase and the read path lowercases before lookup).
  Pass ``preserve_case=True`` to keep the original casing of unmatched tokens
  (useful for display of proper nouns).
* **Convergence is the contract.** Because both paths call :meth:`normalize`
  with the same defaults, a synonym written today is found by any of its
  aliases tomorrow — that is the whole point of the phase.
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, Tuple

# Collapses runs of internal whitespace to a single space.
_WS_RE = re.compile(r"\s+")


class ConceptNormalizer:
    """Resolve synonymous surface forms to a single canonical concept string.

    The alias table maps *lowercased* synonym -> canonical surface form. Keys
    are always compared case-insensitively; values are returned exactly as
    written here, so the canonical form's casing is whatever you choose in the
    table (kept lowercase to match the graph's existing storage convention).
    """

    # ── Local alias dictionary ────────────────────────────────────────────
    # synonym (lowercased)            -> canonical surface form
    #
    # NOTE: relation *verbs* ("created", "made by", "is", "are", ...) are
    # intentionally NOT mapped here. Those belong to the dedicated
    # :mod:`backend.knowledge.predicate_resolver`, which collapses verb
    # synonyms onto core predicates ("create", "be", ...). Mixing the two here
    # previously fragmented one relation across "create" (from the spaCy
    # lemma), "authored" (from this table) and "authored by" — exactly the
    # predicate-grounding bug. Only *entity / noun* aliases live below.
    DEFAULT_ALIASES: Dict[str, str] = {
        # ── Geographic / proper-noun aliases ──────────────────────────────
        "bangalore": "bengaluru",
        "bengaluru": "bengaluru",
        "bombay": "mumbai",
        "calcutta": "kolkata",
        "madras": "chennai",
        "nyc": "new york",
        "new york city": "new york",
        "usa": "united states",
        "u.s.a.": "united states",
        "u.s.": "united states",
        "us": "united states",
        "uk": "united kingdom",
        "u.k.": "united kingdom",
        # ── Self-reference aliases ────────────────────────────────────────
        "i": "user",
        "me": "user",
        "myself": "user",
        "velynx": "velynx",
    }

    def __init__(self, aliases: Dict[str, str] | None = None) -> None:
        # Build a fresh, case-folded table so callers can't accidentally inject
        # mixed-case keys that would silently miss.
        source = aliases if aliases is not None else self.DEFAULT_ALIASES
        self._aliases: Dict[str, str] = {
            self._fold(k): v for k, v in source.items()
        }

    # ── Helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _fold(text: str) -> str:
        """Lowercase + collapse/trim whitespace — the canonical lookup key."""
        return _WS_RE.sub(" ", str(text or "").strip().lower())

    # ── Public API ──────────────────────────────────────────────────────────
    def normalize(self, text: str, *, preserve_case: bool = False) -> str:
        """Return the canonical surface form for ``text``.

        Parameters
        ----------
        text:
            Any concept / entity / relation surface string.
        preserve_case:
            When ``True`` and ``text`` is *not* a known alias, the original
            casing is preserved (whitespace is still collapsed). When ``False``
            (default) an unmatched token is returned lowercased, matching the
            graph's storage convention so write and read paths converge.

        Returns
        -------
        str
            The canonical form. Empty input returns ``""``.
        """
        if text is None:
            return ""
        key = self._fold(text)
        if not key:
            return ""
        # 1. Known synonym -> canonical value (verbatim from the table).
        canonical = self._aliases.get(key)
        if canonical is not None:
            return canonical
        # 2. Unknown token -> clean it but optionally keep its casing.
        if preserve_case:
            return _WS_RE.sub(" ", str(text).strip())
        return key

    def is_alias(self, text: str) -> bool:
        """True when ``text`` resolves to a different canonical form."""
        key = self._fold(text)
        canonical = self._aliases.get(key)
        return canonical is not None and canonical != key

    def add_alias(self, synonym: str, canonical: str) -> None:
        """Register a new ``synonym -> canonical`` mapping at runtime."""
        self._aliases[self._fold(synonym)] = canonical

    def normalize_triple(
        self, subject: str, relation: str, obj: str
    ) -> Tuple[str, str, str]:
        """Normalize a full ``(subject, relation, object)`` triple at once.

        Convenience for the write path so all three components pass through the
        same canonicalization in one call.
        """
        return (
            self.normalize(subject),
            self.normalize(relation),
            self.normalize(obj),
        )

    def normalize_many(
        self, items: Iterable[str], *, preserve_case: bool = False
    ) -> list[str]:
        """Normalize an iterable of concepts, dropping empties, de-duplicating.

        Order is preserved; the first occurrence of each canonical form wins.
        """
        seen: set[str] = set()
        out: list[str] = []
        for item in items or []:
            norm = self.normalize(item, preserve_case=preserve_case)
            if not norm:
                continue
            dedup_key = norm.lower()
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            out.append(norm)
        return out


# Process-wide singleton — import this everywhere so the alias table (and any
# runtime-registered aliases) is shared across the write and read paths.
concept_normalizer = ConceptNormalizer()


__all__ = ["ConceptNormalizer", "concept_normalizer"]
