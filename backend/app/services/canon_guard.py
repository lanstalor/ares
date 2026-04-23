CANON_GUARD_RULES = {
    "darrow": "Darrow of Lykos does not exist in this campaign window.",
    "eo": "Eo does not exist in this campaign window.",
    "cassius": "Cassius au Bellona does not exist in this campaign window.",
    "virginia": "Virginia au Augustus does not exist in this campaign window.",
    "mustang": "Mustang does not exist in this campaign window.",
    "artificial intelligence": "AI is banned in the Society.",
    "faster-than-light": "FTL travel does not exist in Red Rising.",
}


def evaluate_canon_guard(text: str) -> tuple[bool, str | None]:
    lowered = text.lower()
    for trigger, message in CANON_GUARD_RULES.items():
        if trigger in lowered:
            return False, message
    return True, None
