from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import StreamForgeException, global_unhandled_exception_handler, streamforge_exception_handler
from app.core.logging import logger
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.kafka.producer import kafka_producer
from app.kafka.consumer import kafka_consumer
from app.api.v1.router import api_v1_router
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy import select


async def create_tables_and_seed_admin():
    """
    Asynchronously creates database tables if they do not exist
    and seeds an initial default Admin user account.
    """
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed Admin User if none exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.role == UserRole.ADMIN))
        admin_exists = result.scalar_one_or_none()
        if not admin_exists:
            logger.info("Seeding initial Default Admin user...")
            admin_user = User(
                email="admin@streamforge.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("Admin@12345"),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            logger.info("Default Admin user created successfully: admin@streamforge.com / Admin@12345")

        # Seed Initial Hardware Sensors if none exist
        from app.models.sensor import Sensor, SensorReading
        from app.models.alert import Alert, AlertSeverity, AlertStatus

        sensor_count_res = await session.execute(select(Sensor))
        if not sensor_count_res.scalars().all():
            logger.info("Seeding default IoT hardware sensors...")
            default_sensors = [
                Sensor(sensor_code="SNSR-001", name="Processor Unit A", location="Zone A - Server Rack 1", metric_unit="°C", warning_threshold=75.0, critical_threshold=90.0),
                Sensor(sensor_code="SNSR-002", name="Kafka Cluster Node 1", location="Zone A - Server Rack 2", metric_unit="°C", warning_threshold=75.0, critical_threshold=90.0),
                Sensor(sensor_code="SNSR-003", name="PostgreSQL DB Host", location="Zone B - Kafka Cluster", metric_unit="°C", warning_threshold=75.0, critical_threshold=90.0),
                Sensor(sensor_code="SNSR-004", name="Mainframe Bus Node", location="Zone C - Database Host", metric_unit="°C", warning_threshold=75.0, critical_threshold=90.0),
                Sensor(sensor_code="SNSR-005", name="Edge Ingress Gateway", location="Zone D - Edge Ingress", metric_unit="°C", warning_threshold=75.0, critical_threshold=90.0, is_active=False),
            ]
            session.add_all(default_sensors)
            await session.commit()

            # Add initial sample alert
            critical_sensor = default_sensors[2]
            sample_alert = Alert(
                sensor_id=critical_sensor.id,
                reading_value=86.1,
                threshold_value=75.0,
                severity=AlertSeverity.WARNING,
                status=AlertStatus.OPEN,
                message="Elevated thermal profile detected on PostgreSQL DB Host (86.1°C)"
            )
            session.add(sample_alert)
            await session.commit()
            logger.info("Initial IoT sensors & sample alerts seeded successfully.")

        # Seed Initial Live Streams if none exist
        from app.services.stream_service import StreamService
        seeded_streams = await StreamService.seed_default_streams(session)
        if seeded_streams:
            logger.info(f"Seeded {len(seeded_streams)} default live stream channels.")



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Application Lifespan context manager.
    Handles startup services (Kafka, Database) and graceful shutdown hooks.
    """
    logger.info("Starting StreamForge Distributed Processor Engine...")
    
    # 1. Database Initialization & Admin Seeding
    try:
        await create_tables_and_seed_admin()
    except Exception as e:
        logger.warning(f"Database table creation check encountered an error: {str(e)}")

    # 2. Start Kafka Producers and Consumers
    await kafka_producer.start()
    await kafka_consumer.start()

    logger.info("StreamForge application initialized and ready for traffic.")
    yield
    
    # Shutdown sequence
    logger.info("Shutting down StreamForge engine...")
    await kafka_consumer.stop()
    await kafka_producer.stop()
    logger.info("StreamForge shutdown complete.")


# Instantiate FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="StreamForge is a high-performance distributed IoT event processor built with FastAPI, Kafka, and PostgreSQL.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS Middleware for web browser accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Exception Handlers
app.add_exception_handler(StreamForgeException, streamforge_exception_handler)
app.add_exception_handler(Exception, global_unhandled_exception_handler)

# Mount API v1 Routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
