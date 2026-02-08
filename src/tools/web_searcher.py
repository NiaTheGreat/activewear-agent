"""Web search functionality to find manufacturer URLs."""

import time
from typing import List, Optional, Set
from urllib.parse import urlparse

import requests
from rich.console import Console

from config import settings

console = Console()


class WebSearcher:
    """Searches the web for manufacturer URLs."""

    def __init__(self):
        """Initialize the web searcher."""
        self.found_urls: Set[str] = set()

    def search(self, queries: List[str], max_urls: Optional[int] = None) -> List[str]:
        """
        Execute search queries and extract manufacturer URLs.

        Args:
            queries: List of search query strings
            max_urls: Maximum number of URLs to collect (defaults to MAX_URLS_TO_SCRAPE)

        Returns:
            List of unique manufacturer URLs (up to max_urls)
        """
        if max_urls is None:
            max_urls = settings.MAX_URLS_TO_SCRAPE
        console.print(
            f"\n[bold cyan]Step 3: Searching for Manufacturers[/bold cyan] ({len(queries)} queries)\n"
        )

        for i, query in enumerate(queries, 1):
            console.print(f"  [{i}/{len(queries)}] Searching: [dim]{query}[/dim]")

            try:
                urls = self._search_google(query)
                self.found_urls.update(urls)

                console.print(
                    f"      [green]Found {len(urls)} URLs[/green] (total: {len(self.found_urls)})"
                )

                # Rate limiting between searches
                if i < len(queries):
                    time.sleep(settings.REQUEST_DELAY_SECONDS)

            except Exception as e:
                console.print(f"      [yellow]Search failed: {e}[/yellow]")
                continue

            # Stop if we have enough URLs
            if len(self.found_urls) >= max_urls:
                console.print(
                    f"\n[green]✓ Found {len(self.found_urls)} URLs (target reached)[/green]"
                )
                break

        # Clean and deduplicate URLs
        cleaned_urls = self._clean_and_filter_urls(list(self.found_urls))

        # Limit to max_urls
        final_urls = cleaned_urls[:max_urls]

        console.print(f"\n[green]✓ Total unique URLs: {len(final_urls)}[/green]\n")

        return final_urls

    def _search_google(self, query: str) -> List[str]:
        """
        Perform a web search using Brave Search API and extract URLs.

        Args:
            query: Search query string

        Returns:
            List of URLs from search results
        """
        # Check if Brave API key is configured
        if not settings.BRAVE_API_KEY:
            console.print(
                "  [yellow]⚠️  Brave Search API not configured[/yellow]"
            )
            console.print(
                "  [dim]See BRAVE_SEARCH_SETUP.md for setup instructions[/dim]"
            )
            return []

        # Brave Search API
        search_url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": settings.BRAVE_API_KEY,
            "Accept": "application/json",
        }
        params = {
            "q": query,
            "count": 10,  # Number of results per query
        }

        try:
            response = requests.get(
                search_url,
                headers=headers,
                params=params,
                timeout=settings.SCRAPE_TIMEOUT_SECONDS,
            )
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract URLs from search results
            urls = []
            if "web" in data and "results" in data["web"]:
                for item in data["web"]["results"]:
                    url = item.get("url")
                    if url:
                        urls.append(url)

            return urls

        except requests.RequestException as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                console.print(
                    "  [yellow]✗ Invalid Brave API key[/yellow]"
                )
            elif "403" in error_msg:
                console.print(
                    "  [yellow]✗ Brave API access forbidden - check your subscription[/yellow]"
                )
            elif "429" in error_msg or "quota" in error_msg.lower():
                console.print("  [yellow]✗ Brave API quota exceeded[/yellow]")
            else:
                console.print(f"  [yellow]✗ Search API error: {error_msg[:100]}[/yellow]")
            return []


    def manual_input(self, skip_prompt: bool = False, max_count: Optional[int] = None) -> List[str]:
        """
        Allow user to manually input manufacturer URLs.

        Args:
            skip_prompt: If True, skip the initial yes/no prompt (user already chose)
            max_count: Maximum number of URLs to collect (defaults to settings.MAX_MANUFACTURERS)

        Returns:
            List of manually entered URLs
        """
        if max_count is None:
            max_count = settings.MAX_MANUFACTURERS
        if not skip_prompt:
            console.print(
                "\n[yellow]⚠️  Web search returned no results.[/yellow]"
            )
            console.print(
                "[cyan]You can manually enter manufacturer URLs instead.[/cyan]\n"
            )

            use_manual = console.input(
                "[bold]Enter URLs manually? (y/N):[/bold] "
            ).lower()

            if use_manual != "y":
                return []

        console.print(
            f"\n[dim]Enter up to {max_count} manufacturer website URLs.[/dim]"
        )
        console.print(
            "[dim]Paste each URL and press Enter. Type 'done' when finished.[/dim]\n"
        )

        urls = []
        count = 1

        while len(urls) < max_count:
            url = console.input(f"[bold]URL {count}:[/bold] ").strip()

            if url.lower() == "done":
                break

            if not url:
                continue

            # Add https:// if missing
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Validate URL format
            try:
                parsed = urlparse(url)
                if parsed.netloc:
                    urls.append(url)
                    console.print(f"  [green]✓ Added {url}[/green]")
                    count += 1
                else:
                    console.print(f"  [yellow]✗ Invalid URL format[/yellow]")
            except Exception:
                console.print(f"  [yellow]✗ Invalid URL format[/yellow]")

        if urls:
            console.print(
                f"\n[green]✓ Added {len(urls)} URLs manually[/green]\n"
            )
        else:
            console.print("\n[yellow]No URLs added.[/yellow]\n")

        return urls

    def _clean_and_filter_urls(self, urls: List[str]) -> List[str]:
        """
        Clean and filter URLs to keep only likely manufacturer sites.

        Args:
            urls: Raw list of URLs

        Returns:
            Filtered and cleaned list of URLs
        """
        cleaned = []
        seen_domains = set()
        seen_urls = set()

        # B2B platforms host many suppliers on one domain — deduplicate
        # by full URL path instead of just the domain for these sites.
        b2b_platforms = ["alibaba", "indiamart", "made-in-china", "globalsources"]

        # Skip non-manufacturer domains (social media, search engines)
        skip_domains = [
            "google",
            "facebook",
            "linkedin",
            "instagram",
            "twitter",
            "youtube",
            "pinterest",
            "reddit",
            "wikipedia",
        ]

        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower().replace("www.", "")

                if any(skip in domain for skip in skip_domains):
                    continue

                is_b2b = any(plat in domain for plat in b2b_platforms)

                # Clean up URL
                clean_url = f"{parsed.scheme}://{parsed.netloc}"
                if parsed.path and parsed.path != "/":
                    clean_url += parsed.path

                if is_b2b:
                    # For B2B platforms, deduplicate by full URL (each path = different supplier)
                    if clean_url in seen_urls:
                        continue
                    seen_urls.add(clean_url)
                else:
                    # For standalone sites, deduplicate by domain
                    if domain in seen_domains:
                        continue
                    seen_domains.add(domain)

                cleaned.append(clean_url)

            except Exception:
                continue

        return cleaned
