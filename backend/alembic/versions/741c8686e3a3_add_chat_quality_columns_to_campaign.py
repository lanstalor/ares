"""add chat quality columns to campaign

Revision ID: 741c8686e3a3
Revises: 2e8197e3fdef
Create Date: 2026-05-12 01:02:53.803013

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "741c8686e3a3"
down_revision: Union[str, None] = "2e8197e3fdef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("last_scene_state", sa.JSON(), nullable=True))
    op.add_column("campaigns", sa.Column("narrative_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("campaigns", "narrative_summary")
    op.drop_column("campaigns", "last_scene_state")
