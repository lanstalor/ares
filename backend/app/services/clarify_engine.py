from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.campaign import Campaign
from app.services.ai_provider import NarrationProvider, NarrationRequest
from app.services.context_builder import build_turn_context
from app.services.provider_registry import get_narration_provider


def resolve_clarification(
    *,
    session: Session,
    campaign: Campaign,
    query: str,
    narration_provider: NarrationProvider | None = None,
) -> str:
    # We reuse build_turn_context but the "player_input" is the clarification query
    context = build_turn_context(session, campaign, query)

    if narration_provider is None:
        settings = get_settings()
        narration_provider = get_narration_provider(settings.generation_provider, settings.generation_model)

    explanation = narration_provider.clarify(
        NarrationRequest(
            campaign_name=campaign.name,
            current_date_pce=campaign.current_date_pce,
            player_input=query,
            player_safe_brief=context.player_safe_brief,
            hidden_gm_brief=context.hidden_gm_brief,
        )
    )

    return explanation
