from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SensorBase(BaseModel):
    sensor_code: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=100)
    metric_unit: str = Field(..., min_length=1, max_length=20)
    warning_threshold: float = Field(default=75.0)
    critical_threshold: float = Field(default=90.0)


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    metric_unit: Optional[str] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    is_active: Optional[bool] = None


class SensorResponse(SensorBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SensorReadingCreate(BaseModel):
    sensor_code: str
    value: float
    timestamp: Optional[datetime] = None


class SensorReadingResponse(BaseModel):
    id: str
    sensor_id: str
    value: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class SensorEventKafkaMessage(BaseModel):
    """
    Schema representing the payload published to and consumed from Kafka topics.
    """
    event_id: str
    sensor_code: str
    sensor_id: str
    value: float
    timestamp: str
