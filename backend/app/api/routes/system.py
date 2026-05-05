from fastapi import APIRouter
from sqlalchemy import distinct, func, select

from app.core.config import get_settings
from app.db.bootstrap import database_has_required_tables
from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.models.memory import Secret
from app.schemas.system import HealthCheck, SystemStatus

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
def healthcheck() -> HealthCheck:
    return HealthCheck(status="ok")


@router.get("/system/status", response_model=SystemStatus)
def system_status(session: SessionDep) -> SystemStatus:
    settings = get_settings()
    database_initialized = database_has_required_tables()
    campaign_count = 0
    seeded_campaign_count = 0

    if database_initialized:
        campaign_count = session.scalar(select(func.count()).select_from(Campaign)) or 0
        seeded_campaign_count = (
            session.scalar(select(func.count(distinct(Secret.campaign_id))).select_from(Secret)) or 0
        )

    return SystemStatus(
        app_name="Project Ares API",
        environment=settings.app_env,
        ai_generation_provider=settings.generation_provider,
        ai_model=settings.generation_model,
        media_provider=settings.media_provider,
        media_model=settings.media_model,
        embedding_provider=settings.embedding_provider,
        database_bootstrap=settings.database_bootstrap,
        database_initialized=database_initialized,
        hidden_state_enabled=True,
        multi_agent_enabled=True,
        env_file_path=str(settings.env_file_path),
        world_bible_path=str(settings.world_bible_path),
        world_bible_exists=settings.world_bible_path.exists(),
        campaign_count=int(campaign_count),
        seeded_campaign_count=int(seeded_campaign_count),
        campaign_seeded=bool(seeded_campaign_count),
    )
