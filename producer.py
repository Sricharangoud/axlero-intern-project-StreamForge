import json
from typing import Optional
from aiokafka import AIOKafkaProducer
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import KafkaStreamException


class EventProducer:
    """
    Asynchronous Kafka Event Producer client wrapper.
    Responsible for serializing and streaming high-throughput sensor telemetry events.
    """
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Initializes and starts the AIOKafkaProducer client."""
        logger.info(f"Connecting Kafka Producer to brokers at {settings.KAFKA_BOOTSTRAP_SERVERS}...")
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            await self.producer.start()
            logger.info("Kafka Producer started successfully.")
        except Exception as e:
            logger.warning(f"Kafka Producer failed to start: {str(e)}. (Application running in standalone mock mode)")
            self.producer = None

    async def stop(self):
        """Gracefully flushes and stops the Kafka Producer."""
        if self.producer:
            logger.info("Stopping Kafka Producer...")
            await self.producer.stop()
            logger.info("Kafka Producer stopped.")

    async def send_sensor_event(self, topic: str, payload: dict):
        """
        Publishes a JSON-serialized sensor reading event message to Kafka.
        
        :param topic: Target Kafka topic name.
        :param payload: Serialized telemetry dictionary.
        """
        if not self.producer:
            logger.info(f"[MOCK KAFKA PRODUCER] Streamed event to topic '{topic}': {payload}")
            return

        try:
            await self.producer.send_and_wait(topic, payload)
            logger.debug(f"Successfully published event to topic '{topic}': {payload.get('event_id')}")
        except Exception as e:
            logger.error(f"Failed to produce Kafka message to topic '{topic}': {str(e)}")
            raise KafkaStreamException(f"Kafka Producer error: {str(e)}")


# Singleton instance shared across FastAPI application
kafka_producer = EventProducer()
