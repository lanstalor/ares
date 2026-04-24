from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums import ClockType, SecretStatus, Visibility
from app.models.base import Base
from app.models.campaign import Campaign, Clock
from app.models.memory import Memory, Secret
from app.services.ai_provider import NarrationRequest, NarrationResponse
from app.services.consequence_applier import (
    ClockTick,
    Consequences,
    LocationChange,
    MemoryDraft,
    SecretStatusChange,
)
from app.services.turn_engine import resolve_turn


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def _make_campaign(session: Session, *, location: str = "Crescent Block - Callisto Depot District") -> Campaign:
    campaign = Campaign(
        name="Project Ares",
        tagline="Hidden-state test campaign",
        current_date_pce=728,
        current_location_label=location,
    )
    session.add(campaign)
    session.flush()
    return campaign


class FakeProvider:
    def __init__(self, response: NarrationResponse) -> None:
        self.response = response
        self.last_request: NarrationRequest | None = None

    def narrate(self, request: NarrationRequest) -> NarrationResponse:
        self.last_request = request
        return self.response


def test_turn_engine_returns_context_and_summary() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    provider = FakeProvider(
        NarrationResponse(
            narrative="Davan slips through the warm dark.",
            player_safe_summary="Davan walked into the Melt.",
            consequences=Consequences(),
        )
    )

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Check the Melt before shift.",
        narration_provider=provider,
    )

    assert "Project Ares" in result.context_excerpt
    assert result.player_safe_summary == "Davan walked into the Melt."
    assert result.canon_guard_passed is True


def test_turn_engine_passes_full_context_to_provider() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    provider = FakeProvider(
        NarrationResponse(
            narrative="Quiet.", player_safe_summary="Quiet.", consequences=Consequences()
        )
    )

    resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Look around.",
        narration_provider=provider,
    )

    assert provider.last_request is not None
    assert "Crescent Block" in provider.last_request.player_safe_brief
    assert "[GM-only context" in provider.last_request.hidden_gm_brief


def test_turn_engine_applies_consequences_when_canon_guard_passes() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    clock = Clock(
        campaign_id=campaign.id,
        label="Citadel suspicion",
        clock_type=ClockType.THREAT,
        current_value=0,
        max_value=4,
    )
    secret = Secret(
        campaign_id=campaign.id,
        label="NPC: Vex / Hidden agenda",
        content="Vex is informing the Greys.",
        status=SecretStatus.DORMANT,
    )
    session.add_all([clock, secret])
    session.commit()

    provider = FakeProvider(
        NarrationResponse(
            narrative="Vex flinches as Davan watches.",
            player_safe_summary="Vex looks unsettled.",
            consequences=Consequences(
                clock_ticks=[ClockTick(label="Citadel suspicion", delta=1)],
                secret_status_changes=[
                    SecretStatusChange(label="NPC: Vex / Hidden agenda", new_status=SecretStatus.ELIGIBLE)
                ],
                new_memories=[
                    MemoryDraft(content="Vex flinched when asked about Greys.", visibility=Visibility.GM_ONLY)
                ],
            ),
        )
    )

    resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Watch Vex closely.",
        narration_provider=provider,
    )
    session.commit()

    assert session.scalar(select(Clock).where(Clock.id == clock.id)).current_value == 1
    assert session.scalar(select(Secret).where(Secret.id == secret.id)).status == SecretStatus.ELIGIBLE
    memories = list(session.scalars(select(Memory).where(Memory.campaign_id == campaign.id)))
    assert len(memories) == 1
    assert memories[0].visibility == Visibility.GM_ONLY


def test_turn_engine_skips_consequences_when_canon_guard_fails() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    clock = Clock(
        campaign_id=campaign.id,
        label="Citadel suspicion",
        clock_type=ClockType.THREAT,
        current_value=0,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    provider = FakeProvider(
        NarrationResponse(
            narrative="Darrow steps from the shadows.",
            player_safe_summary="A figure appears.",
            consequences=Consequences(
                clock_ticks=[ClockTick(label="Citadel suspicion", delta=2)],
            ),
        )
    )

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Wait.",
        narration_provider=provider,
    )
    session.commit()

    assert result.canon_guard_passed is False
    assert "Darrow" in (result.canon_guard_message or "")
    assert session.scalar(select(Clock).where(Clock.id == clock.id)).current_value == 0


def test_turn_engine_populates_clocks_fired_when_clock_reaches_max() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    clock = Clock(
        campaign_id=campaign.id,
        label="Citadel suspicion",
        clock_type=ClockType.THREAT,
        current_value=3,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    provider = FakeProvider(
        NarrationResponse(
            narrative="The Greys close in.",
            player_safe_summary="Tension rises.",
            consequences=Consequences(
                clock_ticks=[ClockTick(label="Citadel suspicion", delta=1)],
            ),
        )
    )

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Look over your shoulder.",
        narration_provider=provider,
    )

    assert "Citadel suspicion" in result.clocks_fired


def test_turn_engine_clocks_fired_empty_when_clock_does_not_reach_max() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    clock = Clock(
        campaign_id=campaign.id,
        label="Citadel suspicion",
        clock_type=ClockType.THREAT,
        current_value=1,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    provider = FakeProvider(
        NarrationResponse(
            narrative="Nothing happens.",
            player_safe_summary="Quiet.",
            consequences=Consequences(
                clock_ticks=[ClockTick(label="Citadel suspicion", delta=1)],
            ),
        )
    )

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Wait.",
        narration_provider=provider,
    )

    assert result.clocks_fired == []


def test_turn_engine_location_change_updates_campaign_and_result() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    provider = FakeProvider(
        NarrationResponse(
            narrative="Davan slips through the hatch into the Melt.",
            player_safe_summary="Davan moved to the Melt.",
            consequences=Consequences(
                location_change=LocationChange(new_location_label="The Melt"),
            ),
        )
    )

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Go to the Melt.",
        narration_provider=provider,
    )
    session.commit()

    assert result.location_changed_to == "The Melt"
    assert campaign.current_location_label == "The Melt"


def test_turn_engine_location_unchanged_when_no_location_consequence() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    original_location = campaign.current_location_label

    provider = FakeProvider(
        NarrationResponse(
            narrative="Quiet.",
            player_safe_summary="Nothing moved.",
            consequences=Consequences(),
        )
    )

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Stay put.",
        narration_provider=provider,
    )

    assert result.location_changed_to is None
    assert campaign.current_location_label == original_location


def test_turn_engine_skips_location_change_when_canon_guard_fails() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    original_location = campaign.current_location_label

    provider = FakeProvider(
        NarrationResponse(
            narrative="Darrow steps from the shadows.",
            player_safe_summary="A figure appears.",
            consequences=Consequences(
                location_change=LocationChange(new_location_label="The Melt"),
            ),
        )
    )

    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="Watch.",
        narration_provider=provider,
    )

    assert result.canon_guard_passed is False
    assert result.location_changed_to is None
    assert campaign.current_location_label == original_location
