import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ========== Organization Schemas ==========

class OrganizationCreate(BaseModel):
    """Request body for creating an organization."""
    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$", description="URL-friendly slug")
    description: str | None = Field(None, max_length=1000)


class OrganizationUpdate(BaseModel):
    """Request body for updating an organization."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class OrganizationResponse(BaseModel):
    """Response body for organization data."""
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    created_by_user_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    member_count: int | None = None  # Optional, only included in list views

    model_config = {"from_attributes": True}


# ========== Organization Member Schemas ==========

class OrganizationMemberCreate(BaseModel):
    """Request body for inviting a user to an organization."""
    email: str = Field(..., description="Email of user to invite")
    role: str = Field("member", pattern="^(owner|admin|member|viewer)$")


class OrganizationMemberUpdate(BaseModel):
    """Request body for updating a member's role."""
    role: str = Field(..., pattern="^(owner|admin|member|viewer)$")


class OrganizationMemberResponse(BaseModel):
    """Response body for organization member data."""
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    joined_at: datetime
    # Optionally include user details
    user_email: str | None = None
    user_full_name: str | None = None

    model_config = {"from_attributes": True}
