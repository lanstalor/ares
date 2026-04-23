from fastapi import APIRouter

from app.db.session import SessionDep
from app.schemas.seed_runtime import SeedImportRequest, SeedImportResponse
from app.services.seed_runtime import seed_world_bible_into_campaign

router = APIRouter()


@router.post("/world-bible", response_model=SeedImportResponse, status_code=201)
def seed_world_bible(payload: SeedImportRequest, session: SessionDep) -> SeedImportResponse:
    return seed_world_bible_into_campaign(
        session=session,
        source_path=payload.source_path,
        campaign_name_override=payload.campaign_name_override,
    )
