import logging
import json
import requests
import hashlib

import _crypto_actions as crypto
import _split_actions as split
import _tar_builder as tb
import shutil

import os

import _fs_entry_handler as fshandler

SINGLE_TAR_LIMIT_MB = 1024 * 1024 * 20  # 20 MB
TO_SEND_FOLDER = "/to-send"
RECEIVER_URL = "http://localhost:8084/upload"

aes_key_string = os.environ.get("AES_KEY_STRING")
aes_key = hashlib.sha256(aes_key_string.encode()).digest()[:16]  # 16-byte key (128-bit)

def upload_file_to_receiver(file_path, endpoint_url):
    logging.info(f"Encrypting file {file_path}")
    encrypted_file_path = crypto.encrypt_file(file_path, aes_key=aes_key)
    logging.info(f"File {file_path} encrypted to {encrypted_file_path}")
    logging.info(f"Uploading encrypted file {encrypted_file_path} to {endpoint_url}")
    with open(encrypted_file_path, 'rb') as f:
        files = {'file': (os.path.basename(encrypted_file_path), f)}
        response = requests.post(endpoint_url, files=files)
        response.raise_for_status()  # Raise an error for bad HTTP responses
    logging.info(f"File {encrypted_file_path} uploaded successfully to {endpoint_url}.")
    return response


def on_message(channel, method, properties, body):
    message = json.loads(body)
    logging.info(f"Received message: {message}")
    file_paths = [entry['path'] for entry in message]
    total_size_mb = split.measure_mb(file_paths)
    logging.info(f"Total size of files is {total_size_mb} MB")

    if total_size_mb < SINGLE_TAR_LIMIT_MB:
        logging.info(f"Total size of files is less than {SINGLE_TAR_LIMIT_MB} MB. Splitting into parts.")
        tar_file_path = tb.create_tar(file_paths, "/source")
        shutil.move(tar_file_path, TO_SEND_FOLDER)
        logging.info(f"Tar file moved to {TO_SEND_FOLDER}")
        updated_tar_file_path = os.path.join(TO_SEND_FOLDER, os.path.basename(tar_file_path))
        for t in split.walk_on_parts(updated_tar_file_path, chunk_size=SINGLE_TAR_LIMIT_MB):
            logging.info(f"Sending tar part file {t} to app_pad_sender")
            upload_file_to_receiver(t, RECEIVER_URL)
            logging.info(f"Tar part file {t} sent successfully to app_pad_sender")
            os.remove(t)
            logging.info(f"Tar part file {t} removed")

        os.remove(updated_tar_file_path)
        logging.info(f"Tar file {updated_tar_file_path} removed")
    else:
        logging.info(f"Total size of files is greater than {SINGLE_TAR_LIMIT_MB} MB. Walking and splitting each file.")
        for file_path in file_paths:
            tar_file_path = tb.create_tar([file_path], "/source")
            shutil.move(tar_file_path, TO_SEND_FOLDER)
            logging.info(f"Tar file moved to {TO_SEND_FOLDER}")
            updated_tar_file_path = os.path.join(TO_SEND_FOLDER, os.path.basename(tar_file_path))
            for t in split.walk_on_parts(updated_tar_file_path, chunk_size=SINGLE_TAR_LIMIT_MB):
                logging.info(f"Sending tar part file {t} to app_pad_sender")
                upload_file_to_receiver(t, RECEIVER_URL)
                logging.info(f"Tar part file {t} sent successfully to app_pad_sender")
                os.remove(t)
                logging.info(f"Tar part file {t} removed")

            os.remove(updated_tar_file_path)
            logging.info(f"Tar file {updated_tar_file_path} removed")


if __name__ == '__main__':
    RECEIVER_URL = os.environ.get("RECEIVER_URL", RECEIVER_URL)
    logging.info(f"Receiver URL is {RECEIVER_URL}")
    fshandler.start(on_message, prefetch_count=100, output_exchange='app_pad_batch_pipe_to_sender', routing_key='#')
