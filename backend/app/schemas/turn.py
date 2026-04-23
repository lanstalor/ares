from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
