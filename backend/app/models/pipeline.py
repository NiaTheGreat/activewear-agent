import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Pipeline(Base):
    """
    A pipeline is a shared collection of manufacturers within an organization.
    Multiple team members can add manufacturers to the same pipeline.
    A manufacturer can belong to multiple pipelines (many-to-many).

    Examples: "Q1 2026 Production", "Sustainable Suppliers", "Backup Options"
    """
    __tablename__ = "pipelines"
    __table_args__ = (
        Index("ix_pipelines_org_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    color: Mapped[str | None] = mapped_column(String(20))  # Hex color for UI: "#3B82F6"
    icon: Mapped[str | None] = mapped_column(String(50))   # Icon name or emoji: "📌", "target"
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)  # Auto-add new manufacturers here
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    organization = relationship("Organization", back_populates="pipelines")
    created_by = relationship("User")
    pipeline_manufacturers = relationship(
        "PipelineManufacturer",
        back_populates="pipeline",
        cascade="all, delete-orphan"
    )
