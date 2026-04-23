from dataclasses import dataclass

from app.models.campaign import Campaign
from app.core.config import get_settings
from app.services.ai_provider import NarrationRequest
from app.services.canon_guard import evaluate_canon_guard
from app.services.context_builder import build_turn_context
from app.services.provider_registry import get_narration_provider


@dataclass
class TurnEngineResult:
    gm_response: str
    player_safe_summary: str
    context_excerpt: str
    canon_guard_passed: bool
    canon_guard_message: str | None


def resolve_turn(campaign: Campaign, player_input: str) -> TurnEngineResult:
    context_excerpt = build_turn_context(campaign, player_input)
    settings = get_settings()
    narration_provider = get_narration_provider(settings.generation_provider)
    narration = narration_provider.narrate(
        NarrationRequest(
            campaign=campaign,
            player_input=player_input,
            context_excerpt=context_excerpt,
        )
    )
    gm_response = narration.narrative
    player_safe_summary = narration.player_safe_summary
    canon_guard_passed, canon_guard_message = evaluate_canon_guard(gm_response)
    return TurnEngineResult(
        gm_response=gm_response,
        player_safe_summary=player_safe_summary,
        context_excerpt=context_excerpt,
        canon_guard_passed=canon_guard_passed,
        canon_guard_message=canon_guard_message,
    )
