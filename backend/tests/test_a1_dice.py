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


from app.services.anthropic_provider import _build_response


_BASE_TOOL_INPUT = {
    "narrative": "n",
    "player_safe_summary": "s",
    "consequences": {},
    "suggested_actions": [
        {"label": "A", "prompt": "do A"},
        {"label": "B", "prompt": "do B"},
        {"label": "C", "prompt": "do C"},
    ],
    "scene_participants": [],
}


def test_build_response_extracts_rolls() -> None:
    tool_input = {
        **_BASE_TOOL_INPUT,
        "rolls": [
            {
                "attribute": "cunning",
                "target": 14,
                "dice_total": 17,
                "outcome": "success",
                "narration": "Davan reads the tell before it lands.",
            }
        ],
    }
    response = _build_response(tool_input)
    assert len(response.rolls) == 1
    roll = response.rolls[0]
    assert roll.attribute == "cunning"
    assert roll.target == 14
    assert roll.outcome == "success"


def test_build_response_handles_missing_rolls() -> None:
    response = _build_response(_BASE_TOOL_INPUT)
    assert response.rolls == []


def test_build_response_skips_malformed_rolls() -> None:
    tool_input = {
        **_BASE_TOOL_INPUT,
        "rolls": [
            "not-a-dict",
            {"attribute": "will"},  # missing required fields
            {
                "attribute": "tech",
                "target": 12,
                "dice_total": 8,
                "outcome": "failure",
                "narration": "The dataspike chirps the wrong tone.",
            },
        ],
    }
    response = _build_response(tool_input)
    assert len(response.rolls) == 1
    assert response.rolls[0].attribute == "tech"


from app.services.anthropic_provider import AnthropicNarrationProvider


def test_provider_passes_enable_dice_to_schema() -> None:
    captured: dict = {}

    class _Block:
        type = "tool_use"
        name = "record_turn"
        input = _BASE_TOOL_INPUT

    class _Message:
        content = [_Block()]

    def fake_messages_create(**kwargs):
        captured.update(kwargs)
        return _Message()

    from app.services.ai_provider import NarrationRequest

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        enable_dice=True,
    )
    provider.narrate(
        NarrationRequest(
            campaign_name="x",
            current_date_pce=728,
            player_input="probe",
            player_safe_brief="b",
            hidden_gm_brief="h",
        )
    )
    tool_schema = captured["tools"][0]
    assert "rolls" in tool_schema["input_schema"]["properties"]


def test_provider_default_omits_rolls_from_schema() -> None:
    captured: dict = {}

    class _Block:
        type = "tool_use"
        name = "record_turn"
        input = _BASE_TOOL_INPUT

    class _Message:
        content = [_Block()]

    def fake_messages_create(**kwargs):
        captured.update(kwargs)
        return _Message()

    from app.services.ai_provider import NarrationRequest

    provider = AnthropicNarrationProvider(messages_create=fake_messages_create)
    provider.narrate(
        NarrationRequest(
            campaign_name="x",
            current_date_pce=728,
            player_input="probe",
            player_safe_brief="b",
            hidden_gm_brief="h",
        )
    )
    tool_schema = captured["tools"][0]
    assert "rolls" not in tool_schema["input_schema"]["properties"]
