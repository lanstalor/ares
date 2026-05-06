from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.media import SceneArt
from app.schemas.media import SceneArtRead, SceneArtRegenerateRequest
from app.services.scene_art import ensure_scene_art

router = APIRouter()
file_router = APIRouter()


@file_router.get("/scene-art/{filename}")
def get_generated_scene_art_file(filename: str) -> FileResponse:
    if "/" in filename or "\\" in filename or not filename.endswith(".png"):
        raise HTTPException(status_code=404, detail="Scene art not found")

    target_path = get_settings().scene_art_cache_dir / filename
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Scene art not found")

    return FileResponse(target_path, media_type="image/png")


@router.get("/{campaign_id}/scene-art", response_model=list[SceneArtRead])
def list_scene_art(campaign_id: str, session: SessionDep) -> list[SceneArt]:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return list(
        session.scalars(
            select(SceneArt)
            .where(SceneArt.campaign_id == campaign_id)
            .order_by(SceneArt.updated_at.desc())
        )
    )


@router.get("/{campaign_id}/scene-art/current", response_model=SceneArtRead)
def get_current_scene_art(campaign_id: str, session: SessionDep) -> SceneArt:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    scene_art = ensure_scene_art(session=session, campaign=campaign)
    session.commit()
    session.refresh(scene_art)
    return scene_art


@router.post("/{campaign_id}/scene-art/regenerate", response_model=SceneArtRead)
def regenerate_scene_art(
    campaign_id: str,
    payload: SceneArtRegenerateRequest,
    session: SessionDep,
) -> SceneArt:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    scene_art = ensure_scene_art(
        session=session,
        campaign=campaign,
        location_label=payload.location_label,
        force=payload.force,
    )
    session.commit()
    session.refresh(scene_art)
    return scene_art
