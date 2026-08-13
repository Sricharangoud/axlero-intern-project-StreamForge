from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LiveStreamBase(BaseModel):
    channel_name: str
    streamer_name: str
    stream_title: str
    category: str = "Software Engineering"
    viewer_count: int = 0
    peak_viewers: int = 0
    bitrate_kbps: float = 6000.0
    fps: int = 60
    resolution: str = "1080p60"
    dropped_frames_pct: float = 0.05
    chat_velocity_ppm: float = 85.0
    total_donations_usd: float = 0.0
    is_live: bool = True
    avatar_color: str = "#6366f1"


class LiveStreamCreate(LiveStreamBase):
    pass


class LiveStreamResponse(LiveStreamBase):
    id: str
    stream_key: str
    started_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryBreakdown(BaseModel):
    category_name: str
    active_channels: int
    viewer_count: int


class StreamAnalyticsResponse(BaseModel):
    total_active_streams: int
    peak_concurrent_viewers: int
    avg_bitrate_kbps: float
    avg_dropped_frames_pct: float
    total_chat_velocity: float
    total_donations_usd: float
    categories: List[CategoryBreakdown]
    top_streams: List[LiveStreamResponse]


class StreamSimulationRequest(BaseModel):
    stream_id: Optional[str] = None
    action: str = Field(..., description="Action to simulate: 'viewer_spike', 'bitrate_drop', 'chat_burst', 'new_donation'")
    magnitude: Optional[float] = 1.5
