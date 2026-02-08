import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CriteriaPresetCreate(BaseModel):
    name: str
    description: str | None = None
    criteria: dict[str, Any]
    is_public: bool = False


class CriteriaPresetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    criteria: dict[str, Any] | None = None
    is_public: bool | None = None


class CriteriaPresetResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None
    criteria: dict[str, Any]
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SearchCreate(BaseModel):
    criteria: dict[str, Any]
    criteria_preset_id: uuid.UUID | None = None
    search_mode: str = "auto"
    max_manufacturers: int = 10


class SearchStatus(BaseModel):
    id: uuid.UUID
    status: str
    progress: int
    current_step: str | None
    current_detail: str | None
    total_found: int
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    criteria_preset_id: uuid.UUID | None
    criteria: dict[str, Any]
    search_queries: dict[str, Any] | None
    search_mode: str
    status: str
    progress: int
    current_step: str | None
    current_detail: str | None
    total_found: int
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
