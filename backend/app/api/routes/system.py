from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.system import HealthCheck, SystemStatus

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
def healthcheck() -> HealthCheck:
    return HealthCheck(status="ok")


@router.get("/system/status", response_model=SystemStatus)
def system_status() -> SystemStatus:
    settings = get_settings()
    return SystemStatus(
        app_name="Project Ares API",
        environment=settings.app_env,
        ai_generation_provider=settings.generation_provider,
        embedding_provider=settings.embedding_provider,
        hidden_state_enabled=True,
        multi_agent_enabled=True,
        world_bible_path=str(settings.world_bible_path),
        world_bible_exists=settings.world_bible_path.exists(),
    )
