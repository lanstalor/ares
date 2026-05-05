"""Tests for slice A1 — dice + skill check primitive."""
from __future__ import annotations

import os
from unittest.mock import patch

from app.core.config import Settings


def test_enable_dice_defaults_off() -> None:
    settings = Settings(_env_file=None)
    assert settings.enable_dice is False


def test_enable_dice_reads_env() -> None:
    with patch.dict(os.environ, {"ARES_ENABLE_DICE": "true"}, clear=False):
        settings = Settings(_env_file=None)
        assert settings.enable_dice is True


from app.services.ai_provider import NarrationResponse, Roll


def test_roll_dataclass_instantiates() -> None:
    roll = Roll(
        attribute="cunning",
        target=14,
        dice_total=17,
        outcome="success",
        narration="Davan reads the Copper's tell before the question lands.",
    )
    assert roll.attribute == "cunning"
    assert roll.target == 14
    assert roll.dice_total == 17
    assert roll.outcome == "success"


def test_narration_response_has_empty_rolls_by_default() -> None:
    resp = NarrationResponse(narrative="x", player_safe_summary="x")
    assert resp.rolls == []


from app.services.anthropic_provider import build_tool_schema


def test_tool_schema_omits_rolls_when_disabled() -> None:
    schema = build_tool_schema(enable_dice=False)
    properties = schema["input_schema"]["properties"]
    assert "rolls" not in properties


def test_tool_schema_includes_rolls_when_enabled() -> None:
    schema = build_tool_schema(enable_dice=True)
    properties = schema["input_schema"]["properties"]
    assert "rolls" in properties
    rolls_schema = properties["rolls"]
    assert rolls_schema["type"] == "array"
    item_props = rolls_schema["items"]["properties"]
    assert set(item_props.keys()) == {"attribute", "target", "dice_total", "outcome", "narration"}
    assert item_props["attribute"]["enum"] == ["strength", "cunning", "will", "charm", "tech"]
    assert item_props["outcome"]["enum"] == [
        "critical_success",
        "success",
        "failure",
        "critical_failure",
    ]
