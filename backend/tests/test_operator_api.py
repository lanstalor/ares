from app.api.routes.campaigns import create_campaign
from app.api.routes.operator import get_campaign_full_state, operator_health
from app.api.routes.turns import create_turn
from app.core.config import get_settings
from app.models.base import Base
from app.schemas.campaign import CampaignCreate
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
