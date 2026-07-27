from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Aggregations"])


@router.get(
    "/summary",
    response_model=DashboardStatsResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves real-time system metrics and telemetry summaries for monitoring dashboards.
    """
    return await DashboardService.get_dashboard_summary(db)
