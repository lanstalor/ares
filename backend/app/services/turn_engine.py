from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.campaign import Campaign
from app.services.ai_provider import NarrationProvider, NarrationRequest
from app.services.canon_guard import evaluate_canon_guard
from app.services.consequence_applier import apply_consequences
from app.services.context_builder import build_turn_context
from app.services.provider_registry import get_narration_provider


@dataclass
class TurnEngineResult:
    gm_response: str
    player_safe_summary: str
    context_excerpt: str
    canon_guard_passed: bool
    canon_guard_message: str | None


def resolve_turn(
    *,
    session: Session,
    campaign: Campaign,
    player_input: str,
    narration_provider: NarrationProvider | None = None,
) -> TurnEngineResult:
    context = build_turn_context(session, campaign, player_input)

    if narration_provider is None:
        settings = get_settings()
        narration_provider = get_narration_provider(settings.generation_provider)

    narration = narration_provider.narrate(
        NarrationRequest(
            campaign_name=campaign.name,
            current_date_pce=campaign.current_date_pce,
            player_input=player_input,
            player_safe_brief=context.player_safe_brief,
            hidden_gm_brief=context.hidden_gm_brief,
        )
    )

    canon_guard_passed, canon_guard_message = evaluate_canon_guard(narration.narrative)

    if canon_guard_passed:
        apply_consequences(session, campaign, narration.consequences)

    return TurnEngineResult(
        gm_response=narration.narrative,
        player_safe_summary=narration.player_safe_summary,
        context_excerpt=context.player_safe_brief,
        canon_guard_passed=canon_guard_passed,
        canon_guard_message=canon_guard_message,
    )
