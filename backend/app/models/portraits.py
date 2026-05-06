from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class NpcPortrait(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "npc_portraits"
    __table_args__ = (UniqueConstraint("campaign_id", "npc_id", name="uq_npc_portrait_campaign_npc"),)

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    npc_id: Mapped[str] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt: Mapped[str] = mapped_column(Text(), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="generating", nullable=False)
    revised_prompt: Mapped[str | None] = mapped_column(Text(), nullable=True)
    error: Mapped[str | None] = mapped_column(Text(), nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="npc_portraits")
    npc: Mapped["Character"] = relationship(back_populates="portrait")


from app.models.campaign import Campaign  # noqa: E402
from app.models.character import Character  # noqa: E402
