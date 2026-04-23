from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums import ClockType, SecretStatus, Visibility
from app.models.base import Base
from app.models.campaign import Campaign, Clock, Objective
from app.models.character import Character
from app.models.memory import Secret, Turn
from app.models.world import Area, Faction, NPC
from app.services.context_builder import build_turn_context


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def _bootstrap_scenario(session: Session) -> Campaign:
    faction = Faction(name="Sons of Ares")
    session.add(faction)
    session.flush()
    area = Area(
        name="Crescent Block - Callisto Depot District",
        description="A pressed-tin warren beneath the depot.",
        faction_id=faction.id,
    )
    session.add(area)
    npc = NPC(
        name="Vex",
        faction_id=faction.id,
        appearance="Lean Grey in mechanic's grease.",
        personality="Smiling, cautious.",
        hidden_agenda="Vex is informing the Greys of cell movements.",
        visibility=Visibility.GM_ONLY,
    )
    session.add(npc)
    campaign = Campaign(
        name="Sons of Ares — Ganymede",
        tagline="A cell on Ganymede tries to survive 728 PCE.",
        current_date_pce=728,
        current_location_label="Crescent Block - Callisto Depot District",
    )
    session.add(campaign)
    session.flush()
    session.add(
        Character(
            campaign_id=campaign.id,
            name="Davan of Tharsis",
            cover_identity="Dav of Vashti",
            current_hp=38,
            max_hp=38,
            cover_integrity=8,
        )
    )
    session.add(
        Objective(
            campaign_id=campaign.id,
            title="Check the Melt before shift",
            description="Walk the Melt and confirm Vex's status.",
            gm_instructions="If the player asks Vex about Greys, advance Citadel suspicion.",
            is_active=True,
        )
    )
    session.add(
        Clock(
            campaign_id=campaign.id,
            label="Citadel suspicion",
            clock_type=ClockType.THREAT,
            current_value=1,
            max_value=4,
        )
    )
    session.add(
        Secret(
            campaign_id=campaign.id,
            label="NPC: Vex / Hidden agenda",
            content="Vex is informing the Greys.",
            status=SecretStatus.ELIGIBLE,
            reveal_condition="Reveal only after Vex flinches when asked about the Citadel.",
        )
    )
    session.add(
        Secret(
            campaign_id=campaign.id,
            label="Faction: Greys / Citadel briefing",
            content="The Greys briefed the Citadel about a cell at Crescent Block.",
            status=SecretStatus.DORMANT,
        )
    )
    session.add(
        Turn(
            campaign_id=campaign.id,
            player_input="Walk to the Melt.",
            gm_response="Davan steps into the warm dark of the Melt.",
            player_safe_summary="Davan walked into the Melt.",
        )
    )
    session.commit()
    return campaign


def test_player_safe_brief_includes_visible_state() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "Crescent Block - Callisto Depot District" in ctx.player_safe_brief
    assert "Check the Melt before shift" in ctx.player_safe_brief
    assert "Davan walked into the Melt." in ctx.player_safe_brief
    assert "Dav of Vashti" in ctx.player_safe_brief


def test_hidden_gm_brief_includes_eligible_secret_with_reveal_condition() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Ask Vex about the Citadel.")

    assert "Vex is informing the Greys." in ctx.hidden_gm_brief
    assert "Reveal only after Vex flinches" in ctx.hidden_gm_brief


def test_hidden_gm_brief_includes_active_clocks() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "Citadel suspicion" in ctx.hidden_gm_brief
    assert "1/4" in ctx.hidden_gm_brief


def test_hidden_gm_brief_includes_objective_gm_instructions() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "advance Citadel suspicion" in ctx.hidden_gm_brief


def test_hidden_gm_brief_includes_npc_hidden_agenda_in_scene() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "Vex is informing the Greys" in ctx.hidden_gm_brief


def test_player_safe_brief_never_leaks_eligible_secret_content() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Ask Vex about the Citadel.")

    assert "Vex is informing the Greys" not in ctx.player_safe_brief
    assert "Reveal only after Vex flinches" not in ctx.player_safe_brief


def test_player_safe_brief_never_leaks_objective_gm_instructions() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "advance Citadel suspicion" not in ctx.player_safe_brief


def test_player_safe_brief_never_leaks_npc_hidden_agenda() -> None:
    session = _make_session()
    campaign = _bootstrap_scenario(session)

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "informing the Greys" not in ctx.player_safe_brief
