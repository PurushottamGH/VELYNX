"""Tests for Phase 11E — Reasoning Modes."""
from __future__ import annotations

import pytest

from conversation.reasoning_modes import (
    ModeConfig,
    ReasoningMode,
    get_mode_config,
    select_reasoning_mode,
)


class TestReasoningMode:
    def test_all_modes_exist(self):
        assert ReasoningMode.ANALYTICAL
        assert ReasoningMode.EXPLORATORY
        assert ReasoningMode.ADVERSARIAL
        assert ReasoningMode.SYNTHESIS
        assert ReasoningMode.SOCRATIC


class TestSelectReasoningMode:
    def test_explicit_adversarial(self):
        mode = select_reasoning_mode("Think critically about this")
        assert mode == ReasoningMode.ADVERSARIAL

    def test_explicit_exploratory(self):
        mode = select_reasoning_mode("Brainstorm alternatives for me")
        assert mode == ReasoningMode.EXPLORATORY

    def test_explicit_socratic(self):
        mode = select_reasoning_mode("Guide me through this with questions")
        assert mode == ReasoningMode.SOCRATIC

    def test_explicit_analytical(self):
        mode = select_reasoning_mode("Break this down step by step")
        assert mode == ReasoningMode.ANALYTICAL

    def test_explicit_synthesis(self):
        mode = select_reasoning_mode("Connect these ideas and find patterns across")
        assert mode == ReasoningMode.SYNTHESIS

    def test_dialogue_act_challenge(self):
        mode = select_reasoning_mode("Some query", dialogue_act="challenge")
        assert mode == ReasoningMode.ADVERSARIAL

    def test_dialogue_act_follow_up(self):
        mode = select_reasoning_mode("Some query", dialogue_act="follow_up")
        assert mode == ReasoningMode.SYNTHESIS

    def test_domain_science(self):
        intent = {"domains": ["science"]}
        mode = select_reasoning_mode("Generic query", intent_result=intent)
        assert mode == ReasoningMode.ANALYTICAL

    def test_domain_philosophy(self):
        intent = {"domains": ["philosophy"]}
        mode = select_reasoning_mode("Generic query", intent_result=intent)
        assert mode == ReasoningMode.EXPLORATORY

    def test_domain_history(self):
        intent = {"domains": ["history"]}
        mode = select_reasoning_mode("Generic query", intent_result=intent)
        assert mode == ReasoningMode.SYNTHESIS

    def test_default_analytical(self):
        mode = select_reasoning_mode("Random question")
        assert mode == ReasoningMode.ANALYTICAL

    def test_explicit_overrides_dialogue(self):
        # Explicit request in text should override dialogue act
        mode = select_reasoning_mode("Think critically about this", dialogue_act="follow_up")
        assert mode == ReasoningMode.ADVERSARIAL


class TestGetModeConfig:
    def test_all_modes_have_configs(self):
        for mode in ReasoningMode:
            config = get_mode_config(mode)
            assert isinstance(config, ModeConfig)
            assert config.system_prompt_addendum
            assert config.mode == mode

    def test_analytical_temperature(self):
        config = get_mode_config(ReasoningMode.ANALYTICAL)
        assert config.temperature_adjustment < 0  # should be cooler

    def test_exploratory_temperature(self):
        config = get_mode_config(ReasoningMode.EXPLORATORY)
        assert config.temperature_adjustment > 0  # should be warmer

    def test_strategy_hints(self):
        config = get_mode_config(ReasoningMode.ANALYTICAL)
        assert config.strategy_hint == "depth_first"

        config = get_mode_config(ReasoningMode.ADVERSARIAL)
        assert config.strategy_hint == "contradiction_first"
