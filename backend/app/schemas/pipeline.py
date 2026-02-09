import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ========== Pipeline Schemas ==========

class PipelineCreate(BaseModel):
    """Request body for creating a pipeline."""
    name: str = Field(..., min_length=1, max_length=255, description="Pipeline name")
    description: str | None = Field(None, max_length=1000)
    color: str | None = Field(None, max_length=20, description="Hex color code like #3B82F6")
    icon: str | None = Field(None, max_length=50, description="Icon name or emoji")
    is_default: bool = Field(False, description="Auto-add new manufacturers to this pipeline")


class PipelineUpdate(BaseModel):
    """Request body for updating a pipeline."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    color: str | None = Field(None, max_length=20)
    icon: str | None = Field(None, max_length=50)
    is_default: bool | None = None


class PipelineResponse(BaseModel):
    """Response body for pipeline data."""
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    color: str | None
    icon: str | None
    is_default: bool
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    manufacturer_count: int | None = None  # Optional, only included in list views

    model_config = {"from_attributes": True}


# ========== Pipeline-Manufacturer Relationship Schemas ==========

class AddManufacturerToPipelineRequest(BaseModel):
    """Request body for adding a manufacturer to a pipeline."""
    manufacturer_id: uuid.UUID
    pipeline_notes: str | None = Field(None, description="Notes specific to this pipeline")
    pipeline_status: str | None = Field(None, max_length=20, description="Status in this pipeline")
    priority: int | None = Field(None, ge=1, description="Priority within pipeline (1=highest)")


class UpdatePipelineManufacturerRequest(BaseModel):
    """Request body for updating manufacturer context within a pipeline."""
    pipeline_notes: str | None = None
    pipeline_status: str | None = Field(None, max_length=20)
    priority: int | None = Field(None, ge=1)


class PipelineManufacturerResponse(BaseModel):
    """Response body for manufacturer-pipeline relationship."""
    id: uuid.UUID
    pipeline_id: uuid.UUID
    manufacturer_id: uuid.UUID
    added_by_user_id: uuid.UUID
    added_at: datetime
    pipeline_notes: str | None
    pipeline_status: str | None
    priority: int | None

    model_config = {"from_attributes": True}
