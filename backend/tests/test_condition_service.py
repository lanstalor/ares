"""
Tests for Condition Service

Tests all CRUD operations and display functions for conditions.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.enums import ConditionType, CONDITION_METADATA
from app.models.base import Base
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.conditions import Condition
from app.services.condition_service import (
    COLOR_MAP,
    add_or_refresh_condition,
    get_active_conditions,
    get_condition_display,
    remove_condition,
)


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


@pytest.fixture
def session():
    db = _make_session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def campaign(session):
    campaign = Campaign(name="Test Campaign")
    session.add(campaign)
    session.commit()
    return campaign


@pytest.fixture
def character(session, campaign):
    char = Character(campaign_id=campaign.id, name="Davan")
    session.add(char)
    session.commit()
    return char


# --- Test add_or_refresh_condition ---


def test_add_or_refresh_condition_creates_new(session, campaign, character):
    """add_or_refresh_condition creates a new condition."""
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
        source="Combat wound",
    )

    assert condition.id is not None
    assert condition.campaign_id == campaign.id
    assert condition.character_id == character.id
    assert condition.condition_type == ConditionType.BLEEDING.value
    assert condition.duration_remaining == 3
    assert condition.persistence == "persistent"
    assert condition.source == "Combat wound"


def test_add_or_refresh_condition_refreshes_existing(session, campaign, character):
    """add_or_refresh_condition updates duration of existing condition."""
    # Create initial condition
    condition1 = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
        source="Combat wound",
    )
    id1 = condition1.id

    # Refresh with new duration
    condition2 = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=5,
        source="Updated wound",
    )

    # Should be the same condition, just updated
    assert condition2.id == id1
    assert condition2.duration_remaining == 5
    assert condition2.source == "Updated wound"

    # Verify only one record in DB
    all_conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(all_conditions) == 1


def test_add_or_refresh_condition_with_no_source(session, campaign, character):
    """add_or_refresh_condition works with source=None."""
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.STUNNED.value,
        duration=1,
        source=None,
    )

    assert condition.source is None
    assert condition.condition_type == ConditionType.STUNNED.value


def test_add_or_refresh_condition_sets_persistence_from_metadata(session, campaign, character):
    """add_or_refresh_condition sets persistence correctly based on condition type."""
    # Test persistent condition
    persistent = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.WOUNDED.value,
        duration=2,
    )
    assert persistent.persistence == "persistent"

    # Test ephemeral condition
    ephemeral = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.PRONE.value,
        duration=1,
    )
    assert ephemeral.persistence == "ephemeral"


def test_add_or_refresh_condition_rejects_invalid_type(session, campaign, character):
    """add_or_refresh_condition raises ValueError for invalid condition type."""
    with pytest.raises(ValueError, match="Invalid condition_type"):
        add_or_refresh_condition(
            session=session,
            campaign=campaign,
            character=character,
            condition_type="nonexistent_condition",
            duration=1,
        )


def test_add_or_refresh_condition_rejects_mismatched_character(session, campaign, character):
    """add_or_refresh_condition raises ValueError if character doesn't belong to campaign."""
    other_campaign = Campaign(name="Other Campaign")
    session.add(other_campaign)
    session.commit()

    # Character belongs to campaign, not other_campaign
    with pytest.raises(ValueError, match="does not belong to campaign"):
        add_or_refresh_condition(
            session=session,
            campaign=other_campaign,
            character=character,
            condition_type=ConditionType.BLEEDING.value,
            duration=1,
        )


def test_add_or_refresh_condition_allows_metadata_dict(session, campaign, character):
    """add_or_refresh_condition accepts metadata dict (reserved for expansion)."""
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.POISONED.value,
        duration=2,
        metadata={"custom_field": "custom_value"},
    )

    assert condition.id is not None


# --- Test get_active_conditions ---


def test_get_active_conditions_returns_empty_list_by_default(session, campaign, character):
    """get_active_conditions returns empty list when no conditions exist."""
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert conditions == []


def test_get_active_conditions_returns_all_conditions(session, campaign, character):
    """get_active_conditions returns all conditions for a character."""
    # Add three conditions
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
    )
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.STUNNED.value,
        duration=1,
    )
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.EXHAUSTED.value,
        duration=2,
    )

    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 3
    types = {c.condition_type for c in conditions}
    assert types == {
        ConditionType.BLEEDING.value,
        ConditionType.STUNNED.value,
        ConditionType.EXHAUSTED.value,
    }


def test_get_active_conditions_filters_by_campaign(session, campaign, character):
    """get_active_conditions only returns conditions for the specified campaign."""
    # Add condition to campaign 1
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
    )

    # Create another campaign and character
    other_campaign = Campaign(name="Other Campaign")
    session.add(other_campaign)
    session.commit()

    other_character = Character(campaign_id=other_campaign.id, name="Other")
    session.add(other_character)
    session.commit()

    # Add condition to other campaign
    add_or_refresh_condition(
        session=session,
        campaign=other_campaign,
        character=other_character,
        condition_type=ConditionType.WOUNDED.value,
        duration=2,
    )

    # Query campaign 1 should only return its condition
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 1
    assert conditions[0].condition_type == ConditionType.BLEEDING.value


def test_get_active_conditions_filters_by_character(session, campaign):
    """get_active_conditions only returns conditions for the specified character."""
    char1 = Character(campaign_id=campaign.id, name="Davan")
    char2 = Character(campaign_id=campaign.id, name="Other")
    session.add_all([char1, char2])
    session.commit()

    # Add condition to char1
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=char1,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
    )

    # Add condition to char2
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=char2,
        condition_type=ConditionType.WOUNDED.value,
        duration=2,
    )

    # Query char1 should only return its condition
    conditions = get_active_conditions(session, campaign.id, char1.id)
    assert len(conditions) == 1
    assert conditions[0].condition_type == ConditionType.BLEEDING.value

    # Query char2 should only return its condition
    conditions = get_active_conditions(session, campaign.id, char2.id)
    assert len(conditions) == 1
    assert conditions[0].condition_type == ConditionType.WOUNDED.value


# --- Test remove_condition ---


def test_remove_condition_removes_existing(session, campaign, character):
    """remove_condition deletes an existing condition."""
    # Create a condition
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
    )

    # Verify it exists
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 1

    # Remove it
    removed = remove_condition(
        session=session,
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
    )

    # Should return the removed condition
    assert removed is not None
    assert removed.condition_type == ConditionType.BLEEDING.value

    # Should be gone from DB
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 0


def test_remove_condition_handles_missing_gracefully(session, campaign, character):
    """remove_condition returns None if condition doesn't exist."""
    removed = remove_condition(
        session=session,
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
    )

    assert removed is None


def test_remove_condition_only_removes_specified_condition(session, campaign, character):
    """remove_condition only removes the condition with matching type."""
    # Create multiple conditions
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
    )
    add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.STUNNED.value,
        duration=1,
    )

    # Remove bleeding
    remove_condition(
        session=session,
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
    )

    # Only stunned should remain
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 1
    assert conditions[0].condition_type == ConditionType.STUNNED.value


# --- Test get_condition_display ---


def test_get_condition_display_returns_correct_structure(session, campaign, character):
    """get_condition_display returns dict with all required fields."""
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
    )

    display = get_condition_display(condition)

    # Check all required keys are present
    assert "id" in display
    assert "condition_type" in display
    assert "duration_remaining" in display
    assert "persistence" in display
    assert "visibility" in display
    assert "color" in display


def test_get_condition_display_correct_values(session, campaign, character):
    """get_condition_display returns correct values for all fields."""
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=3,
    )

    display = get_condition_display(condition)

    assert display["id"] == condition.id
    assert display["condition_type"] == ConditionType.BLEEDING.value
    assert display["duration_remaining"] == 3
    assert display["persistence"] == "persistent"
    assert display["visibility"] == "player_facing"
    assert display["color"] == "#cc3333"


def test_get_condition_display_uses_color_map(session, campaign, character):
    """get_condition_display uses COLOR_MAP for colors."""
    # Test each condition type
    for condition_type in ConditionType:
        condition = add_or_refresh_condition(
            session=session,
            campaign=campaign,
            character=character,
            condition_type=condition_type.value,
            duration=1,
        )

        display = get_condition_display(condition)

        expected_color = COLOR_MAP.get(condition_type.value, "#cccccc")
        assert display["color"] == expected_color


def test_get_condition_display_visibility_from_metadata(session, campaign, character):
    """get_condition_display gets visibility from CONDITION_METADATA."""
    # Test a player_facing condition
    player_facing = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.BLEEDING.value,
        duration=1,
    )

    display = get_condition_display(player_facing)
    assert display["visibility"] == "player_facing"

    # Test a gm_only condition
    gm_only = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.IDENT_FLAGGED.value,
        duration=1,
    )

    display = get_condition_display(gm_only)
    assert display["visibility"] == "gm_only"


def test_get_condition_display_all_condition_types(session, campaign, character):
    """get_condition_display works for all condition types."""
    for condition_type in ConditionType:
        condition = add_or_refresh_condition(
            session=session,
            campaign=campaign,
            character=character,
            condition_type=condition_type.value,
            duration=1,
        )

        display = get_condition_display(condition)

        # Verify all fields are present and have reasonable values
        assert display["id"] is not None
        assert display["condition_type"] == condition_type.value
        assert display["duration_remaining"] >= 0
        assert display["persistence"] in ["persistent", "ephemeral"]
        assert display["visibility"] in ["player_facing", "gm_only"]
        assert display["color"].startswith("#")


def test_get_condition_display_with_zero_duration(session, campaign, character):
    """get_condition_display handles conditions with zero duration."""
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.STUNNED.value,
        duration=0,
    )

    display = get_condition_display(condition)
    assert display["duration_remaining"] == 0


# --- Integration Tests ---


def test_condition_lifecycle(session, campaign, character):
    """Test complete lifecycle: create, refresh, query, display, remove."""
    # Create
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.WOUNDED.value,
        duration=2,
        source="Arrow wound",
    )
    assert condition.duration_remaining == 2

    # Query
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 1

    # Refresh
    condition = add_or_refresh_condition(
        session=session,
        campaign=campaign,
        character=character,
        condition_type=ConditionType.WOUNDED.value,
        duration=1,
        source="Healed slightly",
    )
    assert condition.duration_remaining == 1

    # Display
    display = get_condition_display(condition)
    assert display["duration_remaining"] == 1

    # Remove
    removed = remove_condition(
        session=session,
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.WOUNDED.value,
    )
    assert removed is not None

    # Verify removed
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 0


def test_multiple_conditions_on_character(session, campaign, character):
    """Test character with multiple simultaneous conditions."""
    # Add multiple conditions
    conditions_to_add = [
        (ConditionType.BLEEDING.value, 3),
        (ConditionType.STUNNED.value, 1),
        (ConditionType.EXHAUSTED.value, 2),
        (ConditionType.DISARMED.value, 1),
    ]

    for cond_type, duration in conditions_to_add:
        add_or_refresh_condition(
            session=session,
            campaign=campaign,
            character=character,
            condition_type=cond_type,
            duration=duration,
        )

    # Verify all exist
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 4

    # Verify display for each
    displays = [get_condition_display(c) for c in conditions]
    assert len(displays) == 4
    assert all("color" in d for d in displays)

    # Remove one
    remove_condition(
        session=session,
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
    )

    # Verify remaining
    conditions = get_active_conditions(session, campaign.id, character.id)
    assert len(conditions) == 3
