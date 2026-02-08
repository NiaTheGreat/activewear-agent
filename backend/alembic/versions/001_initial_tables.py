"""Initial tables

Revision ID: 001
Revises:
Create Date: 2026-02-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("company_name", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --- criteria_presets ---
    op.create_table(
        "criteria_presets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500)),
        sa.Column("criteria", postgresql.JSONB(), nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- searches ---
    op.create_table(
        "searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "criteria_preset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("criteria_presets.id", ondelete="SET NULL"),
        ),
        sa.Column("criteria", postgresql.JSONB(), nullable=False),
        sa.Column("search_queries", postgresql.JSONB()),
        sa.Column("search_mode", sa.String(20), server_default="auto", nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("progress", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("current_step", sa.String(255)),
        sa.Column("current_detail", sa.String(500)),
        sa.Column("total_found", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_searches_user_status", "searches", ["user_id", "status"])

    # --- manufacturers ---
    op.create_table(
        "manufacturers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("search_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("searches.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("website", sa.String(500), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("contact", postgresql.JSONB()),
        sa.Column("materials", postgresql.JSONB()),
        sa.Column("production_methods", postgresql.JSONB()),
        sa.Column("certifications", postgresql.JSONB()),
        sa.Column("moq", sa.Integer()),
        sa.Column("moq_description", sa.String(255)),
        sa.Column("match_score", sa.Float(), server_default=sa.text("0"), nullable=False),
        sa.Column("confidence", sa.String(20), server_default="low", nullable=False),
        sa.Column("scoring_breakdown", postgresql.JSONB()),
        sa.Column("notes", sa.Text()),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("scraped_at", sa.DateTime(timezone=True)),
        sa.Column("user_notes", sa.Text()),
        sa.Column("user_tags", postgresql.JSONB()),
        sa.Column("is_favorite", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("contacted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_manufacturers_search_score", "manufacturers", ["search_id", "match_score"])
    op.create_index("ix_manufacturers_favorite", "manufacturers", ["search_id", "is_favorite"])


def downgrade() -> None:
    op.drop_table("manufacturers")
    op.drop_table("searches")
    op.drop_table("criteria_presets")
    op.drop_table("users")
