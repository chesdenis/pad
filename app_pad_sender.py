import os
import tarfile
import logging
import uuid
import json
import requests
import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

import _fs_entry_handler as fshandler

aes_key_string = os.environ.get("AES_KEY_STRING")
aes_key = hashlib.sha256(aes_key_string.encode()).digest()[:16]  # 16-byte key (128-bit)


def create_tar(file_list, base_dir, output_dir=".", tar_name=None):
    if tar_name is None:
        tar_name = f"{uuid.uuid4().hex}.tar"

    os.makedirs(output_dir, exist_ok=True)

    tar_path = os.path.join(output_dir, tar_name)

    try:
        with tarfile.open(tar_path, "w") as tar:
            for file_path in file_list:
                if not os.path.exists(file_path):
                    logging.warning(f"File not found: {file_path}. Skipping.")
                    continue

                rel_path = os.path.relpath(file_path, start=base_dir)

                logging.info(f"Adding file to tar archive: {file_path} as {rel_path}")
                tar.add(file_path, arcname=rel_path)

        logging.info(f"TAR archive created successfully: {tar_path}")
        return tar_path

    except Exception as e:
        raise RuntimeError(f"Failed to create tar archive: {e}")

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


def encrypt_file(file_path, aes_key):
    """
    Encrypts a file using AES encryption and writes the encrypted data to a new file.
    
    :param file_path: Path to the file to encrypt.
    :param aes_key: 16, 24, or 32 bytes AES key used for the encryption.
    :return: Path to the encrypted file.
    """
    if len(aes_key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. Key must be 16, 24, or 32 bytes.")

    encrypted_file_path = f"{file_path}.enc"

    try:
        iv = os.urandom(16)  # Generate a random IV
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        with open(file_path, "rb") as input_file, open(encrypted_file_path, "wb") as output_file:
            output_file.write(iv)  # Write the IV to the encrypted file
            while chunk := input_file.read(64 * 1024):  # Read and encrypt in chunks
                output_file.write(encryptor.update(chunk))
            output_file.write(encryptor.finalize())

        return encrypted_file_path

    except Exception as e:
        raise RuntimeError(f"Failed to encrypt file: {e}")


def upload_file_to_receiver(file_path, endpoint_url, aes_key):
    encrypted_file_path = encrypt_file(file_path, aes_key=aes_key)
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

    tar_file_path = create_tar(file_list, "/source")
    split_tar_file(tar_file_path)


if __name__ == '__main__':
    fshandler.start(on_message, prefetch_count=100, output_exchange='os_walk_response_batch')
