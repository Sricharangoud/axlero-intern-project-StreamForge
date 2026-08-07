from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.sensor import Sensor, SensorReading
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.schemas.dashboard import DashboardStatsResponse


class DashboardService:
    """
    Aggregates database telemetry metrics for operational monitoring dashboards.
    """

    @staticmethod
    async def get_dashboard_summary(db: AsyncSession) -> DashboardStatsResponse:
        """
        Executes parallel aggregation queries for system metrics.
        """
        # Count total sensors
        total_sensors_res = await db.execute(select(func.count(Sensor.id)))
        total_sensors = total_sensors_res.scalar() or 0

        # Count active sensors
        active_sensors_res = await db.execute(select(func.count(Sensor.id)).where(Sensor.is_active == True))
        active_sensors = active_sensors_res.scalar() or 0

        # Count total readings processed
        total_readings_res = await db.execute(select(func.count(SensorReading.id)))
        total_readings = total_readings_res.scalar() or 0

        # Count open alerts
        open_alerts_res = await db.execute(select(func.count(Alert.id)).where(Alert.status == AlertStatus.OPEN))
        open_alerts_count = open_alerts_res.scalar() or 0

        # Count critical alerts
        critical_alerts_res = await db.execute(select(func.count(Alert.id)).where(Alert.severity == AlertSeverity.CRITICAL))
        critical_alerts_count = critical_alerts_res.scalar() or 0

        # Count warning alerts
        warning_alerts_res = await db.execute(select(func.count(Alert.id)).where(Alert.severity == AlertSeverity.WARNING))
        warning_alerts_count = warning_alerts_res.scalar() or 0

        # Fetch top 5 recent alerts with loaded sensor relationship
        recent_alerts_res = await db.execute(
            select(Alert)
            .options(selectinload(Alert.sensor))
            .order_by(Alert.created_at.desc())
            .limit(5)
        )
        recent_alerts = list(recent_alerts_res.scalars().all())

        return DashboardStatsResponse(
            total_sensors=total_sensors,
            active_sensors=active_sensors,
            total_readings_processed=total_readings,
            open_alerts_count=open_alerts_count,
            critical_alerts_count=critical_alerts_count,
            warning_alerts_count=warning_alerts_count,
            recent_alerts=recent_alerts
        )
