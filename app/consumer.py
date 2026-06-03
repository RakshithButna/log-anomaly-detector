# RabbitMQ consumer
import pika
import json
import os
from dotenv import load_dotenv
from app.detector import detector
from app.database import SessionLocal
from app.models import LogEntry, AnomalyRecord

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "logs")

def process_log(ch, method, properties, body):
    """Called every time a new log arrives from RabbitMQ"""
    db = SessionLocal()
    try:
        # Parse the incoming log
        log = json.loads(body)
        service = log.get("service")
        level = log.get("level")
        message = log.get("message")
        latency_ms = log.get("latency_ms")

        # Save log to PostgreSQL
        log_entry = LogEntry(
            service=service,
            level=level,
            message=message,
            latency_ms=latency_ms
        )
        db.add(log_entry)
        db.commit()

        # Run anomaly detection
        anomalies = detector.analyse(level, latency_ms)

        # Save any anomalies found
        for anomaly in anomalies:
            print(f"🚨 ANOMALY DETECTED: {anomaly['anomaly_type']} - {anomaly['detail']}")
            record = AnomalyRecord(
                service=service,
                anomaly_type=anomaly["anomaly_type"],
                detail=anomaly["detail"],
                latency_ms=latency_ms
            )
            db.add(record)
            db.commit()

        # Acknowledge the message was processed
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing log: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    finally:
        db.close()

def start_consumer():
    """Start listening to RabbitMQ queue"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=process_log)

    print("👂 Consumer started — waiting for logs...")
    channel.start_consuming()
