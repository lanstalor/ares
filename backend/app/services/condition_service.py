"""
Condition Service

Handles condition operations: creating/refreshing conditions, querying them, and preparing them for display.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ConditionType, CONDITION_METADATA
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.conditions import Condition


# Color map for frontend rendering
COLOR_MAP = {
    ConditionType.BLEEDING.value: "#cc3333",
    ConditionType.POISONED.value: "#663399",
    ConditionType.IDENT_FLAGGED.value: "#ff6600",
    ConditionType.WOUNDED.value: "#dd6633",
    ConditionType.EXHAUSTED.value: "#999999",
    ConditionType.STUNNED.value: "#ffff00",
    ConditionType.DISARMED.value: "#ff9999",
    ConditionType.PRONE.value: "#cc9966",
    ConditionType.PANICKED.value: "#ff33ff",
}


def add_or_refresh_condition(
    session: Session,
    campaign: Campaign,
    character: Character,
    condition_type: str,
    duration: int,
    source: str | None = None,
    metadata: dict | None = None,
) -> Condition:
    """
    Create a new condition or refresh an existing one.

    If a condition with the same (campaign_id, character_id, condition_type) exists,
    update its duration. Otherwise, create a new condition.

    Args:
        session: SQLAlchemy session
        campaign: Campaign model instance
        character: Character model instance
        condition_type: Type of condition (must be a valid ConditionType)
        duration: Duration in turns
        source: Optional source description (e.g., "Combat wound")
        metadata: Optional metadata dict (unused for now, reserved for expansion)

    Returns:
        Condition object (created or refreshed)

    Raises:
        ValueError: If condition_type is invalid or character/campaign not found
    """
    # Validate condition type
    valid_types = {ct.value for ct in ConditionType}
    if condition_type not in valid_types:
        raise ValueError(f"Invalid condition_type '{condition_type}'. Valid types: {valid_types}")

    # Verify character exists and belongs to campaign
    if character.campaign_id != campaign.id:
        raise ValueError(
            f"Character {character.id} does not belong to campaign {campaign.id}"
        )

    # Query for existing condition with unique key
    existing = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign.id,
            Condition.character_id == character.id,
            Condition.condition_type == condition_type,
        )
    )

    if existing is not None:
        # Refresh: update duration and source if provided
        existing.duration_remaining = duration
        if source is not None:
            existing.source = source
        session.commit()
        return existing

    # Create new condition
    metadata_dict = metadata or {}
    persistence = CONDITION_METADATA[condition_type]["persistence"]

    new_condition = Condition(
        campaign_id=campaign.id,
        character_id=character.id,
        condition_type=condition_type,
        duration_remaining=duration,
        persistence=persistence,
        source=source,
    )
    session.add(new_condition)
    session.commit()
    return new_condition


def get_active_conditions(
    session: Session,
    campaign_id: str,
    character_id: str,
) -> list[Condition]:
    """
    Retrieve all active conditions for a character in a campaign.

    Args:
        session: SQLAlchemy session
        campaign_id: Campaign ID
        character_id: Character ID

    Returns:
        List of Condition objects. Empty list if none found.
    """
    conditions = session.scalars(
        select(Condition).where(
            Condition.campaign_id == campaign_id,
            Condition.character_id == character_id,
        )
    ).all()
    return conditions


def remove_condition(
    session: Session,
    campaign_id: str,
    character_id: str,
    condition_type: str,
) -> Condition | None:
    """
    Remove a condition by unique key (campaign_id, character_id, condition_type).

    Args:
        session: SQLAlchemy session
        campaign_id: Campaign ID
        character_id: Character ID
        condition_type: Condition type

    Returns:
        The removed Condition if found, None if not found.

    Side effects:
        Commits the transaction if condition was found and deleted.
    """
    condition = session.scalar(
        select(Condition).where(
            Condition.campaign_id == campaign_id,
            Condition.character_id == character_id,
            Condition.condition_type == condition_type,
        )
    )

    if condition is not None:
        session.delete(condition)
        session.commit()

    return condition


def get_condition_display(condition: Condition) -> dict:
    """
    Prepare a condition for frontend display.

    Returns a dict with all necessary fields for rendering:
    - id: Condition ID
    - condition_type: Type of condition
    - duration_remaining: Turns remaining
    - persistence: "persistent" or "ephemeral"
    - visibility: "player_facing" or "gm_only" from metadata
    - color: Hex color code for frontend rendering

    Args:
        condition: Condition model instance

    Returns:
        Dict with condition display data
    """
    metadata = CONDITION_METADATA.get(condition.condition_type, {})
    color = COLOR_MAP.get(condition.condition_type, "#cccccc")

    return {
        "id": condition.id,
        "condition_type": condition.condition_type,
        "duration_remaining": condition.duration_remaining,
        "persistence": condition.persistence,
        "visibility": metadata.get("visibility", "gm_only"),
        "color": color,
    }
