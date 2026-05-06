from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.character import Character
from app.services.scene_art import get_cached_scene_art
from app.schemas.campaign import CampaignCreate, CampaignRead, CampaignState

router = APIRouter()


@router.get("", response_model=list[CampaignRead])
def list_campaigns(session: SessionDep) -> list[Campaign]:
    return list(session.scalars(select(Campaign).order_by(Campaign.created_at.desc())))


@router.post("", response_model=CampaignRead, status_code=201)
def create_campaign(payload: CampaignCreate, session: SessionDep) -> Campaign:
    campaign = Campaign(
        name=payload.name,
        tagline=payload.tagline,
        current_date_pce=payload.current_date_pce,
        hidden_state_enabled=True,
        current_location_label="Crescent Block - Callisto Depot District",
    )
    session.add(campaign)
    session.flush()
    session.add(
        Character(
            campaign_id=campaign.id,
            name="Davan of Tharsis",
            race="HighRed",
            character_class="Operative",
            cover_identity="Dav of Vashti",
            current_hp=38,
            max_hp=38,
            cover_integrity=8,
            inventory_summary="Work harness, tools, forged sigil.",
            notes="Default scaffold character pending world-bible seed integration.",
        )
    )
    session.commit()
    session.refresh(campaign)
    return campaign


@router.get("/{campaign_id}/state", response_model=CampaignState)
def get_campaign_state(campaign_id: str, session: SessionDep) -> CampaignState:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    latest_character = (
        session.scalars(
            select(Character)
            .where(Character.campaign_id == campaign_id)
            .order_by(Character.created_at.asc())
        ).first()
    )
    recent_turns = [
        turn.player_safe_summary or turn.gm_response
        for turn in sorted(campaign.turns, key=lambda turn: turn.created_at, reverse=True)[:5]
    ]
    active_objective = next((objective.title for objective in campaign.objectives if objective.is_active), None)
    scene_art = get_cached_scene_art(
        session=session,
        campaign_id=campaign.id,
        location_label=campaign.current_location_label,
    )
    return CampaignState(
        campaign=campaign,
        current_location=campaign.current_location_label,
        active_objective=active_objective,
        recent_turns=recent_turns,
        player_character=latest_character,
        scene_art=scene_art,
        hidden_state_summary="Hidden state remains server-only.",
    )
