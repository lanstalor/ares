from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums import ClockType, ConditionType, SecretStatus, Visibility
from app.models.base import Base
from app.models.campaign import Campaign, Clock, Objective
from app.models.character import Character
from app.models.conditions import Condition
from app.models.memory import Memory, Secret
from app.services.consequence_applier import (
    ClockTick,
    ConditionUpdate,
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


# Condition consequence tests


def _make_character(session: Session, campaign: Campaign) -> Character:
    """Helper to create a test character."""
    character = Character(campaign_id=campaign.id, name="Davan of Tharsis")
    session.add(character)
    session.flush()
    return character


def test_apply_consequences_creates_new_condition() -> None:
    """Test that condition consequences create new Condition records."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)

    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="bleeding", duration=3, source="combat_wound")
            ]
        ),
    )
    session.commit()

    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
            Condition.condition_type == "bleeding",
        )
    )
    assert condition is not None
    assert condition.duration_remaining == 3
    assert condition.source == "combat_wound"
    assert condition.persistence == "persistent"


def test_apply_consequences_refreshes_existing_condition() -> None:
    """Test that condition consequences refresh existing conditions."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)

    # Create initial condition
    existing = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type="bleeding",
        duration_remaining=1,
        persistence="persistent",
        source="initial_wound",
    )
    session.add(existing)
    session.commit()

    # Apply consequence to refresh it
    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="bleeding", duration=5, source="additional_wound")
            ]
        ),
    )
    session.commit()

    # Verify condition was refreshed
    refreshed = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
            Condition.condition_type == "bleeding",
        )
    )
    assert refreshed is not None
    assert refreshed.id == existing.id  # Same condition record
    assert refreshed.duration_remaining == 5
    assert refreshed.source == "additional_wound"


def test_apply_consequences_uses_base_duration_when_not_specified() -> None:
    """Test that condition consequences use base_duration from metadata when duration is None."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)

    # "bleeding" has base_duration of 3 in metadata
    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="bleeding", duration=None)
            ]
        ),
    )
    session.commit()

    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
            Condition.condition_type == "bleeding",
        )
    )
    assert condition is not None
    assert condition.duration_remaining == 3  # base_duration from metadata


def test_apply_consequences_with_invalid_condition_type() -> None:
    """Test that invalid condition_type is logged and ignored."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)

    # This should not raise an exception, just log an error
    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="invalid_condition_type", duration=3)
            ]
        ),
    )
    session.commit()

    # Verify no condition was created
    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
        )
    )
    assert condition is None


def test_apply_consequences_with_no_character_ignores_conditions() -> None:
    """Test that condition consequences are ignored if no character exists."""
    session = _make_session()
    campaign = _make_campaign(session)
    # Don't create a character

    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="bleeding", duration=3)
            ]
        ),
    )
    session.commit()

    # Verify no condition was created (since there's no character)
    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
        )
    )
    assert condition is None


def test_apply_consequences_multiple_conditions() -> None:
    """Test applying multiple condition consequences in a single call."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)

    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="bleeding", duration=3),
                ConditionUpdate(condition_type="poisoned", duration=2),
                ConditionUpdate(condition_type="stunned", duration=1),
            ]
        ),
    )
    session.commit()

    conditions = list(
        session.scalars(
            select(Condition).where(
                Condition.campaign_id == campaign.id,
                Condition.character_id == character.id,
            )
        )
    )
    assert len(conditions) == 3

    by_type = {c.condition_type: c for c in conditions}
    assert by_type["bleeding"].duration_remaining == 3
    assert by_type["poisoned"].duration_remaining == 2
    assert by_type["stunned"].duration_remaining == 1


def test_apply_consequences_ephemeral_condition() -> None:
    """Test that ephemeral conditions are created with correct persistence."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)

    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="stunned", duration=1)
            ]
        ),
    )
    session.commit()

    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
            Condition.condition_type == "stunned",
        )
    )
    assert condition is not None
    assert condition.persistence == "ephemeral"
    assert condition.duration_remaining == 1


def test_apply_consequences_condition_with_no_source() -> None:
    """Test that conditions created without source use 'system' as default."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)

    apply_consequences(
        session,
        campaign,
        Consequences(
            condition_updates=[
                ConditionUpdate(condition_type="bleeding", duration=3, source=None)
            ]
        ),
    )
    session.commit()

    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
            Condition.condition_type == "bleeding",
        )
    )
    assert condition is not None
    assert condition.source == "system"


def test_apply_consequences_mixed_consequences_with_conditions() -> None:
    """Test that conditions work alongside other consequence types."""
    session = _make_session()
    campaign = _make_campaign(session)
    character = _make_character(session, campaign)
    clock = Clock(
        campaign_id=campaign.id,
        label="Combat tension",
        clock_type=ClockType.TENSION,
        current_value=1,
        max_value=4,
    )
    session.add(clock)
    session.commit()

    apply_consequences(
        session,
        campaign,
        Consequences(
            clock_ticks=[ClockTick(label="Combat tension", delta=1)],
            condition_updates=[
                ConditionUpdate(condition_type="wounded", duration=2),
            ],
        ),
    )
    session.commit()

    # Verify clock was ticked
    refreshed_clock = session.scalar(select(Clock).where(Clock.id == clock.id))
    assert refreshed_clock.current_value == 2

    # Verify condition was created
    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
            Condition.condition_type == "wounded",
        )
    )
    assert condition is not None
    assert condition.duration_remaining == 2
