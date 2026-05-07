from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import CONDITION_METADATA
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.conditions import Condition
from app.services.ai_provider import NarrationProvider, NarrationRequest, Roll
from app.services.canon_guard import evaluate_canon_guard
from app.services.consequence_applier import ConsequenceResult, apply_consequences
from app.services.context_builder import build_turn_context
from app.services.provider_registry import get_narration_provider

logger = logging.getLogger(__name__)


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
    rolls: list[Roll] = field(default_factory=list)


def _process_conditions(session: Session, campaign: Campaign) -> None:
    """
    Process all active conditions at turn boundary.

    For each character in the campaign:
    - Apply condition effects via consequences
    - Decrement duration
    - Remove expired/ephemeral conditions

    This is called AFTER consequences are applied, so consequence-created
    conditions can take effect this turn.
    """
    # Import at function level to avoid circular imports
    from app.services.condition_service import get_active_conditions, remove_condition

    # Get all characters in campaign
    characters = session.scalars(
        select(Character).where(Character.campaign_id == campaign.id)
    ).all()

    for character in characters:
        conditions = get_active_conditions(session, campaign.id, character.id)

        for condition in conditions:
            metadata = CONDITION_METADATA.get(condition.condition_type)
            if not metadata:
                logger.warning(f"Unknown condition type: {condition.condition_type}")
                continue

            # 1. Apply condition effect via consequence BEFORE decrementing duration
            effect = metadata.get("effect")
            effect_value = metadata.get("effect_value")

            if effect == "damage" and effect_value is not None:
                # Apply damage consequence
                if character.current_hp is not None:
                    character.current_hp = max(0, character.current_hp - effect_value)
                    logger.debug(
                        f"Applied {effect} effect to {character.name}: "
                        f"HP reduced by {effect_value} to {character.current_hp}"
                    )
            elif effect == "penalty":
                # Penalty effects are noted but actual check mechanics are
                # evaluated at narration time
                logger.debug(
                    f"Applied {effect} effect to {character.name}: "
                    f"penalty type {effect_value}"
                )

            # 2. Decrement duration
            condition.duration_remaining -= 1
            session.flush()

            # 3. Remove if expired (duration_remaining <= 0) or ephemeral
            if condition.persistence == "ephemeral" or condition.duration_remaining <= 0:
                remove_condition(
                    session,
                    campaign.id,
                    character.id,
                    condition.condition_type,
                )

    session.commit()


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
        narration_provider = get_narration_provider(
            settings.generation_provider,
            settings.generation_model,
            enable_dice=settings.enable_dice,
        )

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
        # Process conditions AFTER consequences are applied
        _process_conditions(session, campaign)

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
        rolls=narration.rolls,
    )
