from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums import ClockType, SecretStatus, Visibility
from app.models.base import Base
from app.models.campaign import Campaign, Clock
from app.models.memory import Memory, Secret
from app.services.consequence_applier import (
    ClockTick,
    Consequences,
    MemoryDraft,
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
            secret_status_changes=[],
            new_memories=[],
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
            secret_status_changes=[],
            new_memories=[],
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
            clock_ticks=[],
            secret_status_changes=[
                SecretStatusChange(label="NPC: Vex / Hidden agenda", new_status=SecretStatus.ELIGIBLE)
            ],
            new_memories=[],
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
            clock_ticks=[],
            secret_status_changes=[],
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
            secret_status_changes=[],
            new_memories=[],
        ),
    )
    session.commit()

    assert session.scalar(select(Clock)) is None
