from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.world import Area, Faction, LorePage, NPC, POI
from app.schemas.operator import CampaignFullState, WorldState

router = APIRouter()


@router.get("/health")
def operator_health():
    return {"status": "ok", "surface": "operator"}


@router.get("/campaigns/{campaign_id}/full-state", response_model=CampaignFullState)
def get_campaign_full_state(campaign_id: str, session: SessionDep) -> CampaignFullState:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # World state is global for now
    world = WorldState(
        factions=list(session.scalars(select(Faction))),
        areas=list(session.scalars(select(Area))),
        pois=list(session.scalars(select(POI))),
        npcs=list(session.scalars(select(NPC))),
        lore_pages=list(session.scalars(select(LorePage))),
    )

    return CampaignFullState(
        campaign=campaign,
        objectives=campaign.objectives,
        clocks=campaign.clocks,
        secrets=campaign.secrets,
        characters=campaign.characters,
        turns=campaign.turns,
        memories=campaign.memories,
        world=world,
    )
