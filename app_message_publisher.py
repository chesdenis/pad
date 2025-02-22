import os
import json
import pika

from _rabbit_client import logger

def process():
    logger.info(f'Start processing')
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    logger.info(f'Connected with rabbit mq')

    json_folder = '/json'

    arr = []
    file_path = os.path.join(json_folder, "input.json")
    logger.info(f'Reading from {file_path}')
    with open(file_path) as f:
        arr = json.load(f)

    for ae in arr:
        channel.basic_publish(exchange='', routing_key=ae['routing_key'],
                              body=json.dumps(ae))
        logger.debug(f'Sent {ae} for client {ae["routing_key"]}')

    logger.info(f'Published {len(arr)} items')


if __name__ == '__main__':
    process()