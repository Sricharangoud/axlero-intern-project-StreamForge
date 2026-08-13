from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.schemas.stream import LiveStreamResponse, StreamAnalyticsResponse, StreamSimulationRequest
from app.services.stream_service import StreamService

router = APIRouter(prefix="/streams", tags=["Live Streaming & Video Telemetry"])


@router.get(
    "/live",
    response_model=List[LiveStreamResponse],
    dependencies=[Depends(get_current_user)]
)
async def list_live_streams(
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all currently active live streams with real-time video encoding metrics.
    """
    return await StreamService.get_live_streams(db)


@router.get(
    "/analytics",
    response_model=StreamAnalyticsResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_stream_analytics(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns aggregated video stream telemetry: peak viewers, bitrate, frame drops,
    chat message velocity, total tip donations, and category stats.
    """
    return await StreamService.get_stream_analytics(db)


@router.post(
    "/simulate",
    response_model=LiveStreamResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
async def simulate_stream_event(
    sim_in: StreamSimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Interactive endpoint for reviewers/testers to simulate live viewer spikes,
    bitrate fluctuations, chat bursts, or tip donations.
    """
    return await StreamService.simulate_broadcast_event(
        db=db,
        stream_id=sim_in.stream_id,
        action=sim_in.action,
        magnitude=sim_in.magnitude or 1.5
    )
