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
