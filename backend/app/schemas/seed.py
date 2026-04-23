from pydantic import BaseModel, Field

from app.core.enums import SecretStatus, Visibility


class SeedNote(BaseModel):
    label: str
    content: str
    visibility: Visibility = Visibility.GM_ONLY


class SeedFaction(BaseModel):
    name: str
    color_hex: str | None = None
    description: str
    visibility: Visibility = Visibility.PLAYER_FACING
    notes: list[SeedNote] = Field(default_factory=list)


class SeedArea(BaseModel):
    name: str
    area_type: str | None = None
    description: str
    appearance: str | None = None
    parent_name: str | None = None
    faction_name: str | None = None
    visibility: Visibility = Visibility.PLAYER_FACING
    notes: list[SeedNote] = Field(default_factory=list)


class SeedPOI(BaseModel):
    name: str
    parent_area_name: str | None = None
    faction_name: str | None = None
    description: str
    gm_instructions: str | None = None
    subtitle: str | None = None
    visibility: Visibility = Visibility.PLAYER_FACING
    notes: list[SeedNote] = Field(default_factory=list)


class SeedNPC(BaseModel):
    name: str
    faction_name: str | None = None
    appearance: str | None = None
    personality: str | None = None
    hidden_agenda: str | None = None
    visibility: Visibility = Visibility.PLAYER_FACING
    aliases: list[str] = Field(default_factory=list)
    notes: list[SeedNote] = Field(default_factory=list)


class SeedLorePage(BaseModel):
    title: str
    content: str
    visibility: Visibility = Visibility.PLAYER_FACING
    notes: list[SeedNote] = Field(default_factory=list)


class SeedPlayerCharacter(BaseModel):
    name: str
    race: str | None = None
    character_class: str | None = None
    faction_name: str | None = None
    level: str | None = None
    cover_identity: dict[str, str] = Field(default_factory=dict)
    appearance: str | None = None
    backstory: str | None = None
    personality: str | None = None
    mannerisms: str | None = None
    proficiencies: list[str] = Field(default_factory=list)
    class_features: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    key_relationships: list[str] = Field(default_factory=list)
    notes: list[SeedNote] = Field(default_factory=list)


class SeedCampaignOpening(BaseModel):
    gm_instructions: str
    opening_message: str


class SeedSecret(BaseModel):
    label: str
    content: str
    status: SecretStatus = SecretStatus.DORMANT
    reveal_condition: str | None = None
    source_reference: str | None = None


class WorldBibleSeed(BaseModel):
    title: str
    version: str | None = None
    world_name: str | None = None
    tagline: str | None = None
    campaign_window: str | None = None
    campaign_start_pce: int = 728
    factions: list[SeedFaction] = Field(default_factory=list)
    areas: list[SeedArea] = Field(default_factory=list)
    pois: list[SeedPOI] = Field(default_factory=list)
    npcs: list[SeedNPC] = Field(default_factory=list)
    lore_pages: list[SeedLorePage] = Field(default_factory=list)
    player_character: SeedPlayerCharacter | None = None
    campaign_opening: SeedCampaignOpening | None = None


class SeedCampaignRow(BaseModel):
    name: str
    tagline: str | None = None
    current_date_pce: int = 728
    hidden_state_enabled: bool = True


class SeedImportBundle(BaseModel):
    campaign: SeedCampaignRow
    factions: list[SeedFaction] = Field(default_factory=list)
    areas: list[SeedArea] = Field(default_factory=list)
    pois: list[SeedPOI] = Field(default_factory=list)
    npcs: list[SeedNPC] = Field(default_factory=list)
    lore_pages: list[SeedLorePage] = Field(default_factory=list)
    secrets: list[SeedSecret] = Field(default_factory=list)
    player_character: SeedPlayerCharacter | None = None
    campaign_opening: SeedCampaignOpening | None = None
