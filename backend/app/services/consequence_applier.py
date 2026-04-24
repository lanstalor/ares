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
class LocationChange:
    new_location_label: str


@dataclass
class Consequences:
    clock_ticks: list[ClockTick] = field(default_factory=list)
    secret_status_changes: list[SecretStatusChange] = field(default_factory=list)
    new_memories: list[MemoryDraft] = field(default_factory=list)
    location_change: LocationChange | None = None


@dataclass
class ConsequenceResult:
    clocks_fired: list[str]
    location_changed_to: str | None = None


def apply_consequences(session: Session, campaign: Campaign, consequences: Consequences) -> ConsequenceResult:
    fired: list[str] = []

    for tick in consequences.clock_ticks:
        clock = session.scalar(
            select(Clock).where(Clock.campaign_id == campaign.id, Clock.label == tick.label)
        )
        if clock is None:
            continue
        was_below_max = clock.current_value < clock.max_value
        clock.current_value = min(clock.max_value, clock.current_value + tick.delta)
        if was_below_max and clock.current_value == clock.max_value:
            fired.append(clock.label)

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

    location_changed_to: str | None = None
    if consequences.location_change is not None:
        campaign.current_location_label = consequences.location_change.new_location_label
        location_changed_to = consequences.location_change.new_location_label

    return ConsequenceResult(clocks_fired=fired, location_changed_to=location_changed_to)
