from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.campaign import Campaign, Objective
from app.models.character import Character
from app.models.memory import Secret
from app.models.world import Area, Faction, LorePage, NPC, POI
from app.schemas.seed_runtime import SeedImportResponse
from app.services.seed_service import build_seed_bundle_from_file


def seed_world_bible_into_campaign(
    session: Session,
    source_path: str | Path | None = None,
    campaign_name_override: str | None = None,
) -> SeedImportResponse:
    settings = get_settings()
    resolved_path = Path(source_path).expanduser().resolve() if source_path else settings.world_bible_path
    bundle = build_seed_bundle_from_file(resolved_path)

    campaign = Campaign(
        name=campaign_name_override or bundle.campaign.name,
        tagline=bundle.campaign.tagline,
        current_date_pce=bundle.campaign.current_date_pce,
        hidden_state_enabled=bundle.campaign.hidden_state_enabled,
        current_location_label="Crescent Block - Callisto Depot District",
    )
    session.add(campaign)
    session.flush()

    faction_ids: dict[str, str] = {}
    for faction_seed in bundle.factions:
        faction = session.scalar(select(Faction).where(Faction.name == faction_seed.name))
        if faction is None:
            faction = Faction(name=faction_seed.name)
            session.add(faction)
            session.flush()
        faction.color_hex = faction_seed.color_hex
        faction.description = faction_seed.description
        faction.visibility = faction_seed.visibility
        faction_ids[faction_seed.name] = faction.id

    area_ids = _insert_areas(session, campaign.id, bundle.areas, faction_ids)
    poi_count = _insert_pois(session, bundle.pois, area_ids, faction_ids)
    npc_count = _insert_npcs(session, bundle.npcs, faction_ids)
    lore_count = _insert_lore_pages(session, bundle.lore_pages)
    secret_count = _insert_secrets(session, campaign.id, bundle.secrets)
    character_count = _insert_player_character(session, campaign.id, bundle.player_character)
    objective_count = _insert_opening_objective(session, campaign.id, bundle.campaign_opening)

    session.commit()

    return SeedImportResponse(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        source_path=str(resolved_path),
        factions_imported=len(faction_ids),
        areas_imported=len(area_ids),
        pois_imported=poi_count,
        npcs_imported=npc_count,
        lore_pages_imported=lore_count,
        secrets_imported=secret_count,
        characters_imported=character_count,
        objectives_imported=objective_count,
    )


def _insert_areas(session: Session, campaign_id: str, areas, faction_ids: dict[str, str]) -> dict[str, str]:
    del campaign_id  # Areas are global in the current ORM shape.
    pending = list(areas)
    inserted: dict[str, str] = {}
    stalled_once = False

    while pending:
        next_round = []
        progress = False
        for area_seed in pending:
            if area_seed.parent_name and area_seed.parent_name not in inserted:
                next_round.append(area_seed)
                continue

            area = session.scalar(select(Area).where(Area.name == area_seed.name))
            if area is None:
                area = Area(name=area_seed.name)
                session.add(area)
                session.flush()
            area.area_type = area_seed.area_type
            area.description = area_seed.description
            area.appearance = area_seed.appearance
            area.parent_area_id = inserted.get(area_seed.parent_name)
            area.faction_id = faction_ids.get(area_seed.faction_name)
            area.visibility = area_seed.visibility
            inserted[area_seed.name] = area.id
            progress = True

        if not progress:
            if stalled_once:
                break
            stalled_once = True
        pending = next_round

    return inserted


def _insert_pois(session: Session, pois, area_ids: dict[str, str], faction_ids: dict[str, str]) -> int:
    count = 0
    for poi_seed in pois:
        poi = session.scalar(select(POI).where(POI.name == poi_seed.name))
        if poi is None:
            poi = POI(name=poi_seed.name)
            session.add(poi)
        poi.parent_area_id = area_ids.get(poi_seed.parent_area_name)
        poi.faction_id = faction_ids.get(poi_seed.faction_name)
        poi.description = poi_seed.description
        poi.gm_instructions = poi_seed.gm_instructions
        poi.visibility = poi_seed.visibility
        count += 1
    return count


def _insert_npcs(session: Session, npcs, faction_ids: dict[str, str]) -> int:
    count = 0
    for npc_seed in npcs:
        npc = session.scalar(select(NPC).where(NPC.name == npc_seed.name))
        if npc is None:
            npc = NPC(name=npc_seed.name)
            session.add(npc)
        npc.faction_id = faction_ids.get(npc_seed.faction_name)
        npc.appearance = npc_seed.appearance
        npc.personality = npc_seed.personality
        npc.hidden_agenda = npc_seed.hidden_agenda
        npc.visibility = npc_seed.visibility
        count += 1
    return count


def _insert_lore_pages(session: Session, lore_pages) -> int:
    count = 0
    for lore_seed in lore_pages:
        page = session.scalar(select(LorePage).where(LorePage.title == lore_seed.title))
        if page is None:
            page = LorePage(title=lore_seed.title, content=lore_seed.content)
            session.add(page)
        page.content = lore_seed.content
        page.visibility = lore_seed.visibility
        count += 1
    return count


def _insert_secrets(session: Session, campaign_id: str, secrets) -> int:
    count = 0
    for secret_seed in secrets:
        secret = Secret(
            campaign_id=campaign_id,
            label=secret_seed.label,
            content=secret_seed.content,
            status=secret_seed.status,
            reveal_condition=secret_seed.reveal_condition,
        )
        session.add(secret)
        count += 1
    return count


def _insert_player_character(session: Session, campaign_id: str, player_character) -> int:
    if player_character is None:
        return 0

    character = Character(
        campaign_id=campaign_id,
        name=player_character.name,
        race=player_character.race,
        character_class=player_character.character_class,
        cover_identity=player_character.cover_identity.get("Registered name"),
        current_hp=38,
        max_hp=38,
        cover_integrity=8,
        inventory_summary=", ".join(player_character.equipment) if player_character.equipment else None,
        notes=player_character.backstory,
    )
    session.add(character)
    return 1


def _insert_opening_objective(session: Session, campaign_id: str, campaign_opening) -> int:
    if campaign_opening is None:
        return 0

    objective = Objective(
        campaign_id=campaign_id,
        title="Check the Melt before shift",
        description=campaign_opening.opening_message,
        gm_instructions=campaign_opening.gm_instructions,
        is_active=True,
        is_complete=False,
    )
    session.add(objective)
    return 1
