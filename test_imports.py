#!/usr/bin/env python3
"""Quick import test to verify all modules load correctly."""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing imports...")

try:
    # Config
    from config import settings
    print("✓ config.settings")

    # Models
    from models.criteria import SearchCriteria
    from models.manufacturer import Manufacturer
    print("✓ models")

    # Utils
    from utils.llm import ClaudeClient, get_client
    print("✓ utils")

    # Agent
    from agent.core import ManufacturerResearchAgent
    from agent.state import AgentState
    print("✓ agent")

    # Tools
    from tools.criteria_collector import CriteriaCollector
    from tools.query_generator import QueryGenerator
    from tools.web_searcher import WebSearcher
    from tools.web_scraper import WebScraper
    from tools.data_extractor import DataExtractor
    from tools.evaluator import Evaluator
    from tools.excel_generator import ExcelGenerator
    print("✓ tools")

    print("\n✅ All imports successful!")
    print("\nProject structure is valid and ready to run.")
    print("\nNext step: Add your ANTHROPIC_API_KEY to .env file")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
