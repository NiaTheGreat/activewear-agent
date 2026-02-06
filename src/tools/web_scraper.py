"""Web scraper for fetching manufacturer website content."""

import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import settings

console = Console()


class WebScraper:
    """Scrapes manufacturer websites to extract HTML content."""

    def __init__(self):
        """Initialize the web scraper."""
        self.session = requests.Session()
        self.failed_urls = []  # Track failed URLs with reasons

        # More realistic headers to avoid bot detection
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }
        )

    def scrape_urls(self, urls: List[str]) -> Dict[str, str]:
        """
        Scrape multiple URLs and return their content.

        Args:
            urls: List of URLs to scrape

        Returns:
            Dictionary mapping URL to cleaned HTML content
        """
        console.print(
            f"\n[bold cyan]Step 4: Scraping Manufacturer Websites[/bold cyan] ({len(urls)} sites)\n"
        )

        results = {}
        successful = 0
        failed = 0
        self.failed_urls = []  # Reset failed URLs list

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scraping websites...", total=len(urls))

            for i, url in enumerate(urls, 1):
                progress.update(
                    task,
                    description=f"[{i}/{len(urls)}] {url[:50]}...",
                    advance=0,
                )

                try:
                    html = self._scrape_single_url(url)
                    if html:
                        results[url] = html
                        successful += 1
                    else:
                        failed += 1
                        self.failed_urls.append((url, "No content returned"))

                except Exception as e:
                    error_msg = str(e)
                    # Extract more specific error messages
                    if "403" in error_msg:
                        error_reason = "403 Forbidden - Site blocked the request"
                    elif "404" in error_msg:
                        error_reason = "404 Not Found - Page doesn't exist"
                    elif "timeout" in error_msg.lower():
                        error_reason = f"Timeout after {settings.SCRAPE_TIMEOUT_SECONDS}s"
                    elif "Connection" in error_msg:
                        error_reason = "Connection failed"
                    else:
                        error_reason = error_msg[:100]

                    console.print(f"  [yellow]✗ Failed: {url}[/yellow]")
                    console.print(f"    [dim]Error: {error_reason}[/dim]")

                    self.failed_urls.append((url, error_reason))
                    failed += 1

                progress.advance(task)

                # Rate limiting
                if i < len(urls):
                    time.sleep(settings.REQUEST_DELAY_SECONDS)

        console.print(
            f"\n[green]✓ Scraped {successful} sites successfully[/green]"
            + (f" [yellow]({failed} failed)[/yellow]" if failed > 0 else "")
        )
        console.print()

        return results

    def _scrape_single_url(self, url: str, retry: bool = True) -> str:
        """
        Scrape a single URL and return cleaned text content.

        Args:
            url: URL to scrape
            retry: Whether to retry on failure

        Returns:
            Cleaned text content from the page
        """
        try:
            # Fetch the page
            response = self.session.get(
                url,
                timeout=settings.SCRAPE_TIMEOUT_SECONDS,
                allow_redirects=True,
            )
            response.raise_for_status()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, "lxml")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned_text = "\n".join(lines)

            # Limit text length to avoid huge payloads (keep first 10000 chars)
            if len(cleaned_text) > 10000:
                cleaned_text = cleaned_text[:10000] + "\n\n[Content truncated...]"

            return cleaned_text

        except (requests.RequestException, Exception) as e:
            # Retry once with a fresh request and different headers
            if retry:
                time.sleep(2)  # Wait before retry
                # Try with a different User-Agent
                alt_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                }
                try:
                    response = requests.get(
                        url,
                        headers={**self.session.headers, **alt_headers},
                        timeout=settings.SCRAPE_TIMEOUT_SECONDS,
                        allow_redirects=True,
                    )
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, "lxml")
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    text = soup.get_text(separator="\n", strip=True)
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    cleaned_text = "\n".join(lines)

                    if len(cleaned_text) > 10000:
                        cleaned_text = cleaned_text[:10000] + "\n\n[Content truncated...]"

                    return cleaned_text
                except Exception:
                    pass  # Fall through to raise original error

            raise e

    def scrape_single_site(self, url: str) -> str:
        """
        Scrape a single site (public method for testing).

        Args:
            url: URL to scrape

        Returns:
            Cleaned HTML content
        """
        return self._scrape_single_url(url)

    def save_failed_urls(self, output_dir) -> str:
        """
        Save failed URLs to a text file for manual research.

        Args:
            output_dir: Directory to save the file

        Returns:
            Path to the saved file, or None if no failures
        """
        if not self.failed_urls:
            return None

        from datetime import datetime
        from pathlib import Path

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"failed_urls_{timestamp}.txt"
        filepath = Path(output_dir) / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("FAILED MANUFACTURER URLs - Manual Research Required\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Failed: {len(self.failed_urls)}\n")
            f.write("=" * 60 + "\n\n")

            for i, (url, reason) in enumerate(self.failed_urls, 1):
                f.write(f"{i}. {url}\n")
                f.write(f"   Reason: {reason}\n")
                f.write(f"   Action: Manually visit and research this manufacturer\n\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("TIPS FOR MANUAL RESEARCH:\n")
            f.write("- Try opening these URLs in a regular browser\n")
            f.write("- Check if the site requires JavaScript or login\n")
            f.write("- Look for 'About', 'Contact', or 'Capabilities' pages\n")
            f.write("- Search for the company on LinkedIn or industry directories\n")

        return str(filepath)
