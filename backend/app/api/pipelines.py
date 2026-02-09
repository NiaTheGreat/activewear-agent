import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.organizations import _get_user_organization_with_role
from app.database import get_db
from app.models.manufacturer import Manufacturer
from app.models.organization_member import OrganizationMember
from app.models.pipeline import Pipeline
from app.models.pipeline_manufacturer import PipelineManufacturer
from app.models.search import Search
from app.models.user import User
from app.schemas.pipeline import (
    AddManufacturerToPipelineRequest,
    PipelineCreate,
    PipelineManufacturerResponse,
    PipelineResponse,
    PipelineUpdate,
    UpdatePipelineManufacturerRequest,
)

router = APIRouter(prefix="/api", tags=["pipelines"])


# ========== Pipeline CRUD ==========


@router.post("/organizations/{org_id}/pipelines", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    org_id: uuid.UUID,
    body: PipelineCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new pipeline in an organization.
    All org members can create pipelines.
    """
    # Verify user is a member
    await _get_user_organization_with_role(db, org_id, current_user.id)

    # If is_default is True, unset any existing default
    if body.is_default:
        await db.execute(
            select(Pipeline)
            .where(Pipeline.organization_id == org_id, Pipeline.is_default == True)  # noqa: E712
        )
        # Update existing defaults to False
        stmt = select(Pipeline).where(Pipeline.organization_id == org_id, Pipeline.is_default == True)  # noqa: E712
        result = await db.execute(stmt)
        for pipeline in result.scalars():
            pipeline.is_default = False

    pipeline = Pipeline(
        organization_id=org_id,
        name=body.name,
        description=body.description,
        color=body.color,
        icon=body.icon,
        is_default=body.is_default,
        created_by_user_id=current_user.id,
    )
    db.add(pipeline)
    await db.flush()

    return pipeline


@router.get("/organizations/{org_id}/pipelines", response_model=list[PipelineResponse])
async def list_organization_pipelines(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all pipelines in an organization.
    Includes manufacturer count for each pipeline.
    """
    # Verify user is a member
    await _get_user_organization_with_role(db, org_id, current_user.id)

    # Query pipelines with manufacturer count
    stmt = (
        select(
            Pipeline,
            func.count(PipelineManufacturer.id).label("manufacturer_count"),
        )
        .outerjoin(PipelineManufacturer, Pipeline.id == PipelineManufacturer.pipeline_id)
        .where(Pipeline.organization_id == org_id)
        .group_by(Pipeline.id)
        .order_by(Pipeline.created_at)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Build response with manufacturer count
    pipelines = []
    for pipeline, manufacturer_count in rows:
        pipeline_dict = PipelineResponse.model_validate(pipeline).model_dump()
        pipeline_dict["manufacturer_count"] = manufacturer_count
        pipelines.append(PipelineResponse(**pipeline_dict))

    return pipelines


@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details for a specific pipeline."""
    pipeline = await _get_user_pipeline(db, pipeline_id, current_user.id)
    return pipeline


@router.put("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: uuid.UUID,
    body: PipelineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update pipeline details.
    All org members can update pipelines.
    """
    pipeline = await _get_user_pipeline(db, pipeline_id, current_user.id)

    # If setting is_default to True, unset any existing default in this org
    if body.is_default is True:
        stmt = select(Pipeline).where(
            Pipeline.organization_id == pipeline.organization_id,
            Pipeline.is_default == True,  # noqa: E712
            Pipeline.id != pipeline_id,
        )
        result = await db.execute(stmt)
        for existing_default in result.scalars():
            existing_default.is_default = False

    # Apply updates
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pipeline, field, value)

    await db.flush()
    return pipeline


@router.delete("/pipelines/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a pipeline.
    This removes all manufacturer associations but doesn't delete the manufacturers themselves.
    """
    pipeline = await _get_user_pipeline(db, pipeline_id, current_user.id)
    await db.delete(pipeline)


# ========== Pipeline-Manufacturer Management ==========


@router.post("/pipelines/{pipeline_id}/manufacturers", response_model=PipelineManufacturerResponse, status_code=status.HTTP_201_CREATED)
async def add_manufacturer_to_pipeline(
    pipeline_id: uuid.UUID,
    body: AddManufacturerToPipelineRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a manufacturer to a pipeline.
    The manufacturer must belong to a search within the same organization.
    """
    pipeline = await _get_user_pipeline(db, pipeline_id, current_user.id)

    # Verify manufacturer exists and belongs to org's search
    result = await db.execute(
        select(Manufacturer)
        .join(Search, Manufacturer.search_id == Search.id)
        .where(
            Manufacturer.id == body.manufacturer_id,
            Search.organization_id == pipeline.organization_id,
        )
    )
    manufacturer = result.scalar_one_or_none()
    if manufacturer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturer not found or doesn't belong to this organization",
        )

    # Check if already in pipeline
    result = await db.execute(
        select(PipelineManufacturer).where(
            PipelineManufacturer.pipeline_id == pipeline_id,
            PipelineManufacturer.manufacturer_id == body.manufacturer_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manufacturer is already in this pipeline",
        )

    # Add to pipeline
    pm = PipelineManufacturer(
        pipeline_id=pipeline_id,
        manufacturer_id=body.manufacturer_id,
        added_by_user_id=current_user.id,
        pipeline_notes=body.pipeline_notes,
        pipeline_status=body.pipeline_status,
        priority=body.priority,
    )
    db.add(pm)
    await db.flush()

    return pm


@router.get("/pipelines/{pipeline_id}/manufacturers", response_model=list[PipelineManufacturerResponse])
async def list_pipeline_manufacturers(
    pipeline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all manufacturers in a pipeline.
    Returns the pipeline-specific context for each manufacturer.
    """
    await _get_user_pipeline(db, pipeline_id, current_user.id)

    stmt = (
        select(PipelineManufacturer)
        .where(PipelineManufacturer.pipeline_id == pipeline_id)
        .order_by(PipelineManufacturer.priority.nulls_last(), PipelineManufacturer.added_at)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/pipeline-manufacturers/{pm_id}", response_model=PipelineManufacturerResponse)
async def update_pipeline_manufacturer(
    pm_id: uuid.UUID,
    body: UpdatePipelineManufacturerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the pipeline-specific context for a manufacturer.
    Updates notes, status, or priority within this pipeline.
    """
    # Fetch the pipeline-manufacturer relationship
    result = await db.execute(select(PipelineManufacturer).where(PipelineManufacturer.id == pm_id))
    pm = result.scalar_one_or_none()
    if pm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline-manufacturer relationship not found")

    # Verify user has access to the pipeline
    await _get_user_pipeline(db, pm.pipeline_id, current_user.id)

    # Apply updates
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pm, field, value)

    await db.flush()
    return pm


@router.delete("/pipeline-manufacturers/{pm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_manufacturer_from_pipeline(
    pm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a manufacturer from a pipeline.
    This doesn't delete the manufacturer, just removes it from this pipeline.
    """
    # Fetch the pipeline-manufacturer relationship
    result = await db.execute(select(PipelineManufacturer).where(PipelineManufacturer.id == pm_id))
    pm = result.scalar_one_or_none()
    if pm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline-manufacturer relationship not found")

    # Verify user has access to the pipeline
    await _get_user_pipeline(db, pm.pipeline_id, current_user.id)

    await db.delete(pm)


# ========== Helper Functions ==========


async def _get_user_pipeline(db: AsyncSession, pipeline_id: uuid.UUID, user_id: uuid.UUID) -> Pipeline:
    """
    Fetch a pipeline and verify the user has access via organization membership.
    Raises 404 if pipeline doesn't exist, 403 if user is not an org member.
    """
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    if pipeline is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")

    # Verify user is a member of the pipeline's organization
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == pipeline.organization_id,
            OrganizationMember.user_id == user_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this pipeline's organization",
        )

    return pipeline
