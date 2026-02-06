"""Interactive criteria collection using Claude for conversational Q&A."""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from models.criteria import SearchCriteria
from utils.llm import get_client

console = Console()


class CriteriaCollector:
    """Collects manufacturer search criteria through interactive Q&A."""

    def __init__(self):
        """Initialize the criteria collector."""
        self.client = get_client()
        self.conversation_history = []

    def collect(self) -> SearchCriteria:
        """
        Collect search criteria through interactive conversation.

        Returns:
            SearchCriteria object populated with user's requirements
        """
        console.print("\n[bold cyan]Step 1: Collecting Your Requirements[/bold cyan]\n")

        # Check if user wants to load a preset
        presets = SearchCriteria.list_presets()
        if presets:
            console.print("[yellow]Available presets:[/yellow]")
            for preset in presets:
                console.print(f"  • {preset}")
            console.print()

            load_preset = console.input(
                "[bold]Load an existing preset? (y/N):[/bold] "
            ).lower()

            if load_preset == "y":
                preset_name = console.input("[bold]Enter preset name:[/bold] ")
                try:
                    criteria = SearchCriteria.load_preset(preset_name)
                    console.print(
                        f"\n[green]✓ Loaded preset '{preset_name}'[/green]\n"
                    )
                    console.print(Panel(criteria.to_summary(), title="Your Criteria"))
                    return criteria
                except FileNotFoundError:
                    console.print(
                        f"[red]Preset '{preset_name}' not found. Starting fresh...[/red]\n"
                    )

        # Start interactive Q&A
        console.print(
            "[dim]I'll ask you a few questions to understand your requirements.[/dim]\n"
        )

        system_prompt = """You are a helpful assistant collecting manufacturer search criteria.

Ask the user questions ONE AT A TIME to gather the following information:
1. Preferred manufacturing locations (countries/regions)
2. Minimum Order Quantity (MOQ) range (min and max)
3. Required certifications (e.g., GOTS, OEKO-TEX, Fair Trade)
4. Preferred certifications (nice to have)
5. Desired materials (e.g., recycled polyester, organic cotton)
6. Required production methods (e.g., sublimation printing, screen printing)
7. Budget tier (budget, mid-range, or premium)
8. Any additional notes or requirements

Keep questions conversational and brief. Accept natural language responses.
After gathering all information, respond with EXACTLY: "CRITERIA_COMPLETE"
Do NOT ask all questions at once - ask them one by one, waiting for responses."""

        self.conversation_history = [
            {
                "role": "user",
                "content": "Hi! I need help finding activewear manufacturers. Can you help me define my search criteria?",
            }
        ]

        # Collected data
        criteria_data = {
            "locations": [],
            "moq_min": None,
            "moq_max": None,
            "required_certifications": [],
            "preferred_certifications": [],
            "materials": [],
            "production_methods": [],
            "budget_tier": None,
            "additional_notes": None,
        }

        while True:
            # Get Claude's next question
            response = self.client.create_message(
                messages=self.conversation_history,
                system=system_prompt,
                max_tokens=500,
                temperature=0.7,
            )

            assistant_message = self.client.extract_text_response(response)

            # Check if collection is complete
            if "CRITERIA_COMPLETE" in assistant_message:
                break

            # Display Claude's question
            console.print(f"[cyan]Agent:[/cyan] {assistant_message}\n")

            # Get user's answer
            user_response = console.input("[bold]You:[/bold] ")
            console.print()

            # Add to conversation history
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )
            self.conversation_history.append(
                {"role": "user", "content": user_response}
            )

        # Extract structured data from conversation
        criteria_data = self._extract_criteria_from_conversation()

        # Create SearchCriteria object
        criteria = SearchCriteria(**criteria_data)

        # Display summary
        console.print(Panel(criteria.to_summary(), title="Your Criteria"))

        # Offer to save as preset
        save_preset = console.input(
            "\n[bold]Save these criteria as a preset? (y/N):[/bold] "
        ).lower()

        if save_preset == "y":
            preset_name = console.input("[bold]Enter preset name:[/bold] ")
            criteria.save_preset(preset_name)
            console.print(f"[green]✓ Saved as '{preset_name}'[/green]\n")

        return criteria

    def _extract_criteria_from_conversation(self) -> dict:
        """
        Extract structured criteria from the conversation history.

        Returns:
            Dictionary with criteria fields
        """
        # Build extraction prompt
        conversation_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.conversation_history
        )

        extraction_prompt = f"""Based on this conversation, extract the manufacturer search criteria.

Conversation:
{conversation_text}

Extract and return ONLY a JSON object with these fields:
- locations: array of strings (countries/regions mentioned)
- moq_min: integer or null (minimum MOQ mentioned)
- moq_max: integer or null (maximum MOQ mentioned)
- required_certifications: array of strings (must-have certifications)
- preferred_certifications: array of strings (nice-to-have certifications)
- materials: array of strings (desired materials)
- production_methods: array of strings (production capabilities needed)
- budget_tier: "budget", "mid-range", "premium", or null
- additional_notes: string or null (any other requirements)

Return ONLY valid JSON, no markdown formatting or explanation."""

        response = self.client.create_message(
            messages=[{"role": "user", "content": extraction_prompt}],
            max_tokens=1000,
            temperature=0,
        )

        json_text = self.client.extract_text_response(response)

        # Remove markdown code blocks if present
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()

        import json

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            console.print(
                "[yellow]Warning: Could not parse criteria. Using defaults.[/yellow]"
            )
            return {
                "locations": [],
                "moq_min": None,
                "moq_max": None,
                "required_certifications": [],
                "preferred_certifications": [],
                "materials": [],
                "production_methods": [],
                "budget_tier": None,
                "additional_notes": None,
            }
