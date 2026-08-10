from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Provides automatic table name generation based on class name.
    """
    id: Any

    # Generate __tablename__ automatically in lowercase (e.g., User -> users)
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
