"""Application configuration and settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
PRESETS_DIR = CONFIG_DIR / "presets"
OUTPUT_DIR = PROJECT_ROOT / "output"
SRC_DIR = PROJECT_ROOT / "src"

# Ensure directories exist
PRESETS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    """Application settings loaded from environment variables."""

    # API Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"

    # Brave Search API Configuration
    BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")

    # Notion Integration (Optional)
    NOTION_ENABLED: bool = os.getenv("NOTION_ENABLED", "false").lower() == "true"
    NOTION_API_TOKEN: str = os.getenv("NOTION_API_TOKEN", "")
    NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")

    # Rate Limiting & Timeouts
    REQUEST_DELAY_SECONDS: int = int(os.getenv("REQUEST_DELAY_SECONDS", "2"))
    SCRAPE_TIMEOUT_SECONDS: int = int(os.getenv("SCRAPE_TIMEOUT_SECONDS", "30"))
    MAX_RETRY_ATTEMPTS: int = 3

    # Search & Scraping Limits
    MAX_MANUFACTURERS: int = int(os.getenv("MAX_MANUFACTURERS", "10"))
    MAX_SEARCH_QUERIES: int = 5
    MAX_URLS_TO_SCRAPE: int = 15

    # API Budget Control
    MAX_TOKENS_PER_REQUEST: int = 4096
    BUDGET_LIMIT_USD: float = 50.0

    # Output Configuration
    EXCEL_FILENAME_PATTERN: str = "manufacturers_{timestamp}.xlsx"
    TIMESTAMP_FORMAT: str = "%Y-%m-%d_%H-%M-%S"

    @classmethod
    def validate(cls) -> bool:
        """Validate required settings are present."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Please set it in .env file."
            )
        return True


# Global settings instance
settings = Settings()
