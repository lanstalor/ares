import base64
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.portraits import NpcPortrait


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    # Enable foreign key constraints for SQLite
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


@pytest.fixture
def session():
    db = _make_session()
    try:
        yield db
    finally:
        db.close()


def test_npc_portrait_model_creation(session):
    """Test that NpcPortrait can be created with all fields."""
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    portrait = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc.id,
        slug="test-npc-portrait",
        prompt="A detailed portrait of a character",
        image_url="https://example.com/portrait.png",
        provider="openai",
        model="dall-e-3",
        status="ready",
    )
    session.add(portrait)
    session.commit()

    retrieved = session.query(NpcPortrait).filter_by(slug="test-npc-portrait").first()
    assert retrieved is not None
    assert retrieved.campaign_id == campaign.id
    assert retrieved.npc_id == npc.id
    assert retrieved.prompt == "A detailed portrait of a character"
    assert retrieved.image_url == "https://example.com/portrait.png"
    assert retrieved.provider == "openai"
    assert retrieved.model == "dall-e-3"
    assert retrieved.status == "ready"


def test_npc_portrait_default_status(session):
    """Test that NpcPortrait defaults to 'generating' status."""
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    portrait = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc.id,
        slug="test-npc",
        prompt="A portrait",
        image_url="https://example.com/portrait.png",
        provider="openai",
    )
    session.add(portrait)
    session.commit()

    retrieved = session.query(NpcPortrait).filter_by(slug="test-npc").first()
    assert retrieved.status == "generating"


def test_npc_portrait_unique_constraint(session):
    """Test that (campaign_id, npc_id) combination is unique."""
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    portrait1 = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc.id,
        slug="portrait-1",
        prompt="First portrait",
        image_url="https://example.com/1.png",
        provider="openai",
    )
    session.add(portrait1)
    session.commit()

    # Try to create another with same campaign_id and npc_id
    portrait2 = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc.id,
        slug="portrait-2",
        prompt="Second portrait",
        image_url="https://example.com/2.png",
        provider="openai",
    )
    session.add(portrait2)

    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        session.commit()


def test_npc_portrait_cascade_delete_on_campaign(session):
    """Test that portraits are deleted when campaign is deleted."""
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    portrait = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc.id,
        slug="test-npc",
        prompt="A portrait",
        image_url="https://example.com/portrait.png",
        provider="openai",
    )
    session.add(portrait)
    session.commit()

    session.delete(campaign)
    session.commit()

    retrieved = session.query(NpcPortrait).filter_by(slug="test-npc").first()
    assert retrieved is None


def test_npc_portrait_cascade_delete_on_npc(session):
    """Test that the foreign key constraint is set to CASCADE on delete."""
    # This test verifies that the ForeignKey has ondelete="CASCADE",
    # which means the database will enforce cascade deletes.
    npc_id_col = NpcPortrait.__table__.columns['npc_id']
    fk_constraints = list(npc_id_col.foreign_keys)
    assert len(fk_constraints) > 0

    # Verify that the FK has CASCADE delete
    for fk in fk_constraints:
        assert fk.ondelete.upper() == "CASCADE"


def test_npc_portrait_nullable_fields(session):
    """Test that model, revised_prompt, and error fields are nullable."""
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    portrait = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc.id,
        slug="test-npc",
        prompt="A portrait",
        image_url="https://example.com/portrait.png",
        provider="openai",
        model=None,
        revised_prompt=None,
        error=None,
    )
    session.add(portrait)
    session.commit()

    retrieved = session.query(NpcPortrait).filter_by(slug="test-npc").first()
    assert retrieved.model is None
    assert retrieved.revised_prompt is None
    assert retrieved.error is None


def test_campaign_relationship_npc_portraits(session):
    """Test that Campaign has npc_portraits relationship."""
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    npc1 = Character(campaign_id=campaign.id, name="NPC 1")
    npc2 = Character(campaign_id=campaign.id, name="NPC 2")
    session.add_all([npc1, npc2])
    session.commit()

    portrait1 = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc1.id,
        slug="npc-1",
        prompt="Portrait 1",
        image_url="https://example.com/1.png",
        provider="openai",
    )
    portrait2 = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc2.id,
        slug="npc-2",
        prompt="Portrait 2",
        image_url="https://example.com/2.png",
        provider="openai",
    )
    session.add_all([portrait1, portrait2])
    session.commit()

    retrieved_campaign = session.query(Campaign).filter_by(name="Test Campaign").first()
    assert len(retrieved_campaign.npc_portraits) == 2
    assert any(p.slug == "npc-1" for p in retrieved_campaign.npc_portraits)
    assert any(p.slug == "npc-2" for p in retrieved_campaign.npc_portraits)


def test_character_relationship_portrait(session):
    """Test that Character has portrait relationship (one-to-one)."""
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()

    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    portrait = NpcPortrait(
        campaign_id=campaign.id,
        npc_id=npc.id,
        slug="test-npc",
        prompt="A portrait",
        image_url="https://example.com/portrait.png",
        provider="openai",
    )
    session.add(portrait)
    session.commit()

    retrieved_npc = session.query(Character).filter_by(name="Test NPC").first()
    assert retrieved_npc.portrait is not None
    assert retrieved_npc.portrait.slug == "test-npc"


# Tests for slugify_npc_name function
class TestSlugifyNpcName:
    def test_slugify_npc_name_basic(self):
        """Test basic slug generation from name."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name("Captain Jag Delmar")
        assert result == "captain-jag-delmar"

    def test_slugify_npc_name_lowercase(self):
        """Test that uppercase is converted to lowercase."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name("GOLD COMMANDER")
        assert result == "gold-commander"

    def test_slugify_npc_name_special_chars(self):
        """Test that special characters are converted to dashes."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name("Alia of House Barca")
        assert result == "alia-of-house-barca"

    def test_slugify_npc_name_multiple_spaces(self):
        """Test that multiple spaces become single dashes."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name("Name    With    Spaces")
        assert result == "name-with-spaces"

    def test_slugify_npc_name_empty(self):
        """Test that empty string returns 'unknown-npc'."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name("")
        assert result == "unknown-npc"

    def test_slugify_npc_name_none(self):
        """Test that None returns 'unknown-npc'."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name(None)
        assert result == "unknown-npc"

    def test_slugify_npc_name_max_length(self):
        """Test that output is capped at 120 characters."""
        from app.services.npc_portrait_service import slugify_npc_name

        long_name = "This is a very long name " * 10
        result = slugify_npc_name(long_name)
        assert len(result) <= 120

    def test_slugify_npc_name_only_special_chars(self):
        """Test that name with only special chars returns 'unknown-npc'."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name("!@#$%^&*()")
        assert result == "unknown-npc"

    def test_slugify_npc_name_with_numbers(self):
        """Test that numbers are preserved."""
        from app.services.npc_portrait_service import slugify_npc_name

        result = slugify_npc_name("Agent 007 Bond")
        assert result == "agent-007-bond"


# Tests for build_portrait_prompt function
class TestBuildPortraitPrompt:
    def test_build_portrait_prompt_includes_name_and_race(self):
        """Test that prompt includes character name and race."""
        from app.services.npc_portrait_service import build_portrait_prompt

        campaign = Campaign(name="Test Campaign")
        session = _make_session()
        session.add(campaign)
        session.commit()

        character = Character(
            campaign_id=campaign.id,
            name="Captain Jag",
            race="Gold",
            character_class="Commander",
        )
        session.add(character)
        session.commit()

        prompt = build_portrait_prompt(session, character)
        assert "Captain Jag" in prompt
        assert "Gold" in prompt

    def test_build_portrait_prompt_includes_character_class(self):
        """Test that prompt includes character_class if available."""
        from app.services.npc_portrait_service import build_portrait_prompt

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(
            campaign_id=campaign.id,
            name="Test Character",
            character_class="Warrior",
        )
        session.add(character)
        session.commit()

        prompt = build_portrait_prompt(session, character)
        assert "Test Character" in prompt
        assert "Warrior" in prompt

    def test_build_portrait_prompt_red_rising_context(self):
        """Test that prompt includes Red Rising universe context."""
        from app.services.npc_portrait_service import build_portrait_prompt

        session = _make_session()
        campaign = Campaign(name="Test Campaign", current_date_pce=728)
        session.add(campaign)
        session.commit()

        character = Character(
            campaign_id=campaign.id,
            name="Test Character",
            race="Red",
        )
        session.add(character)
        session.commit()

        prompt = build_portrait_prompt(session, character)
        assert "Red Rising" in prompt
        assert "728" in prompt or "PCE" in prompt

    def test_build_portrait_prompt_excludes_notes(self):
        """Test that internal notes are excluded from prompt."""
        from app.services.npc_portrait_service import build_portrait_prompt

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(
            campaign_id=campaign.id,
            name="Test Character",
            notes="SECRET_HIDDEN_AGENDA_HERE",
        )
        session.add(character)
        session.commit()

        prompt = build_portrait_prompt(session, character)
        assert "SECRET_HIDDEN_AGENDA_HERE" not in prompt

    def test_build_portrait_prompt_photorealistic_style(self):
        """Test that prompt includes photorealistic style guidance."""
        from app.services.npc_portrait_service import build_portrait_prompt

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(
            campaign_id=campaign.id,
            name="Test Character",
        )
        session.add(character)
        session.commit()

        prompt = build_portrait_prompt(session, character)
        assert "photorealistic" in prompt.lower()

    def test_build_portrait_prompt_minimal_character(self):
        """Test that prompt works with minimal character data."""
        from app.services.npc_portrait_service import build_portrait_prompt

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(
            campaign_id=campaign.id,
            name="Minimal",
        )
        session.add(character)
        session.commit()

        prompt = build_portrait_prompt(session, character)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Minimal" in prompt


# Tests for get_cached_portrait function
class TestGetCachedPortrait:
    def test_get_cached_portrait_found(self):
        """Test that get_cached_portrait returns portrait when found."""
        from app.services.npc_portrait_service import get_cached_portrait

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        npc = Character(campaign_id=campaign.id, name="Test NPC")
        session.add(npc)
        session.commit()

        portrait = NpcPortrait(
            campaign_id=campaign.id,
            npc_id=npc.id,
            slug="test-npc",
            prompt="A portrait",
            image_url="https://example.com/portrait.png",
            provider="openai",
            status="ready",
        )
        session.add(portrait)
        session.commit()

        result = get_cached_portrait(session, campaign.id, npc.id)
        assert result is not None
        assert result.id == portrait.id
        assert result.slug == "test-npc"

    def test_get_cached_portrait_not_found(self):
        """Test that get_cached_portrait returns None when not found."""
        from app.services.npc_portrait_service import get_cached_portrait

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        result = get_cached_portrait(session, campaign.id, "nonexistent-npc-id")
        assert result is None


# Tests for ensure_portrait function
class TestEnsurePortrait:
    def test_ensure_portrait_generates_if_missing(self):
        """Test that ensure_portrait generates a new portrait when none exists."""
        from app.services.npc_portrait_service import ensure_portrait
        from unittest.mock import Mock

        session = _make_session()
        campaign = Campaign(name="Test Campaign", current_date_pce=728)
        session.add(campaign)
        session.commit()

        character = Character(campaign_id=campaign.id, name="Test NPC")
        session.add(character)
        session.commit()

        # Mock media provider
        mock_response = Mock()
        mock_response.provider = "openai"
        mock_response.model = "dall-e-3"
        mock_response.b64_json = base64.b64encode(b"fake-png-data").decode("utf-8")
        mock_response.url = None
        mock_response.revised_prompt = "Revised prompt"

        mock_provider = Mock()
        mock_provider.generate_image.return_value = mock_response

        # Mock cache_dir to avoid writing actual files
        import tempfile
        temp_dir = tempfile.mkdtemp()

        portrait = ensure_portrait(
            session=session,
            campaign=campaign,
            character=character,
            force=False,
            media_provider=mock_provider,
            cache_dir=Path(temp_dir),
        )

        assert portrait is not None
        assert portrait.status == "ready"
        assert portrait.campaign_id == campaign.id
        assert portrait.npc_id == character.id
        assert portrait.provider == "openai"
        assert portrait.model == "dall-e-3"

        # Verify file was written
        expected_path = Path(temp_dir) / "test-npc.png"
        assert expected_path.exists()

    def test_ensure_portrait_returns_cached(self):
        """Test that ensure_portrait returns cached portrait when available."""
        from app.services.npc_portrait_service import ensure_portrait
        from unittest.mock import Mock

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(campaign_id=campaign.id, name="Test NPC")
        session.add(character)
        session.commit()

        # Create cached portrait
        cached_portrait = NpcPortrait(
            campaign_id=campaign.id,
            npc_id=character.id,
            slug="test-npc",
            prompt="Cached prompt",
            image_url="/portraits/test-npc.png",
            provider="openai",
            model="dall-e-3",
            status="ready",
        )
        session.add(cached_portrait)
        session.commit()

        # Mock media provider that should NOT be called
        mock_provider = Mock()

        portrait = ensure_portrait(
            session=session,
            campaign=campaign,
            character=character,
            force=False,
            media_provider=mock_provider,
        )

        assert portrait.id == cached_portrait.id
        # Verify media provider was NOT called
        mock_provider.generate_image.assert_not_called()

    def test_ensure_portrait_force_regenerates(self):
        """Test that ensure_portrait regenerates when force=True."""
        from app.services.npc_portrait_service import ensure_portrait
        from unittest.mock import Mock

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(campaign_id=campaign.id, name="Test NPC")
        session.add(character)
        session.commit()

        # Create cached portrait
        cached_portrait = NpcPortrait(
            campaign_id=campaign.id,
            npc_id=character.id,
            slug="test-npc",
            prompt="Old prompt",
            image_url="/portraits/test-npc.png",
            provider="openai",
            status="ready",
        )
        session.add(cached_portrait)
        session.commit()

        # Mock media provider
        mock_response = Mock()
        mock_response.provider = "openai"
        mock_response.model = "dall-e-3"
        mock_response.b64_json = base64.b64encode(b"new-fake-png-data").decode("utf-8")
        mock_response.url = None
        mock_response.revised_prompt = "New revised prompt"

        mock_provider = Mock()
        mock_provider.generate_image.return_value = mock_response

        # Mock cache_dir
        import tempfile
        temp_dir = tempfile.mkdtemp()

        portrait = ensure_portrait(
            session=session,
            campaign=campaign,
            character=character,
            force=True,
            media_provider=mock_provider,
            cache_dir=Path(temp_dir),
        )

        assert portrait.id == cached_portrait.id
        assert portrait.status == "ready"
        assert portrait.revised_prompt == "New revised prompt"
        # Verify media provider WAS called
        mock_provider.generate_image.assert_called_once()

    def test_ensure_portrait_handles_provider_error(self):
        """Test that ensure_portrait handles provider errors gracefully."""
        from app.services.npc_portrait_service import ensure_portrait
        from unittest.mock import Mock

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(campaign_id=campaign.id, name="Test NPC")
        session.add(character)
        session.commit()

        # Mock media provider that raises an error
        mock_provider = Mock()
        mock_provider.generate_image.side_effect = RuntimeError("Provider timeout")

        portrait = ensure_portrait(
            session=session,
            campaign=campaign,
            character=character,
            force=False,
            media_provider=mock_provider,
        )

        assert portrait is not None
        assert portrait.status == "failed"
        assert "Provider timeout" in portrait.error

    def test_ensure_portrait_handles_cache_error(self):
        """Test that ensure_portrait handles caching errors gracefully."""
        from app.services.npc_portrait_service import ensure_portrait
        from unittest.mock import Mock

        session = _make_session()
        campaign = Campaign(name="Test Campaign")
        session.add(campaign)
        session.commit()

        character = Character(campaign_id=campaign.id, name="Test NPC")
        session.add(character)
        session.commit()

        # Mock media provider with invalid b64_json
        mock_response = Mock()
        mock_response.provider = "openai"
        mock_response.model = "dall-e-3"
        mock_response.b64_json = "invalid-base64!!!"
        mock_response.url = None

        mock_provider = Mock()
        mock_provider.generate_image.return_value = mock_response

        portrait = ensure_portrait(
            session=session,
            campaign=campaign,
            character=character,
            force=False,
            media_provider=mock_provider,
        )

        assert portrait is not None
        assert portrait.status == "failed"
        assert portrait.error is not None
