import asyncio
import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

logger = logging.getLogger(__name__)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import async_session_factory, get_db
from app.models.search import Search
from app.models.user import User
from app.schemas.search import SearchCreate, SearchResponse, SearchStatus
from app.services.agent_service import run_agent_search

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/run", response_model=SearchResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_search(
    body: SearchCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new manufacturer search. The agent runs in the background.
    If organization_id is provided, creates an org search visible to all members.
    Otherwise, creates a personal search.
    """
    # If organization_id is provided, verify user is a member
    if body.organization_id is not None:
        from app.models.organization_member import OrganizationMember

        result = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == body.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

    search = Search(
        user_id=current_user.id,
        organization_id=body.organization_id,
        criteria_preset_id=body.criteria_preset_id,
        criteria=body.criteria,
        search_mode=body.search_mode,
        status="pending",
    )
    db.add(search)
    await db.commit()

    # Schedule the heavy agent work as a background task
    logger.info("Scheduling background search task for search_id=%s", search.id)
    background_tasks.add_task(
        _run_search_wrapper,
        search_id=search.id,
        criteria_dict=body.criteria,
        max_manufacturers=body.max_manufacturers,
    )

    return search


async def _run_search_wrapper(
    search_id: uuid.UUID,
    criteria_dict: dict,
    max_manufacturers: int,
) -> None:
    """Thin wrapper so BackgroundTasks can call the async agent service."""
    logger.info("Background task STARTED for search_id=%s", search_id)
    try:
        await run_agent_search(async_session_factory, search_id, criteria_dict, max_manufacturers)
        logger.info("Background task COMPLETED for search_id=%s", search_id)
    except Exception as exc:
        logger.error("Background task CRASHED for search_id=%s: %s", search_id, exc, exc_info=True)


@router.get("/{search_id}/status", response_model=SearchStatus)
async def get_search_status(
    search_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Poll real-time progress for a running search."""
    search = await _get_user_search(db, search_id, current_user.id)
    return search


@router.get("/history", response_model=list[SearchResponse])
async def search_history(
    organization_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List searches accessible to the current user.
    - If organization_id is provided: shows org searches (requires membership)
    - If organization_id is None: shows personal searches only
    """
    if organization_id is not None:
        # Verify user is a member of the organization
        from app.models.organization_member import OrganizationMember

        result = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        # Return org searches
        result = await db.execute(
            select(Search)
            .where(Search.organization_id == organization_id)
            .order_by(Search.created_at.desc())
        )
    else:
        # Return personal searches only
        result = await db.execute(
            select(Search)
            .where(
                Search.user_id == current_user.id,
                Search.organization_id.is_(None),
            )
            .order_by(Search.created_at.desc())
        )

    return result.scalars().all()


@router.get("/{search_id}", response_model=SearchResponse)
async def get_search(
    search_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full details for a search."""
    search = await _get_user_search(db, search_id, current_user.id)
    return search


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search(
    search_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a search and its manufacturers."""
    search = await _get_user_search(db, search_id, current_user.id)
    await db.delete(search)


async def _get_user_search(db: AsyncSession, search_id: uuid.UUID, user_id: uuid.UUID) -> Search:
    """Fetch a search and verify ownership."""
    result = await db.execute(select(Search).where(Search.id == search_id))
    search = result.scalar_one_or_none()
    if search is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search not found")
    if search.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised")
    return search
