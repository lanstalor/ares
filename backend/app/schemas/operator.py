from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.core.enums import ClockType, SecretStatus, Visibility
from app.schemas.campaign import CampaignRead
from app.schemas.character import CharacterRead
from app.schemas.memory import MemoryRead
from app.schemas.turn import TurnRead


class ObjectiveRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    campaign_id: str
    title: str
    description: str | None
    gm_instructions: str | None
    is_active: bool
    is_complete: bool
    created_at: datetime


class ClockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    campaign_id: str
    label: str
    clock_type: ClockType
    current_value: int
    max_value: int
    hidden_from_player: bool
    created_at: datetime


class SecretRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    campaign_id: str
    label: str
    content: str
    status: SecretStatus
    reveal_condition: str | None
    created_at: datetime


class FactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    color_hex: str | None
    description: str | None
    visibility: Visibility


class AreaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    area_type: str | None
    description: str | None
    appearance: str | None
    parent_area_id: str | None
    faction_id: str | None
    visibility: Visibility


class POIRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    parent_area_id: str | None
    faction_id: str | None
    description: str | None
    gm_instructions: str | None
    visibility: Visibility


class NPCRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    faction_id: str | None
    appearance: str | None
    personality: str | None
    hidden_agenda: str | None
    visibility: Visibility
    level: int | None
    current_hp: int | None
    max_hp: int | None


class LorePageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    content: str
    visibility: Visibility


class WorldState(BaseModel):
    factions: list[FactionRead]
    areas: list[AreaRead]
    pois: list[POIRead]
    npcs: list[NPCRead]
    lore_pages: list[LorePageRead]


class CampaignFullState(BaseModel):
    campaign: CampaignRead
    objectives: list[ObjectiveRead]
    clocks: list[ClockRead]
    secrets: list[SecretRead]
    characters: list[CharacterRead]
    turns: list[TurnRead]
    memories: list[MemoryRead]
    world: WorldState


# Patch Schemas

class CampaignUpdate(BaseModel):
    name: str | None = None
    tagline: str | None = None
    current_date_pce: int | None = None
    current_location_label: str | None = None


class ObjectiveUpdate(BaseModel):
    id: str
    title: str | None = None
    description: str | None = None
    gm_instructions: str | None = None
    is_active: bool | None = None
    is_complete: bool | None = None


class ClockUpdate(BaseModel):
    id: str
    label: str | None = None
    clock_type: ClockType | None = None
    current_value: int | None = None
    max_value: int | None = None
    hidden_from_player: bool | None = None


class SecretUpdate(BaseModel):
    id: str
    label: str | None = None
    content: str | None = None
    status: SecretStatus | None = None
    reveal_condition: str | None = None


class TurnUpdate(BaseModel):
    id: str
    player_input: str | None = None
    gm_response: str | None = None
    player_safe_summary: str | None = None


class CharacterUpdate(BaseModel):
    id: str
    name: str | None = None
    race: str | None = None
    character_class: str | None = None
    cover_identity: str | None = None
    current_hp: int | None = None
    max_hp: int | None = None
    cover_integrity: int | None = None
    inventory_summary: str | None = None
    notes: str | None = None


class NPCUpdate(BaseModel):
    id: str
    appearance: str | None = None
    personality: str | None = None
    hidden_agenda: str | None = None
    visibility: Visibility | None = None
    level: int | None = None
    current_hp: int | None = None
    max_hp: int | None = None


class FactionUpdate(BaseModel):
    id: str
    name: str | None = None
    color_hex: str | None = None
    description: str | None = None
    visibility: Visibility | None = None


class AreaUpdate(BaseModel):
    id: str
    name: str | None = None
    area_type: str | None = None
    description: str | None = None
    appearance: str | None = None
    parent_area_id: str | None = None
    faction_id: str | None = None
    visibility: Visibility | None = None


class POIUpdate(BaseModel):
    id: str
    name: str | None = None
    parent_area_id: str | None = None
    faction_id: str | None = None
    description: str | None = None
    gm_instructions: str | None = None
    visibility: Visibility | None = None


class LorePageUpdate(BaseModel):
    id: str
    title: str | None = None
    content: str | None = None
    visibility: Visibility | None = None


class CampaignStatePatch(BaseModel):
    campaign: CampaignUpdate | None = None
    objectives: list[ObjectiveUpdate] | None = None
    clocks: list[ClockUpdate] | None = None
    secrets: list[SecretUpdate] | None = None
    turns: list[TurnUpdate] | None = None
    characters: list[CharacterUpdate] | None = None
    npcs: list[NPCUpdate] | None = None
    factions: list[FactionUpdate] | None = None
    areas: list[AreaUpdate] | None = None
    pois: list[POIUpdate] | None = None
    lore_pages: list[LorePageUpdate] | None = None


class AuditFinding(BaseModel):
    severity: str  # "info", "warning", "critical"
    entity_type: str  # "clock", "secret", "objective", etc.
    entity_id: str
    message: str
    context: dict | None = None


class CampaignAuditReport(BaseModel):
    campaign_id: str
    findings: list[AuditFinding]
    summary: str
