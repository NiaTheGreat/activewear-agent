#!/usr/bin/env python3
"""
Activewear Manufacturer Research Agent

An AI agent that finds and evaluates activewear manufacturers
based on custom search criteria.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config import settings

console = Console()


def print_welcome():
    """Display welcome message."""
    welcome_text = Text()
    welcome_text.append("Activewear Manufacturer Research Agent\n\n", style="bold cyan")
    welcome_text.append(
        "This agent will help you find manufacturers that match your criteria.\n",
        style="white",
    )
    welcome_text.append(
        "We'll search the web, scrape manufacturer sites, and rank them by fit.\n\n",
        style="white",
    )
    welcome_text.append("Budget: ", style="white")
    welcome_text.append(f"${settings.BUDGET_LIMIT_USD}", style="green bold")
    welcome_text.append(" | Max Results: ", style="white")
    welcome_text.append(f"{settings.MAX_MANUFACTURERS}", style="green bold")

    console.print(Panel(welcome_text, border_style="cyan", padding=(1, 2)))


def ask_mode() -> str:
    """Ask user which mode to run."""
    console.print()
    console.print("[bold]What would you like to do?[/bold]\n")
    console.print("  [cyan]1[/cyan] - New search (find new manufacturers)")
    console.print("  [cyan]2[/cyan] - Rescore existing (re-evaluate manufacturers_scores.xlsx)")
    console.print()

    while True:
        choice = console.input("[bold]Enter choice (1 or 2):[/bold] ").strip()
        if choice in ("1", "2"):
            return choice
        console.print("[yellow]Please enter 1 or 2.[/yellow]")


def main():
    """Main entry point for the application."""
    try:
        # Validate settings
        settings.validate()

        # Print welcome message
        print_welcome()

        # Import agent
        from agent.core import ManufacturerResearchAgent

        agent = ManufacturerResearchAgent()

        # Ask which mode
        mode = ask_mode()

        if mode == "2":
            output_path = agent.rescore()
        else:
            output_path = agent.run()

        # Success message
        console.print(
            f"\n[bold green]All done![/bold green] Open your report at:\n  {output_path}\n"
        )

    except ValueError as e:
        console.print(f"\n[red]Error:[/red] {e}\n", style="bold")
        console.print(
            "[yellow]Please create a .env file with your ANTHROPIC_API_KEY.[/yellow]"
        )
        console.print(
            f"[dim]Example: cp .env.example .env (then edit the file)[/dim]\n"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Agent interrupted by user.[/yellow]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error:[/red] {e}\n", style="bold")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
