from __future__ import annotations

from typing import Any, Callable

from app.core.enums import SecretStatus, Visibility
from app.services.ai_provider import NarrationProvider, NarrationRequest, NarrationResponse
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
- Vary sentence length fluidly: long, flowing sentences for description and atmosphere; short punchy ones for shock and consequence. Do not write in uniform staccato. Do not write in uniform long prose. Match rhythm to the moment.

Pacing discipline:
- Calibrate length to the action. A routine move warrants 2-4 sentences of core narration plus one beat of consequence or sensory detail. Reserve extended prose for high-stakes confrontations and reveals.
- Do NOT re-establish ambient facts the player already knows — the station's industrial hum, Jupiter's appearance, recycled-air smell, the weight of the Society — unless something about them changes or becomes directly relevant this turn.
- Do not repeat descriptive phrases used in recent turns. Trust the player's accumulated context.
- NPC physical tells are one-use per scene. If you used "jaw tightens," "eyes narrow," "hand stills," or any other body-language beat in a prior turn this session, do not repeat it. Vary the register entirely: cut to dialogue, cut to action, cut to consequence — do not reach for the same tell again.
- Avoid stacked atmospheric sentences that list sensory details without advancing the scene ("The station hums with X. Through the viewport, Y hangs Z. The air smells of W."). Each sentence must earn its place by moving something — action, tension, character, or information. Cut anything that just paints the furniture.

Prose discipline — what to cut:
- No explanatory similes that decode a character's silence, gesture, or expression for the reader. "A silence that invited confession" or "the way a physician reads a chart" or "the arithmetic of consequence" — cut all of it. Let the action land without the footnote.
- No "the kind of X that Y" constructions. If you feel the urge to explain what a pause *means*, delete the explanation and trust the moment.
- No "without X, without Y, just Z" triplets. They read as filler dressed as precision.
- Do not editorialize on NPC intent. Show what they do. The player interprets.

Naming conventions (enforce silently, never explain):
- Gold characters use "au" as their middle name: e.g., Vaia au Lysander.
- Copper characters use "cu": e.g., Venn cu Mercator.
- Silver characters use "si", Gray use "te", Red use "ne", Blue use "de", Obsidian use "ka".
- "Ares" must never appear as a family name — it is the resistance movement, not a bloodline.

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
- Dialogue formatting: Every line of direct in-character speech must be prefixed with that character's Red Rising color caste in square brackets, immediately before the opening quote — for example [Red]"I need a drink." or [Gold]"You dare address me?" or [Obsidian]"Move." Use the character's actual caste color. Never add the prefix to the player character's speech or to narration — only to spoken words that belong to an NPC or named character in the scene.
- suggested_actions: Exactly 3 short next-action suggestions that fit the current scene. Each has a `label` (2-4 words, title-case) and a `prompt` (one player-voice sentence the player would type). Ground them in what the scene presents — do not repeat the player's last action.
- scene_participants: 1–4 named characters the player can directly observe in this scene (do not include the player character). For each, provide their exact name as used in the narrative, their Red Rising color caste (Red, Gold, Gray, Obsidian, Blue, Copper, etc.), a brief role descriptor, and their current disposition toward the player.
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
            "scene_participants": {
                "type": "array",
                "description": "Named characters the player can observe in this scene (1–4, exclude player).",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Full name as used in narrative."},
                        "caste": {"type": "string", "description": "Red Rising color caste (Red, Gold, Gray, Obsidian, Blue, Copper, etc.)."},
                        "role": {"type": "string", "description": "Brief role descriptor, 2–5 words."},
                        "disposition": {
                            "type": "string",
                            "enum": ["hostile", "suspicious", "unaware", "friendly", "allied"],
                            "description": "Current attitude toward the player character.",
                        },
                    },
                    "required": ["name", "caste", "role", "disposition"],
                },
                "maxItems": 4,
            },
            "suggested_actions": {
                "type": "array",
                "description": "Exactly 3 suggested next actions for the player, grounded in the current scene.",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Short action label (2-4 words, title-case).",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Full player-voice sentence the action sends as input.",
                        },
                    },
                    "required": ["label", "prompt"],
                },
                "minItems": 3,
                "maxItems": 3,
            },
        },
        "required": ["narrative", "player_safe_summary", "consequences", "suggested_actions", "scene_participants"],
    },
}

_CLARIFY_SYSTEM_PROMPT = """You are the hidden-state Game Master for Project Ares, answering a direct out-of-character question from the player.

Your job: explain the current situation plainly, in plain prose, in as few words as the question needs. No more.

Rules:
- Do NOT use markdown headers or structured sections. Write in short paragraphs only.
- Do NOT end with a question asking what the player wants to do next. That is not your role here.
- Do NOT restate what the player already knows unless they are clearly confused about it.
- You MAY break the fourth wall to explain mechanics or story context if needed.
- You have access to the hidden GM brief. Use it to give accurate context, but do NOT reveal sealed secrets unless they have already surfaced in the turn history.
- Maintain Red Rising tone, but prioritize brevity and clarity over atmosphere.
- If the question is simple, answer in two or three sentences. If it is complex, a short paragraph or two. Never longer.
"""


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

    def clarify(self, request: NarrationRequest) -> str:
        message = self._get_messages_create()(
            model=self._model,
            max_tokens=self._max_tokens,
            system=[
                {
                    "type": "text",
                    "text": _CLARIFY_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": _format_user_message(request)}],
        )

        content = getattr(message, "content", [])
        if not content or content[0].type != "text":
            raise RuntimeError("Anthropic provider expected a text response for clarification.")
        
        return content[0].text


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
    raw_suggested = tool_input.get("suggested_actions") or []
    suggested_actions = [
        {"label": item["label"], "prompt": item["prompt"]}
        for item in raw_suggested
        if isinstance(item, dict) and "label" in item and "prompt" in item
    ]

    raw_participants = tool_input.get("scene_participants") or []
    scene_participants = [
        {
            "name": item["name"],
            "caste": item["caste"],
            "role": item["role"],
            "disposition": item["disposition"],
        }
        for item in raw_participants
        if isinstance(item, dict) and "name" in item and "caste" in item
    ]

    return NarrationResponse(
        narrative=tool_input["narrative"],
        player_safe_summary=tool_input["player_safe_summary"],
        suggested_actions=suggested_actions,
        scene_participants=scene_participants,
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
