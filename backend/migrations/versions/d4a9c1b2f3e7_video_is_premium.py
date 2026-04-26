"""video is_premium

Revision ID: d4a9c1b2f3e7
Revises: 32835af17128
Create Date: 2026-04-26 11:20:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d4a9c1b2f3e7"
down_revision: Union[str, None] = "32835af17128"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "videodb",
        sa.Column(
            "is_premium",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_index(op.f("ix_videodb_is_premium"), "videodb", ["is_premium"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_videodb_is_premium"), table_name="videodb")
    op.drop_column("videodb", "is_premium")
