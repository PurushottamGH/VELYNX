"""Reasoning modes — selects how VELYNX should reason about a query."""
from __future__ import annotations

import logging
import re
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger("uvicorn")


class ReasoningMode(str, Enum):
    ANALYTICAL = "analytical"
    EXPLORATORY = "exploratory"
    ADVERSARIAL = "adversarial"
    SYNTHESIS = "synthesis"
    SOCRATIC = "socratic"


class ModeConfig(BaseModel):
    """Configuration for a reasoning mode."""
    mode: ReasoningMode
    system_prompt_addendum: str
    temperature_adjustment: float = 0.0
    strategy_hint: str = ""


_MODE_CONFIGS: dict[ReasoningMode, ModeConfig] = {
    ReasoningMode.ANALYTICAL: ModeConfig(
        mode=ReasoningMode.ANALYTICAL,
        system_prompt_addendum=(
            "Break down the question step by step. Show your reasoning chain explicitly. "
            "Identify assumptions and verify them against evidence. "
            "Be precise and systematic."
        ),
        temperature_adjustment=-0.1,
        strategy_hint="depth_first",
    ),
    ReasoningMode.EXPLORATORY: ModeConfig(
        mode=ReasoningMode.EXPLORATORY,
        system_prompt_addendum=(
            "Consider multiple angles and perspectives. Brainstorm possibilities. "
            "What are the different ways to interpret this question? "
            "Explore the edges of what we know."
        ),
        temperature_adjustment=0.1,
        strategy_hint="broad_retrieval",
    ),
    ReasoningMode.ADVERSARIAL: ModeConfig(
        mode=ReasoningMode.ADVERSARIAL,
        system_prompt_addendum=(
            "Challenge the premise of the question. What could be wrong? "
            "Find weaknesses in the evidence. Consider counterarguments. "
            "Play devil's advocate — what would a skeptic say?"
        ),
        temperature_adjustment=0.0,
        strategy_hint="contradiction_first",
    ),
    ReasoningMode.SYNTHESIS: ModeConfig(
        mode=ReasoningMode.SYNTHESIS,
        system_prompt_addendum=(
            "Connect disparate ideas and sources. Find patterns across domains. "
            "What's the bigger picture? How do different pieces of evidence relate? "
            "Synthesize a unified understanding."
        ),
        temperature_adjustment=0.05,
        strategy_hint="broad_retrieval",
    ),
    ReasoningMode.SOCRATIC: ModeConfig(
        mode=ReasoningMode.SOCRATIC,
        system_prompt_addendum=(
            "Guide the user toward discovering the answer themselves. "
            "Ask probing questions that reveal assumptions. "
            "Don't just give the answer — help them think through it. "
            "If the question is factual, still provide the answer but also pose follow-up questions."
        ),
        temperature_adjustment=0.1,
        strategy_hint="incremental",
    ),
}

# Domain-to-mode mapping
_DOMAIN_MODE_MAP: dict[str, ReasoningMode] = {
    "science": ReasoningMode.ANALYTICAL,
    "history": ReasoningMode.SYNTHESIS,
    "philosophy": ReasoningMode.EXPLORATORY,
    "human": ReasoningMode.SYNTHESIS,
    "practical": ReasoningMode.ANALYTICAL,
}

# Dialogue act overrides
_ACT_MODE_MAP: dict[str, ReasoningMode] = {
    "challenge": ReasoningMode.ADVERSARIAL,
    "follow_up": ReasoningMode.SYNTHESIS,
    "correction": ReasoningMode.ANALYTICAL,
    "clarification": ReasoningMode.SOCRATIC,
}

# Explicit mode request patterns
_MODE_PATTERNS = {
    ReasoningMode.ADVERSARIAL: re.compile(
        r"\b(critically|challenge|skeptical|devil.?s?.?advocate|argue against|counter)\b",
        re.IGNORECASE,
    ),
    ReasoningMode.EXPLORATORY: re.compile(
        r"\b(brainstorm|explore|what if|alternatives|different ways|possibilities)\b",
        re.IGNORECASE,
    ),
    ReasoningMode.SOCRATIC: re.compile(
        r"\b(socratic|guide me|help me think|ask me questions|walk me through)\b",
        re.IGNORECASE,
    ),
    ReasoningMode.ANALYTICAL: re.compile(
        r"\b(analyze|step by step|break down|systematic|detailed analysis)\b",
        re.IGNORECASE,
    ),
    ReasoningMode.SYNTHESIS: re.compile(
        r"\b(connect|synthesize|big picture|how.*relate|patterns across)\b",
        re.IGNORECASE,
    ),
}


def select_reasoning_mode(
    query: str,
    intent_result: dict | None = None,
    dialogue_act: str | None = None,
) -> ReasoningMode:
    """Select the appropriate reasoning mode based on query, intent, and dialogue act.

    Priority:
    1. Explicit user request in query text
    2. Dialogue act override
    3. Domain-based heuristic from intent
    4. Default to ANALYTICAL
    """
    # 1. Check for explicit mode request
    for mode, pattern in _MODE_PATTERNS.items():
        if pattern.search(query):
            logger.debug("Reasoning mode from explicit request: %s", mode.value)
            return mode

    # 2. Dialogue act override
    if dialogue_act and dialogue_act in _ACT_MODE_MAP:
        mode = _ACT_MODE_MAP[dialogue_act]
        logger.debug("Reasoning mode from dialogue act '%s': %s", dialogue_act, mode.value)
        return mode

    # 3. Domain-based heuristic
    if intent_result:
        domains = intent_result.get("domains", [])
        for domain in domains:
            if domain in _DOMAIN_MODE_MAP:
                mode = _DOMAIN_MODE_MAP[domain]
                logger.debug("Reasoning mode from domain '%s': %s", domain, mode.value)
                return mode

    # 4. Default
    return ReasoningMode.ANALYTICAL


def get_mode_config(mode: ReasoningMode) -> ModeConfig:
    """Get the configuration for a reasoning mode."""
    return _MODE_CONFIGS.get(mode, _MODE_CONFIGS[ReasoningMode.ANALYTICAL])
