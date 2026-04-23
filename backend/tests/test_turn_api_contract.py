from app.api.routes.campaigns import create_campaign, get_campaign_state
from app.api.routes.turns import create_turn
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


def test_create_campaign_bootstraps_default_character() -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Test Cell", tagline="A test tagline"), session)

    state = get_campaign_state(campaign.id, session)

    assert state.campaign.name == "Test Cell"
    assert state.player_character is not None
    assert state.player_character.name == "Davan of Tharsis"


def test_create_turn_persists_response() -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Turn Test"), session)

    resolution = create_turn(campaign.id, TurnCreate(player_input="Check the Melt."), session)
    state = get_campaign_state(campaign.id, session)

    assert resolution.turn.player_input == "Check the Melt."
    assert resolution.canon_guard_passed is True
    assert len(state.recent_turns) == 1
