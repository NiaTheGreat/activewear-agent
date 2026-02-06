"""Notion database integration for manufacturer data."""

from datetime import datetime
from typing import List, Optional, Set
from zoneinfo import ZoneInfo

from rich.console import Console

from config import settings
from models.manufacturer import Manufacturer

console = Console()


class NotionUploader:
    """Uploads manufacturer data to Notion database."""

    def __init__(self):
        """Initialize the Notion uploader."""
        self.client = None
        self.database_id = settings.NOTION_DATABASE_ID

        # Only import and initialize if Notion is enabled
        if settings.NOTION_ENABLED:
            try:
                from notion_client import Client
                self.client = Client(auth=settings.NOTION_API_TOKEN)
            except ImportError:
                console.print(
                    "[yellow]⚠️  notion-client not installed. Run: pip install notion-client[/yellow]"
                )
                self.client = None
            except Exception as e:
                console.print(f"[yellow]⚠️  Notion initialization failed: {e}[/yellow]")
                self.client = None

    def is_enabled(self) -> bool:
        """Check if Notion integration is enabled and configured."""
        return (
            settings.NOTION_ENABLED
            and self.client is not None
            and self.database_id
        )

    def sync_manufacturers(self, manufacturers: List[Manufacturer]) -> Optional[int]:
        """
        Sync manufacturers to Notion database.
        Only adds manufacturers with unique URLs (deduplication).

        Args:
            manufacturers: List of Manufacturer objects to sync

        Returns:
            Number of new manufacturers added, or None if sync failed
        """
        if not self.is_enabled():
            return None

        console.print("\n[bold cyan]Syncing to Notion...[/bold cyan]")

        try:
            # Get existing URLs from Notion database
            existing_urls = self._get_existing_urls()
            console.print(f"[dim]Found {len(existing_urls)} existing manufacturers in Notion[/dim]")

            # Filter to only new manufacturers
            new_manufacturers = [
                m for m in manufacturers
                if m.source_url not in existing_urls
            ]

            if not new_manufacturers:
                console.print("[dim]No new manufacturers to add to Notion (all URLs already exist)[/dim]\n")
                return 0

            # Add new manufacturers
            console.print(f"[cyan]Adding {len(new_manufacturers)} new manufacturers to Notion...[/cyan]")

            added_count = 0
            for manufacturer in new_manufacturers:
                try:
                    self._create_page(manufacturer)
                    added_count += 1
                except Exception as e:
                    console.print(
                        f"[yellow]✗ Failed to add {manufacturer.name}: {str(e)[:100]}[/yellow]"
                    )

            console.print(
                f"[green]✓ Notion sync complete:[/green] {added_count} manufacturers added\n"
            )
            return added_count

        except Exception as e:
            console.print(f"[yellow]⚠️  Notion sync failed: {e}[/yellow]\n")
            return None

    def _get_existing_urls(self) -> Set[str]:
        """
        Query Notion database to get all existing manufacturer URLs.

        Returns:
            Set of existing Source URLs
        """
        existing_urls = set()

        try:
            # Query all pages in the database
            has_more = True
            start_cursor = None

            while has_more:
                query_params = {
                    "database_id": self.database_id,
                    "page_size": 100,
                }

                if start_cursor:
                    query_params["start_cursor"] = start_cursor

                response = self.client.databases.query(**query_params)

                # Extract URLs from each page
                for page in response["results"]:
                    properties = page["properties"]

                    # Get Source URL property
                    if "Source URL" in properties:
                        url_prop = properties["Source URL"]
                        if url_prop["type"] == "url" and url_prop["url"]:
                            existing_urls.add(url_prop["url"])

                has_more = response["has_more"]
                start_cursor = response.get("next_cursor")

        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch existing URLs from Notion: {e}[/yellow]")

        return existing_urls

    def _create_page(self, manufacturer: Manufacturer) -> None:
        """
        Create a new page in the Notion database for a manufacturer.

        Args:
            manufacturer: Manufacturer object to add
        """
        # Get manufacturer data
        row_data = manufacturer.to_excel_row()

        # Get current timestamp (Central Time)
        central_tz = ZoneInfo("America/Chicago")
        date_added = datetime.now(central_tz).isoformat()

        # Build Notion properties
        # Note: Notion property types must match database schema
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": row_data.get("Name") or "Unknown"
                        }
                    }
                ]
            },
            "Match Score": {
                "number": row_data.get("Match Score", 0)
            },
            "Location": {
                "rich_text": [
                    {
                        "text": {
                            "content": row_data.get("Location") or ""
                        }
                    }
                ]
            },
            "Website": {
                "url": row_data.get("Website") or None
            },
            "MOQ": {
                "rich_text": [
                    {
                        "text": {
                            "content": row_data.get("MOQ") or ""
                        }
                    }
                ]
            },
            "Confidence": {
                "rich_text": [
                    {
                        "text": {
                            "content": row_data.get("Confidence") or ""
                        }
                    }
                ]
            },
            "Materials": {
                "rich_text": [
                    {
                        "text": {
                            "content": (row_data.get("Materials") or "")[:2000]  # Notion limit
                        }
                    }
                ]
            },
            "Certifications": {
                "rich_text": [
                    {
                        "text": {
                            "content": (row_data.get("Certifications") or "")[:2000]
                        }
                    }
                ]
            },
            "Production Methods": {
                "rich_text": [
                    {
                        "text": {
                            "content": (row_data.get("Production Methods") or "")[:2000]
                        }
                    }
                ]
            },
            "Email": {
                "email": row_data.get("Email") or None
            },
            "Phone": {
                "phone_number": row_data.get("Phone") or None
            },
            "Address": {
                "rich_text": [
                    {
                        "text": {
                            "content": (row_data.get("Address") or "")[:2000]
                        }
                    }
                ]
            },
            "Notes": {
                "rich_text": [
                    {
                        "text": {
                            "content": (row_data.get("Notes") or "")[:2000]
                        }
                    }
                ]
            },
            "Source URL": {
                "url": row_data.get("Source URL") or manufacturer.source_url
            },
            "Date Added": {
                "date": {
                    "start": date_added
                }
            },
        }

        # Create the page in the database
        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
        )
