from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the profile details of the currently logged-in user.
    """
    return current_user


@router.get(
    "/",
    response_model=List[UserResponse],
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a list of registered users. (Admin Only)
    """
    return await UserService.get_users(db, skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
async def get_user_details(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch specific user profile by User ID. (Admin Only)
    """
    return await UserService.get_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
async def update_user_profile(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's details, role, or active status. (Admin Only)
    """
    return await UserService.update_user(db, user_id, user_in)
