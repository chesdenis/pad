import argparse
import json
import os

import _rabbit_client as rc
from _rabbit_client import logger

def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        client_id = message['client_id']
        path = message['path']
        type = message['type']
        relative_path = message['relative_path']

        logger.info(f"Received for {client_id}, for file {path}.")

        file_name = os.path.basename(path)

        # here we make sure that we skip .ai_attr.txt files
        # we must assign attributes only for regular files
        if not file_name.lower().endswith('.ai_attr.txt'):
            if type == 'file':
                build_attribute(path, relative_path, channel)
            else:
                logger.info(f"Message type is not 'file': {type}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


def build_attribute(file_path, relative_path, channel):
    return


def start(handler_func, prefetch_count=100, parser_modifier= None, args_callback=None):

    global build_attribute
    build_attribute = handler_func

    parser = argparse.ArgumentParser(description="RabbitMQ consumer for populating .ai_attr.txt")
    parser.add_argument('--client_id', type=str, help='client id as string as identifier in data flow')

    if parser_modifier:
        parser_modifier(parser)

    args = parser.parse_args()

    if args_callback:
        args_callback(args)

    client_id = args.client_id

    rc.listen_topic_exclusive_with_retry(
        on_message,
        client_id,
        'os_walk_response', prefetch_count=prefetch_count)

