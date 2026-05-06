from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.character import CharacterRead
from app.schemas.media import SceneArtRead


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    tagline: str | None = Field(default=None, max_length=255)
    current_date_pce: int = 728


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    tagline: str | None
    current_date_pce: int
    hidden_state_enabled: bool
    current_location_label: str | None
    created_at: datetime
    updated_at: datetime


class CampaignState(BaseModel):
    campaign: CampaignRead
    current_location: str | None
    active_objective: str | None
    recent_turns: list[str]
    player_character: CharacterRead | None
    scene_art: SceneArtRead | None = None
    hidden_state_summary: str
