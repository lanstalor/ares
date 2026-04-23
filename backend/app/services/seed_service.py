from __future__ import annotations

from pathlib import Path

from app.schemas.seed import (
    SeedCampaignRow,
    SeedImportBundle,
    SeedNote,
    SeedSecret,
    WorldBibleSeed,
)
from app.services.world_bible_parser import parse_world_bible


def parse_world_bible_file(path: str | Path) -> WorldBibleSeed:
    return parse_world_bible(Path(path).read_text(encoding="utf-8"))


def build_seed_bundle(markdown: str) -> SeedImportBundle:
    seed = parse_world_bible(markdown)
    campaign_name = seed.world_name or seed.title
    return SeedImportBundle(
        campaign=SeedCampaignRow(
            name=campaign_name,
            tagline=seed.tagline,
            current_date_pce=seed.campaign_start_pce,
            hidden_state_enabled=True,
        ),
        factions=seed.factions,
        areas=seed.areas,
        pois=seed.pois,
        npcs=seed.npcs,
        lore_pages=seed.lore_pages,
        secrets=_collect_hidden_secrets(seed),
        player_character=seed.player_character,
        campaign_opening=seed.campaign_opening,
    )


def build_seed_bundle_from_file(path: str | Path) -> SeedImportBundle:
    return build_seed_bundle(Path(path).read_text(encoding="utf-8"))


def _collect_hidden_secrets(seed: WorldBibleSeed) -> list[SeedSecret]:
    secrets: list[SeedSecret] = []

    def add_notes(prefix: str, name: str, notes: list[SeedNote]) -> None:
        for note in notes:
            if note.visibility.value == "player_facing":
                continue
            secrets.append(
                SeedSecret(
                    label=f"{prefix}: {name} / {note.label}",
                    content=note.content,
                    reveal_condition=_extract_reveal_condition(note.content),
                    source_reference=f"{prefix.lower()}:{name}",
                )
            )

    for faction in seed.factions:
        add_notes("Faction", faction.name, faction.notes)
    for area in seed.areas:
        add_notes("Area", area.name, area.notes)
    for poi in seed.pois:
        add_notes("POI", poi.name, poi.notes)
    for npc in seed.npcs:
        add_notes("NPC", npc.name, npc.notes)
    for page in seed.lore_pages:
        add_notes("LorePage", page.title, page.notes)
    if seed.player_character:
        add_notes("PlayerCharacter", seed.player_character.name, seed.player_character.notes)
    if seed.campaign_opening:
        secrets.append(
            SeedSecret(
                label="CampaignOpening: GM instructions",
                content=seed.campaign_opening.gm_instructions,
                source_reference="campaign_opening",
            )
        )
    return secrets


def _extract_reveal_condition(text: str) -> str | None:
    for sentence in text.split("."):
        stripped = sentence.strip()
        if stripped.startswith("Do not ") or stripped.startswith("Act "):
            return f"{stripped}."
    return None
