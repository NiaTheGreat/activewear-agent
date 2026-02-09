"""
Utility functions for organization-related operations.
Provides reusable permission checks and common queries.
"""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember


async def verify_org_membership(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    required_roles: list[str] | None = None,
) -> OrganizationMember:
    """
    Verify that a user is a member of an organization.
    Optionally verify they have one of the required roles.

    Args:
        db: Database session
        organization_id: Organization UUID
        user_id: User UUID
        required_roles: Optional list of required roles (e.g., ["owner", "admin"])

    Returns:
        OrganizationMember if valid

    Raises:
        HTTPException 404 if org doesn't exist
        HTTPException 403 if user is not a member or lacks required role
    """
    # Check org exists
    result = await db.execute(select(Organization).where(Organization.id == organization_id))
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check membership
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    # Check role if required
    if required_roles and membership.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires one of these roles: {', '.join(required_roles)}",
        )

    return membership


async def get_user_organizations(db: AsyncSession, user_id: uuid.UUID) -> list[Organization]:
    """
    Get all organizations a user is a member of.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        List of Organization objects
    """
    stmt = (
        select(Organization)
        .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == user_id)
        .order_by(Organization.created_at.desc())
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def is_org_member(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """
    Check if a user is a member of an organization (simple boolean check).

    Args:
        db: Database session
        organization_id: Organization UUID
        user_id: User UUID

    Returns:
        True if user is a member, False otherwise
    """
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def get_user_role_in_org(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
) -> str | None:
    """
    Get a user's role in an organization.

    Args:
        db: Database session
        organization_id: Organization UUID
        user_id: User UUID

    Returns:
        Role string ("owner", "admin", "member", "viewer") or None if not a member
    """
    result = await db.execute(
        select(OrganizationMember.role).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


# Role hierarchy for permission checks
ROLE_HIERARCHY = {
    "owner": 4,
    "admin": 3,
    "member": 2,
    "viewer": 1,
}


def has_sufficient_role(user_role: str, required_role: str) -> bool:
    """
    Check if a user's role meets the minimum required role.
    Uses role hierarchy: owner > admin > member > viewer

    Args:
        user_role: The user's current role
        required_role: The minimum required role

    Returns:
        True if user_role >= required_role in the hierarchy

    Example:
        has_sufficient_role("admin", "member") -> True
        has_sufficient_role("member", "admin") -> False
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    return user_level >= required_level
