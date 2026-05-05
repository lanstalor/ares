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
