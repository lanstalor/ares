"""
NPC Portrait Service

Handles portrait generation for NPCs, including slug generation and prompt building.
"""

import re
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.character import Character


def slugify_npc_name(name: str | None) -> str:
    """
    Convert an NPC name to a URL-safe slug.

    Rules:
    - Convert to lowercase
    - Replace non-alphanumeric characters with dashes
    - Strip leading/trailing dashes
    - Cap at 120 characters
    - Return "unknown-npc" if result is empty

    Args:
        name: The NPC name to slugify, or None

    Returns:
        A URL-safe slug (max 120 chars), or "unknown-npc"
    """
    if not name:
        return "unknown-npc"

    # Convert to lowercase
    slug = name.lower()

    # Replace non-alphanumeric with dashes using regex
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Strip leading/trailing dashes
    slug = slug.strip("-")

    # Cap at 120 characters
    slug = slug[:120]

    # Return "unknown-npc" if result is empty
    if not slug:
        return "unknown-npc"

    return slug


def build_portrait_prompt(session: Session, character: Character) -> str:
    """
    Build a portrait generation prompt for an NPC.

    Includes:
    - Character name
    - Race (if available)
    - Character class/role (if available)
    - Red Rising universe context
    - Current campaign date (PCE)
    - Photorealistic style guidance

    Excludes:
    - Internal notes
    - Hidden state fields

    Args:
        session: SQLAlchemy session (for accessing campaign data)
        character: Character model instance

    Returns:
        A detailed portrait prompt string
    """
    parts = []

    # Character name and role
    name = character.name or "Unknown Character"
    parts.append(f"Generate a portrait of {name}")

    # Add race if available
    if character.race:
        parts.append(f"a {character.race}")

    # Add character class/role if available
    if character.character_class:
        parts.append(f"{character.character_class}")

    # Join the first parts into a sentence
    prompt = " ".join(parts) + "."

    # Get campaign for context
    campaign = session.query(Campaign).filter_by(id=character.campaign_id).first()
    pce_year = campaign.current_date_pce if campaign else 728

    # Add Red Rising universe context
    prompt += f" Red Rising universe, {pce_year} PCE. Photorealistic portrait style."

    return prompt
