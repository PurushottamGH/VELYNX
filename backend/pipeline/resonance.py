"""Resonance — epistemic honesty injection and resonance composition."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger("uvicorn")


def build_resonance_context(
    soul_answer: dict | None,
) -> tuple[str, list[str], dict[str, float], dict[str, str]]:
    """
    Build the resonance context string from soul activation scores.

    Returns (resonance_context, top_concepts, resonance_scores, epistemic_states).
    Returns empty values when there is no soul_answer or no scores.
    """
    if not soul_answer:
        return "", [], {}, {}

    scores = soul_answer.get("scores", {})
    if not scores:
        return "", [], {}, {}

    # Phase 46: Epistemic Honesty Injection
    from backend.soul.soul_graph import get_epistemic_state

    top_concepts = list(scores.keys())[:5]
    epistemic_states = get_epistemic_state(top_concepts)
    resonance_scores = {c: round(scores[c], 3) for c in top_concepts}

    enriched_scores = []
    for c in top_concepts:
        score = resonance_scores[c]
        state = epistemic_states.get(c, "UNKNOWN")
        enriched_scores.append(f"{c}:{score} ({state})")

    resonance_context = (
        "SYSTEM [RESONANCE FIELD ACTIVE]: The user's query activated "
        "the following deep cognitive concepts: " + ", ".join(enriched_scores)
        + "\nCRITICAL INSTRUCTION: If a concept is marked INFERRED or UNCERTAIN, "
        "you MUST explicitly communicate this doubt to the user "
        "(e.g. 'I am inferring this, but I am not certain...'). "
        "Do not state uncertain concepts as absolute facts."
    )

    return resonance_context, top_concepts, resonance_scores, epistemic_states


async def fetch_episodic_recall(
    memory_manager: Any,
    top_concepts: list[str],
    resonance_context: str,
) -> tuple[dict | None, str]:
    """
    Fetch episodic memory tagged with the primary concept.

    Returns (recalled_memory, updated_resonance_context).
    """
    if not top_concepts or not resonance_context:
        return None, resonance_context

    primary_concept = top_concepts[0]
    try:
        past_eps = await asyncio.wait_for(
            memory_manager.recall_by_tag(primary_concept, limit=1),
            timeout=3.0,
        )
        if past_eps:
            past_prompt = past_eps[0].entry.metadata.get("prompt", "")
            past_answer = past_eps[0].entry.metadata.get("answer", "")[:200]
            recalled_memory = {
                "concept": primary_concept,
                "prompt": past_prompt,
                "answer": past_answer,
            }
            episodic_context = (
                f"\nEPISODIC RECALL: The last time you discussed '{primary_concept}', "
                f"the user said: '{past_prompt}'. "
                f"You answered: '{past_answer}'. "
                f"Use this to contextualize your response."
            )
            return recalled_memory, resonance_context + episodic_context
    except asyncio.TimeoutError:
        logger.debug("Episodic recall timed out (3s)")
    except Exception as exc:
        logger.debug("Episodic recall failed: %s", exc)

    return None, resonance_context
