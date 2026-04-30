from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums import ClockType, SecretStatus, Visibility
from app.models.base import Base
from app.models.campaign import Campaign, Clock, Objective
from app.models.memory import Memory, Secret
from app.services.consequence_applier import (
    ClockTick,
    Consequences,
    LocationChange,
    MemoryDraft,
    ObjectiveUpdate,
    SecretStatusChange,
    apply_consequences,
)


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def _make_campaign(session: Session) -> Campaign:
    campaign = Campaign(name="Test Cell", current_date_pce=728)
    session.add(campaign)
    session.flush()
    return campaign


def test_apply_consequences_advances_clock_by_label() -> None:
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

    apply_consequences(
        session,
        campaign,
        Consequences(
            clock_ticks=[ClockTick(label="Citadel suspicion", delta=2)],
        ),
    )
    session.commit()

    refreshed = session.scalar(select(Clock).where(Clock.id == clock.id))
    assert refreshed.current_value == 3


def test_apply_consequences_clamps_clock_to_max() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    clock = Clock(
        campaign_id=campaign.id,
        label="Reveal: Vex's deal",
        clock_type=ClockType.REVEAL,
        current_value=3,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    apply_consequences(
        session,
        campaign,
        Consequences(
            clock_ticks=[ClockTick(label="Reveal: Vex's deal", delta=10)],
        ),
    )
    session.commit()

    refreshed = session.scalar(select(Clock).where(Clock.id == clock.id))
    assert refreshed.current_value == 4


def test_apply_consequences_transitions_secret_status() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    secret = Secret(
        campaign_id=campaign.id,
        label="NPC: Vex / Hidden agenda",
        content="Vex is informing the Greys.",
        status=SecretStatus.DORMANT,
    )
    session.add(secret)
    session.commit()

    apply_consequences(
        session,
        campaign,
        Consequences(
            secret_status_changes=[
                SecretStatusChange(label="NPC: Vex / Hidden agenda", new_status=SecretStatus.ELIGIBLE)
            ],
        ),
    )
    session.commit()

    refreshed = session.scalar(select(Secret).where(Secret.id == secret.id))
    assert refreshed.status == SecretStatus.ELIGIBLE


def test_apply_consequences_persists_new_memories() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    apply_consequences(
        session,
        campaign,
        Consequences(
            new_memories=[
                MemoryDraft(
                    content="Davan saw a Grey lieutenant near the Melt.",
                    visibility=Visibility.PLAYER_FACING,
                ),
                MemoryDraft(
                    content="The Grey lieutenant was tailing Vex.",
                    visibility=Visibility.GM_ONLY,
                ),
            ],
        ),
    )
    session.commit()

    rows = list(session.scalars(select(Memory).where(Memory.campaign_id == campaign.id)))
    assert len(rows) == 2
    by_visibility = {row.visibility: row for row in rows}
    assert by_visibility[Visibility.PLAYER_FACING].content.startswith("Davan saw")
    assert by_visibility[Visibility.GM_ONLY].content.startswith("The Grey")


def test_apply_consequences_ignores_unknown_clock_label() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    apply_consequences(
        session,
        campaign,
        Consequences(
            clock_ticks=[ClockTick(label="Nonexistent clock", delta=1)],
        ),
    )
    session.commit()

    assert session.scalar(select(Clock)) is None


def test_apply_consequences_fires_clock_when_reaching_max() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    clock = Clock(
        campaign_id=campaign.id,
        label="Reveal: Vex's deal",
        clock_type=ClockType.REVEAL,
        current_value=3,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    result = apply_consequences(
        session,
        campaign,
        Consequences(clock_ticks=[ClockTick(label="Reveal: Vex's deal", delta=1)]),
    )
    session.commit()

    assert result.clocks_fired == ["Reveal: Vex's deal"]


def test_apply_consequences_does_not_refire_clock_already_at_max() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    clock = Clock(
        campaign_id=campaign.id,
        label="Citadel suspicion",
        clock_type=ClockType.THREAT,
        current_value=4,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    result = apply_consequences(
        session,
        campaign,
        Consequences(clock_ticks=[ClockTick(label="Citadel suspicion", delta=1)]),
    )

    assert result.clocks_fired == []


def test_apply_consequences_returns_empty_fired_list_when_no_clocks_tick() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    result = apply_consequences(session, campaign, Consequences())

    assert result.clocks_fired == []
    assert result.location_changed_to is None


def test_apply_consequences_updates_campaign_location() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    result = apply_consequences(
        session,
        campaign,
        Consequences(location_change=LocationChange(new_location_label="The Melt")),
    )
    session.commit()

    assert campaign.current_location_label == "The Melt"
    assert result.location_changed_to == "The Melt"


def test_apply_consequences_no_location_change_returns_none() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    result = apply_consequences(session, campaign, Consequences())

    assert result.location_changed_to is None


def test_apply_consequences_completes_active_objective() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    obj = Objective(
        campaign_id=campaign.id,
        title="Check the Melt before shift",
        is_active=True,
    )
    session.add(obj)
    session.commit()

    apply_consequences(
        session,
        campaign,
        Consequences(
            objective_updates=[ObjectiveUpdate(title="Check the Melt before shift", action="complete")]
        ),
    )
    session.commit()

    refreshed = session.scalar(select(Objective).where(Objective.id == obj.id))
    assert refreshed.is_active is False


def test_apply_consequences_add_creates_new_objective() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    apply_consequences(
        session,
        campaign,
        Consequences(
            objective_updates=[
                ObjectiveUpdate(
                    title="Find Vex's handler",
                    action="add",
                    description="Track who Vex is reporting to.",
                )
            ]
        ),
    )
    session.commit()

    obj = session.scalar(
        select(Objective).where(
            Objective.campaign_id == campaign.id,
            Objective.title == "Find Vex's handler",
        )
    )
    assert obj is not None
    assert obj.is_active is True
    assert obj.description == "Track who Vex is reporting to."


def test_apply_consequences_complete_ignores_unknown_objective() -> None:
    """Completing a non-existent objective should not raise."""
    session = _make_session()
    campaign = _make_campaign(session)

    apply_consequences(
        session,
        campaign,
        Consequences(
            objective_updates=[ObjectiveUpdate(title="Nonexistent objective", action="complete")]
        ),
    )
    session.commit()

    assert session.scalar(select(Objective)) is None


def test_apply_consequences_complete_ignores_already_inactive_objective() -> None:
    """Completing an already-inactive objective should not error."""
    session = _make_session()
    campaign = _make_campaign(session)
    obj = Objective(
        campaign_id=campaign.id,
        title="Old task",
        is_active=False,
    )
    session.add(obj)
    session.commit()

    apply_consequences(
        session,
        campaign,
        Consequences(
            objective_updates=[ObjectiveUpdate(title="Old task", action="complete")]
        ),
    )
    session.commit()

    refreshed = session.scalar(select(Objective).where(Objective.id == obj.id))
    assert refreshed.is_active is False
