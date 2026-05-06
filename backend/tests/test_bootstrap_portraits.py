import base64
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.portraits import NpcPortrait
from app.services.media_provider import MediaRequest, MediaResponse
from app.services.seed_runtime import _queue_npc_portraits


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_queue_npc_portraits_creates_portraits_for_all_characters(tmp_path: Path) -> None:
    """Test that _queue_npc_portraits generates portraits for all campaign characters."""
    import unittest.mock as mock

    session = _make_session()

    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.flush()

    character1 = Character(campaign_id=campaign.id, name="Davan of Tharsis", race="HighRed")
    character2 = Character(campaign_id=campaign.id, name="Alia of House Visigoth", race="Obsidian")
    session.add(character1)
    session.add(character2)
    session.commit()

    # Mock the media provider
    call_count = [0]

    def mock_generate_image(request: MediaRequest) -> MediaResponse:
        call_count[0] += 1
        return MediaResponse(
            provider="fake",
            model="fake-image",
            media_type="image/png",
            b64_json=base64.b64encode(b"png-bytes").decode("ascii"),
            revised_prompt="revised",
            cache_key=request.cache_key,
        )

    with mock.patch(
        "app.services.npc_portrait_service.get_media_provider"
    ) as mock_provider_factory:
        mock_provider = mock.MagicMock()
        mock_provider.generate_image = mock_generate_image
        mock_provider_factory.return_value = mock_provider

        with mock.patch(
            "app.services.npc_portrait_service.get_settings"
        ) as mock_settings:
            mock_settings.return_value.project_root = tmp_path
            _queue_npc_portraits(session, campaign)

    # Verify portraits were created
    portraits = session.scalars(
        select(NpcPortrait).where(NpcPortrait.campaign_id == campaign.id)
    ).all()

    assert len(portraits) == 2
    assert call_count[0] == 2
    portrait_npc_ids = {p.npc_id for p in portraits}
    assert portrait_npc_ids == {character1.id, character2.id}


def test_queue_npc_portraits_handles_errors_gracefully(tmp_path: Path) -> None:
    """Test that _queue_npc_portraits doesn't fail if portrait generation fails."""
    import unittest.mock as mock

    session = _make_session()

    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.flush()

    character1 = Character(campaign_id=campaign.id, name="Davan of Tharsis")
    character2 = Character(campaign_id=campaign.id, name="Alia of House Visigoth")
    session.add(character1)
    session.add(character2)
    session.commit()

    # Mock the media provider to fail
    def mock_generate_image_fails(request: MediaRequest) -> MediaResponse:
        raise RuntimeError("Provider error")

    with mock.patch(
        "app.services.npc_portrait_service.get_media_provider"
    ) as mock_provider_factory:
        mock_provider = mock.MagicMock()
        mock_provider.generate_image = mock_generate_image_fails
        mock_provider_factory.return_value = mock_provider

        with mock.patch(
            "app.services.npc_portrait_service.get_settings"
        ) as mock_settings:
            mock_settings.return_value.project_root = tmp_path

            # Should not raise
            _queue_npc_portraits(session, campaign)

    # Verify portraits were created with error status
    portraits = session.scalars(
        select(NpcPortrait).where(NpcPortrait.campaign_id == campaign.id)
    ).all()

    assert len(portraits) == 2
    for portrait in portraits:
        assert portrait.status == "failed"
        assert portrait.error is not None
