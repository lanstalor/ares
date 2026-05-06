from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ClockType
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Campaign(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tagline: Mapped[str | None] = mapped_column(String(255))
    current_date_pce: Mapped[int] = mapped_column(Integer, default=728)
    hidden_state_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    current_location_label: Mapped[str | None] = mapped_column(String(255))

    objectives: Mapped[list["Objective"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    clocks: Mapped[list["Clock"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    turns: Mapped[list["Turn"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    memories: Mapped[list["Memory"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    secrets: Mapped[list["Secret"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    characters: Mapped[list["Character"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    items: Mapped[list["Item"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    scene_art: Mapped[list["SceneArt"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class Objective(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "objectives"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    gm_instructions: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    campaign: Mapped["Campaign"] = relationship(back_populates="objectives")


class Clock(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clocks"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    clock_type: Mapped[ClockType] = mapped_column(Enum(ClockType), nullable=False)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
    max_value: Mapped[int] = mapped_column(Integer, default=4)
    hidden_from_player: Mapped[bool] = mapped_column(Boolean, default=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="clocks")


from app.models.character import Character, Item  # noqa: E402
from app.models.media import SceneArt  # noqa: E402
from app.models.memory import Memory, Secret, Turn  # noqa: E402
