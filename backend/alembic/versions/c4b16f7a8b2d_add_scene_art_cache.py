"""Add scene art cache

Revision ID: c4b16f7a8b2d
Revises: 05561cace318
Create Date: 2026-05-06 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4b16f7a8b2d'
down_revision: Union[str, None] = '05561cace318'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'scene_art',
        sa.Column('campaign_id', sa.String(length=36), nullable=False),
        sa.Column('location_label', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=160), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('provider', sa.String(length=80), nullable=False),
        sa.Column('model', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('revised_prompt', sa.Text(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('campaign_id', 'slug', name='uq_scene_art_campaign_slug'),
    )


def downgrade() -> None:
    op.drop_table('scene_art')
