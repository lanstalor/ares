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
