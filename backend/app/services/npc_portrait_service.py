"""
NPC Portrait Service

Handles portrait generation for NPCs, including slug generation and prompt building.
"""

import base64
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.portraits import NpcPortrait
from app.services.media_provider import MediaProvider, MediaRequest
from app.services.provider_registry import get_media_provider


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


def get_cached_portrait(
    session: Session,
    campaign_id: str,
    npc_id: str,
) -> NpcPortrait | None:
    """
    Retrieve a cached NPC portrait from the database.

    Args:
        session: SQLAlchemy session
        campaign_id: Campaign ID
        npc_id: NPC character ID

    Returns:
        NpcPortrait if found, None otherwise
    """
    return session.scalar(
        select(NpcPortrait).where(
            NpcPortrait.campaign_id == campaign_id,
            NpcPortrait.npc_id == npc_id,
        )
    )


def cache_portrait_response(
    response,
    slug: str,
    cache_dir: Path | None = None,
) -> str:
    """
    Cache a portrait image to disk and return its URL path.

    Args:
        response: MediaResponse from media provider
        slug: URL-safe slug for the portrait filename
        cache_dir: Directory to cache the portrait PNG. Defaults to frontend/public/portraits

    Returns:
        URL path to the cached portrait image

    Raises:
        ValueError: If response has no usable image payload
    """
    if response.b64_json:
        target_dir = cache_dir or (get_settings().project_root / "frontend" / "public" / "portraits")
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{slug}.png"
        target_path.write_bytes(base64.b64decode(response.b64_json))
        return f"/portraits/{target_path.name}"

    if response.url:
        return response.url

    raise ValueError("Media provider returned no usable portrait payload.")


def ensure_portrait(
    session: Session,
    campaign: Campaign,
    character: Character,
    force: bool = False,
    media_provider: MediaProvider | None = None,
    cache_dir: Path | None = None,
) -> NpcPortrait:
    """
    Ensure a portrait exists for an NPC, generating one if needed.

    If a portrait is cached and force=False, returns the cached portrait.
    Otherwise, generates a new portrait using the media provider.

    Args:
        session: SQLAlchemy session
        campaign: Campaign model instance
        character: Character model instance (the NPC)
        force: If True, regenerate even if cached
        media_provider: MediaProvider instance. Defaults to get_media_provider()
        cache_dir: Directory for caching portraits. Defaults to frontend/public/portraits

    Returns:
        NpcPortrait with status="ready" on success, status="failed" on error

    Side effects:
        - Creates/updates NpcPortrait in database
        - Writes PNG file to cache_dir
        - Commits transaction
    """
    # Check cache first
    cached = get_cached_portrait(session, campaign.id, character.id)
    if cached is not None and cached.status == "ready" and not force:
        return cached

    # Set up provider and paths
    settings = get_settings()
    provider = media_provider or get_media_provider(settings.media_provider, settings.media_model)
    slug = slugify_npc_name(character.name)
    prompt = build_portrait_prompt(session, character)

    try:
        # Generate the image
        response = provider.generate_image(
            MediaRequest(
                prompt=prompt,
                kind="npc_portrait",
                subject=character.name,
                width=512,
                height=512,
                cache_key=f"{campaign.id}:{character.id}",
            )
        )

        # Cache the response and get the URL
        image_url = cache_portrait_response(response, slug, cache_dir)

        # Create or update portrait record
        portrait = cached or NpcPortrait(campaign_id=campaign.id, npc_id=character.id, slug=slug)
        portrait.slug = slug
        portrait.prompt = prompt
        portrait.image_url = image_url
        portrait.provider = response.provider
        portrait.model = response.model
        portrait.status = "ready"
        portrait.revised_prompt = response.revised_prompt
        portrait.error = None

        if cached is None:
            session.add(portrait)

        session.commit()
        return portrait

    except Exception as e:
        # Handle generation errors gracefully
        error_msg = str(e)

        portrait = cached or NpcPortrait(
            campaign_id=campaign.id,
            npc_id=character.id,
            slug=slug,
            prompt=prompt,
            image_url="",
            provider="error",
        )
        portrait.status = "failed"
        portrait.error = error_msg

        if cached is None:
            session.add(portrait)

        session.commit()
        return portrait
