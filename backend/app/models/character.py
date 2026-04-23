from sqlalchemy import ForeignKey, Integer, String, Text
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


from app.models.campaign import Campaign  # noqa: E402
