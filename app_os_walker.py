import fnmatch
import json
import os

import _rabbit_client as rc
from _rabbit_client import logger

cache = {}

#simple cache implementation
def cached(func):
    def wrapper(args):
        if args in cache:
            logger.info(f'Cache hit for {args}')
            return cache[args]
        else:
            logger.info(f'Cache not found for {args}')
            result = func(args)
            cache[args] = result
            logger.debug(f'Stored cache entry. Cache total size {len(cache)}')
            return result
    return wrapper


@cached
def iterate_folder(key):
    args = key.split(';#')

    folder_path  = args[0]
    file_mask = args[1]
    storage_path = args[2]
    recursive = int(args[3])

    result = []

    for root, dirs, files in os.walk(folder_path):
        for name in files:
            if fnmatch.fnmatch(name, file_mask):
                full_path = os.path.join(root, name)
                relative_path = os.path.relpath(full_path, storage_path)
                file_info = {
                    'path': full_path,
                    'relative_path': relative_path,
                    'type': 'file'
                }
                result.append(file_info)

        if not recursive:
            break

        for name in dirs:
            dir_full_name = os.path.join(root, name)
            dir_info = {
                'folder_path': dir_full_name,
                'storage_path': storage_path,
                'recursive': 1,
                'file_mask': file_mask,
                'type': 'folder'
            }
            result.append(dir_info)

        # we exit here because we dont want to process nested dirs,
        # they will be processed on next message as we publish dirs above
        break

    return result

def process_message(channel, method, properties, body):

    logger.info('Received command...')

    message = json.loads(body)
    client_id = message['client_id']
    folder_path = message.get('folder_path', message['storage_path'])
    storage_path = message['storage_path']
    recursive = message['recursive']
    file_mask = message['file_mask']

    exchange = 'os_walk_response'
    routing_key = client_id

    logger.debug(f'Processing command for {client_id}, {storage_path}, {folder_path}, {recursive}, {file_mask}, {exchange}...')

    try:
        channel.exchange_declare(exchange=exchange, exchange_type='topic')

        # here we need to introduce caching and check it first to not scan file system

        key = ";#".join([folder_path, file_mask, storage_path, str(recursive)])

        for message in iterate_folder(key):
            message["client_id"] = client_id

            # for files we publish to specific client directly, no need to lookup to nested folders
            if message["type"] == "file":
                channel.basic_publish(exchange=exchange, routing_key=routing_key,
                                      body=json.dumps(message))
                logger.debug(f'Sent {message} for client {client_id}')

            # for folder we have to pass it again to os walker to lookup nested files
            elif message["type"] == "folder":
                # empty exchange means we publish to queue directly
                channel.basic_publish(exchange='', routing_key='os_walk_request',
                                      body=json.dumps(message))

            else:
                raise Exception('Unsupported message type')


    except Exception as e:
        logger.error(e)

    logger.info(f'Completed command for {client_id}, {storage_path}, {folder_path}, {recursive}, {file_mask}, {exchange}...')

    channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    rc.listen_with_retry(
        process_message,
        'os_walk_request',
        prefetch_count=100)