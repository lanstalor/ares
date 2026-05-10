from app.api.routes.campaigns import create_campaign, get_campaign_state
from app.api.routes.operator import get_campaign_full_state
from app.api.routes.turns import create_turn
from app.core.config import get_settings
from app.models.base import Base
from app.models.campaign import Clock
from app.models.conditions import Condition
from app.schemas.campaign import CampaignCreate
from app.schemas.turn import TurnCreate
from sqlalchemy import create_engine
from sqlalchemy import select
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
    # Character name comes from world_bible seed
    assert state.player_character.name == "Mara of Cimmeria"
    assert state.current_location == "Surface Relay Tower 19"
    clock_labels = set(session.scalars(select(Clock.label).where(Clock.campaign_id == campaign.id)))
    assert "Pelsin Diagnostic Scrub" in clock_labels
    assert "BoQC Heat" in clock_labels


def test_create_turn_persists_response(monkeypatch) -> None:
    monkeypatch.setenv("ARES_GENERATION_PROVIDER", "stub")
    get_settings.cache_clear()
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Turn Test"), session)

    resolution = create_turn(campaign.id, TurnCreate(player_input="Check the Melt."), session)
    state = get_campaign_state(campaign.id, session)

    assert resolution.turn.player_input == "Check the Melt."
    assert resolution.canon_guard_passed is True
    assert len(state.recent_turns) == 1


def test_player_state_filters_gm_only_conditions_but_operator_state_keeps_them() -> None:
    session = _make_session()
    campaign = create_campaign(CampaignCreate(name="Condition Visibility Test"), session)
    character = get_campaign_state(campaign.id, session).player_character
    assert character is not None

    session.add_all(
        [
            Condition(
                campaign_id=campaign.id,
                character_id=character.id,
                condition_type="ident_flagged",
                duration_remaining=5,
                persistence="persistent",
                source="checkpoint slate",
            ),
            Condition(
                campaign_id=campaign.id,
                character_id=character.id,
                condition_type="wounded",
                duration_remaining=2,
                persistence="persistent",
                source="test wound",
            ),
        ]
    )
    session.commit()

    player_state = get_campaign_state(campaign.id, session)
    operator_state = get_campaign_full_state(campaign.id, session)

    assert player_state.player_character is not None
    player_conditions = {condition.condition_type for condition in player_state.player_character.conditions}
    operator_conditions = {
        condition.condition_type
        for operator_character in operator_state.characters
        for condition in operator_character.conditions
    }

    assert player_conditions == {"wounded"}
    assert {"ident_flagged", "wounded"} <= operator_conditions
