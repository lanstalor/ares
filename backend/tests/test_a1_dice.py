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


from app.services.anthropic_provider import build_system_prompt


def test_system_prompt_omits_dice_guidance_when_disabled() -> None:
    prompt = build_system_prompt(enable_dice=False)
    assert "skill check" not in prompt.lower()
    assert "rolls:" not in prompt


def test_system_prompt_includes_dice_guidance_when_enabled() -> None:
    prompt = build_system_prompt(enable_dice=True)
    lowered = prompt.lower()
    assert "skill check" in lowered or "attribute check" in lowered
    assert "cunning" in lowered
    assert "do not call for a roll" in lowered or "do not roll" in lowered
    assert "bluff" in lowered
    assert "must emit one roll" in lowered


from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.campaign import Campaign
from app.services.ai_provider import NarrationRequest
from app.services.consequence_applier import Consequences
from app.services.turn_engine import resolve_turn


class _RollProvider:
    def __init__(self, rolls):
        self._rolls = rolls

    def narrate(self, request: NarrationRequest) -> NarrationResponse:
        return NarrationResponse(
            narrative="n",
            player_safe_summary="s",
            consequences=Consequences(),
            rolls=self._rolls,
        )

    def clarify(self, request: NarrationRequest) -> str:
        return "clarified"


def _bare_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def test_resolve_turn_returns_rolls() -> None:
    session = _bare_session()
    campaign = Campaign(
        name="t",
        tagline="t",
        current_date_pce=728,
        current_location_label="Crescent Block",
    )
    session.add(campaign)
    session.flush()

    provider = _RollProvider(
        [Roll(attribute="cunning", target=14, dice_total=17, outcome="success", narration="x.")]
    )
    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="lie to the Copper",
        narration_provider=provider,
    )
    assert len(result.rolls) == 1
    assert result.rolls[0].attribute == "cunning"


def test_turns_endpoint_returns_rolls(monkeypatch) -> None:
    from app.api.routes.campaigns import create_campaign
    from app.api.routes.turns import create_turn
    from app.schemas.campaign import CampaignCreate
    from app.schemas.turn import TurnCreate
    from app.services import turn_engine as turn_engine_module

    captured_provider = _RollProvider(
        [Roll(attribute="will", target=12, dice_total=15, outcome="success", narration="ok.")]
    )

    original_resolve = turn_engine_module.resolve_turn

    def fake_resolve(*, session, campaign, player_input, narration_provider=None):
        return original_resolve(
            session=session,
            campaign=campaign,
            player_input=player_input,
            narration_provider=captured_provider,
        )

    monkeypatch.setattr(
        "app.api.routes.turns.resolve_turn",
        fake_resolve,
    )

    session = _bare_session()
    campaign = create_campaign(CampaignCreate(name="Turn Test"), session)

    response = create_turn(campaign.id, TurnCreate(player_input="hold the line"), session)
    assert response.rolls[0]["attribute"] == "will"
    assert response.rolls[0]["outcome"] == "success"


def test_openai_provider_passes_enable_dice_to_schema_and_prompt() -> None:
    from types import SimpleNamespace

    from app.services.openai_provider import OpenAINarrationProvider

    captured: dict = {}

    class Completions:
        def create(self, **kwargs):
            captured.update(kwargs)
            message = SimpleNamespace(
                content=None,
                tool_calls=[
                    SimpleNamespace(
                        function=SimpleNamespace(
                            name="record_turn",
                            arguments='{"narrative":"n","player_safe_summary":"s","consequences":{},"suggested_actions":[{"label":"A","prompt":"do A"},{"label":"B","prompt":"do B"},{"label":"C","prompt":"do C"}],"scene_participants":[]}',
                        )
                    )
                ],
            )
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    provider = OpenAINarrationProvider(client=client, enable_dice=True)
    provider.narrate(
        NarrationRequest(
            campaign_name="x",
            current_date_pce=728,
            player_input="probe",
            player_safe_brief="b",
            hidden_gm_brief="h",
        )
    )

    properties = captured["tools"][0]["function"]["parameters"]["properties"]
    assert "rolls" in properties
    assert "skill check" in captured["messages"][0]["content"].lower()


def test_registry_passes_enable_dice_to_openai_provider() -> None:
    from app.services.openai_provider import OpenAINarrationProvider
    from app.services.provider_registry import get_narration_provider

    provider = get_narration_provider("openai", "gpt-test", enable_dice=True)

    assert isinstance(provider, OpenAINarrationProvider)
    assert provider._model == "gpt-test"
    assert provider._enable_dice is True
