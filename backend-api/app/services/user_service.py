from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import DuplicateEntityException, EntityNotFoundException, InvalidCredentialsException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Business Logic service for managing system Users and authentication credentials.
    """

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> User:
        """Fetch a user record by primary key UUID."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise EntityNotFoundException(f"User with ID '{user_id}' was not found.")
        return user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Fetch a user record by unique email address."""
        result = await db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        """Create a new user with bcrypt password hashing."""
        existing_user = await UserService.get_by_email(db, user_in.email)
        if existing_user:
            raise DuplicateEntityException(f"User with email '{user_in.email}' already exists.")

        hashed_pw = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email.lower(),
            full_name=user_in.full_name,
            hashed_password=hashed_pw,
            role=user_in.role
        )
        db.add(db_user)
        await db.flush()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
        """Validates credentials against stored bcrypt hash."""
        user = await UserService.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException("Invalid email or password.")
        if not user.is_active:
            raise InvalidCredentialsException("User account is deactivated.")
        return user

    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieve paginated list of registered users."""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_in: UserUpdate) -> User:
        """Updates user profile or credentials."""
        user = await UserService.get_by_id(db, user_id)
        
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.refresh(user)
        return user
