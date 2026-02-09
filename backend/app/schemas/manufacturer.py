import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


class ManufacturerResponse(BaseModel):
    id: uuid.UUID
    search_id: uuid.UUID
    name: str
    website: str
    location: str | None
    contact: dict[str, Any] | None
    materials: list[str] | None
    production_methods: list[str] | None
    certifications: list[str] | None
    moq: int | None
    moq_description: str | None
    match_score: float
    confidence: str
    scoring_breakdown: dict[str, Any] | None
    notes: str | None
    source_url: str
    scraped_at: datetime | None
    user_notes: str | None
    user_tags: list[str] | None
    is_favorite: bool
    contacted_at: datetime | None
    status: str | None
    next_followup_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ManufacturerCreate(BaseModel):
    name: str
    website: str = ""
    location: str | None = None
    contact: dict[str, Any] | None = None
    materials: list[str] | None = None
    production_methods: list[str] | None = None
    certifications: list[str] | None = None
    moq: int | None = None
    moq_description: str | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("moq")
    @classmethod
    def moq_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("MOQ must be non-negative")
        return v


class ManufacturerUpdate(BaseModel):
    user_notes: str | None = None
    user_tags: list[str] | None = None
    is_favorite: bool | None = None
    contacted_at: datetime | None = None
    status: str | None = None
    next_followup_date: datetime | None = None

    # Data fields
    name: str | None = None
    website: str | None = None
    location: str | None = None
    contact: dict[str, Any] | None = None
    materials: list[str] | None = None
    production_methods: list[str] | None = None
    certifications: list[str] | None = None
    moq: int | None = None
    moq_description: str | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("website")
    @classmethod
    def website_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Website cannot be empty")
        return v

    @field_validator("moq")
    @classmethod
    def moq_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("MOQ must be non-negative")
        return v

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str | None) -> str | None:
        valid = ("new", "contacted", "quoted", "negotiating", "won", "lost")
        if v is not None and v not in valid:
            raise ValueError(f"Status must be one of: {', '.join(valid)}")
        return v


class CopyToOrganizationRequest(BaseModel):
    """Request body for copying a manufacturer to an organization."""
    organization_id: uuid.UUID
    pipeline_ids: list[uuid.UUID] | None = None
