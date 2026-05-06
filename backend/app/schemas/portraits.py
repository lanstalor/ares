from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PortraitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    npc_id: str
    slug: str
    prompt: str
    image_url: str
    provider: str
    model: str | None
    status: str
    revised_prompt: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime


class PortraitRegenerateRequest(BaseModel):
    force: bool = True
