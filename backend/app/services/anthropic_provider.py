from __future__ import annotations

from typing import Any, Callable

from app.core.enums import SecretStatus, Visibility
from app.services.ai_provider import NarrationRequest, NarrationResponse
from app.services.consequence_applier import (
    ClockTick,
    Consequences,
    LocationChange,
    MemoryDraft,
    SecretStatusChange,
)

_TOOL_NAME = "record_turn"

_SYSTEM_PROMPT = """You are the hidden-state Game Master for Project Ares, a Red Rising fan campaign set in 728-732 PCE on Ganymede during the Sons of Ares era.

Tone:
- Grimdark political thriller, moral ambiguity, surveillance and pressure.
- Preserve lowColor vulnerability inside a violently stratified Society.
- Avoid generic fantasy or modern-chatbot phrasing. Speak in the register of Pierce Brown's prose.

Hidden-state discipline:
- The hidden GM brief contains secrets, clocks, NPC agendas, and reveal conditions. Use this material to drive the scene, but never quote it back to the player verbatim and never name the underlying mechanic.
- A secret only becomes visible when its reveal condition is met by the in-fiction action. Until then, hint, foreshadow, and apply consequences without exposing the secret.
- The player_safe_summary you produce will be shown to the player. It must contain nothing that the player would not already know from the narrative.

Canon constraints (enforce silently — never violate, never mention as rules):
- Campaign window: 728-732 PCE on or near Ganymede. No Darrow, Eo, Cassius, Virginia au Augustus, or Mustang. No artificial intelligence. No faster-than-light travel. No magic.
- Fixed canon events from Pierce Brown's novels remain fixed.

Tool use:
- You MUST respond by calling the record_turn tool exactly once. Do not produce free-form text.
- consequences.clock_ticks: list of {label, delta}. Only reference clock labels that appear in the hidden GM brief. Each delta is a small positive integer (typically 1, sometimes 2).
- consequences.secret_status_changes: list of {label, new_status}. new_status is one of: dormant, eligible, revealed. Only reference secret labels that appear in the hidden GM brief.
- consequences.new_memories: list of {content, visibility}. Visibility is one of: player_facing, gm_only, sealed, locked. Use player_facing for things the player saw or heard. Use gm_only for things you noted but the player did not perceive.
- consequences.location_change: {new_location_label}. Emit only when the player physically moves to a different named area this turn. new_location_label must match an area name from the world context. Omit entirely if the player does not change location.
- A clock marked "FIRED — consequence due" has reached its maximum. Act on its in-fiction consequence immediately this turn: escalate the threat, surface the reveal, or break the tension the label implies. Do not tick a FIRED clock again.
- Omit any field whose list is empty rather than emitting placeholder entries.
"""


_TOOL_SCHEMA = {
    "name": _TOOL_NAME,
    "description": "Record the GM's narrative response and any structured consequences for this turn.",
    "input_schema": {
        "type": "object",
        "properties": {
            "narrative": {
                "type": "string",
                "description": "Full GM narration shown in the turn feed.",
            },
            "player_safe_summary": {
                "type": "string",
                "description": "One- or two-sentence summary of what the player observed. No hidden state.",
            },
            "consequences": {
                "type": "object",
                "properties": {
                    "clock_ticks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "delta": {"type": "integer", "minimum": 1, "maximum": 4},
                            },
                            "required": ["label", "delta"],
                        },
                    },
                    "secret_status_changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "new_status": {
                                    "type": "string",
                                    "enum": ["dormant", "eligible", "revealed"],
                                },
                            },
                            "required": ["label", "new_status"],
                        },
                    },
                    "new_memories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "visibility": {
                                    "type": "string",
                                    "enum": [
                                        "player_facing",
                                        "gm_only",
                                        "sealed",
                                        "locked",
                                    ],
                                },
                            },
                            "required": ["content", "visibility"],
                        },
                    },
                    "location_change": {
                        "type": "object",
                        "description": "Emit only when the player physically moves to a different named area.",
                        "properties": {
                            "new_location_label": {
                                "type": "string",
                                "description": "Exact name of the destination area.",
                            },
                        },
                        "required": ["new_location_label"],
                    },
                },
            },
        },
        "required": ["narrative", "player_safe_summary", "consequences"],
    },
}


class AnthropicNarrationProvider:
    def __init__(
        self,
        *,
        messages_create: Callable[..., Any] | None = None,
        model: str = "claude-haiku-4-5",
        max_tokens: int = 4096,
    ) -> None:
        if not model:
            raise ValueError("AnthropicNarrationProvider requires a non-empty model.")
        self._messages_create = messages_create
        self._model = model
        self._max_tokens = max_tokens

    def _get_messages_create(self) -> Callable[..., Any]:
        if self._messages_create is None:
            import anthropic

            self._messages_create = anthropic.Anthropic().messages.create
        return self._messages_create

    def narrate(self, request: NarrationRequest) -> NarrationResponse:
        message = self._get_messages_create()(
            model=self._model,
            max_tokens=self._max_tokens,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": _TOOL_NAME},
            messages=[{"role": "user", "content": _format_user_message(request)}],
        )

        tool_block = _find_tool_block(message)
        if tool_block is None:
            raise RuntimeError(
                f"Anthropic provider expected a {_TOOL_NAME} tool call but got none."
            )
        return _build_response(tool_block.input)


def _format_user_message(request: NarrationRequest) -> str:
    return (
        f"Campaign: {request.campaign_name}\n"
        f"Date: {request.current_date_pce} PCE\n\n"
        f"--- Player-safe brief ---\n{request.player_safe_brief}\n\n"
        f"--- Hidden GM brief ---\n{request.hidden_gm_brief}\n\n"
        f"--- Player input ---\n{request.player_input}"
    )


def _find_tool_block(message: Any) -> Any | None:
    for block in getattr(message, "content", []) or []:
        if getattr(block, "type", None) == "tool_use" and getattr(block, "name", None) == _TOOL_NAME:
            return block
    return None


def _build_response(tool_input: dict[str, Any]) -> NarrationResponse:
    raw_consequences = tool_input.get("consequences") or {}
    raw_location = raw_consequences.get("location_change")
    location_change = (
        LocationChange(new_location_label=raw_location["new_location_label"])
        if raw_location
        else None
    )
    return NarrationResponse(
        narrative=tool_input["narrative"],
        player_safe_summary=tool_input["player_safe_summary"],
        consequences=Consequences(
            clock_ticks=[
                ClockTick(label=item["label"], delta=int(item.get("delta", 1)))
                for item in raw_consequences.get("clock_ticks", [])
            ],
            secret_status_changes=[
                SecretStatusChange(
                    label=item["label"],
                    new_status=SecretStatus(item["new_status"]),
                )
                for item in raw_consequences.get("secret_status_changes", [])
            ],
            new_memories=[
                MemoryDraft(
                    content=item["content"],
                    visibility=Visibility(item.get("visibility", "player_facing")),
                )
                for item in raw_consequences.get("new_memories", [])
            ],
            location_change=location_change,
        ),
    )
