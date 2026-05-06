from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.portraits import NpcPortrait
from app.schemas.portraits import PortraitRead, PortraitRegenerateRequest
from app.services.npc_portrait_service import ensure_portrait

router = APIRouter()
file_router = APIRouter()


@file_router.get("/portraits/{filename}")
def get_npc_portrait_file(filename: str) -> FileResponse:
    """Serve generated NPC portrait PNG files."""
    if "/" in filename or "\\" in filename or not filename.endswith(".png"):
        raise HTTPException(status_code=404, detail="Portrait not found")

    target_path = get_settings().project_root / "frontend" / "public" / "portraits" / filename
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Portrait not found")

    return FileResponse(target_path, media_type="image/png")


@router.get("/{campaign_id}/portraits", response_model=list[PortraitRead])
def list_portraits(campaign_id: str, session: SessionDep) -> list[NpcPortrait]:
    """List all NPC portraits in a campaign."""
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return list(
        session.scalars(
            select(NpcPortrait)
            .where(NpcPortrait.campaign_id == campaign_id)
            .order_by(NpcPortrait.updated_at.desc())
        )
    )


@router.get("/{campaign_id}/portraits/{npc_id}", response_model=PortraitRead)
def get_portrait_detail(campaign_id: str, npc_id: str, session: SessionDep) -> NpcPortrait:
    """Get a specific NPC portrait by NPC ID."""
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    npc = session.get(Character, npc_id)
    if npc is None or npc.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="NPC not found in campaign")

    portrait = session.scalar(
        select(NpcPortrait).where(
            NpcPortrait.campaign_id == campaign_id,
            NpcPortrait.npc_id == npc_id,
        )
    )
    if portrait is None:
        raise HTTPException(status_code=404, detail="Portrait not found")

    return portrait


@router.post("/{campaign_id}/portraits/{npc_id}/regenerate", response_model=PortraitRead)
def regenerate_portrait(
    campaign_id: str,
    npc_id: str,
    payload: PortraitRegenerateRequest,
    session: SessionDep,
) -> NpcPortrait:
    """Regenerate (or generate) an NPC portrait."""
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    npc = session.get(Character, npc_id)
    if npc is None or npc.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="NPC not found in campaign")

    portrait = ensure_portrait(
        session=session,
        campaign=campaign,
        character=npc,
        force=payload.force,
    )
    session.commit()
    session.refresh(portrait)
    return portrait
