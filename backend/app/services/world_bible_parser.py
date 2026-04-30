from __future__ import annotations

import re
from collections.abc import Iterable

from app.core.enums import Visibility
from app.schemas.seed import (
    SeedArea,
    SeedCampaignOpening,
    SeedFaction,
    SeedLorePage,
    SeedNPC,
    SeedNote,
    SeedPOI,
    SeedPlayerCharacter,
    WorldBibleSeed,
)

SECTION_RE = re.compile(r"^##\s+\d+\.\s+.+?\{#(?P<anchor>[^}]+)\}\s*$", re.MULTILINE)
LEVEL3_RE = re.compile(r"^###\s+(?P<title>.+?)\s*$", re.MULTILINE)
LEVEL4_RE = re.compile(r"^####\s+(?P<title>.+?)\s*$", re.MULTILINE)
VISIBILITY_INLINE_RE = re.compile(r"\[(?P<marker>[A-Z -]+)(?:\s+[^\]]+)?\]")
FIELD_TOKEN_RE = re.compile(
    r"\*\*(?P<label>[^:*]+?(?:\s+\[[^]]+\])?)\:\*\*\s*(?P<value>.*?)(?=(?:\s*\|\s*\*\*[^*]+?\:\*\*)|$)"
)
TOP_HEADING_RE = re.compile(r"^#\s+(?P<title>.+)$", re.MULTILINE)


def parse_world_bible(markdown: str) -> WorldBibleSeed:
    normalized = markdown.replace("\r\n", "\n")
    sections = _extract_sections(normalized)
    world_overview = sections.get("world-overview", "")
    canon_contract = sections.get("canon-contract", "")

    return WorldBibleSeed(
        title=_extract_top_heading(normalized) or "Project Ares World Bible",
        version=_extract_version(normalized),
        world_name=_extract_simple_value(world_overview, "World Name"),
        tagline=_extract_simple_value(world_overview, "Tagline"),
        campaign_window=_extract_simple_value(canon_contract, "Campaign window"),
        campaign_start_pce=_extract_campaign_start_year(normalized),
        factions=_parse_factions(sections.get("factions", "")),
        areas=_parse_areas(sections.get("areas", "")),
        pois=_parse_pois(sections.get("pois", "")),
        npcs=_parse_npcs(sections.get("canon-npcs", "")),
        lore_pages=_parse_lore_pages(sections.get("lore", "")),
        player_character=_parse_player_character(sections.get("player-characters", "")),
        campaign_opening=_parse_campaign_opening(sections.get("campaign-opening", "")),
    )


def _extract_sections(markdown: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(markdown))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[match.group("anchor")] = markdown[start:end].strip()
    return sections


def _extract_top_heading(markdown: str) -> str | None:
    match = TOP_HEADING_RE.search(markdown)
    return match.group("title").strip() if match else None


def _extract_version(markdown: str) -> str | None:
    match = re.search(r"^###\s+(Version [^\n]+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_campaign_start_year(markdown: str) -> int:
    match = re.search(r"Campaign window:\s*(\d{3,4})[–-]\d{3,4}\s*PCE", markdown)
    if match:
        return int(match.group(1))
    return 728


def _extract_simple_value(section: str, label: str) -> str | None:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)$", section, re.MULTILINE)
    return match.group(1).strip() if match else None


def _split_level3_entries(section: str) -> list[tuple[str, str]]:
    matches = list(LEVEL3_RE.finditer(section))
    entries: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        entries.append((match.group("title").strip(), section[start:end].strip()))
    return entries


def _split_level4_entries(section: str) -> list[tuple[str, str]]:
    matches = list(LEVEL4_RE.finditer(section))
    entries: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        entries.append((match.group("title").strip(), section[start:end].strip()))
    return entries


def _clean_text(text: str) -> str:
    text = text.replace("-----", "")
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _parse_visibility(value: str | None) -> Visibility | None:
    if not value:
        return None
    upper = value.upper()
    if "PLAYER-FACING" in upper:
        return Visibility.PLAYER_FACING
    if "SEALED" in upper:
        return Visibility.SEALED
    if "LOCKED" in upper:
        return Visibility.LOCKED
    if "GM ONLY" in upper:
        return Visibility.GM_ONLY
    return None


def _strip_inline_visibility(text: str) -> tuple[str, Visibility | None]:
    match = VISIBILITY_INLINE_RE.search(text)
    visibility = _parse_visibility(match.group("marker")) if match else None
    cleaned = VISIBILITY_INLINE_RE.sub("", text).replace("``", "`").strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned, visibility


def _strip_leading_marker(text: str) -> tuple[str, Visibility | None]:
    stripped = text.strip()
    stripped = stripped.strip("*`")
    if not stripped.startswith("["):
        return text.strip(), None
    end = stripped.find("]")
    if end == -1:
        return text.strip(), None
    marker = stripped[1:end]
    visibility = _parse_visibility(marker)
    cleaned = stripped[end + 1 :].strip(" :*-")
    return cleaned.strip(), visibility


def _split_inline_marker(text: str) -> tuple[str, str | None, Visibility | None]:
    match = VISIBILITY_INLINE_RE.search(text)
    if not match:
        return text.strip(), None, None
    visibility = _parse_visibility(match.group("marker"))
    visible = text[: match.start()].strip().rstrip(" -—:`")
    hidden = text[match.end() :].strip().lstrip(" -—:`")
    return visible.strip(), hidden.strip() or None, visibility


def _parse_inline_fields(line: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for match in FIELD_TOKEN_RE.finditer(line):
        values[match.group("label").strip()] = match.group("value").strip()
    return values


def _extract_field_blocks(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_label: str | None = None
    chunks: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if not line or line == "-----":
            if current_label is not None:
                chunks.append("")
            continue

        inline_fields = _parse_inline_fields(line)
        if inline_fields and line.lstrip().startswith("**"):
            if len(inline_fields) > 1 or (len(inline_fields) == 1 and line.strip().count("**") > 2):
                if current_label is not None:
                    fields[current_label] = _clean_text("\n".join(chunks))
                    current_label = None
                    chunks = []
                fields.update(inline_fields)
                continue

            if current_label is not None:
                fields[current_label] = _clean_text("\n".join(chunks))
            current_label, value = next(iter(inline_fields.items()))
            chunks = [value]
            continue

        if current_label is not None:
            chunks.append(line)

    if current_label is not None:
        fields[current_label] = _clean_text("\n".join(chunks))
    return fields


def _split_paragraphs(text: str) -> list[str]:
    cleaned = _clean_text(text)
    if not cleaned:
        return []
    return [part.strip() for part in re.split(r"\n\s*\n", cleaned) if part.strip()]


def _extract_reveal_condition(text: str) -> str | None:
    match = re.search(r"(Do not [^.]+\.|Act \d[^.]*\.)", text)
    return match.group(1).strip() if match else None


def _build_note(label: str, content: str, fallback: Visibility = Visibility.GM_ONLY) -> SeedNote:
    visibility = _parse_visibility(label) or fallback
    stripped_content, leading_visibility = _strip_leading_marker(content)
    return SeedNote(
        label=label,
        content=stripped_content,
        visibility=leading_visibility or visibility,
    )


def _parse_factions(section: str) -> list[SeedFaction]:
    factions: list[SeedFaction] = []
    for heading, body in _split_level3_entries(section):
        fields = _extract_field_blocks(body)
        color_value = fields.get("Color")
        color_hex_match = re.search(r"`(#[0-9A-Fa-f]{6})`", color_value or "")
        notes: list[SeedNote] = []
        for label, value in fields.items():
            if label.startswith("GM note"):
                notes.append(_build_note(label, value))

        factions.append(
            SeedFaction(
                name=heading,
                color_hex=color_hex_match.group(1) if color_hex_match else None,
                description=fields.get("Description", ""),
                notes=notes,
            )
        )
    return factions


def _parse_areas(section: str) -> list[SeedArea]:
    areas: list[SeedArea] = []
    for heading, body in _split_level3_entries(section):
        heading_clean, heading_visibility = _strip_inline_visibility(heading)
        parent_match = re.match(r"(?P<name>.+?)\s+\*\(nested under (?P<parent>.+?)\*\)$", heading_clean)
        area_name = parent_match.group("name").strip() if parent_match else heading_clean.strip()
        parent_name = parent_match.group("parent").strip() if parent_match else None

        level4_entries = _split_level4_entries(body)
        area_body = body[: LEVEL4_RE.search(body).start()].strip() if LEVEL4_RE.search(body) else body
        fields = _extract_field_blocks(area_body)
        type_line = next((line for line in area_body.splitlines() if line.strip().startswith("**Type:**")), "")
        type_fields = _parse_inline_fields(type_line)
        notes: list[SeedNote] = []
        if "GM note" in fields:
            notes.append(_build_note("GM note", fields["GM note"]))

        areas.append(
            SeedArea(
                name=area_name,
                area_type=type_fields.get("Type"),
                description=fields.get("Description", ""),
                appearance=fields.get("Appearance"),
                parent_name=parent_name,
                faction_name=type_fields.get("Faction"),
                visibility=heading_visibility or Visibility.PLAYER_FACING,
                notes=notes,
            )
        )

        for _, district_text in level4_entries:
            for block in _iter_bold_entry_blocks(district_text):
                area = _parse_area_block(block, area_name)
                if area:
                    areas.append(area)
    return areas


def _iter_bold_entry_blocks(section: str) -> Iterable[str]:
    lines = [line for line in section.splitlines() if line.strip() != "-----"]
    matches = [index for index, line in enumerate(lines) if line.lstrip().startswith("**")]
    for position, start in enumerate(matches):
        end = matches[position + 1] if position + 1 < len(matches) else len(lines)
        yield "\n".join(lines[start:end]).strip()


def _parse_area_block(block: str, parent_name: str) -> SeedArea | None:
    lines = [line.rstrip() for line in block.splitlines() if line.strip()]
    if not lines:
        return None
    header, visibility = _strip_inline_visibility(lines[0])
    name_match = re.match(r"\*\*(?P<name>.+?)\*\*(?:\s*\|\s*Faction:\s*(?P<faction>.+))?$", header)
    if not name_match:
        return None

    description = _clean_text("\n".join(lines[1:]))
    return SeedArea(
        name=name_match.group("name").strip(),
        area_type="district",
        description=description,
        parent_name=parent_name,
        faction_name=(name_match.group("faction") or "").strip() or None,
        visibility=visibility or Visibility.PLAYER_FACING,
    )


def _parse_pois(section: str) -> list[SeedPOI]:
    pois: list[SeedPOI] = []
    for _, body in _split_level3_entries(section):
        for block in _iter_bold_entry_blocks(body):
            poi = _parse_poi_block(block)
            if poi:
                pois.append(poi)
    return pois


def _parse_poi_block(block: str) -> SeedPOI | None:
    lines = [line.rstrip() for line in block.splitlines() if line.strip()]
    if not lines:
        return None

    header, visibility = _strip_inline_visibility(lines[0])
    match = re.match(
        r"\*\*(?P<name>.+?)\*\*(?:\s+\*\((?P<subtitle>.+?)\)\*)?(?:\s*\|\s*Parent:\s*(?P<parent>[^|]+))?(?:\s*\|\s*Faction:\s*(?P<faction>.+))?$",
        header,
    )
    if not match:
        return None

    description_parts: list[str] = []
    gm_parts: list[str] = []
    notes: list[SeedNote] = []
    entry_visibility = visibility or Visibility.PLAYER_FACING
    for paragraph in _split_paragraphs("\n".join(lines[1:])):
        visible_text, hidden_text, paragraph_visibility = _split_inline_marker(paragraph)
        if paragraph_visibility:
            if visible_text:
                description_parts.append(visible_text)
            if hidden_text:
                notes.append(SeedNote(label="GM note", content=hidden_text, visibility=paragraph_visibility))
                gm_parts.append(hidden_text)
            if not description_parts and entry_visibility == Visibility.PLAYER_FACING:
                entry_visibility = paragraph_visibility
            continue
        if paragraph.startswith("*Tension mechanic:*"):
            gm_parts.append(paragraph.strip("*"))
            continue
        description_parts.append(paragraph)

    description = "\n\n".join(description_parts) or "\n\n".join(gm_parts)
    gm_instructions = "\n\n".join(gm_parts) or None
    return SeedPOI(
        name=match.group("name").strip(),
        subtitle=(match.group("subtitle") or "").strip() or None,
        parent_area_name=(match.group("parent") or "").strip() or None,
        faction_name=(match.group("faction") or "").strip() or None,
        description=description.strip(),
        gm_instructions=gm_instructions.strip() if gm_instructions else None,
        visibility=entry_visibility,
        notes=notes,
    )


def _parse_npc_hp(body: str) -> int | None:
    # Extract HP value from Stats line, e.g. STR 16 | DEX 18 | HP 78 | AC 16
    match = re.search(r"\bHP\s+(\d+)\b", body)
    return int(match.group(1)) if match else None


def _parse_npcs(section: str) -> list[SeedNPC]:
    npcs: list[SeedNPC] = []
    for heading, body in _split_level3_entries(section):
        fields = _extract_field_blocks(body)
        aliases = [part.strip(" “”—\"") for part in fields.get("Aliases", "").split(",") if part.strip()]
        notes: list[SeedNote] = []
        gm_rule = fields.get("GM rule")
        if gm_rule:
            notes.append(_build_note("GM rule", gm_rule))

        max_hp = _parse_npc_hp(body)

        npcs.append(
            SeedNPC(
                name=heading,
                faction_name=fields.get("Faction"),
                appearance=fields.get("Appearance"),
                personality=_join_nonempty(fields.get("Personality"), fields.get("Mannerisms")),
                hidden_agenda=gm_rule,
                aliases=aliases,
                notes=notes,
                max_hp=max_hp,
            )
        )
    return npcs
def _join_nonempty(*parts: str | None) -> str | None:
    values = [part.strip() for part in parts if part and part.strip()]
    return "\n\n".join(values) if values else None


def _parse_lore_pages(section: str) -> list[SeedLorePage]:
    pages: list[SeedLorePage] = []
    for heading, body in _split_level3_entries(section):
        paragraphs = _split_paragraphs(body)
        page_visibility = Visibility.PLAYER_FACING
        content_parts: list[str] = []
        notes: list[SeedNote] = []
        for paragraph in paragraphs:
            cleaned, visibility = _strip_leading_marker(paragraph)
            if visibility:
                if visibility == Visibility.PLAYER_FACING and not content_parts:
                    page_visibility = visibility
                    continue
                notes.append(SeedNote(label="Lore note", content=cleaned, visibility=visibility))
                continue
            content_parts.append(paragraph)

        pages.append(
            SeedLorePage(
                title=heading,
                content="\n\n".join(content_parts).strip(),
                visibility=page_visibility,
                notes=notes,
            )
        )
    return pages


def _parse_player_character(section: str) -> SeedPlayerCharacter | None:
    entries = _split_level3_entries(section)
    if not entries:
        return None

    heading, body = entries[0]
    fields = _extract_field_blocks(body)
    identity_fields = {
        key.strip(): value.strip()
        for key, value in (line.split(":", 1) for line in fields.get("Cover Identity", "").splitlines() if line.strip().startswith("- "))
    }
    identity_fields = {key.lstrip("- ").strip(): value for key, value in identity_fields.items()}
    stat_line = re.search(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", body)
    if stat_line:
        identity_fields.setdefault(
            "Stats",
            f"STR {stat_line.group(1)}, DEX {stat_line.group(2)}, CON {stat_line.group(3)}, "
            f"INT {stat_line.group(4)}, WIS {stat_line.group(5)}, CHA {stat_line.group(6)}",
        )

    race_line = next((line for line in body.splitlines() if line.strip().startswith("**Race:**")), "")
    inline_fields = _parse_inline_fields(race_line)
    notes: list[SeedNote] = []
    gm_notes = fields.get("GM Notes [SEALED]")
    if gm_notes:
        notes.append(_build_note("GM Notes [SEALED]", gm_notes, fallback=Visibility.SEALED))

    key_relationships: list[str] = []
    for item in _parse_bullet_list(fields.get("Key Relationships", "")):
        visible_text, hidden_text, visibility = _split_inline_marker(item)
        if visible_text:
            key_relationships.append(visible_text)
        if hidden_text and visibility:
            notes.append(SeedNote(label="Key Relationship", content=hidden_text, visibility=visibility))

    return SeedPlayerCharacter(
        name=heading,
        race=inline_fields.get("Race"),
        character_class=inline_fields.get("Class"),
        faction_name=inline_fields.get("Faction"),
        level=inline_fields.get("Level"),
        cover_identity=identity_fields,
        appearance=fields.get("Appearance"),
        backstory=fields.get("Backstory"),
        personality=fields.get("Personality"),
        mannerisms=fields.get("Mannerisms"),
        proficiencies=[item.strip() for item in fields.get("Proficiencies", "").split(",") if item.strip()],
        class_features=_parse_bullet_list(fields.get("Class Features (Operative — Shadow)", "")),
        equipment=_parse_bullet_list(fields.get("Equipment", "")),
        key_relationships=key_relationships,
        notes=notes,
    )


def _parse_bullet_list(text: str) -> list[str]:
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def _parse_campaign_opening(section: str) -> SeedCampaignOpening | None:
    entries = {title: body for title, body in _split_level3_entries(section)}
    gm_body = entries.get("GM Instructions (AI reads, player does not see)")
    opening_body = entries.get("Opening Message (Player-facing)")
    if not gm_body or not opening_body:
        return None
    return SeedCampaignOpening(
        gm_instructions=_extract_code_block(gm_body),
        opening_message=_extract_code_block(opening_body),
    )


def _extract_code_block(body: str) -> str:
    match = re.search(r"```(?:[^\n]*)\n(?P<content>[\s\S]+?)\n```", body)
    return _clean_text(match.group("content")) if match else _clean_text(body)
