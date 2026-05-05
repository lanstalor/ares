from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    character_id: str | None
    name: str
    description: str | None
    item_type: str | None
    rarity: str | None
    tags: str | None
    is_equippable: bool
    is_equipped: bool
    quantity: int
    created_at: datetime
    updated_at: datetime


class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    name: str
    race: str | None
    character_class: str | None
    cover_identity: str | None
    current_hp: int | None
    max_hp: int | None
    cover_integrity: int | None
    inventory_summary: str | None
    notes: str | None
    items: list[ItemRead] = []
    created_at: datetime
    updated_at: datetime
