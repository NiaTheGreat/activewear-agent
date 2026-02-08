import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ManufacturerUpdate(BaseModel):
    user_notes: str | None = None
    user_tags: list[str] | None = None
    is_favorite: bool | None = None
    contacted_at: datetime | None = None
