from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ConditionType
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Condition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "conditions"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    condition_type: Mapped[str] = mapped_column(String(40), nullable=False)
    duration_remaining: Mapped[int] = mapped_column(Integer, nullable=False)
    persistence: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str | None] = mapped_column(Text())

    __table_args__ = (
        UniqueConstraint("campaign_id", "character_id", "condition_type", name="uq_campaign_character_condition"),
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="conditions")
    character: Mapped["Character"] = relationship(back_populates="conditions")


from app.models.campaign import Campaign  # noqa: E402
from app.models.character import Character  # noqa: E402
