"""
VELYNX Answer Synthesizer v3 — Zero-Inference Translation Layer
================================================================
Deterministic natural language formatter for symbolic ReasoningTrace data.
No LLM calls, no external models, no inference beyond what the trace contains.

The synthesizer is the final step in VELYNX's cognitive pipeline. It receives
a purely symbolic ReasoningTrace from the ReasoningEngine and translates it
into human-readable English without adding, inventing, or inferring any facts
beyond what the trace explicitly records.

Confidence is integrated dynamically — the output text is visibly marked with
CERTAIN / PROBABLE / UNCERTAIN / SPECULATIVE / INSUFFICIENT labels, and the
verbosity and structure of the response adapt to the system's thermodynamic
state (hot/chaotic → concise; cold/calm → narrative).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("velynx.answer_synthesizer")

# --------------------------------------------------------------------------- #
#  Confidence taxonomy
# --------------------------------------------------------------------------- #


class ConfidenceGrade(str, Enum):
    CERTAIN = "CERTAIN"
    PROBABLE = "PROBABLE"
    UNCERTAIN = "UNCERTAIN"
    SPECULATIVE = "SPECULATIVE"
    INSUFFICIENT = "INSUFFICIENT"


# Threshold, grade, and the prose prefix that precedes the formatted answer.
_CONFIDENCE_BANDS: list[tuple[float, ConfidenceGrade, str]] = [
    (0.90, ConfidenceGrade.CERTAIN, "I am confident that"),
    (0.70, ConfidenceGrade.PROBABLE, "It is likely that"),
    (0.50, ConfidenceGrade.UNCERTAIN, "Based on available information,"),
    (0.25, ConfidenceGrade.SPECULATIVE, "This is speculative —"),
    (0.00, ConfidenceGrade.INSUFFICIENT, "I cannot determine"),
]


def _grade_confidence(score: float) -> tuple[ConfidenceGrade, str]:
    """Return the grade and prose prefix for a confidence score in [0, 1]."""
    for threshold, grade, prefix in _CONFIDENCE_BANDS:
        if score >= threshold:
            return grade, prefix
    return _CONFIDENCE_BANDS[-1][1], _CONFIDENCE_BANDS[-1][2]


# --------------------------------------------------------------------------- #
#  Output data structure
# --------------------------------------------------------------------------- #


@dataclass
class SynthesisResult:
    """Structured output of the AnswerSynthesizer."""

    text: str
    confidence: float
    confidence_label: str = ""
    sources: list[str] = field(default_factory=list)
    reasoning_used: bool = False
    why: str = ""
    how: str = ""
    contradiction_count: int = 0
    unresolved_concepts: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
#  AnswerSynthesizer
# --------------------------------------------------------------------------- #


class AnswerSynthesizer:
    """
    Zero-inference translation layer for symbolic ReasoningTrace data.

    Takes a :class:`ReasoningTrace` (produced by the deterministic
    :class:`ReasoningEngine`) and formats it into natural language using
    **only** the data fields present in the trace.  No LLM calls, no
    external knowledge, no generative creativity.

    Parameters
    ----------
    kg : optional
        Retained for API compatibility with ``VelynxBrain``.  Not used during
        synthesis — all required data must already be in the ``ReasoningTrace``.
    """

    def __init__(self, kg: Any = None) -> None:
        self.kg = kg

    # ------------------------------------------------------------------ #
    #  Public API  (async for backward compatibility with VelynxBrain)
    # ------------------------------------------------------------------ #

    async def synthesize(
        self,
        query: str,
        reasoning_trace: Any,
        vec_results: list | None = None,
    ) -> SynthesisResult:
        """
        Translate a symbolic ``ReasoningTrace`` into natural-language text.

        Parameters
        ----------
        query:
            The original user prompt (used only to echo back the topic).
        reasoning_trace:
            A ``ReasoningTrace`` instance (or any object with the expected
            attributes: ``paths``, ``winning_facts``, ``inferred_facts``,
            ``contradictions``, ``unresolved_concepts``, ``confidence``,
            ``thermodynamic_state``).
        vec_results:
            Ignored during zero-inference synthesis.  Retained for API
            compatibility — *no* vector data is consulted for content.

        Returns
        -------
        SynthesisResult
            The deterministic natural-language response.
        """
        return self._format(query, reasoning_trace)

    # ================================================================== #
    #  Core formatting
    # ================================================================== #

    def _format(self, query: str, trace: Any) -> SynthesisResult:
        """Deterministic formatting — the heart of the synthesizer."""

        # --- Extract trace metadata (with safe defaults) ----------------- #
        paths = getattr(trace, "paths", []) or []
        winning_facts = getattr(trace, "winning_facts", []) or []
        contradictions = getattr(trace, "contradictions", []) or []
        unresolved = getattr(trace, "unresolved_concepts", []) or []
        confidence = getattr(trace, "confidence", 0.0)
        thermo = getattr(trace, "thermodynamic_state", 0.5)
        inferred = getattr(trace, "inferred_facts", []) or []

        # Defensive coercion: the trace's scalars may arrive as None or a
        # non-numeric type from upstream. Coerce to float with safe fallbacks
        # so the clamp/grade math below can never raise.
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        try:
            thermo = float(thermo)
        except (TypeError, ValueError):
            thermo = 0.5

        # Clamp & grade.
        confidence = max(0.0, min(1.0, confidence))
        grade, prefix = _grade_confidence(confidence)
        thermo = max(0.0, min(1.0, thermo))

        # --- Fallback: empty / broken trace ------------------------------ #
        if not paths and not winning_facts:
            if unresolved:
                fallback = self._fallback_broken_path(unresolved, contradictions)
            else:
                fallback = (
                    "I don't have enough information to answer this confidently."
                )
            return SynthesisResult(
                text=fallback,
                confidence=confidence,
                confidence_label=grade.value,
                reasoning_used=False,
                unresolved_concepts=list(unresolved),
                contradiction_count=len(contradictions),
            )

        # --- Build the answer body -------------------------------------- #
        parts: list[str] = []

        # 1) Opening line with confidence integration.
        opening = self._opening_line(query, grade, prefix, paths, winning_facts)
        parts.append(opening)

        # 2) Path narrative — adapted to thermodynamic state.
        path_text = self._format_paths(paths, thermo, winning_facts)
        if path_text:
            parts.append("")

            bodies = path_text.split("\n\n")
            for b in bodies:
                parts.append(b.strip())

        # 3) Contradictions (if any).
        if contradictions:
            contradiction_text = self._format_contradictions(contradictions)
            if contradiction_text:
                parts.append("")
                parts.append(contradiction_text)

        # 4) Unresolved concepts.
        if unresolved:
            unresolved_text = self._format_unresolved(unresolved)
            if unresolved_text:
                parts.append("")
                parts.append(unresolved_text)

        # 5) Inferred facts (deduced knowledge).
        deduped = self._unique_facts(inferred)
        if deduped and grade not in (ConfidenceGrade.INSUFFICIENT,):
            inferred_text = self._format_inferred(deduped)
            if inferred_text:
                parts.append("")
                parts.append(inferred_text)

        # 6) Closing confidence marker.
        parts.append("")
        parts.append(self._format_confidence_closing(grade, confidence))

        text = "\n".join(parts).strip()

        # Collect sources from facts on paths.
        sources: list[str] = []
        seen_src: set[str] = set()
        for p in paths:
            for step in getattr(p, "steps", []):
                src = getattr(step.fact if hasattr(step, "fact") else step, "source", "")
                if src and src not in seen_src:
                    seen_src.add(src)
                    sources.append(src)

        return SynthesisResult(
            text=text,
            confidence=confidence,
            confidence_label=grade.value,
            sources=sources,
            reasoning_used=len(paths) > 0 or len(winning_facts) > 0,
            contradiction_count=len(contradictions),
            unresolved_concepts=list(unresolved),
        )

    # ================================================================== #
    #  Sub-formatters
    # ================================================================== #

    def _opening_line(
        self,
        query: str,
        grade: ConfidenceGrade,
        prefix: str,
        paths: list[Any],
        winning_facts: list[Any],
    ) -> str:
        """Build the opening sentence integrating confidence grade."""
        # How many facts are we reasoning from?
        fact_count = len(winning_facts) + sum(
            len(getattr(p, "steps", [])) for p in paths
        )
        topic = query.strip().rstrip("?.") if query else "this"

        if grade == ConfidenceGrade.CERTAIN:
            return f"{prefix} {topic}:"
        elif grade == ConfidenceGrade.PROBABLE:
            return f"{prefix} {topic}:"
        elif grade in (ConfidenceGrade.UNCERTAIN, ConfidenceGrade.SPECULATIVE):
            if fact_count > 0:
                return f"{prefix} {topic} can be partially answered:"
            return f"{prefix} there is limited evidence about {topic}:"
        else:
            return f"{prefix} about {topic} from the available evidence."

    def _format_paths(
        self,
        paths: list[Any],
        thermo: float,
        winning_facts: list[Any],
    ) -> str:
        """
        Format the reasoning paths.

        Thermodynamic adaptation:
        - Hot (>= 0.7):  Concise, structural, almost schematic.
        - Medium (0.3-0.7): Balanced — one sentence per path.
        - Cold (< 0.3): Narrative — full sentences linking concepts.
        """
        if not paths:
            # Fall back to flat fact list.
            return self._format_fact_list(winning_facts, thermo)

        lines: list[str] = []

        if thermo >= 0.7:
            # High energy — concise, structural, schematic.
            for p in paths[:3]:  # cap at strongest 3 paths
                step_strs: list[str] = []
                for step in getattr(p, "steps", []):
                    f = step.fact if hasattr(step, "fact") else step
                    step_strs.append(
                        f"{f.subject} \u2014[{f.predicate}]\u2192 {f.obj}"
                    )
                if step_strs:
                    chain = " \u2192 ".join(step_strs)
                    lines.append(f"\u2022 {chain}")
            if len(paths) > 3:
                lines.append(f"\u2022 ... and {len(paths) - 3} additional reasoning paths")

        elif thermo >= 0.3:
            # Medium energy — balanced, one sentence per path.
            for i, p in enumerate(paths[:2]):
                step_strs = []
                for step in getattr(p, "steps", []):
                    f = step.fact if hasattr(step, "fact") else step
                    step_strs.append(
                        f"'{f.subject}' is linked to '{f.obj}' via '{f.predicate}'"
                    )
                if step_strs:
                    chain = ", and then ".join(step_strs)
                    lines.append(f"A reasoning path shows: {chain}.")
            if len(paths) > 2:
                lines.append(
                    f"There are {len(paths)} reasoning paths in total."
                )

        else:
            # Cold — narrative, fully formed sentences.
            for i, p in enumerate(paths[:1]):
                step_strs = []
                for step in getattr(p, "steps", []):
                    f = step.fact if hasattr(step, "fact") else step
                    step_strs.append(
                        f"considering that {f.subject} {self._predicate_phrase(f.predicate)} {f.obj}"
                    )
                if step_strs:
                    narrative = ", ".join(step_strs)
                    lines.append(
                        f"The reasoning begins by {narrative}, forming a complete logical chain."
                    )
            if len(paths) > 1:
                lines.append(
                    f"This is supported by {len(paths)} distinct reasoning paths through the knowledge graph."
                )

        return "\n".join(lines)

    def _format_fact_list(self, facts: list[Any], thermo: float) -> str:
        """Format a flat list of winning facts (no paths found)."""
        if not facts:
            return ""
        items: list[str] = []
        for f in facts[:5]:
            items.append(
                f"\u2022 {f.subject} \u2014[{f.predicate}]\u2192 {f.obj}"
                f"  (c={f.confidence:.2f})"
            )
        if len(facts) > 5:
            items.append(f"\u2022 ... and {len(facts) - 5} more facts")
        return "\n".join(items)

    def _format_contradictions(self, contradictions: list[Any]) -> str:
        """Format resolved and unresolved contradictions."""
        lines: list[str] = []

        for c in contradictions:
            w, l = c.winner, c.loser
            if c.resolved:
                lines.append(
                    f"\u2022 Contradiction resolved: '{w.subject}' has conflicting "
                    f"'{c.predicate}' assertions. The evidence "
                    f"('{w.obj}', c={w.confidence:.2f}) outweighs "
                    f"('{l.obj}', c={l.confidence:.2f})."
                )
            else:
                lines.append(
                    f"\u2022 Unresolved conflict about '{c.subject}': "
                    f"one source says '{w.obj}', another says '{l.obj}'. "
                    f"The evidence is too close to decide conclusively."
                )

        return "Note on conflicting information:\n" + "\n".join(lines)

    def _format_unresolved(self, unresolved: list[str]) -> str:
        """Format unresolved concepts."""
        if len(unresolved) == 1:
            return f"Note: I found no connecting evidence for the concept '{unresolved[0]}'."
        concepts = ", ".join(f"'{c}'" for c in unresolved)
        return f"Note: I found no connecting evidence for the following concepts: {concepts}."

    def _format_inferred(self, inferred: list[Any]) -> str:
        """Format deductively inferred facts."""
        items: list[str] = []
        for f in inferred[:3]:
            items.append(
                f"\u2022 By deduction: {f.subject} \u2014[{f.predicate}]\u2192 {f.obj}"
            )
        if len(inferred) > 3:
            items.append(f"\u2022 ... and {len(inferred) - 3} additional inferred facts")
        return "Inferred knowledge:\n" + "\n".join(items)

    def _format_confidence_closing(
        self, grade: ConfidenceGrade, score: float
    ) -> str:
        """Closing line with the raw confidence score."""
        return f"Confidence: {grade.value} ({score:.2f})"

    # ================================================================== #
    #  Fallbacks (deterministic, no inference)
    # ================================================================== #

    def _fallback_broken_path(
        self, unresolved: list[str], contradictions: list[Any]
    ) -> str:
        """
        Deterministic fallback when the trace found no reasoning paths.

        Reports the exact internal state — no invented text.
        """
        parts: list[str] = []

        if contradictions:
            parts.append(
                "Logic path broken — the system encountered contradictory "
                "information that could not be fully resolved."
            )
            for c in contradictions[:2]:
                parts.append(
                    f"  \u2022 Conflict about '{c.subject}': "
                    f"'{c.winner.obj}' vs '{c.loser.obj}'"
                )

        if unresolved:
            concept_list = ", ".join(f"'{c}'" for c in unresolved[:3])
            parts.append(
                f"Logic path broken at concept{'s' if len(unresolved) > 1 else ''} "
                f"{concept_list} — no connecting evidence found."
            )

        return "\n".join(parts) if parts else (
            "Logic path broken — the reasoning engine found no valid paths "
            "through the knowledge graph for this query."
        )

    # ================================================================== #
    #  Helpers
    # ================================================================== #

    @staticmethod
    def _predicate_phrase(predicate: str) -> str:
        """Convert a predicate like 'located_in' to a readable phrase."""
        mapping = {
            "is": "is",
            "is_a": "is a",
            "isa": "is a",
            "has_property": "has property",
            "has_value": "has value",
            "located_in": "is located in",
            "part_of": "is part of",
            "causes": "causes",
            "leads_to": "leads to",
            "results_in": "results in",
            "requires": "requires",
            "depends_on": "depends on",
            "precedes": "precedes",
            "implies": "implies",
            "born_in": "was born in",
            "type_of": "is a type of",
            "subclass_of": "is a subclass of",
            "color_is": "has color",
            "state_is": "has state",
        }
        return mapping.get(predicate, predicate.replace("_", " "))

    @staticmethod
    def _unique_facts(facts: list[Any]) -> list[Any]:
        """Deduplicate facts by their (subject, predicate, object) key."""
        seen: set[tuple[str, str, str]] = set()
        unique: list[Any] = []
        for f in facts:
            key = (
                str(getattr(f, "subject", "")).lower().strip(),
                str(getattr(f, "predicate", "")).lower().strip(),
                str(getattr(f, "obj", "")).lower().strip(),
            )
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique
