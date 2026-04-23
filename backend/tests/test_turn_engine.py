from app.models.campaign import Campaign
from app.services.turn_engine import resolve_turn


def test_turn_engine_returns_context_and_summary() -> None:
    campaign = Campaign(name="Project Ares", tagline="Hidden-state test campaign", current_date_pce=728)
    result = resolve_turn(campaign, "Check the Melt before shift.")

    assert "Project Ares" in result.context_excerpt
    assert "Check the Melt" in result.player_safe_summary
    assert result.canon_guard_passed is True
