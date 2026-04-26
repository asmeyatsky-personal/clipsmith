"""video privacy controls

Revision ID: f8b7c9d1a2e3
Revises: e7f8a2b3c4d5
Create Date: 2026-04-26 14:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f8b7c9d1a2e3"
down_revision: Union[str, None] = "e7f8a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "videodb",
        sa.Column(
            "visibility", sa.String(), nullable=False, server_default="public"
        ),
    )
    op.add_column(
        "videodb",
        sa.Column(
            "allow_comment", sa.String(), nullable=False, server_default="everyone"
        ),
    )
    op.add_column(
        "videodb",
        sa.Column(
            "allow_duet", sa.String(), nullable=False, server_default="everyone"
        ),
    )
    op.create_index(op.f("ix_videodb_visibility"), "videodb", ["visibility"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_videodb_visibility"), table_name="videodb")
    op.drop_column("videodb", "allow_duet")
    op.drop_column("videodb", "allow_comment")
    op.drop_column("videodb", "visibility")
