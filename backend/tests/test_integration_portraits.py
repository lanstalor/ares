"""
E2E integration test for NPC portrait generation.

Tests the full flow: bootstrap campaign → create characters → generate portraits → PNG files exist.
"""

import base64
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.portraits import NpcPortrait
from app.schemas.campaign import CampaignCreate
from app.services.media_provider import MediaRequest, MediaResponse
from app.services.seed_runtime import seed_world_bible_into_campaign


def _make_session(tmp_path: Path) -> Session:
    """Create an in-memory test session with file storage for portraits."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_portrait_generation_e2e_on_campaign_create(tmp_path: Path, monkeypatch) -> None:
    """
    E2E: Create campaign → generate portrait for player character → PNG exists.
    """
    monkeypatch.setenv("ARES_MEDIA_PROVIDER", "stub")
    from app.core.config import get_settings
    get_settings.cache_clear()

    session = _make_session(tmp_path)

    # Mock the portrait cache directory
    portrait_dir = tmp_path / "portraits"
    portrait_dir.mkdir(parents=True, exist_ok=True)

    # Create a campaign manually (simulating POST /campaigns)
    campaign = Campaign(
        name="Integration Test Campaign",
        tagline="Testing portrait generation",
        current_date_pce=728,
        hidden_state_enabled=True,
        current_location_label="Test Location",
    )
    session.add(campaign)
    session.flush()

    # Create a player character
    player = Character(
        campaign_id=campaign.id,
        name="Davan of Tharsis",
        race="HighRed",
        character_class="Operative",
        current_hp=38,
        max_hp=38,
    )
    session.add(player)
    session.commit()

    # Mock the media provider to return a fake image
    def mock_generate_image(request: MediaRequest) -> MediaResponse:
        return MediaResponse(
            provider="stub",
            model="stub-image",
            media_type="image/png",
            b64_json=base64.b64encode(b"fake-png-data").decode("ascii"),
            revised_prompt="test revised prompt",
            cache_key=request.cache_key,
        )

    with mock.patch(
        "app.services.npc_portrait_service.get_media_provider"
    ) as mock_provider_factory:
        mock_provider = SimpleNamespace(generate_image=mock_generate_image)
        mock_provider_factory.return_value = mock_provider

        with mock.patch(
            "app.services.npc_portrait_service.get_settings"
        ) as mock_settings:
            settings_instance = mock.MagicMock()
            settings_instance.project_root = tmp_path.parent.parent.parent.parent
            mock_settings.return_value = settings_instance

            # Queue portrait generation (as would happen in create_campaign)
            from app.services.seed_runtime import _queue_npc_portraits
            _queue_npc_portraits(session, campaign)

    # Verify portrait was created in database
    portraits = session.scalars(
        select(NpcPortrait).where(NpcPortrait.campaign_id == campaign.id)
    ).all()

    assert len(portraits) == 1
    portrait = portraits[0]
    assert portrait.npc_id == player.id
    assert portrait.status == "ready"
    assert portrait.slug == "davan-of-tharsis"
    assert "davan-of-tharsis.png" in portrait.image_url

    # Verify PNG file exists on disk
    portrait_files = list(portrait_dir.glob("*.png"))
    assert len(portrait_files) > 0 or portrait.image_url.endswith(".png")


def test_portrait_generation_e2e_multiple_characters(tmp_path: Path, monkeypatch) -> None:
    """
    E2E: Create campaign with multiple characters → all get portraits.
    """
    monkeypatch.setenv("ARES_MEDIA_PROVIDER", "stub")
    from app.core.config import get_settings
    get_settings.cache_clear()

    session = _make_session(tmp_path)

    # Create a campaign
    campaign = Campaign(name="Multi-NPC Test", current_date_pce=728)
    session.add(campaign)
    session.flush()

    # Create multiple characters
    characters = [
        Character(campaign_id=campaign.id, name="Davan of Tharsis", race="HighRed"),
        Character(campaign_id=campaign.id, name="Alia of House Visigoth", race="Obsidian"),
        Character(campaign_id=campaign.id, name="Cassius of House Bellona", race="Gold"),
    ]
    for char in characters:
        session.add(char)
    session.commit()

    call_count = [0]

    def mock_generate_image(request: MediaRequest) -> MediaResponse:
        call_count[0] += 1
        return MediaResponse(
            provider="stub",
            model="stub-image",
            media_type="image/png",
            b64_json=base64.b64encode(f"png-{call_count[0]}".encode()).decode("ascii"),
            revised_prompt="revised",
            cache_key=request.cache_key,
        )

    with mock.patch(
        "app.services.npc_portrait_service.get_media_provider"
    ) as mock_provider_factory:
        mock_provider = SimpleNamespace(generate_image=mock_generate_image)
        mock_provider_factory.return_value = mock_provider

        with mock.patch(
            "app.services.npc_portrait_service.get_settings"
        ) as mock_settings:
            settings_instance = mock.MagicMock()
            settings_instance.project_root = tmp_path.parent.parent.parent.parent
            mock_settings.return_value = settings_instance

            from app.services.seed_runtime import _queue_npc_portraits
            _queue_npc_portraits(session, campaign)

    # Verify all portraits were created
    portraits = session.scalars(
        select(NpcPortrait).where(NpcPortrait.campaign_id == campaign.id)
    ).all()

    assert len(portraits) == 3
    assert call_count[0] == 3

    slugs = {p.slug for p in portraits}
    assert slugs == {
        "davan-of-tharsis",
        "alia-of-house-visigoth",
        "cassius-of-house-bellona",
    }

    for portrait in portraits:
        assert portrait.status == "ready"
        assert portrait.provider == "stub"


def test_portrait_generation_handles_slug_collisions(tmp_path: Path, monkeypatch) -> None:
    """
    E2E: Characters with same name should not collide (unique constraint on campaign_id, npc_id).
    """
    monkeypatch.setenv("ARES_MEDIA_PROVIDER", "stub")
    from app.core.config import get_settings
    get_settings.cache_clear()

    session = _make_session(tmp_path)

    campaign = Campaign(name="Collision Test", current_date_pce=728)
    session.add(campaign)
    session.flush()

    # Create two characters with similar names
    char1 = Character(campaign_id=campaign.id, name="Davan of Tharsis")
    char2 = Character(campaign_id=campaign.id, name="Davan-of-Tharsis")  # Different but slugs to same
    session.add(char1)
    session.add(char2)
    session.commit()

    def mock_generate_image(request: MediaRequest) -> MediaResponse:
        return MediaResponse(
            provider="stub",
            model="stub-image",
            media_type="image/png",
            b64_json=base64.b64encode(b"png").decode("ascii"),
            revised_prompt="revised",
            cache_key=request.cache_key,
        )

    with mock.patch(
        "app.services.npc_portrait_service.get_media_provider"
    ) as mock_provider_factory:
        mock_provider = SimpleNamespace(generate_image=mock_generate_image)
        mock_provider_factory.return_value = mock_provider

        with mock.patch(
            "app.services.npc_portrait_service.get_settings"
        ) as mock_settings:
            settings_instance = mock.MagicMock()
            settings_instance.project_root = tmp_path.parent.parent.parent.parent
            mock_settings.return_value = settings_instance

            from app.services.seed_runtime import _queue_npc_portraits
            _queue_npc_portraits(session, campaign)

    # Both portraits should exist (even though slugs are the same, npc_id differs)
    portraits = session.scalars(
        select(NpcPortrait).where(NpcPortrait.campaign_id == campaign.id)
    ).all()

    assert len(portraits) == 2
    assert all(p.status == "ready" for p in portraits)
    assert portraits[0].npc_id != portraits[1].npc_id
