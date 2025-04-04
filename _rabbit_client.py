import pika
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", 5672)
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "guest")

def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                RABBITMQ_HOST,
                RABBITMQ_PORT,
                '/',
                pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)))
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection error: {e}, retrying in 5 seconds...")
            time.sleep(5)


def listen(on_message_func, queue_to_listen: str, prefetch_count: int = 1):
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=queue_to_listen, durable=True)
    channel.basic_qos(prefetch_count=prefetch_count)
    channel.basic_consume(queue=queue_to_listen, on_message_callback=on_message_func)

    channel.start_consuming()
    logger.info('Waiting for messages...')


def listen_topic_exclusive(
        on_message_func,
        queue_to_listen: str,
        exchange_name: str,
        routing_key: str,
        prefetch_count: int = 1):
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.basic_qos(prefetch_count=prefetch_count)
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
    result = channel.queue_declare(queue=queue_to_listen, exclusive=False)
    queue_name = result.method.queue

    if routing_key:
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key)
    else:
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=queue_to_listen)

    logger.info(f"Waiting for messages from queue: '{queue_name}'...")

    channel.basic_consume(queue=queue_name, on_message_callback=on_message_func)
    channel.start_consuming()


def listen_with_retry(on_message_func, queue_to_listen: str, prefetch_count: int = 1):
    while True:
        try:
            listen(on_message_func, queue_to_listen, prefetch_count)
        except pika.exceptions.AMQPConnectionError:
            logger.error("Connection lost, reconnecting...")
            time.sleep(5)


def listen_topic_exclusive_with_retry(
        on_message_func,
        queue_to_listen: str,
        exchange_name: str,
        routing_key: str,
        prefetch_count: int = 1):
    while True:
        try:
            listen_topic_exclusive(
                on_message_func,
                queue_to_listen,
                exchange_name,
                routing_key,
                prefetch_count)
        except pika.exceptions.AMQPConnectionError:
            logger.error("Connection lost, reconnecting...")
            time.sleep(5)

