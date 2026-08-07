import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings Manager.
    Uses Pydantic BaseSettings to read configuration parameters from
    environment variables or the .env file automatically.
    """
    # Project Settings
    PROJECT_NAME: str = "StreamForge - Distributed Python Event Processor"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "streamforge_user"
    POSTGRES_PASSWORD: str = "streamforge_secret"
    POSTGRES_DB: str = "streamforge_db"
    
    # Default to local SQLite database for instant zero-config testing if PostgreSQL is not active
    DATABASE_URL: str = "sqlite+aiosqlite:///./streamforge.db"

    # JWT Authentication Settings
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Apache Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SENSOR_TOPIC: str = "sensor_events"
    KAFKA_ALERT_TOPIC: str = "sensor_alerts"
    KAFKA_CONSUMER_GROUP: str = "streamforge_processor_group"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Instantiate global settings object for access across the application
settings = Settings()
