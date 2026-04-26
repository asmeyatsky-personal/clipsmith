"""duet composed_url

Revision ID: e7f8a2b3c4d5
Revises: d4a9c1b2f3e7
Create Date: 2026-04-26 12:30:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e7f8a2b3c4d5"
down_revision: Union[str, None] = "d4a9c1b2f3e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("duetdb", sa.Column("composed_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("duetdb", "composed_url")
