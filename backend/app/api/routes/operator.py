from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.enums import SecretStatus
from app.db.session import SessionDep
from app.models.campaign import Campaign, Clock, Objective
from app.models.character import Character, Item
from app.models.memory import Secret, Turn
from app.models.world import Area, Faction, LorePage, NPC, POI
from app.schemas.operator import (
    AuditFinding,
    CampaignAuditReport,
    CampaignFullState,
    CampaignStatePatch,
    WorldState,
)

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
        items=campaign.items,
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

    if payload.items:
        for update in payload.items:
            item = session.get(Item, update.id)
            if item and item.campaign_id == campaign_id:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(item, field, value)

    if payload.npcs:
        for update in payload.npcs:
            npc = session.get(NPC, update.id)
            if npc:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(npc, field, value)

    if payload.factions:
        for update in payload.factions:
            faction = session.get(Faction, update.id)
            if faction:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(faction, field, value)

    if payload.areas:
        for update in payload.areas:
            area = session.get(Area, update.id)
            if area:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(area, field, value)

    if payload.pois:
        for update in payload.pois:
            poi = session.get(POI, update.id)
            if poi:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(poi, field, value)

    if payload.lore_pages:
        for update in payload.lore_pages:
            lp = session.get(LorePage, update.id)
            if lp:
                for field, value in update.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(lp, field, value)

    session.commit()
    session.refresh(campaign)

    # Return full state as confirmation
    return get_campaign_full_state(campaign_id, session)


@router.get("/campaigns/{campaign_id}/audit", response_model=CampaignAuditReport)
def audit_campaign_state(campaign_id: str, session: SessionDep) -> CampaignAuditReport:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    findings = []

    # 1. Clock checks
    for clock in campaign.clocks:
        if clock.current_value >= clock.max_value:
            findings.append(
                AuditFinding(
                    severity="critical",
                    entity_type="clock",
                    entity_id=clock.id,
                    message=f"Clock '{clock.label}' has reached its max value ({clock.max_value}).",
                )
            )
        elif clock.current_value >= clock.max_value - 1:
            findings.append(
                AuditFinding(
                    severity="warning",
                    entity_type="clock",
                    entity_id=clock.id,
                    message=f"Clock '{clock.label}' is near its max value ({clock.current_value}/{clock.max_value}).",
                )
            )

    # 2. Secret checks
    for secret in campaign.secrets:
        if secret.status == SecretStatus.DORMANT:
            # Basic reminder, could be more complex (e.g. check against context)
            findings.append(
                AuditFinding(
                    severity="info",
                    entity_type="secret",
                    entity_id=secret.id,
                    message=f"Secret '{secret.label}' is dormant.",
                )
            )

    # 3. Objective checks
    active_objectives = [o for o in campaign.objectives if o.is_active]
    if not active_objectives:
        findings.append(
            AuditFinding(
                severity="warning",
                entity_type="campaign",
                entity_id=campaign_id,
                message="No active objectives found for this campaign.",
            )
        )
    for obj in active_objectives:
        if not obj.description:
            findings.append(
                AuditFinding(
                    severity="warning",
                    entity_type="objective",
                    entity_id=obj.id,
                    message=f"Active objective '{obj.title}' has no description.",
                )
            )

    # 4. NPC HP checks
    # Note: NPCs are global currently, but we can check all or filter if we had a participation mapping
    all_npcs = session.scalars(select(NPC)).all()
    for npc in all_npcs:
        if npc.current_hp is not None and npc.max_hp is not None:
            if npc.current_hp <= 0:
                findings.append(
                    AuditFinding(
                        severity="critical",
                        entity_type="npc",
                        entity_id=npc.id,
                        message=f"NPC '{npc.name}' is at 0 HP.",
                    )
                )
            elif npc.current_hp <= npc.max_hp * 0.25:
                findings.append(
                    AuditFinding(
                        severity="warning",
                        entity_type="npc",
                        entity_id=npc.id,
                        message=f"NPC '{npc.name}' is at low HP ({npc.current_hp}/{npc.max_hp}).",
                    )
                )

    summary = f"Audit complete. Found {len(findings)} issues."
    return CampaignAuditReport(campaign_id=campaign_id, findings=findings, summary=summary)
