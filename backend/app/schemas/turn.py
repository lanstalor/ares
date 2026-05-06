from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.media import SceneArtRead


class TurnCreate(BaseModel):
    player_input: str = Field(min_length=1, max_length=8000)


class TurnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    player_input: str
    gm_response: str
    player_safe_summary: str | None
    created_at: datetime
    updated_at: datetime


class TurnResolution(BaseModel):
    turn: TurnRead
    context_excerpt: str
    canon_guard_passed: bool
    canon_guard_message: str | None
    clocks_fired: list[str] = Field(default_factory=list)
    location_changed_to: str | None = None
    suggested_actions: list[dict] = Field(default_factory=list)
    scene_participants: list[dict] = Field(default_factory=list)
    revealed_secrets: list[dict] = Field(default_factory=list)
    rolls: list[dict] = Field(default_factory=list)
    scene_art: SceneArtRead | None = None
