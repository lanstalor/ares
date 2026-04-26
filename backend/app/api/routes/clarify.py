from fastapi import APIRouter, HTTPException

from app.db.session import SessionDep
from app.models.campaign import Campaign
from app.schemas.clarify import ClarifyRequest, ClarifyResponse
from app.services.clarify_engine import resolve_clarification

router = APIRouter()


@router.post("/{campaign_id}/clarify", response_model=ClarifyResponse)
def clarify_story(campaign_id: str, payload: ClarifyRequest, session: SessionDep) -> ClarifyResponse:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    explanation = resolve_clarification(
        session=session,
        campaign=campaign,
        query=payload.query,
    )

    return ClarifyResponse(explanation=explanation)
