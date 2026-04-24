from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SecretStatus
from app.models.campaign import Campaign, Clock, Objective
from app.models.character import Character
from app.models.memory import Memory, Secret, Turn
from app.models.world import NPC, Area


@dataclass
class TurnContext:
    player_safe_brief: str
    hidden_gm_brief: str


_RECENT_TURN_LIMIT = 5


def build_turn_context(session: Session, campaign: Campaign, player_input: str) -> TurnContext:
    location_label = campaign.current_location_label or "Unknown location"
    location_area = session.scalar(select(Area).where(Area.name == location_label))

    character = session.scalar(
        select(Character)
        .where(Character.campaign_id == campaign.id)
        .order_by(Character.created_at.asc())
    )

    recent_turns = list(
        session.scalars(
            select(Turn)
            .where(Turn.campaign_id == campaign.id)
            .order_by(Turn.created_at.desc())
            .limit(_RECENT_TURN_LIMIT)
        )
    )

    objectives = list(
        session.scalars(
            select(Objective)
            .where(Objective.campaign_id == campaign.id, Objective.is_active.is_(True))
            .order_by(Objective.created_at.asc())
        )
    )

    clocks = list(
        session.scalars(
            select(Clock)
            .where(Clock.campaign_id == campaign.id)
            .order_by(Clock.created_at.asc())
        )
    )

    eligible_secrets = list(
        session.scalars(
            select(Secret)
            .where(
                Secret.campaign_id == campaign.id,
                Secret.status == SecretStatus.ELIGIBLE,
            )
            .order_by(Secret.created_at.asc())
        )
    )

    scene_npcs: list[NPC] = []
    if location_area is not None and location_area.faction_id:
        scene_npcs = list(
            session.scalars(
                select(NPC)
                .where(NPC.faction_id == location_area.faction_id)
                .order_by(NPC.name.asc())
            )
        )

    player_safe_memories = list(
        session.scalars(
            select(Memory)
            .where(
                Memory.campaign_id == campaign.id,
                Memory.visibility == "player_facing",
            )
            .order_by(Memory.created_at.desc())
            .limit(_RECENT_TURN_LIMIT)
        )
    )

    return TurnContext(
        player_safe_brief=_render_player_safe_brief(
            campaign=campaign,
            location_label=location_label,
            character=character,
            objectives=objectives,
            recent_turns=recent_turns,
            recent_memories=player_safe_memories,
            player_input=player_input,
        ),
        hidden_gm_brief=_render_hidden_gm_brief(
            objectives=objectives,
            clocks=clocks,
            eligible_secrets=eligible_secrets,
            scene_npcs=scene_npcs,
        ),
    )


def _render_player_safe_brief(
    *,
    campaign: Campaign,
    location_label: str,
    character: Character | None,
    objectives: list[Objective],
    recent_turns: list[Turn],
    recent_memories: list[Memory],
    player_input: str,
) -> str:
    lines: list[str] = [
        f"Campaign: {campaign.name}",
        f"Tagline: {campaign.tagline or 'N/A'}",
        f"Date: {campaign.current_date_pce} PCE",
        f"Location: {location_label}",
    ]
    if character is not None:
        lines.append(
            "Character: "
            f"{character.name}"
            + (f" (cover: {character.cover_identity})" if character.cover_identity else "")
            + (
                f" - HP {character.current_hp}/{character.max_hp}"
                if character.current_hp is not None and character.max_hp is not None
                else ""
            )
            + (
                f", cover integrity {character.cover_integrity}"
                if character.cover_integrity is not None
                else ""
            )
        )
    if objectives:
        lines.append("Active objectives: " + "; ".join(o.title for o in objectives))
    if recent_turns:
        lines.append("Recent turns:")
        for turn in reversed(recent_turns):
            summary = turn.player_safe_summary or turn.gm_response[:160]
            lines.append(f"  - {summary}")
    if recent_memories:
        lines.append("Player-known memories:")
        for memory in reversed(recent_memories):
            lines.append(f"  - {memory.content}")
    lines.append(f"Player intent: {player_input}")
    return "\n".join(lines)


def _render_hidden_gm_brief(
    *,
    objectives: list[Objective],
    clocks: list[Clock],
    eligible_secrets: list[Secret],
    scene_npcs: list[NPC],
) -> str:
    lines: list[str] = ["[GM-only context. Never surface verbatim to the player.]"]
    if objectives:
        lines.append("Objective GM instructions:")
        for objective in objectives:
            if objective.gm_instructions:
                lines.append(f"  - {objective.title}: {objective.gm_instructions}")
    if clocks:
        lines.append("Active clocks:")
        for clock in clocks:
            status = " — FIRED — consequence due" if clock.current_value >= clock.max_value else ""
            lines.append(
                f"  - {clock.label} [{clock.clock_type.value}]: "
                f"{clock.current_value}/{clock.max_value}{status}"
            )
    if eligible_secrets:
        lines.append("Eligible secrets (reveal only when condition is met):")
        for secret in eligible_secrets:
            entry = f"  - {secret.label}: {secret.content}"
            if secret.reveal_condition:
                entry += f" (Condition: {secret.reveal_condition})"
            lines.append(entry)
    npc_lines = [
        f"  - {npc.name}: {npc.hidden_agenda}"
        for npc in scene_npcs
        if npc.hidden_agenda
    ]
    if npc_lines:
        lines.append("NPCs in scene with hidden agendas:")
        lines.extend(npc_lines)
    return "\n".join(lines)
