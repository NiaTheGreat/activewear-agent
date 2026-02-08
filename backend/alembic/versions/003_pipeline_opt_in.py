"""Make manufacturer status nullable (null = not in pipeline)

Revision ID: 003
Revises: 002
Create Date: 2026-02-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make status nullable and remove server_default
    op.alter_column(
        "manufacturers",
        "status",
        existing_type=sa.String(20),
        nullable=True,
        server_default=None,
    )
    # Set all existing "new" status rows to null (not yet in pipeline)
    op.execute("UPDATE manufacturers SET status = NULL WHERE status = 'new'")


def downgrade() -> None:
    op.execute("UPDATE manufacturers SET status = 'new' WHERE status IS NULL")
    op.alter_column(
        "manufacturers",
        "status",
        existing_type=sa.String(20),
        nullable=False,
        server_default="new",
    )
