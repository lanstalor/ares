from app.api.routes.campaigns import create_campaign, get_campaign_state
from app.models.base import Base
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def test_campaign_state_includes_combat_state_when_populated() -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Combat State Test"), session)

    # Directly set combat_state on the Campaign row
    db_campaign = session.get(Campaign, campaign.id)
    assert db_campaign is not None
    db_campaign.combat_state = {
        "active": True,
        "round": 1,
        "combatants": ["Mara", "Guard Alpha"],
        "current_turn": "Mara",
    }
    session.commit()

    state = get_campaign_state(campaign.id, session)

    assert state.combat_state is not None
    assert state.combat_state["active"] is True
    assert state.combat_state["round"] == 1
    assert state.combat_state["current_turn"] == "Mara"
    assert "Guard Alpha" in state.combat_state["combatants"]


def test_campaign_state_combat_state_is_none_when_not_set() -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="No Combat Test"), session)

    state = get_campaign_state(campaign.id, session)

    assert state.combat_state is None
