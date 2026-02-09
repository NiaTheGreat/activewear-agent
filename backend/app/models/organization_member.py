import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrganizationMember(Base):
    """
    Join table connecting users to organizations with role-based permissions.
    A user can be a member of multiple organizations.
    Each membership has a role: owner, admin, member, or viewer.
    """
    __tablename__ = "organization_members"
    __table_args__ = (
        # Ensure a user can only be a member of an org once
        UniqueConstraint("organization_id", "user_id", name="uq_org_user"),
        # Index for looking up all members of an org
        Index("ix_org_members_org_id", "organization_id"),
        # Index for looking up all orgs a user belongs to
        Index("ix_org_members_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    # Role determines permissions: owner > admin > member > viewer
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships")
