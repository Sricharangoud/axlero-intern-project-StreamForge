import random
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException
from app.models.stream import LiveStream
from app.schemas.stream import LiveStreamCreate, StreamAnalyticsResponse, CategoryBreakdown


class StreamService:
    """
    Business logic service layer for live streaming telemetry, viewer analytics,
    and broadcast simulation.
    """

    @staticmethod
    async def get_live_streams(db: AsyncSession) -> List[LiveStream]:
        """Fetch all currently broadcasting live streams."""
        query = select(LiveStream).where(LiveStream.is_live == True).order_by(LiveStream.viewer_count.desc())
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def get_stream_by_id(db: AsyncSession, stream_id: str) -> LiveStream:
        """Fetch stream record by ID."""
        query = select(LiveStream).where(LiveStream.id == stream_id)
        res = await db.execute(query)
        stream = res.scalar_one_or_none()
        if not stream:
            raise EntityNotFoundException(f"Stream with ID '{stream_id}' was not found.")
        return stream

    @staticmethod
    async def get_stream_analytics(db: AsyncSession) -> StreamAnalyticsResponse:
        """Computes live aggregated platform video telemetry and viewer stats."""
        live_streams = await StreamService.get_live_streams(db)

        if not live_streams:
            return StreamAnalyticsResponse(
                total_active_streams=0,
                peak_concurrent_viewers=0,
                avg_bitrate_kbps=0.0,
                avg_dropped_frames_pct=0.0,
                total_chat_velocity=0.0,
                total_donations_usd=0.0,
                categories=[],
                top_streams=[]
            )

        total_active_streams = len(live_streams)
        total_viewers = sum(s.viewer_count for s in live_streams)
        peak_concurrent_viewers = max((s.peak_viewers for s in live_streams), default=total_viewers)
        avg_bitrate = round(sum(s.bitrate_kbps for s in live_streams) / total_active_streams, 1)
        avg_dropped_pct = round(sum(s.dropped_frames_pct for s in live_streams) / total_active_streams, 3)
        total_chat_velocity = round(sum(s.chat_velocity_ppm for s in live_streams), 1)
        total_donations = round(sum(s.total_donations_usd for s in live_streams), 2)

        # Category breakdown
        category_map = {}
        for s in live_streams:
            if s.category not in category_map:
                category_map[s.category] = {"active_channels": 0, "viewer_count": 0}
            category_map[s.category]["active_channels"] += 1
            category_map[s.category]["viewer_count"] += s.viewer_count

        categories = [
            CategoryBreakdown(
                category_name=cat,
                active_channels=data["active_channels"],
                viewer_count=data["viewer_count"]
            )
            for cat, data in category_map.items()
        ]

        return StreamAnalyticsResponse(
            total_active_streams=total_active_streams,
            peak_concurrent_viewers=peak_concurrent_viewers,
            avg_bitrate_kbps=avg_bitrate,
            avg_dropped_frames_pct=avg_dropped_pct,
            total_chat_velocity=total_chat_velocity,
            total_donations_usd=total_donations,
            categories=categories,
            top_streams=live_streams
        )

    @staticmethod
    async def simulate_broadcast_event(
        db: AsyncSession,
        stream_id: Optional[str] = None,
        action: str = "viewer_spike",
        magnitude: float = 1.5
    ) -> LiveStream:
        """Interactively mutates stream telemetry to demonstrate live real-time metrics updates."""
        live_streams = await StreamService.get_live_streams(db)
        if not live_streams:
            raise EntityNotFoundException("No active live streams available to simulate.")

        target_stream = None
        if stream_id:
            target_stream = await StreamService.get_stream_by_id(db, stream_id)
        else:
            target_stream = live_streams[0]  # Default to top live stream

        if action == "viewer_spike":
            added_viewers = int(random.randint(250, 1200) * magnitude)
            target_stream.viewer_count += added_viewers
            if target_stream.viewer_count > target_stream.peak_viewers:
                target_stream.peak_viewers = target_stream.viewer_count
            target_stream.chat_velocity_ppm = round(target_stream.chat_velocity_ppm * 1.3, 1)

        elif action == "bitrate_drop":
            target_stream.bitrate_kbps = max(1200.0, target_stream.bitrate_kbps - (800.0 * magnitude))
            target_stream.dropped_frames_pct = min(12.5, target_stream.dropped_frames_pct + (1.2 * magnitude))

        elif action == "chat_burst":
            target_stream.chat_velocity_ppm = round(target_stream.chat_velocity_ppm + (150.0 * magnitude), 1)

        elif action == "new_donation":
            donation_amount = round(float(random.choice([5, 10, 25, 50, 100])) * magnitude, 2)
            target_stream.total_donations_usd = round(target_stream.total_donations_usd + donation_amount, 2)
            target_stream.viewer_count += random.randint(10, 40)

        await db.commit()
        await db.refresh(target_stream)
        return target_stream

    @staticmethod
    async def seed_default_streams(db: AsyncSession) -> List[LiveStream]:
        """Seeds initial realistic stream records if none exist."""
        query = select(LiveStream)
        res = await db.execute(query)
        if res.scalars().all():
            return []

        default_streams = [
            LiveStream(
                channel_name="AliceCodes",
                streamer_name="Alice (Senior Eng)",
                stream_title="🚀 Building Distributed Event Pipeline with FastAPI & Kafka",
                category="Software Engineering",
                viewer_count=1420,
                peak_viewers=1850,
                bitrate_kbps=6120.0,
                fps=60,
                resolution="1080p60",
                dropped_frames_pct=0.02,
                chat_velocity_ppm=185.0,
                total_donations_usd=350.0,
                avatar_color="#6366f1"
            ),
            LiveStream(
                channel_name="BobTheGamer",
                streamer_name="Bob Pro",
                stream_title="🎮 Cyberpunk 2077 Night City Speedrun [100% World Record]",
                category="Cyberpunk 2077",
                viewer_count=3250,
                peak_viewers=4100,
                bitrate_kbps=6500.0,
                fps=60,
                resolution="1080p60",
                dropped_frames_pct=0.08,
                chat_velocity_ppm=340.0,
                total_donations_usd=1240.00,
                avatar_color="#ec4899"
            ),
            LiveStream(
                channel_name="DevTalksLive",
                streamer_name="Tech Community",
                stream_title="💬 Software Architecture Q&A: Async Python vs Go Routines",
                category="Just Chatting",
                viewer_count=890,
                peak_viewers=1100,
                bitrate_kbps=5800.0,
                fps=60,
                resolution="1080p60",
                dropped_frames_pct=0.01,
                chat_velocity_ppm=95.0,
                total_donations_usd=180.50,
                avatar_color="#10b981"
            ),
            LiveStream(
                channel_name="RustMechanic",
                streamer_name="Alex R",
                stream_title="🦀 High-Performance Memory Safety in Systems Programming",
                category="Software Engineering",
                viewer_count=615,
                peak_viewers=750,
                bitrate_kbps=5950.0,
                fps=60,
                resolution="1080p60",
                dropped_frames_pct=0.04,
                chat_velocity_ppm=62.0,
                total_donations_usd=95.00,
                avatar_color="#f59e0b"
            )
        ]

        db.add_all(default_streams)
        await db.commit()
        return default_streams
