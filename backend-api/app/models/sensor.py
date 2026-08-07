from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Sensor(Base):
    """
    Sensor metadata registry table storing active IoT/hardware sensor nodes.
    """
    __tablename__ = "sensors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_unit: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., Celsius, PSI, RPM
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=75.0)
    critical_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=90.0)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    readings: Mapped[list["SensorReading"]] = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    """
    High-volume time-series database model for ingested sensor measurement events.
    """
    __tablename__ = "sensor_readings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_id: Mapped[str] = mapped_column(String(36), ForeignKey("sensors.id"), index=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )

    # Relationships
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="readings")
