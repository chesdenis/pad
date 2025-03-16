import os
import logging
import _fs_entry_handler as fshandler
import json

storage_folder = '/source'
meta_folder = '/meta'

BATCH_SIZE_LIMIT_MB = 100
TARGET_EXCHANGE = 'os_walk_response_batch'

# Batch processing state
current_batch = []
current_batch_size = 0

def handle_event_entry(file_path, relative_path, channel, args):
    global current_batch, current_batch_size

    channel.exchange_declare(exchange=TARGET_EXCHANGE, exchange_type='topic')

    # Get the size of the file
    message_size_mb = os.path.getsize(file_path) >> 20

    # Add message to the current batch
    current_batch.append({
        "file_path": file_path,
        "relative_path": relative_path,
        "args": args
    })

    current_batch_size += message_size_mb

    logging.info(f"Added {file_path} to batch. Current batch size: {current_batch_size:.2f} MB")

    if current_batch_size >= BATCH_SIZE_LIMIT_MB:
        logging.info("Batch size limit reached, publishing batch...")
        channel.basic_publish(exchange=TARGET_EXCHANGE, routing_key='#',
                              body=json.dumps(current_batch))

        # Reset batch
        current_batch = []
        current_batch_size = 0

if __name__ == '__main__':
    BATCH_SIZE_LIMIT_MB = int(os.getenv('BATCH_SIZE_LIMIT_MB'))
    fshandler.start(handle_event_entry, prefetch_count=100)