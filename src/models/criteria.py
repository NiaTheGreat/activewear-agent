"""Search criteria data model."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator

from config import PRESETS_DIR


class SearchCriteria(BaseModel):
    """Model representing manufacturer search criteria."""

    locations: List[str] = Field(
        default_factory=list,
        description="Desired countries/regions (e.g., USA, China, Vietnam)",
    )
    moq_min: Optional[int] = Field(
        default=None, description="Minimum order quantity (lower bound)", ge=0
    )
    moq_max: Optional[int] = Field(
        default=None, description="Maximum order quantity (upper bound)", ge=0
    )
    certifications_of_interest: List[str] = Field(
        default_factory=list,
        description="Certifications of interest (e.g., GOTS, OEKO-TEX, Fair Trade). Used for informational purposes, not penalty-based scoring.",
    )
    preferred_certifications: List[str] = Field(
        default_factory=list,
        description="Nice-to-have certifications",
    )
    materials: List[str] = Field(
        default_factory=list,
        description="Desired materials (e.g., recycled polyester, organic cotton)",
    )
    production_methods: List[str] = Field(
        default_factory=list,
        description="Required production capabilities (e.g., sublimation, screen printing)",
    )
    budget_tier: List[str] = Field(
        default_factory=list,
        description="Budget categories (can be multiple): budget, mid-range, and/or premium",
    )
    additional_notes: Optional[str] = Field(
        default=None, description="Any additional requirements or preferences"
    )
    created_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="before")
    @classmethod
    def handle_deprecated_fields(cls, data: Any) -> Any:
        """Map deprecated 'required_certifications' to 'certifications_of_interest'."""
        if isinstance(data, dict):
            if "required_certifications" in data and "certifications_of_interest" not in data:
                data["certifications_of_interest"] = data.pop("required_certifications")
            elif "required_certifications" in data:
                data.pop("required_certifications")
        return data

    def save_preset(self, name: str) -> Path:
        """
        Save criteria as a reusable preset.

        Args:
            name: Name for the preset (without .json extension)

        Returns:
            Path to the saved preset file
        """
        preset_path = PRESETS_DIR / f"{name}.json"

        # Convert to dict and save
        with open(preset_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(mode="json"), f, indent=2, default=str)

        return preset_path

    @classmethod
    def load_preset(cls, name: str) -> "SearchCriteria":
        """
        Load criteria from a saved preset.

        Args:
            name: Name of the preset (without .json extension)

        Returns:
            SearchCriteria instance

        Raises:
            FileNotFoundError: If preset doesn't exist
        """
        preset_path = PRESETS_DIR / f"{name}.json"

        if not preset_path.exists():
            raise FileNotFoundError(f"Preset '{name}' not found at {preset_path}")

        with open(preset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def list_presets(cls) -> List[str]:
        """
        List all available preset names.

        Returns:
            List of preset names (without .json extension)
        """
        if not PRESETS_DIR.exists():
            return []

        return [p.stem for p in PRESETS_DIR.glob("*.json")]

    def to_summary(self) -> str:
        """
        Generate a human-readable summary of the criteria.

        Returns:
            Formatted string summarizing the criteria
        """
        summary_parts = []

        if self.locations:
            summary_parts.append(f"Locations: {', '.join(self.locations)}")

        if self.moq_min is not None or self.moq_max is not None:
            moq_range = []
            if self.moq_min is not None:
                moq_range.append(f"min: {self.moq_min}")
            if self.moq_max is not None:
                moq_range.append(f"max: {self.moq_max}")
            summary_parts.append(f"MOQ: {', '.join(moq_range)}")

        if self.certifications_of_interest:
            summary_parts.append(
                f"Certifications of Interest: {', '.join(self.certifications_of_interest)}"
            )

        if self.preferred_certifications:
            summary_parts.append(
                f"Preferred Certs: {', '.join(self.preferred_certifications)}"
            )

        if self.materials:
            summary_parts.append(f"Materials: {', '.join(self.materials)}")

        if self.production_methods:
            summary_parts.append(
                f"Production Methods: {', '.join(self.production_methods)}"
            )

        if self.budget_tier:
            summary_parts.append(f"Budget Tier: {', '.join(self.budget_tier)}")

        if self.additional_notes:
            summary_parts.append(f"Notes: {self.additional_notes}")

        return "\n".join(f"  • {part}" for part in summary_parts)
