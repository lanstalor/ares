from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.campaign import Campaign
from app.services.ai_provider import NarrationProvider, NarrationRequest
from app.services.canon_guard import evaluate_canon_guard
from app.services.consequence_applier import ConsequenceResult, apply_consequences
from app.services.context_builder import build_turn_context
from app.services.provider_registry import get_narration_provider


@dataclass
class TurnEngineResult:
    gm_response: str
    player_safe_summary: str
    context_excerpt: str
    canon_guard_passed: bool
    canon_guard_message: str | None
    clocks_fired: list[str] = field(default_factory=list)
    location_changed_to: str | None = None
    suggested_actions: list[dict] = field(default_factory=list)
    scene_participants: list[dict] = field(default_factory=list)
    revealed_secrets: list[dict] = field(default_factory=list)


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
        narration_provider = get_narration_provider(settings.generation_provider, settings.generation_model)

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

    consequence_result = ConsequenceResult(clocks_fired=[], location_changed_to=None)
    if canon_guard_passed:
        consequence_result = apply_consequences(session, campaign, narration.consequences)

    return TurnEngineResult(
        gm_response=narration.narrative,
        player_safe_summary=narration.player_safe_summary,
        context_excerpt=context.player_safe_brief,
        canon_guard_passed=canon_guard_passed,
        canon_guard_message=canon_guard_message,
        clocks_fired=consequence_result.clocks_fired,
        location_changed_to=consequence_result.location_changed_to,
        suggested_actions=narration.suggested_actions,
        scene_participants=narration.scene_participants,
        revealed_secrets=consequence_result.revealed_secrets,
    )
