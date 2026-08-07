from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.alert import AlertSeverity, AlertStatus
from app.schemas.sensor import SensorResponse


class AlertResponse(BaseModel):
    id: str
    sensor_id: str
    reading_value: float
    threshold_value: float
    severity: AlertSeverity
    status: AlertStatus
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    sensor: Optional[SensorResponse] = None

    model_config = ConfigDict(from_attributes=True)


class AlertUpdate(BaseModel):
    status: AlertStatus
