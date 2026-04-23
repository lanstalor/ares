from pydantic import BaseModel, Field


class SeedImportRequest(BaseModel):
    source_path: str | None = None
    campaign_name_override: str | None = Field(default=None, max_length=200)


class SeedImportResponse(BaseModel):
    campaign_id: str
    campaign_name: str
    source_path: str
    factions_imported: int
    areas_imported: int
    pois_imported: int
    npcs_imported: int
    lore_pages_imported: int
    secrets_imported: int
    characters_imported: int
    objectives_imported: int
