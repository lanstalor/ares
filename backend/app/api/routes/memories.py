from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.memory import Memory
from app.schemas.memory import MemoryRead

router = APIRouter()


@router.get("/{campaign_id}/memories", response_model=list[MemoryRead])
def list_memories(
    campaign_id: str,
    session: SessionDep,
    limit: int = Query(default=10, ge=1, le=50),
) -> list[Memory]:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    statement = (
        select(Memory)
        .where(Memory.campaign_id == campaign_id, Memory.visibility == "player_facing")
        .order_by(Memory.created_at.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))
