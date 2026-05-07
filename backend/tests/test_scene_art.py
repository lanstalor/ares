import base64
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.campaigns import create_campaign
from app.api.routes.media import get_current_scene_art, regenerate_scene_art
from app.core.config import get_settings
from app.models.base import Base
from app.models.campaign import Objective
from app.schemas.campaign import CampaignCreate
from app.schemas.media import SceneArtRegenerateRequest
from app.services.media_provider import MediaRequest, MediaResponse
from app.services.scene_art import build_scene_art_prompt, ensure_scene_art, slugify_scene_label


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_slugify_scene_label_is_stable() -> None:
    assert slugify_scene_label("Crescent Block - Callisto Depot District") == "crescent-block-callisto-depot-district"


def test_scene_art_prompt_uses_player_safe_context_only() -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Prompt Test", tagline="Public premise"), session)

    # Deactivate the bootstrap objective and add a test one
    default_objective = session.query(Objective).filter(
        Objective.campaign_id == campaign.id,
        Objective.is_active == True,
    ).first()
    if default_objective:
        default_objective.is_active = False

    session.add(
        Objective(
            campaign_id=campaign.id,
            title="Find the relay",
            description="Player-facing objective.",
            gm_instructions="Hidden: betray Davan.",
            is_active=True,
        )
    )
    session.commit()

    prompt = build_scene_art_prompt(
        session=session,
        campaign=campaign,
        location_label="Maintenance Deck",
    )

    assert "Prompt Test" in prompt
    assert "Public premise" in prompt
    assert "Maintenance Deck" in prompt
    assert "Find the relay" in prompt
    assert "betray Davan" not in prompt


def test_ensure_scene_art_caches_b64_payload(tmp_path) -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Art Test"), session)
    calls: list[MediaRequest] = []

    class Provider:
        def generate_image(self, request: MediaRequest) -> MediaResponse:
            calls.append(request)
            return MediaResponse(
                provider="fake",
                model="fake-image",
                media_type="image/png",
                b64_json=base64.b64encode(b"png-bytes").decode("ascii"),
                revised_prompt="revised",
                cache_key=request.cache_key,
            )

    scene_art = ensure_scene_art(
        session=session,
        campaign=campaign,
        location_label="Maintenance Deck",
        media_provider=Provider(),
        cache_dir=tmp_path,
    )
    session.commit()

    assert calls[0].kind == "scene_art"
    assert calls[0].cache_key == f"{campaign.id}:maintenance-deck"
    assert scene_art.image_url == "/api/v1/media/scene-art/maintenance-deck.png"
    assert (tmp_path / "maintenance-deck.png").read_bytes() == b"png-bytes"

    cached = ensure_scene_art(
        session=session,
        campaign=campaign,
        location_label="Maintenance Deck",
        media_provider=SimpleNamespace(generate_image=lambda _: (_ for _ in ()).throw(AssertionError("uncached"))),
    )
    assert cached.id == scene_art.id


def test_media_routes_create_and_regenerate_scene_art(monkeypatch) -> None:
    monkeypatch.setenv("ARES_MEDIA_PROVIDER", "stub")
    get_settings.cache_clear()
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Route Test"), session)

    current = get_current_scene_art(campaign.id, session)
    regenerated = regenerate_scene_art(
        campaign.id,
        SceneArtRegenerateRequest(location_label="The Gyre", force=True),
        session,
    )

    assert current.provider == "stub"
    assert current.image_url.startswith("/scene-art/")
    assert regenerated.slug == "the-gyre"
    assert regenerated.provider == "stub"
