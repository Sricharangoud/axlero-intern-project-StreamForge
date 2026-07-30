import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Read the database URL, default to a local SQLite database for easy local testing
# if no PostgreSQL database URL is provided.
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///streamforge.db"
)

# Convert DB_ECHO to a boolean. True will log all generated SQL queries to console.
DB_ECHO = os.getenv("DB_ECHO", "False").lower() in ("true", "1", "yes")

# Print connection info to help beginners understand what's happening
if DATABASE_URL.startswith("sqlite"):
    print(f"[DB] Using local SQLite database file: {DATABASE_URL}")
else:
    print(f"[DB] Connecting to PostgreSQL database: {DATABASE_URL.split('@')[-1]}")
