import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationMemberUpdate,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


# ========== Organization CRUD ==========


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new organization.
    The creating user automatically becomes the owner.
    """
    # Check if slug is already taken
    result = await db.execute(select(Organization).where(Organization.slug == body.slug))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization slug '{body.slug}' is already taken",
        )

    # Create organization
    org = Organization(
        name=body.name,
        slug=body.slug,
        description=body.description,
        created_by_user_id=current_user.id,
    )
    db.add(org)
    await db.flush()

    # Add creator as owner
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(membership)
    await db.flush()

    return org


@router.get("", response_model=list[OrganizationResponse])
async def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all organizations the current user is a member of.
    Includes member count for each org.
    """
    # Query orgs where user is a member, with member count
    stmt = (
        select(
            Organization,
            func.count(OrganizationMember.id).label("member_count"),
        )
        .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .group_by(Organization.id)
        .order_by(Organization.created_at.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Build response with member count
    orgs = []
    for org, member_count in rows:
        org_dict = OrganizationResponse.model_validate(org).model_dump()
        org_dict["member_count"] = member_count
        orgs.append(OrganizationResponse(**org_dict))

    return orgs


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details for a specific organization."""
    org = await _get_user_organization(db, org_id, current_user.id)
    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    body: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization details.
    Requires admin or owner role.
    """
    org, membership = await _get_user_organization_with_role(db, org_id, current_user.id)

    # Only owner/admin can update
    if membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can update the organization",
        )

    # Apply updates
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)

    await db.flush()
    return org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an organization.
    Only the owner can delete an organization.
    This will cascade delete all pipelines, searches, and memberships.
    """
    org, membership = await _get_user_organization_with_role(db, org_id, current_user.id)

    # Only owner can delete
    if membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete the organization",
        )

    await db.delete(org)


# ========== Organization Member Management ==========


@router.get("/{org_id}/members", response_model=list[OrganizationMemberResponse])
async def list_organization_members(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all members of an organization."""
    # Verify user is a member
    await _get_user_organization(db, org_id, current_user.id)

    # Fetch all members with user details
    stmt = (
        select(OrganizationMember, User.email, User.full_name)
        .join(User, OrganizationMember.user_id == User.id)
        .where(OrganizationMember.organization_id == org_id)
        .order_by(OrganizationMember.joined_at)
    )

    result = await db.execute(stmt)
    rows = result.all()

    members = []
    for member, email, full_name in rows:
        member_dict = OrganizationMemberResponse.model_validate(member).model_dump()
        member_dict["user_email"] = email
        member_dict["user_full_name"] = full_name
        members.append(OrganizationMemberResponse(**member_dict))

    return members


@router.post("/{org_id}/members", response_model=OrganizationMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: uuid.UUID,
    body: OrganizationMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite a user to the organization by email.
    Requires admin or owner role.
    """
    org, membership = await _get_user_organization_with_role(db, org_id, current_user.id)

    # Only owner/admin can invite
    if membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can invite members",
        )

    # Find user by email
    result = await db.execute(select(User).where(User.email == body.email))
    invited_user = result.scalar_one_or_none()
    if invited_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email '{body.email}'",
        )

    # Check if already a member
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == invited_user.id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization",
        )

    # Create membership
    new_member = OrganizationMember(
        organization_id=org_id,
        user_id=invited_user.id,
        role=body.role,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(new_member)
    await db.flush()

    return new_member


@router.put("/{org_id}/members/{member_id}", response_model=OrganizationMemberResponse)
async def update_member_role(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    body: OrganizationMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a member's role.
    Only owners can change roles.
    """
    org, requester_membership = await _get_user_organization_with_role(db, org_id, current_user.id)

    # Only owner can change roles
    if requester_membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can change member roles",
        )

    # Fetch the member to update
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == org_id,
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    # Prevent owner from demoting themselves if they're the only owner
    if member.user_id == current_user.id and member.role == "owner" and body.role != "owner":
        owner_count = await db.scalar(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.role == "owner",
            )
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the only owner. Promote another member first.",
            )

    member.role = body.role
    await db.flush()
    return member


@router.delete("/{org_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from the organization.
    Owners/admins can remove others. Members can remove themselves.
    """
    org, requester_membership = await _get_user_organization_with_role(db, org_id, current_user.id)

    # Fetch the member to remove
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == org_id,
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    # Permission check: owner/admin can remove anyone, members can only remove themselves
    if requester_membership.role not in ("owner", "admin") and member.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove yourself unless you are an owner or admin",
        )

    # Prevent removing the last owner
    if member.role == "owner":
        owner_count = await db.scalar(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.role == "owner",
            )
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the only owner. Promote another member first.",
            )

    await db.delete(member)


# ========== Helper Functions ==========


async def _get_user_organization(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID
) -> Organization:
    """
    Fetch an organization and verify the user is a member.
    Raises 404 if org doesn't exist, 403 if user is not a member.
    """
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Verify membership
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    return org


async def _get_user_organization_with_role(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID
) -> tuple[Organization, OrganizationMember]:
    """
    Fetch an organization and the user's membership.
    Returns both the org and the membership (which includes the role).
    Raises 404 if org doesn't exist, 403 if user is not a member.
    """
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Fetch membership
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    return org, membership
