from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SecretStatus, Visibility
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Turn(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "turns"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    player_input: Mapped[str] = mapped_column(Text(), nullable=False)
    gm_response: Mapped[str] = mapped_column(Text(), nullable=False)
    player_safe_summary: Mapped[str | None] = mapped_column(Text())

    campaign: Mapped["Campaign"] = relationship(back_populates="turns")


class Memory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "memories"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), default=Visibility.PLAYER_FACING)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    embedding_model: Mapped[str | None] = mapped_column(String(120))

    campaign: Mapped["Campaign"] = relationship(back_populates="memories")


class Secret(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "secrets"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[SecretStatus] = mapped_column(Enum(SecretStatus), default=SecretStatus.DORMANT)
    reveal_condition: Mapped[str | None] = mapped_column(Text())

    campaign: Mapped["Campaign"] = relationship(back_populates="secrets")


from app.models.campaign import Campaign  # noqa: E402
