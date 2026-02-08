import csv
import io
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.manufacturer import Manufacturer
from app.models.search import Search
from app.models.user import User
from app.schemas.manufacturer import ManufacturerResponse, ManufacturerUpdate

router = APIRouter(tags=["manufacturers"])


@router.get(
    "/api/manufacturers",
    response_model=list[ManufacturerResponse],
)
async def list_all_manufacturers(
    sort_by: Literal["match_score", "name", "created_at"] = "match_score",
    sort_dir: Literal["asc", "desc"] = "desc",
    favorites_only: bool = Query(False),
    min_score: float = Query(0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List ALL manufacturers across all searches owned by the current user."""
    stmt = (
        select(Manufacturer)
        .join(Search, Manufacturer.search_id == Search.id)
        .where(
            Search.user_id == current_user.id,
            Manufacturer.match_score >= min_score,
        )
    )
    if favorites_only:
        stmt = stmt.where(Manufacturer.is_favorite == True)  # noqa: E712

    sort_col = getattr(Manufacturer, sort_by)
    stmt = stmt.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


# NOTE: This route MUST be before /api/manufacturers/{manufacturer_id}
# so FastAPI doesn't try to parse "export" as a UUID.
@router.get("/api/manufacturers/export/csv")
async def export_manufacturers_csv(
    favorites_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export manufacturers as a CSV file."""
    stmt = (
        select(Manufacturer)
        .join(Search, Manufacturer.search_id == Search.id)
        .where(Search.user_id == current_user.id)
    )
    if favorites_only:
        stmt = stmt.where(Manufacturer.is_favorite == True)  # noqa: E712
    stmt = stmt.order_by(Manufacturer.match_score.desc())

    result = await db.execute(stmt)
    manufacturers = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Name",
        "Website",
        "Location",
        "Score",
        "MOQ",
        "Materials",
        "Production Methods",
        "Certifications",
        "Email",
        "Phone",
        "Favorite",
        "Notes",
        "Source URL",
    ])
    for m in manufacturers:
        contact = m.contact or {}
        writer.writerow([
            m.name,
            m.website,
            m.location or "",
            round(m.match_score, 1),
            m.moq or "",
            ", ".join(m.materials or []),
            ", ".join(m.production_methods or []),
            ", ".join(m.certifications or []),
            contact.get("email", ""),
            contact.get("phone", ""),
            "Yes" if m.is_favorite else "No",
            m.user_notes or "",
            m.source_url,
        ])

    output.seek(0)
    filename = "favorites.csv" if favorites_only else "manufacturers.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/api/search/{search_id}/manufacturers",
    response_model=list[ManufacturerResponse],
)
async def list_manufacturers(
    search_id: uuid.UUID,
    sort_by: Literal["match_score", "name", "created_at"] = "match_score",
    sort_dir: Literal["asc", "desc"] = "desc",
    favorites_only: bool = Query(False),
    min_score: float = Query(0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List manufacturers for a search with optional filters and sorting."""
    # Verify search ownership
    search_result = await db.execute(select(Search).where(Search.id == search_id))
    search = search_result.scalar_one_or_none()
    if search is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search not found")
    if search.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised")

    # Build query
    stmt = select(Manufacturer).where(
        Manufacturer.search_id == search_id,
        Manufacturer.match_score >= min_score,
    )
    if favorites_only:
        stmt = stmt.where(Manufacturer.is_favorite == True)  # noqa: E712

    sort_col = getattr(Manufacturer, sort_by)
    stmt = stmt.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/api/manufacturers/{manufacturer_id}", response_model=ManufacturerResponse)
async def get_manufacturer(
    manufacturer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single manufacturer by ID."""
    mfg = await _get_owned_manufacturer(db, manufacturer_id, current_user.id)
    return mfg


@router.put("/api/manufacturers/{manufacturer_id}", response_model=ManufacturerResponse)
async def update_manufacturer(
    manufacturer_id: uuid.UUID,
    body: ManufacturerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user-editable fields (notes, tags, favorite, contacted_at)."""
    mfg = await _get_owned_manufacturer(db, manufacturer_id, current_user.id)
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mfg, field, value)
    await db.flush()
    return mfg


@router.delete(
    "/api/manufacturers/{manufacturer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_manufacturer(
    manufacturer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a manufacturer."""
    mfg = await _get_owned_manufacturer(db, manufacturer_id, current_user.id)
    await db.execute(
        sa_delete(Manufacturer).where(Manufacturer.id == mfg.id)
    )
    await db.commit()


async def _get_owned_manufacturer(
    db: AsyncSession, manufacturer_id: uuid.UUID, user_id: uuid.UUID
) -> Manufacturer:
    """Fetch a manufacturer and verify the parent search belongs to the user."""
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == manufacturer_id))
    mfg = result.scalar_one_or_none()
    if mfg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturer not found")

    # Check ownership via the search
    search_result = await db.execute(select(Search).where(Search.id == mfg.search_id))
    search = search_result.scalar_one_or_none()
    if search is None or search.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised")
    return mfg
