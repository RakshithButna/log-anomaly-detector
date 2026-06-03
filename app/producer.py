# RabbitMQ producer
import pika
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "logs")

def get_connection():
    """Create a connection to RabbitMQ"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def publish_log(service: str, level: str, message: str, latency_ms: float = None):
    """Send a log event to RabbitMQ"""
    try:
        connection = get_connection()
        channel = connection.channel()

        # Make sure the queue exists
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        # Build the log payload
        log = {
            "service": service,
            "level": level,
            "message": message,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Push it into the queue
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(log),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )

        connection.close()
        return True

    except Exception as e:
        print(f"Failed to publish log: {e}")
        return False
