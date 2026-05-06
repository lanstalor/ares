from __future__ import annotations

import base64
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.campaign import Campaign, Objective
from app.models.media import SceneArt
from app.services.media_provider import MediaProvider, MediaRequest, MediaResponse
from app.services.provider_registry import get_media_provider


_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
_GENERATED_SCENE_ART_PREFIX = "/api/v1/media/scene-art"


def slugify_scene_label(value: str | None) -> str:
    normalized = _SLUG_PATTERN.sub("-", (value or "unknown-location").lower()).strip("-")
    return normalized[:120] or "unknown-location"


def get_cached_scene_art(
    *,
    session: Session,
    campaign_id: str,
    location_label: str | None,
) -> SceneArt | None:
    slug = slugify_scene_label(location_label)
    return session.scalar(
        select(SceneArt).where(
            SceneArt.campaign_id == campaign_id,
            SceneArt.slug == slug,
        )
    )


def ensure_scene_art(
    *,
    session: Session,
    campaign: Campaign,
    location_label: str | None = None,
    force: bool = False,
    media_provider: MediaProvider | None = None,
    cache_dir: Path | None = None,
) -> SceneArt:
    target_location = location_label or campaign.current_location_label or "Unknown location"
    cached = get_cached_scene_art(
        session=session,
        campaign_id=campaign.id,
        location_label=target_location,
    )
    if cached is not None and cached.status == "ready" and not force:
        return cached

    settings = get_settings()
    provider = media_provider or get_media_provider(settings.media_provider, settings.media_model)
    prompt = build_scene_art_prompt(session=session, campaign=campaign, location_label=target_location)
    slug = slugify_scene_label(target_location)

    response = provider.generate_image(
        MediaRequest(
            prompt=prompt,
            kind="scene_art",
            subject=target_location,
            negative_prompt=(
                "named canon character cameos, Darrow, Eo, Cassius, Virginia, Mustang, "
                "UI overlays, readable text, spoilers, hidden agendas"
            ),
            width=1024,
            height=1024,
            cache_key=f"{campaign.id}:{slug}",
        )
    )
    image_url = cache_scene_art_response(response=response, slug=slug, cache_dir=cache_dir)

    scene_art = cached or SceneArt(campaign_id=campaign.id, location_label=target_location, slug=slug)
    scene_art.location_label = target_location
    scene_art.prompt = prompt
    scene_art.image_url = image_url
    scene_art.provider = response.provider
    scene_art.model = response.model
    scene_art.status = "ready"
    scene_art.revised_prompt = response.revised_prompt
    scene_art.error = None

    if cached is None:
        session.add(scene_art)

    return scene_art


def build_scene_art_prompt(
    *,
    session: Session,
    campaign: Campaign,
    location_label: str,
) -> str:
    active_objective = session.scalar(
        select(Objective).where(
            Objective.campaign_id == campaign.id,
            Objective.is_active.is_(True),
        )
    )
    objective_text = active_objective.title if active_objective is not None else "No active objective"
    tagline = campaign.tagline or "Hidden-state Red Rising solo campaign"

    return "\n".join(
        [
            "Create atmospheric scene art for Project Ares, a Red Rising-inspired solo RPG.",
            f"Campaign: {campaign.name}.",
            f"Public campaign premise: {tagline}.",
            f"Current player-facing location: {location_label}.",
            f"Current player-facing objective: {objective_text}.",
            "Style: cinematic retro terminal companion art, lived-in science-fantasy, grounded industrial detail.",
            "Do not include hidden-state secrets, private NPC motives, UI chrome, logos, or readable text.",
            "Keep the image suitable as a 4:3 gameplay backdrop behind overlays.",
        ]
    )


def cache_scene_art_response(
    *,
    response: MediaResponse,
    slug: str,
    cache_dir: Path | None = None,
) -> str:
    if response.b64_json:
        target_dir = cache_dir or get_settings().scene_art_cache_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{slug}.png"
        target_path.write_bytes(base64.b64decode(response.b64_json))
        return f"{_GENERATED_SCENE_ART_PREFIX}/{target_path.name}"

    if response.url:
        return response.url

    raise ValueError("Media provider returned no usable scene art payload.")
