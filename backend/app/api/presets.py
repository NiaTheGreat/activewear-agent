import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.search import CriteriaPreset
from app.models.user import User
from app.schemas.search import CriteriaPresetCreate, CriteriaPresetResponse, CriteriaPresetUpdate

router = APIRouter(prefix="/api/presets", tags=["presets"])


@router.get("", response_model=list[CriteriaPresetResponse])
async def list_presets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's presets (plus any public ones)."""
    result = await db.execute(
        select(CriteriaPreset)
        .where((CriteriaPreset.user_id == current_user.id) | (CriteriaPreset.is_public == True))  # noqa: E712
        .order_by(CriteriaPreset.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=CriteriaPresetResponse, status_code=status.HTTP_201_CREATED)
async def create_preset(
    body: CriteriaPresetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new criteria preset."""
    preset = CriteriaPreset(
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        criteria=body.criteria,
        is_public=body.is_public,
    )
    db.add(preset)
    await db.flush()
    return preset


@router.get("/{preset_id}", response_model=CriteriaPresetResponse)
async def get_preset(
    preset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single preset by ID."""
    result = await db.execute(select(CriteriaPreset).where(CriteriaPreset.id == preset_id))
    preset = result.scalar_one_or_none()
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    if preset.user_id != current_user.id and not preset.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised")
    return preset


@router.put("/{preset_id}", response_model=CriteriaPresetResponse)
async def update_preset(
    preset_id: uuid.UUID,
    body: CriteriaPresetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing preset."""
    result = await db.execute(select(CriteriaPreset).where(CriteriaPreset.id == preset_id))
    preset = result.scalar_one_or_none()
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    if preset.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preset, field, value)
    await db.flush()
    return preset


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(
    preset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a preset."""
    result = await db.execute(select(CriteriaPreset).where(CriteriaPreset.id == preset_id))
    preset = result.scalar_one_or_none()
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    if preset.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised")
    await db.delete(preset)
