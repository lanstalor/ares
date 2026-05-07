import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.enums import ConditionType, CONDITION_METADATA
from app.models.base import Base
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.conditions import Condition


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


def test_condition_type_enum_has_all_persistent_conditions():
    """ConditionType enum contains all persistent condition types."""
    persistent_conditions = {
        ConditionType.BLEEDING,
        ConditionType.POISONED,
        ConditionType.IDENT_FLAGGED,
        ConditionType.WOUNDED,
        ConditionType.EXHAUSTED,
    }
    assert len(persistent_conditions) == 5


def test_condition_type_enum_has_all_ephemeral_conditions():
    """ConditionType enum contains all ephemeral condition types."""
    ephemeral_conditions = {
        ConditionType.STUNNED,
        ConditionType.DISARMED,
        ConditionType.PRONE,
        ConditionType.PANICKED,
    }
    assert len(ephemeral_conditions) == 4


def test_condition_type_enum_has_nine_total_conditions():
    """ConditionType enum has exactly 9 condition types."""
    all_conditions = [c for c in ConditionType]
    assert len(all_conditions) == 9


def test_condition_metadata_exists():
    """CONDITION_METADATA constant is defined."""
    assert CONDITION_METADATA is not None
    assert isinstance(CONDITION_METADATA, dict)


def test_condition_metadata_has_all_condition_types():
    """CONDITION_METADATA has entries for all condition types."""
    for condition in ConditionType:
        assert condition.value in CONDITION_METADATA, f"Missing metadata for {condition.value}"


def test_condition_metadata_structure():
    """Each CONDITION_METADATA entry has required keys."""
    required_keys = {"persistence", "visibility", "base_duration", "effect", "effect_value"}

    for condition_value, metadata in CONDITION_METADATA.items():
        assert isinstance(metadata, dict), f"Metadata for {condition_value} is not a dict"
        assert required_keys.issubset(metadata.keys()), (
            f"Metadata for {condition_value} missing required keys. "
            f"Has: {set(metadata.keys())}, needs: {required_keys}"
        )


def test_condition_metadata_persistence_values():
    """Each condition has persistence set to 'persistent' or 'ephemeral'."""
    valid_persistence = {"persistent", "ephemeral"}

    for condition_value, metadata in CONDITION_METADATA.items():
        persistence = metadata.get("persistence")
        assert persistence in valid_persistence, (
            f"Condition {condition_value} has invalid persistence '{persistence}'. "
            f"Must be one of {valid_persistence}"
        )


def test_condition_metadata_visibility_values():
    """Each condition has visibility set to 'player_facing' or 'gm_only'."""
    valid_visibility = {"player_facing", "gm_only"}

    for condition_value, metadata in CONDITION_METADATA.items():
        visibility = metadata.get("visibility")
        assert visibility in valid_visibility, (
            f"Condition {condition_value} has invalid visibility '{visibility}'. "
            f"Must be one of {valid_visibility}"
        )


def test_condition_metadata_base_duration_is_int():
    """Each condition has base_duration as a positive integer."""
    for condition_value, metadata in CONDITION_METADATA.items():
        duration = metadata.get("base_duration")
        assert isinstance(duration, int), (
            f"Condition {condition_value} has non-int base_duration: {duration}"
        )
        assert duration > 0, (
            f"Condition {condition_value} has non-positive base_duration: {duration}"
        )


def test_condition_metadata_effect_is_string():
    """Each condition has effect as a string."""
    for condition_value, metadata in CONDITION_METADATA.items():
        effect = metadata.get("effect")
        assert isinstance(effect, str), (
            f"Condition {condition_value} has non-string effect: {effect}"
        )
        assert len(effect) > 0, (
            f"Condition {condition_value} has empty effect"
        )


def test_condition_metadata_effect_value():
    """Each condition has effect_value as int or string."""
    for condition_value, metadata in CONDITION_METADATA.items():
        effect_value = metadata.get("effect_value")
        assert isinstance(effect_value, (int, str)), (
            f"Condition {condition_value} has invalid effect_value type: {type(effect_value)}"
        )


def test_persistent_conditions_have_correct_persistence_type():
    """All persistent conditions are marked as persistent in metadata."""
    persistent_condition_values = {
        ConditionType.BLEEDING.value,
        ConditionType.POISONED.value,
        ConditionType.IDENT_FLAGGED.value,
        ConditionType.WOUNDED.value,
        ConditionType.EXHAUSTED.value,
    }

    for condition_value in persistent_condition_values:
        metadata = CONDITION_METADATA[condition_value]
        assert metadata["persistence"] == "persistent", (
            f"Condition {condition_value} should be marked persistent"
        )


def test_ephemeral_conditions_have_correct_persistence_type():
    """All ephemeral conditions are marked as ephemeral in metadata."""
    ephemeral_condition_values = {
        ConditionType.STUNNED.value,
        ConditionType.DISARMED.value,
        ConditionType.PRONE.value,
        ConditionType.PANICKED.value,
    }

    for condition_value in ephemeral_condition_values:
        metadata = CONDITION_METADATA[condition_value]
        assert metadata["persistence"] == "ephemeral", (
            f"Condition {condition_value} should be marked ephemeral"
        )


# --- Model Creation Tests (TDD) ---


def test_condition_model_can_be_created(session, campaign, character):
    """Condition model can be created with required fields."""
    condition = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
        duration_remaining=3,
        persistence="persistent",
        source="Combat wound",
    )
    session.add(condition)
    session.commit()

    stored = session.query(Condition).filter_by(id=condition.id).first()
    assert stored is not None
    assert stored.campaign_id == campaign.id
    assert stored.character_id == character.id
    assert stored.condition_type == ConditionType.BLEEDING.value
    assert stored.duration_remaining == 3
    assert stored.persistence == "persistent"
    assert stored.source == "Combat wound"


def test_condition_has_timestamps(session, campaign, character):
    """Condition has created_at and updated_at timestamps."""
    condition = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.STUNNED.value,
        duration_remaining=1,
        persistence="ephemeral",
    )
    session.add(condition)
    session.commit()

    stored = session.query(Condition).filter_by(id=condition.id).first()
    assert stored.created_at is not None
    assert stored.updated_at is not None


def test_condition_unique_constraint_prevents_duplicates(session, campaign, character):
    """Unique constraint prevents duplicate (campaign_id, character_id, condition_type)."""
    condition1 = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
        duration_remaining=3,
        persistence="persistent",
    )
    session.add(condition1)
    session.commit()

    # Try to add a duplicate
    condition2 = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
        duration_remaining=2,
        persistence="persistent",
    )
    session.add(condition2)

    # Should raise IntegrityError
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        session.commit()


def test_condition_relationships(session, campaign, character):
    """Condition relationships to Campaign and Character work correctly."""
    condition = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.EXHAUSTED.value,
        duration_remaining=2,
        persistence="persistent",
    )
    session.add(condition)
    session.commit()

    # Load from DB and verify relationships
    stored = session.query(Condition).filter_by(id=condition.id).first()
    assert stored.campaign.id == campaign.id
    assert stored.campaign.name == "Test Campaign"
    assert stored.character.id == character.id
    assert stored.character.name == "Davan"


def test_campaign_has_conditions_relationship(session, campaign, character):
    """Campaign can access its conditions through relationship."""
    condition1 = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.BLEEDING.value,
        duration_remaining=3,
        persistence="persistent",
    )
    condition2 = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.STUNNED.value,
        duration_remaining=1,
        persistence="ephemeral",
    )
    session.add_all([condition1, condition2])
    session.commit()

    # Query campaign and verify conditions
    stored_campaign = session.query(Campaign).filter_by(id=campaign.id).first()
    assert len(stored_campaign.conditions) == 2
    assert any(c.condition_type == ConditionType.BLEEDING.value for c in stored_campaign.conditions)
    assert any(c.condition_type == ConditionType.STUNNED.value for c in stored_campaign.conditions)


def test_character_has_conditions_relationship(session, campaign, character):
    """Character can access its conditions through relationship."""
    condition1 = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.WOUNDED.value,
        duration_remaining=2,
        persistence="persistent",
    )
    condition2 = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.PRONE.value,
        duration_remaining=1,
        persistence="ephemeral",
    )
    session.add_all([condition1, condition2])
    session.commit()

    # Query character and verify conditions
    stored_character = session.query(Character).filter_by(id=character.id).first()
    assert len(stored_character.conditions) == 2
    assert any(c.condition_type == ConditionType.WOUNDED.value for c in stored_character.conditions)
    assert any(c.condition_type == ConditionType.PRONE.value for c in stored_character.conditions)


def test_condition_cascade_delete_on_campaign(session, campaign, character):
    """Deleting campaign cascades to delete conditions."""
    condition = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.POISONED.value,
        duration_remaining=3,
        persistence="persistent",
    )
    session.add(condition)
    session.commit()

    condition_id = condition.id

    # Delete campaign
    session.delete(campaign)
    session.commit()

    # Condition should be deleted
    stored = session.query(Condition).filter_by(id=condition_id).first()
    assert stored is None


def test_condition_cascade_delete_on_character(session, campaign, character):
    """Deleting character cascades to delete conditions."""
    condition = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.IDENT_FLAGGED.value,
        duration_remaining=5,
        persistence="persistent",
    )
    session.add(condition)
    session.commit()

    condition_id = condition.id

    # Delete character
    session.delete(character)
    session.commit()

    # Condition should be deleted
    stored = session.query(Condition).filter_by(id=condition_id).first()
    assert stored is None


def test_condition_source_nullable(session, campaign, character):
    """Condition source field is optional/nullable."""
    condition = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=ConditionType.DISARMED.value,
        duration_remaining=1,
        persistence="ephemeral",
        source=None,
    )
    session.add(condition)
    session.commit()

    stored = session.query(Condition).filter_by(id=condition.id).first()
    assert stored.source is None
