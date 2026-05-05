from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.session import SessionDep
from app.models.campaign import Campaign, Clock, Objective
from app.models.character import Character
from app.models.memory import Secret, Turn
from app.models.world import Area, Faction, LorePage, NPC, POI
from app.schemas.operator import CampaignFullState, CampaignStatePatch, WorldState

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


@router.patch("/campaigns/{campaign_id}/state", response_model=CampaignFullState)
def patch_campaign_state(
    campaign_id: str, payload: CampaignStatePatch, session: SessionDep
) -> CampaignFullState:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if payload.campaign:
        for field, value in payload.campaign.model_dump(exclude_unset=True).items():
            setattr(campaign, field, value)

    if payload.objectives:
        for update in payload.objectives:
            obj = session.get(Objective, update.id)
            if obj and obj.campaign_id == campaign_id:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(obj, field, value)

    if payload.clocks:
        for update in payload.clocks:
            clock = session.get(Clock, update.id)
            if clock and clock.campaign_id == campaign_id:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(clock, field, value)

    if payload.secrets:
        for update in payload.secrets:
            secret = session.get(Secret, update.id)
            if secret and secret.campaign_id == campaign_id:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(secret, field, value)

    if payload.turns:
        for update in payload.turns:
            turn = session.get(Turn, update.id)
            if turn and turn.campaign_id == campaign_id:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(turn, field, value)

    if payload.characters:
        for update in payload.characters:
            char = session.get(Character, update.id)
            if char and char.campaign_id == campaign_id:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(char, field, value)

    if payload.npcs:
        for update in payload.npcs:
            npc = session.get(NPC, update.id)
            if npc:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(npc, field, value)

    session.commit()
    session.refresh(campaign)

    # Return full state as confirmation
    return get_campaign_full_state(campaign_id, session)
