from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str


class SystemStatus(BaseModel):
    app_name: str
    environment: str
    ai_generation_provider: str
    embedding_provider: str
    hidden_state_enabled: bool
    multi_agent_enabled: bool
    world_bible_path: str
    world_bible_exists: bool
