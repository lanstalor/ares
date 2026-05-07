from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Character(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "characters"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    race: Mapped[str | None] = mapped_column(String(120))
    character_class: Mapped[str | None] = mapped_column(String(120))
    cover_identity: Mapped[str | None] = mapped_column(String(255))
    current_hp: Mapped[int | None] = mapped_column(Integer)
    max_hp: Mapped[int | None] = mapped_column(Integer)
    cover_integrity: Mapped[int | None] = mapped_column(Integer)
    inventory_summary: Mapped[str | None] = mapped_column(Text())
    notes: Mapped[str | None] = mapped_column(Text())

    campaign: Mapped["Campaign"] = relationship(back_populates="characters")
    items: Mapped[list["Item"]] = relationship(back_populates="owner")
    portrait: Mapped["NpcPortrait | None"] = relationship(back_populates="npc")
    conditions: Mapped[list["Condition"]] = relationship(back_populates="character", cascade="all, delete-orphan")


class Item(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "items"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    character_id: Mapped[str | None] = mapped_column(ForeignKey("characters.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    item_type: Mapped[str | None] = mapped_column(String(120))  # e.g., weapon, gear, tech
    rarity: Mapped[str | None] = mapped_column(String(50))  # e.g., common, relic
    tags: Mapped[str | None] = mapped_column(String(255))  # comma-separated tags
    is_equippable: Mapped[bool] = mapped_column(Boolean, default=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    campaign: Mapped["Campaign"] = relationship(back_populates="items")
    owner: Mapped["Character | None"] = relationship(back_populates="items")


from app.models.campaign import Campaign  # noqa: E402
from app.models.conditions import Condition  # noqa: E402
from app.models.portraits import NpcPortrait  # noqa: E402
