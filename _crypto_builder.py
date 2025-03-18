from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import logging
import os

def decrypt_file(source_path, decrypted_path, aes_key):
    if len(aes_key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. Key must be 16, 24, or 32 bytes.")

    with open(source_path, "rb") as file:
        # Read the encrypted file content
        encrypted_data = file.read()

        # The first 16 bytes of the encrypted file contain the IV
        iv = encrypted_data[:16]
        encrypted_content = encrypted_data[16:]

        try:
            # Initialize the AES cipher for decryption
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            os.makedirs(os.path.dirname(decrypted_path), exist_ok=True)

            # Decrypt the content in chunks and write to the output path
            with open(decrypted_path, "wb") as output_file:
                output_file.write(decryptor.update(encrypted_content))
                output_file.write(decryptor.finalize())

            logging.info(f"Decrypted file saved to: {decrypted_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to decrypt file: {e}")


def encrypt_file(source_path, aes_key):
    if len(aes_key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. Key must be 16, 24, or 32 bytes.")

    encrypted_file_path = f"{source_path}.enc"

    try:
        iv = os.urandom(16)  # Generate a random IV
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        with (open(source_path, "rb") as input_file,
              open(encrypted_file_path, "wb") as output_file):
            output_file.write(iv)  # Write the IV to the encrypted file
            while chunk := input_file.read(64 * 1024):  # Read and encrypt in chunks
                output_file.write(encryptor.update(chunk))
            output_file.write(encryptor.finalize())

        return encrypted_file_path

    except Exception as e:
        raise RuntimeError(f"Failed to encrypt file: {e}")
