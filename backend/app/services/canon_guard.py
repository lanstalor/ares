from __future__ import annotations

import re

CANON_GUARD_RULES: dict[str, str] = {
    "darrow": "Darrow of Lykos does not exist in this campaign window.",
    "eo": "Eo does not exist in this campaign window.",
    "cassius": "Cassius au Bellona does not exist in this campaign window.",
    "virginia au augustus": "Virginia au Augustus does not exist in this campaign window.",
    "mustang": "Mustang does not exist in this campaign window.",
    "artificial intelligence": "AI is banned in the Society.",
    "faster-than-light": "FTL travel does not exist in Red Rising.",
}

_COMPILED: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b" + re.escape(trigger) + r"\b", re.IGNORECASE), message)
    for trigger, message in CANON_GUARD_RULES.items()
]


def evaluate_canon_guard(text: str) -> tuple[bool, str | None]:
    for pattern, message in _COMPILED:
        if pattern.search(text):
            return False, message
    return True, None
