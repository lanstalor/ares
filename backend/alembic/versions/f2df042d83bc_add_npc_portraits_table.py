"""add npc_portraits table

Revision ID: f2df042d83bc
Revises: c4b16f7a8b2d
Create Date: 2026-05-06 22:44:37.131862

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f2df042d83bc'
down_revision: Union[str, None] = 'c4b16f7a8b2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'npc_portraits',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('campaign_id', sa.String(length=36), nullable=False),
        sa.Column('npc_id', sa.String(length=36), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('provider', sa.String(length=80), nullable=False),
        sa.Column('model', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=40), nullable=False, server_default='generating'),
        sa.Column('revised_prompt', sa.Text(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['npc_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('campaign_id', 'npc_id', name='uq_npc_portrait_campaign_npc'),
    )
    op.create_index(op.f('ix_npc_portraits_campaign_id'), 'npc_portraits', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_npc_portraits_npc_id'), 'npc_portraits', ['npc_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_npc_portraits_npc_id'), table_name='npc_portraits')
    op.drop_index(op.f('ix_npc_portraits_campaign_id'), table_name='npc_portraits')
    op.drop_table('npc_portraits')
