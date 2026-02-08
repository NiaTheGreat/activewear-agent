import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Manufacturer(Base):
    __tablename__ = "manufacturers"
    __table_args__ = (
        Index("ix_manufacturers_search_score", "search_id", "match_score"),
        Index("ix_manufacturers_favorite", "search_id", "is_favorite"),
        Index("ix_manufacturers_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("searches.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    contact: Mapped[dict | None] = mapped_column(JSONB)
    materials: Mapped[list | None] = mapped_column(JSONB)
    production_methods: Mapped[list | None] = mapped_column(JSONB)
    certifications: Mapped[list | None] = mapped_column(JSONB)
    moq: Mapped[int | None] = mapped_column(Integer)
    moq_description: Mapped[str | None] = mapped_column(String(255))
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[str] = mapped_column(String(20), default="low")
    scoring_breakdown: Mapped[dict | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_notes: Mapped[str | None] = mapped_column(Text)
    user_tags: Mapped[list | None] = mapped_column(JSONB)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str | None] = mapped_column(String(20), default=None)
    next_followup_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    search = relationship("Search", back_populates="manufacturers")
    activities = relationship("ContactActivity", back_populates="manufacturer", cascade="all, delete-orphan")
