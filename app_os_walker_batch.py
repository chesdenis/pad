import os
import logging
import _fs_entry_handler as fshandler
import json
import threading

storage_folder = '/source'
meta_folder = '/meta'

TARGET_EXCHANGE = 'os_walk_response_batch'
BATCH_SIZE_LIMIT_MB = 100
FLUSH_INTERVAL_SECONDS = 60

# Batch processing state
current_batch = []
current_batch_size = 0

batch_lock = threading.Lock()  # Synchronization for batch access

def publish_batch(channel):
    """Helper to publish the batch and reset its state."""
    global current_batch, current_batch_size
    if current_batch:
        logging.info("Publishing batch due to timed/threshold trigger...")
        channel.basic_publish(exchange=TARGET_EXCHANGE, routing_key='#',
                              body=json.dumps(current_batch))
        current_batch = []
        current_batch_size = 0

def timed_flush(channel):
    """Periodically flush the batch regardless of size."""
    global current_batch, current_batch_size

    with batch_lock:  # Ensure no modification to batch during this
        if current_batch:
            logging.info("Timed flush triggered. Publishing current batch...")
            publish_batch(channel)

    # Schedule the next timed flush
    timer = threading.Timer(FLUSH_INTERVAL_SECONDS, timed_flush, [channel])
    timer.daemon = True  # Ensures the timer stops when the program exits
    timer.start()


def handle_event_entry(file_path, relative_path, channel, args):
    global current_batch, current_batch_size

    channel.exchange_declare(exchange=TARGET_EXCHANGE, exchange_type='topic')

    # Get the size of the file
    message_size_mb = os.path.getsize(file_path) >> 20

    with batch_lock:  # Synchronize access to batch
        # Add message to the current batch
        current_batch.append({
            "path": file_path,
            "type": "file",
            "client_id": "app_os_walker_batch", # this is because publish happens to exchange, so not specific client here
            "relative_path": relative_path,
            "args": args
        })

        current_batch_size += message_size_mb

        logging.info(f"Added {file_path} to batch. Current batch size: {current_batch_size:.2f} MB")

        if current_batch_size >= BATCH_SIZE_LIMIT_MB:
            logging.info("Batch size limit reached, publishing batch...")
            publish_batch(channel)


if __name__ == '__main__':
    BATCH_SIZE_LIMIT_MB = int(os.getenv('BATCH_SIZE_LIMIT_MB', BATCH_SIZE_LIMIT_MB))
    TARGET_EXCHANGE = os.getenv('TARGET_EXCHANGE', TARGET_EXCHANGE)
    fshandler.start(handle_event_entry, prefetch_count=100)