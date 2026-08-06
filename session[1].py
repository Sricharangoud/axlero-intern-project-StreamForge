from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.core.logging import logger

# Prepare engine parameters based on database dialect (PostgreSQL vs SQLite)
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}

if settings.DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 10
    })

# Initialize Async Engine
engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Async Session Factory for generating isolated session instances per request
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency that provides a transactional AsyncSession for DB operations.
    Automatically closes the session upon request completion or rolls back on exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database transaction failure, rolling back: {str(e)}")
            raise e
        finally:
            await session.close()
