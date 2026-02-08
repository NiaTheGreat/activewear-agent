import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.contact_activity import ContactActivity
from app.models.manufacturer import Manufacturer
from app.models.search import Search
from app.models.user import User
from app.schemas.contact_activity import (
    ContactActivityCreate,
    ContactActivityResponse,
    ContactActivityUpdate,
)

router = APIRouter(tags=["activities"])


async def _verify_manufacturer_ownership(
    db: AsyncSession, manufacturer_id: uuid.UUID, user_id: uuid.UUID
) -> Manufacturer:
    """Verify that the manufacturer belongs to the user via search ownership."""
    result = await db.execute(select(Manufacturer).where(Manufacturer.id == manufacturer_id))
    mfg = result.scalar_one_or_none()
    if mfg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturer not found")

    search_result = await db.execute(select(Search).where(Search.id == mfg.search_id))
    search = search_result.scalar_one_or_none()
    if search is None or search.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised")
    return mfg


@router.post(
    "/api/manufacturers/{manufacturer_id}/activities",
    response_model=ContactActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity(
    manufacturer_id: uuid.UUID,
    body: ContactActivityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new contact activity for a manufacturer."""
    await _verify_manufacturer_ownership(db, manufacturer_id, current_user.id)

    activity = ContactActivity(
        manufacturer_id=manufacturer_id,
        user_id=current_user.id,
        activity_type=body.activity_type,
        subject=body.subject,
        content=body.content,
        contact_date=body.contact_date,
        reminder_date=body.reminder_date,
    )
    db.add(activity)
    await db.flush()
    return activity


@router.get(
    "/api/manufacturers/{manufacturer_id}/activities",
    response_model=list[ContactActivityResponse],
)
async def list_activities(
    manufacturer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all activities for a manufacturer, newest first."""
    await _verify_manufacturer_ownership(db, manufacturer_id, current_user.id)

    result = await db.execute(
        select(ContactActivity)
        .where(ContactActivity.manufacturer_id == manufacturer_id)
        .order_by(ContactActivity.contact_date.desc())
    )
    return result.scalars().all()


@router.put("/api/activities/{activity_id}", response_model=ContactActivityResponse)
async def update_activity(
    activity_id: uuid.UUID,
    body: ContactActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing activity."""
    result = await db.execute(select(ContactActivity).where(ContactActivity.id == activity_id))
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    await _verify_manufacturer_ownership(db, activity.manufacturer_id, current_user.id)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    await db.flush()
    return activity


@router.delete("/api/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an activity."""
    result = await db.execute(select(ContactActivity).where(ContactActivity.id == activity_id))
    activity = result.scalar_one_or_none()
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    await _verify_manufacturer_ownership(db, activity.manufacturer_id, current_user.id)
    await db.delete(activity)
