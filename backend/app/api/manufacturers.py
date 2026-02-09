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
from app.schemas.manufacturer import (
    CopyToOrganizationRequest,
    ManufacturerCreate,
    ManufacturerResponse,
    ManufacturerUpdate,
)

router = APIRouter(tags=["manufacturers"])


@router.get(
    "/api/manufacturers",
    response_model=list[ManufacturerResponse],
)
async def list_all_manufacturers(
    organization_id: uuid.UUID | None = None,
    sort_by: Literal["match_score", "name", "created_at"] = "match_score",
    sort_dir: Literal["asc", "desc"] = "desc",
    favorites_only: bool = Query(False),
    min_score: float = Query(0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List manufacturers across searches.
    - If organization_id provided: shows manufacturers from org searches (requires membership)
    - If organization_id is None: shows manufacturers from personal searches only
    """
    stmt = select(Manufacturer).join(Search, Manufacturer.search_id == Search.id)

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

        # Filter to org searches
        stmt = stmt.where(
            Search.organization_id == organization_id,
            Manufacturer.match_score >= min_score,
        )
    else:
        # Filter to personal searches only
        stmt = stmt.where(
            Search.user_id == current_user.id,
            Search.organization_id.is_(None),
            Manufacturer.match_score >= min_score,
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


@router.post(
    "/api/manufacturers/manual",
    response_model=ManufacturerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_manual_manufacturer(
    body: ManufacturerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually add a manufacturer (not from a search) and place it in the pipeline."""
    # Find or create a "manual_entry" search container for this user
    result = await db.execute(
        select(Search).where(
            Search.user_id == current_user.id,
            Search.search_mode == "manual_entry",
        )
    )
    manual_search = result.scalar_one_or_none()

    if manual_search is None:
        from datetime import datetime, timezone

        manual_search = Search(
            user_id=current_user.id,
            criteria={},
            search_mode="manual_entry",
            status="completed",
            progress=100,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(manual_search)
        await db.flush()

    mfg = Manufacturer(
        search_id=manual_search.id,
        name=body.name.strip(),
        website=body.website.strip() if body.website else "",
        location=body.location,
        contact=body.contact,
        materials=body.materials,
        production_methods=body.production_methods,
        certifications=body.certifications,
        moq=body.moq,
        moq_description=body.moq_description,
        notes=body.notes,
        source_url="manual_entry",
        confidence="manual",
        match_score=0.0,
        status="new",
    )
    db.add(mfg)
    await db.flush()
    return mfg


@router.post(
    "/api/manufacturers/{manufacturer_id}/copy-to-organization",
    response_model=ManufacturerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def copy_manufacturer_to_organization(
    manufacturer_id: uuid.UUID,
    body: CopyToOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Copy a manufacturer from personal workspace to an organization.
    - Verifies user owns the source manufacturer
    - Verifies user is a member of the target organization
    - Creates a duplicate in the organization's manual_entry search
    - Optionally adds to specified pipelines
    """
    # Get and verify ownership of source manufacturer
    source_mfg = await _get_owned_manufacturer(db, manufacturer_id, current_user.id)

    # Verify user is a member of the target organization
    from app.models.organization_member import OrganizationMember

    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == body.organization_id,
            OrganizationMember.user_id == current_user.id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    # Find or create a "manual_entry" search for this organization
    result = await db.execute(
        select(Search).where(
            Search.organization_id == body.organization_id,
            Search.search_mode == "manual_entry",
        )
    )
    org_manual_search = result.scalar_one_or_none()

    if org_manual_search is None:
        from datetime import datetime, timezone

        org_manual_search = Search(
            user_id=current_user.id,
            organization_id=body.organization_id,
            criteria={},
            search_mode="manual_entry",
            status="completed",
            progress=100,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(org_manual_search)
        await db.flush()

    # Create a duplicate manufacturer in the organization
    new_mfg = Manufacturer(
        search_id=org_manual_search.id,
        name=source_mfg.name,
        website=source_mfg.website,
        location=source_mfg.location,
        contact=source_mfg.contact,
        materials=source_mfg.materials,
        production_methods=source_mfg.production_methods,
        certifications=source_mfg.certifications,
        moq=source_mfg.moq,
        moq_description=source_mfg.moq_description,
        notes=source_mfg.notes,
        source_url=f"copied_from_personal:{source_mfg.id}",
        confidence="manual",
        match_score=source_mfg.match_score,
        status="new",
    )
    db.add(new_mfg)
    await db.flush()

    # Add to pipelines if specified
    if body.pipeline_ids:
        from app.models.pipeline import Pipeline
        from app.models.pipeline_manufacturer import PipelineManufacturer

        # Verify all pipelines belong to the organization
        for pipeline_id in body.pipeline_ids:
            pipeline_result = await db.execute(
                select(Pipeline).where(
                    Pipeline.id == pipeline_id,
                    Pipeline.organization_id == body.organization_id,
                )
            )
            pipeline = pipeline_result.scalar_one_or_none()
            if pipeline is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pipeline {pipeline_id} not found in this organization",
                )

            # Add manufacturer to pipeline
            pipeline_mfg = PipelineManufacturer(
                pipeline_id=pipeline_id,
                manufacturer_id=new_mfg.id,
                added_by_user_id=current_user.id,
            )
            db.add(pipeline_mfg)

        await db.flush()

    await db.commit()
    return new_mfg


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
    """Update manufacturer fields."""
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
