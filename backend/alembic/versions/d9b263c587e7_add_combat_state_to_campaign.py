"""add combat state to campaign

Revision ID: d9b263c587e7
Revises: 741c8686e3a3
Create Date: 2026-05-12 08:22:10.925666

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd9b263c587e7'
down_revision: Union[str, None] = '741c8686e3a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("combat_state", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("campaigns", "combat_state")
