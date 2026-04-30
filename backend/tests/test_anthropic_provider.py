from dataclasses import dataclass, field
from typing import Any

import pytest

from app.core.enums import SecretStatus, Visibility
from app.services.ai_provider import NarrationRequest
from app.services.anthropic_provider import AnthropicNarrationProvider


@dataclass
class _FakeBlock:
    type: str
    text: str = ""
    name: str = ""
    input: dict[str, Any] = field(default_factory=dict)


@dataclass
class _FakeMessage:
    content: list[_FakeBlock]
    stop_reason: str = "tool_use"


def _make_request() -> NarrationRequest:
    return NarrationRequest(
        campaign_name="Test Cell",
        current_date_pce=728,
        player_input="Watch Vex closely.",
        player_safe_brief="Player-safe brief here.",
        hidden_gm_brief="[GM-only context.] Hidden brief.",
    )


def _make_canned_response(consequences: dict[str, Any] | None = None) -> _FakeMessage:
    return _FakeMessage(
        content=[
            _FakeBlock(
                type="tool_use",
                name="record_turn",
                input={
                    "narrative": "Vex flinches as Davan watches.",
                    "player_safe_summary": "Vex looks unsettled.",
                    "suggested_actions": [
                        {
                            "label": "Watch Vex",
                            "prompt": "I keep my eyes on Vex and wait for the tell.",
                        },
                        {
                            "label": "Press Quietly",
                            "prompt": "I lower my voice and press Vex for the truth.",
                        },
                        {
                            "label": "Scan Exits",
                            "prompt": "I scan the exits and look for the cleanest way out.",
                        },
                    ],
                    "scene_participants": [
                        {
                            "name": "Vex ti Rhone",
                            "caste": "Gray",
                            "role": "Security escort",
                            "disposition": "suspicious",
                        }
                    ],
                    "consequences": consequences
                    or {
                        "clock_ticks": [],
                        "secret_status_changes": [],
                        "new_memories": [],
                    },
                },
            )
        ]
    )


def test_provider_parses_narrative_and_summary_from_tool_call() -> None:
    captured: dict[str, Any] = {}

    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        captured.update(kwargs)
        return _make_canned_response()

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create, model="claude-opus-4-7"
    )

    response = provider.narrate(_make_request())

    assert response.narrative == "Vex flinches as Davan watches."
    assert response.player_safe_summary == "Vex looks unsettled."


def test_provider_parses_suggested_actions_and_scene_participants() -> None:
    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        return _make_canned_response()

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        model="claude-sonnet-test",
    )

    response = provider.narrate(_make_request())

    assert len(response.suggested_actions) == 3
    assert response.suggested_actions[0]["label"] == "Watch Vex"
    assert response.suggested_actions[1]["prompt"] == "I lower my voice and press Vex for the truth."
    assert len(response.scene_participants) == 1
    assert response.scene_participants[0]["name"] == "Vex ti Rhone"
    assert response.scene_participants[0]["disposition"] == "suspicious"


def test_provider_parses_consequences_from_tool_call() -> None:
    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        return _make_canned_response(
            consequences={
                "clock_ticks": [{"label": "Citadel suspicion", "delta": 2}],
                "secret_status_changes": [
                    {
                        "label": "NPC: Vex / Hidden agenda",
                        "new_status": "eligible",
                    }
                ],
                "new_memories": [
                    {"content": "Vex flinched.", "visibility": "gm_only"}
                ],
            }
        )

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        model="claude-sonnet-test",
    )

    response = provider.narrate(_make_request())

    assert len(response.consequences.clock_ticks) == 1
    assert response.consequences.clock_ticks[0].label == "Citadel suspicion"
    assert response.consequences.clock_ticks[0].delta == 2
    assert len(response.consequences.secret_status_changes) == 1
    assert (
        response.consequences.secret_status_changes[0].new_status
        == SecretStatus.ELIGIBLE
    )
    assert len(response.consequences.new_memories) == 1
    assert response.consequences.new_memories[0].visibility == Visibility.GM_ONLY


def test_provider_sends_briefs_in_user_message_and_pins_tool_choice() -> None:
    captured: dict[str, Any] = {}

    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        captured.update(kwargs)
        return _make_canned_response()

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create, model="claude-opus-4-7"
    )
    provider.narrate(_make_request())

    assert captured["model"] == "claude-opus-4-7"
    assert captured["tool_choice"] == {"type": "tool", "name": "record_turn"}
    assert any(t["name"] == "record_turn" for t in captured["tools"])

    user_messages = [m for m in captured["messages"] if m["role"] == "user"]
    assert user_messages, "expected at least one user message"
    user_text = user_messages[-1]["content"]
    assert "Player-safe brief here." in user_text
    assert "[GM-only context.] Hidden brief." in user_text
    assert "Watch Vex closely." in user_text


def test_provider_system_prompt_includes_canon_and_hidden_state_rules() -> None:
    captured: dict[str, Any] = {}

    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        captured.update(kwargs)
        return _make_canned_response()

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        model="claude-sonnet-test",
    )
    provider.narrate(_make_request())

    system_blocks = captured["system"]
    if isinstance(system_blocks, str):
        system_text = system_blocks
    else:
        system_text = "\n".join(b.get("text", "") for b in system_blocks)

    assert "Red Rising" in system_text
    assert "Darrow" in system_text
    assert "hidden" in system_text.lower()


def test_provider_raises_when_no_tool_call_returned() -> None:
    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        return _FakeMessage(
            content=[_FakeBlock(type="text", text="I refuse to narrate.")],
            stop_reason="end_turn",
        )

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        model="claude-sonnet-test",
    )

    with pytest.raises(RuntimeError, match="record_turn"):
        provider.narrate(_make_request())


def test_provider_requires_non_empty_model() -> None:
    with pytest.raises(ValueError, match="non-empty model"):
        AnthropicNarrationProvider(messages_create=lambda **_: _make_canned_response(), model="")


def test_provider_parses_objective_updates_from_tool_call() -> None:
    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        return _make_canned_response(
            consequences={
                "objective_updates": [
                    {"title": "Check the Melt before shift", "action": "complete"},
                    {
                        "title": "Find Vex's handler",
                        "action": "add",
                        "description": "Track who Vex reports to.",
                    },
                ]
            }
        )

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        model="claude-sonnet-test",
    )

    response = provider.narrate(_make_request())

    updates = response.consequences.objective_updates
    assert len(updates) == 2
    assert updates[0].title == "Check the Melt before shift"
    assert updates[0].action == "complete"
    assert updates[0].description is None
    assert updates[1].title == "Find Vex's handler"
    assert updates[1].action == "add"
    assert updates[1].description == "Track who Vex reports to."


def test_provider_objective_updates_empty_when_absent() -> None:
    def fake_messages_create(**kwargs: Any) -> _FakeMessage:
        return _make_canned_response()

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        model="claude-sonnet-test",
    )

    response = provider.narrate(_make_request())

    assert response.consequences.objective_updates == []
