from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.alert import AlertSeverity, AlertStatus
from app.models.user import UserRole
from app.schemas.alert import AlertResponse, AlertUpdate
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alert Management"])


@router.get(
    "/",
    response_model=List[AlertResponse],
    dependencies=[Depends(get_current_user)]
)
async def list_system_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves triggered system alerts with optional filters for status and severity.
    """
    return await AlertService.get_alerts(db, status=status, severity=severity, limit=limit)


@router.patch(
    "/{alert_id}",
    response_model=AlertResponse,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))]
)
async def update_alert_lifecycle_status(
    alert_id: str,
    alert_in: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates the operational status of an alert (e.g., mark ACKNOWLEDGED or RESOLVED).
    """
    return await AlertService.update_alert_status(db, alert_id=alert_id, new_status=alert_in.status)


@router.post(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))]
)
async def acknowledge_system_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Convenience endpoint to acknowledge an open system alert.
    """
    return await AlertService.update_alert_status(db, alert_id=alert_id, new_status=AlertStatus.ACKNOWLEDGED)
