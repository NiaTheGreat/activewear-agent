"""Add contact tracking: status, next_followup_date, and contact_activities table

Revision ID: 002
Revises: 001
Create Date: 2026-02-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to manufacturers
    op.add_column("manufacturers", sa.Column("status", sa.String(20), server_default="new", nullable=False))
    op.add_column("manufacturers", sa.Column("next_followup_date", sa.DateTime(timezone=True)))
    op.create_index("ix_manufacturers_status", "manufacturers", ["status"])

    # Create contact_activities table
    op.create_table(
        "contact_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "manufacturer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("manufacturers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activity_type", sa.String(50), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("content", sa.Text()),
        sa.Column("contact_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reminder_date", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_contact_activities_manufacturer", "contact_activities", ["manufacturer_id"])


def downgrade() -> None:
    op.drop_table("contact_activities")
    op.drop_index("ix_manufacturers_status", table_name="manufacturers")
    op.drop_column("manufacturers", "next_followup_date")
    op.drop_column("manufacturers", "status")
