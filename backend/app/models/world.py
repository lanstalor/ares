from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Visibility
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Area(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "areas"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    area_type: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text())
    appearance: Mapped[str | None] = mapped_column(Text())
    parent_area_id: Mapped[str | None] = mapped_column(ForeignKey("areas.id"))
    faction_id: Mapped[str | None] = mapped_column(ForeignKey("factions.id"))
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), default=Visibility.PLAYER_FACING)


class POI(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pois"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_area_id: Mapped[str | None] = mapped_column(ForeignKey("areas.id"))
    faction_id: Mapped[str | None] = mapped_column(ForeignKey("factions.id"))
    description: Mapped[str | None] = mapped_column(Text())
    gm_instructions: Mapped[str | None] = mapped_column(Text())
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), default=Visibility.PLAYER_FACING)


class Faction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "factions"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    color_hex: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text())
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), default=Visibility.PLAYER_FACING)


class NPC(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "npcs"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    faction_id: Mapped[str | None] = mapped_column(ForeignKey("factions.id"))
    appearance: Mapped[str | None] = mapped_column(Text())
    personality: Mapped[str | None] = mapped_column(Text())
    hidden_agenda: Mapped[str | None] = mapped_column(Text())
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), default=Visibility.PLAYER_FACING)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)


class LorePage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lore_pages"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), default=Visibility.PLAYER_FACING)
