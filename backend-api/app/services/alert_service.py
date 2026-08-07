from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException
from app.core.logging import logger
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.sensor import Sensor


class AlertService:
    """
    Real-time Business Logic Engine for threshold monitoring and alert lifecycle management.
    """

    @staticmethod
    async def process_reading_for_alerts(
        db: AsyncSession,
        sensor: Sensor,
        reading_value: float
    ) -> Optional[Alert]:
        """
        Evaluates an ingested sensor reading against defined threshold limits.
        If a threshold breach occurs, an Alert record is created and committed.
        """
        severity: Optional[AlertSeverity] = None
        threshold_breached: float = 0.0

        if reading_value >= sensor.critical_threshold:
            severity = AlertSeverity.CRITICAL
            threshold_breached = sensor.critical_threshold
        elif reading_value >= sensor.warning_threshold:
            severity = AlertSeverity.WARNING
            threshold_breached = sensor.warning_threshold

        if not severity:
            return None  # Value is within safe limits

        message = (
            f"Sensor '{sensor.name}' ({sensor.sensor_code}) reported value {reading_value} {sensor.metric_unit}, "
            f"exceeding {severity.value.upper()} threshold of {threshold_breached} {sensor.metric_unit}."
        )

        logger.warning(f"THRESHOLD BREACH DETECTED: {message}")

        alert = Alert(
            sensor_id=sensor.id,
            reading_value=reading_value,
            threshold_value=threshold_breached,
            severity=severity,
            status=AlertStatus.OPEN,
            message=message
        )
        db.add(alert)
        await db.flush()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def get_alerts(
        db: AsyncSession,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Fetch filtered list of system alerts."""
        query = select(Alert).options(selectinload(Alert.sensor)).order_by(Alert.created_at.desc()).limit(limit)

        if status:
            query = query.where(Alert.status == status)
        if severity:
            query = query.where(Alert.severity == severity)

        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def update_alert_status(db: AsyncSession, alert_id: str, new_status: AlertStatus) -> Alert:
        """Updates the operational status of an alert (e.g. mark RESOLVED)."""
        query = select(Alert).options(selectinload(Alert.sensor)).where(Alert.id == alert_id)
        res = await db.execute(query)
        alert = res.scalar_one_or_none()
        
        if not alert:
            raise EntityNotFoundException(f"Alert with ID '{alert_id}' was not found.")

        alert.status = new_status
        if new_status == AlertStatus.RESOLVED:
            alert.resolved_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(alert)
        return alert
