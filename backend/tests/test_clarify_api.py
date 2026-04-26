import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.campaigns import create_campaign
from app.api.routes.clarify import clarify_story
from app.core.config import get_settings
from app.models.base import Base
from app.schemas.campaign import CampaignCreate
from app.schemas.clarify import ClarifyRequest


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_clarify_api_contract(monkeypatch) -> None:
    monkeypatch.setenv("ARES_GENERATION_PROVIDER", "stub")
    get_settings.cache_clear()
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Test Cell"), session)

    # Test the clarification endpoint
    # Note: Using the default NullNarrationProvider which returns a static message
    response = clarify_story(campaign.id, ClarifyRequest(query="What is happening?"), session)

    assert response.explanation is not None
    assert "GM clarification engine" in response.explanation


def test_clarify_nonexistent_campaign(monkeypatch) -> None:
    monkeypatch.setenv("ARES_GENERATION_PROVIDER", "stub")
    get_settings.cache_clear()
    session = _make_session()
    with pytest.raises(HTTPException) as excinfo:
        clarify_story("nonexistent-id", ClarifyRequest(query="Hello?"), session)
    assert excinfo.value.status_code == 404
