from enum import StrEnum


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
