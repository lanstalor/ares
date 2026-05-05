from app.api.routes.campaigns import create_campaign
from app.api.routes.operator import get_campaign_full_state, operator_health, patch_campaign_state
from app.api.routes.turns import create_turn
from app.core.config import get_settings
from app.core.enums import SecretStatus
from app.models.base import Base
from app.models.campaign import Clock
from app.models.memory import Secret
from app.schemas.campaign import CampaignCreate
from app.schemas.operator import CampaignStatePatch, ClockUpdate, SecretUpdate
from app.schemas.turn import TurnCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_operator_health():
    assert operator_health() == {"status": "ok", "surface": "operator"}


def test_get_campaign_full_state(monkeypatch):
    monkeypatch.setenv("ARES_GENERATION_PROVIDER", "stub")
    get_settings.cache_clear()
    session = _make_session()

    # Create campaign
    campaign = create_campaign(CampaignCreate(name="Op Test"), session)

    # Add a turn to ensure turns/memories exist
    create_turn(campaign.id, TurnCreate(player_input="Testing operator access."), session)

    # Retrieve full state
    full_state = get_campaign_full_state(campaign.id, session)

    assert full_state.campaign.name == "Op Test"
    assert len(full_state.turns) == 1
    assert full_state.world is not None
    # Verify we can see all fields
    assert hasattr(full_state.world, "factions")
    assert isinstance(full_state.world.factions, list)


def test_patch_campaign_state(monkeypatch):
    monkeypatch.setenv("ARES_GENERATION_PROVIDER", "stub")
    get_settings.cache_clear()
    session = _make_session()

    # Create campaign
    campaign = create_campaign(CampaignCreate(name="Patch Test"), session)

    # Add a clock manually
    clock = Clock(campaign_id=campaign.id, label="Test Clock", clock_type="tension", current_value=0, max_value=4)
    session.add(clock)
    # Add a secret manually
    secret = Secret(campaign_id=campaign.id, label="Test Secret", content="Hidden truth", status=SecretStatus.DORMANT)
    session.add(secret)
    session.commit()

    # Prepare patch
    patch = CampaignStatePatch(
        clocks=[ClockUpdate(id=clock.id, current_value=2)],
        secrets=[SecretUpdate(id=secret.id, status=SecretStatus.REVEALED)]
    )

    # Apply patch
    updated_state = patch_campaign_state(campaign.id, patch, session)

    # Verify updates
    updated_clock = next(c for c in updated_state.clocks if c.id == clock.id)
    assert updated_clock.current_value == 2

    updated_secret = next(s for s in updated_state.secrets if s.id == secret.id)
    assert updated_secret.status == SecretStatus.REVEALED
