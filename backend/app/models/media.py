from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SceneArt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scene_art"
    __table_args__ = (UniqueConstraint("campaign_id", "slug", name="uq_scene_art_campaign_slug"),)

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    location_label: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False)
    prompt: Mapped[str] = mapped_column(Text(), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ready", nullable=False)
    revised_prompt: Mapped[str | None] = mapped_column(Text(), nullable=True)
    error: Mapped[str | None] = mapped_column(Text(), nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="scene_art")


from app.models.campaign import Campaign  # noqa: E402
