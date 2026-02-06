"""Extract structured manufacturer data from HTML using Claude."""

import json
from typing import Dict, List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from models.manufacturer import ContactInfo, Manufacturer
from utils.llm import get_client

console = Console()


class DataExtractor:
    """Extracts structured manufacturer data from scraped HTML."""

    def __init__(self):
        """Initialize the data extractor."""
        self.client = get_client()
        self.failed_extractions = []  # Track extraction failures

    def extract(self, scraped_data: Dict[str, str]) -> List[Manufacturer]:
        """
        Extract manufacturer data from scraped content.

        Args:
            scraped_data: Dictionary mapping URLs to HTML content

        Returns:
            List of Manufacturer objects
        """
        console.print(
            f"\n[bold cyan]Step 5: Extracting Manufacturer Data[/bold cyan] ({len(scraped_data)} sites)\n"
        )

        manufacturers = []
        self.failed_extractions = []  # Reset failures list

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Extracting data...", total=len(scraped_data))

            for url, content in scraped_data.items():
                progress.update(
                    task, description=f"Extracting: {url[:40]}...", advance=0
                )

                try:
                    manufacturer = self._extract_from_content(url, content)
                    if manufacturer:
                        manufacturers.append(manufacturer)
                except Exception as e:
                    error_msg = str(e)

                    # Categorize extraction errors
                    if "validation error" in error_msg.lower():
                        error_reason = f"Data validation failed - {error_msg[:100]}"
                    elif "json" in error_msg.lower():
                        error_reason = "Invalid JSON response from LLM"
                    else:
                        error_reason = error_msg[:150]

                    console.print(f"  [yellow]✗ Extraction failed for {url}[/yellow]")
                    console.print(f"    [dim]{error_reason}[/dim]")

                    self.failed_extractions.append((url, error_reason))

                progress.advance(task)

        console.print(
            f"\n[green]✓ Extracted data from {len(manufacturers)} manufacturers[/green]\n"
        )

        return manufacturers

    def _extract_from_content(self, url: str, content: str) -> Manufacturer:
        """
        Extract manufacturer data from a single page's content.

        Args:
            url: Source URL
            content: Cleaned text content from the page

        Returns:
            Manufacturer object
        """
        system_prompt = """You are an expert at extracting manufacturer information from website content.

Extract the following information from the provided text:
- Company name
- Location (city, country)
- Contact email
- Contact phone
- Physical address
- Materials they work with (list)
- Production methods/capabilities (list)
- Minimum Order Quantity (MOQ) as an integer
- Certifications (list)

Return ONLY a JSON object with these fields. If information is not found, use null for strings/integers or empty arrays for lists.

Example output:
{
  "name": "ABC Manufacturing",
  "location": "Los Angeles, USA",
  "email": "info@abc.com",
  "phone": "+1-555-0100",
  "address": "123 Main St, LA, CA 90001",
  "materials": ["recycled polyester", "organic cotton"],
  "production_methods": ["sublimation printing", "screen printing"],
  "moq": 500,
  "certifications": ["OEKO-TEX", "GOTS"]
}"""

        extraction_prompt = f"""Extract manufacturer information from this website content:

URL: {url}

Content:
{content[:8000]}

Return ONLY valid JSON, no markdown or explanation."""

        response = self.client.create_message(
            messages=[{"role": "user", "content": extraction_prompt}],
            system=system_prompt,
            max_tokens=2000,
            temperature=0,
        )

        response_text = self.client.extract_text_response(response)

        # Clean up markdown if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(response_text)

            # Validate and clean the name field
            name = data.get("name")
            if not name or not isinstance(name, str) or name.strip() == "":
                # Name is missing, null, or invalid - use fallback
                name = self._extract_name_fallback(content, url)

            # Validate other string fields
            location = data.get("location")
            if location and not isinstance(location, str):
                location = None

            # Validate list fields
            materials = data.get("materials", [])
            if not isinstance(materials, list):
                materials = []

            production_methods = data.get("production_methods", [])
            if not isinstance(production_methods, list):
                production_methods = []

            certifications = data.get("certifications", [])
            if not isinstance(certifications, list):
                certifications = []

            # Validate MOQ
            moq = data.get("moq")
            if moq is not None and not isinstance(moq, (int, float)):
                moq = None

            # Build Manufacturer object with validated data
            manufacturer = Manufacturer(
                name=name,
                website=url,
                location=location,
                contact=ContactInfo(
                    email=data.get("email") if isinstance(data.get("email"), str) else None,
                    phone=data.get("phone") if isinstance(data.get("phone"), str) else None,
                    address=data.get("address") if isinstance(data.get("address"), str) else None,
                ),
                materials=materials,
                production_methods=production_methods,
                moq=int(moq) if moq is not None else None,
                certifications=certifications,
                source_url=url,
                confidence="medium",  # Will be refined by evaluator
            )

            return manufacturer

        except (json.JSONDecodeError, ValueError) as e:
            # If parsing fails, create a minimal manufacturer object
            console.print(f"  [yellow]JSON parsing failed for {url}[/yellow]")
            return Manufacturer(
                name=self._extract_name_fallback(content, url),
                website=url,
                source_url=url,
                confidence="low",
            )

    def _extract_name_fallback(self, content: str, url: str) -> str:
        """
        Extract company name using simple heuristics if LLM extraction fails.

        Args:
            content: Page content
            url: Source URL

        Returns:
            Company name (or domain name as fallback)
        """
        from urllib.parse import urlparse

        # Try to find company name in first few lines
        lines = content.split("\n")[:10]
        for line in lines:
            if len(line) > 5 and len(line) < 100:
                # Simple heuristic: first reasonably-sized line might be company name
                return line.strip()

        # Fallback to domain name
        domain = urlparse(url).netloc.replace("www.", "")
        return domain.split(".")[0].title()
