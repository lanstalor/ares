import base64
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.campaigns import create_campaign
from app.api.routes.portraits import get_portrait_detail, list_portraits, regenerate_portrait
from app.core.config import get_settings
from app.models.base import Base
from app.models.character import Character
from app.schemas.campaign import CampaignCreate
from app.schemas.portraits import PortraitRegenerateRequest
from app.services.media_provider import MediaRequest, MediaResponse
from app.services.npc_portrait_service import ensure_portrait, slugify_npc_name


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_slugify_npc_name_is_stable() -> None:
    assert slugify_npc_name("Alia of House Visigoth") == "alia-of-house-visigoth"
    assert slugify_npc_name("Cassius") == "cassius"
    assert slugify_npc_name(None) == "unknown-npc"


def test_list_portraits_returns_empty_initially() -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Portrait Route Test"), session)

    portraits = list_portraits(campaign.id, session)

    assert portraits == []


def test_list_portraits_after_ensure_portrait(tmp_path) -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Portrait Route Test"), session)
    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    class Provider:
        def generate_image(self, request: MediaRequest) -> MediaResponse:
            return MediaResponse(
                provider="fake",
                model="fake-image",
                media_type="image/png",
                b64_json=base64.b64encode(b"png-bytes").decode("ascii"),
                revised_prompt="revised",
                cache_key=request.cache_key,
            )

    ensure_portrait(
        session=session,
        campaign=campaign,
        character=npc,
        media_provider=Provider(),
        cache_dir=tmp_path,
    )
    session.commit()

    portraits = list_portraits(campaign.id, session)

    assert len(portraits) == 1
    assert portraits[0].npc_id == npc.id
    assert portraits[0].status == "ready"


def test_get_portrait_detail_by_npc_id(tmp_path) -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Portrait Route Test"), session)
    npc = Character(campaign_id=campaign.id, name="Alia of House Visigoth")
    session.add(npc)
    session.commit()

    class Provider:
        def generate_image(self, request: MediaRequest) -> MediaResponse:
            return MediaResponse(
                provider="fake",
                model="fake-image",
                media_type="image/png",
                b64_json=base64.b64encode(b"png-bytes").decode("ascii"),
                revised_prompt="revised",
                cache_key=request.cache_key,
            )

    ensure_portrait(
        session=session,
        campaign=campaign,
        character=npc,
        media_provider=Provider(),
        cache_dir=tmp_path,
    )
    session.commit()

    portrait = get_portrait_detail(campaign.id, npc.id, session)

    assert portrait.npc_id == npc.id
    assert portrait.slug == "alia-of-house-visigoth"
    assert portrait.status == "ready"


def test_regenerate_portrait_with_force(tmp_path) -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Portrait Route Test"), session)
    npc = Character(campaign_id=campaign.id, name="Test NPC")
    session.add(npc)
    session.commit()

    call_count = [0]

    class Provider:
        def generate_image(self, request: MediaRequest) -> MediaResponse:
            call_count[0] += 1
            return MediaResponse(
                provider="fake",
                model="fake-image",
                media_type="image/png",
                b64_json=base64.b64encode(b"png-bytes").decode("ascii"),
                revised_prompt="revised",
                cache_key=request.cache_key,
            )

    # First generation
    ensure_portrait(
        session=session,
        campaign=campaign,
        character=npc,
        media_provider=Provider(),
        cache_dir=tmp_path,
    )
    session.commit()

    assert call_count[0] == 1

    # Regenerate with force=True
    portrait = regenerate_portrait(
        campaign.id,
        npc.id,
        PortraitRegenerateRequest(force=True),
        session,
    )
    session.commit()

    assert call_count[0] == 2
    assert portrait.status == "ready"
