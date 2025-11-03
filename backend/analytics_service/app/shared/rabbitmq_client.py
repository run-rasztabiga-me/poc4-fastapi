import pika
import json
import logging
from typing import Callable, Optional
from pydantic import BaseModel
from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQClient:
    """RabbitMQ client for publishing and consuming messages"""

    def __init__(self, rabbitmq_url: Optional[str] = None):
        """
        Initialize RabbitMQ client

        Args:
            rabbitmq_url: RabbitMQ connection URL (defaults to config value)
        """
        self.rabbitmq_url = rabbitmq_url or config.RABBITMQ_URL
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")

    def declare_exchange(self, exchange_name: str, exchange_type: str = "fanout"):
        """
        Declare an exchange

        Args:
            exchange_name: Name of the exchange
            exchange_type: Type of exchange (fanout, direct, topic, headers)
        """
        if not self.channel:
            self.connect()

        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        logger.info(f"Declared exchange: {exchange_name} ({exchange_type})")

    def declare_queue(self, queue_name: str):
        """
        Declare a queue

        Args:
            queue_name: Name of the queue
        """
        if not self.channel:
            self.connect()

        self.channel.queue_declare(queue=queue_name, durable=True)
        logger.info(f"Declared queue: {queue_name}")

    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str = ""):
        """
        Bind a queue to an exchange

        Args:
            queue_name: Name of the queue
            exchange_name: Name of the exchange
            routing_key: Routing key for binding
        """
        if not self.channel:
            self.connect()

        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        logger.info(f"Bound queue {queue_name} to exchange {exchange_name}")

    def publish(self, exchange_name: str, message: BaseModel, routing_key: str = ""):
        """
        Publish a message to an exchange

        Args:
            exchange_name: Name of the exchange
            message: Pydantic model to publish
            routing_key: Routing key for message
        """
        if not self.channel:
            self.connect()

        message_body = message.model_dump_json()

        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type="application/json"
            )
        )
        logger.info(f"Published message to {exchange_name}: {message.event_type}")

    def consume(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False
    ):
        """
        Start consuming messages from a queue

        Args:
            queue_name: Name of the queue to consume from
            callback: Callback function to process messages
            auto_ack: Whether to automatically acknowledge messages
        """
        if not self.channel:
            self.connect()

        def wrapper_callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                logger.info(f"Received message from {queue_name}: {message.get('event_type')}")
                callback(message)

                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if not auto_ack:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapper_callback,
            auto_ack=auto_ack
        )

        logger.info(f"Started consuming from queue: {queue_name}")
        self.channel.start_consuming()


# ============================================
# EXCHANGE AND QUEUE NAMES
# ============================================

# Exchanges
USERS_EXCHANGE = "users.events"
NOTES_EXCHANGE = "notes.events"

# Queues
ANALYTICS_USERS_QUEUE = "analytics.users.queue"
ANALYTICS_NOTES_QUEUE = "analytics.notes.queue"


def setup_rabbitmq_infrastructure():
    """
    Setup RabbitMQ exchanges and queues
    Should be called on application startup
    """
    client = RabbitMQClient()
    try:
        client.connect()

        # Declare exchanges
        client.declare_exchange(USERS_EXCHANGE, "fanout")
        client.declare_exchange(NOTES_EXCHANGE, "fanout")

        # Declare queues
        client.declare_queue(ANALYTICS_USERS_QUEUE)
        client.declare_queue(ANALYTICS_NOTES_QUEUE)

        # Bind queues to exchanges
        client.bind_queue(ANALYTICS_USERS_QUEUE, USERS_EXCHANGE)
        client.bind_queue(ANALYTICS_NOTES_QUEUE, NOTES_EXCHANGE)

        logger.info("RabbitMQ infrastructure setup completed")
    finally:
        client.close()
