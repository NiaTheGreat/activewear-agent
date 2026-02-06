"""Evaluate and score manufacturers against search criteria."""

from typing import List

from rich.console import Console

from models.criteria import SearchCriteria
from models.manufacturer import Manufacturer

console = Console()


class Evaluator:
    """Evaluates manufacturers against search criteria and assigns match scores."""

    def __init__(self):
        """Initialize the evaluator."""
        pass

    def evaluate(
        self, manufacturers: List[Manufacturer], criteria: SearchCriteria
    ) -> List[Manufacturer]:
        """
        Evaluate manufacturers against criteria and assign match scores.

        Scoring breakdown (0-100 total):
        - Location match: 20 points
        - MOQ match: 20 points
        - Certifications: 20 points
        - Materials: 20 points
        - Production methods: 20 points

        Args:
            manufacturers: List of Manufacturer objects to evaluate
            criteria: SearchCriteria to evaluate against

        Returns:
            List of Manufacturer objects with updated match_score, confidence, and notes
        """
        console.print(
            f"\n[bold cyan]Step 6: Evaluating Manufacturers[/bold cyan] ({len(manufacturers)} candidates)\n"
        )

        for manufacturer in manufacturers:
            # Calculate scores for each category
            location_score = self._score_location(manufacturer, criteria)
            moq_score = self._score_moq(manufacturer, criteria)
            cert_score = self._score_certifications(manufacturer, criteria)
            materials_score = self._score_materials(manufacturer, criteria)
            methods_score = self._score_production_methods(manufacturer, criteria)

            # Total score (0-100)
            total_score = (
                location_score + moq_score + cert_score + materials_score + methods_score
            )

            # Update manufacturer
            manufacturer.match_score = round(total_score, 1)
            manufacturer.confidence = self._assess_confidence(manufacturer)
            manufacturer.notes = self._generate_notes(
                manufacturer,
                criteria,
                location_score,
                moq_score,
                cert_score,
                materials_score,
                methods_score,
            )

        # Sort by match score (descending)
        manufacturers.sort(key=lambda m: m.match_score, reverse=True)

        # Display top matches
        console.print("[bold]Top Matches:[/bold]")
        for i, mfr in enumerate(manufacturers[:5], 1):
            console.print(
                f"  {i}. {mfr.name} - [green]{mfr.match_score}[/green] ({mfr.confidence})"
            )

        console.print()

        return manufacturers

    def _score_location(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> float:
        """Score location match (0-20 points)."""
        if not criteria.locations:
            return 20.0  # No preference, full points

        if not manufacturer.location:
            return 0.0  # No location data

        # Check if any preferred location is in manufacturer's location
        location_lower = manufacturer.location.lower()
        for pref_location in criteria.locations:
            if pref_location.lower() in location_lower:
                return 20.0

        return 0.0

    def _score_moq(self, manufacturer: Manufacturer, criteria: SearchCriteria) -> float:
        """Score MOQ match (0-20 points)."""
        if criteria.moq_min is None and criteria.moq_max is None:
            return 20.0  # No MOQ preference

        if manufacturer.moq is None:
            return 5.0  # Unknown MOQ, give some points

        moq = manufacturer.moq

        # Check if within range
        if criteria.moq_min and moq < criteria.moq_min:
            return 5.0  # MOQ too low (might still work)

        if criteria.moq_max and moq > criteria.moq_max:
            # MOQ too high - penalize more
            if moq > criteria.moq_max * 2:
                return 0.0
            else:
                return 5.0

        # Within range
        return 20.0

    def _score_certifications(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> float:
        """Score certifications match (0-20 points)."""
        if not criteria.required_certifications and not criteria.preferred_certifications:
            return 20.0  # No certification requirements

        if not manufacturer.certifications:
            # No certifications listed
            if criteria.required_certifications:
                return 0.0  # Required certs missing
            else:
                return 10.0  # Only preferred certs, give partial

        mfr_certs_lower = [c.lower() for c in manufacturer.certifications]

        score = 0.0

        # Check required certifications (15 points)
        if criteria.required_certifications:
            required_lower = [c.lower() for c in criteria.required_certifications]
            matches = sum(1 for cert in required_lower if cert in mfr_certs_lower)
            score += (matches / len(required_lower)) * 15.0

        else:
            score += 15.0  # No required certs, full points

        # Check preferred certifications (5 points)
        if criteria.preferred_certifications:
            preferred_lower = [c.lower() for c in criteria.preferred_certifications]
            matches = sum(1 for cert in preferred_lower if cert in mfr_certs_lower)
            score += (matches / len(preferred_lower)) * 5.0
        else:
            score += 5.0  # No preferred certs, full points

        return score

    def _score_materials(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> float:
        """Score materials match (0-20 points)."""
        if not criteria.materials:
            return 20.0  # No material preferences

        if not manufacturer.materials:
            return 5.0  # No materials listed, give some points

        mfr_materials_lower = [m.lower() for m in manufacturer.materials]
        criteria_materials_lower = [m.lower() for m in criteria.materials]

        # Count matches
        matches = sum(
            1 for mat in criteria_materials_lower if mat in mfr_materials_lower
        )

        # Partial credit for each match
        score = (matches / len(criteria_materials_lower)) * 20.0

        return score

    def _score_production_methods(
        self, manufacturer: Manufacturer, criteria: SearchCriteria
    ) -> float:
        """Score production methods match (0-20 points)."""
        if not criteria.production_methods:
            return 20.0  # No method preferences

        if not manufacturer.production_methods:
            return 5.0  # No methods listed, give some points

        mfr_methods_lower = [m.lower() for m in manufacturer.production_methods]
        criteria_methods_lower = [m.lower() for m in criteria.production_methods]

        # Count matches
        matches = sum(
            1 for method in criteria_methods_lower if method in mfr_methods_lower
        )

        # Partial credit for each match
        score = (matches / len(criteria_methods_lower)) * 20.0

        return score

    def _assess_confidence(self, manufacturer: Manufacturer) -> str:
        """
        Assess confidence in the extracted data.

        Args:
            manufacturer: Manufacturer object

        Returns:
            Confidence level: "low", "medium", or "high"
        """
        # Count how many fields have data
        fields_with_data = 0
        total_fields = 8

        if manufacturer.location:
            fields_with_data += 1
        if manufacturer.contact.email:
            fields_with_data += 1
        if manufacturer.contact.phone:
            fields_with_data += 1
        if manufacturer.materials:
            fields_with_data += 1
        if manufacturer.production_methods:
            fields_with_data += 1
        if manufacturer.moq is not None:
            fields_with_data += 1
        if manufacturer.certifications:
            fields_with_data += 1
        if manufacturer.contact.address:
            fields_with_data += 1

        # Determine confidence based on data completeness
        completeness = fields_with_data / total_fields

        if completeness >= 0.6:
            return "high"
        elif completeness >= 0.3:
            return "medium"
        else:
            return "low"

    def _generate_notes(
        self,
        manufacturer: Manufacturer,
        criteria: SearchCriteria,
        location_score: float,
        moq_score: float,
        cert_score: float,
        materials_score: float,
        methods_score: float,
    ) -> str:
        """
        Generate notes highlighting strengths and weaknesses.

        Args:
            manufacturer: Manufacturer object
            criteria: SearchCriteria
            *_score: Individual category scores

        Returns:
            Notes string
        """
        notes = []

        # Strengths
        if location_score == 20.0:
            notes.append("✓ Located in preferred region")
        if moq_score == 20.0:
            notes.append("✓ MOQ within acceptable range")
        if cert_score >= 15.0:
            notes.append("✓ Has required certifications")
        if materials_score >= 15.0:
            notes.append("✓ Works with desired materials")
        if methods_score >= 15.0:
            notes.append("✓ Has required production capabilities")

        # Weaknesses
        if location_score == 0.0 and criteria.locations:
            notes.append("✗ Location not in preferred regions")
        if moq_score < 10.0 and criteria.moq_max:
            notes.append("✗ MOQ may be too high")
        if cert_score < 10.0 and criteria.required_certifications:
            notes.append("✗ Missing required certifications")
        if materials_score < 10.0 and criteria.materials:
            notes.append("✗ Limited material capabilities")
        if methods_score < 10.0 and criteria.production_methods:
            notes.append("✗ Limited production methods")

        # Data quality
        if manufacturer.confidence == "low":
            notes.append("⚠ Limited data available")

        return " | ".join(notes) if notes else "No specific notes"
