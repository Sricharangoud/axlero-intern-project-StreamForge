import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.core.config import settings
from app.core.exceptions import EntityNotFoundException
from app.kafka.producer import kafka_producer
from app.models.user import User, UserRole
from app.schemas.sensor import (
    SensorCreate,
    SensorReadingCreate,
    SensorReadingResponse,
    SensorResponse
)
from app.services.sensor_service import SensorService

router = APIRouter(prefix="/sensors", tags=["Sensors & Telemetry Ingestion"])


@router.post(
    "/",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))]
)
async def register_sensor(
    sensor_in: SensorCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new physical IoT or industrial hardware sensor node in the database.
    """
    return await SensorService.create_sensor(db, sensor_in)


@router.get(
    "/",
    response_model=List[SensorResponse],
    dependencies=[Depends(get_current_user)]
)
async def list_sensors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns list of registered sensor nodes.
    """
    return await SensorService.get_sensors(db, skip=skip, limit=limit)


@router.get(
    "/{sensor_id}",
    response_model=SensorResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_sensor(
    sensor_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves sensor metadata details by ID.
    """
    return await SensorService.get_by_id(db, sensor_id)


@router.post(
    "/ingest",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_current_user)]
)
async def ingest_sensor_telemetry(
    reading_in: SensorReadingCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Asynchronously ingests high-volume sensor event measurements.
    Publishes the telemetry payload directly into Apache Kafka topic for distributed processing.
    """
    sensor = await SensorService.get_by_code(db, reading_in.sensor_code)
    if not sensor:
        raise EntityNotFoundException(f"Sensor code '{reading_in.sensor_code}' is not registered.")

    timestamp_str = (reading_in.timestamp or datetime.now(timezone.utc)).isoformat()
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "sensor_code": sensor.sensor_code,
        "sensor_id": sensor.id,
        "value": reading_in.value,
        "timestamp": timestamp_str
    }

    # Stream event payload to Kafka topic
    await kafka_producer.send_sensor_event(
        topic=settings.KAFKA_SENSOR_TOPIC,
        payload=event_payload
    )

    return {
        "success": True,
        "message": "Telemetry reading accepted and streamed to Kafka topic.",
        "event": event_payload
    }


@router.get(
    "/{sensor_id}/readings",
    response_model=List[SensorReadingResponse],
    dependencies=[Depends(get_current_user)]
)
async def get_sensor_reading_history(
    sensor_id: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches time-series reading history for a specified sensor.
    """
    await SensorService.get_by_id(db, sensor_id)  # Validate sensor exists
    return await SensorService.get_readings_history(db, sensor_id=sensor_id, limit=limit)
