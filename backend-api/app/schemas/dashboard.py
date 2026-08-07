from pydantic import BaseModel
from typing import List
from app.schemas.alert import AlertResponse


class DashboardStatsResponse(BaseModel):
    total_sensors: int
    active_sensors: int
    total_readings_processed: int
    open_alerts_count: int
    critical_alerts_count: int
    warning_alerts_count: int
    recent_alerts: List[AlertResponse]
