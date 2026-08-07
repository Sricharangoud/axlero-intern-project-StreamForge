from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src import config

# Extra configuration arguments
# check_same_thread=False is needed only for SQLite to allow multiple threads to access it
connect_args = {}
if config.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# The engine connects SQLAlchemy to the physical database (PostgreSQL/SQLite)
engine = create_engine(
    config.DATABASE_URL,
    echo=config.DB_ECHO,  # Logs generated SQL queries when True
    connect_args=connect_args
)

# SessionLocal is a class which will generate database sessions.
# Each instance of SessionLocal will be a database transaction block.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# DeclarativeBase is the new SQLAlchemy 2.0 base class for class-based models.
# All our database tables will inherit from this class.
class Base(DeclarativeBase):
    pass

# Helper context manager for session management in scripts
# It ensures that database connections are properly closed even if an error occurs.
class db_session:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()  # Rollback if an exception occurred
        else:
            self.db.commit()    # Commit transactions if successful
        self.db.close()
