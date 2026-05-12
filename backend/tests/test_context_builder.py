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
    assert "Davan steps into the warm dark of the Melt." in ctx.player_safe_brief
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


def test_hidden_gm_brief_marks_fired_clock() -> None:
    session = _make_session()
    campaign = Campaign(
        name="Fired Clock Test",
        current_date_pce=728,
        current_location_label="Crescent Block - Callisto Depot District",
    )
    session.add(campaign)
    session.flush()
    clock = Clock(
        campaign_id=campaign.id,
        label="Citadel suspicion",
        clock_type=ClockType.THREAT,
        current_value=4,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "FIRED" in ctx.hidden_gm_brief
    assert "Citadel suspicion" in ctx.hidden_gm_brief


def test_hidden_gm_brief_does_not_mark_unfired_clock() -> None:
    session = _make_session()
    campaign = Campaign(
        name="Unfired Clock Test",
        current_date_pce=728,
        current_location_label="Crescent Block - Callisto Depot District",
    )
    session.add(campaign)
    session.flush()
    clock = Clock(
        campaign_id=campaign.id,
        label="Citadel suspicion",
        clock_type=ClockType.THREAT,
        current_value=2,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    ctx = build_turn_context(session, campaign, "Look around.")

    assert "FIRED" not in ctx.hidden_gm_brief


def test_extract_repeated_phrases_finds_cross_turn_repeats():
    from app.services.context_builder import _extract_repeated_phrases

    class _T:
        def __init__(self, text): self.gm_response = text

    turns = [
        _T("She kept her hands where I can see them and waited."),
        _T("The boots on the rail scuffed once. Hands where I can see them."),
        _T("Boots on the rail again, hard now."),
        _T("Her hands where i can see them, palms open."),
        _T("Different scene entirely with no repeats."),
    ]
    phrases = _extract_repeated_phrases(turns)
    joined = " | ".join(phrases)

    assert "hands where i can see them" in joined
    assert "boots on the rail" in joined
    assert len(phrases) <= 6


def test_extract_repeated_phrases_empty_when_no_repeats():
    from app.services.context_builder import _extract_repeated_phrases

    class _T:
        def __init__(self, text): self.gm_response = text

    turns = [_T("alpha bravo charlie delta echo"), _T("foxtrot golf hotel india juliet")]
    assert _extract_repeated_phrases(turns) == []



def test_hidden_brief_includes_gm_only_memories() -> None:
    session = _make_session()
    from app.models.campaign import Campaign
    from app.models.memory import Memory
    from app.core.enums import Visibility

    campaign = Campaign(name="Test", current_date_pce=728)
    session.add(campaign)
    session.flush()

    session.add_all([
        Memory(campaign_id=campaign.id, content="GM noted Mara flinched at Gray's name", visibility=Visibility.GM_ONLY),
        Memory(campaign_id=campaign.id, content="Player saw Vaia bow", visibility=Visibility.PLAYER_FACING),
    ])
    session.commit()

    ctx = build_turn_context(session, campaign, "test input")

    assert "GM-only observations" in ctx.hidden_gm_brief
    assert "Mara flinched" in ctx.hidden_gm_brief
    assert "Mara flinched" not in ctx.player_safe_brief


def test_briefs_include_scene_state_and_narrative_summary() -> None:
    session = _make_session()
    from app.models.campaign import Campaign

    campaign = Campaign(
        name="Test",
        current_date_pce=728,
        last_scene_state={
            "tension_tier": 3,
            "key_holdings": "Mara holds strip; Gray holds wand",
            "last_concrete_change": "Copper joined the catwalk",
        },
        narrative_summary="Mara entered Surface Relay 19 on a sabotage run and pulled a hidden carrier strip from the maintenance port under Gray scrutiny.",
    )
    session.add(campaign)
    session.commit()

    ctx = build_turn_context(session, campaign, "next action")

    assert "Scene state at start of this turn" in ctx.hidden_gm_brief
    assert "Tension tier: 3" in ctx.hidden_gm_brief
    assert "Mara holds strip" in ctx.hidden_gm_brief
    assert "Copper joined the catwalk" in ctx.hidden_gm_brief

    assert "Story so far" in ctx.hidden_gm_brief
    assert "Story so far" in ctx.player_safe_brief
    assert "sabotage run" in ctx.player_safe_brief


def test_briefs_omit_empty_scene_state_and_summary() -> None:
    session = _make_session()
    from app.models.campaign import Campaign

    campaign = Campaign(name="Test", current_date_pce=728)
    session.add(campaign)
    session.commit()

    ctx = build_turn_context(session, campaign, "first turn")

    assert "Scene state at start of this turn" not in ctx.hidden_gm_brief
    assert "Story so far" not in ctx.hidden_gm_brief
    assert "Story so far" not in ctx.player_safe_brief


def test_hidden_brief_includes_repeated_phrase_banlist() -> None:
    session = _make_session()
    from app.models.campaign import Campaign
    from app.models.memory import Turn

    campaign = Campaign(name="Test", current_date_pce=728)
    session.add(campaign)
    session.flush()

    session.add_all([
        Turn(campaign_id=campaign.id, player_input="x", gm_response="She kept her hands where I can see them. She waited.", player_safe_summary="s"),
        Turn(campaign_id=campaign.id, player_input="x", gm_response="Hands where I can see them, palms open. Quiet.", player_safe_summary="s"),
        Turn(campaign_id=campaign.id, player_input="x", gm_response="He said hands where I can see them and stepped back.", player_safe_summary="s"),
    ])
    session.commit()

    ctx = build_turn_context(session, campaign, "next action")

    assert "Banned phrases this scene" in ctx.hidden_gm_brief
    assert "hands where i can see them" in ctx.hidden_gm_brief
