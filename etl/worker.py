import hashlib
import logging
import sys
import pika
import psycopg2
from app import run
from common.config import RabbitMQConfig, PostgresConfig

rabbitmq_config = RabbitMQConfig()
postgres_config = PostgresConfig()

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_config.RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_config.RABBITMQ_QUEUE)

# Ensure a single unacknowledged message per consumer (fair dispatch)
channel.basic_qos(prefetch_count=1)

# Configure logger to write to stdout so docker logs capture it reliably
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def _device_lock_key(device_id: str) -> int:
    """Derive a 64-bit lock key from device_id using a stable hash."""
    h = hashlib.sha256(device_id.encode()).digest()
    return int.from_bytes(h[:8], byteorder='big', signed=False)

def callback(ch, method, properties, body):
    device_id = body.decode()
    delivery_tag = method.delivery_tag
    lock_key = _device_lock_key(device_id)

    conn = None
    try:
        # connect to Postgres to acquire advisory lock
        conn = psycopg2.connect(
            dbname=postgres_config.POSTGRES_DB,
            user=postgres_config.POSTGRES_USER,
            password=postgres_config.POSTGRES_PASSWORD,
            host=postgres_config.POSTGRES_HOST,
            port=postgres_config.POSTGRES_PORT,
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s);", (lock_key,))
            got_lock = cur.fetchone()[0]

        if not got_lock:
            # Another worker is processing this device — requeue to try later
            ch.basic_nack(delivery_tag=delivery_tag, requeue=True)
            return

        logger.info("[etl worker] Received device_id: %s (locked)", device_id)

        try:
            run(device_id)
            # processing succeeded -> ack
            ch.basic_ack(delivery_tag=delivery_tag)
        except Exception as e:
            # processing failed -> nack and requeue
            logger.exception("[etl worker] Error processing %s", device_id)
            ch.basic_nack(delivery_tag=delivery_tag, requeue=True)
            raise
        finally:
            # release advisory lock
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(%s);", (lock_key,))
                logger.info("[etl worker] Release device_id: %s (unlocked)", device_id)

    except Exception as exc:
        # If something unexpected happened, ensure message is requeued
        try:
            ch.basic_nack(delivery_tag=delivery_tag, requeue=True)
        except Exception:
            pass
        logger.exception("[etl worker] Unexpected error")
    finally:
        if conn:
            conn.close()


channel.basic_consume(queue=rabbitmq_config.RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=False)
logger.info("[etl worker] Waiting for device IDs in queue '%s'...", rabbitmq_config.RABBITMQ_QUEUE)
channel.start_consuming()
