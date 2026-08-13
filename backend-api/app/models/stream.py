from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class LiveStream(Base):
    """
    Live Stream broadcast telemetry table storing live streamer video feed status,
    viewer count, stream encoding bitrate, fps, dropped frame rate, and chat velocity.
    """
    __tablename__ = "live_streams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    streamer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stream_title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="Software Engineering")
    
    viewer_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    peak_viewers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bitrate_kbps: Mapped[float] = mapped_column(Float, default=6000.0, nullable=False)
    fps: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    resolution: Mapped[str] = mapped_column(String(20), default="1080p60", nullable=False)
    dropped_frames_pct: Mapped[float] = mapped_column(Float, default=0.05, nullable=False)
    chat_velocity_ppm: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)  # posts / messages per min
    total_donations_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    is_live: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    stream_key: Mapped[str] = mapped_column(String(100), unique=True, default=lambda: f"live_{uuid.uuid4().hex[:12]}")
    avatar_color: Mapped[str] = mapped_column(String(20), default="#6366f1")

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
