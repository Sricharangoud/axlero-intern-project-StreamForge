import asyncio
import json
from typing import Optional
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.core.logging import logger
from app.db.session import AsyncSessionLocal
from app.services.sensor_service import SensorService
from app.services.alert_service import AlertService


class EventConsumer:
    """
    Asynchronous Kafka Event Consumer background worker.
    Continuously listens to sensor topics, persists time-series events to DB,
    and evaluates threshold rules for instant alert triggering.
    """
    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_running: bool = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        """Initializes consumer subscription and launches async background loop task."""
        logger.info(f"Initializing Kafka Consumer for topic '{settings.KAFKA_SENSOR_TOPIC}'...")
        try:
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_SENSOR_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP,
                auto_offset_reset="latest",
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )
            await self.consumer.start()
            self.is_running = True
            self.task = asyncio.create_task(self._consume_loop())
            logger.info("Kafka Consumer loop running in background.")
        except Exception as e:
            logger.warning(f"Kafka Consumer failed to connect: {str(e)}. (Background consumer disabled)")
            self.is_running = False

    async def stop(self):
        """Signals shutdown and stops the background consumer task."""
        self.is_running = False
        if self.task:
            self.task.cancel()
        if self.consumer:
            logger.info("Stopping Kafka Consumer...")
            await self.consumer.stop()
            logger.info("Kafka Consumer stopped.")

    async def _consume_loop(self):
        """Background asynchronous consumer loop processing event streams."""
        try:
            async for msg in self.consumer:
                if not self.is_running:
                    break

                payload = msg.value
                logger.info(f"Kafka Consumer received message: {payload}")

                # Process consumed event inside dedicated DB session transaction
                async with AsyncSessionLocal() as db:
                    try:
                        sensor_code = payload.get("sensor_code")
                        value = payload.get("value")

                        sensor = await SensorService.get_by_code(db, sensor_code)
                        if sensor:
                            # 1. Save time-series reading event
                            await SensorService.record_reading(db, sensor.id, value)
                            # 2. Evaluate threshold rules and trigger alerts
                            await AlertService.process_reading_for_alerts(db, sensor, value)
                            await db.commit()
                        else:
                            logger.warning(f"Received reading for unregistered sensor code '{sensor_code}'")
                    except Exception as err:
                        await db.rollback()
                        logger.error(f"Error processing Kafka event: {str(err)}", exc_info=True)

        except asyncio.CancelledError:
            logger.info("Kafka consumer loop task cancelled.")
        except Exception as e:
            logger.error(f"Kafka consumer loop encountered unexpected exception: {str(e)}", exc_info=True)


# Singleton instance shared across FastAPI lifespan
kafka_consumer = EventConsumer()
