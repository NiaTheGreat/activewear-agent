"""Wraps the existing CLI agent for use as an async background service."""

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.manufacturer import Manufacturer as DBManufacturer
from app.models.search import Search as DBSearch

# Path to the agent source code (resolved once, imported lazily)
_AGENT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # project root


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
        # -- Mark as running ------------------------------------------------
        await _update_search(
            session_factory,
            search_id,
            status="running",
            progress=0,
            current_step="Initialising",
            current_detail="Preparing search criteria",
            started_at=datetime.now(timezone.utc),
        )

        # Lazy-import agent modules
        _ensure_agent_path()
        from models.criteria import SearchCriteria as AgentSearchCriteria
        from tools.query_generator import QueryGenerator
        from tools.web_searcher import WebSearcher
        from tools.web_scraper import WebScraper
        from tools.data_extractor import DataExtractor
        from tools.evaluator import Evaluator

        # Build the agent-native criteria model
        criteria = AgentSearchCriteria(**criteria_dict)

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
                    name=mfg.name,
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
        await _update_search(
            session_factory,
            search_id,
            status="failed",
            current_step="Error",
            current_detail=str(exc)[:500],
            error_message=str(exc),
        )
