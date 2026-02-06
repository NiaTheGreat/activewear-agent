"""Manufacturer data model."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ContactInfo(BaseModel):
    """Contact information for a manufacturer."""

    email: Optional[str] = Field(default=None, description="Contact email address")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    address: Optional[str] = Field(default=None, description="Physical address")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Basic email validation."""
        if v and "@" not in v:
            return None  # Invalid email, return None instead of raising
        return v


class Manufacturer(BaseModel):
    """Model representing a manufacturer with evaluation metrics."""

    name: str = Field(description="Company name")
    website: str = Field(description="Company website URL")
    location: Optional[str] = Field(
        default=None, description="Location (city, country)"
    )
    contact: ContactInfo = Field(
        default_factory=ContactInfo, description="Contact information"
    )
    materials: List[str] = Field(
        default_factory=list, description="Materials they work with"
    )
    production_methods: List[str] = Field(
        default_factory=list, description="Production capabilities/methods"
    )
    moq: Optional[int] = Field(
        default=None, description="Minimum order quantity", ge=0
    )
    certifications: List[str] = Field(
        default_factory=list, description="Certifications held"
    )
    match_score: float = Field(
        default=0.0, description="Match score against criteria (0-100)", ge=0, le=100
    )
    confidence: str = Field(
        default="low",
        description="Confidence in extracted data: low, medium, or high",
        pattern="^(low|medium|high)$",
    )
    notes: Optional[str] = Field(
        default=None, description="Strengths, weaknesses, or other observations"
    )
    source_url: str = Field(description="URL where data was scraped from")
    scraped_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp of scraping"
    )

    @property
    def rank_display(self) -> str:
        """Display format for ranking (score + confidence)."""
        return f"{self.match_score:.1f} ({self.confidence})"

    def to_excel_row(self) -> dict:
        """
        Convert manufacturer to dictionary for Excel export.

        Returns:
            Dictionary with keys matching Excel column headers
        """
        return {
            "Rank": 0,  # Will be set during sorting
            "Name": self.name,
            "Location": self.location or "Unknown",
            "Website": self.website,
            "MOQ": self.moq if self.moq is not None else "Unknown",
            "Match Score": self.match_score,
            "Confidence": self.confidence,
            "Materials": ", ".join(self.materials) if self.materials else "Unknown",
            "Certifications": (
                ", ".join(self.certifications) if self.certifications else "None listed"
            ),
            "Production Methods": (
                ", ".join(self.production_methods)
                if self.production_methods
                else "Unknown"
            ),
            "Email": self.contact.email or "Unknown",
            "Phone": self.contact.phone or "Unknown",
            "Address": self.contact.address or "Unknown",
            "Notes": self.notes or "",
            "Source URL": self.source_url,
        }

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
