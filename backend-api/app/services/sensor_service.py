from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DuplicateEntityException, EntityNotFoundException
from app.models.sensor import Sensor, SensorReading
from app.schemas.sensor import SensorCreate, SensorReadingCreate, SensorUpdate


class SensorService:
    """
    Business logic for managing hardware sensors and time-series reading events.
    """

    @staticmethod
    async def create_sensor(db: AsyncSession, sensor_in: SensorCreate) -> Sensor:
        """Register a new physical or virtual sensor node."""
        query = select(Sensor).where(Sensor.sensor_code == sensor_in.sensor_code)
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise DuplicateEntityException(f"Sensor with code '{sensor_in.sensor_code}' already exists.")

        sensor = Sensor(
            sensor_code=sensor_in.sensor_code,
            name=sensor_in.name,
            location=sensor_in.location,
            metric_unit=sensor_in.metric_unit,
            warning_threshold=sensor_in.warning_threshold,
            critical_threshold=sensor_in.critical_threshold
        )
        db.add(sensor)
        await db.flush()
        await db.refresh(sensor)
        return sensor

    @staticmethod
    async def get_by_code(db: AsyncSession, sensor_code: str) -> Optional[Sensor]:
        """Fetch sensor metadata by unique sensor code."""
        query = select(Sensor).where(Sensor.sensor_code == sensor_code)
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, sensor_id: str) -> Sensor:
        """Fetch sensor by database primary key ID."""
        query = select(Sensor).where(Sensor.id == sensor_id)
        res = await db.execute(query)
        sensor = res.scalar_one_or_none()
        if not sensor:
            raise EntityNotFoundException(f"Sensor with ID '{sensor_id}' was not found.")
        return sensor

    @staticmethod
    async def get_sensors(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Sensor]:
        """Retrieve paginated list of registered sensors."""
        query = select(Sensor).offset(skip).limit(limit)
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def record_reading(db: AsyncSession, sensor_id: str, value: float, ts: Optional[datetime] = None) -> SensorReading:
        """Persists a single time-series sensor measurement."""
        timestamp = ts or datetime.now(timezone.utc)
        reading = SensorReading(
            sensor_id=sensor_id,
            value=value,
            timestamp=timestamp
        )
        db.add(reading)
        await db.flush()
        await db.refresh(reading)
        return reading

    @staticmethod
    async def get_readings_history(
        db: AsyncSession,
        sensor_id: str,
        limit: int = 100
    ) -> List[SensorReading]:
        """Retrieve recent historical data points for a specific sensor node."""
        query = (
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
        )
        res = await db.execute(query)
        return list(res.scalars().all())
