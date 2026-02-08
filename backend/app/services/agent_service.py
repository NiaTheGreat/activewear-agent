"""Wraps the existing CLI agent for use as an async background service."""

import asyncio
import logging
import re
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.manufacturer import Manufacturer as DBManufacturer
from app.models.search import Search as DBSearch

# Path to the agent source code (resolved once, imported lazily)
_AGENT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # project root


def _clean_name(name: str | None, url: str | None) -> str:
    """Return a readable name; fall back to the URL domain if the name is garbled."""
    if name and name.isprintable() and not re.search(r'[\x00-\x08\x0e-\x1f\x7f-\x9f\ufffd]', name):
        return name
    if url:
        domain = urlparse(url).netloc or urlparse(url).path
        domain = domain.removeprefix("www.")
        # "knitwear.io" -> "Knitwear"
        label = domain.split(".")[0]
        return label.replace("-", " ").title()
    return "Unknown Manufacturer"


def _ensure_agent_path() -> None:
    """Add the agent source directories to sys.path if not already present."""
    src_path = str(_AGENT_ROOT / "src")
    root_path = str(_AGENT_ROOT)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    if root_path not in sys.path:
        sys.path.insert(0, root_path)


async def _update_search(
    session_factory: async_sessionmaker[AsyncSession],
    search_id: uuid.UUID,
    **fields: Any,
) -> None:
    """Helper to update a search record in its own session."""
    async with session_factory() as session:
        await session.execute(
            update(DBSearch).where(DBSearch.id == search_id).values(**fields)
        )
        await session.commit()


async def run_agent_search(
    session_factory: async_sessionmaker[AsyncSession],
    search_id: uuid.UUID,
    criteria_dict: dict,
    max_manufacturers: int = 10,
) -> None:
    """
    Execute the full agent pipeline in the background and persist results.

    Agent modules are imported lazily so the FastAPI app can start without
    the agent's runtime dependencies (rich, anthropic, etc.) in the backend
    virtualenv — they only need to be importable at search time.
    """
    try:
        logger.info("[%s] run_agent_search ENTERED", search_id)

        # -- Mark as running ------------------------------------------------
        logger.info("[%s] Updating status to 'running'", search_id)
        await _update_search(
            session_factory,
            search_id,
            status="running",
            progress=0,
            current_step="Initialising",
            current_detail="Preparing search criteria",
            started_at=datetime.now(timezone.utc),
        )
        logger.info("[%s] Status updated to 'running'", search_id)

        # Lazy-import agent modules
        logger.info("[%s] Ensuring agent path...", search_id)
        _ensure_agent_path()
        logger.info("[%s] Agent path: src=%s, root=%s", search_id, _AGENT_ROOT / "src", _AGENT_ROOT)
        logger.info("[%s] sys.path[0:3] = %s", search_id, sys.path[:3])

        logger.info("[%s] Importing agent modules...", search_id)
        from models.criteria import SearchCriteria as AgentSearchCriteria
        logger.info("[%s] Imported SearchCriteria", search_id)
        from tools.query_generator import QueryGenerator
        logger.info("[%s] Imported QueryGenerator", search_id)
        from tools.web_searcher import WebSearcher
        logger.info("[%s] Imported WebSearcher", search_id)
        from tools.web_scraper import WebScraper
        logger.info("[%s] Imported WebScraper", search_id)
        from tools.data_extractor import DataExtractor
        logger.info("[%s] Imported DataExtractor", search_id)
        from tools.evaluator import Evaluator
        logger.info("[%s] All agent modules imported OK", search_id)

        # Build the agent-native criteria model
        logger.info("[%s] Building criteria from dict: %s", search_id, criteria_dict)
        criteria = AgentSearchCriteria(**criteria_dict)
        logger.info("[%s] Criteria built: %s", search_id, criteria)

        # -- Phase 1: Generate queries --------------------------------------
        await _update_search(
            session_factory,
            search_id,
            progress=10,
            current_step="Generating queries",
            current_detail="Using AI to craft search queries",
        )
        qg = QueryGenerator()
        queries: list[str] = await asyncio.to_thread(qg.generate, criteria)

        await _update_search(
            session_factory,
            search_id,
            progress=20,
            search_queries={"queries": queries},
            current_step="Queries ready",
            current_detail=f"Generated {len(queries)} queries",
        )

        # -- Phase 2: Web search --------------------------------------------
        await _update_search(
            session_factory,
            search_id,
            progress=30,
            current_step="Searching the web",
            current_detail="Querying Brave Search API",
        )
        ws = WebSearcher()
        urls: list[str] = await asyncio.to_thread(ws.search, queries, max_manufacturers)

        await _update_search(
            session_factory,
            search_id,
            progress=40,
            current_step="Search complete",
            current_detail=f"Found {len(urls)} manufacturer URLs",
        )

        if not urls:
            await _update_search(
                session_factory,
                search_id,
                status="completed",
                progress=100,
                current_step="Done",
                current_detail="No manufacturer URLs found",
                total_found=0,
                completed_at=datetime.now(timezone.utc),
            )
            return

        # -- Phase 3: Scrape websites ---------------------------------------
        await _update_search(
            session_factory,
            search_id,
            progress=50,
            current_step="Scraping websites",
            current_detail=f"Scraping {len(urls)} sites",
        )
        scraper = WebScraper()
        scraped_data: dict[str, str] = await asyncio.to_thread(
            scraper.scrape_urls, urls[:max_manufacturers]
        )

        await _update_search(
            session_factory,
            search_id,
            progress=65,
            current_step="Scraping complete",
            current_detail=f"Scraped {len(scraped_data)} of {len(urls)} sites",
        )

        if not scraped_data:
            await _update_search(
                session_factory,
                search_id,
                status="completed",
                progress=100,
                current_step="Done",
                current_detail="Could not scrape any websites",
                total_found=0,
                completed_at=datetime.now(timezone.utc),
            )
            return

        # -- Phase 4: Extract data ------------------------------------------
        await _update_search(
            session_factory,
            search_id,
            progress=70,
            current_step="Extracting data",
            current_detail="Using AI to extract manufacturer info",
        )
        extractor = DataExtractor()
        manufacturers = await asyncio.to_thread(extractor.extract, scraped_data)

        # -- Phase 5: Evaluate / score -------------------------------------
        await _update_search(
            session_factory,
            search_id,
            progress=85,
            current_step="Evaluating",
            current_detail=f"Scoring {len(manufacturers)} manufacturers",
        )
        evaluator = Evaluator()
        manufacturers = await asyncio.to_thread(evaluator.evaluate, manufacturers, criteria)

        # -- Phase 6: Persist results ---------------------------------------
        await _update_search(
            session_factory,
            search_id,
            progress=95,
            current_step="Saving results",
            current_detail="Writing to database",
        )

        async with session_factory() as session:
            for mfg in manufacturers:
                db_mfg = DBManufacturer(
                    search_id=search_id,
                    name=_clean_name(mfg.name, mfg.website or mfg.source_url),
                    website=mfg.website,
                    location=mfg.location,
                    contact={
                        "email": mfg.contact.email,
                        "phone": mfg.contact.phone,
                        "address": mfg.contact.address,
                    } if mfg.contact else None,
                    materials=mfg.materials or [],
                    production_methods=mfg.production_methods or [],
                    certifications=mfg.certifications or [],
                    moq=mfg.moq,
                    moq_description=mfg.moq_description,
                    match_score=mfg.match_score,
                    confidence=mfg.confidence,
                    scoring_breakdown=None,
                    notes=mfg.notes,
                    source_url=mfg.source_url,
                    scraped_at=mfg.scraped_at,
                )
                session.add(db_mfg)

            await session.commit()

        # -- Done -----------------------------------------------------------
        await _update_search(
            session_factory,
            search_id,
            status="completed",
            progress=100,
            current_step="Complete",
            current_detail=f"Found {len(manufacturers)} manufacturers",
            total_found=len(manufacturers),
            completed_at=datetime.now(timezone.utc),
        )

    except Exception as exc:
        logger.error("Search %s failed: %s\n%s", search_id, exc, traceback.format_exc())
        await _update_search(
            session_factory,
            search_id,
            status="failed",
            current_step="Error",
            current_detail=str(exc)[:500],
            error_message=str(exc),
        )
