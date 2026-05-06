from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SecretStatus, Visibility
from app.models.campaign import Campaign, Clock, Objective
from app.models.character import Character, Item
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
class ObjectiveUpdate:
    title: str
    action: str  # "complete" or "add"
    description: str | None = None
    gm_instructions: str | None = None


@dataclass
class InventoryUpdate:
    name: str
    action: str  # "add", "remove", "update"
    quantity: int | None = None
    description: str | None = None
    tags: str | None = None


@dataclass
class Consequences:
    clock_ticks: list[ClockTick] = field(default_factory=list)
    secret_status_changes: list[SecretStatusChange] = field(default_factory=list)
    new_memories: list[MemoryDraft] = field(default_factory=list)
    location_change: LocationChange | None = None
    objective_updates: list[ObjectiveUpdate] = field(default_factory=list)
    inventory_updates: list[InventoryUpdate] = field(default_factory=list)


@dataclass
class ConsequenceResult:
    clocks_fired: list[str]
    location_changed_to: str | None = None
    revealed_secrets: list[dict] = field(default_factory=list)


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

    revealed: list[dict] = []
    for change in consequences.secret_status_changes:
        secret = session.scalar(
            select(Secret).where(Secret.campaign_id == campaign.id, Secret.label == change.label)
        )
        if secret is None:
            continue
        secret.status = change.new_status
        if change.new_status == SecretStatus.REVEALED:
            revealed.append({"label": secret.label, "content": secret.content})

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

    for update in consequences.objective_updates:
        if update.action == "complete":
            obj = session.scalar(
                select(Objective).where(
                    Objective.campaign_id == campaign.id,
                    Objective.title == update.title,
                    Objective.is_active.is_(True),
                )
            )
            if obj:
                obj.is_active = False
        elif update.action == "add":
            session.add(
                Objective(
                    campaign_id=campaign.id,
                    title=update.title,
                    description=update.description,
                    gm_instructions=update.gm_instructions,
                    is_active=True,
                )
            )

    if consequences.inventory_updates:
        character = session.scalar(select(Character).where(Character.campaign_id == campaign.id))
        if character:
            for update in consequences.inventory_updates:
                item = session.scalar(
                    select(Item).where(
                        Item.campaign_id == campaign.id,
                        Item.character_id == character.id,
                        Item.name == update.name
                    )
                )
                if update.action == "add":
                    if item:
                        item.quantity += (update.quantity or 1)
                        if update.description:
                            item.description = update.description
                        if update.tags:
                            item.tags = update.tags
                    else:
                        session.add(
                            Item(
                                campaign_id=campaign.id,
                                character_id=character.id,
                                name=update.name,
                                quantity=update.quantity or 1,
                                description=update.description,
                                tags=update.tags,
                            )
                        )
                elif update.action == "remove":
                    if item:
                        if update.quantity and item.quantity > update.quantity:
                            item.quantity -= update.quantity
                        else:
                            session.delete(item)
                elif update.action == "update":
                    if item:
                        if update.quantity is not None:
                            item.quantity = update.quantity
                        if update.description:
                            item.description = update.description
                        if update.tags:
                            item.tags = update.tags

    return ConsequenceResult(clocks_fired=fired, location_changed_to=location_changed_to, revealed_secrets=revealed)
