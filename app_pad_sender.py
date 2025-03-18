import logging
import json
import requests
import hashlib

import _crypto_builder as crypto
import _tar_builder as comp

import os

import _fs_entry_handler as fshandler

aes_key_string = os.environ.get("AES_KEY_STRING")
aes_key = hashlib.sha256(aes_key_string.encode()).digest()[:16]  # 16-byte key (128-bit)

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


def upload_file_to_receiver(file_path, endpoint_url, aes_key):
    encrypted_file_path = crypto.encrypt_file(file_path, aes_key=aes_key)
    with open(encrypted_file_path, 'rb') as f:
        files = {'file': (os.path.basename(encrypted_file_path), f)}
        response = requests.post(endpoint_url, files=files)
        response.raise_for_status()  # Raise an error for bad HTTP responses
    logging.info(f"File {encrypted_file_path} uploaded successfully to {endpoint_url}.")
    return response


def on_message(channel, method, properties, body):
    message = json.loads(body)
    file_list = []
    for entry in message:
        file_path = entry['file_path']
        file_list.append(file_path)

    tar_file_path = comp.create_tar(file_list, "/source")
    split_tar_file(tar_file_path)

if __name__ == '__main__':
    fshandler.start(on_message, prefetch_count=100, output_exchange='os_walk_response_batch')
