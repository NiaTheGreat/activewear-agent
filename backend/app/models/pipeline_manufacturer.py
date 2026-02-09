import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PipelineManufacturer(Base):
    """
    Join table connecting manufacturers to pipelines (many-to-many).
    A manufacturer can exist in multiple pipelines.
    Each pipeline-manufacturer relationship can have its own context:
    - Different notes per pipeline
    - Different status per pipeline
    - Different priority per pipeline

    This allows the same manufacturer to be evaluated differently in different contexts.
    Example: "Nike Clone Co." might be:
      - Priority 1 in "Q1 2026 Production" pipeline
      - Priority 3 in "Backup Suppliers" pipeline
    """
    __tablename__ = "pipeline_manufacturers"
    __table_args__ = (
        # Ensure a manufacturer can only be added to a pipeline once
        UniqueConstraint("pipeline_id", "manufacturer_id", name="uq_pipeline_manufacturer"),
        # Index for looking up all manufacturers in a pipeline
        Index("ix_pipeline_mfg_pipeline_id", "pipeline_id"),
        # Index for looking up all pipelines containing a manufacturer
        Index("ix_pipeline_mfg_manufacturer_id", "manufacturer_id"),
        # Index for filtering by status within a pipeline
        Index("ix_pipeline_mfg_status", "pipeline_id", "pipeline_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pipelines.id", ondelete="CASCADE"),
        nullable=False
    )
    manufacturer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("manufacturers.id", ondelete="CASCADE"),
        nullable=False
    )
    # Who added this manufacturer to THIS pipeline
    added_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Pipeline-specific context (can differ from the manufacturer's base values)
    pipeline_notes: Mapped[str | None] = mapped_column(Text)  # Notes specific to this pipeline
    pipeline_status: Mapped[str | None] = mapped_column(String(20))  # Status in this pipeline context
    priority: Mapped[int | None] = mapped_column(Integer)  # Priority within this pipeline (1=highest)

    # Relationships
    pipeline = relationship("Pipeline", back_populates="pipeline_manufacturers")
    manufacturer = relationship("Manufacturer", back_populates="pipeline_manufacturers")
    added_by = relationship("User")
