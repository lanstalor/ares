from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.memory import Turn
from app.schemas.turn import TurnCreate, TurnRead, TurnResolution
from app.services.scene_art import ensure_scene_art
from app.services.turn_engine import resolve_turn

router = APIRouter()


@router.get("/{campaign_id}/turns", response_model=list[TurnRead])
def list_turns(
    campaign_id: str,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[Turn]:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    statement = (
        select(Turn)
        .where(Turn.campaign_id == campaign_id)
        .order_by(Turn.created_at.desc())
        .limit(limit)
    )
    return list(reversed(list(session.scalars(statement))))


@router.post("/{campaign_id}/turns", response_model=TurnResolution, status_code=201)
def create_turn(campaign_id: str, payload: TurnCreate, session: SessionDep) -> TurnResolution:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input=payload.player_input,
    )

    turn = Turn(
        campaign_id=campaign.id,
        player_input=payload.player_input,
        gm_response=result.gm_response,
        player_safe_summary=result.player_safe_summary,
    )
    session.add(turn)
    scene_art = None
    if result.location_changed_to:
        scene_art = ensure_scene_art(
            session=session,
            campaign=campaign,
            location_label=result.location_changed_to,
        )
    session.commit()
    session.refresh(turn)
    if scene_art is not None:
        session.refresh(scene_art)

    return TurnResolution(
        turn=turn,
        context_excerpt=result.context_excerpt,
        canon_guard_passed=result.canon_guard_passed,
        canon_guard_message=result.canon_guard_message,
        clocks_fired=result.clocks_fired,
        location_changed_to=result.location_changed_to,
        suggested_actions=result.suggested_actions,
        scene_participants=result.scene_participants,
        revealed_secrets=result.revealed_secrets,
        rolls=[
            {
                "attribute": roll.attribute,
                "target": roll.target,
                "dice_total": roll.dice_total,
                "outcome": roll.outcome,
                "narration": roll.narration,
            }
            for roll in result.rolls
        ],
        scene_art=scene_art,
    )
