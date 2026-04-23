from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SecretStatus, Visibility
from app.models.campaign import Campaign, Clock
from app.models.memory import Memory, Secret


@dataclass
class ClockTick:
    label: str
    delta: int = 1


@dataclass
class SecretStatusChange:
    label: str
    new_status: SecretStatus


@dataclass
class MemoryDraft:
    content: str
    visibility: Visibility = Visibility.PLAYER_FACING


@dataclass
class Consequences:
    clock_ticks: list[ClockTick] = field(default_factory=list)
    secret_status_changes: list[SecretStatusChange] = field(default_factory=list)
    new_memories: list[MemoryDraft] = field(default_factory=list)


def apply_consequences(session: Session, campaign: Campaign, consequences: Consequences) -> None:
    for tick in consequences.clock_ticks:
        clock = session.scalar(
            select(Clock).where(Clock.campaign_id == campaign.id, Clock.label == tick.label)
        )
        if clock is None:
            continue
        clock.current_value = min(clock.max_value, clock.current_value + tick.delta)

    for change in consequences.secret_status_changes:
        secret = session.scalar(
            select(Secret).where(Secret.campaign_id == campaign.id, Secret.label == change.label)
        )
        if secret is None:
            continue
        secret.status = change.new_status

    for draft in consequences.new_memories:
        session.add(
            Memory(
                campaign_id=campaign.id,
                content=draft.content,
                visibility=draft.visibility,
            )
        )
