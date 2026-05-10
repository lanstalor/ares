from pathlib import Path

from app.core.enums import ClockType, Visibility
from app.services.seed_service import build_seed_bundle
from app.services.world_bible_parser import parse_world_bible


WORLD_BIBLE_PATH = Path(__file__).resolve().parents[2] / "world_bible.md"


def _load_world_bible() -> str:
    return WORLD_BIBLE_PATH.read_text(encoding="utf-8")


def test_parse_world_bible_extracts_primary_sections() -> None:
    seed = parse_world_bible(_load_world_bible())

    assert seed.world_name == "The Solar Society — Sons of Ares Era"
    assert seed.tagline == "The Society believes it has perfected humanity. Ares believes it has only perfected its chains."
    assert seed.campaign_start_pce == 728
    assert len(seed.factions) >= 15
    assert len(seed.areas) >= 20
    assert len(seed.pois) >= 15
    assert len(seed.npcs) >= 8
    assert len(seed.lore_pages) >= 5
    assert seed.player_character is not None
    assert seed.player_character.name == "Mara of Cimmeria"
    assert seed.player_character.race == "HighRed"
    assert seed.player_character.max_hp == 40
    assert seed.campaign_opening is not None
    assert "Surface Relay Tower 19" in seed.campaign_opening.opening_message
    assert len(seed.campaign_clocks) >= 5
    clock_labels = {clock.label for clock in seed.campaign_clocks}
    assert "Pelsin Diagnostic Scrub" in clock_labels
    assert "BoQC Heat" in clock_labels
    pelsin_clock = next(clock for clock in seed.campaign_clocks if clock.label == "Pelsin Diagnostic Scrub")
    assert pelsin_clock.clock_type == ClockType.THREAT
    assert pelsin_clock.current_value == 0
    assert pelsin_clock.max_value == 4
    assert pelsin_clock.hidden_from_player is True


def test_parse_world_bible_preserves_visibility_markers() -> None:
    seed = parse_world_bible(_load_world_bible())

    weaver = next(faction for faction in seed.factions if faction.name == "The Weaver’s Network")
    assert weaver.notes[0].visibility == Visibility.SEALED
    assert "Do not reveal before session 8 minimum." in weaver.notes[0].content

    counting_house = next(area for area in seed.areas if area.name == "The Counting House")
    assert counting_house.visibility == Visibility.GM_ONLY

    block_iv = next(poi for poi in seed.pois if poi.name == "Interrogation Block IV")
    assert block_iv.visibility == Visibility.GM_ONLY
    assert block_iv.gm_instructions is not None

    dockyards = next(page for page in seed.lore_pages if page.title == "The Ganymede Dockyards — Strategic Context")
    assert dockyards.visibility == Visibility.PLAYER_FACING
    assert dockyards.notes[0].visibility == Visibility.GM_ONLY

    assert seed.player_character is not None
    assert seed.player_character.notes[0].visibility == Visibility.SEALED


def test_seed_service_builds_name_based_payloads_and_hidden_secrets() -> None:
    bundle = build_seed_bundle(_load_world_bible())

    assert bundle.campaign.name == "The Solar Society — Sons of Ares Era"
    assert any("IO" in area.name.upper() for area in bundle.areas)
    assert any(poi.name == "The Melt" and poi.parent_area_name == "Callisto Depot District" for poi in bundle.pois)
    assert any(poi.name == "Surface Relay Tower 19" for poi in bundle.pois)
    assert any(secret.label.startswith("Faction: The Weaver’s Network") for secret in bundle.secrets)
    assert any(secret.label == "CampaignOpening: GM instructions" for secret in bundle.secrets)
    assert any(clock.label == "Pelsin Diagnostic Scrub" for clock in bundle.campaign_clocks)
