import argparse
import json
import os

import _rabbit_client as rc
from _rabbit_client import logger

def on_message(channel, method_frame, header_frame, body):
    try:
        message = json.loads(body)
        logger.info(f"Received {message}")

        if isinstance(message, list):
            logger.info(f"Received list of entries. Delegating processing to client...")
            handle_event_entry(channel, method_frame, header_frame, body)

        client_id = message['client_id']
        path = message['path']
        type = message['type']
        relative_path = message['relative_path']
        args = message.get('args', {})

        logger.info(f"Received for {client_id}, for file {path}.")

        if type == 'file':
            handle_event_entry(path, relative_path, channel, args)
        else:
            logger.info(f"Message type is not 'file': {type}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")

    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


def handle_event_entry(file_path, relative_path, channel, args):
    return


def start(handler_func, prefetch_count=100, parser_modifier= None, args_callback=None, output_exchange='os_walk_response', routing_key=None):

    global handle_event_entry
    handle_event_entry = handler_func

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
        output_exchange, routing_key, prefetch_count=prefetch_count)

