from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.exceptions import InvalidCredentialsException, UnauthorizedException
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.user_service import UserService

# OAuth2 Scheme specifying token URL endpoint for Swagger UI Authorization header
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    FastAPI dependency that decodes JWT bearer tokens and yields the authenticated User.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await UserService.get_by_id(db, user_id)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account."
        )
    return user


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency factory enforcing Role-Based Access Control (RBAC).
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' lacks permission for this action. Allowed roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker
