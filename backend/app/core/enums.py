from enum import StrEnum
from typing import TypedDict


class Visibility(StrEnum):
    PLAYER_FACING = "player_facing"
    GM_ONLY = "gm_only"
    SEALED = "sealed"
    LOCKED = "locked"


class ClockType(StrEnum):
    TENSION = "tension"
    REVEAL = "reveal"
    THREAT = "threat"


class SecretStatus(StrEnum):
    DORMANT = "dormant"
    ELIGIBLE = "eligible"
    REVEALED = "revealed"


class ConditionType(StrEnum):
    # Persistent conditions (survive across turns)
    BLEEDING = "bleeding"
    POISONED = "poisoned"
    IDENT_FLAGGED = "ident_flagged"
    WOUNDED = "wounded"
    EXHAUSTED = "exhausted"

    # Ephemeral conditions (last only current turn)
    STUNNED = "stunned"
    DISARMED = "disarmed"
    PRONE = "prone"
    PANICKED = "panicked"


class ConditionMetadata(TypedDict):
    """Structure for condition metadata."""
    persistence: str  # "persistent" or "ephemeral"
    visibility: str  # "player_facing" or "gm_only"
    base_duration: int  # number of turns
    effect: str  # type of effect (e.g., "damage", "penalty")
    effect_value: int | str  # numeric or string value


CONDITION_METADATA: dict[str, ConditionMetadata] = {
    # Persistent conditions
    "bleeding": {
        "persistence": "persistent",
        "visibility": "player_facing",
        "base_duration": 3,
        "effect": "damage",
        "effect_value": 1,
    },
    "poisoned": {
        "persistence": "persistent",
        "visibility": "player_facing",
        "base_duration": 3,
        "effect": "damage",
        "effect_value": 1,
    },
    "ident_flagged": {
        "persistence": "persistent",
        "visibility": "gm_only",
        "base_duration": 5,
        "effect": "penalty",
        "effect_value": "Cunning checks",
    },
    "wounded": {
        "persistence": "persistent",
        "visibility": "player_facing",
        "base_duration": 2,
        "effect": "penalty",
        "effect_value": "Strength checks",
    },
    "exhausted": {
        "persistence": "persistent",
        "visibility": "player_facing",
        "base_duration": 2,
        "effect": "penalty",
        "effect_value": "all checks",
    },
    # Ephemeral conditions
    "stunned": {
        "persistence": "ephemeral",
        "visibility": "player_facing",
        "base_duration": 1,
        "effect": "action_loss",
        "effect_value": "cannot act",
    },
    "disarmed": {
        "persistence": "ephemeral",
        "visibility": "player_facing",
        "base_duration": 1,
        "effect": "weapon_loss",
        "effect_value": "cannot use weapons",
    },
    "prone": {
        "persistence": "ephemeral",
        "visibility": "player_facing",
        "base_duration": 1,
        "effect": "movement_penalty",
        "effect_value": "disadvantage on escape",
    },
    "panicked": {
        "persistence": "ephemeral",
        "visibility": "player_facing",
        "base_duration": 1,
        "effect": "penalty",
        "effect_value": "Will checks",
    },
}
