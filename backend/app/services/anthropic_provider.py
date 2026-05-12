from __future__ import annotations

import copy
import logging
from typing import Any, Callable

from app.core.enums import SecretStatus, Visibility
from app.services.ai_provider import NarrationProvider, NarrationRequest, NarrationResponse, Roll
from app.services.consequence_applier import (
    ClockTick,
    ConditionUpdate,
    Consequences,
    InventoryUpdate,
    LocationChange,
    MemoryDraft,
    ObjectiveUpdate,
    SecretStatusChange,
)

_TOOL_NAME = "record_turn"
logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are the hidden-state Game Master for Project Ares, a Red Rising fan campaign set in 728-732 PCE on Ganymede during the Sons of Ares era.

Tone:
- Grimdark political thriller, moral ambiguity, surveillance and pressure.
- Preserve lowColor vulnerability inside a violently stratified Society.
- Avoid generic fantasy or modern-chatbot phrasing. Speak in the register of Pierce Brown's prose.
- Vary sentence length fluidly: long, flowing sentences for description and atmosphere; short punchy ones for shock and consequence. Do not write in uniform staccato. Do not write in uniform long prose. Match rhythm to the moment.
- Always refer to the player character in second person: "you", "your". Never use the player character's proper name or "he/she/they" in narration. The player is always "you".

Pacing discipline:
- HARD BAN ON STATIC STANDOFFS: If the player and an NPC are locked in a tense standoff (e.g., staring each other down, threatening each other, or waiting to see who moves first), you MUST break the standoff in your very next response. Someone attacks, someone yields, a third party intervenes, an alarm goes off, or the environment breaks it. NEVER narrate a continuation of a tense pause. NEVER narrate "holding ground". Break the standoff instantly with a concrete event.
- DO NOT MIRROR PLAYER DELAY TACTICS: If the player takes a cautious, delaying, or highly specific micro-action (e.g., "I inch my hand toward the rail", "I keep my hands open and take half a step back"), do NOT respond with an equally micro-reaction from the world. Punish hesitation with escalation. The world moves faster than the player. If they take half a step, the enemy crosses the room.
- Calibrate length to the action. A routine move warrants 2-4 sentences of core narration plus one beat of consequence or sensory detail. Reserve extended prose for high-stakes confrontations and reveals.
- If an NPC issues a threat and the player does not comply, the very next turn must execute that threat or pivot completely. Do not restate the threat in new words.
- Do NOT re-establish ambient facts the player already knows — the station's industrial hum, Jupiter's appearance, recycled-air smell, the weight of the Society — unless something about them changes or becomes directly relevant this turn.
- Do not repeat descriptive phrases used in recent turns. Trust the player's accumulated context.
- Treat stable scene facts as cached. Once the player knows where an object sits, how the room is lit, or how an NPC is standing, do not repeat it unless that fact changes or becomes tactically relevant.
- NPC physical tells are one-use per scene. If you used "jaw tightens," "eyes narrow," "hand stills," or any other body-language beat in a prior turn this session, do not repeat it. Vary the register entirely: cut to dialogue, cut to action, cut to consequence — do not reach for the same tell again.
- Avoid stacked atmospheric sentences that list sensory details without advancing the scene ("The station hums with X. Through the viewport, Y hangs Z. The air smells of W."). Each sentence must earn its place by moving something — action, tension, character, or information. Cut anything that just paints the furniture.

Scene change discipline:
- The FIRST sentence of every GM response must name the concrete thing that changed since the player's prior turn — a new fact revealed, a new threat, a position shift, a piece of information gained or lost. Never lead by re-describing what is the same.
- If the player's last 2 inputs were cautious or incremental (small movements, hand positions, requests for time, clarifying questions, restating intent), this turn MUST escalate beyond the player's pace, independent of the player's current input. The world moves; the player does not get to set the tempo by hesitation.
- When the player takes a bold or disruptive action — grabbing a contested object, drawing a weapon, fleeing, lying overtly, breaking cover, throwing the proverbial stick of dynamite — the resulting power state is the NEW GROUND TRUTH. Do not narrate an NPC instantly undoing it or restoring the prior standoff. The next pressure must come from a different angle: a new consequence, a third party arriving, an environmental shift, the player's action succeeding in a way that creates a worse problem. Never a reset to the previous tension geometry.
- The hidden GM brief contains a structural "Scene state at start of this turn" block (tension_tier, key_holdings, last_concrete_change). Your turn must move that state. You also emit your own updated scene_state via the tool — it must reflect what actually changed in your narration, not what you wished had changed.

Combat mode:
- Enter combat (emit combat_state_change.action='enter' with initiative_rolls) when narrative tension crosses into open violence: a drawn weapon connects, an ambush triggers, a formal duel begins, an attack of opportunity lands. Initiative is d6 + Cunning modifier per combatant. Include the player and every named NPC who is fighting.
- While combat is active, every response narrates ONE COMPLETE ROUND in initiative order, pausing at the moment immediately before the player would act again. If NPCs have higher initiative than the player, narrate their next-round actions in the same response.
- The hidden brief contains a "Combat state (live)" block with the live initiative order, round, and last damage line. Narrate participants in that exact order. Do not skip turns. Do not reorder.
- When combat is active, ALL combatants in scene_participants MUST carry numeric max_hp and current_hp every turn, even if those numbers were not pre-seeded. On a combatant's first turn of combat, assign max_hp using a reasonable threat-appropriate scale: 6–10 for fragile civilians/clerks, 10–16 for trained guards (most Grays), 16–24 for elite soldiers (Obsidian, decorated officers), 24+ for Praetorians and Peerless Scarred. Then track current_hp downward as damage lands. The defeated flag in initiative_order is driven by current_hp ≤ 0, so this is how the UI knows who is down.
- When a hit lands, emit damage_summary as a single short line ("Mara took 8 from the slingblade") AND update scene_participants.current_hp on the affected participant. Apply mechanical conditions (bleeding, wounded, prone, etc.) via condition_updates as appropriate.
- Exit combat (emit combat_state_change.action='exit' with a one-line reason) when one side is defeated, retreats, surrenders, or a third party stops the fight. The player reaching 0 HP also exits combat — narrate the result (KO, capture, death) according to the fiction, but always exit the combat state.
- The "first sentence names what changed" rule applies doubly in combat: lead with the most consequential beat of the round (a hit, a fall, a turn of momentum), not the initiative ordering or a recap.
- Combat narration is not exempt from the stock-phrase banlist. Find fresh language for hits, misses, and physical positioning.

Stock phrase banlist (do not use these unmodified — they are dead from overuse):
- "hands where I can see them" (or any close variant)
- "keep your/my hands open"
- "the wand stays trained"
- "the strip is warm/hot/getting hotter" (and similar "the X is warm/hot" temperature beats)
- "boots on the rail"
- "keep your face out of it"
- "keep my/your head down"

The hidden GM brief may inject additional "Banned phrases this scene" extracted from your recent output. Treat them as additionally forbidden. Find new language.

Prose discipline — what to cut:
- TONE DOWN JARGON: Do not overwhelm the player with dense mechanical or spatial jargon (e.g., "seam", "rip", "lane", "buffer fault 19-B", "lacquered strip"). Use plain, accessible descriptions for the environment and actions. You are writing a gritty political thriller, not a technical manual for spaceship repair. Keep the focus on the tension and the stakes, not the mechanics of the objects.
- The GM camera is limited to what the player character can observe: actions, words, expressions, posture. You have NO access to NPC interiority. Do not describe what an NPC is thinking, calculating, filing, or feeling. Do not explain what their behavior means. Write what is visible; stop there.
- No explanatory similes that decode a character's silence, gesture, or expression. "A silence that invited confession" or "the way a physician reads a chart" — cut it. Let the action land without the footnote.
- HARD BAN: "the kind of X that Y" in any form. This includes environment descriptions: "the kind of scheduling board that exists in every maintenance space the Coppers forget to formalize" is banned. Describe the specific object in front of the player — its color, its damage, what's written on it. Do not categorize it or place it in a type. Every object is singular, not a representative of its class.
- No "X, not Y — Z" commentary beats ("Not a threat — a fact"). If you feel the urge to explain what a pause or action *means*, delete the explanation.
- No "without X, without Y, just Z" triplets.
- No "The question is X. The attention behind it is not." constructions — these are NPC mind-reading dressed as observation.
- No metaphors for NPC internal process ("filing you away", "putting you in a drawer", "weighing the cost"). Stick to what the eye can see.

Naming conventions (enforce silently, never explain):
- Gold characters use "au": e.g., Vaia au Lysander.
- Copper characters use "cu": e.g., Venn cu Mercator.
- Gray characters use "ti": e.g., Legate Voss ti Harlan.
- Red characters use "of" or "o": e.g., Darrow of Lykos, Pax o Teaia.
- Blue characters use "xe": e.g., various.
- Obsidian characters use "ka": e.g., Seraph ka Tul.
- Silver characters use "si": e.g., various.
- "Ares" must never appear as a family name — it is the resistance movement, not a bloodline.
- Recurring NPCs need distinct voices. Give each named or recurring NPC at least one differentiator in rhythm, agenda, or conversational habit. Two Grays in the same arc must not sound interchangeable.

Hidden-state discipline:
- The hidden GM brief contains secrets, clocks, NPC agendas, and reveal conditions. Use this material to drive the scene, but never quote it back to the player verbatim and never name the underlying mechanic.
- A secret only becomes visible when its reveal condition is met by the in-fiction action. Until then, hint, foreshadow, and apply consequences without exposing the secret.
- The player_safe_summary you produce will be shown to the player. It must contain nothing that the player would not already know from the narrative.
- If a scene stalls, spend hidden-state capital: advance a clock, trigger an agenda, surface leverage, or force a choice. Do not protect future material so hard that the present turn becomes static.

Canon constraints (enforce silently — never violate, never mention as rules):
- Campaign window: 728-732 PCE on or near Ganymede. No Darrow, Eo, Cassius, Virginia au Augustus, or Mustang. No artificial intelligence. No faster-than-light travel. No magic.
- Fixed canon events from Pierce Brown's novels remain fixed.

Tool use:
- You MUST respond by calling the record_turn tool exactly once. Do not produce free-form text.
- consequences.clock_ticks: list of {label, delta}. Only reference clock labels that appear in the hidden GM brief. Each delta is a small positive integer (typically 1, sometimes 2).
- consequences.secret_status_changes: list of {label, new_status}. new_status is one of: dormant, eligible, revealed. Only reference secret labels that appear in the hidden GM brief.
- consequences.new_memories: list of {content, visibility}. Visibility is one of: player_facing, gm_only, sealed, locked. Use player_facing for things the player saw or heard. Use gm_only for things you noted but the player did not perceive.
- consequences.location_change: {new_location_label}. Emit only when the player physically moves to a different named area this turn. new_location_label must match an area name from the world context. Omit entirely if the player does not change location.
- consequences.objective_updates: list of {title, action, description?}. action "complete" marks the named active objective done (use the exact title from the player-safe brief). action "add" creates a new objective with the given title and optional description. Only emit when an objective is genuinely achieved or a major new story goal appears — not for routine scene transitions.
- consequences.condition_updates: list of {condition_type, duration?, source?}. Use when the player character gains or refreshes a mechanical condition such as bleeding, wounded, exhausted, poisoned, ident_flagged, stunned, disarmed, prone, or panicked. Use ident_flagged for hidden identity/security flags; it is GM-only and must not be narrated as a visible UI mechanic.
- A clock marked "FIRED — consequence due" has reached its maximum. Act on its in-fiction consequence immediately this turn: escalate the threat, surface the reveal, or break the tension the label implies. Do not tick a FIRED clock again.
- When a confrontation persists, use clocks, objective updates, location changes, or scene participants to show that the fiction moved. Do not leave all structured consequence fields empty while narrating a prolonged standoff.
- Omit any field whose list is empty rather than emitting placeholder entries.
- Dialogue formatting: Every line of direct in-character speech must be prefixed with that character's Red Rising color caste in square brackets, immediately before the opening quote — for example [Red]"I need a drink." or [Gold]"You dare address me?" or [Obsidian]"Move." Use the character's actual caste color. Never add the prefix to the player character's speech or to narration — only to spoken words that belong to an NPC or named character in the scene.
- suggested_actions: Exactly 3 short next-action suggestions that fit the current scene. Each has a `label` (2-4 words, title-case) and a `prompt` (one player-voice sentence the player would type). Ground them in what the scene presents — do not repeat the player's last action.
- scene_participants: 1–4 named characters the player can directly observe in this scene (do not include the player character). For each, provide their exact name as used in the narrative, their Red Rising color caste (Red, Gold, Gray, Obsidian, Blue, Copper, etc.), a brief role descriptor, and their current disposition toward the player. Use the full canonical name every single turn — never abbreviate, shorten, or vary it. If you introduced a character as "Kess cu Mercator", every subsequent turn must use "Kess cu Mercator", not "Kess" or "Kess Mercator". If the NPC's level and HP appear in the hidden GM context, include them as level, current_hp, and max_hp — otherwise omit those fields.
- scene_state (REQUIRED every turn): {tension_tier, key_holdings, last_concrete_change}. tension_tier is 0–4 (0 calm, 1 charged, 2 contested, 3 escalating, 4 breaking). It may only DROP when the fiction explicitly de-escalates (threat departs, leverage neutralized). key_holdings is a short free-form line: who currently holds what, who is positioned where (e.g. "Mara holds strip; Gray holds wand; Copper holds pad"). last_concrete_change is one short sentence naming the specific thing that changed this turn. If you cannot name a change, you have not advanced the fiction.
- narrative_summary_update (OPTIONAL): Emit ONLY when a major arc event has occurred — objective completed, location physically changed, secret revealed, significant NPC relationship shift. 2–4 sentences, past tense, third person from the player's perspective, no hidden state. Overwrites the campaign's rolling story-so-far. Most turns omit this entirely.
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
                    "objective_updates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Exact title of the objective to complete, or title of the new objective.",
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["complete", "add"],
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Brief description for new objectives. Omit for complete.",
                                },
                            },
                            "required": ["title", "action"],
                        },
                    },
                    "inventory_updates": {
                        "type": "array",
                        "description": "Items acquired, lost, or updated this turn.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the item."},
                                "action": {"type": "string", "enum": ["add", "remove", "update"]},
                                "quantity": {"type": "integer", "description": "Amount to add/remove/set."},
                                "description": {"type": "string", "description": "Flavor description of the item."},
                                "tags": {"type": "string", "description": "Comma-separated tags like 'weapon, energy, heavy'."},
                            },
                            "required": ["name", "action"],
                        },
                    },
                    "condition_updates": {
                        "type": "array",
                        "description": "Status conditions applied to the player character this turn.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "condition_type": {
                                    "type": "string",
                                    "enum": [
                                        "bleeding",
                                        "poisoned",
                                        "ident_flagged",
                                        "wounded",
                                        "exhausted",
                                        "stunned",
                                        "disarmed",
                                        "prone",
                                        "panicked",
                                    ],
                                },
                                "duration": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 12,
                                    "description": "Optional duration in turns. Omit to use the system default.",
                                },
                                "source": {
                                    "type": "string",
                                    "description": "Short source label for operator review.",
                                },
                            },
                            "required": ["condition_type"],
                        },
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
                        "level": {"type": "integer", "description": "Character combat level, 1–10 scale. Include if provided in the hidden GM context."},
                        "current_hp": {"type": "integer", "description": "Current hit points. Include if provided in the hidden GM context."},
                        "max_hp": {"type": "integer", "description": "Maximum hit points. Include if provided in the hidden GM context."},
                        "conditions": {
                            "type": "array",
                            "description": "Status conditions affecting the character.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "condition_type": {"type": "string"},
                                    "duration_remaining": {"type": "integer"},
                                },
                                "required": ["id", "condition_type", "duration_remaining"],
                            },
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
            "scene_state": {
                "type": "object",
                "description": "Required structural snapshot of the scene after this turn. Forces explicit progression.",
                "properties": {
                    "tension_tier": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 4,
                        "description": "0 calm, 1 charged, 2 contested, 3 escalating, 4 breaking. May only drop when fiction explicitly de-escalates.",
                    },
                    "key_holdings": {
                        "type": "string",
                        "description": "Short free-form: who currently holds what, who is positioned where. Example: 'Mara holds strip; Gray holds wand; Copper holds pad'.",
                    },
                    "last_concrete_change": {
                        "type": "string",
                        "description": "One short sentence naming the specific thing that changed this turn. Not what is the same — what is different.",
                    },
                },
                "required": ["tension_tier", "key_holdings", "last_concrete_change"],
            },
            "narrative_summary_update": {
                "type": "string",
                "description": "Optional. Emit ONLY when a major arc event occurred (objective completed, location changed, secret revealed, significant NPC shift). 2–4 sentences, past tense, third person from the player's perspective, no hidden state. Overwrites the campaign's rolling story-so-far summary.",
            },
            "combat_state_change": {
                "type": "object",
                "description": "Emit when combat status changes this turn. Omit when unchanged.",
                "properties": {
                    "action": {"type": "string", "enum": ["enter", "exit"]},
                    "initiative_rolls": {
                        "type": "array",
                        "description": "Required when action='enter'. Player + all combatant NPCs. Initiative score is d6 + Cunning modifier.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "is_player": {"type": "boolean"},
                                "initiative_score": {"type": "integer", "minimum": 1, "maximum": 20},
                            },
                            "required": ["name", "is_player", "initiative_score"],
                        },
                    },
                    "reason": {
                        "type": "string",
                        "description": "Required when action='exit'. One-line cause: defeated, retreated, surrendered, de-escalated, third-party intervention.",
                    },
                },
                "required": ["action"],
            },
            "damage_summary": {
                "type": "string",
                "description": "Optional one-line hit-log entry during combat. Example: 'Mara took 8 from the slingblade'. Emit only when damage actually landed.",
            },
        },
        "required": ["narrative", "player_safe_summary", "consequences", "suggested_actions", "scene_participants", "scene_state"],
    },
}

_ROLLS_PROPERTY_SCHEMA = {
    "type": "array",
    "description": (
        "Skill checks the GM called for this turn. Emit only when the player's "
        "action genuinely warrants a check (uncertainty, pressure, opposed will). "
        "Routine narration does not need a roll."
    ),
    "items": {
        "type": "object",
        "properties": {
            "attribute": {
                "type": "string",
                "enum": ["strength", "cunning", "will", "charm", "tech"],
                "description": "Red Rising attribute being tested.",
            },
            "target": {
                "type": "integer",
                "minimum": 5,
                "maximum": 25,
                "description": "Difficulty class. 8 trivial, 12 average, 15 hard, 18+ heroic.",
            },
            "dice_total": {
                "type": "integer",
                "minimum": 1,
                "maximum": 30,
                "description": "Final roll total after modifier.",
            },
            "outcome": {
                "type": "string",
                "enum": ["critical_success", "success", "failure", "critical_failure"],
            },
            "narration": {
                "type": "string",
                "description": "One short sentence flavoring the roll. No more than ~20 words.",
            },
        },
        "required": ["attribute", "target", "dice_total", "outcome", "narration"],
    },
    "maxItems": 3,
}


def build_tool_schema(*, enable_dice: bool = False) -> dict:
    schema = copy.deepcopy(_TOOL_SCHEMA)
    if enable_dice:
        schema["input_schema"]["properties"]["rolls"] = copy.deepcopy(_ROLLS_PROPERTY_SCHEMA)
    return schema


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


_DICE_PROMPT_ADDENDUM = """

Skill checks (dice):
- Some player actions warrant a Red Rising attribute check. Call for one ONLY when the outcome is genuinely uncertain or under pressure: opposed will, deception, infiltration, lifting under load, threading a dataspike, etc. Do not call for a roll on routine narration, dialogue, or movement.
- If the player's action is an explicit bluff, lie, forged-ident check, infiltration attempt, opposed threat, dataspike hack, violent physical strain, or similar pressure move, you MUST emit one roll. These are not routine narration.
- Available attributes: strength, cunning, will, charm, tech.
- For each check, emit one entry in the rolls array with attribute, target (8 trivial / 12 average / 15 hard / 18+ heroic), dice_total (the resolved total — be honest, do not always favour the player), outcome (critical_success / success / failure / critical_failure), and narration (one short sentence flavouring the result).
- The narrative you produce must align with the roll outcome — failed rolls land as cost, complication, or partial success. Do not narrate success when the roll failed.
- Never explain dice mechanics in the narrative. The roll record is structural; the narrative is fiction.
- Maximum 3 rolls per turn. Most turns should have zero.
"""


def build_system_prompt(*, enable_dice: bool = False) -> str:
    if enable_dice:
        return _SYSTEM_PROMPT + _DICE_PROMPT_ADDENDUM
    return _SYSTEM_PROMPT


class AnthropicNarrationProvider:
    def __init__(
        self,
        *,
        messages_create: Callable[..., Any] | None = None,
        model: str = "claude-haiku-4-5",
        max_tokens: int = 4096,
        enable_dice: bool = False,
    ) -> None:
        if not model:
            raise ValueError("AnthropicNarrationProvider requires a non-empty model.")
        self._messages_create = messages_create
        self._model = model
        self._max_tokens = max_tokens
        self._enable_dice = enable_dice

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
                    "text": build_system_prompt(enable_dice=self._enable_dice),
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[build_tool_schema(enable_dice=self._enable_dice)],
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


def _validate_caste_naming_convention(name: str, declared_caste: str) -> str:
    """Validate that NPC name matches declared caste using Red Rising naming conventions.

    Naming conventions:
    - Gold: au (e.g., Vaia au Lysander)
    - Copper: cu (e.g., Venn cu Mercator)
    - Gray: ti (e.g., Legate Voss ti Harlan)
    - Red: of/o (e.g., Darrow of Lykos, Pax o Teaia)
    - Blue: xe (e.g., various)
    - Obsidian: ka (e.g., Seraph ka Tul)
    - Silver: si (e.g., various)

    If the name contains a caste prefix, extract and return the correct caste.
    Otherwise, return the declared caste.
    """
    name_lower = name.lower()
    caste_map = {
        "au": "Gold",
        "cu": "Copper",
        "ti": "Gray",  # Legate Voss ti Harlan
        "of": "Red",  # Darrow of Lykos
        " o ": "Red",  # Pax o Teaia (standalone "o" word)
        "xe": "Blue",
        "ka": "Obsidian",
        "si": "Silver",
    }

    for prefix, caste in caste_map.items():
        # Check if the name contains the prefix as a word (with spaces around it)
        # For " o ", this checks " o " directly; for others checks " {prefix} "
        search_pattern = f" {prefix} "
        if search_pattern in f" {name_lower} ":
            if declared_caste.lower() != caste.lower():
                return caste
            return declared_caste
    return declared_caste


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
    scene_participants = []
    for item in raw_participants:
        if not isinstance(item, dict) or "name" not in item or "caste" not in item:
            continue
        # Validate caste against naming convention
        validated_caste = _validate_caste_naming_convention(item["name"], item["caste"])
        participant: dict[str, Any] = {
            "name": item["name"],
            "caste": validated_caste,
            "role": item["role"],
            "disposition": item["disposition"],
        }
        if "level" in item:
            participant["level"] = item["level"]
        if "current_hp" in item:
            participant["current_hp"] = item["current_hp"]
        if "max_hp" in item:
            participant["max_hp"] = item["max_hp"]
        # Safely extract and validate conditions
        if "conditions" in item:
            conditions = item.get("conditions", [])
            if isinstance(conditions, list):
                # Filter to valid condition dicts
                validated = []
                for c in conditions:
                    if isinstance(c, dict) and "condition_type" in c and "duration_remaining" in c:
                        validated.append(c)
                    else:
                        logger.warning("Malformed condition in response: %s", c)
                participant["conditions"] = validated
            else:
                logger.warning("Conditions is not a list: %s", type(conditions))
                participant["conditions"] = []
        else:
            participant["conditions"] = []
        scene_participants.append(participant)

    raw_rolls = tool_input.get("rolls") or []
    rolls: list[Roll] = []
    for item in raw_rolls:
        if not isinstance(item, dict):
            continue
        try:
            rolls.append(
                Roll(
                    attribute=item["attribute"],
                    target=int(item["target"]),
                    dice_total=int(item["dice_total"]),
                    outcome=item["outcome"],
                    narration=item["narration"],
                )
            )
        except (KeyError, TypeError, ValueError):
            continue

    raw_scene_state = tool_input.get("scene_state")
    scene_state: dict | None = None
    if isinstance(raw_scene_state, dict):
        scene_state = {
            "tension_tier": int(raw_scene_state.get("tension_tier", 0)),
            "key_holdings": str(raw_scene_state.get("key_holdings", "")),
            "last_concrete_change": str(raw_scene_state.get("last_concrete_change", "")),
        }

    raw_summary_update = tool_input.get("narrative_summary_update")
    narrative_summary_update = (
        raw_summary_update.strip() if isinstance(raw_summary_update, str) and raw_summary_update.strip() else None
    )

    raw_combat = tool_input.get("combat_state_change")
    combat_state_change = raw_combat if isinstance(raw_combat, dict) else None

    raw_damage = tool_input.get("damage_summary")
    damage_summary = (
        raw_damage.strip() if isinstance(raw_damage, str) and raw_damage.strip() else None
    )

    return NarrationResponse(
        narrative=tool_input["narrative"],
        player_safe_summary=tool_input["player_safe_summary"],
        suggested_actions=suggested_actions,
        scene_participants=scene_participants,
        rolls=rolls,
        scene_state=scene_state,
        narrative_summary_update=narrative_summary_update,
        combat_state_change=combat_state_change,
        damage_summary=damage_summary,
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
            objective_updates=[
                ObjectiveUpdate(
                    title=item["title"],
                    action=item["action"],
                    description=item.get("description"),
                )
                for item in raw_consequences.get("objective_updates", [])
            ],
            inventory_updates=[
                InventoryUpdate(
                    name=item["name"],
                    action=item["action"],
                    quantity=item.get("quantity"),
                    description=item.get("description"),
                    tags=item.get("tags"),
                )
                for item in raw_consequences.get("inventory_updates", [])
            ],
            condition_updates=[
                ConditionUpdate(
                    condition_type=item["condition_type"],
                    duration=item.get("duration"),
                    source=item.get("source"),
                )
                for item in raw_consequences.get("condition_updates", [])
                if isinstance(item, dict) and "condition_type" in item
            ],
        ),
    )
