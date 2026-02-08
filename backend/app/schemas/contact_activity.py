import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


VALID_ACTIVITY_TYPES = ("email", "call", "meeting", "quote_received", "sample_requested", "note")


class ContactActivityCreate(BaseModel):
    activity_type: str
    subject: str
    content: str | None = None
    contact_date: datetime
    reminder_date: datetime | None = None

    @field_validator("activity_type")
    @classmethod
    def activity_type_valid(cls, v: str) -> str:
        if v not in VALID_ACTIVITY_TYPES:
            raise ValueError(f"activity_type must be one of: {', '.join(VALID_ACTIVITY_TYPES)}")
        return v

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Subject cannot be empty")
        return v


class ContactActivityUpdate(BaseModel):
    activity_type: str | None = None
    subject: str | None = None
    content: str | None = None
    contact_date: datetime | None = None
    reminder_date: datetime | None = None

    @field_validator("activity_type")
    @classmethod
    def activity_type_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_ACTIVITY_TYPES:
            raise ValueError(f"activity_type must be one of: {', '.join(VALID_ACTIVITY_TYPES)}")
        return v

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Subject cannot be empty")
        return v


class ContactActivityResponse(BaseModel):
    id: uuid.UUID
    manufacturer_id: uuid.UUID
    user_id: uuid.UUID
    activity_type: str
    subject: str
    content: str | None
    contact_date: datetime
    reminder_date: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
