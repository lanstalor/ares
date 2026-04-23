from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.memory import Turn
from app.schemas.turn import TurnCreate, TurnRead, TurnResolution
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
        .order_by(Turn.created_at.asc())
        .limit(limit)
    )
    return list(session.scalars(statement))


@router.post("/{campaign_id}/turns", response_model=TurnResolution, status_code=201)
def create_turn(campaign_id: str, payload: TurnCreate, session: SessionDep) -> TurnResolution:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = resolve_turn(campaign=campaign, player_input=payload.player_input)

    turn = Turn(
        campaign_id=campaign.id,
        player_input=payload.player_input,
        gm_response=result.gm_response,
        player_safe_summary=result.player_safe_summary,
    )
    session.add(turn)
    session.commit()
    session.refresh(turn)

    return TurnResolution(
        turn=turn,
        context_excerpt=result.context_excerpt,
        canon_guard_passed=result.canon_guard_passed,
        canon_guard_message=result.canon_guard_message,
    )
