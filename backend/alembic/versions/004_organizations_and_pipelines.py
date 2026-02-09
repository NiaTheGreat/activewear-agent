"""Add organizations and pipelines for team collaboration

Revision ID: 004
Revises: 003
Create Date: 2026-02-08

This migration adds:
- organizations: Team workspaces
- organization_members: User membership in orgs with roles
- pipelines: Shared manufacturer collections within orgs
- pipeline_manufacturers: Many-to-many join for manufacturers in pipelines
- Modifies searches to optionally belong to an organization
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========== Create organizations table ==========
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.String(1000)),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    # ========== Create organization_members table ==========
    op.create_table(
        "organization_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), server_default="member", nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
    )
    # Unique constraint: a user can only be a member of an org once
    op.create_unique_constraint("uq_org_user", "organization_members", ["organization_id", "user_id"])
    op.create_index("ix_org_members_org_id", "organization_members", ["organization_id"])
    op.create_index("ix_org_members_user_id", "organization_members", ["user_id"])

    # ========== Create pipelines table ==========
    op.create_table(
        "pipelines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000)),
        sa.Column("color", sa.String(20)),
        sa.Column("icon", sa.String(50)),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pipelines_org_id", "pipelines", ["organization_id"])

    # ========== Create pipeline_manufacturers table ==========
    op.create_table(
        "pipeline_manufacturers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "pipeline_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pipelines.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "manufacturer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("manufacturers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "added_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pipeline_notes", sa.Text()),
        sa.Column("pipeline_status", sa.String(20)),
        sa.Column("priority", sa.Integer()),
    )
    # Unique constraint: a manufacturer can only be in a pipeline once
    op.create_unique_constraint(
        "uq_pipeline_manufacturer", "pipeline_manufacturers", ["pipeline_id", "manufacturer_id"]
    )
    op.create_index("ix_pipeline_mfg_pipeline_id", "pipeline_manufacturers", ["pipeline_id"])
    op.create_index("ix_pipeline_mfg_manufacturer_id", "pipeline_manufacturers", ["manufacturer_id"])
    op.create_index("ix_pipeline_mfg_status", "pipeline_manufacturers", ["pipeline_id", "pipeline_status"])

    # ========== Modify searches table to support organizations ==========
    # Add organization_id column (nullable - NULL means personal search)
    op.add_column(
        "searches",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
        ),
    )
    # Add index for querying org searches
    op.create_index("ix_searches_org_status", "searches", ["organization_id", "status"])


def downgrade() -> None:
    """Reverse the migration."""
    # Remove organization_id from searches
    op.drop_index("ix_searches_org_status", table_name="searches")
    op.drop_column("searches", "organization_id")

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("pipeline_manufacturers")
    op.drop_table("pipelines")
    op.drop_table("organization_members")
    op.drop_table("organizations")
