import json
import os
import _fs_entry_handler as fshandler
import _tar_builder as comp
import shutil
import logging

CHUNK_SIZE = 1024 * 1024 * 20  # 20 MB
TO_SEND_FOLDER = "/to-send"


def calculate_total_file_size_mb(file_paths):
    return sum(os.path.getsize(file) for file in file_paths) / (1024 * 1024)


def split_tar_file(file_path, chunk_size=1024 * 1024 * 20):  # Default chunk size: 20 MB
    total_parts = (os.path.getsize(file_path) + chunk_size - 1) // chunk_size

    with open(file_path, 'rb') as f:
        index = 1
        while chunk := f.read(chunk_size):
            chunk_file_path = f"{file_path}.part{index}_of_{total_parts}"
            with open(chunk_file_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
                yield chunk_file_path
            index += 1


def on_message(channel, method, properties, body):
    message = json.loads(body)
    logging.info(f"Received message: {message}")
    file_paths = [entry['path'] for entry in message]
    total_size_mb = calculate_total_file_size_mb(file_paths)

    if total_size_mb < CHUNK_SIZE / (1024 * 1024):
        tar_file_path = comp.create_tar(file_paths, "/source")
        shutil.move(tar_file_path, TO_SEND_FOLDER)
        updated_tar_file_path = os.path.join(TO_SEND_FOLDER, os.path.basename(tar_file_path))
        split_tar_file(updated_tar_file_path, chunk_size=CHUNK_SIZE)
    else:
        for file_path in file_paths:
            tar_file_path = comp.create_tar([file_path], "/source")
            shutil.move(tar_file_path, TO_SEND_FOLDER)
            updated_tar_file_path = os.path.join(TO_SEND_FOLDER, os.path.basename(tar_file_path))
            split_tar_file(updated_tar_file_path, chunk_size=CHUNK_SIZE)


if __name__ == '__main__':
    fshandler.start(on_message, prefetch_count=100, output_exchange='os_walk_response_batch', routing_key='#')