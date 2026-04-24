from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str


class SystemStatus(BaseModel):
    app_name: str
    environment: str
    ai_generation_provider: str
    ai_model: str | None
    embedding_provider: str
    database_bootstrap: str
    database_initialized: bool
    hidden_state_enabled: bool
    multi_agent_enabled: bool
    env_file_path: str
    world_bible_path: str
    world_bible_exists: bool
    campaign_count: int
    seeded_campaign_count: int
    campaign_seeded: bool
